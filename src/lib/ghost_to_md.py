#!/usr/bin/env python3
"""
Ghost CMS JSON export → Markdown files migrator.

Usage:
    python3 ghost_to_md.py [ghost.json] [output_dir]

Defaults:
    ghost.json  → ./ghost.json
    output_dir  → ./ghost-to-md-output
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional, Dict, List
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

GHOST_URL = "https://cbennell.com"          # base URL to replace __GHOST_URL__
INPUT_FILE = "ghost.json"
OUTPUT_DIR = "ghost-to-md-output"
POSTS_DIR  = "posts"                        # sub-folder for posts
PAGES_DIR  = "pages"                        # sub-folder for pages
IMAGES_DIR = "images"                       # relative to OUTPUT_DIR

# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert text to a URL/filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def resolve_ghost_url(text: str) -> str:
    """Replace __GHOST_URL__ placeholder with the real base URL."""
    return text.replace("__GHOST_URL__", GHOST_URL) if text else text


def html_to_markdown(html: str, image_map: dict) -> str:
    """
    Convert Ghost post HTML to Markdown.
    Handles: headings, bold/italic, links, images, lists, blockquotes,
             code spans, fenced code blocks, horizontal rules, paragraphs.
    """
    if not html:
        return ""

    # Replace downloaded image src paths
    for original_url, local_path in image_map.items():
        html = html.replace(original_url, local_path)

    # ── Block-level transformations (order matters) ────────────────────────

    # Fenced code blocks: <pre><code class="language-X">…</code></pre>
    def replace_code_block(m):
        lang_match = re.search(r'class="language-([^"]+)"', m.group(1))
        lang = lang_match.group(1) if lang_match else ""
        inner = m.group(2)
        inner = re.sub(r"<[^>]+>", "", inner)   # strip any inner tags
        inner = unescape_html(inner)
        return f"\n```{lang}\n{inner}\n```\n"

    html = re.sub(
        r"<pre([^>]*)><code([^>]*)>(.*?)</code></pre>",
        lambda m: replace_code_block_full(m),
        html,
        flags=re.DOTALL,
    )

    # Headings
    for n in range(6, 0, -1):
        html = re.sub(
            rf"<h{n}[^>]*>(.*?)</h{n}>",
            lambda m, n=n: "\n" + "#" * n + " " + strip_tags(m.group(1)) + "\n",
            html,
            flags=re.DOTALL,
        )

    # Blockquotes
    html = re.sub(
        r"<blockquote[^>]*>(.*?)</blockquote>",
        lambda m: "\n> " + strip_tags(m.group(1)).replace("\n", "\n> ") + "\n",
        html,
        flags=re.DOTALL,
    )

    # Unordered lists
    html = re.sub(
        r"<ul[^>]*>(.*?)</ul>",
        lambda m: convert_list(m.group(1), ordered=False),
        html,
        flags=re.DOTALL,
    )

    # Ordered lists
    html = re.sub(
        r"<ol[^>]*>(.*?)</ol>",
        lambda m: convert_list(m.group(1), ordered=True),
        html,
        flags=re.DOTALL,
    )

    # Horizontal rules
    html = re.sub(r"<hr\s*/?>", "\n---\n", html)

    # Images  (must come before links)
    html = re.sub(
        r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]*)"[^>]*/?>',
        lambda m: f"![{m.group(2)}]({m.group(1)})",
        html,
    )
    html = re.sub(
        r'<img[^>]+src="([^"]+)"[^>]*/?>',
        lambda m: f"![]({m.group(1)})",
        html,
    )

    # Links
    html = re.sub(
        r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        lambda m: f"[{strip_tags(m.group(2))}]({m.group(1)})",
        html,
        flags=re.DOTALL,
    )

    # Inline formatting
    html = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", html, flags=re.DOTALL)
    html = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", html, flags=re.DOTALL)
    html = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", html, flags=re.DOTALL)
    html = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", html, flags=re.DOTALL)
    html = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", html, flags=re.DOTALL)

    # Paragraphs
    html = re.sub(r"<p[^>]*>(.*?)</p>", lambda m: "\n" + strip_tags(m.group(1)) + "\n", html, flags=re.DOTALL)

    # Line breaks
    html = re.sub(r"<br\s*/?>", "\n", html)

    # Strip remaining HTML tags
    html = re.sub(r"<[^>]+>", "", html)

    # Unescape HTML entities
    html = unescape_html(html)

    # Normalise blank lines (max 2 consecutive)
    html = re.sub(r"\n{3,}", "\n\n", html)

    return html.strip()


def replace_code_block_full(m):
    """Handle <pre ...><code ...>…</code></pre> with attributes on both tags."""
    pre_attrs  = m.group(1)
    code_attrs = m.group(2) if m.lastindex >= 2 else ""
    inner      = m.group(3) if m.lastindex >= 3 else m.group(2)

    # Detect language from either pre or code attributes
    lang = ""
    for attrs in (code_attrs, pre_attrs):
        lang_match = re.search(r'class="[^"]*language-([^\s"]+)', attrs)
        if lang_match:
            lang = lang_match.group(1)
            break

    inner = re.sub(r"<[^>]+>", "", inner)
    inner = unescape_html(inner)
    return f"\n```{lang}\n{inner}\n```\n"


# Monkey-patch the earlier regex to use the correct function
import types

def strip_tags(html: str) -> str:
    """Remove all HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", html).strip()


def convert_list(items_html: str, ordered: bool) -> str:
    items = re.findall(r"<li[^>]*>(.*?)</li>", items_html, re.DOTALL)
    lines = []
    for i, item in enumerate(items, 1):
        text = strip_tags(item).strip()
        prefix = f"{i}. " if ordered else "- "
        lines.append(prefix + text)
    return "\n" + "\n".join(lines) + "\n"


def unescape_html(text: str) -> str:
    replacements = [
        ("&amp;",  "&"),
        ("&lt;",   "<"),
        ("&gt;",   ">"),
        ("&quot;", '"'),
        ("&#39;",  "'"),
        ("&nbsp;", " "),
        ("&#8216;", "\u2018"),
        ("&#8217;", "\u2019"),
        ("&#8220;", "\u201c"),
        ("&#8221;", "\u201d"),
        ("&#8230;", "\u2026"),
        ("&#8212;", "\u2014"),
        ("&#8211;", "\u2013"),
    ]
    for entity, char in replacements:
        text = text.replace(entity, char)
    # Numeric entities
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    return text


def download_image(url: str, dest_dir: Path):
    """Download an image to dest_dir; return the local relative path or None."""
    filename = url.split("/")[-1].split("?")[0]
    if not filename:
        return None
    dest = dest_dir / filename
    if dest.exists():
        return str(dest)
    try:
        print(f"  ↓  {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "ghost-migrator/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
        return str(dest)
    except Exception as e:
        print(f"  ✗  Failed to download {url}: {e}")
        return None


def collect_image_urls(html: str, feature_image: Optional[str]) -> list[str]:
    """Find all image URLs in the post HTML (after resolving __GHOST_URL__)."""
    urls = []
    if feature_image:
        urls.append(resolve_ghost_url(feature_image))
    # src attributes
    urls += re.findall(r'src="(https?://[^"]+)"', html)
    # Ghost URL references in html
    ghost_refs = re.findall(r"__GHOST_URL__(/content/images/[^\s\"'>]+)", html)
    urls += [GHOST_URL + ref for ref in ghost_refs]
    return list(dict.fromkeys(urls))  # deduplicate, preserve order


def format_frontmatter(data: dict) -> str:
    """Render a dict as YAML frontmatter (simple, no dependency required)."""
    lines = ["---"]
    for key, value in data.items():
        if value is None:
            lines.append(f"{key}:")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                escaped = str(item).replace('"', '\\"')
                lines.append(f'  - "{escaped}"')
        elif isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        else:
            escaped = str(value).replace('"', '\\"')
            lines.append(f'{key}: "{escaped}"')
    lines.append("---")
    return "\n".join(lines)


def post_filename(post: dict) -> str:
    """Generate $timestamp-$slug.md filename."""
    pub = post.get("published_at") or post.get("created_at") or ""
    if pub:
        dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d")
    else:
        date_str = "undated"
    slug = post.get("slug") or slugify(post.get("title", "untitled"))
    return f"{date_str}-{slug}.md"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_dir = Path(sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR)

    posts_dir  = output_dir / POSTS_DIR
    pages_dir  = output_dir / PAGES_DIR
    images_dir = output_dir / IMAGES_DIR

    for d in (posts_dir, pages_dir, images_dir):
        d.mkdir(parents=True, exist_ok=True)

    print(f"Reading {input_file} …")
    with open(input_file, encoding="utf-8") as f:
        ghost_data = json.load(f)

    db_data = ghost_data["db"][0]["data"]
    posts   = db_data["posts"]
    tags    = {t["id"]: t["name"] for t in db_data.get("tags", [])}
    posts_tags = db_data.get("posts_tags", [])

    # Build post_id → [tag names] mapping
    post_tag_map: Dict[str, List[str]] = {}
    for pt in posts_tags:
        pid = pt["post_id"]
        tid = pt["tag_id"]
        post_tag_map.setdefault(pid, []).append(tags.get(tid, ""))

    print(f"Found {len(posts)} posts/pages.\n")

    for post in posts:
        is_page      = post.get("type") == "page"
        is_published = post.get("status") == "published"
        target_dir   = pages_dir if is_page else posts_dir
        filename     = post_filename(post)
        filepath     = target_dir / filename

        print(f"{'[page]' if is_page else '[post]'} {filename}  (status={post['status']})")

        # ── Resolve images ───────────────────────────────────────────────────
        html = resolve_ghost_url(post.get("html") or "")
        feature_image = resolve_ghost_url(post.get("feature_image") or "")

        image_urls = collect_image_urls(html, feature_image or None)
        image_map  = {}   # original_url → relative local path

        for url in image_urls:
            # Only download actual image files (not post links)
            if re.search(r"\.(jpe?g|png|gif|webp|svg|avif)(\?.*)?$", url, re.I):
                local_path = download_image(url, images_dir)
                if local_path:
                    # Make path relative to target_dir
                    try:
                        rel = os.path.relpath(local_path, target_dir)
                    except ValueError:
                        rel = local_path
                    image_map[url] = rel

        # ── Convert HTML → Markdown ──────────────────────────────────────────
        markdown_body = html_to_markdown(html, image_map)

        # ── Build frontmatter ────────────────────────────────────────────────
        pub_date = post.get("published_at") or post.get("created_at") or ""
        post_tags = [t for t in post_tag_map.get(post["id"], []) if t]

        fm: dict = {
            "title":       post.get("title", ""),
            "pubDate":     pub_date,
            "description": post.get("custom_excerpt") or "",
            "slug":        post.get("slug", ""),
            "status":      post.get("status", ""),
        }

        if feature_image and feature_image in image_map:
            img_filename = os.path.basename(image_map[feature_image])
            fm["heroImage"] = f"../../assets/images/{img_filename}"
        elif feature_image:
            img_filename = feature_image.split("/")[-1].split("?")[0]
            fm["heroImage"] = f"../../assets/images/{img_filename}"

        if post_tags:
            fm["tags"] = post_tags

        if post.get("featured"):
            fm["featured"] = True

        # Mark drafts/unpublished clearly
        if not is_published:
            fm["draft"] = True

        frontmatter = format_frontmatter(fm)

        # ── Write file ───────────────────────────────────────────────────────
        with open(filepath, "w", encoding="utf-8") as out:
            out.write(frontmatter)
            out.write("\n\n")
            out.write(markdown_body)
            out.write("\n")

    print("\nDone.")
    print(f"  Posts  → {posts_dir}")
    print(f"  Pages  → {pages_dir}")
    print(f"  Images → {images_dir}")


if __name__ == "__main__":
    # Patch: the regex callback needs all 3 groups — redefine inline handler
    _orig_html_to_markdown = html_to_markdown

    def html_to_markdown(html: str, image_map: dict) -> str:  # noqa: F811
        if not html:
            return ""
        for original_url, local_path in image_map.items():
            html = html.replace(original_url, local_path)

        # Fenced code blocks
        html = re.sub(
            r"<pre([^>]*)><code([^>]*)>(.*?)</code></pre>",
            replace_code_block_full,
            html,
            flags=re.DOTALL,
        )

        for n in range(6, 0, -1):
            html = re.sub(
                rf"<h{n}[^>]*>(.*?)</h{n}>",
                lambda m, n=n: "\n" + "#" * n + " " + strip_tags(m.group(1)) + "\n",
                html, flags=re.DOTALL,
            )

        html = re.sub(
            r"<blockquote[^>]*>(.*?)</blockquote>",
            lambda m: "\n> " + strip_tags(m.group(1)).replace("\n", "\n> ") + "\n",
            html, flags=re.DOTALL,
        )
        html = re.sub(r"<ul[^>]*>(.*?)</ul>",
                      lambda m: convert_list(m.group(1), ordered=False),
                      html, flags=re.DOTALL)
        html = re.sub(r"<ol[^>]*>(.*?)</ol>",
                      lambda m: convert_list(m.group(1), ordered=True),
                      html, flags=re.DOTALL)
        html = re.sub(r"<hr\s*/?>", "\n---\n", html)

        # Images before links
        html = re.sub(
            r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]*)"[^>]*/?>',
            lambda m: f"![{m.group(2)}]({m.group(1)})",
            html,
        )
        html = re.sub(
            r'<img[^>]+src="([^"]+)"[^>]*/?>',
            lambda m: f"![]({m.group(1)})",
            html,
        )
        html = re.sub(
            r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            lambda m: f"[{strip_tags(m.group(2))}]({m.group(1)})",
            html, flags=re.DOTALL,
        )

        html = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", html, flags=re.DOTALL)
        html = re.sub(r"<b[^>]*>(.*?)</b>",           r"**\1**", html, flags=re.DOTALL)
        html = re.sub(r"<em[^>]*>(.*?)</em>",          r"*\1*",   html, flags=re.DOTALL)
        html = re.sub(r"<i[^>]*>(.*?)</i>",            r"*\1*",   html, flags=re.DOTALL)
        html = re.sub(r"<code[^>]*>(.*?)</code>",      r"`\1`",   html, flags=re.DOTALL)
        html = re.sub(r"<p[^>]*>(.*?)</p>",
                      lambda m: "\n" + strip_tags(m.group(1)) + "\n",
                      html, flags=re.DOTALL)
        html = re.sub(r"<br\s*/?>", "\n", html)
        html = re.sub(r"<[^>]+>", "", html)
        html = unescape_html(html)
        html = re.sub(r"\n{3,}", "\n\n", html)
        return html.strip()

    main()
