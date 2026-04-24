---
title: "I Tried Three CSS Frameworks So You Don't Have To"
pubDate: "2024-11-25T17:13:00.000Z"
description: "I tested OpenProps, Bulma, and TailwindCSS while migrating to Bridgetown, and found they fall on a revealing continuum from pure CSS custom properties to all-in utility classes. Here's what I learned about each approach."
slug: "three-css-frameworks"
status: "published"
heroImage: "../../assets/images/grain-blue.jpeg"
tags:
  - "css"
  - "tailwindcss"
  - "bulma"
  - "api"
---

As part of my recent migration from WordPress to Bridgetown, I investigated three CSS frameworks to build my frontend. I spent some time with each, building out parts of my design. As I investigated, I noticed an interesting pattern emerge: these frameworks can be assessed based on their reliance on utility classes vs CSS rules. The three frameworks I assessed formed a nice range on this continuum.

## Open Props

At one end of the spectrum, [Open Props](https://open-props.style/) relies entirely on CSS custom properties. There are no class name hooks provided, so you're using the framework entirely within your CSS files. You do, of course, need to add class names to your HTML elements so you have some hooks on which to hang the custom. An example:

```html
.card { border-radius: var(--radius-2); padding: var(--size-fluid-3);
box-shadow: var(--shadow-2); } ...
```

OpenProps can be used with no build process using the CDN, or you can use tools like PostCSS to import only the properties you actually need.

I appreciate how a pre-built, thoughtful set of [design tokens](https://www.contentful.com/blog/design-token-system/) promotes consistent design and provides a great starting point. OpenProps is just CSS, so you're not mooring yourself to a specific tool chain. The defaults are quite nice, and include some [pretty gradients](https://open-props.style/#gradients) and [masks](https://open-props.style/#masks).

The downside to this approach is that you're responsible for naming all your components, and there's a lot of back-and-forth between your markup and your CSS. There are no pre-built components here, so if you're looking for a UI library, this is not it. I did not love the documentation, and I had a hard time figuring out how I was supposed to be using it: the concept is simple, but it's not really laid out anywhere in their documentation. I think they could use a better "Getting Started" section.

## Bulma

[Bulma](https://bulma.io/) is a more fully-feature library, including a range of components, like the drop down menu. It's an alternate take on Bootstrap, with a few modernized features, but lacking some of the maturity.

I think Bulma would be a bit easier to learn than Bootstrap, but I'm don't see that Bulma offers a huge amount of value over Bootstrap, considering that Bootstrap offers more features and better accessibility (according to Bulma's [own comparison](https://bulma.io/alternative-to-bootstrap/)).

I think Bulma is a good project and could be a good fit for people building UIs, and prefer its approach over Bootstrap. The documentation is great, and I can see the appeal of this library.

Bulma is in the middle of the "utility-vs-css" spectrum: it offers helper/utility classes, but you still need to add class names as CSS hooks. This is perhaps the worst of both worlds: it's unclear where a particular CSS property might be defined: as a helper class, or in you own CSS. You're going to be mixing framework classes and your custom class names in the same HTML element.

## TailwindCSS

Finally, we have [TailwindCSS](https://tailwindcss.com/) coming in at the "all-utility" end of the spectrum. Much has been written about Tailwind's approach, so I won't rehash it.

Like many people, I was sceptical about the idea of cluttering my HTML with big fistfuls of utility classes. My project was a blank slate, and I had a dream of clean, unadulterated markup. I didn't want multi-line lists of classes marring that. But here's the thing: you're going to be adding class names into your project anyways; maybe even extra HTML elements to make your layouts work. Your markup is always going to need concessions to your CSS.

For a project like mine, where I build the layout once and my day-to-day interactions don't really touch the HTML (Markdown, baby!), this approach makes sense. I can embed a bunch of classes into my markup and never have to open a CSS file. There's no need to name components, and there's no ambiguity about where the styles are defined.

I think this approach would shine in component-based projects, such as those using [Phlex](https://www.phlex.fun/) or [ViewComponent](https://viewcomponent.org/). However, the more often you need to interact with the HTML, the less appealing this approach is.

## Wrap Up

For this project, TailwindCSS proved to be the best fit. It clicked immediately, and I was able to build my design with good velocity. But I recognize that it’s not the right choice for every project.

Exploring these frameworks was a valuable exercise. As someone who primarily works on back-end development, this experience provided a deeper understanding of these tools, and I enjoyed learning more about the these tools which I have been hearing so much about.
