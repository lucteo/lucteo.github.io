---
layout: post
title:  "The Global Lockdown of Locks"
date:   2020-08-06
banner_image: Overload158.jpg
image: images/posts/Overload158.jpg
description: "We demonstrate why you should not need mutexes in high-level code, since any concurrent algorithm can be implemented safely and efficiently using tasks"
tags: [concurrency, design, Overload]
img_credits:
    - ["https://accu.org/journals/overload/28/158/overload158.pdf", "ACCU", "Overload 158, August 2020", ""]
---

In my [previous Overload article]({{page.previous.url}}) I showed how one can achieve great speedups using tasks as the foundation for concurrent programming instead of locks. The one thing that is not clear is whether one can use tasks for all the concurrent algorithms. Tasks may be applicable to certain types of problem, but not to all problems. This article tries to complete the picture by showing that all algorithms can use tasks and there is no need for locks.

<!--more-->

The article proves that one can find a general algorithm for implementing all concurrent algorithms just by using a task system, without the need for locks or other synchronisation primitives in user code. It also gives some ideas on how to replace locks with abstractions based on tasks.

Hopefully, by the end of the article, the reader will be convinced that locks should not be used in day-to-day problems but instead should be confined to use by experts when building concurrent systems.

Please refer to the [Overload article](https://accu.org/journals/overload/28/158/overload158.pdf):

<iframe width="620" height="876.5" src="https://accu.org/journals/overload/28/158/overload158.pdf" frameborder="0"></iframe>

Keep truthing!
