---
layout: post
title:  "Clean code != well engineered"
date:   2019-02-16
banner_image: light-work.jpg
image: images/posts/light-work.jpg
description: "Being a good craftsman doesn't make you a good engineer. Nor does blindly following Clean Code."
tags: [software engineering, design, modifiability, natuaralness]
img_credits:
    - ["https://unsplash.com/photos/xrVDYZRGdw4", "Émile Perron", "Light work", ""]
---

I've recently re-read [Clean Code: A Handbook of Agile Software Craftsmanship](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882) by Robert C. Martin et al. And, once again, I have mixed feelings about the book.

This post is discussing some weak points of the book.


<!--more-->

**Contents**:
* TOC
{:toc}


## Disclaimer: It's actually a good book

Overall, this is a good book that all software developers should definitely read. It contains a ton of material on how to write better software. However, for the good content in order to be understood, the weak points also need to be analyzed. The purpose of this post is not to analyze the merits---otherwise very well known---of the book.


Big apologies to Uncle Bob and the co-authors for the following critique.

## Main critique

I can generalize my critique of the book in 4 points:
1. Too dogmatic
2. Not balanced
3. Argues for a bad division of complexity
4. The focus seems to be on accidental complexity

Let's analyze these points in detail.

### Too dogmatic
I would expect from a book in software engineering to be written in an argumentative style, bringing a lot of supporting evidence before reaching a conclusion. After all, we are talking about an engineering discipline. Mary Show argues in a [beautiful talk](https://www.youtube.com/watch?v=lLnsi522LS8&t=5s) that engineering is defined by applying scientific knowledge (or systematically codified knowledge, the best we can get at the moment). She explains that engineering is (or should be) two levels above *craftsmanship*. I'm not sure if this is a coincidence, but the subtitle of the book (*A Handbook of Agile Software Craftsmanship*) refers to *craftsmanship* and not to *engineering*.

The book is a collection of best practices. Instead of explaining why those practices are to be followed, it just states them, without providing any arguments.

The main takeaway for an analytic reader would be that the book expresses the *personal beliefs* of the authors and that those things are not generally applicable. It produces an effect of distrust, and actually a disservice for all that good advice that the book contains.

On the other hand, there are some readers who seem to be charmed by the book. They would simply believe in it. The effect of this is that it forms some sort of a *Clean Code* cult; this is highly counterproductive in an engineering discipline.

Also, the book focuses too much on elements of style (for example, it *mandates* the order of declarations in a Java class). This is just it: style. Not everybody writes code in the same style, and there are a lot of arguments that insist that diversity in style is actually a good thing. Imagine what would the literature be today if everyone was writing like Homer.

I strongly believe that mature software engineers should know to ignore stylistic differences in code. Moreover, they should find joy in seeing how the style of a programmer resonates with the type of program that is being solved. (Hehehe, I'm finding myself copying the style of the book. The reader must excuse me for the lack of arguments for this paragraph :blush:).

Some immediate examples that lack proper argumentation:
* functions should be small, and smaller than small; same with classes
* functions should take ideally no argument; maximum is 3
* avoid flag arguments
* avoid switch statements
* etc.


### Not balanced
In general, in software, balance is the key. Everything tends to have pros and cons. There is no such thing as one size fits all. A classic example is that improving efficiency tends to lead to degraded modifiability.

Let us take one example: the book preaches the avoidance of `switch` statements. As a sort of explanation, it's invoked that *it's hard to make a small `switch` statement*. Ok, let's assume that this is a valid argument.

The proposed alternative would be subtype polymorphism. That is, instead of having one switch statement with 5 cases, we would have 1 base class + 5 derived classes. Of course, the immediate question arises: *how would 6 classes be smaller than 20 lines of code?* The book should have provided the answer to this question.

Next, there is another question that this small advice did not cover: the level of details for the generated classes. Taking this advice (and others in the book), the user will end up with classes that span from high-level of abstractions to very low-level abstractions. Of course, a class invented to avoid a `switch` statement would most probably represent a very low-level abstraction. The problem is that there is a huge mental cost to switch the level of abstractions when jumping from one class to another. This disadvantage is not properly explained.

And, of course, there is the performance argument. Polymorphism is typically slower than a well placed `switch` statement (beware, this is not always true).

So, instead of saying, "*there are a lot of times it makes sense to replace a `switch` statement with polymorphism*", with a proper explanation when to use polymorphism and when to use `switch` statements, the text basically imply: "*`switch` statements are the root of all evil*".

BTW. I find the statement "*by their nature, `switch` statements always do N things*" extremely strange. The same thing can be said about a `for` loop.



### Argues for a bad division of complexity

> The first rule of functions is that they should be small. The second rule of functions is that **they should be smaller than that**.

> The first rule of classes is that they should be small. The second rule of classes is that they should be smaller than that.

We would all love for a few classes, with a few functions, and all of them to be very small. But, one cannot create complex projects with this. The complexity of a software system needs to go somewhere. If all the classes are small, and all the functions are small, where is the complexity laying?

Well, the book doesn't provide an answer to this question. And I believe is one of the fundamental questions in software engineering.

To be honest, the [previous post]({{page.previous.url}}) was written just so that I can properly argue this point.

Whenever we divide the complexity of a software system, we need to have a balanced approach: we need to make sure that, at every step, we don't divide the software into too many subsystems, and at the same time in too little subsystems. See the [Grouping of a large number of elements]({{page.previous.url}}#grouping-of-a-large-number-of-elements) section.

If we blindly apply the advice in the books, we will create a huge interconnection mess between classes and functions. Instead of encapsulating some of the complexity into classes and functions, we expose all the complexity and the interconnectivity level.

For example, let's assume that we need to follow a complex flow. Instead of looking just inside the class that encapsulates the flow, the clean coder would have to follow a lot of tiny classes to understand the flow. This, of course, makes it harder to understand the flow.

Also, it's easy to argue that the performance tends to degrade if algorithms are split into very small pieces. Personally, I'm having trouble imagining how most of the well-known algorithms would be implemented decently by a clean coder.

To strengthen my argument, I would like to continue an example given by the book:

> a system with many small classes has no more moving parts than a system with a few large classes. [...] So the question is: do you want your tools to be organized into toolboxes with many small drawers each containing well-defined and well-labeled components? or do you want a few drawers that you toss everything into?

Let's assume that I have 1000 screws of various types and sizes. We have wood screws, machine screws, tag bolts, mirror screws, drywall screws, steel metal screws, twinfast screws, security head screws, hex cap screws, self-drilling screws, fine adjustment screws, etc. For each of these types, we would have multiple sizes.

A clean coder would split all the screws into the smaller possible container. There would not be two types of screws in the same container, and there would not be two different screw sizes in the same container. In the end, the clean coder would spend a lot of time to create more than 100 types of containers. In the vast majority of the containers, there would be only one screw.

A more pragmatic coder would probably organize the screws into something like 10 boxes, each box containing 2 screws that are not the same.

It's much easier to create 10 generally labeled boxes instead of 100 fine-grained labeled containers. Then, when searching for a screw, it's much easier to go directly to the right container if we have 10 containers as opposed to 100 containers.

Also, consider refactoring. If for some reason, we decide to place bolts into containers by age instead of by length, how much re-labeling is needed for 10 containers, and how much for 100 containers?

A purist clean coder would tend to be constantly resorting and indexing screws, while a pragmatic coder would tend to just use the screws to get the job done. (again an over-generalization, in the spirit of the book).


### The focus seems to be on accidental complexity

After the first chapter that describes what *clean code* is, the book starts with a chapter on names. We are informed how names are the pinnacle of software development, we are told that we need good names, and we are told how to make the names pronounceable, how to avoid encodings, mental mappings, and puns, and how to pick names from solution and problem domain names to add meaningful context.

Names are also important in literature. But there we don't reject novels because the characters have names like Lev Nikolayevich Myshkin, Parfyón Semyónovich, Prince S, Princess Darya "Dolly" Alexandrovna Oblonskaya, Dr. Baron Knobelsdorff, Fukikoshi Mitsuru, Leon Płoszowski, Jón Hreggviðsson, etc. We don't have huge debates arguing that the main character needs to be Eva Karenina instead of Anna Karenina, we don't complain about reading unpronounceable names, we don't complain about 1-letter encodings, and we don't even complain if the main characters don't have explicit names.

As the case for novels, names are not the essential part of software engineering (that doesn't mean that we should not care).

After Chapter 3, which is about functions and which are important, Chapter 4 focuses on comments and Chapter 5 focuses on Formatting. Comments and formatting? I hope that everyone agrees that these are not essential problems. Yes, they have an impact on the understandability of the code, but those should not be the focus of software engineering.

As mentioned above, a lot of the advice in the book is purely stylistic. It seems that the vast majority of the book avoids (or gets it wrong) the essence of software engineering: breaking down complexity.


## My experience with clean coders

I believe there are a lot of clean coders that are good software engineers. But personally, I haven't met any -- but don't take me as a good indicator of knowing a very diverse set of coders.

Actually, my experience with so-called clean coders was more negative than positive. They tend to be too dogmatic, not seeing the forest from the trees, tend to think small. They typically make the functions small, just because, even if this would decrease cohesion, increase coupling and break SRP.

Of course, the performance of the code is usually reduced by the strong clean code believers. There are cases in which linear algorithms become quadratic (and even worse) just because we want to keep our functions small, and we break down the problem at the wrong levels.

I would hope that this is just bad luck on my side. But my suspicion is that---because the book is too dogmatic and provides just advice without proper justification---there is a correlation between clean coders and some poor software engineering practices; this could happen because many readers are blindly following the recommendations from the book, without being too critical about the context at hand.


## What I would recommend?

* Read the book; despite my critique above there is still a big set of good advice in it.
* Analyze the pros and cons of each statement. Instead of taking for granted everything, take the opportunity to enhance your analytical skills.
* Always balance things out. There is no such advice that applies in all contexts.
* Use engineering approaches to software. Try to base all your software decisions on some sort of evidence. The evidence can be strong facts (i.e., performance measurements), but also lighter facts such as empirical evidence, historical data, experience, informed judgments, etc.
* Strive to be a better engineer, not necessarily a good craftsman.
* Distinguish between essential issues in software engineering and accidental ones. Focus on the essential things and be more flexible with the accidental ones.
* Embrace the diversity of coding styles. Adapt your style to match the problem you are working on and the environment you are working in.

And, as always, keep truthing!
