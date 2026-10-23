"""Verify Ahrefs Web Analytics is present in deployed public HTML without logging its key."""

from __future__ import annotations

from html import unescape
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://pakistanfoodrecipes.top"
SCRIPT_URL = "https://analytics.ahrefs.com/analytics.js"
CONFIG = Path("_config.yml").read_text(encoding="utf-8")
match = re.search(r'^ahrefs_analytics_key:\s*["\']?([^"\'\s]+)["\']?\s*$', CONFIG, re.M)
if not match:
    raise SystemExit("FAIL: Ahrefs analytics key missing or malformed in _config.yml")
expected_key = match.group(1)

PAGES = (
    "/",
    "/recipes/chicken-biryani.html",
    "/recipes/rice/",
)
TAG_RE = re.compile(r"<script\b[^>]*>", re.I)


def get(url: str) -> str:
    """Fetch a public page with bounded retries for transient CDN/hosting errors."""
    last_error: Exception | None = None
    for attempt in range(1, 6):
        request = Request(
            url,
            headers={
                "User-Agent": "PakistanFoodAhrefsVerification/1.0",
                "Cache-Control": "no-cache",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            },
        )
        try:
            with urlopen(request, timeout=25) as response:
                if response.status == 200:
                    return response.read().decode("utf-8", errors="replace")
                last_error = RuntimeError(f"HTTP {response.status} for {url}")
        except HTTPError as exc:
            last_error = exc
            if exc.code not in (408, 429, 500, 502, 503, 504):
                break
        except (URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt < 5:
            print(f"Retry {attempt}/4 for {url}: {type(last_error).__name__}")
            time.sleep(3)
    raise SystemExit(f"FAIL: Could not fetch {url} after retries: {type(last_error).__name__}") from last_error


for path in PAGES:
    html = unescape(get(BASE + path))
    tags = TAG_RE.findall(html)
    matching = []
    for tag in tags:
        src = re.search(r'\bsrc=["\']([^"\']+)["\']', tag, re.I)
        if src and src.group(1) == SCRIPT_URL:
            matching.append(tag)
    if len(matching) != 1:
        raise SystemExit(f"FAIL: {path} expected one Ahrefs analytics script tag; found {len(matching)}")
    key_attr = re.search(r'\bdata-key=["\']([^"\']+)["\']', matching[0], re.I)
    if not key_attr or key_attr.group(1) != expected_key:
        raise SystemExit(f"FAIL: {path} Ahrefs data-key is missing or does not match configured key")
    print(f"PASS: {path} contains exactly one correctly configured Ahrefs script (key redacted)")

# Confirm the vendor script URL itself responds, without printing response content.
vendor_error: Exception | None = None
for attempt in range(1, 6):
    try:
        request = Request(SCRIPT_URL, headers={"User-Agent": "PakistanFoodAhrefsVerification/1.0"})
        with urlopen(request, timeout=25) as response:
            if response.status != 200:
                vendor_error = RuntimeError(f"HTTP {response.status}")
            else:
                content_type = response.headers.get("Content-Type", "").lower()
                if "javascript" not in content_type and "text/plain" not in content_type:
                    raise SystemExit("FAIL: Ahrefs analytics.js returned an unexpected content type")
                vendor_error = None
        if vendor_error is None:
            break
    except HTTPError as exc:
        vendor_error = exc
        if exc.code not in (408, 429, 500, 502, 503, 504):
            break
    except (URLError, TimeoutError, OSError) as exc:
        vendor_error = exc
    if attempt < 5:
        print(f"Retry {attempt}/4 for Ahrefs analytics.js: {type(vendor_error).__name__}")
        time.sleep(3)
if vendor_error is not None:
    raise SystemExit(f"FAIL: Ahrefs analytics.js could not be fetched after retries: {type(vendor_error).__name__}") from vendor_error

print("PASS: Ahrefs analytics.js endpoint responds successfully")
print("AHREFS LIVE VERIFICATION PASSED")
