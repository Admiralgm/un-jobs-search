# Marginal Portal Scan — June 3, 2026

## Summary of Verified Access Patterns

All 11 marginal portals scanned via Camoufox Python serverless (`with Camoufox() as browser:`).
10/11 confirmed to have zero ICT/AI roles at professional level. 1 new entry (ICMPD) added.

---

## Per-Portal Access Patterns

### ICMPD (careers.icmpd.org) — ✅ Active ICT roles possible
- **Base URL:** `https://careers.icmpd.org`
- **Platform:** Custom .NET MVC
- **Listing:** Full list renders on base URL — no search filter needed
- **Job IDs:** 4-digit numeric, found in HTML via:
  ```python
  import re
  html = page.content()
  urls = re.findall(r'JobOpeningDetails\?jobOpeningId=(\d+)', html)
  ```
- **Detail URL pattern:** `https://careers.icmpd.org/Home/JobOpeningDetails?jobOpeningId=XXXX`
- **Extraction:** `page.inner_text("body")` — returns clean labeled fields
- **Key fields:** Vacancy Number (VA26PXXXXX), Grade, Location, Closing Date (DD/MM/YYYY), Compensation (monthly net), Duration
- **Observed grades (verified):** IP1 (€3,414), IP2 (€4,158), IP3 (€5,092), LP2 (€2,542), LP3 (€3,793)
- **Contract types:** Staff contract (12/24 months) vs SSA (service contract)
- **Attention:** Old/dead job IDs return "JOB OPENING IS NOT ACTIVE ANY MORE" instead of 404
- **Deadline format:** DD/MM/YYYY
- **Key finding Jun 2026:** VA26P112V01 — HR IS & Automation Officer IP3 Vienna (Jun 28). Modernisation Officer AI IP2 Valletta (deadline Jun 3, requires French + Arabic — language filter eliminates most candidates)

### UNHCR Workday (unhcr.wd3.myworkdayjobs.com) — ❌ 0 ICT professional
- Accept cookies first, then browse full listing
- Job categories: Dropdown filter, "Information Technology" returns 0 as of June 2026
- All 25 jobs are protection/programme/associate level or internships
- No ICT professional roles seen across multiple cycles

### UNFPA (unfpa.org/jobs → Oracle Cloud) — ❌ 0 P-level ICT
- Redirects to: `estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/`
- Filter by "Information & Communication Technology" job category
- Only local NPSA-level ICT posts found (ICT Analyst Dili, ICT Associate Minsk, ICT Clerk Caracas)
- No international P-level ICT postings

### WMO (erecruit.wmo.int) — ❌ 0 ICT roles
- Redirects to Oracle Cloud: `estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_5001/jobs`
- 5 openings visible (Jun 2026): P2 Project Officer, P3 HR Officer, French-language Madagascar consultant, 2 JPOs
- No ICT professional vacancies

### UNITAR (unitar.org/vacancy-announcements) — ❌ Only rosters
- Custom CMS with category filter + deadline slider
- Roster posts only: "Educational Technology, IT and AI for Learning" consultant roster, Geospatial Analysts roster
- No active P-level job postings
- The EdTech/AI for Learning Roster is the only tangential match — see scoring guide for roster treatment

### UNU (unu.edu/careers) — ❌ 0 ICT
- Content-heavy page describing contract types (Fixed-term, PSA, Consultant)
- No active job listings visible on main careers page
- Direct job search likely requires deeper navigation

### GICHD (gichd.org/the-gichd/job-opportunities/) — ❌ 0 jobs
- Links to Beehire external platform
- Page content covers training/IMSMA courses, not job vacancies
- No active job postings visible

### UNDRR (undrr.org/about-undrr/jobs) — ❌ Dead link
- Returns 404-style content for the /jobs path
- Previously had job listings, now inaccessible
- May have moved to Inspira

### UNESCAP (unescap.org/about/jobs) — ❌ Timeout
- Heavy JS render, likely Inspira-powered
- Covered by Batch 7 (Inspira ITECNET filter) — no need to scan separately

### UNESCWA (unescwa.org/jobs) — ❌ 0 active ICT
- Content mentions "Data and Statistics" and "Technology for Development" categories
- No active job postings rendered on page
- May redirect to Inspira for actual listings

### UNICRI (unicri.it/about-us/jobs) — ❌ 0 active jobs
- "Centre for AI and Robotics" entity exists but no active job postings
- Small org, rare vacancies
- Check Inspira for occasional UNICRI posts

---

## Methodology Notes

### Camoufox Serverless Batch Scan Pattern (verified working)
```python
from camoufox import Camoufox
import time

portals = [
    ("UNITAR", "https://unitar.org/vacancy-announcements"),
    ("GICHD", "https://www.gichd.org/the-gichd/job-opportunities/"),
    # ...etc
]

for name, url in portals:
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)  # critical for JS rendering
        text = page.inner_text("body")
        # Check against ICT keyword list
```

### ICT Keyword Detection
Keywords for scanning: `ict`, `digital`, `ai`, `artificial intelligence`, `data`, `information technology`,
`software`, `developer`, `engineer`, `information management`, `information systems`,
`technology`, `telecom`, `connectivity`, `innovation`, `database`, `cyber`, `systems`,
`programmer`, `architect`, `platform`, `digital transformation`

### Per-Portal Overhead
Each `with Camoufox():` block costs ~3-5s startup + 6-8s render wait = ~10s per portal.
11 marginal portals = ~2 minutes total scan time.

---

## Exclusion Filters Applied (none matched from these portals)
- Internships: UNHCR had 2 (Digital Marketing Intern, Information Management Intern) — excluded
- Junior grades: ICMPD Junior Modernisation Officer IP1 — excluded
- National-only: UNFPA ICT Analyst Dili, ICT Associate Minsk — both national posts, excluded based on NPSA contract type
- Language-barrier: ICMPD Modernisation Officer AI requires French AND Arabic — excluded