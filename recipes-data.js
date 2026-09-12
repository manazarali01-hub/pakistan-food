---
---
window.PAKISTAN_FOOD_RECIPES = [
{% for recipe_pair in site.data.recipes %}
  {{ recipe_pair[1] | jsonify }}{% unless forloop.last %},{% endunless %}
{% endfor %}
];

/* Keep the Drinks controls in sync with the CMS recipe category. */
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

/* Never replace a failed recipe photo with another recipe's photo.
   This prevents misleading duplicate images. */
document.addEventListener("error", (event) => {
  const img = event.target;
  if (!(img instanceof HTMLImageElement) || !img.closest(".recipe-card, .modal")) return;
  if (img.dataset.imageErrorHandled === "1") return;
  img.dataset.imageErrorHandled = "1";
  img.style.display = "none";
}, true);
