#!/usr/bin/env python3
"""Lab (not field) measurements in headless Chromium: LCP, CLS, load timings, weight; WCAG AA text contrast;
WCAG 2.2 target size (2.5.8, 24x24 CSS px) on a 375px viewport. Google Fonts/GTM are unreachable offline, so numbers
exclude third-party time. Usage: python3 audit/perf_a11y_audit.py"""
import os, sys, json, threading, http.server, socketserver, functools, glob
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); PORT = 8770
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address = True
srv = S(('127.0.0.1', PORT), functools.partial(H, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f'http://127.0.0.1:{PORT}'
pages = []
for p in sorted(glob.glob(ROOT + '/**/index.html', recursive=True)):
    rel = os.path.relpath(p, ROOT)
    if rel.startswith(('audit', 'node_modules')): continue
    pages.append('/' if rel == 'index.html' else '/' + rel[:-10])
R = []; 
def rec(st, area, name, detail=''): R.append(dict(status=st, area=area, name=name, detail=str(detail)[:400]))
CONTRAST_JS = '''()=>{
 const parse=c=>{const m=c.match(/rgba?\\(([^)]+)\\)/);if(!m)return null;const p=m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number);return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}};
 const lum=c=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b)};
 const over=(f,b)=>({r:f.r*f.a+b.r*(1-f.a),g:f.g*f.a+b.g*(1-f.a),b:f.b*f.a+b.b*(1-f.a),a:1});
 const gradStops=e=>{const out=[];while(e){const bi=getComputedStyle(e).backgroundImage;if(bi&&bi.includes('gradient')){(bi.match(/rgba?\([^)]+\)/g)||[]).forEach(c=>out.push(parse(c)));return out}
    const c=parse(getComputedStyle(e).backgroundColor);if(c&&c.a===1)return [];e=e.parentElement}return []};
 const bg=e=>{let layers=[];let x=e;while(x){const c=parse(getComputedStyle(x).backgroundColor);if(c&&c.a>0){layers.push(c);if(c.a===1)break}x=x.parentElement}
   let base={r:255,g:255,b:255,a:1};for(let i=layers.length-1;i>=0;i--)base=over(layers[i],base);return base};
 const bad=[];const seen=new Set();
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 while(w.nextNode()){const n=w.currentNode;if(!n.textContent.trim())continue;const e=n.parentElement;if(!e||seen.has(e))continue;seen.add(e);
  const s=getComputedStyle(e);if(s.visibility==='hidden'||s.display==='none'||e.closest('[hidden],script,style,canvas'))continue;
  const r=e.getBoundingClientRect();if(r.width===0||r.height===0)continue;
  let fg0=parse(s.color);if(!fg0)continue;
  // gradient backgrounds: test against every gradient stop and keep the worst contrast (conservative)
  const bgs=[bg(e),...gradStops(e).filter(Boolean).map(g=>over(g,{r:255,g:255,b:255,a:1}))];
  let cr=99;for(const b of bgs){const fg=over({...fg0,a:fg0.a*(parseFloat(s.opacity)||1)},b);const L1=lum(fg),L2=lum(b);cr=Math.min(cr,(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05))}
  const size=parseFloat(s.fontSize),bold=parseInt(s.fontWeight)>=700;const large=size>=24||(size>=18.66&&bold);
  if(cr<(large?3:4.5))bad.push({t:n.textContent.trim().slice(0,30),cr:+cr.toFixed(2),sel:e.tagName+'.'+String(e.className).slice(0,25)})}
 return bad}'''
TARGET_JS = '''()=>{const bad=[];document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button]').forEach(e=>{
  const r=e.getBoundingClientRect();if(r.width===0||r.height===0)return;
  const inline=e.tagName==='A'&&getComputedStyle(e).display==='inline'&&e.closest('p,li,span,td');if(inline)return; // WCAG 2.5.8 inline exception
  if(r.width<24||r.height<24)bad.push(e.tagName+':'+(e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,20)+' '+Math.round(r.width)+'x'+Math.round(r.height))});return bad}'''
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for u in pages:
        ctx = br.new_context(viewport={'width': 375, 'height': 812}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = ctx.new_page(); pg.add_init_script("""window.__lcp=0;window.__cls=0;
          new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
          new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});""")
        pg.goto(B + u, wait_until='load'); pg.wait_for_timeout(600)
        m = pg.evaluate("""()=>{const n=performance.getEntriesByType('navigation')[0];const res=performance.getEntriesByType('resource').filter(r=>r.name.startsWith(location.origin));
           return {lcp:Math.round(window.__lcp),cls:+window.__cls.toFixed(4),ttfb:Math.round(n.responseStart),dcl:Math.round(n.domContentLoadedEventEnd),load:Math.round(n.loadEventEnd),
           kb:Math.round((n.transferSize+res.reduce((a,r)=>a+r.transferSize,0))/1024),reqs:res.length+1,dom:document.getElementsByTagName('*').length}}""")
        rec('pass' if m['lcp'] <= 2500 and m['cls'] <= 0.1 else 'fail', 'perf-lab', f'{u} (375px, no throttling, offline third parties)', m)
        c = pg.evaluate(CONTRAST_JS); rec('pass' if not c else 'fail', 'contrast-AA', u, c[:4])
        # dynamic state: generate results (and show the wheel winner box) then re-check contrast
        try:
            if u == '/random-name-wheel/': pg.evaluate("document.getElementById('winnerBox').classList.add('show');document.getElementById('winnerName').innerText='Sample Winner'")
            btn = pg.locator('[data-generate], button.btn-primary').first
            if btn.count() and u != '/random-name-wheel/' and u != '/': btn.click(); pg.wait_for_timeout(150)
            pg.evaluate("document.querySelectorAll('.toast-popup,#toast').forEach(e=>e.classList.add('show'))")
        except Exception as ex: rec('fail', 'contrast-AA-dynamic', u + ' (could not set state)', ex)
        c2 = pg.evaluate(CONTRAST_JS); rec('pass' if not c2 else 'fail', 'contrast-AA-dynamic', u + ' after generate/winner/toast', c2[:4])
        t = pg.evaluate(TARGET_JS); rec('pass' if not t else 'fail', 'target-size-2.5.8', u, t[:5])
        ctx.close()
    br.close()
srv.shutdown()
out = ROOT + '/audit/perf_a11y_results.json'; json.dump(R, open(out, 'w'), indent=1)
print(sum(r['status'] == 'pass' for r in R), 'pass /', sum(r['status'] == 'fail' for r in R), 'fail')
for r in R:
    if r['status'] == 'fail': print('FAIL', r['area'], r['name'], '|', r['detail'][:300])
sys.exit(1 if any(r['status'] == 'fail' for r in R) else 0)
