# Entry Block Parsing — Proven Approach

> Based on cleanup operations that succeeded (2026-05-28) after a first
> attempt with naive `split("=")` corrupted the file. Restored from backup
> and retried with this method, which works correctly.

## The Right Way to Parse Tracker Files

The three tracker files (`UN_SECTOR_VACCANCIES.txt`, `*_IMPACTPOOL.txt`,
`*_ARCHIVE.txt`) look like `====`-delimited entry blocks, but they are NOT.

A naive `text.split('=' * 80)` will produce blocks that include **partial
headers** (the color emoji line) **between** two separator lines, and the
actual fields (`- Title:`, `- VACANCY ID:`) in a **different** block segment.
Splitting by `=` and treating each block as one entry will silently drop
all data fields, producing an empty file.

### Proven Approach

```python
blocks = text.split('=' * 80)
entry_blocks = []

for block in blocks:
    block = block.strip()
    if not block:
        continue
    # An entry block is one that has BOTH Title AND VACANCY ID
    if '- Title:' in block and '- VACANCY ID:' in block:
        entry_blocks.append(block)
    else:
        # Anything else is a header, footer, or partial separator fragment
        pass
```

After this, `entry_blocks` contains exactly the entry data you need.
Parse each block for its fields individually.

### Why Naive Split Fails

An actual entry in the file looks like:

```
================================================================================

🟠 ORANGE — Some Title Here

================================================================================
- Title: Some Title Here
- VACANCY ID: XXX-12345
...
================================================================================
```

Three `====` blocks are produced for this one entry:
1. Empty block before the color line
2. The color emoji header line only
3. The data fields

Only block 3 has `- Title:` and `- VACANCY ID:`. Filtering on those
criteria is mandatory.

### Verification After Parse

After rebuilding the file:

```python
import re

main_check = main_path.read_text()
remaining_applied = re.findall(r'- APPLIED:\s*YES', main_check)  # must be 0
title_count = len(re.findall(r'- Title:', main_check))
vid_count = len(re.findall(r'- VACANCY ID:', main_check))
assert title_count == vid_count, "Mismatch between Title and VACANCY ID counts"
```

### Backup Recovery

If a write corrupts the file, immediately restore from the session's backup:

```bash
cp /path/to/backup/UN_VACCANCIES_BACKUP_YYYYMMDD.txt \
   ~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt
```

Then fix the parsing logic before retrying. Do NOT attempt to repair the
file in-place — restoration + correct rebuild is faster and safer.
