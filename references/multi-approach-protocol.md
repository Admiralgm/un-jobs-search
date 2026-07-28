# Multi-Approach Scanning Protocol — UN Job Portals

## Rule: NEVER Give Up After One Failed Approach

When a portal returns no results or fails to load, you MUST try at least 3 different approaches before reporting "no data" or skipping the portal. The user explicitly called out that skipping portals after a single attempt is unacceptable.

## Required Approach Chain (try in order)

### Approach 1: Direct URL with Search Parameters
Navigate directly to the portal's search URL with keywords in the URL:
```
browser_navigate("https://jobs.unicef.org/en-us/search/?q=Digital")
browser_navigate("https://jobs.fao.org/careersection/fao_external/jobsearch.ftl?keyword=ICT")
```
This avoids the `browser_type` crash issue entirely.

### Approach 2: browser_navigate + browser_type + browser_press(Enter)
If URL params don't work, try interacting with the search box:
```
browser_navigate("https://portal-url")
browser_type(ref="search-box-ref", text="Digital")
browser_press(key="Enter")
```
**KNOWN ISSUE:** Camoufox crashes (500 error) on `browser_type` for some sites (UNICEF, WFP). If this happens, fall back to Approach 1 or 3.

### Approach 3: browser_navigate + browser_console(JS extraction)
If the page loads but snapshot shows empty results, use JS console to extract data:
```
browser_navigate("https://portal-url")
browser_console(expression="document.body.innerText")
browser_console(expression="document.querySelectorAll('[class*=\"job\"]').length")
```

### Approach 4: web-clean.py (for non-JS sites)
Only for sites that return 200 with full HTML:
```
terminal("python3 config/scripts/web-preclean.py URL 8000")
```

### Approach 5: Scrapling StealthyFetcher (last resort)
For JS-heavy SPAs that don't render in Camoufox:
```python
from scrapling import StealthyFetcher
page = StealthyFetcher.fetch("URL", headless=True, wait=8000, block_webrtc=True)
text = page.get_all_text()
```

## Camoufox Crash Pattern — browser_type

**Sites where `browser_type` crashes Camoufox (500 error):**
- UNICEF (jobs.unicef.org)
- WFP Workday (wd3.myworkdaysite.com/recruiting/wfp/job_openings)

**Workaround:** Use `browser_navigate` with URL parameters instead of typing in the search box. If URL params don't filter results, use `browser_console` to execute JS search or extract all results and filter locally.

## Sites Requiring Multiple Approaches (from May 2026 scan)

| Portal | URL params | type+enter | console | web-clean | Result |
|--------|-----------|-----------|---------|-----------|--------|
| UNICEF | partial | crashes | partial | empty | All internships |
| World Bank CSOD | empty | N/A | text only | N/A | Need Scrapling |
| IMF Workday | works | works | works | 403 | 13 jobs |
| FAO Taleo | works | works | works | partial | 123 jobs |
| UNJobNet | no render | no render | templates | empty | Need scrapling |

## User Expectation

The user expects thoroughness. If you skip a portal after one failed attempt, the user will notice and call it out. Always document:
1. Which approaches you tried
2. What each approach returned
3. Why you concluded there are no relevant vacancies

Never just say "skipped" without evidence of multiple attempts.
