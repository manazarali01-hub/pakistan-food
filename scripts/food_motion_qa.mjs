import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const base=process.env.QA_BASE_URL||'http://127.0.0.1:4173';
fs.mkdirSync('qa-screenshots',{recursive:true});
const browser=await chromium.launch();
const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'no-preference',recordVideo:{dir:'qa-screenshots/motion-video',size:{width:390,height:844}}});
await context.route(/googlesyndication|doubleclick|googleadservices/,r=>r.abort());
const page=await context.newPage();
const errors=[];page.on('pageerror',e=>errors.push(e.message));
const sample=()=>page.locator('.featured-card .pf-wisp').first().evaluate(e=>({transform:getComputedStyle(e).transform,opacity:getComputedStyle(e).opacity,animations:e.getAnimations().map(a=>a.playState)}));
try {
 for(const width of [320,360,390,430,768,1280]) {
  await page.setViewportSize({width,height:844});
  await page.goto(base+'/',{waitUntil:'networkidle'});
  await page.locator('.featured-card').first().scrollIntoViewIfNeeded();
  await page.waitForTimeout(600);
  assert.equal(await page.locator('#pfMotionToggle').getAttribute('aria-pressed'),'true');
  const layer=page.locator('.featured-card .pf-food-atmosphere').first();
  await layer.waitFor({state:'visible'});
  const a=await sample();await page.waitForTimeout(700);const b=await sample();
  assert.notEqual(a.transform,b.transform,`actual movement ${width}`);
  assert.notEqual(a.opacity,b.opacity,`actual fading ${width}`);
  assert(a.animations.includes('running'));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),`overflow ${width}`);
  assert(await layer.evaluate(e=>getComputedStyle(e).pointerEvents==='none'));
  assert(await page.locator('.pf-motion-running').count()<=4);
  await page.screenshot({path:`qa-screenshots/food-motion-${width}.png`});
  console.log(`PASS ${width}px touch: visible motion, fade, budget, no overflow`);
 }
 await page.setViewportSize({width:390,height:844});
 await page.locator('#pfMotionToggle').click();
 assert.equal(await page.locator('#pfMotionToggle').getAttribute('aria-pressed'),'false');
 assert.deepEqual((await sample()).animations,[]);
 await page.locator('#pfMotionToggle').click();await page.locator('.featured-card').first().scrollIntoViewIfNeeded();await page.waitForTimeout(500);
 assert((await sample()).animations.includes('running'));
 await page.emulateMedia({reducedMotion:'reduce'});await page.waitForTimeout(100);
 assert.deepEqual((await sample()).animations,[]);
 await page.locator('#pfMotionToggle').click();await page.locator('.featured-card').first().scrollIntoViewIfNeeded();await page.waitForTimeout(500);
 assert((await sample()).animations.includes('running'));
 await page.emulateMedia({reducedMotion:'no-preference'});
 const wisp=page.locator('.featured-card .pf-wisp').first();
 const direction=await wisp.evaluate(e=>{const a=e.getAnimations()[0];a.pause();a.currentTime=2500;const y1=new DOMMatrix(getComputedStyle(e).transform).m42;a.currentTime=5500;const y2=new DOMMatrix(getComputedStyle(e).transform).m42;return y2<y1;});
 assert(direction,'steam moves upward');
 await page.evaluate(()=>document.body.classList.add('dark'));
 await page.screenshot({path:'qa-screenshots/food-motion-dark.png'});
 assert.equal(await page.locator('.featured-card[href*="mango-lassi"] .pf-steam').count(),0);
 assert.equal(await page.locator('.featured-card[href*="mango-lassi"] .pf-fresh').count(),1);
 await page.locator('.featured-card').first().click();
 await page.waitForURL('**/chicken-biryani.html');
 await page.locator('picture .pf-steam').waitFor({state:'visible'});
 assert.equal(await page.locator('link[rel="canonical"]').getAttribute('href'),'https://pakistanfoodrecipes.top/recipes/chicken-biryani.html');
 for(const [slug,type] of [['kashmiri-chai','steam'],['doodh-patti-chai','steam'],['masala-chai','steam'],['chapli-kabab','heat'],['chicken-sajji','heat'],['mango-lassi','fresh'],['sweet-lassi','fresh'],['namkeen-lassi','fresh'],['rice-kheer','light']]) {
   await page.goto(base+'/recipes/'+slug+'.html',{waitUntil:'domcontentloaded'});
   await page.locator('picture .pf-'+type).waitFor({state:'attached'});
 }
 assert.deepEqual(errors,[]);
 console.log('PASS pause/resume, reduced motion, explicit preview, upward steam, dark theme, cold drink safety, recipe navigation, dish mapping, canonical and no JS errors');
} finally {await context.close();await browser.close();}
