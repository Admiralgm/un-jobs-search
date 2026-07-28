#!/usr/bin/env python3
"""Extract ALL jobs from World Bank CSOD via JS + check tracker for ICMPD."""

import json, re, time
from pathlib import Path

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")
TRACKER_DIR = Path("~/Downloads/DATA_REPOSITORY")

from camoufox import Camoufox

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Extract all jobs from CSOD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=" * 60)
print("World Bank CSOD - Full Job List Extraction")
print("=" * 60)

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    page.goto("https://worldbankgroup.csod.com/ats/careersite/search.aspx?site=1&c=worldbankgroup", wait_until="networkidle")
    time.sleep(8)
    
    # Extract ALL job cards via JS
    jobs = page.evaluate("""() => {
        // Try multiple selectors for job cards
        const cards = document.querySelectorAll('[class*="panel"]');
        const results = [];
        const seen = new Set();
        
        for (const card of cards) {
            const text = card.innerText?.trim();
            if (!text || text.length < 20) continue;
            
            // Extract job title (first line)
            const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 2) continue;
            
            const title = lines[0];
            // Skip non-job content
            if (title.includes('Filters') || title.includes('Welcome') || title.includes('Realize') || 
                title.includes('Connect with us') || title.includes('Country') || title.includes('City') ||
                title.includes('State') || title.includes('About') || title.includes('Sign In') ||
                title.includes('Create Profile') || title.includes('Reset') || title.includes('Search') ||
                title.length > 120 || seen.has(title)) continue;
            
            seen.add(title);
            
            // Extract link if any
            const link = card.querySelector('a');
            const href = link ? link.getAttribute('href') : '';
            
            results.push({
                title: title,
                lines: lines,
                href: href
            });
        }
        
        // Also try A tags with job titles
        const jobLinks = document.querySelectorAll('a[class*="link"]');
        for (const a of jobLinks) {
            const t = a.innerText?.trim();
            if (t && t.length > 5 && t.length < 150 && !seen.has(t)) {
                // Check if this is a job title (not a menu link)
                if (t.includes('Temporary') || t.includes('Consultant') || t.includes('Analyst') || 
                    t.includes('Officer') || t.includes('Specialist') || t.includes('Manager') ||
                    t.includes('Engineer') || t.includes('Developer') || t.includes('Advisor')) {
                    seen.add(t);
                    const parent = a.closest('div');
                    const parentText = parent ? parent.innerText : '';
                    results.push({
                        title: t,
                        lines: parentText.split('\\n').map(l => l.trim()).filter(l => l),
                        href: a.getAttribute('href') || ''
                    });
                }
            }
        }
        
        return JSON.stringify(results, null, 2);
    }""")
    
    print(f"\nExtracted jobs:")
    print(jobs)
    
    # Save
    (RESULTS_DIR / "worldbank_csod_jobs.json").write_text(jobs)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Check existing tracker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "=" * 60)
print("Check tracker for ICMPD and WB jobs")
print("=" * 60)

tt = TRACKER_DIR / "UN_SECTOR_VACCANCIES.txt"
if tt.exists():
    content = tt.read_text()
    # Look for ICMPD
    if "ICMPD" in content or "VA26P112" in content:
        print("ICMPD HR IS already tracked!")
    else:
        print("ICMPD HR IS NOT in tracker - NEW!")
    
    # Look for World Bank
    wb_count = len(re.findall(r"World Bank|WB ", content))
    print(f"World Bank entries in tracker: {wb_count}")
    
    # Count total entries
    title_count = len(re.findall(r"^- Title:", content, re.MULTILINE))
    print(f"Total entries: {title_count}")
    
    # Check archive too
    archive = TRACKER_DIR / "UN_SECTOR_VACCANCIES_ARCHIVE.txt"
    if archive.exists():
        arch_content = archive.read_text()
        if "ICMPD" in arch_content:
            print("ICMPD in ARCHIVE (already applied/expired)")
        else:
            print("ICMPD not in archive either")

print("\nDone!")