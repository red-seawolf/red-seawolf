// Lazada (lazada.co.th) adapter.
//
// Strategy: load the catalog search page and read the product list that Lazada
// embeds in the page as `window.pageData` (its SSR payload). This avoids any
// signed-API reverse engineering; we just read what the page already ships.
import { newContext } from '../browser.js';

export const meta = {
  id: 'lazada',
  label: 'Lazada',
  homepage: 'https://www.lazada.co.th',
};

export async function search(keyword, { limit = 40, timeoutMs = 45000 } = {}) {
  const context = await newContext();
  const page = await context.newPage();
  try {
    const url = `https://www.lazada.co.th/catalog/?q=${encodeURIComponent(keyword)}&page=1`;
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    // Lazada hydrates listItems into window.pageData; wait for it (or a fallback).
    await page
      .waitForFunction(
        () => window.pageData?.mods?.listItems?.length > 0,
        { timeout: 12000 },
      )
      .catch(() => {});

    const items = await page.evaluate(() => {
      const list = window.pageData?.mods?.listItems;
      return Array.isArray(list) ? list : [];
    });

    if (!items.length) {
      // Second attempt: some regions return data via an inline JSON blob.
      const blob = await page.evaluate(() => {
        const m = document.body.innerHTML.match(/"listItems":(\[.*?\]),"seoInfo"/s);
        if (!m) return [];
        try { return JSON.parse(m[1]); } catch { return []; }
      });
      if (!blob.length) {
        throw new Error('Lazada: no listItems found (likely a bot challenge or empty result)');
      }
      return blob.slice(0, limit).map(mapItem).filter(Boolean);
    }

    return items.slice(0, limit).map(mapItem).filter(Boolean);
  } finally {
    await context.close().catch(() => {});
  }
}

function mapItem(it) {
  if (!it) return null;
  const price = it.price != null ? parseFloat(String(it.price).replace(/,/g, '')) : null;
  let url = it.itemUrl || it.productUrl || '';
  if (url.startsWith('//')) url = 'https:' + url;
  else if (url.startsWith('/')) url = 'https://www.lazada.co.th' + url;
  let image = it.image || it.images?.[0] || null;
  if (image && image.startsWith('//')) image = 'https:' + image;
  return {
    site: 'lazada',
    id: String(it.nid || it.itemId || it.sku || ''),
    title: it.name || '',
    price: Number.isFinite(price) ? price : null,
    currency: 'THB',
    image,
    url: url || null,
    seller: it.sellerName || it.brandName || null,
    location: it.location || null,
    sold: parseSold(it.itemSoldCntShow || it.soldCount),
    rating: it.ratingScore ? parseFloat(it.ratingScore) : null,
    flags: {
      overseas: /overseas|abroad|china|cross|ต่างประเทศ|จีน/i.test(it.location || ''),
    },
  };
}

function parseSold(s) {
  if (s == null) return null;
  const m = String(s).match(/([\d.]+)\s*([kK]?)/);
  if (!m) return null;
  let n = parseFloat(m[1]);
  if (m[2]) n *= 1000;
  return Math.round(n);
}
