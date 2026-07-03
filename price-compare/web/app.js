// Frontend for the two ways this app can run:
//
//  1. Self-hosted — the Node server (src/server.js) serves this UI and exposes
//     /api/search; live Shopee/Lazada scraping happens on the server.
//  2. Static web app (e.g. GitHub Pages) — there is no same-origin API, so:
//       - the Demo source runs entirely in the browser (fixtures + the same
//         normalize.js the server uses),
//       - Shopee/Lazada searches become direct marketplace links (their bot
//         defenses + CORS make in-browser scraping impossible),
//       - a self-hosted backend can be connected from the ⚙ panel to get live
//         merged results (the server sends CORS headers for this).
//
// Sorting and filtering always run client-side so changing controls is instant.
import { enrich } from '../src/normalize.js';

const BACKEND_KEY = 'th-price-compare.backend-url';

const form = document.getElementById('search-form');
const qInput = document.getElementById('q');
const btn = document.getElementById('search-btn');
const sortSel = document.getElementById('sort');
const sellerSel = document.getElementById('seller');
const statusEl = document.getElementById('status');
const sourcesEl = document.getElementById('sources');
const linkoutsEl = document.getElementById('linkouts');
const resultsEl = document.getElementById('results');
const emptyEl = document.getElementById('empty');
const modeEl = document.getElementById('mode');
const modeTextEl = document.getElementById('mode-text');
const settingsEl = document.getElementById('settings');
const backendInput = document.getElementById('backend-url');
const backendSaveBtn = document.getElementById('backend-save');
const backendClearBtn = document.getElementById('backend-clear');
const backendStatusEl = document.getElementById('backend-status');

let lastProducts = [];
let lastQuery = '';
// '' = same-origin API (self-hosted), 'https://…' = remote backend, null = static
let backend = null;

function selectedSites() {
  return [...document.querySelectorAll('input[name="site"]:checked')].map((c) => c.value);
}

const baht = (n) =>
  n == null ? '—' : '฿' + Number(n).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 });

// --- backend detection --------------------------------------------------------
async function probeBackend(base) {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 4000);
    const res = await fetch(`${base}/api/health`, { signal: ctrl.signal });
    clearTimeout(t);
    if (!res.ok) return false;
    const data = await res.json();
    return data?.ok === true;
  } catch {
    return false;
  }
}

async function initBackend() {
  const saved = (localStorage.getItem(BACKEND_KEY) || '').trim();
  if (saved) {
    backendInput.value = saved;
    if (await probeBackend(saved)) {
      backend = saved;
      updateModeUi();
      return;
    }
    setBackendStatus(`Saved backend ${saved} is not responding — running without it.`, false);
  }
  backend = (await probeBackend('')) ? '' : null;
  updateModeUi();
}

function updateModeUi() {
  if (backend === '') {
    // Self-hosted: the server is the backend, nothing to explain.
    modeEl.hidden = true;
    return;
  }
  modeEl.hidden = false;
  if (backend) {
    modeTextEl.textContent = `Live backend connected: ${backend}`;
    modeEl.classList.add('connected');
  } else {
    modeTextEl.textContent =
      'Running as a web app — Demo search works right here in your browser; Shopee/Lazada open as marketplace links. Connect a self-hosted backend for live merged results.';
    modeEl.classList.remove('connected');
  }
}

function setBackendStatus(msg, ok) {
  backendStatusEl.textContent = msg;
  backendStatusEl.classList.toggle('ok', ok === true);
  backendStatusEl.classList.toggle('err', ok === false);
}

backendSaveBtn.addEventListener('click', async () => {
  let url = backendInput.value.trim().replace(/\/+$/, '');
  if (!url) return setBackendStatus('Enter the URL of your self-hosted server first.', false);
  if (!/^https?:\/\//i.test(url)) url = `http://${url}`;
  backendInput.value = url;
  backendSaveBtn.disabled = true;
  setBackendStatus('Testing…', null);
  const ok = await probeBackend(url);
  backendSaveBtn.disabled = false;
  if (!ok) {
    setBackendStatus(
      'Could not reach the backend. Check the URL, that the server is running, and that this page is allowed to reach it (an https page cannot call an http backend).',
      false,
    );
    return;
  }
  localStorage.setItem(BACKEND_KEY, url);
  backend = url;
  setBackendStatus('Connected — live Shopee/Lazada searches now go through your backend.', true);
  updateModeUi();
});

backendClearBtn.addEventListener('click', async () => {
  localStorage.removeItem(BACKEND_KEY);
  backendInput.value = '';
  setBackendStatus('Backend removed.', null);
  backend = (await probeBackend('')) ? '' : null;
  updateModeUi();
});

// --- in-browser demo source (same behaviour as src/adapters/demo.js) ----------
let demoFixtures = null;
async function demoSearch(keyword, limit = 40) {
  if (!demoFixtures) {
    const res = await fetch(new URL('../src/fixtures/demo.json', import.meta.url));
    if (!res.ok) throw new Error(`fixtures HTTP ${res.status}`);
    demoFixtures = await res.json();
  }
  const terms = String(keyword || '').toLowerCase().trim().split(/\s+/).filter(Boolean);
  const matched = demoFixtures.filter((p) => {
    if (!terms.length) return true;
    const hay = p.title.toLowerCase();
    return terms.some((t) => hay.includes(t));
  });
  return matched.slice(0, limit).map((p) => ({ ...p, currency: 'THB', flags: {} }));
}

// --- direct marketplace links (static mode) ------------------------------------
function marketplaceUrl(site, q, sort) {
  const enc = encodeURIComponent(q);
  if (site === 'shopee') {
    let u = `https://shopee.co.th/search?keyword=${enc}`;
    if (sort === 'price-asc') u += '&sortBy=price&order=asc';
    else if (sort === 'price-desc') u += '&sortBy=price&order=desc';
    return u;
  }
  if (site === 'lazada') {
    let u = `https://www.lazada.co.th/catalog/?q=${enc}`;
    if (sort === 'price-asc') u += '&sort=priceasc';
    else if (sort === 'price-desc') u += '&sort=pricedesc';
    return u;
  }
  return null;
}

function renderLinkouts() {
  if (backend !== null || !lastQuery) {
    linkoutsEl.innerHTML = '';
    return;
  }
  const sort = sortSel.value;
  const sortNote =
    sort === 'price-asc' ? ' (price ↑)' : sort === 'price-desc' ? ' (price ↓)' : '';
  linkoutsEl.innerHTML = selectedSites()
    .filter((s) => s !== 'demo')
    .map((s) => {
      const url = marketplaceUrl(s, lastQuery, sort);
      if (!url) return '';
      return `<a class="linkout ${s}" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">
        Search “${escapeHtml(lastQuery)}” on ${s}${sortNote} ↗</a>`;
    })
    .join('');
}

// --- search --------------------------------------------------------------------
async function runSearch(e) {
  if (e) e.preventDefault();
  const q = qInput.value.trim();
  if (!q) return;
  const sites = selectedSites();
  if (!sites.length) {
    setStatus('Select at least one site.');
    return;
  }
  lastQuery = q;
  btn.disabled = true;
  resultsEl.innerHTML = '';
  sourcesEl.innerHTML = '';
  emptyEl.hidden = true;
  renderLinkouts();
  try {
    if (backend !== null) {
      setStatus('Searching ' + sites.join(', ') + '… (real marketplace scrapes can take 10–40s)');
      await apiSearch(q, sites);
    } else {
      await staticSearch(q, sites);
    }
  } catch (err) {
    setStatus('Error: ' + err.message);
  } finally {
    btn.disabled = false;
  }
}

async function apiSearch(q, sites) {
  const url = `${backend}/api/search?q=${encodeURIComponent(q)}&sites=${encodeURIComponent(sites.join(','))}`;
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  lastProducts = data.products || [];
  renderSources(data.sources || [], data.cached);
  render();
  setStatus(`${lastProducts.length} results for “${data.query}”.`);
}

async function staticSearch(q, sites) {
  const liveSites = sites.filter((s) => s !== 'demo');
  lastProducts = [];
  const sources = [];
  if (sites.includes('demo')) {
    setStatus('Searching demo data…');
    const started = performance.now();
    try {
      const raw = await demoSearch(q);
      lastProducts = raw.map(enrich);
      sources.push({ id: 'demo', ok: true, count: lastProducts.length, ms: Math.round(performance.now() - started) });
    } catch (err) {
      sources.push({ id: 'demo', ok: false, error: String(err.message || err) });
    }
  }
  renderSources(sources, false);
  render();
  const parts = [];
  if (sites.includes('demo')) parts.push(`${lastProducts.length} demo results`);
  if (liveSites.length) {
    parts.push(
      `for live ${liveSites.join('/')} prices use the link${liveSites.length > 1 ? 's' : ''} above or connect a backend (⚙ below)`,
    );
  }
  setStatus(parts.join(' — ') + '.');
}

function setStatus(msg) {
  statusEl.hidden = false;
  statusEl.textContent = msg;
}

function renderSources(sources, cached) {
  sourcesEl.innerHTML = sources
    .map((s) => {
      if (s.ok) return `<span class="chip ok">${s.id}: ${s.count} items · ${s.ms}ms</span>`;
      return `<span class="chip err" title="${escapeHtml(s.error || '')}">${s.id}: blocked/failed</span>`;
    })
    .join('') + (cached ? ' <span class="chip">cached</span>' : '');
}

function render() {
  let items = [...lastProducts];

  const seller = sellerSel.value;
  if (seller === 'local') items = items.filter((p) => p.isLocal === true);
  else if (seller === 'overseas') items = items.filter((p) => p.isLocal === false);

  const sort = sortSel.value;
  const cmp = {
    'price-asc': (a, b) => nn(a.price) - nn(b.price),
    'price-desc': (a, b) => nn(b.price) - nn(a.price),
    'ppu-asc': (a, b) => nn(a.pricePerUnit) - nn(b.pricePerUnit),
    'ppu-desc': (a, b) => nn(b.pricePerUnit) - nn(a.pricePerUnit),
  }[sort];
  if (cmp) items.sort(cmp);

  resultsEl.innerHTML = items.map(card).join('');
  emptyEl.hidden = items.length > 0 || (backend === null && lastQuery !== '');
}

// push nulls to the end for ascending, keep them low for descending
function nn(v) {
  return v == null || Number.isNaN(v) ? Number.POSITIVE_INFINITY : v;
}

function card(p) {
  const ppu = p.pricePerUnit != null
    ? `<div class="ppu">${baht(p.pricePerUnit)} ${p.pricePerUnitLabel || ''}${p.packCount > 1 ? ` · pack of ${p.packCount}` : ''}</div>`
    : `<div class="ppu unknown">unit price n/a</div>`;
  const originBadge =
    p.sellerOrigin === 'local'
      ? '<span class="badge local">local</span>'
      : p.sellerOrigin === 'overseas'
      ? '<span class="badge overseas">overseas</span>'
      : '<span class="badge unknown">origin ?</span>';
  const img = p.image
    ? `<img src="${escapeHtml(p.image)}" alt="" loading="lazy" onerror="this.style.display='none'" />`
    : '';
  return `
  <article class="card">
    <div class="thumb">${img}</div>
    <div class="body">
      <div class="title" title="${escapeHtml(p.title)}">${escapeHtml(p.title)}</div>
      <div class="price">${baht(p.price)}</div>
      ${ppu}
      <div class="meta">
        <span class="badge ${p.site}">${p.site}</span>
        ${originBadge}
        ${p.location ? `<span>${escapeHtml(p.location)}</span>` : ''}
        ${p.sold != null ? `<span>${p.sold.toLocaleString()} sold</span>` : ''}
      </div>
      <a class="buy" href="${escapeHtml(p.url || '#')}" target="_blank" rel="noopener noreferrer">View on ${p.site} ↗</a>
    </div>
  </article>`;
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]),
  );
}

form.addEventListener('submit', runSearch);
sortSel.addEventListener('change', () => {
  render();
  renderLinkouts();
});
sellerSel.addEventListener('change', render);
modeEl.addEventListener('click', (e) => {
  if (e.target.closest('a')) return;
  settingsEl.open = true;
  settingsEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
});

// --- boot ----------------------------------------------------------------------
initBackend().then(() => {
  // With no backend, tick Demo so a first search shows something immediately.
  if (backend === null) {
    const demoBox = document.querySelector('input[name="site"][value="demo"]');
    if (demoBox) demoBox.checked = true;
  }
});

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register(new URL('./sw.js', import.meta.url)).catch(() => {});
}
