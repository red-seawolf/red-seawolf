# 📷 Multi-QR Extractor — rev.3

A privacy-first web app that **extracts every QR code from a photo** — even when one picture is
packed with many codes — **scans several photos in one batch**, and now **pulls the bare code out
of QR codes that wrap it inside a link**. Everything runs in your browser; no image is ever
uploaded to a server.

👉 **Live app:** https://red-seawolf.github.io/red-seawolf/

## 🆕 What's new in rev.3

- **Code extraction.** Many QR codes don't contain a plain code — they wrap it inside a URL. For
  example a LINE messaging QR encodes `https://line.me/R/oaMessage/%40viffc/?397GTN1P9FVM04KHMNREKFY8`,
  where the code you actually want is `397GTN1P9FVM04KHMNREKFY8`. The app now detects this pattern
  (and the general case of a URL whose query is a single bare token), shows the **bare code** up
  front with a **Copy code** button, and keeps the full scanned URL behind a “Show full QR value”
  toggle.
- **Exports include the code.** “Copy codes” copies the extracted codes (one per line); JSON and
  CSV now carry both a `code` and the original `value` column.

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

Because it loads ES modules, open it through any static server (not `file://`):

```bash
# Python
python3 -m http.server 8000
# then visit http://localhost:8000

# …or Node
npx serve .
```

## 🌐 Deploy (GitHub Pages)

The site is published straight from the `main` branch — no build step, no workflow:

- **Settings → Pages → Build and deployment → Source = “Deploy from a branch”**,
  branch `main`, folder `/ (root)`.
- Every push to `main` republishes the site automatically.
- A `.nojekyll` file at the root makes Pages serve the `vendor/` assets untouched.

## 🔒 Privacy

All decoding happens locally in your browser using WebAssembly. The image never leaves your device.

## 🛒 Also in this repo: TH Price Compare

A second web app lives at [`price-compare/`](price-compare/) — search Shopee & Lazada Thailand
at once and compare by price and **price per unit**. On GitHub Pages it runs at
`https://red-seawolf.github.io/red-seawolf/price-compare/` as an installable, offline-capable
PWA (demo search + marketplace deep links), and it can connect to a
[self-hosted backend](price-compare/README.md) for live scraped results.

---

QR Code is a registered trademark of DENSO WAVE INCORPORATED.
