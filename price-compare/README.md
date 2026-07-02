# 🛒 TH Price Compare — Shopee & Lazada

A self-hostable **search engine + price comparison** tool for Thai marketplaces.
Search one keyword and get a merged, sortable list of products from
**Shopee (shopee.co.th)** and **Lazada (lazada.co.th)** — each with a computed
**price-per-unit**, a **seller-origin** filter (local/domestic vs overseas), and
a direct link to the product page. More sites can be plugged in later without
touching the rest of the app.

## Features

- **One search, all sites** — queries every enabled marketplace in parallel and
  shows a single result list.
- **Price-per-unit comparison** — parses the pack size and unit from each product
  title (e.g. `200g x 3`, `1L x 12`, `500 ml`, `50 pcs`, Thai units like `แพ็ค`,
  `ชิ้น`, `ขวด`) and normalizes to **฿/kg**, **฿/L**, or **฿/piece** so unequal
  pack sizes are actually comparable.
- **Sorting** — by price (↑/↓), by price-per-unit (↑/↓), or relevance.
- **Seller filters** — **Local / domestic (Thailand)** vs **Overseas /
  international**, derived from each listing's seller location / cross-border flag.
- **Product links** — every card links straight to the item on its marketplace.
- **Per-site status** — the UI shows which sources returned data and which were
  blocked, so a block on one site never hides the others.
- **Pluggable adapters** — add a new marketplace by dropping in one file.

## Quick start

```bash
cd price-compare
npm install
npm start
# open http://localhost:3000
```

Try the pipeline with **no network** by ticking the **Demo** site (bundled
fixture data) — useful for development or when the marketplaces are unreachable.

## How it works

```
web/ (static UI)  ──►  GET /api/search?q=…&sites=shopee,lazada
                          │
                    src/aggregator.js   run adapters in parallel, enrich, cache
                          │
        ┌─────────────────┼──────────────────┐
   adapters/shopee     adapters/lazada     adapters/demo
        │                  │
   headless Chromium (Playwright) → real browser context
        │                  │
   Shopee search API   Lazada SSR payload
   (fetched same-origin  (window.pageData
    from inside the page) .mods.listItems)
```

Each adapter returns raw products; `src/normalize.js` enriches every product
with `pricePerUnit`, `unit`, `packCount`, and `sellerOrigin`. Results are cached
in-memory for 5 minutes per (query, sites).

### On blocking (important)

Shopee and Lazada actively defend against automated access, and some networks
block them outright. This tool takes the most robust *non-abusive* approach
available:

- It drives a **real headless Chromium** (not raw HTTP), with a realistic
  user-agent, `th-TH` locale, Bangkok timezone, and the `navigator.webdriver`
  flag hidden — so requests look like a normal browser session.
- **Shopee**: it loads the site to obtain real cookies, then calls Shopee's own
  search API **from inside the page** (`fetch()` same-origin). This avoids CORS
  and request-signing entirely — the call is indistinguishable from the site's
  own XHR.
- **Lazada**: it reads the product list Lazada already embeds in the page
  (`window.pageData.mods.listItems`) — no private API needed.

If a site still challenges the request (CAPTCHA / bot page) or the network blocks
it, that source returns a clean error and the UI marks it *blocked/failed* while
still showing results from the other sites. Ways to improve success rate on your
own host:

- Run it from a **residential / Thai IP** (datacenter IPs are commonly blocked).
- Set `CHROMIUM_PATH` to a full Chrome build and consider `headless: false` on a
  desktop for the hardest cases.
- Increase the per-request timeout and add small delays between searches (the
  built-in cache already helps).

> ⚠️ This environment's egress policy blocks `shopee.co.th` and `lazada.co.th`, so
> the live adapters can't be demonstrated *here* — they're verified to fail
> gracefully, and the Demo source exercises the full pipeline. Run it on a machine
> that can reach the sites to get live data.

Respect each marketplace's Terms of Service and `robots.txt`, and keep request
volume low. This project is for personal price comparison, not bulk harvesting.

## Adding a new site (later)

Create `src/adapters/<site>.js` exporting:

```js
export const meta = { id: 'newsite', label: 'New Site', homepage: 'https://…' };
export async function search(keyword, { limit }) {
  // ...return an array of raw products (see the shape below)
}
```

Raw product shape consumed by the aggregator:

```js
{
  site, id, title, price, currency, image, url,
  seller, location, sold, rating,
  flags: { overseas?: boolean, domestic?: boolean }
}
```

Then register it in `src/adapters/index.js` and add a checkbox in
`web/index.html`. Nothing else changes — normalization, sorting, filtering and
price-per-unit come for free.

## API

- `GET /api/health` → `{ ok, sites }`
- `GET /api/sites` → available adapters
- `GET /api/search?q=<kw>&sites=shopee,lazada&limit=40` →
  `{ query, count, products[], sources[] }`
  - each `product` includes `price`, `pricePerUnit`, `pricePerUnitLabel`,
    `unit`, `packCount`, `sellerOrigin` (`local`/`overseas`/`unknown`), and `url`.
  - `sources[]` reports per-site `ok` / `error` / `count` / `ms`.

## Tests

```bash
npm test   # unit tests for the price-per-unit and seller-origin logic
```

## Configuration

See `.env.example` — `PORT`, `CHROMIUM_PATH`, `SCRAPER_UA` (all optional).
