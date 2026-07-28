# UNHCR Workday Career Portal — Extraction Guide
# URL: https://unhcr.wd3.myworkdayjobs.com/en-GB/External
# Last verified: 2026-05-15

## Access
- Method: browser_navigate (NOT web-clean.py — JS-rendered SPA, returns empty via requests)
- No login required for search
- JS-rendered SPA — content loads dynamically
- Returns 28+ job openings (as of May 2026)
- Cloudflare-protected but passes bot detection (unlike unhcr.org/careers which blocks completely)

## Extraction Pattern

### Step 1: Navigate
```
browser_navigate: https://unhcr.wd3.myworkdayjobs.com/en-GB/External
```

### Step 2: Extract job listings via innerText
Standard DOM selectors (querySelectorAll, etc.) return EMPTY — the page renders via
a framework that doesn't expose elements to the DOM tree in a queryable way.

**Use innerText instead:**
```javascript
document.body.innerText
```

This returns the full page text including:
- Job titles (one per line)
- Locations (prefixed with "locations")
- Post dates (prefixed with "Posted" or "Posted Today"/"Posted Yesterday"/"Posted X Days Ago")
- Job reference numbers (e.g., "JR2666591")
- Job categories (e.g., "Affiliate/Internship > Hire", "Regular > Regular Assignment")

### Step 3: Parse the innerText output
The text structure is:
```
[JOB TITLE]
locations
[City, Country]
posted on
Posted [Today|Yesterday|X Days Ago]
JR[NUMBER][GRADE][CATEGORY]
```

### Step 4: Navigate to job detail
Job detail URLs follow pattern:
```
https://unhcr.wd3.myworkdayjobs.com/en-GB/External/job/[JOB_TITLE]/[JR_NUMBER]
```

## Login Behavior
- Login is NOT required for job search — all 28+ jobs are visible without authentication
- Workday portals may show "Sign In" but all job listings and detail pages are publicly accessible
- The "Apply" button may redirect to a login/registration flow, but job data is fully visible

## Notes
- Job reference numbers use format: JR + 7 digits (e.g., JR2666591)
- Grade codes: GS4-GS6 (General Service), NOB/NOC/NOD (National Professional), P2-P5 (International Professional), D1-D2 (Director)
- Categories: "Affiliate/Internship > Hire", "Regular > Regular Assignment"
- The old URL unhcr.org/careers is BLOCKED (Cloudflare bot detection) — use the Workday URL instead
- Workday portals are also used by other agencies — this innerText extraction pattern may apply to other Workday-based career sites