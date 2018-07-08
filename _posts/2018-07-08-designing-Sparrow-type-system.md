---
layout: post
title:  "Designing Sparrow's type system"
date:   2018-07-08
banner_image: notebook-pen.jpg
image: images/posts/notebook-pen.jpg
description: "How would one design the type system of a static programming language? Here is an example. Applied to the Sparrow programming language."
tags: [Sparrow, type system, efficiency, naturalness, immutability]
---

The type system is the core of a statically-typed language. It also needs to be central to Sparrow. --- [Sparrow](https://github.com/Sparrow-lang/sparrow) is a general-purpose programming language that aims to integrate efficiency, flexibility and naturalness. It is flexible enough to allow the user to write efficient code in a method that does not compromise a natural manner. It features both low-level access code constructs and high-level features. One of the central features of the language is hyper-metaprogramming; this allows using complex data structures and algorithms at compile-time, as one typically does at run-time.

But, unfortunately, the current type system in Sparrow is not powerful/safe enough. We need to improve it. This post is a high-level proposal to improve the type system in Sparrow.

<!--more-->

## The problem with the current type system

Currently Sparrow has a relatively simple type system. Data types can be created by using two different kinds of types (not counting arrays):
- proper data types, with zero or more references
- lvalue types

An expression like `Int` will denote a proper data type with 0 references. A reference to `Int` will be expressed by `@Int`. One can have a higher number of references associated with a type, by applying multiple times the `@` operator: `@ @Int` (2 references), `@ @ @Int` (3 references), and so on. (Note that in the above examples the spaces between `@` are needed, so that the lexer will not interpret one operator `@@` instead of applying twice the `@` operator.)

If one has a variable declaration `var a: Int`, then `a` would be a *lvalue* of the data type `Int`. This is a way for telling the compiler that, in essence, the type of `a` will be `Int`, but you have some kind of special hidden reference for it. Lvalue types will be equivalent to a proper data type with a single reference.

That is it in a nutshell. No *const* types, no rvalue references, no pointers (other than references), no other complications. This generates some simple type rules for Sparrow, but also some of the consequences are sub-optimal.

First, Sparrow cannot properly guarantee immutability of programs. For example, the following program would compile fine:

{% highlight Sparrow %}
fun addOne(n: @Int)
    n += 1

addOne(1)
{% endhighlight %}

Pause for a moment and guess what this program does at runtime.

Because some types can be heavy, Sparrow had to allow the user to pass values by reference (similar to C++'s `const T&`). But because there is no `const` in Sparrow, everything is a simple reference. Therefore, Sparrow needs to allow the conversion between value types (i.e., `1`) and reference types. Sparrow creates a small object (lvalue), initializes it with the proper value, and transforms it into a reference. That is how the above code worked.

The problem is that, most of the generic code would have to use pass by reference to avoid potential large copying of the object. Therefore, Sparrow code tend to have a lot of references to the parameters. Not only it does require more typing, but it is also not safe.

Because of the simple type system, safety is actually worse than indicated above. Too many implicit conversions would make the compiler easily accept bad code that just leads to crashes and debugging problems. In some areas like pointer management, the compiler should force the user to be more explicit with the intent of the program.


## Goals

We attempt here to sketch a redesign of the Sparrow type system. But, in order to do so, we need to have some clear goals. These are:
1. have proper support for immutability; if possible immutability by default
2. allow safe *const reference* passing for input parameters, preferably, without the user needing to type too much
3. simpler and safer rules for lifetime of objects passed as parameters
4. support move semantics
5. support forwarding pass semantics

For the first two points, the motivating example would be:
{% highlight sparrow %}
fun dontCopyArguments(vec: Int Vector) {...}
{% endhighlight %}

The parameter for this function would need to be constant for the whole function (i.e., user cannot modify the input vector), and also the vector should be passed by const reference to avoid the inefficiency of copying the elements of the vector. In other words, should be similar to C++'s:
{% highlight C++ %}
void dontCopyArguments(const vector<int>& vec) {...}
{% endhighlight %}

### A note on immutability

*Why immutability by default?* some may ask. Most of the imperative programming languages will use mutability by default. It feels like Sparrow would be moving more towards functional programming, and we know that this is not as efficient as imperative programming. So why this choice?

First, immutability by default doesn't really mean immutability everywhere. We are not trying to make Sparrow a pure functional programming language. One can still use mutability for implementing efficient algorithms.

Then, we argue that, if immutability is possible, it should be preferred over mutability. It's far easier to reason about immutable state, and far safer. If, for example, one looks at a given length and finds that it equals 1 meter, it is not possible to look at the same length and find that it has a different value. Similarly, circles don't grow or shrink, geometric shapes do not move. See Sean Parent's inspiring talk [Inheritance is the base class of evil](https://www.youtube.com/watch?v=bIhUE5uUFOA), for a better insight into this.

Finally, immutability works far better with multi-threading processing. As Kevlin Henney likes to point out (see for example [Thinking Outside the Synchronization Quadrant](https://www.youtube.com/watch?v=2yXtZ8x7TXw)), threading problems appear only when we use mutable and shared state. If the data is not mutable, or if the data is not shared, then we don't have any problems (3 out of 4 quadrants are safe w.r.t threading).

## Design of the type system

In the following sections we will consider all the places in which types are used in Sparrow, and attempt to deduce the optimal traits of the types in those scenarios. We would consider the following aspects:
* read-only vs write-only vs read-write
* ownership and lifetime

We will also look at what the implementation would look like (in LLVM code, or equivalent C++ code). With all these, we can form a complete picture of the interactions of the types inside the Sparrow language.

### Function parameters -- part 1

Parameters to a function can serve multiple roles:
* input parameters
* output parameters
* input/output parameters
* consume (sink) parameters
* forward parameters

First, let's simply remove the output parameters. Any output of a function should be handled as a return value. It should not be a parameter. That leaves us with 4 kinds of parameters.

#### Input parameters

By far, the most frequent role of a parameter is for input. Then, it makes sense to focus on input parameters. Also, input parameters is probably the place in which the programmer will explicitly write type names. This needs to be the simplest possible way of defining types (while being coherent with the rest of the type system).

Then, it follows that, according to the first two goals, the following function parameter:
{% highlight Sparrow %}
fun f(param: MyType) {...}
{% endhighlight %}
should be read-only. The lifetime of the parameter should be guaranteed to be at least the for the duration of the function.

This can be translated as `const MyType&` would be translated in C++, with the option to be transfered by value whenever possible. According to our [previous post]({{page.previous.url}}), C++ by-value parameters are also translated the same way in the function signature. But here the semantics differ: if C++ ensures that a new copy is made to the object (i.e., copy constructor called), Sparrow should not require that.

**Discussion.** This is divergence from the C++ tradition; why did we want this? The reason is simple: in its most basic form an input parameter does not care if the source object was copied or not; it just has a value that can be read from. Also, from C++ we can see that the cases in which input parameters are taken by const-reference are more frequent than the ones in which they are taken by (copy) value.

#### Input/output parameters

Input/out parameters need to be read-write, with lifetime larger than the function scope.

If input parameters are like C++'s const-references, input-output parameters need to be similar to non-const references. In other words, they are a "mutable" version of the input parameters. For this reason, we will invent a *mutability operator*; we'll denote it by a `!` (bang). Here is an example:

{% highlight Sparrow %}
fun f(inOut: !MyType) {...}
{% endhighlight %}


The key point here is that `!` should be taken to represent a reference; it represents *mutability*.

In terms of implementation, this will be similar to C++'s `MyType&`, and in LLVM terms it will be a simple pointer.


Other parameter roles are treated later on.

#### Mutability and immutability

With our discussion about input and input/parameters we covered the distinction between mutable and immutable values.

Immutability is achieved by default for function parameters, but mutability is achieved by adding the `!` operator. For symmetry, we also add an immutability operator: `const(T)`. Therefore we have the following mutability scenarios:

| Operator | Meaning |
| --- | --- |
| none | read-only value; same as `const` |
| `const` | read-only value |
| `!` | read-write value |



### Function return values

Function return values have the following traits: read-only (for the caller), lifetime controlled by the caller.

Syntactically, it needs to have a very simple form:
{% highlight Sparrow %}
fun f(): MyType
    return MyType()
{% endhighlight %}

In terms of implementation, we would have something similar to C++17's guaranteed copy elision (see [proposal](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/p0135r0.html) and [more detailed explanation](https://akrzemi1.wordpress.com/2018/05/16/rvalues-redefined/)). That is, the caller creates a variable on its stack, and passes the pointer to the called function, which will fill it. With this schema, we won't be copying objects.

In LLVM, the function declaration would look like:
{% highlight LLVM %}
define void @f(%MyType* noalias sret) #0 {...}
{% endhighlight %}


So far, we assumed that the returned value is not mutable. But the user can declare it as mutable `fun f(): !MyType`. This should have no effect on the function. It can however have an effect on the caller side (for example, if we pass the result of the function to an in/out parameter of another function) -- but that is something that we expect to have no practical use.


### Variables

Variables need to be either read-only or read-write, and the lifetime associated with the variable should be determined by the scope in which the variable is defined. The important distinction here is between read-only and read-write. To be consistent, it should have a syntax similar to the input & input/output parameters.

For that, we propose the following syntax:
{% highlight Sparrow %}
val readOnlyVal: MyType = f()
val readOnlyVal2: MyType const = f()    // same as above
val readWriteVal: !MyType = f()
{% endhighlight %}

Again, the `!` operator means mutability.

We use the keyword `val` from *value* to introduce these entities. They are actually named values. We should probably change our vocabulary to use the term *value* or *named value* instead of the term *variable*. The emphasis moves from looking at something that constantly changes (it *varies*) to something that gives a name to a value

In both cases, we give a name for the value returned by function `f()`. In the first case, after initializing `readOnlyVal`, we cannot mutate it. It's just like declaring a `const MyType` variable in C++.

In the second case, we can mutate `readWriteVal` after initializing it.

Please note that, in both cases, at the end of the scope the appropriate destructor will be called (assuming we have one). This destructor will receive under the hood a mutable version of the value.

In the first case, the type can be omitted when it can be deduced from the context:
{% highlight Sparrow %}
val readOnlyVal = f()
{% endhighlight %}

This expresses even better the idea that `readOnlyVal` is the value returned by `f()`.

Because the second case is encountered often too, we would probably have an alternative syntax too:
{% highlight Sparrow %}
var readWriteVal1: !MyType = f()
var readWriteVal2: MyType = f()
var readWriteVal3 = f()
{% endhighlight %}

This makes it explicit that we are dealing with variables -- things that can change their value during their lifetimes. All the three values defined above will have the type `!MyType` (assuming `f` is defined as `fun f: MyType` or `fun f: !MyType`).

The rules for deducing the type of a value when the type is not specified (and there is an initializer) should be very simple:
* for a `val` declaration, the value will have the exact type as the initializer
* for a `var` declaration, the value will have the type of the initializer, made mutable

For example:
{% highlight Sparrow %}
fun cf: MyType {...}
fun mf: !MyType {...}

val a = cf() // MyType
val b = mf() // !MyType
var c = cf() // !MyType
var d = mf() // !MyType
{% endhighlight %}

The two forms of values (regular and mutable) are similar to const and non-const variables in C++. In LLVM they would both be translated similar to `%1 = alloca %MyType, align 4`, where the type of `%1` would be `%MyType*` -- the mutability aspect is lost.

### Datatype fields

Datatype fields should be similar to value declarations. There should be read-only or read-write fields, and the lifetime of the fields should be exactly the same as the lifetime of the parent datatype object.

Depending on the mutability of fields, we should have multiple forms of fields:

{% highlight Sparrow %}
datatype CompoundData
    regularField: MyType
    constField: MyType const
    mutableField: !MyType
{% endhighlight %}

At this point it is important for us to not assume that `regularField` is immutable. What we propose is *transitive mutability*. The mutability aspect of `regularField` is inherited for the mutability of the parent object. The following example should clarify this:

{% highlight Sparrow %}
fun regularFun(x: CompoundData, val: MyType)
    x.regularField = val    // ERROR
    x.constField = val      // ERROR; always immutable
    x.mutableField = val    // OK; always mutable

fun immutableFun(x: CompoundData const, val: MyType)
    x.regularField = val    // ERROR; parent is immutable
    x.constField = val      // ERROR; always immutable
    x.mutableField = val    // OK; always mutable

fun mutableFun(x: !CompoundData, val: MyType)
    x.regularField = val    // OK; parent is mutable
    x.constField = val      // ERROR; always immutable
    x.mutableField = val    // OK; always mutable
{% endhighlight %}

One can see that in the context of datatypes the `!` type operator behaves like the `mutable` type specifier in C++. Similarly, `const` in Sparrow behaves like `const` in C++. But here, the absence of these two represent *transitive mutability*.

None of the three variants mean references in the context of fields.

Reflecting at all we've discussed so far, this schema is simple and coherent. The absence of `!` means regular value, while its presence means that the value can be mutated. `const` is used to enforce immutability.


### Storing references

So far, we haven't introduced any possibility of references and pointers. That is, of course, something that we need to address.

We need to have read-only, and read-write references. The lifetime of the referred object can be completely independent of the lifetime of the object containing the reference. Unlike all the other places in which types appear, here we can also have null values (or not). These three aspects of references are completely perpendicular.

The most important aspect of references is the lifetime. From C++'s experience, we can have three main categories of lifetimes for references (in C++ we call them pointers):
* unique references -- in C++, `std::unique_ptr<MyType>`
* shared references -- in C++, `std::shared_ptr<MyType>`
* weak references, or unconstrained references -- in C++, `std::weak_ptr<MyType>` or `MyType*`

We want to make Sparrow implement these categories as well. Therefore, we should have: `UniqueRef(MyType)`, `SharedRef(MyType)`, `WeakRef(MyType)` and `UnconstrainedRef(MyType)`. All these should be (or behave like) generic datatypes.

If the language defines means of implementing `UnconstrainedRef(T)`, then all the other references can be implemented on top of this. The important consequence is that one can define all these reference types inside the language, and extend the available categories at any time.

As stated above, mutability aspect is independent of these categories. The rules of mutability for references is similar to the mutability rules for other types:





The rules for mutability are the same as above:
* if `const` is used, then the referred data is read-only
* if `!` is used, then the referred data is read-write
* if none of the two is used, then we inherit the mutability from the reference value -- *transitive mutability*

That is, if we are declaring reference values, we have the following equivalence with C++:

| Sparrow construct | C++ equivalent |
| --- | --- |
| `val v: UnconstrainedRef(MyType)` | `const MyType* const` |
| `val v: UnconstrainedRef(!MyType)` | `MyType* const` |
| `val v: !UnconstrainedRef(MyType)` | `const MyType*` |
| `val v: !UnconstrainedRef(!MyType)` | `MyType*` |
| `var v: UnconstrainedRef(MyType)` | `MyType*` |
| `var v: UnconstrainedRef(!MyType)` | `MyType*` |
| `var v: !UnconstrainedRef(MyType)` | `MyType*` |
| `var v: !UnconstrainedRef(!MyType)` | `MyType*` |
| `var v: UnconstrainedRef(MyType const)` | `const MyType*` |
| `var v: UnconstrainedRef(MyType) const` | `const MyType* const` |
| `var v: UnconstrainedRef(MyType const) const` | `const MyType* const` |

These tables shows how the mutability rules should apply in Sparrow, and how they are consistent across different usage scenarios.


### More function parameter roles

So far, we've discussed the basic forms of parameter kinds, and introduced the read-only vs read-write distinction. With this distinction we were able to build a simple system for handling value and datatype declarations, and also references.

We now discuss the last two parameter roles, and the implications that these have.

#### Consume (sink) parameters and temporary values

Consume (sink) parameters would facilitate *move* of values from one place to another. C++ example:

{% highlight C++ %}
void sinkString(std::string str) {
    otherString = std::move(str);
}
void sinkString2(std::string&& str) {
    otherString = str;
}
{% endhighlight %}

In order to support this functionality in Sparrow, we need an equivalent of r-value references. Something to represent values with temporary lifetime. Let's denote that by `tmp(T)`. With this type, the above C++ example can be translated in Sparrow into:

{% highlight Sparrow %}
fun sinkStr(str: String tmp)
    otherString = str
{% endhighlight %}

Essentially, `tmp` is an operator that would be equivalent to `&&` in C++. In order to make this work, we need the language to create implicit conversions between temporary value and `tmp` types. Example:

{% highlight Sparrow %}
val i = 1
fun genInt = 4

val x1: Int tmp = i;        // ERROR: 'i' is not a temporary value
val x2: Int tmp = genInt(); // OK
val x3: Int tmp = 10;       // OK
{% endhighlight %}

In the above example, all three expressions after `=` should have the same type: `Int`; yet the compiler needs to distinguish between them when dealing with `tmp` types. Just like C++ deals with value categories.

Please note that the accent falls in this section on the consume parameters, and not on temporary values. There should not be no distinction between temporary values and non-temporary ones if we would not want to sink some values into some functions. When, in C++, we think about moving one value into some other place, we think about passing that value as a sink parameter to some function -- be that a move constructor or a move assignment operator.

Here, the lifetime aspect is the most important one. A temporary value is assumed to be destroyed immediately after it's passed as a sink parameter. Therefore, inside the function we can *move* content out of it, or apply transformation that will destruct the object.

There are two ways in which this can be implemented:
* a destructor needs to be called after the value is sinked -- the lifetime of the original value remains the same
* a destructor doesn't need to be called if the value is sinked -- the lifetime of the original value ends when it sinks into a function

If the second option can be implemented, it is probably more efficient than the first one. At this point, we leave that decision open.

Regardless of which option is implemented, it is safe to assume that, at least conceptually, the lifetime of the source value ends at the *sink-in* point. At the start of the function, the original value enters into a limbo (temporary) phase; at the end of the function call, the original object is assumed to be deprived of its actual meaning (depending on the implementation, calling a destructor after sink-in may or may not happen).


The mutability aspect is also interesting. On one hand, we are required to be able to *move out* parts of the value, so clearly the value needs to be mutable. But then, most of the temporary objects are immutable. To solve this problem, we assume that the *sink-in* operation is similar to a destructor: it can be called even for immutable objects.

As the reader may have guessed, this is a more complex topic, that would probably require its own individual post.

#### Forward parameters

So far, so good. We have all the right abstractions to construct efficient programs using simple constructs. Especially when generics are not heavily used.

Things get more complicated when generics are heavily used. Or when one attempts to write highly-reusable components.

For example, let us write an `identity` generic function:

{% highlight Sparrow %}
fun identity(x: AnyType) = x
{% endhighlight %}

We would want the returning type of the function to be exactly the type of the value given as argument when instantiating the generic. In other words:

{% highlight Sparrow %}
val c = 10
var v = 20
identity(c)     // Int const == Int
identity(v)     // !Int
identity(10)    // Int tmp
{% endhighlight %}

This is a requirement that we will impose on the type deduction system of generics.


### Type constructors and type expressions

So far, we introduced several operators to allow us to deal with types: `const`, `!`, `tmp` and, why not, the reference types (denoted below as `ref`). They are functions that take types as arguments and return other types.

It is interesting to see how they should combine with each other. The following table attempts to define the combination rules:

| Type constructor | Meaning |
| --- | --- |
| `T` | the type `T` --  defaults to `const(T)`; implements transitive mutability |
| `const(T)` | `T` is read-only |
| `!(T)` | `T` is read-write |
| `tmp(T)` | `T` is temporary |
| `ref(T)` | a reference to a value of type `T` |
| `const(const(T))` | `const(T)` |
| `const(!T)` | `const(T)` |
| `const(tmp(T))` | `const(T)` |
| `const(ref(T))` | usually similar to C++'s `const T* const` |
| `!(const(T))` | `const(T)` |
| `!(!(T))` | `!(T)` |
| `!(tmp(T))` | `tmp(T)` |
| `!(ref(T))` | usually similar to C++'s `const T*` |
| `tmp(const(T))` | `tmp(T)` |
| `tmp(!(T))` | `tmp(T)` |
| `tmp(tmp(T))` | `tmp(T)` |
| `tmp(ref(T))` | usually similar to C++'s `const T*&&` |

In some cases, the operators should be reduced, but not always. In the cases where transitive mutability kicks in, we showed the default/typical case.

The types produced by the type constructors are types themselves. That means they can participate in type expressions. For example, if we have an operator `fun *(t1, t2: Type)` to create a pair of types, we can apply it to our type constructors: `!Int * !Bool` -- this creates a pair between a mutable integer and a mutable boolean.

### Implicit conversions

In order for this type system to work, Sparrow needs to have in place some implicit conversions between the types. The following table shows the needed rules:

| Conversion | Explanation |
| --- | --- |
| `T` &#8594; `const(T)` | Everything is convertible to immutable value |
| `const(T)` &#8594; `T` | By default, `T` is immutable |
| `!T` &#8594; `T` | Mutable converts to immutable |
| `!T` &#8594; `const(T)` | Mutable converts to immutable |
| `tmp(T)` &#8594; `T` | Temporary converts to everything |
| `tmp(T)` &#8594; `const(T)` | Temporary converts to everything |
| `tmp(T)` &#8594; `!T` | Temporary also means mutable |


All these conversions are transitive.


### Using the type with generics

In the session about forward parameters we already hinted on how generics need to play with this new type system. The deduction algorithm should use the type of the argument passed in. Other than that, there is nothing special. It should work with both function and datatype generics.

Example:
{% highlight Sparrow %}
datatype Vector(valueType: Type)
    _begin: UnconstrainedRef(valueType)
    _size, _capacity: Int

val v1: Vector(Int)     // _begin: UnconstrainedRef(Int)
val v2: Vector(!Int)    // _begin: UnconstrainedRef(!Int)
val v3: !Vector(Int)    // _begin: UnconstrainedRef(Int)
val v3: !Vector(!Int)   // _begin: UnconstrainedRef(!Int)
{% endhighlight %}

This example also allows us to iterate once more on the transitive mutability principle. Because of this principle, we have the following consequences:
* on `v1` we cannot change `_begin` or any element pointed by it
* on `v2` we cannot change `_begin` but we can mutate the elements of the vector
* on `v3` we can mutate both `_begin` and the elements of the vector -- the mutability of `v3` is applied to the elements of the vector as well
* on `v4` we can mutate both `_begin` and the elements of the vector

To make `v3` be able to change `_begin`, but not able to mutate the content of the elements, one should declare it with the type `Vector(Int const)`.

We believe this model is superior to the one from C++, when the immutability is not transitive. It allows one to write safer code, while typing less.

### What we've left out

We only focused on data types, and completely ignored arrays and function types. The type rules for those should be straight forward, if the rules for datatypes are good.

We also left out any discussion about lambda functions. The rules should follow the same rules as with regular functions.

## Evaluation

The tentative type system presented here meets the initial goals. We can safely divide the proposal from this blog post into three main parts:
1. rules for dealing with mutability/immutability
2. rules for references
3. rules for move semantics and forwarding pass semantics

On the first point, the proposal allows dealing with immutability, and moreover makes it the default. Switching between mutability and immutability is easy (most of the time, just adding `!`). The transitive mutability rule, is simple to understand, and allows a safer type system, with less typing.

This is clearly much better than what Sparrow had, and, because of the transitive mutability rule, it seems to be superior to what C++ has.

Related to rules for references, compared with the current rules in Sparrow, the proposed type system is far safer. Yes, we would still allow low-level primitives that one can use to shoot oneself in the foot, but that should be the minority of cases. Also, we make lifetime operations explicit. This would lead to safer code. Not allowing easy syntax for references and pointers seems to be a strength over the C++ system, as it tends to result in safer code.

The rules for move semantics and forwarding pass semantics are new to Sparrow. They are somehow similar to C++, but I would argue that they are slightly simpler. C++ has complex rules for handling r-value references; sometimes `T&&` means r-value reference (for moving temporaries), and sometimes it means forwarding reference (for perfect forwarding). Also, we are sometimes encouraged to use `T&&` for some operations, but are also encouraged to take sink-in parameters by value.

Based on these thee points we can conclude the following:
* the proposal seems to be a strong improvement on what Sparrow currently has
* the proposal seems to generate a type system that is slightly better than C++'s

Now, the disclaimer: Everything I said here is just a simple thought experiment. We need two things to prove the above claims:
* implement these in Sparrow, and make sure they work
* let see if they stand the test of time

With these said, it's time to roll up the sleeves, prepare a lot of coffee and start implementing these into Sparrow. Wish me luck!

## References

There are many articles and talks that have influenced the outcome of this blog post. However, just a few of them stuck into my memory as being directly relevant. I'll try to list them here. Apologies for everything important that I've left out.

* My previous post -- [Beyond the type system]({{page.previous.url}})
* Sean Parent, [Inheritance is the base class of evil](https://www.youtube.com/watch?v=bIhUE5uUFOA)
* Kevlin Henney, [Thinking Outside the Synchronization Quadrant](https://www.youtube.com/watch?v=2yXtZ8x7TXw)
* Richard Smith, [Guaranteed copy elision through simplified value categories](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/p0135r0.html)
* Andrzej Krzemieński, [rvalues redefined](https://akrzemi1.wordpress.com/2018/05/16/rvalues-redefined/)
* Jonathan Müller, [Rethinking pointers](https://www.youtube.com/watch?v=kYiEvVEh6Tw)


{% highlight Sparrow %}
{% endhighlight %}
