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

EXPECTED_ADS = "google.com, pub-4531216214099892, DIRECT, f08c47fec0942fa0"
_config_text = Path("_config.yml").read_text(encoding="utf-8")
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

home = require("/", "Pakistan Food", "Flavours worth sharing.")
if f"?v={RECIPE_IMAGE_VERSION}" not in home:
    raise SystemExit(f"/: recipe image cache-busting version {RECIPE_IMAGE_VERSION!r} missing")
if "{{ dish.name }}" in home:
    raise SystemExit("/: unresolved Liquid/template marker found in deployed homepage")

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
if not re.search(r'"keywords"\\s*:\\s*"[^"]+"', halwa):
    raise SystemExit("/recipes/halwa-puri.html: Recipe structured data keywords missing")
if "noindex" in re.search(r'<meta[^>]+name=["\']robots["\'][^>]*>', halwa, re.I).group(0).lower() if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*>', halwa, re.I) else True:
    raise SystemExit("/recipes/halwa-puri.html: expected an indexable robots meta tag")


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

ads = require("/ads.txt", "pub-4531216214099892")
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
