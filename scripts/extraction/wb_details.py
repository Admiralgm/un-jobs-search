#!/usr/bin/env python3
"""Get World Bank CSOD detail pages for AI roles + ICMPD scoring."""

import json, time, re
from pathlib import Path

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")
TRACKER_DIR = Path("~/Downloads/DATA_REPOSITORY")

from camoufox import Camoufox

# Check what's already in tracker
tracker = TRACKER_DIR / "UN_SECTOR_VACCANCIES.txt"
archive = TRACKER_DIR / "UN_SECTOR_VACCANCIES_ARCHIVE.txt"
impactpool = TRACKER_DIR / "UN_SECTOR_VACCANCIES_IMPACTPOOL.txt"

tracked_ids = set()
for f in [tracker, archive, impactpool]:
    if f.exists():
        content = f.read_text()
        # Extract Vacancy IDs
        ids = re.findall(r'^\d+\s+\S+.*?\s+([\w-]+(?:/[\w-]+)?)\s+(?:NO|YES)', content, re.MULTILINE)
        for i in ids:
            tracked_ids.add(i.strip())

print(f"Tracked vacancy IDs: {len(tracked_ids)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. World Bank AI roles detail pages
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("World Bank - AI Roles Details")
print("=" * 60)

wb_roles = [
    ("AI Solutions Analyst", "/ux/ats/careersite/1/home/requisition/36831?c=worldbankgroup", "36831"),
    ("AI Service Mgmt Transformation Lead", "/ux/ats/careersite/1/home/requisition/36827?c=worldbankgroup", "36827"),
    ("AI Incident & Problem Mgmt Lead", "/ux/ats/careersite/1/home/requisition/36825?c=worldbankgroup", "36825"),
    ("Senior GenAI Engineering Practitioner", "/ux/ats/careersite/1/home/requisition/36819?c=worldbankgroup", "36819"),
    ("Database Administrator (E T Consultant)", "/ux/ats/careersite/1/home/requisition/36677?c=worldbankgroup", "36677"),
]

wb_results = []

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    base_url = "https://worldbankgroup.csod.com"
    
    for title, path, req_id in wb_roles:
        full_url = base_url + path
        print(f"\n--- {title} ({req_id}) ---")
        
        page.goto(full_url, wait_until="networkidle")
        time.sleep(6)
        text = page.inner_text("body")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        print(f"  {len(text)} chars, {len(lines)} lines")
        
        # Extract key fields
        for l in lines[:60]:
            print(f"  {l[:150]}")
        
        wb_results.append({
            "title": title,
            "req_id": req_id,
            "text": text[:6000],
            "lines": lines[:40],
        })

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Check tracker for existing WB entries
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("Checking tracker for any World Bank entries")
print("=" * 60)

# Read tracker summary table
tracker_text = tracker.read_text()
# Find all lines that mention World Bank or WB or worldbank
wb_tracker_lines = [l for l in tracker_text.split("\n") if "World" in l or "worldbank" in l.lower() or "WB" in l]
for l in wb_tracker_lines:
    print(f"  {l[:120]}")

print(f"\nNumber of existing WB entries in tracker: {len(wb_tracker_lines)}")

outfile = RESULTS_DIR / "worldbank_ai_details.json"
outfile.write_text(json.dumps(wb_results, indent=2, default=str))
print(f"\nSaved -> {outfile}")
print("\nDone!")