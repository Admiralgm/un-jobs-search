# UN Career Portal Accessibility — May 2026 Verification

This file documents the results of systematic verification of UN organization career
portals conducted across May 2026 using SearXNG search + browser_navigate + Scrapling StealthyFetcher + Camoufox.

## Summary

| Organization | Portal | Status | Scraping Method |
|-------------|--------|--------|-----------------|
| FAO | jobs.fao.org | JS-rendered SPA | ~~RSS feed~~ **BROKEN 2026-05-19** — use browser |
| ICAO | icaocareers.icao.int | ACCESSIBLE | Direct HTML scraping (browser) |
| IMO | recruit.imo.org | JS-rendered | Camoufox / Scrapling StealthyFetcher |
| World Bank | worldbankgroup.csod.com | JS-rendered + SAML | Camoufox (partial) / Scrapling StealthyFetcher |
| WFP | wd3.myworkdaysite.com | Workday SPA | Camoufox (accept cookies first) |
| IMF | imf.org | 403 / login required | NOT FEASIBLE |
| IAEA | iaea.taleo.net | ACCESSIBLE | Camoufox — 31 jobs |
| ILO | jobs.ilo.org | ACCESSIBLE | Camoufox — 12 jobs |
| UNOPS | careers.unops.org | ACCESSIBLE | Camoufox — 21 jobs, 2 AI roles |
| UNESCO | careers.unesco.org | ACCESSIBLE | Camoufox — 57 jobs |
| UNICEF | jobs.unicef.org | CRASHES Camoufox | Default browser (internships only) |
| UNDP | undp.org/careers | No postings | "No job postings at this time" |
| WHO | careers.who.int | ACCESSIBLE | Camoufox — 56 jobs |
| UNHCR | unhcr.wd3.myworkdaysite.com | ACCESSIBLE | Camoufox — 41 jobs |

## Scraping Tool Priority (2026-05-19, Camoufox is default)

1. **Camoufox** (default browser via `CAMOFOX_URL=http://localhost:9377`) — PRIMARY for JS-rendered SPAs
   - Works for: WHO Taleo, IAEA Taleo, ILO Jobs, UNOPS, WFP Workday, UNHCR Workday, ICAO, IMO, UNESCO
   - Known crash: `browser_type` on some sites returns 500 — navigate away and back to recover
   - UNICEF crashes Camoufox (Internal Server Error) — fall back to default browser

2. **Scrapling StealthyFetcher** — Fallback if Camoufox unavailable

3. **curl + RSS** — for FAO — **BROKEN as of 2026-05-19, use browser instead**

4. **Tesseract OCR** — last resort on screenshots

## Key Findings (2026-05-19 Scan)

### FAO RSS BROKEN
- RSS URL now returns "Unable to Create an RSS Feed" error
- Fallback: Use browser_navigate to FAO Taleo (JS-rendered SPA)

### UNDP — No Postings
- Careers page shows "There are no job postings at this time"

### UNOPS — New AI Roles
- AI Adoption Coordinator (Mid Level, Copenhagen, deadline 26-May-2026, Job ID 3184)
- AI Centre of Excellence Lead (Senior Level, Copenhagen/Home, deadline 24-May-2026, Job ID 3059)

### ILO — CIO Role
- Director, IT Management Department (Chief Information Officer) — Geneva, D-2, Job ID 13630

### ICAO — BI Developer
- Business Intelligence (BI) Developer (2 posts) — Montreal, Job ID 34241

### IAEA — Technical Consultants
- Consultant - Software and Database Development (TAL-NAHU20260506-001)
- Consultant - ERP Oracle Functional and Technical (HR and Payroll) (TAL-MTIT20260303-001)

### WHO — Data Management
- Data Management Officer (Job 2601918, Congo-Brazzaville, NO-B)

### UNESCO — No New P-level ICT
- 57 jobs, mostly consultants/junior/internships

### UNHCR — No ICT Professional Roles
- 41 jobs, mostly interns/drivers/admin

### IMF — Blocked
- 403 via all methods

### UNJobNet — Unreliable Filtering
- 3,518 jobs, client-side Vue.js rendering
- Search filtering via URL params doesn't work

### Impactpool — Unreliable
- 144 ICT jobs found, but always verify on official portal
