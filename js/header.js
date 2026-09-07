// Header behavior on scroll: once the page is scrolled, the b and rd
// letters tuck into the hex; scrolling back to the top restores b⬡rd.
// (The album has one ground the whole way down, so the bar no longer
// recolours over passing panels.)
(function () {
  var header = document.querySelector(".site-header");
  if (!header) return;
  var queued = false;

  function update() {
    queued = false;
    header.classList.toggle("is-collapsed", window.scrollY > 40);
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
