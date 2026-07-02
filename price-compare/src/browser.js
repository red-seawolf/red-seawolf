// Shared headless-Chromium manager. One browser instance is reused across
// requests; each scrape gets its own context (fresh cookies, realistic
// fingerprint) which is the main lever we have against anti-bot blocking.
import { chromium } from 'playwright-core';

const EXECUTABLE =
  process.env.CHROMIUM_PATH ||
  '/opt/pw-browsers/chromium'; // pre-installed in this environment

const UA =
  process.env.SCRAPER_UA ||
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

let browserPromise = null;

export async function getBrowser() {
  if (!browserPromise) {
    browserPromise = chromium
      .launch({
        executablePath: EXECUTABLE,
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-blink-features=AutomationControlled',
          '--disable-dev-shm-usage',
        ],
      })
      .catch((err) => {
        browserPromise = null;
        throw err;
      });
  }
  return browserPromise;
}

/**
 * Create a realistic browser context for one scrape. Callers must close it.
 */
export async function newContext() {
  const browser = await getBrowser();
  const context = await browser.newContext({
    userAgent: UA,
    locale: 'th-TH',
    timezoneId: 'Asia/Bangkok',
    viewport: { width: 1366, height: 900 },
    extraHTTPHeaders: { 'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8' },
  });
  // Light stealth: hide the webdriver flag that headless Chromium exposes.
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  return context;
}

export async function closeBrowser() {
  if (browserPromise) {
    const b = await browserPromise.catch(() => null);
    browserPromise = null;
    if (b) await b.close().catch(() => {});
  }
}
