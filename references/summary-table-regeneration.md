# Summary Table Regeneration — Technique & Pitfalls
# un-jobs-search skill reference
# Created: 2026-05-15

## Problem
The summary table at the top of UN_SECTOR_VACCANCIES.txt must be regenerated after every file write (add/remove/modify entries). The file uses emoji-prefixed color markers (🔴 RED, 🟠 ORANGE, 🟡 YELLOW, 🟢 GREEN) as entry delimiters.

## Failed Approach — Single Regex with DOTALL
```python
# DO NOT USE THIS — only captures 1 entry
entry_blocks = re.findall(
    r'(🔴 RED|🟠 ORANGE|🟡 YELLOW|🟢 GREEN) — ([^\n]+)\n={80}\n(.*?)(?=\n(?:🔴|🟠|🟡|🟢) — |\Z)',
    content, re.DOTALL
)
```
**Why it fails:** The emoji characters in the lookahead cause the regex to match too greedily. Only 1 entry is captured instead of all 35+.

## Working Approach — Two-Step Parse
```python
import re

# Step 1: Find all entry header positions
entry_pattern = re.compile(r'(🔴 RED|🟠 ORANGE|🟡 YELLOW|🟢 GREEN) — ([^\n]+)')
matches = list(entry_pattern.finditer(content))

# Step 2: Extract blocks between consecutive headers
entries = []
for i, m in enumerate(matches):
    color = m.group(1).strip()
    title = m.group(2).strip()
    start = m.end()
    if i + 1 < len(matches):
        block = content[start:matches[i+1].start()]
    else:
        block = content[start:]
    
    # Extract fields from block
    id_match = re.search(r'VACANCY ID:\s*(\S+)', block)
    org_match = re.search(r'Organization:\s*([^\n]+)', block)
    deadline_match = re.search(r'Deadline:\s*([^\n]+)', block)
    score_match = re.search(r'SCORE:\s*(\d+)/100', block)
    
    entries.append({
        'color': color, 'title': title,
        'id': id_match.group(1).strip() if id_match else 'UNKNOWN',
        'org': org_match.group(1).strip() if org_match else 'UNKNOWN',
        'deadline': deadline_match.group(1).strip() if deadline_match else 'TBD',
        'score': int(score_match.group(1)) if score_match else 0,
    })
```

## Sorting Entries
```python
from datetime import datetime

def sort_key(e):
    d = e['deadline']
    if 'TBD' in d or 'verify' in d.lower():
        return (2, '9999-99-99')
    for fmt in ['%Y-%m-%d', '%B %d, %Y', '%b %d, %Y']:
        try:
            return (0, datetime.strptime(d, fmt).strftime('%Y-%m-%d'))
        except:
            pass
    return (1, d)

entries.sort(key=sort_key)
```

## Building the Table
```python
table_lines = [
    "=" * 120,
    "VACANCY SUMMARY TABLE — UN_SECTOR_VACCANCIES.txt",
    f"Generated: {today} | Total Active Entries: {total}",
    "Sorted by: Deadline (nearest first) | Score Color: 🔴 90+ STRONG | 🟠 80-89 COMPETITIVE | 🟡 70-79 STRETCH | 🟢 <70 LOW",
    "=" * 120,
    "",
    f"#    {'Organization':30} {'Position Title':50} {'Deadline':20} {'Score':8} {'Vacancy ID':20}",
    "-" * 120,
]
for i, e in enumerate(entries, 1):
    score_str = f"{'🔴' if e['score'] >= 90 else '🟠' if e['score'] >= 80 else '🟡' if e['score'] >= 70 else '🟢'} {e['score']}"
## Problem
The summary table at the top of UN_SECTOR_VACCANCIES.txt must be regenerated after every file write (add/remove/modify entries). **There is exactly ONE table per file — never duplicate tables.** New vacancies are added as new rows to this single table, not as a second table. The file uses emoji-prefixed color markers (🔴 RED, 🟠 ORANGE, 🟡 YELLOW, 🟢 GREEN) as entry delimiters.

## Finding and Replacing the Single Table
```python
# Find the single summary table block (starts with ===...=== \\n VACANCY SUMMARY TABLE)
# The table extends from the first === separator to the end of the scoring model section
table_start = content.find("=" * 120 + "\\nVACANCY SUMMARY TABLE")
scoring_end = content.find("COLOR CODING:", table_start)
table_end = content.find("\\n", scoring_end) + 1  # end of color coding line

# After the table ends, the REFINED UN SECTOR VACANCIES MASTER LIST begins
# Verify the next content is the REFINED section
rest = content[table_end:].strip()
if rest.startswith("REFINED UN SECTOR VACANCIES"):
    new_content = content[:table_start] + new_table + "\\n\\n\\n" + content[table_end:]
else:
    new_content = new_table + "\\n\\n\\n" + content  # fallback: prepend

path.write_text(new_content)
```

## IMPORTANT — NEVER create a second or third table
The file format now uses a SINGLE table at the top. After replacing, verify:
```python
# Count tables — should be exactly 1
table_count = content.count("VACANCY SUMMARY TABLE")
assert table_count == 1, f"Expected 1 table, found {table_count}"
```
If more than 1 table is found, strip the extras by finding all table occurrences and keeping only the first one.

## Table Format (Wide — 120 char separator)
Use the wide format with 120-char `=` separators:
```
If an entry has `UNKNOWN` org and score 0, it's corrupted. To remove:
```python
# Find the line numbers of the corrupted block
lines = content.splitlines()
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'UNKNOWN' in line and 'Roster' in line:
        start_line = i - 2  # back up to the color header
    if start_line and 'Confidence Level:' in line:
        end_line = i + 1
        break

if start_line and end_line:
    del lines[start_line:end_line]
    new_content = "\n".join(lines)
```
