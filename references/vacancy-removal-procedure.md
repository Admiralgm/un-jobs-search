# Vacancy Removal Procedure

When the user directs you to remove specific vacancies from the tracker (e.g., unverified, expired, or user-rejected entries), use this procedure. It avoids the "over-removal" pitfall where matching on `====` delimiters removes adjacent entries.

## Step-by-Step

### 1. Parse: Split by Entry Blocks

Split the file into entry blocks using `====` as the delimiter. Each block spans from one `====` line to the next `====` line. The first block is the header (summary table area).

```python
with open('/path/to/UN_SECTOR_VACCANCIES.txt') as f:
    text = f.read()

# Split into blocks delimited by ====
blocks = re.split(r'(?=^={5,})', text, flags=re.MULTILINE)
```

### 2. Classify Each Block

For each block, determine if it's a vacancy entry block (contains `- Title:` and `- VACANCY ID:`) and check if the ID matches a target for removal.

```python
target_ids = {"592902", "592948", ...}  # IDs to remove
kept_blocks = []

for block in blocks:
    # Check if this block is an entry with a target ID
    if '- VACANCY ID:' in block:
        vid_match = re.search(r'- VACANCY ID:\s*(\S+)', block)
        if vid_match and vid_match.group(1) in target_ids:
            print(f"REMOVING: {vid_match.group(1)}")
            continue  # Skip this block
    kept_blocks.append(block)
```

### 3. Rebuild from Kept Blocks

Join the kept blocks back together.

```python
new_text = ''.join(kept_blocks)
```

### 4. Clean Summary Table

Remove summary table rows that reference the removed vacancy IDs.

```python
for vid in target_ids:
    new_text = re.sub(
        r'^\s*\d+\s+UNICEF\s+.*?' + re.escape(vid) + r'.*$',
        '',
        new_text,
        flags=re.MULTILINE
    )
```

### 5. Renumber Summary Table

Find the summary table section and renumber all remaining rows sequentially.

```python
lines = new_text.split('\n')
# Find table boundaries
table_start = None
for i, line in enumerate(lines):
    if 'VACANCY SUMMARY TABLE' in line:
        table_start = i
        break

# Collect data rows (lines starting with a number)
data_rows = []
for i in range(table_start, len(lines)):
    stripped = lines[i].strip()
    if re.match(r'^\d+\s', stripped) and '--' not in stripped:
        # Remove old number, rebuild with correct one
        cleaned = re.sub(r'^\s*\d+\s+', '', stripped)
        data_rows.append(cleaned)

# Replace old numbered rows with new sequential ones
```

### 6. Write & Verify

```python
new_text = '\n'.join(new_lines)
new_text = re.sub(r'\n{4,}', '\n\n\n', new_text)  # Remove excess blank lines

with open('/path/to/UN_SECTOR_VACCANCIES.txt', 'w') as f:
    f.write(new_text)

# Verify: run sync, check no target IDs remain, check entry count
```

## Real Example (29 May 2026)

Removed 10 UNICEF TBD entries (592902, 592948, 593037, 593033, 593140, 593154, 593155, 592874, 592891, 592958) that showed "job not found" on the live UNICEF portal:

- Source file: 125KB / 2841 lines
- After removal: 114KB / 2514 lines
- 10 entry blocks removed (each ~1KB including analysis text)
- Summary table renumbered from 76 → 66 rows
- Backup saved as `.backup` before any writes

## Key Lessons

1. **Split on `====` not `\n`** — each entry block is self-contained between `====` separators
2. **Never match on `====` alone** — it appears at both start AND end of each block. Match on VACANCY ID inside the block
3. **Check for duplicate title lines** — the tracker file lists each title twice (once as standalone, once with fields). Removing by VACANCY ID handles both
4. **Renumber summary AFTER removal** — never try to preserve old numbers. Just rebuild
5. **Backup always** — use `.backup` suffix before destructive writes
6. **Verify with grep** after: `grep -c 'VACANCY ID:'` should match summary row count
