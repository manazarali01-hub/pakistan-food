# Pakistan Food

Pakistani recipes published at https://pakistanfoodrecipes.top/ with GitHub Pages and Jekyll.

## Edit a recipe

Recipe content lives in `_data/recipes/<slug>.json`. The `slug` is the permanent URL name; keep the filename when changing a recipe title. The homepage reads this data through `recipes-data.js`, and all category pages read it during the Jekyll build.

The existing Pages CMS configuration is in `.pages.yml`. The optional Decap configuration is in `admin/config.yml`. Both save images to `assets/` and use URLs under `/assets/`. A recipe can be edited through the connected CMS without changing HTML manually.

## Add a recipe

Create one JSON recipe in `_data/recipes/` with a lowercase, hyphenated filename. Include `name`, `category`, `time`, `serves`, `image`, `description`, `ingredients` and `method`. Use a fitting image you have permission to publish, and update `image-credits.html` when an external source requires credit. Do not enter a rating unless it comes from real reviews; the site currently does not display ratings.

The **Sync new CMS recipes** workflow creates `recipes/<slug>.html` and adds its URL to both XML sitemaps. It requests a new GitHub Pages build after saving the generated pages. The existing URLs and modification dates are preserved. If the workflow reports an error, inspect its run in GitHub Actions before treating the new page as published.

For a local check, run `python3 scripts/sync_recipes.py` followed by `python3 scripts/verify_site.py`. Existing recipe pages and the main sitemap URL remain unchanged.


## Urdu recipe names

Existing recipes use `_data/urdu_names.json` for a compact Urdu display name on recipe cards, category pages and individual recipe pages. New CMS recipes can optionally set `name_urdu` directly; that value takes priority over the shared map.

## Trust and policy pages

The public trust pages are `privacy-policy.html`, `editorial-policy.html`, `disclaimer.html`, `terms.html` and `image-credits.html`. Keep their sitemap and footer links intact when redesigning the site.

## Deployment and ownership handover

The site is designed for GitHub Pages + Jekyll. The custom domain is stored in `CNAME` and `_config.yml`. After an ownership transfer, update the domain/DNS only when the buyer is ready to take control so the live site is not interrupted.

Before handover, replace the public contact email and phone number in `index.html` with the new owner's details. The AdSense publisher value in `_config.yml` belongs to the current publisher and must be replaced with the buyer's own approved AdSense publisher ID; do not transfer an AdSense account as part of the website files. Check the generated `/ads.txt` after changing the publisher value.

Transfer or grant access to the GitHub repository separately from the domain registrar account. After the transfer, confirm GitHub Pages deployment, HTTPS/custom-domain status, `/robots.txt`, `/sitemap.xml`, `/ads.txt`, the homepage, category pages and several recipe pages before changing or removing the seller's access.

## Pre-sale verification

Run `python3 scripts/sync_recipes.py` and then `python3 scripts/verify_site.py`. Confirm the custom domain resolves over HTTPS, recipe pages load without broken assets, policy/footer links work, and the canonical sitemap remains `https://pakistanfoodrecipes.top/sitemap.xml`. Search Console and AdSense accounts should be handled as separate services and should not be represented as automatically transferring with the repository.
