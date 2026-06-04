---
title: A Tangled.org Deploy Script for Cloudflare
pubDate: 2026-06-02
description: Deploy your static content to Cloudflare with Tangled.org CI workflows. Goodbye, GitHub Actions.
slug: tangled-cloudflare-deploy
status: published
standardDocId: 3mnd37gw6ukup
blueskyId: 3mnd6esklak2o
heroImage: "grid-1.jpeg"
tags:
  - ops
  - atproto
---

[Tangled.org](https://tangled.org) is an atproto-powered git collaboration site. It's like GitHub, without the bloat and Copilot shoehorned in every corner.

I've been doing [some](/lab/puzzmo/) [experiments](/lab/pindrops-an-experiment-in-atproto-svelte-maps-wip/) building atproto tools, and [sampling](https://sifa.id/p/cbennell.com) the [ecosystem](https://grain.social/profile/did:plc:wkqtjo7h6w64nbe7aelfenuo), and I've been eager to explore Tangled. I've been equally eager to migrate some of my content away from GitHub, as it has been increasingly unreliable and unpleasant to use.

I host a lot of my static content on Cloudflare Workers (formerly "Pages"), and I rely on git-based CI process to build and deploy to Cloudflare. Cloudflare has tight integration with GitHub, so you can set up push-based deployments and preview environments without needing to think about it. With Tangled, we need to build that bit ourselves.

Fortunately, the Tangled CI config is quite straightforward. I've set up CI configs to deploy to production when I push to `main`, and to create preview environments when I create pull requests.

## Prerequisites

For this to work, we need a few things. First, we add Cloudflare's CLI, wrangler, to the project dependencies (not devDependencies), so it will get installed with the other packages requied for the build.

We also need to add two CI secrets in the Tangled repo settings. These should be named `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`. The [Cloudflare docs](https://developers.cloudflare.com/workers/ci-cd/external-cicd/gitlab-cicd/) explain where to find the values for these variables.

These scripts assume we can use `npm run build` to build our site (outputting to `/dist`), and we have a [wrangler.jsonc](https://developers.cloudflare.com/workers/wrangler/configuration/) file with some basic configuration. Here's mine:

```json
{
  "name": "cbennell-com",
  "compatibility_date": "2026-05-02",
  "assets": {
    "directory": "./dist",
    "not_found_handling": "404-page"
  },
  "preview_urls": true
}
---
wranger.jsonc
---
```

And of course, we need a Cloudflare Workers project already set up.

## The scripts

### Deploy to Production

```yaml
when:
  - event: ["push", "manual"]
    branch: ["main"]
engine: "nixery"
dependencies:
  nixpkgs:
    - nodejs
steps:
  - name: "Install dependencies"
    command: "npm ci"
  - name: "Build"
    command: "npm run build"
    environment:
      NODE_ENV: "production"
  - name: "Login to Cloudflare"
    command: "npx wrangler login"
  - name: "Deploy"
    command: "npx wrangler deploy"
---
.tangled/workflows/deploy.yml
---
```

### Deploy Preview Enviroment for Pull Requests

```yaml
when:
  - event: ["pull_request"]
    branch: ["main"]
engine: "nixery"
dependencies:
  nixpkgs:
    - nodejs
steps:
  - name: "Install dependencies"
    command: "npm ci"
  - name: "Build"
    command: "npm run build"
    environment:
      NODE_ENV: "production"
  - name: "Login to Cloudflare"
    command: "npx wrangler login"
  - name: "Deploy"
    command: "npx wrangler versions upload --preview-alias ${TANGLED_PR_SOURCE_BRANCH}"
---
.tangled/workflows/deploy_preview.yml
---
```

A cool feature of Tangled is that when you push commits that trigger CI runs, the remote will reply with a SSH command you can run to watch the CI log, right in your terminal.

## The Future?

I'm not yet certain how much I will be migrating away from GitHub. There's some stuff that still needs to live there, and it's not ideal to have my work scattered across platforms. This is an experiment, to learn about the experience.

Tangled.org is not even a year-and-a-half old at the time I'm writing this. I'm not certain it will emerge as the successor to GitHub, and there are other platforms, like [CodeBerg](https://codeberg.org/) that are getting some attention. We will see what happens. But atproto is such an exciting technology. I'm really enjoying watching it develop, and I'll have more to say about this soon.
