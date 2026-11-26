/* COLE mockups: language switch, nav, reveals, footer fit, and the "Choose a model" page.
   Vanilla JS, no build step. Text for both languages is in the markup (CSS shows one);
   only strings built at run time live in STR below. */
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- language ---------- */
  var LANG_KEY = "cole-lang";
  function initialLang() {
    var q = new URLSearchParams(location.search).get("lang");
    if (q === "fr" || q === "en") return q;
    try { var s = localStorage.getItem(LANG_KEY); if (s === "fr" || s === "en") return s; } catch (e) { /* private mode */ }
    return "fr";
  }
  var lang = initialLang();
  function applyAttrs() {
    document.querySelectorAll("[data-i18n-attrs]").forEach(function (el) {
      el.getAttribute("data-i18n-attrs").split("|").forEach(function (name) {
        var v = el.getAttribute("data-" + lang + "-" + name);
        if (v != null) el.setAttribute(name, v);
      });
    });
    var t = document.querySelector("title");
    if (t && t.getAttribute("data-" + lang)) document.title = t.getAttribute("data-" + lang);
  }
  function setLang(l, persist) {
    lang = l;
    root.setAttribute("lang", l);
    if (persist) { try { localStorage.setItem(LANG_KEY, l); } catch (e) { /* ignore */ } }
    document.querySelectorAll(".lang button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.lang === l)); });
    applyAttrs();
    fitFooterName();
    document.dispatchEvent(new CustomEvent("langchange", { detail: l }));
  }
  document.querySelectorAll(".lang button").forEach(function (b) {
    b.addEventListener("click", function () { setLang(b.dataset.lang, true); });
  });

  /* ---------- the chosen model follows the reader from step to step (?model=slug) ---------- */
  window.coleCarry = function (slug) {
    document.querySelectorAll("a[data-carry]").forEach(function (a) {
      var u = a.getAttribute("href").split("?")[0].split("#")[0];
      a.setAttribute("href", slug ? u + "?model=" + encodeURIComponent(slug) : u);
    });
  };
  var carried = new URLSearchParams(location.search).get("model");
  if (carried) window.coleCarry(carried);

  /* ---------- "?" help popovers: closed by default, Escape and outside click close ---------- */
  function closeHelp(except) {
    document.querySelectorAll("[data-help]").forEach(function (h) {
      if (h === except) return;
      var b = h.querySelector(".help-btn"), p = h.querySelector(".help-pop");
      b.setAttribute("aria-expanded", "false"); p.hidden = true;
    });
  }
  document.querySelectorAll("[data-help]").forEach(function (h) {
    var b = h.querySelector(".help-btn"), p = h.querySelector(".help-pop");
    b.addEventListener("click", function () {
      var open = b.getAttribute("aria-expanded") !== "true";
      closeHelp(h); b.setAttribute("aria-expanded", String(open)); p.hidden = !open;
      p.classList.remove("flip");
      if (open && p.getBoundingClientRect().right > window.innerWidth - 12) p.classList.add("flip");
    });
  });
  document.addEventListener("click", function (e) { if (!e.target.closest("[data-help]")) closeHelp(); });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var o = document.querySelector('.help-btn[aria-expanded="true"]');
    if (o) { closeHelp(); o.focus(); }
  });

  /* ---------- nav menu (phone) ---------- */
  var menuBtn = document.querySelector(".menu-btn");
  var navLinks = document.getElementById("nav-links");
  if (menuBtn && navLinks) {
    menuBtn.addEventListener("click", function () {
      var open = navLinks.classList.toggle("is-open");
      menuBtn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && navLinks.classList.contains("is-open")) {
        navLinks.classList.remove("is-open"); menuBtn.setAttribute("aria-expanded", "false"); menuBtn.focus();
      }
    });
  }

  /* ---------- contact dialog (no address shown) ---------- */
  var dlg = document.getElementById("contact-dialog");
  var lastTrigger = null;
  document.querySelectorAll("[data-open-contact]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      lastTrigger = b;
      if (navLinks) navLinks.classList.remove("is-open");
      if (dlg && dlg.showModal) dlg.showModal();
    });
  });
  if (dlg) {
    dlg.addEventListener("close", function () { if (lastTrigger) lastTrigger.focus(); });
    dlg.querySelectorAll("[data-close]").forEach(function (b) { b.addEventListener("click", function () { dlg.close(); }); });
  }

  /* ---------- entrances: once per part, staggered; masked headlines ---------- */
  var io = null;
  function reveal(el) { el.classList.add("is-in"); }
  if ("IntersectionObserver" in window) {
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { reveal(en.target); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px 12% 0px", threshold: 0 });
    document.querySelectorAll("[data-reveal], .mask-block, .pic, .bars").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll("[data-reveal], .mask-block, .pic, .bars").forEach(reveal);
  }
  // stagger index within siblings
  document.querySelectorAll("[data-stagger]").forEach(function (parent) {
    Array.prototype.forEach.call(parent.children, function (c, i) { c.style.setProperty("--i", i); });
  });
  document.querySelectorAll(".mask-block").forEach(function (b) {
    b.querySelectorAll(".mask-line").forEach(function (l, i) { l.style.setProperty("--line", i); });
  });
  // also reveal on scroll (covers fast jumps), and fail open on load
  var pending = function () { return document.querySelectorAll("[data-reveal]:not(.is-in), .mask-block:not(.is-in), .pic:not(.is-in), .bars:not(.is-in)"); };
  var ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return; ticking = true;
    window.requestAnimationFrame(function () {
      ticking = false;
      pending().forEach(function (el) { if (el.getBoundingClientRect().top < window.innerHeight * 1.12) { reveal(el); if (io) io.unobserve(el); } });
    });
  }, { passive: true });
  // fail-open: never leave content hidden if the observer never fires
  window.setTimeout(function () {
    document.querySelectorAll("[data-reveal], .mask-block, .pic, .bars").forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 1.2) reveal(el);
    });
  }, 400);

  /* ---------- footer name fitted to the content box by measurement ---------- */
  function fitFooterName() {
    var el = document.querySelector(".footer-name");
    if (!el) return;
    var span = el.firstElementChild;
    var box = el.parentElement.clientWidth - parseFloat(getComputedStyle(el.parentElement).paddingLeft) - parseFloat(getComputedStyle(el.parentElement).paddingRight);
    el.style.fontSize = "100px";
    var w = span.scrollWidth || span.getBoundingClientRect().width;
    // measure the glyph run, not the block
    var probe = document.createElement("span");
    probe.textContent = span.textContent;
    probe.style.cssText = "position:absolute;visibility:hidden;white-space:nowrap;font:inherit;letter-spacing:inherit;";
    el.appendChild(probe);
    w = probe.getBoundingClientRect().width; el.removeChild(probe);
    el.style.fontSize = (100 * (box + 0.06 * 100 * 0) / w * 0.995) + "px";
  }
  window.addEventListener("resize", fitFooterName);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitFooterName);

  setLang(lang, false);

})();
