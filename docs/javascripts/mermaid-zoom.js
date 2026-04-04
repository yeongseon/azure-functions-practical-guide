/**
 * Mermaid Diagram Zoom
 * Click any mermaid diagram to open a fullscreen zoomable/pannable overlay.
 * Press Escape or click the close button to dismiss.
 */
(function () {
  "use strict";

  var OVERLAY_ID = "mermaid-zoom-overlay";

  function createOverlay() {
    var overlay = document.createElement("div");
    overlay.id = OVERLAY_ID;

    var closeBtn = document.createElement("button");
    closeBtn.className = "mermaid-zoom-close";
    closeBtn.innerHTML = "&times;";
    closeBtn.setAttribute("aria-label", "Close");
    closeBtn.addEventListener("click", destroyOverlay);

    var hint = document.createElement("div");
    hint.className = "mermaid-zoom-hint";
    hint.textContent = "Scroll to zoom \u00b7 Drag to pan \u00b7 Esc to close";

    var container = document.createElement("div");
    container.className = "mermaid-zoom-container";

    overlay.appendChild(closeBtn);
    overlay.appendChild(hint);
    overlay.appendChild(container);

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) destroyOverlay();
    });

    return { overlay: overlay, container: container };
  }

  function destroyOverlay() {
    var overlay = document.getElementById(OVERLAY_ID);
    if (overlay) {
      overlay.classList.add("mermaid-zoom-fade-out");
      setTimeout(function () {
        if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
      }, 200);
    }
    document.removeEventListener("keydown", onKeyDown);
  }

  function onKeyDown(e) {
    if (e.key === "Escape") destroyOverlay();
  }

  function enablePanZoom(container, svgEl) {
    var scale = 1;
    var panX = 0;
    var panY = 0;
    var isPanning = false;
    var startX = 0;
    var startY = 0;

    function applyTransform() {
      svgEl.style.transform =
        "translate(" + panX + "px, " + panY + "px) scale(" + scale + ")";
    }

    container.addEventListener(
      "wheel",
      function (e) {
        e.preventDefault();
        var delta = e.deltaY > 0 ? -0.1 : 0.1;
        scale = Math.min(Math.max(0.3, scale + delta), 5);
        applyTransform();
      },
      { passive: false }
    );

    container.addEventListener("mousedown", function (e) {
      isPanning = true;
      startX = e.clientX - panX;
      startY = e.clientY - panY;
      container.style.cursor = "grabbing";
      e.preventDefault();
    });

    document.addEventListener("mousemove", function (e) {
      if (!isPanning) return;
      panX = e.clientX - startX;
      panY = e.clientY - startY;
      applyTransform();
    });

    document.addEventListener("mouseup", function () {
      isPanning = false;
      container.style.cursor = "grab";
    });

    // Touch support
    var lastTouchDist = 0;
    container.addEventListener(
      "touchstart",
      function (e) {
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
      },
      { passive: true }
    );

    container.addEventListener(
      "touchmove",
      function (e) {
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
      },
      { passive: true }
    );

    container.addEventListener("touchend", function () {
      isPanning = false;
      lastTouchDist = 0;
    });
  }

  function openDiagram(mermaidEl) {
    // Remove existing overlay if any
    var existing = document.getElementById(OVERLAY_ID);
    if (existing && existing.parentNode) existing.parentNode.removeChild(existing);

    var parts = createOverlay();
    var svgSource = mermaidEl.querySelector("svg");
    if (!svgSource) return;

    var svgClone = svgSource.cloneNode(true);
    svgClone.style.maxWidth = "none";
    svgClone.style.maxHeight = "none";
    svgClone.style.width = "auto";
    svgClone.style.height = "auto";
    svgClone.style.transformOrigin = "center center";
    svgClone.style.transition = "transform 0.1s ease-out";
    svgClone.style.cursor = "grab";

    parts.container.appendChild(svgClone);
    document.body.appendChild(parts.overlay);

    // Trigger fade-in
    requestAnimationFrame(function () {
      parts.overlay.classList.add("mermaid-zoom-visible");
    });

    enablePanZoom(parts.container, svgClone);
    document.addEventListener("keydown", onKeyDown);
  }

  function init() {
    document.addEventListener("click", function (e) {
      var mermaidEl = e.target.closest(".mermaid");
      if (mermaidEl && mermaidEl.querySelector("svg")) {
        openDiagram(mermaidEl);
      }
    });

    // Add pointer cursor to all mermaid diagrams
    var style = document.createElement("style");
    style.textContent = ".mermaid { cursor: pointer; }";
    document.head.appendChild(style);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
