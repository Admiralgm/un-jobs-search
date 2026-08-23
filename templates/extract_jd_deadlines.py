#!/usr/bin/env python3
"""Extract all vacancy IDs + metadata from tracker, then search JD files for deadlines."""
import re, os, glob
from pathlib import Path
from datetime import datetime

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
TRACKER = WORKDIR / "UN-VACANCIES-TRACKER.txt"
JD_ROOT = WORKDIR / "JD_FILES"

# Parse tracker
with open(TRACKER) as f:
    lines = f.readlines()

vacancies = []
for i, line in enumerate(lines):
    stripped = line.rstrip()
    num_part = stripped[:5].strip()
    if not num_part.isdigit():
        continue
    row_num = int(num_part)
    # Find the applied flag at the end
    end_match = re.search(r'(\S+)\s+(NO|YES)\s*$', stripped)
    vid = end_match.group(1) if end_match else ""
    applied = end_match.group(2) if end_match else "NO"
    
    # Extract deadline: look for YYYY-MM-DD or "TBD" or "Open (Roster)"
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', stripped)
    if date_match:
        deadline = date_match.group(1)
    elif "TBD" in stripped:
        deadline = "TBD"
    elif "Open (Roster)" in stripped or "Roster" in stripped:
        deadline = "Open (Roster)"
    else:
        deadline = "TBD"
    
    # Org: chars 5-27 (22 chars)
    org = stripped[5:27].strip()
    # Title: chars 27-71 (44 chars)
    title = stripped[27:71].strip()
    
    vacancies.append({
        "row": row_num, "org": org, "title": title, "deadline": deadline,
        "vid": vid, "applied": applied, "raw": stripped
    })

print(f"Total parsed vacancies: {len(vacancies)}")
print(f"With actual dates: {sum(1 for v in vacancies if v['deadline'] not in ('TBD','Open (Roster)') and v['deadline'] != 'TBD')}")
print(f"TBD: {sum(1 for v in vacancies if v['deadline'] == 'TBD')}")

# Now search JD files for each vacancy
# Build a map: org -> list of jd file paths
jd_files = {}
for subdir in JD_ROOT.iterdir():
    if subdir.is_dir():
        org_name = subdir.name.replace("UN_", "").replace("UN", "")
        files = list(subdir.glob("*.md"))
        jd_files[subdir.name] = files
        
print(f"\nJD file directories: {len(jd_files)}")

# Search each JD file for deadline patterns
deadline_patterns = [
    r'deadline.*?[:\s]+([\d]{1,2}\s+[A-Za-z]+\s+\d{4})',
    r'closing\s*date.*?[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
    r'apply\s*before.*?[:\s]+([\d]{1,2}[/-][\d]{1,2}[/-]\d{4})',
    r'removal\s*date.*?[:\s]+([\d]{1,2}[/-][\d]{1,2}[/-]\d{4})',
    r'application\s*deadline.*?[:\s]+([\d]{1,2}\s+[A-Za-z]+\s+\d{4})',
    r'Closing\s*Date[:\s]*([A-Za-z]+\s+[\d]{1,2},\s+\d{4})',
    r'Apply\s*before[:\s]*([\d]{2}/[\d]{2}/[\d]{4})',
    r'autoclose\s*date.*?[:\s]+(\d{4}-\d{2}-\d{2})',
]

found_deadlines = {}
for org, files in jd_files.items():
    for fpath in files:
        try:
            text = fpath.read_text(errors='ignore')[:15000]
            for pat in deadline_patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    date_str = m.group(1).strip()
                    # Normalize to YYYY-MM-DD
                    for fmt in ("%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y", 
                                "%m/%d/%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            iso = dt.strftime("%Y-%m-%d")
                            found_deadlines[fpath.name] = iso
                            break
                        except ValueError:
                            continue
                    if fpath.name in found_deadlines:
                        break
        except Exception as e:
            pass

print(f"\nDeadlines found in JD files: {len(found_deadlines)}")
for name, dl in list(found_deadlines.items())[:20]:
    print(f"  {name}: {dl}")
