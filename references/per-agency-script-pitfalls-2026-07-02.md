# Per-Agency Scraper Script Pitfalls (2026-07-02 Session)

## Context
These issues were discovered during a full 16-portal scan using the `un-jobs-search` skill's per-agency scripts (`run_who.py`, `run_itu_v4.py`, etc.). They apply to any session using those scripts, which are shared between `un-jobs-search` and `un-jobs-search-minimaltoken`.

## Pitfall 1: Scripts Save to ~/Downloads/TEST/ Not Workdir

**All per-agency scraper scripts save JD files to `~/Downloads/TEST/UN_{AGENCY}/` NOT to the workdir `JD_FILES/{AGENCY}/`.**

Confirmed on 2026-07-02: 15 new JD files from 16 scraper scripts ALL landed in `~/Downloads/TEST/`. Scripts report "SAVED" in stdout but files are NOT in the expected `WORKDIR/JD_FILES/` location.

**Mandatory post-scan step:**
```bash
SRC="~/Downloads/TEST"
DST="~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES"
for f in $(find "$SRC" -name "*.md" -newermt "$(date +%Y-%m-%d) 00:00" -type f); do
    agency=$(echo "$f" | sed "s|$SRC/||" | cut -d'/' -f1)
    mkdir -p "$DST/$agency"
    cp "$f" "$DST/$agency/"
done
```

Do NOT assume "0 new JDs" just because `JD_FILES/` has no new files — ALWAYS check `~/Downloads/TEST/` first.

## Pitfall 2: Tracker Re-numbering Corrupts Existing Entry Titles

**When rebuilding the tracker with Python, NEVER parse and reformat existing entry lines into fields. The re-numbering process corrupts titles by misaligning columns.**

**Safe approach:**
1. Preserve each existing entry's FULL original line text (just `line.strip()`)
2. When re-numbering, use regex to strip ONLY the leading number: `re.sub(r'^\d+\s+', '', raw_line)`
3. Prepend the new number with `f"{str(num).ljust(5)}{raw_stripped}"`
4. Do NOT split fields and reassemble — column widths and emoji positioning will break

**Confirmed failure mode (2026-07-02):** First write attempt parsed each row into fields (org, title, deadline, score, vid, applied) and reformatted them. This caused:
- UNICEF entries lost their titles entirely (blank space)
- "World Bank" entries split into "World" + "Bank" across columns
- "UN Secretariat" entries split into "UN" + "Secretariat"
- FAO entries lost their titles

Fix: Restore from backup, only replace the leading number, preserve the rest verbatim.

## Pitfall 3: UNESCO TextHandler Decode Error

`run_unesco_v4.py` fails with `'TextHandler' object has no attribute 'decode'` on every keyword query. This is a Scrapling library compatibility issue, not a script bug. UNESCO scans will produce 0 results until Scrapling is updated. Report "UNESCO — TextHandler Scrapling error, 0 new jobs" and move on.

## Pitfall 4: UNICEF HTTP 202 Throttling

UNICEF scraper (`run_unicef.py`) successfully fetches listing pages but gets HTTP 202 on all JD detail page fetches, resulting in 0 saved JDs. This is server-side throttling, not a script bug. The 3 ICT candidates found in listing were not saveable. Report "UNICEF — HTTP 202 throttled, 0 JDs saved" and move on.

## Pitfall 5: Running All 16 Scripts in Parallel Works

Confirmed on 2026-07-02: all 16 per-agency scripts can be launched simultaneously via `terminal(background=true, notify_on_complete=true)` with no conflicts. Camoufox health check showed `browserConnected: false` initially but scripts that use Camoufox (ITU, UNESCO) connected fine. Scripts that use curl/Scrapling (WHO, FAO, UNDP, WMO, ICAO, INSPIRA, World Bank) ran independently. Total wall time ~4 minutes for all 16.

## Scan Results Summary (2026-07-02)

| Agency | New JDs | Notes |
|--------|---------|-------|
| WHO | 2 | 1 disqualified (Vanuatu nationals), 1 French-required capped 65 |
| ITU | 0 | All 30 existing or non-ICT |
| UNICEF | 0 | HTTP 202 throttled |
| IAEA | 0 | All existing |
| UNOPS | 2 | Both disqualified (LICA-3, fundraising) |
| ICRC | 0 | All existing |
| UNESCO | 0 | TextHandler error |
| ILO | 0 | All existing |
| OECD | 2 | Both junior/P-2 disqualified |
| WFP/IMF | 0 | 0 ICT from IMF |
| UNDP | 1 | Climate mismatch disqualified |
| WMO | 2 | Both disqualified (P-2, climate comms) |
| FAO | 3 | 2 scored 86 (P-4 IT Officer), 1 scored 72 (climate) |
| ICAO | 0 | All existing |
| INSPIRA | 1 | Scored 79 (P-3 IS Officer UNJSPF) |
| World Bank | 2 | 1 scored 89 (AI for Outcomes), 1 scored 73 (HR analytics) |

**4 new tracker entries added (all ≥75):** FAO_2601382 (86), FAO_2601381 (86), UN_279904 (79), WB_37368 (89)