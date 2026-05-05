import { getCollection, type CollectionEntry } from "astro:content";

export async function getPublishedPosts(): Promise<CollectionEntry<"posts">[]> {
  return (
    await getCollection("posts", ({ data }) => data.status === "published")
  ).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}
