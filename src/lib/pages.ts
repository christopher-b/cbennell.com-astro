import { getCollection } from "astro:content";

export async function getPageBySlug(slug: string) {
  const results = await getCollection(
    "pages",
    ({ data }) => data.slug === slug,
  );
  return results[0];
}
