#!/usr/bin/env node
// Fetches real Thai Government Lottery results and writes them into
// lotto-history/data/draws.{json,js} for the lotto-history web app.
//
// Data source: https://lotto.api.rayriffy.com (public API, results scraped
// from published draw archives). No dependencies; requires Node >= 18.
//
// Behavior:
//   - Incremental by default: stops paging once it reaches draws it already
//     has. A pre-existing SAMPLE dataset (isSample: true) is discarded.
//   - FULL_SYNC=1 refetches everything; MAX_PAGES caps list pagination.
//   - Writes files only when the dataset actually changed, so the calling
//     workflow can use `git diff` to decide whether to commit.
//   - Exits non-zero only when it ends up with no usable data at all.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DATA_DIR = join(ROOT, 'lotto-history', 'data');
const JSON_PATH = join(DATA_DIR, 'draws.json');
const JS_PATH = join(DATA_DIR, 'draws.js');

const API = 'https://lotto.api.rayriffy.com';
const FULL_SYNC = process.env.FULL_SYNC === '1';
const MAX_PAGES = Number(process.env.MAX_PAGES || 120);
const RETRY_BASE_MS = Number(process.env.RETRY_BASE_MS || 2000);
const CONCURRENCY = 4;

function log(...a) { console.log(new Date().toISOString().slice(11, 19), ...a); }

async function getJson(url, tries = 3) {
  for (let attempt = 1; ; attempt++) {
    try {
      const res = await fetch(url, {
        signal: AbortSignal.timeout(20000),
        headers: { 'user-agent': 'red-seawolf/lotto-history data updater' },
      });
      if (!res.ok) {
        const err = new Error(`HTTP ${res.status}`);
        err.permanent = res.status >= 400 && res.status < 500; // 4xx won't heal on retry
        throw err;
      }
      return await res.json();
    } catch (err) {
      if (attempt >= tries || err.permanent) {
        const out = new Error(`${url}: ${err.message}`);
        out.permanent = !!err.permanent;
        throw out;
      }
      await new Promise((r) => setTimeout(r, attempt * RETRY_BASE_MS));
    }
  }
}

// rayriffy draw ids are DDMMYYYY in the Buddhist Era calendar.
function idToIso(id) {
  const s = String(id);
  if (!/^\d{8}$/.test(s)) return null;
  const dd = +s.slice(0, 2), mm = +s.slice(2, 4), by = +s.slice(4, 8);
  if (dd < 1 || dd > 31 || mm < 1 || mm > 12 || by < 2400) return null;
  return `${by - 543}-${String(mm).padStart(2, '0')}-${String(dd).padStart(2, '0')}`;
}

function validDraw(d) {
  return d && /^\d{4}-\d{2}-\d{2}$/.test(d.date || '')
    && /^\d{6}$/.test(d.first || '')
    && /^\d{2}$/.test(d.last2 || '')
    && Array.isArray(d.front3) && d.front3.every((x) => /^\d{3}$/.test(x))
    && Array.isArray(d.back3) && d.back3.every((x) => /^\d{3}$/.test(x));
}

function apiDrawToRecord(id, res) {
  const iso = idToIso(id);
  if (!iso || !res) return null;
  const prizes = Array.isArray(res.prizes) ? res.prizes : [];
  const run = Array.isArray(res.runningNumbers) ? res.runningNumbers : [];
  const nums = (list, rid) => {
    const e = list.find((x) => x && x.id === rid);
    return e && Array.isArray(e.number) ? e.number.map(String) : [];
  };
  const rec = {
    id: iso,
    date: iso,
    thaiDate: typeof res.date === 'string' ? res.date.trim() : '',
    first: String(nums(prizes, 'prizeFirst')[0] || ''),
    front3: nums(run, 'runningNumberFrontThree'),
    back3: nums(run, 'runningNumberBackThree'),
    last2: String(nums(run, 'runningNumberBackTwo')[0] || ''),
  };
  return validDraw(rec) ? rec : null;
}

function loadExisting() {
  try {
    const payload = JSON.parse(readFileSync(JSON_PATH, 'utf8'));
    if (payload.isSample) {
      log('existing dataset is a sample — starting fresh');
      return { draws: [], missingIds: [] };
    }
    return {
      draws: (payload.draws || []).filter(validDraw),
      missingIds: Array.isArray(payload.missingIds)
        ? payload.missingIds.filter((x) => /^\d{8}$/.test(x))
        : [],
    };
  } catch {
    return { draws: [], missingIds: [] };
  }
}

async function main() {
  // Existing draws are ALWAYS kept as the merge base — a FULL_SYNC with partial
  // fetch failures must never shrink the committed archive. FULL_SYNC only
  // widens what gets (re)fetched.
  const { draws: existing, missingIds: prevMissing } = loadExisting();
  const have = new Set(FULL_SYNC ? [] : existing.map((d) => d.id));
  log(`existing real draws: ${existing.length}${FULL_SYNC ? ' (FULL_SYNC — refetching all)' : ''}`);

  // 1. Page through the draw list, collecting unknown draw ids.
  //    Draws that failed transiently on a previous run are retried first —
  //    without this, a failure behind an already-known page becomes a
  //    permanent hole (the caught-up break would stop before reaching it).
  const wantIds = [];
  for (const id of prevMissing) {
    const iso = idToIso(id);
    if (iso && !have.has(iso)) wantIds.push(id);
  }
  if (wantIds.length) log(`retrying ${wantIds.length} previously-failed draws`);
  for (let page = 1; page <= MAX_PAGES; page++) {
    const j = await getJson(`${API}/list/${page}`);
    const list = Array.isArray(j?.response) ? j.response : [];
    if (!list.length) { log(`list page ${page} empty — end of archive`); break; }
    let known = 0;
    for (const item of list) {
      const iso = idToIso(item?.id);
      if (!iso) continue;
      if (have.has(iso)) { known++; continue; }
      if (!wantIds.includes(String(item.id))) wantIds.push(String(item.id));
    }
    if (page % 10 === 0 || known) log(`list page ${page}: +${list.length - known} new`);
    if (!FULL_SYNC && known === list.length) { log(`page ${page} fully known — caught up`); break; }
  }
  log(`draws to fetch: ${wantIds.length}`);

  // 2. Fetch each unknown draw with modest concurrency. Transient failures
  //    (network, 5xx) are recorded in missingIds and retried next run;
  //    unrecognized payloads and 4xx are skipped permanently.
  const fetched = [];
  const failedIds = [];
  let invalid = 0;
  const queue = [...wantIds];
  await Promise.all(Array.from({ length: CONCURRENCY }, async () => {
    while (queue.length) {
      const id = queue.shift();
      try {
        const j = await getJson(`${API}/lotto/${id}`);
        const rec = apiDrawToRecord(id, j?.response);
        if (rec) fetched.push(rec);
        else { invalid++; log(`skip ${id}: unrecognized/incomplete draw payload`); }
      } catch (err) {
        if (err.permanent) { invalid++; log(`skip ${id}: ${err.message}`); }
        else { failedIds.push(id); log(`retry-later ${id}: ${err.message}`); }
      }
      const done = fetched.length + failedIds.length + invalid;
      if (done % 25 === 0) log(`fetched ${done}/${wantIds.length}`);
    }
  }));
  log(`fetched ok: ${fetched.length}, transient failures: ${failedIds.length}, invalid: ${invalid}`);

  // 3. Merge + write (only if something changed).
  const map = new Map(existing.map((d) => [d.id, d]));
  for (const d of fetched) map.set(d.id, d);
  const draws = [...map.values()].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));

  if (!draws.length) {
    console.error('ERROR: no draws fetched and no existing data — refusing to write an empty dataset');
    process.exit(1);
  }
  if (!fetched.length && wantIds.length) {
    // New draws exist but every fetch failed — fail loudly so the workflow
    // run goes red instead of silently stalling behind a green check.
    console.error(`ERROR: ${wantIds.length} draws pending but none could be fetched`);
    process.exit(1);
  }
  if (!fetched.length && existing.length) {
    log('no new draws — dataset unchanged, nothing written');
    return;
  }

  const payload = {
    schema: 1,
    isSample: false,
    source: 'สลากกินแบ่งรัฐบาล — ผลจริงผ่าน lotto.api.rayriffy.com',
    updatedAt: new Date().toISOString(),
    draws,
    missingIds: failedIds,
  };
  mkdirSync(DATA_DIR, { recursive: true });
  writeFileSync(JSON_PATH, JSON.stringify(payload, null, 1) + '\n');
  writeFileSync(
    JS_PATH,
    '// Auto-generated by scripts/fetch-lotto-data.mjs — do not edit by hand.\n' +
    '// Real Thai Government Lottery results for the lotto-history web app.\n' +
    'window.LOTTO_DRAWS = ' + JSON.stringify(payload) + ';\n',
  );
  log(`wrote ${draws.length} draws (${draws[draws.length - 1].date} .. ${draws[0].date})`);
}

main().catch((err) => {
  console.error('FATAL:', err);
  process.exit(1);
});
