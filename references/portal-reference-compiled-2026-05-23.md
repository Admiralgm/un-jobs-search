# UN Job Scan — Compiled Portal Reference (2026-05-23)

Migrated from the removed legacy companion skill. Portal-by-portal scan results,
URL discoveries, and platform migration notes for UN job scanning.

## SearXNG Discovery Results (2026-05-23)

| Organization | Old/Guessed URL | Correct URL | Method | Notes |
|---|---|---|---|---|
| WTO | wto.org/careers (404) | wto.wd103.myworkdayjobs.com/External | SearXNG | Migrated to Workday. JR-format IDs. Only 5 total jobs. |
| UNESCWA | unescwa.org/careers (404) | unescwa.org/about/jobs | SearXNG | 1 P4 role. Josour platform requires login. |
| UNESCAP | unescap.org/vacancies (404) | unescap.org/jobs | SearXNG | All jobs redirect to INSPIRA |
| UNOV | unov.org/vacancies (404) | careers.un.org (INSPIRA) | SearXNG + browser | No standalone portal |
| UNON | unon.org/vacancies (404) | careers.un.org (INSPIRA) | SearXNG + browser | No standalone portal |
| OECD | oecd.org/careers (info only) | careers.smartrecruiters.com/OECD/ | SearXNG | SmartRecruiters portal |
| UNICRI | unicri.org/jobs (404) | unicri.org/institute/join_us/jobs/vacancies | SearXNG | Has own portal. AI Centre in The Hague. |
| UNDRR | undrr.org/jobs (PreventionWeb) | undrr.org/about-undrr/work-us | SearXNG | Has own portal |
| GICHD | gichd.org/jobs (login) | gichd.org/the-gichd/job-opportunities/ | SearXNG | Beehire platform (app.beehire.com) |
| UNWTO | unwto.org/careers (404) | careers.un.org (INSPIRA) | Skill doc | No standalone portal |
| UPU | upu.int/vacancies | careers.un.org (INSPIRA) | Skill doc | Internships on erecruit.upu.int |
| UN-Habitat | unhabitat.org/join-us | careers.un.org (INSPIRA) | Skill doc | JS-rendered, empty |
| UNCTAD | unctad.org/careers | careers.un.org (INSPIRA) | Skill doc | Redirects to INSPIRA |
| UNECE | unece.org/careers | careers.un.org (INSPIRA) | Skill doc | Cloudflare-blocked |
| UNECA | uneca.org/careers (404) | careers.un.org (INSPIRA) | Skill doc | Redirects via bit.ly |

## Platform Migration Log

| Date | Organization | From | To |
|---|---|---|---|
| 2026-05-23 | WTO | wto.org (INSPIRA) | Workday (wto.wd103.myworkdayjobs.com) |
| 2026-05-23 | UNICRI | Assumed 404 | Has own portal (unicri.org/institute/join_us/jobs/vacancies) |
| 2026-05-23 | UNDRR | Assumed INSPIRA | Has own portal (undrr.org/about-undrr/work-us) |

## INSPIRA Keyword Search Results (2026-05-23)

| Keyword | Results | New P-grade ICT | Notes |
|---|---|---|---|
| Information Technology | 22 | 1 (OICT P5, 274439) | Most are UNJSPF, OCHA field, or already tracked |
| Artificial Intelligence | 11 | 0 | All consultants/interns |
| Information Systems | 9 | 0 | All UNJSPF or already tracked |
| Telecom | 3 | 0 | Broadcast/conferencing, not strategic ICT |

## Key Insight
Most INSPIRA ICT roles are UNJSPF (pension systems), OCHA (field humanitarian IM), or OICT (central IT ops). Strategic AI/LLM roles are rare on INSPIRA — most are consultant-grade or at specialized agencies (UNICEF, UNDP, etc.).

## Portal Access Methods (Confirmed Working)

| Platform | Sites | Camoufox | web-preclean.py |
|---|---|---|---|
| Workday | WTO, IMF, WFP, UNHCR, UNOPS | ✅ | ❌ |
| Taleo | WHO, FAO, IAEA | ✅ | ❌ |
| Oracle HCM | UNFPA, WMO | ✅ | ❌ |
| SmartRecruiters | OECD | ✅ | ❌ |
| CSOD | World Bank | ❌ (skeleton only) | ❌ |
| Beehire | GICHD | ✅ (direct URLs work) | ❌ |
| INSPIRA | UN Secretariat | ✅ | ❌ |
| Custom Drupal | UNICEF, UNU, ICMPD | ✅ | ❌ |
