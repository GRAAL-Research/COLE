/* Step 1, model sheet: one model, its rank, its seven skills, every test. The model comes from ?model=slug and follows the reader. */
(function () {
  "use strict";
  var C = window.COLE, $ = function (id) { return document.getElementById(id); };
  var STR = {
    en: {
      loading: "Loading the model sheet…", errorTitle: "We could not load the results.", errorBody: "The data file did not answer. Check your connection and try again.", retry: "Try again",
      unknown: "We do not know a model called “{m}”. Pick one from the list.", pick: "Model",
      rank: "Rank {r} of {n}", overall: "Overall score (%)", skills: "Seven skills", tests: "{n} of {of} tests", partial: "A test is missing for this skill, so the score uses {n} of {of}.",
      best: "Strongest skill: {c} ({v} %). Weakest: {w} ({x} %).", marker: "Marker: random guessing", all: "Every test (%)", task: "Test", skill: "Skill", metric: "Metric", score: "Score", na: "n/a",
      capTasks: "Score per test, in percent. n/a means no result for that test, never zero.", emptyTitle: "No model chosen.", emptyBody: "Pick a model in the list to see where it is strong.", showing: "Showing {m}.", deeper: "Go further: all tests of this model, and 95 other models", date: "Model version dated {d}", fam: "Family: {f}", unk: "unknown", exOpen: "See an example", exClose: "Hide the example", exLead: "A real item from the public data of these tests ({s} part).", exAns: "Answer given by the dataset: {a}", exTrain: "training", exVal: "validation"
    },
    fr: {
      loading: "Chargement de la fiche du modèle…", errorTitle: "Nous n’avons pas pu charger les résultats.", errorBody: "Le fichier de données n’a pas répondu. Vérifiez votre connexion et réessayez.", retry: "Réessayer",
      unknown: "Nous ne connaissons pas de modèle nommé « {m} ». Choisissez-en un dans la liste.", pick: "Modèle",
      rank: "Rang {r} sur {n}", overall: "Score général (%)", skills: "Sept compétences", tests: "{n} tests sur {of}", partial: "Un test manque pour cette compétence ; le score repose sur {n} tests sur {of}.",
      best: "Compétence la plus forte : {c} ({v} %). La plus faible : {w} ({x} %).", marker: "Repère : tirage au hasard", all: "Chaque test (%)", task: "Test", skill: "Compétence", metric: "Métrique", score: "Score", na: "n.d.",
      capTasks: "Score par test, en pourcentage. n.d. signifie aucun résultat pour ce test, jamais zéro.", emptyTitle: "Aucun modèle choisi.", emptyBody: "Choisissez un modèle dans la liste pour voir où il est fort.", showing: "Affichage : {m}.", deeper: "Aller plus loin : tous les tests de ce modèle, et 95 autres modèles", date: "Version du modèle datée du {d}", fam: "Famille : {f}", unk: "inconnue", exOpen: "Voir un exemple", exClose: "Masquer l’exemple", exLead: "Un vrai exemple tiré des données publiques de ces tests (partie {s}).", exAns: "Réponse donnée par le jeu de données : {a}", exTrain: "entraînement", exVal: "validation"
    }
  };
  var t = C.makeT(STR), D, X = null, cur = null, host = $("sheet-host");
  function cl(c) { return c.short[C.lang()]; }
  var ICONS = {
    sentiment: '<circle cx="12" cy="12" r="9"/><path d="M8 14c1.2 2 6.8 2 8 0M9 9v1M15 9v1"/>',
    reasoning: '<path d="M4 4h6v6H4zM14 14h6v6h-6zM10 7h4v7"/>',
    questions: '<path d="M4 5h16v11h-9l-5 4v-4H4z"/><path d="M10 9.5c0-2 4-2 4 0 0 1.5-2 1.5-2 3"/>',
    grammar: '<path d="M4 7h16M4 12h9M4 17h6M14 17l3 3 5-6"/>',
    meaning: '<circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/>',
    pronouns: '<circle cx="8" cy="8" r="3"/><path d="M3 20v-3a5 5 0 0 1 10 0v3M16 8h5M19 5l3 3-3 3"/>',
    quebec: '<path d="M12 3v18M5 9c3 0 5 2 7 4 2-2 4-4 7-4M7 17l5-4 5 4"/>'
  };
  function state(kind, extra) {
    if (kind === "loading") host.innerHTML = '<div class="skel-rows" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div><p class="small">' + C.esc(t("loading")) + "</p>";
    else host.innerHTML = '<div class="state"><h3 class="lead strong">' + C.esc(t("errorTitle")) + "</h3><p>" + C.esc(t("errorBody")) + '</p><button class="btn" type="button" id="retry">' + C.esc(t("retry")) + "</button></div>";
    host.setAttribute("aria-busy", kind === "loading");
    if (kind === "error") $("retry").addEventListener("click", load);
  }
  /* one real item per skill when the quiz data has a verified one (shortest wins); none invented, no model result per item */
  function exampleFor(c) {
    if (!X) return null;
    var L = C.lang(), pool = X.quiz.filter(function (q) { return c.tasks.indexOf(q.task) !== -1; });
    pool.sort(function (a, b) { return (a.prompt || a.options.join(" ")).length - (b.prompt || b.options.join(" ")).length; });
    var q = pool[0]; if (!q) return null;
    var txt = q.prompt || q.options.map(function (o, i) { return (i + 1) + ". " + o; }).join("\n");
    return { q: q, txt: txt, ans: q.labels[q.answer][L], head: C.loc2(q.family[L]) };
  }
  function render() {
    var m = cur;
    var h = '<div class="sheet-grid"><div class="stack"><h2 class="head">' + C.esc(C.mlabel(m)) + '</h2><p class="facts">' + C.esc(C.mtype(m)) + "</p></div>";
    h += '<div class="stack"><p class="figure-big">' + C.pct(m.overall) + '</p><p class="strong">' + C.esc(t("overall")) + " · " + C.esc(t("rank", { r: m.rank, n: D.models.length })) + "</p></div></div>";
    h += '<h3 class="lead strong">' + C.esc(t("skills")) + '</h3><div class="bars-sheet">';
    D.cats.forEach(function (c, i) {
      var cs = m.categories[c.key], sc = cs.score, part = cs.n < cs.of && sc != null ? t("tests", { n: cs.n, of: cs.of }) : "";
      h += '<div class="bar-row" style="--i:' + i + '"><span class="bar-label cat-line"><svg class="icon-cat" viewBox="0 0 24 24" aria-hidden="true">' + (ICONS[c.key] || "") + "</svg><span>" + C.esc(cl(c)) + '<span class="cat-plain">' + C.esc(c.plain[C.lang()]) + "</span>" + (part ? '<span class="cat-plain">' + C.esc(part) + "</span>" : "") + "</span></span>" +
        (sc == null ? '<span class="bar-line"><span class="bar-track"></span><span class="bar-val">' + C.esc(t("na")) + "</span></span>" : '<span class="bar-line"><span class="bar-track"><span class="bar-fill is-in" style="--w:' + (sc * 100).toFixed(1) + '%"></span></span><span class="bar-val">' + C.pct(sc) + "</span></span>");
      var ex = exampleFor(c);
      if (ex) h += '<div class="ex"><button type="button" class="link-btn ex-btn" aria-expanded="false" aria-controls="ex-' + c.key + '" data-ex="' + c.key + '" data-open="' + C.esc(t("exOpen")) + '" data-close="' + C.esc(t("exClose")) + '">' + C.esc(t("exOpen")) + '</button><div class="ex-body" id="ex-' + c.key + '" hidden><p class="strong">' + C.esc(ex.head) + '</p><p class="ex-text">' + C.esc(ex.txt) + '</p><p>' + C.esc(t("exAns", { a: ex.ans })) + '</p><p class="small">' + C.esc(t("exLead", { s: t(ex.q.split === "train" ? "exTrain" : "exVal") })) + "</p></div></div>";
      h += "</div>";
    });
    h += '</div><p class="small axis-ends"><span>0</span><span>100</span></p>';
    host.innerHTML = h; host.setAttribute("aria-busy", "false");
    host.querySelectorAll(".ex-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        var open = b.getAttribute("aria-expanded") !== "true";
        host.querySelectorAll(".ex-btn").forEach(function (o) { o.setAttribute("aria-expanded", "false"); o.textContent = o.dataset.open; $(o.getAttribute("aria-controls")).hidden = true; });
        if (open) { b.setAttribute("aria-expanded", "true"); b.textContent = b.dataset.close; $(b.getAttribute("aria-controls")).hidden = false; }
      });
    });
    $("m-live").textContent = t("showing", { m: C.mlabel(m) });
    if (window.coleCarry) window.coleCarry(m.name);
  }
  function fill() {
    var sel = $("m-pick");
    sel.innerHTML = D.models.slice().sort(function (a, b) { return a.rank - b.rank; }).map(function (m) { return '<option value="' + C.esc(m.name) + '">' + C.esc(C.mlabel(m)) + "</option>"; }).join("");
    sel.innerHTML = '<option value="" hidden></option>' + sel.innerHTML; sel.value = cur.name; sel.disabled = false;
  }
  function set(slug, push) {
    cur = D.bySlug[slug]; $("m-pick").value = cur.name;
    if (push) history.replaceState(null, "", location.pathname + "?model=" + encodeURIComponent(cur.name));
    if (window.coleCarry) window.coleCarry(cur.name);
    render();
  }
  function load() {
    state("loading");
    if (C.forced === "empty") { C.load().then(function (d) { D = d; cur = D.bySlug["claude-opus-4"]; fill(); $("m-pick").value = ""; host.setAttribute("aria-busy", "false"); host.innerHTML = '<div class="state"><h3 class="lead strong">' + C.esc(t("emptyTitle")) + "</h3><p>" + C.esc(t("emptyBody")) + "</p></div>"; }).catch(function () { state("error"); }); return; }
    C.json("data/extra.json").then(function (x) { X = x; }, function () { X = null; }).then(function () { return C.load(); }).then(function (d) {
      D = d; var p = new URLSearchParams(location.search).get("model"), bad = p && !D.bySlug[p];
      cur = D.bySlug[p] || D.bySlug["claude-opus-4"]; fill();
      if (window.coleCarry) window.coleCarry(cur.name);
      render();
      if (bad) { var n = document.createElement("p"); n.className = "state-note strong"; n.setAttribute("role", "status"); n.textContent = t("unknown", { m: p }); host.prepend(n); }
    }).catch(function () { state("error"); });
  }
  $("m-pick").addEventListener("change", function (e) { set(e.target.value, true); });
  document.addEventListener("langchange", function () { if (D) { fill(); render(); } else if (C.forced === "error") state("error"); else state("loading"); });
  load();
})();
