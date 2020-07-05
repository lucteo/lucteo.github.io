---
layout: post
title:  "Refocusing Amdahl's Law"
date:   2020-07-04
banner_image: Overload157.jpg
image: images/posts/Overload157.jpg
description: "Amdahl's law doesn't have to severely limit our performance. We can construct parallel programs without severe degradation in speedup. Don't take my word for it; look at the formulas."
tags: [inheritance, oop, software engineering, philosophy, Overload]
img_credits:
    - ["https://accu.org/var/uploads/journals/Overload157.pdf", "ACCU", "Overload 156, April 2020", ""]
---

At this point, I'm decided to pass most of my articles to Overload. I still have the freedom to talk about the topics that are close to my heart, but I also get all the benefits of publishing in a peer-reviewed journal. I highly appreciate the high-quality feedback coming from the reviewers, and the professionalism of all involved. Respect!

This article is proof that one can achieve high speedups by using task-based concurrency rather than locks. I personally was delighted with the results after working our the formulas.

<!--more-->

If you still use mutexes in your codebase, you need to read the article. If you are not using mutexes, the article explains you (at least one facet of) why you are doing the right thing. So, read the [article](https://accu.org/var/uploads/journals/Overload157.pdf):

<iframe width="620" height="876.5" src="https://accu.org/var/uploads/journals/Overload157.pdf" frameborder="0"></iframe>

Keep truthing!
