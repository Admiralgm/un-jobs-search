# DEADLINE FORMATS & AUDIT PROTOCOL — Authoritative

**Status: ACTIVE.** Replaces all prior informal deadline guidance. Created 2026-08-21
after the TBD-epidemic incident (13 expired vacancies sat in the tracker with TBD or
stale deadlines because rows were written from stale script scrapes without live
verification).

## ⛔ THE ONE RULE — DEADLINE MEANS VERIFIED

**A deadline is recorded in the tracker ONLY if it was extracted from the LIVE
portal on the day the row is written (or revalidated live).**

- `YYYY-MM-DD` = verified from the portal page/API **today** (or carried over from a
  previous verified value if the portal was re-checked today and still shows it).
- `TBD` = **genuine rolling/roster position** confirmed on the portal TODAY
  (e.g. ITU roster validThrough = Dec 31 of current year, UNITAR rosters).
- `TBD` NEVER means "not checked". "Not checked" is not a valid deadline state.

**If a deadline is not verifiable today: DO NOT record the vacancy as OPEN with an
unverified TBD. Record it only with a verified deadline, or queue it for the
verification protocol below and flag it in the scan report.**

## What "not checked" did — 2026-08-21 incident

13 WB vacancies with `TBD` in the tracker were actually EXPIRED (expired 08-11 …
08-20). They were written as TBD during a scan and never revalidated; the tracker
kept showing them as OPEN. The user applied the audit protocol and all 13 were
archived. Root cause: TBD was used as "unknown", not as "verified rolling".

## Per-portal LIVE deadline extraction (validated)

### World Bank (CSOD) — WARNING: ValidThrough alone is NOT proof of open
```bash
curl -sL --max-time 10 "https://worldbankgroup.csod.com/ux/ats/careersite/1/home/requisition/{id}" | grep -o '"ValidThrough":"[^"]*"'
```
- `ValidThrough` alone does NOT prove the job is open. The job can be removed from
  the active listing (closed) while its stale requisition page still renders with
  ValidThrough. **EXPIRED = absent from the search/listing API, regardless of what
  the requisition page shows.**
- Only record a WB deadline when the requisition page loads WITH ValidThrough AND
  the requisition is still present in the search results.
- Long-term/roster requisitions with ValidThrough far in the future (e.g. 12-31)
  are genuine rolling.

### ITU — jobs.itu.int
```bash
curl -sL --max-time 10 "https://jobs.itu.int/job/-/{vid}/" | grep -i "Application deadline\|validThrough"
```
- Active: `validThrough` meta + text `Application deadline (Midnight Geneva Time): 31 December 2026`
- Expired: `<strong>Sorry, the deadline for this vacancy has passed.</strong>`
- Rosters: validThrough = Dec 31 of current year → genuine TBD/rolling.

### INSPIRA / careers.un.org (UN_ prefix) — OFF-BY-ONE WARNING
- API `endDate` `2026-06-21T03:59:59.000Z` = UTC midnight grace → displayed deadline
  is ONE DAY EARLIER (`2026-06-20`). **Real deadline = endDate date MINUS 1 day.**
- After extracting endDate, verify the job is still in the ACTIVE listing
  (`/api/public/opening/jo/list/filteredV2/en`). Absent from active listing =
  EXPIRED regardless of endDate.
- When in doubt: set deadline ONE DAY EARLIER. Better a day early than an expired
  job in the tracker.

### UNICEF — jobs.unicef.org (JS-rendered listing)
- Browser/console extraction required. Look for "Application deadline" / closing
  date in the job detail rendered by the listing page.
- Local JD files often contain the closing date in the body text.

### WHO — careers.who.int
- Detail pages show "Closing Date". Cross-check displayed date on the page, not
  raw API endDate (WHO also has a UTC-midnight offset on some postings).

### UNOPS — jobs.unops.org
- Local JD files: `grep -A2 "Posting End Date" JD_FILES/UN_UNOPS/{vid}_*.md`
  → `28-Jun-2026` (DD-Mon-YYYY). Cross-check with the live job page when the JD
  file is older than the scan.

### IAEA — iaea.org
- Local JD files: `grep -i "Closing Date" JD_FILES/UN_IAEA/{vid}_*.md`
  → `YYYY-MM-DD, HH:MM:SS PM`. Cross-check live job page.

### FAO — jobs.fao.org (Taleo)
```bash
curl -sL --max-time 10 "https://jobs.fao.org/careersection/fao_external/jobdetail.ftl?job={id}" | grep -o "'[0-9]*/[A-Z][a-z]*/[0-9]*, [0-9]*:[0-9]*:[0-9]* PM'"
```
- `'13/Jul/2026, 2:59:00 PM'` → deadline `2026-07-13`.

### UNESCO — careers.unesco.org (JS-rendered)
- Browser required: `https://careers.unesco.org/jobs/{vid}`, wait 3+s, extract from
  rendered DOM / browser_console.
- Local file fallback: grep deadline text in `JD_FILES/UN_UNESCO/{vid}_*.md`.
- UNESCO positions can be "closed" on the portal while the JD file still exists.
  Verify the detail page says applications are open.

### ICRC — careers.icrc.org (Taleo)
```bash
curl -sL --max-time 10 "https://careers.icrc.org/job/{slug}/{vid}/" | grep -i "Application deadline"
```
- DD.MM.YYYY format. Some pages require browser.

### WFP / Workday (wd3.myworkdaysite.com)
- JS-rendered, curl returns shell only. Browser required.
- Local files: "DEADLINE FOR APPLICATIONS" header, date in separate section —
  extract via browser console on the live posting.

### UNITAR — unitar.org (roster)
- Roster positions have NO fixed deadline → GENUINE TBD, keep in Rolling section.
- If the page shows a deadline, record it; otherwise TBD = correct only here.

## Audit procedure (run when deadlines are questioned OR before finalizing a scan)

1. Extract every deadline from the tracker summary table (regex on the table rows).
2. Group by agency.
3. For each agency, fetch LIVE deadline via the methods above (curl batch first,
   browser only for JS-rendered).
4. For every entry: VERIFIED (live = tracker, date matches) | CORRECTED (live
   differs — update) | EXPIRED (portal says closed / no longer listed → ARCHIVE).
5. Genuine TBD = portal confirmed rolling/roster TODAY → keep TBD with note.
6. Never guess. Never copy from memory. Never reuse a date from a previous session
   without re-verifying the live portal.
7. Write updates to the tracker ONLY after verification completes (backup first).

## Deadline storage rules in the tracker

- Format: `YYYY-MM-DD` always. No `DD/MM/YYYY`, no `Jul 31`.
- TBD allowed ONLY for confirmed rolling/roster.
- When a verified deadline is written, the row is placed in deadline-sorted
  position (active by deadline, TBD/rolling at bottom).

## When the portal is unreachable

- If the live portal cannot be reached and the deadline cannot be verified, mark
  the entry "TBD — verify" BUT flag it in the report so a revalidation is queued.
- **Do NOT silently keep an unverified date or an unqueued TBD.**

---
Revision log:
- 2026-08-21: created; supersedes the (never-existing) inline references and the
  informal TBD-extraction doc; adds WB live-requisition caveat.
