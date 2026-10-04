#!/usr/bin/env python3
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "_data" / "recipes"

REPLACEMENTS = {
  "jalebi": {
    "filename": "FOOD Jalebi.jpg",
    "source": "https://commons.wikimedia.org/wiki/File:FOOD_Jalebi.jpg",
    "author": "Grueslayer",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "pakistani-samosa": {
    "filename": "Samosa-and-Chatni.jpg",
    "source": "https://commons.wikimedia.org/wiki/File:Samosa-and-Chatni.jpg",
    "author": "Kaushalspeed",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "beef-nihari": {
    "filename": "Beef Nihari.JPG",
    "source": "https://commons.wikimedia.org/wiki/File:Beef_Nihari.JPG",
    "author": "Miansari66",
    "license": "CC0 1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/"
  },
  "aloo-gosht": {
    "filename": "Aaloo Gosht.JPG",
    "source": "https://commons.wikimedia.org/wiki/File:Aaloo_Gosht.JPG",
    "author": "Miansari66",
    "license": "CC0 1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/"
  },
  "aloo-paratha": {
    "filename": "AlooParatha.JPG",
    "source": "https://commons.wikimedia.org/wiki/File:AlooParatha.JPG",
    "author": "Yash Agarwal",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "anda-paratha": {
    "filename": "Chotpot mughlai paratha.jpg",
    "source": "https://commons.wikimedia.org/wiki/File:Chotpot_mughlai_paratha.jpg",
    "author": "Rajeeb Dutta",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "bun-kabab": {
    "filename": "Kebab bun 01.jpg",
    "source": "https://commons.wikimedia.org/wiki/File:Kebab_bun_01.jpg",
    "author": "FALHakaFalLin",
    "license": "CC BY-SA 2.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/2.0/"
  },
  "chicken-achari": {
    "filename": "Achari Chicken.jpg",
    "source": "https://commons.wikimedia.org/wiki/File:Achari_Chicken.jpg",
    "author": "Monali.mishra",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "chicken-sajji": {
    "filename": "Sajji.JPG",
    "source": "https://commons.wikimedia.org/wiki/File:Sajji.JPG",
    "author": "Miansari66",
    "license": "CC0 1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/"
  },
  "kabli-pulao": {
    "filename": "Afghani Pulao 1.JPG",
    "source": "https://commons.wikimedia.org/wiki/File:Afghani_Pulao_1.JPG",
    "author": "Miansari66",
    "license": "CC0 1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/"
  },
  "chicken-jalfrezi": {
    "filename": "Chicken Jalfrezi (2103956162).jpg",
    "source": "https://commons.wikimedia.org/wiki/File:Chicken_Jalfrezi_(2103956162).jpg",
    "author": "David Pursehouse",
    "license": "CC BY 2.0",
    "license_url": "https://creativecommons.org/licenses/by/2.0/"
  },
  "rajma-masala": {
    "filename": "Rajma Masala (32081557778).jpg",
    "source": "https://commons.wikimedia.org/wiki/File:Rajma_Masala_(32081557778).jpg",
    "author": "Gaurav Nemade",
    "license": "CC BY-SA 2.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/2.0/"
  }
}

def fetch_commons(filename):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(filename) + "?width=1800"
    req = urllib.request.Request(url, headers={
        "User-Agent": "PakistanFoodPhotoRefresh/1.0 (+https://pakistanfoodrecipes.top/)",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read()
        if not data:
            raise RuntimeError(f"empty download for {filename}")
        return data, resp.geturl()

def open_image(raw_or_path):
    if isinstance(raw_or_path, bytes):
        im = Image.open(io.BytesIO(raw_or_path))
    else:
        im = Image.open(raw_or_path)
    im = ImageOps.exif_transpose(im)
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im

def premium_crop(im):
    target_ratio = 4 / 3
    w, h = im.size
    ratio = w / h

    if ratio > target_ratio:
        crop_h = h
        crop_w = int(round(h * target_ratio))
    else:
        crop_w = w
        crop_h = int(round(w / target_ratio))

    # Necessary aspect crop is already a meaningful zoom for square/portrait/wide photos.
    # Only add a gentle 6% zoom when the source is already close to 4:3.
    if 1.22 <= ratio <= 1.45:
        crop_w = int(crop_w * 0.94)
        crop_h = int(crop_h * 0.94)

    left = max(0, (w - crop_w) // 2)
    top = max(0, (h - crop_h) // 2)
    right = min(w, left + crop_w)
    bottom = min(h, top + crop_h)
    cropped = im.crop((left, top, right, bottom))

    out_w = min(1440, cropped.width)
    out_h = int(round(out_w * 3 / 4))
    if out_h > cropped.height:
        out_h = cropped.height
        out_w = int(round(out_h * 4 / 3))
    if (out_w, out_h) != cropped.size:
        cropped = cropped.resize((out_w, out_h), Image.Resampling.LANCZOS)
    return cropped

def save_webp(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "WEBP", quality=86, method=6)
    with Image.open(path) as check:
        check.verify()
    return path.stat().st_size

def main():
    recipe_files = sorted(RECIPES.glob("*.json"))
    if len(recipe_files) != 66:
        raise SystemExit(f"Expected 66 recipes, found {len(recipe_files)}")

    download_log = {}
    # First replace the 10 explicitly rejected photos with different copyright-safe sources.
    for slug, meta in REPLACEMENTS.items():
        path = RECIPES / f"{slug}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        raw, resolved = fetch_commons(meta["filename"])
        image_path = ROOT / str(data["image"]).lstrip("/")
        im = premium_crop(open_image(raw))
        size = save_webp(im, image_path)

        data["image_source"] = meta["source"]
        data["image_author"] = meta["author"]
        data["image_creator"] = meta["author"]
        data["image_license"] = meta["license"]
        data["image_license_url"] = meta["license_url"]
        data["image_source_label"] = "Wikimedia Commons"
        data["date_modified"] = "2026-10-04"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        download_log[slug] = {
            "source": meta["source"],
            "resolved_download": resolved,
            "author": meta["author"],
            "license": meta["license"],
            "output": str(data["image"]),
            "bytes": size,
        }
        print(f"REPLACED {slug}: {resolved} -> {data['image']} ({size} bytes)")

    # Then normalize the full library to subject-forward 4:3 crops for mobile.
    crop_log = []
    for path in recipe_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        image_rel = str(data.get("image") or "").lstrip("/")
        image_path = ROOT / image_rel
        if not image_path.exists():
            raise SystemExit(f"Missing local image for {path.stem}: {image_rel}")
        im = premium_crop(open_image(image_path))
        size = save_webp(im, image_path)
        crop_log.append({"slug": path.stem, "image": image_rel, "bytes": size})
        print(f"CROPPED {path.stem}: {image_rel} ({size} bytes)")

    report = {
      "policy": "No AI-generated recipe photos. Replacements are downloaded from copyright-safe Wikimedia Commons sources with license metadata retained.",
      "replaced_count": len(REPLACEMENTS),
      "cropped_total": len(crop_log),
      "target_aspect": "4:3",
      "zoom_policy": "Minimum aspect crop plus gentle 6% extra zoom only for images already close to 4:3; avoids over-zooming portrait/square/wide sources.",
      "replacements": download_log,
      "images": crop_log,
    }
    report_path = ROOT / "docs" / "premium-food-photo-crops-2026-10-04.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK replaced={len(REPLACEMENTS)} cropped={len(crop_log)}")

if __name__ == "__main__":
    main()
