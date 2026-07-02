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
