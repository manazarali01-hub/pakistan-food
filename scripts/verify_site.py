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

try:
    urdu_names = json.loads((ROOT / "_data/urdu_names.json").read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    urdu_names = {}
    errors.append(f"_data/urdu_names.json: {exc}")

bilingual_by_slug = {}
for path in sorted((ROOT / "_data/bilingual").glob("*.json")):
    try:
        category_data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
        continue
    if not isinstance(category_data, dict):
        errors.append(f"{path.relative_to(ROOT)}: expected object")
        continue
    for slug, details in category_data.items():
        if slug in bilingual_by_slug:
            errors.append(f"{slug}: duplicate bilingual entry")
        bilingual_by_slug[slug] = details

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
    if not (recipe.get("name_urdu") or urdu_names.get(slug)):
        errors.append(f"{slug}: Urdu recipe name is missing")
    bilingual = bilingual_by_slug.get(slug, {})
    method_en = bilingual.get("method_en") or recipe.get("method") or []
    method_ur = recipe.get("method_ur") or bilingual.get("method_ur") or []
    ingredients_ur = recipe.get("ingredients_ur") or bilingual.get("ingredients_ur") or []
    tips_ur = recipe.get("tips_ur") or bilingual.get("tips_ur") or []
    if len(method_en) < 5:
        errors.append(f"{slug}: detailed English method needs at least 5 steps")
    if len(method_ur) < 5:
        errors.append(f"{slug}: Urdu method needs at least 5 steps")
    if not ingredients_ur:
        errors.append(f"{slug}: Urdu ingredients are missing")
    if len(tips_ur) < 3:
        errors.append(f"{slug}: Urdu tips need at least 3 items")
    for field in ("description_ur", "storage_ur", "serving_ur"):
        if not (recipe.get(field) or bilingual.get(field)):
            errors.append(f"{slug}: {field} is missing")
    if not (ROOT / f"recipes/{slug}.html").is_file():
        errors.append(f"{slug}: permanent recipe page is missing")
    image = str(recipe.get("image", ""))
    if image and not image.startswith(("http://", "https://")) and not (ROOT / image.lstrip("/")).is_file():
        errors.append(f"{slug}: local image {image} is missing")
    for field in ("ingredients", "method"):
        if field in recipe and (not isinstance(recipe[field], list) or not all(isinstance(s, str) and s.strip() for s in recipe[field])):
            errors.append(f"{slug}: {field} must be a non-empty list of text")

if set(bilingual_by_slug) != set(recipes):
    missing = sorted(set(recipes) - set(bilingual_by_slug))
    extra = sorted(set(bilingual_by_slug) - set(recipes))
    if missing:
        errors.append("Bilingual data missing for: " + ", ".join(missing))
    if extra:
        errors.append("Bilingual data has unknown recipes: " + ", ".join(extra))

pages = {p.stem for p in (ROOT / "recipes").glob("*.html") if p.name != "index.html"}
for slug in pages - recipes.keys():
    errors.append(f"{slug}: recipe page has no matching data")

all_paths = []
try:
    tree = ET.parse(ROOT / "sitemap-v2.xml")
    urls = [node.text for node in tree.findall(".//{*}loc")]
except (OSError, ET.ParseError) as exc:
    errors.append(f"sitemap-v2.xml: {exc}")
    urls = []

paths = []
for url in urls:
    parsed = urlparse(url or "")
    if f"{parsed.scheme}://{parsed.netloc}" != DOMAIN or parsed.query or parsed.fragment:
        errors.append(f"sitemap-v2.xml: incorrect canonical URL {url}")
    path = parsed.path
    paths.append(path)
    source = ROOT / (path.lstrip("/") + "index.html" if path.endswith("/") else path.lstrip("/"))
    if not source.is_file():
        errors.append(f"sitemap-v2.xml: {path} has no source page")
for path, count in Counter(paths).items():
    if count > 1:
        errors.append(f"sitemap-v2.xml: duplicate URL {path}")
for slug in recipes:
    if f"/recipes/{slug}.html" not in paths:
        errors.append(f"sitemap-v2.xml: recipe {slug} missing")
all_paths.append(paths)

try:
    index_tree = ET.parse(ROOT / "sitemap.xml")
    sitemap_locs = [node.text for node in index_tree.findall(".//{*}loc")]
    if sitemap_locs != [DOMAIN + "/sitemap-v2.xml"]:
        errors.append("sitemap.xml must point only to sitemap-v2.xml")
except (OSError, ET.ParseError) as exc:
    errors.append(f"sitemap.xml: {exc}")

for trust_page in ("privacy-policy.html", "editorial-policy.html", "disclaimer.html", "terms.html", "image-credits.html"):
    if not (ROOT / trust_page).is_file():
        errors.append(f"{trust_page}: trust page is missing")
    if f"/{trust_page}" not in paths:
        errors.append(f"{trust_page}: missing from sitemap-v2.xml")

if DOMAIN + "/sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
    errors.append("robots.txt does not point to the canonical sitemap")

if errors:
    raise SystemExit("\n".join(errors))
print(f"Verified {len(recipes)} recipes and {len(all_paths[0]) if all_paths else 0} sitemap URLs.")
