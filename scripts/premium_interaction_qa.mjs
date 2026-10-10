/* Premium appearance and functionality smoke test — run against Jekyll output.
   These checks guard live controls, icons and layout; they do not modify content. */
import { chromium } from "playwright";

const base = process.env.QA_BASE_URL || "http://127.0.0.1:4173";
const widths = [320, 360, 390, 430, 768, 1024, 1440];
const failures = [];
const passed = [];

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 390, height: 870 },
  deviceScaleFactor: 1,
});
await context.route(/googlesyndication|doubleclick|googleadservices/, route => route.abort());
const page = await context.newPage();
page.on("pageerror", error => failures.push("Browser exception: " + error.message));

async function check(description, action) {
  try {
    const result = await action();
    if (result === false) throw Error("Assertion returned false");
    passed.push(description);
  } catch (error) {
    failures.push(description + ": " + (error?.message || String(error)));
  }
}
const cards = () => page.locator(".recipe-card").count();

await check("Custom SVG sprite is served with all required symbols", async () => {
  const response = await page.request.get(base + "/assets/food-premium-icons.svg");
  if (!response.ok()) return false;
  const text = await response.text();
  return ["rice", "chicken", "bbq", "vegetarian", "search", "phone", "mail", "pin"].every(
    key => text.includes('<symbol id="' + key + '"')
  );
});

for (const width of widths) {
  await page.setViewportSize({ width, height: 870 });
  await check("Homepage and recipe cards load at " + width + "px", async () => {
    const response = await page.goto(base + "/", { waitUntil: "domcontentloaded" });
    if (!response?.ok()) return false;
    await page.waitForFunction(() => document.querySelectorAll(".recipe-card").length >= 60);
    await page.waitForFunction(() => document.querySelectorAll(".category-box .pf-picto").length >= 9);
    return (await cards()) >= 60;
  });
  await check("Original icons render in all category and contact cards at " + width + "px", async () => {
    const state = await page.evaluate(() => ({
      categories: [...document.querySelectorAll(".category-box")].filter(b => b.querySelector("svg.pf-picto use[href*='food-premium-icons.svg#']")).length,
      contacts: [...document.querySelectorAll(".contact-card")].filter(b => b.querySelector("svg.pf-picto use")).length,
      search: !!document.querySelector(".search-box svg.pf-picto use"),
      accessible: [...document.querySelectorAll(".category-box svg.pf-picto")].every(svg => svg.getAttribute("aria-hidden") === "true"),
    }));
    return state.categories === 9 && state.contacts === 3 && state.search && state.accessible;
  });
  await check("No sideways overflow or clipped category filter controls at " + width + "px", async () => {
    const metrics = await page.evaluate(() => {
      const root = document.documentElement;
      const buttons = [...document.querySelectorAll(".recipes .filter-btn")].map(el => {
        const rect = el.getBoundingClientRect();
        return { left: rect.left, right: rect.right, w: rect.width };
      });
      return {
        overflow: Math.max(root.scrollWidth, document.body.scrollWidth) - window.innerWidth,
        controls: buttons.length,
        clipped: buttons.filter(b => b.left < -1 || b.right > window.innerWidth + 1 || b.w < 50),
      };
    });
    if (metrics.overflow > 2) throw Error("horizontal overflow " + metrics.overflow + "px");
    if (metrics.controls !== 10) throw Error("only " + metrics.controls + " filters");
    if (metrics.clipped.length) throw Error("filter clips " + JSON.stringify(metrics.clipped));
    return true;
  });
  await check("Photographic glass treatment stays visible at " + width + "px", async () => {
    const state = await page.evaluate(() => {
      const heading = document.querySelector("main .featured .section-heading");
      const section = document.querySelector("main .featured");
      const bg = getComputedStyle(section).backgroundImage;
      const frost = getComputedStyle(heading).backdropFilter ||
        getComputedStyle(heading).webkitBackdropFilter;
      return { bg, frost, headingColor: getComputedStyle(heading.querySelector("h2")).color };
    });
    return state.bg.includes("pexels") && state.frost.includes("blur");
  });
  if (width !== 390) continue;

  await check("Featured badge visibly animates on a 390px mobile viewport", async () => {
    await page.emulateMedia({ reducedMotion: "no-preference" });
    const badge = page.locator(".featured-card:first-child .pf-featured-motion");
    if (!(await badge.isVisible())) throw Error("Static featured badge absent");
    const properties = await badge.evaluate(el => {
      const style = getComputedStyle(el);
      const shine = getComputedStyle(el.closest(".featured-card"), "::before");
      return {
        animationName: style.animationName,
        display: style.display,
        imageLightAnimation: shine.animationName,
        pointerEvents: style.pointerEvents,
      };
    });
    if (!properties.animationName.includes("pf-featured-badge-float")) {
      throw Error("Badge animation not running: " + JSON.stringify(properties));
    }
    if (!properties.imageLightAnimation.includes("pf-featured-light-sweep")) {
      throw Error("Photo light animation missing: " + JSON.stringify(properties));
    }
    if (properties.pointerEvents !== "none") throw Error("Badge may block recipe clicks");
    const frames = [];
    for (const delay of [0, 430, 650]) {
      if (delay) await page.waitForTimeout(delay);
      frames.push(await badge.evaluate(el => getComputedStyle(el).transform));
    }
    if (new Set(frames).size < 2) throw Error("Badge does not change position: " + frames.join(" / "));
    await page.emulateMedia({ reducedMotion: "reduce" });
    const reduced = await badge.evaluate(el => getComputedStyle(el).animationName);
    if (!(await badge.isVisible()) || reduced !== "none") {
      throw Error("Reduced-motion presentation unsafe: " + reduced);
    }
    await page.emulateMedia({ reducedMotion: "no-preference" });
    return true;
  });

  await check("Natural biryani steam auto-rises and cold lassi gets reflection on mobile", async () => {
    await page.emulateMedia({reducedMotion: "no-preference"});
    await page.evaluate(() => localStorage.removeItem("pfFoodMotionPreference"));
    await page.reload({waitUntil: "domcontentloaded"});
    const photo = page.locator('.featured-card:first-child .pf-food-photo');
    await photo.scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector('.featured-card:first-child .pf-food-photo')?.classList.contains("pf-atmosphere-visible"));
    const steam = photo.locator('.pf-effect-steam .pf-vapor-line').first();
    if (!(await steam.count())) throw Error("Biryani steam overlay missing");
    const before = await steam.evaluate(el => ({
      animation: getComputedStyle(el).animationName,
      transform: getComputedStyle(el).transform,
      pointerEvents: getComputedStyle(el.closest(".pf-food-atmosphere")).pointerEvents,
    }));
    if (!before.animation.includes("pf-vapor-rise-one") || before.pointerEvents !== "none") {
      throw Error("Auto steam is inactive or blocks taps: " + JSON.stringify(before));
    }
    await page.waitForTimeout(660);
    const after = await steam.evaluate(el => getComputedStyle(el).transform);
    if (before.transform === after) throw Error("Steam did not visibly rise: " + after);
    if (!(await page.locator('.featured-card:nth-child(2) .pf-effect-steam').count())) {
      throw Error("Chicken karahi steam missing");
    }
    if (!(await page.locator('.featured-card:nth-child(3) .pf-effect-fresh .pf-fresh-light').count())) {
      throw Error("Mango lassi reflection missing");
    }
    if (await page.locator('.featured-card:nth-child(3) .pf-effect-steam').count()) {
      throw Error("Cold lassi mistakenly got hot-food steam");
    }
    await page.emulateMedia({reducedMotion: "reduce"});
    const reduced = await steam.evaluate(el => ({
      name: getComputedStyle(el).animationName,
      container: getComputedStyle(el.closest(".pf-food-atmosphere")).display,
    }));
    if (reduced.container !== "none") throw Error("Reduced-motion smoke still shown: " + JSON.stringify(reduced));
    await page.emulateMedia({reducedMotion: "no-preference"});
    return true;
  });

  await check("Permanent recipe page has natural steam without SEO or print regression", async () => {
    const resp = await page.goto(base + "/recipes/chicken-biryani.html", {waitUntil:"domcontentloaded"});
    if (!resp?.ok()) return false;
    const seo = await page.evaluate(() => ({
      canonical: document.querySelector('link[rel="canonical"]')?.href,
      description: document.querySelector('meta[name="description"]')?.content,
      print: !!document.querySelector(".print-recipe"),
      photo: !!document.querySelector('.pf-recipe-photo[data-pf-dish="chicken-biryani"] .pf-effect-steam'),
      correctAlt: !!document.querySelector('.pf-recipe-photo img[alt]'),
      jsErrors: !document.querySelector(".pf-food-atmosphere")?.getAttribute("aria-hidden"),
    }));
    if (!seo.canonical?.endsWith("/recipes/chicken-biryani.html") || !seo.description || !seo.print || !seo.photo || !seo.correctAlt) {
      throw Error("Permanent page content/atmosphere issue: "+JSON.stringify(seo));
    }
    await page.goto(base + "/", {waitUntil:"domcontentloaded"});
    return true;
  });

  await check("Manual Play Motion works even with reduced-motion device settings", async () => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.reload({ waitUntil: "domcontentloaded" });
    const button = page.locator("#pfMotionToggle");
    const badge = page.locator(".featured-card:first-child .pf-featured-motion");
    const orb = page.locator(".pf-motion-orb");
    if (!(await button.isVisible())) throw Error("Play Motion button missing");
    const warning = await page.locator("#pfMotionStatus").textContent();
    if (!warning.includes("prefers reduced motion")) {
      throw Error("Mobile reduced-motion diagnosis missing: " + warning);
    }
    if ((await badge.evaluate(el => getComputedStyle(el).animationName)) !== "none") {
      throw Error("Reduced-motion preference was not respected initially");
    }
    await button.click();
    if ((await button.getAttribute("aria-pressed")) !== "true") throw Error("Play button did not toggle on");
    const playing = await page.evaluate(() => ({
      badge: getComputedStyle(document.querySelector(".pf-featured-motion")).animationName,
      badgeDuration: getComputedStyle(document.querySelector(".pf-featured-motion")).animationDuration,
      orb: getComputedStyle(document.querySelector(".pf-motion-orb")).animationName,
      shine: getComputedStyle(document.querySelector(".featured-card:first-child"), "::before").animationName,
      bodyClass: document.body.className,
    }));
    if (!playing.badge.includes("pf-manual-demo-badge") || !playing.orb.includes("pf-manual-demo-orb")) {
      throw Error("Opt-in mobile animations did not activate: " + JSON.stringify(playing));
    }
    if (!playing.shine.includes("pf-featured-light-sweep")) throw Error("Biryani light sweep remains off");
    if (parseFloat(playing.badgeDuration) < 1) {
      throw Error("Device CSS globally disabled animation: " + playing.badgeDuration);
    }
    const positions = [];
    for (const delay of [0, 350, 400]) {
      if (delay) await page.waitForTimeout(delay);
      positions.push(await badge.evaluate(el => getComputedStyle(el).transform));
    }
    if (new Set(positions).size < 2) {
      throw Error("Play Motion produced zero physical movement: " + JSON.stringify(positions));
    }
    const orbPositions = [];
    for (const delay of [0, 300]) {
      if (delay) await page.waitForTimeout(delay);
      orbPositions.push(await orb.evaluate(el => getComputedStyle(el).transform));
    }
    if (new Set(orbPositions).size < 2) throw Error("Star demo remained stationary");
    await button.click();
    const paused = await badge.evaluate(el => getComputedStyle(el).animationName);
    if (paused !== "none" || (await button.getAttribute("aria-pressed")) !== "false") {
      throw Error("Pause Motion did not stop animation");
    }
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.evaluate(() => localStorage.removeItem("pfFoodMotionPreference"));
    await page.reload({ waitUntil: "domcontentloaded" });
    return true;
  });

  await check("Live search finds biryani and handles empty results", async () => {
    await page.locator("#searchInput").fill("chicken biryani");
    const matched = await cards();
    if (matched < 1 || matched > 8) throw Error("incorrect search count " + matched);
    await page.locator("#searchInput").fill("zzzz-not-a-food-9876");
    if (await cards() !== 0 || !(await page.locator("#noResults").isVisible())) {
      throw Error("No-results state missing");
    }
    await page.locator("#clearResults").click();
    if (await cards() < 60) throw Error("Clear results failed");
    return true;
  });
  await check("Category filters still work after vector icons are installed", async () => {
    await page.locator('.filter-btn[data-filter="BBQ"]').click();
    const badges = await page.locator(".recipe-card .recipe-badge").allTextContents();
    if (!badges.length || badges.length > 60 || badges.some(x => x.trim() !== "BBQ")) {
      throw Error("Bad category filtering: " + JSON.stringify(badges.slice(0, 5)));
    }
    await page.locator('.filter-btn[data-filter="All"]').click();
    return (await cards()) >= 60;
  });
  await check("Favorites toggle, persists across reload and removes correctly", async () => {
    const button = page.locator(".recipe-card .favorite-btn").first();
    await button.click();
    if (await page.locator("#favoriteCount").textContent() !== "1") throw Error("Favorite was not saved");
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => document.querySelectorAll(".recipe-card").length >= 60);
    if (await page.locator("#favoriteCount").textContent() !== "1") throw Error("Favorite was lost on reload");
    await page.locator("#favoritesFilter").click();
    if (await cards() !== 1) throw Error("Saved filter failed");
    await page.locator(".recipe-card .favorite-btn").first().click();
    if (await page.locator("#favoriteCount").textContent() !== "0") throw Error("Favorite removal failed");
    await page.locator("#favoritesFilter").click();
    return (await cards()) >= 60;
  });
  await check("Dark and light mode toggles remain functional", async () => {
    await page.locator("#themeBtn").click();
    if (!(await page.locator("body").evaluate(el => el.classList.contains("dark")))) {
      throw Error("Dark theme did not activate");
    }
    if (await page.locator("#themeBtn").getAttribute("aria-pressed") !== "true") {
      throw Error("Dark theme aria-pressed missing");
    }
    await page.locator("#themeBtn").click();
    const light = await page.locator("body").evaluate(el => !el.classList.contains("dark"));
    return light && (await page.locator("#themeBtn").getAttribute("aria-pressed")) === "false";
  });
  await check("Mobile menu opens and closes with restored page scrolling", async () => {
    await page.locator("#menuBtn").click();
    if (await page.locator("#mobileMenu").getAttribute("aria-hidden") !== "false") {
      throw Error("Menu not opened");
    }
    if (!(await page.locator("body").evaluate(el => el.classList.contains("no-scroll")))) {
      throw Error("Menu did not lock page scroll");
    }
    await page.locator("#closeMenu").click();
    return (await page.locator("#mobileMenu").getAttribute("aria-hidden")) === "true" &&
      await page.locator("body").evaluate(el => !el.classList.contains("no-scroll"));
  });
}
// Real mobile touch environment, separate from CSS-only 390px responsive tests.
await check("Android-style touch viewport auto-animates natural food steam", async () => {
  const phone = await browser.newContext({
    viewport: {width:390,height:844},
    deviceScaleFactor:2,
    isMobile:true,
    hasTouch:true,
    reducedMotion:"no-preference",
  });
  try {
    const mobilePage = await phone.newPage();
    mobilePage.on("pageerror", error => failures.push("Touch-browser exception: " + error.message));
    const response = await mobilePage.goto(base + "/", {waitUntil:"domcontentloaded"});
    if (!response?.ok()) throw Error("Mobile homepage failed");
    const frame = mobilePage.locator('.featured-card:first-child .pf-food-photo');
    await frame.scrollIntoViewIfNeeded();
    await mobilePage.waitForFunction(() => document.querySelector('.featured-card:first-child .pf-food-photo')?.classList.contains("pf-atmosphere-visible"));
    const steam = frame.locator(".pf-vapor-line").first();
    if (!(await steam.count())) throw Error("Food atmosphere did not attach on touch browser");
    const first = await steam.evaluate(el => ({
      transform:getComputedStyle(el).transform,
      animation:getComputedStyle(el).animationName,
    }));
    await mobilePage.waitForTimeout(620);
    const last = await steam.evaluate(el => getComputedStyle(el).transform);
    if (!first.animation.includes("pf-vapor-rise-one") || first.transform === last) {
      throw Error("Mobile touch animation not moving: "+JSON.stringify({first,last}));
    }
    const button = mobilePage.locator("#pfMotionToggle");
    await button.tap();
    if ((await button.getAttribute("aria-pressed")) !== "false") {
      throw Error("Tap could not pause autoplay");
    }
    await button.tap();
    if ((await button.getAttribute("aria-pressed")) !== "true") {
      throw Error("Tap could not resume autoplay");
    }
    return true;
  } finally {
    await phone.close();
  }
});

await browser.close();

for (const description of passed) console.log("PASS " + description);
for (const message of failures) console.error("FAIL " + message);
console.log("Premium browser QA: " + passed.length + " passed, " + failures.length + " failed");
if (failures.length) process.exit(1);
