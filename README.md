# cbennell.com

Personal site for Christopher Bennell, built with Astro.

## Todo

- Investigate local copy of Inter font, without losing features like slashed zeros

## Requirements

- Node.js `>=22.12.0`
- Yarn

## Commands

Run commands from the project root.

| Command            | Description                              |
| ------------------ | ---------------------------------------- |
| `yarn install`     | Install dependencies                     |
| `yarn dev`         | Start the dev server at `localhost:4321` |
| `yarn build`       | Build the production site to `dist/`     |
| `yarn preview`     | Preview the production build locally     |
| `yarn astro sync`  | Generate Astro content/types metadata    |
| `yarn astro check` | Typecheck Astro files and content        |

There is no separate lint or test script. Use `yarn astro check` for verification.

## Project Structure

```text
src/
├── assets/          Static source assets, including cover images and fonts
├── components/      Reusable Astro components
├── content/         Markdown and MDX content collections
├── layouts/         Page layout shells
├── lib/             Shared data and utility functions
├── pages/           File-based routes
├── plugins/         Markdown/remark plugins
└── styles/          Global CSS, tokens, utilities, prose, and code styles
```

## Content

Content collections are defined in `src/content.config.ts`.

### Posts

Posts live in `src/content/posts/` and support Markdown or MDX.

Required frontmatter:

- `title`
- `description`
- `slug`
- `pubDate`
- `section`: `post` or `lab`

Optional frontmatter:

- `heroImage`
- `status`: `draft` or `published`
- `tags`

Only posts with `status: published` are returned by the post helpers in `src/lib/posts.ts`.

### Pages

Standalone content pages live in `src/content/pages/`.

Required frontmatter:

- `title`
- `slug`
- `description`

Optional frontmatter:

- `heroImage`
- `status`: `draft` or `published`

## Images

Cover images live in `src/assets/covers/`.

Use the `heroImage` frontmatter field to reference a cover image by filename. Shared cover-image lookup is handled by `src/lib/images.ts`.

## Styling

Global styles are imported through `src/styles/index.css`.

Important files:

- `src/styles/tokens.css` for design tokens
- `src/styles/mixins.css` for PostCSS mixins
- `src/styles/layout.css` for page-level layout
- `src/styles/type.css` for typography
- `src/styles/prose.css` for rendered Markdown content
- `src/styles/code.css` for code block styling

The project uses `postcss-mixins`; check `src/styles/mixins.css` before adding new raw layout CSS.

## Markdown Features

- Markdown and MDX are supported.
- `src/plugins/reading-time.mjs` injects reading-time metadata into rendered content.
- `astro-expressive-code` handles code block rendering.
- Code block captions are provided through the expressive-code caption plugin.

## Deployment

The configured production site URL is `https://cbennell.com` in `astro.config.mjs`.

Build output is written to `dist/` with:

```sh
yarn build
```
