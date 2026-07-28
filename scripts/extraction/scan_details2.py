#!/usr/bin/env python3
"""Get ICMPD full JD + World Bank CSOD search + UNITAR EdTech roster detail."""

import json, time
from pathlib import Path

from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Download ICMPD PDF attachment
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=" * 60)
print("ICMPD - Download Job Profile PDF")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://careers.icmpd.org/Home/JobOpeningDetails?jobOpeningId=1163", wait_until="networkidle")
    time.sleep(4)
    
    # Check for PDF link
    links = page.query_selector_all("a")
    for a in links:
        href = a.get_attribute("href") or ""
        t = a.inner_text().strip()
        if "pdf" in href.lower() or "pdf" in t.lower() or "Job Profile" in t or "HR System" in t:
            print(f"PDF link: {t} -> {href}")
            full_url = href if href.startswith("http") else "https://careers.icmpd.org" + href
            print(f"Full URL: {full_url}")
    
    # Full description from the page
    page_data = page.evaluate("""() => {
        const main = document.querySelector('main') || document.querySelector('[role="main"]') || document.body;
        return main.innerText;
    }""")
    
    print(f"\nFull page data ({len(page_data)} chars):")
    lines = [l.strip() for l in page_data.split("\n") if l.strip()]
    for l in lines[:40]:
        print(f"  {l[:160]}")
    
    (RESULTS_DIR / "icmpd_hr_is_full.txt").write_text(page_data)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. World Bank CSOD - search jobs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("World Bank CSOD - job search via Camoufox")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    # Need to navigate to a search URL that shows results
    urls = [
        "https://worldbankgroup.csod.com/ats/careersite/search.aspx?site=1&c=worldbankgroup&search=IT",
        "https://worldbankgroup.csod.com/ats/careersite/search.aspx?site=1&c=worldbankgroup",
    ]
    
    for url in urls:
        print(f"\n{url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(6)
        text = page.inner_text("body")
        print(f"  {len(text)} chars")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for l in lines[:50]:
            print(f"  {l[:150]}")
        
        # Try clicking search/filter
        all_links = page.query_selector_all("a, button")
        for el in all_links:
            t = el.inner_text().strip()
            if "ict" in t.lower() or "digital" in t.lower() or "it" in t.lower():
                print(f"  Found keyword match: [{t}]")
    
    # Get JS console data - check for hidden job elements
    try:
        job_elements = page.evaluate("""() => {
            const all = document.querySelectorAll('*');
            const results = [];
            for (const el of all) {
                const t = el.innerText?.trim();
                if (t && t.length > 5 && t.length < 200 && 
                    (t.includes('IT') || t.includes('Digital') || t.includes('Data') || 
                     t.includes('Engineer') || t.includes('Developer') || t.includes('ICT') ||
                     t.includes('Technology') || t.includes('Analyst') || t.includes('AI'))) {
                    results.push({tag: el.tagName, text: t.substring(0, 120), class: el.className?.substring(0, 40)});
                }
            }
            return JSON.stringify(results.slice(0, 40), null, 2);
        }""")
        print(f"\nHidden job elements:")
        print(job_elements[:2000])
    except Exception as e:
        print(f"Eval error: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. UNITAR - EdTech/AI Roster detail
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("UNITAR EdTech/AI Roster Detail")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    url = "/vacancy-announcements/roster/consultant-learning-solutions-roster-educational-technology-informatio"
    page.goto("https://www.unitar.org" + url, wait_until="networkidle")
    time.sleep(4)
    text = page.inner_text("body")
    print(f"{len(text)} chars")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:50]:
        print(f"  {l[:150]}")
    
    (RESULTS_DIR / "unitar_edtech_roster.txt").write_text(text)

print("\nDone!")