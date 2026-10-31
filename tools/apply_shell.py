#!/usr/bin/env python3
"""Apply ONE shared header + footer + head basics to every page.

Run from the repo root:   python3 tools/apply_shell.py
Safe to re-run (idempotent): the generated blocks are wrapped in marker comments and
replaced in place. To change the menu or footer links, edit NAV / FOOTER_COLS below
and run it again -- do not hand-edit headers/footers in individual pages.
"""
import glob, html, os, re, sys

SITE = "https://namesunlimited.github.io"
THEME_COLOR = "#26344E"
VIEWPORT = "width=device-width, initial-scale=1"

# (label, href, [url prefixes that should highlight this tab])
NAV = [
    ("Baby Names", "/baby-name-generator/", ["/baby-name-generator/", "/random-name-for-baby/", "/random-boy-names/", "/random-girl-names/", "/gender-neutral-names/"]),
    ("Characters", "/random-name-for-character/", ["/random-name-for-character/", "/city-name-generator/", "/school-name-generator/", "/band-name-generator/"]),
    ("Fantasy", "/fantasy-name-generator/", ["/fantasy-name-generator/", "/elf-name-generator/"]),
    ("Japanese", "/japanese-name-generator/", ["/japanese-name-generator/"]),
    ("Usernames", "/random-username-generator/", ["/random-username-generator/", "/instagram-username-generator/"]),
    ("Fake Names", "/fake-name-generator/", ["/fake-name-generator/"]),
    ("Name Wheel", "/random-name-wheel/", ["/random-name-wheel/"]),
    ("Guides", "/guides/", ["/guides/"]),
]

FOOTER_COLS = [
    ("Baby &amp; People", [
        ("Baby Name Generator", "/baby-name-generator/"),
        ("Random Baby Names", "/random-name-for-baby/"),
        ("Random Boy Names", "/random-boy-names/"),
        ("Random Girl Names", "/random-girl-names/"),
        ("Gender-Neutral Names", "/gender-neutral-names/"),
    ]),
    ("Fiction &amp; Places", [
        ("Character Names", "/random-name-for-character/"),
        ("Fantasy Names", "/fantasy-name-generator/"),
        ("Elf Names", "/elf-name-generator/"),
        ("Japanese Names", "/japanese-name-generator/"),
        ("City Names", "/city-name-generator/"),
        ("School Names", "/school-name-generator/"),
        ("Band Names", "/band-name-generator/"),
    ]),
    ("Usernames &amp; Tools", [
        ("Random Usernames", "/random-username-generator/"),
        ("Aesthetic Usernames", "/instagram-username-generator/"),
        ("Fake Name Generator", "/fake-name-generator/"),
        ("Random Name Wheel", "/random-name-wheel/"),
    ]),
    ("Site", [
        ("Home", "/"),
        ("Guides", "/guides/"),
        ("About", "/about/"),
        ("Contact", "/contact/"),
        ("Privacy Policy", "/privacy-policy/"),
        ("Terms of Service", "/terms/"),
        ("XML Sitemap", "/sitemap.xml"),
    ]),
]

BRAND_SVG = ('<svg class="brand-mark" width="28" height="28" viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
             '<rect width="28" height="28" rx="5" fill="#26344E"/><rect x="4" y="4" width="20" height="20" rx="2.5" fill="#F6F1E4"/>'
             '<text x="14" y="20" font-family="Georgia, serif" font-weight="700" font-size="15" text-anchor="middle" fill="#26344E">N</text>'
             '<circle cx="22" cy="6" r="3" fill="#A6392E"/></svg>')


def page_url(path):
    if path == "index.html":
        return "/"
    if path.endswith("/index.html"):
        return "/" + path[:-len("index.html")]
    return "/" + path


def header_html(url):
    items = []
    for label, href, prefixes in NAV:
        active = url in prefixes or (href == "/guides/" and url.startswith("/guides/"))
        cls = ' class="is-active" aria-current="page"' if url == href else (' class="is-active"' if active else "")
        items.append(f'        <li><a href="{href}"{cls}>{label}</a></li>')
    return (
        "<!-- shell:header -->\n"
        '<header class="site-header">\n'
        '  <div class="container">\n'
        f'    <a class="brand" href="/">{BRAND_SVG}<span>Names<span class="dot">&nbsp;</span>Unlimited</span></a>\n'
        '    <button class="nav-toggle" type="button" data-nav-toggle aria-label="Toggle menu" aria-expanded="false">Menu</button>\n'
        '    <ul class="nav-tabs" data-nav-tabs>\n' + "\n".join(items) + "\n    </ul>\n"
        "  </div>\n</header>\n<!-- /shell:header -->"
    )


def footer_html():
    cols = []
    for title, links in FOOTER_COLS:
        lis = "\n".join(f'          <li><a href="{h}">{l}</a></li>' for l, h in links)
        cols.append(f'        <div class="footer-col">\n          <p class="footer-h">{title}</p>\n          <ul>\n{lis}\n          </ul>\n        </div>')
    return (
        "<!-- shell:footer -->\n"
        '<footer class="site-footer">\n'
        '  <div class="container">\n'
        '    <div class="footer-top">\n'
        '      <div class="footer-about">\n'
        f'        <a class="brand" href="/">{BRAND_SVG}<span>Names<span class="dot">&nbsp;</span>Unlimited</span></a>\n'
        '        <p class="footer-desc">Free online name generators for writers, game masters, parents, developers and anyone who needs a name quickly. Names are generated in your browser.</p>\n'
        "      </div>\n"
        '      <nav class="footer-cols" aria-label="Footer">\n' + "\n".join(cols) + "\n      </nav>\n"
        "    </div>\n"
        '    <p class="footer-fine">&copy; 2026 Names Unlimited. Generated results are suggestions and may occasionally resemble real names or existing organizations.</p>\n'
        "  </div>\n</footer>\n<!-- /shell:footer -->"
    )


def meta_get(s, key):
    m = re.search(r'<meta\s+(?:name|property)="%s"\s+content="([^"]*)"' % re.escape(key), s)
    return m.group(1) if m else None


def set_meta(s, key, value, attr="name"):
    tag = f'<meta {attr}="{key}" content="{value}">'
    pat = re.compile(r'<meta\s+(?:name|property)="%s"\s+content="[^"]*"\s*/?>' % re.escape(key))
    if pat.search(s):
        return pat.sub(lambda m: tag, s, count=1)
    return s.replace("</head>", f"{tag}\n</head>", 1)


def process(path):
    s = open(path, encoding="utf-8").read()
    orig = s
    url = page_url(path)

    # ---- head basics (indexable pages only touch what exists / is missing)
    s = set_meta(s, "theme-color", THEME_COLOR)
    s = set_meta(s, "viewport", VIEWPORT)
    if re.search(r'name="robots"\s+content="[^"]*noindex', s) is None:
        title = meta_get(s, "og:title")
        if title is None:
            m = re.search(r"<title>([^<]*)</title>", s)
            title = html.escape(html.unescape(m.group(1))) if m else None
        desc = meta_get(s, "og:description") or meta_get(s, "description")
        if meta_get(s, "og:site_name") is None:
            s = set_meta(s, "og:site_name", "Names Unlimited", "property")
        if meta_get(s, "twitter:card") is None:
            s = set_meta(s, "twitter:card", "summary_large_image")
        if title and meta_get(s, "twitter:title") is None:
            s = set_meta(s, "twitter:title", title)
        if desc and meta_get(s, "twitter:description") is None:
            s = set_meta(s, "twitter:description", desc)

    # ---- shared stylesheet, loaded last
    if "/css/site-shell.css" not in s:
        links = list(re.finditer(r'<link[^>]*rel="stylesheet"[^>]*href="/css/[^"]+"[^>]*>', s))
        last = links[-1]
        s = s[: last.end()] + '\n<link rel="stylesheet" href="/css/site-shell.css">' + s[last.end():]

    # ---- header
    hdr = header_html(url)
    if "<!-- shell:header -->" in s:
        s = re.sub(r"<!-- shell:header -->.*?<!-- /shell:header -->", lambda m: hdr, s, count=1, flags=re.S)
    elif re.search(r'<header class="site-header">', s):
        s = re.sub(r'<header class="site-header">.*?</header>', lambda m: hdr, s, count=1, flags=re.S)
    elif re.search(r'<nav class="site-nav">', s):
        s = re.sub(r'<nav class="site-nav">.*?</nav>', lambda m: hdr, s, count=1, flags=re.S)
    else:
        print("!! no header found:", path)

    # ---- footer
    ftr = footer_html()
    if "<!-- shell:footer -->" in s:
        s = re.sub(r"<!-- shell:footer -->.*?<!-- /shell:footer -->", lambda m: ftr, s, count=1, flags=re.S)
    elif re.search(r'<footer class="site-footer">', s):
        s = re.sub(r'<footer class="site-footer">.*?</footer>', lambda m: ftr, s, count=1, flags=re.S)
    else:
        print("!! no footer found:", path)

    # ---- Google Fonts: load without blocking first paint (same pattern the other pages already use)
    s = re.sub(
        r'(?<!<noscript>)<link rel="stylesheet" href="(https://fonts\.googleapis\.com/css2[^"]+)">',
        lambda m: ('<link rel="preload" as="style" href="%s" onload="this.onload=null;this.rel=\'stylesheet\'">\n'
                   '<noscript><link rel="stylesheet" href="%s"></noscript>') % (m.group(1), m.group(1)),
        s)

    s = re.sub(r'<noscript><link rel="preload" as="style" href="([^"]+)"[^>]*></noscript>',
               lambda m: '<noscript><link rel="stylesheet" href="%s"></noscript>' % m.group(1), s)

    # ---- <main> landmark (pages that do not have one wrap everything between header and footer)
    if "<main" not in s:
        s = s.replace("<!-- /shell:header -->", '<!-- /shell:header -->\n<main id="main">', 1)
        s = s.replace("<!-- shell:footer -->", "</main>\n<!-- shell:footer -->", 1)

    # ---- nav script (mobile menu) on every page
    if "/js/nav.js" not in s:
        s = s.replace("</body>", '<script src="/js/nav.js" defer></script>\n</body>', 1)

    if s != orig:
        open(path, "w", encoding="utf-8").write(s)
        return True
    return False


def main():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    changed = 0
    for path in sorted(glob.glob("**/index.html", recursive=True)) + ["404.html"]:
        if process(path):
            changed += 1
    print(f"updated {changed} page(s)")


if __name__ == "__main__":
    main()
