---
---
window.PAKISTAN_FOOD_RECIPES = [
{% for recipe_pair in site.data.recipes %}
  {{ recipe_pair[1] | jsonify }}{% unless forloop.last %},{% endunless %}
{% endfor %}
];

(() => {
  const recipes = Array.isArray(window.PAKISTAN_FOOD_RECIPES) ? window.PAKISTAN_FOOD_RECIPES : [];
  const isMobile = window.matchMedia("(max-width: 900px)").matches;

  recipes.forEach((recipe) => {
    if (!recipe || !recipe.image) return;
    let image = String(recipe.image).trim();
    image = image.replace("commons.wikimedia.org/wiki/Special:Redirect/file/", "commons.wikimedia.org/wiki/Special:FilePath/");
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
    if (dropdown && !dropdown.querySelector(`[data-category-link="${name}"]`)) dropdown.insertAdjacentHTML("beforeend", `<a href="#recipes" data-category-link="${name}">${icon} ${name}${name === "Vegetarian" ? " Recipes" : ""}</a>`);
    if (categoryGrid && !categoryGrid.querySelector(`[data-category="${name}"]`)) categoryGrid.insertAdjacentHTML("beforeend", `<button type="button" class="category-box" data-category="${name}"><div>${icon}</div><h3>${name}</h3><p>${subtitle}</p></button>`);
    if (filterButtons && !filterButtons.querySelector(`[data-filter="${name}"]`)) filterButtons.insertAdjacentHTML("beforeend", `<button type="button" class="filter-btn" data-filter="${name}">${name}</button>`);
    if (footerCategories && !footerCategories.querySelector(`[data-category-link="${name}"]`)) footerCategories.insertAdjacentHTML("beforeend", `<a href="#recipes" data-category-link="${name}">${name}${name === "Vegetarian" ? " Recipes" : ""}</a>`);
  });

  const stats = document.querySelectorAll(".hero-stats strong");
  if (stats.length >= 2) { stats[0].textContent = `${recipes.length}+`; stats[1].textContent = "9"; }
  const results = document.getElementById("recipeResults");
  if (results) results.textContent = `Showing all ${recipes.length} recipes`;

  const exactFallbacks = {
    "chicken biryani": "assets/chicken-biryani.webp", "chicken pulao": "assets/chicken-pulao.webp",
    "chicken karahi": "assets/chicken-karahi.webp", "chicken handi": "assets/chicken-handi.webp",
    "beef nihari": "assets/nihari.webp", "seekh kabab": "assets/seekh-kebab.webp",
    "chapli kabab": "assets/chapli-kebab.webp", "pakistani samosa": "assets/samosa.webp",
    "pakora": "assets/pakora.webp", "aloo paratha": "assets/aloo-paratha.webp",
    "halwa puri": "assets/halwa-puri.webp", "rice kheer": "assets/kheer.webp",
    "gulab jamun": "assets/gulab-jamun.webp", "daal chawal": "assets/daal-chawal.webp",
    "beef pulao": "assets/beef-pulao.webp",
    "sarson ka saag": "https://commons.wikimedia.org/wiki/Special:FilePath/Sarson-Ka-Saag.jpg",
    "zinger burger": "https://commons.wikimedia.org/wiki/Special:FilePath/Crispy_chicken_burger.jpg?width=900"
  };

  document.addEventListener("error", (event) => {
    const img = event.target;
    if (!(img instanceof HTMLImageElement) || !img.closest(".recipe-card, .modal")) return;
    const current = img.currentSrc || img.src || "";
    const attempt = Number(img.dataset.fallbackAttempt || "0");
    const label = (img.alt || "").replace(/ Pakistani recipe$/i, "").trim().toLowerCase();

    if (attempt === 0 && /\.webp(?:\?|$)/i.test(current) && current.includes("/assets/")) {
      img.dataset.fallbackAttempt = "1";
      img.src = current.replace(/\.webp(?=\?|$)/i, ".jpg");
      return;
    }
    if (attempt < 2 && exactFallbacks[label]) {
      img.dataset.fallbackAttempt = "2";
      img.src = exactFallbacks[label];
      return;
    }
    img.style.display = "none";
  }, true);
})();
