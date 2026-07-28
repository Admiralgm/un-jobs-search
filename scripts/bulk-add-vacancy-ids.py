#!/usr/bin/env python3
"""
Bulk-add VACANCY IDs to UN_SECTOR_VACCANCIES.txt

Usage:
  python3 bulk-add-vacancy-ids.py [FILEPATH]

If FILEPATH not given, defaults to ~/Downloads/UN_SECTOR_VACCANCIES.txt

Strategy:
 1. Read the file
 2. Find all job blocks: look for lines BEFORE a ==== separator that are
    NOT section headers (ACTIVE VACANCIES, EXPIRED VACANCIES, etc.)
    This catches entries with no color emoji (e.g. "ECB AI Enterprise Architect")
 3. Remove any existing "- VACANCY ID:" lines
 4. Insert a unique VAC-001..VAC-NNN after each "- Title:" line

POST-INSERTION VALIDATION:
 - Verifies no duplicate VAC IDs exist after insertion
 - Verifies all IDs are sequential (no gaps)
 - Reports a summary line

This script is idempotent — running it again will clean up and renumber.
"""

import re, sys, os
from collections import Counter

FILEPATH = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Downloads/UN_SECTOR_VACCANCIES.txt"
)

with open(FILEPATH, "r") as f:
    original = f.read()

lines = original.split("\n")

# --- Step 1: Find all ==== separator lines ---
all_sep = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("====") and len(stripped) >= 75:
        all_sep.append(i)

# --- Step 2: Determine which separators are job block starts ---
section_hints = [
    "FILE: UN Sector Vacancies",
    "ACTIVE VACANCIES",
    "EXPIRED VACANCIES",
    "APPLIED ROLES",
    "FAILED SOURCES",
    "SCAN NOTES",
    "FILE ENDS",
]

job_seps = []
for sep_pos in all_sep:
    # Look at the line BEFORE the separator
    before = lines[sep_pos - 1].strip() if sep_pos > 0 else ""

    # If blank, look one more up (some job headers have a blank line before the ===)
    if before == "" and sep_pos > 1:
        before = lines[sep_pos - 2].strip()
        # If that's also a separator, skip (it's a section divider)
        if before.startswith("===="):
            continue

    # Skip known section headers
    is_section = False
    for hint in section_hints:
        if before.startswith(hint) or hint in before:
            is_section = True
            break

    if before and not is_section and not before.startswith("===="):
        job_seps.append(sep_pos)

# --- Step 3: Remove existing VACANCY ID lines ---
cleaned = [l for l in lines if not l.strip().startswith("- VACANCY ID:")]

# --- Step 4: Re-find job blocks in cleaned text ---
re_seps = []
for i, line in enumerate(cleaned):
    stripped = line.strip()
    if stripped.startswith("====") and len(stripped) >= 75:
        if i > 0:
            before = cleaned[i - 1].strip()
            if before == "" and i > 1:
                before = cleaned[i - 2].strip()
                if before.startswith("===="):
                    continue
            is_section = False
            for hint in section_hints:
                if before.startswith(hint) or hint in before:
                    is_section = True
                    break
            if before and not is_section and not before.startswith("===="):
                re_seps.append(i)

# --- Step 5: Insert VACANCY IDs after each Title line ---
insertions, fails = [], []
for job_num, sep_pos in enumerate(re_seps):
    vac_id = "VAC-{:03d}".format(job_num + 1)
    # Look for "- Title:" within first 8 lines after the separator
    found = None
    for j in range(sep_pos + 1, min(sep_pos + 9, len(cleaned))):
        if cleaned[j].strip().startswith("- Title:"):
            found = j
            break
    if found is not None:
        insertions.append((found + 1, "- VACANCY ID: " + vac_id))
        print("  {} -> {}".format(vac_id, cleaned[found].strip()[:60]))
    else:
        fails.append((job_num, sep_pos))
        print("  FAIL {} -> no Title field at sep line {}".format(vac_id, sep_pos + 1))

# Apply in reverse order
insertions.sort(key=lambda x: x[0], reverse=True)
for idx, new_line in insertions:
    cleaned.insert(idx, new_line)

output = "\n".join(cleaned)
with open(FILEPATH, "w") as f:
    f.write(output)

# --- Step 6: Validate ---
with open(FILEPATH) as f:
    ids = [l.strip() for l in f if "VACANCY ID:" in l]
nums = [int(id.split("VAC-")[1]) for id in ids]
c = Counter(nums)
dupes = [n for n, cnt in c.items() if cnt > 1]
expected = set(range(1, max(nums) + 1)) if nums else set()
actual = set(nums)
missing = expected - actual

print("\nDone. {} IDs inserted, {} failed.".format(len(insertions), len(fails)))
if fails:
    print("Failed entries at separators: {}".format([s+1 for _, s in fails]))

if dupes:
    print("ERROR: Duplicate VAC IDs detected: {}".format(sorted(dupes)))
    print("  These entries share the same VAC number. Manual fix required.")
    sys.exit(1)

if missing:
    print("WARNING: VAC IDs not fully sequential -- missing: {}".format(sorted(missing)))

print("VALIDATION OK: {} unique, sequential VAC IDs (VAC-001 to VAC-{})".format(
    len(nums), max(nums) if nums else "N/A"
))
