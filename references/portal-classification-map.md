# UN Job Portal Classification Map
# Last verified: 2026-05-18

## Accessible via web-clean.py (200, no browser needed)
| Portal | URL | Notes |
|--------|-----|-------|
| UNDP | jobs.undp.org/cj_view_jobs.cfm | **Only portal where web-clean.py returns actual job listings** (99+ jobs). |
| World Bank | worldbank.org/ext/en/careers | Returns landing page only. |
| UNICEF | jobs.unicef.org/en-us/listing/ | Returns filter/nav only. |
| WHO | who.int/careers | Returns landing page only. |

**CRITICAL FINDING (2026-05-13):** web-clean.py only extracts real job listings from UNDP. All other portals are JS-rendered SPAs. Use browser_navigate for all non-UNDP portals.

## Accessible via browser_navigate only
| Portal | URL | Notes |
|--------|-----|-------|
| **WHO Taleo** | careers.who.int/careersection/ex/jobsearch.ftl | 44+ jobs. No login. |
| **UNHCR Workday** | unhcr.wd3.myworkdayjobs.com/en-GB/External | 29+ jobs. No login. |
| **IAEA Taleo** | iaea.taleo.net/careersection/ex/jobsearch.ftl | 36+ jobs. Login: YOUR_EMAIL / YOUR_PASSWORD |
| **IOM Oracle Cloud** | fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs | 174+ jobs. No login. |
| **COE Talents** | talents.coe.int/en_GB/careersmarketplace/SearchJobs | 13+ jobs. Pagination via JS click. |
| **IMF Workday** | imf.wd5.myworkdayjobs.com/IMF | 12 jobs (non-ICT). Search works: add `?q=ICT`. Accept cookies first. |
| **World Bank CSOD** | worldbankgroup.csod.com/ux/ats/careersite/1/home?c=worldbankgroup | 32+ jobs. Search box ref=e148, search button ref=e100. Filter by country/date. **URL jobFamily params are IGNORED** — the site shows all jobs regardless of URL filter params. **BEST: Use Camoufox** (npm `camofox-browser` server + `CAMOFOX_URL` env var). Also works with Scrapling StealthyFetcher. |
| **ITU** | jobs.itu.int/search/?q=Digital&sortby=Relevancy | 30 jobs per search. Cookie banner must be dismissed. Page 2 via JS click (URL params don't work). **Use Camoufox for best results.** |
| **UNITAR** | unitar.org/vacancy-announcements | Consultant/roster positions. Accessible via scrapling stealthy-fetch. |
| **GICHD** | gichd.org/the-gichd/job-opportunities/ | 6+ vacancies. Uses Beehire platform for applications. |
| **UNICRI** | unicri.org/institute/join_us/jobs | Join us page. Extract job listings from HTML h2/h3 tags. |
| **UNWTO** | untourism.int/work-with-us | Employment conditions + JPO programme. Site migrated from unwto.org to untourism.int. |
| **WMO** | wmo.int/jobs | Career categories page (Professional, General Service, JPO, Interns). No direct listings. |
| **UNSSC** | unssc.org/about/employment-opportunities | Employment opportunities page. Extract from HTML. |
| **FAO** | fao.org/employment/home/en/ | JPO and Young Professionals Programme. Also uses Inspira for full listings. |
| **UNCTAD** | unctad.org/employment | Info page only. Uses UN Inspira system (careers.un.org). Site rebranded from old unctad.org structure. |

## Accessible via scrapling stealthy-fetch only (not web-clean.py, not browser)
| Portal | URL | Notes |
|--------|-----|-------|
| **IMF Workday** | imf.wd5.myworkdayjobs.com/IMF/search?q=ICT | Same as browser but fetches HTML. 350KB JS-rendered. Content in body.innerText via browser JS execution. |
| **UNICRI** | unicri.org/institute/join_us/jobs | JS-rendered. Use stealthy-fetch to get raw HTML, extract h2/h3 tags. |
| **UNITAR** | unitar.org/vacancy-announcements | JS-rendered. stealthy-fetch returns full HTML with job links. |
| **GICHD** | gichd.org/the-gichd/job-opportunities/ | JS-rendered. stealthy-fetch works. |
| **UNWTO** | untourism.int/work-with-us | Migrated domain. stealthy-fetch works. |
| **WMO** | wmo.int/jobs | stealthy-fetch works. |
| **UNSSC** | unssc.org/about/employment-opportunities | stealthy-fetch works. |
| **FAO** | fao.org/employment/home/en/ | stealthy-fetch works. |
| **UNITAR** | unitar.org/vacancy-announcements | stealthy-fetch works. |
| **UNECA** | uneca.org | Main site accessible. Careers link → UN Inspira. |
| **UNESCAP** | unescap.org | Main site accessible. Careers link → UN Inspira. |
| **UNIDIR** | unidir.org | Main site accessible. |

## Cloudflare-Blocked (stealthy-fetch returns 403)
| Portal | URL | Notes |
|--------|-----|-------|
| **UNECE** | unece.org | ALL paths return 403. Completely behind Cloudflare. |
| **UNESCWA** | unescwa.org | ALL paths return 403. Completely behind Cloudflare. |
| **UN Careers** | careers.un.org | Returns 403 via CloudFront. Inspira system not accessible. |

## Removed from active scanning
| Portal | URL | Block type | Status |
|--------|-----|------------|--------|
| UN Women | unwomen.org/careers | 403 Forbidden | Removed |
| IDB | iadb.org/careers | Cloudflare | Removed |

## Old URLs → New Platforms
| Agency | Old URL | Working URL |
|--------|---------|-------------|
| COE | coe.int/jobs | talents.coe.int/en_GB/careersmarketplace/SearchJobs |
| IOM | iom.int/careers | fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs |
| UNHCR | unhcr.org/careers | unhcr.wd3.myworkdayjobs.com/en-GB/External |
| WHO | who.int/careers | careers.who.int/careersection/ex/jobsearch.ftl |
| IAEA | iaea.org/careers | iaea.taleo.net/careersection/ex/jobsearch.ftl |
| UNWTO | unwto.org/careers | untourism.int/work-with-us |
| UNCTAD | unctad.org/careers (old) | unctad.org/employment (new, rebranded site) |

## Key Rules
1. **web-clean.py only works for UNDP** — all other portals need browser or stealthy-fetch
2. **stealthy-fetch CLI syntax**: `scrapling extract stealthy-fetch <URL> <OUTPUT_FILE>` — requires output file argument
3. **Workday portals** (IMF, UNHCR, WHO): Use browser_navigate. Content loads via JS after page load. Search via URL params `?q=KEYWORD`.
4. **CSOD portals** (World Bank): Use browser_navigate. Search box and filters available after page load.
5. **Taleo portals** (IAEA, WHO): Use browser_navigate. Keyword search in textbox ref=e36/e10.
6. **Cloudflare sites** (UNECE, UNESCWA, careers.un.org): Cannot be scraped. Report as BLOCKED.
7. **Impactpool is UNRELIABLE** — always verify on official portal
8. **UN Inspira** (careers.un.org): CloudFront-blocked. Agencies using it (UNCTAD, UNOV, UNON, FAO) must be checked via their own career pages or Impactpool proxy.
