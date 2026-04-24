import { getCollection } from "astro:content";

export async function getPublishedPosts() {
  return (
    await getCollection("posts", ({ data }) => data.status === "published")
  ).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}
