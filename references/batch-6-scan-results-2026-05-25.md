# Batch 6 Scan Results — 2026-05-25

## Portals Scanned

| Portal | URL | Method | Total Jobs | ICT Found | Qualifying | Notes |
|--------|-----|--------|-----------|-----------|------------|-------|
| UNDP | undp.org/careers | browser | 0 | 0 | 0 | "No job postings at this time" |
| WFP | wd3.myworkdaysite.com/recruiting/wfp/job_openings | browser Workday | 113 | 2 | 1 | Data Privacy Specialist P3 (Rome) ✅; Sr IT Ops G7 (Jordan) — GS grade exclude |
| World Bank | worldbank.org/en/about/careers | blocked | — | — | 0 | JS SPA, no public listing |
| UNHCR | unhcr.wd3.myworkdayjobs.com/External | browser/curl Workday | ~50 | 1 | 0 | Only "Digital Visibility National Consultant" (not P-grade) |
| UNFPA | unfpa.org/jobs | browser Oracle HCM | ~25 | 0 | 0 | All Ukraine-based (exclude) or NO-grade nationals |
| ICMPD | careers.icmpd.org | browser | 20+ | 2 | 1 | Modernisation Officer AI & Automation IP2 (Valletta, DL Jun 3) ✅; Junior ICT Officer IP1 — Junior exclude |
| UNITAR | unitar.org/vacancy-announcements | web-preclean | 1 | 0 | 0 | Only Korean-English Interpreter |
| UNU | careers.unu.edu | web-preclean | 0 | 0 | 0 | Empty listing |
| GICHD | gichd.org/the-gichd/job-opportunities/ | web-preclean | ~5 | 0 | 0 | No ICT jobs |
| UNDRR | undrr.org/about-undrr/work-us | web-preclean | — | — | 0 | All jobs redirect to INSPIRA |
| WMO | wmo.int/careers | web-preclean | ~3 | 0 | 0 | No ICT jobs |
| UNESCAP | unescap.org/jobs | web-preclean | — | — | 0 | All jobs redirect to INSPIRA |
| UNESCWA | unescwa.org/about/jobs | web-preclean | ~2 | 0 | 0 | No ICT jobs |
| UNICRI | unicri.org/institute/join_us/jobs/vacancies | web-preclean | ~3 | 1 | 0 | Only Research Intern at Centre for AI & Robotics (intern = exclude); rest via INSPIRA |

## Qualifying Jobs Found

### 1. WFP — Data Privacy Specialist P3
- **JR:** JR122936
- **Location:** Rome, Italy
- **Grade:** P-3
- **Contract:** Fixed Term
- **Deadline:** 2026-05-25 ⚠️ TODAY
- **URL:** https://wd3.myworkdaysite.com/en-US/recruiting/wfp/job_openings/job/Rome-Italy/Data-Privacy-Specialist-P3_JR122936

### 2. ICMPD — Modernisation Officer – AI and Automation Support IP2
- **ID:** VA26P075V01
- **Location:** Valletta, Malta
- **Grade:** IP2 (International Professional)
- **Contract:** Staff (12 months)
- **Deadline:** 2026-06-03
- **URL:** https://careers.icmpd.org/Home/JobOpeningDetails?jobOpeningId=1122

## Key Learnings

1. **UNDP portal empty** — As of May 2026, UNDP has no job postings. Check back later.
2. **UNFPA keyword search broken** — All current listings are Ukraine-based or NO-grade.
3. **WFP Workday** — Search "digital" returns better results than "ICT" or "AI". Most ICT roles are G-grade or consultants.
4. **UNHCR Workday** — ICT/digital searches return only interns, consultants, and GS roles. No P-grade ICT.
5. **ICMPD grades** — IP grades (IP1, IP2) are International Professional (eligible). LP/S grades are Local (may have restrictions).
6. **Camoufox stale tab ID** — When camoufox server restarts mid-session, browser tools get stuck on stale tab ID. Use curl to REST API directly, or restart Hermes session.
