# UN/IO Career Portal Directory — Scan Results (Updated 2026-05-30)

## Key URL Corrections (May 30)
- **OECD:** careers.smartrecruiters.com/OECD (was jobs.smartrecruiters.com/OECD, now 404)
- **WTO:** careers.smartrecruiters.com/WTO
- **INSPIRA ITECNET pre-filtered URL:** `https://careers.un.org/jobopening?language=en&data=%7B%22jn%22:[%22ITECNET%22],%22jf%22:[],%22jc%22:[],%22jle%22:[]%7D`
- **INSPIRA alternative (all jobs, manual filter):** `https://careers.un.org/jobopening?language=en&data=%257B%2522aoe%2522:%255B%255D,%2522aoi%2522:%255B%255D,%2522el%2522:%255B%255D,%2522ct%2522:%255B%255D,%2522ds%2522:%255B%255D,%2522jn%2522:%255B%255D` — must manually check ITEC NET checkbox

## Organization → Portal Mapping (Verified 2026-05-30)

### Batch 1 — UNICEF
| Org | URL | Platform | ICT Roles? | Extraction Notes |
|-----|-----|----------|------------|-----------------|
| UNICEF | jobs.unicef.org/en-us/listing/ | PageUp Custom | Yes — AI, digital, ICT | Search box + Enter filters. DOM extraction. "More Jobs" flaky. Better: keyword search per term, extract from DOM, filter in Python. |

### Batch 2 — FAO
| Org | URL | Platform | ICT Roles? |
|-----|-----|----------|------------|
| FAO | jobs.fao.org (Taleo) + RSS | Taleo + RSS | 83 jobs. Salesforce, Data Mgmt. |

### Batch 3 — WHO, ITU
| Org | URL | Platform | ICT Roles? | Notes |
|-----|-----|----------|------------|-------|
| WHO | careers.who.int | Taleo | 46 jobs. AI Software Eng Lead P4, Data Eng Developer, GIS Spec. |
| ITU | jobs.itu.int | SuccessFactors | 33 jobs. Green Digital, Digital Ecosystem, SW Dev, Cyber, Telecom/ICT Stats Roster. |

### Batch 4 — UNESCO, ILO, ICAO, IMO
| Org | URL | Platform | ICT Roles? | Notes |
|-----|-----|----------|------------|-------|
| UNESCO | careers.unesco.org | SuccessFactors | /search/?q=keyword. Front-end Dev, DevOps, ICT Assistant. |
| ILO | jobs.ilo.org | Custom SPA | Director CIO (D2). "View all jobs" link. |
| ICAO | icaocareers.icao.int | Oracle HCM | BI Developer. ⚠️ Camoufox click crash. |
| IMO | recruit.imo.org | **SKIP** | ~8 non-IT only. |

### Batch 5 — IMF, WTO, UNOPS, OECD, ECB
| Org | URL | Platform | ICT Roles? | Notes |
|-----|-----|----------|------------|-------|
| IMF | imf.wd5.myworkdayjobs.com/IMF | Workday | 13 jobs. IT Strategist, Data Engineer. |
| WTO | careers.smartrecruiters.com/WTO | SmartRecruiters | Very few openings. |
| UNOPS | careers.unops.org | Custom ICS | 21 total. AI Geo Data Science Advisor, App Mgmt Lead. |
| OECD | careers.smartrecruiters.com/OECD | SmartRecruiters | ~80 jobs. Deputy Head Digital Workplace. |
| ECB | talent.ecb.europa.eu/careers | Custom | EU nationals-only. |

### Batch 6 — Tiered/Marginal Portals (TESTED 2026-05-30)
| Org | URL | Platform | ICT Roles? | Notes |
|-----|-----|----------|------------|-------|
| UNDP | jobs.undp.org/cj_view_jobs.cfm | Oracle HCM | Few P-level. Mostly NPSA. Keyword filter works. |
| WFP | wd3.myworkdaysite.com | Workday | 100 jobs/5 pages. Full-stack dev (Rome). Accept cookies. |
| UNHCR | unhcr.wd3.myworkdayjobs.com | Workday | **SKIP** — 0 ICT prof roles all cycles. |
| World Bank | worldbankgroup.csod.com | CSOD | **FAIL** — Empty in browser. Use Scrapling. |
| UNFPA | www.unfpa.org/jobs | Oracle HCM | Low ICT. Mostly health. Search works. |
| ICMPD | careers.icmpd.org | Custom | HR IS & Auto Officer (IP3). search/?q= EMPTY — use base URL. |
| UNITAR | unitar.org/vacancy-announcements | CMS | Roster only. EdTech/AI Learning, Geospatial Analysts. |
| UNU | careers.unu.edu | Custom | Geospatial PSA-5. |
| GICHD | gichd.org/.../job-opportunities/ | Custom/Beehire | No ICT found. Consider dropping. |
| UNDRR | undrr.org/.../work-us | → INSPIRA | |
| WMO | Oracle HCM | 0 ICT prior. | |
| UNESCAP | unescap.org/jobs | → INSPIRA | |
| UNESCWA | unescwa.org/.../jobs | → INSPIRA | |
| UNICRI | unicri.org/.../vacancies | → INSPIRA | |

### Batch 7 — INSPIRA
| Org | URL | Platform | Notes |
|-----|-----|----------|-------|
| INSPIRA | careers.un.org (ITECNET URL) | UN Sec | ~15 ICT jobs. body.innerText on detail (Expand All first). |

### Batch 8 — Impactpool, UNJobNet (SKIPPED per user instruction)

### Batch 10 — All Tested Portals (2026-05-30) — ALL kept in scan rotation
| Org | URL | Platform | ICT Roles? | Notes |
|-----|-----|----------|------------|-------|
| WIPO | wipo.int/.../wipo-jobs | Custom JS | **CAMOUFOX CRASH** — JS buttons crash Camoufox. Needs Scrapling. HIGH priority. |
| UNIDO | careers.unido.org/search/?q=Digital | SuccessFactors | Sr Process Transformation & AI Integration Expert (Vienna, ISA-P5). |
| IFAD | www.ifad.org/en/work-with-us | → PeopleSoft | External link to job.ifad.org. Keep scanning. |
| UNDP | jobs.undp.org/cj_view_jobs.cfm | Oracle HCM | Enterprise Data Architecture Analyst (NPSA-9). Mostly NPSA. Keep scanning. |
| UNITAR | unitar.org/vacancy-announcements | Custom CMS | EdTech/AI for Learning roster, Geospatial roster. Keep scanning for P-level. |
| GICHD | gichd.org/the-gichd/job-opportunities/ | Custom + Beehire | Links to external Beehire. Keep scanning. |
| UNFPA | www.unfpa.org/jobs | Oracle HCM | Health mandate. Low ICT yield. Keep scanning. |
| ICMPD | careers.icmpd.org | Custom | HR IS & Automation Officer (IP3). search/?q= empty — use base URL. Keep scanning. |
| UNHCR | unhcr.wd3.myworkdayjobs.com | Workday | 0 ICT professional roles across all cycles. Keep scanning — org changes. |
| IMO | recruit.imo.org | Custom JS | ~8 non-IT jobs. Keep scanning. |
| ICRC | careers.icrc.org/go/All-Jobs/3807301/ | SuccessFactors | ANAPLAN Model Builder, BI Reporting Analyst, Information Management Officer. ⚠️ Triple-rendering dedup bug. RSS feed available. |
| UNEP/UNODC/OHCHR | → careers.un.org | INSPIRA | Covered by Batch 7. Add org filter explicitly. |
| UNESCAP/UNESCWA/UNDRR/UNICRI | → careers.un.org | INSPIRA | Covered by Batch 7 INSPIRA scan. |

## Grade Equivalences
| Org | Grade | ≈UN Level |
|-----|-------|-----------|
| UN/UNU | PSA-5 | P-4 |
| UN/UNU | PSA-6 | P-5 |
| OECD | CF6 | P-4/P-5 |
| ICMPD | IP3 | P-3 |
| ICMPD | LP4 | P-4 |
| NATO | G10 | ≈P-3 |
| NATO | G14 | ≈P-4 |
| IMF | A11/A12 | Mid-professional |

## Exclusion Rules
- Ukraine, Internships, NO-grade (nationals-only), expired, score < 50 → EXCLUDE
