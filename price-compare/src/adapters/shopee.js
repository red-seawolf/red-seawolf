// Shopee (shopee.co.th) adapter.
//
// Strategy: open a real Shopee page to obtain cookies + a same-origin context,
// then call Shopee's own search API (/api/v4/search/search_items) from inside
// the page with fetch(). Doing it same-origin sidesteps CORS and makes the
// request look like the site's own XHR, which is the most reliable way past
// Shopee's anti-bot layer without reverse-engineering their request signing.
import { newContext } from '../browser.js';

const PRICE_DIVISOR = 100000; // Shopee prices are in micro-units

export const meta = {
  id: 'shopee',
  label: 'Shopee',
  homepage: 'https://shopee.co.th',
};

export async function search(keyword, { limit = 40, timeoutMs = 45000 } = {}) {
  const context = await newContext();
  const page = await context.newPage();
  try {
    await page.goto('https://shopee.co.th/', {
      waitUntil: 'domcontentloaded',
      timeout: timeoutMs,
    });
    // Give anti-bot cookies a moment to settle.
    await page.waitForTimeout(1200);

    const apiUrl =
      `/api/v4/search/search_items?by=relevancy&keyword=${encodeURIComponent(keyword)}` +
      `&limit=${limit}&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2`;

    const data = await page.evaluate(async (url) => {
      const res = await fetch(url, {
        headers: {
          'x-api-source': 'pc',
          'x-shopee-language': 'th',
          'x-requested-with': 'XMLHttpRequest',
        },
        credentials: 'include',
      });
      if (!res.ok) return { __error: `HTTP ${res.status}` };
      try {
        return await res.json();
      } catch {
        return { __error: 'non-JSON response (likely a bot challenge page)' };
      }
    }, apiUrl);

    if (data?.__error) throw new Error(`Shopee API: ${data.__error}`);

    const items = Array.isArray(data?.items) ? data.items : [];
    return items
      .map((it) => mapItem(it))
      .filter(Boolean);
  } finally {
    await context.close().catch(() => {});
  }
}

function mapItem(it) {
  const b = it?.item_basic || it;
  if (!b || b.itemid == null || b.shopid == null) return null;
  const priceRaw = b.price ?? b.price_min ?? b.price_max;
  const price = priceRaw != null ? priceRaw / PRICE_DIVISOR : null;
  const image = b.image
    ? `https://cf.shopee.co.th/file/${b.image}`
    : null;
  const slug = String(b.name || 'product')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-ก-๙]/g, '')
    .slice(0, 80);
  return {
    site: 'shopee',
    id: `${b.shopid}.${b.itemid}`,
    title: b.name || '',
    price,
    currency: b.currency || 'THB',
    image,
    url: `https://shopee.co.th/${slug}-i.${b.shopid}.${b.itemid}`,
    seller: b.shop_name || null,
    location: b.shop_location || null,
    sold: b.historical_sold ?? b.sold ?? null,
    rating: b.item_rating?.rating_star ?? null,
    flags: {
      // Shopee marks cross-border items; treat a non-TH shop_location as overseas.
      overseas: /overseas|china|cross|ต่างประเทศ|จีน/i.test(b.shop_location || ''),
    },
  };
}
