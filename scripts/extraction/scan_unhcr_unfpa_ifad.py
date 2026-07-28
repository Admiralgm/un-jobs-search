#!/usr/bin/env python3
"""Scan UNHCR (Workday), UNFPA (Oracle HCM), IFAD (PeopleSoft) for ICT/AI roles."""

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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. UNHCR Workday
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=" * 60)
print("UNHCR — unhcr.wd3.myworkdayjobs.com/en-GB/External")
print("=" * 60)

unhcr = {}

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://unhcr.wd3.myworkdayjobs.com/en-GB/External", wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"\nMain page: {len(text)} chars")
    show(text, 60)
    
    unhcr["main"] = {"text": text[:5000], "lines": len([l for l in text.split("\n") if l.strip()])}
    
    # Try IT keyword search
    page.goto("https://unhcr.wd3.myworkdayjobs.com/en-GB/External?q=IT", wait_until="networkidle")
    time.sleep(6)
    text_it = page.inner_text("body")
    print(f"\nSearched 'IT': {len(text_it)} chars")
    show(text_it, 40)
    unhcr["q_it"] = text_it[:3000]
    
    # Try Digital
    page.goto("https://unhcr.wd3.myworkdayjobs.com/en-GB/External?q=Digital", wait_until="networkidle")
    time.sleep(6)
    text_dig = page.inner_text("body")
    print(f"\nSearched 'Digital': {len(text_dig)} chars")
    show(text_dig, 40)
    unhcr["q_digital"] = text_dig[:3000]
    
    # Try ICT
    page.goto("https://unhcr.wd3.myworkdayjobs.com/en-GB/External?q=ICT", wait_until="networkidle")
    time.sleep(6)
    text_ict = page.inner_text("body")
    print(f"\nSearched 'ICT': {len(text_ict)} chars")
    show(text_ict, 40)
    unhcr["q_ict"] = text_ict[:3000]
    
    # Try AI
    page.goto("https://unhcr.wd3.myworkdayjobs.com/en-GB/External?q=AI", wait_until="networkidle")
    time.sleep(6)
    text_ai = page.inner_text("body")
    print(f"\nSearched 'AI': {len(text_ai)} chars")
    show(text_ai, 40)
    unhcr["q_ai"] = text_ai[:3000]

(RESULTS_DIR / "unhcr_results.json").write_text(json.dumps(unhcr, indent=2, default=str))
print("\n✅ UNHCR done")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. UNFPA Oracle HCM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("UNFPA — www.unfpa.org/jobs")
print("=" * 60)

unfpa = {}

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://www.unfpa.org/jobs", wait_until="networkidle")
    time.sleep(6)
    text = page.inner_text("body")
    print(f"\nMain jobs page: {len(text)} chars")
    n = show(text, 60)
    unfpa["main"] = {"text": text[:5000], "lines": n}
    
    # Get all links for job postings
    links = page.query_selector_all("a")
    job_links = []
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if t and len(t) > 5:
            job_links.append({"text": t[:100], "href": href[:120]})
    
    print(f"\nLinks found: {len(job_links)}")
    for jl in job_links:
        if any(kw in jl["text"].lower() for kw in ["ict", "digital", "data", "it ", "technology", "ai", "information"]):
            print(f"  ICT match: {jl['text']} -> {jl['href']}")
    
    unfpa["links"] = job_links[:30]

(RESULTS_DIR / "unfpa_results.json").write_text(json.dumps(unfpa, indent=2, default=str))
print("✅ UNFPA done")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. IFAD PeopleSoft
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("IFAD — www.ifad.org/en/work-with-us")
print("=" * 60)

ifad = {}

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # First get the IFAD work-with-us page
    page.goto("https://www.ifad.org/en/work-with-us", wait_until="networkidle")
    time.sleep(5)
    text = page.inner_text("body")
    print(f"\nWork with us: {len(text)} chars")
    show(text, 50)
    ifad["work_with_us"] = text[:3000]
    
    # Find links to job portal
    links = page.query_selector_all("a")
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if t and len(t) > 3:
            print(f"  [{t[:80]}] -> {href[:120]}")
        if "job" in href.lower() or "career" in href.lower() or "vacanc" in href.lower():
            print(f"  🔗 JOB LINK: [{t[:80]}] -> {href[:120]}")
    
    # Try PeopleSoft direct
    people_soft_urls = [
        "https://job.ifad.org",
        "https://ifad.csod.com",
    ]
    for ps_url in people_soft_urls:
        try:
            page.goto(ps_url, wait_until="networkidle")
            time.sleep(6)
            text = page.inner_text("body")
            print(f"\n{ps_url}: {len(text)} chars")
            show(text, 40)
            ifad[ps_url] = text[:3000]
        except Exception as e:
            print(f"  {ps_url}: ERROR {e}")
            ifad[ps_url] = f"ERROR: {e}"

(RESULTS_DIR / "ifad_results.json").write_text(json.dumps(ifad, indent=2, default=str))
print("✅ IFAD done")

print("\n" + "=" * 60)
print("ALL SCANS COMPLETE")
print("=" * 60)