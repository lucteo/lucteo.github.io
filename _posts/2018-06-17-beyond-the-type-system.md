---
layout: post
title:  "Beyond the type system"
date:   2018-06-17
banner_image: value.jpg
image: images/posts/value.jpg
description: "What low-level code is generated from using our C++ types? What's the difference between a regular reference and a rvalue reference? Find some answers here."
tags: [C++, type system, efficiency]
---

Often when we consider a type system we think about a complex formalism to denote the semantics of a language. Languages typically add features by increasing the complexity of the type system.

But there is also another perspective on the type system: how does the generated code look like? what is the ABI for the code that uses different features of the type system? We'll try to explore this perspective in this blog post.

<!--more-->

## Our perspective

For the purpose of this post, we assume a narrow perspective when analyzing the C++ type system. Assuming that we have a `MyType` class type, we are interested in how the compiler passes this around in various contexts, how this type is adjusted based on the context need.

We care about the distinction between value type, reference type and pointer type, but we also look at r-value references and we briefly touch on C++'s [value categories](http://en.cppreference.com/w/cpp/language/value_category) (glvalue, rvalue, lvalue, xvalue, prvalue).

On top of these, we are also briefly interested in the `const` modifier (and we don't care about the `volatile` modifier for types).

From the all possible usages of types in C++, we will look at:
- defining variables
- fields in a structure/class
- function parameters
- function return value

For all these, we write C++ code and then we use a clang compiler to inspect the generated LLVM code. Of course, different compiler may have different rules, they generate different code. But this is not our main goal here; we don't strive for completeness, but rather for some insights on how the compiler may do it.

## Values, references, pointers

Let us take a trivial example:
{% highlight C++ %}
struct MyType {
    int data[5]{0};
};

void valueVsRef() {
    MyType value;
    MyType& ref = value;
    const MyType& cref = value;
    MyType* ptr = &value;
    const MyType* cptr = &value;
}
{% endhighlight %}

If we compile this with clang, the LLVM output would be something similar to:
{% highlight LLVM %}
%struct.MyType = type { [5 x i32] }

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z10valueVsRefv() #0 {
  %1 = alloca %struct.MyType, align 4
  %2 = alloca %struct.MyType*, align 8
  %3 = alloca %struct.MyType*, align 8
  %4 = alloca %struct.MyType*, align 8
  %5 = alloca %struct.MyType*, align 8
  call void @_ZN6MyTypeC1Ev(%struct.MyType* %1) #3
  store %struct.MyType* %1, %struct.MyType** %2, align 8
  store %struct.MyType* %1, %struct.MyType** %3, align 8
  store %struct.MyType* %1, %struct.MyType** %4, align 8
  store %struct.MyType* %1, %struct.MyType** %5, align 8
  ret void
}
{% endhighlight %}

The compiler will not properly name the variables, but we can easily guess which is which. The variable `%1` corresponds to the value type; the rest are variables `%2` to `%5`. What is immediately visible is that there is no difference between references and pointers; moreover, `const` modifier doesn't change the LLVM output. All these references and pointers get translated into simple pointers by LLVM. For each of this pointer, the initialization is translated in a `store` instruction.

At this level, the constness of types is completely ignored. That's why, from now on, we won't be looking into const values, references and pointer anymore.

There is another important fact proved by this example. Look at the constructor call for the value. It takes the object to be constructed as a pointer. Actually, all the LLVM `alloca` functions declare pointers instead of values. The type of `%1` is `%struct.MyType*`, and not `%struct.MyType`; similarly, the type of `%2` is `%struct.MyType**`, and not `%struct.MyType*`. In the case of references and pointers, clang actually transforms them into double pointers.

This is the first indicator that lvalues (all these C++ variables are lvalues) are translated into pointers.

## lvalues, xvalues, prvalues

Let us take another example to show the difference between different value categories:

{% highlight C++ %}
MyType makeMyType() { return MyType{}; }

void lvalueAndPrvalue() {
    MyType value;               // lvalue
    makeMyType();               // result is prvalue
}
void xvalue() {
    std::move(makeMyType());
}
void xvalue2() {
    MyType&& rvalueref = makeMyType();
}
{% endhighlight %}

The resulting LLVM translation looks like:
{% highlight LLVM %}
define void @_Z10makeMyTypev(%struct.MyType* noalias sret) #0 {...}

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z16lvalueAndPrvaluev() #0 {
  %1 = alloca %struct.MyType, align 4
  %2 = alloca %struct.MyType, align 4
  call void @_ZN6MyTypeC1Ev(%struct.MyType* %1) #3
  call void @_Z10makeMyTypev(%struct.MyType* sret %2)
  ret void
}
; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z6xvaluev() #0 {
  %1 = alloca %struct.MyType*, align 8
  %2 = alloca %struct.MyType, align 4
  call void @_Z10makeMyTypev(%struct.MyType* sret %2)
  store %struct.MyType* %2, %struct.MyType** %1, align 8
  %3 = load %struct.MyType*, %struct.MyType** %1, align 8
  ret void
}
; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z7xvalue2v() #0 {
  %1 = alloca %struct.MyType*, align 8
  %2 = alloca %struct.MyType, align 4
  call void @_Z10makeMyTypev(%struct.MyType* sret %2)
  store %struct.MyType* %2, %struct.MyType** %1, align 8
  ret void
}
{% endhighlight %}

Based on this, the following conclusions can be taken:
- lvalues and prvalues behave the same; they both result into a pointer created by the compiler
- xvalue requires both a pointer and a pointer-to-pointer
- std::move does an extra dereference compared to just a rvalue-reference creation
- xvalues (rvalue-references) behave like regular user-defied references

This way, we can arrange the value categories based on the underlying types in the following table:


| Value category | Underlying type | Observation |
| --- | --- | --- |
| lvalue | `MyType*` | |
| prvalue | `MyType*` | |
| xvalue | `MyType**` | Just like references |

One point that keeps recurring through this post is that there is no pure value types in the ABI (exceptions apply).

## Members of structures

Let's look at the following C++ code using structures:

{% highlight C++ %}
struct MyStruct {
    MyType value;
    MyType& ref;
    MyType* ptr;
    MyType&& rvalueref;
};

void process(MyType& ref) {}
void process(MyType&& rvref) {}

void useStruct() {
    MyType v;
    MyStruct obj = {v, v, &v, std::move(v)};
    process(obj.value);
    process(obj.ref);
    process(*obj.ptr);
    process(obj.rvalueref);
}
{% endhighlight %}

It defines a structure containing multiple values of different types. The point of this example is to check how different attributes of the structs are being used. The corresponding LLVM code looks like:

{% highlight LLVM %}
%struct.MyStruct = type { %struct.MyType, %struct.MyType*, %struct.MyType*, %struct.MyType* }

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z7processR6MyType(%struct.MyType* dereferenceable(20)) #0 {
  %2 = alloca %struct.MyType*, align 8
  store %struct.MyType* %0, %struct.MyType** %2, align 8
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z7processO6MyType(%struct.MyType* dereferenceable(20)) #0 {
  %2 = alloca %struct.MyType*, align 8
  store %struct.MyType* %0, %struct.MyType** %2, align 8
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z9useStructv() #0 {
  %1 = alloca %struct.MyType*, align 8
  %2 = alloca %struct.MyType, align 4
  %3 = alloca %struct.MyStruct, align 8
  call void @_ZN6MyTypeC1Ev(%struct.MyType* %2) #4
  %4 = getelementptr inbounds %struct.MyStruct, %struct.MyStruct* %3, i32 0, i32 0
  %5 = bitcast %struct.MyType* %4 to i8*
  %6 = bitcast %struct.MyType* %2 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* %5, i8* %6, i64 20, i32 4, i1 false)
  %7 = getelementptr inbounds %struct.MyStruct, %struct.MyStruct* %3, i32 0, i32 1
  store %struct.MyType* %2, %struct.MyType** %7, align 8
  %8 = getelementptr inbounds %struct.MyStruct, %struct.MyStruct* %3, i32 0, i32 2
  store %struct.MyType* %2, %struct.MyType** %8, align 8
  %9 = getelementptr inbounds %struct.MyStruct, %struct.MyStruct* %3, i32 0, i32 3
  store %struct.MyType* %2, %struct.MyType** %1, align 8
  %10 = load %struct.MyType*, %struct.MyType** %1, align 8
  store %struct.MyType* %10, %struct.MyType** %9, align 8
  %11 = getelementptr inbounds %struct.MyStruct, %struct.MyStruct* %3, i32 0, i32 0
  call void @_Z7processR6MyType(%struct.MyType* dereferenceable(20) %11)
  %12 = getelementptr inbounds %struct.MyStruct, %struct.MyStruct* %3, i32 0, i32 1
  %13 = load %struct.MyType*, %struct.MyType** %12, align 8
  call void @_Z7processR6MyType(%struct.MyType* dereferenceable(20) %13)
  %14 = getelementptr inbounds %struct.MyStruct, %struct.MyStruct* %3, i32 0, i32 2
  %15 = load %struct.MyType*, %struct.MyType** %14, align 8
  call void @_Z7processR6MyType(%struct.MyType* dereferenceable(20) %15)
  %16 = getelementptr inbounds %struct.MyStruct, %struct.MyStruct* %3, i32 0, i32 3
  %17 = load %struct.MyType*, %struct.MyType** %16, align 8
  call void @_Z7processR6MyType(%struct.MyType* dereferenceable(20) %17)
  ret void
}
{% endhighlight %}

If we just look at the LLVM structure definition, things may be confusing. In there we have the first member (apparently) as pure value, and the rest of the members as pointers. But we need to look at how the structure is used to actually determine the *proper* values of the struct members.

The key point here is that whenever we need to access a struct member, we have two things: a *handle* to the structure itself, and the actual member in the structure (offset + type). That is, the final type of a struct member is always given by the combination of the structure access type and the underlying member type. For our example, we can summarize the results as:

| Member type | Structure access | Underlying type | Combined type | Observation |
| --- | --- | --- | --- |
| `MyType` | `MyStruct*` | `MyType` | `MyType*` | Just like regular values|
| `MyType&` | `MyStruct*` | `MyType*` | `MyType**` | Just like regular references|
| `MyType*` | `MyStruct*` | `MyType*` | `MyType**` | Just like regular references |
| `MyType&&` | `MyStruct*` | `MyType*` | `MyType**` | Just like regular references |

Indeed, if we look at the generated LLVM code, we see that each time we want to access a member (to call `process`) we have either a `MyType*` (first case), or a `MyType**` (look at the extra `load` instruction).

Again, pointers everywhere; no pure value types in underlying ABI.


## Passing arguments to functions

Consider the following C++ functions:

{% highlight C++ %}
void checkParam(int val) {}
void checkParam(MyType obj) {}
void checkParam(MyType& obj) {}
void checkParam(MyType* obj) {}
void checkParam(MyType&& obj) {}
{% endhighlight %}

These get translated into LLVM in the following way:
{% highlight LLVM %}
; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z10checkParami(i32) #0 {
  %2 = alloca i32, align 4
  store i32 %0, i32* %2, align 4
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z10checkParam6MyType(%struct.MyType* byval align 8) #0 {
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z10checkParamR6MyType(%struct.MyType* dereferenceable(20)) #0 {
  %2 = alloca %struct.MyType*, align 8
  store %struct.MyType* %0, %struct.MyType** %2, align 8
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z10checkParamP6MyType(%struct.MyType*) #0 {
  %2 = alloca %struct.MyType*, align 8
  store %struct.MyType* %0, %struct.MyType** %2, align 8
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z10checkParamO6MyType(%struct.MyType* dereferenceable(20)) #0 {
  %2 = alloca %struct.MyType*, align 8
  store %struct.MyType* %0, %struct.MyType** %2, align 8
  ret void
}
{% endhighlight %}

The function that just takes an `int` as an argument is different from the rest of the other functions. It takes the parameter by value, but then it creates a temporary variable (`i32*`) and copies the value of the argument into it. This will enable the users to dereference the parameter inside the function (`&val`). Although we actually pass this by value, we always have a local variable that we can use.

All the rest of the functions take a `MyType*` as parameter. Please note that `byval` and `dereferenceable` are only hints for the optimizer.

Inside of these functions, we use the parameter in different ways. That is why there is a difference in the body of the second function and the bodies of the last 3 functions. In the last 3 functions, we are actually creating new variables (`MyType**`).

This can be summarized by the following table:

| Parameter type | Underlying type | Local variable underlying type | Observation |
| --- | --- | --- | --- |
| `int` | `i32` | `i32*` | |
| `MyType` | `MyType*` | N/A | No need for local var; just use param |
| `MyType&` | `MyType*` | `MyType**` | |
| `MyType*` | `MyType*` | `MyType**` | |
| `MyType&&` | `MyType*` | `MyType**` | |

Here, we need to discuss why do we have the `int` parameter passed by value, but an `MyType` parameter is actually passed with a pointer. In general, the compiler will pass a value through a pointer whenever one of the two conditions are met:
* object identity may be used in the definition of the object (i.e., object is not a POD)
* object size is larger than a given threshold.

If, for example, we would change the definition of `MyType` to:
{% highlight C++ %}
struct MyType {
    int data[4]{0};
};
{% endhighlight %}

then we would get the following translation to LLVM of our pass-by-value function:

{% highlight LLVM %}
define void @_Z10checkParam6MyType(i64, i64) #0 {
  %3 = alloca %struct.MyType, align 4
  %4 = bitcast %struct.MyType* %3 to { i64, i64 }*
  %5 = getelementptr inbounds { i64, i64 }, { i64, i64 }* %4, i32 0, i32 0
  store i64 %0, i64* %5, align 4
  %6 = getelementptr inbounds { i64, i64 }, { i64, i64 }* %4, i32 0, i32 1
  store i64 %1, i64* %6, align 4
  ret void
}
{% endhighlight %}

As one can see, the compiler will pass the value of `MyType` as two 64-bit integers, and then recompose the object inside the function.

Of course, this works on a compiler in which an `int` is translated to `i32`. Other compilers may have different rules / thresholds.

In general, we can treat this as an optimization. We can assume that every pass-by-value will be translated into a pass-by-pointer in the underlying ABI, and sometimes the compiler can optimize on this.

If we ignore this optimization, we can conclude that all parameters are passed by pointers in the underlying ABI.


## Returning from functions

Let's now turn the attention towards expressing the return values in the ABI. Let's look at the following C++ code:

{% highlight C++ %}
MyType ret1() { return {}; }
MyType* ret2() { return nullptr; }
MyType& ret3() { return global; }
MyType&& ret4() { return std::move(global); }
{% endhighlight %}

This gets translated to:

{% highlight LLVM %}
; Function Attrs: noinline nounwind optnone ssp uwtable
define void @_Z4ret1v(%struct.MyType* noalias sret) #0 {
  %2 = getelementptr inbounds %struct.MyType, %struct.MyType* %0, i32 0, i32 0
  %3 = getelementptr inbounds [5 x i32], [5 x i32]* %2, i64 0, i64 0
  store i32 0, i32* %3, align 4
  %4 = getelementptr inbounds i32, i32* %3, i64 1
  %5 = getelementptr inbounds i32, i32* %3, i64 5
  br label %6

; <label>:6:                                      ; preds = %6, %1
  %7 = phi i32* [ %4, %1 ], [ %8, %6 ]
  store i32 0, i32* %7, align 4
  %8 = getelementptr inbounds i32, i32* %7, i64 1
  %9 = icmp eq i32* %8, %5
  br i1 %9, label %10, label %6

; <label>:10:                                     ; preds = %6
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define %struct.MyType* @_Z4ret2v() #0 {
  ret %struct.MyType* null
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define dereferenceable(20) %struct.MyType* @_Z4ret3v() #0 {
  ret %struct.MyType* @global
}

; Function Attrs: noinline nounwind optnone ssp uwtable
define dereferenceable(20) %struct.MyType* @_Z4ret4v() #0 {
  %1 = alloca %struct.MyType*, align 8
  store %struct.MyType* @global, %struct.MyType** %1, align 8
  %2 = load %struct.MyType*, %struct.MyType** %1, align 8
  ret %struct.MyType* %2
}
{% endhighlight %}


Here, the translation rules are a little bit more interesting, but they still follow the same pattern. The results are summarized by the following table:

| Return type | Actual return | Additional parameter | Observation |
| --- | --- | --- | --- |
| `MyType` | `void` | `MyType*` | Return through an output param |
| `MyType&` | `MyType*` | N/A | |
| `MyType*` | `MyType*` | N/A | |
| `MyType&&` | `MyType*` | N/A | |

The function that returns a value is transformed into a function that returns `void` and takes the location of where to write the resulting value as a pointer to the function -- there is an implicit (`sret`) parameter to the underlying function.

Again, ignoring the optimization for small POD types, the compiler will not use value-types for returning values from a function. There are pointers everywhere.

If we were to make a function that returns a smaller POD type (i.e., `int`), then the compiler will actually generate a proper value return for it. But again, we can consider that as an optimization.


## But why not values?

For non-trivial user-defined types, the compiler will not translate into values. Everything is a pointer down at generated code level. The language and the compiler just maintain the **illusion** of value types. Why can't it just use values?

Besides reasons that involve performance, there is also a semantic reason for which a general type **needs** to be translated as pointer in all these contexts.

An object can store inside it (directly or indirectly) a pointer to itself. And there is no good way for the compiler to determine this.

Let me give an example, to clarify things. Let us consider the example of a double-linked list; we ignore genericity, and consider that the list stores simple `int`s. The data structures would look like the following:

{% highlight C++ %}
struct Node {
    int val;
    Node* next;
    Node* prev;
};
struct List {
    Node sentinel;
};
{% endhighlight %}

For implementing this `List`, we have the following conventions:
* we keep a sentinel (node that is not actually part of the list)
* sentinel's `next` will point to the first element in the list
* sentinel's `prev` will point to the last element in the list
* we don't want to make a heap allocation for the sentinel, so we store it directly in the `List` structure

There are actually many implementations that follow the same idea. So far so good.

Let us consider now how do we represent the empty list:
* it obviously has a sentinel (as it's embedded in the `List` object)
* `sentinel->next == &sentinel` -- the absence of the first element is marked with the sentinel
* `sentinel->prev == &sentinel` -- the absence of the last element is marked with the sentinel

Now, because `sentinel` is the only member of `List`, the address of a `List` object will be equal to the address of its sentinel. If the list is empty, the sentinel will point to itself (twice), and therefore will also point to the `List` object.

Therefore, in our empty list example, all `List` objects will contain two pointers to themselves. The same is true for non-empty lists, but there are multiple levels of indirections.

The compiler cannot figure out whether a `List` object will point at itself or not without following the logic of how the `List` objects are constructed and used.

In general, for an object that has a user-defined constructor, the compiler may assume that the object may actually be containing its own address. Therefore it cannot simply copy the value bits from one place to the other.

This is why, for most of the types, the compiler needs to maintain pointers everywhere when translating to machine code.


## Brief conclusions and some unanswered questions

C++ has a complex type system. It distinguishes between values, references and pointers. Also from glvalues, rvalues, lvalues, xvalues, and prvalues. There are also const and non-const types, and also volatile and non-volatile types. All this complexity boils down to just a few options in the generated code.

The most important conclusion, is that the compiler generates almost everywhere pointer types for everything that the user writes. For non-trivial objects the compiler needs to guarantee that the object identity always remain in sync. In most cases, **the compiler just provides the illusion of value semantics**.

Considering all these, the following questions can be used to further explore this topic:
* is the C++ type system more complex than it needs to be? could it have been simpler?
* is the distinction between `T` and `const T&` really needed? Can't the compiler just use the same semantics for both? (i.e., avoid copying, and simplifying syntax)
* do we really need both references and pointers?


Keep truthing!
