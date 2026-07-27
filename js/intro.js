// Launch intro sequencing. The choreography lives in css/intro.css;
// this only starts it, ends it, and knows when not to play at all:
// once per session, and never under prefers-reduced-motion.
// Must load before reveal.js (which waits on "bord:intro-done").

(function () {
  var intro = document.getElementById("intro");

  function done() {
    if (intro && intro.parentNode) intro.parentNode.removeChild(intro);
    window.__bordIntroDone = true;
    window.dispatchEvent(new Event("bord:intro-done"));
  }

  if (!intro) { window.__bordIntroDone = true; return; }

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var force = /[?&]intro\b/.test(location.search);   // ?intro replays it
  var seen = false;
  try { seen = sessionStorage.getItem("bord-intro") === "1"; } catch (e) {}

  if (reduced || (seen && !force)) { done(); return; }
  try { sessionStorage.setItem("bord-intro", "1"); } catch (e) {}

  intro.classList.add("is-playing");

  // Hex snaps ~0.1s, letters draw staggered to ~1.9s, fills land ~2.1s,
  // beat, then the screen settles away — the app's exit, in web time.
  setTimeout(function () { intro.classList.add("is-leaving"); }, 2250);
  setTimeout(done, 2750);
})();
