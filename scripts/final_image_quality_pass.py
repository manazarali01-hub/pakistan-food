#!/usr/bin/env python3
import base64
import html
import io
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "_data" / "recipes"
REPORT = ROOT / "docs" / "final-image-quality-pass-2026-10-04.json"
UA = "PakistanFoodFinalImagePass/1.0 (+https://pakistanfoodrecipes.top/)"

COMMONS = {
    "aloo-paratha": {
        "filename": "Aloo Paratha.jpg",
        "source": "https://commons.wikimedia.org/wiki/File:Aloo_Paratha.jpg",
        "author": "Gannu03",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "zoom": 0.94,
    },
    "anda-paratha": {
        "filename": "Anda Paratha.jpg",
        "source": "https://commons.wikimedia.org/wiki/File:Anda_Paratha.jpg",
        "author": "Vinodbarc",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "zoom": 0.96,
    },
    "chicken-sajji": {
        "filename": "Sajji. A culture itself.jpg",
        "source": "https://commons.wikimedia.org/wiki/File:Sajji._A_culture_itself.jpg",
        "author": "Mustafa usman",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "zoom": 0.92,
    },
    "daal-chawal": {
        "filename": "C8-DPPxXsAEeCOy.jpg",
        "source": "https://commons.wikimedia.org/wiki/File:C8-DPPxXsAEeCOy.jpg",
        "author": "Maryum Siddiqui",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "zoom": 0.92,
    },
    "halwa-puri": {
        "filename": "Halwa Puri, a traditional food made in Walled City of Lahore.jpg",
        "source": "https://commons.wikimedia.org/wiki/File:Halwa_Puri,_a_traditional_food_made_in_Walled_City_of_Lahore.jpg",
        "author": "Tahsin Shah",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "zoom": 0.98,
    },
    "kashmiri-chai": {
        "filename": "Noon Chai.jpg",
        "source": "https://commons.wikimedia.org/wiki/File:Noon_Chai.jpg",
        "author": "Naryiitmandi",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "zoom": 0.91,
    },
    "paya": {
        "filename": "Siri Payey (Head and feet curry of Goat), a traditional breakfast food of Pakistan.jpg",
        "source": "https://commons.wikimedia.org/wiki/File:Siri_Payey_(Head_and_feet_curry_of_Goat),_a_traditional_breakfast_food_of_Pakistan.jpg",
        "author": "Tahsin Shah",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "zoom": 0.90,
    },
    "aloo-gosht": {
        "filename": "Odia Mutton Curry (Mansha Tarkari).jpg",
        "source": "https://commons.wikimedia.org/wiki/File:Odia_Mutton_Curry_(Mansha_Tarkari).jpg",
        "author": "Satwik Cuttack",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "zoom": 0.90,
    },
}

# Existing real photos that only need a stronger food-first crop.
ZOOM = {
    "chicken-biryani": 0.86,
    "beef-nihari": 0.88,
    "aloo-keema": 0.90,
    "aloo-palak": 0.90,
    "bhindi-gosht": 0.90,
    "chicken-handi": 0.90,
    "chicken-qorma": 0.90,
    "kabli-pulao": 0.86,
    "lahori-chargha": 0.88,
    "mutton-karahi": 0.90,
    "reshmi-kabab": 0.90,
    "white-chicken-karahi": 0.90,
}

def request_bytes(url, accept="image/avif,image/webp,image/apng,image/*,*/*;q=0.8"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=50) as response:
        data = response.read()
        if not data:
            raise RuntimeError(f"empty response: {url}")
        return data, response.geturl(), response.headers.get("Content-Type", "")

def fetch_commons(filename):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(filename) + "?width=1800"
    return request_bytes(url)

def open_rgb(raw_or_path):
    if isinstance(raw_or_path, bytes):
        im = Image.open(io.BytesIO(raw_or_path))
    else:
        im = Image.open(raw_or_path)
    im = ImageOps.exif_transpose(im)
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im

def crop_4x3(im, zoom=1.0, focal_x=0.5, focal_y=0.5):
    w, h = im.size
    target = 4 / 3
    if w / h >= target:
        crop_h = h
        crop_w = int(round(h * target))
    else:
        crop_w = w
        crop_h = int(round(w / target))

    zoom = max(0.80, min(1.0, float(zoom)))
    crop_w = max(4, int(crop_w * zoom))
    crop_h = max(3, int(crop_h * zoom))
    # Preserve exact 4:3 after extra zoom.
    if crop_w / crop_h > target:
        crop_w = int(round(crop_h * target))
    else:
        crop_h = int(round(crop_w / target))

    cx = int(round(w * focal_x))
    cy = int(round(h * focal_y))
    left = max(0, min(w - crop_w, cx - crop_w // 2))
    top = max(0, min(h - crop_h, cy - crop_h // 2))
    out = im.crop((left, top, left + crop_w, top + crop_h))

    max_w = min(1440, out.width, int(out.height * 4 / 3))
    target_w = max(4, (max_w // 4) * 4)
    target_h = (target_w // 4) * 3
    if out.size != (target_w, target_h):
        out = out.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return out

def save_webp(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "WEBP", quality=86, method=6)
    with Image.open(path) as check:
        check.verify()
    return {"bytes": path.stat().st_size, "width": im.width, "height": im.height}

def recipe(slug):
    path = RECIPES / f"{slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return path, data

def write_recipe(path, data):
    data["date_modified"] = "2026-10-04"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def image_path(data):
    rel = str(data["image"]).lstrip("/")
    if rel.startswith(("http://", "https://")):
        raise RuntimeError(f"Expected local image, got {rel}")
    return ROOT / rel

def apply_source(data, source, author, license_name, license_url, label):
    data["image_source"] = source
    data["image_author"] = author
    data["image_creator"] = author
    data["image_license"] = license_name
    data["image_license_url"] = license_url
    data["image_source_label"] = label

def reconstruct_samosa():
    parts = sorted((ROOT / "tmp").glob("samosa.b64.part*"))
    if len(parts) != 5:
        raise RuntimeError(f"Expected 5 samosa base64 parts, found {len(parts)}")
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    raw = base64.b64decode(encoded, validate=True)
    path, data = recipe("pakistani-samosa")
    out = image_path(data)
    im = crop_4x3(open_rgb(raw), zoom=0.96, focal_x=0.53, focal_y=0.50)
    info = save_webp(im, out)
    # User supplied this exact photograph in the conversation. Do not invent a third-party attribution.
    for key in ("image_source", "image_author", "image_creator", "image_license", "image_license_url", "image_source_label"):
        data.pop(key, None)
    data["image_caption"] = "Golden Pakistani samosas served with fresh greens and sliced red onion."
    data["image_alt"] = "Golden Pakistani samosas with fresh greens and sliced red onion"
    write_recipe(path, data)
    return {"slug": "pakistani-samosa", "action": "user-photo", **info}

def replace_commons(slug, meta):
    path, data = recipe(slug)
    raw, resolved, content_type = fetch_commons(meta["filename"])
    im = crop_4x3(open_rgb(raw), zoom=meta.get("zoom", 0.94))
    info = save_webp(im, image_path(data))
    apply_source(data, meta["source"], meta["author"], meta["license"], meta["license_url"], "Wikimedia Commons")
    write_recipe(path, data)
    return {"slug": slug, "action": "replace-commons", "resolved": resolved, "content_type": content_type, **info}

def zoom_existing(slug, factor):
    path, data = recipe(slug)
    out = image_path(data)
    im = crop_4x3(open_rgb(out), zoom=factor)
    info = save_webp(im, out)
    data["date_modified"] = "2026-10-04"
    write_recipe(path, data)
    return {"slug": slug, "action": "zoom-existing", "zoom_factor": factor, **info}

def main():
    results = []
    results.append(reconstruct_samosa())

    for slug, meta in COMMONS.items():
        results.append(replace_commons(slug, meta))
    for slug, factor in ZOOM.items():
        results.append(zoom_existing(slug, factor))

    # Mutton biryani intentionally untouched: user explicitly approved it.
    # Chicken Handi remains existing real local photo, only reframed.
    expected = {"pakistani-samosa", *COMMONS.keys(), *ZOOM.keys()}
    done = {row["slug"] for row in results}
    if done != expected:
        raise RuntimeError(f"Image pass mismatch: expected {sorted(expected)}, got {sorted(done)}")

    for row in results:
        if row["width"] * 3 != row["height"] * 4:
            raise RuntimeError(f"{row['slug']}: output is not exact 4:3 ({row['width']}x{row['height']})")
        if row["bytes"] < 20_000:
            raise RuntimeError(f"{row['slug']}: suspiciously small output ({row['bytes']} bytes)")

    report = {
        "policy": "Real photographs only. No AI-generated food images used.",
        "user_supplied_samosa": True,
        "replacements": sorted([r["slug"] for r in results if r["action"].startswith("replace") or r["action"] == "user-photo"]),
        "zoom_only": sorted([r["slug"] for r in results if r["action"] == "zoom-existing"]),
        "untouched_approved": ["mutton-biryani"],
        "results": sorted(results, key=lambda x: x["slug"]),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))
    print(f"OK final image quality pass: {len(results)} recipe images changed")

if __name__ == "__main__":
    main()
