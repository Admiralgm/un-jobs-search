#!/usr/bin/env python3
"""Quick WMO job listings + UNESCAP Data Analyst check."""

import time
from pathlib import Path
from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

def show(text, n=50):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:n]:
        print(f"  {l[:150]}")
    return len(lines)

# WMO - try clicking "read more" or finding job list
print("=" * 60)
print("WMO - actual job listings")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://erecruit.wmo.int/public/", wait_until="networkidle")
    time.sleep(6)
    
    # Check if there's a search/results section
    text = page.inner_text("body")
    print(f"{len(text)} chars")
    show(text, 60)
    
    # Look for the e-recruitment system link
    links = page.query_selector_all("a")
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if "search" in href.lower() or "vacanc" in href.lower() or "open" in t.lower() or "current" in t.lower():
            print(f"  LINK: [{t[:80]}] -> {href[:100]}")
    
    # Try direct search URLs
    for search_url in [
        "https://erecruit.wmo.int/public/search",
        "https://erecruit.wmo.int/public/search?key=",
    ]:
        print(f"\nTrying: {search_url}")
        page.goto(search_url, wait_until="networkidle")
        time.sleep(5)
        text2 = page.inner_text("body")
        print(f"{len(text2)} chars")
        show(text2, 40)

# UNESCAP Data Analyst - from the data already obtained, I know:
# "Data Analyst, Individual Contractor, Statistics Division, Bangkok"
print("\n" + "=" * 60)
print("UNESCAP Data Analyst assessment (from scan data)")
print("=" * 60)
print("""
Role:   Data Analyst
Grade:  Individual Contractor (not P-level)
Div:    Statistics Division
Loc:    Bangkok, Thailand
Deadline: 15 June 2026
Link:  via inspira.un.org

Assessment: Individual Contractor ≠ P-3+ international staff.
It's a short-term consultancy for data processing.
=> NOT at target grade. Exclude.
""")

# Check tracker for any UNESCAP entries
print("=" * 60)
print("Checking tracker for UNESCAP/WMO entries")
print("=" * 60)
tracker = Path("~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt")
if tracker.exists():
    content = tracker.read_text()
    for term in ["ESCAP", "WMO", "GICHD", "UNDRR", "UNICRI", "IFAD"]:
        matches = [l for l in content.split("\n") if term in l or term.lower() in l.lower()]
        if matches:
            for m in matches:
                print(f"  {term} -> {m[:120]}")
        else:
            print(f"  {term} -> not tracked")

print("\n✅ Done")