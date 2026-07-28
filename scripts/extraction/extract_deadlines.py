#!/usr/bin/env python3
"""
Deep deadline extraction from ALL JD files.
Scans body text with portal-specific patterns for each format.
"""
import re, json
from pathlib import Path
from datetime import datetime

JD_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")

PARSE_FMTS = [
    '%Y-%m-%d', '%B %d, %Y', '%B %d %Y', '%b %d, %Y', '%b %d %Y',
    '%d %B %Y', '%d %b %Y', '%m/%d/%Y', '%d/%m/%Y',
]

def parse_date(s):
    s = s.strip().rstrip('.,;')
    for fmt in PARSE_FMTS:
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except: pass
    return None

PATTERNS = [
    # WHO/FAO/IAEA: "Closing Date\nJun 4, 2026, 11:59:00 PM" (multi-line Taleo)
    (r'Closing Date\s*[:\n]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})', 1),
    (r'Deadline\s*[:\n]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})', 1),
    
    # "deadline: YYYY-MM-DD"
    (r'(?:deadline|closing date|apply before|application deadline)[:\s]*(\d{4}-\d{2}-\d{2})', 1),
    
    # UNDP: "Apply Before: 06/10/2026, 05:59 AM"
    (r'(?:Apply Before|Closing Date|Deadline)[:\s]*(\d{1,2}/\d{1,2}/\d{4})', 1),
    
    # INSPIRA/TJO: "Deadline for Applications: 21 June 2026"
    (r'(?:Deadline for Applications|Deadline)[:\s]*(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})', 1),
    
    # Generic "June 1, 2026" / "01 June 2026" near deadline/closing
    (r'(?:deadline|closing|apply|closes)[^.]{0,100}((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})', 1),
    
    # IMF: "Removal Date: 06/01/2026"
    (r'(?:Removal Date|End Date|Closing Date)[:\s]*(\d{1,2}/\d{1,2}/\d{4})', 1),
    
    # UNOPS: "Deadline: 15-Jun-2026"
    (r'(?:Deadline|Closing)[:\s]*(\d{1,2}[-/]\w{3}[-/]\d{4})', 1),
    
    # Workday/ICs: "End Date: 2026-06-15"  
    (r'(?:End Date|Job Posting End)[:\s]*(\d{4}-\d{2}-\d{2})', 1),
    
    # ITU-specific: look deep in the body text for dates near "deadline"
    (r'(?:This vacancy|Applications?)[^.]{0,100}(?:deadline|close|by\s+)[^.]{0,80}((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})', 1),
]

def extract_all(filepath):
    content = Path(filepath).read_text(encoding='utf-8', errors='replace')
    results = set()
    
    for pat, grp in PATTERNS:
        for m in re.finditer(pat, content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
            raw = m.group(grp).strip()
            parsed = parse_date(raw)
            if parsed:
                results.add(parsed)
    
    # Also look for any YYYY-MM-DD in first 50 lines (metadata block)
    first_part = '\n'.join(content.split('\n')[:50])
    for m in re.finditer(r'(\d{4}-\d{2}-\d{2})', first_part):
        results.add(m.group(1))
    
    return sorted(results) if results else ["TBD"]

results = {}

for agency_dir in sorted(JD_DIR.iterdir()):
    if not agency_dir.is_dir():
        continue
    for jf in sorted(agency_dir.glob("*.md")):
        dates = extract_all(jf)
        results[jf.name] = dates

# Print key findings where TBD was found but we found dates
for fname, dates in sorted(results.items()):
    if dates != ["TBD"]:
        print(f"{fname[:50]:50s} → {dates}")
    else:
        # Just count TBDs
        pass

print("\n=== TBD FILES ===")
tbds = [f for f, d in results.items() if d == ["TBD"]]
print(f"Total TBD: {len(tbds)}")
for f in tbds:
    print(f"  {f}")

# Write results to JSON for the rebuild script
Path("/tmp/deadline_map.json").write_text(json.dumps(results, indent=2), encoding='utf-8')
print(f"\nDeadline map saved. {len(results)} files processed, {len(tbds)} still TBD")