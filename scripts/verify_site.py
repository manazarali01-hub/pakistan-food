"""Check the source files that GitHub Pages publishes for Pakistan Food."""

from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://pakistanfoodrecipes.top"
REQUIRED = ("name", "category", "time", "serves", "image", "description", "ingredients", "method")
ISO_DURATION = re.compile(r"^P(?=\d|T\d)(?:\d+D)?(?:T(?=\d)(?:\d+H)?(?:\d+M)?(?:\d+(?:\.\d+)?S)?)?$")
DISPLAY_TIME = re.compile(
    r"^(?:(\d+)\s+(?:hr|hrs)(?:\s+(\d+)\s+(?:min|mins))?(?:\s+including\s+(?:marinating|chilling))?|"
    r"(\d+)\s+(?:min|mins)(?:\s+plus\s+(\d+)\s+(?:hr|hrs)\s+marinating)?)$"
)
DURATION_PARTS = re.compile(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?")


def display_time_seconds(value):
    """Convert the recipe's human-readable time to seconds using template rules."""
    match = DISPLAY_TIME.fullmatch(value.strip()) if isinstance(value, str) else None
    if not match:
        return None
    hours, extra_minutes, minutes, marinating_hours = match.groups()
    return (
        int(hours or 0) * 3600
        + int(extra_minutes or 0) * 60
        + int(minutes or 0) * 60
        + int(marinating_hours or 0) * 3600
    )


def duration_seconds(value):
    """Convert a validated ISO 8601 duration to seconds for consistency checks."""
    if not isinstance(value, str) or not ISO_DURATION.fullmatch(value):
        return None
    match = DURATION_PARTS.fullmatch(value)
    if not match:
        return None
    days, hours, minutes, seconds = match.groups()
    return (
        int(days or 0) * 86400
        + int(hours or 0) * 3600
        + int(minutes or 0) * 60
        + float(seconds or 0)
    )


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
    servings = recipe.get("serves")
    if isinstance(servings, bool) or not isinstance(servings, int) or servings < 1:
        errors.append(f"{slug}: serves must be a positive integer for Recipe structured data")
    display_time = recipe.get("time")
    display_seconds = display_time_seconds(display_time)
    if display_seconds is None or display_seconds <= 0:
        errors.append(f"{slug}: time must be a positive supported duration such as '45 min', '4 hrs', or '1 hr 30 min'")
    if recipe.get("total_time_iso"):
        total_seconds_for_display = duration_seconds(recipe["total_time_iso"])
        if (
            display_seconds is not None
            and total_seconds_for_display is not None
            and display_seconds != total_seconds_for_display
        ):
            errors.append(
                f"{slug}: time ({display_time}) does not match total_time_iso "
                f"({recipe['total_time_iso']})"
            )
    if "rating" in recipe:
        errors.append(f"{slug}: rating requires a real review source")
    prep_duration = recipe.get("prep_time_iso")
    cook_duration = recipe.get("cook_time_iso")
    # Prep and cook durations are independently optional: no-cook drinks,
    # fruit chaat and chilled desserts may legitimately have prep time only.
    for duration_field in ("prep_time_iso", "cook_time_iso", "total_time_iso"):
        duration_value = recipe.get(duration_field)
        if duration_value and (not isinstance(duration_value, str) or not ISO_DURATION.fullmatch(duration_value)):
            errors.append(f"{slug}: {duration_field} must be a valid ISO 8601 duration")
    if (prep_duration or cook_duration) and recipe.get("total_time_iso"):
        component_durations = [
            duration_seconds(value)
            for value in (prep_duration, cook_duration)
            if value
        ]
        total_seconds = duration_seconds(recipe["total_time_iso"])
        if (
            component_durations
            and all(value is not None for value in component_durations)
            and total_seconds is not None
            and total_seconds < sum(component_durations)
        ):
            errors.append(
                f"{slug}: total_time_iso is shorter than the supplied prep/cook durations"
            )
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
    if "commons.wikimedia.org" in image:
        source_url = str(recipe.get("image_source", ""))
        if source_url and "commons.wikimedia.org/wiki/File:" not in source_url:
            errors.append(f"{slug}: image_source must point to the Commons file page")
        if bool(recipe.get("image_author")) != bool(recipe.get("image_license")):
            errors.append(f"{slug}: image_author and image_license must be supplied together")
    elif "staticflickr.com" in image:
        source_url = str(recipe.get("image_source", ""))
        if "flickr.com/photos/" not in source_url:
            errors.append(f"{slug}: Flickr image_source must point to the Flickr photo page")
        for field in ("image_author", "image_license", "image_license_url", "image_source_label"):
            if not recipe.get(field):
                errors.append(f"{slug}: {field} is required for Flickr image attribution")
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
    url_entries = tree.findall(".//{*}url")
    urls = [node.text for node in tree.findall(".//{*}loc")]
    sitemap_lastmod = {
        node.findtext("{*}loc"): node.findtext("{*}lastmod")
        for node in url_entries
    }
    # A missing lastmod is valid; a supplied one must be a real W3C/ISO date
    # or datetime. Invalid dates can make sitemap freshness signals unreliable.
    for node in url_entries:
        loc = node.findtext("{*}loc")
        lastmod = node.findtext("{*}lastmod")
        if not loc:
            errors.append("sitemap-v2.xml: URL entry is missing loc")
            continue
        if lastmod:
            try:
                if len(lastmod) == 10:
                    date.fromisoformat(lastmod)
                else:
                    datetime.fromisoformat(lastmod.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"sitemap-v2.xml: invalid lastmod {lastmod!r} for {loc}")
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
for slug, recipe in recipes.items():
    recipe_path = f"/recipes/{slug}.html"
    if recipe_path not in paths:
        errors.append(f"sitemap-v2.xml: recipe {slug} missing")
    source_date = recipe.get("date_modified")
    if source_date:
        recipe_url = DOMAIN + recipe_path
        sitemap_date = sitemap_lastmod.get(recipe_url)
        if sitemap_date != source_date:
            errors.append(
                f"sitemap-v2.xml: lastmod mismatch for {slug}: "
                f"{sitemap_date!r} != {source_date!r}"
            )
all_paths.append(paths)

try:
    index_tree = ET.parse(ROOT / "sitemap.xml")
    sitemap_locs = [node.text for node in index_tree.findall(".//{*}loc")]
    if sitemap_locs != [DOMAIN + "/sitemap-v2.xml"]:
        errors.append("sitemap.xml must point only to sitemap-v2.xml")
except (OSError, ET.ParseError) as exc:
    errors.append(f"sitemap.xml: {exc}")

for trust_page in ("about.html", "contact.html", "privacy-policy.html", "editorial-policy.html", "disclaimer.html", "terms.html", "image-credits.html"):
    if not (ROOT / trust_page).is_file():
        errors.append(f"{trust_page}: trust page is missing")
    if f"/{trust_page}" not in paths:
        errors.append(f"{trust_page}: missing from sitemap-v2.xml")

# Every guide deliberately submitted to Google should be reachable from the
# main Cooking Guides directory, not only through its sitemap URL.
guide_hub_path = ROOT / "guides/index.html"
guide_hub = ""
if guide_hub_path.is_file():
    guide_hub = guide_hub_path.read_text(encoding="utf-8")
    for guide_url in urls:
        guide_path = urlparse(guide_url or "").path
        if guide_path.startswith("/guides/") and guide_path.endswith(".html"):
            guide_filename = guide_path.rsplit("/", 1)[-1]
            if f'href="{guide_filename}"' not in guide_hub:
                errors.append(f"indexable guide missing from directory: {guide_filename}")

    # Reverse-check local guide links in the hub so the directory cannot point
    # to a missing page or to a page omitted from the canonical sitemap.
    for guide_filename in sorted(set(re.findall(r'href="([^"/?#]+\.html)"', guide_hub))):
        if guide_filename == "index.html":
            continue
        guide_file = ROOT / "guides" / guide_filename
        guide_url = f"{DOMAIN}/guides/{guide_filename}"
        if not guide_file.is_file():
            errors.append(f"guides/index.html: linked guide file is missing: {guide_filename}")
        if guide_url not in urls:
            errors.append(f"guides/index.html: linked guide missing from sitemap: {guide_filename}")
else:
    errors.append("guides/index.html: directory is missing")

# Category hubs must link only to guides that are both in the canonical sitemap
# and discoverable from the main Cooking Guides directory.
category_template_path = ROOT / "_layouts/category.html"
try:
    category_template = category_template_path.read_text(encoding="utf-8")
except OSError as exc:
    category_template = ""
    errors.append(f"_layouts/category.html: {exc}")

for guide_filename in sorted(set(re.findall(r'href="\.\./\.\./guides/([^"]+\.html)"', category_template))):
    guide_url = f"{DOMAIN}/guides/{guide_filename}"
    if guide_url not in urls:
        errors.append(f"_layouts/category.html: guide link missing from sitemap: {guide_filename}")
    if f'href="{guide_filename}"' not in guide_hub:
        errors.append(f"_layouts/category.html: guide link missing from directory: {guide_filename}")

if DOMAIN + "/sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
    errors.append("robots.txt does not point to the canonical sitemap")


# Keep recipe search snippets concise, non-boilerplate, and within the common
# 155-character search-snippet target. This mirrors Liquid's truncate filter.
recipe_template_path = ROOT / "_layouts/recipe.html"
try:
    recipe_template = recipe_template_path.read_text(encoding="utf-8")
except OSError as exc:
    recipe_template = ""
    errors.append(f"_layouts/recipe.html: {exc}")

if "{% capture search_description %}" not in recipe_template:
    errors.append("_layouts/recipe.html: dedicated search_description capture is missing")
if '<meta name="description" content="{{ search_description | strip_html | strip | escape }}">' not in recipe_template:
    errors.append("_layouts/recipe.html: meta description must use the dedicated search_description")
if "See ingredients and the easy step-by-step method." in recipe_template:
    errors.append("_layouts/recipe.html: generic recipe meta-description boilerplate should be removed")
if "search_description_source | split: ' '" not in recipe_template or "search_description_word_budget" not in recipe_template:
    errors.append("_layouts/recipe.html: long search descriptions must truncate at word boundaries")

if '"recipeYield": {{ recipe.serves | jsonify }}' not in recipe_template:
    errors.append("_layouts/recipe.html: recipeYield must preserve the numeric serving count")

for slug, recipe in recipes.items():
    suffix = f" Ready in {recipe.get('time', '')}"
    if recipe.get("serves"):
        suffix += f"; serves {recipe['serves']}"
    suffix += "."
    description_budget = 155 - len(suffix)
    if description_budget < 4:
        errors.append(f"{slug}: search-description suffix leaves no useful description space")
        continue
    # Match _layouts/recipe.html: seo_description takes precedence over description.
    source_description = str(recipe.get("seo_description") or recipe.get("description", "")).strip()
    description = source_description
    if len(source_description) > description_budget:
        prefix = source_description[:description_budget - 3]
        prefix = prefix.rsplit(" ", 1)[0] if " " in prefix else ""
        description = prefix + "..."
        if len(prefix) < len(source_description) and source_description[len(prefix)] != " ":
            errors.append(f"{slug}: generated search description truncates inside a word")
    if len(description + suffix) > 155:
        errors.append(
            f"{slug}: generated search description exceeds 155 characters "
            f"({len(description + suffix)})"
        )

if errors:
    raise SystemExit("\n".join(errors))
print(f"Verified {len(recipes)} recipes and {len(all_paths[0]) if all_paths else 0} sitemap URLs.")
