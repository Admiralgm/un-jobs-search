#!/usr/bin/env python3
"""Robust deadline extraction: fuzzy match JD files to tracker rows, then scrape the rest online."""
import re, os, json
from pathlib import Path
from datetime import datetime

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
TRACKER = WORKDIR / "UN-VACANCIES-TRACKER.txt"
JD_ROOT = WORKDIR / "JD_FILES"

# Read all JD file content and build a searchable index
print("Building JD file index...")
jd_index = []
for subdir in JD_ROOT.iterdir():
    if not subdir.is_dir():
        continue
    for fpath in sorted(subdir.glob("*.md")):
        try:
            text = fpath.read_text(errors='ignore')
            # Extract org from subdir
            org_raw = subdir.name
            org_short = org_raw.replace("UN_", "").replace("UN", "")
            
            # Try to extract title from first line or metadata
            title = ""
            for line in text.split('\n')[:10]:
                line_s = line.strip()
                if line_s and not line_s.startswith('#') and not line_s.startswith('---'):
                    title = line_s
                    break
            
            # Try to extract deadline via multiple patterns
            deadline = None
            raw_date = ""
            
            # Pattern list: (regex, output_format)
            pat_list = [
                (r'(?i)closing\s+date[:\s\n]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', '%B %d, %Y'),
                (r'(?i)closing\s+date[:\s\n]+(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
                (r'(?i)closing\s+date[:\s\n]+([\d]{1,2}/[\d]{1,2}/[\d]{4})', '%m/%d/%Y'),
                (r'(?i)deadline[:\s\n]+([\d]{1,2}\s+[A-Za-z]+\s+\d{4})', '%d %B %Y'),
                (r'(?i)deadline[:\s]+([\d]{1,2}\s+[A-Za-z]{3}\s+\d{4})', '%d %b %Y'),
                (r'(?i)deadline[:\s]+([\d]{1,2}[/-][A-Za-z]{3}[/-]\d{4})', '%d-%b-%Y'),
                (r'(?i)apply\s+before[:\s\n]+([\d]{2}/[\d]{2}/[\d]{4})', '%m/%d/%Y'),
                (r'(?i)apply\s+before[:\s\n]+([\d]{1,2}/\d{1,2}/\d{4})', '%m/%d/%Y'),
                (r'(?i)removal\s+date[:\s\n]+([\d]{1,2}/[\d]{1,2}/[\d]{4})', '%m/%d/%Y'),
                (r'(?i)auto[-\s]?close\s*[:\n\s]+(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
                (r'(?i)auto[-\s]?close\s+date[:\n\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', '%B %d, %Y'),
            ]
            
            # Search first 8KB for deadline
            search_text = text[:8000] + text[-2000:] if len(text) > 8000 else text
            for pat, fmt in pat_list:
                m = re.search(pat, search_text)
                if m:
                    date_str = m.group(1).strip()
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        # Sanity check: year between 2025-2028
                        if 2025 <= dt.year <= 2028:
                            deadline = dt.strftime('%Y-%m-%d')
                            raw_date = date_str
                            break
                    except ValueError:
                        pass
            
            # Try text extraction for "extended deadline: ..." patterns
            if not deadline:
                m2 = re.search(r'(?i)(?:extended|final)\s+deadline[:\s]+([\d]{1,2}[/-][\d]{1,2}[/-]\d{2,4})', text)
                if m2:
                    ds = m2.group(1)
                    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%y'):
                        try:
                            dt = datetime.strptime(ds, fmt)
                            if 2025 <= dt.year <= 2028:
                                deadline = dt.strftime('%Y-%m-%d')
                                raw_date = ds
                                break
                        except ValueError:
                            pass
            
            # Also try INSPIRA pattern: "Deadline for Applications: DD Month YYYY"
            if not deadline:
                m = re.search(r'(?i)deadline\s+for\s+applications[:\s]+([\d]{1,2}\s+[A-Za-z]+\s+\d{4})', text)
                if m:
                    ds = m.group(1)
                    try:
                        dt = datetime.strptime(ds, '%d %B %Y')
                        deadline = dt.strftime('%Y-%m-%d')
                        raw_date = ds
                    except ValueError:
                        try:
                            dt = datetime.strptime(ds, '%d %b %Y')
                            deadline = dt.strftime('%Y-%m-%d')
                            raw_date = ds
                        except ValueError:
                            pass
            
            jd_index.append({
                "path": str(fpath),
                "fname": fpath.name,
                "org_dir": org_raw,
                "org_short": org_short,
                "title": title,
                "deadline": deadline,
                "raw_date": raw_date,
                "text_len": len(text)
            })
        except Exception as e:
            pass

print(f"Indexed {len(jd_index)} JD files")
jd_with_dl = [j for j in jd_index if j["deadline"]]
print(f"JD files with extractable deadlines: {len(jd_with_dl)}")

# Parse tracker
with open(TRACKER) as f:
    lines = f.readlines()

vacancies = []
for line in lines:
    stripped = line.rstrip()
    num_part = stripped[:5].strip()
    if not num_part.isdigit():
        continue
    row_num = int(num_part)
    end_match = re.search(r'(\S+)\s+(NO|YES)\s*$', stripped)
    vid = end_match.group(1) if end_match else ""
    applied = end_match.group(2) if end_match else "NO"
    
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', stripped)
    if date_match:
        deadline = date_match.group(1)
    else:
        deadline = "TBD"
    
    org = stripped[5:27].strip()
    title = stripped[27:71].strip()
    # Extract score for sorting later
    score_match = re.search(r'([🔴🟠🟡🟢])\s*(\d+)', stripped)
    score = int(score_match.group(2)) if score_match else 0
    
    vacancies.append({
        "row": row_num, "org": org, "title": title, "deadline": deadline,
        "vid": vid, "applied": applied, "score": score
    })

print(f"\nTracker vacancies: {len(vacancies)}")
print(f"Already with dates: {sum(1 for v in vacancies if v['deadline'] != 'TBD')}")

# Multi-pass matching
matched = 0

# Pass 1: exact VID match
for vac in vacancies:
    if vac["deadline"] != "TBD":
        continue
    vid = vac["vid"]
    if vid and vid != "**":
        for jd in jd_index:
            if jd["deadline"] and vid in jd["fname"]:
                vac["deadline"] = jd["deadline"]
                vac["source"] = "VID_MATCH"
                matched += 1
                break

# Pass 2: org + title fuzzy matching
import difflib
def normalize(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

for vac in vacancies:
    if vac["deadline"] != "TBD":
        continue
    vac_org_norm = normalize(vac["org"])
    vac_title_norm = normalize(vac["title"])
    best = None
    best_score = 0
    for jd in jd_index:
        if not jd["deadline"]:
            continue
        # Org match
        jd_org_norm = normalize(jd["org_short"])
        org_match = False
        if vac_org_norm and (vac_org_norm in jd_org_norm or jd_org_norm in vac_org_norm):
            org_match = True
        
        # Also map known aliases
        org_aliases = {
            "unsecretariat": ["inspira","careersun"],
            "unicef" : ["unicef","dp"],
            "who": ["who"],
            "itu": ["itu"],
            "worldbank": ["worldbank","worl"],
            "unops": ["unops","ops"],
            "undp": ["undp"],
            "unfpa": ["unfpa","fpa"],
            "unido": ["unido","ido"],
            "wfp": ["wfp"],
            "who": ["who"],
            "icrc": ["icrc","139"],
            "icao": ["icao"],
            "ilo": ["ilo"],
            "wipo": ["wipo"],
            "imf": ["imf"],
            "ecb": ["ecb"],
            "oecd": ["oecd"],
            "fao": ["fao"],
            "unesco": ["unesco"],
            "unitar": ["unitar"],
            "imu": ["imu"],
            "unu": ["unu"],
        }
        for key, aliases in org_aliases.items():
            if key in vac_org_norm or vac_org_norm in key:
                for a in aliases:
                    if a in jd_org_norm:
                        org_match = True
                        break
        
        if not org_match:
            continue
        
        # Title fuzzy match using filename + title from file
        jd_title_norm = normalize(jd["fname"].split('.')[0])
        # Calculate similarity
        sm = difflib.SequenceMatcher(None, vac_title_norm[:40], jd_title_norm[:80])
        ratio = sm.ratio()
        # Also check word overlap
        v_words = set(w for w in normalize(vac["title"]).replace('amp','') if len(w) > 3)
        j_words = set(w for w in jd_title_norm.replace('amp','') if len(w) > 3)
        overlap = len(v_words & j_words) / max(1, len(v_words))
        combined_score = ratio * 0.5 + overlap * 0.5
        
        if combined_score > best_score:
            best_score = combined_score
            best = jd
    
    if best and best_score >= 0.15:  # lowered threshold
        vac["deadline"] = best["deadline"]
        vac["source"] = f"FUZZY({best_score:.2f})"
        matched += 1
        # Mark JD as used
        best["used"] = True

print(f"Total matched after fuzzy: {matched}")
print(f"Still TBD: {sum(1 for v in vacancies if v['deadline'] == 'TBD')}")

# Count by org for remaining TBD
from collections import Counter
remaining = [v for v in vacancies if v['deadline'] == 'TBD']
org_counts = Counter(v['org'] for v in remaining)
print("\nRemaining TBD by organization:")
for org, cnt in org_counts.most_common(30):
    print(f"  {org}: {cnt}")

# Save intermediate
out = {
    "vacancies": [{"row": v["row"], "org": v["org"], "title": v["title"], "deadline": v["deadline"],
                   "vid": v["vid"], "score": v["score"], "applied": v["applied"]} for v in vacancies],
    "remaining_by_org": dict(org_counts.most_common()),
}
with open(WORKDIR / "deadline_extraction_intermediate.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {WORKDIR / 'deadline_extraction_intermediate.json'}")

# Print first 20 still TBD with enough detail for manual lookup
print("\n--- FIRST 20 STILL TBD (need online scraping) ---")
for v in remaining[:20]:
    print(f"#{v['row']} | {v['org']} | {v['title'][:55]} | VID={v['vid']}")
