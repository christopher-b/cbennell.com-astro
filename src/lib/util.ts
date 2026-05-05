type Entry = {
  collection: string;
  id: string;
  data: { link?: string };
};

export function getEntryUrl(entry: Entry): string {
  return entry.data.link ?? `/${entry.collection}/${entry.id}/`;
}

export function colorScheme() {
  if (
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    return "dark";
  } else {
    return "light";
  }
}
