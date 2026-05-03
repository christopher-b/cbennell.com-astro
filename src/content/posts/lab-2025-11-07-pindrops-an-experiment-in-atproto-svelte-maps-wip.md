---
title: "PinDrops: an experiment in ATProto / Svelte / Maps"
pubDate: "2025-11-07T20:56:45.000Z"
heroImage: "pindrops.png"
description: "An ATProto application. Add pins to your map."
slug: "pindrops-an-experiment-in-atproto-svelte-maps-wip"
status: "published"
section: "lab"
---

I built [PinDrops](https://pindrops.app/) ([repo](https://github.com/christopher-b/pindrops)) as an excuse to learn AT Protocol and Svelte/Kit.

ATProto is a very exciting technology. Dan Abramov has written a few [excellent](https://overreacted.io/open-social/) [primers](https://overreacted.io/where-its-at/) on the topic. ATProto inverts the power structure of traditional social media platforms by giving people ownership over their own content. The graph of posts, follows, likes, etc live on the open web. Even better, a person can give permission to any application to modify their data, allowing developers to build on top of the protocol. The entire data graph lives in the open, and can be read without authentication.

I had also been hearing a lot of good thing about Svelte and SvelteKit, so I was eager to build something with it to give it a try.

So I built PinDrops. The concept is simple: add pins to a map. Your pins could be places you've visited, places you want to visit, or whatever you like. Pins are stored in your ATProto personal data store, under the "app.pindrops.pin" schema.

PinDrops is very much a work in progress and has many rough edges, but as a proof of concept, it exists and it works.

## Update: Feb 19th, 2026

PinDrops has been sitting untouched for several months. I've had a list of thing to polish and features to add, but haven't had the time or will to address them. I really wanted to get these things done so I could call the project "finished" (to a degree).

Yesterday, I decided to let an LLM take a crack at these features. After a few hours of prompting and backgrounding, the work was done and the features were ready. And I have mixed feelings about that.

PinDrops was written almost entirely by hand, and I felt good about the quality of the project, at least for tech that was new to me. I felt I had written idiomatic code and come up with elegant solutions to some of the design challenges.

I had code I was proud of. I have no idea how it works anymore. There's so much new code across the project, and I don't have any sense of whether it's idiomatic, efficient, elegant, correct or even necessary. I only know that it appears to work.

I would never work like this on a professional project, nor on something with a server-side component where security is a concern. Maybe this is OK for a hobby project. I would probably never have implemented my wish list otherwise. But I can't help feeling that I've somehow ruined something that I was proud of. Maybe I should have slowed down and worked through the process more carefully, but at that point, why not do it by hand?
