# 📊 หวย — สถิติย้อนหลัง & วิเคราะห์ (Lotto History Analytics)

A Thai-language, static web app that analyzes **Thai Government Lottery (สลากกินแบ่งรัฐบาล)
draw history**: frequency heatmaps, hot/cold numbers, overdue streaks, digit-position
distributions, trends, a number checker, and a full searchable history table.

It is the companion to the astro predictor from the previous session
(`lottery-astro-panchangam.html`) — same dark/gold look, but this app is about **real
historical results**, not predictions.

👉 On GitHub Pages: `https://red-seawolf.github.io/red-seawolf/lotto-history/`

## ✨ Features

- **เลขท้าย 2 ตัว** — 10×10 frequency heatmap (00–99) with click-through detail
  (appearance timeline, gaps), hot/cold top-10, overdue numbers, tens/units digit
  distributions, odd/even & high/low splits.
- **รางวัลที่ 1** — per-position digit frequency (6 small multiples), digit-sum
  distribution, most frequent last-2 of the first prize, unique-digit counts.
- **เลข 3 ตัว** — front-3 / back-3 digit analysis, sum distribution, exact repeats.
- **แนวโน้ม** — last-2 values over time with a 10-draw moving average, rolling even-%
  line, month × tens-digit heatmap, consecutive repeats & double numbers.
- **ตรวจเลข** — enter a 2-, 3-, or 6-digit number and see its complete history.
- **ตารางย้อนหลัง** — searchable, paginated table of every draw; every chart value is
  also readable here (accessibility twin). CSV/JSON export.
- One **filter row** (year range · month · draw day) scopes every chart and table.

## 🗃️ Where the data comes from

The app reads `data/draws.js` (`window.LOTTO_DRAWS`). Three ways it gets filled:

1. **GitHub Actions (primary).** `.github/workflows/update-lotto-data.yml` runs
   `scripts/fetch-lotto-data.mjs` daily (17:30 ICT) and after pipeline changes,
   fetching real results from the public
   [rayriffy lotto API](https://lotto.api.rayriffy.com) and committing the updated
   dataset. It only commits when new draws actually landed.
2. **In-browser sync.** The “🔄 ดึงผลจริง / อัปเดต” button fetches the same API from the
   visitor's browser and stores the merged dataset in `localStorage` — useful when the
   repo data is stale or while the repo still ships the sample dataset.
3. **Import.** Paste in a JSON/CSV export (schema below).

Until the workflow's first run lands, the repo ships a deterministic **random sample
dataset** clearly labeled `isSample: true`; the app shows a warning banner and treats
it as throwaway (it is discarded, never merged, the moment real data arrives).

### Draw record schema

```json
{
  "id": "2025-06-16",
  "date": "2025-06-16",
  "thaiDate": "16 มิถุนายน 2568",
  "first": "507392",
  "front3": ["371", "904"],
  "back3": ["112", "620"],
  "last2": "57"
}
```

`front3` exists only from August 2015 onward; before that draws carried four `back3`
numbers. CSV columns: `date,first,front3,back3,last2` with `|` separating multiple
3-digit numbers.

## 🛠️ Run locally

No build step. Serve the repo root with any static server:

```bash
python3 -m http.server 8000
# → http://localhost:8000/lotto-history/
```

Refresh the dataset manually:

```bash
node scripts/fetch-lotto-data.mjs            # incremental
FULL_SYNC=1 node scripts/fetch-lotto-data.mjs # refetch the whole archive
```

## ⚠️ Responsible use

Lottery draws are independent random events. Historical frequencies **cannot predict
future results**, and an "overdue" number is not "due" (the gambler's fallacy). This
app is for education and entertainment — please play responsibly.
