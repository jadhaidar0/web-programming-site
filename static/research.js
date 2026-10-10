/* =====================================================================
   research.js — GIN446

   One job: drive the live-versus-static demonstration on the research
   page. Every other card on that page demonstrates itself with plain
   HTML and CSS, but the difference between an HTMLCollection and a
   NodeList is only visible when the DOM changes, and nothing but
   JavaScript can change the DOM. A card describing it without a running
   demonstration would be a screenshot in prose.

   Wrapped in an IIFE so nothing here becomes a global, and it exits
   immediately on any page that does not contain the demo.
   ===================================================================== */

(function () {
  "use strict";

  const box = document.getElementById("chipBox");
  if (box === null) {
    return;                       // not the research page
  }

  const liveOut = document.getElementById("liveCount");
  const snapOut = document.getElementById("snapCount");
  const log     = document.getElementById("collLog");

  /* The two collections are captured ONCE, here, and never looked up
     again. That is the whole point of the demonstration: whatever
     happens to the page from now on, one of these two keeps up by
     itself and the other does not. */

  // Live. getElementsByClassName returns an HTMLCollection that stays
  // attached to the document, so it reports what is there right now.
  const live = box.getElementsByClassName("chip");

  // Static. querySelectorAll returns a NodeList that is a snapshot of
  // the matches at the moment it ran. It is re-taken only on Reset.
  let snap = box.querySelectorAll(".chip");

  let made = 0;

  function render() {
    liveOut.textContent = live.length;
    snapOut.textContent = snap.length;
  }

  function say(message) {
    log.textContent = message;
  }

  // The one place a chip is made. addChip() and reset() both use it.
  function makeChip() {
    made = made + 1;

    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = "chip " + made;
    box.appendChild(chip);
  }

  function addChip() {
    makeChip();
    render();
    say("Added one chip. The live collection reports " + live.length +
        " on its own. The snapshot still says " + snap.length +
        ", because it was taken before the chip existed.");
  }

  /* The classic bug, on purpose.
     Removing an element takes it out of the live collection as well, so
     length shrinks on every pass while i counts up. The two meet in the
     middle and the loop stops with half the chips still on the page. */
  function removeWithLiveLoop() {
    const before = live.length;

    for (let i = 0; i < live.length; i++) {
      live[i].remove();
    }

    render();
    say("Tried to remove " + before + " chips by counting up through a live " +
        "collection. " + live.length + " are still here: the list got shorter " +
        "while the loop got longer, so every other chip was skipped.");
  }

  /* The fix. A static NodeList cannot shrink underneath the loop, so
     every element captured gets removed. forEach is available here
     because NodeList has it; an HTMLCollection does not. */
  function removeWithSnapshot() {
    const nodes = box.querySelectorAll(".chip");
    const before = nodes.length;

    nodes.forEach(function (node) {
      node.remove();
    });

    render();
    say("Removed all " + before + " chips with a fresh querySelectorAll. " +
        "The snapshot cannot shrink while the loop runs, so nothing is " +
        "skipped. This also uses forEach, which a NodeList has and an " +
        "HTMLCollection does not.");
  }

  function reset() {
    box.innerHTML = "";
    made = 0;

    for (let i = 0; i < 4; i++) {
      makeChip();
    }

    // Re-take the snapshot so the demonstration can be run again.
    snap = box.querySelectorAll(".chip");

    render();
    say("Back to four chips, and the snapshot has been taken again. " +
        "Both now agree at " + live.length + ".");
  }

  document.getElementById("chipAdd").addEventListener("click", addChip);
  document.getElementById("chipKillLive").addEventListener("click", removeWithLiveLoop);
  document.getElementById("chipKillSnap").addEventListener("click", removeWithSnapshot);
  document.getElementById("chipReset").addEventListener("click", reset);

  render();
})();
