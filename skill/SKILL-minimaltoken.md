---
name: un-jobs-search-minimaltoken
description: >
  Token-optimized UN sector job vacancy scanning. Scans 32+ sources using
  web-preclean.py pre-cleaner (94-95% token reduction via trafilatura), API-first approach, and
  browser only for CF-blocked sites. Maintains TWO files in workdir:
  UN-VACANCIES-TRACKER.txt (active vacancies) and
  UN-VACANCIES-ARCHIVE.txt (vacancies marked APPLIED: YES or EXPIRED).
  There is NO separate Impactpool file — all entries go to UN-VACANCIES-TRACKER.txt.
  Incorporates all rules from the original un-jobs-search skill plus token optimization protocol v1.0.
  This is the ONLY UN jobs search skill — there is no separate "un-jobs-search" skill to load.
triggers:
  - "un job search minimal"
  - "UN jobs token optimized"
  - "UN sector vacancies fast"
  - "scan UN jobs efficiently"

---

# UN Jobs Search Agent — Token-Optimized Protocol v1.0

## MODEL-SPECIFIC EXECUTION PROTOCOL (DEEPSEEK V4 FLASH)

**This section is MANDATORY for Deepseek V4 Flash. Read it FIRST. Follow it EXACTLY.**

### Who You Are
You are a disciplined scanning agent. You scan UN career portals for ICT/AI/Digital job vacancies, score them, and maintain two tracker files. You do NOT think creatively. You do NOT improvise. You follow the steps below in order. If something is not covered by these rules, report it and move on — do NOT invent solutions.

### HARD LIMITS
- Maximum 40 tool calls per session (for 5-portal scan)
- Maximum 60 tool calls per session (for full 15-portal scan)
- Maximum 5 portals per session (pick from the Daily Scan Queue below) — or scan all 15+ when user says "scan everything"
- Maximum 1 execute_code call per phase (bulk operations)
- If a portal scan takes more than 3 tool calls, SKIP it and report "SKIPPED — timeout"
- If turn count exceeds 60, STOP immediately — write results, deliver report, stop

### ABSOLUTE PROHIBITIONS (violating ANY of these is a critical failure)
1. NEVER read or write files outside the workdir: `~/Downloads/DATA_REPOSITORY/WORKDIR/`
2. NEVER create new Python scripts (.py files) — use `terminal` with `python3 << 'PYEOF'` heredoc for all inline Python
3. NEVER use `write_file` or `patch` on tracker files — use `terminal` with `python3 << 'PYEOF'` heredoc and `Path().write_text()` only
4. NEVER use `execute_code` for ANY file read or write operation — the execute_code sandbox has an isolated filesystem that DESTROYED UN-VACANCIES-TRACKER.txt on 2026-06-29. Use `terminal` with `python3 << 'PYEOF'` heredoc for all Python that touches files. Use `read_file` for reading files.
5. NEVER reference paths under `config/` or the skill's own directory — only workdir paths
6. NEVER hallucinate job titles, deadlines, grades, locations, or vacancy IDs — if you did not see it on a live page, do NOT add it
7. NEVER delegate scanning to subagents — do everything in the parent agent
8. NEVER retry a failed portal more than once — report "SKIPPED" and move on
9. NEVER skip Phase 1 (file hygiene) — expired cleanup is mandatory every session

### DAILY SCAN QUEUE (pick 5 per session, rotate daily)
Priority order — scan top 5 that were NOT scanned in the previous session:
1. WHO — careers.who.int/careersection/ex/jobsearch.ftl — search "Digital" (Camoufox)
2. ITU — jobs.itu.int — search "Digital" (Camoufox)
3. ILO — jobs.ilo.org/go/All-Jobs/2842101/ (Camoufox)
4. UNOPS — careers.unops.org/careersmarketplace/SearchJobs (Camoufox)
5. IAEA — iaea.taleo.net/careersection/ex/jobsearch.ftl — search "Digital" (Camoufox)
6. UNESCO — careers.unesco.org (Camoufox)
7. ICRC — careers.icrc.org/go/All-Jobs/3807301/ (Camoufox)
8. OECD — jobs.smartrecruiters.com/OECD (Camoufox)
9. WFP — wd3.myworkdaysite.com/recruiting/wfp/job_openings (Camoufox)
10. IMF — imf.wd5.myworkdayjobs.com/IMF (Camoufox)
11. UNDP — jobs.undp.org (Camoufox)
12. WMO — erecruit.wmo.int (Camoufox)
13. UNICEF — jobs.unicef.org/en-us/listing/ (Camoufox, may crash — use browser_console JS extraction)
14. INSPIRA — careers.un.org (Camoufox + Cloudflare bypass)

### EXECUTION SEQUENCE (follow in order — do NOT skip steps)

**STEP 1 — Date Check (1 tool call)**
```
terminal: date +%Y-%m-%d
```
Store the date. You will use it for expiry comparison.

**STEP 2 — Read Files & Backup (1 terminal heredoc call)**
Read both files from workdir:
- UN-VACANCIES-TRACKER.txt
- UN-VACANCIES-ARCHIVE.txt

Backup both to BACKUP/ subdirectory with today's date suffix.

Extract all existing Vacancy IDs from both files into a Python set. This is your dedup set.

**STEP 3 — Expired Cleanup (same terminal heredoc call as Step 2)**
Parse every deadline in the tracker. If deadline < today AND APPLIED: NO:
- Move entry to UN-VACANCIES-ARCHIVE.txt with APPLIED: EXPIRED
- Remove from UN-VACANCIES-TRACKER.txt
- Count how many were moved

If any entry has APPLIED: YES, move it to archive regardless of deadline.

Rebuild the summary table after removals.

**STEP 4 — Report Urgent Deadlines**
From the tracker, list entries with deadline within 48 hours of today.
Report them immediately before scanning new portals.

**STEP 5 — Scan Portals (3 tool calls per portal max)**
For each of the 5 portals in your queue:

a) `browser_navigate` to the portal URL
b) If page loads with job listings: extract via `browser_console` JS expression:
   ```javascript
   JSON.stringify(Array.from(document.querySelectorAll('a[href*="jobdetail"], a[href*="JobDetail"], article, .job-item')).map(el => ({title: el.innerText, url: el.href || '', text: el.innerText})))
   ```
   If Camoufox returns 500 on browser_type/browser_click: SKIP this portal, report "SKIPPED — Camoufox 500"
c) If page is blank or shows bot check: SKIP, report "SKIPPED — blocked/JS-failed"

For each extracted job, check:
- Is the title ICT/AI/Digital/IT/IS/Data/Analytics/Telecom relevant? If NO, skip.
- Is it an internship/volunteer/junior/Ukraine-located? If YES, skip.
- Is the Vacancy ID already in your dedup set? If YES, skip.
- If all checks pass: extract title, ID, location, grade, deadline, contract type, URL

**STEP 6 — Score New Entries (1 terminal heredoc call)**
For each new entry, apply the 3-dimension scoring model:
- Technical Relevance (60%): 0-100 based on match to candidate profile
- Seniority Alignment (20%): 0-100 based on P-grade match
- Strategic Alignment (20%): 0-100 based on system-level/policy experience
- TOTAL = Technical × 0.60 + Seniority × 0.20 + Strategic × 0.20
- Color: 🔴 >=75, 🟠 65-74, 🟡 50-64, 🟢 <50

**STEP 7 — Write Tracker (1 terminal heredoc call)**
Build the complete new file content in Python:
- Regenerate summary table (sorted by deadline, color-coded)
- Append new entries in the canonical entry format
- Write ONCE with Path().write_text()
- Run `sync` in terminal
- Verify with `wc -l`

**STEP 8 — Deliver Report (final output)**
Report exactly:
- Date scanned
- Portals scanned (list with status: OK / SKIPPED / FAILED)
- New entries added (count + list with score)
- Expired entries moved to archive (count)
- Urgent deadlines (within 48h)
- Total tracker entries (before/after)
- Blocked sources

### ANTI-HALLUCINATION RULES (Deepseek V4 Flash specific)
1. If browser_navigate returns an error or blank page, do NOT assume jobs exist there. Report "SKIPPED — page not accessible" and move on.
2. If you cannot extract a Vacancy ID from the live page, do NOT invent one. Use `[GEN-UNKNOWN]` and flag it.
3. If a deadline is not visible on the page, write "TBD" — do NOT guess.
4. If a grade is not visible, write "Unknown" — do NOT guess.
5. If browser_console returns empty or error, do NOT fabricate job listings. Report "SKIPPED — extraction failed".
6. NEVER copy job titles from memory or previous sessions. ONLY use what the live page shows right now.
7. If a portal has 0 ICT-relevant jobs, that is a valid result. Report "0 ICT jobs found" — do NOT pad the results.

### ERROR HANDLING DECISION TREE
```
Camoufox health check fails (curl localhost:9377/health)?
  → terminal(background=true, command="camofox server start")
  → wait 5 seconds
  → retry health check once
  → if still fails: report "CANNOT SCAN — Camoufox down", deliver Phase 1-4 results only

browser_navigate returns 500?
  → navigate away to about:blank, then back to the URL
  → if still 500: SKIP portal, report "SKIPPED — Camoufox 500"

browser_navigate returns blank page (no job listings)?
  → try browser_scroll down once
  → if still blank: SKIP portal, report "SKIPPED — JS render failed"

browser_type returns 500?
  → do NOT retry browser_type
  → use browser_console with JS to set the search field value instead
  → if that also fails: SKIP portal, report "SKIPPED — cannot search"

execute_code fails with error?
  → read the error message
  → fix the Python syntax/logic
  → retry ONCE
  → if still fails: report error, deliver what you have, STOP

Portal returns 403/Cloudflare?
  → SKIP immediately, report "SKIPPED — Cloudflare blocked"
  → do NOT retry with different methods
```

### CAMOUFOX HEALTH CHECK (do this BEFORE Step 5)
```
terminal: curl -s http://localhost:9377/health | head -1
```
If response does not contain `"ok":true`:
```
terminal(background=true, command="camofox server start")
```
Wait 5 seconds, then retry health check. If still failing, scan 0 portals — deliver Phase 1-4 results only.

### WHAT TO DO IF YOU ARE CONFUSED
If you are unsure about any step:
1. Do NOT improvise or guess
2. Report "UNCLEAR — need guidance on: [specific question]"
3. Skip that step and continue with the next one
4. Deliver partial results

It is ALWAYS better to deliver partial correct results than to hallucinate full results.

---

## Role
Scan UN/International sector ICT/AI/telecom/digital-transformation job vacancies
using token-optimized scraping. Target: 90%+ token reduction vs raw HTML methods.

## Candidate Profile (for scoring context)
- Primary Profile: See `JD_FILES/` in workdir for job descriptions
- Expertise: AI Product Leadership | LLMs, Agentic Systems, RAG | ICT/Telecom | 4G/5G/FTTX | Digital Transformation | UN/Africa/EU Advisory
- Grade target: P-3 and above | Fixed-Term / Consultancy / Roster
- Nationality: Serbian AND Czech Republic (EU) — Serbian nationals-only positions are OPEN. Never exclude Serbian-national positions.

---

## TOKEN OPTIMIZATION RULES (MANDATORY)

### Rule 1 — Detect Site Type Before Fetching
Before scraping any URL, classify it:

| Type | Signs | Strategy |
|------|-------|----------|
| OPEN | Returns 200 to requests | `web-clean.py` + targeted extraction |
| WAF-PROTECTED | 403, Cloudflare | `StealthyFetcher` (Scrapling) |
| JS-RENDERED | Blank HTML, dynamic content | `StealthyFetcher` (Scrapwright) — PRIMARY; `browser_navigate` — fallback |
| API-AVAILABLE | JSON endpoints | Fetch JSON directly — skip HTML |
| BLOCKED-HARD | 403 even with browser | Escalate — do NOT retry |
| SSO/SAML | Redirect to login.microsoftonline.com | `StealthyFetcher` or skip |

**UPDATED (2026-05-19):** Camoufox is now the **default browser** for all Hermes browser tools. When `CAMOFOX_URL=http://localhost:9377` is set in `.env`, ALL browser tools (`browser_navigate`, `browser_click`, `browser_type`, `browser_snapshot`, etc.) automatically route through Camoufox. No code changes needed.

**Camoufox setup (already configured):**
- Python package: `camoufox` 0.4.11 (`pip install camoufox`)
- Browser binary: v135.0.1-beta.24 at `~/Library/Caches/camoufox/`
- Camofox server: `camofox-browser` npm v2.4.5 (upgraded from v2.4.3), port 9377
- `.env`: `CAMOFOX_URL=http://localhost:9377`
- `config.yaml`: `browser.camofox.user_id=hermes-default`, `browser.camofox.session_key=hermes-session-1`, `browser.camofox.managed_persistence=true`
- Start server: `terminal(background=true, command="/usr/local/bin/camofox server start")`
- Health check: `curl http://localhost:9377/health`
- Stealth verified: `navigator.webdriver = False`

**Priority order for JS-rendered sites:**
1. **Camoufox** (default, via `CAMOFOX_URL`) — works for 95% of JS SPAs, best stealth, C++ fingerprint spoofing
2. `browser_navigate` + `browser_console` — fallback for sites that need interaction (if Camoufox crashes)
3. `StealthyFetcher.fetch(URL, headless=True, wait=8000, block_webrtc=True)` — Scrapling fallback
4. `tesseract` OCR on screenshot — last resort when all else fails

**Known Camoufox issues (historical, resolved in v2.4.5):**
- UNICEF (jobs.unicef.org) — was crashing on Camoufox v2.4.3 (Internal Server Error). ✅ RESOLVED by Camoufox v2.4.5. Page now loads and renders job listings normally via `browser_navigate`. The search keyword box + Enter filters results by keyword. Use `references/unicef-browser-console-extraction.md` for JS DOM bulk extraction if search doesn't narrow enough.
- Some sites with heavy anti-bot may still block Camoufox — use Scrapling StealthyFetcher as fallback

### Rule 2 — Always Pre-Clean Before Reading
**NEVER use `web_extract` or `web_extract_plus` for UN job scanning.**
Always use `web-preclean.py` first:
```bash
python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/web-preclean.py URL 6000
```
**IMPORTANT:** Use ONLY the workdir copy at the path above. NEVER use `config/scripts/web-preclean.py` or the skill's own scripts directory — those are FORBIDDEN.
Token savings benchmark: 701KB raw HTML -> 39KB clean Markdown = **94% reduction (trafilatura)**
Impactpool job page: 60KB raw HTML -> 3KB clean Markdown = **95% reduction (trafilatura)**

**Pipeline:** trafilatura (primary) -> html2text (fallback) -> BeautifulSoup4 (fallback) -> regex (last resort)

**Why this matters:** The `web_extract` auxiliary model (gemini-3-flash-preview) has a massive context window. Without preprocessing, raw unparsed HTML is dumped directly into the summarization prompt, resulting in 10x token bloat. `web-preclean.py` enforces a strict 90-95% token reduction BEFORE content reaches the LLM.

### Rule 3 — API-First Rule
ReliefWeb API v1 is DEPRECATED (410 as of May 2026). No UN system has a reliable
public API. Use web-clean.py on career portals.

### Rule 4 — Targeted Extraction
```bash
python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/web-preclean.py URL 6000 | grep -i -E "(title|deadline|grade|location|contract)"
```

### Rule 5 — Hard Token Limits
| Task Type | char_limit |
|-----------|-----------|
| Quick lookup | 2,000 |
| Single job read | 6,000 |
| Search results | 8,000 |
| Deep extraction | 15,000 |

CONFIRMED ACCESSIBLE via web-clean.py (no browser needed):
- **FAO RSS**: https://jobs.fao.org/careersection/feed/joblist.rss?lang=en&portal=8105120163 — returns ~11 recent jobs via curl. Parse XML `<item>` blocks. Vacancy ID format: `FAO-XXXXXXX`.
- **World Bank** (worldbank.org/ext/en/careers) — Returns 200, full content via web-clean.py

NOTE: The main WHO careers site (who.int/careers) is informational only and does not contain job listings. The actual WHO job listings are on the Taleo system (careers.who.int) which requires browser_navigate (JS-rendered SPA).
- UNJobNet: https://www.unjobnet.org/jobs (3,594 jobs, returns 200, Vue.js SPA) — use `scrapling stealthy-fetch` CLI to download HTML, then parse with regex. Job detail URLs: `/jobs/detail/<numeric>`. ID format: `UNJN-<numeric>`.

**CONFIRMED ACCESSIBLE via web-clean.py (no browser needed):**
- **WHO** (who.int/careers) — Returns 200, full content via web-clean.py
- **FAO RSS** (jobs.fao.org/careersection/feed/joblist.rss) — Returns XML via curl, ~11 recent jobs with title, link, description. Most reliable FAO source.
**CONFIRMED INACCESSIBLE:** None currently. All previously blocked sites have been removed from active scanning.

CONFIRMED ACCESSIBLE via Camoufox (JS-rendered SPAs — default browser):
- **IMO** (recruit.imo.org) — Camoufox renders full job list (10 jobs). Jobs rendered as button elements with full text. Vacancy Reference format: V.N. XX-XX (Fixed Term), CA XX-XX (Consultant), STA XX-XX (Temporary/Roster).
- **OECD SmartRecruiters** (jobs.smartrecruiters.com/OECD) — Camoufox renders full job list (~80 jobs). Deputy Head of Digital Workplace Services found (score 83). Same platform used by WTO (jobs.smartrecruiters.com/WTO, ~10 jobs, no ICT roles found). See `references/oecd-smartrecruiters.md`.
- **WFP Workday** (wd3.myworkdaysite.com/recruiting/wfp/job_openings) — Camoufox renders full job list (124 jobs). Cookie consent handled automatically.
- **ITU** (jobs.itu.int) — JS-rendered SPA. Camoufox renders full job list with search results.
- **IMF Workday** (imf.wd5.myworkdayjobs.com/IMF) — Camoufox renders full job list (13 jobs). IT Strategist and Data Management Analyst roles found. Same Workday platform as WFP/UNHCR.
- **ILO Jobs** (jobs.ilo.org) — Camoufox renders full job list (12 jobs). Director IT Management/CIO role found. Search by keyword works.
- **UNOPS** (careers.unops.org) — Camoufox renders full job list (21 jobs). AI Adoption Coordinator and AI Centre of Excellence Lead found.
- **FAO Taleo** (jobs.fao.org/careersection/fao_external/jobsearch.ftl) — Camoufox renders full job list (123 jobs). Keyword search works.
- **UNHCR Workday** (unhcr.wd3.myworkdayjobs.com/en-GB/External) — Camoufox renders full job list (41 jobs). Mostly interns/admin, no ICT professional roles.
- **IAEA Taleo** (iaea.taleo.net/careersection/ex/jobsearch.ftl) — Camoufox renders full job list (31 jobs). Keyword search works.
- **WHO Taleo** (careers.who.int/careersection/ex/jobsearch.ftl) — Camoufox renders full job list (56 jobs). Keyword search works.
- **ICAO** (icaocareers.icao.int/careers/Home/Vacancies) — HTML tables with job listings. BI Developer role found.
- **UNESCO** (careers.unesco.org) — Camoufox renders full job list (50 jobs). Mix of internships/junior AND senior consultant roles. Search "Digital" yields ~19 results including senior EdTech/ICT/AI roles (e.g., Educational Technology and Digital Pedagogies Expert, Level 3 Senior). Do NOT dismiss as "mostly internships" — always search keywords to find hidden senior roles.

CONFIRMED PARTIALLY WORKING via Camoufox (page loads but issues):
- **World Bank CSOD** (worldbankgroup.csod.com/ux/ats/careersite/1/home?c=worldbankgroup) — ⚠️ JS SPA fails to render job list in Camoufox. Shows only skeleton (comboboxes, "Current Openings" heading). Heavy JS execution required. **Use Scrapling StealthyFetcher or tesseract OCR as fallback.** Confirmed 21 IT/ICT jobs exist in filters but cannot extract details via browser tools.
- **UNFPA** (unfpa.org/jobs) — ⚠️ Camoufox CRASHES this portal. Causes browser tab 404, invalidating all subsequent Camoufox actions. Requires full tab crash recovery (see Known Pitfalls). Use Impactpool UNFPA filter or default browser instead. See `references/unfpa-portal.md`.
- **UNICEF (jobs.unicef.org)** — ⚠️ Camoufox crashes (500 error) on `browser_type` action. Page loads but search box interaction fails. **Use browser_console with JavaScript DOM extraction instead** — see `references/unicef-browser-console-extraction.md`. Navigate to `/en-us/listing/`, close cookie dialog, extract jobs via `document.querySelectorAll('h4')`, click "More Jobs" button via JS, repeat. ~200+ jobs extractable. Filter client-side for ICT/AI/Digital keywords.

- **UNICEF "More Jobs" button gets stuck**: After ~10-15 clicks, the "More Jobs" button becomes hidden (`offsetParent === null`) and stops responding. This is a UI bug in UNICEF's infinite scroll. **Workaround**: Extract all loaded data from the DOM at this point — you'll have ~200+ jobs. The remaining ~3 jobs are not worth pursuing. Use `document.querySelector('a.more-link.button').innerText` to check remaining count.
- **UNJobNet** (unjobnet.org/jobs) — ⚠️ Vue.js SPA. Page loads with search boxes but job results don't render in snapshot. Need longer wait or JS console extraction. **Use scrapling stealthy-fetch CLI.**

CONFIRMED ACCESSIBLE via Scrapling StealthyFetcher (if Camoufox unavailable):
- Use only if Camoufox server is not running. Same sites as above.

CONFIRMED ACCESSIBLE via browser_navigate ONLY (JS-rendered, web-clean.py returns only cookie banner):
- **FAO Taleo** (jobs.fao.org/careersection/fao_external/jobsearch.ftl) — 118+ jobs, JS-rendered. Use RSS feed instead for recent jobs.
- **ICAO** (icaocareers.icao.int/careers/Home/Vacancies) — HTML tables with job listings. Sections: Professional, General Service, Consulting. Extract via browser console `document.body.innerText` or table parsing. Job IDs are numeric (e.g., 34167, 276434). No SSL mismatch — direct browser access works.

CONFIRMED ACCESSIBLE via browser_navigate only:
- **IMF (imf.org/en/about/recruitment)** — 403 via requests, 200 via browser. Links to Workday at imf.wd5.myworkdayjobs.com/IMF
- **WHO Taleo (careers.who.int/careersection/ex/jobsearch.ftl)** — Full job listings, 44+ openings, JS-rendered SPA
- **UNHCR Workday (unhcr.wd3.myworkdayjobs.com/en-GB/External)** — Full job listings, 28+ openings, JS-rendered SPA
- **IAEA Taleo (iaea.taleo.net/careersection/ex/jobsearch.ftl)** — Full job listings, 36+ openings, JS-rendered SPA
- **IOM Oracle Cloud (fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs)** — Full job listings, 174+ openings, JS-rendered SPA
- **COE Talents (talents.coe.int/en_GB/careersmarketplace/SearchJobs)** — Full job listings, 13+ openings, JS-rendered SPA. Pagination via JS click.
- **UNICEF (jobs.unicef.org)** — Empty via web-clean.py, requires browser_navigate
- **UNDP (jobs.undp.org)** — 403 via requests, requires browser_navigate
- **UNESCO (careers.unesco.org)** — JS-rendered, requires browser_navigate
- **ILO (www.ilo.org/careers)** — JS-rendered, requires browser_navigate

CONFIRMED TECHNICAL ISSUES (skip or use Impactpool proxy):
- **ICAO** (icaocareers.icao.int) — FULLY ACCESSIBLE via browser_navigate. HTML tables with job listings. No SSL mismatch. Direct scraping works.
- **IMO** (recruit.imo.org) — JS-rendered, only shows "Refine Search" heading. DNS resolution works but job list needs browser automation.

### Rule 6 — Speed Rule: One-Shot Writes, Not Iterative Edits
**Never iterate to fix file content turn-by-turn.** The user's primary frustration is agents going silent for "million years" of iterative compute cycles. Instead:
1. Parse all existing entries in ONE `terminal` heredoc call
2. Build the full new file content (table + all entries) in ONE Python dict/list
3. Write ONCE with `Path().write_text()` via terminal heredoc, then `sync` + verify ONCE
4. If a table/entry mismatch is found, fix in ONE shot — do NOT read-write-verify-loop
5. NEVER use `execute_code` for any of these steps — use `terminal` with `python3 << 'PYEOF'` heredoc

The scoring engine + summary table must be fully computed in-memory before the first write. A single Python script should:
- Parse existing entries from current files
- Add new scored entries
- Rebuild the sorted summary table from the complete entry list
- Write both files (tracker + archive if changes)
- Do ONE final verification

### Rule 7 — Escalation Protocol
If a site returns 403 with both requests AND browser:
1. Report: SCRAPE FAILED
2. Do NOT retry the same method more than once
3. Use Impactpool as lead generator only (verify on official portal)

### Rule 8 — Expired Vacancy Cleanup (MANDATORY)
**Every scan MUST detect and archive expired vacancies.**

1. After loading both files, parse every entry's deadline
2. Compare against today's date (query host: `date +%Y-%m-%d`)
3. Any entry with deadline < today AND APPLIED: NO → move to archive
4. Mark moved entries as APPLIED: EXPIRED in the archive file
5. Rebuild the active file summary table after removals
6. Report number of expired entries moved

**Date parsing:** Handle YYYY-MM-DD, "Month Day Year", "Month Day" (assume current year).
Use `datetime.date.fromisoformat()` for ISO format, fallback to `strptime` with `%B %d %Y`.

**Critical:** Do NOT skip this step. Expired vacancies corrupt the active file and waste tokens during scoring. The user explicitly requested this cleanup.

---

## WORKDIR CONSTRAINT (MANDATORY — DO NOT CHANGE)

**This skill operates EXCLUSIVELY within the workdir: `~/Downloads/DATA_REPOSITORY/WORKDIR/`**

**ABSOLUTELY FORBIDDEN to read or write to any path outside this workdir.** This includes:
- `~/Downloads/UN_SECTOR_VACCANCIES.txt` — DO NOT USE (old file name)
- `config/scripts/web-preclean.py` — DO NOT USE (belongs to default profile)
- `skills/research/un-jobs-search-minimaltoken/scripts/` — DO NOT USE (skill's own directory, read-only reference only, never execute from here)
- `config/wiki/entities/goran-markovic.md` — DO NOT USE
- `config/wiki/entities/positioning-*.md` — DO NOT USE
- `config/wiki/concepts/matching-keywords.md` — DO NOT USE
- Any path under `~/Downloads/` outside the workdir
- Any path under `config/` outside the workdir

**All file operations MUST use paths under the workdir only.**

## CANONICAL FILE WRITE METHOD

**Prefer `Path().write_text()` for bulk operations (rebuilding the entire file). Use `patch` for single-entry additions to the table-only format.**

**CRITICAL — execute_code is FORBIDDEN for file operations.** The `execute_code` sandbox has an isolated filesystem. `read_file` inside it returns EMPTY for real filesystem files. `write_file` inside it DESTROYS real files by writing nothing back. On 2026-06-29 this nuked UN-VACANCIES-TRACKER.txt. **ALL Python that reads or writes tracker files MUST run via `terminal` with `python3 << 'PYEOF'` heredoc**, NOT `execute_code`. Use `read_file` for reading files.

**Two files are maintained in the workdir:**
1. `UN-VACANCIES-TRACKER.txt` — Active vacancies (replaces UN_SECTOR_VACCANCIES.txt)
2. `UN-VACANCIES-ARCHIVE.txt` — Vacancies marked APPLIED: YES or EXPIRED (replaces UN_SECTOR_VACCANCIES_ARCHIVE.txt)

**Note:** There is NO separate Impactpool file in this workdir. All entries go to UN-VACANCIES-TRACKER.txt.

**Deduplication across both files is MANDATORY:**
Before adding any new entry, check the Vacancy ID against BOTH files. A vacancy that already exists in ANY file (tracker or archive) must NOT be added again.

**Primary method (bulk updates) — run via terminal heredoc, NOT execute_code:**
```bash
python3 << 'PYEOF'
from pathlib import Path
WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
path = WORKDIR / "UN-VACANCIES-TRACKER.txt"
content = path.read_text()
path.write_text(new_content)
PYEOF
```
Then run `sync` in terminal.

**After EVERY write — mandatory verification:**
```bash
sync
wc -l ~/Downloads/DATA_REPOSITORY/WORKDIR/UN-VACANCIES-TRACKER.txt
wc -l ~/Downloads/DATA_REPOSITORY/WORKDIR/UN-VACANCIES-ARCHIVE.txt
```

**Archive file maintenance:**
When a vacancy is marked APPLIED: YES, move it from the tracker file to UN-VACANCIES-ARCHIVE.txt.
The archive file is loaded during every scan session to prevent re-adding applied vacancies.

---

## Execution Strategy: Direct Terminal Over Delegation

**CRITICAL PERFORMANCE RULE — Do NOT delegate browser-based scanning to subagents.**
All three delegate_task calls for multi-batch scanning in this session timed out at 600s. Browser_navigate inside subagents blocks on slow API calls. Instead:

1. Run web-preclean.py terminal commands directly in the parent agent
2. Each site scan takes 10-30s via terminal, vs 600s timeout per batch via delegation
3. Return structured data from subagents for data processing (parsing, scoring), NOT for scraping
4. File writing (Path().write_text() + sync) must happen in the parent agent — subagents cannot write tracker files reliably

**Recommended pattern:**
```
parent agent:
  - PHASE 1-2: read files, backup, parse state (direct terminal heredoc or read_file)
  - PHASE 3: for EACH portal, run `python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/web-preclean.py URL 8000` directly in terminal
  - PHASE 4: collect all findings, dedup, score (terminal heredoc Python)
  - PHASE 5: build complete file fresh in Python via terminal heredoc, write once, verify
```

## Session Budget Rule

**CRITICAL — Do NOT develop new scripts during execution.**
The workdir already contains 33+ scripts from previous sessions. Do NOT create new Python scripts, do NOT write custom scrapers, do NOT build new scoring engines. Use ONLY:
1. The workdir copy at `WORKDIR/scripts/web-preclean.py` for page cleaning
2. `terminal` with `python3 << 'PYEOF'` heredoc for inline Python (parsing, scoring, file writing) — NEVER `execute_code`
3. `browser_navigate`/`browser_snapshot` for JS-rendered portals
4. `terminal` for curl, grep, sync, wc
If you find yourself wanting to write a .py file, STOP — use terminal heredoc instead.

**If turn count exceeds 60:**
1. Write all results to disk
2. Verify with `wc -l`
3. Deliver partial report
4. Stop

## Execution Phases

### Phase 1: Urgency Triage & File Hygiene
1. Read both files: UN-VACANCIES-TRACKER.txt, UN-VACANCIES-ARCHIVE.txt (from workdir)
2. Get today's date from host: `date +%Y-%m-%d`
3. **EXPIRED CLEANUP (Rule 8):** Parse every entry's deadline in the tracker file. Any entry with deadline < today AND APPLIED: NO → move to UN-VACANCIES-ARCHIVE.txt with APPLIED: EXPIRED. Rebuild summary table after removals. Report count.
4. Flag deadlines within 48 hours from tracker file
5. Backup both files:
```bash
DATE=$(date +%Y%m%d)
WORKDIR="~/Downloads/DATA_REPOSITORY/WORKDIR"
cp "$WORKDIR/UN-VACANCIES-TRACKER.txt" "$WORKDIR/BACKUP/UN-VACANCIES-TRACKER_BACKUP_${DATE}.txt"
cp "$WORKDIR/UN-VACANCIES-ARCHIVE.txt" "$WORKDIR/BACKUP/UN-VACANCIES-ARCHIVE_BACKUP_${DATE}.txt"
```
6. Archive expired/applied entries: move APPLIED: YES and EXPIRED entries from tracker file to UN-VACANCIES-ARCHIVE.txt. **IMPORTANT:** Check BOTH conditions independently — (a) deadline < today AND APPLIED: NO → mark as EXPIRED, (b) APPLIED: YES regardless of deadline → move as APPLIED: YES. The expiry check alone will NOT catch APPLIED:YES entries with future/TBD deadlines.
7. **Cross-file deconflict**: If a Vacancy ID exists in UN-VACANCIES-ARCHIVE.txt, it MUST NOT remain in UN-VACANCIES-TRACKER.txt. Remove it from the tracker file.
8. **Date parsing for expiry detection**: Handle multiple deadline formats (YYYY-MM-DD, "Month Day, Year" like "May 12, 2026", "Month Day" without year assuming current year). The first pass with ISO regex will miss these.
9. Rebuild summary table after every move. Table must use 🔴🟠🟡🟢 emoji color coding, not text color names (RED/ORANGE/YELLOW/GREEN).
10. Verify cross-file overlap is zero after cleanup. Use `grep "VACANCY ID:"` on both files and `comm -12` to check tracker vs archive overlap.
11. Update footers of both files

### PHASE 2: Load State
1. Read both tracking files with `read_file` or `terminal` heredoc Python `Path().read_text()` — NEVER `execute_code`
2. Extract existing Vacancy IDs from all files for deduplication

### PHASE 3: Batched Scanning (Token-Optimized)

**Keyword Broadening Strategy (MANDATORY):**
If a combined search (e.g., "AI ICT Digital") returns 0 results on a portal:
1.  **Broaden**: Search for "Digital", "ICT", and "AI" individually.
2.  **Reason**: Many UN portals (especially Taleo-based like WHO/IAEA and Workday-based like UNHCR) use strict AND logic or have poor relevancy ranking for multi-term queries.
3.  **Result**: Searching "Digital" on WHO/IAEA often reveals high-value roles (e.g., CIO, Technical Officer) that were hidden by the "AI" filter.

**Primary scan pattern (confirmed working 2026-05-13):**
Always start with the hiring organization's direct career portal. Use `web-clean.py` for
accessible sites, `browser_navigate` for CF-blocked sites. Only use Impactpool as a
lead generator for hard-blocked sites, NEVER as the primary source.

**Impactpool is UNRELIABLE:** Known to list expired, duplicate, or phantom vacancies.
Deadlines are frequently inaccurate. Job titles may be paraphrased. If using Impactpool
at all, always verify on the hiring org's official career portal before recording any entry.

**Batches:**
- **Batch 1: UNICEF** — browser_console JS extraction (Camoufox crashes here). Extracts ~200 jobs. Job detail URLs: `/en-us/job/<numeric-id>`.
- **Batch 2: FAO** — Camoufox Taleo (jobs.fao.org/careersection/fao_external/jobsearch.ftl). Focus on OIG/CSI divisions for ICT roles. RSS fallback: https://jobs.fao.org/careersection/feed/joblist.rss?lang=en&portal=8105120163 (~11 recent jobs).
- **Batch 3: WHO, ITU** — Camoufox. WHO (careers.who.int/careersection/ex/jobsearch.ftl): Search "Digital" (yields ~10 results), "AI" (~6), "ICT" (~8). ITU (jobs.itu.int): Full listing query, search "Digital" (~30 results).
- **Batch 4: UNESCO, ILO, ICAO, IMO, ICRC** — Mixed JavaScript extraction. ICRC (careers.icrc.org/go/All-Jobs/3807301/) uses SuccessFactors; RSS feed at /services/rss/category/?catid=3807301 works well. Deduplicate ICRC's triple-rendering bug. ICRC grading: B3 ≈ P-3.
- **Batch 5: IMF, WTO, UNOPS, OECD, ECB** — Camoufox small portals. Include EU/OECD/NATO nationality exceptions. IMF Workday (imf.wd5.myworkdayjobs.com/IMF). WTO SmartRecruiters. UNOPS (careers.unops.org — web-preclean.py works). OECD SmartRecruiters. ECB via impactpool proxy.
- **Batch 6: Tiered/Marginal Portals** — UNDP, WFP, World Bank, UNHCR, UNFPA, ICMPD, UNITAR, UNU, GICHD, UNDRR, WMO, UNESCAP, UNESCWA, UNICRI. Uses web-preclean.py for efficiency where browser isn't needed. Many are Inspira-backed or have limited ICT postings.
- **Batch 7: INSPIRA (Secretariat)** — Public front-end (careers.un.org). Covers UNCTAD, UNECE, UNECA, UNWTO, UPU, UN-Habitat, UNOV, UNON, UNSSC, UNIDIR, UNGM, UNJSPF, and all other orgs that use the UN Secretariat staff selection system. Cloudflare-protected; use browser_navigate + browser_console JS extraction. All 7 mandatory keywords: "ICT", "Information Technology", "Digital", "Artificial Intelligence", "ISP", "Telecom", "connectivity".
- **Batch 8 (UNRELIABLE — separate run, separate file)**: Impactpool.org, UNJobNet.org
  - Results written to: `UN-VACANCIES-TRACKER.txt` (same file as all other entries)
  - Same file structure as other entries
  - Only entries confirmed on the official hiring org portal may be added
  - Impactpool/UNJobNet entries must be clearly marked with source in the entry block
  - Only entries confirmed on the official hiring org portal may be added to UN-VACANCIES-TRACKER.txt
- **Batch 9: NATO, ESA** — RESTRICTED. Requires your explicit approval to run. NATO G-grades (Brussels) and ESA A-grades. Nationals-only restrictions apply.

**Manual-only sources:** None currently.

### PHASE 3.5: Vacancy Filtering (Exclusion Rules)

**Apply the following exclusion filters BEFORE scoring and merging entries into `UN-VACANCIES-TRACKER.txt`:**

Any vacancy matching ANY of the following criteria MUST be excluded from the reliable sources file:

| Filter | Match Criteria | Action |
|--------|---------------|--------|
| **Nationals-only** | Title or description contains "nationals only", "nationals ONLY", "national position", "for [country] nationals", "open to [nationality] nationals only" | EXCLUDE |
| **Internships** | Contract type contains "Intern" or "Internship" | EXCLUDE |
| **Volunteers** | Contract type contains "Volunteer" or title contains "Volunteer" | EXCLUDE |
| **Ukraine** | Location contains "Ukraine" or any Ukrainian city name (Kyiv, Lviv, Odesa, Kharkiv, etc.) | EXCLUDE |
| **Junior** | Grade/Level contains "Junior" or "L1-Junior" or title contains "Junior" | EXCLUDE |

**Implementation:**
```python
EXCLUDE_CONTRACT = ["intern", "internship", "volunteer"]
EXCLUDE_LOCATIONS = ["ukraine"]
EXCLUDE_GRADES = ["junior", "l1-junior"]

def should_exclude(entry):
    contract = entry.get("contract", "").lower()
    location = entry.get("location", "").lower()
    grade = entry.get("grade", "").lower()
    title = entry.get("title", "").lower()
    
    if any(kw in contract for kw in EXCLUDE_CONTRACT):
        return True
    if any(kw in title for kw in EXCLUDE_CONTRACT):
        return True
    if any(loc in location for loc in EXCLUDE_LOCATIONS):
        return True
    if any(gr in grade for gr in EXCLUDE_GRADES):
        return True
    if "junior" in title:
        return True
    return False
```

**Note:** Excluded vacancies are NOT added to `UN-VACANCIES-TRACKER.txt`. They are simply skipped.

### PHASE 4: Deduplicate, Score & Merge

⚠️ **Important:** All filtering from Phase 3.5 (Internships, Volunteers, Ukraine locations, Junior positions) has already been applied. Entries in this phase are pre-filtered.

**Deduplication — before adding any entry, check against BOTH files:**
- Same Vacancy ID (check UN-VACANCIES-TRACKER.txt AND UN-VACANCIES-ARCHIVE.txt)
- Same `(title.lower(), organization.lower())` tuple
- Same org + grade + location combination
- **If a Vacancy ID exists in EITHER file, do NOT add it again.**
- The archive file (UN-VACANCIES-ARCHIVE.txt) contains APPLIED: YES entries — these must never re-enter the tracker.

**Scoring formula — 3-dimension model (100 max):**
TOTAL MATCH (%) = (Technical Relevance × 0.60) + (Seniority Alignment × 0.20) + (Strategic Alignment × 0.20)

- **Technical Relevance (60%):** Domain expertise match, relevance of past experience to job responsibilities, hands-on vs theoretical experience, tools/technologies/methodologies, sector alignment (education, public sector, development)
  - 90-100 = Direct and deep expertise
  - 75-89 = Strong relevance, minor gaps
  - 60-74 = Partial overlap
  - 40-59 = Weak relevance
  - <40 = Not relevant

- **Seniority Alignment (20%):** Years of experience vs requirement, leadership level (team/national/global), scope (projects vs systems vs policy), stakeholder level (schools vs ministries vs global orgs), scale of responsibility
  - 90-100 = Fully aligned or exceeds (P-5-ready)
  - 75-89 = Slightly below but credible
  - 60-74 = Mid-level vs senior mismatch
  - 40-59 = Junior mismatch
  - <40 = Strong mismatch

- **Strategic Alignment (20%):** Alignment with mission and impact level, policy and system transformation experience, multi-country or global exposure, thought leadership and influence, ability to shape strategy and advise stakeholders
  - 90-100 = Strong strategic/system-level profile
  - 75-89 = Some strategic exposure
  - 60-74 = Mostly operational
  - 40-59 = Execution-focused
  - <40 = No strategic alignment

**Advanced Rules:**
1. **Bias Correction:** If candidate has non-traditional background (private sector, startup, innovation-driven), do NOT heavily penalize lack of UN/bureaucratic experience. Give more weight to real-world impact and innovation.
2. **High-Value Signal Boosters:** Increase scoring if candidate demonstrates COVID-scale transformation, AI integration in education, national-level/system-level reform, work with governments/ministries, UNICEF/UN exposure.
3. **Red Flags:** Decrease scoring if no relevant domain experience, no leadership for senior roles, purely technical with no system understanding, no stakeholder engagement.

**Color coding (summary table — MANDATORY EMOJI FORMAT):** 🔴 RED (>=75 STRONG FIT), 🟠 ORANGE (65-74 COMPETITIVE), 🟡 YELLOW (50-64 STRETCH), 🟢 GREEN (<50 LOW FIT)

The summary table MUST use emoji color indicators (🔴🟠🟡🟢), not plain text color names. Example row format:
```
1     UNICEF       Innovation Manager, P-4    2026-06-12     🟠 85    00137134
```

**Verdict Logic:**
- 75-100 → STRONG FIT
- 65-74 → COMPETITIVE
- 50-64 → STRETCH
- <50 → LOW FIT

### PHASE 5: Deliver Report

Report separately:
- New entries added to UN-VACANCIES-TRACKER.txt (from reliable sources)
- Number of entries moved to UN-VACANCIES-ARCHIVE.txt (APPLIED: YES / EXPIRED)
- Top 5 matches with scores, deadlines, days remaining
- URGENT deadlines (within 48 hours)
- Blocked sources
- Two files maintained: UN-VACANCIES-TRACKER.txt (active), UN-VACANCIES-ARCHIVE.txt (applied/expired)

---

## Vacancy ID Extraction (NO Sequential IDs)

**Always extract the hiring organization's official ID (NEVER Impactpool's ID):**
- **UNICEF**: `#XXXXXX` from title (e.g., `#00133283`)
- **ITU**: 10-digit numeric from URL
- **UNDP**: Job ID from jobs.undp.org
- **ECB**: Numeric from URL
- **UN Careers (Inspira)**: 6-digit Job ID

**NEVER use Impactpool's numeric ID as the Vacancy ID.**

**Fallback only:** Use `[GEN-XXXXXX]`. Never use `VAC-XXX`.

---

## Anti-Hallucination Checklist (MANDATORY)

Before adding ANY entry, answer YES to all 7:
1. Did I actually visit a live page?
2. Does the job title match exactly?
3. Did I extract a real Vacancy ID (from official portal, NOT Impactpool)?
4. Did I verify the deadline on the live page?
5. Did I verify the grade/level?
6. Did I verify the location?
7. Is this entry actually new?

**For Impactpool/UNJobNet entries (Batch 12):** Additional requirement:
8. Did I verify the job exists on the hiring org's official career portal?

---

## File Format

### Summary Table (Top of File)

Every tracker file begins with a **Vacancy Summary Table** inserted after the header block. The table is auto-generated and must be regenerated whenever entries are added, removed, or modified.

**Table columns:** `# | Organization | Position Title | Deadline | Score (color-coded) | Vacancy ID`

**Sorting:** By deadline date (nearest first). TBD deadlines appear at the end.

**Score color coding in table:**
- 🔴 >=75 STRONG FIT
- 🟠 65-74 COMPETITIVE
- 🟡 50-64 STRETCH
- 🟢 <50 LOW FIT

**Regeneration rule:** The summary table MUST be regenerated after every file write operation (add, remove, modify entries). Use `execute_code` Python to rebuild the table from the current entries and prepend it to the file content.

---

## Entry Format (exact — MANDATORY consistent structure)

Every entry MUST follow this exact format. The colored header block with separator lines is required — never omit it.

```
================================================================================

🟠 ORANGE — Full Job Title Here

================================================================================
- Title: Full Title (exact from live page)
- VACANCY ID: xxxxxxxx
- Organization: Org Name
- Grade: P-X / Consultant / etc.
- Location: City, Country
- Deadline: YYYY-MM-DD
- Contract type: Fixed Term / Consultancy / Roster
- Estimated compensation (USD): $XXK-$XXK (include if available)
- HYPERLINK: https://...
- SCORE: XX/100
- APPLIED: NO

MATCH ANALYSIS:
- Technical Relevance (60%): XX — Description of domain expertise match, relevance of past experience, hands-on vs theoretical, tools/technologies, sector alignment
- Seniority Alignment (20%): XX — Description of years of experience, leadership level, scope, stakeholder level, scale
- Strategic Alignment (20%): XX — Description of mission alignment, policy/system transformation, multi-country exposure, thought leadership

-

🚀 Positioning Advice:
- Bullet points on how candidate should present themselves for this specific role
- Reference specific experience signals that match the job requirements
- Note any gaps and how to frame them positively


📊 Verdict: [STRONG FIT / COMPETITIVE / STRETCH / LOW FIT] (XX%)
Confidence Level: [HIGH / MEDIUM / LOW]
KEY OVERLAPPING SKILLS: skill1, skill2, skill3
POTENTIAL GAPS: gap1, gap2
STRATEGIC FIT: Brief strategic fit assessment


```

**Format rules:**
- The `================================================================================` separator (80 chars) appears BEFORE and AFTER the colored header line
- The colored header line format: `🔴 RED — Title` / `🟠 ORANGE — Title` / `🟡 YELLOW — Title` / `🟢 GREEN — Title`
- Color is determined by score: 🔴 75+, 🟠 65-74, 🟡 50-64, 🟢 <50
- Blank line before and after the colored header line (between the two separators)
- `Estimated compensation` line is optional — include only if the source page lists it
- After `🚀 Positioning Advice:` section: TWO blank lines before `📊 Verdict:`
- After `📊 Verdict:`: extra lines (Confidence Level, KEY OVERLAPPING SKILLS, POTENTIAL GAPS, STRATEGIC FIT, INTERVIEW PROBABILITY) follow directly
- Entries are separated by the next entry's leading `================================================================================` separator
- Some entries may lack a Verdict line or Positioning Advice — this is OK if the original source data didn't include them. Preserve whatever data exists.

---

## Known Pitfalls & Solutions

- **User says "stop" or "stop stop":** HALT current work immediately. Do not continue the previous task. Do not over-process. Execute the new instruction directly.

- **FAO RSS feed broken (2026-05-19)**: The RSS URL now returns "Unable to Create an RSS Feed" error. Use browser_navigate to FAO Taleo instead (JS-rendered SPA, 118+ jobs).

- **Camoufox `browser_type` 500 errors**: Camoufox intermittently returns 500 Internal Server Error on `browser_type` actions (observed on WFP, WHO). The browser recovers automatically — navigate away and back, then retry. Do NOT treat this as a permanent failure.

- **Camoufox full tab crash recovery**: After repeated 500 errors across multiple sites, the Camoufox browser tab can become completely unresponsive (all subsequent browser calls fail). The "navigate away and back" recovery does NOT fix this. Full recovery requires: (1) DELETE the dead tab via `curl -X DELETE http://localhost:9377/tabs/<tab_id>`, (2) restart the Camoufox server: `terminal(background=true, command="/usr/local/bin/camofox server start")` — the Hermes Camofox client auto-creates a new tab on the next browser call. Signal: if you see `500 Internal Server Error` on `browser_navigate` (not just `browser_type`), the tab is likely dead. Check with `curl http://localhost:9377/health` to confirm the server is still alive.

- **Camoufox full crash — profile wipe required**: When Camoufox browser spontaneously stops responding after prolonged scraping (5+ portals), simply killing the headless browser and restarting the server may not work — the profile dir becomes corrupted. The server reports `browserConnected: false` indefinitely. **Fix**: Kill the server, wipe profiles, restart:
  ```bash
  pkill -9 -f camofox
  rm -rf ~/.camofox/profiles
  rm -rf config/profiles/agent/home/.camofox/profiles
  camofox server start
  ```
  Wait for `browserConnected: true` in health check before using browser tools. The stale tab ID cached by Hermes tools will cause 404 errors on the first browser_navigate — do `/reset` in the TUI or just navigate to a new URL (the client auto-creates a fresh tab).

- **Camoufox stuck/zombie during long scanning sessions**: After scanning 5+ portals in one session, the headless Camoufox browser can accumulate stale tabs and become unresponsive even though the Camofox server responds on `/health`. **Quick fix**: Load `skill_view(name='camoufox-clean')` and follow its steps — it kills only the headless browser process (cascade-killing all tabs/children) while preserving the Node.js REST server on port 9377. The server auto-spawns a fresh browser on the next request. If browser tools still fail afterward, do `/reset` in the Hermes TUI to clear the cached stale tab ID.

- **WHO Taleo extraction**: The main `who.int/careers` page is informational. Actual listings are on the Taleo side (`careers.who.int/careersection/ex/jobsearch.ftl`). Search for "Digital" (yields ~10 results, as of 2026-05-28), "AI", and "ICT" individually — each returns different subsets. "Digital" yields the most ICT-relevant roles (AI Software Engineer Lead, Data Engineering Developer, GIS Specialist, IHIP Web Developer).
- **UNHCR Workday navigation**: Requires accepting cookies (`Accept Cookies` button) before search results or filters will behave correctly.
- **WFP (SuccessFactors)**: Direct deep links often trigger `Bad Request (400)`. Use a clean entry URL and navigate/search manually or use UN JobNet as a proxy.
- **`write_file` silently fails when called from subagents:** delegate_task subagents cannot reliably write tracker files. Always return structured data from subagents and do the file write in the parent agent using execute_code + Path().write_text() + sync.
- **Subagent timeout on browser-based scanning:** Batch scanning via delegate_task with browser_navigate consistently times out at 600s. For multi-batch scanning, use direct terminal commands (web-preclean.py) from the parent agent instead of delegating browser work. Terminal-based scanning is 10-30s per site vs 600s timeout per batch.
- **Impactpool via web-preclean.py:** 119KB raw HTML -> 0KB clean markdown (100% reduction, trafilatura). Home page returns empty extraction. **Must use browser_navigate for Impactpool.** Working search URL: `https://www.impactpool.org/search?q=ICT` (NOT `/jobs` path). Results render client-side. Filter by organization type "United Nations System" for relevant results.
- **Non-standard deadline formats cause silent expiry misses:** Entries may have "May 12, 2026", "May 7, 2026" (no year), or just "May" as deadline text instead of YYYY-MM-DD. When parsing for expiry detection, try `'%B %d %Y'` (with comma stripped), then `'%B %d'` + assume current year. ISO regex `^\d{4}-\d{2}-\d{2}` alone will miss these and leave expired entries in the active file.
- **Cross-file cleanup must be destructive on archive IDs:** After moving expired entries to archive, verify that NO Vacancy ID from UN-VACANCIES-ARCHIVE.txt still exists in UN-VACANCIES-TRACKER.txt. Use `comm -12` to check. If overlap exists, the active entry MUST be removed — the archive is authoritative for "do not track."
- **Summary table row count must equal entry count exactly:** After every file write, count `- Title:` lines vs numbered rows in the table. If they mismatch, the table was built from a subset. **Fix: Rebuild the table by parsing ALL entry blocks (split by `================================================================================` separator blocks containing `- Title:`).** The correct approach: find all blocks containing `- Title:`, extract fields from each, build the sorted table from the complete list.
- **UNJobNet via web-preclean.py:** 72KB raw HTML -> 1KB clean (99% reduction). Returns only JS template placeholders (e.g., `{{pager.total.toLocaleString()}} jobs`). URL search params do NOT filter results — all jobs shown regardless of query. **Must use browser_navigate for UNJobNet.** Even in browser, level filters via URL don't work reliably. The site shows 3,387+ total jobs; filtering for ICT requires browser interaction or manual parsing of full job list.
- **WHO Taleo search:** Use keyword "Digital" (yields 7 results). "ICT" and "AI" return 0 results on WHO Taleo. The RSS feed button + multi-line view switch reveals job titles/URLs without needing to parse the JS-rendered table. Job detail pages are JS-rendered SPA and return empty via web-preclean.py.
- **os.fsync Bad file descriptor:** Use `Path().write_text()` in Python, then `sync` in terminal
- **🚨 TRACKER RE-NUMBERING CORRUPTS TITLES (2026-07-02):** When rebuilding the tracker summary table with Python, NEVER parse existing entry lines into fields and reassemble them. Splitting on whitespace breaks multi-word organization names ("World Bank" → "World" + "Bank", "UN Secretariat" → "UN" + "Secretariat") and destroys titles. **Safe approach:** preserve each line's full original text, strip ONLY the leading number with `re.sub(r'^\d+\s+', '', raw_line)`, and prepend the new number. Do NOT split fields and reformat.
- **write_file fails on new directories:** If the parent directory doesn't exist, write_file may silently fail. Always create directories first via `terminal(command='mkdir -p ...')` before writing files.
- **UN-VACANCIES-TRACKER.txt file format:** The file has a summary table at top (emoji color-coded rows) followed by full entry blocks. Each entry block starts with `================================================================================`, then a blank line, then the colored header (`🔴 RED — Title` / `🟠 ORANGE — Title` / `🟡 YELLOW — Title` / `🟢 GREEN — Title`), then another blank line, then `================================================================================`, then the fields starting with `- Title:`. When adding entries: (1) restore from backup, (2) parse existing entries by splitting on `================================================================================` blocks containing `- Title:`, (3) add new entries to the list, (4) rebuild the COMPLETE file (summary table + all entries in canonical format) in one write via `Path().write_text()`, (5) run `sync`, (6) verify with `wc -l` and count of `- Title:` occurrences matching the table row count. NEVER append to the existing file — it corrupts the format.

- **🚨 TRACKER FILE IS TABLE-ONLY — no entry blocks exist**: The current UN-VACANCIES-TRACKER.txt file contains ONLY the summary table (no full entry blocks with MATCH ANALYSIS, Positioning Advice, or Verdict sections). The entry block format described in this skill is the TARGET format for new entries, but the existing file is table-only. When adding a new entry: (1) insert a table row in the correct deadline-sorted position, (2) append the full entry block AFTER the table footer, (3) update the total count. Do NOT try to parse the file as entry blocks — it has none. Use `patch` to insert the table row, then append the entry block at the end. Verify by reading the file after write.
- **OCR for difficult sites:** Tesseract 5.5.2 is pre-installed on macOS at `/usr/local/bin/tesseract` with English language pack. Use for screenshot-based text extraction when other methods fail. Workflow: (1) browser_navigate to page, (2) screenshot captured automatically at `config/cache/screenshots/`, (3) run `tesseract <screenshot.png> /tmp/ocr_output --psm 6`, (4) read `/tmp/ocr_output.txt`. Successfully extracted World Bank CSOD job listings from screenshot when browser_navigate returned empty page. Limitation: current model (owl-alpha) does not support vision/image input, so `vision_analyze` and `browser_vision` cannot process screenshots. Tesseract is the only OCR option.
- **Scrapling StealthyFetcher for JS-rendered SPAs:** Fallback method when Camoufox is unavailable or crashes on a specific site. Scrapling v0.4.7 at `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`. Pattern:
```python
from scrapling import StealthyFetcher
page = StealthyFetcher.fetch("URL", headless=True, wait=8000, block_webrtc=True)
text = page.get_all_text()  # use this, NOT .text which may be empty
```
The `wait` parameter (milliseconds) is critical — 8000-10000ms needed for SPAs to fully render. Use `block_webrtc=True` to prevent WebRTC leaks that trigger bot detection.
- **web_extract token inefficiency (gemini-3-flash-preview):** The auxiliary model's massive context window causes raw/unprocessed HTML to be dumped directly into the summarization prompt, resulting in 10x token bloat. **FIX: Always pre-process with `web-preclean.py` (trafilatura -> html2text -> bs4 -> regex) BEFORE any content reaches the LLM.** This enforces a strict 90-95% token reduction. See Rule 2.
- **ReliefWeb API v1 deprecated (410):** Use website directly
- **Impactpool is UNRELIABLE:** Never use as primary source; always verify on official portal
- **UNJobNet scraping method:** `/jobs` returns 200 with full HTML (no Cloudflare). Use `scrapling extract stealthy-fetch` CLI or `web-preclean.py` to download. Parse with Python regex: split by `<a class="py-2 link-primary h6 fw-bold" href="/jobs/detail/\d+">` then extract title, org, location from each card. Job detail URLs: `/jobs/detail/<numeric-id>`. Vacancy ID format: `UNJN-<numeric-id>`.
- **ITU (jobs.itu.int) — JS-rendered, requires browser_navigate** (NOT web-clean.py). The search page renders job results via JavaScript. web-clean.py returns only cookie consent banner. Use browser_navigate, accept cookies, then extract job data from the rendered table. Search with keywords "Digital" (30 results), "AI" (10 results), "ICT" for comprehensive coverage.
- **UNICEF careers portal appears JS-rendered or blocks automated requests:** The main portal (jobs.unicef.org) returns empty or incomplete content via web-clean.py. Use browser_navigate for full access, or verify accessibility before scanning.
- **Camoufox server start:** The `camofox server start --background` flag doesn't exist. Using `nohup` or `&` gets blocked by Hermes shell guards. The ONLY working pattern is `terminal(background=true, command="camofox server start")`. Verify with `curl http://localhost:9377/health`. If the server stops, browser tools fall back to the default browser silently — always check health before scanning.
- **Camoufox config requirements:** The Hermes Camofox client requires `browser.camofox.user_id` and `browser.camofox.session_key` to be set in `config.yaml` for tab creation. Without these, the `/tabs` endpoint returns "userId and session_key required". Set both to non-empty strings (e.g., `user_id: hermes-default`, `session_key: hermes-session-1`). Also requires `CAMOFOX_URL=http://localhost:9377` in `config/.env`.
- **Camoufox UNICEF crash:** Camoufox (v2.4.3 server) crashes with "Internal Server Error" when navigating to `careers.unicef.org`. This is a known compatibility issue with UNICEF's JS-heavy SPA. **Fall back to default browser** for UNICEF scanning. Detect the crash by checking for empty snapshots or error responses after navigation.
- **Camoufox LaunchAgent PATH:** If using a macOS LaunchAgent to auto-start the server, the plist MUST include `EnvironmentVariables.PATH` with `/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin`. Without this, the LaunchAgent gets "env: node: No such file or directory" errors.

- **Impactpool file corruption from previous merges:** If the tracker file accumulates duplicate summary tables from previous merge operations, rebuild from backup. Before writing, check for multiple "VACANCY SUMMARY TABLE" headers. If found, rebuild the entire file from scratch: parse all entry blocks, rebuild the single summary table, write once. **Always restore from backup first.** After every file write, count `- Title:` lines vs numbered rows in the table. If they mismatch, the table was built from a subset — rebuild.

- **Block removal over-removal pitfall:** When removing specific entries from tracker files, matching on `===` delimiter lines causes over-removal because `===` appears at the start AND end of each entry block. **Fix: Match on the color-emoji title line specifically** (regex: `^[🔴🟠🟡🟢] [A-Z]+ — `) to identify entry starts, then extract the Vacancy ID from the following lines. Each entry block spans from one `================================================================================` (before colored header) to the next entry's `================================================================================`.
- **UNHCR Workday:** IT job family filter returns "0 JOBS FOUND" as of 2026-05-18. UNHCR currently has no relevant ICT/AI vacancies. Skip UNHCR in future scans unless specifically requested.
- **IOM Oracle Cloud:** Direct deep links trigger 400 Bad Request. Use clean entry URL (https://fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs) and navigate/search manually.
- **ILO Cloudflare on www.ilo.org:** The main ILO website (www.ilo.org/careers) is Cloudflare-protected and shows a bot verification page. Use jobs.ilo.org directly — it is a separate SuccessFactors platform (NOT Taleo) and works fine via Camoufox. Navigate to jobs.ilo.org/go/All-Jobs/2842101/ for the full listing. As of 2026-06-21, only 9 jobs total, mostly admin/finance — very few ICT roles.
- **UNOPS page size parameter ignored:** The URL parameter `jobRecordsPerPage=84` is ignored by the UNOPS careers platform — it always returns 6 results per page. Do NOT attempt to increase page size via URL params. Either paginate through pages 1-14 manually, or extract all jobs via browser_console JS DOM extraction (`Array.from(document.querySelectorAll('article'))`).
- **CRITICAL — Never reference the skill's own scripts directory for execution:** All script paths in active instructions MUST point to the workdir copy (e.g., `WORKDIR/scripts/web-preclean.py`), NEVER to `skills/research/un-jobs-search-minimaltoken/scripts/`. The skill's own directory is read-only reference only. If a script is needed, copy it into the workdir first, then reference the workdir path. The user explicitly rejected mixing execution with the skill's own files.
- **🚨 PER-AGENCY SCRIPTS SAVE TO ~/Downloads/TEST/ NOT WORKDIR (2026-07-02):** All `run_{portal}.py` scripts save JD files to `~/Downloads/TEST/UN_{AGENCY}/` instead of the workdir `JD_FILES/{AGENCY}/`. After all scripts complete, ALWAYS check `~/Downloads/TEST/` for new files and copy them to the correct workdir location. Do NOT assume "0 new JDs" just because `JD_FILES/` has no new files. See `references/per-agency-script-pitfalls-2026-07-02.md` for the full copy script.
- **UNICEF search URL:** The /en-us/search/ path redirects to /en-us/listing/. Use the listing page directly with keyword filter via browser search box.
- **WHO Taleo "Digital" search:** Returns 10 results (as of 2026-05-28, vs 7-8 in earlier scans). "AI" returns ~6 results (including re-listed Digital/AI roles), "ICT" returns ~8 results covering emergency telecom, connectivity infrastructure, and digital policy roles. Job details (`/jobdetail.ftl?job=XXXXXXX`) are JS-rendered SPAs — use `browser_navigate` to view them, or use `web-preclean.py` which returns clean markdown from ITU job detail pages (93% token reduction). Use all three keywords ("Digital", "AI", "ICT") for comprehensive WHO coverage.
- **UNDP web-clean.py:** Works via /cj_view_jobs.cfm path. Most ICT roles are NPSA (national) level. No new P-level ICT roles found in 2026-05-18 scan.
- **UNESCO web-clean.py:** Works and returns structured table. Search for "Digital AI ICT" returns 21 results, mostly internships/nationals-only/junior.
- **FAO** (jobs.fao.org/careersection/fao_external/jobsearch.ftl) — JS-rendered SPA with 118+ jobs. RSS feed available at https://jobs.fao.org/careersection/feed/joblist.rss?lang=en&portal=8105120163 (returns ~11 most recent jobs). Use RSS feed instead of browser for quick scans.
- **ICAO** (icaocareers.icao.int/careers/Home/Vacancies) — FULLY ACCESSIBLE via browser. HTML tables with job listings. Sections: Professional, General Service, Consulting, YAPP. Extract via `document.body.innerText` or table parsing. Job IDs are numeric (e.g., 34167, 276434).
- **IMO** (recruit.imo.org) — JS-rendered. Jobs in button elements. Extract via `document.body.innerText`. Vacancy Reference format: V.N. XX-XX (Fixed Term), CA XX-XX (Consultant), STA XX-XX (Temporary/Roster).
- **World Bank CSOD** — browser_navigate returns empty page (JS SPA fails to render). Scrapling StealthyFetcher also only gets filter sidebar (country counts), NOT actual job listings. API endpoints require SAML authentication (redirect to login.microsoftonline.com). **Best approach:** Use Impactpool as lead generator for World Bank, then verify on official portal. Alternatively use tesseract OCR on a browser screenshot as last resort.
- **UNCTAD** — No dedicated career portal. Uses UN Secretariat Inspira system. Search via inspira.un.org or careers.un.org with UNCTAD filter.
- **Impactpool browser extraction:** 138 ICT jobs found with UN System filter. Notable leads: Chief IT Service (UNOV, D-1), Sr Info Systems Officer (UNEP, P-5), Director IT (CIMMYT). Always verify on official portal.
- **UNJobNet:** Vue.js SPA, results render client-side. Filter for "United Nations System" available. Shows 3,387+ total jobs.
- **UNOPS careers search returns zero for ICT keywords:** Use Impactpool proxy
- **UNDP tiered applications:** Note Tier 0/1/2/3 in match analysis
|- **Workday downtime:** 5PM Sat – 5AM Sun Belgrade time
- **Low-yield batches 7-11 confirmation (2026-05-28):** Batches 7-11 cover small UN specialized agencies (UNWTO, UPU, WMO, UN-Habitat, UNDRR, UNICRI, UNITAR, UNSSC, UNU, UNIDIR, UNGM, GICHD, UNOV, UNON). After systematic verification, these batches produce ~0 ICT/AI vacancies per scan cycle. **Recommended approach:** For these batches, use SearXNG quick-check first (see `references/searxng-portal-discovery.md`) rather than full browser-based scanning. If SearXNG returns no ICT-relevant results for an org, skip it. WMO (erecruit.wmo.int) is the only exception — its e-recruit system occasionally posts ICT roles (IT Project Manager, Cloud Telecoms Officer), but as of 2026-05-28 all were expired. UNITAR had a P5 Chief ICT Section reference but the URL returned 404.
- **Exclusion filters active:** Internships, Volunteers, Ukraine-located, and Junior positions are automatically excluded from `UN-VACANCIES-TRACKER.txt` (see Phase 3.5).

---

## References

- `references/credentials.md` — Login credentials for portals
- `references/inspira-extraction.md` — INSPIRA (careers.un.org) browser console extraction protocol, keyword strategy, Cloudflare bypass
- `references/icrc-rss-extraction.md` — ICRC careers RSS feed extraction, Belgrade Hub rules, triplicate dedup bug
- `references/portal-access-patterns-2026-05.md` — Newly discovered portals (WHO Taleo, UNHCR Workday, IAEA Taleo), JS-rendered SPA extraction patterns, URL redirects, inaccessible list
- `references/scoring-guide.md` — Detailed scoring rubric
- `references/matching-keywords.md` — Target tokens for search/scoring
- `references/safe-file-rebuild-procedure.md` — Step-by-step safe rebuild procedure to avoid entry loss
- `references/portal-classification-map.md` — All sources and access patterns
- `references/impactpool-extraction.md` — Impactpool search patterns
- `references/anti-hallucination-checklist.md` — Pre-entry verification
- `references/cloudflare-blocked-sites.md` — CF-blocked sites and workarounds
- `references/pre-cleaner-scraper.md` — web-preclean.py usage and benchmarks (v2.0 — trafilatura + html2text + bs4 pipeline)
- `scripts/web-preclean.py` — The precleaning script (copied to workdir at `WORKDIR/scripts/web-preclean.py`); run as `python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/web-preclean.py <URL> [max_chars]`
- `references/who-taleo-extraction.md` — WHO Taleo portal extraction guide (browser_navigate + JS patterns)
- `references/coe-talents-extraction.md` — COE Talents portal extraction guide (browser_navigate + JS pagination)
- `references/unjobnet-extraction.md` — UNJobNet.org extraction guide (scrapling stealth CLI + regex parsing)
- `references/token-optimization-protocol.md` — Decision tree, hard token limits, scrape report format
- `references/unreliable-sources.md` — Impactpool.org and UNJobNet.org unreliability notice, rules, separate file output
- `references/three-file-architecture.md` — Historical reference: original three-file tracking system (now simplified to two files). Merge logic and scoring model still apply.
- `references/test-run-validation-2026-06-21.md` — Full skill audit + 3-portal test run (WHO, ILO, UNOPS). Browser console extraction patterns, scoring validation, issues found and fixed.
- `references/scrapling-stealthy-fetcher.md` — Scrapling v0.4.7 usage for JS-rendered SPAs (World Bank CSOD, IMO, WFP Workday)
- `references/camoufox-browser-type-crashes.md` — Camoufox anti-detect browser integration (preferred for JS SPAs as of 2026-05-19)
- `references/unicef-browser-console-extraction.md` — UNICEF job scraping via browser_console JS DOM extraction (avoids browser_type crash)
- `references/imf-workday-portal.md` — IMF Workday portal (imf.wd5.myworkdayjobs.com/IMF) — small job count, few ICT roles
- `references/tesseract-ocr-screenshots.md` — Tesseract OCR fallback for screenshot text extraction
- `references/portal-accessibility-verification-2026-05.md` — May 2026 systematic verification of all blocked/inaccessible UN career portals with per-portal findings
- `references/file-cleanup-lessons-2026-05-19.md` — File cleanup and reformatting lessons: APPLIED:YES detection, stray separator fragments, inconsistent formatting, rebuild verification checklist
- `references/oecd-smartrecruiters.md` — OECD SmartRecruiters portal (jobs.smartrecruiters.com/OECD) and WTO shared platform
- `references/unfpa-portal.md` — UNFPA career portal crash pattern and fallback strategies
- `references/per-agency-script-pitfalls-2026-07-02.md` — Per-agency scraper script pitfalls: scripts save to ~/Downloads/TEST/ not workdir, tracker re-numbering corrupts titles, UNESCO TextHandler error, UNICEF HTTP 202 throttling, parallel execution confirmed working
