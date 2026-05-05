import { getCollection, type CollectionEntry } from "astro:content";

export async function getPublishedLabs(): Promise<CollectionEntry<"lab">[]> {
  return (
    await getCollection("lab", ({ data }) => data.status === "published")
  ).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}
