---
title: 'On "Layered Design for Ruby on Rails Applications"'
pubDate: "2024-04-28T02:11:00.000Z"
description: "From DDD-inspired architecture to patterns like query objects and service layers, Dementyev’s book explores how Rails apps can evolve stronger abstractions over time. Ideal for developers who want to move beyond basics and design with clarity and intent."
slug: "on-layered-design-for-ruby-on-rails-applications"
status: "published"
heroImage: "mylar-1.jpeg"
tags:
  - "books"
  - "application design"
  - "rails"
---

[Layered Design for Ruby on Rails Applications](https://www.packtpub.com/product/layered-design-for-ruby-on-rails-applications/9781801813785) (By Vladimir Dementyev, published by Packt August 2023) discusses advanced topics in Ruby on Rails application design.

The core of the book, as can be gathered from the title, is the concept of _layers_. Dementyev actually uses _layer_ in two different ways:

## Architectural Layers

Architectural layers are high-level categories for application components. The application layers discussed in the book are borrowed from [Domain-Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design) concepts:

- Presentation: Rendering the UI and handling user input.
- Application: Applying structure to other domain objects to handle requests or commands.
- Domain: Business logic and application state.
- Infrastructure: Interacting with external services and resources.

Concepts from DDD are explained, like the principle that low-level layers should not depend on higher levels, and implementation details shouldn’t leak between layers. For example, a domain object shouldn’t contain code that is specific to the presentation layer.

## Abstraction Layers

An abstraction layer is a pattern or solution to a common problem that has evolved into a convention or a well-defined subsystem. For example: [Query Objects](https://thoughtbot.com/blog/a-case-for-query-objects-in-rails), an approach to managing complex database queries in the domain layer. Capturing these conventions into patterns has clear advantages: by giving them an API, the patterns become self-documenting, discoverable, well-defined responsibilities.

One idea in the book I appreciated was the idea of growing into your abstractions, allowing them to emerge from your code over time. The trick is recognizing when it’s time to extract an abstraction from existing code. One indicator is when an object’s responsibilities stretch across architectural domains. Dementyev describes the infamous _Service Layer_ as a kind of waiting room for abstractions that have yet to reveal themselves.

## What Else?

The book starts with analysis of some core Rails components and the design decisions behind them. This analysis lays groundwork for later chapters which discuss additional abstractions that help shore up Rails’ shortcomings.

Dementyev does a great job presenting patterns for OO application design. These examples follow a formula: start with an example of the problem, implement a naive solution, evolve into a more elegant solution, then turn that solution into an abstraction. There are also many references to excellent gems that have implemented these solutions.

A lot of these design ideas will be familiar to anyone who has done much reading about designing Rails applications. For example, “use model callbacks sparingly”. But the book well explains the nature of these problems, and describes the path to the elegant solutions.

Overall, this is a good read full of great concepts for Rails app developers. I would recommend this book to folks who are have a good grasp of Rails basics and are ready to level up.
