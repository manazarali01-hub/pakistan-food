#!/usr/bin/env python3
from __future__ import annotations
from collections import Counter
from html import unescape
from pathlib import Path
import json, math, re

ROOT=Path(__file__).resolve().parents[1]
GUIDES=ROOT/"guides"
OUT=ROOT/"docs"/"search-intent-overlap-2026-10-04.json"
STOP=set("""how to why is are does do the a an of for in on with without and or your you pakistani pakistan food recipe recipes guide best what when use make keep get too from at home cooking""".split())

def robots(html):
    m=re.search(r'<meta\s+[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)',html,re.I)
    if not m: m=re.search(r'<meta\s+[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']robots["\']',html,re.I)
    return (m.group(1).lower() if m else "index,follow")

def text_only(html):
    html=re.sub(r'<script\b[^>]*>[\s\S]*?</script>',' ',html,flags=re.I)
    html=re.sub(r'<style\b[^>]*>[\s\S]*?</style>',' ',html,flags=re.I)
    html=re.sub(r'<[^>]+>',' ',html)
    return re.sub(r'\s+',' ',unescape(html)).strip()

def title_of(html,path):
    m=re.search(r'<title>(.*?)</title>',html,re.I|re.S)
    return re.sub(r'\s+',' ',unescape(m.group(1))).replace('| Pakistan Food','').strip() if m else path.stem

def tokens(s):
    vals=re.findall(r"[a-z0-9]+",s.lower())
    return [v for v in vals if len(v)>2 and v not in STOP]

rows=[]
for p in sorted(GUIDES.glob("*.html")):
    if p.name=="index.html": continue
    h=p.read_text(encoding="utf-8")
    if "noindex" in robots(h): continue
    title=title_of(h,p)
    visible=text_only(h)
    rows.append({"file":p.name,"title":title,"words":len(visible.split()),"title_tokens":sorted(set(tokens(title))),"body_tokens":tokens(visible)})

# IDF from indexed bodies, downweight generic site terms.
df=Counter()
for r in rows:
    df.update(set(r["body_tokens"]))
N=max(1,len(rows))

def weighted_set(r):
    counts=Counter(r["body_tokens"])
    return {t:(1+math.log(c))*math.log((N+1)/(df[t]+1)) for t,c in counts.items() if df[t] <= N*0.55}

weights={r["file"]:weighted_set(r) for r in rows}

def cosine(a,b):
    common=set(a)&set(b)
    dot=sum(a[t]*b[t] for t in common)
    na=math.sqrt(sum(v*v for v in a.values())); nb=math.sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na and nb else 0

def jaccard(a,b):
    a=set(a); b=set(b)
    return len(a&b)/len(a|b) if a or b else 0

pairs=[]
for i,a in enumerate(rows):
    for b in rows[i+1:]:
        tj=jaccard(a["title_tokens"],b["title_tokens"])
        bc=cosine(weights[a["file"]],weights[b["file"]])
        # Emphasize title-level intent collision; body cosine catches near-duplicate support pages.
        score=0.62*tj+0.38*bc
        if score>=0.30 or tj>=0.40 or bc>=0.60:
            pairs.append({
              "a":a["file"],"a_title":a["title"],"a_words":a["words"],
              "b":b["file"],"b_title":b["title"],"b_words":b["words"],
              "title_jaccard":round(tj,3),"body_cosine":round(bc,3),"score":round(score,3)
            })
pairs.sort(key=lambda x:(-x["score"],-x["title_jaccard"],-x["body_cosine"],x["a"]))
report={
 "indexed_guides":len(rows),
 "candidate_pairs":len(pairs),
 "top_pairs":pairs[:120],
 "method":"Title-token Jaccard plus IDF-weighted body cosine. Report only; human review required before noindex/consolidation."
}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"indexed_guides":len(rows),"candidate_pairs":len(pairs),"top":pairs[:20]},indent=2))
