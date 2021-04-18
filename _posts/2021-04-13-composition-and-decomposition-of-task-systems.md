---
layout: post
title:  "Composition and Decomposition of Task Systems"
date:   2021-04-13
banner_image: Overload162.jpg
image: images/posts/Overload162.jpg
description: "Composition and decomposition are fundamental. How do they apply to task systems?"
tags: [concurrency, design, C++, Overload]
img_credits:
    - ["https://accu.org/journals/overload/29/162/overload162.pdf", "ACCU", "Overload 162, April 2021", ""]
---

Composition and decomposition are probably the most important tools we have as software engineers. And yet, for multi-threaded programs that use locks and raw threads, composition and decomposition doesn't properly hold.

This article tries to consider composition and decomposition of task systems, showing that task systems play nice with regards to those two.

<!--more-->

As with most of the later articles, this was published in [Overload][1].

<iframe width="620" height="876.5" src="https://accu.org/journals/overload/29/162/overload162.pdf" frameborder="0"></iframe>

Don't forget to support [nolocks.org][2] by spreading the word.

Keep truthing!

[1]:    https://accu.org/journals/overload/29/162/overload162.pdf
[2]:	http://nolocks.org