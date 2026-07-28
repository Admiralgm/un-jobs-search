# 2026-06-25 Full Scan — Discovered Pitfalls

## 1. BROKEN SYMLINK — scripts/ directory
The `skills/research/un-jobs-search/scripts/` symlink is **self-referencing** (points to itself). `ls` returns "Too many levels of symbolic links".

**Actual script location:**
```
skills/experiments/new-jobs-search/scripts/
```

**Fix:** Always use the `experiments/new-jobs-search/scripts/` path when running per-agency scraper scripts.

## 2. SCRIPT OUTPUT DIR — hardcoded to TEST/
All per-agency scraper scripts hardcode their output directory:
```python
BASE_DIR = Path("~/Downloads/TEST")
```

They do NOT write to the workdir (`WORKDIR/JD_FILES/{AGENCY}/`).

**Before running any script**, ensure TEST/ subdirectories exist:
```bash
mkdir -p ~/Downloads/TEST/UN_{WHO,ITU,IAEA,UNOPS,ICRC,ILO,UNESCO,UNICEF}
```

**After scripts complete**, new JD files are in `~/Downloads/TEST/UN_{AGENCY}/`. Cross-reference VIDs against the tracker to identify genuinely new entries.

## 3. ICRC COOKIE WALL — Scrapling gets empty HTML
ICRC career pages (`careers.icrc.org`) serve a cookie consent wall that Scrapling cannot bypass. The `run_icrc_v2.py` script saves ~900-line HTML files containing only cookie-banner markup — **no actual JD content**.

**Do NOT use these files for scoring.** They have zero real content.

**Workarounds:**
- Use Camoufox browser to render ICRC detail pages and extract inner_text
- The `camoufox_fulljd_scraper_v2.py` script (in `experiments/new-jobs-search/scripts/`) handles ICRC via Camoufox REST API

## 4. UNICEF HTTP 202 on JD fetch
UNICEF's listing page returns HTTP 202 (Accepted) for some JD detail pages — the content isn't ready yet. These jobs are skipped by the script. No workaround available; retry in next scan.

## 5. WHO Taleo — Scrapling works but JD content is Taleo HTML
WHO uses Oracle Taleo. Scrapling fetches the HTML successfully but the JD content is embedded in Taleo's JS-rendered template. The `run_who.py` script extracts what it can, but some fields (full description) may be incomplete. Camoufox is more reliable for WHO.
