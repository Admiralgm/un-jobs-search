# UNICEF Scrapling Crash Root Cause — 2026-06-04

## The Two-Factor Failure

`run_unicef.py` uses Scrapling's `StealthyFetcher.async_fetch(headless=True)` which launches Playwright. UNICEF careers (jobs.unicef.org) sits behind **AWS WAF** (CloudFront with `x-amzn-waf-action: challenge`). Two independent failures block it:

### 1. AWS WAF Challenge
- Plain HTTP (curl, httpx, requests) → HTTP 202 + empty body + `x-amzn-waf-action: challenge` header
- WAF requires JS execution to solve the challenge cookie before serving content
- HTTP-only clients get zero content regardless of user-agent

### 2. Playwright Node.js v24 Crash
```
TypeError: Cannot read properties of undefined (reading 'url')
    at FFBrowserContext.<anonymous> (.../coreBundle.js:49624)
```
- The Playwright driver bundle crashes on Node.js v24 (system has v24.15.0 and v25.6.1)
- `FFBrowserContext` → `pageError.location.url` is undefined — a known Node.js v24+ compatibility bug
- This prevents Scrapling's StealthyFetcher from even opening a browser to solve the WAF challenge

## Working Solution: Camoufox v2.4.5
Camoufox bypasses both problems:
- Its C++/Rust browser engine doesn't use the bundled Playwright Node.js driver
- It handles the AWS WAF JS challenge transparently
- Pipeline: `browser_navigate` → close cookie popup → `browser_type` keyword → Enter → `browser_console` JS extraction

## Lesson for other Scrapling portals
Any portal where `run_*.py` relies on `StealthyFetcher.async_fetch(headless=True)` and the system has Node.js v24+ will crash with the same `coreBundle.js:49624` TypeError. Switch those scripts to use Camoufox Python (`from camoufox import Camoufox`) or Hermes `browser_navigate` instead.

## Portals confirmed affected (same Playwright crash)
- ICRC (`run_icrc_v2.py`) — all 6 keyword fetches failed
- UNICEF (`run_unicef.py`) — listing page returned LISTING_ERROR
- Any script using `StealthyFetcher` headless mode with Playwright driver under Node v24+ is at risk