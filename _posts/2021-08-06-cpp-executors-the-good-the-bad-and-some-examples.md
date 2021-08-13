---
layout: post
title:  "C++ Executors: the Good, the Bad, and Some Examples"
date:   2021-08-06
banner_image: overload164.jpg
image: images/posts/overload164.jpg
description: "C++ executors: a very strong proposal, or just a big hype? Well, it depends..."
tags: [concurrency, C++, standardisation, Overload]
img_credits:
    - ["https://accu.org/journals/overload/29/164/overload164.pdf", "ACCU", "Overload 164, August 2021", ""]
---

Executors are one of the most expected features for the upcoming C++ standards.
This article tries to cast a critical perspective of some of the main proposals discussed for adoption.
Besides briefly explaining the content of the executors proposal and providing a few examples, the article tries to pick on some decisions made in those proposals.
It tries to argue about the strong and the weak points by adding simplistic labels of "good" and "bad".

<!--more-->

As with most of the later articles, this was published in [Overload][1].

<iframe width="620" height="876.5" src="https://accu.org/journals/overload/29/164/overload164.pdf" frameborder="0"></iframe>

**NOTE**: The article contains one major error: I argue that executors do not provide a monadic bind.
This is completely wrong. The `let_value` provides just this functionality.
I'll try to correct the mistake in the next article.

Don't forget to support [nolocks.org][2] by spreading the word.

Keep truthing!

[1]:    https://accu.org/journals/overload/29/164/overload164.pdf
[2]:	http://nolocks.org