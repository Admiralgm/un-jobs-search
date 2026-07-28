# Batch 4/5/6 Portal Notes — 2026-05-26

## UNESCO SuccessFactors
- **Working URL:** `careers.unesco.org/go/All-jobs-openings-US/782502/` (54 jobs, 3 pages)
- **JS extraction issue:** `browser_console` with `querySelectorAll('table tbody tr')` returned empty array despite visible table. Use `browser_snapshot` (full=True) to extract data instead.
- **Pagination:** Pages 2-3 via URL `/25/` and `/50/` suffixes
- **Key ICT roles found (2026-05-26):**
  - Associate Research Scientist (Applied AI), P-2, Trieste, DL 2026-05-27 (vid: 1359193257)
  - Senior Project Officer (Standards & Data Integration), P-4, Canada, DL 2026-06-12 (vid: 1361719057)
  - Consultoría Tecnologías inclusivas e Inteligencia Artificial, Chile, DL 2026-06-05 (vid: 1360698057)
- **Excluded:** All Ukraine-located roles, all internships, NO-grade nationals-only

## ILO (jobs.ilo.org)
- **URL:** `jobs.ilo.org/go/All-Jobs/2842101/` — Taleo, 16 jobs, 2 pages
- **Key ICT role (2026-05-26):**
  - Director, Information & Technology Management Dept (CIO/CITO), D-2, Geneva, DL 2026-06-15 (vid: 13630)
- **Note:** Most roles field-based/NO-grade; D-2 ICT role is rare

## IMF Workday
- **URL:** `imf.wd5.myworkdayjobs.com/IMF` — 11 jobs total
- **ICT roles (already in tracker):** Data Engineer (26-R9271), IT Strategist (26-R9262)
- **Note:** All ICT roles Contractual (DC), score < 55 for candidate profile

## WTO Workday
- **URL:** `wto.wd103.myworkdayjobs.com/External` — 5 jobs total
- **ICT role (already in tracker):** Digital Learning Technology Specialist, Grade 7 (JR104152)
- **Cookie banner:** Requires clicking "Accept Cookies" before content loads

## UNOPS Careers Marketplace
- **URL:** `careers.unops.org/careersmarketplace/SearchJobs` — 88+ jobs, 15 pages
- **Cookie banner:** Click "Accept all" before scanning
- **Key ICT roles (already in tracker):**
  - AI Centre of Excellence Lead, Senior, Copenhagen/Home, DL 2026-05-26
  - AI Adoption Coordinator, Mid Level, Copenhagen, DL 2026-05-26

## Batch 6 (scanned 2026-05-25, skipped per incremental protocol)
- UNDP: No ICT (mostly empty)
- WFP: Data Privacy Specialist expired May 25
- UNHCR: IT family returns 0
- UNFPA: Oracle HCM, keyword broken
- ICMPD: 2 ICT already in tracker
- UNITAR: Roster EdTech/AI, ongoing deadlines
- UNU: PSA grades, no deadlines on listing
- GICHD/UNDRR/WMO/UNESCAP/UNESCWA/UNICRI: No new ICT

## Scoring Notes (2026-05-26)
- UNESCO Applied AI P-2: score 57 (🟡 STRETCH) — low seniority but strong AI match
- ILO IT Director D-2: score 67 (🟡 STRETCH) — excellent seniority + strategic
- UNOPS AI Centre of Excellence Lead: score 66 (🟡 STRETCH) — strong AI + seniority
- IMF contractual roles: score <55 (🟢 LOW FIT) — DC-based, not strategic match
- WTO Grade 7: score <55 (🟢 LOW FIT) — below target grade

## Tracker Write Technique Fixes (2026-05-26)
- **f-string int bug:** `f"{i:<5s}"` fails with `ValueError: Unknown format code 's' for object of type 'int'`. Always use `str(i).ljust(5)`.
- **Table row regex:** Use `re.findall(r'^\s*\d+\s+[A-Z]', content, re.MULTILINE)` with MULTILINE flag — without it, returns 0 matches.
- **Verification pattern:** After write, verify `table_rows == entry_blocks == total` using `re.MULTILINE` for both counts.
