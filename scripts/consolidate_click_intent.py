#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
GUIDES=ROOT/"guides"
SITEMAP=ROOT/"sitemap-v2.xml"

MAP={
  "how-to-skewer-kabab-without-falling.html": ("seekh-kabab-not-sticking.html","How to Stop Seekh Kabab from Falling Off the Skewer"),
  "why-roti-gets-hard-after-cooling.html": ("how-to-keep-roti-soft.html","How to Keep Roti Soft After Cooking"),
  "why-gulab-jamun-gets-hard.html": ("how-to-make-gulab-jamun-soft.html","How to Make Gulab Jamun Soft, Not Hard"),
  "why-chai-is-too-strong.html": ("how-to-make-strong-chai-without-bitterness.html","How to Make Strong Chai Without Bitterness"),
  "how-to-drain-fried-food.html": ("why-fried-food-gets-soggy.html","Why Fried Food Gets Soggy and How to Fix It"),
}

def set_noindex(html):
    p1=r'(<meta\s+[^>]*name=["\']robots["\'][^>]*content=["\'])[^"\']+(["\'])'
    p2=r'(<meta\s+[^>]*content=["\'])[^"\']+(["\'][^>]*name=["\']robots["\'])'
    if re.search(p1,html,re.I):
        return re.sub(p1,r'\1noindex,follow\2',html,count=1,flags=re.I)
    if re.search(p2,html,re.I):
        return re.sub(p2,r'\1noindex,follow\2',html,count=1,flags=re.I)
    return html.replace("</head>",'  <meta name="robots" content="noindex,follow">\n</head>',1)

changed=[]
for source,(target,label) in MAP.items():
    p=GUIDES/source
    html=p.read_text(encoding="utf-8")
    new=set_noindex(html)
    marker='data-intent-consolidated="true"'
    if marker not in new:
        note=(
          f'\n<section class="guide-handoff" {marker}>'
          f'<h2>Use the stronger guide</h2>'
          f'<p>This narrow topic is now covered more completely in '
          f'<a href="{target}">{label}</a>. The original page remains available for existing links, '
          f'but the fuller guide is the recommended resource.</p></section>\n'
        )
        if "</main>" in new:
            new=new.replace("</main>",note+"</main>",1)
        else:
            new=new.replace("</body>",note+"</body>",1)
    if new!=html:
        p.write_text(new,encoding="utf-8")
        changed.append(str(p.relative_to(ROOT)))

# Replace public/internal links outside the consolidated source itself.
for p in ROOT.rglob("*.html"):
    rel=str(p.relative_to(ROOT))
    text=p.read_text(encoding="utf-8")
    new=text
    for source,(target,_) in MAP.items():
        if rel == f"guides/{source}":
            continue
        new=new.replace(source,target)
    if new!=text:
        p.write_text(new,encoding="utf-8")
        changed.append(rel)

# Remove consolidated pages from canonical sitemap.
s=SITEMAP.read_text(encoding="utf-8")
for source in MAP:
    pattern=r'\s*<url>\s*<loc>https://pakistanfoodrecipes\.top/guides/'+re.escape(source)+r'</loc>[\s\S]*?</url>'
    s,n=re.subn(pattern,"",s,count=1)
    if n!=1:
        raise SystemExit(f"Expected exactly one sitemap entry for {source}, removed {n}")
SITEMAP.write_text(s,encoding="utf-8")
changed.append(str(SITEMAP.relative_to(ROOT)))

# Verify selected pages are noindex and sitemap-free.
s=SITEMAP.read_text(encoding="utf-8")
for source,(target,_) in MAP.items():
    html=(GUIDES/source).read_text(encoding="utf-8")
    if "noindex,follow" not in html:
        raise SystemExit(f"{source}: noindex not applied")
    if source in s:
        raise SystemExit(f"{source}: still present in sitemap")
    if target not in html:
        raise SystemExit(f"{source}: target handoff missing")

print("CLICK-FOCUSED INTENT CONSOLIDATION")
print(f"Consolidated micro-guides: {len(MAP)}")
for source,(target,_) in MAP.items():
    print(f"- {source} -> {target}")
print(f"Changed source files: {len(set(changed))}")
