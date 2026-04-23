// @ts-check

import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import { defineConfig, fontProviders } from "astro/config";
import { readingTime } from "./src/plugins/reading-time.mjs";

// https://astro.build/config
export default defineConfig({
  site: "https://cbennell.com",
  integrations: [mdx(), sitemap()],
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
