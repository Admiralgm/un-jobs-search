# Duplicate Entry Removal — 2-Chunk Pattern

> Based on successful dedup of 5 duplicate vacation entries
> (2026-05-28). The naive approach (remove by position alone)
> fails because entries span 2 chunks in the `====`-split
> representation. This doc captures the correct algorithm.

## The Problem

Each entry in `UN_SECTOR_VACCANCIES.txt` spans **2 chunks** when
the file is split by `=` (80-char separator). This is because the
file format has:

```
================================================================================       ← chunk boundary

🟠 ORANGE — Title Here                           ← chunk N (title-only, color header)

================================================================================       ← chunk boundary
- Title: Title Here                              ← chunk N+1 (data fields)
- VACANCY ID: XXX-12345
...
```

So position 1 in the summary table = chunks [1,2], position 2 = chunks [3,4], etc.

## Algorithm

### Step 1: Parse and Identify Duplicates

```python
import re

text = Path('/path/to/UN_SECTOR_VACCANCIES.txt').read_text()
chunks = text.split('=' * 80)

# Each entry = 2 consecutive non-empty, non-header chunks
# Entry at table position N (1-indexed) = chunks[N*2 - 1, N*2]
# (chunks[0] is the file header block)

# Example: remove positions 1,6,14,22,25
# Keep their duplicates at positions 2,7,15,23,26
to_remove = {1, 6, 14, 22, 25}
keep_at = {2, 7, 15, 23, 26}  # keep these instead

# Convert positions to 0-indexed chunk tuples
# Position N → chunks (2*N - 1, 2*N) in 0-indexed list
remove_chunk_indices = set()
for pos in to_remove:
    remove_chunk_indices.add(2 * pos - 1)  # title-only chunk
    remove_chunk_indices.add(2 * pos)      # data chunk

# Build remaining chunks
remaining = [c for i, c in enumerate(chunks) if i not in remove_chunk_indices]

# Rejoin
new_text = ('=' * 80).join(remaining)
```

### Step 2: Rebuild Summary Table from Remaining Entries

After removing the chunks, parse all remaining entry blocks to
extract fields for the summary table:

```python
# Parse remaining entries
entries = []
for i in range(1, len(remaining) - 1, 2):  # step by 2
    if i + 1 >= len(remaining):
        break
    block = remaining[i + 1]  # data chunk
    if '- Title:' not in block or '- VACANCY ID:' not in block:
        continue  # not an entry block
    title_m = re.search(r'- Title:\s*(.+)', block)
    org_m = re.search(r'- Organization:\s*(.+)', block)
    deadline_m = re.search(r'- Deadline:\s*(\d{4}-\d{2}-\d{2})', block)
    score_m = re.search(r'- SCORE:\s*(\d+)', block)
    vid_m = re.search(r'- VACANCY ID:\s*(\S+)', block)
    # Build entry dict for sorting
    entries.append({...})

# Sort by deadline, build table
entries.sort(key=lambda e: e.get('deadline', '9999-99-99'))
table = '# | Organization | Position Title | Deadline | Score | Vacancy ID\\n'
for i, e in enumerate(entries, 1):
    score = int(e.get('score', 0))
    emoji = '🔴' if score >= 85 else '🟠' if score >= 70 else '🟡' if score >= 55 else '🟢'
    table += f'{i:<5} {e["org"]:<22} {e["title_short"]:<44} {e["deadline"]:<12} {emoji:<2} {e["score"]:<3} {e["vid"]}\\n'
```

### Step 3: Reassemble and Write

```python
# Find header block (chunks before first entry)
header_chunks = []
for c in chunks:
    if '- Title:' in c and '- VACANCY ID:' in c:
        break
    header_chunks.append(c)

# Rebuild: header (with new table) + entry chunks
new_header = ('=' * 80).join(header_chunks)

# Replace old table with new table in the last header chunk
old_header_data = new_header.split('================================================================================')
old_header_data[-1] = '\n\n' + table + '\n\n'
new_final_header = '================================================================================'.join(old_header_data)

# Append entries
new_full = new_final_header + ('=' * 80).join(remaining[1:])

Path(output_path).write_text(new_full)
```

## The 2-Chunk Mapping (CRITICAL)

This mapping is the key insight that is NOT obvious from reading the file:

| Table Row | Position (1-idx) | Chunk 1 (title) | Chunk 2 (data) |
|-----------|------------------|------------------|-----------------|
| 1         | 1                | chunks[1]        | chunks[2]       |
| 2         | 2                | chunks[3]        | chunks[4]       |
| 3         | 3                | chunks[5]        | chunks[6]       |
| ...       | ...              | ...              | ...             |
| N         | N                | chunks[2N-1]     | chunks[2N]      |

Chunk 0 is always the file header (up to and including the old summary
table and the "Total: N active vacancies" line).

## Verification

```python
new_text = Path(output_path).read_text()
# Check: Title count == VACANCY ID count
title_count = len(re.findall(r'- Title:', new_text))
vid_count = len(re.findall(r'- VACANCY ID:', new_text))
assert title_count == vid_count, f"Mismatch: {title_count} titles vs {vid_count} VIDs"

# Check: removed VIDs are gone
for vid in removed_vids:
    assert vid not in new_text, f"VID {vid} still present after removal"

# Check: kept VIDs are present
for vid in kept_vids:
    assert vid in new_text, f"VID {vid} missing after removal"

# Check: 0 APPLIED:YES in main file
applied_count = len(re.findall(r'- APPLIED:\s*YES', new_text))
assert applied_count == 0, f"{applied_count} APPLIED:YES still present"
```

## Pitfalls

- **Removing the wrong chunk:** If you remove chunks[2N-1] but not chunks[2N],
  the file will contain orphaned data fields with no title header. Always
  remove BOTH chunks for each duplicate position.
- **Removing the kept duplicate:** Be precise about which position is the
  "lower" duplicate (to remove) vs the "higher" duplicate (to keep).
  Vacancy IDs in table positions 1,6,14,22,25 were the lower-scored
  duplicates of positions 2,7,15,23,26 in the 2026-05-28 cleanup.
- **Table renumbering:** After removal, positions shift. The summary table
  must be rebuilt with sequential `#` numbering. `enumerate(entries, 1)`
  handles this automatically.
- **Chunk index off-by-one:** Chunk 0 is the header. Entry 1 starts at
  chunks[1,2], not chunks[0,1]. The formula `2*N - 1` and `2*N` for an
  N-entry at position N is correct.
