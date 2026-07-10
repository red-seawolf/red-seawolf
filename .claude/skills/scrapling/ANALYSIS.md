# Scrapling — Source-Level Analysis

Analysis of [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) **v0.4.10**
(shallow clone of `main`, 2026-07-10), written to accompany the vendored official skill in
this directory. `SKILL.md` tells you *how to use* Scrapling; this file explains *how it is
built* and what was verified in this repo's remote environment.

## What it is

Scrapling is a BSD-3-Clause Python web-scraping framework (Python **3.10+**) that combines,
in one library, what usually takes three: an lxml-based parser with a Scrapy/Parsel-style
selection API, a tiered set of fetchers from plain HTTP up to anti-bot stealth browsers, and
a Scrapy-like spider/crawl framework with checkpointing. Its signature feature is **adaptive
scraping**: elements can be saved (fingerprinted) and later *relocated by similarity* after a
site changes its markup.

## Architecture map

```
scrapling/
├── parser.py            Selector / Selectors — the whole parsing API (lxml + cssselect)
├── cli.py               `scrapling` CLI: extract | shell | mcp | install
├── core/
│   ├── storage.py       StorageSystemMixin + SQLiteStorageSystem (adaptive element store)
│   ├── translator.py    CSS→XPath translation layer
│   ├── shell.py, ai.py  Interactive shell; MCP server implementation
├── engines/
│   ├── static.py        HTTP engine on curl_cffi (TLS fingerprint impersonation, HTTP/3)
│   ├── _browsers/
│   │   ├── _controllers.py  DynamicFetcher engine — vanilla playwright (Chromium/CDP)
│   │   └── _stealth.py      StealthyFetcher engine — patchright (patched Playwright)
│   │                        + browserforge/apify fingerprint datapoints
│   └── toolbelt/        ProxyRotator, header/fingerprint generators, ~3.5k ad-domain
│                        blocklist, response convertor
├── fetchers/            Public facade: Fetcher/AsyncFetcher/FetcherSession (requests.py),
│                        DynamicFetcher/DynamicSession (chrome.py),
│                        StealthyFetcher/StealthySession (stealth_chrome.py)
├── spiders/             Spider engine: scheduler, request/response, checkpoint (pause/
│                        resume), cache (development_mode), robotstxt (protego),
│                        links (LinkExtractor), templates (CrawlSpider, SitemapSpider)
└── integrations/        scrapy.py — `scrapling_response` decorator for Scrapy projects
```

### The three fetch tiers (escalation ladder)

| Tier | Class | Backend | Use for |
|---|---|---|---|
| 1 | `Fetcher` / `FetcherSession` | `curl_cffi` — real browser TLS/JA3 impersonation (`impersonate='chrome'`), optional HTTP/3 | static pages, APIs |
| 2 | `DynamicFetcher` / `DynamicSession` | Playwright Chromium (or real Chrome / remote CDP) | JS-rendered SPAs |
| 3 | `StealthyFetcher` / `StealthySession` | **patchright** (leak-patched Playwright fork) + generated fingerprints, canvas noise, WebRTC blocking, `solve_cloudflare=True` for Turnstile/interstitial | protected sites |

All three return the same `Response` object, which **is a `Selector`** — fetch result and
parse tree share one API. Async twins exist for every tier (`AsyncFetcher`,
`AsyncDynamicSession`, `AsyncStealthySession`); browser sessions pool tabs (`max_pages`)
and expose `get_pool_stats()`. Extra niceties: XHR capture (`capture_xhr=regex` →
`page.captured_xhr`), DNS-over-HTTPS, per-request proxies plus a `ProxyRotator`.

### Parser

`Selector` wraps lxml with: `css()` (with `::text` / `::attr(x)` pseudo-elements via a
custom translator), `xpath()`, BeautifulSoup-style `find()/find_all()/find_by_text()`,
navigation (`parent`, `next_sibling`, `below_elements()`), and regex helpers. Results come
back as `Selectors` (list-like, chainable) and text as `TextHandler` (a `str` subclass with
`.json()`, `.re()`, `.clean()`). It's fast because selection compiles to XPath and runs in
lxml/C — the project benchmarks text extraction at ~2 ms vs ~1.5 s for BeautifulSoup.

### Adaptive scraping (the differentiator)

Constructing a `Selector`/fetch with `adaptive=True` attaches a `SQLiteStorageSystem`
(per-domain tables). `css(..., auto_save=True)` fingerprints matched elements (tag,
attributes, text, path context); after a site redesign, `css(..., adaptive=True)` or
`element.find_similar()` relocates the equivalent element by similarity scoring instead of
failing. `identifier=` names a saved element explicitly. Off by default — zero overhead
unless enabled.

### Spiders

Scrapy-shaped but asyncio-native: subclass `Spider`, `yield` dicts (items) or `Request`
objects from `async def parse()`. Engine features verified in source: concurrent scheduling
(`concurrent_requests`), multi-session routing (`configure_sessions` + `Request(sid=...)`),
graceful pause/resume via `crawldir` checkpoints, `development_mode` response cache,
`robots_txt_obey` (protego), `download_delay`, blocked-response retry, and
`CrawlSpider`/`SitemapSpider` templates with `LinkExtractor` rules. `result.items` exports
via `.to_json()` / `.to_csv()`.

## Dependency/extras model

Core install (`pip install scrapling`) is parser-only: `lxml`, `cssselect`, `orjson`, `tld`,
`w3lib`. Extras gate the heavy parts:

- `[fetchers]` → `curl_cffi`, `playwright`, `patchright`, `browserforge`, `protego`, `click` …
- `[ai]` → `mcp`, `markdownify` (MCP server)
- `[shell]` → IPython shell
- `[all]` → everything. Browser binaries install via `scrapling install`.

## How this is embedded as a tool for Claude

1. **This skill** (`.claude/skills/scrapling/`) — the author's official agent skill,
   vendored verbatim (SKILL.md + `references/` + `examples/` + LICENSE), auto-discovered by
   Claude Code in this repo. It covers the CLI (`scrapling extract get|fetch|stealthy-fetch`,
   always with `--ai-targeted`), the Python API, and spiders.
2. **CLI path** — no code needed: `scrapling extract get URL out.md -s "selector" --ai-targeted`.
3. **MCP path (optional)** — Scrapling ships an MCP server (10 tools: `get`, `bulk_get`,
   `fetch`, `stealthy_fetch`, bulk variants, `open_session`/`close_session`/`list_sessions`,
   `screenshot`); see `references/mcp-server.md`. To enable it in this repo, install
   `scrapling[all]`, run `scrapling install`, then add to `.mcp.json`:

   ```json
   "scrapling": { "command": "scrapling", "args": ["mcp"] }
   ```

   Not enabled by default here because it requires the package + browsers to be installed in
   the session environment first (a SessionStart hook could automate that).

## Verified in this environment (2026-07-10)

Smoke-tested with `scrapling[fetchers]` 0.4.10 in a venv (Python 3.11):

- **Parser: PASS** — `css('::text')`, `xpath()`, `find_all(class_=...)`, `find_by_text()`,
  and `find_similar()` all returned expected results on sample HTML.
- **Fetcher: pipeline PASS, egress limited** — `Fetcher.get(..., impersonate='chrome')`
  completed the full request→response→parse cycle against github.com. Non-allowlisted hosts
  (e.g. quotes.toscrape.com) are rejected by this sandbox's egress proxy with `CONNECT 403`
  — an environment network policy, not a Scrapling failure. When using curl_cffi through the
  proxy, set `CURL_CA_BUNDLE=/root/.ccr/ca-bundle.crt`; note that TLS impersonation may
  still conflict with the MITM proxy on some hosts (connection reset). On an unrestricted
  machine none of this applies.
- **Browser tiers: not exercised here** (no `scrapling install` browsers in the sandbox);
  their APIs are documented in `references/fetching/`.

## Guardrails

Same as SKILL.md: scrape only what you're authorized to access, respect robots.txt/ToS
(`robots_txt_obey = True`), add `download_delay` on large crawls, never harvest
personal/sensitive data, and always pass `--ai-targeted` on CLI scrapes to sanitize
prompt-injection vectors.
