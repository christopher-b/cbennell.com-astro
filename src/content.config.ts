import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const posts = defineCollection({
  loader: glob({ base: "./src/content/posts", pattern: "**/*.{md,mdx}" }),
  schema: () =>
    z.object({
      title: z.string(),
      description: z.string(),
      link: z.string().optional(),
      slug: z.string(),
      pubDate: z.coerce.date(),
      heroImage: z.string().optional(),
      status: z.enum(["draft", "published"]).optional(),
      section: z.enum(["post", "lab"]),
      tags: z.array(z.string()).optional(),
    }),
});

const pages = defineCollection({
  loader: glob({ base: "./src/content/pages", pattern: "**/*.{md,mdx}" }),
  schema: () =>
    z.object({
      title: z.string(),
      slug: z.string(),
      description: z.string(),
      heroImage: z.string().optional(),
      status: z.enum(["draft", "published"]).optional(),
    }),
});

export const collections = { posts, pages };
