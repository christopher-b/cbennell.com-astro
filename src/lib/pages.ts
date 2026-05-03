import { getEntry } from "astro:content";

export async function getPageBySlug(slug: string) {
  return getEntry("pages", slug);
}
