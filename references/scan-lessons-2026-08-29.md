# Scan Session Lessons — 2026-08-29

Verified operational facts from the 2026-08-29 full 27-portal scan (all tiers).

## run_workday.py requires a portal argument
`run_workday.py` defaults to `imf` only (line: `portal=sys.argv[1] if len(sys.argv)>1 else "imf"`).
A bare run does NOT cover WFP/UNHCR/WTO. For full coverage run all four:
```
run_workday.py imf ; run_workday.py wfp ; run_workday.py unhcr ; run_workday.py wto
```
WTO tenant uses CXS REST API; WFP/UNHCR use HTML Scrapling fetch. UNHCR Workday
scraper also exists standalone (run_unhcr.py) — both work; pick one.

## Workday deadline extraction (CXS JSON API)
The Workday HTML text layer DROPS the deadline value (label present, date missing).
Use the CXS JSON endpoint instead:
```
curl "https://wd3.myworkdaysite.com/wday/cxs/wfp/job_openings/job/<LOC>/<Title>_<JID>" \
  -H "Accept: application/json" -H "User-Agent: Mozilla/5.0"
```
→ `jobPostingInfo.endDate` is the deadline (ISO date). Works for WFP tenant;
  IMF tenant (`imf.wd5.myworkdayjobs.com/wday/cxs/imf/IMF/job/...`) analogous.

## Live deadline verification patterns (Scrapling StealthyFetcher.fetch — SYNC, not async)
- async_fetch returns a coroutine when called wrong; use `StealthyFetcher.fetch(...)`.
- UNICEF: `Deadline:?\n?\s*([0-9]{1,2}\s+[A-Z][a-z]{2}\s+[0-9]{4})` — plain curl gets no dates (JS-rendered).
- WHO careers: label `Closing Date : \xa0 Sep 4, 2026, 11:59:00 PM` →
  pattern `Closing Date\s*:?.*?([A-Z][a-z]{2}\s+[0-9]{1,2},\s+[0-9]{4})`.
- UNOPS JobDetail pages: two dates in a right-hand table = posted + closing;
  both dd-Mon-yyyy; closing is the LATER one.
- WMO OracleCloud: preview URL 302s to `/job/{id}`; `Apply Before MM/DD/YYYY, 11:59 PM`.
- UNESCO careers: `Application deadline (Midnight <TZ>) :` — value may be EMPTY
  at source (Brussels IOC Data/Info 1368246457 as of 2026-08-29). Never guess;
  report as unverified.
- World Bank CSOD: `Closing Date: 9/9/2026 (MM/DD/YYYY) at 11:59pm UTC` (page needs wait>=6000).
- OECD SmartRecruiters: bot-walled (813-byte challenge page) — unverified via stealth fetcher.
- UNDP jobs site: dead jobs return HTTP 404 on BOTH /careersection/ex_internal/jobdetail.ftl
  and /careersection/jobdetail.ftl patterns — 404 is a reliable expiry signal.

## Tracker rebuild (column-fixed format)
Open-section rows: `{n:<5}{org:<22}{title:<47}{dl:<15}{emoji} {score:<9}{vid:<30}{applied}`.
Title >44 visible chars → truncate to 43 + `…`. Parse-emoji regex: `([🔴🟠🟡🟢🔵❌⏸✅]) (\d+)`.
When renumbering existing rows via regex, replace only the leading token with
`str(n)` (no padding) or spacing shifts — fixed-width rebuild from parsed
fields is safer (proved 2026-08-29).

## Script results 2026-08-29 (for delta comparison)
INSPIRA 13 fetched (9 ITECNET + 4 IST-only, 0 new) | IAEA 23/0 | UNESCO 0 | FAO 1
(2601848 water-resources false positive by body match, excluded in scoring) |
WHO 3 | UNICEF 4 | UNOPS 3+2 | IMF 1 (26-R9741) | WFP 3 | UNHCR 1 | WB 2 |
OECD 2 | ILO 1 | UNDP 4 | UNFPA 4 | UNIDO 1 | ICRC/ITU/WMO/ICAO/ECB/WIPO/
UNITAR/UNHCR-wd/UNU/WFP… 0. IFAD: JS nav errors (0 saved); IMO: 0 jobs found
(site change or block — investigate next cycle).

## FIXES APPLIED 2026-08-29 (afternoon session)

### run_workday.py — FIXED (verified)
Default is now ALL 4 tenants (imf/wfp/unhcr/wto). Bare run = full coverage;
explicit args still restrict. Verified live: 4 tenant sections in one run.

### run_ifad.py — REWRITTEN v2 (verified: 0 → 8 saved)
PeopleSoft fluid portal: job rows are read-only DIV/SPANs, NO hrefs.
- javascript:DoNavBar() hrefs → net::ERR_ABORTED (dead end)
- direct HRS_APP_JBPST_FL URLs → PeopleSoft error "First operand of . is NULL" (dead end)
- WORKING METHOD: read rows from DOM ids `HRS_APP_JBSCH_I_HRS_JOB_OPENING_ID$N`,
  `SCH_JOB_TITLE$N`, `win0divHRS_JO_PST_CLS_DT$N` (N = DOM row order), then
  click per-row button `HRS_VIEW_DETAILSPB$N` via
  `page.evaluate("document.getElementById('HRS_VIEW_DETAILSPB$N').click()")`.
  Locator text-click on "Select" does NOT work (it's a column header).
- "Register as..." / roster rows are hard-reject candidates; consider adding
  `register` to HARD_REJECT.

### run_imo.py — REWRITTEN (verified: 0 → 3 saved)
recruit.imo.org is now an Angular SPA: vacancy cards have NO <a href> at all
(4 boilerplate hrefs on whole page). Fix: parse rendered card text with regex
(title/DIVISION/Contract Type/Job Close Date dd/mm/yyyy/Vacancy Reference),
then click each card's "Find out more!" via `page.locator("text=Find out more!").nth(idx)`,
read body, `page.go_back()` to listing. Detail URL shape: /vacancies/<num>.

### OECD SmartRecruiters — bot-wall + EXPIRED detection
- StealthyFetcher gets 813-byte challenge page; Camoufox full browser renders fine.
- API api.smartrecruiters.com/v1/companies/OECD/postings/<id> works from curl
  but exposes only releasedDate — NO deadline field.
- "This job has expired" banner renders in snapshot → reliable expiry signal.
- OECD_744000139632346 Senior AI Engineer archived 2026-08-29 (expired; tracker
  09-04 was stale — never live-verified).

### Scoring outcomes of fix-recovered JDs (2026-08-29)
- IMO V.N. 26-16 Cloud and Network Engineer (P3, London, DL 2026-09-11, US$71,335
  net + post adj): Azure/Cisco/Fortinet/VMware/IaC hands-on → deep gaps, below-
  responsibility filter → DO NOT PURSUE.
- IMO G.S. 26-09 Data Engineering Assistant, G.S. 26-08 ICT Client Support
  Assistant (G.S. support roles) → below-grade filter, DO NOT PURSUE.
- IFAD 37601 Geospatial/EO consultant roster → GIS/EO domain, roster → DO NOT PURSUE.
- IFAD 37458 AICRM Senior Programme Coordinator — agriculture/rural domain → exclude.
- IFAD 37414/37328/37281 + 2094/2095/2097 registrations → not ICT-core.
