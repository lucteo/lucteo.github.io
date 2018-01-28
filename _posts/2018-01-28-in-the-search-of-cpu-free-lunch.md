---
layout: post
title:  "In the search of CPU free lunch; a DOD perspective"
date:   2018-01-28
banner_image: cpu-freelunch.jpg
image: images/posts/cpu-freelunch.jpg
description: "Turning the data-oriented design question around: for a perfectly aligned memory access, can we piggyback more CPU instructions to be executed? It seems the answer is yes."
tags: [data-oriented-design, efficiency, exploration]
---

In the [last post](2018-01-04-Data-Oriented-Design-and-efficiency.html) we shown how important data manipulation can be in the efficiency of programs. More specifically, we shown that in some cases, the data access is much slower than the instructions we run on the CPU side. The last post was a show-case for data-oriented design (DOD).

But we can turn the problem upside down, and ask ourselves: assuming data layout is optimal, can we add more CPU instructions to be used while waiting for memory? The answer appears to be yes, within some limits.

This is not a show-case of data-oriented design; rather it's an exploration inside the realm of DOD, to investigate some finer points of DOD. And, compared to last post, we venture outside of game industry to emphasize the point that DOD techniques can be applied in other industries as well.

<!--more-->

## Are there free CPU cycles? A first estimation

The major conclusions of the last post were based on the fact that on the modern processors the data access rate is slower than the rate we can execute instructions on the CPU. This calls for the table with the numbers that every programmer should know:

Operation | Time
--------- | ----:
1 cycle in a 2GHz processor          |         0.5 ns
L1 cache reference                   |         0.5 ns
Branch mispredict                    |           5 ns
L2 cache reference                   |           7 ns
Mutex lock/unlock                    |          25 ns
Main memory reference                |         100 ns
Compress 1K bytes w/ cheap algorithm |       3,000 ns
Send 2K bytes over 1 Gbps network    |      20,000 ns
Read 1 MB sequentially from memory   |     250,000 ns
Round trip within same datacenter    |     500,000 ns
Disk seek                            |  10,000,000 ns
Read 1 MB sequentially from disk     |  20,000,000 ns
Send packet CA->Netherlands->CA      | 150,000,000 ns

See [original article by Jeff Dean](https://static.googleusercontent.com/media/research.google.com/en//people/jeff/Stanford-DL-Nov-2010.pdf), and an up-to-date [version](https://people.eecs.berkeley.edu/%7Ercs/research/interactive_latency.html) of these numbers.

Typical CPU instructions take below 10 ns. A main memory access takes in the order of 100 ns. There is a gap here that we can potentially exploit. However, please note that it may not be as simple as it sounds; it's not like we can completely separate memory access from the CPU instructions. Also, at this scale, it is hard to separate throughput from latency.

Let us start measuring this.

## A simple example

Consider a vector of integers with a lot of values (I've tested with 1,000,000 values). Let's write a loop to increment all the values in this vector:

{% highlight C++ %}
for (int i = 0; i < values.size(); i++)
    values[i]++;
{% endhighlight %}

From a DOD point of view, we are ok: we are using the most compact data structure for our problem, and we are not doing more work than we need.

But now, as a test, let's increment only part of these values. Instead of incrementing `i` by `1`, let's add a variable _step_:

{% highlight C++ %}
for (int i = 0; i < values.size(); i+=step)
    values[i]++;
{% endhighlight %}

Plotting the time needed to execute this (repeating this 1000 times) while varying the step yields the following chart:

<center><div id="skipTraverse_plot" style="height: 400px;"></div></center>

We observe 3 main areas: the first part, in which the time drops significantly, then an almost plateau phase, in which performance seems to not be affected by decreasing `step`, and finally a phase in which the time decreases again with `step`.

These three phases can be seen better if we would also plot the "expected time" for each of this; we compute this expected time as:

$$ expectedTime(step) = \frac{t(0)}{step} $$

Plotting this along the measured time, would yield:

<center><div id="skipTraverse_plot2" style="height: 400px;"></div></center>


The plateau phase seems to be while `step` is between 4 and 16. On my machine that would correspond to a stride between 16 and 64 bytes. Does it surprise you to know that the cache line on my machine is 64 bytes? Once again, memory access seems to be the limiting factor here. It doesn't quite matter if we are making 4 increments or 16 increments per cache line; we are mostly paying for the cache line access.

Now that we know that 16 is a special step for our machine, let's also plot the expected-time computed starting from the 16th point:

$$ expectedTime_{16}(step) = \frac{t(16) * 16}{step} $$

<center><div id="skipTraverse_plot3" style="height: 400px;"></div></center>

It seems that in the third stage, the time decreases roughly proportional with the step. That makes sense if we stop to think about it. Once we passed the cache line boundary, we are not bringing into memory all pages; we will update only one element for each page that we load, so, increasing the step, we will change the stride of cache lines that we are loaded.

From this analysis we can draw the following conclusion:

<div class="box info">
    <p><b>Conclusion so far</b></p>
    <p>Within the boundary of a page line, the number of integer increments that we have does not quite affect performance (if we go after the initial 4 increments). We can do 16 increments in the same time we can do 4 increments.</p>
</div>


## Playing on the plateau

Let us play some more on the plateau part of our measurements (steps between 4 and 16). Let's artificially add more CPU instructions. We will replace the increment with a multiplication, then with two multiplications, three and four multiplications, then we will also add a `fastSqrt` transformation. For each of our 5 new cases, the instruction inside the loop will look like the following:

{% highlight C++ %}
// instead of values[i]++;
// case 1:
values[i] = values[i] * values[i];
// case 2:
values[i] = values[i] * values[i] * values[i];
// case 3:
values[i] = values[i] * values[i] * values[i] * values[i];
// case 4:
values[i] = values[i] * values[i] * values[i] * values[i] * values[i];
// case 5:
values[i] = fastSqrt(values[i]);
{% endhighlight %}

In the last case, instead of using standard `sqrtf` we used a function that appears to be faster, at the expense of some precision. The reason for choosing this method is to prevent the compiler for transforming the instruction into a SSE-specific instruction and thus adding translation overhead. The function we are using is:
{% highlight C++ %}
float fastSqrt(float x) {
    union {
        int32_t i;
        float x;
    } u;
    u.x = x;
    u.i = (1 << 29) + (u.i >> 1) - (1 << 22);
    return u.x;
}
{% endhighlight %}


Measuring the performance for these 5 new cases, will yield the following results:

<center><div id="skipTraverseAlts_plot" style="height: 400px;"></div></center>

Just by looking at this graph, we conclude the following:
- for low `step` values, there is no space for us to squeeze more instructions
- for higher `step` values (but still in the realm of a cache line), there is place for us to insert extra CPU instructions
- the _mul1_ and _mul2_ cases match pretty well the original line

So, there is some slack on the instruction side, but that slack is very limited: just a few multiplications.

For the purpose of this exposition, we are not looking at the generated assembly, and how does the compiler behave with this piece of code. However, please note that it's not just a pure separation between CPU instructions and data accesses. After all, we are also doing stores with the results of our injected instructions. In other words, it's hard to increase the throughput of CPU instructions without also affecting the latency.

<div class="box info">
    <p><b>Conclusion so far</b></p>
    <p>It is tough to increase the throughput of CPU instructions.</p>
</div>

## A real-world example

Let's now turn to an example inspired by a real-life project. And this time, it's inspired from the automotive industry, not the gaming industry.

Let's assume that we have 2 components in our application: one that is responsible for management of some data, and one that uses data provided by the first component for some business processes.

<center>{% include_relative diagrams/DOD_cpufreelunch_components.svg %}</center>

The business logic part needs to be very efficient. So the data that is passed to it needs to be in the right format for using it. For the purpose of our example, let's assume the data is just an array of orientation vectors:
{% highlight C++ %}
struct Vec3 {
    double x;
    double y;
    double z;
};
{% endhighlight %}

This is a 3D vector with a length of 1.

To make the problem slightly more interesting, let's assume that Data manager needs to always concatenate two arrays before passing this to business logic. The process will look like:

{% highlight C++ %}
void prepareData(const vector<Vec3>& s1, const vector<Vec3>& s2,
        vector<Vec3>& out) {
    int sz1 = int(s1.size());
    int sz2 = int(s2.size());
    int idxDst = 0;
    for (int i = 0; i < sz1; i++, idxDst++)
        out[idxDst] = s1[i];
    for (int i = 0; i < sz2; i++, idxDst++)
        out[idxDst] = s2[i];
}
{% endhighlight %}

Let's take this as the baseline, and explore various alternatives starting with this process.

One may try to use `memcpy` here, and it will work faster than these manually written loops, but let's exclude this from our repertoire (imagine that the real-world problem has certain twists that will make `memcpy` not usable).

Doing a data analysis, there is nothing wrong with our data layout. We are using arrays and we are not wasting memory; both inputs and the output are properly compacted.

Please remember that the business logic is critical in terms of performance, so whatever we do, we cannot change the format of the output data. Thus, changing `double` to `float` for the output is not an option.

By the way we set up the problem, the only thing that we can do is to add more CPU instructions here. Let us explore some possibilities of adding useful stuff in this transformation. Let's try to add some basic geometry transformations:

{% highlight C++ %}
Vec3 negateXY(Vec3 v) { return Vec3{-v.x, -v.y, v.z}; }
Vec3 rotateZ30(Vec3 v) {
    constexpr float cos_theta = 0.866025f;
    constexpr float sin_theta = 0.5f;
    return Vec3{v.x * cos_theta - v.y * sin_theta, v.x * sin_theta + v.y * cos_theta, v.z};
}
void prepareData_neg(const vector<Vec3>& s1, const vector<Vec3>& s2,
        vector<Vec3>& out) {
    int sz1 = int(s1.size());
    int sz2 = int(s2.size());
    int idxDst = 0;
    for (int i = 0; i < sz1; i++, idxDst++)
        out[idxDst] = negateXY(s1[i]);
    for (int i = 0; i < sz2; i++, idxDst++)
        out[idxDst] = negateXY(s2[i]);
}
// similar for prepareData_rotate()
{% endhighlight %}

For both transformation we are making a few (floating point) arithmetic operations, and no extra memory operation.

Measuring the performance of these transformations with respect to our baseline, we get:

<center><div id="trasform_plot" style="height: 300px"></div></center>

That is quite good. Not only we added more operations to be performed while concatenating the data, but we also **improved performance**.

The reasons for the improved performance are accidental; the compiler has more hints to go through a SSE based translation, and that will perform better on my machine. This performance difference depends on the compiler and the machine. For the purpose of this post, we won't enter into details about this.

<div class="box info">
    <p><b>Conclusion</b></p>
    <p>Sometimes, adding a small of CPU instructions will make your program faster.</p>
</div>

Let us build on that.

We said that, for performance reasons are are not allowed to change the output data structure. But, we can still change the input structure. The reason for such a change would be to better optimize the data manager component (this was actually the use case that inspired this post).

There are several assumptions that we can make to help in our problem:
- precision is not that important; we are able to sacrifice a few percents in the direction vectors
- the Z component of the vector is always positive (we are always pointing upwards, instead of downwards)

With these assumptions, we can represent the vector into a much more compact structure:
{% highlight C++ %}
struct Vec3Compact {
    float x;
    float y;

    Vec3Compact() {}
    Vec3Compact(float xx, float yy) : x{xx} , y{yy} {}
    Vec3Compact(Vec3 v) : x{(float)v.x}, y{(float)v.y} {}

    explicit operator Vec3() const {
        return Vec3{x, y, 1.0 - fastSqrt(x * x + y * y)};
    }
};
{% endhighlight %}

First thing to notice is that we dropped some of the precision, by moving from `double` to `float`. The second thing, is that we got rid of the Z component. We can do this because a direction vector is normalized, so that:

$$ x^2+y^2+z^2 = 1 $$

and thus:

$$ z = \pm (1 - \sqrt{x^2+y^2}) $$

One of our assumption was that Z is always positive, so we ignored the plus/minus variation. If we wouldn't had this assumption we would have to add an extra bit of information, and add some more CPU instruction for the translations between `Vec3` and `Vec3Compact`.

In terms of memory utilization, this structure has a 66% size reduction compared with the original one.

With this, we can change the input arrays to be of `Vec3Compact` instead of `Vec3`, and the performance of our `prepareData` concatenation would be:

<center><div id="trasform_plot2" style="height: 300px"></div></center>

We achieve even more performance improvement. A simple concatenation of two `Vec3Compact` arrays and converting it into an array of `Vec3` objects would be **about 23% faster** than the case in which we just concatenate two `Vec3` arrays. Please note that in this process we reduced the data size for the input vectors, so in consequence we have fewer memory misses on the input vectors.

Also, as a side effect, the data manager component, having smaller data structures, will probably benefit from improved performance. For example, reading the data from disk is faster if we are reading 66% less data.

For reference, here is the code that does the concatenation of arrays of compact vectors:

{% highlight C++ %}
void concat_compact(
        const vector<Vec3Compact>& s1, const vector<Vec3Compact>& s2,
        vector<Vec3>& out) {
    int sz1 = int(s1.size());
    int sz2 = int(s2.size());
    int idxDst = 0;
    for (int i = 0; i < sz1; i++, idxDst++)
        out[idxDst] = (Vec3)s1[i];
    for (int i = 0; i < sz2; i++, idxDst++)
        out[idxDst] = (Vec3)s2[i];
}
{% endhighlight %}


Adding negate and rotate transformation on this compact method yields some interesting results:

<center><div id="trasform_plot3" style="height: 300px;"></div></center>

The negate variant will perform slightly worse than the base compact version, but still better than the non-compact version. So, once again, we can piggyback more CPU instructions on a data traversal without affecting the performance too much.

The rotate version however produces worse results even than the original non-compact version. In this case, we are adding slightly more instructions. Trying to skip some of the computations will yield better results, but still not extremely good -- see the "c rotate-skip" bar. In this case, we only applied the transformation once every 8 vectors; that is, we apply the transformation twice per cache line.

## Source code and measurements machine

As the last time, all the code is available [on GitHub](https://github.com/lucteo/DOD_samples/tree/master/cpufreelunch).

The performance numbers shown here were obtained on my MacBook Pro Retina (late 2013), 2GHz Intel Core i7 (Haswell/Crystalwell), 8 GB Ram, macOS High Sierra. The cache line is 64 bytes, L1 is 32K, L2 is 256K and L3 cache is 6 MB.

## Conclusions

This is an exploratory post. Instead of proving a point, it explores various aspects related to the existence of a CPU free lunch in the presence of compact data structures, as required by Data-Oriented Design. Even though there is no strong point that we can make, there are still several conclusions that we can draw from this exploratory work:
- **there is a CPU free lunch**; we can add more CPU instructions without degrading performance
- adding more CPU instructions can sometimes lead to improved performance; if this is coupled with a reduction of data size
- the range in which we can add more CPU instructions without affecting performance is small
- compiler optimizations pay an important role in these type of operations, and can affect performance significantly

We've proven that there is a CPU free lunch, but it appears one cannot feast on it. What else is left to do? We shall further explore this technique for other applications.

Keep truthing!



<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/modules/series-label.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>

<script type="text/javascript">
var myColors = ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4'];
Highcharts.theme = { colors: myColors };
Highcharts.setOptions(Highcharts.theme);


var times = [3023,1612,1265,1186,1198,1020,1131,1089,1048,1081,1080,1088,1071,1067,1077,1077,1010,958,928,907,855,812,784,749,726,690,684,661,631,610,599,602,554,540,525,515,511,545,484,463,466,436,429,430,415,423,409,384,395,379,385,364,365,351,351,352,379,331,330,311,324,305,303,322,298,294,282,288,288,261,269,265,263,264,251,249,249,236,246,231,242,233,221,225,215,191,164,169,174,169,164,161,154,155,149,156,148,154,136,127];
var alternatives = [
  [1160,1123,1106,1082,1095,1094,1090,1087,1084,1083,1079,1058,1051],
  [1312,1171,1130,1127,1121,1088,1086,1083,1080,1093,1063,1094,1064],
  [1280,1166,1137,1136,1117,1068,1020,1114,1124,1097,1066,1053,1044],
  [1551,1336,1201,1173,1149,1115,1063,1094,1099,1059,1063,1064,1055],
  [1927,1637,1489,1335,1275,1246,1173,1107,1116,1111,1086,1111,1071]
]

var legend_defaults = { layout: 'vertical', align: 'right', verticalAlign: 'middle' };
var responsive_defaults = {
  rules: [{
    condition: { maxWidth: 500 },
    chartOptions: { legend: { layout: 'horizontal', align: 'center', verticalAlign: 'bottom' } }
  }]
};

function _getExpectedVal(startStep=1) {
  var res = [];
  var startIdx = startStep-1;
  for ( var step=1; step<startStep; step++ ) {
    res.push(null);
  }
  for ( var step=startStep; step<=times.length; step++ ) {
    res.push(times[startIdx] * startStep / step )
  }
  return res;
}
function _fillSkipTraverseDetails(opts) {
  opts.yAxis = { title: { text: 'time' }, min: 0 },
  opts.xAxis = { title: { text: 'step' }, plotBands: [{color: '#ffff0077', from: 4, to: 16}]},
  opts.responsive = responsive_defaults;
  opts.plotOptions = { series: { pointStart: 1 } };
  if ( !opts.legend ) {
    opts.legend = legend_defaults;
  }
  return opts;
}
Highcharts.chart('skipTraverse_plot', _fillSkipTraverseDetails({
  title: { text: 'Skip-traverse performance'},
  series: [{ name: 'time', data: times}],
  legend: 'none',
}));
Highcharts.chart('skipTraverse_plot2', _fillSkipTraverseDetails({
  title: { text: 'Skip-traverse performance vs expected time'},
  series: [
    { name: 'time', data: times},
    { name: 'expectedTime', data: _getExpectedVal(), dashStyle: 'dash'}
  ],
}));
Highcharts.chart('skipTraverse_plot3', _fillSkipTraverseDetails({
  title: { text: 'time vs expected time vs expected time 16'},
  series: [
    { name: 'time', data: times},
    { name: 'expectedTime', data: _getExpectedVal(), dashStyle: 'shortdot'},
    { name: 'expectedTime16', data: _getExpectedVal(16), dashStyle: 'shortdot'}
  ],
}));
Highcharts.chart('skipTraverseAlts_plot', {
  title: { text: 'Adding more instructions'},
  yAxis: { title: { text: 'time' }, min: 0 },
  xAxis: { title: { text: 'step' } },
  plotOptions: { series: { pointStart: 4 } },
  legend: legend_defaults,
  series: [
    { name: 'original', data: times.slice(4, 17)},
    { name: 'mul1', data: alternatives[0]},
    { name: 'mul2', data: alternatives[1]},
    { name: 'mul3', data: alternatives[2]},
    { name: 'mul4', data: alternatives[3]},
    { name: 'fastSqrt', data: alternatives[4]},
  ],
  responsive: responsive_defaults
});

var transData = [
  ['baseline', 891],
  ['negate', 744],
  ['rotate', 757],
  ['compact', 652],
  ['c negate', 683],
  ['c rotate', 1058],
  ['c rotate-skip', 756],
];
function _fillTransformDetails(opts) {
  opts.chart = { type: 'column' };
  opts.xAxis = { type: 'category' };
  opts.yAxis = { min: 0, title: { text: 'time (ms)' } };
  opts.legend = { enabled: false };
  opts.responsive = responsive_defaults;
  return opts;
}
Highcharts.chart('trasform_plot', _fillTransformDetails({
  title: { text: 'Performance of data transformation' },
  colors: [myColors[0], myColors[1], myColors[1]],
  plotOptions: { column: { colorByPoint: true } },
  series: [{name: 'time (ms)', data: transData.slice(0, 3)}]
}));
Highcharts.chart('trasform_plot2', _fillTransformDetails({
  title: { text: 'Performance of compacted method' },
  colors: [myColors[0], 'lightgray', 'lightgray', myColors[1]],
  plotOptions: { column: { colorByPoint: true } },
  series: [{name: 'time (ms)', data: transData.slice(0, 4)}]
}));
Highcharts.chart('trasform_plot3', _fillTransformDetails({
  title: { text: 'Performance of compacted + transformations' },
  colors: [myColors[0], 'lightgray', 'lightgray', myColors[0], myColors[1], myColors[1], myColors[1]],
  plotOptions: { column: { colorByPoint: true } },
  series: [{name: 'time (ms)', data: transData}]
}));
</script>
