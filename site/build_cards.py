"""Build the 1200x630 share cards (SVG, then PNG through a headless browser). Run: python3 build_cards.py"""

import base64
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/models.json").read_text())
MODELS = DATA["models"]
SNAP = DATA["snapshot"]


def quebec(m):
    return m["categories"]["quebec"]["score"]


best = max(MODELS, key=quebec)
open_small = [
    m
    for m in MODELS
    if m["kind"] == "open"
    and m["id"] != "RandomBaselineModel"
    and m["size_b"]
    and m["size_b"] <= 33
]
best_open = max(open_small, key=quebec)
TXT = {
    "en": {
        "head": "Who knows Québécois?",
        "fig": f"{quebec(best) * 100:.1f}",
        "cap": f"highest score on Quebec expressions and words ({best['label']})",
        "open": f"{quebec(best_open) * 100:.0f}",
        "opencap": "strongest model you can run yourself, up to 33 billion parameters",
        "foot": f"GRAAL, Université Laval | {len(MODELS)} models, 23 tests",
    },
    "fr": {
        "head": "Qui parle québécois ?",
        "fig": f"{quebec(best) * 100:.1f}".replace(".", ","),
        "cap": f"score le plus élevé sur les expressions et les mots du Québec ({best['label']})",
        "open": f"{quebec(best_open) * 100:.0f}",
        "opencap": "modèle le plus fort utilisable chez soi, jusqu’à 33 milliards de paramètres",
        "foot": f"GRAAL, Université Laval | {len(MODELS)} modèles, 23 tests",
    },
}


def svg(lang):
    t = TXT[lang]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="{t['head']} {t['fig']}">
<rect width="1200" height="630" fill="#0b2a5c"/>
<text x="64" y="110" font-family="Schibsted Grotesk, sans-serif" font-weight="800" font-size="40" fill="#ffffff">COLE</text>
<text x="64" y="200" font-family="Schibsted Grotesk, sans-serif" font-weight="800" font-size="64" fill="#ffffff">{t['head']}</text>
<text x="64" y="408" font-family="Schibsted Grotesk, sans-serif" font-weight="800" font-size="230" letter-spacing="-12" fill="#ffffff">{t['fig']}</text>
<text x="64" y="482" font-family="Schibsted Grotesk, sans-serif" font-weight="600" font-size="28" fill="#ffffff">{t['cap']}</text>
<rect x="64" y="510" width="6" height="52" fill="#f2a900"/>
<text x="88" y="540" font-family="Schibsted Grotesk, sans-serif" font-weight="800" font-size="34" fill="#f2a900">{t['open']}</text>
<text x="150" y="540" font-family="Schibsted Grotesk, sans-serif" font-weight="400" font-size="26" fill="#ffffff">{t['opencap']}</text>
<text x="64" y="602" font-family="Schibsted Grotesk, sans-serif" font-weight="400" font-size="20" fill="#c9d8f2">{t['foot']}</text>
</svg>"""


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    for lang in ("en", "fr"):
        s = svg(lang)
        (ROOT / f"cards/card-{lang}.svg").write_text(s)
        font = ROOT / "fonts"
        html = (
            "<style>"
            + "".join(
                f'@font-face{{font-family:"Schibsted Grotesk";font-weight:{w};src:url(data:font/ttf;base64,{base64.b64encode((font / f"SchibstedGrotesk-{w}.ttf").read_bytes()).decode()})}}'
                for w in (400, 600, 800)
            )
            + "html,body{margin:0}</style>"
            + s
        )
        pg.set_content(html)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(600)
        pg.screenshot(
            path=str(ROOT / f"cards/card-{lang}.png"),
            clip={"x": 0, "y": 0, "width": 1200, "height": 630},
        )
        print("card", lang)
    b.close()
