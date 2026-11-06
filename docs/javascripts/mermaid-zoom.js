(function () {
  "use strict";

  // Material renders each Mermaid diagram inside a closed shadow root, so the
  // viewer moves the whole host element into the overlay (and back on close)
  // and zooms it with a CSS transform. It never reads the SVG itself.
  if (window.__mermaidZoomInstalled) return;
  window.__mermaidZoomInstalled = true;

  var OVERLAY_ID = "mermaid-zoom-overlay";
  var INITIAL_SCALE = 1.5;
  var MAX_SCALE = 8;
  var MIN_SCALE = 0.3;
  var PADDING = 24;
  var DRAG_THRESHOLD = 4;
  var ZOOM_STEP = 1.4;

  var active = null;

  function button(className, label, text) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = className;
    b.setAttribute("aria-label", label);
    b.textContent = text;
    return b;
  }

  function closeOverlay(restoreFocus) {
    if (!active) return;
    var state = active;
    active = null;

    document.removeEventListener("keydown", state.onKeyDown);
    window.removeEventListener("resize", state.onResize);

    var host = state.host;
    host.style.transform = "";
    host.style.transformOrigin = "";
    host.style.cursor = "";
    if (state.placeholder.parentNode) {
      state.placeholder.replaceWith(host);
    }

    if (state.overlay.parentNode) {
      state.overlay.parentNode.removeChild(state.overlay);
    }
    document.body.style.overflow = state.prevOverflow;

    if (restoreFocus !== false && host.isConnected) {
      try { host.focus({ preventScroll: true }); } catch (err) { /* ignore */ }
    }
  }

  function openDiagram(host) {
    if (active) closeOverlay(false);

    var overlay = document.createElement("div");
    overlay.id = OVERLAY_ID;
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Diagram viewer");

    var viewport = document.createElement("div");
    viewport.className = "mermaid-zoom-container";

    var closeBtn = button("mermaid-zoom-close", "Close", "\u00d7");
    var controls = document.createElement("div");
    controls.className = "mermaid-zoom-controls";
    var zoomOutBtn = button("mermaid-zoom-btn", "Zoom out", "\u2212");
    var fitBtn = button("mermaid-zoom-btn", "Fit to screen", "Fit");
    var zoomInBtn = button("mermaid-zoom-btn", "Zoom in", "+");
    controls.appendChild(zoomOutBtn);
    controls.appendChild(fitBtn);
    controls.appendChild(zoomInBtn);

    var hint = document.createElement("div");
    hint.className = "mermaid-zoom-hint";
    hint.textContent = "Scroll or pinch to zoom \u00b7 Drag to pan \u00b7 Esc to close";

    var placeholder = document.createComment("mermaid-zoom-placeholder");
    host.parentNode.insertBefore(placeholder, host);

    host.style.transformOrigin = "center center";
    host.style.cursor = "grab";
    viewport.appendChild(host);

    overlay.appendChild(viewport);
    overlay.appendChild(controls);
    overlay.appendChild(hint);
    overlay.appendChild(closeBtn);

    var scale = INITIAL_SCALE;
    var panX = 0;
    var panY = 0;
    var naturalW = 1;
    var naturalH = 1;

    // The host is centered in the viewport, so every point is expressed
    // relative to the viewport centre (the transform origin).
    function apply() {
      host.style.transform =
        "translate(" + panX + "px, " + panY + "px) scale(" + scale + ")";
    }

    function measure() {
      // Size of the host at scale 1: read it with the transform cleared.
      var current = host.style.transform;
      host.style.transform = "";
      var r = host.getBoundingClientRect();
      host.style.transform = current;
      naturalW = Math.max(r.width, 1);
      naturalH = Math.max(r.height, 1);
    }

    function fitScale() {
      var availW = Math.max(viewport.clientWidth - PADDING * 2, 1);
      var availH = Math.max(viewport.clientHeight - PADDING * 2, 1);
      return Math.min(availW / naturalW, availH / naturalH);
    }

    function clamp(s) {
      return Math.min(Math.max(MIN_SCALE, s), MAX_SCALE);
    }

    // Zoom about q (offset from the viewport centre) so q stays under the
    // pointer; (fromX, fromY) is q's previous position for pinch tracking.
    function zoomAt(qx, qy, next, fromX, fromY) {
      next = clamp(next);
      var ratio = next / scale;
      if (fromX === undefined) { fromX = qx; fromY = qy; }
      panX = qx - (fromX - panX) * ratio;
      panY = qy - (fromY - panY) * ratio;
      scale = next;
      apply();
    }

    function centerOffset(clientX, clientY) {
      var r = viewport.getBoundingClientRect();
      return { x: clientX - (r.left + r.width / 2), y: clientY - (r.top + r.height / 2) };
    }

    function zoomCenter(factor) { zoomAt(0, 0, scale * factor); }

    function fit() {
      scale = clamp(fitScale());
      panX = 0;
      panY = 0;
      apply();
    }

    closeBtn.addEventListener("click", function () { closeOverlay(); });
    zoomInBtn.addEventListener("click", function () { zoomCenter(ZOOM_STEP); });
    zoomOutBtn.addEventListener("click", function () { zoomCenter(1 / ZOOM_STEP); });
    fitBtn.addEventListener("click", fit);

    viewport.addEventListener("wheel", function (e) {
      e.preventDefault();
      var dy = e.deltaY;
      if (e.deltaMode === 1) dy *= 16;
      else if (e.deltaMode === 2) dy *= viewport.clientHeight;
      var q = centerOffset(e.clientX, e.clientY);
      zoomAt(q.x, q.y, scale * Math.exp(-dy * (e.ctrlKey ? 0.01 : 0.0015)));
    }, { passive: false });

    // Pointer events cover mouse, touch and pen, and are scoped to the
    // viewport so nothing is left on `document` after the overlay closes.
    var pointers = new Map();
    var dragged = false;
    var downAt = null;
    var pinchDist = 0;
    var pinchMid = null;

    function pinchState() {
      var pts = Array.from(pointers.values());
      var mid = centerOffset((pts[0].x + pts[1].x) / 2, (pts[0].y + pts[1].y) / 2);
      return { dist: Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y), mid: mid };
    }

    viewport.addEventListener("pointerdown", function (e) {
      pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      try { viewport.setPointerCapture(e.pointerId); } catch (err) { /* ignore */ }
      if (pointers.size === 1) {
        dragged = false;
        downAt = { x: e.clientX, y: e.clientY };
      } else if (pointers.size === 2) {
        var st = pinchState();
        pinchDist = st.dist;
        pinchMid = st.mid;
        dragged = true;
      }
      host.style.cursor = "grabbing";
    });

    viewport.addEventListener("pointermove", function (e) {
      var prev = pointers.get(e.pointerId);
      if (!prev) return;
      var cur = { x: e.clientX, y: e.clientY };
      if (pointers.size === 1) {
        if (downAt && Math.hypot(cur.x - downAt.x, cur.y - downAt.y) > DRAG_THRESHOLD) {
          dragged = true;
        }
        panX += cur.x - prev.x;
        panY += cur.y - prev.y;
        pointers.set(e.pointerId, cur);
        apply();
      } else if (pointers.size === 2) {
        pointers.set(e.pointerId, cur);
        var st = pinchState();
        if (pinchDist > 0 && pinchMid) {
          zoomAt(st.mid.x, st.mid.y, scale * (st.dist / pinchDist), pinchMid.x, pinchMid.y);
        }
        pinchDist = st.dist;
        pinchMid = st.mid;
        dragged = true;
      }
    });

    function endPointer(e) {
      if (!pointers.delete(e.pointerId)) return;
      pinchDist = 0;
      pinchMid = null;
      if (pointers.size === 1) {
        pointers.forEach(function (pt) { downAt = { x: pt.x, y: pt.y }; });
      }
      if (pointers.size === 0) host.style.cursor = "grab";
    }
    viewport.addEventListener("pointerup", endPointer);
    viewport.addEventListener("pointercancel", endPointer);
    viewport.addEventListener("lostpointercapture", endPointer);

    // Tapping the backdrop (outside the diagram, no drag) closes the viewer.
    // Pointer capture retargets the click to the viewport, so hit-test the
    // diagram rectangle by coordinates.
    viewport.addEventListener("click", function (e) {
      if (dragged) return;
      var r = host.getBoundingClientRect();
      var inside =
        e.clientX >= r.left && e.clientX <= r.right &&
        e.clientY >= r.top && e.clientY <= r.bottom;
      if (!inside) closeOverlay();
    });

    function onKeyDown(e) {
      if (e.key === "Tab") {
        var focusables = Array.from(overlay.querySelectorAll("button"));
        if (!focusables.length) return;
        // Move focus manually so it cycles inside the dialog in every browser
        // (Safari does not make buttons tabbable by default).
        var idx = focusables.indexOf(document.activeElement);
        var next = e.shiftKey
          ? (idx <= 0 ? focusables.length - 1 : idx - 1)
          : (idx === -1 || idx === focusables.length - 1 ? 0 : idx + 1);
        e.preventDefault();
        focusables[next].focus();
        return;
      }
      if (e.key === "Escape") closeOverlay();
      else if (e.key === "+" || e.key === "=") zoomCenter(ZOOM_STEP);
      else if (e.key === "-") zoomCenter(1 / ZOOM_STEP);
      else if (e.key === "0") fit();
    }
    // Keep the user's zoom and pan on resize (mobile URL bar show/hide).
    function onResize() { measure(); }
    document.addEventListener("keydown", onKeyDown);
    window.addEventListener("resize", onResize);

    active = {
      host: host,
      placeholder: placeholder,
      overlay: overlay,
      onKeyDown: onKeyDown,
      onResize: onResize,
      prevOverflow: document.body.style.overflow
    };
    document.body.style.overflow = "hidden";
    document.body.appendChild(overlay);
    measure();
    apply();
    requestAnimationFrame(function () {
      overlay.classList.add("mermaid-zoom-visible");
    });
    closeBtn.focus({ preventScroll: true });
  }

  function enhance(root) {
    if (!root.querySelectorAll) return;
    Array.prototype.forEach.call(
      root.querySelectorAll("div.mermaid:not([data-zoom-enhanced])"),
      function (h) {
        h.setAttribute("data-zoom-enhanced", "true");
        h.setAttribute("tabindex", "0");
        h.setAttribute("role", "button");
        h.setAttribute("aria-label", "Open diagram in zoom viewer");
      }
    );
  }

  function hostFor(e) {
    var target = e.target;
    if (!target || !target.closest) return null;
    // Authored links inside a diagram keep their normal behavior.
    if (target.closest("a")) return null;
    var host = target.closest("div.mermaid");
    // A diagram already inside the overlay must not re-open it.
    if (!host || host.closest("#" + OVERLAY_ID)) return null;
    return host;
  }

  // Delegated listeners are installed once, so diagrams rendered later and
  // page navigation never stack handlers.
  document.addEventListener("click", function (e) {
    if (active) return;
    var host = hostFor(e);
    if (!host) return;
    var sel = window.getSelection && window.getSelection();
    if (sel && !sel.isCollapsed) return;
    openDiagram(host);
  });

  document.addEventListener("keydown", function (e) {
    if (active || (e.key !== "Enter" && e.key !== " ")) return;
    var host = hostFor(e);
    if (!host || e.target !== host) return;
    e.preventDefault();
    openDiagram(host);
  });

  function init() {
    enhance(document);
    new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        Array.prototype.forEach.call(m.addedNodes, function (n) {
          if (n.nodeType === 1) enhance(n);
        });
      });
    }).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Never leave a stale viewer (and the body scroll lock) behind when Material
  // swaps the page content.
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(function () { closeOverlay(false); });
  }
})();
