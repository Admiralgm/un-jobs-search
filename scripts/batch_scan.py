#!/usr/bin/env python3
"""
UN Jobs Batch Scanner - Camoufox Python serverless
Scans multiple UN career portals for ICT/AI job vacancies
"""
import subprocess
import json
import re
import sys
import os
import time
from datetime import datetime

WORKDIR = "~/Downloads/DATA_REPOSITORY/WORKDIR"
TRACKER_FILE = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt"

# Load existing IDs
def load_existing_ids():
    ids = set()
    archive_file = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_ARCHIVE.txt"
    for fpath in [TRACKER_FILE, archive_file]:
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r') as f:
            text = f.read()
        found = re.findall(r'\b(\d{5,})\b', text)
        ids.update(found)
        found2 = re.findall(r'\b([A-Z]{2,}-[\w/-]+)\b', text)
        ids.update(found2)
    return ids

# Camoufox Python serverless scraper
def scrape_with_camoufox(url, wait_ms=8000, keywords=None):
    """Scrape a JS-rendered page using Camoufox Python serverless"""
    kw_js = ""
    if keywords:
        kw_list = '","'.join(keywords)
        kw_js = f'''
    // Try to find and use search box
    var searchBoxes = document.querySelectorAll('input[type="text"], input[placeholder*="earch"], input[name*="earch"]');
    var results = [];
    if(searchBoxes.length > 0 && "{keywords[0]}") {{
        for(var kw of ["{kw_list}"]) {{
            searchBoxes[0].value = kw;
            searchBoxes[0].dispatchEvent(new Event('input', {{bubbles: true}}));
            searchBoxes[0].dispatchEvent(new Event('change', {{bubbles: true}}));
        }}
    }}
    '''
    
    script = f'''
import sys, json, time
sys.path.insert(0, "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages")
try:
    from camoufox import Camoufox
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto("{url}")
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep({wait_ms/1000})
        text = page.inner_text("body")
        # Also try to extract structured job data via JS
        jobs = page.evaluate("""
        () => {{
            var results = [];
            // Taleo pattern
            var taleoRows = document.querySelectorAll('tr[valign="top"]');
            for(var r of taleoRows){{
                var link = r.querySelector('a[href*="jobdetail"]');
                if(!link) continue;
                var href = link.getAttribute('href');
                var title = link.textContent.trim();
                var cells = r.querySelectorAll('td');
                var location = cells.length > 1 ? cells[1].textContent.trim() : '';
                var deadline = cells.length > 2 ? cells[2].textContent.trim() : '';
                results.push({{title: title, href: href, location: location, deadline: deadline}});
            }}
            if(results.length > 0) return {{pattern: 'taleo', jobs: results}};
            
            // Generic link pattern
            var links = document.querySelectorAll('a[href*="job"], a[href*="vacancy"], a[href*="career"]');
            var seen = new Set();
            for(var l of links){{
                var t = l.textContent.trim();
                var h = l.getAttribute('href');
                if(t.length > 15 && t.length < 200 && !seen.has(t)){{
                    seen.add(t);
                    results.push({{title: t, href: h, location: '', deadline: ''}});
                }}
            }}
            return {{pattern: 'generic', jobs: results}};
        }}
        """)
        print(json.dumps({{"text": text[:20000], "jobs": jobs}}))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
'''
    result = subprocess.run(
        ['/Library/Frameworks/Python.framework/Versions/3.13/bin/python3', '-c', script],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        return None, result.stderr
    try:
        data = json.loads(result.stdout)
        return data.get('jobs', {}), data.get('text', '')
    except:
        return None, result.stdout[:500]

# Web preclean for open portals
def scrape_with_preclean(url, max_chars=8000):
    result = subprocess.run(
        ['/Library/Frameworks/Python.framework/Versions/3.13/bin/python3',
         os.path.expanduser('config/scripts/web-preclean.py'),
         url, str(max_chars)],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout

# Portal definitions
PORTALS = [
    # (name, url, method, keywords)
    ("WHO_Taleo", "https://careers.who.int/careersection/ex/jobsearch.ftl", "camoufox", ["Digital", "AI", "ICT"]),
    ("UNOPS", "https://careers.unops.org", "camoufox", ["ICT", "Digital", "Data"]),
    ("ILO", "https://jobs.ilo.org/go/All-Jobs/2842101/", "camoufox", ["Digital", "ICT", "Information"]),
    ("ITU", "https://jobs.itu.int", "camoufox", ["Digital", "AI", "ICT"]),
    ("ICRC", "https://careers.icrc.org/go/All-Jobs/3807301/", "camoufox", ["Information", "Digital", "Data"]),
    ("FAO", "https://jobs.fao.org/careersection/fao_external/jobsearch.ftl", "camoufox", ["Digital", "Data", "ICT"]),
    ("UNIDO", "https://careers.unido.org/search/?q=Digital", "camoufox", None),
    ("UNESCO", "https://careers.unesco.org/search/?q=Digital", "camoufox", None),
    ("UNDP", "https://jobs.undp.org/cj_view_jobs.cfm", "preclean", None),
    ("UNHCR", "https://unhcr.wd3.myworkdayjobs.com/en-GB/External", "camoufox", ["Digital", "ICT", "Information"]),
    ("WFP", "https://wd3.myworkdaysite.com/recruiting/wfp/job_openings", "camoufox", ["Digital", "ICT", "Data"]),
    ("IMF", "https://imf.wd5.myworkdayjobs.com/IMF", "camoufox", ["Digital", "Data", "ICT"]),
    ("OECD", "https://careers.smartrecruiters.com/OECD", "camoufox", ["Digital", "AI", "Data"]),
    ("WTO", "https://careers.smartrecruiters.com/WTO", "camoufox", ["Digital", "Technology"]),
    ("ICAO", "https://icaocareers.icao.int/careers/Home/Vacancies", "camoufox", None),
    ("IMO", "https://recruit.imo.org", "camoufox", None),
    ("ICMPD", "https://careers.icmpd.org", "camoufox", None),
    ("UNITAR", "https://unitar.org/vacancy-announcements", "camoufox", None),
    ("IFAD", "https://job.ifad.org/psc/IFHRPRDE/CAREERS/JOBS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U", "camoufox", None),
    ("GICHD", "https://gichd.org/the-gichd/job-opportunities/", "camoufox", None),
    ("UNFPA", "https://www.unfpa.org/jobs", "camoufox", ["Digital", "ICT", "Data"]),
    ("WIPO", "https://www.wipo.int/en/web/working-at-wipo/wipo-jobs", "camoufox", ["Digital", "ICT"]),
    ("WorldBank", "https://worldbankgroup.csod.com/ux/ats/careersite/1/home?c=worldbankgroup", "camoufox", ["Digital", "ICT", "Data"]),
]

if __name__ == '__main__':
    existing_ids = load_existing_ids()
    print(f"Loaded {len(existing_ids)} existing tracker IDs")
    print(f"Starting batch scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_results = {}
    
    for name, url, method, keywords in PORTALS:
        print(f"\n[{name}] Scanning {url}...")
        try:
            if method == 'camoufox':
                jobs_data, text = scrape_with_camoufox(url, keywords=keywords)
                if jobs_data:
                    pattern = jobs_data.get('pattern', 'unknown')
                    jobs = jobs_data.get('jobs', [])
                    print(f"  Found {len(jobs)} jobs (pattern: {pattern})")
                    all_results[name] = {'jobs': jobs, 'url': url, 'text': text[:5000]}
                else:
                    print(f"  No jobs extracted via JS. Text length: {len(text)}")
                    all_results[name] = {'jobs': [], 'url': url, 'text': text[:5000]}
            elif method == 'preclean':
                text = scrape_with_preclean(url)
                print(f"  Preclean result: {len(text)} chars")
                all_results[name] = {'jobs': [], 'url': url, 'text': text[:5000]}
        except Exception as e:
            print(f"  ERROR: {e}")
            all_results[name] = {'jobs': [], 'url': url, 'text': '', 'error': str(e)}
        
        time.sleep(2)  # Brief pause between portals
    
    # Save results
    output_file = os.path.join(WORKDIR, 'batch_scan_results.json')
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"Batch scan complete. Results saved to {output_file}")
    
    # Summary
    total_jobs = sum(len(r.get('jobs', [])) for r in all_results.values())
    print(f"Total jobs extracted: {total_jobs}")
    for name, r in all_results.items():
        n = len(r.get('jobs', []))
        if n > 0:
            print(f"  {name}: {n} jobs")
