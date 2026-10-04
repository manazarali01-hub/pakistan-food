"""Post-deploy smoke checks for the public Pakistan Food custom domain.

This runs after GitHub Pages reports a successful deployment. It verifies the deployed
site rather than only the repository/Jekyll build, with retries for CDN/DNS propagation.
"""

from __future__ import annotations

from html import unescape
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

BASE = "https://pakistanfoodrecipes.top"
USER_AGENT = "PakistanFoodLiveSmoke/1.0 (+https://pakistanfoodrecipes.top/)"
ATTEMPTS = 8
DELAY_SECONDS = 10

EXPECTED_ADS = "google.com, pub-4531216214099892, DIRECT, f08c47fec0942fa0"

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

home = require("/", "Pakistan Food", "Flavours worth sharing.")
if "{{ dish.name }}" in home:
    raise SystemExit("/: unresolved Liquid/template marker found in deployed homepage")

halwa = require(
    "/recipes/halwa-puri.html",
    "Halwa Puri Recipe",
    "https://live.staticflickr.com/4546/38452599836_a1031bd01d_k.jpg",
    "Umair Abbasi",
    "Flickr",
    "CC BY-SA 2.0",
    'https://pakistanfoodrecipes.top/recipes/halwa-puri.html',
)
if '"@type": "Recipe"' not in halwa and '"@type":"Recipe"' not in halwa:
    raise SystemExit("/recipes/halwa-puri.html: Recipe structured data marker missing")
if "noindex" in re.search(r'<meta[^>]+name=["\']robots["\'][^>]*>', halwa, re.I).group(0).lower() if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*>', halwa, re.I) else True:
    raise SystemExit("/recipes/halwa-puri.html: expected an indexable robots meta tag")

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
