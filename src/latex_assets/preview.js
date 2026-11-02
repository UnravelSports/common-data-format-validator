// Preview buttons on the LaTeX pages: swap a block's source for its rendered PDF.
//
// Copied into docs/latest/latex/ by src/generate_latex.py. Edit it here.
//
// The PDF is drawn into the page with PDF.js, loaded on the first click so a
// page read only for its source never fetches it. PDF.js is served from this
// site rather than a CDN, so no third party can change the code that runs on
// it. docs/latest/latex/pdfjs/ holds pdfjs-dist 3.11.174 from the npm registry,
// checked against the registry's sha512 and against cdnjs's copy; to upgrade,
// replace both .min.js files and LICENSE from a newer pdfjs-dist. The PDFs are
// one very tall page each -- standalone.tex lengthens the page so a long table
// never spills onto a second -- so the page is drawn twice: once small to find
// where the ink is, then at full resolution cropped to that box. Drawing the
// whole page at full resolution would exceed the canvas size iOS Safari allows
// (about 16.7 million pixels).
(function () {
  "use strict";

  var PDFJS = "pdfjs/";
  // standalone.tex sets 15mm margins, so this is the paper's text width in PDF
  // points once subtracted from the page width. Scaling every preview so that
  // the text width, padded, fills the block -- rather than by its own content
  // -- keeps type the same size across blocks, as it is in the paper.
  var MARGIN_PT = (15 / 25.4) * 72;
  var PROBE_SCALE = 0.5;
  var PAD_PT = 6;

  var loading = null;

  function loadPdfjs() {
    if (!loading) {
      loading = new Promise(function (resolve, reject) {
        var script = document.createElement("script");
        script.src = PDFJS + "pdf.min.js";
        script.onload = function () {
          window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS + "pdf.worker.min.js";
          resolve(window.pdfjsLib);
        };
        script.onerror = function () {
          loading = null;
          reject(new Error("PDF.js could not be loaded"));
        };
        document.head.appendChild(script);
      });
    }
    return loading;
  }

  // Smallest box, in canvas pixels, holding every pixel that is not white.
  // The listing background (lightgray!20) is light, so the threshold sits just
  // above it to keep the listing frame inside the box.
  function inkBox(canvas) {
    var data = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height).data;
    var x0 = canvas.width, y0 = canvas.height, x1 = -1, y1 = -1;
    for (var y = 0; y < canvas.height; y++) {
      for (var x = 0; x < canvas.width; x++) {
        var i = (y * canvas.width + x) * 4;
        if (data[i + 3] > 10 && (data[i] < 248 || data[i + 1] < 248 || data[i + 2] < 248)) {
          if (x < x0) x0 = x;
          if (x > x1) x1 = x;
          if (y < y0) y0 = y;
          if (y > y1) y1 = y;
        }
      }
    }
    return x1 < 0 ? null : { x0: x0, y0: y0, x1: x1 + 1, y1: y1 + 1 };
  }

  // `width` is the CSS width to fill. It is measured by the caller before
  // anything is hidden: a hidden target reads as 0 wide, which once drew an
  // empty canvas that every later click then reused.
  async function render(url, target, width, label) {
    var pdfjs = await loadPdfjs();
    // isEvalSupported: false stops PDF.js turning a PDF's font data into
    // JavaScript, the code path CVE-2024-4367 abuses in versions up to 4.1.392.
    var task = pdfjs.getDocument({ url: url, isEvalSupported: false });
    try {
      var canvas = await draw(await task.promise, width);
      canvas.setAttribute("role", "img");
      canvas.setAttribute("aria-label", label);
      target.replaceChildren(canvas);
    } finally {
      // Ends the PDF.js worker thread, which otherwise stays alive for each
      // preview. Destroying the loading task rather than the document also
      // ends it when the PDF fails to load. The canvas keeps its pixels.
      task.destroy();
    }
  }

  async function draw(doc, width) {
    var page = await doc.getPage(1);

    var probeViewport = page.getViewport({ scale: PROBE_SCALE });
    var probe = document.createElement("canvas");
    probe.width = Math.ceil(probeViewport.width);
    probe.height = Math.ceil(probeViewport.height);
    await page.render({ canvasContext: probe.getContext("2d"), viewport: probeViewport }).promise;
    var box = inkBox(probe);
    if (!box) throw new Error("the PDF page is blank");

    // The box in PDF points, padded and kept on the page.
    var page1 = page.getViewport({ scale: 1 });
    var x0 = Math.max(0, box.x0 / PROBE_SCALE - PAD_PT);
    var y0 = Math.max(0, box.y0 / PROBE_SCALE - PAD_PT);
    var x1 = Math.min(page1.width, box.x1 / PROBE_SCALE + PAD_PT);
    var y1 = Math.min(page1.height, box.y1 / PROBE_SCALE + PAD_PT);

    var cssScale = width / (page1.width - 2 * MARGIN_PT + 2 * PAD_PT);
    var scale = cssScale * Math.min(window.devicePixelRatio || 1, 2);
    var viewport = page.getViewport({ scale: scale, offsetX: -x0 * scale, offsetY: -y0 * scale });
    var canvas = document.createElement("canvas");
    canvas.width = Math.ceil((x1 - x0) * scale);
    canvas.height = Math.ceil((y1 - y0) * scale);
    canvas.style.width = Math.round((x1 - x0) * cssScale) + "px";
    await page.render({ canvasContext: canvas.getContext("2d"), viewport: viewport }).promise;
    return canvas;
  }

  // Width of the block's content area, where the preview goes: the block minus
  // the .render padding. The block itself is never hidden, so this is never 0.
  function contentWidth(block, target) {
    var style = getComputedStyle(target);
    return block.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
  }

  // Screen readers read the page's status line aloud when its text changes;
  // the visible "Rendering…" and button text alone are never announced.
  function announce(text) {
    var status = document.getElementById("preview-status");
    if (status) status.textContent = text;
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("button.preview");
    if (!button) return;
    var block = button.closest(".table-block");
    var source = block.querySelector("pre");
    var shown = block.querySelector(".render");
    var name = button.dataset.pdf.replace(/\.pdf$/, "");

    if (shown && !shown.hidden) {
      shown.hidden = true;
      source.hidden = false;
      button.textContent = "Preview";
      announce("Showing the LaTeX source of " + name);
      return;
    }
    source.hidden = true;
    button.textContent = "Source";
    button.classList.remove("failed");
    if (shown) {
      shown.hidden = false;
      announce("Showing the rendered " + name);
      return;
    }
    shown = document.createElement("div");
    shown.className = "render";
    shown.textContent = "Rendering…";
    block.appendChild(shown);
    announce("Rendering " + name);
    var label = "Rendered " + name + "; the Source button shows its LaTeX as text";
    render(button.dataset.pdf, shown, contentWidth(block, shown), label).then(function () {
      announce("Showing the rendered " + name);
    }, function (err) {
      // A failed render is not cached, so the next click tries again.
      shown.remove();
      source.hidden = false;
      // The reason goes to the console only; the page just says it failed.
      // Opened from disk (file://), browsers block the PDF fetch, so serve
      // docs/ over HTTP to preview locally.
      window.console.error("Preview failed for " + button.dataset.pdf, err);
      button.textContent = "Preview failed";
      button.classList.add("failed");
      announce("Preview of " + name + " failed");
    });
  });
})();
