---
title: "Migrating from Wordpress to Bridgetown"
pubDate: "2024-10-26T04:00:00.000Z"
description: "I've used WordPress for many years. It no longer suits my needs as well as it used to, so I've been investigating alternatives, inlcuding migrating this site to Bridgetown, a Ruby-based static site generator. And the switch feels principled and liberating."
slug: "migrating-from-wordpress-to-bridgetown"
status: "published"
heroImage: "../../assets/images/grain-color-1.jpeg"
tags:
  - "bridgetown"
  - "wordpress"
  - "diy"
  - "#Import 2026-02-12 04:57"
---

This is my first post after moving my site to a new architecture. After using WordPress for 18 years across various projects—including this site’s previous version—I’m migrating to statically generated content with [Bridgetown](https://www.bridgetownrb.com/).

This change follows [my WordPress migration](https://cbennell.com/posts/running-wordpress-multisite-on-hetzner-with-custom-domains/) to Hetzner. So why leave WordPress after completing that process?

There are a few reasons. First, I wanted to learn something new. It’s been a while since I’ve gotten my hands dirty with a full front-end build, and I was looking for an excuse to experiment with some front-end frameworks (more on that later).

There’s also something liberating about shedding the weight of a full PHP stack for simple, static HTML. This follows my recent move to self-hosting on Hetzer, to create a real sense of ownership and freedom over my content. I’m still hosting on Hetzner because I’m still running other apps on this machine. But having static content allows for hosting for free on any number of providers. It’s quite wonderful that with a bit of know-how, one can host a rich, static site for only the cost of the domain–about $10 CAD per year.

And then there’s the [recent Wordpress controversy](https://techcrunch.com/2024/10/12/in-latest-move-against-wp-engine-wordpress-takes-control-of-acf-plugin/). Others have explained the issues [in detail](https://world.hey.com/dhh/automattic-is-doing-open-source-dirty-b95cf128), but as a proponent of open source software, I recognize the important role it plays in our society. The commandeering of the ACF plugin was a very troubling action, and this was the thing the pushed me to take this switch.

I don’t think Wordpress is going anywhere, despite the troubling behaviour of its leadership. I still think it’s a great product and the correct choice for folks who want an easy to use CMS without any web development knowledge. I’m still running WordPress sites for non-technical clients, and I would still recommend it in many cases. But for someone like me, who can handle a few markdown files and some deployment automation, this is better aligned with my principles and how I want to work.

## Tools Used

There are several Wordpress-to-Markdown tools out there. I used [this one](https://github.com/lonekorean/wordpress-export-to-markdown), which worked well for me. It generated the post Markdown files with appropriate file names and good content, and it grabbed all my images. I did need to go though all my posts to fix the front matter and do a general proofread pass. My [Code Block Pro](https://wordpress.org/plugins/code-block-pro/) blocks came out as Markdown code blocks (```). Otherwise, the content migration was very painless.

I’m using [TailwindCSS](https://tailwindcss.com/) as my front-end framework, with the [Typography](https://github.com/tailwindlabs/tailwindcss-typography) plugin. I’m also using [Kamal](https://kamal-deploy.org/) to deploy my site.

## Why Bridgetown?

I knew I wanted to use a static site generator. I wanted something written in Ruby, so I would feel comfortable extending the tools if needed. I never got into Jekyll during its heyday, and although it’s still actively maintained, I was interested in something more modern and flexible.

I had heard about Bridgetown on various newsletters, and I did a little digging. Originally a Jekyll fork, Bridgetown has since grow into a more sophisticated project. One aspect I like about Bridgetown is the possibility to do server-side rendering alongside the static content, if I ever have a project that requires it. It’s in active development, with version 2.0 approaching. It offers a lot of flexibility and customization, and seems like a great fit so far!

## Why Tailwind?

I spent a lot time considering and testing my options for a fronted framework. I have a long history with Bootstrap, which I think remains a solid choice. But it was overkill for my needs on this project. Plus, I was looking for an excuse to learn something new.

I explored [Open Props](https://open-props.style/), [Bulma](https://bulma.io/) and [TailwindCSS](https://tailwindcss.com/). I plan to expand on this decision later, but it came down to this: the biggest problem with Tailwind is that it fills your HTML with many, many classes. I had a vision of clean, minimal HTML with only a small sprinkling of ids and classes. After a bit of time with other frameworks, this vision proved a fool’s errand. I was adding extra classes, IDs and HTML elements to satisfy the framework regardless. In some cases the frameworks had me adding custom classes to hang CSS rules from, *in addition to* utility classes on the same element. So I’m in the position of defining my presentation in two different places. Tailwind’s approach makes sense—it centralizes all styling in HTML classes, eliminating the need for custom CSS files altoether.

## I Like SSG

Switching to Bridgetown has been both a satisfying technical exercise and a refreshing change in how I manage my content. Static generation isn’t for everyone, but for those with a bit of knowledge and a desire to shed the bulk of traditional CMSs, it’s well worth exploring. I look forward to refining this setup even further, experimenting with new tools, and sharing what I learn along the way. For now, I’m thrilled with the simplicity, speed, and freedom this new architecture brings to my site.
