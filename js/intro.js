// Launch intro sequencing. The choreography lives in css/intro.css;
// this only starts it, ends it, and knows when not to play at all.
// Must load before reveal.js (which waits on "bord:intro-done").
//
// The app's LaunchView, mascot path: the tile lands, Bord takes the o and
// rolls his dice flip, the letters draw in around him, and the screen
// settles away. It plays on EVERY load (founder call 2026-10-25: "for sure
// does the dice flip every single time"), never under reduced motion.

(function () {
  var intro = document.getElementById("intro");

  function done() {
    if (intro && intro.parentNode) intro.parentNode.removeChild(intro);
    window.__bordIntroDone = true;
    window.dispatchEvent(new Event("bord:intro-done"));
  }

  if (!intro) { window.__bordIntroDone = true; return; }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { done(); return; }

  var bord = document.getElementById("intro-bord");
  if (bord) intro.classList.add("has-bord");
  intro.classList.add("is-playing");

  // App timing: the tile snaps in (80ms delay + 550ms settle), and Bord
  // crouches 0.35s after it starts, so the two moments read separately.
  // Adding .bord--rolling plays his baked roll once from its first frame.
  if (bord) setTimeout(function () { bord.classList.add("bord--rolling"); }, 430);

  // His roll is 1.7s: crouch, hop, tumble, plant, burst back to the flat
  // mark at ~2.1s. The letters finish filling at ~2.1s too. A beat, then the
  // screen settles away, the app's exit in web time.
  // ?intro=hold keeps the intro on screen (for checking the choreography).
  if (/[?&]intro=hold\b/.test(location.search)) return;
  setTimeout(function () { intro.classList.add("is-leaving"); }, 2550);
  setTimeout(done, 3050);
})();
