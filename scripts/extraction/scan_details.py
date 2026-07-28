#!/usr/bin/env python3
"""Get ICMPD HR IS details + UNU careers main portal + CSOD via Scrapling."""

import json, sys, time, re
from pathlib import Path
from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")
TRACKER_DIR = Path("~/Downloads/DATA_REPOSITORY")

def show_text(text, max_lines=60):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:max_lines]:
        print(f"  {l[:150]}")
    return len(lines)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. ICMPD — HR IS & Automation Officer detail
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=" * 60)
print("ICMPD — HR IS & Automation Officer IP3 Vienna")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # Navigate to the specific job
    page.goto("https://careers.icmpd.org/", wait_until="networkidle")
    time.sleep(5)
    
    # Find the link for VA26P112V01
    links = page.query_selector_all("a")
    target_link = None
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if "VA26P112V01" in href or "HR Information Systems" in t:
            target_link = a
            print(f"Found link: {t} -> {href}")
            break
        if "HR Information" in href or "VA26P112" in href or "p112" in href.lower():
            target_link = a
            print(f"Found by href: {t} -> {href}")
            break
    
    if target_link:
        href = target_link.get_attribute("href") or ""
        full_url = href if href.startswith("http") else "https://careers.icmpd.org" + href
        print(f"\nNavigating to: {full_url}")
        page.goto(full_url, wait_until="networkidle")
        time.sleep(5)
        text = page.inner_text("body")
        print(f"\nDetail page ({len(text)} chars):")
        show_text(text, 80)
        
        # Save detail
        (RESULTS_DIR / "icmpd_hr_is_automation_detail.txt").write_text(text)
    else:
        print("Could not find the link. Trying to click 'Read More' buttons...")
        read_mores = page.query_selector_all("a:has-text('Read More')")
        for rm in read_mores:
            parent_text = page.evaluate(f"(() => {{ const e = document.querySelector('a:has-text(\"Read More\")'); return e ? e.closest('div')?.innerText || '' : ''; }})()")
            if "VA26P112" in parent_text or "HR Information" in parent_text:
                print(f"Clicking Read More...")
                rm.click()
                time.sleep(5)
                text = page.inner_text("body")
                print(f"Detail page ({len(text)} chars):")
                show_text(text, 80)
                (RESULTS_DIR / "icmpd_hr_is_automation_detail.txt").write_text(text)
                break

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. UNU careers.unu.edu
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("UNU Careers (careers.unu.edu)")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://careers.unu.edu", wait_until="networkidle")
    time.sleep(5)
    text = page.inner_text("body")
    print(f"\nMain page ({len(text)} chars):")
    show_text(text, 60)
    
    # Check for jobs link
    links = page.query_selector_all("a")
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if t and len(t) > 3:
            print(f"  [{t[:80]}] -> {href[:100]}")
    
    (RESULTS_DIR / "unu_careers_main.txt").write_text(text)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. World Bank CSOD via Scrapling
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("World Bank CSOD (via Scrapling)")
print("=" * 60)

try:
    from scrapling import StealthyFetcher
    
    url = "https://worldbankgroup.csod.com/ats/careersite/search.aspx?site=1&c=worldbankgroup"
    page = StealthyFetcher.fetch(url, headless=True, wait=10000, block_webrtc=True)
    text = page.get_all_text()
    print(f"\nScrapling result ({len(text)} chars):")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    print(f"Lines: {len(lines)}")
    for l in lines[:60]:
        print(f"  {l[:150]}")
    
    (RESULTS_DIR / "worldbank_csod_scrapling.txt").write_text(text)
    
except Exception as e:
    print(f"Scrapling Error: {e}")
    print("Trying Camoufox as fallback...")
    
    with Camoufox(headless=True, humanize=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto("https://worldbankgroup.csod.com/ats/careersite/search.aspx?site=1&c=worldbankgroup", wait_until="networkidle")
        time.sleep(10)
        text = page.inner_text("body")
        print(f"\nCamoufox result ({len(text)} chars):")
        show_text(text, 60)
        (RESULTS_DIR / "worldbank_csod_camoufox.txt").write_text(text)

print("\nDone!")