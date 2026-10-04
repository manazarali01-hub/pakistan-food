#!/usr/bin/env python3
import io
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "_data" / "recipes"
OUT_DIR = ROOT / "assets" / "recipe-images"
REPORT = ROOT / "docs" / "image-localization-report-2026-10-04.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_LICENSE_TOKENS = ("cc by", "cc-by", "cc0", "public domain")
MAX_EDGE = 1600
QUALITY = 84

def allowed_license(value):
    text = str(value or "").strip().lower()
    return bool(text) and any(token in text for token in ALLOWED_LICENSE_TOKENS)

def fetch_bytes(url, attempts=4):
    last = None
    for n in range(attempts):
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "PakistanFoodImageMirror/1.0 (+https://pakistanfoodrecipes.top/)",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = resp.read()
                final_url = resp.geturl()
                content_type = resp.headers.get("Content-Type", "")
                if not data:
                    raise RuntimeError("empty response")
                return data, final_url, content_type
        except Exception as exc:
            last = exc
            if n + 1 < attempts:
                time.sleep(1.5 * (n + 1))
    raise RuntimeError(str(last))

def convert_webp(raw, target):
    with Image.open(io.BytesIO(raw)) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "RGBA"):
            if "A" in im.getbands():
                im = im.convert("RGBA")
            else:
                im = im.convert("RGB")
        if max(im.size) > MAX_EDGE:
            im.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
        target.parent.mkdir(parents=True, exist_ok=True)
        im.save(target, "WEBP", quality=QUALITY, method=6)
        with Image.open(target) as check:
            check.verify()
    return target.stat().st_size

def process(path):
    slug = path.stem
    data = json.loads(path.read_text(encoding="utf-8"))
    image = str(data.get("image") or "").strip()
    if not image.startswith(("http://", "https://")):
        return {"slug": slug, "status": "already-local", "image": image}

    license_name = data.get("image_license")
    source = data.get("image_source")
    creator = data.get("image_creator") or data.get("image_author")
    if not allowed_license(license_name):
        return {
            "slug": slug,
            "status": "skipped-license",
            "image": image,
            "license": license_name,
            "source": source,
            "creator": creator,
        }
    if not source:
        return {
            "slug": slug,
            "status": "skipped-missing-source",
            "image": image,
            "license": license_name,
        }

    raw, final_url, content_type = fetch_bytes(image)
    target = OUT_DIR / f"{slug}.webp"
    size = convert_webp(raw, target)
    local_path = f"assets/recipe-images/{slug}.webp"
    data["image"] = local_path
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "slug": slug,
        "status": "localized",
        "old_image": image,
        "new_image": local_path,
        "resolved_url": final_url,
        "content_type": content_type,
        "bytes": size,
        "license": license_name,
        "source": source,
        "creator": creator,
    }

def main():
    recipe_files = sorted(RECIPES.glob("*.json"))
    external = []
    for path in recipe_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SystemExit(f"Invalid JSON {path}: {exc}")
        if str(data.get("image") or "").startswith(("http://", "https://")):
            external.append(path)

    if not external:
        print("No external recipe images remain; nothing to localize.")
        return

    results = []
    failures = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(process, path): path for path in external}
        for future in as_completed(futures):
            path = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"{result['status']}: {result['slug']}")
            except Exception as exc:
                item = {"slug": path.stem, "status": "failed", "error": str(exc)}
                results.append(item)
                failures.append(item)
                print(f"FAILED: {path.stem}: {exc}")

    results.sort(key=lambda x: x["slug"])
    summary = {
        "external_before": len(external),
        "localized": sum(r["status"] == "localized" for r in results),
        "skipped_license": sum(r["status"] == "skipped-license" for r in results),
        "skipped_missing_source": sum(r["status"] == "skipped-missing-source" for r in results),
        "failed": sum(r["status"] == "failed" for r in results),
        "results": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))

    if failures:
        raise SystemExit(f"{len(failures)} image downloads/conversions failed")
    if summary["skipped_license"] or summary["skipped_missing_source"]:
        raise SystemExit("Some external images were not localized because license/source metadata was insufficient")

if __name__ == "__main__":
    main()
