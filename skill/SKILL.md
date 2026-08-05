---
name: un-jobs-search
description: >-
  Total and fully reliable UN sector vacancies extraction and tracking.
  Merges un-jobs-search-minimaltoken (token-optimized scanning, 32+ direct
  career portals) with new-jobs-search (full JD scraper, 128 JD files,
  25 agencies, Per-Agency Scripts). Scans ALL UN/International organization
  career portals. Extracts full JDs. Maintains UN-VACANCIES-TRACKER.txt.
  Scores using vacancy-compatibility-scoring-engine **v5.0** (loaded as
  a skill, not inline) with full CV repository reference.
  **CONTEXTUAL PRE-FILTER: broad keyword capture across 10 career contexts
  (ICT, EdTech, telecom, AI/ML, UN/dev, government, healthcare, finance,
  enterprise IT, transit). Scrape FIRST, disqualify LATER in scoring.**
  NO batch speedup. NO title-only scoring.
version: 2.1.0
author: User / Hermes Agent
tags: [un-jobs, direct-portals, scoring, full-jd, tracker, one-by-one, broad-scan]
related_skills:
  - vacancy-compatibility-scoring-engine
  - cv-repository
  - tracker-file-format
---

# UN-JOBS-SEARCH — Total UN Sector Vacancies System v1.2

## MODEL-SPECIFIC EXECUTION PROTOCOL (DEEPSEEK V4 FLASH)

**This section is MANDATORY for Deepseek V4 Flash. Read it FIRST. Follow it EXACTLY.**

### Who You Are
You are a disciplined scanning agent. You run per-agency scraper scripts to extract UN job vacancies, score them, and maintain the tracker file. You do NOT think creatively. You do NOT improvise. You follow the steps below in order. If something is not covered by these rules, report it and move on — do NOT invent solutions.

### READING RULE — CRITICAL FOR TOKEN EFFICIENCY
This skill file is 1920 lines / 114KB. Reading it all will burn 300K+ tokens. DO NOT READ THE FULL FILE.
- Read ONLY L24-L218 (the Deepseek section you are reading now). That is ALL you need to execute.
- The remaining 1700 lines are legacy reference material. Do NOT read them unless you hit a specific edge case that requires looking up a reference.
- If you need a specific reference, use `read_file` with `offset` and `limit` to read only the relevant section — never read more than 200 lines at a time.
- The Deepseek section below contains everything you need: scan queue, exact commands, execution steps, error handling. Do NOT scroll past L218.

### HARD LIMITS
- Maximum 50 tool calls per session
- Maximum 8 portals per session (pick from the Daily Scan Queue below)
- Maximum 1 execute_code call per phase (bulk operations)
- If a portal script takes more than 3 tool calls to run, SKIP it and report "SKIPPED — script timeout"
- If turn count exceeds 50, STOP immediately — write results, deliver report, stop
- If the skill file is longer than 200 lines to read, read it in 200-line chunks (offset + limit)

### ABSOLUTE PROHIBITIONS (violating ANY of these is a critical failure)
1. NEVER read or write files outside the workdir: `~/Downloads/DATA_REPOSITORY/WORKDIR/`
2. NEVER write new Python scraper scripts (.py files) — use ONLY existing scripts in `~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/`
3. NEVER use `write_file` or `patch` on tracker files — use `execute_code` with `Path().write_text()` only
4. NEVER hallucinate job titles, deadlines, grades, locations, or vacancy IDs — if a script did not output it, do NOT add it
5. NEVER delegate scanning to subagents — do everything in the parent agent
6. NEVER retry a failed portal script more than once — report "SKIPPED" and move on
7. NEVER skip Phase 0 (hygiene) — backup and expired cleanup are mandatory every session
8. NEVER load the `un-jobs-search-minimaltoken` skill — it is LEGACY. This skill (`un-jobs-search`) is the ONLY correct one.
9. NEVER use `web-preclean.py` — that is a minimaltoken tool. Use the per-agency `run_{portal}.py` scripts instead.

### 🚨🚨🚨 CRITICAL DEADLINE WARNING — READ THIS OR RISK CORRUPTING THE TRACKER 🚨🚨🚨

**INSPIRA API DEADLINE PITFALL (confirmed 2026-06-21):**
The INSPIRA API returns `endDate` as a UTC timestamp like `2026-06-21T03:59:59.000Z`. The `T03:59:59.000Z` is a **UTC midnight rollover grace period** — the actual displayed deadline on the UN careers page is **ONE DAY EARLIER** (June 20 in this example).

**RULE: For ALL INSPIRA jobs, the real deadline = endDate date MINUS 1 day.**
- API says `2026-06-21` → real deadline is `2026-06-20`
- API says `2026-07-18` → real deadline is `2026-07-17`

**VERIFICATION PROTOCOL (MANDATORY — do NOT skip):**
1. After extracting a deadline from the INSPIRA API, check if the job is still in the **active ITECNET listing** (`/api/public/opening/jo/list/filteredV2/en` with ITECNET filter)
2. If the job is **absent** from the active listing → it is **EXPIRED**, regardless of what endDate says
3. If unsure, check the job detail page at `https://careers.un.org/jobSearchDescription/{JID}?language=en` for "no longer available" text
4. **When in doubt, set the deadline ONE DAY EARLIER** — it is far better to mark a job as expired a day early than to keep an expired job in the tracker and waste the user's time

**This applies to INSPIRA jobs only** (UN_ prefix VIDs). Other portals (UNICEF, WHO, ITU, etc.) have their own deadline formats — always verify against the source page.

**Consequence of getting this wrong:** The user will see an expired vacancy as "open" with a deadline that hasn't passed yet, apply to it, and discover it's closed. This wastes their time and erodes trust in the tracker. This happened on 2026-06-21 with UN_276853 — the tracker showed deadline 2026-06-21 but the actual deadline was June 20 and the job was already expired.

### SYSTEM-WIDE TITLE-GATE ELIMINATION (2026-08-05) — ALL 27 SCRIPTS
The FAO miss exposed that **every** portal script still used the title-only `is_ict_title()` pre-filter. On 2026-08-05 the gate was eliminated from ALL scripts:
- **Category A (gate + body check existed):** `run_who.py`, `run_workday.py`, `run_icrc_v2.py`, `run_unido.py`, `run_unesco_v4.py`, `run_unitar_v4.py`, `run_unicef.py`, `run_itu_v4.py`, `run_inspira_v4.py` — gate replaced with `not HARD_REJECT.search(title)`; body check (`is_ict_body`/`is_ict_full`) now decides.
- **Category B (gate, NO body check):** `run_ecb.py`, `run_iaea.py`, `run_icao_v3.py`, `run_icmpd_v3.py`, `run_ifad.py`, `run_ilo_v3.py`, `run_imo.py`, `run_oecd_v4.py`, `run_undp_v4.py`, `run_unfpa_v4.py`, `run_unhcr.py`, `run_unu.py`, `run_wipo.py`, `run_wmo.py`, `run_worldbank.py` — gate removed AND `is_ict_body(jd_text)` check + `HARD_REJECT` regex added before save.
- **Keyword:** bare `"digital"` injected into EVERY script's ICT keyword list (many lists only had `"digital transformation"`, `"digital officer"` — a plain "Digital FAO" title had no match).
- **Body-window:** `body[:1000]` → `body[:3000]` in `run_unicef.py`, `run_unido.py`, `run_workday.py`, `run_icrc_v2.py` (boilerplate pushes ICT content past 1000 chars).
- **FOLLOW-UP (AGENT review 2026-08-05):** scripts with SEPARATE body keyword lists need "digital" injected there too — `run_itu_v4.py`, `run_unesco_v4.py`, `run_unitar_v4.py` each have `ICT_BODY_KW` (independent of `ICT_TITLE_KW`); ITU/UNITAR/UNESCO body lists lacked bare "digital" (only "digital transformation"). Fixed. `run_inspira_v4.py`/`run_unops_v3.py`/`run_who.py` build `ICT_FULL_KW`/`ICT_KW_FULL` from title lists so they inherit it. ALWAYS check for independent body lists when injecting keywords.
- **Pitfall:** when patching gate-removal, watch for orphaned `else:` blocks (happened in `run_oecd_v4.py` — the old `else: print(skip)` survived the replacement and broke syntax).
- **Pitfall:** inserted SKIP prints must use the file's actual loop variable — `run_undp_v4.py` uses `job['title']` not `title` (NameError risk).
- **Verification:** `python3 -m py_compile run_*.py` (all 27 OK); `grep -rn "is_ict_title(" run_*.py | grep -v def` must be empty; smoke test proves `is_ict_full('Deputy Director, CSI Digital FAO...')` → True and IAEA `is_ict_body('Application Maintenance...')` → True.
- **Backup:** `BACKUP/scripts_pre_20260805/` (27 files).

### FAO SCRIPT FIX (2026-08-05) — TITLE GATE REMOVED (same bug class as UNOPS)
The `run_fao.py` script had the title-only ICT gate that missed ICT-adjacent senior roles whose titles contain no ICT keyword. Confirmed miss: **FAO 2600555 Deputy Director, CSI Digital FAO and Agro-Informatics Division (D-1, Rome, DL 2026-08-07)** — title has no ICT keyword ("Deputy Director, CSI Digital...") so `is_ict_title()` returned False and the body was never fetched, even though the body is pure IT ("responsible for all Information Technology (IT) activities", ERP ecosystem, digital transformation).
- **Fix:** `passing=[(j,t,u) for j,t,u in new if not HARD_REJECT.search(t)]` — fetch ALL non-hard-reject candidates, decide on body via `is_ict_full()`.
- **Fix 2:** `is_ict_full` body window raised `body[:1000]` → `body[:3000]` — FAO pages start with boilerplate (diversity statement), ICT content can sit past 1000 chars.
- **Result:** re-run recovered 2600555 + 8 other saved JDs. Verify after FAO scans that `Deputy Director`, `Director`, `Chief`, `Head of` titles with IT bodies are captured.

### TRACKER COLUMN-FIXED INSERT (2026-08-05) — CRITICAL FOR ALL TRACKER EDITS
The tracker file uses FIXED COLUMN positions (not flexible spacing). Measured from the WMO row template:
- `ljust(5)` row number | `ljust(22)` org | `ljust(47)` title (max 44 visible, truncate with `…`) | `ljust(15)` deadline | `ljust(10)` score+emoji | `ljust(30)` VID | applied
- **DO NOT** rebuild rows from scratch with guessed offsets — parse an existing template row, measure token positions, clone.
- Tracker rows may have pre-existing corruption (title bleeding into deadline column) — verify with `re.match(r'^\d{4}-\d{2}-\d{2}$', dl)` before trusting sort order.
- Always backup before edit: `cp UN-VACANCIES-TRACKER.txt BACKUP/UN-VACANCIES-TRACKER_$(date +%Y%m%d_%H%M%S).txt`

### UNOPS SCRIPT FIX (2026-07-20 v4.0)
The `run_unops_v3.py` had 3 bugs fixed on 2026-07-20:
- **Bug 1:** `fetch_page("https://careers.unops.org/")` fetched the **homepage**, not the job search page. Fixed to `https://careers.unops.org/careersmarketplace/SearchJobs/?jobRecordsPerPage=6&jobOffset={offset}` with pagination.
- **Bug 2:** Zero pagination handling — only saw 6 of 85 jobs. Added pagination loop through all pages.
- **Bug 3:** Title-only ICT pre-filter gate (`is_ict_title()`) rejected ICT-adjacent roles like "Project Manager (Implementation)" whose JD body contains digital transformation/innovation/data/AI but title has no ICT keywords. Removed the title gate — now fetches all non-HARD-REJECT jobs and checks body content (`is_ict_body()` only). This follows the skill philosophy: "Scrape FIRST, disqualify LATER in scoring."
- **Result:** 65 new JDs found (was missing ~60 due to wrong URL + title gate). ICT-relevant roles with non-ICT titles (PM, Director, Innovation) are now captured.
- **File:** `scripts/run_unops_v3.py` (kept filename for backward compatibility, code is v4.0)

### UNICEF SCRIPT KNOWN ISSUES (2026-06-21 fix)
The `run_unicef.py` script had 3 bugs fixed on 2026-06-21:
- **Bug 1:** `parse_snapshot_jobs()` looked for `href="/en-us/job/(\d+)/"` but actual UNICEF PageUp URLs are `/cw/en-us/job/...`
- **Bug 2:** Parser looked for `href="..."` but camofox CLI snapshot uses `/url: ...` format
- **Bug 3:** `cf_open("about:blank")` blocked by camofox (only http/https allowed) — changed to `https://jobs.unicef.org/en-us/listing/`
- **Reference:** `references/unicef-script-fix-2026-06-21.md`

### UNICEF TITLE PRE-FILTER TIGHTENED (2026-06-21 v3.0)
The `broad_scan_keywords.py` title pre-filter was tightened from 200+ broad keywords to ~100 focused ICT/AI/telecom/connectivity/education keywords.
- **Removed:** generic management, policy, healthcare, finance, government, Africa locations, climate/energy, transit, GIS/geospatial, "education" (generic), "school", "learning", "monitoring", "evaluation", "procurement", "security", "systems", "technical", "engineer" (generic), "network" (generic), "innovation", "migration", "vendor", "enterprise" (generic), "infrastructure" (generic), "bi ", "knowledge management", "data management", "m&e", "supply chain", "sourcing"
- **Kept:** ICT core, telecom/infrastructure, AI/ML/agentic, enterprise IT, connectivity, ISP, EdTech, data/analytics, platform, cloud, cyber
- **Result:** UNICEF Phase A went from 151 ICT candidates → 7 ICT candidates. Phase B now completes in ~2.5 minutes (no timeout).
- **All 30 portal scripts** import from `broad_scan_keywords.py` — this change affects all scans.
- **Reference:** `references/unicef-script-fix-2026-06-21.md`

### DAILY SCAN QUEUE (pick 8 per session, rotate daily)
Priority order — scan portals that have the most ICT/AI yield:

**Tier 1 (always scan — high ICT yield):**
1. WHO — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_who.py`
2. ITU — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_itu_v4.py`
3. UNICEF — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_unicef.py` (primary, uses tightened broad_scan_keywords.py v3.0)
   - Alternative: `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/camoufox_fulljd_scraper_v2.py` (Camoufox REST API, also covers ICRC)
4. IAEA — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_iaea.py`
5. UNOPS — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_unops_v3.py`

**Tier 2 (rotate daily — medium yield):**
6. ICRC — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_icrc_v2.py` (primary)
   - Alternative: covered by camoufox_fulljd_scraper_v2.py (same script as UNICEF alternative)
7. UNESCO — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_unesco_v4.py`
8. ILO — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_ilo_v3.py`
9. OECD — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_oecd_v4.py`
10. WFP — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_workday.py` (Workday — covers WFP, IMF, UNHCR)
11. WIPO — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_wipo.py` (Taleo portal — ICT Dept posts IT transformation/change management roles)

**Tier 3 (low yield — scan only if time/budget allows):**
12. UNDP — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_undp_v4.py`
13. WMO — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_wmo.py`
14. FAO — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_fao.py`
15. ICAO — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_icao_v3.py`
16. INSPIRA — `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_inspira_v4.py` (covers UNCTAD, UNECE, UNECA, UNWTO, UPU, UN-Habitat, UNOV, UNON, UNSSC, UNIDIR, UNGM, UNJSPF)

### 🚨🚨🚨 CRITICAL: INSPIRA DUAL-QUERY REQUIREMENT — READ THIS OR MISS VACANCIES 🚨🚨🚨

**CONFIRMED BUG (2026-07-27):** The INSPIRA scraper `run_inspira_v4.py` was querying ONLY Job Network `ITECNET`. This missed ~6 Consultant/CON-level roles per cycle that are classified under Job Family `IST` (Information Management Systems and Technology) but have **NO Job Network assignment** (`Job Network: -`).

**Root cause:** INSPIRA/Inspira classifies vacancies by BOTH Job Network (e.g. ITECNET) AND Job Family (e.g. IST). Consultant and Individual Contractor roles are frequently posted with `jf=IST` but `jn=` (empty). The old script queried `jn=["ITECNET"]` only, so it never saw these jobs.

**FIX APPLIED (2026-07-27):** The script now runs TWO API queries:
1. `jn=["ITECNET"]` — staff/permanent ICT roles (P-3 and above)
2. `jf=["IST"]` — catches Consultant/CON roles with no Job Network assignment

Results are deduplicated by Job ID via `seen_ids` set.

**VERIFICATION CHECKLIST (MANDATORY after every INSPIRA scan):**
After running `run_inspira_v4.py`, the agent MUST verify no IST-family jobs were missed:
1. Navigate to `https://careers.un.org/jobopening?language=en&data=%7B%22keyword%22%3A%22%22%2C%22jf%22%3A%5B%22IST%22%5D%7D` (IST filter on careers.un.org)
2. Count the total jobs shown (e.g. "22 Jobs found")
3. Compare with the script output: `Total jobs fetched: N`
4. If the script fetched FEWER jobs than the website shows, the script is missing jobs — REPORT immediately and investigate
5. This check is NON-NEGOTIABLE — skipping it means you might miss vacancies the user expects tracked

**When the user provides a filtered INSPIRA URL:** Always extract the `jf` (Job Family) and/or `jn` (Job Network) parameters from the URL's `data` JSON. Cross-reference against the script's query parameters. If the user's URL uses a filter the script doesn't query, REPORT the gap immediately.

**Skip these (low/zero ICT yield, confirmed 2026-05-28; WIPO removed 2026-07-28 — ICT Dept posts relevant roles):**
- UNFPA, UNICRI, UNITAR, UNU, GICHD, UNDRR, UNESCAP, UNESCWA — produce ~0 ICT vacancies per cycle
- IMO, IFAD, UNIDO, UNHCR — rarely ICT roles, scan only if explicitly requested

### EXECUTION SEQUENCE (follow in order — do NOT skip steps)

**STEP 1 — Date Check (1 tool call)**
```
terminal: date +%Y-%m-%d
```
Store the date. You will use it for expiry comparison.

**STEP 2 — Read Tracker & Backup (1 execute_code call)**
Read both files from workdir:
- UN-VACANCIES-TRACKER.txt
- UN-VACANCIES-ARCHIVE.txt

Backup both to BACKUP/ subdirectory with today's date+time suffix.
Extract all existing Vacancy IDs from the tracker into a Python set for dedup.

**STEP 3 — Expired Cleanup (same execute_code call as Step 2)**
Parse every deadline in the tracker summary table. If deadline < today AND APPLIED: NO:
- Move entry to UN-VACANCIES-ARCHIVE.txt with APPLIED: EXPIRED
- Remove from UN-VACANCIES-TRACKER.txt
- Count how many were moved

If any entry has APPLIED: YES, move it to archive regardless of deadline.
Rebuild the summary table after removals.

**STEP 4 — Report Urgent Deadlines**
From the tracker, list entries with deadline within 48 hours of today.
Report them before scanning new portals.

**STEP 5 — Check Camoufox Health (1 tool call)**
```
terminal: curl -s http://localhost:9377/health
```
If response does not contain `"ok":true`:
```
terminal(background=true, command="camofox server start")
```
Wait 5 seconds, retry health check. If still failing, report "CANNOT SCAN — Camoufox down" and deliver Phase 0-4 results only.

**STEP 6 — Run Per-Agency Scraper Scripts (1-2 tool calls per script)**
For each portal in your queue (8 max):

a) Run the script via terminal:
```
uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_{portal}.py
```
Use `terminal(background=true, notify_on_complete=true)` for long-running scripts.
Wait for completion via `process(action="wait", session_id=..., timeout=120)`.

b) When the script completes, check its output:
- Did it produce JD files in JD_FILES/{AGENCY}/? → Good, proceed to scoring
- Did it produce an error? → Report "SKIPPED — {portal} script failed: {error}" and move on
- Did it produce 0 new jobs? → That's valid. Report "0 new jobs for {portal}" and move on

**STEP 7 — Score New Entries (1 execute_code call)**
Load the vacancy-compatibility-scoring-engine skill:
```
skill_view(name='vacancy-compatibility-scoring-engine')
```
Then for each new JD file found:
- Parse the JD content
- Apply the 7-parameter scoring model from the scoring engine skill
- Score range: 0-100
- Color: RED >=75, ORANGE 65-74, YELLOW 50-64, GREEN <50

**STEP 8 — Write Tracker (1 execute_code call)**
Build the complete new file content in Python:
- Regenerate summary table (sorted by deadline, color-coded)
- Add new entries in the canonical entry format (see TRACKER FILES section below)
- Write ONCE with Path().write_text()
- Run `sync` in terminal
- Verify with `wc -l`

**STEP 9 — Deliver Report (final output)**

The report is MANDATORY. You MUST deliver it even if the scan was interrupted or failed. Use this EXACT format:

```
UN JOBS SCAN REPORT — {DATE}

SCAN SUMMARY
- Date: YYYY-MM-DD
- Camoufox status: OK / DOWN
- Tracker entries before scan: N
- Tracker entries after scan: N
- New entries added: N
- Expired entries moved to archive: N
- Urgent deadlines (within 48h): N

AGENCIES SCANNED
| # | Agency | Script | Status | New JDs | New Tracker Entries | Notes |
|---|--------|--------|--------|---------|---------------------|-------|
| 1 | WHO | run_who.py | OK | 3 | 2 | Found AI/Digital roles |
| 2 | ITU | run_itu_v4.py | OK | 5 | 4 | |
| 3 | IAEA | run_iaea.py | 0-NEW | 0 | 0 | No ICT roles found |
| ... | | | | | | |

AGENCIES NOT SCANNED
| # | Agency | Reason |
|---|--------|--------|
| 1 | UNESCO | Not in today's queue (rotation) |
| 2 | WFP | SKIPPED — script timeout |
| 3 | UNICEF | SKIPPED — Camoufox 500 error |
| 4 | ILO | SKIPPED — script failed: ImportError |
| ... | | |

NEW ENTRIES ADDED TO TRACKER
| # | Vacancy ID | Agency | Title | Grade | Location | Deadline | Score | Color |
|---|-----------|--------|-------|-------|----------|----------|-------|-------|
| 1 | WHO_2601739 | WHO | Unit Head (AI and Frontier Technologies) | P5 | Geneva | 2026-07-01 | 86 | RED |
| 2 | ITU_993610255 | ITU | Senior CIRT Governance Consultant | Consultant | TBD | 82 | RED |
| ... | | | | | | | | |

If NO new entries were added, state: "No new entries added this session."

EXPIRED ENTRIES MOVED TO ARCHIVE
| # | Vacancy ID | Agency | Title | Deadline | Reason |
|---|-----------|--------|-------|----------|--------|
| 1 | UN_276853 | UN Secretariat | INFORMATION SYSTEMS OFFICER | 2026-06-21 | EXPIRED |
| ... | | | | | |

If NO entries expired, state: "No entries expired."

URGENT DEADLINES (within 48 hours)
| # | Vacancy ID | Agency | Title | Deadline | Days Left | Score |
|---|-----------|--------|-------|----------|-----------|-------|
| 1 | UNICEF_593565 | UNICEF | Digital Cash Transfer Advisor | 2026-06-22 | 1 | 75 |
| ... | | | | | | |

If NO urgent deadlines, state: "No urgent deadlines."

BLOCKED / FAILED SOURCES
- List any portal that returned 403/500/timeout with the specific error

END OF REPORT
```

**Rules for the report:**
- The AGENCIES SCANNED table MUST list every portal you actually ran a script for
- The AGENCIES NOT SCANNED table MUST list every portal in the Daily Scan Queue that you did NOT scan, with a reason
- Count in "New JDs" = number of .md files created in JD_FILES/{AGENCY}/
- Count in "New Tracker Entries" = number of entries actually written to UN-VACANCIES-TRACKER.txt
- "Tracker entries before/after" = line count from `wc -l` before and after the write
- If the scan was interrupted before completion, still report what was done and mark remaining agencies as "NOT SCANNED — session interrupted"

### ANTI-HALLUCINATION RULES (Deepseek V4 Flash specific)
1. If a scraper script fails, do NOT assume jobs exist on that portal. Report "SKIPPED" and move on.
2. If you cannot extract a Vacancy ID from the script output or JD file, do NOT invent one. Use `[GEN-UNKNOWN]` and flag it.
3. If a deadline is not visible in the JD file, write "TBD" — do NOT guess.
4. If a grade is not visible, write "Unknown" — do NOT guess.
5. If a script produces empty output, do NOT fabricate job listings. Report "0 new jobs" — that is valid.
6. NEVER copy job titles from memory or previous sessions. ONLY use what the script output and JD files show.
7. If a portal has 0 ICT-relevant jobs, that is a valid result. Report "0 ICT jobs found" — do NOT pad the results.

### ERROR HANDLING DECISION TREE
```
Camoufox health check fails?
  -> terminal(background=true, command="camofox server start")
  -> wait 5 seconds
  -> retry health check once
  -> if still fails: report "CANNOT SCAN - Camoufox down", deliver Phase 0-4 results only

Scraper script fails with error?
  -> read the error message from process output
  -> do NOT retry the same script
  -> report "SKIPPED - {portal}: {error message first line}"
  -> move on to next portal

Scraper script produces 0 JD files?
  -> that is a valid result, not an error
  -> report "0 new jobs for {portal}"
  -> move on to next portal

execute_code fails with Python error?
  -> read the error message
  -> fix the Python syntax/logic
  -> retry ONCE
  -> if still fails: report error, deliver what you have, STOP

Camoufox tab crash (500 on browser_navigate)?
  -> SKIP the portal that caused it
  -> do NOT attempt tab recovery - let the next script handle it
  -> report "SKIPPED - Camoufox tab crash on {portal}"
```

### WHAT TO DO IF YOU ARE CONFUSED
If you are unsure about any step:
1. Do NOT improvise or guess
2. Report "UNCLEAR - need guidance on: [specific question]"
3. Skip that step and continue with the next one
4. Deliver partial results

It is ALWAYS better to deliver partial correct results than to hallucinate full results.

### NATIONALITY NOTE
User holds dual citizenship: Serbian AND Czech Republic (EU). Serbian nationals-only positions are OPEN to him. Czech citizenship grants EU/NATO/OECD eligibility. Never exclude Serbian-national positions. For any "nationals only" filter: exclude ONLY if the required nationality doesn't match Serbian or Czech.

---

## 🚨 DISAMBIGUATION: This skill vs un-jobs-search-minimaltoken

**This skill (`un-jobs-search`) uses `WORKDIR/` — a DIFFERENT directory from `un-jobs-search-minimaltoken` which uses `DATA_REPOSITORY/` files.**

| Aspect | This skill (un-jobs-search) | un-jobs-search-minimaltoken |
|--------|---------------------------|-----------------------------|
| WORKDIR | `WORKDIR/` | `WORKDIR-MINIMALTOKEN/` |
| Tracker | `UN-VACANCIES-TRACKER.txt` | `UN_SECTOR_VACCANCIES.txt` (legacy) |
| JDs | `JD_FILES/{AGENCY}/` | N/A |
| Sources | Direct portals via per-agency scripts | Direct portals via web-preclean.py |

**Before any execution, confirm which skill's WORKDIR to use.** The old `DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt` files are legacy artifacts from the pre-June 2026 format. The current master tracker is `WORKDIR/UN-VACANCIES-TRACKER.txt`.

### 🚨 PITFALL: Loading the wrong skill first causes tracker confusion

If you load `un-jobs-search-minimaltoken` first (which references `DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt`), and then switch to `un-jobs-search` (which uses `WORKDIR/UN-VACANCIES-TRACKER.txt`), the backup will be from the wrong file. The user will notice immediately and be frustrated.

**Rule:** Always confirm which tracker file the session is meant to work with. The canonical answer for "UN-JOBS-SEARCH" (the skill the user asked for) is `WORKDIR/UN-VACANCIES-TRACKER.txt`. Do NOT read or backup `DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt` unless the user explicitly tells you that file is the target.

### 🚨 PITFALL: Legacy-to-Master Migration Gaps

Some entries from the legacy `UN_SECTOR_VACCANCIES.txt` may have been dropped during the June 2026 format migration — especially rolling/TBD entries, applied-YES entries, and entries with duplicate VIDs. When a user asks "does this vacancy exist" and you search only the master tracker, you may falsely report it missing.

**Vacancy validation procedure:** See `references/vacancy-validation-workflow.md` for the full 5-step validate-from-file-to-live-portal protocol. In short: JD_FILES → master tracker → legacy tracker → archive → live portal check.

## WORKING DIRECTORY (ABSOLUTE — ALL PATHS BELOW THIS)

**WORKDIR =** `~/Downloads/DATA_REPOSITORY/WORKDIR`

All generated files, backups, extracted JDs, intermediate output, logs, and
temporary files go here. The data repo root (`DATA_REPOSITORY/`) stays
clean — only old legacy tracker files live there.

### Directory Layout
```
WORKDIR/
├── UN-VACANCIES-TRACKER.txt     ← Master tracker (single source of truth)
├── UN-VACANCIES-ARCHIVE.txt      ← Applied/expired/removed vacancies
├── JD_FILES/                     ← Full JD markdown extracts (204 files, 25 agencies)
│   ├── UN_ECB/       (2 files)
│   ├── UN_FAO/       (4 files)
│   ├── UN_IAEA/      (5 files)
│   ├── UN_ICAO/      (3 files)
│   ├── UN_ICMPD/     (2 files)
│   ├── UN_ICRC/      (8 files)
│   ├── UN_ILO/       (2 files)
│   ├── UN_IMF/       (2 files)
│   ├── UN_INSPIRA/   (15 files)
│   ├── UN_ITU/       (26 files)
│   ├── UN_OECD/      (3 files)
│   ├── UN_UNDP/      (2 files)
│   ├── UN_UNESCO/    (9 files)
│   ├── UN_UNFPA/     (5 files)
│   ├── UN_UNICEF/    (5 files)
│   ├── UN_UNICRI/    (1 file)
│   ├── UN_UNIDO/     (3 files)
│   ├── UN_UNITAR/    (7 files)
│   ├── UN_UNOPS/     (10 files)
│   ├── UN_UNU/       (4 files)
│   ├── UN_WFP/       (5 files)
│   ├── UN_WHO/       (12 files)
│   ├── UN_WMO/       (4 files)
│   ├── UN_WORLDBANK/ (5 files)
│   └── UN_WTO/       (4 files)
├── BACKUP/                       ← Pre-write backups (single folder, timestamped filenames)
├── scripts/                      ← Per-agency scraper scripts
├── references/                   ← Reference docs from both source skills
└── UN-VACANCIES-TRACKER.txt      ← New master tracker
```

---

## 🚨 DAILY ACTIVITY LOG — DO NOT PLACE HERE

When logging daily activity, the log goes at the DATA_REPOSITORY root:
`~/Downloads/DATA_REPOSITORY/DAILY_ACTIVITY_LOG.md`

**NEVER** place the daily log inside `WORKDIR/` or any other subfolder. The daily log is a cross-cutting record spanning all profiles and skills.

See the `daily-activity-logger` skill for the full protocol.

---

## 🚨🚨🚨 BACKUP RULE — ABSOLUTELY MANDATORY 🚨🚨🚨

**BEFORE ANY WRITE to the tracker or archive file, BACKUP FIRST.**

**All backups go to the single `BACKUP/` folder (not timestamped subfolders):**

```bash
mkdir -p "~/Downloads/DATA_REPOSITORY/WORKDIR/BACKUP"
DATE=$(date +%Y%m%d_%H%M)
cp ~/Downloads/DATA_REPOSITORY/WORKDIR/UN-VACANCIES-TRACKER.txt \
   "~/Downloads/DATA_REPOSITORY/WORKDIR/BACKUP/UN-VACANCIES-TRACKER_BACKUP_${DATE}.txt"
cp ~/Downloads/DATA_REPOSITORY/WORKDIR/UN-VACANCIES-ARCHIVE.txt \
   "~/Downloads/DATA_REPOSITORY/WORKDIR/BACKUP/UN-VACANCIES-ARCHIVE_BACKUP_${DATE}.txt"
```

**Verify backups exist** after copying. If files are 0 bytes or missing, fix before proceeding.

**AFTER backup verify, also check cross-file consistency:** No Vacancy ID should appear in both the active tracker and the archive file.

## 🚨🚨🚨 TRACKER CORRUPTION RECOVERY PROTOCOL 🚨🚨🚨

**When another agent (AGENT/2/3) or a bug corrupts the tracker, follow this step-by-step. Do NOT develop new scripts — use existing tools and the WORKDIR only.**

### Step 1: Diagnose the Corruption
The canonical corruption signature (AGENT pattern, 2026-06-09):
- Tracker file balloons from ~97 lines (82 entries) to 238+ lines
- VIDs are broken: `WFP_WFP_JR122932_Fu`, `IMF_IMF_26_R9271_Da`, `UNICEF_593542` → `NICEF_593542`
- Titles repeat or merge with deadlines: `Technical Specialist Technical Specialist fo`
- Sort order lost — entries with deadlines appear after TBD entries
- Duplicate entries with the same VID but different scores

**First check:**
```bash
# Count rows
grep -c '^[0-9]' UN-VACANCIES-TRACKER.txt
# Check for broken VIDs (repeated words, truncated)
grep -oP '^\s*\d+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\K\S+' UN-VACANCIES-TRACKER.txt | grep -E '(.)\1{3,}'
# Compare line count to backup average (82 entries ≈ 97 lines)
```

### Step 2: BACKUP the Corrupted Tracker (before doing anything)
```bash
cp UN-VACANCIES-TRACKER.txt BACKUP/UN-VACANCIES-TRACKER_CORRUPTED_$(date +%Y%m%d_%H%M).txt
```

### Step 3: Find the Best Backup
Check `BACKUP/` for the most recent backup files. Prefer the one with naming pattern indicating final/correct state:
- `UN-VACANCIES-TRACKER_FINAL_*.txt` — most likely clean
- `UN-VACANCIES-TRACKER_BACKUP_*.txt` — good if recent
- Skip `UN-VACANCIES-TRACKER_CORRUPTED_*` (that's the one we just saved)

Verify line count ~97 for 82 entries, ~110 for 95 entries.

### Step 4: Read the Backup
Read the **full** backup file with `read_file()`. Confirm:
- Data rows are properly numbered (1-82)
- Each row ends with `NO` or `YES`
- No duplicate VIDs
- No repeated/truncated titles

### Step 5: Read the Archive
Check the archive file. Extract all VIDs with:
```python
import re
for line in archive_text.split('\n'):
    m = re.search(r'Vacancy ID:\s*(\S+)', line)
    if m: archive_vids.add(m.group(1))
```

### Step 6: Check Overlap
Compare backup VIDs vs archive VIDs. **Zero overlap expected** — the archive is for applied/expired entries, the backup is active vacancies. If overlap exists, flag it but do NOT remove entries — notify the user.

### Step 7: Restore from Backup
```bash
cp BACKUP/UN-VACANCIES-TRACKER_FINAL_*.txt UN-VACANCIES-TRACKER.txt
sync
```

### Step 8: Fix Sort Order
If the backup has entries appended out of sort order (e.g., rows 78-82 are dated entries after TBD rows), parse all entries and re-sort:

**Sort key** (Python):
```python
def sort_key(e):
    dl = e['deadline']
    is_rost = any(k in e['title'].upper() for k in ["ROSTER", "EXPRESSION OF INTEREST", "LTA "])
    if is_rost: return (3, datetime.max, -e['score_val'])
    if dl == 'TBD': return (2, datetime.max, -e['score_val'])
    try:
        dt = datetime.strptime(dl, '%Y-%m-%d').date()
        if dt < TODAY: return (1, datetime.max, -e['score_val'])
        return (0, dt, -e['score_val'])
    except: return (2, datetime.max, -e['score_val'])
```

Write with: `Active (sorted by deadline) → Rolling (sorted by score)`. 4-section format with `🟢 OPEN` / `🟡 ROLLING` headers.

### Step 9: Verification Checklist
1. ✅ Sequential numbering 1-N
2. ✅ All rows end with `NO` or `YES` (regex: `r'\s+(NO|YES)\s*$'`)
3. ✅ No duplicate VIDs
4. ✅ No overlap with archive
5. ✅ Sort: active by deadline ascending, rolling by score descending
6. ✅ `sync` after write
7. ✅ Total line count ≈ N + 15

### Step 10: Clean Up Corrupted Files (optional)
Move the corrupted file with a descriptive name:
```bash
cp BACKUP/UN-VACANCIES-TRACKER_CORRUPTED_*.txt BACKUP/AGENT-CORRUPTED-TRACKER.txt
```
Delete the redundant backups from BACKUP/ (keep only the most recent good one and the first corrupted one as a forensic artifact).

---

## TRACKER FILES

### UN-VACANCIES-TRACKER.txt (Master — Single Source of Truth)

**Format (identical to old UN_SECTOR_VACCANCIES.txt format):**

```
================================================================================
UN VACANCIES TRACKER — Full JD Scoring
Generated: YYYY-MM-DD
================================================================================

🔵 VACANCY SUMMARY TABLE

#     Organization           Position Title                               Deadline         Score      Vacancy ID                     Applied
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1     UNICEF                UPSHIFT AI & Digital Strategy Consultant      2026-06-07      🟠 81      593259                        NO
2     ...
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Total: N active vacancies
Last updated: YYYY-MM-DD | Last scan: YYYY-MM-DD
Color coding: 🔴 75+ STRONG FIT | 🟠 65-74 COMPETITIVE | 🟡 50-64 STRETCH | 🟢 <50 LOW FIT
================================================================================
```

**Column widths (FIXED — pad with spaces) — LIVE FORMAT verified 2026-08-03 (136 chars total, NOT 134):**
- `#`: 5 chars left-aligned (e.g. `1    `)
- `Organization`: 22 chars, truncate with `…` if longer, pad to 22
- `Position Title`: 47 chars, truncate at 47, pad to 47
- `Deadline`: 15 chars (e.g. `2026-06-15     ` or `TBD            ` or `Open (Roster)  `)
- `Score`: 10 chars — emoji + space + 2-digit number (e.g. `🟡 72      `)
- `Vacancy ID`: **30 chars** left-aligned, pad with spaces
- `Applied`: **7 chars** (`NO     ` or `YES    `)

**Total row width: 5 + 22 + 47 + 15 + 10 + 30 + 7 = 136 chars** (verified against live tracker on 2026-08-03)

**🚨 PITFALL (2026-08-03):** This skill previously documented 134 chars / 29-char VID / 44-char title / 16-char deadline / 8-char applied. The LIVE tracker is 136 chars: title=47, deadline=15, vid=30, applied=7. Parsing the live file with the old 134-char spec yields 0 rows (data loss risk on rebuild). ALWAYS measure column boundaries from the live file's anchor regexes before rebuilding: dl=`2026-\d\d-\d\d|TBD|Open`, score=`[🔴🟠🟡🟢] \d+` at index 89, vid=`[A-Za-z0-9_\-]+` at index 99, applied at index 129.

**Build rows with explicit padding:**
```python
def make_row(e):
    num = str(e['num']).ljust(5)[:5]
    org = e['org'].ljust(22)[:22]
    title = e['title'].ljust(47)[:47]
    dl = e['deadline'].ljust(15)[:15]
    score = e['score'].ljust(10)[:10]
    vid = e['vid'].ljust(30)[:30]
    applied = ('YES' if e['applied'] else 'NO').ljust(7)[:7]
    return f"{num}{org}{title}{dl}{score}{vid}{applied}"
```

**Separator line:** exactly 134 dashes (`'-' * 134`)

**Total row width: 136 chars** (5+22+47+15+10+30+7=136)

**🚨 PITFALL — Row width verification must use raw line, not rstrip():**
When verifying row widths after a rebuild, `len(line.rstrip())` will show ~128 chars because trailing spaces after the `Applied` column are stripped. The `Applied` field is 8 chars (`NO      `) but `rstrip()` collapses it to 2 (`NO`), losing 6 chars. Always verify with `len(line)` (no rstrip) to get the true 134-char width. Example:
```python
# ✅ CORRECT
assert len(row) == 134, f"Row width {len(row)} != 134"

# ❌ WRONG — rstrip() strips trailing padding
assert len(row.rstrip()) == 134  # Will fail: shows ~128
```

**Separator line:** exactly 196 dashes (134 row chars + 62 extra = 196 total)

**Sort order:** By deadline ascending. TBD/Roster at bottom. Stable sort for equal deadlines.

**Score emoji color mapping (scoring engine v5.0 ZERO-EMPTY-SCREENING):**
- 🔴 RED: 75+ (STRONG FIT)
- 🟠 ORANGE: 65-74 (COMPETITIVE)
- 🟡 YELLOW: 50-64 (STRETCH)
- 🟢 GREEN: below 50 (LOW FIT)

### UN-VACANCIES-ARCHIVE.txt

```
================================================================================
ARCHIVED: YYYY-MM-DD | APPLIED: YES / EXPIRED
Organization: [org]
Title: [full title]
Vacancy ID: [id]
Deadline: [deadline]
Score: [score]
================================================================================
```

---

## 🚨 SCORING MODE: BATCH + CALIBRATE (20+ files) or ONE-BY-ONE (<20 files) 🚨

**For <20 scoreable files:** Score each manually with the full 7-parameter engine.
**For 20+ scoreable files:** Use programmatic batch scoring (validated Jun 2026) followed by manual calibration of top 10-20 entries.

### Batch Scoring Workflow (20+ files) — Validated 2026-06-03 on 90 files

1. **Load CV Repository:** `skill_view(name='cv-repository')`
2. **Load Scoring Engine:** `skill_view(name='vacancy-compatibility-scoring-engine')`
3. **Run pre-filter** on all JD files: classify as SCOREABLE / DISQUALIFIED / SKIP
   - Use `scripts/prefilter_and_classify.py` as template
   - Hard filters: nationals-only, Ukraine, intern/volunteer, grade too low (P-2/G-series/N0-A/B), expired, non-broad match
   - Check for cookie-banner false positives (file with duties/responsibilities sections is NOT garbage even if it has cookie text)
4. **Run programmatic batch scorer** (see `scripts/batch_score_all.py`)
   - P1: keyword-group scoring per domain, capped by domain (see Domain Caps table below)
   - P2: title/grade-based seniority (Director→13, Senior→11, Lead→10, Specialist→9, Officer→8)
   - P3: org-based base score (UNICEF→9, WHO/ITU/FAO→7, IAEA/ILO→5, IMF/WB→4...)
   - P4: MSc+MPhil base 8-10 depending on field match
   - P5: English+Russian base 8, French required→5
   - P6: EU/Schengen location→10, home-based→10, DC→4, hardship→3-5
   - P7: AI/ML bonus +4, UNICEF+digital +3, telecom +2, Director penalty -3
5. **Apply manual calibration overrides** to top 10-20 entries:
   - Cross-reference against scoring engine's calibration anchors (ILO Director D-2=81, WHO AI Lead=79, UNICEF UPSHIFT=75, IMF IT Strategist=75, etc.)
   - Apply current-work override check (Olivia Education Moodle/Canvas, Hermes AI frameworks)
   - Fix known inflation patterns: keyword-based P1 overcounts non-core domains
6. **Rebuild tracker from structured dict** — see `scripts/rebuild_complete.py` for the canonical approach:
   - Build all entries as Python dict with (org, title, deadline, [total, vid, p1..p7, domain])
   - Split into active (sort by deadline) and roster (sort by score) sections
   - Use `Path().write_text()` with complete rebuilt content — never append/patch/sed
7. **Verify sync** and run post-write checklist

### One-by-One Scoring Rules (for <20 files, or manual calibration of specific entries)
- **Full JD required — NON-NEGOTIABLE:** Never score from title, URL slug, or short description alone. The user explicitly requires scoring on the FULL JD content. If JD content is truncated or empty, re-extract with Camoufox REST API using longer waits (25s+) and `document.body.innerText` (not `outerHTML`). Only score when you have the complete job description including responsibilities, qualifications, and requirements.
- **Arithmetic check:** MUST write `P1(X) + P2(X) + P3(X) + P4(X) + P5(X) + P6(X) + P7(X) = TOTAL(X)` explicitly
- **Domain caps applied (P1 capped by domain):**
  - Telecom / AI / Undersea Fibre → P1 max **22**
  - Data / EdTech / FinTech / Digital Platforms → P1 max **20**
  - Program Management / Strategic Planning / Coordination → P1 max **18**
  - M&E / Learning Design / Partnerships / Policy → P1 max **16**
  - Operations / P-2 equivalent roles / Generalist → P1 max **14**
  - GIS / Remote Sensing (strict) → P1 max **10**
  - Pure SWE / Coding-only (strict) → P1 max **8**
- **Current-work override:** Before finalising any score, check if User's current work (Olivia Education, Hermes) covers role functions not in CV database
- **Do NOT delegate scoring to subagents** — they cannot reference the scoring engine correctly
- **Pre-filter first:** Check hard filters (Ukraine, nationals-only, grade floor, compensation) before scoring
| WFP | 5 | WTO | 1 |

---

## EXISTING JD FILES

**204 JD files from 25 agencies** are already in `JD_FILES/`. See directory layout above.

| Agency | Files | Agency | Files | Agency | Files |
|--------|-------|--------|-------|--------|-------|
|| WHO | 31 | ICRC | 8 | UNICEF | 9 |
|| ITU | 26 | INSPIRA | 16 | UNOPS | 13 |
|| UNESCO | 10 | UNITAR | 7 | WFP | 5 |
|| World Bank | 10 | IAEA | 8 | UNFPA | 7 |
|| UNU | 4 | FAO | 5 | WMO | 5 |
|| WTO | 4 | ICAO | 4 | OECD | 6 |
|| UNIDO | 5 | ECB | 9 | ICMPD | 5 |
|| ILO | 2 | IMF | 2 | UNDP | 13 |
|| UNICRI | 1 | | | | |

---

| WFP | 5 | WTO | 1 |

### Scraped & Working (28 agencies, 204+ JDs)

| # | Agency | Script | Platform | JDs |
|---|--------|--------|----------|-----|
| 1 | INSPIRA (incl. UNDRR, UNESCAP, UNESCWA) | run_inspira_v4.py | API | 15 |
| 2 | ITU | run_itu_v4.py | SuccessFactors | 26 |
| 3 | UNESCO | run_unesco_v4.py | SuccessFactors | 9 |
| 4 | UNITAR | run_unitar_v4.py | Custom CMS | 7 |
| 5 | UNOPS | run_unops_v3.py | Oracle HCM | 10 |
| 6 | UNDP | run_undp_v4.py | Oracle HCM | 2 |
| 7 | UNFPA | run_unfpa_v4.py | Oracle HCM | 5 |
| 8 | WMO | run_wmo.py | Oracle HCM | 4 |
| 9 | ICAO | run_icao_v3.py | Oracle HCM | 3 |
| 10 | WHO | run_who.py + Camoufox REST | Taleo | 12 |
| 11 | IAEA | run_iaea.py | Taleo | 5 |
| 12 | FAO | run_fao.py | Taleo | 4 |
| 13 | ICRC | Camoufox REST API (primary) | Taleo | 8 |
| 14 | OECD | run_oecd_v4.py | SmartRecruiters | 3 |
| 15 | ECB | run_ecb.py | SkillBound | 2 |
| 16 | ICMPD | run_icmpd_v3.py | Custom | 2 |
| 17 | ILO | run_ilo_v3.py | SuccessFactors | 2 |
| 18 | UNIDO | run_unido.py | SuccessFactors | 3 |
| 19 | UNU | run_unu.py | Indeed | 4 |
| 20 | World Bank | run_worldbank.py | CSOD | 5 |
| 21 | IMF | run_workday.py | Workday | 2 |
| 22 | WFP | run_workday.py | Workday | 5 |
| 23 | WTO | Camoufox REST API | Workday | 4 |
| 24 | UNICEF | Camoufox REST API (`camoufox_rest_scan.py`) | PageUp | 10+ |
| 25 | UNICRI | N/A | Inspira | 1 |

### Monitored / Blocked (4 sources)

| # | Agency | Platform | Status |
|---|--------|----------|--------|
| 26 | WIPO | Taleo | ⚪ Monitored — 0 ICT expected |
| 27 | GICHD | Beehire | ⚪ Monitored |
| 28 | IFAD | PeopleSoft | ⚪ Monitored |
| 29 | IMO | Custom | ⚪ Monitored |

**Note:** UNDRR, UNESCAP, and UNESCWA are UN Secretariat entities — their ICT vacancies are covered via the **INSPIRA API** (`run_inspira_v4.py`, ITECNET filter). No separate scraper needed. See rows 26-28 in the Scraped & Working table above.

---

## PLATFORM DECISION TREE

| Platform | Portals | Technique | Status |
|----------|---------|-----------|--------|
| **Camoufox REST API** | WHO, UNICEF, ICRC, WTO | Python urllib → `evaluate` for raw HTML. See `references/camoufox-rest-api-complete-ref.md` | ✅ All 4 working |
| Oracle HCM | WMO, UNDP, UNFPA, ICAO | Playwright API interception → direct detail nav | ✅ Working |
| SuccessFactors | ITU, UNITAR, ILO, UNESCO, UNIDO | Scrapling + Camoufox `inner_text("body")` after JS render | ✅ Working |
| Taleo | ICRC, WHO, IAEA, FAO | Camoufox REST API (ICRC, WHO) / Scrapling (IAEA, FAO) | ✅ Working |
| INSPIRA API | careers.un.org | Direct HTTP POST — no browser | ✅ Working |
| Playwright | ICMPD, ILO, UNU | Standard Playwright with domcontentloaded | ✅ Working |
| Workday | WFP, IMF, UNHCR | Accept cookies → body.innerText | ✅ Working |
| CSOD | World Bank | Camoufox Python serverless + JS DOM query | ✅ Working |
| Scrapling .body | UNESCO search pages | Strip script/style tags, extract text | ✅ Working |
| Indeed | UNU (careers.unu.edu) | Playwright + cookie accept + card text | ✅ Working |
| Cloudflare (blocked) | UNDRR, UNESCAP, UNESCWA, others | Cannot scrape with local tools | ❌ Blocked locally |
| **Cloudflare Browser Rendering** | Any WAF-blocked (REST API) | `cf_crawl`, `cf_scrape`, `cf_markdown`, `cf_content`, `cf_screenshot` | ✅ Active, bypasses WAF |
| **Screenshot→RapidAPI OCR** | Any portal where DOM/API scraping fails (Cloudflare managed JS challenges, broken SPAs) | Camoufox full-page screenshot → RapidAPI OCR `/ocr` endpoint | ✅ Verified 2026-06-15 — ~97% accuracy on detail pages, ~85% on listing pages |
| Custom | IMO | Needs investigation | ❌ Failing |

### Camoufox REST API — Quick Reference

**Server start:** `/usr/local/bin/camofox server start` (background, port 9377)
**Health:** `curl http://localhost:9377/health` → `browserConnected: true`
**⚠️ Initial health check shows `browserConnected: false`** — This is NORMAL. The server starts disconnected. Create a tab first (`POST /tabs`), then check health again. It will show `true` after the first tab is created.
**Server crashes after ~10-15 tab operations** — restart between portals

**Key API rules:**
- `navigate` → `userId` in JSON body (NOT query param)
- `evaluate` → `expression` parameter (NOT `script`), `userId` in body
- `snapshot` → `userId` as query param (returns accessibility tree, NOT raw HTML)
- `/text` endpoint does NOT exist
- Some URLs fail on tab creation → create with example.com first, then navigate

**Portal-specific URLs:**
- WHO: `careers.who.int/careersection/ex/jobsearch.ftl` (Taleo, 7-digit IDs)
- UNICEF: `jobs.unicef.org/en-us/list` (PageUp, 6-digit IDs) — NOT `careers.unicef.org`
- ICRC: `careers.icrc.org/go/All-Jobs/3807301/` (Taleo, 9-digit IDs)
- WTO: `wto.wd103.myworkdayjobs.com/External` (Workday, JR numbers) — NOT SmartRecruiters

**🚨 Camoufox REST API v2 — Methodical One-by-One Extraction (2026-06-06):**
The user prefers quality over speed. When scraping JS-heavy portals (ICRC, UNICEF, WTO):
- **Do NOT rush.** Extract jobs one by one with proper JS render waits (20-25s per page).
- **Wait for content:** Use a `wait_for_content()` helper that polls `document.body.innerText` until it exceeds a minimum character count (2000+ chars) or times out (60s).
- **Full JD required for scoring:** Never score from title or URL slug alone. The scoring engine's FULL-JD RULE is non-negotiable. If the JD content is truncated, re-extract with longer waits or try alternative selectors.
- **is_ict() false positive bug:** When checking ICT relevance, use `document.body.innerText` (rendered text) NOT `document.documentElement.outerHTML` (raw HTML). The HTML contains navigation/boilerplate with ICT keywords (e.g., "information technology" in footer links) that cause false positives. Check the actual visible text content.
- **ICRC Taleo listing:** Renders properly with Camoufox. Job links extractable via regex on `href` attributes. Use 25s wait for listing page.
- **UNICEF PageUp SPA:** Needs 25s+ wait for content. `document.body.innerText` returns 8-14KB of real content (vs 15KB of whitespace from `outerHTML`). Use `innerText` not `innerHTML` for content extraction.
- **`uv run` output buffering:** Scripts run via `terminal(background=True)` with `uv run` buffer ALL output until completion. Do not expect incremental output. Use `process(action='log')` to check progress, or add explicit `print(..., flush=True)` in Python scripts.
- **Server restart between portals:** Kill and restart Camoufox between each portal to avoid the ~10-15 tab crash limit.

**Complete scraper pattern:** See `references/camoufox-rest-api-complete-reference-2026-06-04.md`
**v2 methodical extraction pattern:** See `references/camoufox-rest-api-v2-methodical-extraction-2026-06-06.md`

---

## 📆 DEADLINE AUDIT PROTOCOL — See references/deadline-formats-and-audit-protocol.md

Mission-critical. Contains per-agency deadline format reference, known scraper
date bugs (run_inspira_v4.py off-by-one), systematic audit procedure, and portal
verification URLs. Run whenever deadlines are questioned or before finalizing
a scan report.

---

## ☁️ CLOUDFLARE BROWSER RENDERING API — NEW PREFERRED METHOD (2026-06-05)

The `hermes-cloudflare` plugin has been installed, providing **8 REST tools** via Cloudflare's Browser Rendering API. These run on Cloudflare's edge infrastructure — NOT localhost — meaning they bypass Cloudflare WAF blocks that stop local browsers.

**Plugin:** `~/.hermes/plugins/hermes-cloudflare/` (8 tools, powered by `httpx`)
**Credentials:** `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` (environment variables)
**Storage:** Written to `~/.hermes/profiles/agent/.env` ✓
**Status:** ✅ Verified and active — Cloudflare Browser Rendering API working, confirmed 2026-06-05
**Free-tier limit:** ~10 min browser time per day (~120–300 `cf_content`/`cf_markdown` calls)
**Reactivation:** On Hermes restart, Hermes loads `~/.hermes/profiles/agent/.env` automatically

### Available Tools

| Tool | Emoji | Function | Best For |
|------|-------|----------|----------|
| `cf_crawl` | 🕷️ | Async multi-page crawl | Portal-wide JD discovery |
| `cf_scrape` | 🔍 | CSS selector extraction | Targeted detail scraping (title, deadline, grade) |
| `cf_markdown` | 📝 | Page → clean Markdown | JD text extraction for scoring files |
| `cf_json_extract` | 🤖 | AI-powered structured data | Auto-extracting deadline/grade/location from JD pages |
| `cf_links` | 🔗 | Link discovery from listing pages | Finding job links on portal search pages |
| `cf_content` | 🌐 | Full rendered HTML (post-JS) | Portals that require JS execution (Taleo, Workday, PageUp) |
| `cf_screenshot` | 📸 | Page / element screenshot | Visual verification of job listings |
| `cf_pdf` | 📄 | Page → PDF | Archiving final JD pages |

### Cloudflare Free Tier Limits (CRITICAL — MUST RESPECT)

| Resource | Free Limit | Overage |
|----------|------------|---------|
| **Browser hours** | **10 minutes per DAY** | $0.09 per additional hour (paid: 10 hrs/mo included) |
| **Concurrent browsers** | 3 (only for Browser Sessions, not Quick Actions) | N/A for our use case |

**Our budget: 10 minutes = ~600 seconds per day.**

### UN-JOB-SCAN BUDGET TABLE (Free Tier)

| Operation | Approx. Time per Call | Daily Capacity @ 10 min |
|-----------|---------------------|-------------------------|
| `cf_content` / `cf_markdown` | 2–5 sec | ~120–300 calls |
| `cf_scrape` with selectors | 3–6 sec | ~100–200 calls |
| `cf_screenshot` | 5–10 sec | ~60–120 calls |
| `cf_json_extract` (AI) | 5–12 sec | ~50–120 calls |
| `cf_crawl` (multi-page) | 1–5 min | ~2–10 crawl jobs |
| `cf_pdf` | 5–15 sec | ~40–120 calls |

**🚨 HARD RULE: NEVER exceed 10 minutes/day of browser time.** Track usage per session. Slow/JS-heavy pages (Workday, Taleo, AWS-WAF-challenged sites) burn time faster.

**Cloudflare Browser Rendering limitation — does NOT bypass Cloudflare's own managed JS challenges (verified 2026-06-07)**

**What works:** Hitting a Cloudflare-fronted site that has WAF rules but a plain HTML body. Cloudflare's Browser Rendering API renders the page on Cloudflare's edge and returns the body.

**What DOES NOT work:** Sites that return a *managed JS challenge* (the "Checking your browser / Just a moment..." interstitial). Confirmed failure 2026-06-07 on `https://www.undrr.org/about-us/careers` via the `/browser-rendering/markdown` endpoint — returns the challenge page text, not the careers listing. Same for UNESCAP/UNESCWA.

**Shell token escape technique (2026-06-07):** When calling Cloudflare API from shell, the `export KEY=$(grep ...)` pattern fails because the literal redaction marker `***` injected into terminal commands breaks bash parsing with "unexpected EOF while looking for matching `"'`". ALL approaches that embed the token value in a shell command string fail — bash heredocs, execute_code Python inline, export+grep, and file-based reading all get corrupted. **Fix:** Write a standalone Python wrapper script to `/tmp/` that reads the `.env` file directly using `os.environ` after dotenv-loading it, then calls the Cloudflare API. Execute as `python3 /tmp/script.py` — the key is that no token value ever appears in a shell command string. See `references/shell-token-escape-redaction-2026-06-07.md` for the full working pattern.

**Practical impact:** The skill's optimistic claim that Cloudflare Browser Rendering "bypasses Cloudflare WAF" is partially false. WAF IP/UA rules are bypassed; managed JS challenges (the "I'm human" interstitial) are NOT. Treat these 3 portals as persistently failed.

**Log-and-skip rule:** When CF returns 200 but the body is a "Just a moment..." challenge page, write `PORTAL_ERROR: [Name] — Cloudflare managed JS challenge not bypassed by Browser Rendering API` and move on. Do NOT burn minutes retrying.

### Recommended Usage Pattern for UN Job Scanning

1. **`cf_links`** on listing/search pages: Collect job URLs (fast, ~3 sec each)
2. **`cf_scrape`** on detail pages: Extract specific fields (title, deadline, grade, location) with CSS selectors (~4 sec each)
3. **`cf_markdown`** for full JD text: Only on pre-filtered ICT roles, save to `JD_FILES/` (~5 sec each)
4. **`cf_crawl`**: Reserve for a single portal per scan cycle (e.g., ITU search results with pagination), NOT for portal-hopping

### Do NOT Use for

- ❌ **Wasting calls on non-ICT roles** — pre-filter listing pages first with `cf_links` or `cf_scrape` on title-only selectors
- ❌ **Full-page screenshots of every job** — screenshots are ~8 sec each, strictly reserve for visual verification only
- ❌ **Crawling multiple portals in one crawl job** — `cf_crawl` on cross-domain would burn the budget instantly
- ❌ **Repeated calls to the same unchanged page** — cache results; don't re-scrape until next scan cycle

### Credential Setup (verified 2026-06-05)

Credentials are already saved and working. On a fresh machine, set them like this:

```bash
# File: ~/.hermes/profiles/agent/.env
export CLOUDFLARE_API_TOKEN="cfat_..."
export CLOUDFLARE_ACCOUNT_ID="0e6b9047dd2aa520360de8d051b63471"
```

> Get token from [Cloudflare Dashboard → API Tokens](https://dash.cloudflare.com/profile/api-tokens) — create a **Custom token** with **Browser Rendering → Edit** permission. Account ID is in the right sidebar of any zone.
>
> **Authentication pitfall:** 32-character hex strings (e.g. `0e6b9047...`) are Account IDs, NOT API tokens. Cloudflare rejects Account IDs as tokens with error 6003/6111. The real token is a long alphanumeric string prefixed with `cfat_` (53 chars).

**Quick verification:** Run the standalone script — `uv run python3 scripts/run_cf_verify.py` (or pass token/account_id as args) to verify credentials in one shot without touching the tracker.

### When to Use Cloudflare vs Camoufox vs Local Browser

| Situation | Preferred Tool | Why |
|-----------|--------------|-----|
| Portal behind Cloudflare WAF (UNDRR, UNESCAP, UNESCWA) | `cf_content` / `cf_markdown` | Cloudflare-to-Cloudflare = no WAF block |
| JS-heavy detail page (Taleo, Workday, PageUp) | `cf_scrape` or `cf_markdown` | Headless browser on Cloudflare edge |
| Multi-page listing crawl (ITU pagination, WHO search) | `cf_crawl` | Async + pagination built in |
| Screenshot/verification need | `cf_screenshot` | Cheaper than running local browser |
| Local dev / testing | Camoufox | No per-call cost, but crashes after ~10 ops |
| Local server-rendered HTML | Scrapling + curl | Zero cost, fastest |

See `references/cf-browser-rendering-examples-2026-06-05.md` for runnable Python scripts, concrete UNDRR/UNESCAP/UNESCWA examples, and a budget calculator.  
See `references/cloudflare-browser-rendering-2026-06-05.md` for the complete Cloudflare Browser Rendering API specification, free-tier budget tables, and anti-patterns.  
See `references/cloudflare-auth-pitfall-2026-06-05.md` for authentication debugging — 32-char hex values are Zone/Account IDs, NOT API tokens (error 6003/6111 diagnostic).

---

## 📸 SCREENSHOT→RAPIDAPI OCR — Fallback for Impossible Portals (2026-06-15)

**When DOM/API scraping fails entirely** (Cloudflare managed JS challenges, broken SPAs, portals that return empty HTML to automation tools), use Camoufox full-page screenshots + RapidAPI OCR as a last-resort extraction method.

**Verified accuracy:** ~97% on job detail pages (single-column layout), ~85% on listing pages (table grid layout). Detail page OCR is good enough to produce usable JD markdown files with only minor post-processing.

### ⚠️ Limitations
- **30 calls/minute hard cap** (RapidAPI FreeOCR.ai rate limit) — do NOT exceed
- **~40s per page** (25s Camoufox JS render + 15s OCR API call) — slow, use only when DOM fails
- **~15MB per image limit** — full-page screenshots at 900KB-1.6MB are fine
- **Listing pages lose ~15% of data** — row misalignment, deadline off by 1-2 days, location swaps
- **Detail pages lose ~3%** — minor typos (e.g. `Tresnjino` → `Tresnjinog`, digit errors in UIDs)
- **No job detail page content from listing screenshots** — only captures what's visible on screen

### When to Use

| Situation | Use This? |
|-----------|-----------|
| Portal returns Cloudflare managed JS challenge (UNDRR, UNESCAP, UNESCWA) | ✅ **Yes** — last resort |
| Portal renders empty HTML to automation tools | ✅ **Yes** |
| DOM scraping works but is slow | ❌ **No** — use DOM, it's faster and more accurate |
| You need full JD text for scoring | ✅ **Yes for detail pages** — ~97% accuracy is sufficient |
| You need listing page data (titles, deadlines) | ⚠️ **Only if DOM fails** — ~85% accuracy means manual verification needed |

### Workflow

```bash
# Step 1: Start Camoufox server (if not running)
camofox server start
sleep 8
camofox --format json open "https://www.google.com"

# Step 2: Navigate to target page and wait for JS render
TAB=$(camofox --format json open "https://target-portal.org/job/..." | python3 -c "import sys,json;print(json.load(sys.stdin)['tabId'])")
sleep 25  # JS render wait

# Step 3: Full-page screenshot
camofox --format json screenshot --path /tmp/job_detail.png --full-page "$TAB"

# Step 4: OCR via RapidAPI
curl --request POST \
  --url https://apis-freeocr-ai.p.rapidapi.com/ocr \
  --header 'x-rapidapi-host: apis-freeocr-ai.p.rapidapi.com' \
  --header 'x-rapidapi-key: 7c96c48e62msh0c4ddb5bb4c4944p13b6c6jsnc957462c41ea' \
  -F "image=@/tmp/job_detail.png" \
  --max-time 90

# Step 5: Save as JD file
curl ... | python3 -c "import sys,json;print(json.load(sys.stdin).get('text',''))" > JD_FILES/UN_AGENCY/Job_Title.md
```

### Key Findings from 2026-06-15 ICRC Test

1. **Detail pages OCR much better than listing pages** — Single-column vertical layout avoids the table-row misalignment that plagues listing page OCR.
2. **Output is clean markdown** — RapidAPI returns `##` headings and `-` bullet lists. Almost directly usable as a JD file.
3. **Cookie banners are captured as noise** — Footer text and cookie consent popups appear in output. Strip them in post-processing.
4. **Rate limit is per-minute, not per-second** — 30 calls/minute means you can fire 30 pages in quick succession, then wait 60s. For a 20-job portal, that's one batch.
5. **Full-page screenshots are ~900KB-1.6MB** — Well under the 15MB API limit. No need to compress further.

### Comparison to Other Methods

| Method | Detail Page Accuracy | Speed | Works on Cloudflare JS Challenge? |
|--------|---------------------|-------|----------------------------------|
| DOM snapshot | 100% | ~5s | ❌ No |
| Camoufox REST API evaluate | 100% | ~25s | ❌ No |
| Cloudflare Browser Rendering | 100% | ~5s | ❌ No (managed challenges) |
| **Screenshot→RapidAPI OCR** | **~97%** | **~40s** | **✅ Yes** |

---

## SCANNING PIPELINE

### Phase 0: Hygiene
1. **BACKUP** tracker and archive files
2. Clean expired vacancies (deadline < today → move to archive)
3. Clean APPLIED: YES entries → archive
4. Verify cross-file overlap is zero
5. Remove duplicate entries (same VID, keep the one with real deadline)
6. Renumber entries sequentially
7. Rebuild SCORING DETAILS block
8. Run post-cleanup verification

**Complete cleanup algorithm with code, verification, and archive-append:**
`references/tracker-cleanup-current-format-v1.md` — replaces the legacy
`duplicate-entry-removal-pattern.md` for the current space-padded tracker
format. Use this for any tracker cleanup operation.

## 🚨 WORKDIR HYGIENE — ORPHAN CLEANUP PROTOCOL 🚨

**When another agent (AGENT/2/3) has been working in this WORKDIR, it may leave orphan files that are not referenced by this skill.** Run this cleanup when the user reports clutter or the WORKDIR root has accumulated scripts, JSON artifacts, tracker debris, or reports not used in the skill's pipeline.

### Diagnostic: What Counts as an Orphan?

| Category | Keep (KEEP) | Move to BACKUP |
|----------|-------------|----------------|
| `UN-VACANCIES-TRACKER.txt` | ✅ Master tracker | ❌ All other `UN-VACANCIES-TRACKER-*` variants |
| `UN-VACANCIES-ARCHIVE.txt` | ✅ Master archive | ❌ Any other archive-like variants |
| `JD_FILES/` | ✅ All agency JDs | ❌ Nothing — entire directory stays |
| `scripts/` | ✅ All scripts (even if not explicitly referenced — they may be called dynamically) | ❌ Nothing — entire directory stays |
| `scan_logs/` | ✅ Per-portal scan logs | ❌ `camoufox_wave.log` (aggregate log, not per-portal) |
| Root `.py` scripts | ✅ Only if referenced in skill (`score_all.py`, `batch_score_all.py`, `batch_score_contextual.py`) | ❌ Unreferenced root scripts (`audit_and_dedup.py`, `orchestrator.py`) |
| `*.json` at root | ✅ Only if referenced in skill (`all_jd_deadlines_broad.json`) | ❌ All other `*.json` (intermediate/deadline/rebuild state) |
| `*.md` at root | ❌ Nothing — reports and plans go to BACKUP | ✅ `FULL_SCAN_REPORT_*.md`, `ORCHESTRATED_SCAN_PLAN_*.md` |
| `STATE/` | ❌ Nothing — state cache is ephemeral | ✅ Entire directory |
| `ROSTER/` | ❌ Not part of this skill | ✅ Entire directory |
| `__pycache__/` | ❌ Can be deleted entirely | ✅ Delete (no backup needed) |
| `BACKUP/` | ✅ Protected — never touch | N/A |

### Cleanup Procedure

1. **Load this skill** (`skill_view(name='un-jobs-search')`) to get the reference list
2. **Full WORKDIR inventory**: `find "$WORKDIR" -maxdepth 5 -not -path '*/BACKUP/*' | sort`
3. **Cross-reference** each file against the skill text using a Python script (search filenames and stems in the SKILL.md content)
4. **Snapshot first** — always backup the entire WORKDIR before moving anything:
   ```bash
   rsync -a --exclude='BACKUP' "$WORKDIR/" "$BACKUP/SNAPSHOT_$(date +%Y%m%d)_CLEANUP/"
   ```
5. **Move orphans** to a dated subdirectory:
   ```bash
   mkdir -p "$BACKUP/ORPHANS_$(date +%Y%m%d)" && mv "$WORKDIR/$file" "$_"
   ```
6. **Remove empty directories** left behind (ROSTER/, STATE/, __pycache__/)
7. **Verify** — root should only show the ~6 essential files: `UN-VACANCIES-TRACKER.txt`, `UN-VACANCIES-ARCHIVE.txt`, `score_all.py`, `batch_score_all.py`, `batch_score_contextual.py`, `all_jd_deadlines_broad.json` plus the `JD_FILES/`, `scripts/`, `scan_logs/`, and `BACKUP/` directories.

### What NOT to Clean
- **NEVER** touch anything in `BACKUP/` — it's the safety net
- **NEVER** delete `JD_FILES/` — they are the scoring corpus
- **NEVER** delete `scripts/` — even unreferenced scripts may be called via CLI by the skill pipeline
- **NEVER** delete per-portal `.log` files in `scan_logs/` — they're referenced in the skill's debugging sections

---

## 🚨 HARD RULE: NEVER WRITE NEW SCRAPER SCRIPTS 🚨

**The user explicitly forbids writing new scraper scripts.** This is a hard rule, not a suggestion.

- Use ONLY the existing scripts in `~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/`
- If an existing script fails or doesn't cover a portal, report the failure — do NOT write a new script
- If you need to scrape a portal that has no working script, use the Camoufox REST API directly via `terminal()` calls (navigate → wait → evaluate → save), NOT by writing a Python file to disk
- The `camoufox_fulljd_scraper_v2.py` and `camoufox_rest_scan.py` scripts already exist for UNICEF/ICRC/WTO — use those
- Writing ad-hoc Python scripts to `/tmp/` or anywhere else for scraping is also forbidden
- Exception: one-liner shell pipelines in `terminal()` are acceptable (e.g., `curl ... | python3 -c "..."`)

**Violation:** Writing a new `.py` file for scraping will result in user frustration. Do not do it.

## 🚨 SOLO AGENT MODE — DEFAULT OPERATING MODE 🚨

**The user prefers direct execution. Do NOT dispatch to subagents or other Hermes profiles unless explicitly told.**

- Run ALL scan scripts directly in the current session via `terminal(background=True, notify_on_complete=True)`
- Launch scripts in parallel batches (10-20 at a time) using background terminal processes
- Do NOT use `delegate_task`, `cmux send`, or the `forward` skill for scan dispatch
- The "PARALLEL SCANNING COORDINATION" and "CMUX MULTI-AGENT DISPATCH" sections below are DEPRECATED for normal operation
- Multi-agent dispatch is ONLY used when the user explicitly requests it (e.g., "dispatch to AGENT")

### 🚨 USER PREFERENCE: QUALITY OVER SPEED (2026-06-09)

The user explicitly stated: **"NO HURRY, NO OPTIMIZATION, NO EFFICIENCY, QUALITY ONLY"**

This means:
- **Do NOT batch-optimize** — run scripts one at a time or in small groups, not 20 at once
- **Do NOT skip portals** — every portal gets its own dedicated run
- **Do NOT rush** — let each script complete fully before moving on
- **Do NOT use shortcuts** — no parallel batching for speed, no token optimization tricks
- **Full JD extraction required** — stubs and short extracts are not acceptable
- **Report every failure** — if a portal fails, say why, don't silently skip
- **Quality means**: complete JDs, proper scoring, verified tracker writes

This overrides any efficiency-oriented patterns in the rest of this skill.)

### 🚨 PITFALL: Speed vs Quality Tension (2026-06-14)

The Camoufox REST API v2 full-JD scraper (`camoufox_fulljd_scraper_v2.py`) is inherently slow — it waits 25s per detail page for JS render on SPA portals (UNICEF PageUp, ICRC Taleo). A 20-job scan can take 10+ minutes. This is by design: the skill mandates full JDs for scoring, and JS-heavy SPAs need the wait time.

**When the user expresses impatience** ("why are you so slow?", "speed this up"):
1. **Acknowledge** the quality-first design — "skill zahteva 25s JS render wait po stranici"
2. **Offer faster alternatives** if the user wants speed:
   - Run multiple API-based portals in parallel (INSPIRA, UNESCO, WHO, UNIDO all use `curl`/`requests` — fast)
   - Skip Camoufox REST for portals that have working `run_*.py` scripts (WHO, UNESCO, INSPIRA, ICRC v2)
   - Group Camoufox-dependent portals (UNICEF, ICRC, WTO) and run them as the last batch
   - If the user says "just scan, no full JD", use the light `camoufox_rest_scan.py` (v1) instead of `camoufox_fulljd_scraper_v2.py`
3. **Never sacrifice quality silently** — if the user wants speed, explicitly tell them what they're trading off (no full JD → no accurate scoring possible)

**The default remains quality-first.** Only switch to speed mode when the user explicitly requests it.

### 🚨 PITFALL: User may complain about speed mid-scan (2026-06-14)

The Camoufox REST API v2 methodical extraction uses 25s JS render waits per page. When scanning UNICEF (PageUp SPA), this means ~25-30s per job listing + detail page. The user may send an OOB message like "why are you so slow?" during the scan.

**Do NOT interpret this as a directive to abandon quality.** The 25s wait is necessary for PageUp/Taleo SPAs to fully render — shorter waits produce truncated JDs that fail the FULL-JD RULE. The user's frustration is with the inherent slowness of JS-heavy portals, not with the quality mandate.

**Response pattern:** Acknowledge the frustration, explain the technical reason (25s JS render wait per page is required for full content), and continue. Do NOT switch to faster-but-incomplete extraction methods.

**Exception:** When the user explicitly says "scan only, no scoring" (scan-only mode), listing-page extraction can use 15s waits since full JDs aren't needed. But for full scoring pipelines, 25s remains mandatory.

### Parallel Execution Pattern (SOLO Mode)

```python
# Launch scripts in parallel batches via terminal(background=True)
# Group 1: API-based and fast scripts
terminal(background=True, command="uv run python3 run_inspira_v4.py", notify_on_complete=True, timeout=120)
terminal(background=True, command="uv run python3 run_undp_v4.py", notify_on_complete=True, timeout=120)
# ... up to 10-20 parallel processes

# Group 2: Camoufox-dependent scripts (after Group 1 finishes)
terminal(background=True, command="uv run python3 run_who.py", notify_on_complete=True, timeout=180)
# ...

# Group 3: Camoufox REST API for UNICEF/ICRC/WTO (requires server restart between portals)
# Write a standalone REST script, run via terminal()
```

**Key rules:**
- Always use `notify_on_complete=True` for background processes
- Wait for all processes in a batch before starting the next
- If a script fails, log the error and continue with the next
- Budget ~20 parallel processes maximum (system resource limit)

---

## 🚨 PARALLEL SCANNING COORDINATION — DEPRECATED (Multi-Agent) 🚨

**⚠️ DEPRECATED: Use SOLO AGENT MODE above unless user explicitly requests multi-agent dispatch.**

When dispatching scan tasks to helper agents (AGENT, AGENT), you MUST:

1. **Partition portals exclusively** — Each portal goes to exactly ONE agent. Never assign the same portal to multiple agents.
2. **Verify the partition before dispatching** — Write down which agent gets which portals. Check for overlap.
3. **Scripts write to the same JD_FILES directory** — If two agents run the same script, they will overwrite each other's files or create race conditions.
4. **Do NOT let helpers self-assign** — If a helper says it "completed the whole batch," it may have scanned portals that were also scanned by AGENT, causing duplicate work.

**Correct partitioning example:**
- AGENT (direct): INSPIRA, UNICEF, WHO, UNDP, UNFPA
- AGENT: UNESCO, UNITAR, UNOPS, World Bank, OECD, ICAO, WMO
- AGENT: ITU, IAEA, ILO, FAO, ICRC, ICMPD, UNU, UNIDO, ECB, WFP/WTO (Workday)

**🚨 If helpers receive tasks via `cmux send`, the `[FORWARDED]` prefix is interpreted as a cmux command and the task text is NEVER received by the helper's shell.** Use plain text without bracketed prefixes. See the `forward` skill for details.

### Phase A: Fetch Listing Pages
For each portal in the registry:
1. Run the appropriate platform-specific script or browser technique
2. Extract job links and titles
3. Apply hard pre-filters (Ukraine, nationals-only, interns, juniors, volunteers)

### Phase B: Fetch Full JD Pages
For each pre-filtered job:
1. Navigate to detail page
2. Extract full JD text (article.innerText / body.innerText)
3. Save as `{AGENCY}_{jobID}_{sanitized_title}.md` in `JD_FILES/{AGENCY}/`
4. Apply body full-text ICT keyword check

### Phase C: Score ONE by ONE
For each saved JD file:
1. Load CV Repository + Scoring Engine
2. Score with full 7-parameter manual evaluation
3. Write single row to UN-VACANCIES-TRACKER.txt (full rebuild)
4. Rebuild summary table, re-sort by deadline

---

## TRACKER PARSING — Reliable Row Extraction

The tracker uses **space-padded fixed-width columns** (not pipe-delimited). To parse data rows:

```python
import re
from datetime import date, datetime

today = date.today()

with open('UN-VACANCIES-TRACKER.txt') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    stripped = line.rstrip()
    
    # Data rows: row number is in chars [0:5], left-aligned
    num_part = stripped[:5].strip()
    if not num_part.isdigit():
        continue
    row_num = int(num_part)
    
    # Vacancy ID: second-to-last token before NO/YES
    end_match = re.search(r'(\S+)\s+(NO|YES)\s*$', stripped)
    vid = end_match.group(1) if end_match else None
    
    # Deadline: first YYYY-MM-DD pattern in the line
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', stripped)
    dl = datetime.strptime(date_match.group(1), '%Y-%m-%d').date() if date_match else None
    
    is_tbd = 'TBD' in stripped or 'Open (Roster)' in stripped
```

**Key pitfall:** Do NOT use `re.split(r'\s{2,}', ...)` to parse columns — the title and deadline are merged into one token because the deadline is embedded at the end of the title string with no clear separator. Use regex patterns on the full line instead.

---

## Scan-Only Mode (AGENT Pattern)

**Trigger:** User issues a "AGENT — STRICT SCRAPING ASSIGNMENT" with a numbered agency list, explicit prohibitions, and a specific output marker string.

This is a separate operating mode from the full scan-score-tracker pipeline. Run stripped-down: execute scripts only, report raw findings, never touch scoring or tracker files.

### Protocol
1. Scripts are at `~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/`
2. Execute each with `uv run python3 run_{portal}.py` — one at a time, in exact order
3. If a site fails, write `PORTAL_ERROR: [Name] — [Reason]` and immediately move to the next
4. **CRITICAL PROHIBITIONS:**
   - Do NOT write to or modify UN-VACANCIES-TRACKER.txt
   - Do NOT evaluate or score the jobs
   - Do NOT skip any script
5. Print a plain list of new Vacancy IDs scraped
6. End output with the exact marker string: `AGENT_SCAN_COMPLETE`

### Output format
```
PORTAL_ERROR: ICRC — Playwright Node v24 crash
OECD: 4 ICT jobs found, 0 new
...
New Vacancy IDs:
[NONE]
AGENT_SCAN_COMPLETE
```

### When to use this vs the full pipeline
- **Scan-only mode** (this section): When the user explicitly labels it "AGENT — STRICT SCRAPING ASSIGNMENT" or says "scan only, no scoring"
- **Full pipeline** (rest of this skill): Any other scan request, or when user asks to "update tracker" or "score the jobs"

The mode is distinguished by the instruction format — numbered agency list + explicit prohibitions about not writing to the tracker, not scoring, and not skipping any script.

---

## CMUX MULTI-AGENT DISPATCH — Session Verification Required

**Always verify workspace UUIDs before dispatching.** UUIDs change between cmux restarts.

```bash
# Step 1: Discover current UUIDs
cmux tree --all --id-format uuids

# Step 2: Send task to target window UUID
cmux send --window <TARGET_WINDOW_UUID> "YOUR TASK TEXT HERE"

# Step 3: Trigger execution (MANDATORY — without this, text sits in buffer)
cmux send-key --window <TARGET_WINDOW_UUID> Enter
```

**Critical rules:**
- Use `--window <UUID>` not `--workspace <index>` — named indices frequently fail
- ALWAYS follow `cmux send` with `cmux send-key ... Enter` — text won't execute otherwise
- NEVER use `[FORWARDED]` prefix — cmux interprets `[` as a command, not shell input
- Partition portals exclusively between agents — same portal to two agents = race condition on JD_FILES/

---

## EXCLUSION RULES (Apply BEFORE Scoring)

| Filter | Match Criteria | Action |
|--------|---------------|--------|
| **Nationals-only** | "nationals only", "national position" | EXCLUDE |
| **Local Recruitment** | World Bank "Local Recruitment" | EXCLUDE |
| **Ukraine** | Location contains "Ukraine" | EXCLUDE |
| **Internships** | "Intern" or "Internship" in contract/title | EXCLUDE |
| **Traineeships** | "Traineeship" or "PhD Traineeship" | EXCLUDE |
| **Volunteers** | "Volunteer" in title or contract | EXCLUDE |
| **Junior** | Grade contains "Junior", "L1-Junior" | EXCLUDE |

**Exception:** Serbia duty station = PASS. EU/Schengen = PASS (EU citizenship).

---

## CONTEXTUAL PRE-FILTER (v2.0) — Scrape FIRST, Disqualify LATER

**The pre-filter is now CONTEXTUAL, not just ICT.** The goal is to capture any role
where User could contextually fit, even if the title doesn't contain ICT keywords.
Better to scrape something useless and disqualify it later in scoring, than to
miss something important on initial screening.

### How it works

All per-agency scraper scripts import `broad_scan_keywords.py` and call:
- `is_broad_relevant_title(title)` — checks title against 200+ contextual keywords
- `is_broad_relevant_full(title, body)` — checks title + first 1500 chars of body

### 10 Career Contexts Covered

| # | Context | Example Keywords |
|---|---------|-----------------|
| 1 | ICT / Tech core | it, ict, ai, digital, software, data, cybersecurity, cloud |
| 2 | Telecom / Infrastructure | telecom, connectivity, broadband, fibre, satellite, 5G, ISP, MVNO |
| 3 | AI / ML / Agentic | llm, agentic, mcp, automation, robotics, humanoid, deep learning |
| 4 | Education / EdTech | education, school, learning, edtech, LMS, Moodle, Canvas, GIGA |
| 5 | UN / International Dev | unicef, undp, who, world bank, sdg, humanitarian, multilateral |
| 6 | Government / Public Sector | government, ministry, e-government, public procurement, DPI |
| 7 | Healthcare / HealthTech | health, medical, hospital, digital health, telemedicine |
| 8 | Finance / FinTech | finance, fintech, payment, banking, financial inclusion |
| 9 | Enterprise IT | enterprise, SAP, ERP, IT infrastructure, data center, VMware |
| 10 | Transit / Smart City | transit, transport, ticketing, fare collection, smart city |

### Hard-Reject (still applied at pre-filter level)

Use `\b` word boundaries. Hard-reject: `\bintern\b`, `\bstagiaire\b`, `\bvolunteer\b`,
`\bunpaid\b`, `\bnutrition\b`, `\bagricultur\b`, `\bmedical\b`, `\bdoctor\b`,
`\bnurse\b`, `\bteacher\b`, `\bhr\b`, `\blogistics\b`, `\bsupply chain\b`.

### Keyword file

`scripts/broad_scan_keywords.py` — 200+ title keywords, 100+ body keywords.
Updated to v2.0 (2026-06-09) with full contextual coverage.

**Design rationale:** `references/contextual-pre-filter-design-2026-06-09.md` — explains the 10 career contexts, keyword design principles, and the "scrape first, disqualify later" philosophy.

---

## SCRIPTS

**🚨 CRITICAL: Scripts are in TWO different locations:**

1. **Per-agency scraper scripts** (for scanning portals) are in:
   `~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/`
   Run with: `uv run python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_{portal}.py`

2. **Batch scoring/rebuild scripts** are in the WORKDIR:
   `~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/`
   These include: `batch_score_all.py`, `prefilter_and_classify.py`, `rebuild_complete.py`, `calibrate_scores.py`, etc.

**Do NOT confuse these two directories.** The WORKDIR `scripts/` does NOT contain per-agency scrapers.

Located in `scripts/` directory of this skill. Per-agency scrapers:

**Run with: `uv run python3 run_{portal}.py`** (all portals including WHO — as of 2026-06-04)

> **⚠️ WHO script fix (2026-06-04):** `run_who.py` previously used plain `python3` which hit system Python 3.13 with a cffi architecture mismatch (`_cffi_backend.cpython-313-darwin.so arm64 vs x86_64`). Switching to `uv run python3` (which uses the venv) fixes this. The shebang `#!/usr/bin/env python3` in the script is harmless — `uv run` overrides it.

### New-jobs-search scrapers (25 scripts):
run_unicef.py, run_itu_v4.py, run_unesco_v4.py, run_unitar_v4.py,
run_unops_v3.py, run_who.py, run_iaea.py, run_fao.py, run_icrc_v2.py,
run_icmpd_v3.py, run_ilo_v3.py, run_inspira_v4.py, run_workday.py,
run_wmo.py, run_undp_v4.py, run_unfpa_v4.py, run_ecb.py, run_oecd_v4.py,
run_worldbank.py, run_icao_v3.py, run_unu.py, run_ifad.py, run_imo.py,
run_unhcr.py, run_wipo.py, run_unido.py

### Camoufox REST API scrapers (2 scripts, added 2026-06-06):
camoufox_rest_scan.py — First-pass Camoufox REST scraper for UNICEF + ICRC + **WTO** (basic v1 — covers all 3)
camoufox_fulljd_scraper_v2.py — Full-JD methodical one-by-one extractor for **UNICEF + ICRC only** (quality v2 — does NOT cover WTO)
  - Usage: `uv run python3 camoufox_fulljd_scraper_v2.py`
  - Extracts 8-17KB full JD content per job with 25s JS render waits
  - Filters non-ICT and disqualified jobs automatically
  - Saves with metadata headers (grade, location, deadline, URL)
  - File naming: `UN_ICRC_` / `UN_UNICEF_` prefix (rename to `ICRC_` / `UNICEF_` after)
  - Requires Camoufox server running on port 9377
  - **Coverage gap (patched 2026-06-07):** v2 only handles ICRC + UNICEF. For WTO scraping, fall back to `camoufox_rest_scan.py` (v1) which still has the `scrape_wto()` function and Workday parsing. Do NOT assume v2 covers WTO from its docstring header — it doesn't.

References:
- `references/linkedin-job-scraping-2026-06.md` — LinkedIn job scraping research: tool comparison (`linkedin-jobs-scraper`, Apify, RSS endpoint), query templates for User's target roles, anti-detection notes, and integration with UN-JOBS-SEARCH scoring pipeline.\n- `references/tracker-append-vs-rebuild-2026-06-12.md` — Safe tracker rebuild pattern that appends to existing rows instead of full reconstruction (avoids data loss from missing org/title fields).
- `references/tracker-cleanup-current-format-v1.md` — Complete cleanup algorithm with code, verification, and archive-append
- `references/shell-token-escape-redaction-2026-06-07.md` — How to work around bash mangling literal redaction tokens (`***`) when sourcing secrets in `terminal()` calls — use a wrapper script or Python with `os.environ` instead of inline `export KEY=*** $(cmd)`.

### Minimaltoken utilities (LEGACY — DO NOT USE):
web-preclean.py, merge-vacancies.py, bulk-add-vacancy-ids.py,
audit-and-verify.py, update-internal-ids.py
**WARNING: These are legacy minimaltoken tools. Do NOT use them in this skill. Use the per-agency `run_{portal}.py` scripts instead.**

### Batch scoring scripts (2 scripts, added 2026-06-03):
prefilter_and_classify.py  — Categorise all JD files into SCOREABLE/DISQUALIFIED
batch_score_all.py          — 7-parameter batch scoring + tracker rebuild

### Deadline extraction + rebuild templates (added 2026-06-09):
`templates/extract_jd_deadlines.py` — Body-text regex extractor (25+ patterns), runs against `JD_FILES/**/*.md`
`templates/rebuild_tracker_by_deadline.py` — Section-based tracker rebuild (Open/Expired/Rolling/Roster)

### Calibration helper (1 script, added 2026-06-03):
rebuild_complete.py        — Structured-dict tracker rebuild with manual overrides baked in

### Scoring Engine Architecture (UPDATED 2026-06-09 — v2.1.0)

**The authoritative scoring engine is now the `vacancy-compatibility-scoring-engine` skill (v5.0).**
Load it with `skill_view(name='vacancy-compatibility-scoring-engine')` before any scoring session.
It contains the full 7-parameter methodology, domain caps, calibration anchors, and current-work overrides.

The system has **three scoring scripts. Do NOT confuse them:**

| Script | Location | Type | Scores | Role |
|--------|----------|------|--------|------|
| `batch_score_all.py` | `~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/` | Batch keyword-based | Raw keyword counts, uncapped | Provisional only |
| `score_all.py` | `WORKDIR/` (`WORKDIR/`) | Domain-capped + manual calibration | Honest caps per domain | Authoritative (legacy) |
| `batch_score_contextual.py` | `WORKDIR/` (`WORKDIR/`) | Contextual P1-P7 + P8 (0-20) | Domain-capped + context match | Experimental — P8 adds context bonus |

**Critical rules:**
- `batch_score_all.py` **overwrites** the tracker with raw keyword scores. After running, restore from backup. Never use raw batch scores for the live tracker without manual calibration.
- `score_all.py` is the **legacy authoritative** scorer. It was built during the 2026-06-09 session to implement domain-capped P1 with director double-cap. It is NOT pre-installed — it lives in the WORKDIR and edits accumulate over sessions.
- `batch_score_contextual.py` adds **P8 Contextual Compatibility** (0-20 pts) on top of P1-P7. It evaluates whether the job's SECTOR, FUNCTION, and ENVIRONMENT overlap with User's 9 proven career contexts (education_edtech, telecom_connectivity, ai_ml_agentic, government_public_sector, un_international_dev, healthcare_healthtech, africa_emerging_markets, finance_fintech, enterprise_it, payment_transit). Max total is still 100 (P1-P7 capped at 80, P8 adds up to 20).
- **Before ANY edit to any scoring script, backup first:** `cp score_all.py BACKUP/score_all_$(date +%Y%m%d_%H%M).py`
- The `vacancy-compatibility-scoring-engine` skill is the **authoritative methodology** (SKILL.md + references + calibration anchors). Load it before every scoring session.

**🆕 score_all.py overwritten without backup (2026-06-09):** During a session of penalty tuning, domain cap fixes, and date parser patches, `score_all.py` was overwritten 3+ times with no versioned backup. The original v1 scoring logic is **permanently lost**. The only remaining trace is the backup tracker file `BACKUP/UN-VACANCIES-TRACKER_VALID_20260609_1536.txt`. **Rule: Before ANY edit to the scoring engine, run `cp score_all.py BACKUP/score_all_$(date +%Y%m%d_%H%M).py`.**

---

## KEY TECHNIQUES

### INSPIRA API (no browser needed)
```
POST https://careers.un.org/api/public/opening/jo/list/filteredV2/en
```
JSON body returns full jobDescription HTML + metadata. No auth, no Cloudflare.

**macOS SSL fix:** The careers.un.org API SSL cert fails verification on macOS 26. Add this at the top of the script:
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```
Patched into `run_inspira_v4.py` 2026-06-03 to fix SSLCertVerificationError.

### Camoufox REST API for JS-rendered SPAs (UNICEF, ICRC, WTO, WHO)
```python
# Preferred method: Python urllib → Camoufox REST API
# Server: /usr/local/bin/camofox server start (port 9377)
# See references/camoufox-rest-api-complete-reference-2026-06-04.md

import json, urllib.request, urllib.error, time

def api(method, path, data=None):
    url = f"http://localhost:9377{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body,
          headers={"Content-Type": "application/json"}, method=method)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

# Create tab
t = api("POST", "/tabs", {"userId": "hermes", "sessionKey": "s1", "url": "https://example.com"})
tid = t["tabId"]
time.sleep(20)  # Wait for browser to connect

# Navigate
api("POST", f"/tabs/{tid}/navigate", {"url": "https://jobs.unicef.org/en-us/list", "userId": "hermes"})
time.sleep(25)  # Wait for JS render (critical for PageUp/Taleo SPAs)

# Extract content
text = api("POST", f"/tabs/{tid}/evaluate", {"expression": "document.body.innerText", "userId": "hermes"})
html = api("POST", f"/tabs/{tid}/evaluate", {"expression": "document.documentElement.outerHTML", "userId": "hermes"})

# Close tab
api("DELETE", f"/tabs/{tid}")
```

**Key rules:**
- `navigate` → `userId` in JSON body (NOT query param)
- `evaluate` → `expression` parameter (NOT `script`), `userId` in body
- `snapshot` → `userId` as query param (returns accessibility tree, NOT raw HTML)
- `/text` endpoint does NOT exist
- **Wait 25s after navigation** for JS-heavy SPAs (PageUp, Taleo) to fully render
- Use `document.body.innerText` for text extraction (better than `outerHTML` for SPAs)
- Server starts with `browserConnected: false` — NORMAL, creates tab to connect
- Server crashes after ~10-15 tab operations — restart between portals
- **CRITICAL:** `execute_code()` sandbox blocks localhost HTTP — run via `terminal()` only

### Camoufox Python context manager (alternative)
```python
with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state("networkidle", timeout=25000)
    text = page.inner_text("body")
```
Requires venv Python and server.py null proxy patch.

### Scrapling response.body for search pages
`response.body` contains raw HTML, `.text` is None for JS pages.
Strip `<script>`/`<style>` tags with regex.

### Universal JS extract (any portal)
```javascript
(function(){
  const a = document.querySelector('article');
  return a ? a.innerText : document.body.innerText;
})()
```

### WHO EPIPE prevention
Long-running Playwright Chrome processes die after ~5 pages (EPIPE crash).

---

## Token Optimization Rules (for scanning, NOT scoring)

**NOTE: These rules are from the legacy minimaltoken merge. The per-agency `run_{portal}.py` scripts already handle site detection, rendering, and extraction internally. Do NOT use web-preclean.py — it is a minimaltoken tool. If a per-agency script fails, report and skip — do NOT fall back to web-preclean.py.**

**Rule 1 — Site type detection:** Handled by per-agency scripts internally. OPEN (200) → script uses requests | WAF (403) → script uses Camoufox | JS → script uses Camoufox | API → script uses urllib
**Rule 2 — Scripts handle extraction:** The per-agency scripts produce clean JD markdown files in JD_FILES/{AGENCY}/. No pre-cleaning needed.
**Rule 3 — API-first:** INSPIRA has a direct JSON API (used by run_inspira_v4.py). Other portals use per-agency scripts.
**Rule 4 — Targeted extraction:** Scripts extract title/deadline/grade/location automatically into JD file metadata headers.
**Rule 5 — Hard token limits:** Quick=2000, Single=6000, Search=8000, Deep=15000 (for execute_code inline analysis only, NOT for scraper scripts)
**Rule 5b — Portal selection:** Follow the Daily Scan Queue in the Deepseek section above. Skip low-yield portals listed there.
**Rule 6 — One-shot writes.** Build tracker in memory, write once, verify once.
**Rule 7 — Escalation:** Script fails → report SKIPPED, don't retry.
**Rule 8 — Expired cleanup every scan.**

## Deadline Extraction Protocol (v3 — Body-Text Regex + Rolling/Roster Classification)
### Mapping Extracted Deadlines to Tracker

```python
import re, os
from pathlib import Path
from datetime import datetime

JD_ROOT = Path("JD_FILES")
all_patterns = [
    # **Deadline:** 31 December 2026  ← colon inside bold markers
    r'\*\*Deadline[:\s]*\*\*[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
    # **Closing Date** Dec 31, 2026
    r'\*\*Closing Date[:\s]*\*\*[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
    # Deadline: 2026-12-31
    r'(?i)deadline[:\s]+(\d{4}-\d{2}-\d{2})',
    # Short month forms
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Jan\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Feb\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Mar\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Apr\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+May\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Jun\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Jul\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Aug\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Sep\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Oct\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Nov\w*\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+Dec\w*\s+\d{4})',
    # Full month names (both orders)
    r'(?i)(?:deadline|closing)[:\s]+(\d{1,2}\s+January\s+\d{4})',
    r'(?i)(?:deadline|closing)[:\s]+(January\s+\d{1,2},?\s+\d{4})',
    # ... repeat for all 12 months
]

def parse_date(ds):
    ds = ds.strip().replace(',', '')
    for fmt in ['%d %B %Y', '%d %b %Y', '%B %d %Y', '%b %d %Y', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(ds, fmt)
            if 2025 <= dt.year <= 2028:
                return dt.strftime('%Y-%m-%d')
        except: pass
    return None

def extract_all_deadlines(jd_root):
    deadlines = {}
    for fpath in jd_root.rglob("*.md"):
        text = fpath.read_text(errors='ignore')
        for pat in all_patterns:
            m = re.search(pat, text)
            if m:
                parsed = parse_date(m.group(1))
                if parsed:
                    deadlines[str(fpath)] = parsed
                    break
    return deadlines
```

**Full reference with results and edge cases:** `references/jd-body-text-deadline-extraction-2026-06-09.md`
## Deadline Extraction Protocol (v4 — Body-Text First, Fixed-Position Tracker Rebuild)

**CRITICAL LESSON (2026-06-09):** Most JD files have zero structured frontmatter. Deadlines are embedded in body text as `**Deadline:** 31 December 2026` or `Application deadline (Midnight Geneva Time): 22 June 2026`. A comprehensive regex sweep across ALL `JD_FILES/**/*.md` is **REQUIRED** before any portal-specific metadata extraction.

### Step 1: Body-Text Extraction (Primary)

Run a single Python script that walks ALL `*.md` files under `JD_FILES/` recursively:

```python
import re
from pathlib import Path
from datetime import datetime

JD_ROOT = Path("JD_FILES")
all_patterns = [
    # **Deadline:** 2026-06-22  (ISO inside bold)
    r'\*\*Deadline[:\s]*\*\*[:\s]+(\d{4}-\d{2}-\d{2})',
    # **Deadline:** 31 December 2026
    r'\*\*Deadline[:\s]*\*\*[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
    # Application deadline (Midnight Geneva Time): 22 June 2026
    r'Application deadline[^:]*:[^\n]*?(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
    # Closing Date: January 15, 2026
    r'Closing Date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
    # Deadline for applications: 15 January 2026
    r'Deadline for applications[^:]*:[^\n]*?(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
    # Apply before: 31 December 2026
    r'Apply before[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
]

def parse_date(ds):
    for fmt in ['%d %B %Y', '%d %b %Y', '%B %d, %Y', '%B %d %Y', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(ds.strip().replace(',', ''), fmt)
            if 2025 <= dt.year <= 2028:
                return dt.strftime('%Y-%m-%d')
        except:
            pass
    return None

deadlines = {}  # fpath -> "2026-06-22"
for fpath in JD_ROOT.rglob("*.md"):
    text = fpath.read_text(errors='ignore')
    for pat in all_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            dl = parse_date(m.group(1))
            if dl:
                deadlines[str(fpath.relative_to(JD_ROOT.parent))] = dl
                break
```

**Expect ~99-120 matches out of 382 files** using body-text extraction alone.

### Step 2: "Not Specified" Detection (WITH WORD BOUNDARIES)

After extracting dates, detect files that genuinely have no deadline using a **strict regex with word boundaries** to avoid false positives on words like "**opening**".

```python
# WRONG — false-positives on "opening", "open-ended program"
re.search(r'(?i)(?:deadline|closing)[:\s]*(?:not specified|rolling|open)', text)

# CORRECT — only matches explicit fields
re.search(r'(?i)(?:\*\*Deadline[:\s]*\*\*|\bClosing Date\b)[:\s]+(?:Not specified|Rolling|Open-ended)', text)
```

**Verified false-positive (2026-06-09):** The ITU AI file (`ITU_1354554355_Home_Based_AI_and_Digital_Transformation_Consultant_Pakistan.md`) has "**Deadline:** 2026-06-22" but a naive "open" check matched the word "opening" elsewhere in the text and marked it Rolling.

### Step 3: Portal-Specific Metadata (Fallback)

For TBD entries with real VIDs (rare — most VIDs are "**"), scrape the online portal:

| Portal | URL Pattern | Status |
|--------|-------------|--------|
| WHO | `careers.who.int/careersection/ex/jobdetail.ftl?job=` | ✅ Working via Camoufox |
| World Bank | `wb-1.wd103.myworkdayjobs.com/en-US/External/job/` | ⚠️ Workday maintenance periods |
| WFP | `career5.successfactors.eu/...` | ⚠️ SuccessFactors |

### Step 4: Classification

| Category | Detection | Tracker Value |
|----------|-----------|---------------|
| **Active** | Real date extracted, not expired | `2026-06-22` |
| **Expired** | Real date < today | `2026-06-01` |
| **Rolling** | Explicit "Not Specified" / "Rolling" in JD, OR no date found with word-boundary regex | `Rolling` |
| **Roster** | Title OR filename contains "Roster", "Expression of Interest", "LTA", "Long Term Agreement" | `Rolling` |

### Step 5: Tracker Rebuild

**Use fixed-position parsing** on the original tracker (NOT regex splitting by whitespace):

```python
def parse_tracker_row(line):
    """Parses standard V4 tracker format."""
    l = line.rstrip('\n')
    if len(l) < 128 or not l[0].isdigit():
        return None  # Header/separator
    num   = int(l[0:5].strip())
    org   = l[5:26].strip()
    title = l[26:71].rstrip('…').strip()
    dl    = l[71:87].strip()
    mark  = re.search(r'[🔴🟠🟡🟢]', l[82:95])
    mark  = mark.group(0) if mark else "⚪"
    sc    = int(re.search(r'[🔴🟠🟡🟢]\s+(\d+)', l).group(1))
    tail  = l[95:].strip().split()
    applied = tail[-1] if tail[-1] in ("NO", "YES") else "NO"
    vid   = tail[-2] if len(tail) > 1 else "**"
    return {"num": num, "org": org, "title": title, "dl": dl,
            "mark": mark, "score": sc, "vid": vid, "applied": applied}
```

**Sort ALL entries by `(deadline_ordinal, -score)`:**

```python
TODAY = datetime.now()

def sort_key(e):
    dl = e["dl"]
    is_rost = any(k in e["title"].upper() for k in ["ROSTER", "EXPRESSION OF INTEREST", "LTA ", "LONG TERM"])
    if is_rost:
        return (3, datetime.max, -e["score"])  # Roster always at very bottom
    if dl == "TBD" or dl == "Rolling":
        return (2, datetime.max, -e["score"])  # Rolling after expired
    try:
        dt = datetime.strptime(dl, "%Y-%m-%d")
        if dt < TODAY:
            return (1, datetime.max, -e["score"])  # Expired after active
        return (0, dt, -e["score"])                # Active by deadline
    except:
        return (2, datetime.max, -e["score"])

entries.sort(key=sort_key)
```

**Write complete tracker as single `Path.write_text()` call.**

#### 4-Section Header Format
```
╔════════════════════════════════════════════════════════════════════╗
║  🟢 OPEN APPLICATIONS — Sorted by Deadline (Earliest First)       ║
╚════════════════════════════════════════════════════════════════════╝
╔════════════════════════════════════════════════════════════════════╗
║  🔴 EXPIRED — Deadline Passed (reference only)                    ║
╚════════════════════════════════════════════════════════════════════╝
╔════════════════════════════════════════════════════════════════════╗
║  🟡 ROLLING — No fixed deadline (check periodically)              ║
╚════════════════════════════════════════════════════════════════════╝
╔════════════════════════════════════════════════════════════════════╗
║  🔵 ROSTER / EXPRESSION OF INTEREST — Pool registration           ║
╚════════════════════════════════════════════════════════════════════╝
```

#### Result Reference
| Rebuild Date | Method | Open | Expired | Rolling | Roster | Notes |
|-------------|--------|------|---------|---------|--------|-------|
| 2026-06-09 v7.2 | Body-text + fixed-pos | 39 | 5 | 236 | 20 | 56 TBD entries matched to JD files, 20 roster corrected |

---

## 🚨 TRACKER REBUILD PROTOCOL — CRITICAL RULES

1. **BACKUP first** — `cp UN-VACANCIES-TRACKER.txt BACKUP/...`
2. **Parse with FIXED POSITIONS** — chars [0:5] row, [5:26] org, [26:71] title, [71:87] deadline, [87:97] score, [97:126] vid, [126:] applied
3. **Body-text extract from ALL JD files** — 25+ regex patterns across `JD_FILES/**/*.md`
4. **Word-boundary check for "Not Specified"** — avoid false-positives on "opening"
5. **Match TBD entries to dated JD files** via Jaccard word-overlap (since VIDs are "**")
6. **Classify**: Active → Expired → Rolling → Roster
7. **Sort by `(deadline_ordinal, -score)`**
8. **Write complete file as single `Path.write_text()`**
9. **Verify**: line count ≈ N + 12, every section exists, sort is correct

### When to Rebuild
- After batch JD extraction ≥20 new files
- After scoring pass changes ordering
- Weekly hygiene check
- When user explicitly says "rebuild the tracker"
- NEVER as replacement for daily cleanup — use archive procedure for that
- **Real date** (`YYYY-MM-DD`) — confirmed from JD body-text extraction or portal metadata
- **Rolling** — JD body-text contains "Not Specified", "open-ended", "rolling recruitment", OR the portal has no fixed application window. NOT the default — requires explicit evidence.
- **Roster** — Title or filename contains `Roster`, `Expression of Interest`, `LTA`, `Long Term Agreement`. These go in a separate section entirely.
- **TBD as last resort** — Only when no evidence exists in JD files AND no real VID allows online scraping.

#### Sort Key
```python
def sort_key(e):
    has_date, dt = is_date(e["deadline"])
    if has_date:
        if dt < TODAY:
            return (1, datetime.max, -e["score"])  # Expired
        return (0, dt, -e["score"])               # Active, earliest first
    if is_roster(e):
        return (3, datetime.max, -e["score"])     # Roster at very bottom
    return (2, datetime.max, -e["score"])           # Rolling in middle
```

#### Pitfall: `has_no_dl` False Positive (`"opening" as "open"`)
The naive regex `(?i)(?:deadline|closing date)[:\s]*(?:not specified|...|open)` MATCHES the word "**opening**" inside phrases like "job opening" or "Career Opportunities opening". This false-positived on ~50 high-score entries (e.g. ITU AI 82 → Rolling incorrectly).

**Fix** — Use a **word boundary and case-sensitive field regex** instead of a wide catch-all:

```python
# WRONG — matches "opening"
has_no_dl = re.search(r'(?i)(?:deadline|closing)[:\s]*(?:not|rolling|open)', text)

# CORRECT — only matches fields, not embedded words
has_no_dl = re.search(
    r'(?i)(?:\bdeadline\b|\bclosing date\b)[:\s]+(?:not specified|not yet|not available|rolling|open[-\s]ended)',
    text
)
```

Even better: extract ALL dates first. If a file contains a concrete date that is within 90 days of today's scan date, treat it as the real deadline. Only mark as Rolling when a date search returns NO dates within a plausible window AND the explicit "not specified" wording is present.

#### Rebuild Steps
1. **BACKUP** the original tracker via `cp` into `BACKUP/`
2. **Parse original** with fixed-position parsing (NOT regex splitting by whitespace):
```python
org      = l[5:26].strip()
title    = l[26:71].rstrip('…').strip()
dl       = l[71:83].strip()
mark     = re.search(r'[🔴🟠🟡🟢]', l[82:95]).group(0)
score    = int(re.search(r'[🔴🟠🟡🟢]\s+(\d+)', l).group(1))
tail     = l[95:].strip().split()
applied  = tail[-1] if tail[-1] in ("NO","YES") else "NO"
vid      = tail[-2] if len(tail) > 1 else "**"
```
3. **Extract dates from ALL JD files** recursively across `JD_FILES/**/*.md`
4. **Match TBD tracker entries** to dated JD files using Jaccard word-overlap on lowercase 4+ char words
5. **Apply Rolling/Roster classification**
6. **Sort by `(deadline_ordinal, -score)`**
7. **Write complete new tracker** as a single `Path.write_text()` call
8. **Verify**: check line count ≈ N + 12, each section exists, sort is correct

#### 4-Section Format
```
╔════════════════════════════════════════════════════════════════════╗
║  🟢 OPEN APPLICATIONS — Sorted by Deadline (Earliest First)       ║
╚════════════════════════════════════════════════════════════════════╝
#  Org                  Title                          Deadline  Mark …
─── ─────────────────── ─────────────────────────────  ────────── ── …

╔════════════════════════════════════════════════════════════════════╗
║  🔴 EXPIRED (Deadline Passed — for reference only)                  ║
╚════════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════════╗
║  🟡 ROLLING (No fixed deadline — check periodically)               ║
╚════════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════════╗
║  🔵 ROSTER / EXPRESSION OF INTEREST (No deadline — pool registration) ║
╚════════════════════════════════════════════════════════════════════╝
```

#### Stats Line
```
Total: N | Open: X | Expired: Y | Rolling: Z | Roster: W
```

#### Result Reference
The v7.1 rebuild (2026-06-09) on 300 entries produced:
- **Open: 135** | Expired: 39 | Rolling: 106 | Roster: 20
- **213 new dates** extracted and matched from `JD_FILES/` body text

#### When to Rebuild
- After any batch JD extraction that adds ≥20 new files
- After scoring pass that changes entry ordering
- Weekly as a hygiene check (expired entries should move to Expired section but stay in tracker)
- NEVER as a replacement for daily cleanup of applied/archived entries — use the archive procedure for that

---

## DEDUP PROTOCOL

1. Extract unique job IDs from filenames in JD_FILES/
2. For duplicate IDs, keep the file with the longest content
3. Remove shorter duplicates
4. Before adding ANY entry to tracker, check Vacancy ID against BOTH:
   - UN-VACANCIES-TRACKER.txt
   - UN-VACANCIES-ARCHIVE.txt
   Do NOT check legacy UN_SECTOR_VACCANCIES.txt — it is a minimaltoken file outside the workdir.
5. Same `(title.lower(), organization.lower())` tuple also counts as duplicate

---

**Camoufox Maintenance**

### Server Lifecycle
```bash
# Kill everything
kill -9 $(lsof -ti :9377) 2>/dev/null
pkill -f "camoufox" 2>/dev/null
sleep 5

# Start fresh
/usr/local/bin/camofox server start &
sleep 10

# Verify
curl -s http://localhost:9377/health
# Should show: {"running":true,"browserConnected":true,...}
```

### Playwright 1.60 Shim (REQUIRED)
The npm `camofox-browser` package bundles `playwright-core` v1.60.0 which removed `browserServerImpl.js`.
Without the shim, `browserConnected` stays `false` and tab creation returns 500.

**Verify shim is in place:**
```bash
cd /usr/local/lib/node_modules/camofox-browser/node_modules/playwright-core/lib
node -e "console.log(typeof require('./browserServerImpl.js').BrowserServerLauncherImpl)"
# Should print: function
```

**If missing:** See `references/playwright-160-shim-fix-2026-06-04.md` for the shim content.
Apply to BOTH locations:
1. npm package: `/usr/local/lib/node_modules/camofox-browser/node_modules/playwright-core/lib/browserServerImpl.js`
2. Python venv: `<venv>/lib/python3.x/site-packages/playwright/driver/package/lib/browserServerImpl.js`

### Python server.py Null Proxy Patch
In `<venv>/lib/python3.x/site-packages/camoufox/server.py`, after `config = launch_options(**kwargs)`, add:
```python
if config.get('proxy') is None:
    del config['proxy']
```

### Python Serverless (Alternative to REST API)
When the HTTP server has issues, use the Python context manager directly:
```python
from camoufox import Camoufox
with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto("URL")
    page.wait_for_load_state("networkidle", timeout=15000)
    text = page.inner_text("body")
```
**Note:** Requires the venv Python (`~/venv/bin/python3`) and the server.py patch.

### REST API (Preferred Method)
See `references/camoufox-rest-api-complete-reference-2026-06-04.md` for the complete protocol.
Key: Use Python `urllib` to call the REST API — more stable than the Hermes browser tools.

---

## Canonical File Write Method

**NEVER use append mode, write_file, patch, sed, awk, or line-by-line editing
on tracker files.** Only Path().write_text() with complete rebuilt content.

```python
from pathlib import Path
path = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/UN-VACANCIES-TRACKER.txt")
content = path.read_text()
# modify
path.write_text(new_content, encoding='utf-8')
```

**After EVERY write — mandatory verification:**
```bash
sync
wc -l /path/to/UN-VACANCIES-TRACKER.txt
```

---

## Post-Write Verification Checklist

1. Line count ≈ N + 12 where N = active vacancies
2. Count of numbered rows = N active vacancies
3. "MATCH ANALYSIS" does NOT appear
4. "Applied" DOES appear in header
5. Every data row ends with "NO" or "YES"
6. Sort is correct (deadline ascending, TBD last)
7. sync after write

---

## Known Pitfalls

See `references/batch-scoring-pitfalls-2026-06-09.md` for the full post-mortem and fixes for a session where the tracker lost deadlines, VIDs, and sort order. Key lessons:
- `parse_date()` must handle at least 3 formats (ISO, US MM/DD/YYYY, textual "Jun 17, 2026")
- VID regexes must NOT include ambiguous body-text words like "reference" — use structured field regexes only
- NEVER overwrite a filename-derived VID with a body-text match
- `TODAY_STR` must be live UTC date, never hardcoded
- Tracker sort key must be `(deadline, -score)`, not scan order
- The "Top score" print must use `max()`, not `scored[0]` which is sorted by deadline
- **CRITICAL: The tracker must ALWAYS sort by deadline ascending. Active vacancies sorted by deadline, roster open-ended positions below.**
- **CRITICAL: Every vacancy row MUST have a deadline column. 'TBD' is acceptable only when the portal genuinely has no deadline. Never leave the column empty.**
- **CRITICAL: The 'score' column must be at the end of the row, after the deadline column and before the vacancy ID column. The score emoji must be one of 🔴🟠🟡🟢.**
- **🆕 Body-text deadline extraction is REQUIRED when frontmatter is absent (2026-06-09):** Most JD files (UNICEF, WHO, ITU, etc.) do NOT have structured frontmatter. Deadlines live in body text as `**Deadline:** 31 December 2026`. A comprehensive 25+ pattern regex sweep across all JD files is needed. See `references/jd-body-text-deadline-extraction-2026-06-09.md` for the complete extraction recipe, fuzzy title-matching algorithm (since VIDs are "**"), and the tracker rebuild with 4 sections (Open/Expired/Rolling/Roster).

**See `references/scoring-engine-v2-architecture-2026-06-09.md` for the complete architecture of the programmatic batch scorer (`score_all.py`) built on 2026-06-09, including domain cap tables, director bonus logic, penalty rules, and the three critical bugs fixed during that session (domain overwrite, unicode whitespace, missing backup).**

See `references/camoufox-rest-unicef-pageup-pattern-2026-06-06.md` for the UNICEF PageUp-specific scraping pattern, title extraction from URL slugs, and post-processing workflow.

- **🆕 Domain variable overwrite bug in score_all.py (2026-06-09):** The scoring engine's `dom` variable was sequentially overwritten by each matching domain keyword. AI roles (cap=22) with cybersecurity content could get capped at 14 because `dom='cyber'` was set AFTER `dom='ai'`. The fix: track ALL domains with `dom_scores = {}`, pick the highest-scoring domain for the cap. This is documented in `references/scoring-engine-v2-architecture-2026-06-09.md`.
- **🆕 score_all.py overwritten without backup (2026-06-09):** During a session of penalty tuning, domain cap fixes, and date parser patches, `score_all.py` was overwritten 3+ times with no versioned backup. The original v1 scoring logic (which produced the 2026-06-09 15:36 tracker with 6 STRONG entries) is **permanently lost**. The only remaining trace is the backup tracker file itself. **Rule: Before ANY edit to the scoring engine, run `cp score_all.py BACKUP/score_all_$(date +%Y%m%d_%H%M).py`.** See `references/scoring-engine-v2-architecture-2026-06-09.md` for the recovered architecture and calibration anchors. Additional bug details (domain overwrite, unicode whitespace, missing robotics keywords) are in the `vacancy-compatibility-scoring-engine` skill at `references/batch-scoring-bugs-domain-overwrite-unicode-robotics-2026-06-09.md`.
- **Emoji breaks positional parsing:** 🚨 Fixed-width column parsing FAILS when emoji characters (🔴🟠🟡🟢) are present. A single emoji is 1 Python string index position but 4 bytes in UTF-8, causing all subsequent column positions to shift. The header line shows visual positions that don't match Python string indices. **Solution:** Use regex to find the emoji first, then extract fields relative to the emoji position, not by fixed indices. Or parse the entire line with `re.split(r'\s{2,}', line)` after stripping emoji, then re-insert. See `references/emoji-tracker-parsing-2026-06-04.md` for the canonical parsing approach.
- **🆕 Archive vs Tracker confusion → STOP/HALT incident (2026-06-06):** `UN-VACANCIES-ARCHIVE.txt` (comprehensive historical record with scoring details, roster, new entries) and `UN-VACANCIES-TRACKER.txt` (live active vacancies table, rebuilt from scratch) are NOT interchangeable. When the user says "ARCHIVE", never infer the live tracker also needs editing. If the user gives any STOP/HALT/WRONG-FILE signal, halt immediately, do not "finish the current step," restore from backup. Full protocol: `references/archive-file-structure-and-workflow-pitfalls.md`.
- **Camoufox tab crash after ~10 navigations:** Save progress every 5-8 calls
- **Persistent failure:** If same error after ONE restart, STOP and report
- **Cookie text ≠ no content:** Check for duties/responsibilities sections first
- **Scanner artifacts:** Skip PORTAL_EXTRACT, SCAN_LOG, PROBLEMS_REPORT filenames
- **Timezone edge:** IMF/WB deadlines use EDT (6h behind CEST)
- **UNIDO SuccessFactors title filter gap (patched 2026-06-04):** The UNIDO Division of Digital Transformation and AI (TCS/DAI) posts roles with generic titles like "Industrial Development Officer" (P-3) that contain zero ICT keywords. The standard `is_ict_title()` filter rejects these. **Fix:** `run_unido.py` now has a UNIDO-specific exception for known TCS/DAI roles. Additionally, every UNIDO detail page contains organizational boilerplate mentioning "digital transformation", "TCS/DAI", "AI" across all job postings. The `is_ict_full()` body filter now splits at "Main Responsibilities"/"Functional Responsibilities" before checking keywords to avoid false positives from boilerplate. See `references/unido-successfactors-quirks.md`.\n\n- **UNESCO scraper EPIPE crash (~180s):** `run_unesco_v4.py` hits `Error: write EPIPE` after fetching ~15-20 keyword search pages because Scrapling's embedded Playwright driver crashes. The script fetches successfully but crashes during teardown. If it times out, partial results may still be saved — check `UN_UNESCO/` for new files.
|- **WTO SmartRecruiters URL redirects:** The WTO portal URL `https://careers.smartrecruiters.com/WTO` redirects to `jobs.smartrecruiters.com` root. The SmartRecruiters scraper finds 0 jobs because it lands on the generic root page, not WTO-specific listings. WTO may need a different approach (Camoufox or manual URL discovery).
|- **UNICEF Playwright crash (resolved 2026-06-06):** `run_unicef.py` crashes with Playwright Node v24 incompatibility + AWS WAF. **RESOLVED:** Camoufox REST API with 25s JS render waits extracts FULL JD content (8-14KB). See the "UNICEF Camoufox REST API" pitfall above for details.
|- **Unified scanner UnboundLocalError in Phase A2:**
|- **🚨 camoufox_rest_scan.py saves listing page content, NOT individual job detail pages (verified 2026-06-08):** When run, `camoufox_rest_scan.py` saves files named `UNICEF_XXXXXX_Current vacancies.md` that contain the UNICEF careers listing page (with cookie banners, navigation, and "Current vacancies" h1) — NOT the actual job detail page content. These files are NOT useful for scoring. After running, inspect filenames — any file with "Current vacancies" in the name is a listing dump, not a JD. Delete these files. Use `camoufox_fulljd_scraper_v2.py` instead (runs ICRC + UNICEF one-by-one with 25s waits) for proper full-JD extraction. The `camoufox_rest_scan.py` WTO function similarly only captures Workday listing pages.
|- **🚨 run_workday.py without agency argument only scans IMF (not WFP/UNHCR) (verified 2026-06-08):** The script at `scripts/run_workday.py` accepts an optional positional argument for the target agency (`workday`, `imf`, `unhcr`). When called without arguments, it defaults to IMF only. WFP requires `uv run python3 run_workday.py wfp` and UNHCR requires `uv run python3 run_workday.py unhcr`. To scan all Workday portals, run the script once per agency. Running `run_workday.py` alone does NOT scan WFP or UNHCR.
|- **🚨 camoufox_fulljd_scraper_v2.py re-scrapes jobs already in tracker (verified 2026-06-08):** After running the full-JD scraper for ICRC + UNICEF, 28 new JD files were created but ALL 15 UNICEF jobs and ALL 13 ICRC jobs were already in the tracker from previous scans. Before adding new entries to the tracker, always cross-reference Vacancy IDs against the existing tracker. Use `grep` on UN-VACANCIES-TRACKER.txt to check if a VID already exists before treating it as new. `curl -s "http://localhost:8888/search?q=site:careers.un.org+IT+P4&format=json"`
- **🆕 Found-during-scan but not saved (verified 2026-06-13):** UNICEF_593464 (Digital Learning and Teacher Consultant, Helsinki) was discovered during a keyword search scan but was NOT extracted, saved to JD_FILES/, or added to the tracker. It appeared in a "report" with an incorrect `TBD` note when the live portal showed a clear `17 Jun 2026` deadline. **Rule:** When you find a vacancy during keyword search, you must extract the full JD, save it as a markdown file, and add it to the tracker — in the same session. A "report" is not a substitute for capture. If you cannot extract the full JD (time constraints, portal issues), flag it explicitly with the VID and what happened — never mark a live-deadline vacancy as TBD.
- **🆕 Domain variable overwrite bug + missing robotics keywords (2026-06-09):** See `vacancy-compatibility-scoring-engine/references/batch-scoring-bugs-domain-overwrite-missing-ai-2026-06-09.md` for the complete post-mortem. Three bugs found during a full rescoring audit: (1) `dom` variable overwritten by each domain check → AI roles capped at wrong domain's limit; (2) AI keyword list missing `robot`, `robotics`, `humanoid` → UNICEF Humanoid Robots scored 42 instead of 64; (3) Unicode whitespace `\xa0` in deadline parser → wrong dates parsed. All fixed in current `score_all.py`.
- **🆕 Camoufox tab fatigue (2026-06-09):** Camoufox crashes with SIGKILL (exit 137) after ~10-12 navigations. Root cause: tab accumulation without cleanup. **Mitigation:** Restart Camoufox server between batch operations, or use SearXNG fallback for remaining portals. For batch scraping (e.g. UNICEF), use a single Python script with Camoufox REST API instead of per-job navigation.
- **🆕 Deadline audit protocol (2026-06-12):** See `references/deadline-formats-and-audit-protocol.md` for the complete per-agency deadline format table, known scraper bugs (INSPIRA off-by-one, WTO 404 = expired), and the systematic audit procedure. Run this audit whenever deadlines are questioned or before delivering a scan report.
- **🆕 TBD deadline audit protocol (2026-06-13):** See `references/tbd-deadline-audit-protocol-2026-06-13.md` for the systematic 3-round validation procedure. Most agencies never post without a deadline — every TBD must be justified as Roster or genuinely Rolling. Also captures the UNIDO portal edge case (listing table has deadlines scrapers miss) and the World Bank "Not Specified" template pattern.
- **🆕 broad_scan_keywords v2.0 (2026-06-09):** Expanded from ~50 ICT keywords to 200+ contextual keywords across 10 career contexts. The `is_broad_relevant_full()` function still requires **2 arguments** `(title, body)`. All 25 scraper scripts use this correctly. See `scripts/broad_scan_keywords.py` for the full keyword list.
- **🚨 run_itu_v4.py creates duplicate stub files (verified 2026-06-09):** The ITU scraper saves short stub versions (~700-1000 bytes, 19 lines) alongside full JDs (~5-10KB, 48+ lines) for the same job ID. This happens when the script saves both a listing-page snippet and the full detail page. **Post-scan cleanup:** After each ITU scan, dedup by job ID and keep only the largest file per ID. Use: `python3 -c "from pathlib import Path; import re; from collections import defaultdict; d=defaultdict(list); [d[re.match(r'ITU_(\d+)',f.name).group(1)].append(f) for f in Path('JD_FILES/UN_ITU').glob('ITU_*.md') if re.match(r'ITU_(\d+)',f.name)]; [sorted(v, key=lambda f:f.stat().st_size)[:-1] for v in d.values() if len(v)>1]; [f.unlink() for sub in [sorted(v, key=lambda f:f.stat().st_size)[:-1] for v in d.values() if len(v)>1] for f in sub]"` — deletes all stub duplicates, keeps the largest JD per job ID.
- **✅ ALL 26 scraper scripts FIXED (2026-07-02):** Every per-agency script now has `BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")` — no more `Downloads/TEST` references. All scripts also copied to `WORKDIR/scripts/` for self-containment. The UNICEF script directory was fixed from `UNICEF` to `UN_UNICEF`. No manual path verification needed before scans anymore.
- **🚨 DIR_NOT exists error = mkdir first:** When a scraper script fails with `FileNotFoundError`, the agency subdirectory usually doesn't exist in `JD_FILES/`. Create it with `mkdir -p WORKDIR/JD_FILES/UN_{AGENCY}` and re-run. Example: UNICEF needed `UN_UNICEF/` creating before first run (2026-06-03).
- **macOS SSL cert for careers.un.org:** The INSPIRA API script needs `ssl._create_default_https_context = ssl._create_unverified_context` to bypass macOS 26 cert chain issue. Patched into `run_inspira_v4.py` 2026-06-03.
- **Title-only ICT filter misses division-based ICT roles (UNIDO, etc.):** `is_ict_title()` checks only job title strings against 120+ keyword phrases. Roles in "Digital Transformation & AI" divisions with generic titles like "Industrial Development Officer" are missed. **Fix:** For UNIDO/SuccessFactors, after the script runs, do a Camoufox spot-check on the listing pages for "AI" and "Digital" keywords. Navigate to each job's detail page and inspect the division field in the Organizational Context. Save JDs manually. See `references/unido-scanning-trap.md`.
|- **UNICEF Camoufox REST API / CLI snapshot — BOTH return 0 jobs (✅ confirmed 2026-06-12):** The `run_unicef.py` script has THREE failure modes: (a) Playwright crash on Node v24 + AWS WAF; (b) Camoufox CLI `snapshot` returns 0 jobs even on a fresh server restart; (c) **the Camoufox REST API approach does NOT reliably render job cards** in the snapshot DOM despite showing 40+ vacancies in the real browser. Restarting Camoufox does NOT fix this — it's a fundamental limitation of how the UNICEF PageUp SPA renders content to automation tools. **The FIX (confirmed working every time): Use direct `browser_navigate + browser_console JS DOM extraction`.** The Hermes browser tools (routed through Camoufox via `CAMOFOX_URL`) render the SPA correctly in the headed browser — the issue is specifically with CLI snapshot and REST API responses.

**Confirmed extraction workflow (2026-06-12):**
1. Ensure Camoufox is running: `curl -s http://localhost:9377/health` shows `browserConnected: true`
2. Navigate to `https://jobs.unicef.org/en-us/listing/` via `browser_navigate`
3. Accept cookie popup if shown (click the close button ref)
4. Type a keyword into the search textbox (ref e13 — `browser_type`), then press Enter via `browser_press`
5. Extract ALL rendered job links in one shot with `browser_console(expression="JSON.stringify(Array.from(document.querySelectorAll('h4 a')).map(a => ({title: a.textContent.trim(), url: a.href})))")`
6. For detail pages, navigate to the full URL and extract `document.querySelector('article').innerText`

**Keyword strategy (all yield different subsets — use all for full coverage):**
| Keyword | Typical Yield | Notable Roles Found |
|---------|-------------|---------------------|
| Digital | 30-40 jobs | Data Engineer P-3, Development Lead P-3, DPG Manager, Governance Consultant |
| AI | 5-10 jobs | AI Risk Mitigation, Innovation P-3 |
| ICT | 2-5 jobs | ICT Policy Consultant, ICT Associate |
| IT | 2-5 jobs | IT management roles |

**Key UNICEF-specific extraction notes:**
- The listing page shows ~40+ jobs initially but ONLY for the first page. Use keyword filters to narrow down to ICT-relevant subsets rather than attempting multi-page pagination
- Job numbers are 6-digit (e.g., 593532). The ref number is `#00137299` format. Log as `593532/#00137299`
- Detail page deadlines: found in `<time>` element in listing page, or in detail page as `**Deadline:** 19 Jun 2026 11:55 PM`
- Location is in the listing page paragraph after the h4 heading: `"Location: Spain"`
- Many UNICEF roles are NO/G-level (national officer, junior) — filter at scoring phase, not during scraping
- Cookie popup must be dismissed before keyword search works
  - `jobs.unicef.org/en-us/list` — listing page renders properly, extract job links with `/en-us/job/(\d{6})/([^"]*)` regex
  - Detail pages need 25s wait for PageUp SPA to fully render
  - Use `document.body.innerText` (NOT `outerHTML`) for best content extraction
  - Title is "Current vacancies" in `<h1>` — extract from URL slug instead
  - Job links: `/en-us/job/{6digitID}/{slug}` format
  - Many UNICEF ICT roles are G8/G9 (too junior) or in hardship locations — filter carefully
  - Language: English required, French/Arabic/Spanish often required for field roles
  - Scraper script: `scripts/camoufox_fulljd_scraper_v2.py`
  - **File naming:** Files are saved with slug-based titles (e.g., `UNICEF_593542_Data_Science_Machine_Learning_Consultant.md`)
|- **ICRC Camoufox REST API — FULL JD extraction (✅ WORKING, updated 2026-06-06):** The `run_icrc_v2.py` Playwright script crashes (Node v24). **Working alternative:** Camoufox REST API. Key findings:
  - `careers.icrc.org/go/All-Jobs/3807301/` — listing renders properly
  - Job links: `/job/{LOCATION}-{TITLE}-{JOBID}/{9DIGITID}/` format
  - Full JD content extracts cleanly (5-17KB per job) with 25s waits
  - **Grade filter:** ICRC uses A/B/C grades. Minimum acceptable is B3 (≈ P-3). C2 and below are TOO JUNIOR
  - Most ICRC openings are field operations, HR, finance, legal — not ICT
  - Scraper script: `scripts/camoufox_fulljd_scraper_v2.py`
  - **File naming:** Files are saved with `UN_ICRC_` prefix (e.g., `UN_ICRC_1401156833_Planning_Monitoring_Manager.md`). Rename to `ICRC_` prefix after scraping if consistency with existing files is desired.
|- **Camoufox REST API file naming (2026-06-06):** `camoufox_fulljd_scraper_v2.py` saves files with `UN_ICRC_`/`UN_UNICEF_` prefixes. Existing files use `ICRC_`/`UNICEF_`. Rename after scrape: `UN_ICRC_*` → `ICRC_*`, `UN_UNICEF_*` → `UNICEF_*`.
> **UNICEF deadline extraction + 3-round validation:** `references/unicef-deadline-extraction-3-round-validation.md` — NEVER report TBD for UNICEF. Every UNICEF JD has a concrete deadline.
|- **Unified scanner UnboundLocalError in Phase A2:**