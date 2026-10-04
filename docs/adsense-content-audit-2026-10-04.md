# Pakistan Food — AdSense Low-Value Content Recovery Audit

**Audit date:** 2026-10-04  
**Current verified state:** repository QA through PR #22 (`c1a11bf7`) plus a successful latest-main custom-domain deployment/smoke verification on commit `3e9bb85f` (Live Site Smoke run 37208801821; Pages deployment run 996).  
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

All 66 recipe URLs remain indexable. Current CI reports **0 recipes below 180 English core words**, **0 recipes with fewer than four deep editorial fields**, **0 exact duplicate English methods/descriptions**, **0 generic-phrase hits**, and **0 recipes missing image alt/caption**.

The first intensive manual deep-upgrade group contained 15 priority recipes:

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

Those priority recipes received the most intensive manual pass. The wider 66-recipe set has also been expanded enough to pass the same automated depth/duplication gates, with recipe-specific technique, doneness/visual cues, mistakes, substitutions, storage/reheating, FAQs, image alt/captions and factual time fields where appropriate.

The recipe layout no longer invents generic category filler when recipe-specific data is absent.

## Image audit

Existing images were not replaced simply for novelty.

Evidence-led decisions included:

- old Chicken Biryani hero rejected because boiled eggs were visible but eggs were not in the recipe;
- old Chicken Karahi hero was harsh/flash-heavy;
- old Nihari image was weak/low-resolution;
- old Seekh/Chapli images were dated/weak;
- the misleading Halwa Puri frying-only hero was replaced after browser QA with a complete real breakfast photograph showing puri, halwa and chickpea curry together; its Flickr creator/source/license are displayed on-page;
- Samosa and Jalebi visuals were strong enough to keep;
- the Samosa recipe was explicitly aligned with the optional pea variation visible in its retained hero;
- premium open-license replacements were introduced only when the dish and recipe matched closely enough;
- Rice Kheer's current high-resolution hero was retained because it clearly represents creamy rice kheer with the nut/saffron-style garnish described by the recipe, rather than replacing an accurate image merely for novelty.

Current image audit: **66 local recipe images, 0 externally served recipe images, 0 missing alt text, and 0 missing captions**. Twelve visually weak or AI-origin recipe images were replaced with real openly licensed photographs from Wikimedia Commons, with source/creator/license metadata retained where applicable. All 66 recipe images were normalized to a mobile-friendly 4:3 food-focused crop, using only the minimum aspect crop plus a gentle extra zoom for near-4:3 sources to avoid over-cropping.

PR #21 added a delivery-quality pass and PR #22 hardened image fallback behavior. A later production image-localization pass then moved all 66 recipe images to local assets. The current premium crop pass replaces 12 weak/AI-origin images with real copyright-safe photographs and normalizes the full 66-image set to 4:3 subject-forward crops. Mobile Browser QA now treats placeholders as failures and also checks homepage recipe-card source images for the required 4:3 aspect ratio.

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
- Search Console traffic/backlink evidence is still unavailable: the connected GSC Wizard now reports that its trial/subscription is inactive. Do not hard-delete or redirect the 78 consolidated noindex URLs without that evidence.
- Process/step images are an optional future enhancement, not treated as factual Recipe-schema data unless real source images exist.
- The 15 priority recipes received the deepest manual editorial review; automated quality gates now pass across all 66 recipes, but this does not substitute for future human taste/testing feedback.
- Real Playwright browser QA is now verified across **42 page/viewport combinations** at 320, 360, 375, 390, 412, 430 and 768 px, with zero horizontal overflow, zero broken images and zero recorded interaction/layout failures in the tested set.
- The latest-main custom-domain gate is now verified. Live Site Smoke run **37208801821** completed successfully for commit `3e9bb85f` after matching Pages deployment run **996**. The live checks passed for `/`, `/recipes/halwa-puri.html`, `ads.txt`, `robots.txt`, `sitemap.xml`, `sitemap-v2.xml`, the **223-URL canonical sitemap set**, and the About, Contact, Privacy, Editorial Policy, Disclaimer, Terms and Image Credits pages.

## Resubmission rule

The technical resubmission gate is now satisfied: repository quality checks, mobile browser QA, deployment validation and latest-main custom-domain smoke verification have passed. A new AdSense review may now be requested. Search Console-dependent destructive URL cleanup remains deferred; it is not a prerequisite while the 78 consolidated URLs remain safely noindexed and excluded from the sitemap. AdSense approval itself cannot be guaranteed and must be confirmed by Google's review.
