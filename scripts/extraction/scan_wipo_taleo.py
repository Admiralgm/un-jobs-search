#!/usr/bin/env python3
"""WIPO Taleo career sections - P&D and keyword searches."""

import json, time, re
from pathlib import Path
from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

def show(text, n=60):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:n]:
        print(f"  {l[:150]}")
    return len(lines)

print("=" * 60)
print("WIPO - Taleo Career Sections")
print("=" * 60)

results = {}

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # 1. P and D jobs (international professional - the one we want)
    print("\n--- P and D jobs ---")
    url = "https://wipo.taleo.net/careersection/wp_2_pd/jobsearch.ftl?lang=en&portal=50305027338"
    page.goto(url, wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"{len(text)} chars")
    lines_n = show(text, 60)
    results["pd_main"] = {"text": text[:5000], "lines": lines_n}
    
    # Get links to individual jobs
    links = page.query_selector_all("a")
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if t and len(t) > 5:
            if "jobdetail" in href.lower() or ("-@-" in href) or ("/jobdetail.ftl" in href.lower()):
                print(f"  JOB: [{t[:80]}] -> {href[:120]}")
    
    # Check for keyword search box
    search_inputs = page.query_selector_all("input[type='text'], input[name='keyword'], input[id*='keyword']")
    print(f"\nSearch inputs found: {len(search_inputs)}")
    for inp in search_inputs:
        name = inp.get_attribute("name") or ""
        id_val = inp.get_attribute("id") or ""
        placeholder = inp.get_attribute("placeholder") or ""
        print(f"  Input: name={name}, id={id_val}, placeholder={placeholder}")
    
    # Try searching for 'Digital'
    print("\n--- P&D search: Digital ---")
    try:
        search_box = page.query_selector("input[id*='keyword'], input[placeholder*='keywor']")
        if search_box:
            search_box.fill("")
            page.keyboard.type("Digital")
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(6)
            text = page.inner_text("body")
            print(f"{len(text)} chars")
            show(text, 40)
            results["pd_digital"] = text[:3000]
        else:
            print("No search box found - trying URL-based search")
            page.goto(url + "&keyword=Digital", wait_until="networkidle")
            time.sleep(6)
            text = page.inner_text("body")
            print(f"{len(text)} chars")
            show(text, 40)
            results["pd_digital_url"] = text[:3000]
    except Exception as e:
        print(f"Search error: {e}")
    
    # 2. GS jobs (General Service - local Geneva)
    print("\n--- GS jobs ---")
    gs_url = "https://wipo.taleo.net/careersection/wp_2_gs/jobsearch.ftl?lang=en&portal=50305027338"
    page.goto(gs_url, wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"{len(text)} chars")
    show(text, 40)
    results["gs_main"] = {"text": text[:3000], "lines": len([l for l in text.split("\n") if l.strip()])}

(RESULTS_DIR / "wipo_taleo_results.json").write_text(json.dumps(results, indent=2, default=str))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Check tracker for WIPO entries
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("Check tracker for WIPO entries")
print("=" * 60)

TRACKER_DIR = Path("~/Downloads/DATA_REPOSITORY")
for fname in ["UN_SECTOR_VACCANCIES.txt", "UN_SECTOR_VACCANCIES_IMPACTPOOL.txt", "UN_SECTOR_VACCANCIES_ARCHIVE.txt"]:
    f = TRACKER_DIR / fname
    if f.exists():
        content = f.read_text()
        wipo_lines = [l for l in content.split("\n") if "WIPO" in l or "wipo" in l.lower()]
        if wipo_lines:
            print(f"\n{fname}:")
            for l in wipo_lines:
                print(f"  {l[:120]}")

print("\n✅ Done")