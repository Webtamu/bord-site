// Scroll-entry reveal: opacity + 8px rise, once, gently staggered
// within a shared parent. Respects prefers-reduced-motion (base.css
// disables the transition; elements are simply visible).
// Waits for the launch intro so the hero enters as the overlay leaves.

(function () {
  if (document.getElementById("intro") && !window.__bordIntroDone) {
    window.addEventListener("bord:intro-done", init, { once: true });
  } else {
    init();
  }

  function init() {
  var els = document.querySelectorAll("[data-reveal]");
  if (!("IntersectionObserver" in window)) {
    els.forEach(function (el) { el.classList.add("is-visible"); });
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var siblings = el.parentElement
          ? el.parentElement.querySelectorAll(":scope > [data-reveal]")
          : [];
        var index = Array.prototype.indexOf.call(siblings, el);
        el.style.transitionDelay = index > 0 ? index * 70 + "ms" : "";
        el.classList.add("is-visible");
        observer.unobserve(el);
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.1 }
  );

  els.forEach(function (el) { observer.observe(el); });
  }
})();
