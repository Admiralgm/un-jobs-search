# Portal Classification Update — May 2026 Scan Sessions

## Multi-Approach Rule (MANDATORY — user correction 2026-05-19)

**NEVER skip a portal after a single failed approach.** The user explicitly called out that giving up after one attempt is unacceptable. For EVERY portal, try at least 3 approaches:

1. Direct URL with search params (avoids browser_type crashes)
2. browser_navigate + browser_type + Enter
3. browser_navigate + browser_console JS extraction
4. web-clean.py (non-JS sites only)
5. Scrapling StealthyFetcher (last resort)

**Known Camoufox `browser_type` crash sites:** UNICEF, WFP. Use URL params or console JS.

**Document in report:** Which approaches tried, what each returned, why concluded no vacancies.

## Changed Classifications

### FAO RSS — BROKEN (2026-05-19)
- **Previous**: Listed as accessible via curl/RSS
- **Actual**: RSS feed returns "Unable to Create an RSS Feed" error
- **Method**: Use browser_navigate to FAO Taleo (JS-rendered SPA, 123 jobs)

### FAO Taleo — NOW Camoufox ACCESSIBLE (2026-05-19)
- 123 jobs render correctly via Camoufox
- Keyword search works (type in search box + Enter)
- Mostly agriculture/food roles; no P-level ICT found on first page

### ITU (jobs.itu.int) — NOW browser_navigate ONLY
- **Previous**: Listed as "accessible via web-preclean.py"
- **Actual**: JS-rendered SPA. web-clean.py returns ONLY cookie banner (151KB -> 2KB, no job data)
- **Method**: browser_navigate -> accept cookies -> extract table via JS
- **Search URL**: `https://jobs.itu.int/search/?q=Digital&sortby=Relevancy`

### IMF — NOW Camoufox ACCESSIBLE (2026-05-19)
- **Previous**: Listed as "403 via all methods"
- **Actual**: Workday portal at `imf.wd5.myworkdayjobs.com/IMF` renders via Camoufox
- 13 jobs found including IT Strategist/Sr. IT Strategist (Formulation and Governance)
- Job ID 26-R9262, Washington DC, deadline 06/01/2026

### World Bank CSOD — CONFIRMED NON-RENDERING in Camoufox (2026-05-19)
- **Previous**: "Full job list renders correctly via Camoufox"
- **Actual**: JS SPA fails to render. Shows only skeleton (comboboxes, "Current Openings" heading)
- **Fallback**: Scrapling StealthyFetcher or tesseract OCR on screenshot

### UNICEF — Camoufox CRASHES on browser_type (2026-05-19)
- Page loads but `browser_type` causes 500 error
- URL params (`?q=Digital`) don't filter results
- All visible listings are internships/nationals-only
- **Workaround**: Try default browser or navigate-only with URL params

### UNJobNet — Vue.js SPA, results don't render in snapshot (2026-05-19)
- Page loads with search boxes but job results don't appear in snapshot
- **Fallback**: scrapling stealthy-fetch CLI

### Impactpool (impactpool.org) — NOW browser_navigate ONLY
- web-clean.py returns 0KB extraction (trafilatura empty)
- **Method**: browser_navigate with `/search?q=ICT` path

### UNDP — No Postings (2026-05-19)
- Careers page shows "There are no job postings at this time"

### UNOPS — New AI Roles Found (2026-05-19)
- AI Adoption Coordinator (Mid Level, Copenhagen, deadline 26-May-2026, Job ID 3184)
- AI Centre of Excellence Lead (Senior Level, Copenhagen/Home, deadline 24-May-2026, Job ID 3059)

### ILO — CIO Role Found (2026-05-19)
- Director, IT Management Department (Chief Information Officer) — Geneva, D-2, Job ID 13630

### ICAO — BI Developer Found (2026-05-19)
- Business Intelligence (BI) Developer (2 posts) — Montreal, Job ID 34241

### IAEA — Technical Consultants (2026-05-19)
- Consultant - Software and Database Development (TAL-NAHU20260506-001)
- Consultant - ERP Oracle Functional and Technical (HR and Payroll) (TAL-MTIT20260303-001)

### WHO — Data Management (2026-05-19)
- Data Management Officer (Job 2601918, Congo-Brazzaville, NO-B)

### UNESCO — No New P-level ICT (2026-05-19)
- 57 jobs, mostly consultants/junior/internships

### UNHCR — No ICT Professional Roles (2026-05-19)
- 41 jobs, mostly interns/drivers/admin

## Confirmed 404 URLs (May 2026)
- UNCTAD: unctad.org/about/vacancies
- UNECA: uneca.org/careers
- UNESCAP: unescap.org/careers
- UNDRR: undrr.org/careers
- UNICRI: unicri.org/careers
- UNITAR: unitar.org/careers
- UNSSC: unssc.org/careers
- UNIDIR: unidir.org/careers
- GICHD: gichd.org/careers
- UNWTO: unwto.org/careers
- WMO: wmo.int/careers
- UNOV: unov.org/unov/en/careers.html
- UNON: unon.org/careers
- FAO: fao.org/employment/current-vacancies/en/
- UNECE: unece.org/vacancies.html

## Key Finding: ITU is the Richest ICT Source
- 39 total unique ICT-relevant jobs found in one session
- 20 were new (not previously tracked)
- All are SSA roster consultancies — ongoing opportunities
- Mix of policy, technical, cybersecurity, and digital transformation roles
- Prioritize ITU scanning in every session

### FAO RSS — BROKEN (2026-05-19)
- **Previous**: Listed as accessible via curl/RSS
- **Actual**: RSS feed returns "Unable to Create an RSS Feed" error
- **Method**: Use browser_navigate to FAO Taleo (JS-rendered SPA, 118+ jobs)

### ITU (jobs.itu.int) — NOW browser_navigate ONLY
- **Previous**: Listed as "accessible via web-preclean.py"
- **Actual**: JS-rendered SPA. web-clean.py returns ONLY cookie banner (151KB -> 2KB, no job data)
- **Method**: browser_navigate -> accept cookies -> extract table via JS
- **Search URL**: `https://jobs.itu.int/search/?q=Digital&sortby=Relevancy`
- **Pagination**: Button click works, URL page param does NOT

### Impactpool (impactpool.org) — NOW browser_navigate ONLY
- **Previous**: Listed as accessible via web-preclean.py
- **Actual**: web-clean.py returns 0KB extraction (trafilatura empty)
- **Method**: browser_navigate with `/search?q=ICT` path
- **Filter**: Use "United Nations System" organization type filter in browser

### UNJobNet (unjobnet.org) — NOW browser_navigate ONLY
- **Previous**: Listed as "parse client-side" via web-clean.py
- **Actual**: web-clean.py returns JS template placeholders only
- **Method**: browser_navigate, but even then search filtering is unreliable

### UNDP — No Postings (2026-05-19)
- Careers page shows "There are no job postings at this time"
- Skip in routine scans

### UNOPS — New AI Roles Found (2026-05-19)
- AI Adoption Coordinator (Mid Level, Copenhagen, deadline 26-May-2026, Job ID 3184)
- AI Centre of Excellence Lead (Senior Level, Copenhagen/Home, deadline 24-May-2026, Job ID 3059)
- Camoufox renders full job list (21 jobs)

### ILO — CIO Role Found (2026-05-19)
- Director, IT Management Department (Chief Information Officer) — Geneva, D-2, Job ID 13630
- Camoufox renders (12 jobs in "All Jobs")

### ICAO — BI Developer Found (2026-05-19)
- Business Intelligence (BI) Developer (2 posts) — Montreal, Job ID 34241

### IAEA — Technical Consultants (2026-05-19)
- Consultant - Software and Database Development (TAL-NAHU20260506-001)
- Consultant - ERP Oracle Functional and Technical (HR and Payroll) (TAL-MTIT20260303-001)

### WHO — Data Management (2026-05-19)
- Data Management Officer (Job 2601918, Congo-Brazzaville, NO-B)

### UNESCO — No New P-level ICT (2026-05-19)
- 57 jobs, mostly consultants/junior/internships

### UNHCR — No ICT Professional Roles (2026-05-19)
- 41 jobs, mostly interns/drivers/admin

### IMF — Blocked
- 403 via all methods

### UNICEF — Crashes Camoufox (2026-05-19)
- Default browser shows only internships/nationals-only

## Confirmed 404 URLs (May 2026)
- UNCTAD: unctad.org/about/vacancies
- UNECA: uneca.org/careers
- UNESCAP: unescap.org/careers
- UNDRR: undrr.org/careers
- UNICRI: unicri.org/careers
- UNITAR: unitar.org/careers
- UNSSC: unssc.org/careers
- UNIDIR: unidir.org/careers
- GICHD: gichd.org/careers
- UNWTO: unwto.org/careers
- WMO: wmo.int/careers
- UNOV: unov.org/unov/en/careers.html
- UNON: unon.org/careers
- FAO: fao.org/employment/current-vacancies/en/
- UNECE: unece.org/vacancies.html

## Key Finding: ITU is the Richest ICT Source
- 39 total unique ICT-relevant jobs found in one session
- 20 were new (not previously tracked)
- All are SSA roster consultancies — ongoing opportunities
- Mix of policy, technical, cybersecurity, and digital transformation roles
- Prioritize ITU scanning in every session
