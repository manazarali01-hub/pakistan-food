---
---
window.PAKISTAN_FOOD_RECIPES = [
{% for recipe_pair in site.data.recipes %}
  {{ recipe_pair[1] | jsonify }}{% unless forloop.last %},{% endunless %}
{% endfor %}
];

/* This file loads before script.js, so add the Drinks controls now. */
(() => {
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
    stats[0].textContent = `${window.PAKISTAN_FOOD_RECIPES.length}+`;
    stats[1].textContent = "8";
  }

  const results = document.getElementById("recipeResults");
  if (results) results.textContent = `Showing all ${window.PAKISTAN_FOOD_RECIPES.length} recipes`;
})();

/* If any remote image fails, show a working local image instead of a broken icon. */
document.addEventListener("error", (event) => {
  const img = event.target;
  if (!(img instanceof HTMLImageElement) || !img.closest(".recipe-card, .modal")) return;
  if (img.dataset.fallbackApplied === "1") return;

  img.dataset.fallbackApplied = "1";
  const alt = (img.alt || "").toLowerCase();
  let fallback = "assets/chicken-biryani.webp";

  if (alt.includes("chai") || alt.includes("lassi") || alt.includes("sharbat") || alt.includes("falooda") || alt.includes("milk")) fallback = "assets/kheer.webp";
  else if (alt.includes("chicken")) fallback = "assets/chicken-karahi.webp";
  else if (alt.includes("pulao") || alt.includes("rice")) fallback = "assets/beef-pulao.webp";
  else if (alt.includes("kabab") || alt.includes("burger") || alt.includes("shawarma")) fallback = "assets/chapli-kebab.webp";
  else if (alt.includes("jalebi") || alt.includes("halwa") || alt.includes("ras malai")) fallback = "assets/gulab-jamun.webp";
  else if (alt.includes("paratha")) fallback = "assets/aloo-paratha.webp";
  else if (alt.includes("gosht") || alt.includes("keema") || alt.includes("mutton") || alt.includes("beef")) fallback = "assets/nihari.webp";

  img.src = fallback;
}, true);
