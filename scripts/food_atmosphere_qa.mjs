import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const base=process.env.QA_BASE_URL||'http://127.0.0.1:4173';
fs.mkdirSync('qa-screenshots',{recursive:true});
const browser=await chromium.launch();
const errors=[];
const blockAds=context=>context.route(/googlesyndication|doubleclick|googleadservices/,route=>route.abort());

async function openHome(context,width){
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(error.message));
  await page.setViewportSize({width,height:844});
  await page.goto(base+'/',{waitUntil:'domcontentloaded'});
  const photo=page.locator('.featured-card:first-child .pf-food-photo[data-pf-dish="chicken-biryani"]');
  await photo.scrollIntoViewIfNeeded();
  const canvas=photo.locator('canvas.pf-steam-canvas');
  await canvas.waitFor({state:'attached'});
  await page.waitForFunction(()=>{
    const c=document.querySelector('.featured-card:first-child .pf-food-photo[data-pf-dish="chicken-biryani"] canvas.pf-steam-canvas');
    return c&&c.width>0&&c.height>0;
  });
  return {page,photo,canvas};
}

try {
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'no-preference'});
  await blockAds(context);
  for(const width of [320,360,390,430,768,1280]){
    const {page,photo,canvas}=await openHome(context,width);
    await page.waitForFunction(()=>{
      const c=document.querySelector('.featured-card:first-child .pf-food-photo[data-pf-dish="chicken-biryani"] canvas.pf-steam-canvas');
      return c&&getComputedStyle(c).display==='block';
    });
    await page.waitForTimeout(180);
    const first=await canvas.evaluate(c=>c.toDataURL());
    await page.waitForTimeout(350);
    const second=await canvas.evaluate(c=>c.toDataURL());
    assert.notEqual(first,second,`canvas pixels change over time at ${width}px`);
    assert.equal(await canvas.evaluate(c=>getComputedStyle(c).pointerEvents),'none');
    assert.equal(await photo.getAttribute('data-pf-dish'),'chicken-biryani');
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),`horizontal overflow at ${width}px`);
    if(width===390)await page.screenshot({path:'qa-screenshots/food-atmosphere-390.png',fullPage:false});
    console.log(`PASS ${width}px: visible canvas, changing pixels, no tap interception or overflow`);
    await page.close();
  }
  const reduced=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  await blockAds(reduced);
  const reducedPage=await reduced.newPage();
  reducedPage.on('pageerror',error=>errors.push(error.message));
  await reducedPage.goto(base+'/',{waitUntil:'domcontentloaded'});
  await reducedPage.locator('.featured-card:first-child .pf-food-photo[data-pf-dish="chicken-biryani"]').scrollIntoViewIfNeeded();
  await reducedPage.locator('canvas.pf-steam-canvas').waitFor({state:'attached'});
  await reducedPage.waitForTimeout(180);
  assert.equal(await reducedPage.locator('canvas.pf-steam-canvas').evaluate(c=>getComputedStyle(c).display),'none','reduced-motion preference keeps steam static');
  await reduced.close();

  const paused=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'no-preference'});
  await blockAds(paused);
  const pausedPage=await paused.newPage();
  pausedPage.on('pageerror',error=>errors.push(error.message));
  await pausedPage.goto(base+'/?food-motion=off',{waitUntil:'domcontentloaded'});
  await pausedPage.locator('.featured-card:first-child .pf-food-photo[data-pf-dish="chicken-biryani"]').scrollIntoViewIfNeeded();
  await pausedPage.locator('canvas.pf-steam-canvas').waitFor({state:'attached'});
  await pausedPage.waitForTimeout(150);
  assert.equal(await pausedPage.locator('canvas.pf-steam-canvas').evaluate(c=>getComputedStyle(c).display),'none','explicit off preference pauses steam');
  await pausedPage.goto(base+'/recipes/chicken-biryani.html',{waitUntil:'domcontentloaded'});
  assert.equal(await pausedPage.locator('canvas.pf-steam-canvas').count(),0,'pilot remains limited to the calibrated homepage biryani photo');
  assert.deepEqual(errors,[]);
  console.log('PASS reduced motion, explicit pause, limited photo scope, and no browser errors');
  await paused.close();
  await context.close();
} finally {
  await browser.close();
}
