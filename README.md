# Names Unlimited (namesunlimited.github.io)

Static website of browser-based name generators (fake identities, name wheel, Japanese, fantasy, character, baby, band, city, elf, school, usernames) plus guides. Hosted on **GitHub Pages**; no build step, no server code, no runtime dependencies, no environment variables, no secrets.

## Run locally
```bash
python3 -m http.server 8000        # or: npm start
# open http://localhost:8000/
```
Pretty URLs (`/about/`) work because every page is `<dir>/index.html`. `404.html` is served by GitHub Pages for unknown paths (the local test servers emulate this).

## Deploy
Push to the `main` branch of `namesunlimited/namesunlimited.github.io`; GitHub Pages serves the repository root (`.nojekyll` is present). Rollback = `git revert` / redeploy a previous commit.
When adding a page: create `<slug>/index.html`, add it to the nav/footer or a hub page (avoid orphans), add its URL to `sitemap.xml`, then run the audit.

## Repeatable audit / tests
```bash
pip install -r audit/requirements.txt
playwright install chromium          # Firefox/WebKit optional: playwright install firefox webkit
bash audit/run_all.sh                # runs everything below; logs go to audit/evidence/
```
| Script | What it checks |
|---|---|
| `audit/static_audit.py` | every HTML file: title/description/canonical/og, duplicate metadata, h1/heading order, JSON-LD (syntax, FAQ mirrors visible text, WebApplication fields), image alt/dimensions, broken internal links/anchors/assets, orphan pages, form labels, sitemap vs. files, robots.txt |
| `audit/e2e_audit.py` | Playwright: status/console errors per page, horizontal overflow at 6 viewports (320x568 … 1920x1080), 404 page, generator tools (count boundaries, filter, CSV download, clipboard), focus indicators |
| `audit/tools_audit.py` | every option combination of each inline-script tool, XSS/special-character handling, exports (CSV/JSON), localStorage persistence/corruption, name wheel behaviour |
| `audit/perf_a11y_audit.py` | lab LCP/CLS/weight at 375px, WCAG AA text contrast, WCAG 2.2 target size |

`audit/apply_fixes.py` is a record of the bulk edits made during the audit. **Do not re-run it** on a project that already contains them unless you know what you are doing. Results and open items: see `AUDIT_RESULTS.md`.

## Notes
- Google Tag Manager (`GTM-KLF2FN7L`) and Google Fonts are third-party loads; see `privacy-policy/` and `AUDIT_RESULTS.md`.
- Search-engine indexing, field Core Web Vitals and live HTTP headers can only be verified on the deployed site (Search Console, PageSpeed Insights/CrUX).
