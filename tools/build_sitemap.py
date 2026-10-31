#!/usr/bin/env python3
"""Regenerate sitemap.xml from the pages that actually exist.  Run from the repo root:
    python3 tools/build_sitemap.py            # lastmod = today
    python3 tools/build_sitemap.py 2026-10-31 # or give a date
A page is listed if <dir>/index.html exists and it is not noindex. The sitemap does not list itself."""
import datetime, glob, os, re, sys

BASE = "https://namesunlimited.github.io"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
lastmod = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()

def priority(url):
    if url == "/": return "1.0"
    if url.startswith("/guides/") and url != "/guides/": return "0.6"
    if url in ("/about/", "/contact/", "/privacy-policy/", "/terms/"): return "0.3"
    return "0.8"

urls = []
for f in ["index.html"] + sorted(glob.glob("*/index.html") + glob.glob("*/*/index.html")):
    s = open(f, encoding="utf-8").read()
    if re.search(r'name="robots"[^>]*noindex', s):
        continue
    url = "/" if f == "index.html" else "/" + f[: -len("index.html")]
    urls.append(url)

order = {"1.0": 0, "0.8": 1, "0.6": 2, "0.3": 3}
urls.sort(key=lambda u: (order[priority(u)], u != "/guides/", u))
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    out.append(f"  <url>\n    <loc>{BASE}{u}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>{priority(u)}</priority>\n  </url>")
out.append("</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"sitemap.xml: {len(urls)} URLs")
