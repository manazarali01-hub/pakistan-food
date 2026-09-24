/* =====================================
   PAKISTAN FOOD
   MAIN JAVASCRIPT
===================================== */


/* =====================================
   RECIPE DATA
===================================== */

const defaultRecipes = [

    {
        id: 1,
        name: "Chicken Biryani",
        category: "Rice",
        time: "60 min",
        serves: 6,
        image: "assets/chicken-biryani.webp?v=20260912-fast2",
        description: "Aromatic basmati rice layered with spicy chicken, fried onions and traditional Pakistani spices.",
        ingredients: [
            "750 g bone-in chicken",
            "3 cups basmati rice",
            "3 onions, thinly sliced",
            "3 tomatoes, chopped",
            "1 cup plain yogurt",
            "2 tbsp biryani masala",
            "2 tbsp ginger-garlic paste",
            "4 green chilies",
            "½ cup mint and coriander",
            "Salt and cooking oil"
        ],
        method: [
            "Wash and soak the basmati rice.",
            "Cook chicken with onions, tomatoes, yogurt and spices.",
            "Boil rice separately until nearly cooked.",
            "Layer rice and chicken masala.",
            "Cover and cook on low heat for 15–20 minutes."
        ]
    },

    {
        id: 2,
        name: "Chicken Pulao",
        category: "Rice",
        time: "50 min",
        serves: 5,
        image: "assets/chicken-pulao.webp?v=20260912-fast2",
        description: "Fragrant Pakistani pulao prepared with tender chicken and aromatic whole spices.",
        ingredients: [
            "750 g bone-in chicken",
            "3 cups basmati rice",
            "2 onions, sliced",
            "1 tbsp mixed whole spices",
            "½ cup plain yogurt",
            "2 tbsp ginger-garlic paste",
            "5 cups water for stock",
            "Salt and green chilies"
        ],
        method: [
            "Fry onions until golden.",
            "Add chicken and spices.",
            "Add water and cook chicken.",
            "Add soaked rice.",
            "Cook until rice becomes fluffy."
        ]
    },

    {
        id: 3,
        name: "Chicken Karahi",
        category: "Chicken",
        time: "45 min",
        serves: 4,
        image: "assets/chicken-karahi.webp?v=20260912-fast2",
        description: "Classic Pakistani chicken karahi cooked with tomatoes, green chilies and fresh ginger.",
        ingredients: [
            "1 kg chicken, karahi cut",
            "6 ripe tomatoes, chopped",
            "5 green chilies",
            "2 tbsp fresh ginger, julienned",
            "1 tbsp garlic paste",
            "1 tsp red chili powder",
            "1 tsp crushed coriander",
            "½ cup cooking oil and salt"
        ],
        method: [
            "Heat oil in a karahi.",
            "Add chicken and fry well.",
            "Add tomatoes and spices.",
            "Cook until oil separates.",
            "Finish with ginger, chilies and coriander."
        ]
    },

    {
        id: 4,
        name: "Chicken Handi",
        category: "Chicken",
        time: "45 min",
        serves: 4,
        image: "assets/chicken-handi.webp?v=20260912-fast2",
        description: "Creamy and rich chicken handi with a delicious blend of Pakistani spices.",
        ingredients: [
            "750 g boneless chicken",
            "½ cup cooking cream",
            "½ cup plain yogurt",
            "4 tomatoes, blended",
            "1 onion, finely chopped",
            "1½ tbsp ginger-garlic paste",
            "1 tsp red chili powder",
            "½ tsp garam masala",
            "Salt and cooking oil"
        ],
        method: [
            "Cook onions and chicken.",
            "Add tomatoes and spices.",
            "Add yogurt and cook well.",
            "Add cream.",
            "Simmer for 10 minutes."
        ]
    },

    {
        id: 5,
        name: "Beef Nihari",
        category: "Beef",
        time: "4 hrs",
        serves: 6,
        image: "assets/nihari.webp?v=20260912-fast2",
        description: "Slow-cooked Pakistani beef stew with deep spices and rich traditional flavour.",
        ingredients: [
            "1 kg beef shank",
            "3 tbsp nihari masala",
            "2 tbsp ginger-garlic paste",
            "⅓ cup wheat flour",
            "½ cup cooking oil",
            "7 cups water",
            "Fresh ginger and coriander",
            "Green chilies, lemon and salt"
        ],
        method: [
            "Fry beef with ginger garlic.",
            "Add nihari spices.",
            "Add plenty of water.",
            "Slow cook until beef is tender.",
            "Add flour slurry to thicken."
        ]
    },

    {
        id: 6,
        name: "Seekh Kabab",
        category: "BBQ",
        time: "40 min",
        serves: 5,
        image: "assets/seekh-kebab.webp?v=20260912-fast2",
        description: "Juicy minced-meat seekh kababs seasoned with traditional Pakistani spices.",
        ingredients: [
            "750 g beef mince with some fat",
            "1 small onion, very finely chopped",
            "3 green chilies, chopped",
            "½ cup fresh coriander",
            "1 tbsp ginger-garlic paste",
            "1½ tbsp seekh kabab masala",
            "1 tbsp lemon juice",
            "Salt and oil for brushing"
        ],
        method: [
            "Mix all ingredients with minced meat.",
            "Shape mixture around skewers.",
            "Chill for better shape.",
            "Grill or barbecue.",
            "Serve hot with chutney."
        ]
    },

    {
        id: 7,
        name: "Chapli Kabab",
        category: "BBQ",
        time: "35 min",
        serves: 5,
        image: "assets/chapli-kebab.webp?v=20260912-fast2",
        description: "Famous Pashtun-style flat kababs packed with spices, herbs and rich flavour.",
        ingredients: [
            "750 g beef mince with some fat",
            "1 tomato, finely chopped",
            "1 onion, finely chopped",
            "3 green chilies",
            "½ cup fresh coriander",
            "2 tbsp crushed coriander and cumin",
            "3 tbsp maize flour",
            "1 egg, salt and frying oil"
        ],
        method: [
            "Combine minced meat with all ingredients.",
            "Shape into flat kababs.",
            "Heat oil in a pan.",
            "Fry both sides until cooked.",
            "Serve with chutney."
        ]
    },

    {
        id: 8,
        name: "Pakistani Samosa",
        category: "Snacks",
        time: "45 min",
        serves: 6,
        image: "assets/pakistani-samosa-v2.webp",
        description: "Crispy golden samosas filled with a delicious spicy potato mixture.",
        ingredients: [
            "2 cups plain flour",
            "4 medium potatoes, boiled",
            "3 green chilies, chopped",
            "½ cup fresh coriander",
            "1 tsp cumin seeds",
            "1 tsp crushed red chili",
            "½ tsp ajwain",
            "Salt, water and frying oil"
        ],
        method: [
            "Prepare dough with flour.",
            "Make spicy potato filling.",
            "Shape samosa wrappers.",
            "Fill and seal.",
            "Deep fry until golden."
        ]
    },

    {
        id: 9,
        name: "Pakora",
        category: "Snacks",
        time: "25 min",
        serves: 6,
        image: "assets/pakora.webp?v=20260912-fast2",
        description: "Crispy Pakistani pakoras perfect for rainy evenings and Ramadan iftar.",
        ingredients: [
            "2 cups gram flour",
            "1 potato, thinly sliced",
            "2 onions, sliced",
            "3 green chilies, chopped",
            "½ cup fresh coriander",
            "1 tsp cumin and ½ tsp ajwain",
            "¾ cup water, approximately",
            "Salt and frying oil"
        ],
        method: [
            "Prepare gram flour batter.",
            "Add vegetables and spices.",
            "Heat oil.",
            "Drop spoonfuls into hot oil.",
            "Fry until crisp and golden."
        ]
    },

    {
        id: 10,
        name: "Aloo Paratha",
        category: "Breakfast",
        time: "30 min",
        serves: 4,
        image: "assets/aloo-paratha.webp?v=20260912-fast2",
        description: "Crispy stuffed potato paratha served with yogurt, pickle or chai.",
        ingredients: [
            "2 cups whole-wheat flour",
            "3 medium potatoes, boiled",
            "2 green chilies, chopped",
            "½ cup fresh coriander",
            "½ tsp red chili powder",
            "1 tsp roasted cumin",
            "Water and salt for dough",
            "Ghee or oil for cooking"
        ],
        method: [
            "Prepare soft dough.",
            "Make spiced potato filling.",
            "Stuff filling inside dough.",
            "Roll carefully.",
            "Cook on tawa with oil or ghee."
        ]
    },

    {
        id: 11,
        name: "Halwa Puri",
        category: "Breakfast",
        time: "45 min",
        serves: 5,
        image: "assets/halwa-puri.webp?v=20260912-fast2",
        description: "Traditional Pakistani breakfast of fluffy puris served with sweet halwa and chickpea curry.",
        ingredients: [
            "1 cup semolina",
            "¾ cup sugar",
            "2 cups whole-wheat flour",
            "½ cup ghee for halwa",
            "2 cups cooked chickpeas",
            "1 tbsp chana masala",
            "4 green cardamoms",
            "Water, salt and frying oil"
        ],
        method: [
            "Prepare semolina halwa with sugar.",
            "Prepare chickpea curry.",
            "Make soft puri dough.",
            "Roll small puris.",
            "Deep fry until puffed and golden.",
            "Serve everything hot."
        ]
    },

    {
        id: 12,
        name: "Rice Kheer",
        category: "Desserts",
        time: "60 min",
        serves: 6,
        image: "assets/kheer.webp?v=20260912-fast2",
        description: "Traditional creamy Pakistani rice pudding flavored with cardamom and nuts.",
        ingredients: [
            "1 litre full-fat milk",
            "¼ cup basmati rice",
            "½ cup sugar",
            "4 green cardamoms",
            "2 tbsp sliced almonds",
            "2 tbsp sliced pistachios",
            "1 tsp rose water, optional"
        ],
        method: [
            "Wash and soak rice.",
            "Cook rice in milk.",
            "Add sugar.",
            "Cook until thick and creamy.",
            "Add cardamom and nuts."
        ]
    },

    {
        id: 13,
        name: "Gulab Jamun",
        category: "Desserts",
        time: "40 min",
        serves: 8,
        image: "assets/gulab-jamun.webp?v=20260912-fast2",
        description: "Soft golden milk-solid dumplings soaked in sweet fragrant sugar syrup.",
        ingredients: [
            "1 cup milk powder",
            "¼ cup plain flour",
            "½ tsp baking powder",
            "¼ cup milk, approximately",
            "1½ cups sugar",
            "1½ cups water",
            "4 green cardamoms",
            "2 tbsp ghee and frying oil"
        ],
        method: [
            "Prepare a soft dough.",
            "Shape into small balls.",
            "Deep fry on low heat.",
            "Prepare sugar syrup.",
            "Soak fried gulab jamun in syrup."
        ]
    },

    {
        id: 14,
        name: "Daal Chawal",
        category: "Rice",
        time: "45 min",
        serves: 4,
        image: "assets/daal-chawal.webp?v=20260912-fast2",
        description: "Simple and comforting Pakistani daal served with steamed rice and achaar.",
        ingredients: [
            "1 cup moong or masoor lentils",
            "2 cups basmati rice",
            "1 onion, sliced",
            "1 tomato, chopped",
            "4 garlic cloves, sliced",
            "1 tsp cumin seeds",
            "½ tsp red chili powder",
            "Salt, turmeric and ghee"
        ],
        method: [
            "Wash and boil lentils.",
            "Cook rice separately.",
            "Prepare garlic and onion tempering.",
            "Add tempering to daal.",
            "Serve hot with rice."
        ]
    },

    {
        id: 15,
        name: "Beef Pulao",
        category: "Rice",
        time: "75 min",
        serves: 6,
        image: "assets/beef-pulao.webp?v=20260912-fast2",
        description: "Aromatic beef pulao prepared with fragrant rice and traditional whole spices.",
        ingredients: [
            "1 kg beef with bones",
            "4 cups basmati rice",
            "3 onions, sliced",
            "1½ tbsp mixed whole spices",
            "2 tbsp ginger-garlic paste",
            "5 green chilies",
            "7 cups water for stock",
            "Salt and cooking oil"
        ],
        method: [
            "Cook beef with whole spices.",
            "Prepare flavorful stock.",
            "Add soaked basmati rice.",
            "Cook until rice is tender.",
            "Rest before serving."
        ]
    }

];


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

const recipes = (cmsRecipes.length ? cmsRecipes : defaultRecipes).map((recipe, index) => ({
    ...recipe,
    id: stableRecipeId(recipe, index),
    slug: stableRecipeSlug(recipe, index),
    serves: Number(recipe.serves) || 4,
    image: String(recipe.image || "assets/chicken-biryani.webp").replace(/^\//, ""),
    ingredients: Array.isArray(recipe.ingredients) ? recipe.ingredients : [],
    method: Array.isArray(recipe.method) ? recipe.method : []
}));

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


/* =====================================
   FAVORITES
===================================== */

let favorites = JSON.parse(
    localStorage.getItem("pakistanFoodFavorites") || "[]"
).map(Number).filter(Number.isFinite);


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
            recipe.category,
            recipe.description,
            ...recipe.ingredients,
            ...recipe.method
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
                    src="${recipe.image}"
                    alt="${recipe.name} ready to serve"
                    loading="${index < 3 ? "eager" : "lazy"}" decoding="async"
                    fetchpriority="${index === 0 ? "high" : "auto"}"
                    width="900"
                    height="675"
                >

                <span class="recipe-badge">
                    ${recipe.category}
                </span>

                <button
                    type="button"
                    class="favorite-btn ${isFavorite ? "active" : ""}"
                    data-favorite="${recipe.id}"
                    aria-label="${isFavorite ? "Remove" : "Save"} ${recipe.name} ${isFavorite ? "from" : "to"} favorites"
                    aria-pressed="${isFavorite}"
                >
                    ${isFavorite ? "♥" : "♡"}
                </button>

            </div>


            <div class="recipe-body">

                <div class="recipe-meta">

                    <span class="recipe-time">
                        ⏱ ${recipe.time}
                    </span>

                    <span class="recipe-serves">
                        👥 ${recipe.serves}
                    </span>


                </div>

                <h3><a class="recipe-title-link" href="${recipePagePath(recipe)}">${recipe.name}</a></h3>

                <p>
                    ${recipe.description}
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


    localStorage.setItem(
        "pakistanFoodFavorites",
        JSON.stringify(favorites)
    );


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

    lastFocusedElement = document.activeElement;

    const isFavorite = favorites.includes(recipe.id);


    modalContent.innerHTML = `

        <img
            class="modal-image"
            src="${recipe.image}"
            alt="${recipe.name} ready to serve"
            width="900"
            height="675"
        >

        <div class="modal-body">

            <span class="section-label">
                ${recipe.category} • ${recipe.time} • Serves ${recipe.serves}
            </span>

            <h2 id="modalRecipeTitle">${recipe.name}</h2>

            <a class="modal-full-recipe" href="${recipePagePath(recipe)}">
                Open the permanent recipe page →
            </a>

            <p class="modal-description">
                ${recipe.description}
            </p>

            <button type="button" class="modal-favorite ${isFavorite ? "active" : ""}" data-modal-favorite="${recipe.id}" aria-pressed="${isFavorite}">
                ${isFavorite ? "♥ Saved recipe" : "♡ Save recipe"}
            </button>

            <div class="modal-columns">

                <div>

                    <h3>Ingredients</h3>

                    <ul>
                        ${recipe.ingredients
                            .map(item => `<li>${item}</li>`)
                            .join("")
                        }
                    </ul>

                </div>

                <div>

                    <h3>Cooking Method</h3>

                    <ol>
                        ${recipe.method
                            .map(item => `<li>${item}</li>`)
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

    if (lastFocusedElement instanceof HTMLElement) {
        lastFocusedElement.focus();
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
    localStorage.getItem("pakistanFoodTheme");


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


    localStorage.setItem(
        "pakistanFoodTheme",
        dark ? "dark" : "light"
    );

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

function openRecipeFromHash() {

    const match = window.location.hash.match(/^#recipe-(\d+)$/);

    if (!match) return;

    openRecipe(Number(match[1]));

}

openRecipeFromHash();

window.addEventListener("hashchange", openRecipeFromHash);
