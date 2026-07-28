#!/usr/bin/env python3
"""Retry ECB - find correct career URL."""

import json, sys, time
from pathlib import Path

from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

urls_to_try = [
    "https://www.ecb.europa.eu/careers/what-we-offer/current-vacancies/html/index.en.html",
    "https://www.ecb.europa.eu/careers/html/index.en.html",
    "https://www.ecb.europa.eu/home/html/careers.en.html",
    "https://www.ecb.europa.eu/careers",
]

results = {}

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    for url in urls_to_try:
        try:
            print(f"\n--- Trying: {url}")
            page.goto(url, wait_until="networkidle")
            time.sleep(5)
            text = page.inner_text("body")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            print(f"  Lines: {len(lines)}, text length: {len(text)}")
            
            # Show first 30 non-empty lines
            for l in lines[:30]:
                print(f"  {l[:120]}")
            
            results[url] = {
                "status": "loaded",
                "lines": len(lines),
                "text_len": len(text),
                "preview": lines[:20],
                "has_404": "404" in text or "not exist" in text.lower() or "page does not exist" in text.lower(),
            }
            
            if not results[url]["has_404"] and len(text) > 500:
                print(f"  ✅ THIS ONE LOOKS GOOD!")
                break
                
        except Exception as e:
            print(f"  ERROR: {e}")
            results[url] = {"status": "failed", "error": str(e)}

outfile = RESULTS_DIR / "ecb_retry.json"
outfile.write_text(json.dumps(results, indent=2, default=str))
print(f"\nSaved to {outfile}")