---
title: "Honeybadger Deploy Notifications with Kamal Hooks"
pubDate: "2025-03-17T16:17:00.000Z"
description: "A solution for reporting Kamal deployments to Honeybadger using Kamal post-deploy hooks."
slug: "honeybadger-kamal-hooks"
status: "published"
heroImage: "grain-color2-1.jpeg"
tags:
  - "kamal"
  - "ops"
---

I recently migrated a Rails app to deploy with [Kamal](https://kamal-deploy.org/) on GitLab CI. I wanted to share a few quirks related to [Honeybadger](https://www.honeybadger.io/) integration. This was mostly an out-of-the-box Kamal configuration, using a Dockerfile similar to what ships with Rails 8.

## Reporting Deploys

Honeybadger can [track your deployments](https://docs.honeybadger.io/guides/deployments/), which can help correlate errors to code changes. There are many ways you might go about setting up deploy notifications, but I had a few requirements in mind that narrowed down the options:

- I wanted to use a Kamal post-deploy hook, rather than extra steps to my CI job. This ensures deploys are reported even if the CI process changes (well, to an extent: I'm using GitLab-specific env vars, see below).
- I wanted to use the Honeybadger API key stored in Rails credentials rather than duplicating the key in my CI configuration. This meant running the command in the context of a Rails environment.

A key constraint here is the execution context of the Kamal hooks in the CI environment: when the hook runs, it's running on the CI build host rather than within the application container. This means that it doesn't have your gems installed unless specifically told to install them, which would increase the excecution time of the deploy job. No gems means no Rails, so we can't access the encrypted Honeybadger API key.

### Solution: Kamal Alias

To address these requirements, I put the actual reporting command into a Kamal [alias](https://kamal-deploy.org/docs/configuration/aliases/). Alias tasks run on the application containers. I can then call that alias from the post-deploy hook. This runs the task on one of the just-deployed production containers (the jobs container, in this case) which has access to the Rails credentials to load the API key. It also introduces a bit of abstraction around the parameters supplied to the deploy command.

```yaml

---
aliases:
  record-deploy: >
    app exec --reuse --roles=job 'bundle exec honeybadger deploy
    --user ""
    --repository ""
    --revision ""'
```

config/deploy.yml

```bash
#!/bin/sh
DEPLOY_USER=$CI_COMMIT_AUTHOR \
  DEPLOY_REPO=$CI_PROJECT_URL \
  DEPLOY_REVISION=$CI_COMMIT_SHA \
  kamal record-deploy

```

.kamal/hooks/post-deploy

Since Kamal configuration doesn’t support direct environment variable expansion, we use ERB interpolation to extract the values from environment variables. These variables are then populated using values supplied by GitLab CI.

## Bonus Tip: Rails Crendentials & Honeybadger

Antoher issue I encountered during this migration was the use of Rails credentials in my Honeybadger config, which included this line:

```yaml
api_key:
```

config/honeybadger.yml

This caused an error during the application image build, specifically on this line, asset precompilation:

```Dockerfile
SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

```

Dockerfile

Since we aren't setting a valid `SECRET_KEY_BASE`, Rails can't decrypt our credentials, leading to an error when it fails to find our Honeybadger API key.

### Solution: Safe Navigation

The quick and dirty approach is to use Ruby's safe navigation operator (`&.`) to prevent the error. This will set the API key to `nil`, which the Honeybadger gem will not complain about:

```yaml
api_key:
```

config/honeybadger.yml
