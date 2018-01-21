---
layout: post
title:  "Data-Oriented Design and efficiency"
date:   2018-01-04
banner_image: connections.jpg
image: images/posts/connections.jpg
description: Is Data-Oriented Design worth considering? Can it help us deliver better performance of our software? I argue for a big YES to both questions.
tags: [data-oriented-design, efficiency]
---

[Data-Oriented Design](http://en.wikipedia.org/wiki/Data-oriented_design) (DOD) is an approach of solving computing problems that require efficiency with an emphasis on the data. It was made popular by [Mike Acton](http://www.macton.ninja) with his highly acclaimed talk _Data-Oriented Design and C++_ at CppCon2014. If you are a programmer and you haven't seen the video yet, please do yourself a service and watch it (embedded below).

Over the course of time, I started to believe more and more in this approach. But a belief is just a belief, so in accordance with the goals of this blog, I need to move it towards true-belief and then to truth. This post is about adding evidence to support Data-Oriented Design.

<!--more-->

## What is Data-Oriented Design?

A few words here may not catch the essence of DOD, so please watch the video:
<iframe width="560" height="315" src="https://www.youtube.com/embed/rX0ItVEVjHc" frameborder="0" gesture="media" allow="encrypted-media" allowfullscreen></iframe>

For the sake of completeness, I'll also mention a few key points from Mike Acton's talk:
* program’s purpose = **transform data**
* understand data → understand the problem
* different data → different problem
* hardware platform understanding → understand cost of problem

These should be contrasted with the _main lies of software development_:
* software is a platform
* code to be designed around the model of the world
* code is more important than data

> Solving problems you probably don't have creates more problems that you definitely do <cite>Mike Acton</cite>


## Applicability of Data-Oriented Design

After seeing the talk, it's really important to frame the context in which DOD is applicable. Is it applicable to everybody?, is it applicable to all kinds of problems?, etc. If DOD is not generally applicable, then it is probably irrelevant to us.


We can divide DOD applicability into several layers:
1. it only applies to what Mike Acton is doing in his day-to-day job
2. it only applies to the game industry for their per-frame performance constraints
3. it only applies to the software that has high-performance constraints (regardless of industry)
4. it applies to all software, both for efficiency reasons and for modifiability reasons

In this post I'll argue for something between points 2 and 3. I'm using an example inspired by the game industry, but the problem is generic enough that it can apply to other domains. In future posts I'll make it clear that DOD can successfully meet the demands of point 3, and hopefully, at some point I'll also manage to prove that DOD is also good for modifiability reasons.

By no means I would claim that DOD is a general solution that needs to be applied in every context. That would be an over-generalization, that would make even Mike Acton shiver at its thought. Programming means solving the problem with the appropriate tools, and like every tool DOD has its strengths and weaknesses. For example, you don't want to think about cache misses when adding just two numbers.

## The problem to be solved

It's always fun to build something graphical, so we will build some graphic application with OpenGL. Let's assume that we have a 2D world formed of 10 million objects, which we represent as dots. The world size is 300,000 x 300,000 pixels (or whatever measurements we are using), and we only can see 800 x 800 out of it at a given time. For simplicity, we are only looking at the top-left part of this world.

The objects that we have in our world, will move each frame. Each object will have a velocity vector (pointing in different directions), and we will rotate all the velocities of all the objects each frame. Because of the simple change that we are using, each object will effectively rotate around an imaginary point defined by the initial position and the velocity vector.

At the start of the application we randomly generate the positions of these objects and their velocities. When rendered, the scene will look something like:
![The problem we are solving]({{ "/images/posts/DOD_game_goal.jpg" | absolute_url }})

Please note the following:
* we are viewing only a small part of the world, so as a consequence we are viewing a small number of objects
* due to randomness, we don't know which objects we are viewing
* objects will enter and exit the view frame

# A first attempt to solve the problem

Let's start coding. The core part of our problem can be implemented as:
{% highlight C++ %}
class IGameObject {
public:
    virtual ~IGameObject() {}
    virtual void advance(RotMatrix velocityRotation) = 0;
    virtual void draw() const = 0;
};

class GameObject : public IGameObject {
    Vec2 pos;
    Vec2 velocity;
    char name[32];
    Model* model;
    // ... other members ...
    float someAccumulator;

public:
    GameObject(float px, float py, float vx, float vy)
        : pos{ px, py }
        , velocity{ vx, vy }
        , name{ "dot object" }
        , model{ nullptr }
        , someAccumulator{ 0.0f }
    {
    }

    void advance(RotMatrix velocityRotation)
    {
        Vec2 actualVelocity = rotate(velocityRotation, velocity);
        pos.x += actualVelocity.x;
        pos.y += actualVelocity.y;
    }

    void draw() const
    {
        if (pos.x < g_viewSize && pos.y < g_viewSize)
            drawPoint(pos);
    }
};

class World {
    vector<IGameObject*> objects;

public:
    void generateRandom()
    {
        objects.reserve(g_numPoints);
        for (int i = 0; i < g_numPoints; i++) {
            // Create an object with random position and velocity
            double px = randBetween(0.0f, g_worldSize);
            double py = randBetween(0.0f, g_worldSize);
            double vx = randBetween(-g_maxVelocity, g_maxVelocity);
            double vy = randBetween(-g_maxVelocity, g_maxVelocity);
            IGameObject* obj = nullptr;
            if ( time(NULL) > 100 )
                obj = new GameObject(px, py, vx, vy);
            objects.push_back(obj);
        }
    }
    void advance(RotMatrix velocityRotation)
    {
        for (int i = 0; i < objects.size(); i++)
            objects[i]->advance(velocityRotation);
    }
    void draw() const
    {
        for (int i = 0; i < g_numPoints; i++)
            objects[i]->draw();
    }
};
{% endhighlight %}

Every game object will model the `IGameObject` interface. It will know how to update itself (using the `advance` method), and `draw` itself. For our problem the update consists in multiplying the velocity vector with a simple 2D rotation matrix. A concrete `GameObject` will contain the position, velocity and some other data members that are not used in this part of the code (other parts of our program can use them).

The `World` class, as its name suggests, models our world of objects. It is able to generate random objects, it is able to update and to draw them.


<details>
<summary>The rest of the code (click to expand):</summary>
{% highlight C++ %}
#include <math.h>
#include <vector>

#include <GLUT/glut.h>
#include <OpenGL/gl.h>
#include <OpenGL/glu.h>

using namespace std;

static const int g_numPoints = 10 * 1000 * 1000;

static const float g_worldSize = 300 * 1000.0f;
static const int g_viewSize = 800;
static const float g_maxVelocity = 3.0f;

namespace Util
{
    struct Vec2 {
        float x;
        float y;

        Vec2() : x(0.0f), y(0.0f) {}
        Vec2(float xx, float yy) : x(xx), y(yy) {}
    };

    float randBetween(float minVal, float maxVal) {
        return minVal + (maxVal - minVal) * (static_cast<float>(rand()) / static_cast<float>(RAND_MAX));
    }

    struct RotMatrix {
        float cos_theta;
        float sin_theta;
    };

    RotMatrix getRotMatrix(float angle) {
        return RotMatrix{ cos(angle), sin(angle) };
    }

    Vec2 rotate(RotMatrix mat, Vec2 vec) {
        return Vec2(vec.x * mat.cos_theta - vec.y * mat.sin_theta,
                    vec.x * mat.sin_theta + vec.y * mat.cos_theta);
    }

    void drawPoint(Vec2 pt) {
        if ( pt.x < g_viewSize && pt.y < g_viewSize )
            glVertex2f(pt.x * 2.0f / g_viewSize - 1.0f, pt.y * 2.0f / g_viewSize - 1.0f);
    }

    class Model {
    };
}
using namespace Util;

// Previous code goes here

World g_world;

void displayOneFrame() {
    // First advance the world
    // Always rotate the velocities, for a nice effect
    static float rotAngle = 0.0f;
    rotAngle += 0.01;
    g_world.advance(getRotMatrix(rotAngle));

    // Now draw the points

    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    glPointSize(4.0f);

    glBegin(GL_POINTS);
    glColor3f(1.0f, 0.9f, 0.9f);

    // The actual draw
    g_world.draw();

    glEnd();
    glFlush();

    // Calculate the frames per second
    static int frame = 0;
    static int curTime = 0;
    static int lastSecTime = 0;
    frame++;
    curTime = glutGet(GLUT_ELAPSED_TIME);
    if (curTime - lastSecTime > 1000) {
        static char title[256];
        float fps = frame * 1000.0 / (curTime - lastSecTime);
        int frameTime = int(1000.0f / fps);
        sprintf(title, "GameObject Test - FPS: %4.2f - avg frameTime: %d ms", fps, frameTime);
        glutSetWindowTitle(title);
        lastSecTime = curTime;
        frame = 0;
    }
}

int main(int argc, char** argv) {
    srand(1);

    // Initialize the world with random data
    g_world.generateRandom();

    glutInit(&argc, argv);
    glutInitWindowSize(g_viewSize, g_viewSize);
    glutCreateWindow("GameObject Test");
    glutDisplayFunc(displayOneFrame);
    glutIdleFunc(displayOneFrame);
    glutMainLoop();
    return 0;
}
{% endhighlight %}
</details>

All the code, including other versions detailed below, can be found [on GitHub](https://github.com/lucteo/DOD_samples/tree/master/gameobject).

## Assessing performance

**Quick question** to you, the reader: how fast do you think that will will go? How many milliseconds does it take to update the world and draw it?

In my test code, I've displayed both the average FPS (frame-per-second), and also the average frame-time (they are both calculated on a per-second basis).

On my machine (MacBook Pro Retina, 15-inch, late 2013, macOS High Sierra) I have the following results: **around 182-187 ms per frame**, which represents a FPS of about 5.5-5.3. The results oscillate a bit, they depend on what else is running on my machine, so let's just say that it takes **180 ms per frame** -- makes it easier to reason about.

For something that has animations into it, 5 FPS is pretty bad.

Let's look at what the code does. Each frame we call `advance` and then `draw` on the world. The relevant code is shown again below:

{% highlight C++ %}
struct RotMatrix {
    float cos_theta;
    float sin_theta;
};

void World::advance(RotMatrix velocityRotation) {
    for (int i = 0; i < objects.size(); i++)
        objects[i]->advance(velocityRotation);
}
void GameObject::advance(RotMatrix velocityRotation) {
    Vec2 actualVelocity = rotate(velocityRotation, velocity);
    pos.x += actualVelocity.x;
    pos.y += actualVelocity.y;
}
Vec2 rotate(RotMatrix mat, Vec2 vec) {
    return Vec2(vec.x * mat.cos_theta - vec.y * mat.sin_theta,
                vec.x * mat.sin_theta + vec.y * mat.cos_theta);
}

void World::draw() const {
    for (int i = 0; i < g_numPoints; i++)
        objects[i]->draw();
}
void GameObject::draw() const {
    if (pos.x < g_viewSize && pos.y < g_viewSize)
        drawPoint(pos);
}
void drawPoint(Vec2 pt) {
    if ( pt.x < g_viewSize && pt.y < g_viewSize )
        glVertex2f(pt.x * 2.0f / g_viewSize - 1.0f, pt.y * 2.0f / g_viewSize - 1.0f);
}
{% endhighlight %}

We compute the rotation matrix only once, we call `advance` and `draw` only once per frame. In the `advance` call we are making some mathematical operations on our game objects, and in the `draw` part, we draw the game objects, if they are visible.

**QUESTION**: Why is this so slow? (yes, it can be faster)


Probably, the vast majority of programmers who look at this will answer that the drawing part is slower than the update. After all, the update performs just a few mathematical operations, while the drawing part invokes OpenGL. We know that OpenGL has some complex transformation pipelines that involve some shaders and of course, going back and forth between main CPU and GPU. Clear, right?

Let's put that to the test. Let's comment out the `advance` function call over the world. In this case we would not update the objects after we've generate them, so we are drawing a static scene (over and over again).

On my machine, removing the top-level `advance` will produce a frame-time of 73-80 ms (FPS 12-13). Making the test from the other point of view, removing `draw` will produce a frame-time of 113-115. There is some other job done per frame, like clearing the frame, flushing OpenGL, but apparently the vast majority of time is distributed among the two functions.

Please note that, if we add these frame-times we obtain slightly more than the original time. That is ok. The program does slightly different things, we have caching effects, etc. The rough division between those two functions will be:

<center><div id="piechart-split" style="height: 250px;"></div></center>

The `advance` represents the biggest performance problem that we have.

Let's see how we can improve this.

<div class="box info">
    <p><b>Advice</b></p>
    <p>Data organization often affects by a large margin the performance of algorithms. Look at the data first.</p>
</div>

## Take 1: kill inheritance

Let's look at our `World` class. It contains a vector of `IGameObject` pointers. That means that our game objects are theoretically scattered through the memory (in this example we are constructing the elements one after another, so they will tend to be close to each-other). It also means that whenever we are iterating over the objects, we are jumping through different parts of memory. Our memory access is not linear.

Let's fix this. We can kill the inheritance and instead make the `World` class contain a directly vector of `GameObject` values:
{% highlight C++ %}
class World {
    vector<GameObject> objects;
...
{% endhighlight %}

Except changing a few places (mainly replacing `->` with `.`), the rest of the code remains the same.

Running the new version of the code produces a frame-time of around 144 ms. That is **about 20% better** than before.

If we comment out the top-level `advance` and `draw` calls we obtain frame-times of about 53 ms and 92 ms, respectively. We improved both parts of the program. This makes sense, because in both cases we would iterate over the game objects the same way.

But we can do much more.


## Grouping object data appropriately

We can continue our data analysis at the `GameObject` level. Looking at the definition of the class, and how the rest of the program uses various members, we can split the class in two parts:
* hot data: `pos` and `velocity`
* cold data: `name`, `model`, ...

The cold data is there, but it's actually not used during our time consuming algorithms. It is just hurting our memory loads. Each time we load a `GameObject` into memory we also load some data that we don't use and throw away.

On my machine, the `GameObject` class occupies 72 bytes, and a `Vec2` only 8 bytes. So, each time we load this object into memory, we are using 16 bytes out of 72 bytes; that is only 22%.

**We are throwing away about 78% of the data that we load from memory.**

Let's do something about it. We can split the `GameObject` into multiple parts, so that we don't use the cold data if we don't need it.

The only way to do this is to actually transform the _array-of-structures_ in the `World` class into a _structure of arrays_. The following code shows how:

{% highlight C++ %}
class OtherGameObjectData {
    char name[32];
    Model* model;
    // ... other members ...
    float someAccumulator;

public:
    OtherGameObjectData()
        : name{ "unknown obj" }
        , model{ nullptr }
        , someAccumulator{ 0.0f }
    {}
};

class World {
    vector<Vec2> positions;
    vector<Vec2> velocities;
    vector<OtherGameObjectData> otherData;
...
{% endhighlight %}

We are still keeping the same information in our `World` class, but now it's organized differently. The logical entity of a game object is now split across three different vectors. One must always remember this, and make sure that the access into these vectors is properly synchronized. Apparently harder to maintain, but there are techniques which will ease a lot the complexity of this.

With the data organization changed, the algorithms need to slightly change too:

{% highlight C++ %}
void World::advance(RotMatrix velocityRot) {
    for (int i = 0; i < g_numPoints; i++) {
        Vec2 actualVelocity = rotate(velocityRot, velocities[i]);
        positions[i].x += actualVelocity.x;
        positions[i].y += actualVelocity.y;
    }
}
void World::draw() const {
    for (int i = 0; i < g_numPoints; i++)
        drawPoint(positions[i]);
}
{% endhighlight %}

There is no such thing as `GameObject` class anymore, so the `advance` and `draw` functions of the `World` class will do the job directly. Which is fine, as it is simpler to deal with positions and velocities directly. Please note that we are not using the `otherData` corresponding to the game objects anymore.

**QUESTION**: Would you expect this to be faster or slower? By how much?

Running the new code on my machine produces a frame-time of around 32 ms. That is 4.5 times faster than the previous version. We are now running in 22% of the time we previously run. Does this number sound familiar? Check above for how much memory we were actually utilizing from `GameObject` class.

What can we learn from this?

<div class="box info">
    <p><b>Advice</b></p>
    <p>Prefer structure-of-arrays instead of array-of-structures in performance critical parts.</p>
</div>

<div class="box info">
    <p><b>Advice</b></p>
    <p>Group together only data that is used together. Separate data that is not.</p>
</div>

## Separating the wheat from the chaff

So far, we achieved a great performance boost by doing some simple transformations to the data structures, without changing the core algorithms.

But we can do more, in the light of the same "_separate data that is not_" principle. The key observation here is that we are viewing only a small number of objects at a time, but we process all the objects. If we are viewing only 100 objects at once, then we are processing 9,999,900 without any real benefit.

The problem is that, by updating the positions of the objects each frame, we never know what objects are visible and which are not. The way to overcome this obstacle is to note that there is a limit to how much an object can travel. That means that if an object is very far away, it cannot instantly appear in our view. We can therefore divide the objects in two big classes:
* objects which are in our view, or are close to our view
* objects that are far away from our view

With this distinction in mind, we will partition our data, so that objects that are close to our view will be on the first entries of our vectors, and those who are far away, at the back our vectors. This can be done by the following code:

{% highlight C++ %}
// Do a partial sort: bring all the elements close the view in front;
// push all the others to the end. Make endOfNear indicate the
// boundary between them
void arrangeData() {
    endOfNear = 0;
    for ( int i=0; i < g_numPoints; i++ ) {
        if (isNearView(positions[i])) {
            int destIdx = endOfNear++;
            swap(positions[i], positions[destIdx]);
            swap(velocities[i], velocities[destIdx]);
            swap(otherData[i], otherData[destIdx]);
        }
    }
}
bool isNearView(Vec2 pos) {
    return pos.x < 4*g_viewSize && pos.y < 4*g_viewSize;
}
{% endhighlight %}

The `isNearView` function may be more complex in real-life, but it works ok for our purposes. The `arrangeData` will walk over all the game objects and partially sort them based on our nearness criteria. In our example it will be called only once, after creating the game objects.

With this partition, the `draw` function can only check the _near_ game objects:
{% highlight C++ %}
void World::draw() const {
    for (int i = 0; i < endOfNear; i++)
        drawPoint(positions[i]);
}
{% endhighlight %}

The `advance` function can follow a similar pattern:
{% highlight C++ %}
void World::advance(RotMatrix velocityRot) {
    // Advance only the near-view objects
    for (int i = 0; i < endOfNear; i++) {
        Vec2 actualVelocity = rotate(velocityRot, velocities[i]);
        positions[i].x += actualVelocity.x;
        positions[i].y += actualVelocity.y;
    }
    // What about the far objects?
}
{% endhighlight %}

The question is what to do with the far objects? Should we never update them? It seems like cheating. Typically that would be unacceptable. For example, in a game you would also want to update the monsters that are not in view. But, if the game objects are not visible, do we need to do it every frame? Can't we update them only once in a while?

Let us construct on that idea. We will update all the far game objects only once in 100 frames. However, when we update them, we need to make sure that the update effect is cumulative. For our system, the resulting position will be:

$$
\begin{align*}
    pos_{final} &= pos_0 + v*rot_1 + v*rot_2 + v*rot_3 + ... \\
    &= pos_0 + v*(rot_1 + rot_2 + ...) \\
    &= pos_0 + v*\sum_i{rot_i} \\
\end{align*}
$$

With this in mind, we can complete the `advance` function with:
{% highlight C++ %}
    static const int farUpdateFrequency = 100;
    rotMatSum.cos_theta += velocityRot.cos_theta;
    rotMatSum.sin_theta += velocityRot.sin_theta;
    if ( ++updateSkipCount == farUpdateFrequency ) {
        for (int i = endOfNear; i < g_numPoints; i++) {
            Vec2 actualVelocity = rotate(rotMatSum, velocities[i]);
            positions[i].x += actualVelocity.x;
            positions[i].y += actualVelocity.y;
        }
        // Start over
        rotMatSum.cos_theta = 0.0f;
        rotMatSum.sin_theta = 0.0f;
    }
{% endhighlight %}

So, in the end we are doing the same transformation for all the game objects, but for far objects we perform the update less frequently.

When I run this on my machine I constantly obtain a frame-time of 16 ms. That is because my system limits the frame-rate to 60, so I cannot easily go faster than this. If I remove the `glEnd` and `glFlush` calls, my program reports a frame-time of 0 ms. It's so damn fast, that my simple test cannot reliably measure it.

## More complicated scenarios

I tried to keep the example simple, to make the point of Data-Oriented Design. However, in real-life things can be slightly more complex. I briefly give here some extension points to our discussion.

In my example, I never updated the division between the _near_ and _far_ objects; as the view never moved, I didn't have to. If we want to update this division, we can also do it less frequently. It's an O(n) operation, so we can guess its impact on performance.

In our example, we've made a coarse distinction between _near_ and _far_. One can imagine more complex scenarios in which some objects need to be updated more frequently than others. Even in our example, we've updated (and tried to draw) more objects than are actually visible. We can define a hierarchy of objects based on nearness. In effect, different objects may be updated at different frequencies.

We can also imagine scenarios in which we drop from correctness. Do we really need to ensure 100% correctness in updating objects that are far far away?

And the list can go on.

## Conclusions

We started with a system that has performance problems and which appears to be too simple to let us improve it.

However, by looking at how data is organized, we could make simple transformations to the code to improve the performance dramatically. Below I list a comparison between different methods tried here:


<center><div id="chart" style="height: 250px;"></div></center>

Pretty impressive, right?

I've shown here that Data-Oriented Design can successfully be applied to increase performance of software by a large margin. Although the example was inspired from the game industry, it can be applied to other domains as well.

All the code is available [on GitHub](https://github.com/lucteo/DOD_samples/tree/master/gameobject).



In future posts I will show how it is possible to apply Data-Oriented Design to problems completely outside of gaming industry.

Because some of the readers may argue that we lose modifiability by employing DOD, I will also try to attack how DOD can be used without making the code less maintainable. Moreover, I'll also try to show how a DOD approach can increase modifiability.

Keep truthing!

<script type="text/javascript">
window.onload = function () {
  google.charts.load('current', {'packages':['corechart']});
  google.charts.setOnLoadCallback(drawChartSplit);
  google.charts.setOnLoadCallback(drawChart2);

  function drawChartSplit() {
    var data = google.visualization.arrayToDataTable([
      ['Part', 'time (ms)'],
      ['draw',     73],
      ['advance',  113]
    ]);

    var options = {
      title: 'Rough frame-time split',
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart-split'));

    chart.draw(data, options);
  }
  function drawChart2() {
      var data = google.visualization.arrayToDataTable([
        ['Method', 'Time (ms)'],
        ['OOP classic', 184],
        ['OOP flat', 144],
        ['Split struct', 32],
        ['Split objects', 1]
      ]);

      var materialOptions = {
        chart: {
          title: 'Frame times for different methdos'
        },
        hAxis: {
          title: 'Frame time (ms)',
          minValue: 0,
        },
        vAxis: {
          title: 'Method'
        },
        height: 200,
        width: "100%",
        bars: 'horizontal',
        bar: {groupWidth: "65%"},
        legend: { position: "none" },
      };
      var materialChart = new google.visualization.BarChart(document.getElementById('chart'));
      materialChart.draw(data, materialOptions);
  }
}
</script>

