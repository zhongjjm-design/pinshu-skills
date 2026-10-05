const SC = __SC__;
const tl = gsap.timeline({ paused: true }), E = "power3.out";
const has = (s) => !!document.querySelector(s);

SC.forEach((s) => {
  const t = s.t, v = s.vo, i = s.i, d = s.d;
  // Entrances: video-to-video is a hard cut (fading each clip in from black looked like blinking at every seam); only the clip after a chapter card keeps a fade (the card is fading out over it)
  // Videos are not simply set visible: the renderer draws a video at the wrong scale on its first frame, so a 2-frame fade hides that frame; build.py runs the previous clip 2 frames longer underneath
  const fadeIn = (sel, st, dur, img) => (s.k === "chapter" && st > t + 2.5 && st <= t + 3.05) ? tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: dur, ease: "power1.out" }, st)
    : img ? tl.set(sel, { opacity: 1 }, st) : tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.067, ease: "none" }, st);
  // Video: entrance plus a slow push (animated on the untimed wrapper .vw and on the video's own scale)
  (s.cl || []).forEach((c, ci) => {
    if (c.img) {  // single image: fade in plus slow push
      fadeIn("#imw" + i + "_" + ci, c.st, 0.3, true);
      tl.fromTo("#im" + i + "_" + ci, { opacity: 1, scale: 1.0 }, { opacity: 1, scale: 1.10, duration: c.dd, ease: "none" }, c.st);
      return;
    }
    if (c.gfx) {  // parody "typical anniversary film" cards: same background, hard cuts; rays rotate on absolute time so they stay continuous across cards
      const g = "#gx" + i + "_" + ci, a = c.st, dd = c.dd;
      tl.set(g, { opacity: 1 }, a);
      if (has(g + " .grays")) tl.fromTo(g + " .grays", { rotation: a * 2 }, { rotation: (a + dd) * 2, duration: dd, ease: "none" }, a);
      if (c.gfx === "recap") {  // recap: told numbers light up one by one; the ruler draws when the narration reaches its cue
        document.querySelectorAll(g + " .rci").forEach((b, k) => tl.fromTo(b, { opacity: 0.18, y: 16 }, { opacity: 1, y: 0, duration: 0.35, ease: E }, a + 0.35 + k * 0.32));
        tl.fromTo(g + " .rcl", { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: "power2.inOut" }, c.t2 || a + dd - 2.2);
        return;
      }
      if (c.gfx === "gray") {
        // "what does it have to do with you?": keep colour; the card recedes, blurs and darkens. Never desaturate to black and white: Chinese viewers read black-and-white as mourning.
        tl.fromTo(g, { filter: "blur(0px) brightness(1)" }, { filter: "blur(5px) brightness(0.72)", duration: 0.8, ease: "power1.out" }, a);
        tl.fromTo(g, { scale: 1 }, { scale: 0.86, duration: dd, ease: "none" }, a);
        return;
      }
      if (has(g + " .gc")) tl.fromTo(g + " .gc", { scale: 1.12, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.45, ease: E }, a);
      if (c.gfx === "growth") document.querySelectorAll(g + " .gchart i").forEach((b, k) => tl.fromTo(b, { scaleY: 0 }, { scaleY: 1, duration: 0.45, ease: E }, a + 0.05 + k * 0.07));
      if (c.gfx === "thanks") document.querySelectorAll(g + " .gdot").forEach((b, k) => tl.fromTo(b, { y: 0 }, { y: 1200, duration: 1.6 + (k % 3) * 0.3, ease: "none" }, a + (k % 4) * 0.08));
      if (c.gfx === "future") tl.fromTo(g + " .gsun", { y: 0 }, { y: -520, duration: dd, ease: "power1.out" }, a);
      if (c.gfx === "stamp") {
        document.querySelectorAll(g + " .gp").forEach((b, k) => tl.fromTo(b, { opacity: 0, scale: 1.3 }, { opacity: 0.55, scale: 1, duration: 0.3, ease: E }, a + k * 0.06));
        tl.fromTo(g + " .gstamp", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(1.4)" }, a + 0.4);
      }
      return;
    }
    if (c.flip) {  // posters flip quickly one over another; the last one stays
      const step = c.dd / c.flip;
      tl.set("#fp" + i + "_0", { opacity: 1, scale: 1 }, c.st);  // first poster appears at once (fading in from black reads as a blink); the rest fade in over it
      for (let k = 1; k < c.flip; k++) tl.fromTo("#fp" + i + "_" + k, { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: 0.12, ease: "power2.out" }, c.st + k * step);
      return;
    }
    // original film: scaled up by spec.FRAME (default from the top-left, keeping the broadcaster logo out); stock footage: centred push
    fadeIn("#vw" + i + "_" + ci, c.st, 0.3);
    if (c.card) tl.set("#v" + i + "_" + ci, { scale: 1 }, c.st);  // the original film's own title card: no scale, no push, centred as shot (scaling from top-left pushed it off centre)
    else tl.fromTo("#v" + i + "_" + ci, { scale: __Z0__ }, { scale: __Z1__, duration: c.dd, ease: "none", transformOrigin: c.stock ? "50% 50%" : "__ORIGIN__" }, c.st);
    if (c.quote) {  // comment quote card
      tl.fromTo("#qc" + i + "_" + ci, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.45, ease: E }, c.st + 0.25);
      tl.to("#qc" + i + "_" + ci, { opacity: 0, duration: 0.25, ease: "power1.in" }, c.st + c.dd - 0.25);
    }
  });
  ["v", "b"].forEach((p) => {
    if (!has("#" + p + "w" + i)) return;
    const st = (s.k === "chapter" && p === "v") ? t + 2.9 : t;
    const dd = (s.k === "chapter" && p === "b") ? 3.2 : (s.k === "chapter" ? d - 2.9 : d);
    fadeIn("#" + p + "w" + i, st, 0.4);
    if (p === "v") tl.fromTo("#" + p + i, { scale: __Z0__ }, { scale: __Z1__, duration: dd, ease: "none", transformOrigin: "__ORIGIN__" }, st);
    else tl.fromTo("#" + p + i, { scale: 1.0 }, { scale: 1.05, duration: dd, ease: "none" }, st);
  });
  if (s.k === "full" && has("#o" + i)) tl.fromTo("#o" + i, { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: E }, v + 0.6);
  if (s.k === "comments") {
    tl.fromTo("#ch" + i, { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.5, ease: E }, t + 0.15);
    tl.fromTo("#cm" + i, { opacity: 0, y: 120, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: E }, t + 0.35);
    tl.fromTo("#lk" + i, { opacity: 0 }, { opacity: 1, duration: 0.4 }, t + 1.0);
    tl.fromTo("#cm" + i, { scale: 1 }, { scale: 1.06, duration: Math.max(d - 1.05, 0.5), ease: "none" }, t + 1.05);
  }
  if (s.k === "ask") tl.fromTo("#ak" + i, { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.6)" }, t + 0.1);
  if (s.k === "chapter") {
    tl.fromTo("#cp" + i + " .cno", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5, ease: E }, t + 0.15);
    tl.fromTo("#cp" + i + " .ct1", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.55, ease: E }, t + 0.4);
    tl.fromTo("#cp" + i + " .ct2", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.55, ease: E }, t + 0.7);
    tl.to("#cp" + i, { opacity: 0, duration: 0.4, ease: "power1.in" }, t + 2.7);
  }
  if (s.k === "story") {
    const n0 = s.bite ? v - 0.25 : t + 0.2;  // stories with a speaker bite: the number appears when the bite ends and narration starts (avoids the film's own title card)
    tl.fromTo("#sn" + i, { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: 0.55, ease: "back.out(1.5)", transformOrigin: "right top" }, n0);
    tl.fromTo("#st" + i, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.5, ease: E }, n0 + 0.3);
    ["#st" + i, "#sn" + i].forEach((x, k) => tl.to(x, { opacity: 0, duration: 0.35 }, t + d - 0.5 + k * 0.08));  // staggered exit: last in, first out
  }
  if (s.k === "chips") {
    tl.fromTo("#chd" + i, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.5, ease: E }, v + 0.3);
    const n = document.querySelectorAll('[id^="c' + i + '_"]').length;
    for (let j = 0; j < n; j++) tl.fromTo("#c" + i + "_" + j, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.35, ease: "back.out(1.8)" }, s.chipT ? s.chipT[j] : v + 2.2 + j * 0.5);
  }
  if (s.k === "posters") {
    tl.fromTo("#ph", { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, t);
    for (let j = 0; j < __NPOST__; j++) tl.fromTo("#p" + j, { opacity: 0, scale: 1.2 }, { opacity: 1, scale: 1, duration: 0.35, ease: E }, t + 0.05 + j * 0.16);
  }
  if (s.k === "end") {
    tl.fromTo("#ek", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.5, ease: E }, t + 0.05);  // enter early so the end card never shows an empty red frame
    tl.fromTo("#et", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.7, ease: E }, t + 0.3);
    tl.fromTo("#ea", { opacity: 0 }, { opacity: 1, duration: 0.6 }, t + 1.0);
    if (has("#er")) tl.fromTo("#er", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: E }, t + 1.5);
    tl.fromTo(".endc", { scale: 1 }, { scale: 1.03, duration: d, ease: "none", transformOrigin: "0% 50%" }, t);
  }
});
// opening title page
tl.set("#tvw", { opacity: 1 }, 0);  // the first frame already shows the full title, no fade from black
tl.fromTo("#tv", { scale: __Z0__ }, { scale: __ZT__, duration: 3.4, ease: "none", transformOrigin: "__ORIGIN__" }, 0);
tl.set(["#tk", "#tt1", "#tt2", "#ta"], { opacity: 1 }, 0);
tl.fromTo(".ttl", { scale: 1 }, { scale: 1.03, duration: 3.0, ease: "none", transformOrigin: "0% 50%" }, 0);
["#ta", "#tt2", "#tt1", "#tk"].forEach((x, k) => tl.to(x, { opacity: 0, duration: 0.3, ease: "power1.in" }, 2.9 + k * 0.06));  // staggered exit, done before 3.38 s
// posters/cards: hide the scene labels when an insert appears
SC.forEach((s) => {
  if (s.overlayOff === undefined) return;
  // finish before the new picture appears, staggered last-in-first-out (story numbers once overlapped the poster numbers for 5 frames; labels should not all vanish at once)
  const sel = s.k === "chips" ? ["#s" + s.i + " .chips", "#s" + s.i + " .chead", "#s" + s.i + " .cshade"] : s.k === "story" ? ["#st" + s.i, "#sn" + s.i] : ["#ph", "#s" + s.i + " .pwall"];
  sel.forEach((x, k) => tl.to(x, { opacity: 0, duration: 0.25, ease: "power1.in" }, s.overlayOff - 0.4 + k * 0.08));
});
window.__timelines["main"] = tl;
