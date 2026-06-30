# 📷 Multi-QR Extractor — rev.2

A privacy-first web app that **extracts every QR code from a photo** — even when one picture is
packed with many codes — and now **scans several photos in one batch**. Everything runs in your
browser; no image is ever uploaded to a server.

👉 **Live app:** once GitHub Pages is enabled, it will be available at
`https://red-seawolf.github.io/red-seawolf/`

## 🆕 What's new in rev.2

- **Tuned for 5–8 QR codes in one photo.** A new multi-pass, tiled scan combines a full-image pass
  with overlapping tile passes (upscaling small/dense tiles), then de-duplicates by value and
  position — so a densely-packed sheet of codes gets read reliably instead of returning just a few.
- **Add multiple photos.** Queue several pictures (drag & drop, file picker — now multi-select —
  camera, or paste), see thumbnails, remove any you don't want, then **Scan** them all at once.
  Add more and re-scan any time.
- **Per-photo results + combined export.** Each photo gets its own outlined preview and decoded
  list; JSON/CSV/Copy-all now span every photo and include a `photo` column.

## ✨ Features

- **Multiple QR codes per photo** — decodes all of them (most scanners only find one).
- **Batch of photos** — add and scan many images in a single pass.
- **Several ways to add images** — drag & drop, file picker (multi-select), device camera, or paste.
- **Visual overlay** — each detected code is outlined and numbered on its source image.
- **Smart values** — links become clickable; copy any single value or all at once.
- **Export** — download results as **JSON** or **CSV** (with a per-photo column).
- **Works offline** after the first load, and on phones (camera capture supported).
- **Extra formats** — also reads Micro QR, rMQR, Aztec, Data Matrix and PDF417.

## 🛠️ How it works

The app uses the [`barcode-detector`](https://github.com/Sec-ant/barcode-detector) ponyfill,
which is powered by [ZXing-WASM](https://github.com/Sec-ant/zxing-wasm). `BarcodeDetector.detect()`
returns **an array of every code found** in an image, with bounding boxes and corner points.

To reliably surface **5–8 codes from one photo**, rev.2 doesn't rely on a single pass: it runs the
detector on the whole image *and* on a grid of overlapping tiles (upscaling smaller tiles so dense
codes have enough pixels to decode), then merges the hits, de-duplicating by decoded value and
on-image position.

There is **no build step**. `index.html` is a single, self-contained static page; the detector and
its WebAssembly binary are vendored in `vendor/`, so it loads with no CDN and works offline.

## 🚀 Run locally

Because it loads an ES module from a CDN, open it through any static server (not `file://`):

```bash
# Python
python3 -m http.server 8000
# then visit http://localhost:8000

# …or Node
npx serve .
```

## 🌐 Deploy (GitHub Pages)

A workflow at `.github/workflows/deploy-pages.yml` publishes the site automatically.

1. Merge this branch into `main`.
2. In the repository, go to **Settings → Pages → Build and deployment** and set
   **Source = GitHub Actions**.
3. Every push to `main` then deploys the latest version.

## 🔒 Privacy

All decoding happens locally in your browser using WebAssembly. The image never leaves your device.

---

QR Code is a registered trademark of DENSO WAVE INCORPORATED.
