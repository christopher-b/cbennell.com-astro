import { getCollection } from "astro:content";

export async function getPage(title: string) {
  const results = await getCollection("pages", ({ data }) => data.title === title);
  return results[0];
}
