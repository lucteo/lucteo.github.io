---
layout: post
title:  "Senders/receivers in C++"
date:   2024-08-12
banner_image: sendersreceivers.png
image: images/posts/MeetingCpp2021.png
description: "A few thoughts on the recent additions of senders/receivers to the C++ standard working draft"
tags: [senders/receivers, C++, C++ standard]
---

On June 29th, in St. Louis, MO, USA, the C++ standard committee voted to include [P2300 std::execution][1] in the upcoming C++26 standard. The result is now published in the [C++ standard working draft][2]. A short introduction to this can be found in [Herb's post][3]. As expected by many, the plenary vote was controversial. I wrote this post to share some of my thoughts on the subject.

<!--more-->

## Are senders/receivers a good thing?

Yes, definitely! Senders/receivers provide a foundational approach for expressing concurrency, parallelism, and asynchrony in C++. Similar to structured programming, they enable us to apply [Structured Concurrency][4]. This allows us to address concurrent problems without typical multi-threaded issues such as data races, deadlocks, and performance bottlenecks. Transitioning from classical multi-threaded programming with threads and locks to a structured concurrency model is akin to moving from programming based on `goto` statements to structured programming with clear code abstractions.

Senders/receivers is not just a framework for specific types of problems; it's a [global solution to concurrency][5]. Every problem that can be solved with threads and locks can also be addressed using senders/receivers. From this perspective, senders/receivers is a framework that addresses the fundamental challenges of concurrency.

One criticism of senders/receivers is that they can be challenging to work with and difficult to fully understand. While this may be true, the same can be said of iterators. Iterators are a fundamental part of C++, and much of the language's success is due to their use as a building block for generic programming. Similarly, senders/receivers may not be easy to grasp initially, but they have the potential to profoundly impact the way we write code.

So yes, senders and receivers are a good thing. We need to include them in the C++ standard as soon as possible.

## Is this the perfect concurrency model?

No, it's not. Probably the worst part about senders/receivers is its ergonomics. It may not be that easy to use, especially when compared to other frameworks (coroutines, async/await, etc.). But this is not because there is something inherently broken in the model of senders/receivers. Most of the problem comes from the complexity of C++ and the way people are using the language.

A good concurrency model (see, for example, [the hints from this talk][6]) may require major paradigm changes that C++ may not be ready to adopt. Please note that, even if we decide to use new concurrency frameworks, senders/receivers are probably compatible with those; to my knowledge, every major concurrency paradigm can be (with some effort) mapped to senders/receivers.

So, it may not be the ideal concurrency model, but it's probably the best foundation for general C++ concurrency. At least for now.

## Ergonomics

Using senders/receivers requires the programmer to spend some time wrapping their head around the concepts, and even after that, it's not the easiest framework to work with. This is true. Coroutines provide a much friendlier approach to concurrency.

But, to some extent, the entire C++ language is like that. Ergonomics is not the language's strongest point. C++ programmers are somewhat accustomed to this challenging user experience, so this would not constitute a strong argument against senders/receivers.

Even coroutines, which can be a more user-friendly model than senders/receivers, have significant problems in terms of ergonomics. There is a joke in the C++ community: you watch a lot talks explaining coroutines, and you still don't get it; then you decide that the best way to learn is to give a public talk explaining coroutines — increasing the count by one, probably as a warning to the next person who wants to become a coroutine expert.

## Teachability

There was a significant argument before the vote that senders/receivers are not teachable. I don't think that is true. There have been a relatively large number of talks explaining various aspects of senders/receivers. There are workshops on this topic as well.

While the paper is complex to read, the core ideas for users are simple. They should focus on senders (which, admittedly, is probably not the best name, but no one has proposed a better one). Senders describe concurrent computations. They can be assembled into increasingly complex chains to represent larger computations, and there are algorithms to help users compose these larger computations. That's the essence; the rest is likely easy to learn once this is properly understood. See, for example, [another talk of mine][7] on this subject.

Once the main concepts are clearly explained, the rest should be straightforward. It's mostly about syntax. Even if it's not the prettiest syntax, C++ users are accustomed to features that are not easy to use but allow for squeezing out additional performance.

As mentioned above, senders/receivers allow for structured concurrency. Among other benefits, this means that users can recursively decompose concurrent programs into smaller and smaller pieces, which can eventually be encapsulated with senders. If done properly, the entire program becomes much easier to reason about. I foresee a near future where describing concurrency in terms of senders/receivers is much easier to teach than concurrency with threads and locks.

## Compile-time and diagnostics

Another argument is that senders/receivers have a relatively high compile-time cost. This may be true for the initial implementation, but it is not set in stone. Many C++ features were initially very slow to compile. Over time, they became more efficient. If we include this in the standard, then compiler and library implementers may invest effort in making it compile faster.

There was also an argument that the diagnostics of the library implementing senders/receivers are quite poor. The answer to this concern is similar to the previous one: over time, we would get better diagnostics.

I do believe that time will fix both of these problems, to the point where they won't be worse than other features from the standard library (ranges, concepts, etc.).

## More features are needed

One interesting argument I heard against the senders/receivers framework is that, as currently proposed, it's not complete. Users would need more concurrency and parallelism features to use them properly. This is partially true. But including the basic framework in the standard doesn't prevent users from creating abstractions for common cases; it may be harder to do it right for the average user, but it's not impossible.

A good example from the recent history of C++ is coroutines. We standardized the basic framework without any coroutine types. In C++23, we just got `std::generator`. Why would it be a showstopper if we only got P2300?

Still, some of the authors of P2300 [proposed a plan][8] for adding a series of features to senders/receivers for C++26. Even if only half of the proposed features make it into C++26, I would argue that we've still made a huge step in the right direction.

## Bottom line

I am, of course, biased. I am one of the authors of P2300.

(Truth be told, I'm not sure if I deserve to be one. My contributions to the paper and/or standard implementations are minor. I'll always be grateful to Bryce and Eric for adding me as an author.)

But, trying to be as objective as possible, I still think that this is a good framework to include in the C++ standard. It may not have the nicest syntax, but it's a very powerful feature. It provides a foundation for expressing concurrency in C++.

I think that senders/receivers is one of the most important features that C++ will have, standing very close to iterators. It will open a whole new world of programming in C++.

Keep truthing!

[1]:    https://wg21.link/P2300R10
[2]:    https://eel.is/c++draft/#exec
[3]:    https://herbsutter.com/2024/07/02/trip-report-summer-iso-c-standards-meeting-st-louis-mo-usa/
[4]:    https://www.youtube.com/watch?v=Xq2IMOPjPs0
[5]:    https://wg21.link/P2504R0
[6]:    https://www.youtube.com/watch?v=uSG240pJGPM
[7]:    https://www.youtube.com/watch?v=0i2MnO2_uic
[8]:    https://wg21.link/P3109R0