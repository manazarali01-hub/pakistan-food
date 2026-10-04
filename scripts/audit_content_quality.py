"""Audit Pakistan Food for low-value/template content without changing pages.

This is intentionally evidence-focused: it reports duplicate visible guide bodies,
thin indexed guides, generic template phrases, and sitemap/noindex conflicts.
"""

from __future__ import annotations

from collections import defaultdict
from html import unescape
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
SITEMAP = ROOT / "sitemap-v2.xml"

GENERIC_PHRASES = (
    "consistent preparation, moisture control, moderate heat",
    "balance the main ingredient, liquid, sweetness, aroma and temperature",
    "control ingredient ratio, heat, moisture and cooling",
    "the result depends on the balance of the curry base, moisture, heat and final seasoning",
    "practical pakistani cooking guide with direct answers and bilingual support",
    "adjust one variable",
    "add sweetness gradually",
)

def strip_visible(html: str) -> str:
    html = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style\b[^>]*>[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(html)).strip()

def normalized_guide_body(text: str) -> str:
    lower = text.lower()
    marker = lower.find("quick answer:")
    if marker >= 0:
        text = text[marker:]
    # Related-link labels often differ even when the editorial body is identical.
    text = re.split(r"\b(?:related reading|related:|cook it now|try the recipes)\b", text, maxsplit=1, flags=re.I)[0]
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text

def robots_value(html: str) -> str:
    m = re.search(r'<meta\s+[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)', html, flags=re.I)
    if not m:
        m = re.search(r'<meta\s+[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']robots["\']', html, flags=re.I)
    return (m.group(1).lower() if m else "index,follow")

guide_rows = []
groups: dict[str, list[str]] = defaultdict(list)

for file in sorted(GUIDES.glob("*.html")):
    if file.name == "index.html":
        continue
    html = file.read_text(encoding="utf-8")
    visible = strip_visible(html)
    body = normalized_guide_body(visible)
    words = len(re.findall(r"\b[\w’'-]+\b", visible))
    robots = robots_value(html)
    generic_hits = [phrase for phrase in GENERIC_PHRASES if phrase in visible.lower()]
    indexed = "noindex" not in robots
    guide_rows.append((file.name, words, indexed, generic_hits))
    if body:
        groups[body].append(file.name)

duplicate_groups = [files for files in groups.values() if len(files) > 1]
duplicate_groups.sort(key=lambda files: (-len(files), files[0]))

try:
    tree = ET.parse(SITEMAP)
    sitemap_urls = [node.text or "" for node in tree.findall(".//{*}loc")]
except (OSError, ET.ParseError) as exc:
    raise SystemExit(f"Cannot parse sitemap: {exc}")

sitemap_guides = {
    url.rsplit("/", 1)[-1]
    for url in sitemap_urls
    if "/guides/" in url and url.endswith(".html")
}

noindex_in_sitemap = sorted(name for name, _, indexed, _ in guide_rows if not indexed and name in sitemap_guides)
indexed_missing_sitemap = sorted(name for name, _, indexed, _ in guide_rows if indexed and name not in sitemap_guides)
thin_indexed = sorted((name, words) for name, words, indexed, _ in guide_rows if indexed and words < 220)
generic_indexed = sorted((name, hits) for name, _, indexed, hits in guide_rows if indexed and hits)

print("CONTENT QUALITY AUDIT")
print(f"Guides: {len(guide_rows)}")
print(f"Indexed guides: {sum(1 for _,_,indexed,_ in guide_rows if indexed)}")
print(f"Noindex guides: {sum(1 for _,_,indexed,_ in guide_rows if not indexed)}")
print(f"Sitemap guide URLs: {len(sitemap_guides)}")
print(f"Indexed guides under 220 visible words: {len(thin_indexed)}")
print(f"Indexed guides with generic-template phrase hits: {len(generic_indexed)}")
print(f"Exact duplicate visible-body groups: {len(duplicate_groups)}")

if duplicate_groups:
    print("\nEXACT DUPLICATE BODY GROUPS")
    for files in duplicate_groups:
        print(f"- {len(files)} pages: " + ", ".join(files))

if generic_indexed:
    print("\nGENERIC TEMPLATE PHRASE HITS")
    for name, hits in generic_indexed:
        print(f"- {name}: " + " | ".join(hits))

if thin_indexed:
    print("\nTHIN INDEXED GUIDES (<220 visible words)")
    for name, words in thin_indexed:
        print(f"- {name}: {words} words")

if noindex_in_sitemap:
    print("\nERROR: NOINDEX URLS PRESENT IN SITEMAP")
    for name in noindex_in_sitemap:
        print(f"- {name}")

if indexed_missing_sitemap:
    print("\nNOTE: INDEXED GUIDES MISSING FROM SITEMAP")
    for name in indexed_missing_sitemap:
        print(f"- {name}")

strict = "--strict" in sys.argv
if strict and (duplicate_groups or generic_indexed or noindex_in_sitemap):
    raise SystemExit("Strict content-quality audit failed.")

print("\nAudit complete.")
