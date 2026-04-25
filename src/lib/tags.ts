import type { CollectionEntry } from "astro:content";

type Post = CollectionEntry<"posts">;

export interface DerivedTag {
  name: string;
  slug: string;
  posts: Post[];
}

export function slugifyTag(tag: string) {
  return tag.toLowerCase().trim().replace(/\s+/g, "-");
}

export function deriveTags(posts: Post[]): DerivedTag[] {
  const tags = new Map<string, DerivedTag>();

  for (const post of posts) {
    for (const tag of post.data.tags ?? []) {
      const slug = slugifyTag(tag);
      const existing = tags.get(slug);

      if (existing) {
        existing.posts.push(post);
        continue;
      }

      tags.set(slug, {
        name: tag,
        slug,
        posts: [post],
      });
    }
  }

  return [...tags.values()].sort((a, b) => a.name.localeCompare(b.name));
}

export function findTagBySlug(posts: Post[], slug: string) {
  return deriveTags(posts).find((tag) => tag.slug === slug);
}
