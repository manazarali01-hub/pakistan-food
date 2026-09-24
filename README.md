# Pakistan Food

Pakistani recipes published at https://pakistanfoodrecipes.top/ with GitHub Pages and Jekyll.

## Edit a recipe

Recipe content lives in `_data/recipes/<slug>.json`. The `slug` is the permanent URL name; keep the filename when changing a recipe title. The homepage reads this data through `recipes-data.js`, and all category pages read it during the Jekyll build.

The existing Pages CMS configuration is in `.pages.yml`. The optional Decap configuration is in `admin/config.yml`. Both save images to `assets/` and use URLs under `/assets/`. A recipe can be edited through the connected CMS without changing HTML manually.

## Add a recipe

Create one JSON recipe in `_data/recipes/` with a lowercase, hyphenated filename. Include `name`, `category`, `time`, `serves`, `image`, `description`, `ingredients` and `method`. Use a fitting image you have permission to publish, and update `image-credits.html` when an external source requires credit. Do not enter a rating unless it comes from real reviews; the site currently does not display ratings.

The **Sync new CMS recipes** workflow creates `recipes/<slug>.html` and adds its URL to both XML sitemaps. It requests a new GitHub Pages build after saving the generated pages. The existing URLs and modification dates are preserved. If the workflow reports an error, inspect its run in GitHub Actions before treating the new page as published.

For a local check, run `python3 scripts/sync_recipes.py` followed by `python3 scripts/verify_site.py`. Existing recipe pages and the main sitemap URL remain unchanged.
