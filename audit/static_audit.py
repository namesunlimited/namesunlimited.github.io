#!/usr/bin/env python3
"""Static site audit: metadata, canonical, links, images, headings, JSON-LD, sitemap, robots.
Usage: python3 audit/static_audit.py [--json out.json]   (run from project root)
Exit code 1 if any FAIL-level finding exists."""
import os, sys, json, re, glob
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
from lxml import etree

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ORIGIN = 'https://namesunlimited.github.io'
findings = []
def add(sev, page, check, msg): findings.append(dict(sev=sev, page=page, check=check, msg=msg))

def url_for(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    if rel == 'index.html': return ORIGIN + '/'
    if rel.endswith('/index.html'): return ORIGIN + '/' + rel[:-10]
    return ORIGIN + '/' + rel

def resolve_local(href, page_path):
    """map internal URL path to a file on disk (GitHub Pages semantics)"""
    p = urlparse(href); path = unquote(p.path)
    base = ROOT if path.startswith('/') else os.path.dirname(page_path)
    full = os.path.normpath(os.path.join(base, path.lstrip('/') if path.startswith('/') else path))
    if os.path.isdir(full): full = os.path.join(full, 'index.html')
    if os.path.isfile(full): return full
    if os.path.isfile(full + '.html'): return full + '.html'
    return None

pages = sorted(glob.glob(ROOT + '/**/*.html', recursive=True))
pages = [p for p in pages if '/node_modules/' not in p and '/audit/' not in p and '/tests/' not in p]
meta = {}
titles, descs = {}, {}
inlinks = {url_for(p): set() for p in pages}

for pth in pages:
    rel = os.path.relpath(pth, ROOT)
    u = url_for(pth)
    raw = open(pth, encoding='utf-8').read()
    soup = BeautifulSoup(raw, 'lxml')
    if rel.startswith('google') : continue
    if rel == '404.html':
        if 'noindex' not in raw: add('FAIL', rel, '404', '404.html must be noindex')
        continue
    if not rel.endswith('index.html') and rel != 'jpg-to-png.html':
        add('FAIL', rel, 'file-name', 'Non-standard HTML file name publicly reachable (stray/duplicate page?)')
    robots = soup.find('meta', attrs={'name': 'robots'})
    robots_c = (robots.get('content', '') if robots else '').lower()
    noindex = 'noindex' in robots_c
    t = soup.title.string.strip() if soup.title and soup.title.string else ''
    d = soup.find('meta', attrs={'name': 'description'}); d = d.get('content', '').strip() if d else ''
    can = soup.find('link', rel='canonical'); can = can.get('href', '') if can else ''
    h1s = soup.find_all('h1')
    meta[u] = dict(title=t, desc=d, canonical=can, noindex=noindex, h1=len(h1s))
    if not t: add('FAIL', rel, 'title', 'missing <title>')
    if not d: add('FAIL', rel, 'description', 'missing meta description')
    if t: titles.setdefault(t, []).append(rel)
    if d: descs.setdefault(d, []).append(rel)
    if not can: add('FAIL', rel, 'canonical', 'missing canonical')
    elif can != u and not noindex: add('FAIL', rel, 'canonical', f'canonical {can} != expected {u}')
    if not soup.find('meta', charset=True): add('FAIL', rel, 'charset', 'missing charset')
    if not soup.find('meta', attrs={'name': 'viewport'}): add('FAIL', rel, 'viewport', 'missing viewport')
    if not soup.html.get('lang'): add('FAIL', rel, 'lang', 'missing <html lang>')
    if len(h1s) != 1: add('FAIL', rel, 'h1', f'{len(h1s)} h1 elements')
    # heading order
    lv = [int(h.get('aria-level') or h.name[1]) if h.get('role') == 'heading' else int(h.name[1]) for h in soup.find_all(re.compile('^h[1-6]$'))]
    for a, b in zip(lv, lv[1:]):
        if b - a > 1: add('WARN', rel, 'heading-order', f'heading jumps h{a}->h{b}'); break
    og = {m.get('property'): m.get('content', '') for m in soup.find_all('meta', property=re.compile('^og:'))}
    for k in ('og:title', 'og:description', 'og:url', 'og:image'):
        if k not in og: add('WARN', rel, 'og', f'missing {k}')
    if og.get('og:url') and og['og:url'] != can: add('WARN', rel, 'og:url', f"og:url {og['og:url']} != canonical {can}")
    if og.get('og:image', '').endswith('.svg'): add('WARN', rel, 'og:image', 'og:image is SVG (not supported by most social crawlers)')
    # JSON-LD
    for s in soup.find_all('script', type='application/ld+json'):
        try:
            j = json.loads(s.string or '')
            items = j if isinstance(j, list) else [j]
            flat = []
            for it in items: flat += it['@graph'] if '@graph' in it else [it]
            ctx_ok = all(it.get('@context') in ('https://schema.org', 'http://schema.org') for it in items)
            items = [dict(x, **{'@context': 'https://schema.org'}) if ctx_ok else x for x in flat]
            for it in items:
                if it.get('@type') == 'WebApplication':
                    for req in ('name', 'url', 'applicationCategory'):
                        if not it.get(req): add('FAIL', rel, 'jsonld-webapp', f'WebApplication missing {req}')
                    if it.get('url') and it['url'] != meta[u]['canonical'] and not it['url'].startswith(ORIGIN): add('FAIL', rel, 'jsonld-webapp', 'url off-origin')
            for it in items:
                if it.get('@context') not in ('https://schema.org', 'http://schema.org'): add('FAIL', rel, 'jsonld', 'bad @context')
                if it.get('url') and not it['url'].startswith(ORIGIN): add('FAIL', rel, 'jsonld', f"url {it['url']} off-origin")
                if it.get('@type') == 'FAQPage':  # markup must mirror visible content
                    vis = re.sub(r'\s+', ' ', soup.get_text(' ')).lower().replace('\u2019', "'")
                    for q in it.get('mainEntity', []):
                        if re.sub(r'\s+', ' ', q['name']).lower().replace('\u2019', "'") not in vis: add('FAIL', rel, 'jsonld-faq', f"FAQ question not visible on page: {q['name'][:50]}")
        except Exception as e:
            add('FAIL', rel, 'jsonld', f'invalid JSON-LD: {e}')
    # images
    for im in soup.find_all('img'):
        src = im.get('src', '')
        if im.get('alt') is None: add('FAIL', rel, 'img-alt', f'img without alt: {src}')
        if not (im.get('width') and im.get('height')): add('WARN', rel, 'img-dims', f'img without width/height: {src}')
        if src and not src.startswith(('data:', 'http')) and not resolve_local(src, pth): add('FAIL', rel, 'img-broken', src)
    # links
    for a in soup.find_all('a', href=True):
        h = a['href'].strip()
        if h.startswith(('mailto:', 'tel:', 'javascript:')) or h == '#': 
            if h == '#': add('WARN', rel, 'link', 'href="#" placeholder link')
            continue
        pr = urlparse(h)
        if pr.scheme in ('http', 'https') and pr.netloc != 'namesunlimited.github.io':
            if 'noopener' not in (a.get('rel') or []) and a.get('target') == '_blank': add('WARN', rel, 'rel', f'target=_blank w/o noopener {h}')
            continue
        if h.startswith('#'):
            if h[1:] and not soup.find(id=h[1:]): add('FAIL', rel, 'anchor', f'missing anchor {h}')
            continue
        tgt = resolve_local(h, pth)
        if not tgt: add('FAIL', rel, 'broken-link', h); continue
        tu = url_for(tgt)
        inlinks.setdefault(tu, set()).add(u)
        # trailing-slash/policy: internal links should point at canonical URL
        if pr.path and not pr.path.endswith('/') and '.' not in os.path.basename(pr.path) and pr.path != '':
            add('WARN', rel, 'link-slash', f'internal link without trailing slash: {h}')
        if not a.get_text(strip=True) and not a.get('aria-label') and not a.find('img'): add('FAIL', rel, 'link-name', f'empty link text: {h}')
    # assets
    for tag, attr in (('link', 'href'), ('script', 'src')):
        for el in soup.find_all(tag, **{attr: True}):
            v = el[attr]
            if v.startswith(('http', '//', 'data:')): 
                if tag == 'script' or el.get('rel') == ['stylesheet']: add('INFO', rel, 'external-asset', v)
                continue
            if not resolve_local(v, pth): add('FAIL', rel, 'asset-broken', v)
    # placeholders
    txt = soup.get_text(' ')
    # 'lorem ipsum' appears legitimately as an example in fake-data copy (verified manually)
    for w in ('lorem ipsum', 'TODO', 'FIXME', 'coming soon', 'placeholder text', 'your-domain', 'example.com'):
        if w.lower() in txt.lower() and not (w in ('lorem ipsum','placeholder text') and 'fake-name' in rel): add('WARN', rel, 'placeholder', f'contains "{w}"')
    for el in soup.find_all(['input', 'select', 'textarea']):
        if el.get('type') in ('hidden', 'submit', 'button'): continue
        i = el.get('id')
        if not ((i and soup.find('label', attrs={'for': i})) or el.get('aria-label') or el.get('aria-labelledby') or el.find_parent('label')):
            add('FAIL', rel, 'form-label', f'unlabelled control <{el.name} id={i} name={el.get("name")}>')
    for b in soup.find_all('button'):
        if not (b.get_text(strip=True) or b.get('aria-label')): add('FAIL', rel, 'button-name', 'button without accessible name')

for t, ps in titles.items():
    if len(ps) > 1: add('FAIL', ','.join(ps), 'dup-title', t)
for t, ps in descs.items():
    if len(ps) > 1: add('FAIL', ','.join(ps), 'dup-desc', t)
for u, s in inlinks.items():
    if not s and u != ORIGIN + '/' and 'google' not in u and not u.endswith('/404.html'): add('FAIL', u, 'orphan', 'no internal links point to this page')

# sitemap
try:
    tree = etree.parse(os.path.join(ROOT, 'sitemap.xml'))
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    assert tree.getroot().tag == '{%s}urlset' % ns['s'], 'wrong root/namespace'
    locs = [e.text.strip() for e in tree.findall('.//s:loc', ns)]
    if len(locs) != len(set(locs)): add('FAIL', 'sitemap.xml', 'dups', 'duplicate <loc>')
    page_urls = {url_for(p) for p in pages if not os.path.basename(p).startswith('google') and not p.endswith('404.html')}
    for l in locs:
        if not l.startswith(ORIGIN + '/'): add('FAIL', 'sitemap.xml', 'origin', l)
        if l not in page_urls: add('FAIL', 'sitemap.xml', 'missing-page', f'{l} has no file')
        elif meta[l]['noindex']: add('FAIL', 'sitemap.xml', 'noindex', l)
        elif meta[l]['canonical'] != l: add('FAIL', 'sitemap.xml', 'non-canonical', l)
    for u in page_urls - set(locs):
        if not meta[u]['noindex'] and not u.endswith('.html'): add('WARN', 'sitemap.xml', 'not-listed', f'indexable page missing from sitemap: {u}')
        elif u.endswith('.html') and not meta[u]['noindex']: add('WARN', 'sitemap.xml', 'not-listed', f'indexable page missing from sitemap: {u}')
    for e in tree.findall('.//s:lastmod', ns):
        if not re.match(r'^\d{4}-\d{2}-\d{2}', e.text): add('FAIL', 'sitemap.xml', 'lastmod', e.text)
except Exception as ex:
    add('FAIL', 'sitemap.xml', 'parse', str(ex))

# robots
rb = open(os.path.join(ROOT, 'robots.txt')).read()
if 'Sitemap: ' + ORIGIN + '/sitemap.xml' not in rb: add('FAIL', 'robots.txt', 'sitemap-ref', 'sitemap not referenced')
if re.search(r'^\s*Disallow:\s*/\s*$', rb, re.M): add('FAIL', 'robots.txt', 'block-all', 'Disallow: / present')

order = {'FAIL': 0, 'WARN': 1, 'INFO': 2}
findings.sort(key=lambda f: (order[f['sev']], f['page'], f['check']))
if '--json' in sys.argv:
    json.dump(dict(pages=len(pages), findings=findings), open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
for f in findings: print(f"{f['sev']:5} {f['page']:55} {f['check']:15} {f['msg']}")
nf = sum(1 for f in findings if f['sev'] == 'FAIL')
print(f"\n{len(pages)} pages scanned; FAIL={nf} WARN={sum(1 for f in findings if f['sev']=='WARN')} INFO={sum(1 for f in findings if f['sev']=='INFO')}")
sys.exit(1 if nf else 0)
