---
layout: post
title:  "Concurrency Design Patterns"
date:   2020-10-19
banner_image: Overload159.jpg
image: images/posts/Overload159.jpg
description: "We demonstrate why you should not need mutexes in high-level code, since any concurrent algorithm can be implemented safely and efficiently using tasks"
tags: [concurrency, design, patterns, Overload]
img_credits:
    - ["https://accu.org/journals/overload/28/159/overload159.pdf", "ACCU", "Overload 159, August 2020", ""]
---

As tasks are not very widespread, people may not have sufficient examples to start working with tasks instead of mutexes. This article tries to help with this by providing a series of design patterns that can help ease the adoption of task systems, and that may, at the same time, improve general concurrency design skills. Even more fundamentally, it tries to show how applications can be designed for concurrency.

<!--more-->

This comes as a continuation of my two previous Overload articles ([Refocusing Amdahl’s Law][1] and [The Global Lockdown of Locks][2]) where I tried to show that using tasks instead of mutexes is more performant, is safer and they can be employed in all the places that mutexes can. Tasks are not the only alternative to mutexes, but this seems to be the most general alternative; to a large degree, one can change all programs that use mutexes to use tasks. In general, using tasks, one shifts focus from the details of implementing multithreaded applications to designing concurrent applications. And, whenever the focus is on design, we can be much better at the task at hand – design is central to the software engineering discipline.

This article tries to provide some design patterns for task-based concurrency. Please refer to the [Overload article][3]:

<iframe width="620" height="876.5" src="https://accu.org/journals/overload/28/159/overload159.pdf" frameborder="0"></iframe>

Keep truthing!

[1]:	{%post_url 2020-06-05-refocusing-amdahls-law%}
[2]:	{%post_url 2020-08-06-global-lockdown-of-locks%}
[3]:	https://accu.org/journals/overload/28/159/overload159.pdf