# Scrapling/PW — Node.js v24 FFBrowserContext Crash

## Symptom
When Scrapling's `StealthyFetcher.async_fetch(headless=True)` launches Playwright, the browser crashes immediately:

```
TypeError: Cannot read properties of undefined (reading 'url')
    at FFBrowserContext.<anonymous> (.../coreBundle.js:49624)
```

Followed by:
```
Error: Browser.close: Connection closed while reading from the driver
Error occurred in event listener
Exception: Route.continue_: Connection closed while reading from the driver
```

## Root Cause
The Playwright driver bundle bundled with the pip-installed `playwright` package is compiled against an older Node.js internal API. Node.js v24.15.0 changed the `pageError` object structure — `pageError.location.url` no longer exists (it's now `pageError.location` is `undefined`).

This is a **Node.js version incompatibility**, not a Scrapling bug nor a Playwright version issue. The pip-installed Playwright ships a pre-bundled `coreBundle.js` that cannot be patched.

## Affected Systems
- macOS with Node.js v24+ (current: v24.15.0)
- Any script using `scrapling.fetchers.StealthyFetcher` or `scrapling.fetchers.PlayWrightFetcher`
- Any script using `playwright.sync_api` or `playwright.async_api` directly

## Affected Scripts (un-jobs-search)
- `run_unicef.py` (uses Scrapling StealthyFetcher → crashes on listing page)
- `run_icrc_v2.py` (uses Playwright directly → same crash on all keyword searches)

## Working Alternatives

### 1. Camoufox (preferred — Hermes default browser)
Camoufox v2.4.5+ uses its own Firefox-based fork (camofox binary) and does not depend on the pip Playwright driver. It handles:
- AWS WAF challenges (UNICEF returns HTTP 202 without it)
- JS-rendered SPAs
- `browser_type`, `browser_press`, `browser_click`, `browser_console` reliably

Recovery from Camoufox `browser_type` 500: navigate away and back, retry.

### 2. Camoufox Python serverless
```python
from camoufox import Camoufox
with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state("networkidle")
```

### 3. Static HTTP (only for non-WAF sites)
```python
from scrapling.fetchers import StaticEngine
engine = StaticEngine()
resp = await engine.async_get(url)
```
Note: `StaticEngine.__init__()` requires a `url` parameter — check the API before using.

## The Broken Fallacy
"Sites accessible via Scrapling StealthyFetcher" cannot be reached on this system because StealthyFetcher always goes through Playwright browser mode. There is no HTTP-only mode in StealthyFetcher.