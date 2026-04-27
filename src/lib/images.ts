import type { ImageMetadata } from 'astro';

const coverImages = import.meta.glob<{ default: ImageMetadata }>(
  '/src/assets/covers/*.{jpg,jpeg,png,gif,webp,svg,avif}'
);

export async function getCoverImage(filename: string | undefined) {
  const loader = filename ? coverImages[`/src/assets/covers/${filename}`] : undefined;
  return loader ? (await loader()).default : undefined;
}
