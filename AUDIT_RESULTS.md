# Audit results: namesunlimited.github.io

Audit date: 2026-10-16. Subject: the uploaded repository snapshot (`namesunlimited.github.io-main.zip`), tested **locally** in headless Chromium 1194 (Playwright 1.56) against a local static server. The live site/deployment was **not** reachable from the audit environment (network disabled), so nothing below is a deployment verification.

Status key: **[OK]** implemented and tested successfully (assertions passed) · **[PARTIAL]** implemented but not fully tested · **[FAIL]** failed, requires a fix · **[BLOCKED]** blocked by environment/external dependency.

## 1. Project inventory
Static HTML/CSS/vanilla JS on GitHub Pages. Pages found (29 `.html` files in the original): home, 15 generator/tool pages (fake-name, name-wheel, japanese, fantasy, character, instagram-username, baby-name-generator, band, city, elf, school, random boy/girl/baby/username), 5 guides + guides index, about, contact, privacy, terms, Google verification file, plus two problem files (below). Shared assets: `css/style.css`, `css/unified-page-theme.css`, `js/app.js`, `js/names-data.js`, 5 PNGs in `assets/`, `favicon.svg`. No dependencies, no lockfile (not needed), no build step, no existing automated tests, no redirects, no authenticated routes, no server endpoints. No `<img>` elements exist on any page (graphics are inline SVG/CSS/canvas).

## 2. Issues found and fixed (each re-tested; evidence in `audit/evidence/`)
Baseline before fixes: `audit/evidence/baseline/` (static audit: 40 FAIL / 47 WARN; e2e: 294 pass / 11 fail). After fixes: static 0 FAIL / 0 WARN; e2e 343 pass / 0 fail; tools 45 pass / 0 fail; perf+a11y 104 pass / 0 fail (see logs).

| Sev | Issue | Fix | Status |
|---|---|---|---|
| High | `jpg-to-png.html` (image converter) copied from another site: canonical + JSON-LD pointed to `pixel-forge-stack.github.io`, 12 broken internal links, 4 missing icons, orphan, off-niche for a names site, not in sitemap | **Removed.** If an image tool is wanted it must be rebuilt on this domain | [OK] static audit: file absent, 0 broken links |
| High | `guides/username-reuse-security-riskindex.html.html`: stray near-duplicate of a guide, publicly reachable, canonical pointing to the real guide, loads GTM | **Removed** | [OK] |
| Medium | Fake-name generator: unguarded `JSON.parse(localStorage…)` crashed the whole tool when stored data was corrupted | try/catch + array validation; guarded storage writes | [OK] corrupted-storage test |
| Medium | Name wheel: "Remove Winner" deleted *every* entry with the same name, and did not update saved list (removed names reappeared after reload); Shuffle used biased `sort(random)` and was not persisted; onload storage read unguarded | Remove only the winning slice, persist, Fisher-Yates shuffle, guarded storage | [OK] 4 new tests |
| Medium | `/contact/` text contrast 1.13:1 (white text on pale box, leftover dark-theme inline colours) | use theme variables | [OK] contrast audit, visual check |
| Medium | No `404.html` (GitHub Pages default 404) | Added branded `404.html`, `noindex` | [PARTIAL] verified through a local server that mimics Pages' 404 behaviour; not on live Pages |
| Medium | Unlabelled `input`s (count and filter) on the 8 `data-generator` pages | `aria-label`s | [OK] |
| Medium | Social metadata: 5 tool pages had no og tags; 7 pages used an SVG as `og:image` (unsupported by most crawlers) | og tags added; all point to `assets/og-image.png` (1200x630) with dimensions + alt, `twitter:image` | [OK] static audit |
| Medium | Generators silently returned fewer names than requested (finite pools: e.g. school max 40, city 660) while the UI advertises up to 5000 | Result count + a `role=status` note ("Only N … available, you asked for M") | [OK] boundary tests (1, 7, 5000, 99999, 0, -5, empty) |
| High | **Mobile header too large** (reported by owner after the first audit, which had missed it): on the 13 `.site-nav` pages the sticky header took 199-249 px of a 800 px phone screen and the h1 was 32 px; guide pages had a 32 px h1 with 44 px extra top padding | Compact header: brand row + one horizontally scrollable link row (~80 px), not sticky, smaller hero/tool-panel padding and h1 on <=760 px; `.hero`/guide-article spacing compacted in `style.css` | [OK] new e2e test `mobile-header` (nav <= 90 px, h1 <= 30 px and within 40% of viewport, not covered) on all 26 pages at 360x800 and 375x812 |
| High | **Homepage quick-name box unreadable** (heading 1.01:1, helper text 2.08:1: dark text on leftover dark gradient). The first contrast audit missed it because it ignored gradient backgrounds | Light theme surface for `.hero-quick-tool`; contrast audit now tests gradient stops (worst case) and dynamic states (generated results, wheel winner box, toast) | [OK] |
| Low | Horizontal overflow at 320px: home hub cards, fake-name cards/detail rows | `minmax(min(320px,100%),1fr)`, wrapping | [OK] 26 pages x 6 viewports |
| Low | Heading outline jumps (h1→h3/h4) | `role="heading" aria-level` on existing elements (visual style unchanged) | [OK] static audit |
| Low | Target size < 24px (breadcrumb "Home", card Copy buttons) | min sizes (WCAG 2.2 SC 2.5.8) | [OK] |
| Low | "Home" nav item marked active on every page | active state/`aria-current` follows the current page | [OK] visual/DOM check |
| Low | `alert()` on clipboard failure | inline button text feedback | [OK] code only; clipboard *failure* path not simulated |
| Low | Sitemap `lastmod` stale | set to 2026-10-16 | [OK] |

## 3. What was verified (local)
- **Sitemap**: valid XML, correct namespace, 26 absolute URLs on `https://namesunlimited.github.io`, no duplicates, every URL has a file, all canonical self-referencing & indexable, no noindex/localhost/staging URLs; all indexable pages listed. **robots.txt**: `Allow: /` + correct Sitemap line; nothing blocked. [OK]
- **Metadata**: unique titles & descriptions, charset, viewport, `lang`, canonical = own URL, exactly one h1 per page. [OK]
- **Structured data** (BreadcrumbList, FAQPage, WebApplication, WebSite): JSON-LD parses; schema.org context; URLs on-origin; WebApplication has name/url/applicationCategory; FAQ questions appear in visible text. [OK for syntax and consistency] Not run through Google's Rich Results Test (BLOCKED, no network). Note: Google limits FAQ rich results to authoritative government/health sites, so none should be expected.
- **Links/assets**: all internal links, anchors, CSS/JS/icon references resolve; no orphan pages (Google verification file excluded). [OK]
- **Tools**: all 8 `data-generator` pages and 7 inline-script tools exercised (all select combinations, batch bounds, filter, copy, CSV/JSON export contents, shortlist persistence/clear, wheel spin/remove/shuffle/presets, 2000 entries, HTML/unicode/3000-char entries rendered inertly, instagram keyword sanitised to `[a-z0-9]`). [OK]
- **Responsive**: no horizontal overflow on any page at 320x568, 375x812, 430x932, 768x1024, 1366x768, 1920x1080 (Chromium). [OK]
- **Lessons from the first pass**: automated checks only find what they are written to look for; the two visual problems above (oversized mobile header, unreadable homepage box) were reported by the owner and then covered by new tests. Other visual/UX problems may still exist: a human review on real phones is recommended.
- **Performance (lab only, no throttling, third parties unreachable)**: LCP ≤ ~105 ms, CLS 0, ≤ 4 same-origin requests, ≤ ~70 KB per page. These are not field data and say nothing about real-user Core Web Vitals. INP not measured. [PARTIAL]
- **Accessibility (automated/custom)**: text contrast AA on all pages (static states), control labels, link/button names, target size, focus indicator on 4 pages' first 14 tab stops. [PARTIAL: not full WCAG 2.2 AA conformance]
- **Security/privacy (source review)**: no secrets/keys in repo (scan done); no `eval`/`document.write`; `innerHTML` is only fed by built-in data or sanitised input; no server, so no injection/CSRF/upload surface; external `target=_blank` links have `noopener`; privacy policy's GTM page list matches the pages that actually load GTM; contact form sends nothing (page says so). No dependencies, so a dependency audit is not applicable. [OK for what was reviewed]

## 4. Unresolved / owner decisions
1. **Consent**: GTM loads on 14 pages (elf, city, school, band, boy/girl/baby-random, username, guides) with no consent banner. Disclosed in the privacy policy, but visitors from the EU/UK may require prior consent. Not changed (legal/owner decision).
2. **Google Fonts** loaded from Google on every page (disclosed). Self-hosting not done (font files not obtainable offline); doing so would also remove a render-blocking third-party request.
3. **Security headers** (CSP, X-Content-Type-Options, frame protection, HSTS settings) cannot be set from the repo on GitHub Pages; a meta CSP would need `unsafe-inline` for the many inline scripts/styles and GTM, so none was added. Consider a CDN/proxy in front if headers matter.
4. **Contact form** does not send anything (honestly labelled). Consider removing the form or wiring it to a service.
5. **Content**: FAQ markup retained (valid, mirrors visible text). `changefreq`/`priority` in sitemap are ignored by Google (harmless). `ads.txt` contains only commented placeholder lines. Large inline CSS is duplicated per page (works; consolidation would reduce bytes). Contact page `h1` wraps narrowly at 1366px (cosmetic, unfixed). Pages using `.site-nav` now use a scrollable link strip on phones (not a hamburger); pages using `.site-header` use a hamburger: two different mobile nav patterns remain (consistency not unified). `initMobileNav` in `js/app.js` is unused.
6. Finite name pools: some tools cannot produce thousands of unique names; the UI now says so. Raising the pools is a content decision.

## 5. Not tested / blocked
- **[BLOCKED]** Firefox, WebKit/Safari, Edge, Mobile Safari/Chrome on real devices (only Chromium available; e2e run reports Firefox/WebKit as BLOCKED). No cross-browser claim is made.
- **[BLOCKED]** Live-site checks: HTTPS/TLS, HTTP→HTTPS and hostname redirects, real 404 behaviour, cache/compression headers, MIME types, Search Console indexing, field Core Web Vitals (CrUX/PageSpeed), Lighthouse.
- **[BLOCKED]** axe-core, W3C HTML validator, Google Rich Results Test, `npm audit` (network disabled / no dependencies).
- **Not performed**: screen-reader testing; full keyboard-operability pass of every control (only focus-indicator and button-semantics checks); 200% zoom/text-resize and landscape orientation; `prefers-reduced-motion` behaviour (only `css/style.css` contains a rule; the wheel/confetti animations on the wheel page have none: **[FAIL] open Low issue**); canvas wheel has no text alternative beyond the editable list; hover/focus/dynamic-state contrast; the clipboard-failure path; Firefox/Safari file-download behaviour.
- Image optimisation/alt text: the site contains no `<img>` elements; `assets/` PNGs are 0.3–41 KB (og-image 1200x630). Nothing to alt-text; icon/favicon requests resolve locally.

## 6. How to reproduce
`bash audit/run_all.sh` (see README). Logs of the final run: `audit/evidence/*.log`; machine-readable results: `audit/*_results.json`.
