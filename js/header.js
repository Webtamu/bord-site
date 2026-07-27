// Header wordmark collapse: once the page is scrolled, the B and RD
// letters tuck into the hex; scrolling back to the top restores B⬡RD.
(function () {
  var header = document.querySelector(".site-header");
  if (!header) return;

  function update() {
    header.classList.toggle("is-collapsed", window.scrollY > 40);
  }
  window.addEventListener("scroll", update, { passive: true });
  update();
})();
