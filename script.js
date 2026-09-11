/* =====================================
   PAKISTAN FOOD
   MAIN JAVASCRIPT
===================================== */


/* =====================================
   RECIPE DATA
===================================== */

const recipes = [

    {
        id: 1,
        name: "Chicken Biryani",
        category: "Rice",
        time: "60 min",
        rating: "4.9",
        image: "https://snapcalorie-webflow-website.s3.us-east-2.amazonaws.com/media/food_pics_v2/medium/pakistani_bhiriyani_rice.jpg",
        description: "Aromatic basmati rice layered with spicy chicken, fried onions and traditional Pakistani spices.",
        ingredients: [
            "Chicken",
            "Basmati rice",
            "Onions",
            "Tomatoes",
            "Yogurt",
            "Biryani masala",
            "Ginger & garlic",
            "Green chilies"
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
        rating: "4.8",
        image: "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=900&q=85",
        description: "Fragrant Pakistani pulao prepared with tender chicken and aromatic whole spices.",
        ingredients: [
            "Chicken",
            "Basmati rice",
            "Onions",
            "Whole spices",
            "Yogurt",
            "Ginger garlic"
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
        rating: "4.9",
        image: "https://images.unsplash.com/photo-1716535232842-d10da4eb33d5?auto=format&fit=crop&w=900&q=85",
        description: "Classic Pakistani chicken karahi cooked with tomatoes, green chilies and fresh ginger.",
        ingredients: [
            "Chicken",
            "Tomatoes",
            "Green chilies",
            "Ginger",
            "Garlic",
            "Red chili",
            "Coriander"
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
        rating: "4.7",
        image: "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=900&q=85",
        description: "Creamy and rich chicken handi with a delicious blend of Pakistani spices.",
        ingredients: [
            "Chicken",
            "Cream",
            "Yogurt",
            "Tomatoes",
            "Onions",
            "Ginger garlic",
            "Spices"
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
        rating: "4.9",
        image: "https://snapcalorie-webflow-website.s3.us-east-2.amazonaws.com/media/recipe_pics_v2/medium/nihari_pakistani_stew.jpg",
        description: "Slow-cooked Pakistani beef stew with deep spices and rich traditional flavour.",
        ingredients: [
            "Beef",
            "Nihari masala",
            "Ginger garlic",
            "Flour",
            "Oil",
            "Fresh ginger",
            "Green chilies"
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
        rating: "4.8",
        image: "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?auto=format&fit=crop&w=900&q=85",
        description: "Juicy minced-meat seekh kababs seasoned with traditional Pakistani spices.",
        ingredients: [
            "Minced beef",
            "Onion",
            "Green chilies",
            "Coriander",
            "Ginger garlic",
            "Kabab spices"
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
        rating: "4.8",
        image: "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=85",
        description: "Famous Pashtun-style flat kababs packed with spices, herbs and rich flavour.",
        ingredients: [
            "Minced beef",
            "Tomato",
            "Onion",
            "Green chilies",
            "Coriander",
            "Crushed spices"
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
        rating: "4.8",
        image: "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85",
        description: "Crispy golden samosas filled with a delicious spicy potato mixture.",
        ingredients: [
            "Flour",
            "Potatoes",
            "Green chilies",
            "Coriander",
            "Cumin",
            "Red chili"
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
        rating: "4.7",
     image: "https://img.ananinja.com/media/ninja-catalog-42/restaurants/rzjwuc0nhdzizlksufzkihtutg7z/pakora.jpg",
        description: "Crispy Pakistani pakoras perfect for rainy evenings and Ramadan iftar.",
        ingredients: [
            "Gram flour",
            "Potatoes",
            "Onion",
            "Green chilies",
            "Coriander",
            "Spices"
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
        rating: "4.9",
        image: "https://images.unsplash.com/photo-1668357530437-72a12c660f94?auto=format&fit=crop&w=900&q=85",
        description: "Crispy stuffed potato paratha served with yogurt, pickle or chai.",
        ingredients: [
            "Wheat flour",
            "Potatoes",
            "Green chilies",
            "Coriander",
            "Red chili",
            "Cumin"
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
        rating: "4.9",
        image: "https://www.restonnow.com/files/2021/07/halwah-puti.jpeg",
        description: "Traditional Pakistani breakfast of fluffy puris served with sweet halwa and chickpea curry.",
        ingredients: [
            "Semolina",
            "Sugar",
            "Flour",
            "Oil",
            "Chickpeas",
            "Spices"
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
        rating: "4.8",
        image: "https://irepo.primecp.com/2023/03/550444/1677704667_399942_Large500_ID-5117465.jpg?v=5117465",
        description: "Traditional creamy Pakistani rice pudding flavored with cardamom and nuts.",
        ingredients: [
            "Milk",
            "Rice",
            "Sugar",
            "Cardamom",
            "Almonds",
            "Pistachios"
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
        rating: "4.9",
        image: "https://images.unsplash.com/photo-1666190092159-3171cf0fbb12?auto=format&fit=crop&w=900&q=85",
        description: "Soft golden milk-solid dumplings soaked in sweet fragrant sugar syrup.",
        ingredients: [
            "Milk powder",
            "Flour",
            "Baking powder",
            "Milk",
            "Sugar",
            "Cardamom"
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
        rating: "4.7",
         image: "https://images.deliveryhero.io/image/fd-pk/LH/w0fr-listing.jpg",
        description: "Simple and comforting Pakistani daal served with steamed rice and achaar.",
        ingredients: [
            "Lentils",
            "Rice",
            "Onion",
            "Tomato",
            "Garlic",
            "Cumin",
            "Red chili"
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
        rating: "4.8",
        image: "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=900&q=85",
        description: "Aromatic beef pulao prepared with fragrant rice and traditional whole spices.",
        ingredients: [
            "Beef",
            "Basmati rice",
            "Onions",
            "Whole spices",
            "Ginger garlic",
            "Green chilies"
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


/* =====================================
   ELEMENTS
===================================== */

const recipeGrid = document.getElementById("recipeGrid");
const searchInput = document.getElementById("searchInput");
const noResults = document.getElementById("noResults");

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


/* =====================================
   FAVORITES
===================================== */

let favorites = JSON.parse(
    localStorage.getItem("pakistanFoodFavorites") || "[]"
);


/* =====================================
   RENDER RECIPES
===================================== */

function renderRecipes() {

    const searchTerm = searchInput.value.toLowerCase().trim();

    const filtered = recipes.filter(recipe => {

        const categoryMatch =
            currentCategory === "All" ||
            recipe.category === currentCategory;

        const searchMatch =
            recipe.name.toLowerCase().includes(searchTerm) ||
            recipe.category.toLowerCase().includes(searchTerm) ||
            recipe.description.toLowerCase().includes(searchTerm);

        return categoryMatch && searchMatch;

    });


    recipeGrid.innerHTML = "";


    if (filtered.length === 0) {

        noResults.style.display = "block";

        return;

    }

    noResults.style.display = "none";


    filtered.forEach(recipe => {

        const isFavorite = favorites.includes(recipe.id);

        const card = document.createElement("article");

        card.className = "recipe-card";

        card.innerHTML = `

            <div class="recipe-image">

                <img
                    src="${recipe.image}"
                    alt="${recipe.name}"
                    loading="lazy"
                    onerror="this.src='https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80'"
                >

                <span class="recipe-badge">
                    ${recipe.category}
                </span>

                <button
                    class="favorite-btn ${isFavorite ? "active" : ""}"
                    data-favorite="${recipe.id}"
                    aria-label="Favorite recipe"
                >
                    ${isFavorite ? "♥" : "♡"}
                </button>

            </div>


            <div class="recipe-body">

                <div class="recipe-meta">

                    <span class="recipe-time">
                        ⏱ ${recipe.time}
                    </span>

                    <span class="recipe-rating">
                        ★ ${recipe.rating}
                    </span>

                </div>

                <h3>${recipe.name}</h3>

                <p>
                    ${recipe.description}
                </p>

                <div class="recipe-bottom">

                    <button
                        class="view-recipe"
                        data-recipe="${recipe.id}"
                    >
                        View Recipe →
                    </button>

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


    modalContent.innerHTML = `

        <img
            class="modal-image"
            src="${recipe.image}"
            alt="${recipe.name}"
        >

        <div class="modal-body">

            <span class="section-label">
                ${recipe.category} • ${recipe.time}
            </span>

            <h2>${recipe.name}</h2>

            <p class="modal-description">
                ${recipe.description}
            </p>

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

    document.body.classList.add("no-scroll");

}


/* =====================================
   CLOSE MODAL
===================================== */

function closeRecipe() {

    recipeModal.classList.remove("active");

    document.body.classList.remove("no-scroll");

}


modalClose.addEventListener("click", closeRecipe);

modalOverlay.addEventListener("click", closeRecipe);


document.addEventListener("keydown", event => {

    if (event.key === "Escape") {

        closeRecipe();

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

}


themeBtn.addEventListener("click", () => {

    document.body.classList.toggle("dark");

    const dark =
        document.body.classList.contains("dark");


    themeBtn.textContent =
        dark ? "☀️" : "🌙";


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

    document.body.classList.add("no-scroll");

}


function closeMobileMenu() {

    mobileMenu.classList.remove("active");

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

    showToast(
        "Thank you! Your message has been received."
    );

    contactForm.reset();

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