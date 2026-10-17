"""Generate mobile-sized WebP variants for locally hosted recipe images.

Original files and URLs remain untouched. The generated -640.webp files are
used only for card/mobile requests; full-resolution originals remain available.
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "_data" / "recipes"
MAX_WIDTH = 640
QUALITY = 84


def image_paths() -> list[Path]:
    paths: set[Path] = set()
    for source in sorted(RECIPES.glob("*.json")):
        data = json.loads(source.read_text(encoding="utf-8"))
        value = str(data.get("image", "")).strip()
        if not value or value.startswith(("http://", "https://")):
            continue
        path = (ROOT / value.lstrip("/")).resolve()
        if ROOT.resolve() not in path.parents:
            raise SystemExit(f"Unsafe image path in {source.name}: {value}")
        if path.suffix.lower() != ".webp":
            continue
        if not path.is_file():
            raise SystemExit(f"Recipe image is missing: {source.name} -> {value}")
        paths.add(path)
    return sorted(paths)


def create_variant(source: Path) -> tuple[Path, int, int]:
    target = source.with_name(f"{source.stem}-640.webp")
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        original_width, original_height = image.size
        if original_width > MAX_WIDTH:
            height = max(1, round(original_height * MAX_WIDTH / original_width))
            image = image.resize((MAX_WIDTH, height), Image.Resampling.LANCZOS)
        if "A" in image.getbands():
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
        image.save(
            target,
            "WEBP",
            quality=QUALITY,
            method=6,
            icc_profile=opened.info.get("icc_profile"),
        )
    return target, source.stat().st_size, target.stat().st_size


def main() -> None:
    sources = image_paths()
    if not sources:
        raise SystemExit("No local WebP recipe images found.")
    original_total = 0
    variant_total = 0
    created = 0
    for source in sources:
        target, original_size, variant_size = create_variant(source)
        original_total += original_size
        variant_total += variant_size
        created += 1
        print(
            f"{source.relative_to(ROOT)} -> {target.relative_to(ROOT)}: "
            f"{original_size:,} -> {variant_size:,} bytes"
        )
    saving = (1 - variant_total / original_total) * 100 if original_total else 0
    print(
        f"Generated {created} mobile WebP variants. "
        f"Variant total: {variant_total:,} bytes vs originals: {original_total:,} bytes "
        f"({saving:.1f}% smaller across the variant set)."
    )
    if any(not source.with_name(f"{source.stem}-640.webp").is_file() for source in sources):
        raise SystemExit("One or more mobile variants were not created.")


if __name__ == "__main__":
    main()
