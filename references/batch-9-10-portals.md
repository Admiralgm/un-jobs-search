# Batch 9-10 Portal Extraction Guide

## Batch 11: UNOV, UNON — ✅ COMPLETE (2026-05-22)
- **UNOV** (unov.org/careers): 404 — no standalone portal
- **UNON** (unon.org/careers): 404 — no standalone portal
- **Result**: Both redirect to INSPIRA. All professional vacancies covered in Batch 12.
- **New entries**: 0

## Batch 10: NATO, ECB, ESA — ✅ COMPLETE (2026-05-22)
- **NATO**: 4 ICT entries added (CIS Security AX050, Head E&IT Division, ICT Solution Engineer, Programme Manager IPS)
- **ECB**: 5 ICT entries added (AI Adoption Lead, AI Enterprise Architect, Digital Euro PM ×3)
- **ESA**: ⚠️ BLOCKED — jobs.esa.int JS SPA doesn't render in browser or web-preclean. All vacancies require JS execution. Skip until headless Chrome/Playwright available.
- **Key finding**: ECB AI Adoption Lead (🟠 88) and AI Enterprise Architect (🟠 86) close May 25 — STRONG FIT for candidate's AI/LLM profile

## Batch 9: UNU, UNIDIR, UNGM, GICHD — ✅ COMPLETE (2026-05-22)

### UNU — United Nations University
- **URL**: https://careers.unu.edu/
- **Access**: Camoufox/browser_navigate works. Page renders JS SPA.
- **Grading**: PSA system (PSA-5 ≈ P-4, PSA-6 ≈ P-5)
- **Extraction**: browser_navigate to listing page, then browser_snapshot for structure. ~10 listings visible.
- **⚠️ DEADLINES NOT ON LISTING PAGES**: The UNU listing page shows titles, locations, grades but NO deadlines. Must visit each job detail page individually to extract deadlines. Use `browser_console(expression="document.body.innerText.match(/(?:deadline|closing|apply by|until|closing date)[:\s]*([^\\n]+)/gi)")` for reliable extraction.
- **ICT-relevant roles found**: Geospatial Application and Data Analytics Associate (PSA-5, deadline 2026-05-24), Research Fellow & Academic Associate (PSA-6, deadline 2026-05-31)
- **Excluded**: Library Internship (internship), Junior Research Consultants (junior), Risk Modelling Associates (not ICT), Adjunct Professor/Researcher (roster, not ICT), Assistant for MIDORI (CTC1, junior), Consultant CTC4 (not ICT), Programme Assistant PSA2 (too junior)
- **Vacancy ID format**: UNU has NO standardized numeric ID system. Use slug-based IDs derived from the job URL path: `UNU-INWEH-PSA5-GEO`, `UNU-IAS-PSA6-IVE`. Pattern: `UNU-{INSTITUTE}-{GRADE}-{SHORT-SLUG}`.

### UNIDIR — UN Institute for Disarmament Research
- **URL**: https://www.unidir.org/jobs → redirects to https://unidir.org/who-we-are/join-our-team/
- **Access**: Browser accessible, limited listings (~3)
- **Result**: All positions were entry-level/trainee — no qualifying roles
- **Recommendation**: Skip in future scans unless specifically asked. Very few roles, rare ICT relevance.

### UNGM — UN Global Marketplace
- **URL**: https://www.ungm.org/
- **Result**: Procurement/tender portal only, no staff vacancies
- **Recommendation**: SKIP. All professional UN vacancies are on INSPIRA or agency portals.

### GICHD — Geneva International Centre for Humanitarian Demining
- **URL**: https://www.gichd.org/the-gichd/job-opportunities/
- **⚠️ IMPORTANT**: `/jobs/` redirects to login page. Always use `/the-gichd/job-opportunities/`
- **Access**: Browser_navigate works. Static HTML content, ~5 listings.
- **ATS**: Uses Beehire (app.beehire.com) for job detail pages. Each job has an invite URL like `https://app.beehire.com/invite/{code}`.
- **⚠️ BEEHIRE DEADLINE DISCREPANCY**: Beehire job pages show deadlines in TWO places: (1) a summary line near the top (e.g., "23 May 2026") and (2) an "Application Deadline:" field in the body text. These can differ by 1 day. **The "Application Deadline:" field in the body text is authoritative.** Always use `browser_console` to extract the full text and find the "Application Deadline:" line, not the summary badge.
- **Grading**: Senior/Professional level (Director, Advisor, Research Associate, Engineer)
- **Extraction**: browser_navigate to listing page for titles, then visit each Beehire invite URL for details. Use `browser_console(expression="document.body.innerText")` on Beehire pages.
- **ICT-relevant roles found (2026-05-22)**: Database Engineer (deadline 2026-05-23, but Ukraine location → EXCLUDE per Ukraine filter)
- **Excluded**: Advisor RISO (mine action domain, not core ICT), Director of ISU/APMBC (not ICT), Research Associate Blast & Fragmentation (not ICT), Consultant Ammunition Safety (not ICT)
- **Vacancy ID format**: No standardized ID system; use GICHD-{position-slug}
- **Salary info**: Some GICHD roles list salary (e.g., CHF 106,881/year gross for Advisor RISO). Include in entry when available.

---

## Batch 10: NATO, ECB, ESA

### NATO — North Atlantic Treaty Organization
- **URL**: https://www.nato.int/en/work-with-us/careers/vacancies
- **⚠️ IMPORTANT**: Old career URLs (e.g., careers.nato.int) return 404 or DNS failure. Use the URL above.
- **Access**: Browser_navigate works. 96+ vacancies total, paginated (20 per page, "Load more" button).
- **Grading**: NATO G-grade system (G7-G20). Mapping: G7 ≈ G-2, G10 ≈ P-3, G14 ≈ P-4, G17 ≈ P-5/D-1, G20 ≈ D-2
- **Extraction**: browser_snapshot shows listing with job title, grade, location, organization, deadline. Use "Load more" for pagination.
- **Nationality**: "Open to citizens of a NATO country" — CANDIDATE ELIGIBLE (Czech Republic NATO member since 1999). Note: some NATO roles specify "national delegation nomination required" — flag these with a note.
- **Key ICT roles identified**:
  - Principal Technical Officer OE078 (NSPA, Luxembourg) — closes 18 Jun 2026
  - CIS Security & COMSEC Officer AX050 (NSPA) — closes 16 Jun 2026
  - Head Engineering & IT Division (CMRE, La Spezia) — closes 21 Jun 2026
  - Head Engineering Branch (CMRE) — closes 21 Jun 2026
  - ICT Solution Engineer (NATO HQ, Brussels) — closes 21 Jun 2026
  - Senior Legal Counsel 260285 (DIANA, London) — closes 01 Jun 2026
  - Programme Manager IPS LN-1 (NSPA) — closes 28 Jun 2026
- **Vacancy ID format**: NATO reference codes (e.g., OE078, AX050, 260285)
- **Organizations**: NSPA, CMRE, DIANA, NATO HQ, NCIA — multiple NATO bodies post through the same portal

### ECB — European Central Bank
- **URL**: https://talent.ecb.europa.eu/careers
- **⚠️ IMPORTANT**: Old URL (ecb.europa.eu/careers) redirects to the new talent.ecb.europa.eu domain
- **Access**: Browser_navigate works. 12 vacancies across 2 pages.
- **Grading**: ECB uses AD system (AD5-AD11 ≈ P-2 to P-5+). Also FESA (Fixed-term Expert).
- **Nationality**: "EU nationals only" — CANDIDATE ELIGIBLE (Czech Republic EU member since 2004)
- **Extraction**: browser_snapshot shows listing. Job cards include title, grade, deadline, reference number.
- **Key ICT/AI roles identified**:
  - AI Adoption Lead (AI Office) — closes 25 May 2026 ⚠️
  - AI Enterprise Architect (AI Office) — closes 25 May 2026 ⚠️
  - Climate Scientist — closes 03 Jun 2026
  - Finance Expert Budgeting & Controlling — closes 02 Jun 2026
  - Financial Stability Expert (ESRB) — closes 03 Jun 2026
  - Lead Expert Market Infrastructure PM (Digital Euro) — closes 27 May 2026 ⚠️
  - Market Infrastructure Experts - Offline Tech (Digital Euro) — closes 09 Jun 2026
  - Market Infrastructure PM Specialists (Digital Euro) — closes 08 Jun 2026
  - Supervision Analyst (Operations & Integration) — closes 26 May 2026 ⚠️
- **Excluded**: Traineeships (2 positions)
- **Vacancy ID format**: ECB numeric reference codes

### ESA — European Space Agency
- **URL**: https://jobs.esa.int/
- **⚠️ BLOCKED (2026-05-22)**: JS SPA doesn't render in browser_navigate or web-preclean.py. Page loads but job results never appear. **Cannot extract ESA vacancies with current tooling.** Skip ESA in all future scans until headless Chrome/Playwright is available.
- **Previous reference data** (from skill file, not verified this session):
  - Grading: ESA A-grade system (A2 ≈ P-2, A4 ≈ P-4, A6 ≈ D-1)
  - Nationality: ESA member state nationals. Czech Republic is NOT an ESA member state but IS a cooperating state. Czech Republic is a NATO and EU member.. Check individual posting for nationality requirements.
  - ~31 vacancies, mostly engineering/space roles. ICT roles rare (PostDocs in AI/Cloud, some PM roles).
  - Vacancy ID format: ESA reference codes (e.g., ESA-2026-XXXX)