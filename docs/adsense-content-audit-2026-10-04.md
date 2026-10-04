# Pakistan Food — AdSense Low-Value Content Recovery Audit

**Audit date:** 2026-10-04  
**Current verified state:** repository QA through PR #22 (`c1a11bf7`); custom-domain live smoke was previously verified on main after PR #20 (`c4496aaf`). The latest PR #22 production push still requires its own successful post-deploy smoke result before AdSense resubmission.  
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

Current image audit: **52 external recipe images, 14 local recipe images, 0 external records missing source metadata, 0 partial attribution records, 0 missing alt text, and 0 missing captions**.

PR #21 added a second delivery-quality pass across 45 recipe image mappings: Wikimedia `Special:Redirect/file` URLs were normalized to `Special:FilePath`, 800/900/960px requests were raised to 1280px where supported, and Sarson ka Saag now explicitly requests a 1280px source. PR #21 passed Pages Refresh and Mobile Browser QA before merge. PR #22 then hardened static homepage image fallback handling so a failed `srcset` candidate is removed before switching to the local fallback; PR #22 also passed Pages Refresh, Mobile Browser QA and the Netlify deploy preview before merge.

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
- The current tool environment still cannot independently resolve the custom domain. The GitHub-hosted post-deploy live smoke gate introduced in PR #18 was subsequently exercised successfully on main after PR #20 (`c4496aaf`). Because PR #21 and PR #22 changed image delivery/fallback behavior after that point, the latest main commit still needs its own successful post-deploy live smoke result before the AdSense review is requested.

## Resubmission rule

Do not request a new AdSense review merely because repository CI is green. First require a successful post-deploy live smoke run on the **latest main commit** on the custom domain. Search Console-dependent destructive URL cleanup remains deferred; it is not a prerequisite to keep the 78 consolidated URLs safely noindexed. Even after all technical gates pass, AdSense approval itself cannot be guaranteed and must be confirmed by Google's review.
