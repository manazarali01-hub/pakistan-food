#!/usr/bin/env python3
from __future__ import annotations

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
REPORT = ROOT / "docs" / "visual-polish-repair-2026-10-04.json"
CONFIG = ROOT / "_config.yml"
UA = "PakistanFoodVisualRepair/1.0 (+https://pakistanfoodrecipes.top/)"

def request_bytes(url, accept="image/avif,image/webp,image/apng,image/*,*/*;q=0.8"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
        if not data:
            raise RuntimeError(f"empty response: {url}")
        return data, response.geturl(), response.headers.get("Content-Type", "")

def fetch_pexels(page_url):
    page, _, _ = request_bytes(page_url, "text/html,application/xhtml+xml")
    text = page.decode("utf-8", errors="replace")
    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            image_url = html.unescape(match.group(1))
            return request_bytes(image_url)
    raise RuntimeError(f"Could not find Pexels og:image: {page_url}")

def fetch_commons(filename):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(filename)
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

def crop_4x3(im, zoom=1.0, focal_x=0.5, focal_y=0.5, target_w=1200):
    w, h = im.size
    ratio = 4 / 3
    if w / h >= ratio:
        base_h = h
        base_w = int(round(h * ratio))
    else:
        base_w = w
        base_h = int(round(w / ratio))

    zoom = max(0.55, min(1.0, float(zoom)))
    crop_w = int(base_w * zoom)
    crop_h = int(base_h * zoom)
    if crop_w / crop_h > ratio:
        crop_w = int(round(crop_h * ratio))
    else:
        crop_h = int(round(crop_w / ratio))

    cx = int(round(w * focal_x))
    cy = int(round(h * focal_y))
    left = max(0, min(w - crop_w, cx - crop_w // 2))
    top = max(0, min(h - crop_h, cy - crop_h // 2))
    out = im.crop((left, top, left + crop_w, top + crop_h))

    final_w = min(target_w, out.width)
    final_h = int(round(final_w * 3 / 4))
    if final_h > out.height:
        final_h = out.height
        final_w = int(round(final_h * 4 / 3))
    if out.size != (final_w, final_h):
        out = out.resize((final_w, final_h), Image.Resampling.LANCZOS)
    return out

def save_webp(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "WEBP", quality=88, method=6)
    with Image.open(path) as check:
        check.verify()
    return {"width": im.width, "height": im.height, "bytes": path.stat().st_size}

def load_recipe(slug):
    path = RECIPES / f"{slug}.json"
    return path, json.loads(path.read_text(encoding="utf-8"))

def save_recipe(path, data):
    data["date_modified"] = "2026-10-04"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def set_source(data, source, author, license_name, license_url, label):
    data["image_source"] = source
    data["image_author"] = author
    data["image_creator"] = author
    data["image_license"] = license_name
    data["image_license_url"] = license_url
    data["image_source_label"] = label

def replace_pexels(slug, page, author, out_rel, zoom=0.94, focal_x=0.5, focal_y=0.5):
    path, data = load_recipe(slug)
    raw, resolved, content_type = fetch_pexels(page)
    im = crop_4x3(open_rgb(raw), zoom=zoom, focal_x=focal_x, focal_y=focal_y)
    out = ROOT / out_rel
    info = save_webp(im, out)
    data["image"] = out_rel
    set_source(data, page, author, "Pexels License", "https://www.pexels.com/license/", "Pexels")
    save_recipe(path, data)
    return {"slug": slug, "action": "replace-pexels", "resolved": resolved, "content_type": content_type, **info}

def replace_commons(slug, filename, source, author, license_name, license_url, out_rel, zoom=0.94, focal_x=0.5, focal_y=0.5):
    path, data = load_recipe(slug)
    raw, resolved, content_type = fetch_commons(filename)
    im = crop_4x3(open_rgb(raw), zoom=zoom, focal_x=focal_x, focal_y=focal_y)
    out = ROOT / out_rel
    info = save_webp(im, out)
    data["image"] = out_rel
    set_source(data, source, author, license_name, license_url, "Wikimedia Commons")
    save_recipe(path, data)
    return {"slug": slug, "action": "replace-commons", "resolved": resolved, "content_type": content_type, **info}

def recrop_local(slug, out_rel, zoom, focal_x=0.5, focal_y=0.5):
    path, data = load_recipe(slug)
    src = ROOT / str(data["image"]).lstrip("/")
    im = crop_4x3(open_rgb(src), zoom=zoom, focal_x=focal_x, focal_y=focal_y)
    out = ROOT / out_rel
    info = save_webp(im, out)
    data["image"] = out_rel
    save_recipe(path, data)
    return {"slug": slug, "action": "recrop-local", **info}

def bump_cache():
    text = CONFIG.read_text(encoding="utf-8")
    text, count = re.subn(
        r'^recipe_image_version:\s*["\']?[^"\'\s]+["\']?',
        'recipe_image_version: "20261004-final5"',
        text,
        count=1,
        flags=re.M,
    )
    if count != 1:
        raise RuntimeError("Could not bump recipe_image_version")
    CONFIG.write_text(text, encoding="utf-8")

def main():
    results = []

    # Exact user-supplied Samosa photo recovered as its original Pexels photograph.
    results.append(replace_pexels(
        "pakistani-samosa",
        "https://www.pexels.com/photo/close-up-photo-of-fried-food-on-saucer-2474658/",
        "Marvin Ozz",
        "assets/pakistani-samosa-v3.webp",
        zoom=0.90, focal_x=0.53, focal_y=0.52,
    ))

    # Clearer, food-forward Daal Chawal.
    results.append(replace_pexels(
        "daal-chawal",
        "https://www.pexels.com/photo/meal-with-rice-on-plate-8996219/",
        "I Own My Food Art",
        "assets/recipe-images/daal-chawal-v2.webp",
        zoom=0.94, focal_x=0.50, focal_y=0.50,
    ))

    # Re-fetch the exact Chicken Handi source at full resolution and crop around the food.
    results.append(replace_commons(
        "chicken-handi",
        "Punjabi Chicken Handi 1.JPG",
        "https://commons.wikimedia.org/wiki/File:Punjabi_Chicken_Handi_1.JPG",
        "Miansari66",
        "CC0 1.0",
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "assets/recipe-images/chicken-handi-v2.webp",
        zoom=0.72, focal_x=0.52, focal_y=0.51,
    ))

    # Replace process/raw-looking Sajji with an actual plated Sajji photograph.
    results.append(replace_commons(
        "chicken-sajji",
        "Sajji.JPG",
        "https://commons.wikimedia.org/wiki/File:Sajji.JPG",
        "Miansari66",
        "CC0 1.0",
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "assets/recipe-images/chicken-sajji-v2.webp",
        zoom=0.82, focal_x=0.50, focal_y=0.50,
    ))

    # Put visible halwa, puri and chana in the hero instead of a frying-basket process shot.
    results.append(replace_commons(
        "halwa-puri",
        "Nihari & Halwa Puri - Breakfast of every Lahori.jpg",
        "https://commons.wikimedia.org/wiki/File:Nihari_%26_Halwa_Puri_-_Breakfast_of_every_Lahori.jpg",
        "Robin Crusoe",
        "CC BY-SA 4.0",
        "https://creativecommons.org/licenses/by-sa/4.0/",
        "assets/recipe-images/halwa-puri-v2.webp",
        zoom=0.92, focal_x=0.53, focal_y=0.54,
    ))

    # Use the actual cooked Lahori Chargha source rather than the steam-stage image.
    results.append(replace_commons(
        "lahori-chargha",
        "Lahori Charga.JPG",
        "https://commons.wikimedia.org/wiki/File:Lahori_Charga.JPG",
        "Miansari66",
        "CC0 1.0",
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "assets/recipe-images/lahori-chargha-v2.webp",
        zoom=0.78, focal_x=0.50, focal_y=0.50,
    ))

    # Current Noon Chai photo is accurate, but too much empty table is visible.
    results.append(recrop_local(
        "kashmiri-chai",
        "assets/recipe-images/kashmiri-chai-v2.webp",
        zoom=0.66, focal_x=0.50, focal_y=0.63,
    ))

    bump_cache()

    for row in results:
        if row["width"] * 3 != row["height"] * 4:
            raise RuntimeError(f'{row["slug"]}: not exact 4:3')
        if row["bytes"] < 20000:
            raise RuntimeError(f'{row["slug"]}: suspiciously small output: {row["bytes"]}')

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "policy": "Real photographs only; exact or clearly relevant dish photography; no AI food images.",
        "cache_version": "20261004-final5",
        "changed": [row["slug"] for row in results],
        "results": results,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    print("OK visual polish repair")

if __name__ == "__main__":
    main()
