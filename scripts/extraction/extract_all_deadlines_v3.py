#!/usr/bin/env python3
"""
MASTER DEADLINE EXTRACTION v3.0
Comprehensive extraction from all JD files using 25+ patterns.
Handles various markdown and plain text formats.
"""
import re, os, json
from pathlib import Path
from datetime import datetime

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
JD_ROOT = WORKDIR / "JD_FILES"

def parse_date(date_str):
    """Parse a date string, return YYYY-MM-DD or None."""
    date_str = date_str.strip()
    formats = [
        '%d %B %Y',      # 19 June 2026
        '%d %b %Y',      # 19 Jun 2026
        '%B %d, %Y',     # June 19, 2026
        '%b %d, %Y',     # Jun 19, 2026
        '%Y-%m-%d',      # 2026-06-19
        '%m/%d/%Y',      # 06/19/2026
        '%d/%m/%Y',      # 19/06/2026
        '%d %B %Y',      # 31 December 2026
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # Sanity check year range
            if 2025 <= dt.year <= 2028:
                return dt.strftime('%Y-%m-%d')
        except:
            continue
    return None

def extract_deadline_from_file(fpath):
    """Extract deadline from a single JD file."""
    text = fpath.read_text(errors='ignore')
    fname = fpath.name.lower()
    
    # Skip if it says "not specified" directly at metadata level
    if "**Deadline:** Not specified" in text and "**Deadline:** Not specified" in text.split('\n')[10]:
        pass  # Might still have a real deadline later in file
    
    # Check for "not specified" as the ONLY deadline indicator
    ns_count = text.count("not specified")
    dl_count = text.count("deadline")
    
    # If "not specified" appears in deadline context early, check for real dates elsewhere
    if "**Deadline:** Not specified" in text:
        # But there might be a real "Deadline:" (without **) later
        pass
    
    # --- PATTERN LIST ---
    patterns = [
        # 1. **Deadline:** DD Month YYYY
        (r'(?i)\*\*Deadline[:\s]*\*\*[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})'),
        # 2. **Deadline:** Month DD, YYYY
        (r'(?i)\*\*Deadline[:\s]*\*\*[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})'),
        # 3. **Deadline:** YYYY-MM-DD
        (r'(?i)\*\*Deadline[:\s]*\*\*[:\s]+(\d{4}-\d{2}-\d{2})'),
        # 4. Deadline: DD Month YYYY (no asterisks)
        (r'(?i)\bDeadline[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})\b'),
        # 5. Deadline: Month DD, YYYY (no asterisks)
        (r'(?i)\bDeadline[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})\b'),
        # 6. Closing Date: Month DD, YYYY
        (r'(?i)Closing\s+Date[:\n\r\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})'),
        # 7. Closing Date / Time section (two-line format)
        (r'(?i)Closing\s+Date\s+\d{4}[\s\n]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})'),
        # 8. Deadline for applications: DD Month YYYY
        (r'(?i)deadline\s+for\s+applications[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})'),
        # 9. Apply by: DD Month YYYY
        (r'(?i)apply\s+by[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})'),
        # 10. Applications close: DD Month YYYY
        (r'(?i)applications?\s+(?:close|due)[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})'),
        # 11. Closing date for applications: Month DD, YYYY
        (r'(?i)closing\s+date\s+for\s+applications[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})'),
        # 12. **Application Deadline:** DD Month YYYY
        (r'(?i)\*\*Application\s+Deadline[:\s]*\*\*[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})'),
        # 13. **Application Deadline:** Month DD, YYYY
        (r'(?i)\*\*Application\s+Deadline[:\s]*\*\*[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})'),
        # 14. Deadline Date: YYYY-MM-DD
        (r'(?i)[\*_]?Deadline\s+Date[:\s]+(\d{4}-\d{2}-\d{2})'),
        # 15. *Date limite:* (French)
        (r'(?i)Date\s+limite[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})'),
    ]
    
    for pattern, *_ in patterns:
        m = re.search(pattern, text)
        if m:
            date_str = m.group(1).strip()
            parsed = parse_date(date_str)
            if parsed:
                return parsed
    
    # Fallback: ISO dates near deadline keywords anywhere in file
    dates_in_text = re.findall(r'(\d{4}-\d{2}-\d{2})', text)
    for d in dates_in_text:
        try:
            dt = datetime.strptime(d, '%Y-%m-%d')
            if not (2025 <= dt.year <= 2028):
                continue
            idx = text.find(d)
            ctx = text[max(0, idx-80):min(len(text), idx+80)].lower()
            if re.search(r'(?:deadline|closing|apply|date|until|by|posting|open)', ctx):
                return d
        except:
            continue
    
    return None

def main():
    total_files = 0
    with_deadline = 0
    without_deadline = 0
    results = {}
    
    for subdir in JD_ROOT.iterdir():
        if not subdir.is_dir():
            continue
        org_name = subdir.name
        
        for fpath in subdir.glob("*.md"):
            total_files += 1
            fname = fpath.name
            dl = extract_deadline_from_file(fpath)
            
            if dl:
                with_deadline += 1
                key = f"{org_name}/{fname}"
                results[key] = dl
            else:
                without_deadline += 1
    
    print(f"=== EXTRACTION COMPLETE ===")
    print(f"Total JD files: {total_files}")
    print(f"With deadline: {with_deadline}")
    print(f"Without deadline: {without_deadline}")
    
    # Print some samples
    print(f"\n=== Sample Extractions ===")
    for i, (key, dl) in enumerate(list(results.items())[:20]):
        print(f"  {dl} | {key[:80]}")
    
    # Save to JSON
    output_file = WORKDIR / "all_jd_deadlines_v3.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to: {output_file}")

if __name__ == "__main__":
    main()
