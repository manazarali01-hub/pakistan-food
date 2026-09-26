"""Validate the published Jekyll output, including all canonical recipe pages."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
BASE = "https://pakistanfoodrecipes.top"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.canonicals = []
        self.headings = []
        self.jsonld = []
        self._script = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img" and attrs.get("src"):
            self.images.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "h1":
            self.headings.append(tag)
        if tag == "script" and attrs.get("type") == "application/ld+json":
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


sitemap = ET.parse(ROOT / "sitemap-v2.xml")
urls = [node.text for node in sitemap.findall(".//{*}loc")]
errors = []
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
    for link in parser.links + parser.images:
        if link.startswith(("mailto:", "tel:", "javascript:", "data:")):
            continue
        target = urlparse(urljoin(url, link))
        if target.netloc == "pakistanfoodrecipes.top" and not output_path(target.path).is_file():
            errors.append(f"broken internal target: {url} -> {link}")
    for source in parser.jsonld:
        try:
            graph = json.loads(source)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON-LD {url}: {exc}")
            continue
        if urlparse(url).path.startswith("/recipes/") and url.endswith(".html"):
            items = graph.get("@graph", [])
            recipe_items = [item for item in items if item.get("@type") == "Recipe"]
            if not recipe_items:
                errors.append(f"missing Recipe structured data: {url}")
            else:
                instructions = recipe_items[0].get("recipeInstructions") or []
                if len(instructions) < 5:
                    errors.append(f"recipe schema has fewer than 5 detailed steps: {url}")
            if 'data-recipe-lang="ur"' not in rendered_html or 'data-recipe-panel="ur"' not in rendered_html:
                errors.append(f"missing Urdu recipe interface: {url}")

if errors:
    raise SystemExit("\n".join(errors[:50]))
print(f"Validated {len(urls)} rendered pages, canonical URLs, links, images and JSON-LD.")
