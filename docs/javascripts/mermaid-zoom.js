(function () {
  "use strict";

  var OVERLAY_ID = "mermaid-zoom-overlay";
  var BOUND_ATTR = "data-mermaid-zoom-bound";

  function createOverlay() {
    var overlay = document.createElement("div");
    overlay.id = OVERLAY_ID;

    var closeBtn = document.createElement("button");
    closeBtn.className = "mermaid-zoom-close";
    closeBtn.innerHTML = "&times;";
    closeBtn.setAttribute("aria-label", "Close");

    var hint = document.createElement("div");
    hint.className = "mermaid-zoom-hint";
    hint.textContent = "Scroll to zoom · Drag to pan · Esc to close";

    var container = document.createElement("div");
    container.className = "mermaid-zoom-container";

    overlay.appendChild(closeBtn);
    overlay.appendChild(hint);
    overlay.appendChild(container);

    return { overlay: overlay, container: container, closeBtn: closeBtn };
  }

  var currentPlaceholder = null;
  var currentHost = null;
  var scale = 1.5;
  var panX = 0;
  var panY = 0;

  function closeOverlay() {
    var overlay = document.getElementById(OVERLAY_ID);
    if (!overlay) return;

    if (currentPlaceholder && currentHost) {
      currentHost.style.transform = "";
      currentHost.style.transformOrigin = "";
      currentHost.style.cursor = "";
      currentPlaceholder.replaceWith(currentHost);
    }

    overlay.classList.add("mermaid-zoom-fade-out");
    setTimeout(function () {
      if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    }, 200);

    currentPlaceholder = null;
    currentHost = null;
    scale = 1.5;
    panX = 0;
    panY = 0;

    document.body.style.overflow = "";
    document.removeEventListener("keydown", onKeyDown);
  }

  function onKeyDown(e) {
    if (e.key === "Escape") closeOverlay();
  }

  function applyTransform() {
    if (currentHost) {
      currentHost.style.transform =
        "translate(" + panX + "px, " + panY + "px) scale(" + scale + ")";
    }
  }

  function openDiagram(host) {
    var existing = document.getElementById(OVERLAY_ID);
    if (existing) closeOverlay();

    var parts = createOverlay();

    var placeholder = document.createComment("mermaid-zoom-placeholder");
    host.parentNode.insertBefore(placeholder, host);
    currentPlaceholder = placeholder;
    currentHost = host;

    host.style.transformOrigin = "center center";
    host.style.cursor = "grab";
    parts.container.appendChild(host);

    document.body.appendChild(parts.overlay);
    document.body.style.overflow = "hidden";

    requestAnimationFrame(function () {
      parts.overlay.classList.add("mermaid-zoom-visible");
      applyTransform();
    });

    parts.closeBtn.addEventListener("click", closeOverlay);
    parts.overlay.addEventListener("click", function (e) {
      if (e.target === parts.overlay) closeOverlay();
    });

    var isPanning = false;
    var startX = 0;
    var startY = 0;

    parts.container.addEventListener("wheel", function (e) {
      e.preventDefault();
      var delta = e.deltaY > 0 ? -0.1 : 0.1;
      scale = Math.min(Math.max(0.3, scale + delta), 5);
      applyTransform();
    }, { passive: false });

    parts.container.addEventListener("mousedown", function (e) {
      if (e.target.closest(".mermaid-zoom-close")) return;
      isPanning = true;
      startX = e.clientX - panX;
      startY = e.clientY - panY;
      currentHost.style.cursor = "grabbing";
      e.preventDefault();
    });

    document.addEventListener("mousemove", function handler(e) {
      if (!isPanning) return;
      panX = e.clientX - startX;
      panY = e.clientY - startY;
      applyTransform();
    });

    document.addEventListener("mouseup", function handler() {
      if (isPanning) {
        isPanning = false;
        if (currentHost) currentHost.style.cursor = "grab";
      }
    });

    var lastTouchDist = 0;
    parts.container.addEventListener("touchstart", function (e) {
      if (e.touches.length === 1) {
        isPanning = true;
        startX = e.touches[0].clientX - panX;
        startY = e.touches[0].clientY - panY;
      } else if (e.touches.length === 2) {
        isPanning = false;
        lastTouchDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
      }
    }, { passive: true });

    parts.container.addEventListener("touchmove", function (e) {
      if (e.touches.length === 1 && isPanning) {
        panX = e.touches[0].clientX - startX;
        panY = e.touches[0].clientY - startY;
        applyTransform();
      } else if (e.touches.length === 2) {
        var dist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        if (lastTouchDist > 0) {
          scale = Math.min(Math.max(0.3, scale * (dist / lastTouchDist)), 5);
          applyTransform();
        }
        lastTouchDist = dist;
      }
    }, { passive: true });

    parts.container.addEventListener("touchend", function () {
      isPanning = false;
      lastTouchDist = 0;
    });

    document.addEventListener("keydown", onKeyDown);
  }

  function bindDiagrams() {
    var diagrams = document.querySelectorAll("div.mermaid:not([" + BOUND_ATTR + "])");
    diagrams.forEach(function (el) {
      el.setAttribute(BOUND_ATTR, "true");
      el.style.cursor = "pointer";
      el.addEventListener("click", function (e) {
        e.stopPropagation();
        openDiagram(el);
      });
    });
  }

  function init() {
    bindDiagrams();

    var observer = new MutationObserver(function (mutations) {
      var shouldBind = mutations.some(function (m) {
        return m.addedNodes.length > 0;
      });
      if (shouldBind) bindDiagrams();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      init();
    });
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
