---
layout: post
title:  "Turtles All the way Down!"
date:   2020-10-03
banner_image: turtles.jpg
image: images/posts/turtles.jpg
description: "When taking about the amount of decomposition we use in software, it's turtles all the way down"
tags: [design, software, decomposition, architecture]
img_credits:
    - ["https://unsplash.com/photos/H1gBvc2MWvk", "Chastity Cortijo", "11 Turtles on a lake 11 Turtles on a log", ""]
---


I recently had a debate with one colleague about the distinction between architectural design and detail design. Given an element in our software, how do we determine whether that element is an architectural element, or not?

<!--more-->

My colleague would argue that if you can subdivide the element, it is an architectural element, and thus it needs to be captured in the architectural design. If the item cannot be (reasonably) subdivided is not an architectural element, and it needs to be part of detail design.

While this argument is valid when looking from a particular point of view, I think it is mostly misleading and can do more harm than help.

## I have a hammer
If there is one tool that software engineers use above everything else, then that would be decomposition. We use it everywhere: from breaking down large systems into smaller ones to breaking down functions into instructions.

Let's take a simple example: we have a web application. For the well-functioning of this application, we have two types of components: software components and non-software components (hardware, peopleware, processes, etc.). There is a first-level decomposition. Looking just at the software side, we probably can divide it further into four major components: web client, frontend, backend and database. If the backend is more monolithic, then perhaps it can also be subdivided into parts. If the backend application is relatively big, then we can expect to be able to divide it even further; sometimes we can do that on several more levels. In the end, we reach a relatively small logic corresponding to a functional requirement (e.g., to process a batch of items). Also, most probably, this logic can be furthermore divided, as we typically need several classes to implement it (I assume an OOP approach here, but the argument is the same on functional programming). At this point, the reader may consider the classes as atomic units that we cannot break down any further. But this is false: a class has typically multiple attributes and multiple methods; they are subdivisions of the class. And, going even further, any function can be divided into statements and expressions, and most probably most of them will expand into multiple assembly instructions. The reader surely sees my point now.

There is an awful lot of decomposition in any software project. Some of it may be intentional, and some of it unintentional. Some of it may be a good decomposition, and some of it may just be bad decomposition. But one thing is certain: decomposition is everywhere.

At all the levels, we, as software engineers, are applying decomposition. We should be called *full-stack decomposers*.

## What is *software design*?
Before trying to answer what *architectural design* is, we should consider first what *design* is. There are more formal definitions of software design, but I would just attempt to craft an informal one:

> **Software design** is the activity of selecting solutions for a software problem, or defining constraints that narrow down the possible solutions

For the above example of a web application, the decision to have a frontend and a backend is a constraint on the solution space; it is not the complete solution, but a narrowing down of possible solutions. Similarly, when we break the backend into several components, we are further narrowing down the solution space. The point is that at any level we use decomposition as a form of a design decision.

So, every time we are using decomposition, we are doing a typical design activity. If we are breaking a function int two parts, we are doing a design activity.

## What is *software architectural design*?
First, as the name suggests, it’s a form of software design. It aims at constraining the space of solutions for our problem.

Let’s look at a definition of *software architecture* ([link](https://www.amazon.com/Software-Architecture-Practice-3rd-Engineering/dp/0321815734/)):

> The software architecture of a system is the set of structures needed to reason about the system, which comprise software elements, relations among them, and properties of both.

This definition doesn’t say anything about the granularity of the structures that are needed. One software architecture may contain coarse-grain structures, while another software architecture might be more fine-grained. If it helps us reason about the software system, it’s software architecture.

So, the software architectural design must be the design activities that lead us to software architecture.

Here, it’s important to notice that it would be bad if we cannot make any distinction between *architectural design* and simple *software design*. If that were the case, then there is no point of distinguishing between architecture and the software itself. If we cannot reason about the general properties of a software system without considering all the details (to function level), then we are in a bad position. Therefore, *architectural design* must be done at a higher level than *software design*.

Another school of thought tries to define software architecture as important design decisions. To quote Martin Fowler ([link](https://martinfowler.com/ieeeSoftware/whoNeedsArchitect.pdf)):
> Architecture is about the important stuff. Whatever that is.

Once again, that rule-of-thumb of my colleague is proven invalid.

With that, I would argue to try to define a border between what is architecture and what is not in a way that is specific to the software project considered. For us, the best division would be at a set of high-level components. Yes, those components have sub-components, but that doesn’t matter that much. That’s an implementation detail of every particular component.

If we look just at the ability to decompose, it’s turtles all the way down!
