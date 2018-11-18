---
layout: post
title:  "Look ma, no locks"
date:   2018-11-18
banner_image: no_locks.jpg
image: images/posts/no_locks.jpg
description: "We describe a systematic approach for replacing locks with tasks. In this approach thread blocking is replaced by properly scheduling of tasks."
tags: [concurrency, modifiability, performance, C++]
img_credits:
    - ["https://unsplash.com/photos/-lxVRvBGsao", "Matt Seymour", "Part of a set of photos I took on a recent trip to Crete, Greece.", ""]
---

We previously argued that threads are not the answer to parallelism problems, and also that we should avoid locks as much as possible. But how can we have a world in which threads do not block each other?

We want to explore here a systematic way for replacing locks (mutexes, read-write mutexes, semaphores) in our systems with tasks. We argue that there is a general schema that allows us to move from a world full of locks to a world without locks, in which the simple planning and execution of tasks makes things simpler and more efficient.

<!--more-->


## The world of locks

People introduce locks trying to protect access to shared resources. Multiple actors want to access the same resource in parallel, and at least one of the actors is trying to change the resource. In the locks world, actors accessing the shared resource may prevent other actors by accessing the same resource, causing them to block until the resource is available.

In the most simple case, all accesses to the resource are exclusive: only one actor can access the resource. This is implemented using a **mutex** (critical section, or simply lock). The following diagram depicts two threads trying to access a single resource, and the resource is protected by a mutex:

<figure class="caption">
    <div style="height: 135px;">{% include_relative diagrams/no_locks/1_mutexes.svg %}</div>
    <figcaption class="caption-text"><b>Figure 1</b>. Two threads and a mutex. Yellow represents thread not accessing the resource, magenta represents thread having access over the resource, and red means thread is waiting to acquire the resource.</figcaption>
</figure>

To reduce the amount of locking for the resource, one can divide the types of accesses to the resource in two parts: READ accesses and WRITE accesses. We want to maintain exclusivity to the resource for a WRITE access, but on the other hand we want to allow multiple READ accesses at the same time; READs and WRITEs are not allowed. This is implemented by a **read-write mutex**.


<figure class="caption">
    <div style="height: 126px;">{% include_relative diagrams/no_locks/2_rw_mutexes.svg %}</div>
    <figcaption class="caption-text"><b>Figure 2</b>. Two threads and a read-write mutex. Blue represent READs and magenta represents WRITEs. Multiple READs are allowed, but WRITEs are exclusive.</figcaption>
</figure>

A simple mutex can be seen as a read-write mutex where every access is a WRITE access. In addition to these WRITE operations, a read-write mutex also has READ operations.


Another core synchronization primitive is the **semaphore**. The problem solved by this one is slightly different: there are N resources available, and we cannot have more than N actors accessing these resources. For semaphores, only the number of resources is important, not how actors are allocated to resources. A semaphore is an extension of a simple mutex, as a mutex can be seen as a semaphore with N=1. The following picture shows how two threads compete for a semaphores with N=2:

<figure class="caption">
    <div style="height: 201px;">{% include_relative diagrams/no_locks/3_semaphores.svg %}</div>
    <figcaption class="caption-text"><b>Figure 3</b>. Three threads and a semaphore with N=2. We only block when the third thread tries to access the resource. Two threads accessing the resource is ok.</figcaption>
</figure>

The main purpose of this post is to show how we can implement these cases without any blocking.

We would get rid of the waits that simply put the CPU cores on pause, gaining in performance. There are also modifiability benefits of removing locks, as we gain composability back, and we would have a simpler way of building parallel applications.


## A static view

Things are very simple in a static world, where we know the execution profile for our threads and how they access the resources. If that would be the case, then our three cases above can be transformed into the following tasks graphs:

<figure class="caption">
    <div style="height: 126px;">{% include_relative diagrams/no_locks/4_mutexes_static_tasks.svg %}</div>
    <figcaption class="caption-text"><b>Figure 4</b>. Encoding the problem in Figure 1 (mutex) with static tasks.</figcaption>
</figure>

<figure class="caption">
    <div style="height: 126px;">{% include_relative diagrams/no_locks/5_rw_mutexes_static_tasks.svg %}</div>
    <figcaption class="caption-text"><b>Figure 5</b>. Encoding the problem in Figure 2 (read-write mutex) with static tasks.</figcaption>
</figure>

<figure class="caption">
    <div style="height: 201px;">{% include_relative diagrams/no_locks/6_semaphores_static_tasks.svg %}</div>
    <figcaption class="caption-text"><b>Figure 6</b>. Encoding the problem in Figure 3 (semaphore) with static tasks.</figcaption>
</figure>

Carefully looking at the above diagrams, the reader may argue that we still have waits. There are still gaps on the tasks needed to be executed by a thread. That may be true for our limited example, but in general this is not a problem; please see the *Is a task serializer better than a lock?* section below.


There are however 2 other problems which makes it very hard to use this static assignment of tasks in practice:
* variations of the execution speed of the tasks may require different set of links
* we rarely know what are the exact interactions between threads and their timings

One can solve the first problem by adding more dependency links between tasks (at the cost of making the setup far more complex). But the second problem is not easily solvable. This is why we need to have a dynamic schema of representing the locks and move away from the static view.

Even if the static approach is rarely applicable in practice, it provides a good way intuition on how we can solve the problem. One can easily visualize the required dependencies that need to be added between tasks to solve problems that are typically solved by locks. We will build on that intuition in the rest of the post.

<div class="box info">
    <p><b>Key point</b></p>
    <p>Using a static view of the tasks will provide insights of how tasks need to be implemented, even if it's just an approximation.</p>
</div>


## A better notation

So far we represented tasks as boxes of different colors. We also represented static constraints between tasks by arrows. If there are two tasks *A* and *B*, and there is an arrow from *A* to *B*, then we know for sure, before executing any of these, that *B* can only be executed after *A*.

This notation is limiting for expressing dynamic constraints. For this, we will extend the box notations to contain additional dynamic constraints:

<figure class="caption">
    <div style="height: 71px;">{% include_relative diagrams/no_locks/7_notation.svg %}</div>
    <figcaption class="caption-text"><b>Figure 7</b>. Notation convention for dynamic constraints.</figcaption>
</figure>

To represent dynamic constraints, we draw below each block a small box with one or more colors, and optionally a constraint text.

In the absence of text, the colors in the small box indicates that the task is not supposed to be run in parallel with tasks of those colors. For example, the green tasks should not be run in parallel with any orange tasks; similarly, the magenta task is not supposed to be run in parallel with any magenta or blue tasks.

The text will add more meaning to the constraint. It can have different meanings in different contexts. For the purpose of this post, we assume it will indicate the multiplicity needed for representing semaphores. For example, if c<sub>1</sub> is 2, then we mean that we don't want to run the green task if there are 2 or more orange tasks running, but we can run it if there is only one orange task running.

With this notation, we can better represent all the previous cases: mutex, read-write mutex and semaphore:

<figure class="caption">
    <div style="height: 146px;">{% include_relative diagrams/no_locks/8_mutexes_dynamic.svg %}</div>
    <figcaption class="caption-text"><b>Figure 8</b>. Encoding the problem in Figure 1 (mutex) with dynamic tasks.</figcaption>
</figure>

<figure class="caption">
    <div style="height: 146px;">{% include_relative diagrams/no_locks/9_rw_mutexes_dynamic.svg %}</div>
    <figcaption class="caption-text"><b>Figure 9</b>. Encoding the problem in Figure 2 (read-write mutex) with dynamic tasks.</figcaption>
</figure>

<figure class="caption">
    <div style="height: 221px;">{% include_relative diagrams/no_locks/10_semaphores_dynamic.svg %}</div>
    <figcaption class="caption-text"><b>Figure 10</b>. Encoding the problem in Figure 3 (semaphore) with dynamic tasks.</figcaption>
</figure>

In the first case, we have complete exclusiveness: a magenta box cannot be run in parallel with any magenta box.

In the second case (read-write mutex), we relax a bit the rules. Any blue box (READ operation) cannot be run in parallel with a magenta box (WRITE operation), and a magenta box cannot be run in parallel with a magenta nor with a blue box.

For the semaphore case, we indicate on each magenta box the maximum count of the semaphore. Each magenta box cannot be run in parallel with another two magenta boxes.

That is it. We have a way of representing with tasks and (dynamic) constraints all the problems that one would typically solve with locks (mutexes, read-write mutexes and semaphores).

<div class="box info">
    <p><b>Key point</b></p>
    <p>Any problem that required locks can be reimagined with tasks and dynamic constraints.</p>
</div>


## Implementation tips

### Basic task execution abstraction

To be able to work with tasks, we need to have an abstraction for a task. In the simplest form, a task is a functor that takes not parameters and return nothing. In C++, this would be written as:

{% highlight C++ %}
using Task = std::function<void()>;
{% endhighlight %}

Now, in order to use these tasks we need to have a mechanism of *enqueueing* them, to start them. For this, we will assume the existence of a *TaskExecutor*, with the following interface:

{% highlight C++ %}
class TaskExecutor
{
public:
    virtual void enqueue(Task t) = 0;
};
{% endhighlight %}

We have the following assumptions related to enqueuing the tasks and executing them:
* `enqueue` schedules the task to be executed (at a later time) and exists immediately
* the task will eventually be executed
* assuming the system is not overloaded with other tasks, the task will be executed immediately
* after a task is enqueued, there is no way to cancel it (simplifying assumption)

This minimal interface and these assumptions are all that we need to build a good-enough task system that will allow us to avoid locks completely. (Typically a good task system also requires a `join` abstraction; but this doesn't matter for the scope of our discussion).


### Task serializer: a mutex replacement

We can define a task serializer as a special form of task executor that ensures that only one of the enqueued tasks are running at a given time. It does that by delaying the enqueueing of tasks if there are other tasks belonging to the serializer that is still executed.

Implementation of a task serializer is relatively simple:
* we have one (lockless) list of not-yet-enqueued tasks
* each time a task is added we check (atomically) if there are any tasks in execution
    * if there are tasks in execution, add the task to our internal queue
    * if there are no tasks in execution, start executing the given task
* at the end of a task execution, we enqueue a task from our internal list if there are any
* to be able to do extra work at the end of the task, we wrap our task into a task that call the given tasks and performs the extra work
* special care needs to be taken when enqueing tasks and finishing tasks to be able not to miss tasks or to start executing two tasks

The key point here is that we accumulate tasks into a buffer while other tasks are executed. As soon as we are done executing tasks, we take tasks from our buffer and enqueue them into the task system.

The C++ interface for a task serializer would be:

{% highlight C++ %}
class TaskSerializer : TaskExecutor
{
public:
    TaskSerializer(TaskExecutor& executor);

    void enqueue(Task t) override;
};
{% endhighlight %}

It is interesting to note that a task serializer can itself be considered a task executor: it knows how to schedule the execution of tasks, but it has a constraint applied to them. This is a nice design property.

Task serializers would replace the use of regular mutex. If all the actions that touch a shared resource are enqueued through a task serializer, we are guaranteed not to have 2 threads accessing the shared resource at the same time.


### Read-write task serializer

If a task serializer would replace a regular mutex, we need something to replace a read-write mutex.

In a basic task serializer, all tasks are exclusive, and of the same kind. Here, we need to partition the tasks in two types: WRITE and READ tasks. The WRITE tasks need to behave similar to the tasks in a basic task serializer. The READ tasks however have some special properties:
* we can have multiple READ tasks executing at a given time
* while there is a WRITE executing, we cannot execute any READ tasks


The details on how we might implement such a structure are the following:
* we keep two buffers: one for READ tasks, one for WRITE tasks
* we keep track of the type of task we are currently executing
* if we add a READ task, then:
    * if we are not executing a WRITE task, enqueue the task for execution
    * otherwise, add it to the buffer of READ tasks
* if we add a WRITE task, then:
    * if we are not executing any task, enqueue the task for execution
    * otherwise, add the task to the WRITE buffer
* at any time, keep track of how many tasks we are executing, and of which kind
* if we finish executing a WRITE task, then:
    * if there are other WRITE tasks, enqueue the first one
    * if there are no WRITE tasks, but there are READ tasks, enqueue all of them
* if we finish executing a READ task, then:
    * if there are no WRITE tasks, do nothing
    * otherwise, if there are some other READ tasks executing, do nothing
    * otherwise (WRITE tasks present, and this is the last READ task), enqueue the first WRITE task

Please note that this schema will favor WRITE tasks in front of READ tasks. One can easily change the logic to favor READ instead of WRITE tasks.

The C++ interface for this two-level task serializer would be:

{% highlight C++ %}
class RWTaskSerializer : TaskExecutor
{
public:
    RWTaskSerializer(TaskExecutor& executor);

    void enqueue(Task t) override;
    void enqueueRead(Task t);

    TaskExecutor& getReadExecutor();
};
{% endhighlight %}

This is also a TaskExecutor; by default it will enqueue WRITE tasks (safest). There is a special method for enqueueing READ tasks; there is also a method for obtaining a TaskExecutor that will enqueue READ tasks, for convenience.

This schema corresponds to read-write mutexes. We can completely avoid mutexes by using tasks serializers and read-write task serializers.


### Replacing the semaphore

A task serializer has 1 task executing at a given time. To replace semaphores, we need a special form of task serializer that allows executing *N* tasks at a given time. We call this abstraction a *N-task serializer*.

The idea is the same as with the task serializer:
* we keep a buffer of tasks that are enqueued and not yet allowed to run
* instead of executing one task from the queue, we execute maximum *N*
* instead of just tracking whether we are executing one task or not, we track how many tasks we are executing
* we accumulate tasks into our buffer only when we filled up all our executing positions

The C++ interface for the N-task serializer would be:

{% highlight C++ %}
class NTaskSerializer : TaskExecutor
{
public:
    NTaskSerializer(TaskExecutor& executor, int numParTasks=1);

    void enqueue(Task t) override;
};
{% endhighlight %}


### Generalizing

Looking at the previous abstractions, we can observe a common pattern:
* instead of blocking, we accumulate tasks to be executed in one or more buffers
* we only enqueue tasks into our task executor whenever the conditions are met for safely executing the tasks
* we check whether these conditions are met, each time we add a task and each time a task is completed (note that the two places need to be synchronized)

With these observations in mind, we can use tasks to solve any generic problem that requires waiting. Let us model that problem by the presence of two operations:
* *acquire(L)* -- called at the beginning of the scope to protect; this will check a condition *cond(L)* to determine what to do next
    * if the condition is true, this will enter the lock
    * if the condition is false, this will block the current execution, waiting for the condition to become true
* *release(L)* -- called at the end of the scope to protect; this may change the results of the conditions for all the *acquire* operations that are locked

One can see, that we can easily model mutexes, read-write mutexes and semaphores with these two operations and condition checking.

Transposing this generic locking algorithms to tasks, one would do the following:
* transform *acquire* into an enqueing of task into a serializer-like structure
* consider the end of the task execution as the *release* operation
* make sure that the condition is always evaluated atomically
* whenever enqueuing and the condition evaluates to false, add the task to an internal buffer
* whenever a task finishes up executing, re-evaluate the condition with respect to the first entry in our buffer; if the condition becomes true, enqueue the task for execution

This is a recipe for implementing all sorts of wait-based locking strategies. Far beyond the usage of the three main synchronization primitives: mutex, read-write mutex and semaphore. This enables us to postulate the following:

<div class="box info">
    <p><b>Key point</b></p>
    <p>Every lock-based synchronization primitive should be able to be converted into a strategy that uses tasks and that doesn't do any waiting.</p>
</div>


## Analysis and conclusion

### Is a task serializer better than a lock?

The reader may have noticed that instead of waiting, our block-free approach delays the executions of the tasks. This is somehow similar to a block, but without the explicit use of any blocking algorithm.

This is true to some point; but the scenario is very limited. It's limited only to the case in which we don't have a lot of work to do in the application, and we only measure the latency. As soon as we have other work to do, and we are more interested in the throughput, this stops to be true. The reason is that we don't make the CPU wait on that particular thread, as we can execute other tasks.

Let's consider a simple example: Let's say that we have 3 different resources that we want to access in an exclusive manner (blue, green, magenta), and some tasks that do not require any protection (yellow). All these running on 2 threads. Protecting the accesses to the mutexes with 3 mutexes would look something like:

<figure class="caption">
    <div style="height: 126px;">{% include_relative diagrams/no_locks/11_3_locks_waits.svg %}</div>
    <figcaption class="caption-text"><b>Figure 11</b>. Example of using 3 mutexes on two threads.</figcaption>
</figure>

In this particular example, the second thread would be somehow trying to access the same resources as the first thread, and it will always block (red parts).

Using tasks, the scheduler will not block, and will attempt to execute other tasks that are enqueued. The results can look something like:

<figure class="caption">
    <div style="height: 126px;">{% include_relative diagrams/no_locks/12_3_locks_tasks.svg %}</div>
    <figcaption class="caption-text"><b>Figure 12</b>. Using tasks instead of mutexes</figcaption>
</figure>

Here, instead of blocking on the second thread when executing the blue task, the scheduler picks up a yellow task; the same thing happens again when trying to execute the magenta task. Therefore, by picking yellow tasks instead of waiting, both threads would finish faster the amount of work created.

So yes, using a task serializer is usually better than using a mutex.

<div class="box info">
    <p><b>Key point</b></p>
    <p>Prefer task serializers to using mutexes.</p>
</div>


### You mean no locks at all?

Well, not quite. To some point, certain locks may be used to implement some machinery that is needed for running the task system. Implementations typically use some variants of spin-locks to achieve synchronization.

The main point however is that locks are low-level primitives that should not be used by the user. Library implementors usually do a lot of benchmarks when deciding to go for locks in certain places, and typically the performance of those locks is well understood.

Similarly, one should avoid creating threads directly. The task scheduler should be responsible of creating the threads, ideally to match the number of cores in the system. Running two threads on one core is typically worse than executing the corresponding tasks serially on the core with a single thread.

<div class="box info">
    <p><b>Key point</b></p>
    <p>Users should not use locks and threads directly.</p>
</div>


### Next steps

This post provides the foundation of thinking about parallelism without thinking about locks. Actually, thinking of parallelism in terms of tasks is much better than thinking in terms of synchronization primitives. The main advantage is that tasks are composable, even in the presence of constraints (locks are not).

Thinking in terms of tasks opens new possibilities for constructing parallel applications: we can start discussing about priority queues, parallel map, parallel reduce, parallel map-reduce, pipelines, recursive decomposition, events, etc. That will raise the level of abstraction for building parallel applications, and therefore making it easier to develop state-of-the-art parallel applications.

We should dedicate some more blog posts to these topics.

Also, we should probably dedicate some blog posts to implementation details and performance measurements.

On what of these topics would you like me to write next? Leave your comment below.

May the truthing spirit be with you!
