// Adapter registry. To add a new marketplace later, create a module that
// exports `meta` ({ id, label, homepage }) and `search(keyword, opts)` returning
// an array of raw products, then register it here — nothing else changes.
import * as shopee from './shopee.js';
import * as lazada from './lazada.js';
import * as demo from './demo.js';

const ADAPTERS = new Map();

function register(mod) {
  ADAPTERS.set(mod.meta.id, mod);
}

register(shopee);
register(lazada);
register(demo);

export function getAdapter(id) {
  return ADAPTERS.get(id) || null;
}

export function listAdapters() {
  return [...ADAPTERS.values()].map((m) => ({ ...m.meta }));
}

// Sites hit by default when the client doesn't specify any.
export const DEFAULT_SITES = ['shopee', 'lazada'];
