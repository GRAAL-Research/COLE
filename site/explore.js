/* Step 4, Explore: seven visual tools on the aggregate scores. Every chart has a table or list alternative and a "How to read" note. */
(function () {
  "use strict";
  var C = window.COLE, $ = function (id) { return document.getElementById(id); };
  var STR = {
    en: {
      loading: "Loading the results…", emptyTitle: "Nothing to chart yet.", emptyBody: "No results are available for this view. Open All results to check the data.", errorTitle: "We could not load the results.", errorBody: "The data file did not answer. Check your connection and try again.", retry: "Try again",
      qLeg: "Quebec tests", oLeg: "Other French tests", min: "min", max: "max", tbl: "Show as a table", model: "Model", score: "Score", size: "Size (billions of parameters)", szB: "{n} billion parameters", szU: "size unknown", axOpen: "Open weights", axApi: "Served through an API", med: "Median", nMod: "{n} models", gApi: "Median {d} points stronger for API models", gOpen: "Median {d} points stronger for open-weight models", axSum: "The strongest open-weight model beats the median API model in {k} of {n} skills.", axCap: "Medians by skill", rMed: "Median {v}", strongOpen: "Strongest open", strongApi: "Strongest API", hardSum: "The strongest model is at least {g} points above guessing on every task (closest: {t}). The median model stays within 5 points of guessing on {k} of {n} tasks.", bestM: "Strongest model", hMed: "Median model", chanceV: "Guessing {v}", noCh: "no guessing reference", hardCap: "Strongest and median model against guessing", chTk: "Random guessing", bestMk: "Strongest model", medMk: "Median model", boldK: "Bold name: the median model is within 5 points of guessing", pts: "points above guessing", rank: "Rank",
      qOnly: "Quebec tests: {q}. Two tests only, so read a difference as a hint. The other {n} tests are French in general; the data does not say where their texts come from.",
      chanceLeg: "Score", chanceTick: "Random guessing", noChance: "no chance line for this test", above: "{d} points above chance", below: "{d} points below chance", near: "{d} points from chance", pick: "Model",
      gSum: "{m} is clearly above chance (more than 5 points) on {a} of {n} tests. It is within 5 points of chance on: {list}.", gNone: "It is clearly above chance on every test that has a chance line.", gBelow: " Below chance: {list}.",
      heatSort: "Sort by {c}", overall: "Overall", na: "n/a", more: "Show 25 more", showing: "{s} of {n} models", scale: "Tone scale", hatch: "n/a (no result)",
      metric: "Skill on the vertical axis", hl: "Highlight a model", none: "None", unk: "Size unknown ({n} models)", open: "Open weights", api: "Served through an API", ref: "Random guessing",
      qTitle: "Question {i} of {n}", check: "Check my answer", next: "Next question", seeRes: "See the result", correct: "Correct.", wrong: "Not this one.", yours: "Your answer", truth: "Dataset answer",
      qEnd: "You got {k} of {n}.", qModels: "How the models did on each whole test, not on these questions:", restart: "Start again", choose: "Choose an answer first.", testScore: "{t}: {m} scored {v}",
      tDated: "Models with a date in their name", tNo: "{n} models without a known date are not on this chart.", rec: "Highest so far", mth: "Month", best: "Highest so far", step: "Step line: highest score so far",
      ring: "Ring: a dated model"
    },
    fr: {
      loading: "Chargement des résultats…", emptyTitle: "Rien à représenter pour l’instant.", emptyBody: "Aucun résultat n’est disponible pour cette vue. Ouvrez Tous les résultats pour vérifier les données.", errorTitle: "Nous n’avons pas pu charger les résultats.", errorBody: "Le fichier de données n’a pas répondu. Vérifiez votre connexion et réessayez.", retry: "Réessayer",
      qLeg: "Tests québécois", oLeg: "Autres tests en français", min: "min", max: "max", tbl: "Afficher en tableau", model: "Modèle", score: "Score", size: "Taille (milliards de paramètres)", szB: "{n} milliards de paramètres", szU: "taille inconnue", axOpen: "Poids ouverts", axApi: "Servi par API", med: "Médiane", nMod: "{n} modèles", gApi: "Médiane plus forte de {d} points pour les modèles par API", gOpen: "Médiane plus forte de {d} points pour les modèles à poids ouverts", axSum: "Le modèle à poids ouverts le plus fort dépasse la médiane des modèles par API dans {k} compétences sur {n}.", axCap: "Médianes par compétence", rMed: "Médiane {v}", strongOpen: "Ouvert le plus fort", strongApi: "API le plus fort", hardSum: "Le modèle le plus fort dépasse le hasard d’au moins {g} points sur chaque épreuve (la plus proche : {t}). Le modèle médian reste à moins de 5 points du hasard sur {k} épreuves sur {n}.", bestM: "Modèle le plus fort", hMed: "Modèle médian", chanceV: "Hasard {v}", noCh: "pas de référence de hasard", hardCap: "Modèle le plus fort et modèle médian face au hasard", chTk: "Tirage au hasard", bestMk: "Modèle le plus fort", medMk: "Modèle médian", boldK: "Nom en gras : le modèle médian est à moins de 5 points du hasard", pts: "points au-dessus du hasard", rank: "Rang",
      qOnly: "Tests québécois : {q}. Deux tests seulement, une différence est donc un indice. Les {n} autres tests portent sur le français en général ; les données ne disent pas d’où viennent leurs textes.",
      chanceLeg: "Score", chanceTick: "Tirage au hasard", noChance: "pas de repère de hasard pour ce test", above: "{d} points au-dessus du hasard", below: "{d} points sous le hasard", near: "à {d} points du hasard", pick: "Modèle",
      gSum: "{m} est nettement au-dessus du hasard (plus de 5 points) sur {a} tests sur {n}. Il est à moins de 5 points du hasard sur : {list}.", gNone: "Il est nettement au-dessus du hasard sur tous les tests qui ont un repère.", gBelow: " Sous le hasard : {list}.",
      heatSort: "Trier par {c}", overall: "Général", na: "n.d.", more: "Afficher 25 de plus", showing: "{s} modèles sur {n}", scale: "Échelle de tons", hatch: "n.d. (aucun résultat)",
      metric: "Compétence sur l’axe vertical", hl: "Mettre un modèle en évidence", none: "Aucun", unk: "Taille inconnue ({n} modèles)", open: "Poids ouverts", api: "Utilisé par API", ref: "Tirage au hasard",
      qTitle: "Question {i} sur {n}", check: "Vérifier ma réponse", next: "Question suivante", seeRes: "Voir le résultat", correct: "Juste.", wrong: "Pas celle-ci.", yours: "Votre réponse", truth: "Réponse du jeu de données",
      qEnd: "Vous avez {k} réponses justes sur {n}.", qModels: "Résultats des modèles sur chaque test entier, pas sur ces questions :", restart: "Recommencer", choose: "Choisissez d’abord une réponse.", testScore: "{t} : {m} a obtenu {v}",
      tDated: "Modèles dont le nom porte une date", tNo: "{n} modèles sans date connue ne figurent pas sur ce graphique.", rec: "Plus élevé jusqu’ici", mth: "Mois", best: "Plus élevé jusqu’ici", step: "Courbe en escalier : score le plus élevé jusqu’ici",
      ring: "Anneau : un modèle daté"
    }
  };
  var t = C.makeT(STR), D, X, FOCUS = new URLSearchParams(location.search).get("model");
  var DEF = ["claude-opus-4", "gpt-4o", "Qwen3-14B", "Meta-Llama-3.1-8B-Instruct", "Llama-3.2-1B-Instruct", "RandomBaselineModel"];
  var S = { heatKey: "overall", heatDir: "desc", heatLimit: 25, gauge: null, sy: "overall", hl: FOCUS || "", q: 0, picks: [], checked: false, score: 0 };
  function ml(m) { return C.mlabel(m); }
  function cl(c, sh) { return (sh ? c.short : c.label)[C.lang()]; }
  function mean(a) { return a.length ? a.reduce(function (x, y) { return x + y; }, 0) / a.length : null; }
  function tname(k) { return D.taskNames[k].name; }
  function wid(el) { return Math.max(260, el.clientWidth || 320); }
  function stateAll(kind) {
    if (kind === "empty") { ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8"].forEach(function (id) { var h = $(id); if (h) { h.innerHTML = '<div class="state"><h3 class="lead strong">' + C.esc(t("emptyTitle")) + "</h3><p>" + C.esc(t("emptyBody")) + "</p></div>"; h.setAttribute("aria-busy", "false"); } }); return; }
    ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8"].forEach(function (id) {
      var h = $(id); if (!h) return;
      if (kind === "loading") h.innerHTML = '<div class="skel-rows" aria-hidden="true"><span></span><span></span><span></span></div><p class="small">' + C.esc(t("loading")) + "</p>";
      else { h.innerHTML = '<div class="state"><h3 class="lead strong">' + C.esc(t("errorTitle")) + "</h3><p>" + C.esc(t("errorBody")) + '</p><button class="btn" type="button" data-retry>' + C.esc(t("retry")) + "</button></div>"; h.querySelector("[data-retry]").addEventListener("click", load); }
      h.setAttribute("aria-busy", kind === "loading");
    });
  }
  /* ---- one tooltip for every marker: hover, keyboard focus, tap. Name and facts also live in aria-label and in the table. ---- */
  var tipEl = null, tipOn = null;
  function pt(cx, cy, inner, name, facts, noTab) {
    var label = [name].concat(facts).join(", ");
    return '<g class="pt"' + (noTab ? ' aria-hidden="true"' : ' tabindex="0" role="img" aria-label="' + C.esc(label) + '"') + ' data-name="' + C.esc(name) + '" data-facts="' + C.esc(facts.join(" | ")) + '">' +
      '<circle class="pt-ring" cx="' + cx + '" cy="' + cy + '" r="11"/>' + inner + '<circle class="pt-hit" cx="' + cx + '" cy="' + cy + '" r="10"/></g>';
  }
  function tipHide() { if (tipOn) tipOn.classList.remove("is-active"); tipOn = null; if (tipEl) tipEl.hidden = true; }
  function tipShow(g) {
    if (tipOn === g) return;
    tipHide();
    if (!tipEl) { tipEl = document.createElement("div"); tipEl.className = "chart-tip"; tipEl.setAttribute("aria-hidden", "true"); tipEl.hidden = true; document.body.appendChild(tipEl); }
    tipEl.innerHTML = "<b>" + C.esc(g.dataset.name) + "</b>" + g.dataset.facts.split(" | ").map(function (f) { return "<span>" + C.esc(f) + "</span>"; }).join("");
    tipEl.hidden = false; tipOn = g; g.classList.add("is-active"); tipPlace(g);
  }
  function tipPlace(g) {
    var svg = g.ownerSVGElement.getBoundingClientRect(), m = g.querySelector(".pt-hit").getBoundingClientRect(), r = tipEl.getBoundingClientRect(), pad = 6;
    var left = m.left + m.width / 2 - r.width / 2, top = m.top - r.height - 4;
    if (top < Math.max(svg.top, 0) + pad) top = m.bottom + 4;
    left = Math.max(svg.left + pad, Math.min(left, svg.right - r.width - pad)); left = Math.max(pad, left);
    tipEl.style.left = left + "px"; tipEl.style.top = top + "px";
  }
  function bindTips(host) {
    host.querySelectorAll(".pt").forEach(function (g) {
      g.addEventListener("pointerenter", function (e) { if (e.pointerType !== "touch") tipShow(g); });
      g.addEventListener("pointerleave", function (e) { if (e.pointerType !== "touch" && document.activeElement !== g) tipHide(); });
      g.addEventListener("focus", function () { tipShow(g); });
      g.addEventListener("blur", tipHide);
      g.addEventListener("click", function () { tipShow(g); });
    });
  }
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") tipHide(); });
  document.addEventListener("pointerdown", function (e) { if (!e.target.closest || !e.target.closest(".pt")) tipHide(); });
  window.addEventListener("scroll", function () { if (tipOn) tipPlace(tipOn); }, { passive: true });
  /* label only the few strongest points, never over another label or marker, no leader lines */
  function placeLabels(items, W, H) {
    var boxes = [], out = "";
    items.forEach(function (it) {
      var w = it.text.length * 7.4 + 8, right = it.x + 12 + w < W - 4, x0 = right ? it.x + 12 : it.x - 12 - w, b = { x: x0, y: it.y - 9, w: w, h: 18 };
      if (x0 < 2 || it.y < 10 || it.y > H - 10) return;
      var clash = boxes.some(function (o) { return b.x < o.x + o.w && o.x < b.x + b.w && b.y < o.y + o.h && o.y < b.y + b.h; }) || (it.avoid || []).some(function (p) { return p[0] > b.x - 6 && p[0] < b.x + b.w + 6 && Math.abs(p[1] - it.y) < 12 && !(p[0] === it.x && p[1] === it.y); });
      if (clash) return;
      boxes.push(b);
      out += '<text class="end-label" x="' + (right ? x0 : x0 + w - 8).toFixed(1) + '" y="' + (it.y + 5).toFixed(1) + '" text-anchor="' + (right ? "start" : "end") + '" style="fill:var(--bg)">' + C.esc(it.text) + "</text>";
    });
    return out;
  }
  function factsOf(m, v) { return [C.pct(v, 1) + "\u00a0%", m.size_b == null ? t("szU") : t("szB", { n: C.fmt(m.size_b, 1) })]; }
  function tableOf(head, rows, cap) {
    return '<details class="how"><summary>' + C.esc(t("tbl")) + '</summary><div class="table-scroll" tabindex="0" role="region" aria-label="' + C.esc(cap) + '"><table class="data"><caption class="vh">' + C.esc(cap) + "</caption><thead><tr>" + head.map(function (h, i) { return '<th scope="col"' + (i === 0 ? ' class="l"' : "") + ">" + C.esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" + rows.map(function (r) { return "<tr>" + r.map(function (c, i) { return i === 0 ? '<th scope="row" class="l">' + C.esc(c) + "</th>" : "<td>" + C.esc(c) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div></details>";
  }
  function axisTicks(x, base, a, b, pad, W) {
    var s = "";
    [[a, "start"], [(a + b) / 2, "middle"], [b, "end"]].forEach(function (p) {
      s += '<line class="tick" x1="' + x(p[0]) + '" y1="' + (base - 6) + '" x2="' + x(p[0]) + '" y2="' + (base + 6) + '"/><text class="axis-num" x="' + (p[1] === "start" ? x(p[0]) - 4 : p[1] === "end" ? x(p[0]) + 4 : x(p[0])) + '" y="' + (base - 11) + '" text-anchor="' + p[1] + '">' + C.fmt(p[0] * 100, 0) + "</text>";
    });
    return s;
  }

  /* 1. Quebec against other French tests */
  function dumbbell() {
    var qk = X.quebec_tasks, ids = DEF.slice(); if (FOCUS && ids.indexOf(FOCUS) === -1) ids.push(FOCUS);
    var rows = ids.map(function (s) { return D.bySlug[s]; }).filter(Boolean).map(function (m) {
      var q = [], o = []; Object.keys(m.tasks).forEach(function (k) { if (m.tasks[k] == null) return; (qk.indexOf(k) !== -1 ? q : o).push(m.tasks[k]); });
      return { m: m, q: mean(q), o: mean(o) };
    }).filter(function (r) { return r.q != null && r.o != null; }).sort(function (a, b) { return (a.q - a.o) - (b.q - b.o); });
    var host = $("x1"), W = wid(host), wide = W >= 640, lw = wide ? 210 : 0, pad = 22, x0 = lw + pad, x1 = W - pad, x = function (v) { return x0 + v * (x1 - x0); }, rh = wide ? 70 : 92;
    var QS = { c: "var(--accent)", sh: "circle" }, OS = { c: "var(--s1)", sh: "square" };
    var svg = '<svg viewBox="0 0 ' + W + " " + rows.length * rh + '" width="' + W + '" height="' + rows.length * rh + '" role="img" aria-label="' + C.esc(t("qLeg") + " / " + t("oLeg")) + '">';
    rows.forEach(function (r, i) {
      var y = i * rh, base = y + (wide ? 30 : 56), a = Math.min(r.q, r.o), b = Math.max(r.q, r.o);
      var nm = '<text class="row-name" x="' + (wide ? 0 : pad) + '" y="' + (wide ? base + 5 : y + 18) + '">' + C.esc(ml(r.m)) + "</text>";
      svg += nm + '<line class="track" x1="' + x0 + '" y1="' + base + '" x2="' + x1 + '" y2="' + base + '"/>' + axisTicks(x, base, 0, 1, pad, W);
      svg += '<line class="link" x1="' + x(a).toFixed(1) + '" y1="' + base + '" x2="' + x(b).toFixed(1) + '" y2="' + base + '"/>';
      [[r.q, QS, 0, "qLeg"], [r.o, OS, 1, "oLeg"]].forEach(function (p) {
        var xv = x(p[0]), near = Math.abs(x(r.q) - x(r.o)) < 46, low = p[0] === a, side = near ? (low ? "end" : "start") : "middle", lx = near ? xv + (low ? -11 : 11) : xv;
        if (near && r.q === r.o) { side = p[2] === 0 ? "end" : "start"; lx = xv + (p[2] === 0 ? -11 : 11); }
        var mk = C.shape(p[1].sh, +xv.toFixed(1), base, 7, "fill:" + p[1].c + ";stroke:" + p[1].c, "");
        svg += pt(+xv.toFixed(1), base, mk, ml(r.m), [t(p[3]), C.pct(p[0], 1) + "\u00a0%"]);
        svg += '<text class="end-label" x="' + lx.toFixed(1) + '" y="' + (near ? base + 5 : base + 24) + '" text-anchor="' + side + '" style="fill:' + p[1].c + '">' + C.pct(p[0]) + "</text>";
      });
    });
    host.innerHTML = '<ul class="plate-legend"><li><svg width="16" height="16" aria-hidden="true">' + C.shape("circle", 8, 8, 6, "fill:var(--accent);stroke:var(--accent)", "") + "</svg>" + C.esc(t("qLeg")) + '</li><li><svg width="16" height="16" aria-hidden="true">' + C.shape("square", 8, 8, 6, "fill:var(--s1);stroke:var(--s1)", "") + "</svg>" + C.esc(t("oLeg")) + "</li></ul>" + svg + "</svg>" +
      '<p class="small">' + C.esc(t("qOnly", { q: qk.map(tname).join(", "), n: Object.keys(D.taskNames).length - qk.length })) + "</p>" +
      tableOf([t("model"), t("qLeg"), t("oLeg")], rows.map(function (r) { return [ml(r.m), C.pct(r.q, 2), C.pct(r.o, 2)]; }), t("qLeg"));
    host.setAttribute("aria-busy", "false"); bindTips(host);
  }

  /* 2. Above chance */
  function gauge() {
    var host = $("x2"), slug = S.gauge || FOCUS || "claude-opus-4"; if (!D.bySlug[slug]) slug = "claude-opus-4"; S.gauge = slug;
    var m = D.bySlug[slug], items = [];
    D.cats.forEach(function (c) { c.tasks.forEach(function (k) { var v = m.tasks[k], ch = X.chance[k] ? X.chance[k].value : null; if (v != null) items.push({ k: k, v: v, ch: ch, d: ch == null ? null : v - ch }); }); });
    items.sort(function (a, b) { if (a.d == null) return 1; if (b.d == null) return -1; return b.d - a.d; });
    var withCh = items.filter(function (i) { return i.d != null; }), near = withCh.filter(function (i) { return i.d <= 0.05; });
    var sum = withCh.length - near.length === withCh.length ? t("gNone") : t("gSum", { m: ml(m), a: withCh.length - near.length, n: withCh.length, list: near.map(function (i) { return tname(i.k); }).join(", ") });
    var h = '<div class="picker"><label class="strong" for="g-pick">' + C.esc(t("pick")) + '</label><select id="g-pick" class="select">' + D.models.map(function (x) { return '<option value="' + C.esc(x.name) + '"' + (x.name === slug ? " selected" : "") + ">" + C.esc(ml(x)) + "</option>"; }).join("") + "</select></div>";
    h += '<p>' + C.esc(sum) + '</p><ul class="plate-legend"><li><span class="g-key fill" aria-hidden="true"></span>' + C.esc(t("chanceLeg")) + '</li><li><span class="g-key tick" aria-hidden="true"></span>' + C.esc(t("chanceTick")) + '</li></ul><p class="small axis-ends"><span>0</span><span>100</span></p><ul class="g-list">';
    items.forEach(function (i) {
      var txt = C.pct(i.v) + (i.d == null ? " · " + t("noChance") : " · " + t(i.d > 0.05 ? "above" : i.d < -0.05 ? "below" : "near", { d: C.fmt(Math.abs(i.d) * 100, 1) }));
      h += '<li class="g-row"><span class="g-name">' + C.esc(tname(i.k)) + '</span><span class="g-track"><i class="g-fill" style="width:' + (i.v * 100).toFixed(1) + '%"></i>' + (i.ch == null ? "" : '<i class="g-tick" style="left:' + (i.ch * 100).toFixed(1) + '%"></i>') + '</span><span class="g-val">' + C.esc(txt) + "</span></li>";
    });
    host.innerHTML = h + "</ul>"; host.setAttribute("aria-busy", "false");
    $("g-pick").addEventListener("change", function (e) { S.gauge = e.target.value; gauge(); $("g-pick").focus(); });
  }

  /* 3. Heatmap */
  function bin(v) { var p = v * 100; return p < 20 ? 0 : p < 40 ? 1 : p < 60 ? 2 : p < 80 ? 3 : 4; }
  function heat() {
    var host = $("x3"), cols = [{ k: "overall", l: t("overall") }].concat(D.cats.map(function (c) { return { k: c.key, l: cl(c, true) }; }));
    var val = function (m, k) { return k === "overall" ? m.overall : m.categories[k].score; };
    var rows = D.models.slice().sort(function (a, b) { var x = val(a, S.heatKey), y = val(b, S.heatKey); if (x == null) return 1; if (y == null) return -1; return S.heatDir === "desc" ? y - x : x - y; });
    var shown = rows.slice(0, S.heatLimit);
    var h = '<ul class="plate-legend heat-key" aria-label="' + C.esc(t("scale")) + '">' + ["0 to 20", "20 to 40", "40 to 60", "60 to 80", "80 to 100"].map(function (r, i) { return '<li><span class="hk h' + i + '" aria-hidden="true"></span>' + C.esc(C.lang() === "fr" ? r.replace(/ to /, " à ") : r) + "</li>"; }).join("") + '<li><span class="hk na" aria-hidden="true"></span>' + C.esc(t("hatch")) + "</li></ul>";
    h += '<div class="table-scroll" tabindex="0" role="region" aria-label="' + C.esc(t("scale")) + '"><table class="data heat"><caption class="vh">' + C.esc(t("scale")) + "</caption><thead><tr><th scope=\"col\" class=\"l sticky-2h\">" + C.esc(t("model")) + "</th>";
    cols.forEach(function (c) { var d = S.heatKey === c.k ? S.heatDir : ""; h += '<th scope="col" aria-sort="' + (d ? (d === "desc" ? "descending" : "ascending") : "none") + '"><button class="sort-btn" type="button" data-sort="' + c.k + '"' + (d ? ' data-dir="' + d + '"' : "") + ">" + C.esc(c.l) + "</button></th>"; });
    h += "</tr></thead><tbody>";
    shown.forEach(function (m) {
      h += "<tr" + (m.name === FOCUS ? ' class="is-focus"' : "") + '><th scope="row" class="l sticky-2h">' + C.esc(ml(m)) + "</th>";
      cols.forEach(function (c) { var v = val(m, c.k); h += v == null ? '<td class="hm na">' + C.esc(t("na")) + "</td>" : '<td class="hm h' + bin(v) + '">' + C.pct(v) + "</td>"; });
      h += "</tr>";
    });
    h += "</tbody></table></div><p class=\"small\" role=\"status\">" + C.esc(t("showing", { s: shown.length, n: rows.length })) + "</p>";
    if (rows.length > shown.length) h += '<p><button class="btn btn-ghost" type="button" id="heat-more">' + C.esc(t("more")) + "</button></p>";
    host.innerHTML = h; host.setAttribute("aria-busy", "false");
    host.querySelectorAll("[data-sort]").forEach(function (b) { b.addEventListener("click", function () { var k = b.dataset.sort; if (S.heatKey === k) S.heatDir = S.heatDir === "desc" ? "asc" : "desc"; else { S.heatKey = k; S.heatDir = "desc"; } heat(); var a = host.querySelector('[data-sort="' + k + '"]'); if (a) a.focus(); }); });
    var mb = $("heat-more"); if (mb) mb.addEventListener("click", function () { S.heatLimit += 25; heat(); var n = $("heat-more"); if (n) n.focus(); });
  }

  /* 4. Size against score */
  function scatter() {
    var host = $("x4"), W = wid(host), H = W < 560 ? 400 : 480, L = 46, B = 46, T = 14, stripW = W < 560 ? 84 : 120, R = 10;
    var key = S.sy, val = function (m) { return key === "overall" ? m.overall : m.categories[key].score; };
    var known = D.models.filter(function (m) { return m.size_b != null && val(m) != null; }), unk = D.models.filter(function (m) { return m.size_b == null && val(m) != null; });
    var smin = Math.min.apply(null, known.map(function (m) { return m.size_b; })), smax = Math.max.apply(null, known.map(function (m) { return m.size_b; }));
    var vals = D.models.map(val).filter(function (v) { return v != null; }), ymin = Math.floor(Math.min.apply(null, vals) * 10) / 10, ymax = Math.ceil(Math.max.apply(null, vals) * 10) / 10;
    var px0 = L, px1 = W - stripW - R - 12, sx0 = W - stripW, sx1 = W - R;
    var lx = function (s) { return px0 + 10 + (Math.log(s) - Math.log(smin)) / (Math.log(smax) - Math.log(smin)) * (px1 - px0 - 20); }, y = function (v) { return H - B - (v - ymin) / (ymax - ymin) * (H - B - T); };
    var KS = { open: { sh: "circle", c: "var(--s1)" }, api: { sh: "square", c: "var(--accent)" }, ref: { sh: "cross", c: "var(--s3)" } };
    var kind = function (m) { return m.id === "RandomBaselineModel" ? "ref" : m.kind; };
    var svg = '<svg viewBox="0 0 ' + W + " " + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + C.esc(t("size")) + '">';
    [ymin, (ymin + ymax) / 2, ymax].forEach(function (v) { svg += '<line class="grid" x1="' + px0 + '" x2="' + sx1 + '" y1="' + y(v).toFixed(1) + '" y2="' + y(v).toFixed(1) + '"/><text class="axis-num" x="' + (L - 6) + '" y="' + (y(v) + 4).toFixed(1) + '" text-anchor="end">' + C.fmt(v * 100, 0) + "</text>"; });
    var xt = [smin, smax]; [1, 3, 10, 30, 100, 300, 1000].forEach(function (s) { if (s > smin * 1.6 && s < smax / 1.6) xt.push(s); });
    xt.forEach(function (s) { svg += '<line class="tick" x1="' + lx(s).toFixed(1) + '" x2="' + lx(s).toFixed(1) + '" y1="' + (H - B) + '" y2="' + (H - B + 6) + '"/><text class="axis-num" x="' + lx(s).toFixed(1) + '" y="' + (H - B + 22) + '" text-anchor="middle">' + C.fmt(s, s < 1 ? 1 : 0) + "</text>"; });
    svg += '<text class="axis-num" x="' + ((sx0 + sx1) / 2) + '" y="' + (H - B + 22) + '" text-anchor="middle">?</text>';
    svg += '<line class="grid" x1="' + (sx0 - 6) + '" x2="' + (sx0 - 6) + '" y1="' + T + '" y2="' + (H - B) + '" style="stroke-dasharray:3 4"/>';
    var lab = D.models.filter(function (m) { return val(m) != null; }).sort(function (a, b) { return val(b) - val(a); }).slice(0, 6), hl = D.bySlug[S.hl];
    if (hl && lab.indexOf(hl) === -1) lab.push(hl);
    var swarm = {}, placed = [], cx0 = sx0 + stripW / 2 - 4;
    unk.slice().sort(function (a, b) { return val(b) - val(a); }).forEach(function (m) {
      var yy = y(val(m)), k = 0, xx;
      for (var n = 0; n < 12; n++) { k = n === 0 ? 0 : (n % 2 ? (n + 1) / 2 : -n / 2); xx = cx0 + k * 12; if (placed.every(function (p) { return Math.hypot(p[0] - xx, p[1] - yy) >= 12; })) break; }
      placed.push([xx, yy]); swarm[m.id] = [xx, yy];
    });
    var pos = function (m) { return m.size_b == null ? swarm[m.id] : [lx(m.size_b), y(val(m))]; };
    var allPts = [];
    D.models.forEach(function (m) { if (val(m) == null) return; var p = pos(m), k = KS[kind(m)]; allPts.push(p); svg += pt(+p[0].toFixed(1), +p[1].toFixed(1), C.shape(k.sh, +p[0].toFixed(1), +p[1].toFixed(1), 5, "fill:" + k.c + ";stroke:" + k.c, ""), ml(m), factsOf(m, val(m))); });
    if (hl && val(hl) != null) { var hp = pos(hl); svg += '<circle cx="' + hp[0].toFixed(1) + '" cy="' + hp[1].toFixed(1) + '" r="11" style="fill:none;stroke:var(--accent);stroke-width:3"/>'; }
    var top3 = lab.slice(0, 3).filter(function (m) { return m.size_b != null; }).map(function (m) { var p = pos(m); return { x: p[0], y: p[1], text: C.short(m) + " " + C.pct(val(m)), avoid: allPts }; });
    svg += placeLabels(top3, sx0 - 12, H);
    svg += "</svg>";
    var leg = ["open", "api", "ref"].map(function (k) { return '<li><svg width="16" height="16" aria-hidden="true">' + C.shape(KS[k].sh, 8, 8, 5, "fill:" + KS[k].c + ";stroke:" + KS[k].c, "") + "</svg>" + C.esc(t(k)) + "</li>"; }).join("");
    var ctr = '<div class="ctrls"><div class="picker"><label class="strong" for="s-y">' + C.esc(t("metric")) + '</label><select id="s-y" class="select"><option value="overall">' + C.esc(t("overall")) + "</option>" + D.cats.map(function (c) { return '<option value="' + c.key + '"' + (c.key === key ? " selected" : "") + ">" + C.esc(cl(c)) + "</option>"; }).join("") + '</select></div><div class="picker"><label class="strong" for="s-hl">' + C.esc(t("hl")) + '</label><select id="s-hl" class="select"><option value="">' + C.esc(t("none")) + "</option>" + D.models.map(function (m) { return '<option value="' + C.esc(m.name) + '"' + (m.name === S.hl ? " selected" : "") + ">" + C.esc(ml(m)) + "</option>"; }).join("") + "</select></div></div>";
    var ax = '<p class="small plate-ends"><span>' + C.esc(t("size")) + "</span><span>" + C.esc(t("unk", { n: unk.length })) + "</span></p>";
    var rows = D.models.slice().sort(function (a, b) { return val(b) - val(a); }).map(function (m) { return [ml(m), m.size_b == null ? t("na") : C.fmt(m.size_b, 1), C.pct(val(m))]; });
    host.innerHTML = ctr + '<ul class="plate-legend">' + leg + "</ul>" + svg + ax + tableOf([t("model"), t("size"), t("score")], rows, t("size")); host.setAttribute("aria-busy", "false"); bindTips(host);
    $("s-y").addEventListener("change", function (e) { S.sy = e.target.value; scatter(); $("s-y").focus(); });
    $("s-hl").addEventListener("change", function (e) { S.hl = e.target.value; scatter(); $("s-hl").focus(); });
  }

  /* 5. Quiz */
  function quiz() {
    var host = $("x5"), Q = X.quiz, n = Q.length, L = C.lang();
    if (S.q >= n) {
      var h = '<h3 class="lead strong">' + C.esc(t("qEnd", { k: S.score, n: n })) + '</h3><p>' + C.esc(t("qModels")) + '</p><ul class="g-list">';
      Q.forEach(function (q) { [D.bySlug["claude-opus-4"], D.bySlug["Qwen3-14B"], D.bySlug["RandomBaselineModel"]].forEach(function (m) { h += "<li>" + C.esc(t("testScore", { t: tname(q.task), m: ml(m), v: C.pct(m.tasks[q.task]) })) + "</li>"; }); });
      host.innerHTML = h + '</ul><p><button class="btn" type="button" id="q-restart">' + C.esc(t("restart")) + "</button></p>";
      $("q-restart").addEventListener("click", function () { S.q = 0; S.score = 0; S.checked = false; quiz(); var f = host.querySelector("input"); if (f) f.focus(); });
      return;
    }
    var q = Q[S.q], opts = q.options ? q.options : q.labels.map(function (l) { return l[L]; });
    var h2 = '<p class="strong" id="q-count">' + C.esc(t("qTitle", { i: S.q + 1, n: n })) + '</p><form id="q-form"><fieldset><legend class="lead strong">' + C.esc(C.loc2(q.family[L])) + "</legend>";
    if (q.prompt) h2 += '<p class="q-prompt">' + C.esc(q.prompt) + "</p>";
    h2 += opts.map(function (o, i) { return '<label class="q-opt"><input type="radio" name="q" value="' + i + '"' + (S.checked ? " disabled" : "") + (S.picks[S.q] === i ? " checked" : "") + "><span>" + C.esc(o) + "</span></label>"; }).join("") + "</fieldset>";
    h2 += '<p><button class="btn" type="submit"' + (S.checked ? " hidden" : "") + ">" + C.esc(t("check")) + '</button></p></form><div id="q-fb" role="status" aria-live="polite" class="stack"></div>';
    host.innerHTML = h2;
    var fb = $("q-fb");
    $("q-form").addEventListener("submit", function (e) {
      e.preventDefault();
      var c = host.querySelector("input:checked"); if (!c) { fb.textContent = t("choose"); return; }
      var v = +c.value; S.picks[S.q] = v; S.checked = true; if (v === q.answer) S.score++;
      host.querySelectorAll("input").forEach(function (i) { i.disabled = true; }); host.querySelector("button[type=submit]").hidden = true;
      fb.innerHTML = '<p class="strong">' + C.esc(t(v === q.answer ? "correct" : "wrong")) + "</p><p>" + C.esc(C.loc2(q.why[L])) + '</p><p><button class="btn" type="button" id="q-next">' + C.esc(t(S.q === n - 1 ? "seeRes" : "next")) + "</button></p>";
      $("q-next").focus();
      $("q-next").addEventListener("click", function () { S.q++; S.checked = false; quiz(); var f = host.querySelector("input,#q-restart"); if (f) f.focus(); });
    });
    host.setAttribute("aria-busy", "false");
  }

  /* 7. Progress over time */
  function progress() {
    var host = $("x6"), W = wid(host), H = W < 560 ? 340 : 400, L = 44, B = 44, T = 16, R = 16;
    var dated = D.models.filter(function (m) { return m.date; }).sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
    var mi = function (d) { var p = d.split("-"); return +p[0] * 12 + (+p[1] - 1); }, m0 = mi(dated[0].date), m1 = mi(dated[dated.length - 1].date);
    var vs = dated.map(function (m) { return m.overall; }), ymin = Math.floor(Math.min.apply(null, vs) * 10) / 10, ymax = Math.ceil(Math.max.apply(null, vs) * 10) / 10;
    var x = function (i) { return L + 12 + (i - m0) / Math.max(1, m1 - m0) * (W - L - R - 24); }, y = function (v) { return H - B - (v - ymin) / (ymax - ymin) * (H - B - T); };
    var d2 = function (d) { var p = d.split("-"); return new Date(+p[0], +p[1] - 1, 1).toLocaleDateString(C.loc(), { month: "long", year: "numeric" }); };
    var best = -1, path = "", recs = [], cur = null, rows = [];
    dated.forEach(function (m) { var rec = m.overall > best; if (rec) { best = m.overall; recs.push(m); } rows.push([m.date, ml(m), C.pct(m.overall, 2), C.pct(best, 2)]); });
    var steps = []; recs.forEach(function (m) { steps.push([mi(m.date), m.overall]); });
    path = "M" + x(steps[0][0]).toFixed(1) + "," + y(steps[0][1]).toFixed(1);
    for (var i = 1; i < steps.length; i++) path += "H" + x(steps[i][0]).toFixed(1) + "V" + y(steps[i][1]).toFixed(1);
    path += "H" + x(m1).toFixed(1);
    var svg = '<svg viewBox="0 0 ' + W + " " + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + C.esc(t("step")) + '">';
    [ymin, (ymin + ymax) / 2, ymax].forEach(function (v) { svg += '<line class="grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + y(v).toFixed(1) + '" y2="' + y(v).toFixed(1) + '"/><text class="axis-num" x="' + (L - 6) + '" y="' + (y(v) + 4).toFixed(1) + '" text-anchor="end">' + C.fmt(v * 100, 0) + "</text>"; });
    [[m0, "start"], [m1, "end"]].forEach(function (p) { var d = new Date(Math.floor(p[0] / 12), p[0] % 12, 1); svg += '<text class="axis-num" x="' + x(p[0]).toFixed(1) + '" y="' + (H - B + 22) + '" text-anchor="' + p[1] + '">' + d.toLocaleDateString(C.loc(), { month: "short", year: "numeric" }) + "</text>"; });
    svg += '<path d="' + path + '" style="fill:none;stroke:var(--accent);stroke-width:3"/>';
    dated.forEach(function (m) { var isRec = recs.indexOf(m) !== -1, px = +x(mi(m.date)).toFixed(1), py = +y(m.overall).toFixed(1); svg += pt(px, py, isRec ? C.shape("circle", px, py, 6, "fill:var(--accent);stroke:var(--accent)", "") : C.shape("ring", px, py, 6, "fill:none;stroke:var(--s1)", ""), ml(m), [d2(m.date), C.pct(m.overall, 1) + "\u00a0%"]); });
    var lastRecs = recs.slice(-2).map(function (m) { return { x: x(mi(m.date)), y: y(m.overall) - 14, text: C.short(m) + " " + C.pct(m.overall) }; });
    svg += placeLabels(lastRecs, W, H);
    svg += "</svg>";
    var leg = '<ul class="plate-legend"><li><svg width="30" height="16" aria-hidden="true"><path d="M0,8H30" style="stroke:var(--accent);stroke-width:3"/></svg>' + C.esc(t("step")) + '</li><li><svg width="16" height="16" aria-hidden="true">' + C.shape("ring", 8, 8, 6, "fill:none;stroke:var(--s1)", "") + "</svg>" + C.esc(t("ring")) + "</li></ul>";
    host.innerHTML = leg + svg + '<p class="small">' + C.esc(t("tNo", { n: D.models.length - dated.length })) + "</p>" + tableOf([t("mth"), t("model"), t("score"), t("best")], rows, t("tDated")); host.setAttribute("aria-busy", "false"); bindTips(host);
  }


  function median(a) { if (!a.length) return null; var b = a.slice().sort(function (x, y) { return x - y; }), n = b.length; return n % 2 ? b[(n - 1) / 2] : (b[n / 2 - 1] + b[n / 2]) / 2; }
  /* split a caption over two lines at the space nearest the middle (SVG text does not wrap) */
  function wrap2(str, lines, x) {
    if (lines < 2) return C.esc(str);
    var mid = str.length / 2, best = -1, i;
    for (i = 0; i < str.length; i++) if (str[i] === " " && (best < 0 || Math.abs(i - mid) < Math.abs(best - mid))) best = i;
    return C.esc(str.slice(0, best)) + '<tspan x="' + x + '" dy="16">' + C.esc(str.slice(best + 1)) + "</tspan>";
  }
  function pc1(v) { return C.pct(v, 1); }
  function legendShape(sh, c, label) { return '<li><svg width="16" height="16" aria-hidden="true">' + C.shape(sh, 8, 8, 5, "fill:" + c + ";stroke:" + c, "") + "</svg>" + C.esc(label) + "</li>"; }
  /* spread of points in one lane, no overlap: offsets 0, +1, -1, +2, -2 ... of one marker step */
  function lane(vals, x, cy, step, maxK) {
    var placed = [], out = [];
    vals.slice().sort(function (a, b) { return a.v - b.v; }).forEach(function (o) {
      var xx = x(o.v), best = 0, bestScore = -1;
      for (var n = 0; n < 2 * maxK + 1; n++) {
        var k = n === 0 ? 0 : (n % 2 ? (n + 1) / 2 : -n / 2), yy = cy + k * step, mn = 99;
        placed.forEach(function (p) { mn = Math.min(mn, Math.hypot(p[0] - xx, p[1] - yy)); });
        if (mn >= step) { best = k; bestScore = 99; break; }
        if (mn > bestScore) { bestScore = mn; best = k; }
      }
      var yy2 = cy + best * step; placed.push([xx, yy2]); out.push({ o: o, x: xx, y: yy2 });
    });
    return out;
  }

  /* 8. Open weights against API, per skill */
  function access() {
    var host = $("x7"), W = wid(host), wide = W >= 640, lw = wide ? 210 : 0, pad = 22, x0 = lw + pad, x1 = W - pad, x = function (v) { return x0 + v * (x1 - x0); };
    var pool = D.models.filter(function (m) { return m.id !== "RandomBaselineModel" && (m.kind === "open" || m.kind === "api"); });
    var rows = D.cats.map(function (c) {
      var g = { open: [], api: [] };
      pool.forEach(function (m) { var sc = m.categories[c.key]; if (sc && sc.score != null) g[m.kind].push({ m: m, v: sc.score }); });
      var mo = median(g.open.map(function (o) { return o.v; })), ma = median(g.api.map(function (o) { return o.v; }));
      return { c: c, g: g, mo: mo, ma: ma, d: ma - mo, so: Math.max.apply(null, g.open.map(function (o) { return o.v; })), sa: Math.max.apply(null, g.api.map(function (o) { return o.v; })) };
    }).filter(function (r) { return r.g.open.length && r.g.api.length; }).sort(function (a, b) { return Math.abs(b.d) - Math.abs(a.d); });
    var k = rows.filter(function (r) { return r.so > r.ma; }).length, LH = 54, head = wide ? 0 : 40, rh = LH * 2 + 14 + head, top = 30;
    var svg = '<svg viewBox="0 0 ' + W + " " + (top + rows.length * rh) + '" width="' + W + '" height="' + (top + rows.length * rh) + '" role="img" aria-label="' + C.esc(t("axCap")) + '">' + axisTicks(x, 22, 0, 1, pad, W);
    rows.forEach(function (r, i) {
      var y0 = top + i * rh, nm = cl(r.c), gap = t(r.d >= 0 ? "gApi" : "gOpen", { d: C.fmt(Math.abs(r.d) * 100, 1) });
      var cyO = y0 + head + LH / 2, cyA = y0 + head + LH + LH / 2 - 2;
      svg += '<text class="row-name" x="' + (wide ? 0 : pad) + '" y="' + (wide ? y0 + 22 : y0 + 14) + '">' + C.esc(nm) + '</text><text class="small-svg" x="' + (wide ? 0 : pad) + '" y="' + (wide ? y0 + 40 : y0 + 33) + '">' + wrap2(gap, wide ? 2 : 1, wide ? 0 : pad) + "</text>";
      [[r.g.open, cyO, "circle", "var(--s1)", r.mo, "axOpen"], [r.g.api, cyA, "square", "var(--accent)", r.ma, "axApi"]].forEach(function (L) {
        svg += '<line class="track" x1="' + x0 + '" y1="' + L[1] + '" x2="' + x1 + '" y2="' + L[1] + '"/>';
        lane(L[0], x, L[1], 8, 3).forEach(function (p) { svg += pt(+p.x.toFixed(1), +p.y.toFixed(1), C.shape(L[2], +p.x.toFixed(1), +p.y.toFixed(1), 3.4, "fill:" + L[3] + ";stroke:" + L[3] + ";fill-opacity:.7", ""), ml(p.o.m), [t(L[5]), pc1(p.o.v) + "\u00a0%"], true); });
        var mx = +x(L[4]).toFixed(1);
        svg += pt(mx, L[1], '<rect x="' + (mx - 2) + '" y="' + (L[1] - 17) + '" width="4" height="34" style="fill:var(--bg);stroke:var(--deep);stroke-width:1"/>', t("med") + ", " + t(L[5]), [pc1(L[4]) + "\u00a0%", t("nMod", { n: L[0].length })]);
      });
    });
    svg += "</svg>";
    var leg = '<ul class="plate-legend">' + legendShape("circle", "var(--s1)", t("axOpen")) + legendShape("square", "var(--accent)", t("axApi")) + '<li><svg width="16" height="16" aria-hidden="true"><rect x="6" y="1" width="4" height="14" style="fill:var(--bg)"/></svg>' + C.esc(t("med")) + "</li></ul>";
    var tbl = tableOf([C.lang() === "en" ? "Skill" : "Compétence", t("axOpen") + " (" + t("med").toLowerCase() + ")", t("axApi") + " (" + t("med").toLowerCase() + ")", t("strongOpen"), t("strongApi")], rows.map(function (r) { return [cl(r.c), pc1(r.mo), pc1(r.ma), pc1(r.so), pc1(r.sa)]; }), t("axCap"));
    host.innerHTML = '<p class="lead">' + C.esc(t("axSum", { k: k, n: rows.length })) + "</p>" + leg + svg + tbl; host.setAttribute("aria-busy", "false"); bindTips(host);
  }

  /* 9. The hardest tasks: strongest and median model against random guessing.
     Build note (not shown on the page): fquad zeros are under verification, so fquad never drives the "close to guessing" highlight. */
  var UNVERIFIED = ["fquad"];
  function hard() {
    var host = $("x8"), W = wid(host), wide = W >= 640, lw = wide ? 210 : 0, pad = 22, x0 = lw + pad, x1 = W - pad - (wide ? 34 : 30), x = function (v) { return x0 + v * (x1 - x0); };
    var pool = D.models.filter(function (m) { return m.id !== "RandomBaselineModel"; }), groups = [];
    D.cats.forEach(function (c) {
      var rs = c.tasks.map(function (k) {
        var xs = pool.filter(function (m) { return m.tasks[k] != null; }), vs = xs.map(function (m) { return m.tasks[k]; }), ch = X.chance[k], cv = ch && ch.basis === "random-baseline" && ch.value != null ? ch.value : null;
        var bm = xs.reduce(function (a, m) { return a == null || m.tasks[k] > a.tasks[k] ? m : a; }, null), best = bm.tasks[k], med = median(vs);
        return { k: k, best: best, bm: bm, med: med, ch: cv, gap: cv == null ? null : best - cv, near: cv != null && UNVERIFIED.indexOf(k) === -1 && med - cv <= 0.05, n: vs.length };
      }).sort(function (a, b) { if (a.gap == null) return 1; if (b.gap == null) return -1; return a.gap - b.gap; });
      groups.push({ c: c, rs: rs, first: rs[0].gap == null ? 9 : rs[0].gap });
    });
    groups.sort(function (a, b) { return a.first - b.first; });
    var all = [].concat.apply([], groups.map(function (g) { return g.rs; })), meaningful = all.filter(function (r) { return r.gap != null; }), minGap = meaningful.slice().sort(function (a, b) { return a.gap - b.gap; })[0];
    var nearN = all.filter(function (r) { return r.near; }).length, RH = wide ? 36 : 58, GH = 40, top = 30;
    var H = top + groups.length * GH + all.length * RH, y = top, svg = '<svg viewBox="0 0 ' + W + " " + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + C.esc(t("hardCap")) + '">' + axisTicks(x, 22, 0, 1, pad, W);
    groups.forEach(function (g) {
      svg += '<text class="row-name" x="0" y="' + (y + 28) + '">' + C.esc(cl(g.c)) + "</text>"; y += GH;
      g.rs.forEach(function (r) {
        var cy = y + (wide ? RH / 2 : RH - 14), nameY = wide ? cy + 5 : y + 14;
        svg += '<text class="task-name' + (r.near ? " is-hard" : "") + '" x="' + (wide ? 0 : pad) + '" y="' + nameY + '">' + C.esc(tname(r.k)) + "</text>";
        svg += '<line class="track" x1="' + x0 + '" y1="' + cy + '" x2="' + x(1) + '" y2="' + cy + '"/>';
        if (r.ch != null) svg += '<line class="link" x1="' + x(r.ch).toFixed(1) + '" y1="' + cy + '" x2="' + x(r.best).toFixed(1) + '" y2="' + cy + '" style="stroke:var(--s1);stroke-width:4"/><line x1="' + x(r.ch).toFixed(1) + '" y1="' + (cy - 9) + '" x2="' + x(r.ch).toFixed(1) + '" y2="' + (cy + 9) + '" style="stroke:var(--accent);stroke-width:3"/>';
        var facts = [pc1(r.best) + "\u00a0%"].concat(r.ch == null ? [t("noCh")] : [t("chanceV", { v: pc1(r.ch) + "\u00a0%" })]);
        svg += pt(+x(r.med).toFixed(1), cy, C.shape("square", +x(r.med).toFixed(1), cy, 5, "fill:var(--bg);stroke:var(--deep);stroke-width:1.5", ""), t("hMed") + " " + tname(r.k), [pc1(r.med) + "\u00a0%", t("nMod", { n: r.n })], true);
        svg += pt(+x(r.best).toFixed(1), cy, C.shape("circle", +x(r.best).toFixed(1), cy, 6, "fill:var(--bg);stroke:var(--s1);stroke-width:3", ""), ml(r.bm), [t("bestM") + ", " + tname(r.k), pc1(r.best) + "\u00a0%"].concat(r.ch == null ? [t("noCh")] : [t("chanceV", { v: pc1(r.ch) + "\u00a0%" })]));
        svg += '<text class="end-label" x="' + (x(r.best) + 12).toFixed(1) + '" y="' + (cy + 5) + '" style="fill:var(--bg)">' + C.pct(r.best) + "</text>";
        y += RH;
      });
    });
    svg += "</svg>";
    var leg = '<ul class="plate-legend"><li><svg width="16" height="16" aria-hidden="true"><line x1="8" y1="1" x2="8" y2="15" style="stroke:var(--accent);stroke-width:3"/></svg>' + C.esc(t("chTk")) + "</li>" + legendShape("circle", "var(--bg)", t("bestMk")) + legendShape("square", "var(--bg)", t("medMk")) + '<li class="strong">' + C.esc(t("boldK")) + "</li></ul>";
    var tbl = tableOf([C.lang() === "en" ? "Task" : "Épreuve", C.lang() === "en" ? "Skill" : "Compétence", t("bestM"), t("hMed"), t("chTk")], all.map(function (r) {
      var cat = groups.filter(function (g) { return g.rs.indexOf(r) !== -1; })[0].c; return [tname(r.k), cl(cat), ml(r.bm) + " " + pc1(r.best), pc1(r.med), r.ch == null ? t("na") : pc1(r.ch)];
    }), t("hardCap"));
    host.innerHTML = '<p class="lead">' + C.esc(t("hardSum", { g: C.fmt(minGap.gap * 100, 0), t: tname(minGap.k), k: nearN, n: meaningful.length })) + "</p>" + leg + svg + tbl; host.setAttribute("aria-busy", "false"); bindTips(host);
  }

  function renderAll() { dumbbell(); gauge(); hard(); heat(); scatter(); access(); quiz(); progress(); }
  function load() {
    stateAll("loading");
    Promise.all([C.load(), C.json("data/extra.json")]).then(function (r) { D = r[0]; X = r[1]; if (C.forced === "empty") stateAll("empty"); else renderAll(); }).catch(function (e) { console.error(e); stateAll("error"); });
  }
  document.addEventListener("langchange", function () { if (D) renderAll(); else if (C.forced === "error") stateAll("error"); else stateAll("loading"); });
  var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(function () { if (D) { dumbbell(); hard(); scatter(); access(); progress(); } }, 160); });
  load();
})();
