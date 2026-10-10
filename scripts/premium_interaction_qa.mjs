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

  await check("Only the photo-calibrated featured Biryani gets steam; no table or Haleem smoke", async () => {
    await page.emulateMedia({reducedMotion:"no-preference"});
    await page.evaluate(() => {localStorage.removeItem("pfFoodMotionEnabled");localStorage.removeItem("pfFoodMotionPreference");});
    await page.reload({waitUntil:"domcontentloaded"});
    const frame=page.locator(".featured-card:first-child .pf-food-photo");
    await frame.scrollIntoViewIfNeeded();
    await page.waitForFunction(() => {
      const canvas=document.querySelector(".featured-card:first-child .pf-steam-canvas");
      return canvas && canvas.width>50 && getComputedStyle(canvas).display!=="none";
    });
    if(await page.locator(".pf-mist, .pf-vapor-line, #pfMotionToggle, .pf-motion-preview, .pf-featured-motion").count()){
      throw Error("Legacy fake waves, cloud or Play/Pause control remains");
    }
    const count=await page.locator(".pf-steam-canvas").count();
    if(count!==1) throw Error("Expected only one food-calibrated steam preview, found "+count);
    if(await page.locator('.popular-recipe-card .pf-steam-canvas, .featured-card:nth-child(2) .pf-steam-canvas').count()){
      throw Error("Generic card smoke still enabled, including ambiguous Haleem composition");
    }
    const info=await frame.locator("canvas").evaluate(el=>({
      touch:getComputedStyle(el).pointerEvents,
      arialabel:el.getAttribute("aria-hidden"),
      size:[el.width,el.height],
    }));
    if(info.touch!=="none"||info.arialabel!=="true"||info.size[0]<50){
      throw Error("Canvas intercepts taps or is missing accessible hidden state "+JSON.stringify(info));
    }
    return true;
  });

  await check("Steam alpha appears above Biryani rice but NEVER over the lower plate/table", async () => {
    const frame=page.locator(".featured-card:first-child .pf-food-photo");
    await frame.scrollIntoViewIfNeeded();
    await page.waitForTimeout(850);
    const density=await frame.locator("canvas").evaluate(canvas=>{
      const ctx=canvas.getContext("2d");
      const w=canvas.width,h=canvas.height;
      const px=ctx.getImageData(0,0,w,h).data;
      let food=0,bright=0,lower=0;
      for(let y=0;y<h;y+=2){
        for(let x=0;x<w;x+=2){
          const alpha=px[(y*w+x)*4+3];
          if(y>=h*.58 && alpha>2)lower++;
          if(y>=h*.04&&y<=h*.45&&x>=w*.27&&x<=w*.73){
            if(alpha>3)food++;
            if(alpha>18)bright++;
          }
        }
      }
      return {food,bright,lower,w,h};
    });
    if(density.food<100||density.bright<10||density.lower>0){
      throw Error("Steam invisible or painted below food onto plate: "+JSON.stringify(density));
    }
    return true;
  });

  await check("Steam makes a measurable visual change to original photo pixels", async () => {
    const frame=page.locator(".featured-card:first-child .pf-food-photo");
    await frame.scrollIntoViewIfNeeded();
    await page.waitForTimeout(450);
    const canvas=frame.locator("canvas");
    const visible=PNG.sync.read(await frame.screenshot({animations:"allow"}));
    await canvas.evaluate(el=>el.style.visibility="hidden");
    const clear=PNG.sync.read(await frame.screenshot({animations:"allow"}));
    await canvas.evaluate(el=>el.style.visibility="");
    if(visible.width!==clear.width||visible.height!==clear.height) throw Error("Screenshots have different dimensions");
    let affected=0,max=0;
    const w=visible.width,h=visible.height;
    for(let y=Math.floor(h*.04);y<Math.floor(h*.48);y+=2){
      for(let x=Math.floor(w*.26);x<Math.floor(w*.75);x+=2){
        const at=(y*w+x)*4;
        const d=(Math.abs(visible.data[at]-clear.data[at])+Math.abs(visible.data[at+1]-clear.data[at+1])+Math.abs(visible.data[at+2]-clear.data[at+2]))/3;
        if(d>=5)affected++;
        if(d>max)max=d;
      }
    }
    if(affected<60||max<9) throw Error("Steam not clearly visible in final screenshot: "+JSON.stringify({affected,max}));
    return true;
  });

  await check("Respect reduced-motion; explicit URL opt-in works automatically with no button", async () => {
    await page.emulateMedia({reducedMotion:"reduce"});
    await page.evaluate(()=>{localStorage.removeItem("pfFoodMotionEnabled");localStorage.removeItem("pfFoodMotionPreference");});
    await page.goto(base+"/",{waitUntil:"domcontentloaded"});
    const frame=page.locator(".featured-card:first-child .pf-food-photo");
    await frame.scrollIntoViewIfNeeded();
    if(await frame.locator("canvas").evaluate(el=>getComputedStyle(el).display)!=="none")throw Error("Reduced motion not honored");
    await page.goto(base+"/?food-motion=on#featured",{waitUntil:"domcontentloaded"});
    await frame.scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>document.querySelector(".featured-card:first-child .pf-steam-canvas")?.style.display==="block");
    if(await page.locator("#pfMotionToggle").count())throw Error("Play/Pause button reintroduced");
    await page.goto(base+"/",{waitUntil:"domcontentloaded"});
    await frame.scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>document.querySelector(".featured-card:first-child .pf-steam-canvas")?.style.display==="block");
    await page.evaluate(()=>{localStorage.removeItem("pfFoodMotionEnabled");localStorage.removeItem("pfFoodMotionPreference");});
    await page.emulateMedia({reducedMotion:"no-preference"});
    await page.reload({waitUntil:"domcontentloaded"});
    return true;
  });

  await check("Permanent recipe preserves SEO, Urdu and print; no uncalibrated smoke", async () => {
    const response=await page.goto(base+"/recipes/haleem.html",{waitUntil:"domcontentloaded"});
    if(!response?.ok())throw Error("Haleem recipe is unavailable");
    const haleem=await page.evaluate(()=>({
      canonical:document.querySelector('link[rel="canonical"]')?.href,
      description:document.querySelector('meta[name="description"]')?.content,
      print:!!document.querySelector(".print-recipe"),
      urdu:!!document.querySelector('[data-recipe-lang="ur"]'),
      photo:!!document.querySelector(".pf-recipe-photo img[alt]"),
      unwanted:!!document.querySelector(".pf-steam-canvas, .pf-mist"),
    }));
    if(!haleem.canonical?.endsWith("/recipes/haleem.html")||!haleem.description||!haleem.print||!haleem.urdu||!haleem.photo||haleem.unwanted){
      throw Error("Uncorrected Haleem table steam or recipe SEO regression: "+JSON.stringify(haleem));
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
await check("Android touch device runs original food-only vapor without buttons", async()=>{
  const phone=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true,reducedMotion:"no-preference"});
  try{
    const p=await phone.newPage();
    p.on("pageerror",e=>failures.push("Android browser exception: "+e.message));
    const response=await p.goto(base+"/",{waitUntil:"domcontentloaded"});
    if(!response?.ok())throw Error("Homepage failed on mobile");
    const photo=p.locator(".featured-card:first-child .pf-food-photo");
    await photo.scrollIntoViewIfNeeded();
    await p.waitForFunction(()=>{
      const c=document.querySelector(".featured-card:first-child .pf-steam-canvas");
      return c&&c.width>0&&c.style.display==="block";
    });
    await p.waitForTimeout(450);
    const first=await photo.locator("canvas").evaluate(c=>c.getContext("2d").getImageData(0,0,c.width,c.height).data.reduce((a,x)=>a+x,0));
    await p.waitForTimeout(930);
    const next=await photo.locator("canvas").evaluate(c=>c.getContext("2d").getImageData(0,0,c.width,c.height).data.reduce((a,x)=>a+x,0));
    if(first===next || first===0 || next===0)throw Error("Canvas isn't moving on Android touch viewport");
    if(await p.locator("#pfMotionToggle").count())throw Error("Unexpected button present");
    return true;
  }finally{await phone.close();}
});

await browser.close();

for (const description of passed) console.log("PASS " + description);
for (const message of failures) console.error("FAIL " + message);
console.log("Premium browser QA: " + passed.length + " passed, " + failures.length + " failed");
if (failures.length) process.exit(1);
