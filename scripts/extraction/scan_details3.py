#!/usr/bin/env python3
"""Check UNESCAP Data Analyst + WMO e-recruitment + UNICRI alternative URL."""

import json, time
from pathlib import Path
from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

def show(text, n=50):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:n]:
        print(f"  {l[:150]}")

# 1. UNESCAP - Data Analyst detail + ICT-related roles
print("=" * 60)
print("UNESCAP - Data Analyst + ICT role details")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # Check if there's an ICT committee or digital roles
    page.goto("https://www.unescap.org/jobs", wait_until="networkidle")
    time.sleep(4)
    
    # Get all job links
    jobs_data = page.evaluate("""() => {
        const links = document.querySelectorAll('a[href*="inspira"], a[href*="career"], a[href*="job"], a[href*="vacanc"]');
        return JSON.stringify(Array.from(links).slice(0, 20).map(a => ({
            text: a.innerText.trim().substring(0, 100),
            href: a.getAttribute('href')?.substring(0, 120)
        })).filter(x => x.text.length > 5), null, 2);
    }""")
    print(f"Job links from JS:\n{jobs_data}")

# 2. WMO - try e-recruitment
print("\n" + "=" * 60)
print("WMO - e-recruitment system")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://erecruit.wmo.int/public/", wait_until="networkidle")
    time.sleep(5)
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    show(text, 50)
    
    # Try searching "Digital" or "ICT"  
    try:
        search_input = page.query_selector("input[name='key'], input[id*='key']")
        if search_input:
            print("Search box found, typing 'Digital'...")
            search_input.fill("Digital")
            time.sleep(1)
            # Find search button
            search_btn = page.query_selector("button:has-text('Search'), input[type='submit']")
            if search_btn:
                search_btn.click()
            else:
                page.keyboard.press("Enter")
            time.sleep(5)
            text = page.inner_text("body")
            print(f"\nAfter search: {len(text)} chars")
            show(text, 50)
    except Exception as e:
        print(f"Search error: {e}")
    
    # Try URL-based search
    page.goto("https://erecruit.wmo.int/public/search?key=Digital", wait_until="networkidle")
    time.sleep(5)
    text = page.inner_text("body")
    print(f"\nURL search: {len(text)} chars")
    show(text, 40)
    
    page.goto("https://erecruit.wmo.int/public/search?key=ICT", wait_until="networkidle")
    time.sleep(5)
    text = page.inner_text("body")
    print(f"\nURL search ICT: {len(text)} chars")
    show(text, 40)

# 3. UNICRI - alternative URLs
print("\n" + "=" * 60)
print("UNICRI - alternative URLs")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    for url in [
        "https://unicri.it/vacancies",
        "https://www.unicri.it/vacancies",
        "https://unicri.it/careers",
    ]:
        try:
            page.goto(url, wait_until="networkidle")
            time.sleep(4)
            text = page.inner_text("body")
            print(f"\n{url}: {len(text)} chars")
            show(text, 30)
        except Exception as e:
            print(f"\n{url}: ERROR {e}")

print("\n✅ Done!")