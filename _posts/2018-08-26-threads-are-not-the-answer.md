---
layout: post
title:  "Threads are not the answer"
date:   2018-08-26
banner_image: traffic_jam.jpg
image: images/posts/traffic_jam.jpg
description: "We argue that the thread-oriented approach to concurrency is a bad approach. It has severe modifiability problems, but also performance problems. We should not think in terms of low level primitives."
tags: [concurrency, modifiability, performance]
img_credits:
    - ["https://unsplash.com/photos/8osoVBQWWHc", "Jens Herrndorff", "Traffic jam in Tel Aviv", ""]
---

Whatever the problem is, threads are not the answer. At least, not to most software engineers.

In this post I will attack the traditional way in which we write concurrent applications (mostly in C++, but also in other languages). It's not that concurrency it's bad, it's just we are doing it wrong.

The abstractions that we apply in industry to make our programs concurrent-enabled are wrong. Moreover, it seems that the way this subject is thought in universities is also wrong.

<!--more-->

By the way, whenever I'll say concurrency, I will refer to multithreaded applications that have multiple things running at the same time, in the same process, on the same machine. I'm also implying that these applications are run on multi-core systems.


## The common mindset

In general, whenever we think about concurrency, we think about applications running on multiple threads, doing work in parallel. That means that the application is responsible for creating and managing threads. Then, we all know that we have threading issues; we solve them by using some sort of synchronization mechanisms: mutexes, semaphores, barriers, etc. I call this *thread-and-lock-oriented concurrency*, or simply *thread-oriented concurrency*.

Now, what would be the fundamental concepts that somebody needs to learn to do multitreading in C++? Let's look at [a tutorial](https://www.tutorialspoint.com/cplusplus/cpp_multithreading.htm). It teaches us how to create threads, how to terminate them, and how to join/detach them. The implicit information is that we would put the computations directly on that thread. Most readers will also deduce that for anything that they may want to do in parallel with the rest of the application they would need to create another thread. I believe this model is wrong.

The same site has multithreading tutorials for [Java](https://www.tutorialspoint.com/java/java_multithreading.htm) and [C#](https://www.tutorialspoint.com/csharp/csharp_multithreading.htm). The information is slightly different, but the main takeaways are the same.

The Java tutorial states that: *A multi-threaded program contains two or more parts that can run concurrently and each part can handle a different task at the same time making optimal use of the available resources specially when your computer has multiple CPUs*, and then *Multi-threading extends the idea of multitasking into applications where you can subdivide specific operations within a single application into individual threads*. In other words: if you have multiple things that can be run in parallel, create one thread for each, and your application would optimally use the CPU cores optimally. This is completely wrong.

Maybe these tutorials are not covering the essentials; let us find some other tutorials. Checking out [this](https://www.geeksforgeeks.org/multithreading-in-cpp/), and [this](https://www.tutorialcup.com/cplusplus/multithreading.htm), and [this](https://www.studytonight.com/cpp/multithreading-in-cpp.php) (all for C++), I see the same things over and over again. For Java, I find [this](https://www.javatpoint.com/multithreading-in-java), [this](https://www.guru99.com/multithreading-java.html), [this](http://tutorials.jenkov.com/java-concurrency/index.html), and [this](https://docs.oracle.com/javase/tutorial/essential/concurrency/); again same basic concepts. To be fair, the last two tutorials have sections for executors (which can be much better), but the focus is still on threading low-level primitives.

That is the common belief about writing multi-threaded applications: you create one thread for each thing that you want to run in parallel. If one goes to more advanced expositions of multi-threading, it would find discussions about thread synchronization issues, and different (locking-based) techniques to avoid these problems. The discussion always focuses on low-level threading primitives. That is, in a nutshell, the thread-oriented or thread-and-lock-oriented concurrency.

## The problems with *thread-and-lock-oriented* model

If we take this model to be the essence of multi-threading development, then a transition from single-threaded application to multi-threaded will encounter the following problems (from a modifiability point of view, not considering performance):
1. losing understandability, predictability, determinism
2. not composable
3. needs syncrhonization
4. thread safety problems
5. hard to control

The first problem is seen when developers spend countless hours of debugging, testing and profiling. If one has a single-threaded algorithm/process that is easy to understand, the same algorithm/process transposed into multi-threaded environment would be much harder to understand. Although, to some point, this is a common problem with multi-threaded development, the thread-oriented model makes this worse. People will sometimes use some form of locking to alleviate some of these problems.

The second problem is slightly more abstract, but extremely important. Let's say that module *A* has some properties, and module *B* has some other properties. In a single-threaded environment, putting these modules into the same program will typically not change the properties of these modules. But, if we try to compose them in a multi-threaded environment, we may encounter problems. We have to know the inner details of these modules to check if they work together. We need to check what threads each module uses, what locks they acquire, and more importantly the inner syncrhonization requirements that they have. For example, if *A* holds a lock while calling *B*, and at the same time *B* holds a lock while trying to call *A*, we enter a deadlock.

I want to stress some more on how important this point is. The main method of solving problem in software engineering is through decomposition. This non-composability property of multi-threaded applications (developed with a thread-oriented approach) makes our programming job much harder.

Threads do not operate in isolation. They typically need to cooperate to achieve the goals of the application. This interaction between threads needs to be solved with some kind of *syncrhonization*. Most often, people will use mutexes, semaphores, events and other blocking primitives. Those are really bad; see below for more details.

There is a vast amount of literature describing thread safety issues that commonly appear in multi-threaded programs: deadlocks, livelocks, race conditions, resource starvation, etc. Unfortunately, these problems are typically solved by introducing more locks/waits (directly or indirectly). Again, we will discuss below why this is that bad.

Threads are also hard to control. Once you started a thread with some procedure to be executed, you don't have much control over how the job is done. Some threads are more important than others and need to finish their job faster; some threads consume resources that are needed for more important threads. These resources may be protected by locks (case in which the more important thread will just wait, wasting time); in some other cases, accessing certain resources (i.e., CPU, cache, memory) will indirectly make other threads slower. The mechanisms for enforcing priorities for different jobs are relatively primitive: just assign a priority to the thread, and throttle the less important threads --- this will hardly solve some of the problems.


## Lock the locks away

Locks are extremely bad tools (I'm freely using the term *lock* here to mean any wait-based threading primitive). In a large number of cases, they hurt more than they can help.

The main problem is that they are pure waits; they just introduce delays in the jobs that need to be done. They simply defeat the purpose of having threads to do work in parallel. As Kevlin Henney ([DevTube](https://dev.tube/@kevlinhenney), [Twitter](https://twitter.com/KevlinHenney)) likes to ironically put it, **all computers wait at the same speed** (see [video](https://youtu.be/MS3c9hz0bRg?t=2652)).

We are using threading to improve the amount of things that a program can do, but on the other hand use locks to slow down the processing. We should avoid locks as much as possible.

Another problem with locks is composability. Using locks the wrong way can easily lead to deadlocks. You simply cannot compose different modules if they hold locks when calling external code.

But, probably the biggest problem with locks is the cumulation of waits. One lock can wait on another lock, which waits on another lock, and so on. I have a very good example from a project that I've worked on some time ago. We used a lot of threads (complicated application), and everyone used locks as the only way to solve threading problems. We had a **chain of 11 locks**, each waiting on some other locks. Also, at given times, the application would just **hang for seconds** because most of the important threads were locked, waiting for something else. Using threads was supposed to make our application faster, not slower!

As a summary, let me paraphrase a famous quote:

<div class="box info">
    <p><b>Key point</b></p>
    <p>Mutexes provide <b>exclusive</b> access to <b>evil</b>.</p>
</div>

## Performance: expectation vs reality

The main argument for using threads is the performance: we use more threads, to be able to divide the work to multiple workers, with the expectation that the job will be done faster. Let us put this assumption to the test.

Let's assume that we have a problem that can be split up in units of work, like in the following picture:

<figure class="caption">
    <div style="height: 300px;">{% include_relative diagrams/threads-are-not-the-answer/0_Tasks.svg %}</div>
    <figcaption class="caption-text"><b>Figure 1</b>. An example of work units and their dependencies</figcaption>
</figure>

For the sake of simplicity, we assume that each work unit does the same amount of work (take the same time & resources when executed). The work units will have some predecessors (other work units that need to be done in order to execute it), and some successors (work units that can only start after the current work unit is done). We mark with yellow the work units on the critical path, the ones that are vital for the functioning of the program --- we'll pay special attention to them.

Please note that every process can be divided in such a directed graph of work units. In some cases the graph is known from the start, and in other cases the graph is dynamic --- it is not known in advance, it depends on the inputs of the process. For our example, we assume that this work breakdown is known in advance.

The thread-oriented model of concurrency would make us assign threads to various lines in this graph. The next figure shows how a possible thread assignment might be:

<figure class="caption">
    <div style="height: 300px;">{% include_relative diagrams/threads-are-not-the-answer/1_NaiveAssignment.svg %}</div>
    <figcaption class="caption-text"><b>Figure 2</b>. The thread-oriented model of concurrency: assignment of work units to threads. Each line is a thread.</figcaption>
</figure>

Each horizontal represents one thread, and various work units are assigned to one thread. We chose not to add arrows for consecutive work units on the same thread (except in the case of waiting for a work unit's predecessors to be executed).

The diagram shows what I would call the *expected execution plan*. With the current assignment of work units to threads, we expect the tasks to be executed just like shown in the picture. If the duration of a work unit is 40 ms, we expect the whole processing to be done in 240 ms. That is, instead of waiting 720 ms for all the work units to be executed on a single thread, we wait only 240 ms. We have a speedup of 3 --- it can't be higher, as the dependencies are limiting the amount of parallelism we have.

But, our machines are not ideal. We have limited number of cores. Let's say that on this machine we only have 4 cores available (and nobody else is using these cores). This means, that every time we have more than 4 threads doing meaningful work, they will be fitted into the 4 cores. The cores will jump back and forth between the threads, leaning to a slowdown in the execution of the work units.

For our example, the third column shows 8 work units in parallel; this is the only case in which we execute more than 4 work units in parallel. As a consequence, the execution time for the work units in the third column will double. This is depicted by the following picture:

<figure class="caption">
    <div style="height: 300px;">{% include_relative diagrams/threads-are-not-the-answer/2_LimitedCores.svg %}</div>
    <figcaption class="caption-text"><b>Figure 3</b>. Because of limited cores (4), execution times for work items in the third column will double. We also include some overhead needed for syncrhonization between threads to handle dependencies.</figcaption>
</figure>

The figure also shows delays (depicted with gray) for all the syncrhonization points between threads needed to handle the dependencies. Each time a work unit needs to communicate to other threads to start other work units, or each time multiple work units need to complete to start a new work units, we add such a gray box.

For our example, we considered the synchronization blocks to take 25% of the work unit. If we a work unit takes 40 ms, a synchronization block would take 10 ms. This may be too much in some cases, but nevertheless is possible --- and there are always worse cases.

With these 2 effects considered, we raise the total execution time from 240 ms to 320 ms -- that is a 33% loss in performance.

But assigning work units/threads per core is more complex than that. We assumed that if two work units need to share a core, both work units would finish in double the time. But, this may not be the case. We may have cache effects between the two, and actually be slower than 2 times. The constant back and forth between threads, will also have an impact on the cache, and thus can make the work units run even slower. Also the actual switching takes time, so additional overhead. Figure 4 shows some extra overhead on the work units that have to switch cores; we add 25% more to those work units. In total, the execution time would grow to 340 ms.

<figure class="caption">
    <div style="height: 300px;">{% include_relative diagrams/threads-are-not-the-answer/3_CacheEffects.svg %}</div>
    <figcaption class="caption-text"><b>Figure 4</b>. Cache effects can slow down even more the work units that have to constantly switch cores. In our case, we increased the duration of these work units by 25%</figcaption>
</figure>

But wait, we are not done yet. Threads usually don't work in isolation, and they access shared resources. And the standard view on concurrency is that we need locks to protect these. Those add more delays to the work units, as exemplified in Figure 5:

<figure class="caption">
    <div style="height: 300px;">{% include_relative diagrams/threads-are-not-the-answer/4_WithLocks.svg %}</div>
    <figcaption class="caption-text"><b>Figure 5</b>. Adding locks will make our tasks even slower. To simplify our problem, we only added locks for the highly shared part of our work tree.</figcaption>
</figure>

To simplify our example, we only added lock overheads to the work units in the middle, where we overbook our cores. We drawn 3 locks of 10 ms each. With this the total time increases to 370 ms.

Compared to the ideal model (Figure 2), the execution time increased with 54%. That is a very large increase.

If for your application some work units are more important than others, then you may want to ensure that those work units are done faster than the other ones. That is, you can assign higher priorities to some threads compared to other threads. Let's say that in our example we care more about the yellow work units, and don't care that much on the blue ones. We may be templed to the raise the priority of the 7th thread. A possible outcome of this thread priority change can be seen in Figure 6. We would reduce the amount of time needed by the work units assigned to this thread, but, as we have limited resources, we would increase the time needed for other threads to complete their work units.

<figure class="caption">
    <div style="height: 300px;">{% include_relative diagrams/threads-are-not-the-answer/5_WithThrottling.svg %}</div>
    <figcaption class="caption-text"><b>Figure 6</b>. Increasing the priority of the 7th thread will decrease the execution time on that thread, but will increase the execution times for all the other threads.</figcaption>
</figure>


As one can see from the picture, the results are kind-of strange. We reduced the total execution time from 370 to 360 ms, but on the other hand we've made all the other threads slower, and in some case, the critical path computations would wait on those threads.

Compare this with the Figure 2. What we've expected and what we've got. Not only the total time of executing is much bigger, but we've also made sure that we consume most of the cores for a longer period of time. This has typically a ripple effect; other work units are getting slower, which will generate more unexpected behavior.

So, using the common approach to concurrency, we are not gaining as much as we think out of adding more threads performance-wise.


## Intersection analogy

Concurrency allows us to have multiple threads going in parallel, and thus increase the throughput of our applications. That is a good thing. But, unfortunately these threads need to communicate: they need to access the same data, the same resources, they need to make progress towards the same goal. And this obviously is the root of the problem.

Here is a good analogy for thread-oriented concurrency model by Kevlin Henney: [Concurrency Versus Locking](https://youtu.be/mEtoXwB9HFk). Building on this idea, we can define:

Software world | Automotive world
-------------- | ----------------
thread | road
work unit | set of cars that pass over a road in a period of time
work unit dependencies | cars need to go from one road to another
total execution time | total time for all cars to reach the destination
lock/semaphore | traffic lights / roundabout
too few work unit dependencies | (highway) road network badly connected (sometimes this means long way to nearby locations)
too many work unit dependencies | too many intersections or access points (too much time spent in these)
too many small threads (descheduled often) | small roads
threads that are not descheduled from cores | highways

This analogy allows us to properly feel the scale of the problem, and also it can guide us to find better solutions.

For example, using this analogy, it is clear that adding too many work unit dependencies (i.e., very small work units) will make us spend too much time in the synchronization part. At the opposite pole, if we have very few dependencies, once you start a work unit, you have to wait for its completion to get new work units executed on the same thread.

In the automotive world, we would like to have as many highways as possible, and as little (blocking) intersections as possible.

According to the common concurrently mindset, we create a lot of small threads (small roads), and to solve our problems we add a lot of locks (traffic lights).

We all want our threads to behave like highways, but instead we add a lot of locks.

<div class="box info">
    <p><b>Key point</b></p>
    <p>An application with a lot of locks it's like <b>a highway with traffic lights every few miles</b>.</p>
</div>

Think about that, next time you want to add a lock in your application! It may also help to consider the following picture when adding locks:


{% include image_caption.html imageurl="/images/posts/traffic_jam.jpg"
title="The effect of locks" caption="<b>Figure 7</b>. The effect of locks, using the car analogy." %}


## Teasing: a way our of this mess

Do not despair. Concurrency doesn't need to be like that. The automotive world teaches us that we can have high-speed highways and a well-connected road network at the same time. I'll try in this small section a short teasing to what I think is the solution of all these concurrency problems.

The key point is that we shall start **thinking in terms of tasks**; not in terms of threads and locks. We shall raise our abstractions levels from using threading primitives to using concurrency high-level constructs. These tasks correspond to the work units we've discussed so far (I wanted to use a different terminology to indicate the fact that the previous example is not the right way to encode concurrency). The main point is that we shall approach concurrency problems with a breakdown of a problem in a directed acyclic graph of tasks like shown in Figure 1 above.

Let us go through the list of problems and see how these are solved in a task-oriented approach:

Thread-oriented problem | Task-oriented correspondent
----------------------- | ---------------------------
losing understandability, predictability, determinism | If every problem is decomposed into tasks, then it's much easier to understand the problem, predict the outcome, and determinism is greatly improved
not composable | directed acyclic graphs are composable; problem completely solved
needs syncrhonization | a proper execution graph will be able to avoid in most situations the need for locking; there would be only the need for synchronization at task begin/end, and this can be pushed at framework level
thread safety problems | if the graph is properly constructed, these will disappear; problem solved
hard to control | by definition a task-oriented system is much flexible, and can be better controlled

As one can see, most of the problems are either solved or greatly alleviated. But, above all, there is an even more important benefit that I want to stress out. The traditional thread-oriented approach, being bad at composability, impeded the use of top-down decomposition approaches for solving problems (divide and conquer approaches) --- and this is (most probably) the best known method of software design. On the other hand, a task-oriented approach would actually help in this method: it's easy to compose directed acyclic graphs. In other words, task-oriented is much better than thread-oriented from a design perspective.

From the performance point of view, task-oriented concurrency can also be much better than thread-oriented. The main idea is to let a framework to decide the best execution strategy, instead of letting the user pick a predefined schema. By embedding this into the framework, one can much better optimize the task scheduling. Note: although doing the scheduling of tasks automatically works better than a statically arranged system, an expect can always use a hand-picked optimizations to match or even be better than the automatic system; but this typically involves a lot of effort.

For the problem that we've defined in Figure 1, a task-oriented system would produce an execution similar to:

<figure class="caption">
    <div style="height: 238px;">{% include_relative diagrams/threads-are-not-the-answer/6_TaskBased.svg %}</div>
    <figcaption class="caption-text"><b>Figure 8</b>. Possible outcome in a task-oriented system of the problem in Figure 1. To make it easier to identify the tasks and to compare this with task-oriented systems, we added numbers to correspond the the rows in Figures 2-6.</figcaption>
</figure>

This arrangement is very possible within a task-oriented system. And, we don't use more threads than cores, we don't use locks and we won't throttle threads. We only need synchronization when taking tasks that are not direct followers of the previous tasks executing on a given worker thread. A good task system would have a highly optimized synchronization, so this is typically very small --- we made it here be 1/8 of the task time. If the task time is 40 ms, then the total time would be 255 ms. This is close to the ideal time with no synchronization (240 ms), and much better than the typical time obtained with a thread-oriented approach (360 ms) -- 50% improvement.

More on task-oriented approach in a later post.


## Conclusion

We discussed in this post the thread-and-lock-oriented model, which is to add threads to create parallelism, and then create locks to protect shared resources. We then discuss the main problems with this model. Besides the problems related to modifiability, we discuss how locks are an anti-pattern, and then go to show that the model has performance problems --- the execution time differs from the (naive) expected execution time. We use the analogy with cars, roads and intersection to give an intuition on how threading, the way we typically think of it, is a bad approach. Finally, we briefly introduce another way of thinking about concurrency, a task-oriented approach, that promises to solve most of the problems associated with concurrency.

Things to remember:
* traditional approach to concurrency is to create threads, and use low-level primitives to battle with the problems introduced by threads
* locks are evil; they simply defeat the purpose of multi-threading; they are an anti-pattern
* *Mutexes provide exclusive access to evil*
* in terms of performance, the typical expectation is wrong; the reality is typically far worse then what we would expect from creating threads
* every time you add locks to a system, think about how bad would a highway be with traffic lights every few miles; and think about the worst traffic jam that you have, and the fact that adding locks can turn your software into something similar to a traffic jam
* *an application with a lot of locks it's like a highway with traffic lights every few miles*
* consider a task-oriented approach when dealing with concurrency; this promisses to have modifiability advantages, but also performance gains
* avoid locks, avoid locks, avoid locks

Until next time. Keep truthing!

