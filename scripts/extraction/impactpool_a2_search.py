#!/usr/bin/env python3
"""PHASE A2 — Impactpool search via Camoufox. 6 keyword queries, collect new IDs."""

import json, re, time, sys
from pathlib import Path

sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages')
from camoufox import Camoufox

BASE = Path("~/Downloads/DATA_REPOSITORY")
TRACKER = BASE / "UN_SECTOR_VACCANCIES_IMPACTPOOL.txt"

# Load existing IDs
existing_ids = set()
ip_dir = BASE / "JOBS-RAW-EXTRACT/impactpool"
if ip_dir.exists():
    for f in ip_dir.glob("IP_*.md"):
        m = re.match(r'IP_(\d+)', f.name)
        if m:
            existing_ids.add(int(m.group(1)))
if TRACKER.exists():
    tids = set(re.findall(r'IP_(\d+)', TRACKER.read_text()))
    existing_ids.update(int(x) for x in tids if x.isdigit())

print(f"Existing Impactpool IDs: {len(existing_ids)}")

QUERIES = [
    "AI+ICT+digital",
    "telecom+connectivity+cyber+innovation+transformation",
    "agentic+automation+cybersecurity",
    "Artificial+Intelligence+IT+ISP",
    "digitalisation+data+platform+cloud",
    "machine+learning+LLM+generative",
]

TOTAL_IDS_FOUND = set()
all_results = {}

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    for query in QUERIES:
        url = f"https://www.impactpool.org/search?q={query}"
        print(f"\nSearch: '{query[:40]}'")
        
        try:
            page.goto(url, wait_until="networkidle")
            time.sleep(5)
            
            text = page.inner_text("body")
            
            # Try JS to extract job IDs
            job_data = page.evaluate("""() => {
                const links = document.querySelectorAll('a[href*="/jobs/"]');
                const ids = [];
                const seen = new Set();
                for (const a of links) {
                    const m = a.getAttribute('href').match(/\/jobs\/(\\d{5,8})/);
                    if (m && !seen.has(m[1])) {
                        seen.add(m[1]);
                        ids.push({id: m[1], title: a.innerText.trim().substring(0, 80)});
                    }
                }
                return JSON.stringify(ids.slice(0, 50));
            }""")
            
            jobs = json.loads(job_data) if job_data else []
            print(f"  Found {len(jobs)} jobs")
            
            for j in jobs:
                TOTAL_IDS_FOUND.add(int(j["id"]))
            
            all_results[query[:30]] = {"count": len(jobs), "jobs": jobs[:10]}
            
        except Exception as e:
            print(f"  ERROR: {e}")
            all_results[query[:30]] = {"error": str(e)}

new_ids = sorted(TOTAL_IDS_FOUND - existing_ids)
print(f"\n\nTotal unique IDs found: {len(TOTAL_IDS_FOUND)}")
print(f"New IDs (not in extracts/tracker): {len(new_ids)}")

for jid in new_ids:
    print(f"  IP_{jid}")

# Save results
(RESULTS_DIR / "impactpool_search_results.json").write_text(json.dumps(all_results, indent=2, default=str))

print("\n=== PHASE A2 Impactpool search complete ===")