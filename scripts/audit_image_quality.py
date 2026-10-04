"""Audit recipe image transparency and client-side image delivery."""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "_data" / "recipes"

rows = []
for file in sorted(RECIPES.glob("*.json")):
    data = json.loads(file.read_text(encoding="utf-8"))
    image = str(data.get("image", ""))
    external = image.startswith(("http://", "https://"))
    commons = "commons.wikimedia.org" in image
    rows.append({
        "slug": file.stem,
        "image": image,
        "external": external,
        "commons": commons,
        "source": bool(data.get("image_source")),
        "author": bool(data.get("image_author")),
        "license": bool(data.get("image_license")),
        "alt": bool(data.get("image_alt")),
        "caption": bool(data.get("image_caption")),
    })

external = [r for r in rows if r["external"]]
local = [r for r in rows if not r["external"]]
full_credit = [r for r in external if r["source"] and r["author"] and r["license"]]
missing_source = [r for r in external if not r["source"]]
partial_credit = [r for r in external if any((r["source"], r["author"], r["license"])) and not all((r["source"], r["author"], r["license"]))]

print("IMAGE QUALITY AUDIT")
print(f"Recipes: {len(rows)}")
print(f"External recipe images: {len(external)}")
print(f"Local recipe images: {len(local)}")
print(f"External images with full source/author/license metadata: {len(full_credit)}")
print(f"External images missing image_source: {len(missing_source)}")
print(f"External images with partial attribution metadata: {len(partial_credit)}")
print(f"Missing image alt text: {sum(not r['alt'] for r in rows)}")
print(f"Missing image captions: {sum(not r['caption'] for r in rows)}")

if missing_source:
    print("\nEXTERNAL IMAGES MISSING SOURCE METADATA")
    for r in missing_source:
        print(f"- {r['slug']}: {r['image']}")

if partial_credit:
    print("\nPARTIAL ATTRIBUTION RECORDS")
    for r in partial_credit:
        print(f"- {r['slug']}: source={r['source']} author={r['author']} license={r['license']}")

client = (ROOT / "recipes-data.js").read_text(encoding="utf-8")
main_js = (ROOT / "script.js").read_text(encoding="utf-8")

errors = []
if "images.weserv.nl" in client or "images.weserv.nl" in main_js:
    errors.append("third-party weserv image proxy remains in homepage client code")
if "const localFallbacks" in client or "const jpgFallbacks" in client:
    errors.append("stale hard-coded image fallback catalogue remains in recipes-data.js")
if "assets/chicken-biryani.webp" in client:
    errors.append("old chicken-biryani hero remains as a client fallback")
if any(not r["alt"] or not r["caption"] for r in rows):
    errors.append("one or more recipes are missing image alt/caption")

if errors:
    raise SystemExit("\n".join(errors))

print("\nImage delivery audit complete.")
