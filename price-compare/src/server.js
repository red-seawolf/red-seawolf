// Express server: serves the static UI and the search API.
import express from 'express';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { aggregateSearch } from './aggregator.js';
import { listAdapters } from './adapters/index.js';
import { closeBrowser } from './browser.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(join(__dirname, '..', 'web')));

// The browser app imports the shared normalize module and demo fixtures via
// relative URLs (../src/…) so the exact same files work when the repo is served
// statically (e.g. GitHub Pages). Expose just those two paths here.
app.get('/src/normalize.js', (_req, res) => res.sendFile(join(__dirname, 'normalize.js')));
app.get('/src/fixtures/demo.json', (_req, res) => res.sendFile(join(__dirname, 'fixtures', 'demo.json')));

// CORS: allow the statically-hosted web app (e.g. GitHub Pages) to use this
// server as its live-search backend.
app.use('/api', (req, res, next) => {
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, sites: listAdapters() });
});

app.get('/api/sites', (_req, res) => {
  res.json({ sites: listAdapters() });
});

app.get('/api/search', async (req, res) => {
  const q = String(req.query.q || '').trim();
  if (!q) return res.status(400).json({ error: 'missing query parameter q' });
  const sites = req.query.sites
    ? String(req.query.sites).split(',').map((s) => s.trim()).filter(Boolean)
    : undefined;
  const limit = Math.min(Math.max(parseInt(req.query.limit, 10) || 40, 1), 60);
  try {
    const result = await aggregateSearch(q, { sites, limit });
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: String(err.message || err) });
  }
});

const server = app.listen(PORT, () => {
  console.log(`th-price-compare listening on http://localhost:${PORT}`);
});

async function shutdown() {
  await closeBrowser().catch(() => {});
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(0), 3000).unref();
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
