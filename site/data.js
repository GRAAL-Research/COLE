/* COLE mockups: shared helpers for the data pages (formatting, data loading, series styles, selection hash). */
window.COLE = (function () {
  "use strict";
  var root = document.documentElement;
  var STY = [
    { color: "var(--s1)", dash: "", shape: "circle", word: { en: "solid line, circle", fr: "trait plein, cercle" } },
    { color: "var(--s2)", dash: "10 6", shape: "square", word: { en: "dashed line, square", fr: "tirets, carré" } },
    { color: "var(--s3)", dash: "2 6", shape: "triangle", word: { en: "dotted line, triangle", fr: "pointillés, triangle" } },
    { color: "var(--s4)", dash: "14 5 2 5", shape: "diamond", word: { en: "dash-dot line, diamond", fr: "tiret-point, losange" } },
    { color: "var(--s5)", dash: "5 4", shape: "cross", word: { en: "short dashes, cross", fr: "tirets courts, croix" } },
    { color: "var(--s6)", dash: "1 4", shape: "ring", word: { en: "fine dots, ring", fr: "points fins, anneau" } }
  ];
  function lang() { return root.getAttribute("lang") === "fr" ? "fr" : "en"; }
  function loc() { return lang() === "fr" ? "fr-CA" : "en-CA"; }
  function fmt(v, d) { d = d == null ? 1 : d; return v.toLocaleString(loc(), { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function pct(v, d) { return fmt(v * 100, d); }
  function pts(v, d) { var x = v * 100; return (x >= 0 ? "+" : "−") + fmt(Math.abs(x), d); }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function norm(t) { return String(t).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
  function nbsp(s) { return String(s).replace(/ ([?!:;»])/g, "\u00a0$1").replace(/« /g, "«\u00a0"); }
  function loc2(s) { return lang() === "fr" ? nbsp(s) : s; }
  function makeT(STR) {
    return function (key, vars) {
      var s = (STR[lang()] && STR[lang()][key]) || (STR.en && STR.en[key]) || key;
      if (vars) Object.keys(vars).forEach(function (k) { s = s.split("{" + k + "}").join(vars[k]); });
      return lang() === "fr" ? nbsp(s) : s;
    };
  }
  var cache = {};
  function json(url) { return cache[url] || (cache[url] = fetch(url).then(function (r) { if (!r.ok) throw new Error(url + " " + r.status); return r.json(); })); }
  var forced = new URLSearchParams(location.search).get("state");
  var D = null;
  function load() {
    if (forced === "error") return Promise.reject(new Error("forced"));
    if (forced === "loading") return new Promise(function () {});
    return Promise.all([json("data/models.json"), json("data/categories.json")]).then(function (r) {
      D = { models: r[0].models, snapshot: r[0].snapshot, protocol: r[0].protocol, cats: r[1].categories, taskNames: r[1].task_names, byId: {}, bySlug: {} };
      D.cats.forEach(function (c) { ["label", "short", "plain"].forEach(function (k) { if (c[k] && c[k].fr) c[k].fr = nbsp(c[k].fr); }); });
      D.models.forEach(function (m) {
        D.byId[m.id] = m; D.bySlug[m.name] = m;
        m.partial = D.cats.some(function (c) { return m.categories[c.key].n < m.categories[c.key].of; });
      });
      return D;
    });
  }
  function mlabel(m) { return m.id === "RandomBaselineModel" ? (lang() === "fr" ? "Tirage au hasard" : "Random guessing") : m.label; }
  function short(m) {
    if (m.id === "RandomBaselineModel") return lang() === "fr" ? "Hasard" : "Random";
    return m.label.replace(/^Meta /, "").replace(/ Instruct( v[\d.]+)?$/, " Inst.").replace(/ latest$/, "");
  }
  function mtype(m) {
    if (m.id === "RandomBaselineModel") return lang() === "fr" ? "référence, répond au hasard" : "reference, picks at random";
    if (m.kind === "api") return lang() === "fr" ? "utilisé par API" : "served through an API";
    var q = m.quantized_4bit ? (lang() === "fr" ? ", 4 bits" : ", 4-bit") : "";
    return (lang() === "fr" ? "poids ouverts" : "open weights") + q;
  }
  function msize(m) {
    if (m.size_b == null) return lang() === "fr" ? "taille n.d." : "size n/a";
    return lang() === "fr" ? fmt(m.size_b, 2) + " milliards de paramètres" : fmt(m.size_b, 2) + " billion parameters";
  }
  function bucket(m) {
    if (m.size_b == null) return "unknown";
    if (m.size_b < 3) return "lt3"; if (m.size_b < 10) return "3to10"; if (m.size_b < 35) return "10to35"; return "gt35";
  }
  /* one set of marks: equal visual area (circle 1.13 x, triangle 1.3 x), same stroke width in the key and on the chart */
  function shape(sh, x, y, r, style, extra) {
    var s = style || "", e = extra || "";
    if (sh === "circle") return '<circle cx="' + x + '" cy="' + y + '" r="' + (r * 1.13).toFixed(2) + '" style="' + s + '" ' + e + "/>";
    if (sh === "ring") return '<circle cx="' + x + '" cy="' + y + '" r="' + (r * 1.13 - 1).toFixed(2) + '" style="' + s + ';fill:var(--deep);stroke-width:2.5" ' + e + "/>";
    if (sh === "square") return '<rect x="' + (x - r) + '" y="' + (y - r) + '" width="' + 2 * r + '" height="' + 2 * r + '" style="' + s + '" ' + e + "/>";
    if (sh === "triangle") { var q = r * 1.3; return '<polygon points="' + x + "," + (y - q - 1) + " " + (x + q + 1) + "," + (y + q) + " " + (x - q - 1) + "," + (y + q) + '" style="' + s + '" ' + e + "/>"; }
    if (sh === "diamond") return '<polygon points="' + x + "," + (y - r - 2) + " " + (x + r + 2) + "," + y + " " + x + "," + (y + r + 2) + " " + (x - r - 2) + "," + y + '" style="' + s + '" ' + e + "/>";
    return '<path d="M' + (x - r) + "," + y + "H" + (x + r) + "M" + x + "," + (y - r) + "V" + (y + r) + '" style="' + s + ';fill:none;stroke-width:3" ' + e + "/>";
  }
  /* legend key: same 44x16 box for every series, line in two segments around the marker so a dash never touches it */
  function swatch(i) {
    var st = STY[i % 6], c = "fill:" + st.color + ";stroke:" + st.color + ";stroke-width:3", ln = "stroke:" + st.color + ";stroke-width:3;fill:none" + (st.dash ? ";stroke-dasharray:" + st.dash : "");
    return '<svg class="sw" width="44" height="16" viewBox="0 0 44 16" aria-hidden="true"><line x1="0" y1="8" x2="13" y2="8" style="' + ln + '"/><line x1="31" y1="8" x2="44" y2="8" style="' + ln + '"/>' + shape(st.shape, 22, 8, 4.5, st.shape === "cross" ? "stroke:" + st.color : c, "") + "</svg>";
  }
  /* shareable selection: #m=a,b,c&v=cats&r=a,b,c */
  function readHash() {
    var o = { m: [], v: "", r: [], c: "" }, h = location.hash.replace(/^#/, "");
    h.split("&").forEach(function (p) {
      var kv = p.split("="), k = kv[0], v = decodeURIComponent(kv[1] || "");
      if (k === "m" || k === "r") o[k] = v ? v.split(",").filter(Boolean) : []; else if (k === "v") o.v = v; else if (k === "c") o.c = v;
    });
    return o;
  }
  function hashFor(o) {
    var p = [];
    if (o.m && o.m.length) p.push("m=" + o.m.map(encodeURIComponent).join(","));
    if (o.v) p.push("v=" + o.v);
    if (o.c) p.push("c=" + o.c);
    if (o.r && o.r.length) p.push("r=" + o.r.map(encodeURIComponent).join(","));
    return p.length ? "#" + p.join("&") : "";
  }
  function writeHash(o) { history.replaceState(null, "", location.pathname + location.search + hashFor(o)); }
  function setBusy(host, on) { host.setAttribute("aria-busy", String(on)); }
  return { nbsp: nbsp, loc2: loc2, STY: STY, lang: lang, loc: loc, fmt: fmt, pct: pct, pts: pts, esc: esc, norm: norm, makeT: makeT, json: json, load: load, get D() { return D; }, forced: forced,
    mlabel: mlabel, short: short, mtype: mtype, msize: msize, bucket: bucket, shape: shape, swatch: swatch, readHash: readHash, hashFor: hashFor, writeHash: writeHash, setBusy: setBusy };
})();
