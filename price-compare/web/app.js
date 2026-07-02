// Frontend: calls /api/search, then sorts + filters client-side so changing the
// sort/seller controls is instant (no re-fetch).
const form = document.getElementById('search-form');
const qInput = document.getElementById('q');
const btn = document.getElementById('search-btn');
const sortSel = document.getElementById('sort');
const sellerSel = document.getElementById('seller');
const statusEl = document.getElementById('status');
const sourcesEl = document.getElementById('sources');
const resultsEl = document.getElementById('results');
const emptyEl = document.getElementById('empty');

let lastProducts = [];

function selectedSites() {
  return [...document.querySelectorAll('input[name="site"]:checked')].map((c) => c.value);
}

const baht = (n) =>
  n == null ? '—' : '฿' + Number(n).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 });

async function runSearch(e) {
  if (e) e.preventDefault();
  const q = qInput.value.trim();
  if (!q) return;
  const sites = selectedSites();
  if (!sites.length) {
    setStatus('Select at least one site.');
    return;
  }
  btn.disabled = true;
  setStatus('Searching ' + sites.join(', ') + '… (real marketplace scrapes can take 10–40s)');
  resultsEl.innerHTML = '';
  sourcesEl.innerHTML = '';
  emptyEl.hidden = true;
  try {
    const url = `/api/search?q=${encodeURIComponent(q)}&sites=${encodeURIComponent(sites.join(','))}`;
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    lastProducts = data.products || [];
    renderSources(data.sources || [], data.cached);
    render();
    setStatus(`${lastProducts.length} results for “${data.query}”.`);
  } catch (err) {
    setStatus('Error: ' + err.message);
  } finally {
    btn.disabled = false;
  }
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
  emptyEl.hidden = items.length > 0;
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
sortSel.addEventListener('change', render);
sellerSel.addEventListener('change', render);
