# File Sort/Rebuild Procedure

## Problem

When re-sorting `UN_SECTOR_VACCANCIES.txt` entries by deadline, the file corrupts because it accumulates stale `END OF FILE — X entries | Last scan: ...` footers between entries from previous append-based writes. Splitting on `=====` delimiter lines and reordering embeds these footers inside entries 22, 49, 50 etc.

## Correct Procedure

1. **Restore from backup first** — always `cp UN_VACCANCIES_BACKUP_YYYYMMDD.txt UN_SECTOR_VACCANCIES.txt` before starting.

2. **Use color-emoji headers as entry boundaries** — NOT `=====` lines. Parse by finding all positions of the pattern `\n={80}\n\n[🔴🟠🟡🟢⚪] [A-Z]`. Each entry spans from one header to the next.

3. **Strip trailing junk** — for each extracted entry block, find the last meaningful line containing one of: `STRATEGIC FIT:`, `INTERVIEW PROBABILITY:`, `Verdict:`, `POTENTIAL GAPS:`, `Confidence Level:`. Cut there. Also remove any lines containing `END OF FILE` with `=` characters.

4. **Sort once, build twice** — sort the parsed entry list by deadline key:
   - Parse `- Deadline:` field, extract ISO date via regex `(\d{4}-\d{2}-\d{2})`
   - If TBD/Open/not found → use sort key `"9999-99-99"` (sorts last)
   - Sort ascending by key
   - Build BOTH the summary table rows AND the entry blocks from the same sorted list in one execute_code block. Never split across two sandbox calls.

5. **One-shot write** — rebuild the ENTIRE file (header + table + sorted entries + footer) with `Path().write_text()` in a single call.

6. **Verify** — count `- Title:` occurrences must equal numbered table rows. Check that the file is not truncated (compare to backup size, should be similar minus expired entries).

## Deadline Annotation for Urgent Entries

- Keep `⚠️` for entries expiring within 3 days that score ≥70 (COMPETITIVE+)
- In the summary table row: place `⚠️` AFTER the Vacancy ID at end of line
  - ✅ ` 1     IAEA     Consultant ...  2026-05-22    🟡 76   IAEA-TAL-... ⚠️`
- In the detail `- Deadline:` field: place `⚠️` after the date at end of line
  - ✅ `- Deadline: 2026-05-22 ⚠️`
- Add header banner: `⚠️ URGENT — N high-match vacancies expiring soon: ...`
