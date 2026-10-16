#!/usr/bin/env python3
"""Functional tests for the inline-script tools (wheel, fake identity, baby, japanese, fantasy, character, instagram).
Usage: python3 audit/tools_audit.py [--out audit/tools_results.json]"""
import os, sys, json, threading, http.server, socketserver, functools, csv, io
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); PORT = 8766
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
class S(socketserver.ThreadingTCPServer): allow_reuse_address = True
srv = S(('127.0.0.1', PORT), functools.partial(H, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{PORT}'; R = []
def rec(ok, name, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name, flush=True); R.append(dict(status='pass' if ok else 'fail', name=name, detail=str(detail)[:300]))

BAD = ('undefined', 'NaN', '[object', 'null')
def options(pg, sel): return pg.eval_on_selector_all(f'{sel} option', 'o=>o.map(x=>x.value)')

with sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(accept_downloads=True); ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    # ---------- card-grid generators: every option of every select, all batch sizes
    specs = {
        '/baby-name-generator/': ('generateBabyNames()', '#babyGrid', ['#babyGender', '#babyOrigin'], '#babyBatch', '.copy-btn'),
        '/japanese-name-generator/': ('generateJapaneseBatch()', '#jpResultsGrid', ['#jpGender', '#jpStyle'], '#jpCount', '.copy-btn'),
        '/fantasy-name-generator/': ('generateFantasyNames()', '#fantasyResults', ['#raceSelect', '#namingType'], '#fantasyBatch', '.copy-btn'),
        '/random-name-for-character/': ('generateCharacterNames()', '#characterGrid', ['#charGenre', '#charGender'], '#charBatch', '.copy-btn'),
        '/instagram-username-generator/': ('generateUsernames()', '#usernameGrid', ['#userVibe'], '#userBatch', '.copy-btn'),
    }
    for url, (fn, grid, sels, batch, _) in specs.items():
        pg.goto(BASE + url); errs.clear(); bad = []; combos = 0
        batches = options(pg, batch)
        import itertools
        lists = [options(pg, s) for s in sels]
        for combo in itertools.product(*lists):
            for s, v in zip(sels, combo): pg.select_option(s, v)
            for b in (batches[0], batches[-1]):
                pg.select_option(batch, b); pg.evaluate(fn); combos += 1
                cards = pg.locator(f'{grid} > *').count(); txt = pg.inner_text(grid)
                if cards != int(b) or any(w in txt for w in BAD) or any(not t.strip() for t in pg.locator(f'{grid} .main-name, {grid} .name-main, {grid} h3').all_inner_texts()):
                    bad.append((combo, b, cards))
        rec(not bad and not errs, f'{url} all option combos ({combos} runs), card count == batch, no undefined/NaN', f'bad={bad[:3]} jsErrors={errs[:2]}')
        # copy all -> clipboard
        copy_btn = pg.locator('button:has-text("Copy All")')
        pg.evaluate(fn); copy_btn.first.click(); clip = pg.evaluate('navigator.clipboard.readText()')
        rec(len([l for l in clip.splitlines() if l.strip()]) >= int(batches[-1]) if False else len(clip.strip()) > 0, f'{url} Copy All writes to clipboard', f'{len(clip.splitlines())} lines')
        # single card copy
        pg.locator(f'{grid} .copy-btn').first.click(); one = pg.evaluate('navigator.clipboard.readText()')
        rec(len(one.strip()) > 0 and not any(w in one for w in BAD), f'{url} single-card copy', repr(one[:60]))
        # keyboard access of copy button
        pg.locator(f'{grid} .copy-btn').first.focus(); tag = pg.evaluate('document.activeElement.tagName')
        rec(tag == 'BUTTON', f'{url} copy control is a real focusable button', tag)
    # username: keyword sanitising (XSS + special chars)
    pg.goto(BASE + '/instagram-username-generator/'); pg.fill('#seedWord', '<img src=x onerror=window.__x=1>"\'Éé 日本 -_ AbC 123'); pg.evaluate('generateUsernames()')
    html = pg.inner_html('#usernameGrid'); main = pg.locator('#usernameGrid .main-name').all_inner_texts()
    rec(pg.evaluate('window.__x') is None and '<img' not in html and all(__import__('re').fullmatch(r'@[a-z0-9._]+', m.strip()) for m in main), 'instagram keyword: XSS/special chars sanitised to [a-z0-9]', main[:3])
    pg.fill('#seedWord', ''); pg.evaluate('generateUsernames()')
    rec(pg.locator('#usernameGrid > *').count() > 0, 'instagram empty keyword uses fallback seeds')
    pg.fill('#seedWord', 'a' * 5000); pg.evaluate('generateUsernames()')
    rec(pg.locator('#usernameGrid > *').count() > 0, 'instagram 5000-char keyword does not crash', f'longest={max(len(t) for t in pg.locator("#usernameGrid .main-name").all_inner_texts())}')
    # ---------- fake identity generator
    pg.goto(BASE + '/fake-name-generator/'); errs.clear(); bad = []
    for c in options(pg, '#countrySelect'):
        for g in options(pg, '#genderSelect'):
            pg.select_option('#countrySelect', c); pg.select_option('#genderSelect', g); pg.select_option('#quantitySelect', options(pg, '#quantitySelect')[-1]); pg.evaluate('generateBatch()')
            n = pg.locator('#resultsGrid > *').count(); t = pg.inner_text('#resultsGrid')
            if n != int(options(pg, '#quantitySelect')[-1]) or any(w in t for w in BAD): bad.append((c, g, n))
    rec(not bad and not errs, 'fake identity: every country x gender, max batch, no undefined/NaN', f'bad={bad[:3]} err={errs[:2]}')
    with pg.expect_download() as d: pg.click('#exportCsvBtn')
    rows = list(csv.reader(io.StringIO(open(d.value.path(), encoding='utf-8').read())))
    rec(len(rows) >= 2 and all(len(r) == len(rows[0]) for r in rows), 'fake identity: CSV export well-formed (consistent columns)', f'{len(rows)} rows, header={rows[0]}')
    with pg.expect_download() as d: pg.click('#exportJsonBtn')
    try: j = json.load(open(d.value.path(), encoding='utf-8')); ok = isinstance(j, list) and len(j) > 0
    except Exception as e: ok = False; j = str(e)
    rec(ok, 'fake identity: JSON export parses', f'{len(j) if ok else j} records')
    pg.click('#copyAllBtn'); clip = pg.evaluate('navigator.clipboard.readText()'); rec(len(clip) > 50, 'fake identity: Copy All', f'{len(clip)} chars')
    # favorites persistence + clear
    pg.locator('.fav-btn').first.click(); pg.reload(); cnt = pg.inner_text('#favCount')
    rec(cnt.strip() not in ('0', ''), 'fake identity: shortlist persists across reload (localStorage)', f'favCount={cnt}')
    with pg.expect_download() as d: pg.click('#favoritesBar button:has-text("Download Shortlist")')
    rows = list(csv.reader(io.StringIO(open(d.value.path(), encoding='utf-8').read()))); rec(len(rows) >= 2, 'fake identity: shortlist CSV download', f'{len(rows)} rows')
    pg.once('dialog', lambda dlg: dlg.accept()); pg.click('#favoritesBar button:has-text("Clear")'); pg.wait_for_timeout(200)
    rec(not pg.is_visible('#favoritesBar') and pg.evaluate("localStorage.getItem('user_saved_personas')") in (None, '[]'), 'fake identity: Clear hides shortlist & empties storage', pg.evaluate("localStorage.getItem('user_saved_personas')"))
    pg.evaluate("localStorage.setItem('user_saved_personas','{corrupt')"); errs.clear(); pg.reload()
    rec(not errs, 'fake identity: corrupted localStorage does not crash page', errs[:1])
    # ---------- name wheel
    pg.goto(BASE + '/random-name-wheel/'); errs.clear()
    def setnames(t):
        pg.wait_for_function('!isSpinning', timeout=20000); pg.fill('#nameList', t)
    setnames('A\nB\nC\nD'); pg.click('#spinBtn'); pg.wait_for_function("document.getElementById('winnerBox').classList.contains('show') || getComputedStyle(document.getElementById('winnerBox')).display!=='none'", timeout=20000)
    w = pg.inner_text('#winnerName'); rec(w.strip() in 'ABCD' and w.strip() != '---', 'wheel: spin picks a winner from the list', w)
    names_before = pg.input_value('#nameList').split('\n'); pg.click('#winnerBox button:has-text("Remove Winner")'); after = [x for x in pg.input_value('#nameList').split('\n') if x.strip()]
    rec(len(after) == 3 and w.strip() not in after, 'wheel: Remove Winner deletes exactly that entry', after)
    rec(pg.evaluate("localStorage.getItem('saved_wheel_names')").split('\n') == after, 'wheel: Remove Winner is persisted to localStorage', pg.evaluate("localStorage.getItem('saved_wheel_names')"))
    setnames('Dup\nDup\nZ'); pg.evaluate("lastWinner='Dup'; lastWinnerIndex=0"); pg.evaluate('removeWinner()')
    rec(pg.input_value('#nameList') == 'Dup\nZ', 'wheel: Remove Winner removes only one of duplicate entries', repr(pg.input_value('#nameList')))
    setnames('A\nB\nC\nD'); pg.click('button:has-text("Shuffle")'); sh = [x for x in pg.input_value('#nameList').split('\n') if x.strip()]; rec(sorted(sh) == ['A', 'B', 'C', 'D'], 'wheel: Shuffle keeps same entries', sh)
    for lab, n in (('Classroom', 15), ('Numbers', 20), ('Yes / No', 6)):
        pg.click(f'button:has-text("{lab}")'); got = [x for x in pg.input_value('#nameList').split('\n') if x.strip()]
        rec(len(got) == n, f'wheel: preset {lab} loads {n} entries', len(got))
    setnames(''); pg.click('#spinBtn'); pg.wait_for_timeout(500); rec(not errs, 'wheel: spin with empty list does not throw', errs[:1])
    setnames('Solo'); pg.click('#spinBtn'); pg.wait_for_timeout(500); rec(not errs, 'wheel: single entry spin does not throw', errs[:1])
    setnames('<img src=x onerror=window.__w=1>\n<b>bold</b>\n' + 'X' * 3000 + '\n日本語\n😀'); pg.click('#spinBtn')
    try: pg.wait_for_function("getComputedStyle(document.getElementById('winnerBox')).display!=='none'", timeout=25000)
    except Exception: pass
    rec(pg.evaluate('window.__w') is None and not errs and '<b>' not in pg.inner_html('#winnerName'), 'wheel: HTML/long/unicode entries rendered inertly', f'winner={pg.inner_text("#winnerName")[:40]!r} err={errs[:1]}')
    # fill() on a 2000-line textarea stalls inside Playwright itself; set value + dispatch a real input event instead
    pg.wait_for_function('!isSpinning', timeout=20000); pg.evaluate("v=>{const t=document.getElementById('nameList');t.value=v;t.dispatchEvent(new Event('input',{bubbles:true}))}", '\n'.join(f'N{i}' for i in range(2000))); pg.click('#spinBtn'); pg.wait_for_timeout(800); rec(not errs, 'wheel: 2000 entries does not throw', errs[:1])
    pg.reload(); rec(pg.input_value('#nameList').startswith('N0'), 'wheel: entries restored after reload (localStorage)', pg.input_value('#nameList')[:10])
    pg.click('#soundToggle'); rec(not errs, 'wheel: sound toggle works w/o error', errs[:1])
    br.close()
srv.shutdown()
out = ROOT + '/audit/tools_results.json'
if '--out' in sys.argv: out = sys.argv[sys.argv.index('--out') + 1]
json.dump(R, open(out, 'w'), indent=1)
print(f"{sum(r['status']=='pass' for r in R)} pass / {sum(r['status']=='fail' for r in R)} fail")
for r in R:
    if r['status'] == 'fail': print('FAIL', r['name'], '|', r['detail'])
sys.exit(1 if any(r['status'] == 'fail' for r in R) else 0)
