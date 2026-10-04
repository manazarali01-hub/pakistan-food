---
---
window.PAKISTAN_FOOD_RECIPES = [
{% for recipe_pair in site.data.recipes %}
  {% assign urdu_name = recipe_pair[1].name_urdu %}
  {% unless urdu_name %}{% assign urdu_name = site.data.urdu_names[recipe_pair[0]] %}{% endunless %}
  {% assign bilingual_category_key = recipe_pair[1].category | downcase %}
  {% assign bilingual_recipe = site.data.bilingual[bilingual_category_key][recipe_pair[0]] %}
  Object.assign({{ recipe_pair[1] | jsonify }}, { slug: {{ recipe_pair[0] | jsonify }}, nameUrdu: {{ urdu_name | jsonify }}, bilingual: {{ bilingual_recipe | jsonify }} }){% unless forloop.last %},{% endunless %}
{% endfor %}
];

(() => {
  const recipes = Array.isArray(window.PAKISTAN_FOOD_RECIPES) ? window.PAKISTAN_FOOD_RECIPES : [];
  const cleanCategory = (value) => {
    const text = String(value || "").trim().toLowerCase();
    const map = {
      rice: "Rice",
      chicken: "Chicken",
      beef: "Beef",
      bbq: "BBQ",
      snacks: "Snacks",
      breakfast: "Breakfast",
      desserts: "Desserts",
      drinks: "Drinks",
      drink: "Drinks",
      vegetarian: "Vegetarian"
    };
    return map[text] || String(value || "Other").trim();
  };


  recipes.forEach((recipe) => {
    if (!recipe) return;

    recipe.category = cleanCategory(recipe.category);

    let image = String(recipe.image || "assets/recipe-image-unavailable.svg").trim();

    image = image
      .replace("commons.wikimedia.org/wiki/Special:Redirect/file/", "commons.wikimedia.org/wiki/Special:FilePath/")
      .replace(/^\/(?!\/)/, "");

    recipe.image = image;
  });

  const categories = [
    { name: "Drinks", slug: "drinks", icon: "🥤", subtitle: "Lassi, Chai & Sharbat" },
    { name: "Vegetarian", slug: "vegetarian", icon: "🥬", subtitle: "Saag, Chana & Vegetables" }
  ];

  const dropdown = document.querySelector(".dropdown-menu");
  const categoryGrid = document.querySelector(".category-grid");
  const filterButtons = document.querySelector(".filter-buttons");
  const footerCategories = document.querySelector(".footer-links:nth-of-type(3)");

  categories.forEach(({ name, slug, icon, subtitle }) => {
    const href = `recipes/${slug}/`;

    if (dropdown && !dropdown.querySelector(`a[href="${href}"]`)) {
      dropdown.insertAdjacentHTML("beforeend", `<a href="${href}">${icon} ${name}${name === "Vegetarian" ? " Recipes" : ""}</a>`);
    }
    if (categoryGrid && !categoryGrid.querySelector(`[data-category="${name}"]`)) {
      categoryGrid.insertAdjacentHTML("beforeend", `<button type="button" class="category-box" data-category="${name}"><div>${icon}</div><h3>${name}</h3><p>${subtitle}</p></button>`);
    }
    if (filterButtons && !filterButtons.querySelector(`[data-filter="${name}"]`)) {
      filterButtons.insertAdjacentHTML("beforeend", `<button type="button" class="filter-btn" data-filter="${name}">${name}</button>`);
    }
    if (footerCategories && !footerCategories.querySelector(`a[href="${href}"]`)) {
      footerCategories.insertAdjacentHTML("beforeend", `<a href="${href}">${name}${name === "Vegetarian" ? " Recipes" : ""}</a>`);
    }
  });

  const stats = document.querySelectorAll(".hero-stats strong");
  if (stats.length >= 2) {
    stats[0].textContent = String(recipes.length);
    stats[1].textContent = String(new Set(recipes.map((r) => r.category).filter(Boolean)).size);
  }

  const results = document.getElementById("recipeResults");
  if (results) results.textContent = `Showing all ${recipes.length} recipes`;

})();
