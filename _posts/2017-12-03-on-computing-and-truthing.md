---
layout: post
title:  "On Computing and Truthing"
date:   2017-12-03
banner_image: grain-field.jpg
image: images/posts/grain-field.jpg
description: What does it mean to 'know' in computing? Is it universal, is it too relative? I need to start truthing
tags: [computing, truthing, epistemology, computer science, knowledge, relativism]
---

The first time I've met a computer I was 10. It wasn't love at first sight, but very soon the relationship turned into a steady long-lasting one. While other kids of my age were playing games, I was trying to program small games. I've been a programmer since then; I've got my first programming full-time job while I was still 18 -- that was over 15 years ago. I've later become a proper software engineer, and then a computer scientist (with a PhD in programming languages).

Over the years, I've gathered some knowledge about programming and computer science. At the same time, I've come to know much better the things that I don't know, even in fields in which I'm supposed to be an expert (the so-called [Socratic paradox](http://en.wikipedia.org/wiki/I_know_that_I_know_nothing)).

This post is about what I know, what I don't know, and about how to know if I know a subject. And above all, about the process of knowing. Mostly related to computing.

<!--more-->

## Knowledge in computing

Computer science can be divided in two branches: theoretical computer science and applied computer science. The theoretical computer science deals with formal properties of computer systems. When you read _formal_, think of definitions, lemmas and theorems; just like in mathematics. We say that it's a [formal science](http://en.wikipedia.org/wiki/Formal_science). The applied part of computer science uses all the findings of the theoretical computer science for solving practical problems. It is not as formal, but still is far away from social sciences.

The entire computer science is built on top of logics. Everything needs to follow a set of rules. In essence, computers don't like ambiguity and interpretations.

As a consequence, we associate computer science and programming with hard facts and exactitude. Similar to mathematics, computer science and programming must be discussing about **universal truths**.

For simplicity, from now on, I'll use the term _computing_ loosely to represent both _computer science_ and _programming_.


## The problem

Universal truths in computing? Good joke! :laughing:

Let's take a few examples:
1. **static languages** vs **dynamic languages**. Can somebody say nowadays that one category of programming languages is definitely better than the other?
1. on a similar note, **Java** vs **C#**?
1. **OOP** vs **functional programming**?
1. **Scrum** vs **Waterfall** vs **RUP**?
1. what's the best compromise between **performance** and **modifiability**? (please note the use of the word **compromise**)
1. can somebody please define what **extensibility** really means?

It seems like we don't have good answers for important questions in computing. The science behind computing guarantees the correctness of some algorithms or some methods, but it doesn't consider the _appropriatnesss_ of a technique; it doesn't consider the _human factor_ of computing.

Everything seems to be relative; too many points of view. But how can we assess them? We can't just give up! We need a framework for helping us take the right decisions.


## Enter _knowledge_, enter _truth_

We are now concerned with how do we acquire _knowledge_; the object of study for [epistemology](https://plato.stanford.edu/entries/epistemology/).

Without going in too many technicalities, let's take a proposition as a running example: "__static languages are better than dynamic languages__". The two main questions we need to ask are: is this knowledge (as opposed to a mere belief, or falsity)? how can we arrive to this conclusion?

For a proposition to be considered knowledge, the following 3 things need to hold:
1. the proposition needs to be true
1. the proposition needs to be believed (by its originator) -- you cannot count as knowledge something in which nobody believes
1. the originator of the proposition must be justified in his belief, by some kind of proof or reasoning

The second point is obvious. Two millenniums of epistemology haven't yet come to a good understanding of the third point; we still debate what does count as a good _justification_. Does making a merely plausible argument count as a good _justification_? We don't quite know. But let's assume that there is a limit of argumentation that one needs to make to _justify_ a belief.

To me, especially in computing, the first point is way more problematic. What does it mean for a proposition to be true? It's easier to determine whether "yesterday it rained in Sahara" is true or not, but how do you analyze the truth of a complex proposition that has subsumed a lot of consequences? It may not be even possible to enumerate all the consequences of such a complex proposition.

For example, what do we mean by "__static languages are better than dynamic languages__"? How many aspects should we consider? Better in terms of safety? What does safety means? How many types of errors do static languages detect? Is there a lower bound and an upper bound? Does it apply to all the programs the same way, or does it depend from program to program? And the list can go on forever.

The first major obstacle in the way of acquiring knowledge.

## Using the knowledge

Now, let's assume that we find some magic algorithm to avoid these inherent problems of truth and knowledge. We somehow find a framework for judging the truth value of propositions; most probably we define the problem inside a system of examples, and we use some kind of _expert system_ to classify our propositions.

But even if we have this method of determining the truth value of propositions, we can only do that **in certain contexts**. Here, I want to stress some more on the context part.

The fact that "static languages are better than dynamic languages" is a true proposition in a given context, doesn't tell us how we can use this knowledge to deduce other facts.

Coming back to our main proposition, it is not apparent how this proposition is related to "_desigining static languages is more important than dynamic languages_". Depending on the context in which we deduced the validity of the first claim, we can argue for and against the latter claim.

For example, if the context of our deduction includes things like _resulting programs are better_, _usability_, _performance_, etc., then we probably could argue for the second claim. If the reasoning for which the first proposition is true is based on the fact that "_we don't know how to build efficient/safe/better dynamic languages_", then we can argue that the latter proposition is false, and we should put more effort in designing dynamic languages.

Basically, all the nitty-gritty details of the reasoning corresponding to the first proposition need to be carried over in the argumentation for the second proposition. Each time we reason for another proposition we need to carry more and more details. Very soon it becomes very hard to argue anything.

If you find the above reasoning too convoluted, let me recapitulate the main problems of knowledge we've discussed:
* it's hard to determine which propositions constitute knowledge
* if some propositions hold (in some contexts), it's hard to use them to deduce the truth values of other propositions


## Towards a relativistic truth?

At this point, you may think that I'm nitpicking over what knowledge means, and that, in general, things are not that bad. If that's the case, you may be surprised to know that humanity abandoned the concept of _universal truth_ for some time. This departure is at the core of [postmodernism](http://en.wikipedia.org/wiki/Postmodernism)) and especially at the late [relativism](https://plato.stanford.edu/entries/relativism/).

As Nietzsche famously puts it:
> There are no facts, only interpretations. <cite>Friedrich Nietzsche</cite>

Ok, but what does that mean to us? Can we simply say that, for me, static languages are better, while for you, dynamic languages are better? That there is no trace of objective truth?

If that would be the case, then any reasoning would disappear, and every argumentative discussion in computing would become like religion: _your religion is true; until you start describing it to me_ -- a taboo.

Another way to put it: can we never have a rational discussion about Android vs iOS?

If that's the reality, I want out.

## Truthing: reconstructing the lost Truth

In the last period of time it has become evident to me that we need to rebuild the idea of an independent and impartial Truth, despite all the acquisitions of postmodernity. Both in professional and in personal life.

How can we make progress in computing without the ability to objectively judge a system/proposition? How can we become better persons, if we've lost the ability to know what _good_ is?

I don't claim that I have the solution for it. I don't. In fact, what **I do know** is that **I do not know** what truth it (thank you, [Socrates](http://en.wikipedia.org/wiki/I_know_that_I_know_nothing)).

However, I have some starting ideas:
* we need to apply critical thinking; don't believe everything that you are told
* theory can be a savior for practice (if applied judiciously)
* searching for general principles can bring light into a messy problem
* repetitive inductions/deductions can help in focusing on correctly assessing a system

To me, the Truth has stopped to be universal, has stopped to be relative, it became a process. I need to start **truthing**.

Keep the faith!
