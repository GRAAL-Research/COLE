/* Choose a model: compare 2 to 6 models. Views: radar (max 3 series), by skill (small multiples), table. */
(function () {
  "use strict";
  var C = window.COLE, $ = function (id) { return document.getElementById(id); };
  var STR = {
    en: {
      loading: "Loading the model results…", errorTitle: "We could not load the results.", errorBody: "The data file did not answer. Check your connection and try again.", retry: "Try again",
      noMatch: "No model matches “{q}”.", clear: "Clear search", suggested: "Suggested",
      same: "", add: "Add model", full: "6 models is the maximum. Remove one to add another.", minNote: "Keep at least 2 models.", remove: "Remove {m}",
      reset: "Reset to the default pair", quick: "Quick add", added: "Added {m}. {n} of 6 models.", removed: "Removed {m}. {n} of 6 models.", addLabel: "Add a model", addPh: "Choose a model", emptyTitle: "No model to compare yet.", emptyBody: "Add 2 models with the list on the left, then the chart appears here.", suggested: "Suggested", allModels: "All models", pickFirst: "Choose a model in the list first.", help: "How to read this chart",
      views: "View", vRadar: "Radar", vCats: "By skill", vTable: "Table",
      radarNote: "Check up to 3 models", replaced: "{a} replaced by {b}",
      moreCats: "See more skills", fewerCats: "Show fewer skills", overall: "Overall", skill: "Skill", tests: "{n} tests", testsOne: "{n} test", partial: "{n} of {m} tests",
      caption: "Score by skill", best: "strongest", bestNote: "* strongest in the row",
      showTasks: "Show the {n} tasks", hideTasks: "Hide the tasks", task: "Task", na: "n/a", naList: "n/a: {list}",
      rank: "Rank", model: "Model", more: "Show all {n} models", less: "Show the top 10 only",
      lbCaption: "Overall score and score by skill, in percent. Blue rows are your selected models.", partialNote: "Fewer tests than the other models.",
      plateTitle: "Radar plate comparing models on seven skills", scale: "Scores in %. Hollow marks mean fewer tests than expected.",
      ahead: "{L} is stronger on {k} of {n} skills.", close: "{L} is stronger on {k} of {n} skills.",
      leads: " {O} is stronger on: {list}.", leadsNone: " {L} is ahead on every skill.", sameModel: "",
      gLead: "{L} is stronger on {k} of {n} skills.", gOther: " {O} leads on {list}.", gAll: "", gGap: "",
      models: "Models (2 to 6)", rowLabel: "{m}: {v}"
    },
    fr: {
      loading: "Chargement des résultats des modèles…", errorTitle: "Nous n’avons pas pu charger les résultats.", errorBody: "Le fichier de données n’a pas répondu. Vérifiez votre connexion et réessayez.", retry: "Réessayer",
      noMatch: "Aucun modèle ne correspond à « {q} ».", clear: "Effacer la recherche", suggested: "Suggestions",
      add: "Ajouter le modèle", full: "6 modèles au maximum. Retirez-en un pour en ajouter.", minNote: "Gardez au moins 2 modèles.", remove: "Retirer {m}",
      reset: "Revenir à la paire par défaut", quick: "Ajout rapide", added: "{m} ajouté. {n} modèles sur 6.", removed: "{m} retiré. {n} modèles sur 6.", addLabel: "Ajouter un modèle", addPh: "Choisir un modèle", emptyTitle: "Aucun modèle à comparer pour l’instant.", emptyBody: "Ajoutez 2 modèles avec la liste à gauche ; le graphique apparaîtra ici.", suggested: "Suggestions", allModels: "Tous les modèles", pickFirst: "Choisissez d’abord un modèle dans la liste.", help: "Comment lire ce graphique",
      views: "Vue", vRadar: "Radar", vCats: "Par compétence", vTable: "Tableau",
      radarNote: "Cochez jusqu’à 3 modèles", replaced: "{a} remplacé par {b}",
      moreCats: "Voir plus de compétences", fewerCats: "Voir moins de compétences", overall: "Général", skill: "Compétence", tests: "{n} tests", testsOne: "{n} test", partial: "{n} tests sur {m}",
      caption: "Score par compétence", best: "le plus fort", bestNote: "* le plus fort de la ligne",
      showTasks: "Afficher les {n} tâches", hideTasks: "Masquer les tâches", task: "Tâche", na: "n.d.", naList: "n.d. : {list}",
      rank: "Rang", model: "Modèle", more: "Afficher les {n} modèles", less: "Afficher seulement les 10 premiers",
      lbCaption: "Score général et score par compétence, en pourcentage. Les lignes en bleu sont vos modèles choisis.", partialNote: "Moins de tests que les autres modèles.",
      plateTitle: "Radar comparant des modèles sur sept compétences", scale: "Scores en %. Une marque creuse signifie moins de tests que prévu.",
      ahead: "{L} est plus fort sur {k} compétences sur {n}.", close: "{L} est plus fort sur {k} compétences sur {n}.",
      leads: " {O} est plus fort sur : {list}.", leadsNone: " {L} est en avance sur toutes les compétences.",
      gLead: "{L} est plus fort sur {k} compétences sur {n}.", gOther: " {O} est en tête sur : {list}.", gAll: "", gGap: "",
      models: "Modèles (2 à 6)", rowLabel: "{m} : {v}"
    }
  };
  var t = C.makeT(STR);
  var DEFAULT_PAIR = ["claude-opus-4", "Qwen3-14B"];
  var QUICK = ["claude-opus-4", "gpt-4o", "Qwen3-14B", "Meta-Llama-3.1-8B-Instruct", "Llama-3.2-1B-Instruct", "RandomBaselineModel"];
  var BASIC = ["quebec", "grammar", "meaning", "reasoning"];
  var S = { moreCats: false, sel: [], view: "radar", viewChosen: false, rpick: [], showAll: false, sortKey: "overall", sortDir: "desc", tasksOpen: false };
  var D;
  var forced = C.forced;

  function ml(m) { return C.mlabel(m); }
  function M(slug) { return D.bySlug[slug]; }
  function cats() { return S.moreCats || S.view === "radar" ? D.cats : D.cats.filter(function (c) { return BASIC.indexOf(c.key) !== -1; }); }
  function selModels() { return S.sel.map(M); }
  function clabel(c) { return c.short[C.lang()]; }
  function say(msg, quiet) { $(quiet ? "live-note" : "add-note").textContent = msg; if (!quiet) $("live-note").textContent = ""; }
  function setBusy(b) {
    ["s-add", "btn-add", "btn-reset", "more-cats"].forEach(function (id) { var e = $(id); if (e) e.disabled = b; });
    document.querySelectorAll("[data-busy-target]").forEach(function (e) { C.setBusy(e, b); });
    document.querySelectorAll(".plate-legend, .plate-scale, .seg").forEach(function (e) { e.hidden = b; });
  }
  function showLoading() {
    setBusy(true);
    var st = $("plate-state"); st.hidden = false; st.className = "skel";
    st.innerHTML = '<div><div class="skel-ring" aria-hidden="true"></div><p class="small" role="status" style="margin-top:1rem">' + C.esc(t("loading")) + "</p></div>";
    $("plate-svg-host").hidden = true;
        $("compare-host").innerHTML = '<div class="skel-rows" aria-hidden="true"><span></span><span></span><span></span></div>';
  }
  function showError() {
    setBusy(true);
    var st = $("plate-state"); st.hidden = false; st.className = "state";
    st.innerHTML = '<h3 class="lead strong">' + C.esc(t("errorTitle")) + "</h3><p>" + C.esc(t("errorBody")) + '</p><button class="btn" type="button" id="retry">' + C.esc(t("retry")) + "</button>";
    $("plate-svg-host").hidden = true;
    document.querySelectorAll("#seg button, #more-cats").forEach(function (e) { e.disabled = true; });
    $("compare-host").innerHTML = "";
    $("retry").addEventListener("click", load); $("retry").focus();
  }

  /* ---- selection ---- */
  function sanitize() {
    S.sel = S.sel.filter(function (s, i) { return D.bySlug[s] && S.sel.indexOf(s) === i; }).slice(0, 6);
    if (S.sel.length < 2) S.sel = DEFAULT_PAIR.slice();
    S.rpick = S.rpick.filter(function (s) { return S.sel.indexOf(s) !== -1; }).slice(0, 3);
    if (S.rpick.length === 0) S.rpick = S.sel.slice(0, 3);
  }
  function persist() {
    C.writeHash({ c: S.moreCats ? "all" : "", m: S.sel, v: S.view === "radar" && !S.viewChosen ? "" : S.view, r: S.sel.length > 3 ? S.rpick : [] });
    if (window.coleCarry && S.sel[0]) window.coleCarry(S.sel[0]);
  }
  function addModel(slug) {
    if (S.sel.length >= 6) { say(t("full")); return; }
    if (S.sel.indexOf(slug) !== -1) return;
    S.sel.push(slug);
    if (S.sel.length > 3 && S.view === "radar" && !S.viewChosen) S.view = "cats";
    if (S.rpick.length < 3) S.rpick.push(slug);
    say("", false); say(t("added", { m: ml(M(slug)), n: S.sel.length }), true);
    renderAll(true);
  }
  function removeModel(slug) {
    if (S.sel.length <= 2) { say(t("minNote")); return; }
    S.sel = S.sel.filter(function (s) { return s !== slug; });
    S.rpick = S.rpick.filter(function (s) { return s !== slug; });
    sanitize();
    say("", false); say(t("removed", { m: ml(M(slug)), n: S.sel.length }), true);
    renderAll(true);
    var first = document.querySelector(".chip-x"); if (first) first.focus();
  }

  function renderChips() {
    var n = S.sel.length;
    $("chips").innerHTML = S.sel.map(function (s, i) {
      var m = M(s), dis = n <= 2;
      return '<li class="chip">' + C.swatch(i) + '<span class="chip-name">' + C.esc(ml(m)) + '</span><button type="button" class="chip-x" data-rm="' + C.esc(s) + '" aria-label="' + C.esc(t("remove", { m: ml(m) })) + '"' + (dis ? ' aria-disabled="true" title="' + C.esc(t("minNote")) + '"' : "") + ">×</button></li>";
    }).join("");
    $("chips").querySelectorAll("[data-rm]").forEach(function (b) { b.addEventListener("click", function () { removeModel(b.dataset.rm); }); });
    $("suggest").innerHTML = QUICK.filter(function (s) { return S.sel.indexOf(s) === -1 && D.bySlug[s]; }).slice(0, 3).map(function (s) {
      return '<li><button type="button" class="chip-add" data-add="' + C.esc(s) + '"' + (n >= 6 ? ' aria-disabled="true" title="' + C.esc(t("full")) + '"' : "") + ">+ " + C.esc(ml(M(s))) + "</button></li>";
    }).join("");
    $("suggest").querySelectorAll("[data-add]").forEach(function (b) { b.addEventListener("click", function () { addModel(b.dataset.add); }); });
    $("btn-add").setAttribute("aria-disabled", String(n >= 6));
    $("btn-add").title = n >= 6 ? t("full") : "";
  }
  function renderList() {
    var sel = $("s-add"), rest = D.models.filter(function (m) { return S.sel.indexOf(m.name) === -1; });
    var first = QUICK.map(M).filter(function (m) { return m && S.sel.indexOf(m.name) === -1; });
    var opt = function (m) { return '<option value="' + C.esc(m.name) + '">' + C.esc(ml(m)) + "</option>"; };
    sel.innerHTML = '<option value="">' + C.esc(t("addPh")) + "</option>" + (first.length ? '<optgroup label="' + C.esc(t("suggested")) + '">' + first.map(opt).join("") + "</optgroup>" : "") + '<optgroup label="' + C.esc(t("allModels")) + '">' + rest.filter(function (m) { return first.indexOf(m) === -1; }).map(opt).join("") + "</optgroup>";
  }
  function addFromInput() {
    var sel = $("s-add"); if (!sel.value) { say(t("pickFirst"), false); return; }
    var slug = sel.value; sel.value = ""; addModel(slug);
  }

  /* ---- helpers on scores ---- */
  function cscore(m, key) { return key === "overall" ? m.overall : m.categories[key].score; }
  function leaderOf(models, key) {
    var best = null, tie = false;
    models.forEach(function (m) { var v = cscore(m, key); if (v == null) return; if (!best || v > best.v) { best = { m: m, v: v }; tie = false; } else if (v === best.v) tie = true; });
    return tie ? null : best;
  }
  function spreadOf(models, key) {
    var vs = models.map(function (m) { return cscore(m, key); }).filter(function (v) { return v != null; });
    return vs.length < 2 ? 0 : Math.max.apply(null, vs) - Math.min.apply(null, vs);
  }

  /* ---- sentences ---- */
  function skillLeads(models) {
    var lead = leaderOf(models, "overall"); if (!lead) lead = { m: models[0] };
    var mine = [], others = {}, order = [], all = cats();
    all.forEach(function (c) {
      var l = leaderOf(models, c.key);
      if (!l) return;
      if (l.m === lead.m) mine.push(c); else { if (!others[l.m.id]) { others[l.m.id] = { m: l.m, list: [] }; order.push(l.m.id); } others[l.m.id].list.push(clabel(c)); }
    });
    return { lead: lead.m, k: mine.length, n: all.length, others: order.map(function (id) { return others[id]; }) };
  }
  function summary(models) {
    var r = skillLeads(models), out = t(models.length === 2 ? "ahead" : "gLead", { L: ml(r.lead), k: r.k, n: r.n });
    if (!r.others.length) return out;
    r.others.forEach(function (o) { out += t("leads", { O: ml(o.m), list: o.list.join(", ") }); });
    return out;
  }

  /* ---- radar ---- */
  var NS = "http://www.w3.org/2000/svg";
  function drawRadar(animate) {
    var host = $("plate-svg-host"), W = Math.max(280, host.clientWidth || 320), narrow = W < 560;
    var padX = narrow ? 82 : 118, padY = 34, R = Math.min(W / 2 - padX, 235), cx = W / 2, cy = R + padY + 6, H = cy + R + padY + 14, n = cats().length;
    var ang = function (i) { return -Math.PI / 2 + (i * 2 * Math.PI) / n; };
    var pt = function (i, r) { return [cx + r * Math.cos(ang(i)), cy + r * Math.sin(ang(i))]; };
    var picks = S.sel.length > 3 ? S.rpick : S.sel;
    var svg = '<svg viewBox="0 0 ' + W + " " + H + '" width="' + W + '" height="' + H + '" role="img" aria-labelledby="plate-title plate-desc"><title id="plate-title">' + C.esc(t("plateTitle")) + '</title><desc id="plate-desc">' + C.esc(picks.map(function (s) { return ml(M(s)); }).join(", ") + ". " + t("caption")) + "</desc>";
    [25, 50, 75, 100].forEach(function (p) {
      svg += '<polygon class="ring" points="' + cats().map(function (c, i) { return pt(i, (R * p) / 100).map(function (v) { return v.toFixed(1); }).join(","); }).join(" ") + '"/>';
    });
    cats().forEach(function (c, i) { var p = pt(i, R); svg += '<line class="spoke" x1="' + cx + '" y1="' + cy + '" x2="' + p[0].toFixed(1) + '" y2="' + p[1].toFixed(1) + '"/>'; });
    [50, 100].forEach(function (p) { var q = pt(0, 0), a = ang(0) + Math.PI / n, x = cx + (R * p / 100) * Math.cos(a), y = cy + (R * p / 100) * Math.sin(a); svg += '<text class="ring-label" x="' + (x + 4).toFixed(1) + '" y="' + (y - 4).toFixed(1) + '">' + p + "</text>"; });
    picks.forEach(function (slug, k) {
      var m = M(slug), slot = S.sel.indexOf(slug), st = C.STY[slot], col = "stroke:" + st.color + ";fill:" + st.color;
      var coords = [], dots = "", best = { i: 0, v: -1 };
      cats().forEach(function (c, i) {
        var v = m.categories[c.key].score, p = pt(i, v == null ? 0 : R * v);
        coords.push(p[0].toFixed(1) + "," + p[1].toFixed(1));
        if (v != null && v > best.v) best = { i: i, v: v };
        var partial = m.categories[c.key].n < m.categories[c.key].of;
        var tip = ml(m) + ", " + clabel(c) + ": " + (v == null ? t("na") : C.pct(v) + " %");
        dots += C.shape(st.shape, +p[0].toFixed(1), +p[1].toFixed(1), 5, col, "") .replace("/>", "><title>" + C.esc(tip) + "</title></" + (st.shape === "square" ? "rect" : st.shape === "triangle" || st.shape === "diamond" ? "polygon" : st.shape === "cross" ? "path" : "circle") + ">");
      });
      svg += '<g class="series' + (animate ? " enter" : "") + '"><polygon points="' + coords.join(" ") + '" style="fill:' + st.color + ";fill-opacity:0.1;stroke:" + st.color + ";stroke-width:3;stroke-linejoin:round" + (st.dash ? ";stroke-dasharray:" + st.dash : "") + '"/>' + dots + "</g>";
    });
    cats().forEach(function (c, i) {
      var p = pt(i, R + 16), dx = Math.cos(ang(i)), anchor = dx > 0.2 ? "start" : dx < -0.2 ? "end" : "middle", dy = Math.sin(ang(i)) > 0.5 ? 14 : (Math.sin(ang(i)) < -0.5 ? -4 : 5);
      svg += '<text class="axis-label" x="' + p[0].toFixed(1) + '" y="' + (p[1] + dy).toFixed(1) + '" text-anchor="' + anchor + '">' + C.esc(clabel(c, true)) + "</text>";
    });
    host.innerHTML = svg + "</svg>";
  }
  function radarPicker() {
    var box = $("radar-pick");
    if (S.view !== "radar" || S.sel.length <= 3) { box.hidden = true; box.innerHTML = ""; return; }
    box.hidden = false;
    box.innerHTML = '<fieldset><legend class="small strong">' + C.esc(t("radarNote")) + ' <span class="counter">' + S.rpick.length + " / 3</span></legend>" + S.sel.map(function (s, i) {
      var on = S.rpick.indexOf(s) !== -1;
      return '<label class="check"><input type="checkbox" value="' + C.esc(s) + '"' + (on ? " checked" : "") + ">" + C.swatch(i) + "<span>" + C.esc(ml(M(s))) + "</span></label>";
    }).join("") + '</fieldset><p class="small" id="radar-msg" role="status" aria-live="polite"></p>';
    box.querySelectorAll("input").forEach(function (cb) {
      cb.addEventListener("change", function () {
        var msg = "";
        if (cb.checked) {
          if (S.rpick.length >= 3) { var old = S.rpick.shift(); msg = t("replaced", { a: ml(M(old)), b: ml(M(cb.value)) }); }
          S.rpick.push(cb.value);
        } else {
          S.rpick = S.rpick.filter(function (s) { return s !== cb.value; });
          if (S.rpick.length === 0) { S.rpick = [cb.value]; }
        }
        persist(); radarPicker(); drawRadar(false);
        $("radar-msg").textContent = msg;
        var again = box.querySelector('input[value="' + cb.value + '"]'); if (again) again.focus();
      });
    });
  }

  /* ---- by skill: small multiples ---- */
  function catsView() {
    var host = $("plate-svg-host"), models = selModels();
    var keys = ["overall"].concat(cats().map(function (c) { return c.key; })).sort(function (a, b) {
      if (a === "overall") return -1; if (b === "overall") return 1; return spreadOf(models, b) - spreadOf(models, a);
    });
    var h = '<div class="cat-list">';
    keys.forEach(function (key) {
      var c = key === "overall" ? null : cats().filter(function (x) { return x.key === key; })[0];
      var label = c ? clabel(c) : t("overall");
      var na = models.filter(function (m) { return cscore(m, key) == null; });
      h += '<div class="cat-row" data-key="' + key + '"><div class="cat-head"><h3 class="strong">' + C.esc(label) + "</h3>" + (na.length ? '<p class="small">' + C.esc(t("naList", { list: na.map(ml).join(", ") })) + "</p>" : "") + '</div><div class="cat-plot"></div></div>';
    });
    host.innerHTML = h + "</div>";
    host.querySelectorAll(".cat-row").forEach(function (row) { drawCatRow(row, models, row.dataset.key); });
  }
  /* one row: an axis, one marker per model, its value printed under it on a thin leader line (the marker shape is not repeated in the label) */
  function drawCatRow(row, models, key) {
    var plot = row.querySelector(".cat-plot"), W = Math.max(240, plot.clientWidth || 300), pad = 18, x = function (v) { return pad + v * (W - 2 * pad); };
    var items = models.map(function (m) { return { m: m, slot: S.sel.indexOf(m.name), v: cscore(m, key) }; }).filter(function (o) { return o.v != null; }).sort(function (a, b) { return a.v - b.v; });
    var lanes = [], base = 26;
    items.forEach(function (o) {
      var txt = C.pct(o.v), w = txt.length * 9 + 8, cxl = Math.min(Math.max(x(o.v), pad + w / 2 - 6), W - pad - w / 2 + 6), l = cxl - w / 2, ln = 0;
      while (lanes[ln] != null && lanes[ln] > l - 4) ln++;
      lanes[ln] = l + w; o.txt = txt; o.lane = ln; o.cx = cxl;
    });
    var H = base + 12 + Math.max(1, lanes.length) * 22 + 4;
    var svg = '<svg viewBox="0 0 ' + W + " " + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + C.esc(row.querySelector("h3").textContent + ": " + items.map(function (o) { return ml(o.m) + " " + C.pct(o.v); }).join(", ")) + '">';
    svg += '<line class="track" x1="' + pad + '" y1="' + base + '" x2="' + (W - pad) + '" y2="' + base + '"/>';
    [[0, "start"], [0.5, "middle"], [1, "end"]].forEach(function (a) { var lab = C.fmt(a[0] * 100, 0); svg += '<line class="tick" x1="' + x(a[0]) + '" y1="' + (base - 6) + '" x2="' + x(a[0]) + '" y2="' + (base + 6) + '"/><text class="axis-num" x="' + (a[1] === "start" ? pad - 4 : a[1] === "end" ? W - pad + 4 : x(a[0])) + '" y="' + (base - 11) + '" text-anchor="' + (a[1] === "start" ? "start" : a[1] === "end" ? "end" : "middle") + '">' + lab + "</text>"; });
    items.forEach(function (o) {
      var st = C.STY[o.slot], col = "stroke:" + st.color + ";fill:" + st.color, xv = x(o.v), ly = base + 12 + o.lane * 22 + 14;
      if (o.lane > 0 || Math.abs(o.cx - xv) > 1) svg += '<line class="leader" x1="' + xv.toFixed(1) + '" y1="' + base + '" x2="' + xv.toFixed(1) + '" y2="' + (ly - 14) + '" style="stroke:' + st.color + '"/>';
      svg += C.shape(st.shape, +xv.toFixed(1), base, 6, col, "");
      svg += '<text class="end-label" x="' + o.cx.toFixed(1) + '" y="' + ly + '" text-anchor="middle" style="fill:' + st.color + '">' + C.esc(o.txt) + "</text>";
    });
    plot.innerHTML = svg + "</svg>";
  }

  /* ---- table ---- */
  function bestIdx(vals) { var b = -1, bv = -1; vals.forEach(function (v, i) { if (v != null && v > bv) { bv = v; b = i; } }); return b; }
  function tableHtml(withTasks, id) {
    var models = selModels(), d = 1;
    var h = '<div class="table-scroll" tabindex="0" role="region" aria-label="' + C.esc(t("caption")) + '"><table class="data cmp"><caption>' + C.esc(t("caption")) + "</caption><thead><tr><th scope=\"col\" class=\"l\">" + C.esc(t("skill")) + "</th>";
    models.forEach(function (m, i) { h += '<th scope="col">' + C.esc(ml(m)) + "</th>"; });
    h += "</tr></thead><tbody>";
    var cell = function (vals) {
      var b = bestIdx(vals);
      return vals.map(function (v, i) { return "<td>" + (v == null ? C.esc(t("na")) : (i === b ? '<b class="best">' + C.pct(v, d) + '</b><span aria-hidden="true">*</span><span class="vh"> (' + C.esc(t("best")) + ")</span>" : C.pct(v, d))) + "</td>"; }).join("");
    };
    h += '<tr class="row-overall"><th scope="row" class="l">' + C.esc(t("overall")) + "</th>" + cell(models.map(function (m) { return m.overall; })) + "</tr>";
    cats().forEach(function (c) {
      h += "<tr><th scope=\"row\" class=\"l\">" + C.esc(clabel(c)) + "</th>" + cell(models.map(function (m) { return m.categories[c.key].score; })) + "</tr>";
      if (withTasks) c.tasks.forEach(function (k) {
        h += '<tr class="row-task" data-task-row hidden><th scope="row" class="l task-name">' + C.esc(D.taskNames[k].name) + '<span class="note-part">' + C.esc(D.taskNames[k].metric) + "</span></th>" + cell(models.map(function (m) { return m.tasks[k] == null ? null : m.tasks[k]; })) + "</tr>";
      });
    });
    h += "</tbody></table></div><p class=\"small\">" + C.esc(t("bestNote")) + "</p>";
    if (withTasks) h += '<p><button class="btn btn-ghost" type="button" data-toggle-tasks aria-expanded="false">' + C.esc(t("showTasks", { n: D.cats.reduce(function (s, c) { return s + c.tasks.length; }, 0) })) + "</button></p>";
    return h;
  }
  function bindTaskToggle(host) {
    var b = host.querySelector("[data-toggle-tasks]"); if (!b) return;
    var apply = function () { host.querySelectorAll("[data-task-row]").forEach(function (r) { r.hidden = !S.tasksOpen; }); b.setAttribute("aria-expanded", String(S.tasksOpen)); b.textContent = S.tasksOpen ? t("hideTasks") : t("showTasks", { n: D.cats.reduce(function (s, c) { return s + c.tasks.length; }, 0) }); };
    b.addEventListener("click", function () { S.tasksOpen = !S.tasksOpen; apply(); }); apply();
  }

  /* ---- chrome ---- */
  function moreBtn() {
    var b = $("more-cats"); if (!b) return;
    b.textContent = S.moreCats ? t("fewerCats") : t("moreCats"); b.setAttribute("aria-expanded", String(S.moreCats));
    if (b.parentNode) b.parentNode.hidden = S.view === "radar";
  }
  var VIEWS = [["radar", "vRadar"], ["cats", "vCats"], ["table", "vTable"]];
  function seg() {
    var wrap = $("seg");
    wrap.innerHTML = VIEWS.map(function (v) { var on = S.view === v[0]; return '<button type="button" role="tab" id="tab-' + v[0] + '" data-view="' + v[0] + '" aria-selected="' + on + '" tabindex="' + (on ? 0 : -1) + '" aria-controls="plate-svg-host">' + C.esc(t(v[1])) + "</button>"; }).join("");
    wrap.querySelectorAll("button").forEach(function (b, i) {
      b.addEventListener("click", function () { S.view = b.dataset.view; S.viewChosen = true; renderAll(false); $("tab-" + S.view).focus(); });
      b.addEventListener("keydown", function (e) {
        var k = e.key, n = VIEWS.length, to = k === "ArrowRight" ? (i + 1) % n : k === "ArrowLeft" ? (i + n - 1) % n : k === "Home" ? 0 : k === "End" ? n - 1 : -1;
        if (to < 0) return; e.preventDefault(); S.view = VIEWS[to][0]; S.viewChosen = true; renderAll(false); $("tab-" + S.view).focus();
      });
    });
    wrap.setAttribute("aria-label", t("views"));
    $("plate-svg-host").setAttribute("aria-labelledby", "tab-" + S.view);
  }
  function figure(animate) {
    var host = $("plate-svg-host");
    host.className = "plate-box view-" + S.view;
    if (S.view === "radar") { drawRadar(animate); }
    else if (S.view === "cats") { catsView(); }
    else { host.innerHTML = tableHtml(false); }
    $("plate-scale").hidden = S.view !== "radar";
  }
  function renderAll(animate) {
    sanitize();
    $("chips").setAttribute("aria-label", t("models")); $("add-label").textContent = t("addLabel");
    renderChips(); renderList(); seg(); moreBtn(); radarPicker(); figure(animate !== false);
    var models = selModels();
    $("verdict").textContent = summary(models);
    $("compare-host").innerHTML = S.view === "table" ? "" : tableHtml(false);
    persist();
  }

  /* ---- wiring ---- */
  $("btn-add").addEventListener("click", addFromInput);
  $("more-cats").addEventListener("click", function () { S.moreCats = !S.moreCats; renderAll(false); $("more-cats").focus(); });
  $("btn-reset").addEventListener("click", function () { S.sel = DEFAULT_PAIR.slice(); S.moreCats = false; S.rpick = []; S.view = "radar"; S.viewChosen = false; say(""); renderAll(true); });
  function load() {
    showLoading();
    C.load().then(function (d) {
      D = d; setBusy(false);
      $("plate-state").hidden = true; $("plate-state").className = ""; $("plate-svg-host").hidden = false;
      var h = C.readHash();
      var mp = new URLSearchParams(location.search).get("model");
      S.sel = h.m.length ? h.m : (mp && D.bySlug[mp] ? [mp].concat(DEFAULT_PAIR.filter(function (x) { return x !== mp; }).slice(0, 1)) : DEFAULT_PAIR.slice());
      S.view = ["radar", "cats", "table"].indexOf(h.v) !== -1 ? h.v : "radar"; S.viewChosen = !!h.v;
      S.rpick = h.r; S.moreCats = h.c === "all";
      sanitize();
      if (!h.v && S.sel.length > 3) S.view = "cats";
      renderAll(true);
      if (forced === "empty") {
        var st = $("plate-state"); st.hidden = false; st.className = "state"; $("plate-svg-host").hidden = true; $("compare-host").innerHTML = ""; $("verdict").textContent = "";
        st.innerHTML = '<h3 class="lead strong">' + C.esc(t("emptyTitle")) + "</h3><p>" + C.esc(t("emptyBody")) + "</p>";
        document.querySelectorAll("#seg button, #more-cats").forEach(function (e) { e.disabled = true; });
      }
    }).catch(function (e) { console.error(e); showError(); });
  }
  document.addEventListener("langchange", function () { if (D) renderAll(false); else if (forced === "error") showError(); else showLoading(); });
  window.addEventListener("hashchange", function () { if (!D) return; var h = C.readHash(); if (h.m.length) { S.sel = h.m; S.rpick = h.r; if (h.v) { S.view = h.v; S.viewChosen = true; } renderAll(false); } });
  var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(function () { if (D && S.view !== "table") figure(false); }, 140); });
  document.querySelectorAll(".js-only").forEach(function (e) { e.hidden = false; });
  document.querySelectorAll(".no-js-only").forEach(function (e) { e.hidden = true; });
  load();
})();
