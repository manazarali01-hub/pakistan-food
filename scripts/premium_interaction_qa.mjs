/* Premium appearance and functionality smoke test — run against Jekyll output.
   These checks guard live controls, icons and layout; they do not modify content. */
import { chromium } from "playwright";
import { PNG } from "pngjs";

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

  await check("Natural mist rises gently from the FOOD, without a manual button or animated badge", async () => {
    await page.emulateMedia({reducedMotion:"no-preference"});
    await page.reload({waitUntil:"domcontentloaded"});
    const frame = page.locator(".featured-card:first-child .pf-food-photo");
    await frame.scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector(".featured-card:first-child .pf-food-photo")?.classList.contains("pf-atmosphere-visible"));
    if (await page.locator("#pfMotionToggle, .pf-motion-preview, .pf-featured-motion").count()) {
      throw Error("Removed Play/Pause control or floating badge still exists");
    }
    const mist = frame.locator(".pf-mist").first();
    if (!(await mist.count()) || await frame.locator(".pf-vapor-line, svg").count()) {
      throw Error("Soft mist absent or old drawn SVG waves still present");
    }
    const state = await mist.evaluate(el => {
      const box=el.getBoundingClientRect();
      const photo=el.closest(".pf-food-photo").getBoundingClientRect();
      const style=getComputedStyle(el);
      return {
        start:Math.round((box.top-photo.top)/photo.height*100),
        end:Math.round((box.bottom-photo.top)/photo.height*100),
        animation:style.animationName,
        transform:style.transform,
        pointerEvents:getComputedStyle(el.closest(".pf-food-atmosphere")).pointerEvents,
      };
    });
    if (state.start>15 || state.end>57 || state.pointerEvents!=="none") {
      throw Error("Mist improperly placed near plate or intercepts taps: "+JSON.stringify(state));
    }
    if (!state.animation.includes("pf-mist-rises")) {
      throw Error("Automatic soft mist failed to start: "+JSON.stringify(state));
    }
    await page.waitForTimeout(810);
    if (state.transform===await mist.evaluate(el=>getComputedStyle(el).transform)) {
      throw Error("Natural mist not rising on mobile");
    }
    return true;
  });

  await check("Biryani steam is visibly different from unchanged food photo (PNG pixel contrast)", async () => {
    // Existing CSS-only motion tests passed when vapor was imperceptibly faint.
    // Compare the *same paused frame* with and without the decorative layer,
    // and require nontrivial actual on-screen color difference.
    await page.emulateMedia({reducedMotion:"no-preference"});
    const frame=page.locator(".featured-card:first-child .pf-food-photo");
    await frame.scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>document.querySelector(".featured-card:first-child .pf-food-photo")?.classList.contains("pf-atmosphere-visible"));
    await frame.locator(".pf-mist").first().evaluate(el=>{
      for(const cloud of el.parentElement.querySelectorAll(".pf-mist")){
        for(const anim of cloud.getAnimations()){anim.currentTime=2700;anim.pause();}
      }
    });
    await page.waitForTimeout(100);
    const exposed=PNG.sync.read(await frame.screenshot({animations:"allow"}));
    const layer=frame.locator(".pf-food-atmosphere");
    await layer.evaluate(el=>el.style.visibility="hidden");
    const plain=PNG.sync.read(await frame.screenshot({animations:"allow"}));
    await layer.evaluate(el=>el.style.visibility="");
    if(exposed.width!==plain.width||exposed.height!==plain.height) throw Error("Photo sizes differ");
    let strong=0,maxDifference=0,all=0,regionPixels=0;
    const w=exposed.width,h=exposed.height;
    for(let y=0;y<Math.round(h*.58);y++){
      for(let x=Math.round(w*.24);x<Math.round(w*.77);x++){
        const i=(y*w+x)*4;
        const v=(Math.abs(exposed.data[i]-plain.data[i])+
          Math.abs(exposed.data[i+1]-plain.data[i+1])+
          Math.abs(exposed.data[i+2]-plain.data[i+2]))/3;
        if(v>=12) strong++;
        if(v>maxDifference) maxDifference=v;
        all+=v;
        regionPixels++;
      }
    }
    const share=strong/regionPixels;
    const avg=all/regionPixels;
    if(share<.008 || maxDifference<20 || avg<.65){
      throw Error("Steam has insufficient visible contrast on biryani: "+
        JSON.stringify({share:+share.toFixed(4),maxDifference,avg:+avg.toFixed(3)}));
    }
    return true;
  });

  await check("Explicit mobile opt-in enables automatic steam without any controls", async () => {
    await page.emulateMedia({reducedMotion:"reduce"});
    await page.goto(base+"/?food-motion=on#featured",{waitUntil:"domcontentloaded"});
    const frame=page.locator(".featured-card:first-child .pf-food-photo");
    await frame.scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>document.querySelector(".featured-card:first-child .pf-food-photo")?.classList.contains("pf-atmosphere-visible"));
    const enabled=await page.evaluate(()=>{
      const cloud=document.querySelector(".featured-card:first-child .pf-mist");
      return {
        optedIn:document.body.classList.contains("pf-food-motion-opted-in"),
        display:getComputedStyle(cloud.closest(".pf-food-atmosphere")).display,
        animation:getComputedStyle(cloud).animationName,
        button:document.getElementById("pfMotionToggle")!==null,
      };
    });
    if(!enabled.optedIn || enabled.display==="none" || !enabled.animation.includes("pf-mist-rises") || enabled.button){
      throw Error("Explicit motion preference not respected: "+JSON.stringify(enabled));
    }
    await page.goto(base+"/",{waitUntil:"domcontentloaded"});
    if(!(await page.evaluate(()=>document.body.classList.contains("pf-food-motion-opted-in")))){
      throw Error("Automatic steam opt-in did not persist across page loads");
    }
    await page.evaluate(()=>localStorage.removeItem("pfFoodMotionEnabled"));
    await page.emulateMedia({reducedMotion:"no-preference"});
    await page.reload({waitUntil:"domcontentloaded"});
    return true;
  });

  await check("Selected hot dishes only: no fake BBQ heat or cold-drink shimmer", async () => {
    if (!(await page.locator(".featured-card:nth-child(2) .pf-mist").count())) {
      throw Error("Chicken karahi mist missing");
    }
    if (await page.locator(".featured-card:nth-child(3) .pf-food-atmosphere").count()) {
      throw Error("Cold mango lassi has unnecessary animation");
    }
    if (await page.locator(".popular-recipe-card:nth-child(5) .pf-food-atmosphere").count()) {
      throw Error("BBQ still has artificial heat motion");
    }
    const photos=await page.locator(".featured-card .pf-food-photo img").count();
    return photos===3;
  });

  await check("Reduced-motion users see a fully static unobstructed photo", async () => {
    await page.emulateMedia({reducedMotion:"reduce"});
    const mist=page.locator(".featured-card:first-child .pf-mist").first();
    const visibility=await mist.evaluate(el=>getComputedStyle(el.closest(".pf-food-atmosphere")).display);
    if(visibility!=="none") throw Error("Reduced-motion setting ignored");
    if(await page.locator("#pfMotionToggle").count()) throw Error("Unwanted manual control exists");
    await page.emulateMedia({reducedMotion:"no-preference"});
    return true;
  });

  await check("Permanent recipe has food mist and intact canonical, description, print", async () => {
    const response=await page.goto(base+"/recipes/chicken-biryani.html",{waitUntil:"domcontentloaded"});
    if(!response?.ok()) throw Error("Recipe page HTTP error");
    const report=await page.evaluate(()=>({
      canonical:document.querySelector('link[rel="canonical"]')?.href,
      description:document.querySelector('meta[name="description"]')?.content,
      print:!!document.querySelector(".print-recipe"),
      mist:!!document.querySelector('.pf-recipe-photo[data-pf-dish="chicken-biryani"] .pf-mist'),
      alt:!!document.querySelector('.pf-recipe-photo img[alt]'),
      urdu:!!document.querySelector('[data-recipe-lang="ur"]')
    }));
    if(!report.canonical?.endsWith("/recipes/chicken-biryani.html") || !report.description || !report.print || !report.mist || !report.alt || !report.urdu) {
      throw Error("Recipe SEO, text, or steam regression: "+JSON.stringify(report));
    }
    await page.goto(base+"/",{waitUntil:"domcontentloaded"});
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
await check("Android-style touchscreen runs automatic soft mist without Play/Pause", async () => {
  const phone=await browser.newContext({
    viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true,
    reducedMotion:"no-preference"
  });
  try {
    const mobile=await phone.newPage();
    mobile.on("pageerror",error=>failures.push("Touch-browser exception: "+error.message));
    const response=await mobile.goto(base+"/",{waitUntil:"domcontentloaded"});
    if(!response?.ok()) throw Error("Touch homepage request failed");
    const frame=mobile.locator(".featured-card:first-child .pf-food-photo");
    await frame.scrollIntoViewIfNeeded();
    await mobile.waitForFunction(()=>document.querySelector(".featured-card:first-child .pf-food-photo")?.classList.contains("pf-atmosphere-visible"));
    const mist=frame.locator(".pf-mist").first();
    if(!(await mist.count())) throw Error("Mist missing in touchscreen browser");
    const before=await mist.evaluate(el=>({
      animation:getComputedStyle(el).animationName,
      transform:getComputedStyle(el).transform
    }));
    await mobile.waitForTimeout(730);
    const after=await mist.evaluate(el=>getComputedStyle(el).transform);
    if(!before.animation.includes("pf-mist-rises") || before.transform===after) {
      throw Error("No actual automatic mist movement on touch device: "+JSON.stringify({before,after}));
    }
    if(await mobile.locator("#pfMotionToggle").count()) throw Error("Play/Pause control reappeared");
    return true;
  } finally {await phone.close();}
});

await browser.close();

for (const description of passed) console.log("PASS " + description);
for (const message of failures) console.error("FAIL " + message);
console.log("Premium browser QA: " + passed.length + " passed, " + failures.length + " failed");
if (failures.length) process.exit(1);
