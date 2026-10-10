# Natural food atmosphere

The motion system is in `food-motion.js` and the final section of `premium.css`.
It replaces the overlapping October 10 motion patches and inline preview script.
No recipe data, original photographs, licensing metadata, canonicals, structured
data, robots directives or sitemap entries are changed.

## Behaviour

Ordinary motion preference starts automatically. Reduced motion starts static;
Play motion is an explicit temporary preview. A system preference change resets
to that preference. Pause motion disables the decorative system. Hidden tabs and
offscreen surfaces stop; at most four surfaces animate simultaneously. No user
preference is persisted, so a fresh page always respects the operating system.
Without JavaScript, normal content and navigation remain visible.

Steam: chicken biryani, chicken karahi, beef nihari, haleem, halwa puri,
Kashmiri chai, doodh patti chai and masala chai.
Warmth: seekh kabab, chapli kabab, chicken sajji and chicken tikka.
Refreshing light: mango lassi, sweet lassi and namkeen lassi.
Dessert light: jalebi, rice kheer, gulab jamun and ras malai.
Effects appear on matching featured/popular homepage photographs and primary
recipe-page photographs. The discovery grid stays quiet for browsing.

Original SVG strokes and CSS gradients are decorative illustrations, not video
or evidence of cooking. No new third-party art or animation dependencies.

## Verification

`node scripts/food_motion_qa.mjs` runs against a Jekyll server by default;
`QA_BASE_URL=https://pakistanfoodrecipes.top` runs the same checks in production.
It checks six widths (320, 360, 390, 430, 768, 1280), touch contexts, visible
transforms and opacity changing over time, upward travel, pause/resume, reduced
motion and manual preview, dish mapping, recipe navigation and canonical URL.
Screenshots and a WebM recording are saved to `qa-screenshots/` by CI.
The existing mobile and premium interaction suites cover other site controls.
Live Site Smoke waits for the matching Pages deployment before browser checks.

Local recipe/sitemap, recipe content, image and strict guide audits pass. Local
Chromium installation was unavailable; GitHub Actions runs the rendered build
and browser checks. CI results, not this document, determine pass/fail. Touch
emulation does not establish frame rate or battery usage on a physical Android
phone, and no such hardware benchmark is claimed.
