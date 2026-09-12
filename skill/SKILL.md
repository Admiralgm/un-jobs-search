---
name: un-jobs-search
description: >-
  Total and fully reliable UN sector vacancies extraction and tracking.
  Per-agency scraper scripts for 28+ UN/International organization career
  portals (executed from the WORKDIR), full-JD extraction, mandatory
  live-deadline verification, manual one-by-one scoring via the
  vaccancy-compatibility-scoring-engine skill (v7.0.0, 8-parameter),
  and maintenance of UN-VACANCIES-TRACKER.txt (136-char fixed-width
  table format). CONTEXTUAL PRE-FILTER: broad keyword capture across
  10 career contexts — scrape FIRST, disqualify LATER in scoring.
  NO batch speedup. NO title-only scoring.
version: 3.0.0
author: User / Hermes Agent
tags: [un-jobs, direct-portals, scoring, full-jd, tracker, one-by-one, broad-scan]
related_skills:
  - vaccancy-compatibility-scoring-engine
  - cv-repository
  - tracker-file-format
---

# UN-JOBS-SEARCH — Total UN Sector Vacancies System v3.0.0

## CHANGELOG
- **v3.0.0 (2026-09-12)** — Cleanup with user mandate: preserve scanning/scoring/tracking capability on ALL 28+ portals. Removed: duplicate protocol sections (deadline extraction v3/v4, 3× tracker rebuild, 3× Camoufox REST reference), dead 4-section box-drawing tracker formats, deprecated multi-agent dispatch essays, batch-scoring workflow (superseded by engine v7.0.0 manual rule), Cloudflare "preferred method" essay (self-refuted; blocked portals are persistently failed), stale snapshot tables ("204 JDs", agency counts — live JD_FILES has 2900+ files), incident essays compressed to one-line pitfalls, INDEX.md legacy pointers. Fixed: execute_code tracker writes → venv-python via terminal (sandbox-isolated FS hazard), scoring references v5.0/7-param → engine v7.0.0/8-param, tracker spec unified to measured live format (136 chars, 5 emoji bands incl. 🔵 0-49), 4 scripts (run_wvi.py, run_untourism.py, camoufox_rest_scan.py, camoufox_fulljd_scraper_v2.py) + unops-avature-verification-protocol copied into this skill's tree.
- **v2.1.0** — previous version (inherited structure; full history in backup `DATA_REPOSITORY/skill-backups/2026-09-12-un-jobs-search-cleanup/un-jobs-search/`).

---

# PART 1 — EXECUTION PROTOCOL (read fully before scanning)

## Who You Are
You are a disciplined scanning agent. You run per-agency scraper scripts, extract UN job vacancies, score them manually, and maintain the tracker. You do NOT improvise. If something is not covered by these rules, report it and move on.

## READING RULE (token efficiency)
This skill is ~850 lines. Read PART 1 fully. Consult PART 2 (queue/scripts), PART 3 (tracker), PART 4 (scoring) and PART 5 (protocols/pitfalls) on demand via read_file. Do NOT re-read sections you already executed against in this session.

## HARD LIMITS
- Maximum 50 tool calls per session; maximum 8 portals per session (pick from the Daily Scan Queue, rotate daily).
- If a portal script fails, do NOT retry more than once — report "SKIPPED — {portal}: {error}" and move on.
- If turn count exceeds 50, STOP immediately — write results, deliver the report, stop.

## ABSOLUTE PROHIBITIONS (violating ANY is a critical failure)
1. NEVER read or write files outside the WORKDIR: `~/Downloads/DATA_REPOSITORY/WORKDIR/`
2. NEVER write new Python scraper scripts (.py) — use ONLY the existing scripts in `WORKDIR/scripts/`. Ad-hoc scraping .py files in /tmp are also forbidden. One-liner shell pipelines (`curl ... | python3 -c "..."`) are acceptable.
3. NEVER use `execute_code` for tracker/archive writes — its sandbox has an isolated filesystem (destroyed the tracker 2026-06-29). Use `~/.venv/bin/python3` via `terminal` with `Path().write_text()`, or `read_file`+`write_file`.
4. NEVER hallucinate job titles, deadlines, grades, locations, or vacancy IDs — only what script output / JD files show.
5. NEVER delegate scanning or scoring to subagents — everything in the parent agent. No `delegate_task`, no cmux dispatch, unless the user EXPLICITLY requests multi-agent dispatch.
6. NEVER skip Phase 0 (hygiene) — backup and expired cleanup are mandatory every session.
7. NEVER write "TBD" without LIVE confirmation of a rolling/roster posting (see DEADLINE PROTOCOL).
8. NEVER use `web-preclean.py` — legacy utility. Use the per-agency `run_{portal}.py` scripts.
9. NEVER write new tracker rows with guessed fixed offsets — parse the live format (PART 3) or clone a template row.

## 🚨 PYTHON INVOCATION RULE — READ FIRST (2026-08-16)
**ALL `run_*.py` scripts MUST be executed with the direct venv path:**
```
~/.venv/bin/python3 <script>
```
- NEVER `uv run python3` — breaks PyYAML's CLoader (`hasattr(yaml,'CLoader')=False`) → camoufox ImportError crash (2026-08-16 UNICEF failure + tracker corruption).
- NEVER bare `python3` — system Python 3.14 has no packages and a cffi architecture mismatch.
- Verified: `~/.venv/bin/python3 -c "import yaml; hasattr(yaml,'CLoader')"` → True.

## 🚨 INSPIRA DEADLINE -1 DAY RULE (confirmed 2026-06-21; script-fixed 2026-08-30)
The INSPIRA API returns `endDate` as UTC timestamp (`...T03:59:59.000Z`) = midnight rollover grace. **Real deadline = endDate date MINUS 1 day.** `run_inspira_v4.py` now subtracts the day internally (verify: any NEW INSPIRA row's deadline matches the careers.un.org page). Verification protocol:
1. Check the job against the active ITECNET listing (`/api/public/opening/jo/list/filteredV2/en`); absent → EXPIRED regardless of endDate.
2. When in doubt, set the deadline ONE DAY EARLIER — better to mark expired early than keep an expired job open (2026-06-21 UN_276853 incident).
3. Applies to INSPIRA (UN_ prefix VIDs) only; other portals have their own formats.

## 🚨 INSPIRA QUERY MODEL (v4.2 keyword-union, 2026-09-01 — supersedes dual-query)
The historical dual-query (jn=ITECNET + jf=IST) MISSED roles classified under other
networks — confirmed miss UN_283767 (OCHA ReliefWeb Product Manager P4, jn=Economic,
Social and Development + jf=Programme Management). **v4.2 now runs a keyword-union
across the whole portal** (`filterConfig.keyword`: information, data, technology,
digital, innovation, ICT, system, cyber, telecommunication, AI, knowledge
management, software, information systems, information management, database,
network), paginated, deduped by jobId. Verified 2026-09-01: returns ~263+ jobs — a
strict SUPERSET of everything ITECNET+IST returned (11 jobs, 0 uncovered). The API
keyword match is fuzzy, so precision comes from downstream HARD_REJECT +
`is_ict_body()` filtering — never trust the raw union count as the ICT yield.

**Post-scan verification (MANDATORY):** the script prints `Total jobs fetched
(keyword union): N`. Expect N ≥ ~250 on a healthy run (today's observed baseline:
283). N far below that → the API or pagination may be degraded — REPORT. If a
specific vacancy can't be found, check it directly on careers.un.org before
declaring it expired.

## ⚠️ UNOPS VERIFICATION — AVATURE PAGINATION TRAP (2026-08-30)
UNOPS Careers Marketplace is JS-rendered Avature. NEVER verify via (a) curl (60KB CSS shell, zero job data), (b) list-pagination clicking (false 'vacancy gone' negatives after ~2 pages; 2026-08-30 incident), or (c) JS form-input injection (ignored). ALWAYS use the direct JobDetail URL `https://careers.unops.org/careersmarketplace/JobDetail/<any-slug>/<numericJobId>` in Camoufox — renders the full job card incl. canonical `Posting End Date` (slug ignored; Avature routes on numeric ID). Protocol: `references/unops-avature-verification-protocol-2026-08-30.md` in this skill's references/ (and WORKDIR/references/).

---

# PART 2 — DAILY SCAN QUEUE & SCRIPTS

All scripts execute from **WORKDIR/scripts/** (`~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/`) with the venv python. The skill's own `scripts/` tree mirrors the same set (run_wvi.py, run_untourism.py, camoufox_rest_scan.py, camoufox_fulljd_scraper_v2.py copied in 2026-09-12) — WORKDIR/ is operative.

**Tier 1 (always scan — high ICT yield):**
1. WHO — `run_who.py`
2. ITU — `run_itu_v4.py`
3. UNICEF — `run_unicef.py` (primary; alternative `camoufox_fulljd_scraper_v2.py` via Camoufox REST API — also covers ICRC)
4. IAEA — `run_iaea.py`
5. UNOPS — `run_unops_v3.py`

**Tier 2 (rotate daily — medium yield):**
6. ICRC — `run_icrc_v2.py` (primary; alt: camoufox_fulljd_scraper_v2.py)
7. UNESCO — `run_unesco_v4.py`
8. ILO — `run_ilo_v3.py`
9. OECD — `run_oecd_v4.py`
10. WFP — `run_workday.py` (Workday — covers WFP, IMF, UNHCR; see argument pitfall below)
11. WIPO — `run_wipo.py` (Taleo — ICT Dept posts IT transformation/change mgmt roles). PREREQUISITE: Playwright binary. If `Executable doesn't exist ... chrome-headless-shell-1223`: run `~/.venv/bin/python3 -m playwright install chromium` (~92MB into ~/Library/Caches/ms-playwright/).
12. WVI (World Vision International, NON-UN INGO) — `run_wvi.py` (Workday cxs JSON API, direct HTTP — no browser). See WVI notes below.

**Tier 3 (low yield — scan only if time/budget allows):**
13. UNDP — `run_undp_v4.py`
14. WMO — `run_wmo.py`
15. FAO — `run_fao.py`
16. ICAO — `run_icao_v3.py`
17. INSPIRA — `run_inspira_v4.py` (covers UNCTAD, UNECE, UNECA, UNWTO, UPU, UN-Habitat, UNOV, UNON, UNSSC, UNIDIR, UNGM, UNJSPF + UNDRR/UNESCAP/UNESCWA via ITECNET/IST)
18. UN Tourism (ex-UNWTO) — `run_untourism.py` (server-rendered HTML at untourism.int/work-with-us; apply links are S3 PDFs; ICT roster = Area II Information Technology, Madrid + Riyadh, ONGOING)

**Skip these (low/zero ICT yield, confirmed 2026-05-28; WIPO re-added 2026-07-28):**
UNFPA, UNICRI, UNITAR, UNU, GICHD, UNDRR, UNESCAP, UNESCWA, IMO, IFAD, UNIDO, UNHCR — produce ~0 ICT vacancies per cycle; scan only if explicitly requested. UNICRI's ICT roles come through the INSPIRA script.

**Orchestrator:** `run_broad_scan.py` v6.0 — REAL orchestrator: discovers all run_*.py, excludes itself, wave scheduling (HTTP parallel → browser waves of 6 → camoufox strictly sequential), per-script logs in `logs/`, JSON report from actual subprocess outcomes. Flags: `--list`, `--only`, `--skip`, `--timeout`. If ever edited, verify it ACTUALLY launches subprocesses — never accept a report file it did not earn (the v5.0 stub wrote plausible reports without running anything — data-integrity hazard).

## WVI PORTAL NOTES (2026-09-08)
- **Portal:** https://worldvision.wd1.myworkdayjobs.com/WorldVisionInternational. Scraper `run_wvi.py` v1.0 (HTTP wave class in orchestrator). Baseline 2026-09-08: 304/304 JDs fetched+scored → 0 applications recommended.
- **Eligibility architecture (CRITICAL):** ~90% of postings are "Local Applicants Only". The global IT/digital cluster is gated to "countries where WVI is legally registered" — **Serbia is NOT one — do NOT re-litigate this filter per session** (verified against all 304 JD bodies). Only JDs whose footer says **"Local and International Applicants (IA's) Accepted"** are reachable → `run_wvi.py` saves ONLY those (~33/304). `workerSubType` facet is UNRELIABLE — eligibility comes ONLY from JD body text.
- **Traps:** paginate to 2 consecutive empty batches, never break on `total=0`; cxs JSON has NO closing date (regex catches "application deadline/closing date/apply before" in body); Emergency Response Roster (~22) + GAM Talent Pipeline (4) are pre-qualification pools, not funded vacancies (scoring → CONFIRM_WITH_USER); Christian-identity clause is standard on WV JDs — flag as personal-preference signal; Intern roles appear occasionally — population gate.
- When it reports saved>0, score the new files per PART 4; expect the IT cluster to keep producing local-only roles.

## All-run_* scripts (28) — quick reference
`run_ecb.py` (ECB, SkillBound) · `run_fao.py` (FAO, Taleo) · `run_iaea.py` (IAEA, Taleo) · `run_icao_v3.py` (ICAO, Oracle HCM) · `run_icmpd_v3.py` (ICMPD, custom) · `run_icrc_v2.py` (ICRC, Taleo) · `run_ifad.py` (IFAD) · `run_ilo_v3.py` (ILO, SuccessFactors) · `run_imo.py` (IMO) · `run_inspira_v4.py` (INSPIRA API) · `run_itu_v4.py` (ITU, SuccessFactors) · `run_oecd_v4.py` (OECD, SmartRecruiters) · `run_undp_v4.py` (UNDP, Oracle HCM) · `run_unesco_v4.py` (UNESCO, SuccessFactors) · `run_unfpa_v4.py` (UNFPA, Oracle HCM) · `run_unhcr.py` (UNHCR, Workday) · `run_unicef.py` (UNICEF, PageUp) · `run_unido.py` (UNIDO, SuccessFactors) · `run_unitar_v4.py` (UNITAR) · `run_unops_v3.py` (UNOPS, Avature) · `run_untourism.py` (UN Tourism) · `run_unu.py` (UNU, Indeed) · `run_who.py` (WHO, Taleo) · `run_wipo.py` (WIPO, Taleo) · `run_wmo.py` (WMO, Oracle HCM) · `run_workday.py` (Workday: WFP/IMF/UNHCR) · `run_worldbank.py` (World Bank, CSOD) · `run_wvi.py` (WVI, Workday cxs JSON).

---

# PART 3 — WORKDIR, TRACKER FILES & TRACKER MAINTENANCE

## WORKDIR (canonical)
- WORKDIR: `~/Downloads/DATA_REPOSITORY/WORKDIR/`
- Tracker: `UN-VACANCIES-TRACKER.txt` (single source of truth) · Archive: `UN-VACANCIES-ARCHIVE.txt` · JDs: `JD_FILES/{AGENCY}/` · Scripts: `scripts/` · Backups: `BACKUP/` (single folder, timestamped filenames) · Logs: `logs/` (14-day retention) · Legacy `DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt` = pre-June-2026 format; do NOT read/back up unless the user names it.

**CANONICAL OUTPUT LOCATIONS — NO RANDOM ROOT WRITES (user mandate 2026-09-09).** Workdir root keeps ONLY: `UN-VACANCIES-TRACKER.txt`, `UN-VACANCIES-ARCHIVE.txt`, `score_all.py`, `batch_score_all.py`, `batch_score_contextual.py`, `all_jd_deadlines_broad.json`, plus `JD_FILES/ scripts/ logs/ references/ BACKUP/` dirs.
- Per-portal logs, Broad_SCAN_REPORT_*.json, SCORING_SESSION_*.md, scan_session_info* → `logs/`; new utility scripts → `scripts/`; intermediate state → `BACKUP/`; JD extracts → `JD_FILES/{AGENCY}/`.

## 🚨 BACKUP RULE — ABSOLUTELY MANDATORY
**BEFORE ANY WRITE to tracker or archive: backup first.**
```bash
mkdir -p "~/Downloads/DATA_REPOSITORY/WORKDIR/BACKUP"
DATE=$(date +%Y%m%d_%H%M)
cp .../UN-VACANCIES-TRACKER.txt ".../BACKUP/UN-VACANCIES-TRACKER_BACKUP_${DATE}.txt"
cp .../UN-VACANCIES-ARCHIVE.txt  ".../BACKUP/UN-VACANCIES-ARCHIVE_BACKUP_${DATE}.txt"
```
Verify backups exist and are non-zero. After backup, check cross-file consistency: no Vacancy ID in both tracker and archive.

## LIVE TRACKER FORMAT (measured 2026-09-12 — ANCHOR-based parsing, not fixed columns)
```
================================================================================
UN VACANCIES TRACKER — Full JD Scoring
Generated: YYYY-MM-DD | Last cleanup: YYYY-MM-DD | Last scan: YYYY-MM-DD
================================================================================

🔴🟠🟡🟢 OPEN APPLICATIONS — Sorted by Deadline (Earliest First)
#    Organization           Position Title                               Deadline       Score      Vacancy ID                    Applied
--------------------------------------------------------------------------------------------------------------------------------------
1    World Bank            Lead Digital Specialist, Pretoria (DAEDU)     2026-09-16     🔴 85      WB_38176                      NO
--------------------------------------------------------------------------------------------------------------------------------------
```
**🚨 ROWS ARE HISTORICALLY HETEROGENEOUS (measured 2026-09-12):** existing rows range
139–147 chars; deadline anchor sits at col 81–85, score emoji at col 96–100, vid at
col ~110–118, NO/YES at col 136–140. Different historical builders used different
padding (old 44/16/29/8 spec vs current 47/15/30/7). **NEVER bulk-normalize row
widths — re-padding existing rows risks misaligning titles and deadlines.
ALWAYS parse with anchor regexes** (deadline `2026-\d\d-\d\d|TBD|Open`, score
`[🔴🟠🟡🟢🔵] \d{2}`, vid `(\S+)\s+(NO|YES)\s*$`), never blind fixed indices.
- **Canonical NEW-row builder (matching live recent rows):** `#` 5 · org 22 ·
  title 47 (truncate at 47 with `…` when longer than 47) · deadline 15 ·
  score 10 (`emoji space NN`) · vid 30 · applied 7 (`NO`/`YES`) = 136 chars.
  Separator lines in the file are 134 dashes. Build with `ljust`/`[:n]` padding,
  verify new rows with `len(line.strip())` sanity + anchor regex check.
- Score emoji bands (matching engine v7.0.0 + live tracker): 🔴 85–100 · 🟠 75–84 · 🟡 65–74 · 🟢 50–64 · 🔵 0–49.
- Sort: deadline ascending; roster/rolling at bottom; stable sort for equal deadlines.

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
Pitfall (2026-08-03): parsers using the old 134-char spec (title=44, dl=16, vid=29) yield 0 rows on the live file — always measure boundaries from the live anchor regexes: dl=`2026-\d\d-\d\d|TBD|Open`, score=`[🔴🟠🟡🟢🔵] \d+`, vid at col 99, applied at col 129.

## UN-VACANCIES-ARCHIVE.txt format
```
================================================================================
ARCHIVED: YYYY-MM-DD | APPLIED: YES / NO (EXPIRED)
Organization: [org]
Title: [full title]
Vacancy ID: [id]
Deadline: [deadline]
Score: [score]
================================================================================
```

## Execution sequence per scan session (do NOT skip steps)
1. **Date check (1 call):** `terminal: date +%Y-%m-%d` — store for expiry comparison.
2. **Read tracker + archive, backup both (terminal + venv python):** extract all VIDs into a set for dedup. NOTE: `execute_code` is FORBIDDEN for these file operations (sandbox-isolated FS) — use `terminal` with the venv python or `read_file`/`write_file`.
3. **LIVE DEADLINE VERIFICATION (MANDATORY):** for every remaining-open and every new entry, verify the deadline LIVE today (curl batch first; browser only for JS-rendered portals; UNOPS via Avature JobDetail URL). Classify VERIFIED | CORRECTED | EXPIRED (→ archive) | ROLLING (genuine TBD confirmed live). Never write a row whose deadline was not verified today — this step exists because unverified TBD rows let 13 expired WB vacancies sit OPEN (2026-08-21 incident).
4. **Expired cleanup:** deadline < today AND not APPLIED → move to archive (`APPLIED: EXPIRED`), remove from tracker, renumber; any `APPLIED: YES` → archive regardless of deadline. Rebuild summary table after removals.
5. **Report urgent deadlines** (within 48h) before scanning new portals.
6. **Camoufox health (1 call):** `curl -s http://localhost:9377/health` — if no `"ok":true`, `terminal(background=true, command="camofox server start")`, wait 5s, retry once; still failing → report "CANNOT SCAN — Camoufox down", deliver Phase 0–4 results only.
7. **Run per-agency scripts (1–2 calls each, 8 portals max):** `~/.venv/bin/python3 ~/Downloads/DATA_REPOSITORY/WORKDIR/scripts/run_{portal}.py` via `terminal(background=true, notify_on_complete=true)`, wait with `process(action="wait", timeout=120)`. Check output: JD files in JD_FILES/{AGENCY}/ → proceed; error → "SKIPPED"; 0 new → valid.
8. **Score manually** per PART 4 (engine v7.0.0, 8-parameter, one-by-one, full JD required).
9. **Write tracker ONCE** via venv python `Path().write_text()` (fully rebuilt content: summary table + entries sorted; write once; `sync`; verify `wc -l`).
10. **Deliver the report** (mandatory, exact format below).

## Scan report format (MANDATORY — deliver even if interrupted)
```
UN JOBS SCAN REPORT — {DATE}
SCAN SUMMARY: Date | Camoufox status | Tracker entries before/after | New entries | Expired moved | Urgent (48h)
AGENCIES SCANNED: | # | Agency | Script | Status | New JDs | New Tracker Entries | Notes |
AGENCIES NOT SCANNED: | # | Agency | Reason | (rotation / SKIPPED — error / timeout)
NEW ENTRIES ADDED TO TRACKER: | # | Vacancy ID | Agency | Title | Grade | Location | Deadline | Score | Color |
EXPIRED ENTRIES MOVED TO ARCHIVE: | # | Vacancy ID | Agency | Title | Deadline | Reason |
URGENT DEADLINES (within 48 hours): | # | Vacancy ID | Agency | Title | Deadline | Days Left | Score |
BLOCKED / FAILED SOURCES: list portal + specific error
END OF REPORT
```
Rules: AGENCIES SCANNED lists every portal actually run; AGENCIES NOT SCANNED lists every queue portal skipped WITH reason; "New JDs" = .md files created in JD_FILES/{AGENCY}/; session interrupted → mark remaining "NOT SCANNED — session interrupted".

## Tracker corruption recovery (AGENT/2/3 pattern)
Canonical corruption signature: file balloons (82 entries ≈ 97 lines → 238+), broken VIDs (`IMF_IMF_26_R9271_Da`, `NICEF_593542`), titles merging into deadlines, sort lost, duplicate VIDs.
1. Diagnose: `grep -c '^[0-9]' UN-VACANCIES-TRACKER.txt`; check broken VIDs; compare line count vs backup average.
2. **Backup the corrupted file** to `BACKUP/UN-VACANCIES-TRACKER_CORRUPTED_$(date +%Y%m%d_%H%M).txt` before anything.
3. Find best backup (prefer `_FINAL_*`, then recent `_BACKUP_*`; skip `_CORRUPTED_*`).
4. Read the full backup; confirm proper numbering, rows end `NO`/`YES`, no dup VIDs, no truncated titles.
5. Extract archive VIDs; zero overlap expected (overlap → flag to user, do NOT remove).
6. Restore: `cp BACKUP/UN-VACANCIES-TRACKER_FINAL_*.txt UN-VACANCIES-TRACKER.txt && sync`.
7. Re-sort with sort key: roster (bottom, by score) → TBD/rolling → expired → active by deadline ascending, `datetime.max` + `-score` tiebreakers; use 136-char rows (PART 3).
8. Verify: sequential numbering, all rows end NO/YES, no dup VIDs, no archive overlap, sort correct, `sync`, line count ≈ N+15.
9. Cleanup: keep the most recent good backup + first corrupted one as forensic artifact.

## WORKDIR hygiene — orphan cleanup protocol (user mandate 2026-09-09)
When another agent left clutter: full inventory (`find "$WORKDIR" -maxdepth 5 -not -path '*/BACKUP/*'`), snapshot first (`rsync -a --exclude='BACKUP' ... BACKUP/SNAPSHOT_$(date +%Y%m%d)_CLEANUP/`), then:
- **Keep:** tracker, archive, JD_FILES/ (entire), scripts/ (entire — even unreferenced, called dynamically), BACKUP/ (protected — NEVER touch), logs/ within 14-day window.
- **Move to BACKUP/:** stray root `*.json` (except all_jd_deadlines_broad.json), `SCORING_SESSION_*.md`, `scan_session_info*`, `FULL_SCAN_REPORT_*.md`, `ORCHESTRATED_SCAN_PLAN_*.md`, `phase0_kept_rows*.json`, `STATE/`, `ROSTER/`.
- **Move to scripts/:** stray root `*.py` not in the 3-script keep list (e.g. `phase0_cleanup_*.py`).
- **Delete:** root `.DS_Store`, `__pycache__/`, logs older than 14 days:
  `find logs -type f \( -name "*.log" -o -name "*.out" -o -name "*.json" \) -not -newermt "$(date -v-14d +%Y-%m-%d)" -delete` (macOS date syntax).
- Logs live ONLY in `logs/` — legacy `scan_logs/` was consolidated 2026-09-09; if it reappears, merge and rmdir.
- Verify root shows only the 7 essential files + the 5 directories.

---

# PART 4 — SCORING (MANDATORY: MANUAL, ONE-BY-ONE, FULL JD ONLY)

**The user's standing mandate: NEVER batch/keyword/automated scoring.** Every vacancy is scored MANUALLY from the FULL JD against CV_REPOSITORY_DATABASE.md. Batch scripts may only identify new files — they may never produce scores for the tracker.

1. **Load the scoring engine:** `skill_view(name='vaccancy-compatibility-scoring-engine')` — v7.0.0 is the authority (this skill's older v5.0/7-parameter text is STALE — engine wins).
2. **Load the CV repository:** `skill_view(name='cv-repository')` / `references/cv-repository` terms only.
3. **Full JD required — NON-NEGOTIABLE:** never score from title, URL slug, or short description. Truncated/empty JD → re-extract with Camoufox REST API (longer waits 25s+, `document.body.innerText` not `outerHTML`). Only score a complete JD.
4. **Engine arithmetic (8-parameter):** `P1 (__/40) + P2 (__/15) + P3 (__/10) + P4 (__/10) + P5 (__/8) + P6 (__/7) + P7 (__/5) + P8 (__/5) = FIT_SCORE __/100` — write the explicit arithmetic in the scoring record.
5. **Fit verdicts (engine §12):** 85–100 EXCELLENT · 75–84 STRONG · 65–74 CREDIBLE/SELECTIVE · 50–64 BORDERLINE · 0–49 WEAK.
6. **Mandatory-gap caps (engine §10):** apply the lowest applicable cap after raw arithmetic (no central functional overlap → 39; 2+ mandatory GAPs crit 2–3 → 49; central language absent → 49; non-waivable degree/licence absent → 49; one decisive mandatory GAP crit 3 or one important crit 2 → 64). Report raw score, cap trigger, final score.
7. **Application decision (engine §14):** legal FAIL → DO_NOT_PURSUE; preference DO_NOT_PURSUE → DO_NOT_PURSUE; legal UNKNOWN / preference CONFIRM_WITH_USER / decisive user input needed → HOLD; 85–100 → PRIORITY_APPLY; 75–84 → APPLY; 65–74 → SELECTIVE_APPLY; <65 → normally DO_NOT_PURSUE.
8. **Tracker emoji = fit band:** 🔴 85+ · 🟠 75–84 · 🟡 65–74 · 🟢 50–64 · 🔵 <50.
9. **Do NOT delegate scoring to subagents** — they cannot reference the engine correctly.
10. **Current-work override check:** before finalising, check whether User's current work (Olivia Education, Hermes) covers role functions not in the CV database.

## Exclusion rules (apply BEFORE scoring)
| Filter | Match criteria | Action |
|---|---|---|
| Nationals-only | "nationals only", "national position" | EXCLUDE only if required nationality ≠ SR AND ≠ CZ (User: Serbian + Czech/EU dual) |
| Local recruitment | World Bank "Local Recruitment" | EXCLUDE |
| Ukraine | Location contains "Ukraine" | EXCLUDE |
| Internships / Traineeships | "Intern", "Traineeship" | EXCLUDE |
| Volunteers | "Volunteer" in title/contract | EXCLUDE |
| Junior | "Junior", "L1-Junior" | EXCLUDE |

Exception: Serbia duty station = PASS; EU/Schengen = PASS (EU citizenship). NEVER exclude Serbian-national positions.

---

# PART 5 — PROTOCOLS, TECHNIQUES, PITFALLS

## 📆 DEADLINE PROTOCOL — MANDATORY (2026-08-21)
**⛔ NO UNVERIFIED DEADLINES. EVER. NO EXCEPTIONS.** A deadline enters the tracker only if extracted from the LIVE portal that day (or revalidated live that day). TBD = "confirmed rolling/roster on the portal TODAY", never "not checked". Unverifiable → queue the verification + flag in the report. Two enforcement points: (1) BEFORE writing any new/updated row; (2) AFTER scanning, re-verify every carried-over/TBD row (VERIFIED | CORRECTED | EXPIRED | ROLLING). Reference with per-portal formats + audit procedure: `references/deadline-formats-and-audit-protocol.md` (mandatory reading before finalizing a scan report). Origin: 2026-08-21 — 13 World Bank TBD rows sat OPEN while already expired.

## CONTEXTUAL PRE-FILTER — Scrape FIRST, Disqualify LATER
Per-agency scripts import `scripts/broad_scan_keywords.py` (`is_broad_relevant_title(title)`, `is_broad_relevant_full(title, body)` — 2 args, 200+ title keywords, 100+ body keywords). 10 career contexts: ICT/Tech core, Telecom/Infrastructure, AI/ML/Agentic, Education/EdTech, UN/Intl Dev, Government/Public Sector, Healthcare/HealthTech, Finance/FinTech, Enterprise IT, Transit/Smart City. Hard-reject at pre-filter (`\b` boundaries): intern, stagiaire, volunteer, unpaid, nutrition, agricultur, medical, doctor, nurse, teacher, hr, logistics, supply chain.

## Camoufox essentials
- Server: `/usr/local/bin/camofox server start` (port 9377). Health: `curl http://localhost:9377/health` — initial `browserConnected: false` is NORMAL; create a tab first, then re-check. Crashes after ~10–15 tab operations → restart between portals.
- REST API rules: `navigate` → `userId` in JSON body (not query param); `evaluate` → `expression` param (not `script`), `userId` in body; `snapshot` → `userId` as query param (accessibility tree, NOT raw HTML); `/text` endpoint does NOT exist; some URLs fail on tab creation → create with example.com first.
- Full-JD extraction: 25s JS render waits for PageUp/Taleo SPAs; use `document.body.innerText` (NOT outerHTML — footer/nav boilerplate causes ICT false positives); `execute_code` sandbox blocks localhost HTTP — run via `terminal` only.
- Portal URLs: WHO `careers.who.int/careersection/ex/jobsearch.ftl` · UNICEF `jobs.unicef.org/en-us/list` (not careers.unicef.org) · ICRC `careers.icrc.org/go/All-Jobs/3807301/` · WTO `wto.wd103.myworkdayjobs.com/External` (Workday, not SmartRecruiters).
- Playwright 1.60 shim: verify `/usr/local/lib/node_modules/camofox-browser/node_modules/playwright-core/lib` — `node -e "console.log(typeof require('./browserServerImpl.js').BrowserServerLauncherImpl)"` → `function`. Missing shim → `browserConnected` stays false, tab creation 500s. Apply to BOTH the npm package lib and the venv `site-packages/playwright/driver/package/lib/` (shim content: `browserServerImpl.js` exports `BrowserServerLauncherImpl`; the shim is installed — verify only).
- Python server.py null-proxy patch: in `<venv>/lib/python3.x/site-packages/camoufox/server.py`, after `config = launch_options(**kwargs)`: `if config.get('proxy') is None: del config['proxy']`.
- Serverless alternative: `from camoufox import Camoufox; with Camoufox(headless=True) as b: page=b.new_page(); page.goto(url); page.wait_for_load_state("networkidle", timeout=15000); page.inner_text("body")` via venv python.
- Restart: `kill -9 $(lsof -ti :9377) 2>/dev/null; pkill -f camoufox; sleep 5; /usr/local/bin/camofox server start &`; verify health shows `browserConnected:true`.

## INSPIRA API (no browser)
`POST https://careers.un.org/api/public/opening/jo/list/filteredV2/en` — JSON body returns full jobDescription HTML + metadata; no auth, no Cloudflare. **macOS SSL fix:** `ssl._create_default_https_context = ssl._create_unverified_context` at script top (patched into run_inspira_v4.py 2026-06-03).

## Canonical file write + post-write verification
- Tracker writes: build the complete file in memory (venv python via terminal, or read_file+write_file), single `Path().write_text()`, then `sync` and `wc -l`. NEVER append-mode edits, sed/awk/patch on the tracker.
- Post-write checklist: line count ≈ N + header lines (~15); numbered rows == N; "MATCH ANALYSIS" absent; "Applied" present in header; every data row ends NO/YES; sort correct (deadline ascending, roster/TBD last); `sync` done; backup exists.

## Known pitfalls (operative — compress by rule, not by forgetting)
- **run_workday.py without agency arg scans ONLY IMF.** WFP: `run_workday.py wfp`; UNHCR: `run_workday.py unhcr`. Run once per agency.
- **ITU stub duplicates:** run_itu_v4.py saves ~700-byte stubs alongside full JDs for the same ID — post-scan dedup by job ID, keep the largest file.
- **camoufox_rest_scan.py saves LISTING pages, not detail pages** ("Current vacancies" filenames = listing dumps, delete; not usable for scoring). Use camoufox_fulljd_scraper_v2.py for full JDs (ICRC+UNICEF, 25s waits, does NOT cover WTO → use rest_scan v1's scrape_wto for WTO).
- **Found-during-scan must be saved in the same session:** extract full JD → JD_FILES → tracker, or flag with VID + reason (2026-06-13 UNICEF_593464 incident). Never mark a live-deadline vacancy as TBD.
- **UNICEF:** run_unicef.py has 3 failure modes (Playwright Node v24 crash + AWS WAF; CLI snapshot 0 jobs; REST API doesn't render job cards). RELIABLE route: Hermes `browser_navigate` → `browser_console` JS DOM extraction (query `h4 a` links; keyword search Digital/AI/ICT/IT; cookie popup first; 6-digit job IDs; `**Deadline:**` in detail; many roles G8/G9 or hardship — filter at scoring).
- **ICRC:** minimum grade B3 (≈P-3); C2 and below too junior. Filenames `UN_ICRC_*`/`UN_UNICEF_*` → rename to `ICRC_*`/`UNICEF_*` for consistency.
- **Emoji breaks positional parsing:** a single emoji is 1 Python string index but 4 UTF-8 bytes, shifting fixed column positions — parse relative to the emoji/field regexes, never blind fixed indices.
- **Archive vs tracker are NOT interchangeable** — "ARCHIVE" request never implies editing the live tracker; STOP/HALT/WRONG-FILE signals → halt immediately, restore from backup.
- **DIR not exists:** scraper `FileNotFoundError` → `mkdir -p WORKDIR/JD_FILES/UN_{AGENCY}` and re-run (only allowed retry).
- **Cookies ≠ empty content:** check for duties/responsibilities sections before discarding (cookie text can precede real JD).
- **Timezone:** IMF/WB deadlines use EDT (6h behind CEST).
- **WHO EPIPE:** long-running Playwright Chrome processes die after ~5 pages — expect it, partial results are still saved.
- **UNIDO:** generic-titled roles from TCS/DAI division (Digital Transformation & AI) carry no ICT keywords — run_unido.py has a division exception + splits body at "Main Responsibilities" before keyword checks.
- **UNESCO EPIPE:** run_unesco_v4.py may crash after ~15–20 pages during teardown — check UN_UNESCO/ for partial files before declaring zero.
- **Never let batch/stub scripts overwrite real rows** — batch_score_all.py overwrites the tracker with raw keyword scores; after any accidental run, restore from backup. Batch scripts are NOT the scoring path (PART 4).
- **Sort key: (deadline, -score), never scan order; TOP-score prints must use max(), not scored[0].**
- **parse_date must handle ISO + US MM/DD/YYYY + textual dates; VID regexes must not match body words ("reference"); never overwrite a filename-derived VID with a body-text match; TODAY must be live, never hardcoded.**

## References (this skill's references/, 97+ files)
Key operative references — `deadline-formats-and-audit-protocol.md` (MANDATORY for deadlines) · `unops-avature-verification-protocol-2026-08-30.md` (UNOPS verification) · `tracker-cleanup-current-format-v1.md` (table-format cleanup algorithm; replaces duplicate-entry-removal-pattern.md) · `workday-cxs-api-pattern.md` (WVI/full Workday cxs) · `scan-lessons-2026-08-29.md` · `who-boilerplate-only-save-2026-09-08.md` · `summary-table-regeneration.md` · `safe-file-rebuild-procedure.md` · `vacancy-id-convention.md` · `vacancy-verification-protocol.md` · `unreliable-sources.md` · `portal-classification-map.md` · `portal-directory.md` · `extraction-methods-by-platform.md` · `sources-checklist.md`. Batch/snapshot reference files (2026-05/06 scan results, searxng discovery, scoring-calibration essays) are historical — consult only when a specific portal behaves unexpectedly. INDEX.md is not maintained; use this list.

## Nationality note
User holds dual citizenship: Serbian AND Czech Republic (EU). Serbian nationals-only positions are OPEN to him. Czech citizenship grants EU/NATO/OECD eligibility. Exclude ONLY if required nationality matches neither Serbian nor Czech.

## SOLO AGENT MODE — DEFAULT (user preference)
- Direct execution in the current session; background parallel batches OK (`terminal(background=true, notify_on_complete=true)`), but QUALITY OVER SPEED: don't batch-optimize 20 at once, don't skip portals, don't rush, full JDs always, report every failure.
- Multi-agent dispatch ONLY on explicit user request. If requested: partition portals exclusively (one agent per portal), never `[FORWARDED]` prefix via cmux (cmux interprets `[` as command), verify cmux workspace UUIDs first (`cmux tree --all --id-format uuids`), always `cmux send-key ... Enter` after `cmux send`.
- When the user complains about speed mid-scan: acknowledge the quality-first design (25s JS render waits per page are required for full JDs), offer faster alternatives (parallel API scripts, light-mode scan-only), never silently drop full-JD extraction.

## ANTI-HALLUCINATION RULES
1. Script fails → do NOT assume jobs exist; report SKIPPED.
2. No extractable Vacancy ID → `[GEN-UNKNOWN]` + flag; never invent.
3. No visible deadline → LIVE portal per DEADLINE PROTOCOL; only a live-confirmed rolling/roster posting may carry TBD.
4. No visible grade → "Unknown", never guess.
5. Empty script output → "0 new jobs" is a valid result.
6. NEVER copy titles from memory/previous sessions — only script output + JD files.
7. 0 ICT jobs is a valid result — never pad.

## ERROR HANDLING DECISION TREE
- Camoufox health fails → start server, wait 5s, retry once → still failing: "CANNOT SCAN — Camoufox down", deliver Phase 0–4 results.
- Script fails → read error, do NOT retry, "SKIPPED — {portal}: {first line}", next.
- Script 0 JD files → valid; "0 new jobs".
- venv-python error → read error, fix syntax, retry ONCE, else report + stop.
- Camoufox tab crash (500) → SKIP portal; no tab recovery; "SKIPPED — Camoufox tab crash".

## WHAT TO DO IF CONFUSED
Do NOT improvise. Report "UNCLEAR — need guidance on: [question]", skip the step, continue, deliver partial correct results over hallucinated full results.
