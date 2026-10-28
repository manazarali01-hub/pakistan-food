"""Create permanent Jekyll pages and synchronize recipe sitemap entries.

Existing recipe URLs stay unchanged. Sitemap lastmod values follow each
recipe's date_modified field so source edits cannot leave stale sitemap dates.
"""
from datetime import date
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://pakistanfoodrecipes.top/recipes/"
NEW_URLS = []
ALL_URLS = []
latest_category_dates = {}
sitemap = ROOT / "sitemap-v2.xml"
xml = sitemap.read_text(encoding="utf-8")

for data in sorted((ROOT / "_data/recipes").glob("*.json")):
    slug = data.stem
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit(f"Unsafe recipe filename: {data.name}")

    recipe = json.loads(data.read_text(encoding="utf-8"))
    url = f"{BASE}{slug}.html"
    ALL_URLS.append(url)

    wrapper = ROOT / "recipes" / f"{slug}.html"
    if not wrapper.exists():
        wrapper.write_text(
            f"---\nlayout: recipe\nrecipe_key: {slug}\n---\n",
            encoding="utf-8",
        )
        NEW_URLS.append(url)

    source_date = recipe.get("date_modified")
    if source_date:
        try:
            if date.fromisoformat(source_date).isoformat() != source_date:
                raise ValueError("date is not canonical YYYY-MM-DD")
        except (TypeError, ValueError):
            raise SystemExit(
                f"{data.relative_to(ROOT)}: invalid date_modified {source_date!r}"
            )

        category = recipe.get("category")
        if category:
            category_slug = re.sub(r"[^a-z0-9]+", "-", category.lower()).strip("-")
            latest_category_dates[category_slug] = max(
                source_date, latest_category_dates.get(category_slug, source_date)
            )

        entry_pattern = re.compile(
            r"(<url>\s*<loc>" + re.escape(url) +
            r"</loc>\s*<lastmod>)([^<]*)(</lastmod>\s*</url>)"
        )
        xml, changed = entry_pattern.subn(
            lambda match: match.group(1) + source_date + match.group(3),
            xml,
            count=1,
        )

    if url not in xml:
        source_date = recipe.get("date_modified") or date.today().isoformat()
        if "</urlset>" not in xml:
            raise SystemExit("Invalid sitemap-v2.xml: missing closing urlset")
        entry = (
            f"  <url>\n    <loc>{url}</loc>\n"
            f"    <lastmod>{source_date}</lastmod>\n  </url>\n"
        )
        xml = xml.replace("</urlset>", entry + "</urlset>")

# Category pages list recipe names, timings and descriptions, so their sitemap
# dates must not be older than the latest modified recipe they contain.
for category_slug, latest_date in latest_category_dates.items():
    category_url = f"https://pakistanfoodrecipes.top/recipes/{category_slug}/"
    category_pattern = re.compile(
        r"(<url>\s*<loc>" + re.escape(category_url) +
        r"</loc>\s*<lastmod>)([^<]*)(</lastmod>\s*</url>)"
    )

    def update_category_lastmod(match, latest_date=latest_date):
        try:
            current_date = date.fromisoformat(match.group(2))
        except ValueError:
            current_date = date.min
        return (
            match.group(1)
            + max(current_date, date.fromisoformat(latest_date)).isoformat()
            + match.group(3)
        )

    xml, _ = category_pattern.subn(update_category_lastmod, xml, count=1)

sitemap.write_text(xml, encoding="utf-8")
print(
    f"Added {len(NEW_URLS)} permanent recipe pages; "
    "synchronized recipe sitemap modification dates."
)
