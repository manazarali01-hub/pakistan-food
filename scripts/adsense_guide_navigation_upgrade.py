#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
VERSION = "20261005-adsense1"

HEADER = """<header class="guide-site-header">
  <nav class="guide-site-nav" aria-label="Main navigation">
    <a class="guide-site-brand" href="../">Pakistan Food</a>
    <div class="guide-site-links">
      <a href="../">Home</a>
      <a href="../recipes/">Recipes</a>
      <a href="./">Cooking Guides</a>
      <a href="../about.html">About</a>
      <a href="../contact.html">Contact</a>
    </div>
  </nav>
</header>
<div class="guide-trustline">Published by Pakistan Food · <a href="../editorial-policy.html">Editorial standards</a> · <a href="../contact.html">Report a correction</a></div>
"""

FOOTER = """<footer class="guide-site-footer">
  <p>© 2026 Pakistan Food · <a href="../recipes/">Recipes</a> · <a href="./">Cooking Guides</a> · <a href="../about.html">About</a> · <a href="../privacy-policy.html">Privacy</a> · <a href="../editorial-policy.html">Editorial Policy</a> · <a href="../contact.html">Corrections</a></p>
</footer>
"""

def update_css_versions(text: str) -> str:
    text = re.sub(r'(?:\.\./)?style\.css(?:\?v=[^"\'\s>]+)?', f'../style.css?v={VERSION}', text)
    text = re.sub(r'(?:\.\./)?premium\.css(?:\?v=[^"\'\s>]+)?', f'../premium.css?v={VERSION}', text)
    text = re.sub(r'(?:\.\./)?enhancements\.css(?:\?v=[^"\'\s>]+)?', '../enhancements.css?v=20260924-premium1', text)
    return text

changed=[]
for path in sorted(GUIDES.glob("*.html")):
    text=path.read_text(encoding="utf-8")
    original=text
    text=update_css_versions(text)

    if "premium.css" not in text and "style.css" in text:
        m=re.search(r'<link[^>]+href="\.\./style\.css\?v=[^"]+"[^>]*>', text, flags=re.I)
        if m:
            text=text[:m.end()] + f'\n<link rel="stylesheet" href="../premium.css?v={VERSION}">' + text[m.end():]

    if 'name="theme-color"' not in text:
        text=re.sub(r'(<meta\s+name="viewport"[^>]*>)', r'\1\n<meta name="theme-color" content="#f8f1df">', text, count=1, flags=re.I)
    else:
        text=re.sub(r'<meta\s+name="theme-color"\s+content="[^"]*"\s*/?>', '<meta name="theme-color" content="#f8f1df">', text, count=1, flags=re.I)

    if "guide-site-header" not in text:
        text,n=re.subn(r'<body([^>]*)>', lambda m: '<body'+m.group(1)+'>'+HEADER, text, count=1, flags=re.I)
        if n != 1:
            raise RuntimeError(f"{path}: missing body tag")

    if "guide-site-footer" not in text:
        text,n=re.subn(r'</body>', FOOTER+'</body>', text, count=1, flags=re.I)
        if n != 1:
            raise RuntimeError(f"{path}: missing closing body tag")

    if text != original:
        path.write_text(text,encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

print(f"Updated {len(changed)} guide pages")
for p in changed[:25]:
    print("-",p)
if len(changed)>25:
    print(f"... and {len(changed)-25} more")
