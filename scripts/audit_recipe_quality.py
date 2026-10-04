"""Evidence report for recipe depth and duplication.

This audit does not decide indexation automatically. It identifies recipe records that
need manual editorial work, while strict source/render validation remains in verify_site.py.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "_data" / "recipes"

PRIORITY = {
    "chicken-biryani", "chicken-karahi", "beef-nihari", "chicken-pulao", "haleem",
    "seekh-kabab", "chapli-kabab", "pakistani-samosa", "aloo-paratha", "halwa-puri",
    "jalebi", "gulab-jamun", "rice-kheer", "kashmiri-chai", "mango-lassi",
}

DEEP_FIELDS = (
    "technique", "doneness_cues", "mistakes", "substitutions", "reheating", "faqs",
    "image_alt", "image_caption", "prep_time_iso", "cook_time_iso", "total_time_iso",
)

GENERIC_PHRASES = (
    "cook until done",
    "cook until ready",
    "add spices and cook",
    "serve hot and enjoy",
    "adjust seasoning to taste",
    "mix well and cook",
)

def words(value) -> int:
    if isinstance(value, list):
        value = " ".join(
            item if isinstance(item, str)
            else " ".join(str(v) for v in item.values())
            for item in value
        )
    elif isinstance(value, dict):
        value = " ".join(str(v) for v in value.values())
    return len(re.findall(r"\b[\w’'-]+\b", str(value or "")))

def normalize_steps(steps) -> str:
    text = " ".join(str(step) for step in (steps or []))
    return re.sub(r"\s+", " ", text).strip().lower()

rows = []
method_groups = defaultdict(list)
description_groups = defaultdict(list)

for file in sorted(RECIPES.glob("*.json")):
    data = json.loads(file.read_text(encoding="utf-8"))
    slug = file.stem
    core_words = sum(words(data.get(field)) for field in (
        "description", "ingredients", "method", "tips", "storage", "serving"
    ))
    deep_count = sum(bool(data.get(field)) for field in DEEP_FIELDS)
    generic_hits = []
    haystack = " ".join(str(data.get(field, "")) for field in ("description", "method", "tips")).lower()
    for phrase in GENERIC_PHRASES:
        if phrase in haystack:
            generic_hits.append(phrase)

    rows.append({
        "slug": slug,
        "name": data.get("name", slug),
        "core_words": core_words,
        "deep_count": deep_count,
        "priority": slug in PRIORITY,
        "generic_hits": generic_hits,
        "has_alt": bool(data.get("image_alt")),
        "has_caption": bool(data.get("image_caption")),
        "image": str(data.get("image", "")),
    })
    method_groups[normalize_steps(data.get("method"))].append(slug)
    description_groups[str(data.get("description", "")).strip().lower()].append(slug)

method_dupes = [items for key, items in method_groups.items() if key and len(items) > 1]
description_dupes = [items for key, items in description_groups.items() if key and len(items) > 1]
thin = sorted((r for r in rows if r["core_words"] < 180), key=lambda r: (r["core_words"], r["slug"]))
needs_depth = sorted((r for r in rows if r["deep_count"] < 4), key=lambda r: (r["deep_count"], r["core_words"], r["slug"]))
missing_image_text = sorted(r["slug"] for r in rows if not (r["has_alt"] and r["has_caption"]))
generic = sorted((r["slug"], r["generic_hits"]) for r in rows if r["generic_hits"])

print("RECIPE QUALITY AUDIT")
print(f"Recipes: {len(rows)}")
print(f"Priority deep-upgrade set: {sum(r['priority'] for r in rows)}")
print(f"Recipes below 180 English core words: {len(thin)}")
print(f"Recipes with fewer than 4 deep editorial fields: {len(needs_depth)}")
print(f"Recipes missing image alt/caption: {len(missing_image_text)}")
print(f"Exact duplicate English method groups: {len(method_dupes)}")
print(f"Exact duplicate descriptions: {len(description_dupes)}")
print(f"Generic phrase hits: {len(generic)}")

if method_dupes:
    print("\nEXACT DUPLICATE METHODS")
    for items in method_dupes:
        print("- " + ", ".join(items))

if description_dupes:
    print("\nEXACT DUPLICATE DESCRIPTIONS")
    for items in description_dupes:
        print("- " + ", ".join(items))

if generic:
    print("\nGENERIC PHRASE HITS")
    for slug, hits in generic:
        print(f"- {slug}: " + " | ".join(hits))

if thin:
    print("\nTHIN RECIPE CORE COPY (<180 words)")
    for row in thin:
        print(f"- {row['slug']}: {row['core_words']} words; deep fields {row['deep_count']}/{len(DEEP_FIELDS)}")

if needs_depth:
    print("\nNEXT EDITORIAL DEPTH CANDIDATES (<4 deep fields)")
    for row in needs_depth:
        print(f"- {row['slug']}: {row['core_words']} words; deep fields {row['deep_count']}/{len(DEEP_FIELDS)}")

if missing_image_text:
    print("\nMISSING IMAGE ALT/CAPTION")
    for slug in missing_image_text:
        print(f"- {slug}")

# Duplication is a hard quality failure. Thinness remains a manual editorial signal:
# a short recipe can still be useful, but two recipes should not share the same method.
if method_dupes or description_dupes:
    raise SystemExit("Recipe duplication audit failed.")

print("\nRecipe audit complete.")
