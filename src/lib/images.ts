import type { ImageMetadata } from 'astro';

export interface CoverImage {
  src: ImageMetadata;
  alt: string;
}

const coverImages = import.meta.glob<{ default: ImageMetadata }>(
  '/src/assets/covers/*.{jpg,jpeg,png,gif,webp,svg,avif}'
);

export async function getCoverImage(filename: string | undefined, alt = ''): Promise<CoverImage | undefined> {
  const loader = filename ? coverImages[`/src/assets/covers/${filename}`] : undefined;
  const src = loader ? (await loader()).default : undefined;

  return src ? { src, alt } : undefined;
}
