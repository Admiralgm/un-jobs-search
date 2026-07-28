# Camoufox browser_type Crash Pattern

## Symptoms
- `browser_type` action returns: `500 Server Error: Internal Server Error for url: http://localhost:9377/tabs/.../type`
- The tab becomes unresponsive after the crash
- Navigating to a new URL recovers the browser

## Affected Sites (confirmed May 2026)
- **UNICEF** (jobs.unicef.org) — crashes on every `browser_type` attempt
- **WFP Workday** (wd3.myworkdaysite.com/recruiting/wfp/job_openings) — intermittent crashes
- **WHO Taleo** (careers.who.int) — intermittent crashes

## Workaround
1. **Use URL parameters instead of typing**: `browser_navigate("https://jobs.unicef.org/en-us/search/?q=Digital")`
   - Note: URL params don't always filter results on all sites
2. **Use browser_console to execute JS search**:
   ```javascript
   // Type into search box via JS
   document.querySelector('input[placeholder*="Search"]').value = 'Digital';
   document.querySelector('input[placeholder*="Search"]').dispatchEvent(new Event('input'));
   // Click search button
   document.querySelector('button[type="submit"], button.search-btn').click();
   ```
3. **Use default browser** for sites that consistently crash Camoufox
4. **Navigate away and back** — the browser recovers after navigating to a new URL

## Pattern
The crash appears to be related to Camoufox's input handling on certain JS-heavy SPAs. It's not a permanent failure — the browser recovers. The issue is that the specific tab/session becomes unresponsive.
