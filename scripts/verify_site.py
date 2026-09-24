"""Check the source files that GitHub Pages publishes for Pakistan Food."""

from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://pakistanfoodrecipes.top"
REQUIRED = ("name", "category", "time", "serves", "image", "description", "ingredients", "method")
errors = []

recipes = {}
for path in sorted((ROOT / "_data/recipes").glob("*.json")):
    try:
        recipe = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
        continue
    slug = path.stem
    recipes[slug] = recipe
    missing = [field for field in REQUIRED if not recipe.get(field)]
    if missing:
        errors.append(f"{slug}: missing {', '.join(missing)}")
    if "rating" in recipe:
        errors.append(f"{slug}: rating requires a real review source")
    if not (ROOT / f"recipes/{slug}.html").is_file():
        errors.append(f"{slug}: permanent recipe page is missing")
    image = str(recipe.get("image", ""))
    if image and not image.startswith(("http://", "https://")) and not (ROOT / image.lstrip("/")).is_file():
        errors.append(f"{slug}: local image {image} is missing")
    for field in ("ingredients", "method"):
        if field in recipe and (not isinstance(recipe[field], list) or not all(isinstance(s, str) and s.strip() for s in recipe[field])):
            errors.append(f"{slug}: {field} must be a non-empty list of text")

pages = {p.stem for p in (ROOT / "recipes").glob("*.html") if p.name != "index.html"}
for slug in pages - recipes.keys():
    errors.append(f"{slug}: recipe page has no matching data")

all_paths = []
for sitemap in ("sitemap-v2.xml", "sitemap.xml"):
    try:
        tree = ET.parse(ROOT / sitemap)
        urls = [node.text for node in tree.findall(".//{*}loc")]
    except (OSError, ET.ParseError) as exc:
        errors.append(f"{sitemap}: {exc}")
        continue
    paths = []
    for url in urls:
        parsed = urlparse(url or "")
        if f"{parsed.scheme}://{parsed.netloc}" != DOMAIN or parsed.query or parsed.fragment:
            errors.append(f"{sitemap}: incorrect canonical URL {url}")
        path = parsed.path
        paths.append(path)
        source = ROOT / (path.lstrip("/") + "index.html" if path.endswith("/") else path.lstrip("/"))
        if not source.is_file():
            errors.append(f"{sitemap}: {path} has no source page")
    for path, count in Counter(paths).items():
        if count > 1:
            errors.append(f"{sitemap}: duplicate URL {path}")
    for slug in recipes:
        if f"/recipes/{slug}.html" not in paths:
            errors.append(f"{sitemap}: recipe {slug} missing")
    all_paths.append(paths)

if len(all_paths) == 2 and set(all_paths[0]) != set(all_paths[1]):
    errors.append("Sitemaps do not list the same pages")

if DOMAIN + "/sitemap-v2.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
    errors.append("robots.txt does not point to the main sitemap")

if errors:
    raise SystemExit("\n".join(errors))
print(f"Verified {len(recipes)} recipes and {len(all_paths[0]) if all_paths else 0} sitemap URLs.")
