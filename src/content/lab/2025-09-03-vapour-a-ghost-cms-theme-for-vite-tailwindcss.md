---
title: "Vapour: A Ghost CMS Theme for Vite & TailwindCSS"
pubDate: "2025-09-03T18:22:00.000Z"
description: "Vapour is a Ghost CMS theme with support for Vite & TailwindCSS. I breakdown the obstacles for using these technologies together, and how I built a solution."
slug: "vapour-a-ghost-cms-theme-for-vite-tailwindcss"
status: "published"
tags:
  - "lab"
  - "#Import 2026-02-12 04:57"
---

When I started building a [theme](https://github.com/christopher-b/cbennell.com-ghost) for my [Ghost](https://ghost.org/) site, I wanted all the benefits of a modern front-end tool set. For me, that meant [Vite](https://vite.dev/) and [TailwindCSS](https://tailwindcss.com/) (although I ended up [ditching Tailwind](https://cbennell.com/posts/site-redesign-postmortem/) halfway through). It turns out there are some hoops to jump through to get a good experience using Vite with Ghost. I thought it would be worthwhile sharing my solutions, so I packaged them as a standalone Ghost theme: [Vapour](https://github.com/christopher-b/vapour).

(Keep mind, Vapour has a functional but unadorned visual style, but the point is that it is a starting point for using the Ghost + Vite + Tailwind workflow, meant to be customized with your own design.)

There are a few problems we need to solve when using Vite with Ghost:

- Ghost and Vite both provide their development servers, but we point our browser at the Ghost server in development. This means we need to load the Vite client and JS entrypoint in development, but we load built assets in production. Since Ghost doesn't seem to expose a way to determine environments, we solve this by introducing a development_mode custom setting. We turn it on in our development environment and leave defaulted to off in production.
- We want to include built assets bundle in our production deployments, which means we can't hard-code built asset filenames in our templates. We solve this with a custom Vite plugin that reads the Vite asset manifest and outputs dynamically-generated Handlbars templates that include the assets listed in the manifest. We can include these templates in our layouts, using the development_mode setting to ensure they're only loaded in production.

This setup provides hot module replacement and automatic reloads (even on changes to your Handlebars files)

A note about cache busting: Ghost handles assert version automatically using the `{{asset}}` helper, so we don't *need* to use Vite's fingerprinted filenames; we could just output static assets and skip the whole manifest-scanning-partial-generation thing. But I like the flexibility it grants: we can load whatever Vite outputs without modifying our templates manually.

We get full Tailwind support, PrismJS code syntax hightlighting (if you're into that kind of thing) and a GitHub deploy action to update your production site automatically.

[Check it out](https://github.com/christopher-b/vapour), kick the tires, let me know what you think.
