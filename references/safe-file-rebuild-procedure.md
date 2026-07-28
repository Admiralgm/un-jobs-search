# Safe File Rebuild Procedure — Updated 2026-06-06

## File Format (as of 2026-05-29)

Both `UN_SECTOR_VACCANCIES.txt` and `UN_SECTOR_VACCANCIES_IMPACTPOOL.txt` now use TABLE-ONLY format. Entry blocks (MATCH ANALYSIS, Positioning Advice, Verdict) are NO LONGER written.

**File structure:**
```
=== HEADER ===
Summary Line
COLUMN HEADER
---SEPARATOR---
row 1 (data)
row 2 (data)
...
row N (data)
---SEPARATOR---
Color coding legend
Footer
```

**Row format (space-separated, NO `|` delimiters):**
```
#     Organization           Position Title                                     Deadline     Score    Vacancy ID                     Applied
1     UNICEF                 UPSHIFT AI & Digital Strategy Consultant           2026-06-07   🟠 81   593259                         NO
```

## Parsing rows correctly

**DO NOT use `len(parts) >= 7`** — this drops valid rows where long titles cause column merging.

**Working parse pattern:**
```python
import re
rows = []
for line in text.split('\n'):
    stripped = line.lstrip()
    if stripped and stripped[0].isdigit():
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) >= 6:  # NOT 7
            num = parts[0]
            org = parts[1].strip() if len(parts) > 1 else ''
            title = parts[2].strip() if len(parts) > 2 else ''
            deadline = parts[3].strip() if len(parts) > 3 else ''
            score = parts[4].strip() if len(parts) > 4 else ''
            vid = parts[5].strip() if len(parts) > 5 else ''
            applied = parts[6].strip() if len(parts) > 6 else 'NO'
            rows.append({'num': num, 'org': org, 'title': title, 
                        'deadline': deadline, 'score': score, 
                        'vid': vid, 'applied': applied})
```

## Rebuild Steps

### Step 1: Backup ALL THREE files — NEVER skip
```bash
DATE=$(date +%Y%m%d)
WORKDIR="~/Downloads/DATA_REPOSITORY/WORKDIR"
mkdir -p "$WORKDIR"
cp .../UN_SECTOR_VACCANCIES.txt "$WORKDIR/UN_VACCANCIES_BACKUP_${DATE}.txt"
cp .../UN_SECTOR_VACCANCIES_IMPACTPOOL.txt "$WORKDIR/UN_VACCANCIES_IMPACTPOOL_BACKUP_${DATE}.txt"
cp .../UN_SECTOR_VACCANCIES_ARCHIVE.txt "$WORKDIR/UN_VACCANCIES_ARCHIVE_BACKUP_${DATE}.txt"
```

### Step 2: Parse existing rows
Use the `re.split(r'\s{2,}', ...)` pattern above with `len(parts) >= 6`.

### Step 3: Check against ALL THREE files for dedup
Before adding any new entry, check its Vacancy ID against active, impactpool, AND archive files. If found in ANY → SKIP.

### Step 4: Add new entries to the list
Append new rows with proper formatting.

### Step 5: Sort by deadline
Nearest first. TBD/Open at bottom. Expired (< today) at very bottom.

### Step 6: Re-number sequentially
1, 2, 3, ... N

### Step 7: Build the complete file
```python
row_lines = []
for r in rows:
    num = str(r['num']).ljust(5)
    org = r['org'][:22].ljust(22)
    title = r['title'][:44].ljust(44)
    deadline = r['deadline'][:12].ljust(12)
    score = r['score'][:8].ljust(8)
    vid = r['vid'][:28].ljust(28)
    applied = r['applied']
    row_lines.append(f"{num}{org}{title}{deadline}{score}{vid}{applied}")

header = '\n'.join(lines[:data_start])
footer = '\n'.join(lines[data_end:])
new_content = header + '\n' + '\n'.join(row_lines) + '\n' + footer
```

### Step 8: Write + sync + verify
```python
Path(path).write_text(new_content)
```
```bash
sync
```
**Verification:**
```python
verify_rows = [l for l in Path(path).read_text().split('\n') 
               if l.lstrip() and l.lstrip()[0].isdigit() 
               and len(re.split(r'\s{2,}', l.strip())) >= 6]
print(f"Expected: {len(rows)}, Found: {len(verify_rows)}")
assert len(verify_rows) == len(f"{len(rows)}"), "ROW MISMATCH — RESTORE FROM BACKUP"
```

**If row count mismatches after write, DO NOT re-parse and re-write.** The issue is usually that the re-split produces different column counts on the written output vs the in-memory list. Restore from backup and investigate.

## Lessons
- **2026-05-19:** Full rebuild missed entries with different formatting. File went from 10→8 entries. Always verify counts.
- **2026-06-06:** `len(parts) >= 7` drops rows with long titles. Changed to `>= 6`. Row count went from expected 68 to parsed 33 until fix applied.
- **2026-06-06:** The score column emoji (`🟠 81`) can merge with adjacent columns during split. Always use `>= 6` not `>= 7`.
