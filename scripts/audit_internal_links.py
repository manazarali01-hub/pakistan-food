"""Report internal-link coverage for indexable sitemap URLs in the rendered site.

This is a read-only audit. It counts unique indexable source pages linking to each
indexable sitemap target, ignores nofollow links, and resolves relative URLs against
the rendered source page. It does not alter content or automatically add links.
"""
from __future__ import annotations

from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
BASE = "https://pakistanfoodrecipes.top"


class LinksParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.robots = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            rel = {x.lower() for x in (values.get("rel") or "").split()}
            self.links.append((values["href"], "nofollow" in rel))
        if tag == "meta" and (values.get("name") or "").lower() == "robots":
            self.robots.append((values.get("content") or "").lower())


def normalized_url(url: str) -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path or "/")
    if path.endswith("/index.html"):
        path = path[:-10]
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return BASE + path


def main() -> int:
    if not SITE.is_dir():
        raise SystemExit("Rendered _site directory is missing; run the Jekyll build first.")
    try:
        sitemap = ET.parse(SITE / "sitemap-v2.xml")
    except (OSError, ET.ParseError) as exc:
        raise SystemExit(f"Cannot read rendered sitemap-v2.xml: {exc}")
    targets = set()
    for node in sitemap.findall(".//{*}loc"):
        url = (node.text or "").strip()
        parsed = urlparse(url)
        if parsed.scheme == "https" and parsed.netloc == "pakistanfoodrecipes.top" and not parsed.query and not parsed.fragment:
            targets.add(normalized_url(url))

    pages = {}
    for file in SITE.rglob("*.html"):
        relative = file.relative_to(SITE).as_posix()
        path = "/" + relative
        if path.endswith("/index.html"):
            path = path[:-10]
        elif path == "/index.html":
            path = "/"
        page_url = BASE + path
        parser = LinksParser()
        try:
            parser.feed(file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            continue
        robots = " ".join(parser.robots)
        if "noindex" in robots:
            continue
        pages[normalized_url(page_url)] = (page_url, parser.links)

    inbound = defaultdict(set)
    missing = []
    for source_key, (source_url, links) in pages.items():
        for href, nofollow in links:
            if nofollow:
                continue
            absolute = urljoin(source_url, href)
            parsed = urlparse(absolute)
            if parsed.scheme not in ("http", "https") or parsed.netloc.lower() not in ("pakistanfoodrecipes.top", "www.pakistanfoodrecipes.top"):
                continue
            target = normalized_url(absolute)
            if target in targets:
                if target != source_key:
                    inbound[target].add(source_key)
            elif parsed.path.endswith((".html", "/")) and not parsed.query and not parsed.fragment:
                # Record only local HTML-like paths; the rendered-link verifier separately
                # owns hard failures for broken destinations.
                if (SITE / parsed.path.lstrip("/")).is_file() is False and not parsed.path.endswith("/"):
                    missing.append((source_url, parsed.path))

    indexable_targets = sorted(targets)
    counts = [(url, len(inbound[url])) for url in indexable_targets]
    low = [(url, count) for url, count in counts if count <= 1]
    zero = [(url, count) for url, count in counts if count == 0]
    print("INTERNAL LINK COVERAGE AUDIT (rendered sitemap targets)")
    print(f"Indexable sitemap targets: {len(indexable_targets)}")
    print(f"Indexable rendered HTML pages: {len(pages)}")
    print(f"Targets with zero internal followed-linking pages: {len(zero)}")
    print(f"Targets with zero or one internal followed-linking page: {len(low)}")
    print("\nLOW-COVERAGE TARGETS (0–1 unique source pages)")
    for url, count in low:
        print(f"{count}\t{url}")
    print("\nAudit is report-only; no links or pages were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
