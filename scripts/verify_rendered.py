"""Validate the rendered Pakistan Food site: URLs, schema, ads and internal links."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
BASE = "https://pakistanfoodrecipes.top"

RECIPES = {}
for recipe_path in (ROOT / "_data/recipes").glob("*.json"):
    RECIPES[recipe_path.stem] = json.loads(recipe_path.read_text(encoding="utf-8"))


def expected_duration(recipe):
    explicit = recipe.get("total_time_iso")
    if explicit:
        return explicit
    value = str(recipe.get("time", "")).strip().lower()
    match = re.fullmatch(r"(\d+)\s*hr(?:s)?(?:\s+(\d+)\s*min(?:s)?)?", value)
    if match:
        hours, minutes = match.groups()
        return f"PT{hours}H" + (f"{minutes}M" if minutes else "")
    match = re.fullmatch(r"(\d+)\s*min(?:s)?", value)
    if match:
        return f"PT{match.group(1)}M"
    return None


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.canonicals = []
        self.headings = []
        self.jsonld = []
        self.robots = []
        self.adsense_scripts = 0
        self._script = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img" and attrs.get("src"):
            self.images.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "meta" and str(attrs.get("name", "")).lower() == "robots":
            self.robots.append(str(attrs.get("content", "")).lower())
        if tag == "h1":
            self.headings.append(tag)
        if tag == "script":
            src = str(attrs.get("src", ""))
            if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" in src:
                self.adsense_scripts += 1
            if attrs.get("type") == "application/ld+json":
                self._script = True
                self.jsonld.append("")

    def handle_data(self, data):
        if self._script:
            self.jsonld[-1] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self._script = False


def output_path(path):
    path = unquote(path)
    if ".." in Path(path).parts:
        raise ValueError(f"unsafe internal path: {path}")
    return SITE / (path.lstrip("/") + "index.html" if path.endswith("/") else path.lstrip("/"))


errors = []

# ads.txt must render from the same configured publisher ID used by page scripts.
config_text = (ROOT / "_config.yml").read_text(encoding="utf-8")
client_match = re.search(r'^adsense_client:\s*["\']?(ca-pub-\d+)["\']?\s*$', config_text, flags=re.M)
if not client_match:
    errors.append("_config.yml: adsense_client is missing or malformed")
else:
    publisher = client_match.group(1).replace("ca-", "")
    expected_ads = f"google.com, {publisher}, DIRECT, f08c47fec0942fa0"
    rendered_ads_path = SITE / "ads.txt"
    if not rendered_ads_path.is_file():
        errors.append("rendered ads.txt is missing")
    else:
        rendered_ads = rendered_ads_path.read_text(encoding="utf-8").strip()
        if rendered_ads != expected_ads:
            errors.append(f"rendered ads.txt mismatch: {rendered_ads!r}")

sitemap = ET.parse(ROOT / "sitemap-v2.xml")
urls = [node.text for node in sitemap.findall(".//{*}loc")]

for url in urls:
    path = output_path(urlparse(url).path)
    if not path.is_file():
        errors.append(f"missing generated page: {url}")
        continue

    rendered_html = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(rendered_html)

    if parser.canonicals != [url]:
        errors.append(f"bad canonical {url}: {parser.canonicals}")
    if len(parser.headings) != 1:
        errors.append(f"expected one h1: {url}")
    if any("noindex" in value for value in parser.robots):
        errors.append(f"noindex URL must not be in sitemap: {url}")
    if parser.adsense_scripts > 1:
        errors.append(f"duplicate AdSense loader on {url}: {parser.adsense_scripts}")
    if re.search(r'<ins\b[^>]*class=["\'][^"\']*\badsbygoogle\b', rendered_html, flags=re.I):
        errors.append(f"ad unit present before readiness review: {url}")

    for link in parser.links + parser.images:
        if link.startswith(("mailto:", "tel:", "javascript:", "data:")):
            continue
        target = urlparse(urljoin(url, link))
        if target.netloc == "pakistanfoodrecipes.top" and not output_path(target.path).is_file():
            errors.append(f"broken internal target: {url} -> {link}")

    parsed_jsonld = []
    for source in parser.jsonld:
        try:
            parsed_jsonld.append(json.loads(source))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON-LD {url}: {exc}")

    url_path = urlparse(url).path
    if url_path.startswith("/recipes/") and url.endswith(".html"):
        slug = Path(url_path).stem
        source_recipe = RECIPES.get(slug)
        if not source_recipe:
            errors.append(f"missing source recipe data for rendered page: {url}")
            continue

        recipe_items = []
        for graph in parsed_jsonld:
            if isinstance(graph, dict):
                items = graph.get("@graph", [])
                if isinstance(items, list):
                    recipe_items.extend(item for item in items if isinstance(item, dict) and item.get("@type") == "Recipe")
                elif graph.get("@type") == "Recipe":
                    recipe_items.append(graph)

        if len(recipe_items) != 1:
            errors.append(f"expected exactly one Recipe structured-data item: {url}")
            continue

        recipe_item = recipe_items[0]
        required_schema = ("name", "image", "description", "recipeCategory", "recipeCuisine",
                           "keywords", "recipeIngredient", "recipeInstructions", "totalTime", "recipeYield")
        missing = [field for field in required_schema if not recipe_item.get(field)]
        if missing:
            errors.append(f"recipe schema missing {', '.join(missing)}: {url}")

        source_keywords = source_recipe.get("keywords")
        if isinstance(source_keywords, list) and source_keywords:
            expected_keywords = ", ".join(str(item).strip() for item in source_keywords if str(item).strip())
        else:
            recipe_name = str(source_recipe.get("name") or "").strip()
            expected_keywords = (
                f"authentic {recipe_name} recipe, traditional {recipe_name}, "
                f"homemade {recipe_name}, easy {recipe_name}"
            )
        if recipe_item.get("keywords") != expected_keywords:
            errors.append(
                f"recipe schema keywords mismatch {url}: "
                f"{recipe_item.get('keywords')!r} != {expected_keywords!r}"
            )

        instructions = recipe_item.get("recipeInstructions") or []
        if len(instructions) < 5:
            errors.append(f"recipe schema has fewer than 5 detailed steps: {url}")
        for index, instruction in enumerate(instructions, start=1):
            if not isinstance(instruction, dict):
                errors.append(f"recipe instruction {index} is not a structured HowToStep: {url}")
                continue
            if not instruction.get("image") and not instruction.get("video"):
                errors.append(f"recipe instruction {index} has neither image nor video: {url}")
            image_value = instruction.get("image")
            if image_value and isinstance(image_value, str) and not image_value.startswith(("https://", "http://")):
                errors.append(f"recipe instruction {index} image is not absolute: {url} -> {image_value}")

        duration = expected_duration(source_recipe)
        if duration and recipe_item.get("totalTime") != duration:
            errors.append(f"wrong totalTime {url}: {recipe_item.get('totalTime')} != {duration}")

        source_modified = source_recipe.get("date_modified")
        schema_modified = recipe_item.get("dateModified")
        if source_modified and schema_modified != source_modified:
            errors.append(f"dateModified mismatch {url}: {schema_modified} != {source_modified}")
        if not source_modified and schema_modified:
            errors.append(f"dateModified rendered without a source editorial date: {url}")

        if not source_recipe.get("calories") and recipe_item.get("nutrition"):
            errors.append(f"nutrition schema rendered without source calories: {url}")
        if not (source_recipe.get("rating_value") and source_recipe.get("rating_count")) and recipe_item.get("aggregateRating"):
            errors.append(f"rating schema rendered without source rating data: {url}")
        if not (source_recipe.get("video_url") and source_recipe.get("video_thumbnail") and source_recipe.get("video_upload_date")) and recipe_item.get("video"):
            errors.append(f"video schema rendered without source video data: {url}")

        if 'data-recipe-lang="ur"' not in rendered_html or 'data-recipe-panel="ur"' not in rendered_html:
            errors.append(f"missing Urdu recipe interface: {url}")

if errors:
    raise SystemExit("\n".join(errors[:80]))
print(f"Validated {len(urls)} rendered pages, schema, ads.txt, AdSense loading, links and images.")
