---
---
window.PAKISTAN_FOOD_RECIPES = [
{% for recipe_pair in site.data.recipes %}
  Object.assign({{ recipe_pair[1] | jsonify }}, { slug: {{ recipe_pair[0] | jsonify }} }){% unless forloop.last %},{% endunless %}
{% endfor %}
];

(() => {
  const recipes = Array.isArray(window.PAKISTAN_FOOD_RECIPES) ? window.PAKISTAN_FOOD_RECIPES : [];
  const isMobile = window.matchMedia("(max-width: 900px)").matches;

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

  const localFallbacks = {
    "chicken biryani": "assets/chicken-biryani.webp",
    "chicken pulao": "assets/chicken-pulao.webp",
    "chicken karahi": "assets/chicken-karahi.webp",
    "chicken handi": "assets/chicken-handi.webp",
    "beef nihari": "assets/nihari.webp",
    "seekh kabab": "assets/seekh-kebab.webp",
    "chapli kabab": "assets/chapli-kebab.webp",
    "pakistani samosa": "assets/pakistani-samosa-v2.webp",
    "pakora": "assets/pakora.webp",
    "aloo paratha": "assets/aloo-paratha.webp",
    "halwa puri": "assets/halwa-puri.webp",
    "rice kheer": "assets/kheer.webp",
    "gulab jamun": "assets/gulab-jamun.webp",
    "daal chawal": "assets/daal-chawal.webp",
    "beef pulao": "assets/beef-pulao.webp",
    "aloo gosht": "assets/aloo-gosht.webp",
    "bun kabab": "assets/bun-kabab.webp",
    "chana masala": "assets/chana-masala.webp",
    "chicken jalfrezi": "assets/chicken-jalfrezi-v2.webp",
    "chicken sajji": "assets/chicken-sajji.webp",
    "keema matar": "assets/keema-matar.webp",
    "mango lassi": "assets/mango-lassi.webp",
    "matar pulao": "assets/matar-pulao.webp",
    "shami kabab": "assets/shami-kabab.webp"
  };

  const jpgFallbacks = {
    "chicken biryani": "assets/chicken-biryani.jpg",
    "chicken pulao": "assets/chicken-pulao.jpg",
    "chicken karahi": "assets/chicken-karahi.jpg",
    "chicken handi": "assets/chicken-handi.jpg",
    "beef nihari": "assets/nihari.jpg",
    "seekh kabab": "assets/seekh-kebab.jpg",
    "chapli kabab": "assets/chapli-kebab.jpg",
    "pakistani samosa": "assets/samosa.jpg",
    "pakora": "assets/pakora.jpg",
    "aloo paratha": "assets/aloo-paratha.jpg",
    "halwa puri": "assets/halwa-puri.jpg",
    "rice kheer": "assets/kheer.jpg",
    "gulab jamun": "assets/gulab-jamun.jpg",
    "daal chawal": "assets/daal-chawal.jpg",
    "beef pulao": "assets/beef-pulao.jpg"
  };

  recipes.forEach((recipe) => {
    if (!recipe) return;

    recipe.category = cleanCategory(recipe.category);

    const key = String(recipe.name || "").trim().toLowerCase();
    let image = String(recipe.image || localFallbacks[key] || "assets/pakistan-food-logo.png").trim();

    image = image
      .replace("commons.wikimedia.org/wiki/Special:Redirect/file/", "commons.wikimedia.org/wiki/Special:FilePath/")
      .replace(/^\/(?!\/)/, "");

    if (isMobile && image.includes("commons.wikimedia.org/wiki/Special:FilePath/")) {
      const sourceWithoutQuery = image.split("?")[0].replace(/^https?:\/\//i, "");
      image = `https://images.weserv.nl/?url=${encodeURIComponent(sourceWithoutQuery)}&w=720&h=540&fit=cover&output=webp&q=78`;
    }

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

  document.addEventListener("error", (event) => {
    const img = event.target;
    if (!(img instanceof HTMLImageElement) || !img.closest(".recipe-card, .modal")) return;

    const current = img.currentSrc || img.src || "";
    const attempt = Number(img.dataset.fallbackAttempt || "0");
    const label = (img.alt || "")
      .replace(/ (?:ready to serve|Pakistani recipe)$/i, "")
      .trim()
      .toLowerCase();

    if (attempt === 0 && jpgFallbacks[label] && !current.includes(jpgFallbacks[label])) {
      img.dataset.fallbackAttempt = "1";
      img.src = jpgFallbacks[label];
      return;
    }

    if (attempt < 2 && localFallbacks[label] && !current.includes(localFallbacks[label])) {
      img.dataset.fallbackAttempt = "2";
      img.src = localFallbacks[label];
      return;
    }

    if (attempt < 3) {
      img.dataset.fallbackAttempt = "3";
      img.src = "assets/pakistan-food-logo.png";
      img.alt = `${label || "Pakistan Food"} image unavailable`;
      img.style.objectFit = "contain";
      img.style.padding = "24px";
      img.style.background = "#fff8ef";
      return;
    }

    img.style.display = "none";
  }, true);
})();
