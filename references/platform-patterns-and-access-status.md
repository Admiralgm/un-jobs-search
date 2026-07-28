# UN Job Portals — Platform Patterns & Access Status

**Purpose:** Quick-reference for portal access methods, platform types, and known quirks.
**Updated:** 2026-05-23 (after Batches 1–5)
**Main skill:** `un-jobs-search-minimaltoken`

---

## Platform Types (Behavior Patterns)

### Workday Platform
**Portals:** WFP, IMF, UNHCR, WTO
**URL pattern:** `*.myworkdayjobs.com/*` or `*.wd*.myworkdayjobs.com/*`
**Camoufox:** ✅ Renders full job list
**Search:** URL params `?keyword=XXX` or `?jobFamily=XXX` work but may return all results regardless — filter client-side
**Job ID format:** `JR` prefix (e.g., JR123148) for WFP/WTO; `R` prefix (e.g., 26-R9262) for IMF
**Cookie consent:** Auto-handled by Camoufox
**Pagination:** Standard Workday pagination, usually 1 page for filtered results

### Taleo Platform
**Portals:** FAO, IAEA, WHO
**URL pattern:** `*.taleo.net/careersection/*`
**Camoufox:** ✅ Renders full job list
**Search:** `?keyword=XXX` works. "digital" (18 FAO), "software" (16 FAO), "information technology" (7 FAO)
**Job ID format:** 7-digit numeric (FAO: 2601132)
**Note:** FAO "Information Systems and Technology" category has only 2 jobs — most ICT roles are in other divisions (CSI Digital, OIG Audit)

### Oracle HCM Platform
**Portals:** UNFPA, IOM, WMO
**URL pattern:** `estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_XXXX/*`
**Camoufox:** ✅ Renders full job list
**Search:** `?keyword=ICT` filters correctly (unlike main UNFPA site which is broken)
**Job ID format:** Numeric (UNFPA: 34430, 34109)
**Note:** UNFPA main site unfpa.org/jobs keyword search is BROKEN — always use Oracle HCM backend

### SmartRecruiters Platform
**Portals:** OECD
**URL pattern:** `careers.smartrecruiters.com/OECD/*`
**Camoufox:** ✅ Renders full job list
**Search:** oecd.org/careers page is informational only — use direct SmartRecruiters URL
**Job ID format:** REF prefix (e.g., REF3052Q)
**Note:** 13 total jobs across 4 departments. ICT roles rare (1-2 per cycle)

### CSOD Platform
**Portals:** World Bank
**URL pattern:** `worldbankgroup.csod.com/ux/ats/careersite/*`
**Camoufox:** ❌ JS SPA fails to render job list — shows only skeleton
**web-preclean.py:** ❌ Returns empty
**Status:** Known broken. Skip or try Scrapling StealthyFetcher.

### Custom/Proprietary Platforms
**ICMPD:** ASP.NET careers portal at careers.icmpd.org. 24 jobs, 2 pages. VA-format IDs (VA26P###V##). IP/LP/S grade system.
**ILO:** jobs.ilo.org. Camoufox renders. Director-level ICT roles found.
**UNESCO:** careers.unesco.org. Camoufox renders 57 jobs. Mostly internships/junior.
**UNOPS:** careers.unops.org. Camoufox renders 21 jobs. AI roles found.
**ICAO:** icaocareers.icao.int. HTML tables. BI Developer role found.
**IMO:** recruit.imo.org. Camoufox renders 10 jobs. V.N./CA/STA reference format.
**UNICEF:** jobs.unicef.org. Camoufox crashes on browser_type — use browser_console JS extraction.
**ESA:** jobs.esa.int. Camoufox renders with direct keyword URL: `jobs.esa.int/search/?q=ICT`. A2-A6 grade system. PostDocs excluded unless exceptional AI match. Confirmed working 2026-05-23 (was previously misclassified as blocked).
**NATO:** nato.int/en/work-with-us/careers/vacancies. Camoufox renders 96+ jobs, paginated. Filter by "Information Systems and Technology" employment area. G7-G20 grades.

---

## Confirmed INSPIRA-Only (No Standalone Portal)
UNCTAD, UNECE, UNECA, UNESCWA, UNWTO, UPU, UNDRR, UNICRI, UNSSC, UN-Habitat, WMO (partially)
→ All professional vacancies on INSPIRA → covered in Batch 7 (INSPIRA)

## Confirmed 404 (Career Pages Gone)
WIPO, ICAO (old), UNFPA (old), UNDRR, UNITAR, UNSSC, GICHD (old), UNOV, UNON, UNECA, UNESCAP, UNESCWA, UNWTO, WMO (old)
→ Either moved to new platforms or use INSPIRA

## Nationality Restrictions
- **OECD:** Nationals of OECD member countries only. Czech Republic joined OECD in 1995 → ELIGIBLE
- **ECB:** EU nationals only → ELIGIBLE (Czech/EU citizenship)
- **NATO:** NATO member citizens → ELIGIBLE (Czech Republic NATO member since 1999)
- **ICMPD:** Open to all nationalities (no restriction noted)

## Grade Equivalents
| Organization | Grade | Approx. UN Equivalent |
|---|---|---|
| OECD | CF6 | P-4/P-5 |
| ICMPD | IP1 | P-1/P-2 (junior) |
| ICMPD | IP2 | P-2/P-3 |
| ICMPD | IP3 | P-3 |
| ICMPD | IP4 | P-4 |
| ICMPD | LP2-LP4 | P-3 to P-5 |
| IMF | A11/A12 | P-3/P-4 |
| NATO | G10 | P-3 |
| NATO | G14 | P-4 |
| NATO | G17 | P-5/D-1 |
| FAO/UNESCO/ILO | P-3 to D-2 | Standard UN grading |
| UNICEF | P-3 to D-2 | Standard UN grading |
