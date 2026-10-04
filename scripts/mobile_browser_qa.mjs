import { chromium } from "playwright";
import fs from "node:fs";

const base = process.env.QA_BASE_URL || "http://127.0.0.1:4173";
const widths = [320, 360, 375, 390, 412, 430, 768];
const pages = [
  ["home", "/"],
  ["chicken-biryani", "/recipes/chicken-biryani.html"],
  ["chicken-karahi", "/recipes/chicken-karahi.html"],
  ["halwa-puri", "/recipes/halwa-puri.html"],
  ["rice-kheer", "/recipes/rice-kheer.html"],
  ["cooking-guides", "/guides/"],
];

fs.mkdirSync("qa-screenshots", { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 768, height: 920 },
  deviceScaleFactor: 1,
});
await context.route(/googlesyndication|doubleclick|googleadservices/, route => route.abort());
const page = await context.newPage();
const failures = [];
const results = [];

page.on("pageerror", error => failures.push(`pageerror: ${error.message}`));
page.on("requestfailed", request => {
  const url = request.url();
  if (url.startsWith(base)) {
    failures.push(`same-origin request failed: ${url} — ${request.failure()?.errorText || "unknown"}`);
  }
});

async function scrollThrough() {
  await page.evaluate(async () => {
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
    const root = document.documentElement;
    const previousBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";
    const height = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
    const step = Math.max(420, Math.floor(window.innerHeight * 0.72));
    for (let y = 0; y < height; y += step) {
      window.scrollTo(0, y);
      await sleep(80);
    }
    window.scrollTo(0, Math.max(0, height - window.innerHeight));
    await sleep(180);
    window.scrollTo(0, 0);
    await sleep(80);
    root.style.scrollBehavior = previousBehavior;
  });
  await page.waitForFunction(() => window.scrollY === 0, null, { timeout: 1500 });
}

async function settleImages() {
  await page.evaluate(async () => {
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
    const pending = [...document.images]
      .filter(img => !img.complete)
      .map(img => new Promise(resolve => {
        const done = () => resolve();
        img.addEventListener("load", done, { once: true });
        img.addEventListener("error", done, { once: true });
      }));
    await Promise.race([
      Promise.all(pending),
      sleep(2500),
    ]);
    // Give an onerror local fallback a moment to replace and decode.
    await sleep(180);
  });
}

async function inspectLayout(label, width) {
  const report = await page.evaluate(() => {
    const doc = document.documentElement;
    const body = document.body;
    const documentWidth = Math.max(doc.scrollWidth, body?.scrollWidth || 0);
    const h1 = document.querySelector("h1");
    const imageNodes = [...document.querySelectorAll("img")];
    const broken = imageNodes
      .filter(img => img.complete && img.naturalWidth === 0)
      .map(img => ({ src: img.getAttribute("src"), alt: img.getAttribute("alt") }))
      .slice(0, 12);
    const placeholders = imageNodes
      .filter(img => {
        const src = img.getAttribute("src") || "";
        const current = img.currentSrc || "";
        return src.includes("recipe-image-unavailable.svg") || current.includes("recipe-image-unavailable.svg");
      })
      .map(img => ({ src: img.getAttribute("src"), currentSrc: img.currentSrc, alt: img.getAttribute("alt") }))
      .slice(0, 12);

    const smallTapTargets = [...document.querySelectorAll("button, a")]
      .filter(el => {
        const rect = el.getBoundingClientRect();
        const style = getComputedStyle(el);
        if (style.display === "none" || style.visibility === "hidden" || rect.width === 0 || rect.height === 0) return false;
        if (rect.bottom < 0 || rect.top > window.innerHeight) return false;

        if (el.tagName === "BUTTON") {
          // Prominent controls on this site are designed around a 40–44px touch target.
          return rect.width < 40 || rect.height < 40;
        }

        // WCAG 2.2 Target Size (Minimum) uses a 24px floor, while ordinary
        // inline text links have a spacing/inline exception. Do not turn
        // paragraph/breadcrumb links into false failures.
        const inlineTextLink =
          style.display === "inline" &&
          (el.closest("p, li, .seo-breadcrumb, .guide-shell, .policy-page") !== null);
        if (inlineTextLink) return false;

        return rect.width < 24 || rect.height < 24;
      })
      .slice(0, 12)
      .map(el => ({
        tag: el.tagName,
        text: (el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 80),
        width: Math.round(el.getBoundingClientRect().width),
        height: Math.round(el.getBoundingClientRect().height),
      }));

    return {
      viewportWidth: window.innerWidth,
      documentWidth,
      overflow: documentWidth - window.innerWidth,
      hasH1: Boolean(h1 && h1.getClientRects().length),
      h1Text: h1?.textContent?.trim() || "",
      broken,
      placeholders,
      smallTapTargets,
    };
  });

  if (report.overflow > 2) {
    failures.push(`${label} @ ${width}px: horizontal overflow ${report.overflow}px (document ${report.documentWidth}px / viewport ${report.viewportWidth}px)`);
  }
  if (!report.hasH1) {
    failures.push(`${label} @ ${width}px: visible H1 missing`);
  }
  if (report.broken.length) {
    failures.push(`${label} @ ${width}px: broken images: ${JSON.stringify(report.broken)}`);
  }
  if (report.placeholders.length) {
    failures.push(`${label} @ ${width}px: recipe image placeholder rendered: ${JSON.stringify(report.placeholders)}`);
  }
  // Buttons use the site's 40px control floor; non-inline links use WCAG's 24px floor.
  if (report.smallTapTargets.length > 0) {
    failures.push(`${label} @ ${width}px: too many tiny visible tap targets: ${JSON.stringify(report.smallTapTargets)}`);
  }
  return report;
}

async function testHomeInteractions(width) {
  await page.waitForSelector(".recipe-card", { timeout: 15000 });

  const recipeImageShape = await page.locator(".recipe-card img").evaluateAll(imgs => {
    const loaded = imgs
      .filter(img => img.complete && img.naturalWidth > 0 && img.naturalHeight > 0)
      .map(img => ({
        src: img.getAttribute("src") || "",
        ratio: img.naturalWidth / img.naturalHeight,
        width: img.naturalWidth,
        height: img.naturalHeight,
      }));
    const issues = loaded.filter(item => Math.abs(item.ratio - (4 / 3)) > 0.015);
    const unversioned = loaded.filter(item => /^assets\/.+\.webp(?:$|\?)/.test(item.src) && !/[?&]v=/.test(item.src));
    return { count: imgs.length, issues: issues.slice(0, 12), unversioned: unversioned.slice(0, 12) };
  });
  if (recipeImageShape.count < 60) {
    failures.push(`home @ ${width}px: expected at least 60 recipe-card images, found ${recipeImageShape.count}`);
  }
  if (recipeImageShape.issues.length) {
    failures.push(`home @ ${width}px: recipe images are not normalized to 4:3: ${JSON.stringify(recipeImageShape.issues)}`);
  }
  if (recipeImageShape.unversioned.length) {
    failures.push(`home @ ${width}px: recipe images missing cache-busting version: ${JSON.stringify(recipeImageShape.unversioned)}`);
  }

  if (width <= 430) {
    await page.locator("#menuBtn").click();
    await page.waitForSelector("#mobileMenu.active", { timeout: 5000 });
    // The drawer intentionally animates from right:-100% to right:0 over 350ms.
    // Verify its final resting state rather than sampling mid-transition.
    await page.waitForFunction(() => {
      const menu = document.querySelector("#mobileMenu.active");
      if (!menu) return false;
      const rect = menu.getBoundingClientRect();
      return rect.left >= -2 && rect.right <= window.innerWidth + 2;
    }, null, { timeout: 1800 });
    const menuState = await page.evaluate(() => {
      const menu = document.querySelector("#mobileMenu");
      const close = document.querySelector("#closeMenu");
      const rect = menu.getBoundingClientRect();
      const closeRect = close.getBoundingClientRect();
      return {
        ariaHidden: menu.getAttribute("aria-hidden"),
        bodyLocked: document.body.classList.contains("no-scroll"),
        right: rect.right,
        left: rect.left,
        viewport: window.innerWidth,
        closeW: closeRect.width,
        closeH: closeRect.height,
      };
    });
    if (menuState.ariaHidden !== "false" || !menuState.bodyLocked || menuState.left < -2 || menuState.right > menuState.viewport + 2) {
      failures.push(`home @ ${width}px: mobile menu is not contained/accessible: ${JSON.stringify(menuState)}`);
    }
    if (menuState.closeW < 40 || menuState.closeH < 40) {
      failures.push(`home @ ${width}px: mobile close control is too small: ${menuState.closeW}x${menuState.closeH}`);
    }
    await page.locator("#closeMenu").click();
    await page.waitForFunction(() => !document.querySelector("#mobileMenu")?.classList.contains("active"));
  }

  await page.locator(".view-recipe").first().click();
  await page.waitForSelector("#recipeModal.active .modal-box", { timeout: 5000 });
  const modal = await page.evaluate(() => {
    const box = document.querySelector("#recipeModal.active .modal-box");
    const close = document.querySelector("#modalClose");
    const rect = box.getBoundingClientRect();
    const closeRect = close.getBoundingClientRect();
    return {
      left: rect.left,
      right: rect.right,
      top: rect.top,
      bottom: rect.bottom,
      viewportW: window.innerWidth,
      viewportH: window.innerHeight,
      closeW: closeRect.width,
      closeH: closeRect.height,
      bodyLocked: document.body.classList.contains("no-scroll"),
    };
  });
  if (modal.left < -2 || modal.right > modal.viewportW + 2 || modal.top < -2 || modal.bottom > modal.viewportH + 2 || !modal.bodyLocked) {
    failures.push(`home @ ${width}px: Quick View modal exceeds viewport or does not lock body: ${JSON.stringify(modal)}`);
  }
  if (modal.closeW < 40 || modal.closeH < 40) {
    failures.push(`home @ ${width}px: modal close control is too small: ${modal.closeW}x${modal.closeH}`);
  }
  await page.locator("#modalClose").click();
  await page.waitForFunction(() => !document.querySelector("#recipeModal")?.classList.contains("active"));
}

for (const width of widths) {
  await page.setViewportSize({ width, height: 920 });

  for (const [label, path] of pages) {
    const before = failures.length;
    const response = await page.goto(base + path, { waitUntil: "domcontentloaded", timeout: 30000 });
    if (!response || !response.ok()) {
      failures.push(`${label} @ ${width}px: HTTP ${response?.status() || "no response"}`);
      continue;
    }

    await page.waitForTimeout(350);
    if (label === "home") {
      await page.waitForFunction(() => document.querySelectorAll(".recipe-card").length >= 60, null, { timeout: 15000 });
      await testHomeInteractions(width);
    }

    await scrollThrough();
    await settleImages();
    const report = await inspectLayout(label, width);
    results.push({ label, width, ...report, failuresAdded: failures.length - before });

    await page.screenshot({
      path: `qa-screenshots/${label}-${width}.png`,
      fullPage: false,
    });
  }
}

await browser.close();

console.log("MOBILE BROWSER QA");
for (const r of results) {
  console.log(`- ${r.label} @ ${r.width}px: overflow=${r.overflow}px, brokenImages=${r.broken.length}, placeholders=${r.placeholders.length}, h1=${JSON.stringify(r.h1Text)}, failures=${r.failuresAdded}`);
}

if (failures.length) {
  console.error("\nFAILURES");
  for (const failure of [...new Set(failures)]) console.error("- " + failure);
  process.exit(1);
}

console.log(`\nPassed ${results.length} viewport/page combinations across ${widths.join(", ")}px widths.`);
