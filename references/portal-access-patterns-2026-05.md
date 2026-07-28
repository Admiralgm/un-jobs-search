# UN Job Portal Access Patterns — May 2026 Update (Live-Tested 2026-05-14)

> **Session update 2026-05-18:** Full re-scan of all portals. Major findings below.
> **Previous update 2026-05-14:** Live-tested all portals via browser_navigate + web-clean.py.

## Access Method Key
- 🟢 `web-clean.py` — works, returns usable data
- 🟡 `terminal` + `web-clean.py` — works with URL piping
- 🔵 `browser_navigate` — required (JS-rendered SPA)
- 🔴 Blocked — returns 403/404/Cloudflare/empty

---

## CONFIRMED ACCESSIBLE (Live-Tested 2026-05-14)

### UNICEF (jobs.unicef.org)
- **URL:** https://jobs.unicef.org/en-us/listing/
- **Access:** 🔵 browser_navigate (JS-rendered listing page)
- **Also:** 🟡 `web-clean.py` on listing page returns partial HTML with job titles, locations, deadlines visible
- **Pagination:** Page 2 exists at `?page=2` with additional vacancies (Parenting Consultant, Sr. Data Analyst Budapest, Programme Officer Abuja, Senior Consultant WB/IDB Panama)
- **Job detail URLs:** `/en-us/job/<numeric-id>` (e.g., `/en-us/job/593037`)
- **⚠️ NOTE:** Main unicef.org/search returns 403 Forbidden — use jobs.unicef.org only

### WHO Taleo (careers.who.int)
- **URL:** https://careers.who.int/careersection/ex/jobsearch.ftl
- **Access:** 🔵 browser_navigate (JS SPA, requires clicking "View All Jobs")
- **⚠️ web-clean.py FAILS** — returns only login/session timeout page, zero job data
- **Job count:** 45 total (1-25 shown)

### UNESCO Careers (careers.unesco.org)
- **URL:** https://careers.unesco.org/search/result
- **Access:** 🔵 browser_navigate (JS SPA with table layout)
- **Also:** 🟡 `web-clean.py` works partially — returns table with 25 results (59 total, 3 pages)
- **Key insight:** web-clean.py output contains structured table data (Title/Location/Type/Grade/Closing date) — usable for batch extraction

### ITU Careers (jobs.itu.int)
- **URL:** https://jobs.itu.int
- **Access:** 🔵 browser_navigate (JS SPA)
- **🔴 web-clean.py FAILS** — returns only cookie consent + navigation text

### IAEA Taleo (iaea.taleo.net)
- **URL:** https://iaea.taleo.net/careersection/ex/jobsearch.ftl
- **Access:** 🔵 browser_navigate (JS SPA)
- **🔴 iaea.org/careers BLOCKED** — Cloudflare challenge page

### UNHCR Workday (unhcr.wd3.myworkdayjobs.com)
- **URL:** https://unhcr.wd3.myworkdayjobs.com/en-GB/External
- **Access:** 🔵 browser_navigate
- **⚠️ Returns minimal content** — page loads but renders nearly empty generic element
- **UPDATE 2026-05-18:** IT job family filter returns "0 JOBS FOUND". General listing shows no ICT/AI roles. UNHCR currently has no relevant ICT/AI vacancies.

### IOM Oracle Cloud
- **URL:** https://fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs
- **Access:** 🔵 browser_navigate (no login needed)
- **Job count:** 174+ openings
- **UPDATE 2026-05-18:** Direct deep links trigger 400 Bad Request. Use clean entry URL and navigate/search manually or use UN JobNet as proxy.

### UNOPS Careers (careers.unops.org)
- **URL:** https://careers.unops.org/careersmarketplace/SearchJobs
- **Access:** 🟢 web-clean.py works — returns job listings with title, location, level, deadline
- **UPDATE 2026-05-18:** Search for "AI" returns relevant results including AI Adoption Coordinator and AI Centre of Excellence Lead. Pagination shows 80+ total jobs.

### UNDP Jobs (jobs.undp.org)
- **URL:** https://jobs.undp.org/cj_view_jobs.cfm
- **Access:** 🟢 web-clean.py works — returns full job listings
- **UPDATE 2026-05-18:** Search for "Digital AI ICT" returns results. Most ICT roles are NPSA (national) level. Key international roles: Data Science Associate (Brasilia, NPSA-7), Enterprise Data Architecture Analyst (Chisinau, NPSA-9). No new P-level ICT roles found.

### UNESCO Careers (careers.unesco.org)
- **URL:** https://careers.unesco.org/search/
- **Access:** 🟢 web-clean.py works — returns structured table data
- **UPDATE 2026-05-18:** Search for "Digital AI ICT" returns 21 results. Most are internships, nationals-only, or junior. One notable: Associate Research Scientist (Applied AI), P-2, ICTP Trieste, Italy, deadline 27/5/2026.

### WHO Taleo (careers.who.int)
- **URL:** https://careers.who.int/careersection/ex/jobsearch.ftl
- **Access:** 🔵 browser_navigate (JS SPA, requires clicking "View All Jobs")
- **⚠️ web-clean.py FAILS** — returns only login/session timeout page, zero job data
- **Job count:** 48 total (as of 2026-05-18)
- **UPDATE 2026-05-18:** Search for "Digital" returns 8 results. All already in tracker. "AI" and "ICT" searches return 0 results on WHO Taleo.

### ITU Careers (jobs.itu.int)
- **URL:** https://jobs.itu.int
- **Access:** 🔵 browser_navigate (JS SPA)
- **🔴 web-clean.py FAILS** — returns only cookie consent + navigation text
- **UPDATE 2026-05-18:** Search for "Digital" returns 30 results (25 per page). All already in tracker. No new ICT-relevant roles since last scan.

### COE Talents (talents.coe.int)
- **URL:** https://talents.coe.int/en_GB/careersmarketplace/SearchJobs
- **Access:** 🟢 web-clean.py works partially
- **UPDATE 2026-05-18:** Search returns limited results. IT Officer (Chisinau) is local recruitment only. Head of AI and Data Protection Division (COE-1234/2026-AI) already in tracker.

### Impactpool (impactpool.org)
- **URL:** https://www.impactpool.org/search?q=ICT&organization_type=United+Nations+System
- **Access:** 🔵 browser_navigate (JS-rendered)
- **UPDATE 2026-05-18:** Search for "ICT" with UN System filter returns 138 jobs. Many are already in tracker. Notable new leads: Chief Information Technology Service (UNOV, D-1, Vienna), SENIOR INFORMATION SYSTEMS OFFICER (UNEP, P-5, Nairobi), Director IT and Digital Transformation (CIMMYT). Impactpool is unreliable — always verify on official portal.

### UNJobNet (unjobnet.org)
- **URL:** https://www.unjobnet.org/jobs?query=ICT+Digital+AI
- **Access:** 🔵 browser_navigate (JS-rendered Vue.js SPA)
- **UPDATE 2026-05-18:** Search results render client-side. Filter for "United Nations System" available. Shows 3,387+ total jobs. ICT/AI filtering requires browser interaction.

---

## ❌ CONFIRMED INACCESSIBLE (Live-Tested 2026-05-18)

| Source | URL | Status | Reason |
|--------|-----|--------|--------|
| World Bank CSOD | worldbankgroup.csod.com | 🔴 Empty | JS SPA fails to render. API requires SAML auth. No public access. |
| IAEA (main) | iaea.org/careers | 🔴 Cloudflare | Security challenge |
| UNECE | unece.org/careers | 🔴 Cloudflare | "You have been blocked" |
| IMF | imf.org/en/about/recruitment | 🔴 403 | Access denied via curl. Browser shows portal only (no job listings). |
| WMO | wmo.int/jobs | 🔴 Redirect | e-recruitment URLs redirect back to wmo.org/jobs |
| OSCE | osce.org/careers | 🔴 Timeout | Page timed out |

## ✅ NEWLY CONFIRMED ACCESSIBLE (2026-05-18)

### FAO RSS Feed
- **URL:** https://jobs.fao.org/careersection/feed/joblist.rss?lang=en&portal=8105120163&searchtype=3&f=null&s=1|D&a=null&multiline=true
- **Access:** 🟢 curl — returns clean XML, ~11 most recent jobs
- **Parsing:** Split by `<item>`, extract `<title>`, `<link>` (contains job ID), `<pubDate>`, `<description>`
- **Job detail URLs:** `https://jobs.fao.org/careersection/fao_external/jobdetail.ftl?lang=en&job=XXXXXXX`
- **Vacancy ID format:** `FAO-XXXXXXX` (7-digit job number from URL)
- **Note:** This is the MOST RELIABLE FAO source. No browser needed.

### ICAO Careers (SSL issue resolved)
- **URL:** https://icaocareers.icao.int/careers/Home/Vacancies
- **Access:** 🔵 browser_navigate — renders HTML tables with job data
- **Sections:** Professional/higher categories, General service, Consulting, YAPP
- **Columns:** Title, Position level, Job ID, Location, Deadline
- **Vacancy ID format:** `ICAO-XXXXXX` (use Job ID from table)
- **Note:** Old URL `careers.imo.org` had SSL mismatch. Use `icaocareers.icao.int`.

### IMO Vacancy Portal (DNS issue resolved)
- **URL:** https://recruit.imo.org/
- **Access:** 🔵 browser_navigate — jobs rendered as button elements
- **Extraction:** `document.body.innerText` — buttons contain title, division, contract, deadline, ref
- **Vacancy ID format:** Use Vacancy Reference (e.g., `V.N. 26-08`, `CA 26-01`)
- **Note:** Old URL `careers.imo.org` had DNS failure. Use `recruit.imo.org`.
- **Note:** IMO jobs are mostly maritime/conference/admin — few ICT roles.

### UNCTAD — Use UN Inspira
- **URL:** https://inspira.un.org or https://careers.un.org
- **Note:** UNCTAD uses UN Secretariat staff selection system. No dedicated career portal.
- **Note:** unctad.org/employment page links to UN Careers portal.

---

## ⚙️ web-clean.py EFFECTIVENESS (Definitive 2026-05-14 Test)

**✅ WORKS:**
- UNESCO listing — full table data for 25 results
- UNICEF listing — partial HTML with job titles/locations/deadlines
- UNDP (jobs.undp.org/cj_view_jobs.cfm) — full job listings

**❌ FAILS:**
- WHO Taleo — returns only session/login page
- ITU careers — returns only cookie banner + navigation
- World Bank / WFP — marketing content only, no jobs
- UNICEF detail pages — requires browser session cookies

**📌 KEY LESSON:** `web-clean.py` is supplementary for UNESCO/UNICEF listings. **`browser_navigate` is the primary tool** for 80%+ of UN career portals.

---

## 📅 Third-Party Platform Summary

| Platform | Used By | Browser Extractable |
|----------|---------|-------------------|
| Taleo (Oracle) | WHO, IAEA | ✅ Yes |
| Workday | UNHCR | ⚠️ Partial (needs search click) |
| Oracle Cloud HCM | IOM | ✅ Yes |
| Talents | COE | ✅ Yes |
| SuccessFactors | UNESCO, ILO | ⚠️ Not tested |
| CSOD | World Bank | ❌ Empty |
| PageUp | UNICEF | ✅ Yes |
