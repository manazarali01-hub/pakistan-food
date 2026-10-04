#!/usr/bin/env python3
import io, json, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
RECIPES=ROOT/"_data"/"recipes"
CONFIG=ROOT/"_config.yml"
REPORT=ROOT/"docs"/"visual-polish-batch5-2026-10-04.json"
UA="PakistanFoodVisualPolish/5.0 (+https://pakistanfoodrecipes.top/)"

SOURCES={
  "bun-kabab":{
    "filename":"Bun Kabab.JPG",
    "source":"https://commons.wikimedia.org/wiki/File:Bun_Kabab.JPG",
    "author":"LunaticFringe97","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
    "out":"assets/recipe-images/bun-kabab-v2.webp",
    "zoom":0.94,"fx":0.50,"fy":0.50,
    "alt":"Pakistani bun kabab with a spicy kabab patty, chutney and toasted bun",
    "caption":"Pakistani street-style bun kabab with kabab filling and chutney in a toasted bun."
  },
  "chana-chaat":{
    "filename":"Healthy Channa Special.jpg",
    "source":"https://commons.wikimedia.org/wiki/File:Healthy_Channa_Special.jpg",
    "author":"ThamsSelvi","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
    "out":"assets/recipe-images/chana-chaat-v2.webp",
    "zoom":0.82,"fx":0.50,"fy":0.52,
    "alt":"Pakistani chana chaat with chickpeas, tomato, onion, coriander and tangy seasoning",
    "caption":"Chana chaat with boiled chickpeas, tomato, onion and coriander in a tangy masala."
  },
  "fruit-chaat":{
    "filename":"Fruit chaat.JPG",
    "source":"https://commons.wikimedia.org/wiki/File:Fruit_chaat.JPG",
    "author":"Milanography","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
    "out":"assets/recipe-images/fruit-chaat-v2.webp",
    "zoom":0.78,"fx":0.50,"fy":0.50,
    "alt":"Fresh mixed fruit chaat with colorful fruit pieces and crunchy dry fruits",
    "caption":"Fresh mixed fruit chaat with colorful fruit pieces and a crunchy dry-fruit topping."
  },
  "chicken-shawarma":{
    "filename":"Chicken Shawarma.jpg",
    "source":"https://commons.wikimedia.org/wiki/File:Chicken_Shawarma.jpg",
    "author":"Zebaarts","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
    "out":"assets/recipe-images/chicken-shawarma-v2.webp",
    "zoom":0.84,"fx":0.56,"fy":0.52,
    "alt":"Chicken shawarma with browned spiced chicken, flatbread, vegetables and sauce",
    "caption":"Chicken shawarma with browned spiced chicken, flatbread, crisp vegetables and sauce."
  }
}

def fetch_commons(filename):
    url="https://commons.wikimedia.org/wiki/Special:FilePath/"+urllib.parse.quote(filename)+"?width=1800"
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
    with urllib.request.urlopen(req,timeout=60) as r:
        raw=r.read()
        if not raw:
            raise RuntimeError(f"empty response for {filename}")
        return raw,r.geturl(),r.headers.get("Content-Type","")

def open_rgb(raw):
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))
    return im.convert("RGB") if im.mode!="RGB" else im

def crop43(im,zoom,fx,fy):
    w,h=im.size; target=4/3
    if w/h>=target:
        bh=h; bw=round(h*target)
    else:
        bw=w; bh=round(w/target)
    zoom=max(.60,min(1.0,float(zoom)))
    cw=max(4,int(bw*zoom)); ch=max(3,int(bh*zoom))
    if cw/ch>target: cw=round(ch*target)
    else: ch=round(cw/target)
    cx=round(w*fx); cy=round(h*fy)
    left=max(0,min(w-cw,cx-cw//2)); top=max(0,min(h-ch,cy-ch//2))
    out=im.crop((left,top,left+cw,top+ch))
    out=out.resize((1200,900),Image.Resampling.LANCZOS)
    out=ImageEnhance.Contrast(out).enhance(1.04)
    out=ImageEnhance.Sharpness(out).enhance(1.06)
    return out

def save_webp(im,rel):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    im.save(p,"WEBP",quality=88,method=6)
    with Image.open(p) as chk: chk.verify()
    return {"width":im.width,"height":im.height,"bytes":p.stat().st_size}

def update_recipe(slug,meta):
    p=RECIPES/f"{slug}.json"
    data=json.loads(p.read_text(encoding="utf-8"))
    data["image"]=meta["out"]
    data["image_alt"]=meta["alt"]
    data["image_caption"]=meta["caption"]
    data["image_source"]=meta["source"]
    data["image_author"]=meta["author"]
    data["image_creator"]=meta["author"]
    data["image_license"]=meta["license"]
    data["image_license_url"]=meta["license_url"]
    data["image_source_label"]="Wikimedia Commons"
    data["date_modified"]="2026-10-04"
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    results=[]
    for slug,meta in SOURCES.items():
        raw,resolved,ctype=fetch_commons(meta["filename"])
        im=crop43(open_rgb(raw),meta["zoom"],meta["fx"],meta["fy"])
        info=save_webp(im,meta["out"])
        if (info["width"],info["height"])!=(1200,900): raise RuntimeError(f"{slug}: bad dimensions")
        if info["bytes"]<25000: raise RuntimeError(f"{slug}: suspiciously small output")
        update_recipe(slug,meta)
        results.append({"slug":slug,"resolved":resolved,"content_type":ctype,**info})

    txt=CONFIG.read_text(encoding="utf-8")
    txt,n=re.subn(r'^recipe_image_version:\s*["\']?[^"\'\s]+["\']?','recipe_image_version: "20261004-final9"',txt,count=1,flags=re.M)
    if n!=1: raise RuntimeError("recipe_image_version not found")
    CONFIG.write_text(txt,encoding="utf-8")

    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
      "policy":"Real openly licensed food photography only.",
      "cache_version":"20261004-final9",
      "changed":[x["slug"] for x in results],
      "results":results
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(results,indent=2))
    print("OK visual polish batch 5")

if __name__=="__main__": main()
