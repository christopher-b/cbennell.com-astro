import type { CollectionEntry } from "astro:content";

import { getCollection } from "astro:content";

export async function getPublishedPosts(): Promise<CollectionEntry<"posts">[]> {
  return (
    await getCollection("posts", ({ data }) => data.status === "published")
  ).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}

export async function getPublishedPostsBySection(section: "post" | "lab") {
  return (
    await getCollection(
      "posts",
      ({ data }) => data.status === "published" && data.section === section,
    )
  ).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}
