#!/usr/bin/env python3
"""Record of the one-off fixes applied during the audit (kept for traceability; idempotent)."""
import os, re, glob, html
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OG = 'https://namesunlimited.github.io/assets/og-image.png'
def rd(p): return open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)

# A. remove stray duplicate + off-niche page (canonical pointed to another domain)
for f in ('guides/username-reuse-security-riskindex.html.html', 'jpg-to-png.html'):
    if os.path.exists(os.path.join(ROOT, f)): os.remove(os.path.join(ROOT, f))

for p in glob.glob(ROOT + '/**/index.html', recursive=True):
    rel = os.path.relpath(p, ROOT)
    if rel.startswith(('audit', 'node_modules')): continue
    s = rd(rel)
    # B. social metadata
    if 'property="og:title"' not in s:
        t = re.search(r'<title>(.*?)</title>', s, re.S).group(1).strip()
        d = re.search(r'<meta name="description" content="(.*?)">', s, re.S).group(1)
        c = re.search(r'<link rel="canonical" href="(.*?)">', s).group(1)
        blk = (f'  <meta property="og:title" content="{t}">\n  <meta property="og:description" content="{d}">\n'
               f'  <meta property="og:type" content="website">\n  <meta property="og:url" content="{c}">\n'
               f'  <meta property="og:image" content="{OG}">\n')
        s = s.replace('<meta name="robots" content="index, follow">\n', '<meta name="robots" content="index, follow">\n' + blk, 1)
    s = s.replace('content="https://namesunlimited.github.io/favicon.svg"', f'content="{OG}"')
    if 'og:image:width' not in s:
        s = re.sub(r'(<meta property="og:image" content="[^"]+">)', r'\1\n  <meta property="og:image:width" content="1200">\n  <meta property="og:image:height" content="630">\n  <meta property="og:image:alt" content="Names Unlimited: free online name generators">', s, 1)
    if 'twitter:card' not in s:
        s = s.replace('<meta name="theme-color"', f'<meta name="twitter:card" content="summary_large_image">\n  <meta name="twitter:image" content="{OG}">\n  <meta name="theme-color"', 1)
    # C. accessible names for tool inputs
    s = s.replace('<input type="number" min="1" max="5000" value="50" data-count-input>', '<input type="number" min="1" max="5000" value="50" data-count-input aria-label="Number of results to generate">')
    s = s.replace('<input class="search-box" type="search" placeholder="Filter results&hellip;" data-search>', '<input class="search-box" type="search" placeholder="Filter results&hellip;" data-search aria-label="Filter generated results">')
    # D. heading levels (keep visual style, fix exposed outline)
    s = re.sub(r'<h4>(Utility &amp; Mock Tools|Creative &amp; Fiction|Platform &amp; Legal|Utility & Mock Tools|Creative & Fiction|Platform & Legal)</h4>', r'<h4 role="heading" aria-level="2">\1</h4>', s)
    if rel == 'index.html' or rel == 'guides/index.html':
        s = s.replace('<h3>', '<h3 role="heading" aria-level="2">') if rel == 'guides/index.html' else s
    wr(rel, s)

# index: card titles h3 directly under h1 -> expose as level 2
s = rd('index.html'); s = re.sub(r'<h3>(?!Need)', '<h3 role="heading" aria-level="2">', s); s = s.replace('<h3>Need a quick', '<h3 role="heading" aria-level="2">Need a quick')
s = s.replace('<h4>What is', '<h4 role="heading" aria-level="3">What is')
s = re.sub(r'<h4>(?=[A-Z])', '<h4 role="heading" aria-level="3">', s); wr('index.html', s)
for p in glob.glob(ROOT + '/*/index.html'):
    rel = os.path.relpath(p, ROOT); s = rd(rel)
    # FAQ h4 following h2 -> level 3 (leave footer h4s that already carry role)
    s = re.sub(r'<h4>(?!<)', '<h4 role="heading" aria-level="3">', s)
    # contact page has no h2 before footer: footer already set to 2
    wr(rel, s)
# wheel winner h3 appears before any h2 -> level 2
s = rd('random-name-wheel/index.html'); s = s.replace('<h3>🎉 Winner', '<h3 role="heading" aria-level="2">🎉 Winner'); wr('random-name-wheel/index.html', s)

# E. 320px overflow
s = rd('index.html'); s = s.replace('minmax(320px, 1fr)', 'minmax(min(320px, 100%), 1fr)'); wr('index.html', s)
s = rd('fake-name-generator/index.html'); s = s.replace('minmax(320px, 1fr)', 'minmax(min(320px, 100%), 1fr)'); wr('fake-name-generator/index.html', s)
print('fixes applied')
