// Tiny in-memory TTL cache so repeated searches don't re-hit the marketplaces
// (which also reduces the chance of tripping anti-bot rate limits).
const store = new Map();

export function cacheGet(key) {
  const hit = store.get(key);
  if (!hit) return null;
  if (Date.now() > hit.expires) {
    store.delete(key);
    return null;
  }
  return hit.value;
}

export function cacheSet(key, value, ttlMs = 5 * 60 * 1000) {
  store.set(key, { value, expires: Date.now() + ttlMs });
  // opportunistic cleanup
  if (store.size > 500) {
    const now = Date.now();
    for (const [k, v] of store) if (now > v.expires) store.delete(k);
  }
}
