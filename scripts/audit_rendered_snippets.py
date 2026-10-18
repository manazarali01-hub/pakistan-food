"""Report-only audit of rendered SEO titles and meta descriptions.

This audit uses the indexable URL set in sitemap-v2.xml and the actual Jekyll
output. Length ranges are review heuristics, not Google ranking requirements.
It deliberately reports findings without failing the build or rewriting metadata.
"""
from __future__ import annotations

from collections import defaultdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
SITEMAP = ROOT / "sitemap-v2.xml"
BASE = "https://pakistanfoodrecipes.top"


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.in_title = False
        self.descriptions = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = {key.lower(): value for key, value in attrs}
        if tag.lower() == "title":
            self.in_title = True
        elif tag.lower() == "meta" and (attrs.get("name") or "").lower() == "description":
            self.descriptions.append(unescape((attrs.get("content") or "").strip()))
        elif tag.lower() == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.canonicals.append((attrs.get("href") or "").strip())

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    @property
    def title(self):
        return " ".join(" ".join(self.title_parts).split())

def rendered_path(url: str) -> Path:
    path = unquote(urlparse(url).path)
    if path.endswith("/"):
        path += "index.html"
    return SITE / path.lstrip("/")

def group_duplicates(rows, field):
    groups = defaultdict(list)
    for row in rows:
        value = row[field].strip()
        if value:
            groups[value.casefold()].append(row["url"])
    return [(key, urls) for key, urls in groups.items() if len(urls) > 1]

def show_rows(label, rows, field, limit=20):
    print(f"\\n{label}: {len(rows)}")
    for row in rows[:limit]:
        print(f"- {row['url']} ({len(row[field])} chars): {row[field]}")
    if len(rows) > limit:
        print(f"... {len(rows) - limit} more; see full workflow log")

tree = ET.parse(SITEMAP)
urls = [node.text.strip() for node in tree.findall(".//{*}loc") if node.text]
rows = []
missing_files = []
parse_issues = []

for url in urls:
    path = rendered_path(url)
    if not path.is_file():
        missing_files.append(url)
        continue
    parser = MetadataParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        parse_issues.append((url, str(exc)))
        continue
    rows.append({
        "url": url,
        "title": parser.title.strip(),
        "description": parser.descriptions[0].strip() if len(parser.descriptions) == 1 else "",
        "description_count": len(parser.descriptions),
        "canonicals": parser.canonicals,
    })

missing_titles = [row for row in rows if not row["title"]]
missing_descriptions = [row for row in rows if not row["description"]]
multiple_descriptions = [row for row in rows if row["description_count"] != 1]
bad_canonicals = [row for row in rows if row["canonicals"] != [row["url"]]]
duplicate_titles = group_duplicates(rows, "title")
duplicate_descriptions = group_duplicates(rows, "description")
short_titles = [row for row in rows if row["title"] and len(row["title"]) < 25]
long_titles = [row for row in rows if len(row["title"]) > 65]
short_descriptions = [row for row in rows if row["description"] and len(row["description"]) < 70]
long_descriptions = [row for row in rows if len(row["description"]) > 170]

print("RENDERED SEO SNIPPET AUDIT (REPORT ONLY)")
print(f"Indexable sitemap URLs: {len(urls)}")
print(f"Rendered pages inspected: {len(rows)}")
print(f"Missing rendered files: {len(missing_files)}")
print(f"Missing titles: {len(missing_titles)}")
print(f"Missing meta descriptions: {len(missing_descriptions)}")
print(f"Pages with meta description count other than one: {len(multiple_descriptions)}")
print(f"Duplicate title groups: {len(duplicate_titles)}")
print(f"Duplicate meta description groups: {len(duplicate_descriptions)}")
print(f"Canonical URL mismatches: {len(bad_canonicals)}")
print("Review candidates (heuristics only; not Google requirements):")
print(f"Titles under 25 characters: {len(short_titles)}")
print(f"Titles over 65 characters: {len(long_titles)}")
print(f"Descriptions under 70 characters: {len(short_descriptions)}")
print(f"Descriptions over 170 characters: {len(long_descriptions)}")

for label, rows_to_show, field in (
    ("MISSING TITLES", missing_titles, "title"),
    ("MISSING DESCRIPTIONS", missing_descriptions, "description"),
    ("MULTIPLE DESCRIPTION TAGS", multiple_descriptions, "description"),
    ("DUPLICATE TITLE GROUPS", [{"url": ", ".join(group_urls), "title": key} for key, group_urls in duplicate_titles], "title"),
    ("DUPLICATE DESCRIPTION GROUPS", [{"url": ", ".join(group_urls), "description": key} for key, group_urls in duplicate_descriptions], "description"),
    ("CANONICAL MISMATCHES", bad_canonicals, "title"),
    ("SHORT TITLES", short_titles, "title"),
    ("LONG TITLES", long_titles, "title"),
    ("SHORT DESCRIPTIONS", short_descriptions, "description"),
    ("LONG DESCRIPTIONS", long_descriptions, "description"),
):
    show_rows(label, rows_to_show, field)

if missing_files:
    print("\\nMISSING RENDERED FILES:")
    for url in missing_files[:20]:
        print(f"- {url}")
if parse_issues:
    print("\\nPARSE/READ ISSUES:")
    for url, issue in parse_issues[:20]:
        print(f"- {url}: {issue}")

print("\\nAudit is report-only; no metadata or pages were changed.")
