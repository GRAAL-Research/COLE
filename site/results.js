/* All results: the full leaderboard. Sort, search, filter, expand categories into tasks, select models for the comparison, download. */
(function () {
  "use strict";
  var C = window.COLE, $ = function (id) { return document.getElementById(id); };
  var STR = {
    en: {
      loading: "Loading the results…", errorTitle: "We could not load the results.", errorBody: "The data file did not answer. Check your connection and try again.", retry: "Try again",
      rank: "Rank", model: "Model", overall: "Overall", tasks: "Tasks", hideTasks: "Hide tasks", na: "n/a", matching: "{n} models match.", shownOf: "{s} shown.", showing: "{n} models", showingFirst: "First {s} models of {n}", scrollHint: "Scroll the table sideways to see every column.", more: "Show 25 more",
      none: "No model matches these filters.", noneHelp: "Relax a filter or clear them all.", clear: "Clear filters", family: "Family", type: "Type", size: "Size", any: "Any",
      tAPI: "Served through an API", tOpen: "Open weights", tRef: "Reference", sUnknown: "Unknown size", s1: "Under 3 billion", s2: "3 to 10 billion", s3: "10 to 35 billion", s4: "Over 35 billion",
      search: "Search by model name", dec: "Two decimals", sel: "{n} selected (6 at most)", compare: "Compare these {n} models", selClear: "Clear selection", selNeed: "Select 2 to 6 models to compare them.",
      pick: "Compare {m}", maxPick: "Six models are already selected.", remove: "Remove {m}", unknownFam: "Unknown",
      caption: "All results, score in percent. n/a means no result for that test, never zero.", region: "Results table, scrolls sideways",
      naNote: "n/a: no result, never counted as zero.", unrel: "n/a: evaluation not reliable for this model on this task, under verification.", unit: "Scores in %", toggleOn: "Show the tasks (each test and its metric)", toggleOff: "Hide the tasks", csv: "Download CSV", json: "Download JSON", downloaded: "Downloaded {f}.", metricLabel: "Metric: {m}", yourModel: "Your model"
    },
    fr: {
      loading: "Chargement des résultats…", errorTitle: "Nous n’avons pas pu charger les résultats.", errorBody: "Le fichier de données n’a pas répondu. Vérifiez votre connexion et réessayez.", retry: "Réessayer",
      rank: "Rang", model: "Modèle", overall: "Général", tasks: "Tâches", hideTasks: "Masquer les tâches", na: "n.d.", matching: "{n} modèles correspondent.", shownOf: "{s} affichés.", showing: "{n} modèles", showingFirst: "{s} premiers modèles sur {n}", scrollHint: "Faites défiler le tableau latéralement pour voir toutes les colonnes.", more: "Afficher 25 de plus",
      none: "Aucun modèle ne correspond à ces filtres.", noneHelp: "Assouplissez un filtre ou effacez-les tous.", clear: "Effacer les filtres", family: "Famille", type: "Type", size: "Taille", any: "Toutes",
      tAPI: "Utilisé par API", tOpen: "Poids ouverts", tRef: "Référence", sUnknown: "Taille inconnue", s1: "Moins de 3 milliards", s2: "3 à 10 milliards", s3: "10 à 35 milliards", s4: "Plus de 35 milliards",
      search: "Chercher par nom de modèle", dec: "Deux décimales", sel: "{n} sélectionnés (6 au maximum)", compare: "Comparer ces {n} modèles", selClear: "Effacer la sélection", selNeed: "Sélectionnez de 2 à 6 modèles pour les comparer.",
      pick: "Comparer {m}", maxPick: "Six modèles sont déjà sélectionnés.", remove: "Retirer {m}", unknownFam: "Inconnue",
      caption: "Tous les résultats, score en pourcentage. n.d. signifie aucun résultat pour ce test, jamais zéro.", region: "Tableau des résultats, défile horizontalement",
      naNote: "n.d. : pas de résultat, jamais compté comme zéro.", unrel: "n.d. : évaluation non fiable pour ce modèle sur cette épreuve, en cours de vérification.", unit: "Scores en %", toggleOn: "Afficher les tâches (chaque test et sa métrique)", toggleOff: "Masquer les tâches", csv: "Télécharger le CSV", json: "Télécharger le JSON", downloaded: "{f} téléchargé.", metricLabel: "Métrique : {m}", yourModel: "Votre modèle"
    }
  };
  var t = C.makeT(STR), D;
  var FOCUS = new URLSearchParams(location.search).get("model");
  var S = { q: "", fam: "", type: "", size: "", dec: 1, open: {}, sortKey: "overall", sortDir: "desc", limit: 25, sel: [] };
  function ml(m) { return C.mlabel(m); }
  function cl(c, sh) { return (sh ? c.short : c.label)[C.lang()]; }
  function typeOf(m) { return m.id === "RandomBaselineModel" ? "ref" : m.kind; }
  function famLabel(m) { return m.family === "unknown" ? t("unknownFam") : m.family; }
  function columns() {
    var cols = [{ key: "overall", kind: "overall" }];
    D.cats.forEach(function (c) {
      cols.push({ key: c.key, kind: "cat", cat: c });
      if (S.open[c.key]) c.tasks.forEach(function (k) { cols.push({ key: "t:" + k, kind: "task", task: k, cat: c }); });
    });
    return cols;
  }
  function val(m, col) {
    if (col.kind === "overall") return m.overall;
    if (col.kind === "cat") return m.categories[col.key].score;
    var v = m.tasks[col.task]; return v == null ? null : v;
  }
  function sortVal(m, key) {
    if (key === "rank") return -m.rank; if (key === "name") return ml(m).toLowerCase();
    if (key === "overall") return m.overall; if (key.indexOf("t:") === 0) return m.tasks[key.slice(2)] == null ? null : m.tasks[key.slice(2)];
    return m.categories[key].score;
  }
  function filtered() {
    var q = C.norm(S.q);
    var rows = D.models.filter(function (m) {
      if (q && C.norm(ml(m)).indexOf(q) === -1 && C.norm(m.id).indexOf(q) === -1) return false;
      if (S.fam && m.family !== S.fam) return false;
      if (S.type && typeOf(m) !== S.type) return false;
      if (S.size && C.bucket(m) !== S.size) return false;
      return true;
    });
    rows.sort(function (a, b) {
      var x = sortVal(a, S.sortKey), y = sortVal(b, S.sortKey);
      if (x == null && y == null) return 0; if (x == null) return 1; if (y == null) return -1;
      var r = typeof x === "string" ? x.localeCompare(y) : x - y;
      return S.sortDir === "desc" ? -r : r;
    });
    return rows;
  }
  function showState(kind) {
    var host = $("res-host");
    if (kind === "loading") host.innerHTML = '<div class="skel-rows" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span></div><p class="small" role="status">' + C.esc(t("loading")) + "</p>";
    if (kind === "error") { host.innerHTML = '<div class="state"><h3 class="lead strong">' + C.esc(t("errorTitle")) + "</h3><p>" + C.esc(t("errorBody")) + '</p><button class="btn" type="button" id="retry">' + C.esc(t("retry")) + "</button></div>"; $("retry").addEventListener("click", load); $("retry").focus(); }
    document.querySelectorAll("[data-needs-data]").forEach(function (e) { e.disabled = true; });
    $("count").textContent = "";
  }
  function fillSelect(id, items, anyLabel, value) {
    var el = $(id);
    el.innerHTML = '<option value="">' + C.esc(anyLabel) + "</option>" + items.map(function (i) { return '<option value="' + C.esc(i[0]) + '">' + C.esc(i[1]) + "</option>"; }).join("");
    el.value = value;
  }
  function filters() {
    var fams = {}; D.models.forEach(function (m) { fams[m.family] = (fams[m.family] || 0) + 1; });
    fillSelect("f-fam", Object.keys(fams).sort().map(function (f) { return [f, (f === "unknown" ? t("unknownFam") : f) + " (" + fams[f] + ")"]; }), t("any"), S.fam);
    fillSelect("f-type", [["api", t("tAPI")], ["open", t("tOpen")], ["ref", t("tRef")]], t("any"), S.type);
    fillSelect("f-size", [["lt3", t("s1")], ["3to10", t("s2")], ["10to35", t("s3")], ["gt35", t("s4")], ["unknown", t("sUnknown")]], t("any"), S.size);
    $("q").value = S.q; $("dec").checked = S.dec === 2;
    document.querySelectorAll("[data-needs-data]").forEach(function (e) { e.disabled = false; });
  }
  function table(rows) {
    var cols = columns(), shown = rows.slice(0, S.limit), d = S.dec;
    var sortBtn = function (key, label, sub) {
      var dir = S.sortKey === key ? S.sortDir : "";
      return '<button class="sort-btn" type="button" data-sort="' + C.esc(key) + '"' + (dir ? ' data-dir="' + dir + '"' : "") + ">" + C.esc(label) + (sub ? '<span class="note-part">' + C.esc(sub) + "</span>" : "") + "</button>";
    };
    var aria = function (key) { return S.sortKey === key ? (S.sortDir === "desc" ? "descending" : "ascending") : "none"; };
    var h = '<div class="scroll-wrap" id="scroll-wrap"><div class="table-scroll" id="tscroll" tabindex="0" role="region" aria-label="' + C.esc(t("region")) + '"><table class="data wide"><caption class="vh">' + C.esc(t("caption")) + "</caption><thead><tr>";
    h += '<th scope="col" class="sticky-1" aria-sort="' + aria("rank") + '">' + sortBtn("rank", t("rank")) + '</th><th scope="col" class="l sticky-2" aria-sort="' + aria("name") + '">' + sortBtn("name", t("model")) + "</th>";
    cols.forEach(function (c) {
      if (c.kind === "overall") h += '<th scope="col" aria-sort="' + aria("overall") + '">' + sortBtn("overall", t("overall")) + "</th>";
      else if (c.kind === "cat") h += '<th scope="col" aria-sort="' + aria(c.key) + '">' + sortBtn(c.key, cl(c.cat, true)) + "</th>";
      else h += '<th scope="col" class="task" aria-sort="' + aria(c.key) + '">' + sortBtn(c.key, D.taskNames[c.task].name, D.taskNames[c.task].metric) + "</th>";
    });
    h += "</tr></thead><tbody>";
    shown.forEach(function (m) {
      var foc = FOCUS && m.name === FOCUS, on = S.sel.indexOf(m.name) !== -1, dis = !on && S.sel.length >= 6;
      h += "<tr" + (on || foc ? ' class="' + (on ? "is-picked " : "") + (foc ? "is-focus" : "") + '"' : "") + (foc ? ' id="row-focus"' : "") + '><td class="sticky-1">' + m.rank + '</td><th scope="row" class="l sticky-2"><label class="pick"><input type="checkbox" data-pick="' + C.esc(m.name) + '"' + (on ? " checked" : "") + (dis ? ' disabled title="' + C.esc(t("maxPick")) + '"' : "") + ' aria-label="' + C.esc(t("pick", { m: ml(m) })) + '"><span>' + C.esc(ml(m)) + '</span></label>' + (foc ? '<span class="focus-tag">' + C.esc(t("yourModel")) + "</span>" : "") + '<span class="note-part">' + C.esc(famLabel(m) + (m.size_b == null ? "" : ", " + C.msize(m))) + "</span></th>";
      cols.forEach(function (c) { var v = val(m, c); h += "<td" + (c.kind === "task" ? ' class="task"' : "") + ">" + (v == null ? C.esc(t("na")) : C.pct(v, d)) + "</td>"; });
      h += "</tr>";
    });
    h += "</tbody></table></div></div>" + (shown.length ? '<p class="small scroll-hint">' + C.esc(t("scrollHint")) + "</p>" : "");
    var anyNa = shown.some(function (m) { return cols.some(function (c) { return val(m, c) == null; }); });
    var anyUnrel = shown.some(function (m) { return cols.some(function (c) { return c.kind === "task" && val(m, c) == null && (m.unreliable_tasks || []).indexOf(c.task) !== -1; }); });
    if (anyNa) h += '<p class="small" id="na-note">' + C.esc(t("naNote")) + (anyUnrel ? " " + C.esc(t("unrel")) : "") + "</p>";
    if (!shown.length) h = '<div class="state"><h3 class="lead strong">' + C.esc(t("none")) + "</h3><p>" + C.esc(t("noneHelp")) + '</p><button class="btn" type="button" id="empty-clear">' + C.esc(t("clear")) + "</button></div>";
    if (rows.length > shown.length) h += '<p style="margin-top:1rem"><button class="btn btn-ghost" type="button" id="more">' + C.esc(t("more")) + "</button></p>";
    $("res-host").innerHTML = h;
    $("count").textContent = rows.length === D.models.length ? t(shown.length < rows.length ? "showingFirst" : "showing", { s: shown.length, n: rows.length }) : t("matching", { n: rows.length }) + (rows.length > shown.length ? " " + t("shownOf", { s: shown.length }) : "");
    var host = $("res-host");
    host.querySelectorAll("[data-sort]").forEach(function (b) { b.addEventListener("click", function () { var k = b.dataset.sort; if (S.sortKey === k) S.sortDir = S.sortDir === "desc" ? "asc" : "desc"; else { S.sortKey = k; S.sortDir = k === "name" ? "asc" : "desc"; } render(); var a = host.querySelector('[data-sort="' + k + '"]'); if (a) a.focus(); }); });
    host.querySelectorAll("[data-pick]").forEach(function (cb) { cb.addEventListener("change", function () { pick(cb.dataset.pick, cb.checked); }); });
    var mb = $("more"); if (mb) mb.addEventListener("click", function () { S.limit += 25; render(); var nb = $("more"); (nb || $("tscroll")).focus(); });
    var ec = $("empty-clear"); if (ec) ec.addEventListener("click", clearFilters);
    edge();
  }
  function edge() {
    var s = $("tscroll"), w = $("scroll-wrap"); if (!s || !w) return;
    var upd = function () { w.classList.toggle("has-more", s.scrollLeft + s.clientWidth < s.scrollWidth - 4); w.classList.toggle("has-less", s.scrollLeft > 4); };
    s.addEventListener("scroll", upd, { passive: true }); upd();
  }
  /* the model in focus (or the first one ticked) follows the reader to Compare and Explore */
  function carry() { var s = S.sel[0] || FOCUS; if (window.coleCarry && s) window.coleCarry(s); }
  function pick(slug, on) {
    if (on && S.sel.length < 6 && S.sel.indexOf(slug) === -1) S.sel.push(slug);
    if (!on) S.sel = S.sel.filter(function (s) { return s !== slug; });
    C.writeHash({ m: S.sel }); render(); selbar(); carry();
  }
  function selbar() {
    var bar = $("selbar"), n = S.sel.length;
    bar.hidden = n === 0; document.body.classList.toggle("has-selbar", n > 0);
    if (!n) return;
    $("sel-count").textContent = t("sel", { n: n });
    $("sel-chips").innerHTML = S.sel.map(function (s, i) { var m = D.bySlug[s]; return '<li class="chip">' + C.esc(ml(m)) + '<button type="button" class="chip-x" data-rm="' + C.esc(s) + '" aria-label="' + C.esc(t("remove", { m: ml(m) })) + '">×</button></li>'; }).join("");
    $("sel-chips").querySelectorAll("[data-rm]").forEach(function (b) { b.addEventListener("click", function () { pick(b.dataset.rm, false); }); });
    var go = $("sel-go");
    if (n >= 2) { go.removeAttribute("aria-disabled"); go.href = "choose-a-model.html" + C.hashFor({ m: S.sel }); go.textContent = t("compare", { n: n }); $("sel-need").textContent = ""; }
    else { go.setAttribute("aria-disabled", "true"); go.removeAttribute("href"); go.textContent = t("compare", { n: n }); $("sel-need").textContent = t("selNeed"); }
  }
  function clearFilters() { S.q = ""; S.fam = ""; S.type = ""; S.size = ""; S.limit = 25; filters(); render(); }
  function render() {
    if (!D) return;
    var rows = filtered();
    if (FOCUS && !S.focused) { var i = rows.findIndex(function (m) { return m.name === FOCUS; }); if (i >= S.limit) S.limit = Math.ceil((i + 1) / 25) * 25; S.focused = true; S.scrollTo = i !== -1; }
    table(rows);
    var tg = $("toggle-tasks"), open = D.cats.some(function (c) { return S.open[c.key]; }); tg.textContent = t(open ? "toggleOff" : "toggleOn"); tg.setAttribute("aria-expanded", String(open)); $("unit-note").textContent = t("unit");
    if (S.scrollTo) { S.scrollTo = false; var r = $("row-focus"), sc = $("tscroll"); if (r && sc) sc.scrollTop = 0; }
  }

  /* downloads: aggregates only, as displayed (filtered, sorted, current columns) */
  function download(kind) {
    var rows = filtered(), cols = columns(), d = 2;
    var head = ["rank", "model", "model_id", "family", "type", "size_billion_parameters", "protocol", "snapshot"].concat(cols.map(function (c) { return c.kind === "overall" ? "overall_percent" : c.kind === "cat" ? "skill_" + c.key + "_percent" : "task_" + c.task + "_percent"; }));
    var rec = rows.map(function (m) {
      var o = [m.rank, ml(m), m.id, famLabel(m), typeOf(m), m.size_b == null ? "" : m.size_b, m.protocol, m.snapshot];
      cols.forEach(function (c) { var v = val(m, c); o.push(v == null ? "" : +(v * 100).toFixed(d)); });
      return o;
    });
    var blob, name;
    if (kind === "csv") {
      var q = function (x) { x = String(x); return /[",\n]/.test(x) ? '"' + x.replace(/"/g, '""') + '"' : x; };
      blob = new Blob(["﻿" + [head].concat(rec).map(function (r) { return r.map(q).join(","); }).join("\n") + "\n"], { type: "text/csv;charset=utf-8" }); name = "cole-results-" + D.snapshot + ".csv";
    } else {
      blob = new Blob([JSON.stringify({ protocol: D.protocol, snapshot: D.snapshot, source: "COLE, graalul/COLE", unit: "percent", missing: "empty value means no result, never zero", rows: rec.map(function (r) { var o = {}; head.forEach(function (h, i) { o[h] = r[i] === "" ? null : r[i]; }); return o; }) }, null, 1)], { type: "application/json" }); name = "cole-results-" + D.snapshot + ".json";
    }
    var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 500);
    $("dl-note").textContent = t("downloaded", { f: name });
  }

  function load() {
    showState("loading");
    C.load().then(function (d) {
      D = d; S.sel = C.readHash().m.filter(function (s) { return D.bySlug[s]; }).slice(0, 6);
      filters(); render(); selbar(); carry();
    }).catch(function () { showState("error"); });
  }
  $("q").addEventListener("input", function (e) { S.q = e.target.value; S.limit = 25; render(); });
  [["f-fam", "fam"], ["f-type", "type"], ["f-size", "size"]].forEach(function (p) { $(p[0]).addEventListener("change", function (e) { S[p[1]] = e.target.value; S.limit = 25; render(); }); });
  $("dec").addEventListener("change", function (e) { S.dec = e.target.checked ? 2 : 1; render(); });
  $("toggle-tasks").addEventListener("click", function () { var on = !Object.keys(S.open).some(function (k) { return S.open[k]; }); D.cats.forEach(function (c) { S.open[c.key] = on; }); render(); $("toggle-tasks").focus(); });
  $("clear").addEventListener("click", clearFilters);
  $("sel-clear").addEventListener("click", function () { S.sel = []; C.writeHash({}); render(); selbar(); });
  $("dl-csv").addEventListener("click", function () { download("csv"); });
  $("dl-json").addEventListener("click", function () { download("json"); });
  document.addEventListener("langchange", function () { if (D) { filters(); render(); selbar(); carry(); } else if (C.forced === "error") showState("error"); else showState("loading"); });
  if (C.forced === "empty") S.q = "zzzz";
  load();
})();
