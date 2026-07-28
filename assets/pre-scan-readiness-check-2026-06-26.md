# Pre-Scan Readiness Check — 2026-06-26

Two infrastructure gaps were discovered during the 2026-06-26 full scan that caused all Tier 1 scripts to fail on first attempt.

## Gap 1: Self-referencing scripts symlink

The `scripts/` symlink under `skills/research/un-jobs-search/` pointed to itself:

```
scripts -> skills/research/un-jobs-search/scripts
```

This caused `uv run python3 skills/research/un-jobs-search/scripts/run_who.py` to fail with:
```
can't open file: [Errno 62] Too many levels of symbolic links
```

**Fix:**
```bash
rm skills/research/un-jobs-search/scripts
ln -s skills/experiments/new-jobs-search/scripts skills/research/un-jobs-search/scripts
```

**Verify:**
```bash
ls -la skills/research/un-jobs-search/scripts/
# Should show 26 .py files (run_ecb.py, run_fao.py, run_iaea.py, ...)
```

## Gap 2: Scripts hardcode TEST/ output directory

Several per-agency scripts write their output to `~/Downloads/TEST/` instead of the WORKDIR workdir. This means new JD files land in a location invisible to the tracker workflow unless you explicitly check there.

**Affected scripts and their output paths:**

| Script | Writes to |
|--------|-----------|
| `run_undp_v4.py` | `TEST/UN_UNDP/` |
| `run_wmo.py` | `TEST/UN_WMO/` |
| `run_inspira_v4.py` | `TEST/UN_INSPIRA/` |
| `run_unops_v3.py` | `TEST/UN_UNOPS/` |

**Workaround:** After running these scripts, check BOTH locations:
```bash
ls -lt ~/Downloads/TEST/UN_{AGENCY}/
ls -lt ~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES/UN_{AGENCY}/
```

**Root cause:** Each script hardcodes `BASE_DIR = Path("~/Downloads/TEST")` at the top. A proper fix would change these to the WORKDIR workdir, but the user's constraint is "no script modification without explicit approval."
