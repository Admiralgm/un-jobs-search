# File Cleanup & Reformatting — Lessons from 2026-05-19

## APPLIED:YES entries found in active impact file

**Problem:** The impact file (UN_SECTOR_VACCANCIES_IMPACTPOOL.txt) contained 7 entries with `APPLIED: YES` that were never moved to the archive. These had future/TBD deadlines, so the expiry check (deadline < today) didn't catch them.

**Root cause:** Phase 1 cleanup only checked for `deadline < today AND APPLIED: NO` (expired). It did NOT independently check for `APPLIED: YES` regardless of deadline.

**Fix:** During Phase 1, after the expiry check, add a separate pass:
```python
# Check for APPLIED: YES entries in ALL active files (not just expired ones)
for entry in all_active_entries:
    if entry['applied'] == 'YES':
        move_to_archive(entry)
        count_applied_moved += 1
```

**Entries found and moved (2026-05-19):**
- `592902` — UNICEF Data Protection and Privacy Manager, P-4 (was in impact, moved to archive)
- `00107002` — UNICEF Data Protection and Privacy Manager (already in archive)
- `UNDP-NPSA9-EDATA` — UNDP Enterprise Data Architecture Analyst (already in archive)
- `UNDP-NPSA5-ICT` — UNDP ICT Assistant (already in archive)
- `UNDP-NPSA8-ICTCLIM` — UNDP ICT Analyst/Climate (already in archive)
- `IOM-P-ICT` — IOM ICT Officer (already in archive)
- `UNOV-IT-D1` — UNOV Chief, IT Service (was in impact, moved to archive)

## Stray separator fragment corruption

**Problem:** The file contained a stray `--------------------------------------` line (line 24) — much shorter than the standard 80-char `================================================================================` separator. This was a remnant from a previous merge/rebuild that truncated the separator.

**Detection:** After reading the file, scan for lines matching `^-{5,}$` that are NOT exactly 80 characters. These are corruption artifacts.

**Fix:** Rebuild the entire file from scratch after restoring from backup. Do NOT try to patch around the fragment.

## Inconsistent entry formatting in impact file

**Problem:** Some entries had colored headers while others had no colored header at all. Some had Verdict blocks, others didn't. The file was a mix of formats from different sessions.

**Fix:** When rebuilding, ALL entries must follow the canonical format with colored header, separator, fields, match analysis, source warning, and verdict block.

## execute_code + subprocess heredoc failure

**Problem:** Using `subprocess.run` inside `execute_code` with shell heredoc (`<< 'PYEOF'`) caused `SyntaxError: unterminated string literal`.

**Fix:** Pass Python code as a string to `python3 -c "..."` or write to a temp file first.

## Rebuild verification checklist

After ANY file rebuild, verify ALL of:
1. `grep -c "VACANCY ID:"` equals summary table row count
2. `grep -c "^- Title:"` equals summary table row count
3. `grep -c "^[🔴🟠🟡🟢]"` equals summary table row count (colored headers)
4. `grep -c "^📊 Verdict:"` equals summary table row count
5. `grep -c "APPLIED: YES"` equals 0 (in active files only)
6. All three files pass `sync` without errors
