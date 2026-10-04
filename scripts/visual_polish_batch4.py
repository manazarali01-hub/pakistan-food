#!/usr/bin/env python3
import io, json, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
RECIPES=ROOT/"_data"/"recipes"
CONFIG=ROOT/"_config.yml"
REPORT=ROOT/"docs"/"visual-polish-batch4-2026-10-04.json"
UA="PakistanFoodVisualPolish/4.0 (+https://pakistanfoodrecipes.top/)"

SOURCES={
  "chicken-biryani":{
    "filename":"Lahori Biryani.jpg",
    "source":"https://commons.wikimedia.org/wiki/File:Lahori_Biryani.jpg",
    "author":"Muhammad Umair Mirza","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
    "out":"assets/recipe-images/chicken-biryani-v2.webp",
    "zoom":0.76,"fx":0.50,"fy":0.49,
    "alt":"Pakistani chicken biryani with long basmati rice, spiced chicken and fried onion",
    "caption":"Chicken biryani with long basmati rice and spiced chicken in a tighter food-first crop."
  },
  "chicken-qorma":{
    "filename":"Chicken Korma.JPG",
    "source":"https://commons.wikimedia.org/wiki/File:Chicken_Korma.JPG",
    "author":"Miansari66","license":"CC0 1.0",
    "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
    "out":"assets/recipe-images/chicken-qorma-v2.webp",
    "zoom":0.72,"fx":0.50,"fy":0.50,
    "alt":"Pakistani chicken qorma with chicken pieces in a rich red-brown gravy",
    "caption":"Chicken qorma with tender chicken pieces in a rich reduced gravy."
  },
  "mutton-karahi":{
    "filename":"Mutton Karahi 2.JPG",
    "source":"https://commons.wikimedia.org/wiki/File:Mutton_Karahi_2.JPG",
    "author":"Miansari66","license":"CC0 1.0",
    "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
    "out":"assets/recipe-images/mutton-karahi-v2.webp",
    "zoom":0.76,"fx":0.50,"fy":0.50,
    "alt":"Pakistani mutton karahi with tender bone-in meat, tomato masala, ginger and green chilli",
    "caption":"Mutton karahi with bone-in meat in concentrated tomato masala, ginger and green chilli."
  },
  "reshmi-kabab":{
    "filename":"Chicken reshmi kebabs.jpg",
    "source":"https://commons.wikimedia.org/wiki/File:Chicken_reshmi_kebabs.jpg",
    "author":"Prianxi","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
    "out":"assets/recipe-images/reshmi-kabab-v2.webp",
    "zoom":0.80,"fx":0.50,"fy":0.50,
    "alt":"Chicken reshmi kababs grilled until lightly browned and served hot",
    "caption":"Reshmi kababs grilled until lightly browned with a soft juicy centre."
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
    if im.mode!="RGB":
        im=im.convert("RGB")
    return im

def crop43(im,zoom,fx,fy):
    w,h=im.size
    target=4/3
    if w/h>=target:
        bh=h; bw=round(h*target)
    else:
        bw=w; bh=round(w/target)
    zoom=max(.55,min(1.0,float(zoom)))
    cw=max(4,int(bw*zoom)); ch=max(3,int(bh*zoom))
    if cw/ch>target: cw=round(ch*target)
    else: ch=round(cw/target)
    cx=round(w*fx); cy=round(h*fy)
    left=max(0,min(w-cw,cx-cw//2)); top=max(0,min(h-ch,cy-ch//2))
    out=im.crop((left,top,left+cw,top+ch))
    out=out.resize((1200,900),Image.Resampling.LANCZOS)
    out=ImageEnhance.Contrast(out).enhance(1.04)
    return out

def save_webp(im,rel):
    p=ROOT/rel
    p.parent.mkdir(parents=True,exist_ok=True)
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

def bump_cache():
    txt=CONFIG.read_text(encoding="utf-8")
    txt,n=re.subn(r'^recipe_image_version:\s*["\']?[^"\'\s]+["\']?','recipe_image_version: "20261004-final8"',txt,count=1,flags=re.M)
    if n!=1: raise RuntimeError("recipe_image_version not found")
    CONFIG.write_text(txt,encoding="utf-8")

def main():
    results=[]
    for slug,meta in SOURCES.items():
        raw,resolved,ctype=fetch_commons(meta["filename"])
        im=crop43(open_rgb(raw),meta["zoom"],meta["fx"],meta["fy"])
        info=save_webp(im,meta["out"])
        if (info["width"],info["height"])!=(1200,900):
            raise RuntimeError(f"{slug}: incorrect dimensions")
        if info["bytes"]<25000:
            raise RuntimeError(f"{slug}: suspiciously small output")
        update_recipe(slug,meta)
        results.append({"slug":slug,"resolved":resolved,"content_type":ctype,**info})
    bump_cache()
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "policy":"Real openly licensed food photography only.",
        "cache_version":"20261004-final8",
        "changed":[x["slug"] for x in results],
        "results":results
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(results,indent=2))
    print("OK visual polish batch 4")

if __name__=="__main__":
    main()
