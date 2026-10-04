# Pakistan Food — AdSense Low-Value Content Recovery Audit

**Audit date:** 2026-10-04  
**Working branch:** `adsense-quality-recovery-2026-10-04`  
**Main site:** https://pakistanfoodrecipes.top/  
**Reason for recovery work:** Google AdSense — Low value content

## Decision rule

An indexable page should be specific, useful, original enough to justify its own URL, easy to navigate, and useful to a real Pakistani home cook. Page count is not treated as a quality signal.

No fake reviews, ratings, nutrition, video, qualifications or engagement signals are added.

## Repository evidence

| Content group | Count | Current treatment |
| --- | ---: | --- |
| Recipe data/pages | 66 | Kept indexable; top-priority set deeply upgraded first |
| Guide pages (excluding guide index) | 215 | Audited for visible length, duplicate body and template prose |
| Guides kept indexable | 137 | Must pass strict duplicate/template-content gate |
| Guides consolidated + `noindex,follow` | 78 | Retained for existing links; removed from XML sitemap; point to fuller resources |
| Guides removed/deleted | 0 | Destructive removal deferred without Search Console traffic evidence |
| Current XML sitemap URLs | 223 | Canonical, indexable URLs only |
| Recipe URLs in sitemap | 66 | All permanent recipe pages |
| Guide article URLs in sitemap | 137 | Excludes the 78 noindexed guide URLs |
| Guide directory URL | 1 | Curated guide hub |
| Recipe category URLs | 9 | Non-empty category hubs |

## Before cleanup

The first automated content audit found:

- 215 / 215 guide articles indexable.
- 78 indexed guides below 220 visible words.
- 58 indexed guides containing known generic mass-template phrases.
- 5 exact duplicate visible-body groups.
- The largest duplicate families covered pulses/daal/chana/rajma, desserts, drinks/lassi and tikka.
- The XML sitemap was heavily guide-dominated.

Representative repeated prose included generic instructions about controlling heat/moisture, adjusting one variable, distributing ingredients evenly, and using the same corrective language across unrelated dishes.

## Current automated audit result

The strict branch audit now reports:

- **Indexed guides under 220 visible words: 0**
- **Indexed guides with known generic-template phrase hits: 0**
- **Exact duplicate indexed guide-body groups: 0**
- **Noindex guide URLs in XML sitemap: 0**

The CI build fails if exact duplicate indexed guide bodies, known mass-template phrases, or noindex/sitemap conflicts are reintroduced.

## Guide classification

### KEEP + IMPROVE

Kept when the topic has distinct cooking intent and can teach something specific. High-value rewrites include, among others:

- How to Use Cardamom in Chai
- How to Balance Kashmiri Chai
- Why Kheer Is Grainy
- Why Jalebi Is Not Crispy
- How to Balance Daal Tadka
- How to Cook Onions for Pakistani Qorma
- How to Rescue a Scorched Curry
- Why Chai Is Too Strong
- Why Curry Tastes Flat
- Why Chicken Karahi Tastes Too Tomatoey
- Why Oil Separates From Curry
- Why Qorma Tastes Too Sweet
- How to Layer Biryani Evenly
- How to Make Strong Chai Without Bitterness
- How to Make Yakhni for Pakistani Pulao
- How to Reduce Curry Without Burning the Masala
- How to Use Fried Onions in Biryani
- How to Use Saffron in Biryani
- Why the Bottom of Biryani Burns
- Why Biryani Colour Is Uneven
- Why Chai Gets a Skin on Top
- Why Curry Is Watery
- Why Curry Tastes Raw
- Why Naan Gets Hard
- Why Paratha Does Not Form Layers
- Why Pulao Lacks Aroma
- Why Pulao Turns Dry
- Why Rice Smells Stale
- Why Rice Tastes Too Salty

### MERGE / CONSOLIDATE

78 guide URLs were found to be exact duplicates, near-template micro-pages, or strongly overlapping support topics. They were consolidated into stronger recipe/guide resources.

Examples include:

- multiple daal/chana/rajma seasoning, soaking, reheating and tadka micro-pages;
- repetitive lassi/chai/sharbat balance pages;
- repetitive kheer/halwa/gulab-jamun support pages;
- overlapping tikka preparation micro-pages;
- overlapping watery/reduction karahi pages;
- very small roti/paratha/rice support pages already covered by stronger guides.

### NOINDEX

The 78 consolidated URLs now use `noindex,follow`. They retain a self-canonical and a visible handoff to a stronger page so old links do not dead-end. They are excluded from `sitemap-v2.xml`.

This is intentionally reversible.

### REMOVE / REDIRECT

**0 URLs currently deleted or hard-redirected.**

Search Console performance data could not be retrieved because the connected GSC service was unavailable. Destructive URL removal is therefore deferred rather than guessing about historical impressions, clicks or backlinks.

## Recipe quality work

All 66 recipe URLs remain indexable. The first deep-upgrade group contains 15 priority recipes:

1. Chicken Biryani
2. Chicken Karahi
3. Beef Nihari
4. Chicken Pulao
5. Haleem
6. Seekh Kabab
7. Chapli Kabab
8. Pakistani Samosa
9. Aloo Paratha
10. Halwa Puri
11. Jalebi
12. Gulab Jamun
13. Rice Kheer
14. Kashmiri Chai
15. Mango Lassi

Where useful, these data records now include recipe-specific technique, doneness/visual cues, mistakes, substitutions, storage/reheating, FAQs, better image alt/captions, and factual prep/cook/total time fields.

The recipe layout no longer invents generic category filler when recipe-specific data is absent.

## Image audit

Existing images were not replaced simply for novelty.

Evidence-led decisions included:

- old Chicken Biryani hero rejected because boiled eggs were visible but eggs were not in the recipe;
- old Chicken Karahi hero was harsh/flash-heavy;
- old Nihari image was weak/low-resolution;
- old Seekh/Chapli images were dated/weak;
- Halwa Puri existing hero is still a known weakness because it shows a frying scene rather than a complete plated breakfast;
- Samosa and Jalebi visuals were strong enough to keep;
- the Samosa recipe was explicitly aligned with the optional pea variation visible in its retained hero;
- premium licensed Commons replacements were introduced only when the dish and recipe matched closely enough.

## Structured-data rules

Recipe schema is generated from factual recipe data only.

Conditional nutrition, rating and video fields are permitted by the template only when real source fields exist. Current validation fails if those objects are rendered without corresponding source data.

The rendered build also validates:

- one Recipe object per recipe page;
- required recipe schema fields;
- at least five detailed instruction steps;
- factual total-time parsing, including combined hour/minute values;
- `dateModified` only when an editorial date exists in the recipe source;
- canonical URLs and internal links.

## AdSense / crawl safety

Branch validation checks:

- rendered `ads.txt` exactly matches the configured publisher;
- no more than one AdSense loader appears on a sitemap page;
- no explicit ad unit is inserted before readiness review;
- no noindex URL is present in the XML sitemap;
- all sitemap URLs have source/rendered pages;
- trust pages are present and indexable;
- canonical URLs remain on the main domain.

## Remaining weaknesses / not yet verified

- No destructive URL deletion decision should be made until Search Console traffic/backlink evidence is available.
- Halwa Puri and Rice Kheer remain image-upgrade candidates; a replacement should not be accepted unless it matches the actual recipe closely.
- Useful process images for priority recipes are not yet complete.
- The 51 non-priority recipes have not all received the same depth of manual editorial expansion as the first 15.
- Source-level responsive QA and CI are available, but full visual browser screenshots at every requested width (320, 360, 375, 390, 412, 430 and 768 px) still need final verification.
- Live-domain `ads.txt` could not be independently fetched from the current tool environment; branch-rendered `ads.txt` is validated in CI.

## Resubmission rule

Do not request a new AdSense review merely because this branch builds successfully. Merge, deploy, verify the live site, recheck navigation/mobile/important URLs/ads.txt, and complete the remaining final-readiness audit first.
