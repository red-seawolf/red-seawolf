// Demo adapter — serves bundled fixture data (no network). Lets the whole
// pipeline (search -> price-per-unit -> sort -> filter) be exercised even where
// the real marketplaces are blocked. Enable it explicitly via sites=demo.
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

export const meta = {
  id: 'demo',
  label: 'Demo (offline fixtures)',
  homepage: '',
};

let cached = null;
async function load() {
  if (!cached) {
    const path = fileURLToPath(new URL('../fixtures/demo.json', import.meta.url));
    cached = JSON.parse(await readFile(path, 'utf8'));
  }
  return cached;
}

export async function search(keyword, { limit = 40 } = {}) {
  const all = await load();
  const kw = String(keyword || '').toLowerCase().trim();
  const terms = kw.split(/\s+/).filter(Boolean);
  const matched = all.filter((p) => {
    if (!terms.length) return true;
    const hay = p.title.toLowerCase();
    return terms.some((t) => hay.includes(t));
  });
  return matched.slice(0, limit).map((p) => ({ ...p, currency: 'THB', flags: {} }));
}
