#!/usr/bin/env python3
"""Full ECB scan - navigate from careers page to vacancies."""

import json, sys, time
from pathlib import Path

from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # Navigate to careers page
    page.goto("https://www.ecb.europa.eu/careers/html/index.en.html", wait_until="networkidle")
    time.sleep(4)
    
    # Find and click "Vacancies" or "Discover our vacancies" link
    print("Looking for vacancy links...")
    links = page.query_selector_all("a")
    for a in links:
        text = a.inner_text().strip().lower()
        href = a.get_attribute("href") or ""
        if "vacanc" in text or "vacanc" in href:
            print(f"  Found: '{a.inner_text().strip()}' -> {href}")
    
    # Also try clicking "Discover our vacancies" button
    discover = page.query_selector("a:has-text('Discover our vacancies')") or page.query_selector("a:has-text('Vacancies')")
    if discover:
        print(f"\nClicking '{discover.inner_text().strip()}'...")
        discover.click()
        time.sleep(5)
        
        # Get the new page content
        text = page.inner_text("body")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        print(f"\nPage after click: {len(lines)} lines, {len(text)} chars")
        
        for l in lines[:80]:
            print(f"  {l[:140]}")
        
        # Try to extract job listings
        # Check if we're on a job listing page
        if "vacanc" in text.lower() or "job" in text.lower():
            print(f"\n✅ Found vacancy content!")
            
        # Try to get the page URL
        print(f"\nCurrent URL: {page.url}")
    
    # Try direct ECB job listing URLs
    print("\n--- Trying direct vacancy URLs ---")
    direct_urls = [
        "https://www.ecb.europa.eu/careers/vacancies/html/index.en.html",
        "https://www.ecb.europa.eu/careers/jobs/html/index.en.html",
    ]
    
    for url in direct_urls:
        try:
            page.goto(url, wait_until="networkidle")
            time.sleep(5)
            text = page.inner_text("body")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            print(f"\n{url}: {len(lines)} lines")
            
            has_404 = "404" in text or "not exist" in text.lower()
            if not has_404 and len(text) > 1000:
                print("  ✅ Contains content!")
                for l in lines[:60]:
                    print(f"  {l[:140]}")
                break
            else:
                print("  ❌ 404 or empty")
        except Exception as e:
            print(f"  ERROR: {e}")

# Save all output
outfile = RESULTS_DIR / "ecb_full_results.json"
outfile.write_text(json.dumps({"current_url": page.url if 'page' in dir() else "N/A"}, indent=2))
print(f"\nDone")