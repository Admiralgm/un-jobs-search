#!/usr/bin/env python3
"""Scan WIPO (wipo.int) for ICT/AI roles using Camoufox (with Scrapling fallback)."""

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

print("=" * 60)
print("WIPO — World Intellectual Property Organization")
print("wipo.int/en/web/working-at-wipo/wipo-jobs")
print("=" * 60)

wipo_results = {}

# Try Camoufox first
with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # 1. Main WIPO jobs page
    print("\n--- Main jobs page ---")
    page.goto("https://www.wipo.int/en/web/working-at-wipo/wipo-jobs", wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"{len(text)} chars")
    show(text, 50)
    wipo_results["main_page"] = {"text": text[:5000], "lines": len([l for l in text.split("\n") if l.strip()])}
    
    # Get all links
    links = page.query_selector_all("a")
    job_link_found = None
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if t and len(t) > 3:
            if "vacanc" in href.lower() or "vacanc" in t.lower() or "job" in t.lower():
                print(f"  JOB LINK: [{t[:80]}] -> {href[:120]}")
                if not job_link_found and ("vacanc" in href.lower() or "jobs" in href.lower()):
                    job_link_found = (t, href)
    
    # 2. Try direct listing URL
    print("\n--- Direct listing URLs ---")
    listing_urls = [
        "https://www.wipo.int/en/web/working-at-wipo/wipo-jobs/-/vacancies",
        "https://www.wipo.int/en/web/working-at-wipo/vacancies",
        "https://www.wipo.int/careers/en/vacancies",
        "https://recruitment.wipo.int",
        "https://www.wipo.int/recruitment/en/vacancies.html",
    ]
    
    for url in listing_urls:
        try:
            page.goto(url, wait_until="networkidle")
            time.sleep(5)
            text = page.inner_text("body")
            lines_n = len([l for l in text.split("\n") if l.strip()])
            print(f"\n{url}: {len(text)} chars, {lines_n} lines")
            show(text, 30)
            wipo_results[url] = {"text": text[:3000], "lines": lines_n}
            
            # Check if it looks like a job listing page
            if any(kw in text.lower() for kw in ["vacanc", "job opening", "closing date", "deadline", "apply"]) and lines_n > 15:
                print(f"  ✅ JOB LISTING PAGE!")
                break
        except Exception as e:
            print(f"\n{url}: ERROR {e}")
            wipo_results[url] = {"error": str(e)}
    
    # 3. Try Taleo (WIPO uses Oracle Taleo)
    print("\n--- Taleo URLs ---")
    taleo_urls = [
        "https://wipo.taleo.net/careersection/2/jobsearch.ftl",
        "https://wipo.taleo.net/careersection/2/jobsearch.ftl?lang=en",
        "https://wipo.taleo.net/careersection/ex/jobsearch.ftl",
    ]
    
    for url in taleo_urls:
        try:
            page.goto(url, wait_until="networkidle")
            time.sleep(6)
            text = page.inner_text("body")
            lines_n = len([l for l in text.split("\n") if l.strip()])
            print(f"\n{url}: {len(text)} chars, {lines_n} lines")
            show(text, 40)
            wipo_results[url] = {"text": text[:3000], "lines": lines_n}
            
            if any(kw in text.lower() for kw in ["vacanc", "job opening", "closing date", "digital", "search"]):
                print(f"  ✅ HAS CONTENT!")
        except Exception as e:
            print(f"\n{url}: ERROR {e}")
            wipo_results[url] = {"error": str(e)}

(RESULTS_DIR / "wipo_results.json").write_text(json.dumps(wipo_results, indent=2, default=str))
print("\n✅ WIPO done")