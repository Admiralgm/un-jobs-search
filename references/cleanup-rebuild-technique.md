# Tracker File Cleanup & Rebuild — Technique for Parsing Region 3 Entry Blocks
# un-jobs-search skill reference
# Created: 2026-05-27 (Tracker cleanup session)

## Problem
When rebuilding the tracker file (removing expired/applied entries, sorting, rebuilding summary table), Region 3 entry blocks must be parsed correctly. The file format uses `={80}` separators between blocks, but emoji header lines can appear as orphaned text between separators.

## Block Parsing Pattern

```python
from pathlib import Path
import re

SEP = '=' * 80

path = Path("~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt")
content = path.read_text()

# Strip trailing footer junk FIRST
content = re.sub(r'\nEND OF FILE.*', '', content)

# Split into regions (find table boundary)
lines = content.split('\n')
table_end = None
for i, line in enumerate(lines):
    if 'Last updated:' in line:
        table_end = i + 1
        break

region3_text = '\n'.join(lines[table_end:]).strip()

# Split by separator and filter
parts = re.split(r'={80}', region3_text)
entry_blocks = []
for part in parts:
    part = part.strip()
    if not part or '- Title:' not in part:
        continue  # skip orphan headers and empty fragments
    # Strip any standalone emoji header lines within the fragment
    cleaned_lines = [l for l in part.split('\n')
                     if not re.match(r'[🔴🟠🟡🟢]\s+(?:RED|ORANGE|YELLOW|GREEN)\s+—', l)]
    cleaned = '\n'.join(cleaned_lines).strip()
    if cleaned and '- Title:' in cleaned:
        entry_blocks.append(cleaned)
```

## Key Pitfall — Orphaned Emoji Headers
After splitting by `={80}`, some fragments contain ONLY an emoji header line like:
```
🟠 ORANGE — GSS Transformation Lead
```
These have NO `- Title:` field and must be discarded. The real entry block following it (with Title, VACANCY ID, etc.) is the actual entry. Always filter: keep only fragments containing `- Title:`.

## Stripping Stale Urgency Annotations
During cleanup, strip `⚠️` from deadline lines in entry blocks BEFORE rebuilding:
```python
def strip_urgency(block):
    return re.sub(r'^(- Deadline:.*?)\s*⚠️.*$', r'\1', block, flags=re.MULTILINE)
```
Then re-add fresh `⚠️` only for entries within 3 days AND score >= 70.

## NEW ⚠️ Flag Rule
Only add `⚠️` after the Vacancy ID at end of table row when:
- Deadline is within 3 days of today (inclusive: today, today+1, today+2, today+3)
- AND score >= 70

## Summary Table Column Spacing (NON-NEGOTIABLE)
```python
# Correct format — each column width is fixed:
num_str = str(n).ljust(5)          # 5 chars, left-justified number
org_str = org[:22].ljust(22)       # 22 chars
title_str = title[:44].ljust(44)   # 44 chars
dl_display = date[:10]              # exactly 10 chars (YYYY-MM-DD)
# Then: 4 spaces + date + 4 spaces + score + 3 spaces + id + optional flag
row = f"{num_str}{org_str}{title_str}    {dl_display}    {emoji_score}   {vac_id}{urgent}"
```

**WRONG:** Using a 16-char deadline field (e.g., `date.ljust(16)`) — pushes score/ID out of alignment.

## Verification
```python
# Count table data rows (between the two --- separator lines)
table_section = content.split('VACANCY SUMMARY TABLE')[1].split('Total:')[0]
table_rows = re.findall(r'^\d+\s+', table_section, re.MULTILINE)

# Count entry block headers (after Last updated:)
post_table = content.split('Last updated:')[1]
r3_headers = re.findall(r'[🔴🟠🟡🟢]\s+(?:RED|ORANGE|YELLOW|GREEN)\s+—', post_table)

assert len(table_rows) == len(r3_headers) == total_entries, "MISMATCH!"
```

**Split point matters:** Table rows are BETWEEN the `---` lines in the table section. Entry headers are AFTER `Last updated:`. Do NOT use `Last updated:` as the split for counting table rows.

## Expired + Applied Removal Order
1. First identify APPLIED: YES entries (set A)
2. Then identify expired entries (deadline < today, not in set A)
3. Combined removal set = A ∪ expired
4. This prevents double-counting entries that are both expired AND applied

## END OF FILE Footer Junk
Old append-based writes may leave stale footer content at file end:
```
END OF FILE — 58 entries | Last scan: 2026-05-22
```
Always strip before parsing: `content = re.sub(r'\nEND OF FILE.*', '', content)`.
This is NOT an entry block and will corrupt the rebuild if left in place.
