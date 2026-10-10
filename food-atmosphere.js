/* Pakistan Food — photo-anchored food steam pilot · 2026-10-10
 * A deliberately limited pilot: the featured Biryani photograph only.
 * No steam on tables, composite plates, unrelated cards or food-page crops.
 * Small original canvas smoke sprites (not SVG waves, GIFs or new assets).
 * 15fps max; paused outside viewport, in background and for reduced motion. */
(() => {
  "use strict";

  const SELECTOR = '.featured-card:first-child .pf-food-photo[data-pf-dish="chicken-biryani"]';
  const FPS_MS = 66;
  const cloudCount = 21;
  const motion = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  const element = document.querySelector(SELECTOR);
  if (!element || element.dataset.pfAtmosphereReady) return;

  // Never create an overlay without an intentionally calibrated crop.
  element.dataset.pfAtmosphereReady = "biryani-canvas";
  const canvas = document.createElement("canvas");
  canvas.className = "pf-steam-canvas";
  canvas.setAttribute("aria-hidden", "true");
  element.appendChild(canvas);

  const ctx = canvas.getContext("2d", {alpha:true});
  if (!ctx) {canvas.remove();return;}
  const sprite = document.createElement("canvas");
  sprite.width = 104;
  sprite.height = 132;
  const sc = sprite.getContext("2d");
  if (!sc) {canvas.remove();return;}
  // Overlapping softly feathered irregular plumes: no stroked lines.
  const lobes = [
    [48,103,33,[176,181,167],.34],
    [63,74,37,[245,244,228],.42],
    [39,55,35,[193,200,190],.34],
    [58,30,29,[247,244,228],.28],
  ];
  for (const [x,y,rgbRadius,rgb,opacity] of lobes) {
    const g=sc.createRadialGradient(x,y,0,x,y,rgbRadius);
    g.addColorStop(0,`rgba(${rgb.join(",")},${opacity})`);
    g.addColorStop(.25,`rgba(${rgb.join(",")},${opacity*.65})`);
    g.addColorStop(.68,`rgba(${rgb.join(",")},${opacity*.18})`);
    g.addColorStop(1,`rgba(${rgb.join(",")},0)`);
    sc.fillStyle=g;sc.fillRect(x-rgbRadius,y-rgbRadius,rgbRadius*2,rgbRadius*2);
  }

  // Frame content is cropped consistently in featured-card; origin y .35 is
  // INSIDE the heaped rice, not over the exposed white plate or table.
  const emitters = [
    {x:.39,y:.355,seed:.2},
    {x:.52,y:.315,seed:1.6},
    {x:.59,y:.365,seed:2.7},
  ];
  const particles=Array.from({length:cloudCount},(_,i)=>({
    initial:i/cloudCount,
    seed:Math.sin(i*78.233)*43758.5453,
    emitter:emitters[i%emitters.length],
    lifespan:4.6+(i%6)*.3,
  }));
  const fract=x=>x-Math.floor(x);
  let width=0,height=0,scale=1;
  let visible=false,lastPaint=0,raf=0,started=performance.now();

  function userAllowsMotion(){
    let choice=null;
    try {
      const params=new URLSearchParams(location.search);
      if(params.get("food-motion")==="on"){
        localStorage.setItem("pfFoodMotionEnabled","yes");
      } else if(params.get("food-motion")==="off") {
        localStorage.setItem("pfFoodMotionEnabled","no");
      }
      choice=localStorage.getItem("pfFoodMotionEnabled");
      if(choice===null && localStorage.getItem("pfFoodMotionPreference")==="on") choice="yes";
    }catch(_){}
    return choice==="yes" || (choice!=="no" && !(motion&&motion.matches));
  }
  function fit(){
    const r=element.getBoundingClientRect();
    width=Math.round(r.width);
    height=Math.round(r.height);
    if(width<20||height<20)return;
    scale=Math.min(devicePixelRatio||1,1.3);
    canvas.width=Math.round(width*scale);
    canvas.height=Math.round(height*scale);
    ctx.setTransform(scale,0,0,scale,0,0);
  }
  function paint(now){
    raf=0;
    if(!visible||document.hidden||!userAllowsMotion())return;
    raf=requestAnimationFrame(paint);
    if(now-lastPaint<FPS_MS)return;
    lastPaint=now;
    if(width<20||height<20)return;
    ctx.clearRect(0,0,width,height);
    const elapsed=(now-started)/1000;
    const maxRise=height*.33;
    for(const p of particles){
      const phase=fract((elapsed/p.lifespan)+p.initial);
      const random=fract(p.seed);
      // Feathered fade at birth and dissipation, never opaque flat clouds.
      const lifeFade=Math.pow(Math.sin(Math.PI*phase),1.25);
      const x=width*(p.emitter.x+(.036*(random-.5)))+
        Math.sin(phase*5.8+p.emitter.seed+random*7)*width*.014;
      const y=height*p.emitter.y-phase*maxRise;
      const size=Math.min(width*.13,56)*(0.55+phase*.75)*(0.75+random*.40);
      // The photo beneath remains readable: overlapping fine vapor wisps.
      ctx.globalAlpha=.52*lifeFade;
      ctx.drawImage(sprite,x-size*.5,y-size*1.25,size,size*1.45);
    }
    ctx.globalAlpha=1;
  }
  function refresh(){
    const canRun=visible&&!document.hidden&&userAllowsMotion();
    canvas.style.display=canRun?"block":"none";
    if(canRun){if(!raf)raf=requestAnimationFrame(paint);}
    else {
      if(raf)cancelAnimationFrame(raf);
      raf=0;
      ctx.clearRect(0,0,width,height);
    }
  }
  fit();
  const resize="ResizeObserver" in window ? new ResizeObserver(()=>{fit();refresh();}) : null;
  if(resize)resize.observe(element);
  else addEventListener("resize",()=>{fit();refresh();},{passive:true});
  if("IntersectionObserver" in window){
    const view=new IntersectionObserver(entries=>{
      visible=entries[0].isIntersecting;refresh();
    },{rootMargin:"24px 0px",threshold:.02});
    view.observe(element);
  } else {visible=true;refresh();}
  document.addEventListener("visibilitychange",refresh,{passive:true});
  if(motion){
    if(motion.addEventListener)motion.addEventListener("change",refresh);
    else if(motion.addListener)motion.addListener(refresh);
  }
})();
