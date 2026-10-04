#!/usr/bin/env python3
import io, json, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
RECIPES=ROOT/"_data"/"recipes"
CONFIG=ROOT/"_config.yml"
REPORT=ROOT/"docs"/"visual-polish-batch2-2026-10-04.json"
UA="PakistanFoodVisualPolish/2.0 (+https://pakistanfoodrecipes.top/)"

SOURCES={
  "aloo-paratha":{
    "filename": '"Amazing Aloo Paratha and Lovely Lassi".jpg',
    "source":"https://commons.wikimedia.org/wiki/File:%22Amazing_Aloo_Paratha_and_Lovely_Lassi%22.jpg",
    "author":"Mahi Tatavarty","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
    "out":"assets/recipe-images/aloo-paratha-v2.webp",
    "zoom":0.82,"fx":0.39,"fy":0.57,
    "alt":"Golden Punjabi-style aloo parathas with butter, green chilli and lassi",
    "caption":"Golden aloo parathas served with butter, green chilli and traditional lassi."
  },
  "anda-paratha":{
    "filename":"FreshFarm Omlette with Parathas.jpg",
    "source":"https://commons.wikimedia.org/wiki/File:FreshFarm_Omlette_with_Parathas.jpg",
    "author":"Sar8b","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
    "out":"assets/recipe-images/anda-paratha-v2.webp",
    "zoom":0.86,"fx":0.52,"fy":0.55,
    "alt":"Golden parathas served with a fresh onion tomato green chilli omelette",
    "caption":"Golden parathas served beside a freshly cooked masala omelette."
  },
  "bhindi-gosht":{
    "filename":"Bhindi Gosht.JPG",
    "source":"https://commons.wikimedia.org/wiki/File:Bhindi_Gosht.JPG",
    "author":"Miansari66","license":"Public domain",
    "license_url":"https://commons.wikimedia.org/wiki/Commons:Public_domain",
    "out":"assets/recipe-images/bhindi-gosht-v2.webp",
    "zoom":0.76,"fx":0.50,"fy":0.51,
    "alt":"Pakistani bhindi gosht with tender meat and okra in a rich reduced masala",
    "caption":"Bhindi gosht with tender meat and okra in a concentrated onion-tomato masala."
  },
  "kabli-pulao":{
    "filename":"Qabuli palao (rice with carrots & raisins) with lamb - Afghanistan - 04272008.jpg",
    "source":"https://commons.wikimedia.org/wiki/File:Qabuli_palao_(rice_with_carrots_%26_raisins)_with_lamb_-_Afghanistan_-_04272008.jpg",
    "author":"Chen Zhao","license":"CC BY 2.0",
    "license_url":"https://creativecommons.org/licenses/by/2.0/",
    "out":"assets/recipe-images/kabli-pulao-v2.webp",
    "zoom":0.80,"fx":0.53,"fy":0.55,
    "alt":"Kabli pulao with lamb, basmati rice, carrots and raisins",
    "caption":"Kabli pulao with tender lamb, basmati rice, carrots and raisins."
  },
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
    zoom=max(0.60,min(1.0,float(zoom)))
    cw=max(4,int(bw*zoom)); ch=max(3,int(bh*zoom))
    if cw/ch>target: cw=round(ch*target)
    else: ch=round(cw/target)
    cx=round(w*fx); cy=round(h*fy)
    left=max(0,min(w-cw,cx-cw//2)); top=max(0,min(h-ch,cy-ch//2))
    out=im.crop((left,top,left+cw,top+ch))
    fw=min(1400,out.width); fh=round(fw*3/4)
    if fh>out.height:
        fh=out.height; fw=round(fh*4/3)
    if out.size!=(fw,fh):
        out=out.resize((fw,fh),Image.Resampling.LANCZOS)
    # Gentle contrast only; preserve natural food color.
    out=ImageEnhance.Contrast(out).enhance(1.04)
    return out

def save_webp(im,rel):
    p=ROOT/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    im.save(p,"WEBP",quality=88,method=6)
    with Image.open(p) as chk:
        chk.verify()
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
    text=CONFIG.read_text(encoding="utf-8")
    text,n=re.subn(r'^recipe_image_version:\s*["\']?[^"\'\s]+["\']?','recipe_image_version: "20261004-final6"',text,count=1,flags=re.M)
    if n!=1:
        raise RuntimeError("recipe_image_version not found")
    CONFIG.write_text(text,encoding="utf-8")

def main():
    results=[]
    for slug,meta in SOURCES.items():
        raw,resolved,ctype=fetch_commons(meta["filename"])
        im=crop43(open_rgb(raw),meta["zoom"],meta["fx"],meta["fy"])
        info=save_webp(im,meta["out"])
        if info["width"]*3!=info["height"]*4:
            raise RuntimeError(f"{slug}: output is not exact 4:3")
        if info["bytes"]<25000:
            raise RuntimeError(f"{slug}: suspiciously small output {info['bytes']}")
        update_recipe(slug,meta)
        results.append({"slug":slug,"resolved":resolved,"content_type":ctype,**info})
    bump_cache()
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "policy":"Real, openly licensed food photography only.",
        "cache_version":"20261004-final6",
        "changed":[r["slug"] for r in results],
        "results":results
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(results,indent=2))
    print("OK visual polish batch 2")

if __name__=="__main__":
    main()
