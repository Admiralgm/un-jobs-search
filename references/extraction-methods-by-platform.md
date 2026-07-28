# Portal Extraction Methods — Tested 2026-05-30 (Updated 2026-06-03)

## Platform Patterns and How to Scrape Each

### Taleo (Oracle) — WHO, IAEA, FAO
1. `browser_navigate(careersection/ex/jobsearch.ftl)` → loads with "Job Openings 1-N of M" heading
2. `browser_type(keyword textbox)` + `browser_click(Search)` → filtered results
3. **Extract from detail pages:** `document.body.innerText` (no `<article>` tag)
4. **List view:** switch to "Multi-line" view for full text per job in listing
5. Vacancy ID format: numeric (WHO/IAEA: `2601970`, FAO: `2601132`)

### SuccessFactors (SAP) — ITU, UNESCO, UNIDO
1. **UNESCO & UNIDO:** Direct search URL `/search/?q=keyword` → table with results
2. **ITU:** Navigate to homepage → click "View all job openings" → table renders
3. **Extract from detail pages:** `document.body.innerText`
4. Vacancy ID: UNESCO uses long numbers (`1360698057`), UNIDO similar, ITU uses 10-digit numeric

### Custom ICS — UNOPS
1. `browser_navigate(careers.unops.org/careersmarketplace/SearchJobs)` → paginated carousel
2. Keyword search via combobox → filtered results
3. Each job is an `<article>` element → `document.querySelector('article').innerText` on detail pages

### Workday — IMF, WFP, UNHCR
1. Accept cookies first (`Accept Cookies` button)
2. `browser_type(keyword in Search box)` + `browser_click(Search)` or Enter
3. Results render as list with job title + location + date
4. `document.body.innerText` on detail pages
5. IMF job IDs: `26-R9262` format. WFP: `JR122932` format.

### SmartRecruiters — OECD, WTO
1. `browser_navigate(careers.smartrecruiters.com/OECD)` — note: OLD URL jobs.smartrecruiters.com/OECD now 404
2. `browser_type(keyword in search box)` + Enter → filtered results
3. Ref-format IDs (OECD: `REF3052Q`)
4. Detail pages: `document.body.innerText`

### UNICEF PageUp — jobs.unicef.org
1. `browser_navigate(/en-us/listing/)` → search box at top
2. `browser_type(keyword)` + `browser_press(Enter)` → filtered results (but broad matching)
3. **DOM bulk extraction** via browser_console:
   ```javascript
   (function(){
     const seen = new Set();
     const results = [];
     const links = document.querySelectorAll('a[href*="/en-us/job/"]');
     for(const a of links){
       const m = a.href.match(/\/en-us\/job\/(\d+)\//);
       if(!m || seen.has(m[1])) continue;
       seen.add(m[1]);
       const content = a.innerText;
       const locMatch = content.match(/Location:\s*(.+)/);
       const deadlineMatch = content.match(/Deadline:\s*(.+)/);
       results.push({id: m[1], title: a.innerText.split('\n')[0].trim(), href: a.href,
         location: locMatch ? locMatch[1] : '', deadline: deadlineMatch ? deadlineMatch[1] : ''});
     }
     return JSON.stringify(results);
   })()
   ```
4. "More Jobs" button exists but flaky — gets stuck after 10-15 clicks
5. Better approach: search each keyword separately, extract DOM, deduplicate in Python
6. Detail pages: `document.querySelector('article').innerText`

### INSPIRA (careers.un.org)
1. **Primary:** Pre-filtered ITECNET URL (see portal-directory.md)
2. **Alternative:** All-jobs URL with manual filter (user-provided)
3. Results link to `/jobSearchDescription/{ID}?language=en`
4. **Detail pages:** Click "Expand All" button first → `document.body.innerText` (19-22K chars)
5. Vacancy ID: 6-digit numeric
6. No login required for job detail pages

### Custom SPA (non-classified) — ILO, UNDP, UNITAR, UNFPA, ICMPD, GICHD
- **ILO:** Homepage → "View all jobs" → `/go/All-Jobs/2842101/`
- **UNDP:** `/cj_view_jobs.cfm` → keyword filter → Oracle HCM links
- **UNFPA:** `/jobs` → search box → Oracle HCM detail links
- **ICMPD (verified Jun 2026):** `careers.icmpd.org` base URL renders full vacancy list. DO NOT use `/search/?q=` — returns empty. Extract via Camoufox Python serverless: load base URL, then extract all `JobOpeningDetails?jobOpeningId=XXXX` URLs from HTML with regex. Detail page extraction: navigate to `https://careers.icmpd.org/Home/JobOpeningDetails?jobOpeningId={ID}`. Fields: Vacancy Number (VA26PXXXXX), Grade (IP1/IP2/IP3/LP2/LP3), Location, Closing Date (DD/MM/YYYY), Compensation (monthly net). **Important:** old/dead IDs return "JOB OPENING IS NOT ACTIVE ANY MORE" instead of 404 — check for this string. Active ICT roles found: HR IS & Automation Officer IP3 Vienna (VA26P112V01, Jun 28), Modernisation Officer AI IP2 Valletta (VA26P075V01, requires French+Arabic).
- **UNITAR:** `/vacancy-announcements` → filter by category + deadline. Only roster posts confirmed (EdTech/AI for Learning, Geospatial Analysts). No active P-level ICT.
- **GICHD:** `/the-gichd/job-opportunities/` → links to Beehire. No active ICT confirmed Jun 2026.

### Oracle HCM — UNFPA, UNDP, IOM (fa-evlj-saasfaprod1)
- Detail URLs: `estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_*/job/XXXXX/`
- Backend renders job details with full JD

## Camoufox Known Crashes (v2.4.5)
| Portal | Crash Type | Recovery |
|--------|-----------|----------|
| WIPO | 400 on `browser_click` on buttons | Use Scrapling StealthyFetcher |
| ICAO | Intermittent 500 on click | Navigate away and back |
| UNICEF | Search box + Enter sometimes slow | Wait 2-3s after typing |
| World Bank | Empty page on `navigate` | Cannot recover in browser — use Scrapling |

## Fatigue Limit
After 10-15 `browser_navigate` calls in a single tab session, Camoufox becomes unresponsive (500 on all calls).
- Save progress every 5-8 navigations
- Restart: `pkill -f "camofox server"` → `terminal(background=true, command="camofox server start")`
- Verify: health check after restart

## Alternative: Python Serverless for Batch Scans
When scanning 10+ portals, use Python context manager instead of HTTP server:
```python
from camoufox import Camoufox
import time

for name, url in portals:
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)
        text = page.inner_text("body")
```
Zero crashes, no port management, no profile bloat. See `camoufox-browser` skill for full decision framework.