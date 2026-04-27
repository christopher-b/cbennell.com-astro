// @ts-check

import expressiveCode from "astro-expressive-code";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import { pluginCodeCaption } from "@fujocoded/expressive-code-caption";
import { readingTime } from "./src/plugins/reading-time.mjs";
import { defineConfig, fontProviders } from "astro/config";

// https://astro.build/config
export default defineConfig({
  site: "https://cbennell.com",
  integrations: [
    expressiveCode({
      styleOverrides: {
        codeFontSize: "0.75rem",
        frames: {
          frameBoxShadowCssValue: "none",
        },
      },
      plugins: [pluginCodeCaption()],
      themes: ["andromeeda", "catppuccin-latte"],
      extractFileNameFromCode: false,
    }),
    mdx(),
    sitemap(),
  ],
  markdown: {
    remarkPlugins: [readingTime],
  },
  fonts: [
    {
      provider: fontProviders.local(),
      name: "Inter",
      cssVariable: "--font-inter",
      fallbacks: ["sans-serif"],
      options: {
        variants: [
          {
            src: ["./src/assets/fonts/InterVariable-Italic.woff2"],
            weight: 400,
            style: "normal",
            display: "swap",
          },
          {
            src: ["./src/assets/fonts/InterVariable-Italic.woff2"],
            weight: 400,
            style: "italic",
            display: "swap",
          },
        ],
      },
    },
  ],
});
