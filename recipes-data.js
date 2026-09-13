---
---
window.PAKISTAN_FOOD_RECIPES = [
{% for recipe_pair in site.data.recipes %}
  {{ recipe_pair[1] | jsonify }}{% unless forloop.last %},{% endunless %}
{% endfor %}
];

(() => {
  const recipes = Array.isArray(window.PAKISTAN_FOOD_RECIPES)
    ? window.PAKISTAN_FOOD_RECIPES
    : [];

  recipes.forEach((recipe) => {
    if (!recipe || !recipe.image) return;
    let image = String(recipe.image).trim();

    image = image.replace(
      "commons.wikimedia.org/wiki/Special:Redirect/file/",
      "commons.wikimedia.org/wiki/Special:FilePath/"
    );

    /* Prefer the original JPG photography for local assets. */
    if (/^assets\/.*\.webp(?:\?|$)/i.test(image)) {
      image = image.replace(/\.webp(?=\?|$)/i, ".jpg");
    }

    recipe.image = image;
  });

  const dropdown = document.querySelector(".dropdown-menu");
  if (dropdown && !dropdown.querySelector('[data-category-link="Drinks"]')) {
    dropdown.insertAdjacentHTML("beforeend", '<a href="#recipes" data-category-link="Drinks">🥤 Drinks</a>');
  }

  const categoryGrid = document.querySelector(".category-grid");
  if (categoryGrid && !categoryGrid.querySelector('[data-category="Drinks"]')) {
    categoryGrid.insertAdjacentHTML("beforeend", '<button type="button" class="category-box" data-category="Drinks"><div>🥤</div><h3>Drinks</h3><p>Lassi, Chai & Sharbat</p></button>');
  }

  const filterButtons = document.querySelector(".filter-buttons");
  if (filterButtons && !filterButtons.querySelector('[data-filter="Drinks"]')) {
    filterButtons.insertAdjacentHTML("beforeend", '<button type="button" class="filter-btn" data-filter="Drinks">Drinks</button>');
  }

  const footerCategories = document.querySelector(".footer-links:nth-of-type(3)");
  if (footerCategories && !footerCategories.querySelector('[data-category-link="Drinks"]')) {
    footerCategories.insertAdjacentHTML("beforeend", '<a href="#recipes" data-category-link="Drinks">Drinks</a>');
  }

  const stats = document.querySelectorAll(".hero-stats strong");
  if (stats.length >= 2) {
    stats[0].textContent = `${recipes.length}+`;
    stats[1].textContent = "8";
  }

  const results = document.getElementById("recipeResults");
  if (results) results.textContent = `Showing all ${recipes.length} recipes`;

  function finalFallbackFor(img) {
    const alt = (img.alt || "").toLowerCase();

    if (alt.includes("paratha")) return "assets/aloo-paratha.jpg";
    if (alt.includes("biryani")) return "assets/chicken-biryani.jpg";
    if (alt.includes("pulao") || alt.includes("rice")) return "assets/beef-pulao.jpg";
    if (alt.includes("karahi") || alt.includes("chicken") || alt.includes("jalfrezi") || alt.includes("qorma") || alt.includes("handi")) return "assets/chicken-karahi.jpg";
    if (alt.includes("kabab") || alt.includes("kebab") || alt.includes("burger") || alt.includes("shawarma")) return "assets/chapli-kebab.jpg";
    if (alt.includes("samosa") || alt.includes("pakora") || alt.includes("chaat") || alt.includes("pizza")) return "assets/samosa.jpg";
    if (alt.includes("nihari") || alt.includes("beef") || alt.includes("mutton") || alt.includes("gosht") || alt.includes("keema")) return "assets/nihari.jpg";
    if (alt.includes("kheer") || alt.includes("halwa") || alt.includes("jalebi") || alt.includes("gulab") || alt.includes("ras malai")) return "assets/gulab-jamun.jpg";
    if (alt.includes("chai") || alt.includes("lassi") || alt.includes("sharbat") || alt.includes("falooda") || alt.includes("milk")) return "assets/kheer.jpg";

    return "assets/chicken-biryani.jpg";
  }

  document.addEventListener("error", (event) => {
    const img = event.target;
    if (!(img instanceof HTMLImageElement)) return;
    if (!img.closest(".recipe-card, .modal")) return;

    const current = img.currentSrc || img.src || "";
    const attempt = Number(img.dataset.fallbackAttempt || "0");

    /* Local JPG failed: try its WebP copy. */
    if (attempt === 0 && /\.jpg(?:\?|$)/i.test(current) && current.includes("/assets/")) {
      img.dataset.fallbackAttempt = "1";
      img.src = current.replace(/\.jpg(?=\?|$)/i, ".webp");
      return;
    }

    /* Wikimedia thumbnail/redirect failed: retry the same file without query params. */
    if (attempt <= 1 && current.includes("commons.wikimedia.org/wiki/Special:FilePath/") && current.includes("?")) {
      img.dataset.fallbackAttempt = "2";
      img.src = current.split("?")[0];
      return;
    }

    /* Never leave an empty image card. If the real linked image is unavailable,
       show the closest existing high-quality local food photo instead. */
    if (attempt < 3) {
      img.dataset.fallbackAttempt = "3";
      img.src = finalFallbackFor(img);
      img.style.objectFit = "cover";
      return;
    }

    img.style.objectFit = "cover";
    img.style.background = "var(--surface-2)";
  }, true);
})();
