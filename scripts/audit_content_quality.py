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
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
SITEMAP = ROOT / "sitemap-v2.xml"
PREMIUM_CSS = ROOT / "premium.css"

GENERIC_PHRASES = (
    "consistent preparation, moisture control, moderate heat",
    "balance the main ingredient, liquid, sweetness, aroma and temperature",
    "control ingredient ratio, heat, moisture and cooling",
    "the result depends on the balance of the curry base, moisture, heat and final seasoning",
    "practical pakistani cooking guide with direct answers and bilingual support",
    "adjust one variable",
    "add sweetness gradually",
    "this step has the strongest effect on the final result",
    "this is the first practical factor to control",
    "this factor directly changes the final texture or flavour",
    "check this factor first because it has a direct effect on texture or flavour",
    "this is the first thing to check because it directly changes",
    "small, even distribution works better than concentrating one ingredient",
    "protect the rice or bread structure while it is hot",
    "use aroma, visible moisture and texture to decide when to continue",
    "if a correction is needed, make it gradually",
    "finish with a short rest or prompt serving as appropriate",
    "keep it deliberate rather than rushing it",
    "it sets up the ingredient for the rest of the method",
    "this is a primary control point for the result",
    "the correct stage should look and smell ready before you continue",
    "handle the food gently once its structure has softened",
    "extra stirring, pressing or prolonged cooking can turn a small issue into a larger texture problem",
    "make one correction at a time",
    "large last-minute additions often solve one imbalance",
    "cookware, ingredient moisture and stove strength vary",
    "use visible cues alongside measurements",
    "for the next batch, change this variable first",
    "this is the first variable to check because it directly changes the moisture, structure or flavour of the dish",
    "control this factor before adding extra ingredients",
    "correcting the cause is more reliable than masking the result later",
    "watch the food as it cooks",
    "texture, aroma and visible moisture usually show whether this stage is progressing correctly",
    "keep adjustments small and deliberate so you can tell which change actually improved the result",
    "home cookware and ingredient moisture vary",
    "use the stated principle rather than forcing one exact time on every batch",
    "once this factor is under control",
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
bad_meta_descriptions: list[tuple[str, str]] = []
chrome_issues: list[tuple[str, str]] = []
try:
    premium_css = re.sub(r"\s+", " ", PREMIUM_CSS.read_text(encoding="utf-8"))
except OSError:
    premium_css = ""
header_chrome_suppressed = ".guide-site-header ~ .policy-header" in premium_css
footer_chrome_suppressed = all(selector in premium_css for selector in (".guide-shell ~ .policy-footer", ".policy-page ~ .policy-footer"))

for file in sorted(GUIDES.glob("*.html")):
    if file.name == "index.html":
        continue
    html = file.read_text(encoding="utf-8")
    guide_nav_count = len(re.findall(r'<header\b[^>]*class=["\'][^"\']*\bguide-site-header\b', html, flags=re.I))
    policy_nav_count = len(re.findall(r'<header\b[^>]*class=["\'][^"\']*\bpolicy-header\b', html, flags=re.I))
    guide_footer_count = len(re.findall(r'<footer\b[^>]*class=["\'][^"\']*\bguide-site-footer\b', html, flags=re.I))
    policy_footer_count = len(re.findall(r'<footer\b[^>]*class=["\'][^"\']*\bpolicy-footer\b', html, flags=re.I))
    if guide_nav_count > 1 or (guide_nav_count and policy_nav_count and not header_chrome_suppressed):
        chrome_issues.append((file.name, "duplicate or conflicting page headers"))
    if guide_footer_count > 1 or (guide_footer_count and policy_footer_count and not footer_chrome_suppressed):
        chrome_issues.append((file.name, "duplicate or conflicting page footers"))
    visible = strip_visible(html)
    body = normalized_guide_body(visible)
    words = len(re.findall(r"\b[\w’'-]+\b", visible))
    robots = robots_value(html)
    description_tag = re.search(
        r"""<meta\b(?=[^>]*\bname=["']description["'])[^>]*>""",
        html,
        flags=re.I,
    )
    description_match = (
        re.search(r"""\bcontent=["']([^"']*)["']""", description_tag.group(0), flags=re.I)
        if description_tag else None
    )
    if not description_match or not description_match.group(1).strip():
        bad_meta_descriptions.append((file.name, "missing or empty meta description"))
    elif description_match.group(1).rstrip().endswith(("...", "…")):
        bad_meta_descriptions.append((file.name, "meta description ends with an ellipsis (possible accidental truncation)"))
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

# Match the site's known canonical origin. Do not trust the first sitemap URL
# to define the expected host, because a malformed sitemap could start elsewhere.
CANONICAL_ORIGIN = ("https", "pakistanfoodrecipes.top")
sitemap_guides = {
    urlparse(url).path
    for url in sitemap_urls
    if (urlparse(url).scheme, urlparse(url).netloc) == CANONICAL_ORIGIN
    and not urlparse(url).query
    and not urlparse(url).fragment
    and urlparse(url).path.startswith("/guides/")
    and urlparse(url).path.endswith(".html")
}

noindex_in_sitemap = sorted(
    name for name, _, indexed, _ in guide_rows
    if not indexed and "/guides/" + name in sitemap_guides
)
indexed_missing_sitemap = sorted(
    name for name, _, indexed, _ in guide_rows
    if indexed and "/guides/" + name not in sitemap_guides
)
thin_indexed = sorted((name, words) for name, words, indexed, _ in guide_rows if indexed and words < 220)
generic_indexed = sorted((name, hits) for name, _, indexed, hits in guide_rows if indexed and hits)

noindex_guides = {name for name, _, indexed, _ in guide_rows if not indexed}
stale_user_links = []

def record_links(source: Path, html: str, pattern: str):
    for match in re.finditer(pattern, html, flags=re.I):
        target = match.group(1).split("/")[-1]
        if target in noindex_guides:
            stale_user_links.append((str(source.relative_to(ROOT)), target))

# Public hubs, recipe templates and category pages should send users to the stronger
# consolidated resource, not prominently link back to a noindex micro-page.
for source in [
    ROOT / "index.html",
    ROOT / "sitemap.html",
    GUIDES / "index.html",
    ROOT / "_layouts" / "recipe.html",
    ROOT / "_layouts" / "category.html",
]:
    if not source.is_file():
        continue
    html = source.read_text(encoding="utf-8")
    if source == GUIDES / "index.html":
        record_links(source, html, r'href=["\'](?:\.\/)?([^"\'#?]+\.html)')
    record_links(source, html, r'href=["\'](?:\.\.\/)*guides\/([^"\'#?]+\.html)')

recipes_dir = ROOT / "recipes"
if recipes_dir.is_dir():
    for source in recipes_dir.rglob("*.html"):
        html = source.read_text(encoding="utf-8")
        record_links(source, html, r'href=["\'](?:\.\.\/)*guides\/([^"\'#?]+\.html)')

stale_user_links = sorted(set(stale_user_links))

print("CONTENT QUALITY AUDIT")
print(f"Guides: {len(guide_rows)}")
print(f"Indexed guides: {sum(1 for _,_,indexed,_ in guide_rows if indexed)}")
print(f"Noindex guides: {sum(1 for _,_,indexed,_ in guide_rows if not indexed)}")
print(f"Sitemap guide URLs: {len(sitemap_guides)}")
print(f"Indexed guides under 220 visible words: {len(thin_indexed)}")
print(f"Indexed guides with generic-template phrase hits: {len(generic_indexed)}")
print(f"Exact duplicate visible-body groups: {len(duplicate_groups)}")
print(f"Public/hub links to noindex guides: {len(stale_user_links)}")
print(f"Guides with missing or truncated meta descriptions: {len(bad_meta_descriptions)}")
print(f"Guides with duplicate/conflicting headers or footers: {len(chrome_issues)}")

if duplicate_groups:
    print("\nEXACT DUPLICATE BODY GROUPS")
    for files in duplicate_groups:
        print(f"- {len(files)} pages: " + ", ".join(files))

if chrome_issues:
    print("\nDUPLICATE/CONFLICTING GUIDE CHROME")
    for name, issue in chrome_issues:
        print(f"- {name}: {issue}")

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
    print("\nINDEXED GUIDES MISSING FROM SITEMAP")
    for name in indexed_missing_sitemap:
        print(f"- {name}")

if stale_user_links:
    print("\nERROR: PUBLIC/HUB LINKS POINT TO NOINDEX GUIDES")
    for source, target in stale_user_links:
        print(f"- {source} -> {target}")

strict = "--strict" in sys.argv
if bad_meta_descriptions:
    print("\nMETA DESCRIPTION ISSUES")
    for name, issue in bad_meta_descriptions:
        print(f"- {name}: {issue}")

if strict and (duplicate_groups or generic_indexed or noindex_in_sitemap or indexed_missing_sitemap or stale_user_links or bad_meta_descriptions or chrome_issues):
    raise SystemExit("Strict content-quality audit failed.")

print("\nAudit complete.")
