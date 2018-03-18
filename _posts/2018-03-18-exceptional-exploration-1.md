---
layout: post
title:  "Exceptional exploration (1)"
date:   2018-03-18
banner_image: exception.jpg
image: images/posts/exception.jpg
description: "What are the performance implications of handling errors? How fast is code with exception handling? First part of an exploration on what error handling mechanism should we use."
tags: [C++, efficiency, exceptions, error handling]
---

To use or not to use exceptions? That is the question.

And if you have hoped for a simple answer, this is not the right blog to read. On this blog, finding the truth is always a complex endeavor, it involves a complex mix of perspectives and a variety of interpretations. If you are into truthing, read on.

In this post we would only cover the performance aspects of it. A follow up post should discuss aspects like modifiability (how easy is to write error handling) and appropriateness of using exceptions.

<!--more-->

## Error handling context

You try to read something from a file that is not on disk; or the disk just failed. You try to allocate too much memory. You find yourself into a state that shouldn't happen under normal operating conditions. What do you do? -- This is the main question of error handling.

What can a program do when it encounters an error condition? Here are some of the possible alternatives:
* just crash
* initiate shutdown sequence
* ignore the error and continue execution (possible leading to more errors)
* report 'false' or an error code back to the caller
* throw an exception

The first alternative seems really bad. But there are cases in which you may want to do this -- imagine a server that can easily be restarted without loss of function for the whole farm. The second alternative is a little bit nicer way to do this: instead of crashing, shutdown gracefully.

The third alternative is usually the worst one. That is because most of the time it will corrupt the program (in a way that the users see this), and then eventually crash. Imagine a server-side error that will lead to a crash only after it sends back to the client some private account information of other users.

For the vast majority of cases we have to chose between the latter two options. Either use error codes or use exceptions.

Often the choice between these two alternatives need to take the following into account:
* the frequency of the error condition
* desired efficiency
* naturalness of the program
* interoperability issues

Let's start by analyzing the efficiency concern.

## Test setup

Let's imagine a vector of sequences. Each sequence has between 1 and 20 integers (between 0 and 1024), and there are 10,000 such sequences. Something like:

```
seq[0]:  763 415 736 857 129 602 641 358 417 782 348
seq[1]:  692 730 236 559 1013 352 894
seq[2]:  493 571 714 299 725 386 617
seq[3]:  963 644 19 526 166 618 528 179 316 692 846 666 128 79
seq[4]:  774 130 279 244 202 630 698 132 226 988 969 358 79 421 519 396 654 54
seq[5]:  151 220 112 795 527 312 655 763 913 944 544 951 671 912 610 876 129 25
seq[6]:  708 562 71 4 751 251 893 143 242 707 718 971 505 482
seq[7]:  995 301 951 846 736 863 140 365 872 211 320 31 725 756 49 921 702
seq[8]:  130 134 959 691 693 775 318 450 850
seq[9]:  126 112 934 258 327 325 928 803 55 791 638 265 294 287 830 967 955 493 761 453
seq[10]:  923 813 2 385 271 630
...
seq[9996]:  393 825 265
seq[9997]:  98 1015 327 147 26 238 731 132 388 652 460 726 2
seq[9998]:  339 248 458 562 257 25 414 538 1005 756 949 492 775 767 777 447
seq[9999]:  201 290 244 654 640 506 159 966 761 561 78 605 949 607 575 596 272
```

The main assumption that each sequence **contains at least one integer**.

We can easily average the elements into each sequence (using integer arithmetic only). We would then have a vector of 10,000 numbers. For the sake of our example, let's then average these in a sophisticated way. Let's average these results in groups of 10 elements. We would obtain 1,000 such averages. We would average then again in groups of 10, and again and once more, until we end up with just one result. We've made this complex averaging scheme to implement a recursion with 4 levels  ($$10,000 == 10^4$$).

Here is the C++ code that implements this test algorithm:

{% highlight C++ %}
typedef vector<int> Sequence;

int average(const Sequence& seq) {
    auto sum = accumulate(begin(seq), end(seq), 0);
    return sum / int(seq.size());
}

int multilevel_average(const vector<Sequence>& sequences,
        int start, int level) {
    int stride = pow10(level);
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int idx = start + i * stride;
        int val = level == 0
                ? average(sequences[idx])
                : multilevel_average(sequences, idx, level-1);
        sum += val;
    }
    return sum / 10;
}
{% endhighlight %}

Please note that, because we are using integer average, we cannot simply transform the whole algorithm into a simple average. It would produce a different result.

So far so good. But what if our non-empty sequence assumption doesn't hold? What if some sequences don't have any elements at all? The above code would reach a division by zero, and thus will halt immediately. That is not good. We need some error handling.

## Option 1: ignore any errors

The easiest way to solve this problem is to simply ignore the empty sequences, and assume the average is just 0. Like this:


{% highlight C++ %}
int average_ignore(const Sequence& seq) noexcept {
    if (seq.empty())
        return 0;
    auto sum = accumulate(begin(seq), end(seq), 0);
    return sum / int(seq.size());
}

int multilevel_average_ignore(const vector<Sequence>& sequences,
        int start, int level) noexcept {
    int stride = pow10(level);
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int idx = start + i * stride;
        int val = level == 0
                ? average_ignore(sequences[idx])
                : multilevel_average_ignore(sequences, idx, level-1);
        sum += val;
    }
    return sum / 10;
}
{% endhighlight %}

Please note that this solution is lacking on correctness. One shall not invent numbers and assume they are results of the required computations. What if, for example, zero is not a valid average for the numbers that can be in a sequence?

Even if the solution is not 100% correct, it serves us well as a baseline for our performance measurements.


## Option 2: use return value to indicate failure

Another option is to change the return value to indicate success/failure. For this, we would return the actual value in an output parameter. Something like:


{% highlight C++ %}
bool average_ret(const Sequence& seq, int& res) noexcept {
    if (seq.empty())
        return false;
    auto sum = accumulate(begin(seq), end(seq), 0);
    res = sum / int(seq.size());
    return true;
}

bool multilevel_average_ret(const vector<Sequence>& sequences,
        int start, int level, int& res) noexcept {
    int stride = pow10(level);
    int sum = 0;
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int idx = start + i * stride;
        int val = 0;
        bool ok = level == 0
            ? average_ret(sequences[idx], val)
            : multilevel_average_ret(sequences, idx, level-1, val);
        if (!ok)
            return false;
        sum += val;
    }
    res = sum / 10;
    return true;
}
{% endhighlight %}


Please note that, if any of these functions return false, there is no value stored in output parameter `ret`.

If we encounter any zero-length sequences, we bubble up the error and fail the whole computation. This is ok from a correctness point of view, but for performance measurements, we can't compare it with the previous method -- we are doing far less computations. For this reason, we also look at the following method:

{% highlight C++ %}
bool multilevel_average_ret_ign(const vector<Sequence>& sequences,
        int start, int level, int& res) noexcept {
    int stride = pow10(level);
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int idx = start + i * stride;
        int val = 0;
        bool ok = level == 0
            ? average_ret(sequences[idx], val)
            : multilevel_average_ret_ign(sequences, idx, level-1, val);
        if (ok)
            sum += val;
    }
    res = sum / 10;
    return true;
}
{% endhighlight %}

We are doing the same computation as the first method, and we are also doing some error checking outside of the ```average_ret``` function.

Again, the result of this _ingore_ alternative is different than the one in which we bubble out the error.

## Option 3: Using exceptions

As we are in C++, one of the main alternatives for implementing this is to use exceptions:
{% highlight C++ %}
int average_except(const Sequence& seq) {
    if (seq.empty())
        throw runtime_error("empty sequence");
    auto sum = accumulate(begin(seq), end(seq), 0);
    return sum / int(seq.size());
}

int multilevel_average_except(const vector<Sequence>& sequences,
        int start, int level) {
    int stride = pow10(level);
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int idx = start + i * stride;
        int val = level == 0
            ? average_except(sequences[idx])
            : multilevel_average_except(sequences, idx, level-1);
        sum += val;
    }
    return sum / 10;
}

int multilevel_average_except_ign(const vector<Sequence>& sequences,
        int start, int level) {
    int stride = pow10(level);
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int idx = start + i * stride;
        try {
            int val = level == 0
                ? average_except(sequences[idx])
                : multilevel_average_except_ign(sequences, idx, level-1);
            sum += val;
        } catch (...) {
        }
    }
    return sum / 10;
}
{% endhighlight %}

As with return values option, we have two alternatives: let the error bubble out to the callers, or handle it at the point that we catch it. A correct approach is to go with the first alternative, but for being able to compare performance, we also implemented the second alternative.

## Option 4: Use `Expected<T>`

Another way of handling errors is to use an `Expected<T>` return. This is a technique popularized in the C++ world by Andrei Alexandrescu (see [video](https://channel9.msdn.com/Shows/Going+Deep/C-and-Beyond-2012-Andrei-Alexandrescu-Systematic-Error-Handling-in-C)). It is essentially similar to the [`Maybe`  monad in Haskell](https://en.wikibooks.org/wiki/Haskell/Understanding_monads/Maybe), and [`Option[T]` in Scala](https://www.tutorialspoint.com/scala/scala_options.htm), and even with [Boost::optional](http://www.boost.org/doc/libs/1_66_0/libs/optional/doc/html/index.html). It can store a value of the given type, or not. If it doesn't store a valid value, it will store an exception pointer, indicating the failure to produce the value.

A function that returns an `Expected<T>` either returns a valid object of type T or an exception indicating why that object couldn't be returned.

<details>
<summary>Here is a simple implementation of <code class="highlighter-rouge">Expected&lt;T&gt;</code> (click to expand)</summary>
{% highlight C++ %}
template <typename T>
class Expected {
    union {
        T value_;
        exception_ptr error_;
    };
    bool hasValue_;
    Expected() {}
public:
    Expected(const T& val)
        : value_(val)
        , hasValue_(true) {}
    Expected(T&& val)
        : value_(move(val))
        , hasValue_(true) {}
    Expected(const Expected& other)
        : hasValue_(other.hasValue_) {
        if (hasValue_)
            new (&value_) T(other.value_);
        else
            new (&error_) exception_ptr(other.error_);
    }
    Expected(Expected&& other)
        : hasValue_(other.hasValue_) {
        if (hasValue_)
            new (&value_) T(move(other.value_));
        else
            new (&error_) exception_ptr(move(other.error_));
    }
    ~Expected() {}
    template <typename E>
    static Expected<T> fromException(const E& ex) {
        if (typeid(ex) != typeid(E)) {
            throw invalid_argument("invalid exception type; slicing may occur");
        }
        return fromException(make_exception_ptr(ex));
    }
    static Expected<T> fromException(exception_ptr p) {
        Expected<T> res;
        res.hasValue_ = false;
        new (&res.error_) exception_ptr(move(p));
        return res;
    }
    static Expected<T> fromException() { return fromException(current_exception()); }
    bool valid() const { return likely(hasValue_); }
    T& get() {
        if (unlikely(!hasValue_))
            rethrow_exception(error_);
        return value_;
    }
    const T& get() const {
        if (unlikely(!hasValue_))
            rethrow_exception(error_);
        return value_;
    }
    template <typename E>
    bool hasException() const {
        try {
            if (!hasValue_)
                rethrow_exception(error_);
        } catch (const E& ex) {
            return true;
        } catch (...) {
        }
        return false;
    }
};
{% endhighlight %}
</details>

Using this template class we can perform error handling for our problem in the following way:

{% highlight C++ %}
Expected<int> average_expected(const Sequence& seq) {
    if (seq.empty())
        return Expected<int>::fromException(runtime_error("empty sequence"));
    auto sum = accumulate(begin(seq), end(seq), 0);
    return sum / int(seq.size());
}

int multilevel_average_expected(const vector<Sequence>& sequences,
        int start, int level) {
    int stride = pow10(level);
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int idx = start + i * stride;
        Expected<int> val = level == 0
            ? average_expected(sequences[idx])
            : multilevel_average_expected(sequences, idx, level-1);
        sum += val.get();
    }
    return sum / 10;
}

int multilevel_average_expected_ign(const vector<Sequence>& sequences,
        int start, int level) {
    int stride = pow10(level);
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int idx = start + i * stride;
        Expected<int> val = level == 0
            ? average_expected(sequences[idx])
            : multilevel_average_expected_ign(sequences, idx, level-1);
        if (likely(val.valid()))
            sum += val.get();
    }
    return sum / 10;
}
{% endhighlight %}

Again we have the cases in which we bubble up the error or ignore it the first time we see it.

## Option 5: Use `Expected<T>` with error codes

Similar to the previous option, we can use an `Expected<T>`-like class, but this time, instead of keeping the error as exception pointers, we just keep an integer error code.

You probably hate by now the same code over and over, with just a small variation. That's why this time we just show how to raise this error:

{% highlight C++ %}
    if (seq.empty())
        return ExpectedEC<int>::fromErrorCode(1);
{% endhighlight %}

The rest is extremely similar to the previous code.

## Ok, ok, let's see some numbers

All this long exposition to get some measurements. And here we are; these are the measurements taken for the case in which there are no empty sequences:

<center><div id="bars_0" style="height: 300px"></div></center>

All the values are pretty close. Let's zoom in:

<center><div id="bars_0_zoom" style="height: 300px"></div></center>

In these graphs, we plotted the median time it takes for each alternative (each one having two variants) to average our vector of 10,000 sequences. We also plotted the 95% confidence levels associated with the measurements ($$median \pm 2\sigma$$) as black interval lines. To get these numbers, for each test we repeated the measurements for 7 times.

All the code can be found [on Github](https://github.com/lucteo/error_handling).


For all the practical purposes, **all these methods yield similar results for our problem**. It is not that there are no differences in terms of performance, but they simply are in the range of the error for our problem. If we consider the _Ret_ methods to represent the _true value_, then we can see that this value is within the confidence levels of all the measurements.

### Looking at the differences

Theoretically, the first option (ignore errors) should be the fastest. Equally faster should be the ones that have exceptions and no extra `if` checks. The slowest methods shall be the ones with extra `if` checks. But the results don't quite indicate this. Quite the opposite. Running this test multiple times produces similar results.

For example, the different between the _Ignore_ method and the _Ret_ one, is that the _Ret_ variant has an extra `if`. The _Ret_ alternative should be slower than _Ignore_, but apparently the measurements are not indicating this. We can infer that the compiler optimizes produces different results based on these small hints. For the purpose of this post, we are not going to look at the generated code.

This "compiler optimizer can produce interesting results" point can also be seen in the difference performance between _Ret_ and _RetIgnore_, while the code difference is extremely small.

The somehow interesting point is the difference between the two _Ret_ cases and the four _Expected_ cases at the right. The main difference between these groups is that for the latter group we used `likely` and `unlikely` intrinsics to tell the compiler that certain branches are likely or unlikely. Apparently, this improves efficiency of the code. Actually, according to these numbers, _ExpectedIgn_ seems to be the fastest methods. Just some food for thought.

Using exceptions appears not to be the extremely fast compared to other methods.

Again, despite of these differences, the error between these methods is negligible.


### In the presence of errors

Ok, but what happens if we introduce the possibility of errors? Let us make some sequences empty, and measure again; we test with a number of empty sequences equal to 10 and 100. This means an error rate of 0.1% and of 1% respectively.

First, we cannot measure all the alternatives above; the ones without _ignore_ will finish early, without executing the same number of operations. So we simply exclude them.

The results for the rest of the alternatives are shown below:

<center><div id="lines_graph" style="height: 300px"></div></center>

Here, we see that there is a big difference between the alternatives who use exceptions and the ones that don't use exceptions. If we use exceptions, for 0.1% error probability, the execution time increased by 7-9%. If we have 1% error probability, the execution time goes up by 63-95%. We almost double the execution time!

<div class="box info">
    <p><b>Takeaway</b></p>
    <p>In the presence of errors, exception handling adds a lot of overhead.</p>
</div>

This is why the C++ community recommends that exceptions should be used only for truly exceptional cases. They shall not be used to signal cases that happen often in real-life.

## Very short guide to how exceptions work

If for the other alternatives a C++ programmer can easily understand what are the performance implications, for exceptions it's not that easy. The compiler completely hides the implementation details from the user.

If no exception is thrown, exception handling should not change the semantics of the code. If an exception is thrown, the compiler needs to do two things: find the corresponding `catch` block in which the execution will end up, and perform stack unwinding. The most interesting part is the stack unwinding one. Here, the compiler must call the destructors for all the objects created on the stack between the `throw` point and `catch` point.

The easy way to do this is by injecting instructions for each function to keep track of what objects need to be destroyed. These instructions will of course have a performance impact even if no exceptions are thrown.

Modern compilers use table-based approached for stack unwinding. In a nutshell, no extra code will be added to regular flow, but the compiler will encode in some separate tables how to perform stack unwinding for each particular function. There is no performance penalty for code that doesn't have any exceptions, but there will be a significant cost each time an exception is thrown.

This explains to a certain degree the results we saw here.

For an in-depth discussion on how exceptions work, please see [C++ Exception handling; the gory details of an implementation](https://youtu.be/XpRL7exdFL8). Another inquiry of performance implications of exception handling can be found in [Technical Report on C++ Performance](http://www.open-std.org/jtc1/sc22/wg21/docs/TR18015.pdf).

## Bottom line

Here are some conclusions with respect to performance of error handling:
- when no error appears, all alternative behave the same in practice (assuming our example is representative)
- in theory, the exceptions alternative should be faster than the ones based on error codes for the happy flow (because there are no extra `if`s)
- in the presence of errors, exceptions are slower (both in theory and in practice)
- adding exceptions would increase the size of the executable, because of the extra tables (not measured here)

<div class="box info">
    <p><b>Advice</b></p>
    <p>In general, performance should not be a decisive factor for which error handling alternative should be chosen (assuming the rate of error is close to zero).</p>
</div>

## To be continued

In a follow-up post we shall explore error handling from different perspectives: modifiability and appropriateness.

But before that, allow me to leave you with a partial line of thought:
- for performance reasons it is ok/preferred to use exceptions, but only on the happy flows
- as soon as exceptions occur, exceptions are less optimal
- but if we have no exceptions at all, what's the point of exceptions?

Even though I am sure most of the readers caught the fallacy in the above line of thinking, I am sure the full set of arguments will make you think again.

Join me next time for some more truthing!




<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/modules/series-label.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>

<script type="text/javascript">
var myColors = ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4'];
Highcharts.theme = { colors: myColors };
Highcharts.setOptions(Highcharts.theme);

var responsive_defaults = {
  rules: [{
    condition: { maxWidth: 500 },
    chartOptions: { legend: { layout: 'horizontal', align: 'center', verticalAlign: 'bottom' } }
  }]
};

var labels = ['Ignore', 'Ret', 'RetIgn', 'Except', 'ExceptIgn', 'Expected', 'ExpectedIgn', 'ExpectedEC', 'ExpectedECIgn'];
var barColors = [myColors[0], myColors[1], myColors[1], myColors[2], myColors[2], myColors[3], myColors[3], myColors[4], myColors[4]]
var data_0_med = [
  [210.040],
  [203.749],
  [200.855],
  [202.007],
  [208.397],
  [196.881],
  [195.830],
  [198.201],
  [199.050],
];
var possible_val = 203.749;
var data_0_sd = [
  [5.201],
  [2.916],
  [3.128],
  [3.836],
  [2.683],
  [4.271],
  [4.376],
  [3.997],
  [6.975],
];
function _computeErrorRange(meds, sds) {
  var res = [];
  var startIdx = 0;
  for ( var i=0; i<meds.length; i++ ) {
    var med=parseFloat(meds[i]), sd2=parseFloat(2*sds[i]);
    res.push([med-sd2, med+sd2]);
  }
  return res;
}

function _fillBarsDetails(opts, minY = 0, plotLines=null) {
  opts.chart = { type: 'column', zoomType: 'xy' };
  opts.xAxis = { type: 'category', categories: labels};
  opts.yAxis = { min: minY, title: { text: 'time (us)' }, plotLines: plotLines };
  opts.legend = { enabled: false };
  opts.responsive = responsive_defaults;
  return opts;
}
Highcharts.chart('bars_0', _fillBarsDetails({
  title: { text: 'Performance in the case of no errors' },
  plotOptions: { column: { colorByPoint: true } },
  series: [
    {name: 'median', data: data_0_med, colors: barColors},
    {name: 'confidence levels', data: _computeErrorRange(data_0_med, data_0_sd), type: 'errorbar'}
  ]
}));

Highcharts.chart('bars_0_zoom', _fillBarsDetails({
  title: { text: 'Performance in the case of no errors (zoomed)' },
  plotOptions: { column: { colorByPoint: true } },
  series: [
    {name: 'median', data: data_0_med, colors: barColors},
    {name: 'confidence levels', data: _computeErrorRange(data_0_med, data_0_sd), type: 'errorbar'},
  ]
}, 180, [{color: myColors[1], value: possible_val, dashStyle: 'dash', width: 1}]));

var labelsIgn = ['Ignore', 'RetIgn', 'ExceptIgn', 'ExpectedIgn', 'ExpectedECIgn'];
var data_with_error = [
    [210040, 200855, 208397, 195830, 199050],   // 0
    [204682, 196644, 223392, 213754, 196452],   // 10
    [205719, 200321, 340628, 343619, 197919],   // 100
]

function _fillBarsDetails2(opts) {
  _fillBarsDetails(opts);
  opts.xAxis.categories = labelsIgn;
  opts.legend = { layout: 'vertical', align: 'right', verticalAlign: 'middle' };
  return opts;
}
Highcharts.chart('lines_graph', _fillBarsDetails2({
  title: { text: 'Performance in the presence of errors' },
  // colors: [myColors[0], myColors[1], myColors[1]],
  // plotOptions: { column: { colorByPoint: true } },
  series: [
    {name: '0% errors', data: data_with_error[0]},
    {name: '0.1% errors', data: data_with_error[1]},
    {name: '1% errors', data: data_with_error[2]},
  ]
}));

</script>


