/* Pakistan Food · restrained food-warmth illustration v2 · 2026-10-10
   No persistent controls, photos replaced or external motion dependencies. */
(() => {
  "use strict";
  // Positions are deliberate FOOD-surface regions, not the plate/bowl edge.
  // Reduce scope rather than applying an implausible overlay to all 66 recipes.
  const positions = Object.freeze({
    "chicken-biryani": {left:"34%", top:"3%", width:"32%", height:"39%"},
    "chicken-karahi": {left:"38%", top:"7%", width:"29%", height:"40%"},
    "beef-nihari": {left:"38%", top:"7%", width:"28%", height:"39%"},
    "haleem": {left:"36%", top:"7%", width:"30%", height:"39%"},
    "kashmiri-chai": {left:"44%", top:"10%", width:"24%", height:"32%"}
  });
  let observer;
  function addMist(frame) {
    if (frame.dataset.pfAtmosphereReady) return;
    const coordinates = positions[frame.dataset.pfDish];
    if (!coordinates) return;
    frame.dataset.pfAtmosphereReady = "mist";
    const overlay = document.createElement("span");
    overlay.className = "pf-food-atmosphere";
    overlay.setAttribute("aria-hidden", "true");
    overlay.style.setProperty("--pf-steam-left", coordinates.left);
    overlay.style.setProperty("--pf-steam-top", coordinates.top);
    overlay.style.setProperty("--pf-steam-width", coordinates.width);
    overlay.style.setProperty("--pf-steam-height", coordinates.height);
    for (let i = 0; i < 2; i++) {
      const cloud = document.createElement("span");
      cloud.className = "pf-mist";
      overlay.appendChild(cloud);
    }
    frame.appendChild(overlay);
    if (observer) observer.observe(frame);
    else frame.classList.add("pf-atmosphere-visible");
  }
  function scan() {
    document.querySelectorAll(".pf-food-photo[data-pf-dish]").forEach(addMist);
  }
  function init() {
    if ("IntersectionObserver" in window) {
      observer = new IntersectionObserver(entries => {
        entries.forEach(({target,isIntersecting}) => {
          target.classList.toggle("pf-atmosphere-visible", isIntersecting);
        });
      }, {rootMargin:"30px 0px", threshold:.05});
    }
    document.addEventListener("visibilitychange", () => {
      document.body.classList.toggle("pf-motion-page-hidden",document.hidden);
    },{passive:true});
    scan();
  }
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded",init,{once:true});
  else init();
})();
