#!/usr/bin/env python3
"""Check IFAD PeopleSoft job listings and UNFPA ICT detail pages."""

import json, time
from pathlib import Path
from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IFAD - PeopleSoft job search URL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=" * 60)
print("IFAD - PeopleSoft Job Listings")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # The actual job listing URL
    url = "https://job.ifad.org/psc/IFHRPRDE/CAREERS/JOBS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?FOCUS=Applicant"
    page.goto(url, wait_until="networkidle")
    time.sleep(6)
    
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:60]:
        print(f"  {l[:150]}")
    
    # Save
    (RESULTS_DIR / "ifad_peoplesoft.txt").write_text(text)
    
    # Check if there's a "View All Jobs" or search
    links = page.query_selector_all("a, button")
    for el in links:
        t = el.inner_text().strip()
        href = el.get_attribute("href") if hasattr(el, 'get_attribute') else ""
        if t and "job" in t.lower() or "search" in t.lower() or "view" in t.lower():
            print(f"  Element: [{t[:80]}] -> {href}")
    
    # Try clicking "View All Jobs" if visible
    view_all = page.query_selector("a:has-text('View All Jobs')")
    if view_all:
        print("\nClicking 'View All Jobs'...")
        href = view_all.get_attribute("href")
        if href:
            page.goto("https://job.ifad.org" + href, wait_until="networkidle")
            time.sleep(6)
            text2 = page.inner_text("body")
            print(f"\nAfter click: {len(text2)} chars")
            lines2 = [l.strip() for l in text2.split("\n") if l.strip()]
            for l in lines2[:50]:
                print(f"  {l[:150]}")
            (RESULTS_DIR / "ifad_peoplesoft_jobs.txt").write_text(text2)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UNFPA - check ICT-adjacent roles detail
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("UNFPA - ICT-adjacent role details")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # Check the National Consultant Information Management Analyst
    url = "https://www.unfpa.org/jobs/national-consultant-information-management-analyst-addis-ababa-ethiopia"
    page.goto(url, wait_until="networkidle")
    time.sleep(5)
    text = page.inner_text("body")
    print(f"\nInformation Management Analyst: {len(text)} chars")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:40]:
        print(f"  {l[:150]}")
    
    # Get all current jobs list more thoroughly
    page.goto("https://www.unfpa.org/jobs", wait_until="networkidle")
    time.sleep(5)
    
    # Extract all job titles via JS
    jobs_data = page.evaluate("""() => {
        const results = [];
        const items = document.querySelectorAll('[class*="job"], [class*=\"views-row\"], article, .node, tr');
        for (const item of items) {
            const t = item.innerText?.trim();
            if (t && t.length > 20 && t.length < 500) {
                results.push(t.substring(0, 200));
            }
        }
        return JSON.stringify(results.slice(0, 30), null, 2);
    }""")
    print(f"\nJob items extracted:")
    print(jobs_data[:2000])

print("\nDone!")