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

  const isMobile = window.matchMedia("(max-width: 900px)").matches;

  recipes.forEach((recipe) => {
    if (!recipe || !recipe.image) return;
    let image = String(recipe.image).trim();

    image = image.replace(
      "commons.wikimedia.org/wiki/Special:Redirect/file/",
      "commons.wikimedia.org/wiki/Special:FilePath/"
    );

    if (isMobile && image.includes("commons.wikimedia.org/wiki/Special:FilePath/")) {
      const cleanSource = image.split("?")[0].replace(/^https?:\/\//i, "");
      image = `https://images.weserv.nl/?url=${encodeURIComponent(cleanSource)}&w=900&h=675&fit=cover&output=webp&q=82`;
    }

    recipe.image = image;
  });

  const categories = [
    { name: "Drinks", icon: "🥤", subtitle: "Lassi, Chai & Sharbat" },
    { name: "Vegetarian", icon: "🥬", subtitle: "Saag, Chana & Vegetables" }
  ];

  const dropdown = document.querySelector(".dropdown-menu");
  const categoryGrid = document.querySelector(".category-grid");
  const filterButtons = document.querySelector(".filter-buttons");
  const footerCategories = document.querySelector(".footer-links:nth-of-type(3)");

  categories.forEach(({ name, icon, subtitle }) => {
    if (dropdown && !dropdown.querySelector(`[data-category-link="${name}"]`)) {
      dropdown.insertAdjacentHTML("beforeend", `<a href="#recipes" data-category-link="${name}">${icon} ${name}${name === "Vegetarian" ? " Recipes" : ""}</a>`);
    }

    if (categoryGrid && !categoryGrid.querySelector(`[data-category="${name}"]`)) {
      categoryGrid.insertAdjacentHTML("beforeend", `<button type="button" class="category-box" data-category="${name}"><div>${icon}</div><h3>${name}</h3><p>${subtitle}</p></button>`);
    }

    if (filterButtons && !filterButtons.querySelector(`[data-filter="${name}"]`)) {
      filterButtons.insertAdjacentHTML("beforeend", `<button type="button" class="filter-btn" data-filter="${name}">${name}</button>`);
    }

    if (footerCategories && !footerCategories.querySelector(`[data-category-link="${name}"]`)) {
      footerCategories.insertAdjacentHTML("beforeend", `<a href="#recipes" data-category-link="${name}">${name}${name === "Vegetarian" ? " Recipes" : ""}</a>`);
    }
  });

  const stats = document.querySelectorAll(".hero-stats strong");
  if (stats.length >= 2) {
    stats[0].textContent = `${recipes.length}+`;
    stats[1].textContent = "9";
  }

  const results = document.getElementById("recipeResults");
  if (results) results.textContent = `Showing all ${recipes.length} recipes`;

  const exactFallbacks = {
    "chicken biryani": "assets/chicken-biryani.webp",
    "chicken pulao": "assets/chicken-pulao.webp",
    "chicken karahi": "assets/chicken-karahi.webp",
    "chicken handi": "assets/chicken-handi.webp",
    "beef nihari": "assets/nihari.webp",
    "seekh kabab": "assets/seekh-kebab.webp",
    "chapli kabab": "assets/chapli-kebab.webp",
    "pakistani samosa": "assets/samosa.webp",
    "pakora": "assets/pakora.webp",
    "aloo paratha": "assets/aloo-paratha.webp",
    "halwa puri": "assets/halwa-puri.webp",
    "rice kheer": "assets/kheer.webp",
    "gulab jamun": "assets/gulab-jamun.webp",
    "daal chawal": "assets/daal-chawal.webp",
    "beef pulao": "assets/beef-pulao.webp",
    "sarson ka saag": "https://commons.wikimedia.org/wiki/Special:FilePath/Sarson-Ka-Saag.jpg"
  };

  function neutralPlaceholder(label) {
    const safeLabel = String(label || "Pakistani Recipe").replace(/[<>&"']/g, "").slice(0, 42);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="900" height="675" viewBox="0 0 900 675"><rect width="900" height="675" fill="#f3f3f3"/><text x="450" y="310" text-anchor="middle" font-family="Arial,sans-serif" font-size="42" fill="#333">Pakistan Food</text><text x="450" y="370" text-anchor="middle" font-family="Arial,sans-serif" font-size="25" fill="#666">${safeLabel}</text></svg>`;
    return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
  }

  function finalFallbackFor(img) {
    const label = (img.alt || "").replace(/ Pakistani recipe$/i, "").trim();
    const key = label.toLowerCase();
    return exactFallbacks[key] || neutralPlaceholder(label);
  }

  document.addEventListener("error", (event) => {
    const img = event.target;
    if (!(img instanceof HTMLImageElement)) return;
    if (!img.closest(".recipe-card, .modal")) return;

    const current = img.currentSrc || img.src || "";
    const attempt = Number(img.dataset.fallbackAttempt || "0");

    if (attempt === 0 && /\.webp(?:\?|$)/i.test(current) && current.includes("/assets/")) {
      img.dataset.fallbackAttempt = "1";
      img.src = current.replace(/\.webp(?=\?|$)/i, ".jpg");
      return;
    }

    if (attempt < 3) {
      img.dataset.fallbackAttempt = "3";
      img.src = finalFallbackFor(img);
      img.style.objectFit = "cover";
      return;
    }

    img.src = neutralPlaceholder(img.alt || "Pakistani Recipe");
    img.style.objectFit = "cover";
  }, true);
})();
