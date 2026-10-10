/* Pakistan Food · original natural food atmosphere · 2026-10-10
   No dependencies, data writes, redirects or changes to recipe photography. */
(() => {
  "use strict";
  const effects = Object.freeze({
    "chicken-biryani": ["steam", "center"],
    "chicken-karahi": ["steam", "right"],
    "beef-nihari": ["steam", "center"],
    "haleem": ["steam", "center"],
    "halwa-puri": ["steam", "left"],
    "kashmiri-chai": ["steam", "center"],
    "chicken-sajji": ["heat", "center"],
    "seekh-kabab": ["heat", "center"],
    "chapli-kabab": ["heat", "center"],
    "reshmi-kabab": ["heat", "center"],
    "lahori-chargha": ["heat", "center"],
    "mango-lassi": ["fresh", "right"],
    "lassi": ["fresh", "center"],
    "jalebi": ["dessert", "center"],
    "rice-kheer": ["dessert", "center"],
    "ras-malai": ["dessert", "center"]
  });
  const steamPaths = [
    "M48 139 C22 110 86 90 56 63 C34 44 87 28 67 7",
    "M91 143 C115 115 72 91 98 66 C124 44 78 30 104 5",
    "M132 137 C110 112 155 86 131 62 C108 36 155 27 140 9"
  ];
  const watched = new WeakSet();
  const observers = [];
  let observer;
  const svgMarkup = () =>
    '<svg viewBox="0 0 180 150" preserveAspectRatio="xMidYMid meet" focusable="false" aria-hidden="true">' +
    steamPaths.map(path => '<path class="pf-vapor-line" d="' + path + '"></path>').join("") +
    '</svg>';

  function slugFromCard(card) {
    const link = card.querySelector('a.full-recipe[href*="/recipes/"]') ||
      card.querySelector('a[href*="/recipes/"]');
    const href = link?.getAttribute("href") || "";
    const match = href.match(/(?:^|\/)recipes\/([a-z0-9-]+)\.html(?:[?#]|$)/);
    return match ? match[1] : "";
  }
  function attach(frame, slug) {
    if (!frame || frame.hasAttribute("data-pf-atmosphere-ready")) return;
    const config = effects[slug];
    if (!config) return;
    // Mark only after a matching food type is found, never add to unrelated food.
    frame.setAttribute("data-pf-atmosphere-ready", config[0]);
    if (getComputedStyle(frame).position === "static") {
      frame.style.position = "relative";
    }
    const effect = document.createElement("span");
    effect.className = "pf-food-atmosphere pf-effect-" + config[0];
    effect.setAttribute("aria-hidden", "true");
    effect.setAttribute("data-pf-place", config[1]);
    if (config[0] === "steam" || config[0] === "heat") {
      effect.innerHTML = svgMarkup();
    } else {
      const light = document.createElement("span");
      light.className = config[0] === "fresh" ? "pf-fresh-light" : "pf-dessert-light";
      effect.appendChild(light);
    }
    frame.appendChild(effect);
    if (observer) observer.observe(frame);
    else frame.classList.add("pf-atmosphere-visible");
  }
  function scan(root = document) {
    root.querySelectorAll(".pf-food-photo[data-pf-dish]").forEach(frame => {
      attach(frame, frame.dataset.pfDish);
    });
    root.querySelectorAll(".recipe-card .recipe-image").forEach(frame => {
      const card = frame.closest(".recipe-card");
      if (card) attach(frame, slugFromCard(card));
    });
  }
  function init() {
    // Apply one explicitly chosen preference to every recipe page.
    let preference = null;
    try { preference = localStorage.getItem("pfFoodMotionPreference"); } catch (_) {}
    if (preference === "off") {
      document.body.classList.add("pf-motion-paused");
    } else if (preference === "on") {
      document.body.classList.remove("pf-motion-paused");
      document.body.classList.add("pf-motion-force-on");
    }
    if ("IntersectionObserver" in window) {
      observer = new IntersectionObserver(entries => {
        for (const entry of entries) {
          entry.target.classList.toggle("pf-atmosphere-visible", entry.isIntersecting);
        }
      }, {rootMargin:"50px 0px", threshold:0.05});
    }
    const grid = document.getElementById("recipeGrid");
    if (grid && "MutationObserver" in window) {
      const update = new MutationObserver(() => scan(grid));
      update.observe(grid, {childList:true});
      observers.push(update);
    }
    document.addEventListener("visibilitychange", () => {
      document.body.classList.toggle("pf-motion-page-hidden", document.hidden);
    }, {passive:true});
    window.PakistanFoodAtmosphere = {refresh: scan};
    scan();
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, {once:true});
  } else {
    init();
  }
})();
