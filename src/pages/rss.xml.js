import rss from "@astrojs/rss";
import { getPostUrl, getPublishedPosts } from "@lib/posts";
import { SITE_DESCRIPTION, SITE_TITLE } from "../consts";

export async function GET(context) {
  const posts = await getPublishedPosts();
  return rss({
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    site: context.site,
    items: posts.map((post) => ({
      ...post.data,
      link: getPostUrl(post),
    })),
  });
}
