// Core normalization: parse pack size / unit from a product title and derive a
// comparable "price per unit", and classify a seller as domestic vs overseas.
//
// Everything here is pure and dependency-free so it can be unit-tested offline
// and reused by any adapter.

// --- unit tables --------------------------------------------------------------
// Each unit maps to a canonical dimension and a factor into that dimension's
// base unit (ml for volume, g for weight, 1 for count).
const UNIT_TABLE = [
  // volume -> base ml
  { re: /(milliliters?|millilitres?|ml|มล|มิลลิลิตร|ซีซี|cc)\b/i, dim: 'volume', factor: 1 },
  { re: /(liters?|litres?|l|ลิตร)\b/i, dim: 'volume', factor: 1000 },
  // weight -> base g
  { re: /(kilograms?|kgs?|กก|กิโลกรัม|กิโล)\b/i, dim: 'weight', factor: 1000 },
  { re: /(milligrams?|mg|มก|มิลลิกรัม)\b/i, dim: 'weight', factor: 0.001 },
  { re: /(grams?|gr|g|ก|กรัม)\b/i, dim: 'weight', factor: 1 },
  // count -> base piece
  { re: /(capsules?|caps?|tablets?|tabs?|เม็ด|แคปซูล)\b/i, dim: 'count', factor: 1 },
  { re: /(pieces?|pcs?|pc|ชิ้น|อัน|ใบ|ขวด|กล่อง|ซอง|แผง|หลอด|ห่อ|ถุง|กระปุก|แท่ง)\b/i, dim: 'count', factor: 1 },
];

// How each dimension is displayed once we have a total in its base unit.
const DIMENSION_DISPLAY = {
  volume: { label: 'L', divisor: 1000, per: 'per L' },
  weight: { label: 'kg', divisor: 1000, per: 'per kg' },
  count: { label: 'pc', divisor: 1, per: 'per piece' },
};

const NUM = '(\\d+(?:[.,]\\d+)?)';

function toNumber(raw) {
  if (raw == null) return NaN;
  // handle "1,5" (comma decimal) and "1,500" (thousands) — favour decimal when
  // there are 1-2 digits after the comma, thousands otherwise.
  const s = String(raw).trim();
  if (/^\d+,\d{1,2}$/.test(s)) return parseFloat(s.replace(',', '.'));
  return parseFloat(s.replace(/,/g, ''));
}

/**
 * Detect a "pack of N" multiplier from a title, e.g. "x3", "3 pack",
 * "แพ็ค 6", "set of 4", "(2 ชิ้น)".
 * Returns an integer >= 1.
 */
export function parsePackCount(title = '') {
  const t = ` ${title} `;
  // Note: \b does not form a boundary next to Thai characters (they are
  // "non-word" to the regex engine), so the Thai keywords are matched without
  // relying on word boundaries.
  const patterns = [
    new RegExp(`[x×]\\s*${NUM}\\b`, 'i'),
    new RegExp(`\\b${NUM}\\s*[x×]`, 'i'),
    new RegExp(`${NUM}\\s*(?:packs?|แพ็ค|แพ็ก|แพค)`, 'i'),
    new RegExp(`(?:pack|packs|แพ็ค|แพ็ก|แพค|set of|เซ็ต)\\s*${NUM}`, 'i'),
  ];
  for (const re of patterns) {
    const m = t.match(re);
    if (m) {
      const n = Math.round(toNumber(m[1]));
      if (Number.isFinite(n) && n >= 1 && n <= 999) return n;
    }
  }
  return 1;
}

/**
 * Parse the primary size token (quantity + unit) from a title.
 * Returns { dim, baseQty } where baseQty is in the dimension's base unit,
 * or null when nothing recognisable is found.
 */
export function parseSize(title = '') {
  const t = ` ${title} `;
  let best = null;
  for (const u of UNIT_TABLE) {
    // number immediately (optionally with a space) before the unit token
    const re = new RegExp(`${NUM}\\s*${u.re.source}`, 'i');
    const m = t.match(re);
    if (!m) continue;
    const qty = toNumber(m[1]);
    if (!Number.isFinite(qty) || qty <= 0) continue;
    const baseQty = qty * u.factor;
    // Prefer volume/weight over a bare count, and larger explicit sizes over
    // tiny incidental numbers; keep the first strong match otherwise.
    if (!best || (best.dim === 'count' && u.dim !== 'count')) {
      best = { dim: u.dim, baseQty };
    }
  }
  return best;
}

/**
 * Given a title and a price, compute a comparable price-per-unit.
 * Returns { pricePerUnit, unitLabel, unitPer, totalQty, dim } or a null-ish
 * object when the size can't be parsed.
 */
export function pricePerUnit(title, price) {
  const size = parseSize(title);
  const pack = parsePackCount(title);
  if (!size || !Number.isFinite(price) || price <= 0) {
    return { pricePerUnit: null, unitLabel: null, unitPer: null, totalQty: null, dim: null, pack };
  }
  const totalBase = size.baseQty * pack; // in ml / g / pieces
  const disp = DIMENSION_DISPLAY[size.dim];
  const totalQty = totalBase / disp.divisor; // in L / kg / pieces
  if (!Number.isFinite(totalQty) || totalQty <= 0) {
    return { pricePerUnit: null, unitLabel: null, unitPer: null, totalQty: null, dim: null, pack };
  }
  return {
    pricePerUnit: price / totalQty,
    unitLabel: disp.label,
    unitPer: disp.per,
    totalQty,
    dim: size.dim,
    pack,
  };
}

// --- seller origin -----------------------------------------------------------
const OVERSEAS_RE = /(overseas|oversea|cross[\s-]?border|international|from abroad|abroad|mainland|ต่างประเทศ|จีน|china|hong ?kong|singapore|malaysia|shenzhen|guangzhou)/i;
// Common Thai province / city hints that clearly mark a domestic seller.
const THAI_RE = /(thailand|ไทย|ประเทศไทย|bangkok|กรุงเทพ|nonthaburi|นนทบุรี|samut|สมุทร|chiang ?mai|เชียงใหม่|chonburi|ชลบุรี|pathum|ปทุม|nakhon|นครราชสีมา|khon ?kaen|ขอนแก่น|phuket|ภูเก็ต|rayong|ระยอง|songkhla|สงขลา|surat|สุราษฎร์|ayutthaya|อยุธยา)/i;

/**
 * Classify a seller as domestic (local, ships from within Thailand) or
 * overseas (cross-border). Returns true (local), false (overseas), or null
 * when it can't be determined.
 */
export function classifySeller({ location = '', flags = {} } = {}) {
  if (flags.overseas === true) return false;
  if (flags.domestic === true) return true;
  const loc = String(location || '');
  if (OVERSEAS_RE.test(loc)) return false;
  if (THAI_RE.test(loc)) return true;
  if (loc.trim()) return true; // a concrete non-overseas location is treated as local
  return null;
}

/**
 * Take a raw product from an adapter and enrich it with derived fields.
 * Raw product shape (per adapter contract):
 *   { site, id, title, price, currency, image, url, seller, location, sold, rating, flags }
 */
export function enrich(raw) {
  const price = Number(raw.price);
  const ppu = pricePerUnit(raw.title || '', price);
  const isLocal = classifySeller({ location: raw.location, flags: raw.flags });
  return {
    site: raw.site,
    id: String(raw.id ?? ''),
    title: raw.title || '',
    price: Number.isFinite(price) ? price : null,
    currency: raw.currency || 'THB',
    image: raw.image || null,
    url: raw.url || null,
    seller: raw.seller || null,
    location: raw.location || null,
    sold: raw.sold ?? null,
    rating: raw.rating ?? null,
    isLocal, // true = domestic/local, false = overseas, null = unknown
    sellerOrigin: isLocal === true ? 'local' : isLocal === false ? 'overseas' : 'unknown',
    pricePerUnit: ppu.pricePerUnit,
    pricePerUnitLabel: ppu.unitPer, // e.g. "per L"
    unit: ppu.unitLabel, // e.g. "L"
    packCount: ppu.pack,
    totalQty: ppu.totalQty,
  };
}
