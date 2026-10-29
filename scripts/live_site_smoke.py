"""Post-deploy smoke checks for the public Pakistan Food custom domain.

This runs after GitHub Pages reports a successful deployment. It verifies the deployed
site rather than only the repository/Jekyll build, with retries for CDN/DNS propagation.
"""

from __future__ import annotations

from html import unescape
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

BASE = "https://pakistanfoodrecipes.top"
GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GH_TOKEN", "")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_SHA = os.environ.get("GITHUB_SHA", "")
GITHUB_RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
USER_AGENT = "PakistanFoodLiveSmoke/1.0 (+https://pakistanfoodrecipes.top/)"
ATTEMPTS = 8
DELAY_SECONDS = 10

_config_text = Path("_config.yml").read_text(encoding="utf-8")
_client_match = re.search(r'^adsense_client:\s*["\']?(ca-pub-\d+)["\']?\s*$', _config_text, re.M)
if not _client_match:
    raise SystemExit("_config.yml: adsense_client is missing or malformed")
ADSENSE_CLIENT = _client_match.group(1)
EXPECTED_ADS = f"google.com, {ADSENSE_CLIENT.replace('ca-', '')}, DIRECT, f08c47fec0942fa0"
_version_match = re.search(r'^recipe_image_version:\s*["\']?([^"\'\s]+)', _config_text, re.M)
RECIPE_IMAGE_VERSION = _version_match.group(1) if _version_match else "20261004-photo3"


def wait_for_pages_deployment() -> None:
    """Wait until GitHub Pages has successfully deployed the same commit."""

    if not (GITHUB_TOKEN and GITHUB_REPOSITORY and GITHUB_SHA):
        print("Pages deployment wait skipped outside GitHub Actions")
        return

    url = (
        f"{GITHUB_API}/repos/{GITHUB_REPOSITORY}/actions/runs"
        f"?head_sha={GITHUB_SHA}&per_page=30"
    )
    for attempt in range(1, 37):
        req = Request(
            url,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "User-Agent": USER_AGENT,
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urlopen(req, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            if attempt == 36:
                raise SystemExit(f"Could not read Pages workflow status: {exc}")
            print(f"Waiting for Pages status ({attempt}/36): {exc}")
            time.sleep(10)
            continue

        pages_runs = [
            run
            for run in payload.get("workflow_runs", [])
            if run.get("name") == "pages build and deployment"
            and str(run.get("id", "")) != GITHUB_RUN_ID
        ]
        if pages_runs:
            latest = max(pages_runs, key=lambda run: run.get("run_number", 0))
            status = latest.get("status")
            conclusion = latest.get("conclusion")
            if status == "completed":
                if conclusion != "success":
                    raise SystemExit(
                        f"Pages deployment for {GITHUB_SHA} completed with {conclusion!r}"
                    )
                print(
                    f"OK Pages deployment for {GITHUB_SHA[:12]} "
                    f"(run {latest.get('run_number')})"
                )
                return

        if attempt < 36:
            print(f"Waiting for Pages deployment of {GITHUB_SHA[:12]} ({attempt}/36)")
            time.sleep(10)

    raise SystemExit(f"Timed out waiting for Pages deployment of {GITHUB_SHA}")


def fetch(path: str) -> tuple[int, str, str]:
    url = BASE + path
    last_error: Exception | None = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            req = Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml,text/plain;q=0.9,*/*;q=0.8",
                    "Cache-Control": "no-cache",
                },
            )
            with urlopen(req, timeout=20) as response:
                body = response.read().decode("utf-8", errors="replace")
                status = int(getattr(response, "status", 200))
                final_url = response.geturl()
                if status == 200:
                    return status, final_url, body
                last_error = RuntimeError(f"HTTP {status} for {url}")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt < ATTEMPTS:
            print(f"Retry {attempt}/{ATTEMPTS - 1} for {url}: {last_error}")
            time.sleep(DELAY_SECONDS)
    raise SystemExit(f"Live fetch failed after {ATTEMPTS} attempts: {url}: {last_error}")

def fetch_binary(path: str) -> tuple[int, str, bytes, str]:
    url = BASE + path
    last_error: Exception | None = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            req = Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "Cache-Control": "no-cache",
                },
            )
            with urlopen(req, timeout=20) as response:
                body = response.read()
                status = int(getattr(response, "status", 200))
                final_url = response.geturl()
                content_type = response.headers.get("Content-Type", "")
                if status == 200:
                    return status, final_url, body, content_type
                last_error = RuntimeError(f"HTTP {status} for {url}")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt < ATTEMPTS:
            print(f"Retry {attempt}/{ATTEMPTS - 1} for {url}: {last_error}")
            time.sleep(DELAY_SECONDS)
    raise SystemExit(f"Live image fetch failed after {ATTEMPTS} attempts: {url}: {last_error}")


def require(path: str, *needles: str) -> str:
    status, final_url, body = fetch(path)
    if status != 200:
        raise SystemExit(f"{path}: expected HTTP 200, got {status}")
    if final_url.rstrip("/") != (BASE + path).rstrip("/"):
        # www/non-www or CDN normalization is fine only when it stays on the canonical host.
        if not final_url.startswith(BASE + "/") and final_url.rstrip("/") != BASE:
            raise SystemExit(f"{path}: unexpected redirect target {final_url}")
    for needle in needles:
        if needle not in body:
            raise SystemExit(f"{path}: missing deployed marker {needle!r}")
    print(f"OK {path} ({len(body)} bytes)")
    return body

wait_for_pages_deployment()

home = require(
    "/", "Pakistan Food", "Flavours worth sharing.",
    "food-atmosphere.css?v=20261010-biryani-canvas-v5",
    "food-atmosphere.js?v=20261010-biryani-canvas-v5",
    'data-pf-dish="chicken-biryani"',
    "premium.css?v=20261010-refined-v9",
)
# Verify the deployed homepage retains its LCP image hint, not just the source
# template. This catches stale CDN output or a future preload regression.
hero_preloads = re.findall(
    r'<link\b(?=[^>]*\brel=["\']preload["\'])'
    r'(?=[^>]*\bas=["\']image["\'])'
    r'(?=[^>]*\bhref=["\']https://pakistanfoodrecipes\.top/assets/recipe-images/chicken-biryani-v2\.webp["\'])'
    r'[^>]*>',
    home,
    flags=re.I,
)
if len(hero_preloads) != 1:
    raise SystemExit(f"/: expected exactly one deployed chicken biryani hero preload, found {len(hero_preloads)}")
if not re.search(r'\bfetchpriority=["\']high["\']', hero_preloads[0], flags=re.I):
    raise SystemExit("/: deployed chicken biryani hero preload must use fetchpriority=high")
if any(marker in home for marker in (
    'id="pfMotionToggle"', 'id="pfMotionPreview"', "pf-featured-motion"
)):
    raise SystemExit("/: old manual motion control or animated badge remains")
require(
    "/food-atmosphere.css?v=20261010-biryani-canvas-v5",
    "pf-steam-canvas", "pointer-events:none",
    "prefers-reduced-motion:reduce",
)
require(
    "/food-atmosphere.js?v=20261010-biryani-canvas-v5",
    "chicken-biryani", "canvas", "createRadialGradient",
    "IntersectionObserver", "requestAnimationFrame",
    "food-motion", "pfFoodMotionEnabled",
)
require(
    "/premium.css?v=20261010-refined-v9",
    "BALANCED PREMIUM MOTION",
)
# Google has reported a small number of impressions for /index.html.
# Keep the homepage alias canonicalized to the root URL so it is not treated
# as a separate preferred page if the alias remains directly accessible.
home_alias = require("/index.html", "Pakistan Food")
alias_canonical = re.search(
    r'<link\\b[^>]*rel=["\\']canonical["\\'][^>]*>', home_alias, re.I
)
alias_href = (
    re.search(r'href=["\\']([^"\\']+)["\\']', alias_canonical.group(0), re.I)
    if alias_canonical else None
)
if not alias_href or alias_href.group(1) != BASE + "/":
    raise SystemExit("/index.html: homepage alias must canonicalize to the root URL")
print("OK /index.html canonicalizes to the homepage root")

if f"?v={RECIPE_IMAGE_VERSION}" not in home:
    raise SystemExit(f"/: recipe image cache-busting version {RECIPE_IMAGE_VERSION!r} missing")
if "{{ dish.name }}" in home:
    raise SystemExit("/: unresolved Liquid/template marker found in deployed homepage")

biryani = require(
    "/recipes/chicken-biryani.html",
    'data-pf-dish="chicken-biryani"',
    "food-atmosphere.css?v=20261010-biryani-canvas-v5",
    "food-atmosphere.js?v=20261010-biryani-canvas-v5",
    'rel="canonical"',
    '"@type": "Recipe"',
)
directory = require(
    "/recipes/",
    'data-pf-dish="chicken-biryani"',
    "food-atmosphere.js?v=20261010-biryani-canvas-v5",
)
rice_category = require(
    "/recipes/rice/",
    "<title>Pakistani Rice Recipes: Biryani, Pulao &amp; More</title>",
    "<h1>Pakistani Rice Recipes: Biryani, Pulao &amp; More</h1>",
    '<link rel="canonical" href="https://pakistanfoodrecipes.top/recipes/rice/">',
)
if "Pakistani Rice Recipes: Biryani, Pulao & More" not in unescape(rice_category):
    raise SystemExit("/recipes/rice/: search-focused title is missing from deployed page")
halwa = require(
    "/recipes/halwa-puri.html",
    "Halwa Puri Recipe",
    "assets/recipe-images/halwa-puri-v2.webp",
    "Robin Crusoe",
    "Wikimedia Commons",
    "CC BY-SA 4.0",
    'https://pakistanfoodrecipes.top/recipes/halwa-puri.html',
)
if f"assets/recipe-images/halwa-puri-v2.webp?v={RECIPE_IMAGE_VERSION}" not in halwa:
    raise SystemExit("/recipes/halwa-puri.html: versioned local recipe image URL missing")
if '"@type": "Recipe"' not in halwa and '"@type":"Recipe"' not in halwa:
    raise SystemExit("/recipes/halwa-puri.html: Recipe structured data marker missing")
if not re.search(r'"keywords"\s*:\s*"[^"]+"', halwa):
    raise SystemExit("/recipes/halwa-puri.html: Recipe structured data keywords missing")
if "noindex" in re.search(r'<meta[^>]+name=["\']robots["\'][^>]*>', halwa, re.I).group(0).lower() if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*>', halwa, re.I) else True:
    raise SystemExit("/recipes/halwa-puri.html: expected an indexable robots meta tag")

# A no-cook drink must not inherit a fabricated cooking duration in deployed Recipe JSON-LD.
lemon_mint = require(
    "/recipes/lemon-mint-sharbat.html",
    "Lemon Mint Sharbat",
    '"@type": "Recipe"',
)
jsonld_blocks = re.findall(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    lemon_mint,
    flags=re.I | re.S,
)
recipe_objects = []
for block in jsonld_blocks:
    try:
        payload = json.loads(unescape(block))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"/recipes/lemon-mint-sharbat.html: invalid JSON-LD: {exc}") from exc
    if isinstance(payload, list):
        recipe_objects.extend(payload)
    elif isinstance(payload, dict):
        graph = payload.get("@graph")
        recipe_objects.extend(graph if isinstance(graph, list) else [payload])
lemon_mint_schema = next(
    (
        item for item in recipe_objects
        if isinstance(item, dict) and item.get("@type") == "Recipe"
    ),
    None,
)
if lemon_mint_schema is None:
    raise SystemExit("/recipes/lemon-mint-sharbat.html: Recipe JSON-LD object missing")
for field, expected in (
    ("prepTime", "PT10M"),
    ("cookTime", "PT0M"),
    ("totalTime", "PT10M"),
):
    if lemon_mint_schema.get(field) != expected:
        raise SystemExit(
            f"/recipes/lemon-mint-sharbat.html: expected {field}={expected!r}, "
            f"got {lemon_mint_schema.get(field)!r}"
        )
print("OK live Lemon Mint Sharbat no-cook Recipe JSON-LD durations")

recipe_dir = Path("_data/recipes")
recipe_images = []
external_recipe_images = []
for recipe_file in sorted(recipe_dir.glob("*.json")):
    recipe_data = json.loads(recipe_file.read_text(encoding="utf-8"))
    image = str(recipe_data.get("image") or "").strip()
    if image.startswith(("http://", "https://")):
        external_recipe_images.append((recipe_file.stem, image))
    elif image:
        recipe_images.append((recipe_file.stem, "/" + image.lstrip("/")))

if external_recipe_images:
    raise SystemExit(
        "External recipe image URLs remain after localization: "
        + ", ".join(f"{slug}={url}" for slug, url in external_recipe_images)
    )

if len(recipe_images) != 66:
    raise SystemExit(f"Expected 66 local recipe images, found {len(recipe_images)}")

for slug, image_path in recipe_images:
    versioned_image_path = f"{image_path}?v={RECIPE_IMAGE_VERSION}"
    status, final_url, body, content_type = fetch_binary(versioned_image_path)
    if status != 200:
        raise SystemExit(f"{slug}: {image_path} expected HTTP 200, got {status}")
    if final_url.rstrip("/") != (BASE + versioned_image_path).rstrip("/"):
        if not final_url.startswith(BASE + "/"):
            raise SystemExit(f"{slug}: unexpected image redirect target {final_url}")
    if not content_type.lower().startswith("image/"):
        raise SystemExit(f"{slug}: {image_path} returned non-image content type {content_type!r}")
    if len(body) < 1024:
        raise SystemExit(f"{slug}: {image_path} is suspiciously small ({len(body)} bytes)")

print(f"OK live recipe image assets ({len(recipe_images)} local images, 0 external URLs)")

ads = require("/ads.txt", ADSENSE_CLIENT.replace("ca-", ""))
ads_lines = [line.strip() for line in ads.splitlines() if line.strip()]
if ads_lines != [EXPECTED_ADS]:
    raise SystemExit(f"/ads.txt: expected exactly {EXPECTED_ADS!r}, got {ads_lines!r}")

robots = require("/robots.txt", "User-agent: *", BASE + "/sitemap.xml")
if "Disallow: /" in robots:
    raise SystemExit("/robots.txt: site-wide crawl block found")

sitemap_index = require("/sitemap.xml", BASE + "/sitemap-v2.xml")
try:
    root = ET.fromstring(sitemap_index)
except ET.ParseError as exc:
    raise SystemExit(f"/sitemap.xml: invalid XML: {exc}")
locs = [node.text.strip() for node in root.findall(".//{*}loc") if node.text]
if locs != [BASE + "/sitemap-v2.xml"]:
    raise SystemExit(f"/sitemap.xml: unexpected sitemap index entries {locs!r}")

sitemap = require(
    "/sitemap-v2.xml",
    BASE + "/recipes/chicken-biryani.html",
    BASE + "/recipes/halwa-puri.html",
    BASE + "/about.html",
    BASE + "/editorial-policy.html",
)
try:
    root = ET.fromstring(sitemap)
except ET.ParseError as exc:
    raise SystemExit(f"/sitemap-v2.xml: invalid XML: {exc}")
urls = [node.text.strip() for node in root.findall(".//{*}loc") if node.text]
if len(urls) < 200:
    raise SystemExit(f"/sitemap-v2.xml: suspiciously small deployed sitemap ({len(urls)} URLs)")
if len(urls) != len(set(urls)):
    raise SystemExit("/sitemap-v2.xml: duplicate URLs found")
if any(not url.startswith(BASE + "/") for url in urls):
    raise SystemExit("/sitemap-v2.xml: one or more URLs are off the canonical domain")
print(f"OK sitemap-v2 canonical URL set ({len(urls)} URLs)")

# Confirm that every indexable recipe submitted in the sitemap actually
# loads on the public custom domain with coherent SEO and recipe content.
# This is a live HTTP and structured-data check, not Google index coverage.
sitemap_url_set = set(urls)
recipe_files = sorted(recipe_dir.glob("*.json"))
if len(recipe_files) != 66:
    raise SystemExit(f"Expected 66 recipe source files, found {len(recipe_files)}")

# Protect representative recipe-to-guide links at the deployed domain, not only
# in the rendered build. These cover distinct cooking clusters and catch a stale
# or accidentally stripped shared-layout section after deployment.
EXPECTED_CONTEXTUAL_GUIDE_LINKS = {
    "chicken-biryani": "../guides/what-is-dum-cooking.html",
    "chicken-karahi": "../guides/why-karahi-tastes-like-tomato.html",
    "chicken-tikka": "../guides/why-use-yogurt-in-marinade.html",
    "pakistani-samosa": "../guides/why-samosas-burst-while-frying.html",
    "aloo-paratha": "../guides/why-paratha-does-not-layer.html",
    "daal-chawal": "../guides/how-to-balance-daal-tadka.html",
    "rice-kheer": "../guides/why-kheer-burns-at-bottom.html",
    "kashmiri-chai": "../guides/how-to-balance-kashmiri-chai.html",
}

if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" not in home:
    raise SystemExit("/: AdSense publisher loader is missing from the homepage")
if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" in directory:
    raise SystemExit("/recipes/: AdSense loader unexpectedly on the directory")

for recipe_file in recipe_files:
    slug = recipe_file.stem
    source_recipe = json.loads(recipe_file.read_text(encoding="utf-8"))
    url = f"{BASE}/recipes/{slug}.html"
    if url not in sitemap_url_set:
        raise SystemExit(f"{slug}: public recipe URL missing from sitemap")

    page = require(f"/recipes/{slug}.html")
    if "{{" in page or "{%" in page:
        raise SystemExit(f"{slug}: unresolved template syntax in live HTML")
    if f'<h1>{source_recipe["name"]} Recipe</h1>' not in unescape(page):
        raise SystemExit(f"{slug}: expected recipe heading not rendered")

    expected_guide_link = EXPECTED_CONTEXTUAL_GUIDE_LINKS.get(slug)
    if expected_guide_link and f'href="{expected_guide_link}"' not in page:
        raise SystemExit(
            f"{slug}: expected deployed contextual guide link {expected_guide_link!r} is missing"
        )

    canonical_tag = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*>', page, re.I)
    canonical_href = (re.search(r'href=["\']([^"\']+)["\']', canonical_tag.group(0), re.I)
                      if canonical_tag else None)
    if not canonical_href or canonical_href.group(1) != url:
        raise SystemExit(f"{slug}: live canonical is not {url}")

    robots_tag = re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*>', page, re.I)
    if not robots_tag or "noindex" in robots_tag.group(0).lower():
        raise SystemExit(f"{slug}: live recipe has no indexable robots directive")
    if "data-recipe-lang=\"ur\"" not in page or "data-recipe-panel=\"ur\"" not in page:
        raise SystemExit(f"{slug}: English/Urdu recipe switch is missing")
    if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" not in page:
        raise SystemExit(f"{slug}: AdSense publisher loader missing from recipe article")

    scripts = re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        page, re.I | re.S,
    )
    recipe_nodes = []
    for raw in scripts:
        try:
            graph = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{slug}: invalid live JSON-LD: {exc}")
        if isinstance(graph, dict):
            nodes = graph.get("@graph", [graph])
            if isinstance(nodes, list):
                recipe_nodes.extend(
                    item for item in nodes
                    if isinstance(item, dict) and item.get("@type") == "Recipe"
                )
    if len(recipe_nodes) != 1:
        raise SystemExit(f"{slug}: expected one live Recipe schema node, found {len(recipe_nodes)}")
    node = recipe_nodes[0]
    if node.get("name") != source_recipe["name"] or node.get("url") != url:
        raise SystemExit(f"{slug}: live Recipe schema identity differs from source")
    instructions = node.get("recipeInstructions", [])
    if len(instructions) < 5 or len(instructions) != len(source_recipe["method"]):
        raise SystemExit(f"{slug}: live Recipe schema instruction count mismatch")
    for position, instruction in enumerate(instructions, 1):
        if not isinstance(instruction, dict) or instruction.get("@type") != "HowToStep":
            raise SystemExit(f"{slug}: malformed Recipe schema step {position}")
        if instruction.get("url") != f"{url}#step-{position}":
            raise SystemExit(f"{slug}: invalid live step anchor {position}")
        step_photos = source_recipe.get("step_images") or []
        has_source_photo = isinstance(step_photos, list) and (
            position <= len(step_photos) and bool(step_photos[position - 1])
        )
        if bool(instruction.get("image")) != bool(has_source_photo):
            raise SystemExit(f"{slug}: live step image has no matching source photo")

print(f"OK all {len(recipe_files)} deployed recipe HTML pages: canonical, robots, bilingual UI and JSON-LD")
print(f"OK live contextual recipe-to-guide links ({len(EXPECTED_CONTEXTUAL_GUIDE_LINKS)} representative links)")

# The Search Console export reports two pages with redirects but does not
# include their URLs. Recipe pages above already receive full canonical/robots/
# schema checks; inspect every other submitted URL so a redirected category,
# guide, or trust URL cannot silently remain in the XML sitemap.
checked_sitemap_pages = 0
for submitted_url in urls:
    submitted_path = submitted_url.removeprefix(BASE)
    if submitted_path.startswith("/recipes/") and submitted_path.endswith(".html"):
        continue  # All 66 recipe URLs are checked in the recipe loop above.
    status, final_url, _body = fetch(submitted_path)
    if status != 200:
        raise SystemExit(f"sitemap URL did not return HTTP 200: {submitted_url} ({status})")
    if final_url != submitted_url:
        raise SystemExit(
            f"sitemap URL redirects instead of resolving directly: "
            f"{submitted_url} -> {final_url}"
        )
    checked_sitemap_pages += 1
print(f"OK {checked_sitemap_pages} non-recipe sitemap URLs return HTTP 200 without redirects")

guide_hub = require("/guides/", "Pakistani Cooking Guides")
guide_urls = [url for url in urls if url.startswith(BASE + "/guides/") and url.endswith(".html")]
for guide_url in guide_urls:
    filename = guide_url.rsplit("/", 1)[-1]
    if f'href="{filename}"' not in guide_hub:
        raise SystemExit(f"/guides/: live directory is missing indexable guide {filename}")
print(f"OK live guide directory links ({len(guide_urls)} indexable guides)")

for path, marker in (
    ("/about.html", "About"),
    ("/contact.html", "Contact"),
    ("/privacy-policy.html", "Privacy"),
    ("/editorial-policy.html", "Editorial"),
    ("/disclaimer.html", "Disclaimer"),
    ("/terms.html", "Terms"),
    ("/image-credits.html", "Image Credits"),
):
    page = require(path, marker)
    lowered = unescape(page).lower()
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', lowered, re.I):
        raise SystemExit(f"{path}: trust page unexpectedly noindexed")

print("\nLIVE SITE SMOKE PASSED")
