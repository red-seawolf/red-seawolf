# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Thai Lottery 2-digit number predictor that combines Jean Meeus astronomical algorithms with Hindu/Thai astrology (Panchangam) and 35-year historical pattern analysis. The application predicts numbers for Thai lottery draws (1st & 16th of each month) using 25 astrological/calendrical variables.

**There is no build system.** The entire application is `lottery-astro-panchangam.html` — a single self-contained file with no external JS dependencies. To run it, open the file directly in a browser.

## Architecture

### Single-File Layout (`lottery-astro-panchangam.html`)

The `<script>` block (~800 lines) is organized in this execution order:

1. **Lookup tables / constants** — `THAI_KINGS`, `PATRIARCHS`, `PMS`, `NAKSHATRA`, `VAR_W`, `vcol`, `vcat`
2. **Math helpers** — `toRad`, `toDeg`, `norm360`
3. **Astronomical engine** — `julianDay()`, `sunPosition()`, `moonPosition()`, `allPlanets()`
4. **Sidereal / zodiac** — `lahiriAyanamsha()`, `getRasi()`, `getNakshatra()`
5. **Panchangam** — `getTithi()`, `getYoga()`, `getKarana()`, `getHora()`
6. **Person-tracking helpers** — `getKing()`, `getPatr()`, `getPM()`, `ageAt()`
7. **Record builder** — `buildRec(date)` — assembles all 25 variables for a given date
8. **History generation** — `HISTORY[]` array built on load (665 records, 1990–2024)
9. **Prediction engine** — `predict(tgt)`, `getConf(score, max)`
10. **Rendering functions** — `render()`, `renderSky()`, `render*Tab()`, `renderChart()`
11. **Event listeners & init**

### Prediction Data Flow

```
User selects draw date
        ↓
buildRec(targetDate)  →  25 variables for target
        ↓
predict(tgt):
  for each number 00–99:
    L1: Exact pattern match (NK+R2+A+C+F) × 7.0
    L2: Per-variable frequency matching (weighted by VAR_W)
    L3: Recent-draw match (last 60) on A+C+NK × 2.0
    L4: Drought boost if not seen in 30+ draws
    L5: Digit affinity within Nakshatra context
        ↓
Top 5 by score → confidence tiers (1–5 stars)
```

### The 25 Prediction Variables

Defined in `VAR_W` object. The most heavily weighted:

| Key | Description | Weight |
|-----|-------------|--------|
| `NK` | Moon Nakshatra (27 mansions, grouped by 3) | **2.4** |
| `A` | Moon cycle (waxing/waning) | 2.5 |
| `R2` | Moon phase cycle (0–8) | 2.2 |
| `T` | Tithi group (6 groups of 5) | 2.0 |
| `P2` | Jupiter Rasi | 2.0 |
| `C` | Weekday | 2.0 |

Variables `B`, `G`, `H` cover Chinese zodiac/lunar; `J`, `K_dec`, `L`, `M_dec`, `N`, `O_dec` encode the reigning Thai King, Supreme Patriarch, and Prime Minister at each historical draw date.

### Historical Data

`HISTORY` is generated in-memory using a pseudorandom seed (`rng(seed) = |sin(seed×9301+49297)×233280| % 1`) — it is **not** real Thai lottery data. The seed is derived from draw-date fields so it is deterministic.

### Hardcoded Constants

- Bangkok coordinates: `13.75°N, 100.52°E`, timezone offset `+7`
- Ayanamsha (Lahiri Chitrapaksha): `23.85144 + (T*100) * 0.013962`
- Draw schedule: 1st and 16th of each month

## Conventions

**Naming**: UPPERCASE for module-level constants (`THAI_KINGS`, `NAKSHATRA`, `HISTORY`), camelCase for functions and local variables. Short abbreviations are intentional: `tgt` (target record), `sv` (suriyayat/astrological object), `vd` (variable details), `rec` (history record).

**DOM updates**: All rendering is done via `innerHTML` assignment — no virtual DOM, no framework.

**Variable color/category**: The `vcol` object maps variable keys to CSS color strings; `vcat` maps them to category labels. Both must stay in sync when adding new variables.

**Adding a new prediction variable**: Update `VAR_W`, `vcol`, `vcat`, the `buildRec()` function, and the scoring loop inside `predict()`.

**Astronomical accuracy**: Moon position uses 13-term perturbation (Meeus 1998). Planet positions use simplified VSOP87 2-body with eccentricity. Do not replace these with simpler approximations without verifying output against known ephemeris values.
