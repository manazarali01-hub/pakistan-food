/* Pakistan Food progressive enhancements */
(() => {
    const surpriseButton = document.getElementById("surpriseRecipe");
    const modalContent = document.getElementById("modalContent");

    function getRecipes() {
        return Array.isArray(window.PAKISTAN_FOOD_RECIPES)
            ? window.PAKISTAN_FOOD_RECIPES
            : [];
    }

    function recipeId(recipe, index) {
        if (Number.isFinite(Number(recipe.id))) return Number(recipe.id);
        const text = String(recipe.name || `recipe-${index}`);
        let hash = 0;
        for (const character of text) {
            hash = ((hash << 5) - hash + character.charCodeAt(0)) | 0;
        }
        return Math.abs(hash) + 1000;
    }

    if (surpriseButton) {
        surpriseButton.addEventListener("click", () => {
            const list = getRecipes();
            if (!list.length || typeof window.openRecipe !== "function") return;
            const index = Math.floor(Math.random() * list.length);
            window.openRecipe(recipeId(list[index], index));
        });
    }

    function currentRecipe() {
        const match = window.location.hash.match(/^#recipe-(\d+)$/);
        if (!match) return null;
        const id = Number(match[1]);
        const list = getRecipes();
        return list.find((recipe, index) => recipeId(recipe, index) === id) || null;
    }

    function recipeUrl(recipe) {
        if (recipe && recipe.slug) {
            return new URL(`recipes/${encodeURIComponent(recipe.slug)}.html`, document.baseURI).href;
        }
        return window.location.href;
    }

    function injectModalActions() {
        if (!modalContent || modalContent.querySelector(".modal-actions")) return;
        const title = modalContent.querySelector("h2");
        if (!title) return;

        const actions = document.createElement("div");
        actions.className = "modal-actions";
        actions.innerHTML = `
            <button type="button" data-recipe-share>↗ Share</button>
            <button type="button" data-recipe-copy>🔗 Copy link</button>
            <button type="button" data-recipe-print>🖨 Print</button>
        `;
        const favorite = modalContent.querySelector(".modal-favorite");
        if (favorite) favorite.insertAdjacentElement("afterend", actions);
        else title.insertAdjacentElement("afterend", actions);
    }

    if (modalContent) {
        const observer = new MutationObserver(injectModalActions);
        observer.observe(modalContent, { childList: true, subtree: true });
        injectModalActions();

        modalContent.addEventListener("click", async (event) => {
            const recipe = currentRecipe();
            if (!recipe) return;

            if (event.target.closest("[data-recipe-print]")) {
                window.print();
                return;
            }

            if (event.target.closest("[data-recipe-copy]")) {
                const permanentUrl = recipeUrl(recipe);
                try {
                    await navigator.clipboard.writeText(permanentUrl);
                    if (typeof window.showToast === "function") window.showToast("Recipe link copied ✓");
                } catch {
                    window.prompt("Copy this recipe link:", permanentUrl);
                }
                return;
            }

            if (event.target.closest("[data-recipe-share]")) {
                const permanentUrl = recipeUrl(recipe);
                const data = {
                    title: `${recipe.name} | Pakistan Food`,
                    text: `Try this ${recipe.name} recipe from Pakistan Food.`,
                    url: permanentUrl
                };
                if (navigator.share) {
                    try { await navigator.share(data); } catch (_) {}
                } else {
                    try {
                        await navigator.clipboard.writeText(permanentUrl);
                        if (typeof window.showToast === "function") window.showToast("Recipe link copied for sharing ✓");
                    } catch {
                        window.prompt("Copy this recipe link:", permanentUrl);
                    }
                }
            }
        });
    }
})();
