/* =====================================
   PAKISTAN FOOD
   MAIN JAVASCRIPT
===================================== */


/* =====================================
   RECIPE DATA
===================================== */

// Recipe data is generated from _data/recipes into recipes-data.js during the Jekyll build.
// Do not keep a second hard-coded recipe catalogue here: stale fallback content hides data/build errors.

const cmsRecipes = Array.isArray(window.PAKISTAN_FOOD_RECIPES)
    ? window.PAKISTAN_FOOD_RECIPES
    : [];

function stableRecipeId(recipe, index) {
    if (Number.isFinite(Number(recipe.id))) return Number(recipe.id);

    const text = String(recipe.name || `recipe-${index}`);
    let hash = 0;

    for (const character of text) {
        hash = ((hash << 5) - hash + character.charCodeAt(0)) | 0;
    }

    return Math.abs(hash) + 1000;
}

function stableRecipeSlug(recipe, index) {
    const slug = String(recipe.slug || recipe.name || `recipe-${index}`)
        .normalize("NFKD")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");

    return slug || `recipe-${stableRecipeId(recipe, index)}`;
}

function recipePagePath(recipe) {
    return `recipes/${encodeURIComponent(recipe.slug)}.html`;
}

const recipes = cmsRecipes.map((recipe, index) => {
    const bilingual = recipe && typeof recipe.bilingual === "object" && recipe.bilingual ? recipe.bilingual : {};
    return {
        ...recipe,
        id: stableRecipeId(recipe, index),
        slug: stableRecipeSlug(recipe, index),
        serves: Number(recipe.serves) || 4,
        image: safeImageUrl(recipe.image),
        bilingual,
        ingredients: Array.isArray(recipe.ingredients) ? recipe.ingredients : [],
        method: Array.isArray(bilingual.method_en) && bilingual.method_en.length
            ? bilingual.method_en
            : (Array.isArray(recipe.method) ? recipe.method : []),
        ingredientsUrdu: Array.isArray(bilingual.ingredients_ur) ? bilingual.ingredients_ur : [],
        methodUrdu: Array.isArray(bilingual.method_ur) ? bilingual.method_ur : [],
        tipsUrdu: Array.isArray(bilingual.tips_ur) ? bilingual.tips_ur : [],
        descriptionUrdu: String(bilingual.description_ur || ""),
        storageUrdu: String(bilingual.storage_ur || ""),
        servingUrdu: String(bilingual.serving_ur || "")
    };
});

/* =====================================
   ELEMENTS
===================================== */

const recipeGrid = document.getElementById("recipeGrid");
const searchInput = document.getElementById("searchInput");
const noResults = document.getElementById("noResults");
const recipeResults = document.getElementById("recipeResults");
const favoritesFilter = document.getElementById("favoritesFilter");
const favoriteCount = document.getElementById("favoriteCount");
const clearResults = document.getElementById("clearResults");

const recipeModal = document.getElementById("recipeModal");
const modalContent = document.getElementById("modalContent");
const modalClose = document.getElementById("modalClose");
const modalOverlay = document.getElementById("modalOverlay");

const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toastMessage");

const themeBtn = document.getElementById("themeBtn");

const menuBtn = document.getElementById("menuBtn");
const closeMenu = document.getElementById("closeMenu");
const mobileMenu = document.getElementById("mobileMenu");

const backTop = document.getElementById("backTop");

let currentCategory = "All";
let showFavoritesOnly = false;
let lastFocusedElement = null;
let lastFocusedRecipeId = null;


/* =====================================
   FAVORITES
===================================== */

function readPreference(key, fallback = null) {
    try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; }
}
function savePreference(key, value) {
    try { localStorage.setItem(key, value); } catch { /* Browsing still works without storage. */ }
}

const RECENT_RECIPES_KEY = "pakistanFoodRecentlyViewed";

function recentRecipeIds() {
    try {
        const value = JSON.parse(readPreference(RECENT_RECIPES_KEY, "[]"));
        return Array.isArray(value) ? value.map(Number).filter(Number.isFinite) : [];
    } catch {
        return [];
    }
}

function rememberRecentlyViewed(id) {
    const next = [Number(id), ...recentRecipeIds().filter(item => item !== Number(id))].slice(0, 4);
    savePreference(RECENT_RECIPES_KEY, JSON.stringify(next));
    renderRecentlyViewed();
}

function renderRecentlyViewed() {
    const section = document.getElementById("recentlyViewed");
    const grid = document.getElementById("recentGrid");
    if (!section || !grid) return;
    const items = recentRecipeIds().map(id => recipes.find(recipe => recipe.id === id)).filter(Boolean);
    section.hidden = items.length === 0;
    grid.innerHTML = items.map(recipe => `
        <a class="recent-card" href="${recipePagePath(recipe)}">
            <img src="${escapeHtml(sizedRecipeImage(recipe, 480))}" alt="${escapeHtml(recipeImageAlt(recipe))}" width="480" height="360" loading="lazy" decoding="async">
            <span class="recent-card-copy">
                <strong>${escapeHtml(recipe.name)}</strong>
                ${recipe.nameUrdu ? `<span class="recipe-name-urdu" lang="ur" dir="rtl">${escapeHtml(recipe.nameUrdu)}</span>` : ""}
                <small>${escapeHtml(recipe.category)} · ${escapeHtml(recipe.time)}</small>
            </span>
        </a>
    `).join("");
}
let favorites = [];
try {
    const saved = JSON.parse(readPreference("pakistanFoodFavorites", "[]"));
    if (Array.isArray(saved)) favorites = saved.map(Number).filter(Number.isFinite);
} catch { /* Ignore malformed saved favourites. */ }

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
}
function safeImageUrl(value) {
    const url = String(value || "").trim().replace(/^\//, "");
    return /^(assets\/[a-zA-Z0-9._/?=&%-]+|https:\/\/(?:commons\.wikimedia\.org|images\.weserv\.nl)\/[^"<>]*)$/.test(url)
        ? url : "assets/recipe-image-unavailable.svg";
}
function recipeImageAlt(recipe) {
    return String(recipe?.image_alt || recipe?.name || "Pakistani recipe").trim();
}
function sizedRecipeImage(recipe, width) {
    let url = safeImageUrl(recipe?.image);
    if (/^https:\/\/commons\.wikimedia\.org\//.test(url)) {
        if (/([?&]width=)\d+/.test(url)) return url.replace(/([?&]width=)\d+/, `$1${width}`);
        return `${url}${url.includes("?") ? "&" : "?"}width=${width}`;
    }
    if (/^https:\/\/images\.weserv\.nl\//.test(url) && /([?&]w=)\d+/.test(url)) {
        return url.replace(/([?&]w=)\d+/, `$1${width}`);
    }
    return url;
}
function useImageFallback(image) {
    if (image.tagName !== "IMG" || image.src.endsWith("/recipe-image-unavailable.svg")) return;
    image.src = "assets/recipe-image-unavailable.svg";
    image.alt = "Recipe image unavailable";
}
recipeGrid?.addEventListener("error", event => useImageFallback(event.target), true);
modalContent?.addEventListener("error", event => useImageFallback(event.target), true);
document.getElementById("recentGrid")?.addEventListener("error", event => useImageFallback(event.target), true);


/* =====================================
   RENDER RECIPES
===================================== */

function renderRecipes() {

    const searchTerm = searchInput.value.toLowerCase().trim();

    const filtered = recipes.filter(recipe => {

        const categoryMatch =
            currentCategory === "All" ||
            recipe.category === currentCategory;

        const searchableText = [
            recipe.name,
            recipe.nameUrdu,
            recipe.category,
            recipe.description,
            recipe.descriptionUrdu,
            ...recipe.ingredients,
            ...recipe.ingredientsUrdu,
            ...recipe.method,
            ...recipe.methodUrdu
        ].join(" ").toLowerCase();

        const searchMatch = searchableText.includes(searchTerm);

        const favoriteMatch =
            !showFavoritesOnly || favorites.includes(recipe.id);

        return categoryMatch && searchMatch && favoriteMatch;

    });


    recipeGrid.innerHTML = "";

    favoriteCount.textContent = favorites.length;

    const scope = showFavoritesOnly
        ? "saved recipes"
        : currentCategory === "All"
            ? "recipes"
            : `${currentCategory.toLowerCase()} recipes`;

    const resultLabel = filtered.length === 1
        ? scope.replace(/recipes$/, "recipe")
        : scope;

    recipeResults.textContent = `Showing ${filtered.length} ${resultLabel}`;


    if (filtered.length === 0) {

        noResults.style.display = "block";

        return;

    }

    noResults.style.display = "none";


    filtered.forEach((recipe, index) => {

        const isFavorite = favorites.includes(recipe.id);

        const card = document.createElement("article");

        card.className = "recipe-card";

        card.innerHTML = `

            <div class="recipe-image">

                <img
                    src="${escapeHtml(sizedRecipeImage(recipe, 640))}"
                    alt="${escapeHtml(recipeImageAlt(recipe))}"
                    loading="lazy"
                    decoding="async"
                    width="900"
                    height="675"
                >

                <span class="recipe-badge">
                    ${escapeHtml(recipe.category)}
                </span>

                <button
                    type="button"
                    class="favorite-btn ${isFavorite ? "active" : ""}"
                    data-favorite="${recipe.id}"
                    aria-label="${isFavorite ? "Remove" : "Save"} ${escapeHtml(recipe.name)} ${isFavorite ? "from" : "to"} favorites"
                    aria-pressed="${isFavorite}"
                >
                    ${isFavorite ? "♥" : "♡"}
                </button>

            </div>


            <div class="recipe-body">

                <div class="recipe-meta">

                    <span class="recipe-time">
                        ⏱ ${escapeHtml(recipe.time)}
                    </span>

                    <span class="recipe-serves">
                        👥 ${escapeHtml(recipe.serves)}
                    </span>


                </div>

                <h3><a class="recipe-title-link" href="${recipePagePath(recipe)}">${escapeHtml(recipe.name)}</a></h3>
                ${recipe.nameUrdu ? `<div class="recipe-name-urdu" lang="ur" dir="rtl">${escapeHtml(recipe.nameUrdu)}</div>` : ""}

                <p>
                    ${escapeHtml(recipe.description)}
                </p>

                <div class="recipe-bottom">

                    <button
                        type="button"
                        class="view-recipe"
                        data-recipe="${recipe.id}"
                    >
                        Quick View →
                    </button>

                    <a class="full-recipe" href="${recipePagePath(recipe)}">
                        Full Recipe ↗
                    </a>

                </div>

            </div>
        `;

        recipeGrid.appendChild(card);

    });

}


/* =====================================
   CATEGORY FILTER
===================================== */

function setCategory(category) {

    currentCategory = category;
    showFavoritesOnly = false;
    favoritesFilter.classList.remove("active");
    favoritesFilter.setAttribute("aria-pressed", "false");

    document.querySelectorAll(".filter-btn").forEach(btn => {

        btn.classList.toggle(
            "active",
            btn.dataset.filter === category
        );

    });

    renderRecipes();

}


/* =====================================
   FILTER BUTTONS
===================================== */

document.querySelectorAll(".filter-btn").forEach(btn => {

    btn.addEventListener("click", () => {

        setCategory(btn.dataset.filter);

    });

});


/* =====================================
   CATEGORY BOXES
===================================== */

document.querySelectorAll(".category-box").forEach(box => {

    box.addEventListener("click", () => {

        setCategory(box.dataset.category);

        document.getElementById("recipes").scrollIntoView({
            behavior: "smooth"
        });

    });

});


/* =====================================
   CATEGORY DROPDOWN LINKS
===================================== */

document.querySelectorAll("[data-category-link]").forEach(link => {

    link.addEventListener("click", () => {

        setCategory(link.dataset.categoryLink);

    });

});


/* =====================================
   SEARCH
===================================== */

searchInput.addEventListener("input", () => {

    renderRecipes();

});


favoritesFilter.addEventListener("click", () => {

    showFavoritesOnly = !showFavoritesOnly;
    currentCategory = "All";

    favoritesFilter.classList.toggle("active", showFavoritesOnly);
    favoritesFilter.setAttribute("aria-pressed", String(showFavoritesOnly));

    document.querySelectorAll(".filter-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.filter === "All" && !showFavoritesOnly);
    });

    renderRecipes();

});


clearResults.addEventListener("click", () => {

    searchInput.value = "";
    setCategory("All");
    searchInput.focus();

});


/* =====================================
   RECIPE CARD ACTIONS
===================================== */

recipeGrid.addEventListener("click", event => {

    const favoriteButton =
        event.target.closest("[data-favorite]");

    const recipeButton =
        event.target.closest("[data-recipe]");


    if (favoriteButton) {

        const id = Number(favoriteButton.dataset.favorite);

        toggleFavorite(id);

    }


    if (recipeButton) {

        const id = Number(recipeButton.dataset.recipe);

        openRecipe(id);

    }

});


/* =====================================
   FAVORITE FUNCTION
===================================== */

function toggleFavorite(id) {

    if (favorites.includes(id)) {

        favorites = favorites.filter(
            favoriteId => favoriteId !== id
        );

        showToast("Removed from favorites");

    } else {

        favorites.push(id);

        showToast("Added to favorites ❤️");

    }


    savePreference("pakistanFoodFavorites", JSON.stringify(favorites));


    renderRecipes();

}


/* =====================================
   OPEN RECIPE MODAL
===================================== */

function openRecipe(id) {

    const recipe = recipes.find(
        item => item.id === id
    );

    if (!recipe) return;

    rememberRecentlyViewed(recipe.id);

    if (!recipeModal.classList.contains("active")) {
        lastFocusedElement = document.activeElement;
        lastFocusedRecipeId = document.activeElement?.matches?.('[data-recipe]') ? id : null;
    }

    const isFavorite = favorites.includes(recipe.id);


    modalContent.innerHTML = `

        <img
            class="modal-image"
            src="${escapeHtml(sizedRecipeImage(recipe, 960))}"
            alt="${escapeHtml(recipeImageAlt(recipe))}"
            width="900"
            height="675"
            decoding="async"
        >

        <div class="modal-body">

            <span class="section-label">
                ${escapeHtml(recipe.category)} • ${escapeHtml(recipe.time)} • Serves ${escapeHtml(recipe.serves)}
            </span>

            <h2 id="modalRecipeTitle">${escapeHtml(recipe.name)}</h2>
            ${recipe.nameUrdu ? `<p class="recipe-title-urdu" lang="ur" dir="rtl">${escapeHtml(recipe.nameUrdu)}</p>` : ""}

            <a class="modal-full-recipe" href="${recipePagePath(recipe)}">
                Open the permanent recipe page →
            </a>
            ${recipe.methodUrdu.length ? `<a class="modal-full-recipe modal-urdu-link" href="${recipePagePath(recipe)}?lang=ur" lang="ur" dir="rtl">اردو میں مکمل ترکیب ←</a>` : ""}

            <p class="modal-description">
                ${escapeHtml(recipe.description)}
            </p>

            <button type="button" class="modal-favorite ${isFavorite ? "active" : ""}" data-modal-favorite="${recipe.id}" aria-pressed="${isFavorite}">
                ${isFavorite ? "♥ Saved recipe" : "♡ Save recipe"}
            </button>

            <div class="modal-columns">

                <div>

                    <h3>Ingredients</h3>

                    <ul>
                        ${recipe.ingredients
                            .map(item => `<li>${escapeHtml(item)}</li>`)
                            .join("")
                        }
                    </ul>

                </div>

                <div>

                    <h3>Cooking Method</h3>

                    <ol>
                        ${recipe.method
                            .map(item => `<li>${escapeHtml(item)}</li>`)
                            .join("")
                        }
                    </ol>

                </div>

            </div>

        </div>
    `;


    recipeModal.classList.add("active");
    recipeModal.setAttribute("aria-hidden", "false");

    document.body.classList.add("no-scroll");

    history.replaceState(null, "", `#recipe-${recipe.id}`);

    modalClose.focus();

}


/* =====================================
   CLOSE MODAL
===================================== */

function closeRecipe() {

    if (!recipeModal.classList.contains("active")) return;

    recipeModal.classList.remove("active");
    recipeModal.setAttribute("aria-hidden", "true");

    document.body.classList.remove("no-scroll");

    if (window.location.hash.startsWith("#recipe-")) {
        history.replaceState(null, "", `${window.location.pathname}${window.location.search}`);
    }

    if (lastFocusedElement instanceof HTMLElement && lastFocusedElement.isConnected) {
        lastFocusedElement.focus();
    } else if (lastFocusedRecipeId !== null) {
        (recipeGrid.querySelector(`[data-recipe="${lastFocusedRecipeId}"]`) || searchInput).focus();
    }

}


modalClose.addEventListener("click", closeRecipe);

modalOverlay.addEventListener("click", closeRecipe);

modalContent.addEventListener("click", event => {

    const favoriteButton = event.target.closest("[data-modal-favorite]");

    if (!favoriteButton) return;

    const id = Number(favoriteButton.dataset.modalFavorite);

    toggleFavorite(id);
    openRecipe(id);

});


document.addEventListener("keydown", event => {

    if (event.key === "Escape") {

        closeRecipe();

        if (mobileMenu.classList.contains("active")) {
            closeMobileMenu();
            menuBtn.focus();
        }

    }

    if (event.key === "Tab" && recipeModal.classList.contains("active")) {
        const controls = [...recipeModal.querySelectorAll('a[href], button:not([disabled]), input:not([disabled])')]
            .filter(element => element.getClientRects().length);
        if (!controls.length) return;
        const first = controls[0];
        const last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

});


/* =====================================
   DARK MODE
===================================== */

const savedTheme =
    readPreference("pakistanFoodTheme");


if (savedTheme === "dark") {

    document.body.classList.add("dark");

    themeBtn.textContent = "☀️";
    themeBtn.setAttribute("aria-pressed", "true");
    themeBtn.setAttribute("aria-label", "Use light theme");

}


themeBtn.addEventListener("click", () => {

    document.body.classList.toggle("dark");

    const dark =
        document.body.classList.contains("dark");


    themeBtn.textContent =
        dark ? "☀️" : "🌙";

    themeBtn.setAttribute("aria-pressed", String(dark));
    themeBtn.setAttribute("aria-label", dark ? "Use light theme" : "Use dark theme");


    savePreference("pakistanFoodTheme", dark ? "dark" : "light");

});


/* =====================================
   MOBILE MENU
===================================== */

function openMobileMenu() {

    mobileMenu.classList.add("active");
    mobileMenu.setAttribute("aria-hidden", "false");
    mobileMenu.removeAttribute("inert");
    menuBtn.setAttribute("aria-expanded", "true");

    document.body.classList.add("no-scroll");

    closeMenu.focus();

}


function closeMobileMenu() {

    mobileMenu.classList.remove("active");
    mobileMenu.setAttribute("aria-hidden", "true");
    mobileMenu.setAttribute("inert", "");
    menuBtn.setAttribute("aria-expanded", "false");

    document.body.classList.remove("no-scroll");

}


menuBtn.addEventListener("click", openMobileMenu);

closeMenu.addEventListener("click", closeMobileMenu);


document.querySelectorAll(".mobile-menu a").forEach(link => {

    link.addEventListener("click", closeMobileMenu);

});


/* =====================================
   CONTACT FORM
===================================== */

const contactForm =
    document.getElementById("contactForm");


contactForm.addEventListener("submit", event => {

    event.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const subject = document.getElementById("subject").value.trim();
    const message = document.getElementById("message").value.trim();

    const emailSubject = encodeURIComponent(`[Pakistan Food] ${subject}`);
    const emailBody = encodeURIComponent(`${message}\n\nFrom: ${name}\nReply email: ${email}`);

    showToast("Opening your email app…");
    window.location.href = `mailto:manazarali01@gmail.com?subject=${emailSubject}&body=${emailBody}`;

});


/* =====================================
   TOAST
===================================== */

let toastTimer;


function showToast(message) {

    toastMessage.textContent = message;

    toast.classList.add("show");

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);

}


/* =====================================
   HEADER SCROLL
===================================== */

const header =
    document.getElementById("header");


window.addEventListener("scroll", () => {

    if (window.scrollY > 50) {

        header.classList.add("scrolled");

    } else {

        header.classList.remove("scrolled");

    }


    if (window.scrollY > 500) {

        backTop.classList.add("show");

    } else {

        backTop.classList.remove("show");

    }

});


/* =====================================
   BACK TO TOP
===================================== */

backTop.addEventListener("click", () => {

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

});


/* =====================================
   CURRENT YEAR
===================================== */

document.getElementById("year").textContent =
    new Date().getFullYear();


/* =====================================
   INITIAL LOAD
===================================== */

renderRecipes();
renderRecentlyViewed();

function openRecipeFromHash() {

    const match = window.location.hash.match(/^#recipe-(\d+)$/);

    if (!match) return;

    openRecipe(Number(match[1]));

}

openRecipeFromHash();

window.addEventListener("hashchange", openRecipeFromHash);
