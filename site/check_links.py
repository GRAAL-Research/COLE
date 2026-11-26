"""Crawl every href/src/data-href in the generated pages: local targets must exist, anchors must resolve. Exit 1 on any failure."""

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
pages = sorted(ROOT.glob("*.html"))
ids = {p.name: set(re.findall(r'\bid="([^"]+)"', p.read_text())) for p in pages}
bad, n = [], 0
for p in pages:
    html = p.read_text()
    for attr, url in re.findall(r'\b(href|src)="([^"]*)"', html):
        if not url or url.startswith(
            ("http://", "https://", "mailto:", "data:", "javascript:")
        ):
            continue
        n += 1
        u = urlparse(url)
        target = u.path or p.name
        if not (ROOT / target).exists():
            bad.append(f"{p.name}: missing target {url}")
        elif (
            u.fragment
            and target.endswith(".html")
            and u.fragment not in ids.get(target, set())
        ):
            bad.append(f"{p.name}: missing anchor {url}")
print(f"link check: {len(pages)} pages, {n} local links, {len(bad)} broken")
for b in bad:
    print("  " + b)
sys.exit(1 if bad else 0)
