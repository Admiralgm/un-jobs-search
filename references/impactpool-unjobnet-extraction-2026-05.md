# Impactpool + UNJobNet Extraction Guide (May 2026)

## Impactpool

### Search
- URL: `https://www.impactpool.org/search?q=ICT` (NOT `/jobs`)
- Filter: organization type "United Nations System" for relevant results
- ~138 ICT jobs with UN System filter
- Results are JS-rendered — browser_navigate + browser_console extraction required

### Detail Pages
- Pattern: `https://www.impactpool.org/jobs/{slug-numeric-ID}`
- Each detail page loads fully in browser
- Extract via `browser_console(expression="document.body.innerText")`
- Key fields in rendered text: title, organization, deadline, grade, location, contract type

### Known Issues
- **Generic deadline text:** Some pages (WIPO especially) show "deadline in local time" instead of actual date
- **WIPO career site down:** As of 2026-05-21, WIPO career portal was under maintenance
- **Nationality restrictions not visible on listing:** ECB, ELA, NATO YPP restrict to EU/EFTA/NATO nationals — only visible on detail pages
- **263+ total results:** Only first 40 extracted from page 1. Additional pages available via pagination.

### Scoring Results (33 entries, May 2026 scan)
- 🟠 COMPETITIVE (80-89): 1 entry (CHAI Director AI Transformation)
- 🟡 STRETCH (70-79): 13 entries (ILO CITO D-2, ECB Lead Experts, WIPO Chief P-5, etc.)
- 🟢 LOW FIT (<70): 19 entries (NATO YPP, UNDMSPC Assessment, AIIB Consultant, etc.)

## UNJobNet

### Search (Browser + Console Method)
- URL: `https://www.unjobnet.org/jobs?keywords={keyword}`
- Results load but DON'T render in `browser_snapshot`
- Must use `browser_click` on search button, then `browser_console(expression="document.body.innerText.substring(0, 6000)")` to extract
- Keyword results (May 2026):
  - `information+technology` → 8 results
  - `AI+artificial+intelligence` → 7 results  
  - `digital` → 71 results
  - `cybersecurity` → 3 results
  - `ICT` → 14 results
- Total: ~96 results with overlaps between searches

### Dedup Between Impactpool and UNJobNet
- Many UNJobNet listings also appear on Impactpool
- When scanning both unreliable sources in the same session, deduplicate by (title, organization) tuple
- Prefer Impactpool entry for richer detail when keeping one copy

### Official Verification Required
- Both Impactpool and UNJobNet are UNRELIABLE sources
- Every entry MUST be verified on the official hiring org career portal
- Known inaccuracies: expired listings, phantom vacancies, wrong deadlines, paraphrased titles
- Entries live in `UN_SECTOR_VACCANCIES_IMPACTPOOL.txt` (separate from reliable sources file)