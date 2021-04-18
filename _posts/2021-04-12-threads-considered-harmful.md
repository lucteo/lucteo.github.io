---
layout: post
title:  "Threads Considered Harmful"
date:   2021-04-12
banner_image: ACCU2021.jpg
image: images/posts/ACCU2021.jpg
description: "Similar to gotos, raw threads and locks should be banished from day-to-day programming"
tags: [concurrency, design, C++, conference, video]
img_credits:
    - ["", "ACCU", "ACCU Conf 2021", ""]
---

Similar to gotos, raw threads and locks should be banished from day-to-day programming. Moreover, we have far better way to build concurrent applications.

Watch my ACCU 2021 talk to see more.

<!--more-->

Video is available on [YouTube][1]. Slides and more information can be found [here][2]. The session first introduced [nolocks.org][3], which I hope helps in spreading the word that locks should be avoided.

<iframe width="560" height="315" src="https://www.youtube.com/embed/_T1XjxXNSCs" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Keep truthing!

[1]:    https://www.youtube.com/watch?v=_T1XjxXNSCs
[2]:	{% link pres/2021-accu.md %}
[3]:    http://nolocks.org