# AGENTS.md

## Commands

```bash
yarn dev        # Dev server → localhost:4321
yarn build      # Production build → ./dist/
yarn preview    # Preview production build
yarn astro check  # Typecheck .astro files (use this, not tsc directly)
yarn astro sync   # Regenerate .astro/types.d.ts (required in a fresh env before typechecking)
```

No test, lint, or separate typecheck script exists. `yarn astro check` is the only verification step.

Node >=22.12.0 required.

## Toolchain

- **Astro 6.x** with TypeScript strict mode (`astro/tsconfigs/strict`)
- **PostCSS** with `postcss-mixins` — check `src/styles/mixins.css` before writing raw CSS
- **Prettier** with `embeddedLanguageFormatting: off` — embedded HTML/CSS/JS won't be auto-formatted
- No ESLint configured

## Path Aliases

| Alias | Resolves to |
|---|---|
| `@src/*` | `src/*` |
| `@components/*` | `src/components/*` |
| `@layouts/*` | `src/layouts/*` |
| `@lib/*` | `src/lib/*` |
| `@assets/*` | `src/assets/*` |
| `@styles/*` | `src/styles/*` |

## Content Collections

Defined in `src/content.config.ts` using Astro 5+ Content Layer API (glob loader).

- **`posts`** — `src/content/posts/**/*.{md,mdx}` — requires `title`, `description`, `pubDate`; optional `heroImage`, `tags`, `status`
- **`pages`** — `src/content/pages/**/*.{md,mdx}` — same as posts plus required `category`

**Only posts with `status: "published"` are returned** by `getPublishedPosts()` in `src/lib/posts.ts`. Posts without this field are filtered out.

Post filenames follow `YYYY-MM-DD-slug.md`.

## Non-Obvious Details

- **`minutesRead`**: A remark plugin (`src/plugins/reading-time.mjs`) automatically injects `minutesRead` into frontmatter of every markdown/MDX file. Access it via `remarkPluginFrontmatter` in layouts.
- **Code block captions**: `extractFileNameFromCode` is disabled in expressive-code — use explicit caption syntax if you need filenames on code blocks.
- **Code themes**: Two themes are active — `andromeeda` (dark) and `catppuccin-latte` (light). Both are applied to all code blocks.
- **`.astro/types.d.ts`** is generated at runtime (not committed). Run `yarn dev` or `yarn astro sync` in a fresh environment before running `astro check`.
- **`src/lib/ghost_to_md.py`** is a standalone Ghost CMS migration utility — not part of the Astro build. Ignore it during normal development.
