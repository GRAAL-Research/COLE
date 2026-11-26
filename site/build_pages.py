"""Generate the static HTML pages (shared header/footer, static fallbacks computed from data/models.json).

Run: python3 build_pages.py   (after build_models.py)
Both languages are written in the markup; CSS shows one (html[lang]).
"""

import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/models.json").read_text())
CATS = json.loads((ROOT / "data/categories.json").read_text())["categories"]
CREDITS = json.loads((ROOT / "assets/credits.json").read_text())
MODELS = DATA["models"]
BY_ID = {m["id"]: m for m in MODELS}
SNAP = DATA["snapshot"]
ART = json.loads((ROOT / "data/article.json").read_text())

DEFAULTS = [
    "claude-opus-4-20250514",
    "gpt-4o-2024-08-06",
    "unsloth/Qwen3-14B-unsloth-bnb-4bit",
    "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
    "unsloth/Llama-3.2-1B-Instruct-bnb-4bit",
    "RandomBaselineModel",
]


def nb(fr: str) -> str:
    """French typography: no-break space before ? ! : ; and » and after «."""
    fr = re.sub(r" ([?!:;»])", "\u00a0\\1", fr)
    return fr.replace("« ", "«\u00a0")


def bi(en: str, fr: str) -> str:
    return f'<span lang="en">{en}</span><span lang="fr">{nb(fr)}</span>'


def attrs(name: str, en: str, fr: str) -> str:
    """Attribute with both languages; app.js swaps it."""
    return f'{name}="{escape(en)}" data-i18n-attrs="{name}" data-en-{name}="{escape(en)}" data-fr-{name}="{escape(nb(fr))}"'


def lab(m, lang="en"):
    if m["id"] == "RandomBaselineModel":
        return bi("Random guessing", "Tirage au hasard")
    return escape(m["label"])


def n1(v, lang="en"):
    s = f"{v * 100:.1f}"
    return s.replace(".", ",") if lang == "fr" else s


def n1b(v):
    return bi(n1(v), n1(v, "fr"))


def q(m):
    return m["categories"]["quebec"]["score"]


# ---------- facts computed from the data (asserted, so copy cannot drift) ----------
best = max(MODELS, key=q)
local = [
    m
    for m in MODELS
    if m["kind"] == "open"
    and m["id"] != "RandomBaselineModel"
    and m["size_b"]
    and m["size_b"] <= 33
]
best_local = max(local, key=q)
BEST_LABEL = best["label"]
Q_BEST = round(
    q(best) * 100
)  # whole-number score of the strongest model on Quebec tests
Q_LOCAL = round(
    q(best_local) * 100
)  # same for the strongest model run on your own computer
RANDOM = BY_ID["RandomBaselineModel"]
N_OPEN = len(
    [m for m in MODELS if m["kind"] == "open" and m["id"] != "RandomBaselineModel"]
)
N_Q4 = len([m for m in MODELS if m["quantized_4bit"]])
N_MODELS = len(MODELS)  # every count of models shown on the pages comes from here
N_TESTS = len({t for c in CATS for t in c["tasks"]})
N_QUEBEC_TESTS = len(next(c for c in CATS if c["key"] == "quebec")["tasks"])
N_OTHER_TESTS = N_TESTS - N_QUEBEC_TESTS
assert sum(1 for m in DEFAULTS if q(BY_ID[m]) >= 0.5) == 2


_help_n = [0]


def HELP(en, fr, kind="chart", btn_id=""):
    """Small round '?' button with a closed popover (toggled by app.js)."""
    _help_n[0] += 1
    pid = f"help-pop-{_help_n[0]}"
    label = (
        ("How to read this chart", "Comment lire ce graphique")
        if kind == "chart"
        else ("How to read this table", "Comment lire ce tableau")
    )
    idattr = f' id="{btn_id}"' if btn_id else ""
    return (
        f'<span class="help" data-help><button type="button" class="help-btn"{idattr} aria-expanded="false" aria-controls="{pid}" '
        f'{attrs("aria-label", *label)} {attrs("title", *label)}><span aria-hidden="true">?</span></button>'
        f'<span id="{pid}" class="help-pop" role="note" hidden>{bi(en, fr)}</span></span>'
    )


def HOW(en, fr):
    return f'<details class="how"><summary>{bi("How to read this chart", "Comment lire ce graphique")}</summary><p>{bi(en, fr)}</p></details>'


def bars(ids, i0=0, plain=False):
    out = ['<ul class="bars" data-stagger>']
    for i, mid in enumerate(ids):
        m = BY_ID[mid]
        v = q(m)
        val = bi(f"{v * 100:.0f}", f"{v * 100:.0f}") if plain else n1b(v)
        out.append(
            f'<li class="bar-row" style="--i:{i}"><span class="bar-label">{lab(m)}</span>'
            f'<div class="bar-line"><span class="bar-track"><span class="bar-fill" style="--w:{v * 100:.1f}%"></span></span>'
            f'<span class="bar-val">{val}</span></div></li>'
        )
    out.append("</ul>")
    return "".join(out)


def img(file, alt_en, alt_fr, extra=""):
    return f'<img src="assets/{file}" {attrs("alt", alt_en, alt_fr)} loading="lazy" decoding="async" {extra}>'


def mask(en1, fr1, en2=None, fr2=None, tag="h1", cls="display hero-title"):
    lines = f'<span class="mask-line"><span>{bi(en1, fr1)}</span></span>'
    if en2:
        lines += f'<span class="mask-line"><span>{bi(en2, fr2)}</span></span>'
    return f'<{tag} class="{cls} mask-block">{lines}</{tag}>'


STEPS = [
    (
        "model.html",
        "Model sheet",
        "Fiche d’un modèle",
        "model",
        "Look up one model: its rank and where it is strong.",
        "Consulter un modèle : son rang et ses points forts.",
        "Go further: compare this model with others",
        "Aller plus loin : comparer ce modèle avec d’autres",
    ),
    (
        "choose-a-model.html",
        "Compare models",
        "Comparer des modèles",
        "compare",
        "Put 2 to 6 models side by side, skill by skill.",
        "Placer de 2 à 6 modèles côte à côte, compétence par compétence.",
        "Go further: see every model and every test",
        "Aller plus loin : voir tous les modèles et tous les tests",
    ),
    (
        "all-results.html",
        "All results",
        "Tous les résultats",
        "results",
        f"Sort and filter the full table of {N_MODELS} models and {N_TESTS} tests.",
        f"Trier et filtrer le tableau complet des {N_MODELS} modèles et des {N_TESTS} tests.",
        "Next step: explore the results in pictures",
        "Étape suivante : explorer les résultats en images",
    ),
    (
        "explore.html",
        "Explore",
        "Explorer",
        "explore",
        "Visual tools: Quebec against other French tests, heatmap, size against score, a quiz.",
        "Outils visuels : Québec contre autres tests en français, carte de chaleur, taille contre score, quiz.",
        "",
        "",
    ),
]
SECONDARY = [
    ("level-3.html#article", "Article", "Article", "paper"),
    ("level-3.html#protocol", "Methodology", "Méthodologie", None),
    ("plain-language.html", "Poster", "Affiche", "plain"),
]


def header(page: str, ground: str = "") -> str:
    """The same markup on every page; only aria-current changes."""
    steps = ""
    for href, en, fr, key, *_ in STEPS:
        cur = ' aria-current="page"' if key == page else ""
        steps += f'<li><a href="{href}" data-carry{cur}>{bi(en, fr)}</a></li>'
    sec = ""
    for href, en, fr, key in SECONDARY:
        cur = ' aria-current="page"' if key == page else ""
        sec += f'<li><a href="{href}"{cur}>{bi(en, fr)}</a></li>'
    return f"""<header class="site-header {ground}">
<div class="wrap bar">
<a class="wordmark" href="index.html" {attrs("aria-label", "COLE, home", "COLE, accueil")}>COLE</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav-links">{bi("Menu", "Menu")}</button>
<div id="nav-links" class="nav-links">
<nav class="nav-main" {attrs("aria-label", "Main", "Principale")}><ol class="nav-journey" {attrs("aria-label", "Journey, four steps", "Parcours, quatre étapes")}>{steps}</ol></nav>
<div class="nav-right">
<ul class="nav-secondary" {attrs("aria-label", "About the project", "À propos du projet")}>{sec}</ul>
<div class="lang" role="group" {attrs("aria-label", "Language", "Langue")}><button type="button" data-lang="fr" lang="fr" aria-label="Français" aria-pressed="true">FR</button><button type="button" data-lang="en" lang="en" aria-label="English" aria-pressed="false">EN</button></div>
<button class="btn btn-sm" type="button" data-open-contact>{bi("Contact", "Contact")}</button>
</div>
</div>
</div>
</header>"""


def crumbs(*items) -> str:
    """Breadcrumb under the header. items: (href|None, en, fr); the last one is the current page."""
    lis = ""
    path = [("index.html", "Home", "Accueil")] + list(items)
    for i, (href, en, fr) in enumerate(path):
        if i == len(path) - 1:
            lis += f'<li><span aria-current="page">{bi(en, fr)}</span></li>'
        else:
            lis += f'<li><a href="{href}">{bi(en, fr)}</a></li>'
    return f'<nav class="crumbs wrap" {attrs("aria-label", "Breadcrumb", "Fil d’Ariane")}><ol>{lis}</ol></nav>'


def stepbar(cur: str) -> str:
    """Compact journey bar: done, current, next."""
    keys = [s[3] for s in STEPS]
    ci = keys.index(cur)
    lis = ""
    for i, (href, en, fr, key, *_) in enumerate(STEPS):
        st = "done" if i < ci else "current" if i == ci else "next"
        word = {
            "done": bi("done", "fait"),
            "current": bi("current step", "étape en cours"),
            "next": bi("next", "à venir"),
        }[st]
        mark = (
            '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7.5l3.2 3.2L12 3.5" style="fill:none;stroke:currentColor;stroke-width:2.5"/></svg>'
            if st == "done"
            else str(i + 1)
        )
        c = ' aria-current="step"' if st == "current" else ""
        lis += f'<li class="is-{st}"><a href="{href}" data-carry{c}><span class="step-n" aria-hidden="true">{mark}</span><span class="step-t">{bi(en, fr)}</span><span class="vh"> ({word})</span></a></li>'
    return f'<nav class="stepbar wrap" {attrs("aria-label", "Journey", "Parcours")}><p class="small strong stepbar-title">{bi("Journey", "Parcours")}</p><ol>{lis}</ol></nav>'


CTA = {
    "model": ("Compare this model", "Comparer ce modèle"),
    "compare": ("See all results", "Voir tous les résultats"),
    "results": ("Explore the results", "Explorer les résultats"),
}


def suite(cur: str) -> str:
    """Bottom block: ONE primary next action (a card to the next step), the previous step as a quiet link."""
    i = [s[3] for s in STEPS].index(cur)
    if i < len(STEPS) - 1:
        n = STEPS[i + 1]
        card = f'<a class="suite-card" href="{n[0]}" data-carry><span class="small strong">{bi("Next step", "Étape suivante")}</span><span class="suite-t">{bi(n[1], n[2])}</span><span>{bi(n[4], n[5])}</span><span class="btn suite-btn" aria-hidden="true">{bi(CTA[cur][0], CTA[cur][1])} →</span></a>'
    else:
        card = f'<a class="suite-card" href="model.html"><span class="small strong">{bi("Back to the start", "Retour au début")}</span><span class="suite-t">{bi("Pick another model", "Choisir un autre modèle")}</span><span>{bi(STEPS[0][4], STEPS[0][5])}</span><span class="btn suite-btn" aria-hidden="true">{bi("Pick a model", "Choisir un modèle")} →</span></a>'
    prev = ""
    if i > 0:
        p = STEPS[i - 1]
        prev = f'<p class="suite-prev"><a href="{p[0]}" data-carry>{bi("Previous step: ", "Étape précédente : ")}{bi(p[1], p[2])}</a></p>'
    return f'<section class="suite ground-tint" aria-labelledby="suite-title"><div class="wrap"><h2 id="suite-title" class="vh">{bi("Next step", "Étape suivante")}</h2>{card}{prev}</div></section>'


LIC_FR = {"public domain": "domaine public", "CC0": "CC0"}
CREATOR_FR = {
    "Stadanus, Ioan, auteur du modèle": "Stadanus, Ioan, auteur du modèle",
    "Dennison (based on the mark on the other version)": "Dennison (d’après la marque de l’autre version)",
}


NBSP = "\u00a0"
SHORT_TITLE = {
    "assets/market-quebec-1903.jpg": (
        "Champlain Market, Quebec",
        "Marché Champlain, Québec",
    ),
    "assets/champlain-map-1612.jpg": (
        "Champlain’s map of New France",
        "Carte de la Nouvelle-France, Champlain",
    ),
    "assets/type-case-1878.jpg": ("French type case", "Casse française"),
    "assets/printing-house-16c.jpg": (
        "Inside a 16th-century print shop",
        "Vue intérieure d’une imprimerie au XVIe siècle",
    ),
    "assets/postcard-sous-le-cap.jpg": ("Québec, Sous-le-Cap", "Québec, Sous-le-Cap"),
}
DEFAULT_LICENSE = "public domain"


def credits_html() -> str:
    """Collapsed image credits. Source of truth: assets/credits.json (one link per image, licence stated once)."""
    items = ""
    for c in CREDITS:
        en, fr = SHORT_TITLE.get(c["file"], (c["title"], c["title"]))
        note = ""
        if c["license"] != DEFAULT_LICENSE:
            note = f'{NBSP}({escape(c["license"])})'
        items += (
            f'<li><a href="{c["page"]}">{bi(escape(en), escape(fr))}</a>{note}</li>'
        )
    lead = bi(
        "Greyscale images from Wikimedia Commons. All in the public domain, except where noted.",
        "Images en niveaux de gris, Wikimedia Commons. Toutes du domaine public, sauf mention.",
    )
    return (
        f'<details class="credits"><summary>{bi("Image credits", "Crédits des images")}</summary>'
        f"<p>{lead}</p><ul>{items}</ul></details>"
    )


def footer() -> str:
    return f"""<footer class="site-footer ground-deep">
<div class="wrap">
<div class="footer-grid">
<p class="small zone-note" data-reveal>{bi("COLE is a GRAAL research project, Université Laval, Quebec.", "COLE est un projet de recherche du GRAAL, Université Laval, Québec.")}</p>
<div class="stack">
<ul class="footer-links" data-reveal>
<li><a href="level-3.html">{bi("Article", "Article")}</a></li>
<li><a href="plain-language.html">{bi("Poster", "Affiche")}</a></li>
<li><a href="https://github.com/GRAAL-Research/COLE">GitHub</a></li>
</ul>
{credits_html()}
</div>
</div>
</div>
</footer>
<dialog id="contact-dialog" aria-labelledby="contact-title">
<div class="dlg">
<h2 id="contact-title">{bi("Contact", "Contact")}</h2>
<p>{bi("To ask for an evaluation of your model, open an issue on the project’s GitHub page. We do not promise a delay, and each dated model version is evaluated once.", "Pour demander l’évaluation de votre modèle, ouvrez une demande sur la page GitHub du projet. Aucun délai n’est promis, et chaque version datée d’un modèle est évaluée une seule fois.")}</p>
<p><a class="btn" href="https://github.com/GRAAL-Research/COLE/issues/new">{bi("Open an issue", "Ouvrir une demande")}</a></p>
<p><button class="link-btn" type="button" data-close>{bi("Close", "Fermer")}</button></p>
</div>
</dialog>"""


SITE_URL = "https://colebenchmark.org"
OG_TITLE_FR = "COLE : quelle IA comprend le français québécois ?"
OG_DESC_FR = f"COLE : {N_MODELS} modèles de langage, {N_TESTS} tests en français."


def name_to_file(name):
    files = {
        "home": "",
        "model": "model.html",
        "compare": "choose-a-model.html",
        "results": "all-results.html",
        "explore": "explore.html",
        "plain": "plain-language.html",
        "paper": "level-3.html",
    }
    return files.get(name, name + ".html")


def page(name, title_en, title_fr, body, ground_header="", scripts=(), extra_head=""):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title data-en="{escape(title_en)}" data-fr="{escape(title_fr)}">{escape(title_fr)}</title>
<meta name="description" content="Évaluation de {N_MODELS} modèles de langage sur {N_TESTS} tests de compréhension du français, dont le français québécois.">
<meta property="og:site_name" content="COLE">
<meta property="og:locale" content="fr_CA">
<meta property="og:locale:alternate" content="en_CA">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/{name_to_file(name)}">
<meta property="og:title" content="{escape(OG_TITLE_FR)}">
<meta property="og:description" content="{escape(OG_DESC_FR)}">
<meta property="og:image" content="{SITE_URL}/cards/card-fr.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Carte de partage COLE : trois chiffres tirés des résultats.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(OG_TITLE_FR)}">
<meta name="twitter:description" content="{escape(OG_DESC_FR)}">
<meta name="twitter:image" content="{SITE_URL}/cards/card-fr.png">
<link rel="icon" href="data:,">
<link rel="stylesheet" href="tokens.css">
<link rel="preload" href="fonts/SchibstedGrotesk-800.ttf" as="font" type="font/ttf" crossorigin>
{extra_head}
</head>
<body data-page="{name}">
<a class="skip" href="#main">{bi("Skip to content", "Aller au contenu")}</a>
{body}
<script src="app.js"></script>
<script src="data.js"></script>
{"".join(f'<script src="{s}"></script>' for s in scripts)}
</body>
</html>
"""


def cat_label(c, lang):
    return c["label"][lang]


# ---------- tables ----------
def static_table(models, caption_en, caption_fr, cols_two=False):
    d = "{:.2f}" if cols_two else None
    h = f'<div class="table-scroll" tabindex="0" role="region" {attrs("aria-label", caption_en, caption_fr)}><table class="data"><caption>{bi(caption_en, caption_fr)}</caption><thead><tr>'
    h += f'<th scope="col" class="sticky-1">{bi("Rank", "Rang")}</th><th scope="col" class="l sticky-2">{bi("Model", "Modèle")}</th><th scope="col">{bi("Overall", "Général")}<span class="unit">(%)</span></th>'
    for c in CATS:
        h += f'<th scope="col">{bi(c["short"]["en"], c["short"]["fr"])}<span class="unit">(%)</span></th>'
    h += "</tr></thead><tbody>"
    for m in models:
        h += f'<tr><td class="sticky-1">{m["rank"]}</td><th scope="row" class="l sticky-2">{lab(m)}</th><td>{n1(m["overall"])}</td>'
        for c in CATS:
            v = m["categories"][c["key"]]["score"]
            h += f'<td>{n1(v) if v is not None else "n/a"}</td>'
        h += "</tr>"
    return h + "</tbody></table></div>"


# ---------- index ----------
def index():
    journey_items = "".join(
        f'<li data-reveal><a class="format-row" href="{h}"><span class="step-n" aria-hidden="true">{i + 1}</span><h3>{bi(en, fr)}</h3><p>{bi(pe, pf)}</p></a></li>'
        for i, (h, en, fr, k, pe, pf, *_) in enumerate(STEPS)
    )
    skills = ""
    for i, c in enumerate(CATS):
        n = len(c["tasks"])
        skills += f"""<div data-reveal style="--i:{i % 2}"><h3 class="strong lead">{bi(c["label"]["en"], c["label"]["fr"])}</h3>
<p>{bi(escape(c["plain"]["en"]), escape(c["plain"]["fr"]))}</p>
<p class="small muted">{bi(f"{n} tests", f"{n} tests")}</p></div>"""
    body = f"""{header("home")}
<main id="main">
<section class="hero ground-deep" aria-labelledby="hero-title">
<div class="wrap hero-grid">
{mask("Who knows", "Qui parle", "Québécois?", "québécois&nbsp;?").replace('<h1 class="display hero-title mask-block">', '<h1 id="hero-title" class="display hero-title mask-block">')}
<div class="hero-talk" data-stagger>
<p data-reveal>{bi(f"We tested {N_MODELS} AI models on {N_TESTS} French tests. Here is who understands Quebec.", f"Nous avons testé {N_MODELS} modèles d’IA sur {N_TESTS} tests en français. Voici lesquels comprennent le Québec.")}</p>
<a class="btn" data-reveal href="model.html">{bi("Look up a model", "Consulter un modèle")}</a>
</div>
<div class="hero-pic">
<div class="hero-block" data-reveal><b>{n1b(q(best))}</b><span>{bi(f"% highest of {N_MODELS} models on Quebec expressions and words: {BEST_LABEL}", f"% score le plus élevé parmi {N_MODELS} modèles sur les expressions et les mots du Québec : {BEST_LABEL}")}</span></div>
<div class="pic">{img("market-quebec-1903.jpg", "Illustrated postcard of the Champlain Market in Quebec City, around 1903: carts, vegetable sellers and tall stone houses.", "Carte postale illustrée du marché Champlain à Québec, vers 1903 : charrettes, marchands de légumes et hautes maisons de pierre.", 'style="object-position:50% 70%" fetchpriority="high"').replace('loading="lazy"', '')}</div>
</div>
</div>
</section>

<section class="section ground-tint" aria-labelledby="journey-title" >
<div class="wrap axis">
<div class="zone-note" data-reveal><p class="small strong">{bi("Journey", "Parcours")}</p></div>
<div class="axis-main stack-lg">
<h2 id="journey-title" class="head" data-reveal>{bi("Four steps, one path", "Quatre étapes, un seul chemin")}</h2>
<p class="lead col-text" data-reveal>{bi("Start from one model, then widen. The model you pick follows you from step to step.", "Partez d’un modèle, puis élargissez. Le modèle choisi vous suit d’une étape à l’autre.")}</p>
<ol class="journey-steps" data-stagger>{journey_items}</ol>
</div>
</div>
</section>

<section class="section" aria-labelledby="formats-title">
<div class="wrap axis">
<div class="zone-note" data-reveal><div class="pic pic-tall">{img("type-case-1878.jpg", "A page from a French printer’s catalogue showing a type case, the wooden tray where each letter has its box.", "Une page d’un catalogue d’imprimeur français montrant une casse, le casier de bois où chaque lettre a sa case.", 'style="object-position:50% 20%"')}</div></div>
<div class="axis-main stack-lg">
<h2 id="formats-title" class="head" data-reveal>{bi("One study, three formats", "Une étude, trois formats")}</h2>
<p class="lead col-text" data-reveal>{bi("Pick the format that fits how you read.", "Choisissez le format qui convient à votre façon de lire.")}</p>
<div class="formats" data-stagger>
<a class="format-row" href="plain-language.html" data-reveal><h3>{bi("The poster", "L’affiche")}</h3><p><span class="for">{bi("For everyone", "Pour tout le monde")}</span><br>{bi("The essentials on one page: one question, one plain answer, six bars on one skill.", "L’essentiel en une page : une question, une réponse simple, six barres sur une compétence.")}</p><span class="go">{bi("Read the poster", "Lire l’affiche")}</span></a>
<a class="format-row" href="choose-a-model.html" data-reveal><h3>{bi("The data sheet", "La fiche de données")}</h3><p><span class="for">{bi("For people who must choose", "Pour celles et ceux qui doivent choisir")}</span><br>{bi("Pick 2 to 6 models and compare them on seven skills, as a radar plate and a table.", "Choisissez de 2 à 6 modèles et comparez-les sur sept compétences, en radar et en tableau.")}</p><span class="go">{bi("Open the data sheet", "Ouvrir la fiche")}</span></a>
<a class="format-row" href="level-3.html" data-reveal><h3>{bi("The article", "L’article")}</h3><p><span class="for">{bi("For researchers", "Pour la recherche")}</span><br>{bi(f"The accepted paper, the protocol, the {N_TESTS} tasks and every score to two decimals.", f"L’article accepté, le protocole, les {N_TESTS} tâches et chaque score à deux décimales.")}</p><span class="go">{bi("Open the article page", "Ouvrir la page de l’article")}</span></a>
</div>
</div>
</div>
</section>

<section class="section ground-blue" aria-labelledby="live-title">
<div class="wrap axis">
<div class="zone-note"></div>
<div class="axis-main stack-lg">
<h2 id="live-title" class="head" data-reveal>{bi("Quebec expressions, model by model", "Les expressions québécoises, modèle par modèle")}</h2>
<p class="lead col-text" data-reveal>{bi(f"Six models on the two Quebec tests. Guessing at random scores {n1(q(RANDOM))}.", f"Six modèles sur les deux tests québécois. Le hasard obtient {n1(q(RANDOM), 'fr')}.")}</p>
<p class="small strong" data-reveal>{bi("Correct answers (%)", "Réponses justes (%)")}</p>
{bars(DEFAULTS)}
<p data-reveal><a class="link-btn" href="choose-a-model.html">{bi("Compare models, 2 to 6 at a time", "Comparer des modèles, de 2 à 6 à la fois")}</a></p>
</div>
</div>
</section>

<section class="section" aria-labelledby="skills-title">
<div class="wrap axis">
<div class="zone-note" data-reveal><div class="pic" style="aspect-ratio:4/5">{img("printing-house-16c.jpg", "Engraving of a sixteenth-century printing house: compositors set type while a pressman works the press.", "Gravure d’une imprimerie du XVIe siècle : des compositeurs assemblent les caractères pendant qu’un imprimeur actionne la presse.", 'style="object-position:62% 50%"')}</div></div>
<div class="axis-main stack-lg">
<h2 id="skills-title" class="head" data-reveal>{bi("Seven skills, in plain words", "Sept compétences, en mots simples")}</h2>
<div class="cols-2">{skills}</div>
<p data-reveal><a class="link-btn" href="level-3.html#protocol">{bi("How the scores are computed", "Comment les scores sont calculés")}</a></p>
</div>
</div>
</section>

<section class="section ground-tint" aria-labelledby="snap-title">
<div class="wrap axis">
<div class="zone-note stats note-after" data-stagger>
<div class="stat" data-reveal><b>{N_MODELS}</b><span>{bi("models evaluated", "modèles évalués")}</span></div>
<div class="stat" data-reveal><b>{N_TESTS}</b><span>{bi("tests in French", "tests en français")}</span></div>
</div>
<div class="axis-main stack-lg">
<h2 id="snap-title" class="head" data-reveal>{bi("What this snapshot holds", "Ce que contient cet instantané")}</h2>
<div class="stack col-text lead" data-reveal>
<p>{bi(f"Scores follow the protocol of the COLE paper, taken from colebenchmark.org. Newer models are not in yet, for example Claude Sonnet 4.5, GPT-5.1 and Gemini 3 Pro.", f"Les scores suivent le protocole de l’article COLE, repris de colebenchmark.org. Les modèles plus récents n’y sont pas encore, par exemple Claude Sonnet 4.5, GPT-5.1 et Gemini 3 Pro.")}</p>
<p>{bi("A test a model did not take is left empty, never counted as zero. Planned next: a second protocol that re-runs every model, with these entries kept as an archive.", "Un test que le modèle n’a pas passé reste vide, jamais compté comme zéro. Prévu ensuite : un second protocole qui réévalue chaque modèle, ces entrées restant en archive.")}</p>
</div>
</div>
</div>
</section>

<section class="section ground-deep" aria-labelledby="close-title" style="padding-bottom:0">
<div class="wrap closing-grid">
<div class="closing-talk" data-stagger>
<h2 id="close-title" class="head" data-reveal>{bi("Is your model missing?", "Il manque votre modèle ?")}</h2>
<p class="lead" data-reveal>{bi("Ask for an evaluation with the contact button. No delay is promised.", "Demandez une évaluation avec le bouton de contact. Aucun délai n’est promis.")}</p>
<button class="btn" type="button" data-open-contact data-reveal>{bi("Contact", "Contact")}</button>
</div>
<div class="pic" style="aspect-ratio:16/8">{img("champlain-map-1612.jpg", "Samuel de Champlain’s 1612 map of New France, with the St. Lawrence river, compass roses and drawings of people and animals.", "Carte de la Nouvelle-France de Samuel de Champlain, 1612, avec le fleuve Saint-Laurent, des roses des vents et des dessins de personnes et d’animaux.", 'style="object-position:50% 0"')}</div>
</div>
</section>
</main>
{footer()}"""
    return page(
        "home",
        "COLE: which AI understands Quebec French?",
        "COLE : quelle IA comprend le français québécois ?",
        body,
    )


# ---------- step 1: model sheet ----------
def model():
    m0 = BY_ID["claude-opus-4-20250514"]
    rows = "".join(
        f'<tr><th scope="row" class="l">{bi(c["label"]["en"], c["label"]["fr"])}</th><td>{n1b(m0["categories"][c["key"]]["score"])}</td></tr>'
        for c in CATS
    )
    static = f"""<div class="stack" id="sheet-static"><h2 class="head">{lab(m0)}</h2>
<p class="lead">{bi(f"Rank {m0['rank']} of {N_MODELS}, overall score {n1(m0['overall'])} %.", f"Rang {m0['rank']} sur {N_MODELS}, score général {n1(m0['overall'], 'fr')} %.")}</p>
<div class="table-scroll" tabindex="0" role="region" {attrs("aria-label", "Skills of the model", "Compétences du modèle")}><table class="data"><caption>{bi("Score per skill, in percent.", "Score par compétence, en pourcentage.")}</caption><thead><tr><th scope="col" class="l">{bi("Skill", "Compétence")}</th><th scope="col">{bi("Score", "Score")}<span class="unit">(%)</span></th></tr></thead><tbody>{rows}</tbody></table></div></div>"""
    body = f"""{header("model")}
{crumbs((None, "Model sheet", "Fiche d’un modèle"))}
<main id="main">
<section class="section" style="padding-block:calc(var(--pad-section) * 0.5)" aria-labelledby="page-title">
<div class="wrap stack-lg">
{mask("Model sheet", "Fiche d’un modèle", cls="display").replace('<h1 class="display mask-block">', '<h1 id="page-title" class="display mask-block">')}
<div class="axis" style="margin-top:1.5rem"><div class="zone-note"></div><div class="stack" data-stagger>
<p class="lead col-text" data-reveal>{bi("Start from one model. See where it is strong.", "Partez d’un modèle. Voyez où il est fort.")}</p>
</div></div>
</div>
</section>

<section class="section ground-deep sheet" aria-labelledby="sheet-title" style="padding-block:calc(var(--pad-section) * 0.6)">
<div class="wrap stack-lg">
<h2 id="sheet-title" class="vh">{bi("The model", "Le modèle")}</h2>
<div class="picker"><label class="strong" for="m-pick">{bi("Model", "Modèle")}</label><select id="m-pick" class="select" data-needs-data disabled></select><p class="vh" id="m-live" role="status" aria-live="polite"></p></div>
<div id="sheet-host" aria-live="polite" aria-busy="true">{static}</div>
</div>
</section>
</main>
{suite("model")}
{footer()}"""
    return page(
        "model",
        "Model sheet | COLE",
        "Fiche d’un modèle | COLE",
        body,
        scripts=("model.js",),
    )


# ---------- step 4: explore ----------
EXTRA = json.loads((ROOT / "data/extra.json").read_text())


def _explore_notes():
    """Counts and task lists used in the Explore how-to-read notes (computed from the data, never typed)."""
    cats = json.loads((ROOT / "data/categories.json").read_text())
    chance = json.loads((ROOT / "data/extra.json").read_text())["chance"]
    names = cats["task_names"]
    no_chance = [
        k
        for k, v in chance.items()
        if v["basis"] != "random-baseline" or v["value"] is None
    ]
    en = (
        "No tick for "
        + ", ".join(names[k]["name"] for k in no_chance)
        + ": for these, guessing is not a meaningful reference (correlations and free-text answers); they come last."
    )
    fr = (
        "Pas de repère pour "
        + ", ".join(names[k]["name"] for k in no_chance)
        + " : le hasard n’y est pas une référence utile (corrélations et réponses libres) ; elles viennent en dernier."
    )
    unknown = sum(
        1
        for m in DATA["models"]
        if m["id"] != "RandomBaselineModel" and m["kind"] not in ("open", "api")
    )
    return en, fr, unknown


HARD_NOTE_EN, HARD_NOTE_FR, UNKNOWN_ACCESS = _explore_notes()
HAS_UNRELIABLE = any(
    m.get("unreliable_tasks") for m in DATA["models"]
)  # false while the n.d. rule is off
NA_EN = (
    " n/a: evaluation not reliable for this model on this task, under verification."
    if HAS_UNRELIABLE
    else ""
)
NA_FR = (
    " n.d. : évaluation non fiable pour ce modèle sur cette épreuve, en cours de vérification."
    if HAS_UNRELIABLE
    else ""
)


def explore():
    def sec(i, ground, title, lead, how, host, anchor):
        dc = " data-chart" if ground == "ground-deep" else ""
        return f"""<section id="{anchor}" class="section {ground}"{dc} aria-labelledby="{anchor}-title" style="padding-block:calc(var(--pad-section) * 0.6)">
<div class="wrap stack-lg">
<div class="head-row" data-reveal><h2 id="{anchor}-title" class="head">{title}</h2>{HELP(*how)}</div>
<p class="lead col-text" data-reveal>{lead}</p>
<div id="{host}" aria-busy="true"><noscript><p>{bi("This chart needs JavaScript. The same numbers are in the table of all results.", "Ce graphique demande JavaScript. Les mêmes chiffres sont dans le tableau de tous les résultats.")} <a href="all-results.html">{bi("All results", "Tous les résultats")}</a></p></noscript></div>
</div>
</section>"""

    secs = "".join(
        [
            sec(
                1,
                "ground-deep",
                bi(
                    "Quebec tests against other French tests",
                    "Tests québécois contre autres tests en français",
                ),
                bi(
                    "Does a model do as well on Quebec French as on French in general?",
                    "Un modèle réussit-il aussi bien le français québécois que le français en général ?",
                ),
                (
                    "One line per model. The first mark is its average on the two Quebec tests, the second its average on the other French tests. The farther apart the marks, the bigger the difference.",
                    "Une ligne par modèle. Le premier repère est sa moyenne sur les deux tests québécois, le second sa moyenne sur les autres tests en français. Plus les repères sont éloignés, plus la différence est grande.",
                ),
                "x1",
                "quebec",
            ),
            sec(
                2,
                "ground-deep",
                bi("Above chance?", "Au-dessus du hasard ?"),
                bi(
                    "A test with two answers is passed half the time by guessing. This shows how far a model is from guessing.",
                    "Un test à deux réponses est réussi une fois sur deux au hasard. Voici la distance entre un modèle et le hasard.",
                ),
                (
                    "The bar is the model’s score. The gold tick is the score of the project’s random-guessing model on the same test. Two tests have no tick because their score is a correlation, not a share of right answers.",
                    "La barre est le score du modèle. Le repère doré est le score du modèle de tirage au hasard du projet sur le même test. Deux tests n’ont pas de repère, car leur score est une corrélation et non une part de réponses justes.",
                ),
                "x2",
                "chance",
            ),
            sec(
                8,
                "ground-deep",
                bi("The hardest tasks", "Les épreuves les plus difficiles"),
                bi(
                    "Against guessing, where do the strongest and the typical model stand?",
                    "Face au hasard, où se situent le modèle le plus fort et le modèle typique ?",
                ),
                (
                    f"One row per task, grouped by skill, the closest to guessing first. The gold tick is the score of random guessing, the circle the strongest model, the square the median model. A bold name means the median model is within 5 points of guessing. {HARD_NOTE_EN}",
                    f"Une ligne par épreuve, regroupées par compétence, les plus proches du hasard d’abord. Le repère doré est le score du tirage au hasard, le rond le modèle le plus fort, le carré le modèle médian. Un nom en gras signale que le modèle médian est à moins de 5 points du hasard. {HARD_NOTE_FR}",
                ),
                "x8",
                "hard",
            ),
            sec(
                3,
                "ground-tint",
                bi("Heatmap", "Carte de chaleur"),
                bi(
                    "Every model, every skill, one tone per band of scores.",
                    "Chaque modèle, chaque compétence, un ton par tranche de scores.",
                ),
                (
                    "Darker means a higher score. The value is printed in each cell. Hatched cells have no result. Press a column title to sort.",
                    "Plus c’est foncé, plus le score est élevé. La valeur est inscrite dans chaque case. Les cases hachurées n’ont pas de résultat. Appuyez sur un titre de colonne pour trier.",
                ),
                "x3",
                "heatmap",
            ),
            sec(
                4,
                "ground-deep",
                bi("Size against score", "Taille contre score"),
                bi(
                    "Does a bigger model score higher?",
                    "Un modèle plus gros obtient-il un score plus fort ?",
                ),
                (
                    "Each mark is a model. Left to right is its size on a log scale, bottom to top its score. Models whose size is not published are in the strip on the right.",
                    "Chaque repère est un modèle. De gauche à droite, sa taille sur une échelle logarithmique ; de bas en haut, son score. Les modèles dont la taille n’est pas publiée sont dans la bande de droite.",
                ),
                "x4",
                "size",
            ),
            sec(
                9,
                "ground-deep",
                bi("Open weights against API", "Poids ouverts contre API"),
                bi(
                    "Do models with open weights trail the ones served through an API?",
                    "Les modèles à poids ouverts sont-ils moins forts que ceux servis par API ?",
                ),
                (
                    f"One block per skill. Each mark is a model: circles are open-weight models, squares are models served through an API. The white bar is the median of each group. The random-guessing model is left out. Models with unknown access: {UNKNOWN_ACCESS}, so none is left out of a group.",
                    f"Un bloc par compétence. Chaque repère est un modèle : les ronds sont les modèles à poids ouverts, les carrés ceux servis par API. La barre blanche est la médiane de chaque groupe. Le modèle de tirage au hasard est exclu. Modèles à accès inconnu : {UNKNOWN_ACCESS}, donc aucun n’est laissé hors d’un groupe.",
                ),
                "x7",
                "access",
            ),
            sec(
                5,
                "ground-tint",
                bi("Would you pass?", "Réussiriez-vous ?"),
                bi(
                    "Four real questions from the public data of the tests. Answer, then check.",
                    "Quatre vraies questions tirées des données publiques des tests. Répondez, puis vérifiez.",
                ),
                (
                    "The questions come from the public training and validation parts of the data, with the answer given by the dataset. Models are not tested on these four questions here: the scores shown at the end are for the whole test.",
                    "Les questions viennent des parties publiques d’entraînement et de validation des données, avec la réponse du jeu de données. Les modèles ne sont pas testés ici sur ces quatre questions : les scores affichés à la fin portent sur le test entier.",
                ),
                "x5",
                "quiz",
            ),
            sec(
                7,
                "ground-deep",
                bi("Progress over time", "Progrès dans le temps"),
                bi(
                    "The highest score reached so far, by month, among models whose name carries a date.",
                    "Le score le plus élevé atteint jusqu’ici, mois par mois, parmi les modèles dont le nom porte une date.",
                ),
                (
                    "The step goes up each time a dated model beats every earlier one. The vertical axis starts at the lowest score shown, not at zero.",
                    "L’escalier monte chaque fois qu’un modèle daté dépasse tous les précédents. L’axe vertical commence au plus bas score affiché, pas à zéro.",
                ),
                "x6",
                "time",
            ),
        ]
    )
    card = f"""<section id="card" class="section" aria-labelledby="card-title" style="padding-block:calc(var(--pad-section) * 0.6)">
<div class="wrap axis">
<div class="zone-note"><picture><img class="card-prev" src="cards/card-en.svg" {attrs("alt", "Share card: the highest Quebec score, the strongest open model and the date of the data.", "Carte de partage : le score québécois le plus élevé, le modèle ouvert le plus fort et la date des données.")} width="1200" height="630" loading="lazy"></picture></div>
<div class="axis-main stack">
<h2 id="card-title" class="head" data-reveal>{bi("Share the headline", "Partager le constat")}</h2>
<p class="lead col-text">{bi("A picture of the main figures, sized for social networks.", "Une image des chiffres principaux, au format des réseaux sociaux.")}</p>
<p><a class="btn" href="cards/card-en.png" download>{bi("Download the card (PNG, English)", "Télécharger la carte (PNG, anglais)")}</a> <a class="btn btn-ghost" href="cards/card-fr.png" download>{bi("Download the card (PNG, French)", "Télécharger la carte (PNG, français)")}</a></p>
</div>
</div>
</section>"""
    anchors = [
        ("quebec", "Quebec and France", "Québec et France"),
        ("chance", "Above chance", "Au-dessus du hasard"),
        ("hard", "Hardest tasks", "Épreuves difficiles"),
        ("heatmap", "Heatmap", "Carte de chaleur"),
        ("size", "Size and score", "Taille et score"),
        ("access", "Open and API", "Ouverts et API"),
        ("quiz", "Quiz", "Quiz"),
        ("time", "Over time", "Dans le temps"),
        ("card", "Share", "Partager"),
    ]
    toc = "".join(f'<li><a href="#{a}">{bi(e, f)}</a></li>' for a, e, f in anchors)
    body = f"""{header("explore")}
{crumbs((None, "Explore", "Explorer"))}
<main id="main">
<section class="section" style="padding-block:calc(var(--pad-section) * 0.5)" aria-labelledby="page-title">
<div class="wrap stack-lg">
{mask("Explore the results", "Explorer les résultats", cls="display").replace('<h1 class="display mask-block">', '<h1 id="page-title" class="display mask-block">')}
<div class="axis" style="margin-top:1.5rem"><div class="zone-note"></div><div class="stack" data-stagger>
<p class="lead col-text" data-reveal>{bi("Eight ways to look at the same scores. All scores are percentages.", "Huit façons de regarder les mêmes scores. Tous les scores sont des pourcentages.")}</p>
<ul class="explore-nav" data-reveal>{toc}</ul>
</div></div>
</div>
</section>
{secs}
{card}
</main>
{suite("explore")}
{footer()}"""
    ex = '<meta property="og:image" content="cards/card-en.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
    return page(
        "explore",
        "Explore the results | COLE",
        "Explorer les résultats | COLE",
        body,
        scripts=("explore.js",),
    )


# ---------- choose a model ----------
def choose():
    six = [BY_ID[i] for i in DEFAULTS]
    notes = [
        (
            "n/a is not zero.",
            "n.d. n’est pas zéro.",
            "It means the model has no result for that test.",
            "Cela signifie que le modèle n’a pas de résultat pour ce test.",
        ),
        (
            "API models and open models are not run the same way.",
            "Les modèles par API et les modèles ouverts ne sont pas exécutés de la même façon.",
            "Some open models were run in a lighter form, so a full run could score a little differently.",
            "Certains modèles ouverts ont été exécutés sous une forme allégée ; une exécution complète pourrait donner des scores un peu différents.",
        ),
    ]
    nh = "".join(
        f'<div data-reveal><h3 class="strong lead">{bi(a, b)}</h3><p>{bi(c, d)}</p></div>'
        for a, b, c, d in notes
    )
    body = f"""{header("compare")}
{crumbs((None, "Compare models", "Comparer des modèles"))}
<main id="main">
<section class="section" style="padding-block:calc(var(--pad-section) * 0.5)" aria-labelledby="page-title">
<div class="wrap stack-lg">
{mask("Choose a model", "Choisir un modèle", cls="display").replace('<h1 class="display mask-block">', '<h1 id="page-title" class="display mask-block">')}
<div class="axis" style="margin-top:1.5rem"><div class="zone-note"></div><div class="stack" data-stagger>
<p class="lead col-text" data-reveal>{bi("Pick 2 to 6 models. See where each one is stronger.", "Choisissez de 2 à 6 modèles. Voyez où chacun est le plus fort.")}</p>
</div></div>
</div>
</section>

<section id="compare" class="section ground-deep" aria-labelledby="compare-title">
<div class="wrap axis compare-grid">
<div class="c-head"><h2 id="compare-title" class="head" data-reveal>{bi("Where each one is stronger", "Où chacun est le plus fort")}</h2></div>
<div class="c-pick js-only" hidden data-busy-target aria-busy="true">
<label for="s-add" id="add-label" class="strong">{bi("Add a model", "Ajouter un modèle")}</label>
<div class="add-row"><select id="s-add" class="select"></select><button id="btn-add" class="btn btn-ghost" type="button">{bi("Add", "Ajouter")}</button></div>
<p id="add-note" class="small" role="alert"></p><p id="live-note" class="vh" role="status" aria-live="polite"></p>
<ul id="suggest" class="chips"></ul>
<p><button id="btn-reset" class="link-btn" type="button">{bi("Reset to the default pair", "Revenir à la paire par défaut")}</button></p>
</div>
<div class="c-plate plate js-only" hidden data-chart>
<ul id="chips" class="chips" aria-live="off"></ul>
<div class="seg-row"><div id="seg" class="seg" role="tablist"></div>{HELP("Radar: the farther a point is from the centre, the higher the score. By skill: one row per skill, each model is a marker on a line. Table: the same numbers, strongest starred.", "Radar : plus un point est loin du centre, plus le score est élevé. Par compétence : une ligne par compétence, chaque modèle est un repère sur une ligne. Tableau : les mêmes chiffres, le plus fort marqué d’une étoile.", "chart", "help-sum")}</div>
<p><button id="more-cats" class="btn btn-ghost" type="button" aria-expanded="false">Voir plus</button></p>
<div id="radar-pick" hidden></div>
<p id="plate-scale" class="small plate-scale">{bi("Scores in %.", "Scores en %.")}</p>
<div id="plate-state" hidden></div>
<div id="plate-svg-host" class="plate-box" role="tabpanel"></div>
<div id="compare-host" class="vh"></div>
<p id="verdict" class="verdict" aria-live="polite" tabindex="-1"></p>
</div>
<div class="no-js-only c-plate"><p class="lead">{bi("The comparison needs JavaScript. This table of six models works without it.", "La comparaison demande JavaScript. Ce tableau de six modèles fonctionne sans.")}</p><div class="tbl-wide">{static_table(six, "Six models, score by skill, in percent.", "Six modèles, score par compétence, en pourcentage.")}</div></div>
</div>
</section>



<section class="section" aria-labelledby="notes-title">
<div class="wrap axis">
<div class="zone-note" data-reveal><div class="pic pic-wide">{img("champlain-map-1612.jpg", "Detail of Champlain’s 1612 map of New France.", "Détail de la carte de la Nouvelle-France de Champlain, 1612.", 'style="object-position:0% 50%"')}</div></div>
<div class="axis-main stack-lg"><h2 id="notes-title" class="head" data-reveal>{bi("Worth knowing", "À savoir")}</h2>
<details class="how"><summary>{bi("Read the notes", "Lire les notes")}</summary><div class="stack">{nh}</div></details></div>
</div>
</section>
</main>
{suite("compare")}
{footer()}"""
    return page(
        "compare",
        "Choose a model | COLE",
        "Choisir un modèle | COLE",
        body,
        scripts=("choose.js",),
    )


def _tease():
    qk = EXTRA["quebec_tasks"]
    m = BY_ID["claude-opus-4-20250514"]
    qv = [m["tasks"][k] for k in qk if m["tasks"].get(k) is not None]
    ov = [v for k, v in m["tasks"].items() if k not in qk and v is not None]
    qa, oa = sum(qv) / len(qv) * 100, sum(ov) / len(ov) * 100
    ch = EXTRA["chance"]["qfrcola"]["value"] * 100
    sc = m["tasks"]["qfrcola"] * 100
    en_q = f"{m['label']} averages {qa:.1f} on the two Quebec tests and {oa:.1f} on the other French tests. Two tests are few, so read the gap as a hint."
    fr_q = f"{m['label']} obtient en moyenne {qa:.1f} sur les deux tests québécois et {oa:.1f} sur les autres tests en français. Deux tests, c’est peu : lisez l’écart comme un indice.".replace(
        ".", ",", 0
    )
    en_c = f"On a yes-or-no test about Quebec sentences, guessing scores {ch:.0f}. {m['label']} scores {sc:.0f}."
    fr_c = f"Sur un test par oui ou non sur des phrases québécoises, le hasard obtient {ch:.0f}. {m['label']} obtient {sc:.0f}."
    return (
        en_q,
        fr_q.replace(f"{qa:.1f}", f"{qa:.1f}".replace(".", ",")).replace(
            f"{oa:.1f}", f"{oa:.1f}".replace(".", ",")
        ),
    ), (en_c, fr_c)


TEASE_Q, TEASE_C = _tease()


# ---------- poster (plain-language.html) ----------
def plain():
    ids = [
        "claude-opus-4-20250514",
        "gpt-4o-2024-08-06",
        "unsloth/Qwen3-14B-unsloth-bnb-4bit",
        "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
        "unsloth/Llama-3.2-1B-Instruct-bnb-4bit",
        "RandomBaselineModel",
    ]
    blocks = [
        (
            "It is not the whole of Quebec French.",
            "Ce n’est pas tout le français québécois.",
            f"{N_QUEBEC_TESTS} of the {N_TESTS} tests are about Quebec. The other {N_OTHER_TESTS} test French in general.",
            f"{N_QUEBEC_TESTS} des {N_TESTS} tests portent sur le Québec. Les {N_OTHER_TESTS} autres testent le français en général.",
        ),
        (
            "It says nothing about cost or speed.",
            "Il ne dit rien du coût ni de la vitesse.",
            "A high score does not tell you the price, the delay or where your data goes.",
            "Un score élevé n’indique ni le prix, ni le délai, ni où vont vos données.",
        ),
        (
            "It is a snapshot.",
            "C’est un instantané.",
            f"Results use one protocol, a single snapshot. Newer models are not in yet.",
            f"Les résultats suivent un seul protocole et un seul instantané. Les modèles plus récents n’y sont pas encore.",
        ),
        (
            "It may not match your job.",
            "Il ne correspond pas forcément à votre tâche.",
            "The tests are short, scored questions, not conversations. A model can do well here and still write badly for you.",
            "Les tests sont de courtes questions notées, pas des conversations. Un modèle peut bien réussir ici et mal écrire pour vous.",
        ),
    ]
    bh = "".join(
        f'<div data-reveal><h3 class="strong lead">{bi(a, b)}</h3><p>{bi(c, d)}</p></div>'
        for a, b, c, d in blocks
    )
    body = f"""{header("plain")}
<main id="main">
<section class="hero ground-deep" aria-labelledby="poster-title" style="padding-bottom:0">
{crumbs((None, "Poster", "Affiche"))}
<div class="wrap poster-grid">
<div class="poster-pic"><div class="pic" data-reveal>{img("postcard-sous-le-cap.jpg", "Old postcard of a narrow street in Quebec City, Sous-le-Cap, with wooden balconies and clothes lines.", "Ancienne carte postale d’une ruelle de Québec, Sous-le-Cap, avec des balcons de bois et des cordes à linge.", 'style="object-position:50% 25%"').replace('loading="lazy"', '')}</div></div>
<div class="poster-main">
{mask("Does AI get", "L’IA parle", "Québécois?", "québécois&nbsp;?").replace('<h1 class="display hero-title mask-block">', '<h1 id="poster-title" class="display hero-title mask-block">')}
<p class="lead" data-reveal>{bi(f"Some do. The strongest model answered {Q_BEST} out of 100 on Quebec expressions and words. The models you can run on your own computer, up to 33 billion parameters, scored no more than {Q_LOCAL}.", f"Certaines, oui. Le modèle le plus fort a répondu juste à {Q_BEST} questions sur 100 sur les expressions et les mots du Québec. Les modèles qu’on peut exécuter sur son propre ordinateur, jusqu’à 33 milliards de paramètres, ont obtenu {Q_LOCAL} au maximum.")}</p>
<p data-reveal><a class="btn" href="#bars">{bi("See six models", "Voir six modèles")}</a></p>
</div>
</div>
</section>

<section class="section" aria-labelledby="words-title">
<div class="wrap">
<h2 id="words-title" class="head" style="margin-bottom:1.5rem" data-reveal>{bi("Three words", "Trois mots")}</h2>
<dl class="def-list" data-stagger>
<div class="def-row" data-reveal><dt>COLE</dt><dd>{bi(f"A set of {N_TESTS} French tests built by researchers. {N_QUEBEC_TESTS} of them are about Quebec expressions and words.", f"Un ensemble de {N_TESTS} tests en français créé par des chercheurs. {N_QUEBEC_TESTS} portent sur les expressions et les mots du Québec.")}</dd></div>
<div class="def-row" data-reveal><dt>{bi("Benchmark", "Banc d’essai")}</dt><dd>{bi("A test that asks every model the same questions, so their scores can be compared.", "Un test qui pose les mêmes questions à chaque modèle, pour que leurs scores soient comparables.")}</dd></div>
<div class="def-row" data-reveal><dt>{bi("Model", "Modèle")}</dt><dd>{bi("An AI program that reads and writes text, like the one behind a chatbot.", "Un programme d’IA qui lit et écrit du texte, comme celui derrière un robot conversationnel.")}</dd></div>
</dl>
</div>
</section>

<section id="bars" class="section ground-blue" aria-labelledby="bars-title">
<div class="wrap axis">
<div class="zone-note stack" data-reveal><p class="figure-big">{round(q(best) * 100)}</p><p class="small">{bi(f"out of 100: the highest score, {BEST_LABEL}.", f"sur 100 : le score le plus élevé, {BEST_LABEL}.")}</p></div>
<div class="axis-main stack-lg">
<h2 id="bars-title" class="head" data-reveal>{bi("How well do they know Quebec words?", "Connaissent-ils les mots du Québec ?")}</h2>
<p class="lead col-text" data-reveal>{bi("Each model got the same questions: match a Quebec expression or word with its meaning.", "Chaque modèle a reçu les mêmes questions : associer une expression ou un mot du Québec à son sens.")}</p>
{bars(ids, plain=True)}
<p class="col-text" data-reveal>{bi(f"Guessing at random scores {round(q(RANDOM) * 100)}. The two smallest models score barely higher.", f"Le hasard obtient {round(q(RANDOM) * 100)}. Les deux plus petits modèles obtiennent à peine plus.")}</p>
</div>
</div>
</section>

<section class="section" aria-labelledby="limits-title">
<div class="wrap axis">
<div class="zone-note stack" data-reveal><p class="stat"><b>{N_QUEBEC_TESTS} {bi("of", "sur")} {N_TESTS}</b><span>{bi("tests are about Quebec French.", "tests portent sur le français québécois.")}</span></p></div>
<div class="axis-main stack-lg"><h2 id="limits-title" class="head" data-reveal>{bi("What this does not tell you", "Ce que ce score ne dit pas")}</h2>
<div class="cols-2">{bh}</div></div>
</div>
</section>

<section class="section ground-deep" aria-labelledby="next-title" style="padding-bottom:0">
<div class="wrap closing-grid">
<div class="closing-talk" data-stagger>
<h2 id="next-title" class="head" data-reveal>{bi("Want the details?", "Envie de détails ?")}</h2>
<p class="lead" data-reveal>{bi("Compare 2 to 6 models side by side, or read how the scores are computed.", "Comparez de 2 à 6 modèles côte à côte, ou lisez comment les scores sont calculés.")}</p>
<a class="btn" href="choose-a-model.html" data-carry data-reveal>{bi("Compare models", "Comparer des modèles")}</a>
<a class="link-btn" href="level-3.html" data-reveal>{bi("Read the article page", "Lire la page de l’article")}</a>
</div>
<div class="pic" style="aspect-ratio:16/8">{img("printing-house-16c.jpg", "Engraving of a sixteenth-century printing house.", "Gravure d’une imprimerie du XVIe siècle.", 'style="object-position:50% 30%"')}</div>
</div>
</section>
<section class="section ground-tint" aria-labelledby="tease-title">
<div class="wrap axis">
<div class="zone-note" data-reveal><p class="small strong">{bi("Two more ways to look", "Deux autres façons de regarder")}</p></div>
<div class="axis-main stack-lg">
<h2 id="tease-title" class="head" data-reveal>{bi("Quebec against the rest", "Le Québec contre le reste")}</h2>
<p class="lead col-text" data-reveal>{bi(TEASE_Q[0], TEASE_Q[1])}</p>
<p class="col-text" data-reveal>{bi(TEASE_C[0], TEASE_C[1])}</p>
<p data-reveal><a class="btn" href="explore.html#quebec" data-carry>{bi("Explore the charts", "Explorer les graphiques")}</a></p>
</div>
</div>
</section>
</main>
{footer()}"""
    return page(
        "plain", "Does AI get Québécois? | COLE", "L’IA parle québécois ? | COLE", body
    )


# ---------- all results ----------
def results():
    body = f"""{header("results")}
{crumbs((None, "All results", "Tous les résultats"))}
<main id="main">
<section class="section" style="padding-block:calc(var(--pad-section) * 0.5)" aria-labelledby="page-title">
<div class="wrap stack-lg">
{mask("All results", "Tous les résultats", cls="display").replace('<h1 class="display mask-block">', '<h1 id="page-title" class="display mask-block">')}
<div class="axis" style="margin-top:1.5rem"><div class="zone-note"></div><div class="stack" data-stagger>
<p class="lead col-text" data-reveal>{bi("Every model, every skill, every task. Sort, filter, then select 2 to 6 models to compare.", "Chaque modèle, chaque compétence, chaque tâche. Triez, filtrez, puis sélectionnez de 2 à 6 modèles à comparer.")}</p>
</div></div>
</div>
</section>

<section class="section ground-tint" aria-labelledby="table-title" id="results">
<div class="wrap axis">
<div class="zone-note"></div>
<div class="axis-main seg-row"><h2 id="table-title" class="head" data-reveal>{bi("The full table", "Le tableau complet")}</h2>{HELP("Sort with the column headers. Tick a model to compare it." + NA_EN, "Triez avec les en-têtes de colonne. Cochez un modèle pour le comparer." + NA_FR, "table")}</div>
<div class="span-all tools" data-reveal>
<div class="field"><label for="q">{bi("Search by model name", "Chercher par nom de modèle")}</label><input id="q" type="search" autocomplete="off" data-needs-data disabled></div>
<div class="field"><label for="f-fam">{bi("Family", "Famille")}</label><select id="f-fam" data-needs-data disabled><option value="">{bi("Any", "Toutes")}</option></select></div>
<div class="field"><label for="f-type">{bi("Type", "Type")}</label><select id="f-type" data-needs-data disabled><option value="">{bi("Any", "Toutes")}</option></select></div>
<div class="field"><label for="f-size">{bi("Size", "Taille")}</label><select id="f-size" data-needs-data disabled><option value="">{bi("Any", "Toutes")}</option></select></div>
<button id="toggle-tasks" class="btn btn-ghost" type="button" aria-expanded="false" data-needs-data disabled>{bi("Show the tasks (each test and its metric)", "Afficher les tâches (chaque test et sa métrique)")}</button>
<label class="check"><input id="dec" type="checkbox" data-needs-data disabled><span>{bi("Two decimals", "Deux décimales")}</span></label>
<button id="clear" class="link-btn" type="button">{bi("Clear filters", "Effacer les filtres")}</button>
</div>
<p class="span-all"><span class="strong" id="count" role="status" aria-live="polite"></span> <span class="small" id="unit-note"></span></p>
<div class="span-all" id="res-host" aria-busy="false">{static_table(MODELS[:25], "All results, first 25 models, score in percent.", "Tous les résultats, 25 premiers modèles, score en pourcentage.")}</div>
<div class="span-all dl" data-reveal><button class="btn btn-ghost" id="dl-csv" type="button" data-needs-data disabled>{bi("Download CSV", "Télécharger le CSV")}</button><button class="btn btn-ghost" id="dl-json" type="button" data-needs-data disabled>{bi("Download JSON", "Télécharger le JSON")}</button>
<p class="small col-text">{bi("Aggregated scores as displayed (filters, sort and open columns), in percent with two decimals. No per-example data.", "Scores agrégés tels qu’affichés (filtres, tri et colonnes ouvertes), en pourcentage avec deux décimales. Aucune donnée par exemple.")}</p><p class="small" id="dl-note" role="status"></p></div>
</div>
</section>
</main>
<div id="selbar" class="selbar" role="region" {attrs("aria-label", "Selected models", "Modèles sélectionnés")} hidden>
<div class="wrap selbar-in"><p class="strong" id="sel-count"></p><ul id="sel-chips" class="chips"></ul><a id="sel-go" class="btn btn-sm" href="choose-a-model.html"></a><button id="sel-clear" class="link-btn" type="button">{bi("Clear selection", "Effacer la sélection")}</button><p class="small" id="sel-need" role="status"></p></div>
</div>
{footer()}"""
    return page(
        "results",
        "All results | COLE",
        "Tous les résultats | COLE",
        body,
        scripts=("results.js",),
    )


# ---------- level 3 stub ----------
TASKS = {
    "allocine": ("AlloCiné", "Accuracy"),
    "mms": ("MMS", "Accuracy"),
    "fracas": ("FraCaS", "Accuracy"),
    "gqnli": ("GQNLI-Fr", "Accuracy"),
    "lingnli": ("LingNLI", "Accuracy"),
    "mnli-nineeleven-fr-mt": ("MNLI nineeleven FR-MT", "Accuracy"),
    "rte3-french": ("RTE3-French", "Accuracy"),
    "sickfr": ("SICK-FR", "Pearson"),
    "xnli": ("XNLI", "Accuracy"),
    "daccord": ("DACCORD", "Accuracy"),
    "fquad": ("FQuAD", "F1, exact match"),
    "french_boolq": ("French BoolQ", "Accuracy"),
    "piaf": ("PIAF", "F1, exact match"),
    "multiblimp": ("MultiBLiMP-Fr", "Accuracy"),
    "qfrcola": ("QFrCoLA", "Accuracy"),
    "qfrblimp": ("QFrBLiMP", "Accuracy"),
    "paws_x": ("PAWS-X", "Accuracy"),
    "sts22": ("STS22", "Pearson"),
    "wsd": ("WSD-Fr", "Exact match"),
    "wino_x_lm": ("WiNo-X LM", "Accuracy"),
    "wino_x_mt": ("WiNo-X MT", "Accuracy"),
    "qfrcore": ("QFrCoRE", "Accuracy"),
    "qfrcort": ("QFrCoRT", "Accuracy"),
}


def level3():
    six = [BY_ID[i] for i in DEFAULTS]
    rows = ""
    for c in CATS:
        for t in c["tasks"]:
            name, metric = TASKS[t]
            rows += f'<tr><th scope="row" class="l">{name}</th><td class="l">{bi(c["short"]["en"], c["short"]["fr"])}</td><td class="l">{metric}</td>'
            for m in six:
                v = m["tasks"].get(t)
                rows += (
                    f'<td>{bi("n/a", "n.d.")}</td>'
                    if v is None
                    else f"<td>{v * 100:.2f}</td>"
                )
            rows += "</tr>"
    head = "".join(
        f'<th scope="col">{lab(m)}<span class="unit">(%)</span></th>' for m in six
    )
    tbl = f'<div class="table-scroll" tabindex="0" role="region" {attrs("aria-label", "Score per task, two decimals", "Score par tâche, deux décimales")}><table class="data"><caption>{bi("Score per task for the six default models, two decimals, in percent.", "Score par tâche pour les six modèles par défaut, deux décimales, en pourcentage.")}</caption><thead><tr><th scope="col" class="l sticky-1" style="min-width:12rem;position:sticky;left:0">{bi("Task", "Tâche")}</th><th scope="col" class="l">{bi("Skill", "Compétence")}</th><th scope="col" class="l">{bi("Metric", "Métrique")}</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
    body = f"""{header("paper")}
{crumbs((None, "Article", "Article"))}
<main id="main">
<section class="section" style="padding-block:calc(var(--pad-section) * 0.5)" aria-labelledby="page-title">
<div class="wrap stack-lg">
{mask("Article", "Article", cls="display").replace('<h1 class="display mask-block">', '<h1 id="page-title" class="display mask-block">')}
<div class="axis" style="margin-top:1.5rem"><div class="zone-note"></div><div class="stack" data-stagger>
<p class="lead col-text" data-reveal>{bi("For researchers. Scores here carry two decimals, as in the paper.", "Pour la recherche. Les scores ont ici deux décimales, comme dans l’article.")}</p>
</div></div>
</div>
</section>

<section id="article" class="section ground-deep" aria-labelledby="paper-title">
<div class="wrap axis">
<div class="zone-note" data-reveal><p class="stat"><b>ICLR 2026</b><span>{bi("workshop poster", "affiche d’atelier")}</span></p></div>
<div class="axis-main stack-lg"><h2 id="paper-title" class="head" data-reveal>{bi("Article", "Article")}</h2>
<div class="stack col-text" data-reveal>
<p class="lead">{escape(ART["title"])}</p>
<p>{escape(ART["authors"])} ({ART["year"]})</p>
<p>{escape(ART["venue"])}. {bi("This is a workshop poster, not a main-conference paper.", "C’est une affiche d’atelier, pas un article de la conférence principale.")}</p>
<p><a class="btn" href="{ART["primary_url"]}">{bi("Read the accepted paper", "Lire l’article accepté")}</a></p>
</div>
<div class="stack col-text" data-reveal><p class="strong">{bi("Abstract (English original)", "Résumé (original anglais)")}</p><p lang="en" style="display:block !important">{escape(ART["abstract"])}</p></div>
<details class="how" data-reveal><summary>BibTeX</summary><pre class="bib"><code>{escape(ART["bibtex"])}</code></pre></details>
</div>
</div>
</section>

<section id="protocol" class="section" aria-labelledby="protocol-title">
<div class="wrap axis">
<div class="zone-note stack-lg" data-reveal><div class="pic pic-wide">{img("printing-house-16c.jpg", "Engraving of a sixteenth-century printing house.", "Gravure d’une imprimerie du XVIe siècle.", 'style="object-position:60% 50%"')}</div></div>
<div class="axis-main stack-lg"><h2 id="protocol-title" class="head" data-reveal>{bi("Protocol note", "Note de protocole")}</h2>
<div class="cols-2">
<div data-reveal><p>{bi("A task score is the mean of its metrics among accuracy, f1, pearson, pearsonr, spearman, fquad and exact match. A value above 1 is divided by 100.", "Le score d’une tâche est la moyenne de ses métriques parmi accuracy, f1, pearson, pearsonr, spearman, fquad et exact match. Une valeur supérieure à 1 est divisée par 100.")}</p></div>
<div data-reveal><p>{bi("A skill score is the mean of the tasks the model has. Missing tasks are never counted as zero. The overall score follows the live leaderboard.", "Le score d’une compétence est la moyenne des tâches du modèle. Une tâche manquante n’est jamais comptée comme zéro. Le score général suit le classement en ligne.")}</p></div>
<div data-reveal><p>{bi(f"To check with the authors: the entry frblimp duplicates qfrblimp in all {N_MODELS} results, so it is left out and counted once; in this snapshot the Quebec grammar test (qfrblimp) therefore cannot be told apart from the general one. The wsd metric also holds values below 1.", f"À vérifier avec les auteurs : l’entrée frblimp duplique qfrblimp dans les {N_MODELS} résultats ; elle est donc écartée et comptée une fois. Dans ce relevé, le test de grammaire québécoise (qfrblimp) ne se distingue donc pas de la version générale. La métrique wsd contient aussi des valeurs inférieures à 1.")}</p></div>
</div></div>
</div>
</section>

<section class="section ground-tint" aria-labelledby="tasks-title">
<div class="wrap axis">
<div class="zone-note" data-reveal><p class="lead">{bi(f"The {N_TESTS} tasks, grouped into seven skills.", f"Les {N_TESTS} tâches, regroupées en sept compétences.")}</p></div>
<div class="axis-main"><h2 id="tasks-title" class="head" data-reveal>{bi("Task list", "Liste des tâches")}</h2></div>
<div class="span-all tbl-wide" data-reveal>{tbl}</div>
</div>
</section>
</main>
{footer()}"""
    return page("paper", "Article | COLE", "Article | COLE", body)


for name, fn in (
    ("index.html", index),
    ("choose-a-model.html", choose),
    ("plain-language.html", plain),
    ("level-3.html", level3),
    ("all-results.html", results),
    ("model.html", model),
    ("explore.html", explore),
):
    (ROOT / name).write_text(fn())
    print("wrote", name)
import subprocess, sys

sys.exit(subprocess.call([sys.executable, str(ROOT / "check_links.py")]))
