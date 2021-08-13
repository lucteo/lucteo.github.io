---
layout: post
title:  "Designing Concurrent C++ Applications"
date:   2021-07-10
banner_image: cppnow2021.jpg
image: images/posts/cppnow2021.jpg
description: "How can one design concurrent applications in C++, without safety issus, with good performance"
tags: [concurrency, design, C++, conference, video]
img_credits:
    - ["", "C++ now", "C++ now 2021", ""]
---

C++, like most imperative languages, have a bad tradition in writing multi-threaded applications.
Concurrency safety ranks first in terms of C++ development frustration (far ahead from the second place).
This talk shows how concurrent C++ applications can be designed by shifting the focus from low-level synchronisation to a set of concurrency patterns that deal with higher-level constructs.

<!--more-->

The talk walks over a lot of examples of how one can introduce concurrency abstractions in a C++ application.
As a side-effect, it shows how one can use profiling tools like Tracy to investigate concurrent behaviour.

Video is available on [YouTube][2]. Slides and more information can be found [here][3].

<iframe width="560" height="315" src="https://www.youtube.com/embed/nGqE48_p6s4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Don't forget to support [nolocks.org][4] by spreading the word.

Keep truthing!

[1]:    https://github.com/wolfpld/tracy
[2]:    https://www.youtube.com/watch?v=nGqE48_p6s4
[3]:    {% link pres/2021-cppnow.md %}
[4]:    http://nolocks.org