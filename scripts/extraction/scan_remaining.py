#!/usr/bin/env python3
"""Scan IFAD (correct URL) + remaining small portals: GICHD, UNDRR, WMO, UNESCAP, UNESCWA, UNICRI."""

import json, time, re
from pathlib import Path
from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def show(text, n=60):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:n]:
        print(f"  {l[:150]}")
    return len(lines)

def check_links(page, keyword_filter=None):
    """Find job-like links."""
    links = page.query_selector_all("a")
    job_links = []
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if t and len(t) > 3:
            if keyword_filter:
                if any(kw in t.lower() or kw in href.lower() for kw in keyword_filter):
                    print(f"  [{t[:80]}] -> {href[:100]}")
                    job_links.append((t, href))
            else:
                print(f"  [{t[:80]}] -> {href[:100]}")
                job_links.append((t, href))
    return job_links

all_results = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. IFAD (correct PeopleSoft URL)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=" * 60)
print("IFAD - PeopleSoft job search")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(60000)
    
    url = "https://job.ifad.org/psc/IFHRPRDE/CAREERS/JOBS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U"
    page.goto(url, wait_until="networkidle")
    time.sleep(8)
    
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    show(text, 80)
    all_results["ifad"] = {"text": text[:6000]}
    
    # Try to find and click search buttons
    buttons = page.query_selector_all("button, input[type='submit'], a")
    for b in buttons:
        t = b.inner_text().strip() if hasattr(b, 'inner_text') else ""
        href = b.get_attribute("href") if hasattr(b, 'get_attribute') else ""
        if t and ("search" in t.lower() or "view" in t.lower() or "job" in t.lower()):
            print(f"  B: [{t[:60]}] -> {href[:80]}")
    
    # Try URL with search parameter
    print("\n--- Trying with search params ---")
    search_url = "https://job.ifad.org/psc/IFHRPRDE/CAREERS/JOBS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U&SearchReqDescr=Digital"
    page.goto(search_url, wait_until="networkidle")
    time.sleep(8)
    text2 = page.inner_text("body")
    print(f"{len(text2)} chars")
    show(text2, 60)
    all_results["ifad_search"] = text2[:4000]
    
    # Try View All Jobs link
    view_all = page.query_selector("a:has-text('View All Jobs')")
    if view_all:
        href = view_all.get_attribute("href") or ""
        print(f"\nView All Jobs href: {href}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. GICHD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("GICHD - gichd.org/the-gichd/job-opportunities/")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://www.gichd.org/the-gichd/job-opportunities/", wait_until="networkidle")
    time.sleep(5)
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    show(text, 60)
    all_results["gichd"] = {"text": text[:5000]}
    
    # Find job links
    check_links(page, keyword_filter=["job", "vacanc", "opportunit"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. WMO (World Meteorological Org)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("WMO - erecruit.wmo.int")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://erecruit.wmo.int/public/", wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    show(text, 60)
    all_results["wmo"] = {"text": text[:5000]}
    
    # Try searching for ICT
    inputs = page.query_selector_all("input")
    for inp in inputs:
        name = inp.get_attribute("name") or ""
        placeholder = inp.get_attribute("placeholder") or ""
        if "key" in name.lower() or "search" in name.lower() or "key" in placeholder.lower():
            print(f"Search box: name={name}, placeholder={placeholder}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. UNDRR (UN Disaster Risk Reduction)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("UNDRR - undrr.org/jobs")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://www.undrr.org/jobs", wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    show(text, 60)
    all_results["undrr"] = {"text": text[:5000]}
    
    # Check for job listings
    check_links(page, keyword_filter=["job", "vacanc", "apply", "closing"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. UNESCAP (Economic & Social Comm. Asia/Pacific)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("UNESCAP - unescap.org/jobs")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://www.unescap.org/jobs", wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    show(text, 60)
    all_results["unescap"] = {"text": text[:5000]}
    check_links(page)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. UNESCWA (Economic & Social Comm. W. Asia)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("UNESCWA - unescwa.org/jobs")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://www.unescwa.org/jobs", wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    show(text, 60)
    all_results["unescwa"] = {"text": text[:5000]}
    check_links(page)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. UNICRI (Interregional Crime & Justice)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("UNICRI - unicri.it/jobs")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://unicri.it/jobs", wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"\n{len(text)} chars")
    show(text, 60)
    all_results["unicri"] = {"text": text[:5000]}
    check_links(page)

# Save all
(RESULTS_DIR / "remaining_portals.json").write_text(json.dumps(all_results, indent=2, default=str))
print("\n" + "=" * 60)
print("ALL REMAINING PORTALS SCANNED")
print("=" * 60)