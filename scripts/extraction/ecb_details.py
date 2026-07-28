#!/usr/bin/env python3
"""Get ECB page 2 + detail pages for ICT-adjacent roles."""

import json, sys, time
from pathlib import Path

from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

# Jobs to investigate from page 1
ict_adjacent = [
    # (url part, title)
    ("Market-Infrastructure-Experts-off", "Market Infrastructure Experts (offline technology) - Digital Euro"),
    ("Market-Infrastructure-Project-Man", "Market Infrastructure Project Management Specialists - Digital Euro"),
    ("Information-Management-Specialist", "Information Management Specialist (Librarian)"),
]

results = {"page2": {}, "details": []}

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # 1. Get page 2
    print("=== Page 2 ===")
    page.goto("https://talent.ecb.europa.eu/careers/SearchJobs/?jobRecordsPerPage=10&jobOffset=10", wait_until="networkidle")
    time.sleep(5)
    text = page.inner_text("body")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    print(f"Lines: {len(lines)}")
    for l in lines[:50]:
        print(f"  {l[:150]}")
    results["page2"]["text"] = text[:3000]
    
    # 2. Get detail pages for ICT-adjacent roles
    base_url = "https://talent.ecb.europa.eu/careers/JobDetail/"
    
    for url_part, title in ict_adjacent:
        print(f"\n=== {title} ===")
        full_url = base_url + url_part
        page.goto(full_url, wait_until="networkidle")
        time.sleep(4)
        text = page.inner_text("body")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        print(f"Lines: {len(lines)}, chars: {len(text)}")
        for l in lines[:60]:
            print(f"  {l[:150]}")
        results["details"].append({
            "title": title,
            "url": full_url,
            "text": text[:5000],
        })

outfile = RESULTS_DIR / "ecb_details.json"
outfile.write_text(json.dumps(results, indent=2, default=str))
print(f"\nSaved to {outfile}")