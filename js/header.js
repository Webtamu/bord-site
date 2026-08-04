// Header behavior on scroll:
//   1. Wordmark collapse — once the page is scrolled, the B and RD letters
//      tuck into the hex; scrolling back to the top restores B⬡RD.
//   2. Panel blending — the bar adopts the ground of whichever section is
//      passing beneath it, so it fades into the dark bands instead of
//      hovering over them. Sections opt in with data-header-theme; the
//      colors themselves live in css/sections.css.
(function () {
  var header = document.querySelector(".site-header");
  if (!header) return;

  var panels = Array.prototype.slice.call(
    document.querySelectorAll("[data-header-theme]")
  );
  var theme = "";
  var queued = false;

  function themeAtHeader() {
    // The header's midline decides: a panel owns the bar once it has
    // covered half of it, which lands the crossfade on the seam.
    var line = header.offsetHeight / 2;
    for (var i = 0; i < panels.length; i++) {
      var box = panels[i].getBoundingClientRect();
      if (box.top <= line && box.bottom > line) {
        return panels[i].getAttribute("data-header-theme");
      }
    }
    return "linen";
  }

  function update() {
    queued = false;
    header.classList.toggle("is-collapsed", window.scrollY > 40);

    var next = themeAtHeader();
    if (next !== theme) {
      theme = next;
      header.setAttribute("data-theme", theme);
    }
  }

  function schedule() {
    if (queued) return;
    queued = true;
    requestAnimationFrame(update);
  }

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  update();
})();
