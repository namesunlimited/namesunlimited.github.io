#!/usr/bin/env python3
"""Browser audit with Playwright (Chromium; Firefox/WebKit if installed).
Serves the project locally, then for every page checks: HTTP 200, console errors, failed requests,
horizontal overflow at 6 viewports, generator tool behaviour, CSV download, keyboard focus, 404 handling.
Usage: python3 audit/e2e_audit.py [--out audit/e2e_results.json]"""
import os, sys, json, threading, http.server, socketserver, functools, re, glob
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PORT = 8765
VIEWPORTS = {'320x568': (320, 568), '375x812': (375, 812), '430x932': (430, 932),
             '768x1024': (768, 1024), '1366x768': (1366, 768), '1920x1080': (1920, 1080)}
results = []
def rec(status, area, name, detail=''): results.append(dict(status=status, area=area, name=name, detail=detail))

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.isfile(os.path.join(ROOT, '404.html')):
            body = open(os.path.join(ROOT, '404.html'), 'rb').read()
            self.send_response(404); self.send_header('Content-Type', 'text/html'); self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body)
        else: super().send_error(code, message, explain)
class S(socketserver.ThreadingTCPServer): allow_reuse_address = True
srv = S(('127.0.0.1', PORT), functools.partial(H, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{PORT}'

def page_list():
    out = []
    for p in sorted(glob.glob(ROOT + '/**/*.html', recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(('audit', 'tests', 'node_modules', 'google', '404')): continue
        url = '/' + rel[:-10] if rel.endswith('/index.html') else '/' + rel
        out.append('/' if rel == 'index.html' else url)
    return out
PAGES = page_list()

def run(browser_name, bt):
    br = bt.launch()
    ctx = br.new_context(viewport={'width': 1366, 'height': 768}, accept_downloads=True)
    ctx.grant_permissions(['clipboard-read', 'clipboard-write']) if browser_name == 'chromium' else None
    pg = ctx.new_page()
    errs, failed = [], []
    pg.on('console', lambda m: errs.append((pg.url, m.text)) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append((pg.url, str(e))))
    pg.on('requestfailed', lambda r: failed.append((r.url, r.failure)))
    # --- load + console
    for u in PAGES:
        errs.clear(); failed.clear()
        r = pg.goto(BASE + u, wait_until='load')
        ok = r.status == 200
        ext_fail = [f for f in failed if '127.0.0.1' in f[0]]
        loc_errs = [e for e in errs if 'googletagmanager' not in e[1] and 'fonts.g' not in e[1] and 'ERR_' not in e[1]]
        rec('pass' if ok and not ext_fail and not loc_errs else 'fail', f'{browser_name}/load', u, f'status={r.status} localFailed={ext_fail} errors={loc_errs}')
    # --- responsive overflow
    for u in PAGES:
        for vn, (w, h) in VIEWPORTS.items():
            pg.set_viewport_size({'width': w, 'height': h}); pg.goto(BASE + u, wait_until='load')
            o = pg.evaluate('''()=>{const de=document.documentElement;const bad=[];
              document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();
                if(r.width>0&&r.right>de.clientWidth+1&&getComputedStyle(e).position!=='fixed'){let p=e.parentElement,clipped=false;
                  while(p&&p!==document.body){const s=getComputedStyle(p);if(/(auto|scroll|hidden)/.test(s.overflowX)){clipped=true;break}p=p.parentElement}
                  if(!clipped)bad.push(e.tagName+'.'+(e.className||'').toString().slice(0,30))}});
              return {sw:de.scrollWidth,cw:de.clientWidth,bad:bad.slice(0,3)}}''')
            rec('pass' if o['sw'] <= o['cw'] + 1 else 'fail', f'{browser_name}/overflow', f'{u} @{vn}', json.dumps(o))
    # --- compact mobile header: header must not eat the phone screen, and the h1 must be visible near the top
    for u in PAGES:
        for vn, (w, h) in (('360x800', (360, 800)), ('375x812', (375, 812))):
            pg.set_viewport_size({'width': w, 'height': h}); pg.goto(BASE + u, wait_until='load')
            m = pg.evaluate('''()=>{const n=document.querySelector('.site-nav,.site-header');const e=document.querySelector('h1');const r=e.getBoundingClientRect();
              const x=Math.min(Math.max(r.left+r.width/2,0),innerWidth-1);const top=document.elementFromPoint(x,r.top+Math.min(r.height/2,10));
              return {nav:Math.round(n.getBoundingClientRect().height),h1bottom:Math.round(r.bottom+scrollY),vh:innerHeight,h1px:parseFloat(getComputedStyle(e).fontSize),
                      covered:!(top&&(top===e||e.contains(top)))}}''')
            ok = m['nav'] <= 90 and m['h1bottom'] <= 0.40 * m['vh'] and m['h1px'] <= 30 and not m['covered']
            rec('pass' if ok else 'fail', f'{browser_name}/mobile-header', f'{u} @{vn}', json.dumps(m))
    pg.set_viewport_size({'width': 1366, 'height': 768})
    # --- 404 handling
    r = pg.goto(BASE + '/definitely-not-a-page/', wait_until='load')
    rec('pass' if r.status == 404 and 'Page not found' in pg.inner_text('h1') and pg.locator('a[href="/"]').count() >= 1 else 'fail', f'{browser_name}/404', 'unknown route', f'status={r.status} body={pg.inner_text("body")[:80]!r}')
    # --- generator pages (data-generator)
    for u in PAGES:
        pg.goto(BASE + u, wait_until='load')
        if pg.locator('[data-generator]').count() == 0: continue
        g = '[data-generator] '
        pg.click(g + '[data-generate]')
        n = pg.locator(g + '[data-name-list] li').count()
        rec('pass' if n > 0 else 'fail', f'{browser_name}/tool', f'{u} generate default', f'{n} items')
        # count input boundaries
        ci = pg.locator(g + '[data-count-input]')
        if ci.count():
            for val, exp in (('1', 1), ('7', 7), ('5000', 5000), ('99999', 5000), ('0', 1), ('-5', 1), ('', 50)):
                ci.fill(val); pg.click(g + '[data-generate]')
                n = pg.locator(g + '[data-name-list] li').count()
                note = pg.locator(g + '.entry-note').inner_text() if pg.locator(g + '.entry-note').count() else ''
                # finite name pools: result may be smaller than requested, but then the UI must say so with the true count
                ok = (n == exp and not note) or (0 < n < exp and f'Only {n} ' in note and f'asked for {exp}' in note)
                rec('pass' if ok else 'fail', f'{browser_name}/tool', f'{u} count="{val}"', f'got {n}, requested {exp}, note={note!r}')
            ci.fill('25'); pg.click(g + '[data-generate]')
        # uniqueness / empties
        names = pg.locator(g + '[data-name-list] .nm').all_inner_texts()
        bad = [x for x in names if not x.strip() or 'undefined' in x or 'NaN' in x or '[object' in x]
        rec('pass' if not bad else 'fail', f'{browser_name}/tool', f'{u} output sanity', f'{len(names)} names, bad={bad[:3]}')
        # search filter
        sb = pg.locator(g + '[data-search]')
        if sb.count() and names:
            q = names[0][:2].lower(); sb.fill(q)
            shown = pg.locator(g + '[data-name-list] .nm').all_inner_texts()
            rec('pass' if shown and all(q in s.lower() for s in shown) else 'fail', f'{browser_name}/tool', f'{u} filter "{q}"', f'{len(shown)} shown')
            sb.fill('zzzqqq'); 
            rec('pass' if pg.locator(g + '[data-name-list] li').count() == 0 else 'fail', f'{browser_name}/tool', f'{u} filter no-match', 'list empty')
            sb.fill('')
        # download csv
        dl = pg.locator(g + '[data-download]')
        if dl.count():
            with pg.expect_download() as d: dl.click()
            path = d.value.path(); txt = open(path, encoding='utf-8').read().split('\n')
            rec('pass' if d.value.suggested_filename.endswith('.csv') and len(txt) >= 2 and txt[0] in ('name', 'username') else 'fail', f'{browser_name}/tool', f'{u} CSV download', f'{d.value.suggested_filename} lines={len(txt)} header={txt[0]!r}')
        cp = pg.locator(g + '[data-copy]')
        if cp.count() and browser_name == 'chromium':
            pg.locator(g + '[data-search]').fill('') if sb.count() else None
            cp.click(); clip = pg.evaluate('navigator.clipboard.readText()')
            rec('pass' if len(clip.split('\n')) == len(names) else 'fail', f'{browser_name}/tool', f'{u} copy', f'clip lines={len(clip.splitlines())} names={len(names)}')
    # --- keyboard focus visible on first 12 tabs, homepage + a tool
    for u in ('/', '/random-boy-names/', '/random-name-wheel/', '/fake-name-generator/'):
        pg.goto(BASE + u, wait_until='load'); bad = []
        for i in range(14):
            pg.keyboard.press('Tab')
            info = pg.evaluate('''()=>{const e=document.activeElement;if(!e||e===document.body)return null;const s=getComputedStyle(e);
               return {t:e.tagName+(e.id?'#'+e.id:''),ol:s.outlineStyle+' '+s.outlineWidth,bs:s.boxShadow!=='none',bd:s.borderColor}}''')
            if info and info['ol'].startswith('none') and not info['bs']: bad.append(info['t'])
        rec('pass' if not bad else 'fail', f'{browser_name}/a11y', f'{u} focus indicator (first 14 tab stops, outline/box-shadow)', f'no outline/shadow on {bad[:6]}')
    br.close()

with sync_playwright() as pw:
    for name in ('chromium', 'firefox', 'webkit'):
        try: run(name, getattr(pw, name))
        except Exception as e: rec('blocked', f'{name}', 'browser run', f'{type(e).__name__}: {str(e)[:160]}')
srv.shutdown()
out = ROOT + '/audit/e2e_results.json'
if '--out' in sys.argv: out = sys.argv[sys.argv.index('--out') + 1]
json.dump(results, open(out, 'w'), indent=1)
from collections import Counter
print(Counter((r['area'].split('/')[0], r['status']) for r in results))
for r in results:
    if r['status'] != 'pass': print(r['status'].upper(), r['area'], r['name'], '|', r['detail'][:200])
sys.exit(1 if any(r['status'] == 'fail' for r in results) else 0)
