// Runs the selected site adapters in parallel, enriches every product with
// price-per-unit and seller-origin, and returns a merged result plus per-site
// status so the UI can show which sources succeeded or were blocked.
import { getAdapter, DEFAULT_SITES } from './adapters/index.js';
import { enrich } from './normalize.js';
import { cacheGet, cacheSet } from './cache.js';

export async function aggregateSearch(keyword, { sites, limit = 40 } = {}) {
  const chosen = (sites && sites.length ? sites : DEFAULT_SITES).filter((id) => getAdapter(id));
  const cacheKey = `search:${keyword}:${chosen.join(',')}:${limit}`;
  const cached = cacheGet(cacheKey);
  if (cached) return { ...cached, cached: true };

  const settled = await Promise.allSettled(
    chosen.map(async (id) => {
      const adapter = getAdapter(id);
      const started = Date.now();
      try {
        const raw = await adapter.search(keyword, { limit });
        return {
          id,
          ok: true,
          count: raw.length,
          ms: Date.now() - started,
          products: raw.map(enrich),
        };
      } catch (err) {
        return { id, ok: false, error: String(err.message || err), ms: Date.now() - started, products: [] };
      }
    }),
  );

  const sources = settled.map((s) =>
    s.status === 'fulfilled' ? s.value : { ok: false, error: String(s.reason) },
  );
  const products = sources.flatMap((s) => s.products || []);

  const result = {
    query: keyword,
    count: products.length,
    products,
    sources: sources.map(({ products: _p, ...rest }) => rest),
    cached: false,
  };
  cacheSet(cacheKey, result);
  return result;
}
