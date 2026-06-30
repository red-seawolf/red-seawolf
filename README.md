# 📷 Multi-QR Extractor

A privacy-first web app that **extracts every QR code from a single photo** — even when one
picture contains many codes at once. Everything runs in your browser; no image is ever uploaded
to a server.

👉 **Live app:** once GitHub Pages is enabled, it will be available at
`https://red-seawolf.github.io/red-seawolf/`

## ✨ Features

- **Multiple QR codes per photo** — decodes all of them in one pass (most scanners only find one).
- **Several ways to add an image** — drag & drop, file picker, device camera, or paste from clipboard.
- **Visual overlay** — each detected code is outlined and numbered on the source image.
- **Smart values** — links become clickable; copy any single value or all at once.
- **Export** — download results as **JSON** or **CSV**.
- **Works offline** after the first load, and on phones (camera capture supported).
- **Extra formats** — also reads Micro QR, rMQR, Aztec, Data Matrix and PDF417.

## 🛠️ How it works

The app uses the [`barcode-detector`](https://github.com/Sec-ant/barcode-detector) ponyfill,
which is powered by [ZXing-WASM](https://github.com/Sec-ant/zxing-wasm). Unlike single-shot
libraries (e.g. `jsQR`), `BarcodeDetector.detect()` returns **an array of every code found** in the
image, with bounding boxes and corner points — which is exactly what's needed to pull multiple QR
codes out of one photo.

There is **no build step**. `index.html` is a single, self-contained static page that loads the
detector from a CDN as an ES module.

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
