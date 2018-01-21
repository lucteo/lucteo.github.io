---
layout: post
title:  "Why do we need to go meta?"
date:   2017-12-17
banner_image: Lake_mapourika_NZ.jpg
image: images/posts/Lake_mapourika_NZ.jpg
description: Physicists claim nowadays that metaphysics is dead. But how can they make claims about what's beyond physics? They can't. There are always hidden assumptions. We can learn something from this.
tags: [physics, metaphysics, meta, generalization, ignorance, computruthing]
---

This post is inspired by the blog post [Why physicists need philosophy](https://blog.oup.com/2017/12/physicists-need-philosophy/). Richard Healey, the author of the post, rightfully argues against the mainstream belief among top physicists that physics has an answer for everything. He argues that philosophy is still needed to answer some of the aspects that physicists are still unable to answer. Stephen Hawking is so wrong when he [considers philosophy to be dead](http://www.telegraph.co.uk/technology/google/8520033/Stephen-Hawking-tells-Google-philosophy-is-dead.html).

<!--more-->

## The incompleteness of physics

Let's not delve yet into modern physics, and stay in the realm of Newtonian mechanics. According to it, a body starts moving whenever a force is applied to it. Physics tells us **how**:

$$F = m \cdot a$$

Starting with this fundamental law, we can construct all the classic mechanics, and explain a range variety of natural phenomenons from the movement of sand grains to the movement of the stars (at least with a good approximation). We can really stay in awe in front of how much we can explain with a few physics laws.

But let's not fool ourselves. This does not fully explain everything. And moreover, like modern physics proved, it may also not be true.

The fundamental problem of physics is that it doesn't fundamentally answer the **why** questions for fundamental laws: Why force is mass times acceleration? Why acceleration and not velocity:

$$F = m \cdot v$$

Pause for a second, and imagine how the reality would look if we could change this fundamental law. And physics doesn't care about this basic fact at all. For it, this is just a _postulate_, something that we agree to believe is true. We rarely ponder whether postulates are true; we just believe in them.

If we switch to modern physics, we can never find answers to questions like: _why isn't there an absolute system of reference?_, _why does the Heisenberg uncertainty principle hold?_, _why is the nature discrete at small scales?_, etc.

Every theory in physics is built on some postulates, representing the limits of the domain. This is to say that physics can never go beyond.

## Metaphysics to the rescue

[Metaphysics](https://plato.stanford.edu/entries/metaphysics/) is the discipline that goes _beyond_ physics. The word comes from one of [Aristotle](https://en.wikipedia.org/wiki/Aristotle)'s books. Aristotle didn't use this term himself (he used the terms like _first philosophy_, _first science_, _wisdom_ and _theology_), but rather [Andronicus of Rhodes](https://en.wikipedia.org/wiki/Andronicus_of_Rhodes), when arranging Aristotle's book named it tà metà tà physikà biblía -- _the book after physics_. Since then, we refer to metaphysics as that which is **beyond physics**.

Metaphysics is concerned with matters of _being_, _existence_ and _reality_ --- actually, it's much more complex than that, we don't have a good boundary to what metaphysics means, but let's keep it simple.

Questions like _is there an objective reality?_, _is there only one reality?_, _what does reality mean?_, all are subjects of metaphysics. Therefore, as matters of _reality_, the fact that _physics has laws_ and the _inner meaning of those laws_ are also under the jurisdiction of metaphysics. Only the identification and the consequences of the general laws are treated by physics.

If you are inside a sealed box, you cannot see outside the box. Similarly, physics cannot see outside physics, and cannot be used to infer **meta**physics.

To draw an example from computing, if you are a Java program, you cannot simply deny the existence of a real computing machine. Yes, you only care about the Java virtual machine, but in the end, you will still run on a real computing machine.

Statements like "_metaphysics is dead_" go beyond the realm of physics. They concern _existence_ and _reality_ and they are metaphysics. So, instead of denying metaphysics, they are just creating another metaphysics. A metaphysics of ignorance.

There is no avoiding it: metaphysics is there to stay.


## Utility is not reality

Let's not deny it: it's sometimes useful to forget about metaphysics. After all, you don't need to explain why $$F = m \cdot a$$ to build up mechanics on top of it.

Actually, this is the general process of how we build theories:
- we limit ourselves to a certain domain
- we generalize, ignoring irrelevant attributes/conditions
- we derive conclusions based on the above two

But let's remember: the strength of our conclusions is always limited by the strength of the assumptions we used to draw the conclusions. After arriving at some amazing conclusions, we cannot automatically apply these conclusions to the things that we intentionally left out before arriving to these conclusions.

If physicists ignored metaphysics for a couple hundreds of years, it doesn't mean that metaphysics is not there.

At the heart of every utilitarian approach there is a fair amount of ignorance. It is fine to ignore stuff to reach to some conclusions, but one should never forget what they excluded.


## The great beyond; and some computing

What do all these mean to me? It means that there are always some meta- to everything. We should always go beyond the status-quo and ask ourselves _but what do all these mean?_.

That is true in general, and also for computing. Let me quickly apply this to some simple examples.

### Premature optimization

We all know this slogan:
> Premature optimization is the root of all evil. <cite>[Donald Knuth](https://en.wikiquote.org/wiki/Donald_Knuth)</cite>

What does this mean? How general is this?

Let's first look at the immediate context of this maxim:
> The real problem is that programmers have spent far too much time worrying about efficiency in the wrong places and at the wrong times; premature optimization is the root of all evil (or at least most of it) in programming <cite>Donald Knuth</cite>

Ok. So Knuth was analyzing (in 1974) some code, and found that programmers were optimizing in the wrong places and at the wrong times. This makes me wonder the following:
- how representative was the software that Knuth analyzed?
- does this still apply nowadays? the software industry has changed a lot in 43 years
- it seems like Knuth refers to optimizing at the wrong places; this may not have too much to do with _premature optimization_
- does this imply that we should optimize only after the whole system was build, as many of programmers nowadays think?
- etc.

Don't get me wrong: I've seen a lot of programmers that would try to optimize before measuring, so that they should be reminded of this quote. But unfortunately, I've seen much more programmers who simply don't care about performance, because this quote affected in a negative manner the software industry.

Let us not fall into ignorance when we hear once more Knuth's famous quote.

### C/C++ are 'fast' programming languages

There is a common belief that C and C++ programming languages are fast, meaning that they produce efficient code. Let us see what we've left out when making this generalization:
- not all the generated code will be fast; if the input program is inefficient, so will be the output program
- this doesn't mean that there are no programs that are faster to be run in Java than C++
- if the program doesn't take into consideration some run-time usage patterns, it may not be as efficient

The first point is self-explained. Please see [this](http://scribblethink.org/Computer/javaCbenchmark.html) and [this](https://www.forbes.com/sites/quora/2015/05/26/when-is-java-faster-than-c/#4e18453a3100) for an explanation of why Java could be faster than C++ in certain circumstances. As Java typically runs the optimizer dynamically, it can optimize better for certain usage patterns, compared to a typical C++ optimizer. In other words, the typical optimizations found in C/C++ compilers, even though they are good in general, they can sometimes produce less optimal code for certain usage patterns.

---

Next time somebody makes an overgeneralizing statement, question the original assumptions. You will always find things that were ignored in the premises.

And, because we started our discussion from metaphysics, let me finish with some words from the first book of Aristotelian metaphysics:

> Since we are seeking this knowledge, we must inquire of what kind are the causes and the principles, the knowledge of which is Wisdom. <cite>Aristotle, [Metaphyics](http://classics.mit.edu/Aristotle/metaphysics.1.i.html)</cite>

Keep truthing!
