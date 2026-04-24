---
title: '"Every Layout" Mixins'
pubDate: "2026-02-04T17:38:38.000Z"
description: "Every Layout is a collection of composable CSS layout patterns. Here's how I've extracted them into a reusable pattern library I can use in any project."
slug: "every-layout-mixins"
status: "published"
heroImage: "AdobeStock_1884449252.jpeg"
tags:
  - "css"
  - "frontend"
---

There's a great feeling I get when I find a resource that presents elegant, comprehensive solutions to a problem; something that allows me to say "Good: I know how to do this properly now."

[Every Layout](https://every-layout.dev/) is such a resource for me. It presents composable CSS "layout primitives" that can be used to build... well, it's in the title. It also includes a series of articles explaining the principles behind the design decisions ("rudiments"); great reading if you want a deeper dive into the concepts.

The site you're reading now was built with several of the patterns in the small but comprehensive list. To make using these layouts easier, I extract them into reusable [PostCSS Mixins](https://github.com/postcss/postcss-mixins). This provides a library of layout patterns that I can apply to any element just by calling the mixin. It has become one of the first things I import into new projects.

Here's an example of the [Stack](https://every-layout.dev/layouts/stack/) layout, a way to apply margins to elements in their block flow direction (chosen from the list of layouts you can access without purchasing).

```css
@define-mixin stack $margin {
  & > * + * {
    margin-block-start: $margin;
  }
}

/***/

article-list {
  @mixin stack var(--s2);
}
```

And a slightly more complicated example, the [Sidebar](https://every-layout.dev/layouts/sidebar/).

```css
@define-mixin sidebar $basis {
  flex-basis: $basis;
  flex-grow: 1;
}

@define-mixin sidebar-content $min-inline-size {
  flex-basis: 0;
  flex-grow: 999;
  min-inline-size: $min-inline-size;
}

@define-mixin sidebar-parent $gap {
  display: flex;
  flex-wrap: wrap;
  gap: $gap;
}

/***/

body {
  @mixin sidebar-parent 2rem;
  padding: 2vw;
}

body > header {
  @mixin sidebar 20rem;
}

body > main {
  @mixin sidebar-content 50%;
}
```

These mixins are trivial to extract from the code provided by Every Layout.

I highly recommend [giving it a glance](https://every-layout.dev/) if you’re looking for an elegant, composable approach to building all your CSS layouts.
