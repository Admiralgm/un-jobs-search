#!/usr/bin/env python3
"""Scan ECB career portal directly at talent.ecb.europa.eu."""

import json, sys, time
from pathlib import Path

from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")

results = {}

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    url = "https://talent.ecb.europa.eu/careers"
    print(f"Navigating to {url}...")
    page.goto(url, wait_until="networkidle")
    time.sleep(6)
    
    text = page.inner_text("body")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    print(f"Total lines: {len(lines)}, chars: {len(text)}")
    
    for l in lines[:100]:
        print(f"  {l[:150]}")
    
    results[url] = {
        "lines_count": len(lines),
        "preview": lines[:50],
    }
    
    # Also check browser_console for any job data
    print(f"\nCurrent URL: {page.url}")
    
    # Try to find job-related data in the console
    try:
        page.evaluate("console.log(document.title)")
        console_data = page.evaluate("JSON.stringify(Array.from(document.querySelectorAll('a, button, h2, h3, h4')).map(e => ({tag: e.tagName, text: e.innerText.trim(), href: e.getAttribute('href') || ''})).filter(x => x.text.length > 0).slice(0, 50))")
        print(f"\nConsole data:")
        items = json.loads(console_data)
        for item in items:
            print(f"  <{item['tag']}> {item['text'][:100]} -> {item['href'][:80]}")
    except Exception as e:
        print(f"Console eval error: {e}")
    
    # Save full text
    (RESULTS_DIR / "ecb_talent_full.txt").write_text(text)

outfile = RESULTS_DIR / "ecb_talent_results.json"
outfile.write_text(json.dumps(results, indent=2, default=str))
print(f"\nDone. Full text saved to ecb_talent_full.txt")