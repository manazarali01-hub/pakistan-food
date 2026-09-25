"""Create permanent Jekyll pages and sitemap entries for new CMS recipes.

Existing URLs and lastmod values stay unchanged. Run this after adding JSON data.
"""

from datetime import date
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://pakistanfoodrecipes.top/recipes/"
NEW_URLS = []
ALL_URLS = []

for data in sorted((ROOT / "_data/recipes").glob("*.json")):
    slug = data.stem
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit(f"Unsafe recipe filename: {data.name}")
    ALL_URLS.append(f"{BASE}{slug}.html")
    wrapper = ROOT / "recipes" / f"{slug}.html"
    if not wrapper.exists():
        wrapper.write_text(f"---\nlayout: recipe\nrecipe_key: {slug}\n---\n", encoding="utf-8")
        NEW_URLS.append(f"{BASE}{slug}.html")

for name in ("sitemap-v2.xml",):
    file = ROOT / name
    xml = file.read_text(encoding="utf-8")
    entries = []
    for url in ALL_URLS:
        if f"<loc>{url}</loc>" not in xml:
            entries.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{date.today().isoformat()}</lastmod>\n  </url>\n")
    if entries:
        if "</urlset>" not in xml:
            raise SystemExit(f"Invalid sitemap: {name}")
        file.write_text(xml.replace("</urlset>", "".join(entries) + "</urlset>"), encoding="utf-8")

print(f"Added {len(NEW_URLS)} permanent recipe pages; existing URLs unchanged.")
