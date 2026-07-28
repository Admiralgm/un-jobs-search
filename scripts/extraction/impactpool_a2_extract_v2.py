#!/usr/bin/env python3
"""PHASE A2b — Extract job card metadata from Impactpool search pages to pre-filter.
Then only navigate to detail pages for passing jobs."""

import json, re, time, sys
from pathlib import Path
from camoufox import Camoufox

RAW_DIR = Path("~/Downloads/DATA_REPOSITORY/JOBS-RAW-EXTRACT/impactpool")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# New IDs to check
NEW_IDS = [
    656133, 660185, 660301, 662683, 663402, 691539,
    1149062, 1173444, 1173856, 1175924, 1180873, 1187863,
    1193626, 1195463, 1196082, 1196689, 1200445, 1202312,
    1206018, 1206894, 1207312, 1210016, 1210169, 1211165,
    1211232, 1211344, 1211567, 1211816, 1212116, 1212383,
    1212579, 1212683, 1212868, 1213132, 1213133, 1213235,
    1213548, 1213557, 1213565, 1213603, 1213724, 1213934,
    1214048, 1214092, 1214172, 1214241, 1214260, 1214311,
    1214312, 1214327, 1214385, 1214459, 1214541, 1214544,
    1214619, 1214703, 1214759, 1214784, 1214787, 1214843,
    1214858, 1214893, 1214944, 1214961, 1215040, 1215152,
    1215257, 1215305, 1215326, 1215432, 1215512, 1215528,
    1215660, 1215785, 1215794, 1215823, 1215828, 1215830,
    1215925, 1215986, 1216097, 1216120, 1216279, 1216331,
    1216558, 1216615, 1216685, 1216706,
]

# Hard filter keywords in title
EXCLUDE_TITLE_KW = [
    "intern", "volunteer", "junior", "assistant", "driver", "clerk",
    "national officer", "npo", "accounting assistant", "hr assistant",
    "receptionist", "security", "courier", "administrative assistant",
]

def matches_filter(title):
    tl = title.lower()
    return any(kw in tl for kw in EXCLUDE_TITLE_KW)

# Use Scrapling in terminal for search page card metadata
# Then Camoufox only for detail pages of passing jobs

print("=== Phase A2b: Extract card metadata from search pages ===")

# Run the metadata extraction via terminal python3
import subprocess
result = subprocess.run([
    sys.executable, "-c", """
import json, re
from pathlib import Path
import sys
sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages')

# We already got the IDs from search. Now extract card data.
# Use Scrapling to fetch one search page that contains most IDs
from scrapling.fetchers import StealthyFetcher

import asyncio

async def get_card_data():
    url = "https://www.impactpool.org/search?q=AI+ICT+digital"
    page = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=6000)
    html = page.html_content if hasattr(page, 'html_content') else ""
    
    # Extract job cards: title + org + grade from search results
    # Impactpool cards use specific class patterns
    cards = re.findall(r'class="job-card[^"]*"[^>]*>.*?</div>\\s*</div>\\s*</div>', html, re.DOTALL)
    print(f"Found {len(cards)} raw cards")
    
    # Try simpler: extract all job-title elements
    titles = re.findall(r'class="job-title[^"]*"[^>]*>([^<]+)', html)
    print(f"Titles found: {len(titles)}")
    for t in titles[:5]:
        print(f"  {t.strip()[:80]}")
    
    # Extract from href patterns
    entries = re.findall(r'href="/jobs/(\\d{5,8})"[^>]*>\\s*([^<]+)', html)
    print(f"Href+title pairs: {len(entries)}")
    for jid, t in entries[:10]:
        print(f"  IP_{jid}: {t.strip()[:80]}")

asyncio.run(get_card_data())
"""
], capture_output=True, text=True, timeout=30)
print(result.stdout[:2000])
if result.stderr:
    print("STDERR:", result.stderr[:500])

print("\n=== Approach: Direct Camoufox detail pages for new IDs in batches ===")

# Process in batches of 10 with fresh browser per batch
BATCH_SIZE = 8
batches = [NEW_IDS[i:i+BATCH_SIZE] for i in range(0, len(NEW_IDS), BATCH_SIZE)]
print(f"Total: {len(NEW_IDS)} IDs in {len(batches)} batches of {BATCH_SIZE}")

all_passed = []
all_failed = []

for batch_num, batch in enumerate(batches):
    print(f"\n--- Batch {batch_num+1}/{len(batches)} ({len(batch)} IDs) ---")
    
    with Camoufox(headless=True, humanize=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(20000)
        
        for jid in batch:
            url = f"https://www.impactpool.org/jobs/{jid}"
            print(f"  IP_{jid}...", end=" ", flush=True)
            
            try:
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(3)
                text = page.inner_text("body")
                
                # Extract metadata for pre-filter
                title_match = re.search(r'^([A-Z][^\\n]{10,150})', text, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else "(unknown)"
                tl = title.lower()
                grade_match = re.search(r'(P-[345]|D-[12]|IP[345]|GG|GF|EC2|PSA|IPS[AI]|G[FGHE])', text)
                grade = grade_match.group(1) if grade_match else "unknown"
                
                print(f"[{grade:8s}] {title[:60]}", flush=True)
                
                # Hard filters
                if matches_filter(title):
                    print(f"     ❌ Hard filter: title")
                    all_failed.append({"id": jid, "title": title, "reason": "title filter"})
                    continue
                if "intern" in text.lower() or "volunteer" in text.lower():
                    print(f"     ❌ Intern/Volunteer")
                    all_failed.append({"id": jid, "title": title, "reason": "intern/volunteer"})
                    continue
                if "ukraine" in text.lower() or "kyiv" in text.lower():
                    print(f"     ❌ Ukraine")
                    all_failed.append({"id": jid, "title": title, "reason": "ukraine"})
                    continue
                if "national officer" in text.lower() or "npsa" in text.lower() or "nationals only" in text.lower():
                    print(f"     ❌ National position")
                    all_failed.append({"id": jid, "title": title, "reason": "national"})
                    continue
                
                # Save full JD
                slug = re.sub(r'[^a-zA-Z0-9]+', '_', title[:40]).strip('_')[:40]
                org_match = re.search(r'Organization[\\s:]+([^\\n]+)', text)
                org = org_match.group(1).strip()[:15] if org_match else "Unknown"
                org_slug = re.sub(r'[^a-zA-Z0-9]+', '_', org).strip('_')
                fname = f"IP_{jid}_{org_slug}_{slug}.md"
                
                (RAW_DIR / fname).write_text(text)
                print(f"     ✅ Saved: {fname} ({len(text)} chars)")
                all_passed.append({"id": jid, "title": title, "grade": grade, "org": org, "file": fname})
                
            except Exception as e:
                err = str(e)[:60]
                print(f"⚠️ {err}")
                all_failed.append({"id": jid, "title": "", "reason": err})

print(f"\n{'='*60}")
print(f"EXTRACTION COMPLETE")
print(f"Passed: {len(all_passed)}")
print(f"Failed: {len(all_failed)}")
print(f"{'='*60}")

print(f"\nPASSED JOBS:")
for p in sorted(all_passed, key=lambda x: x['id']):
    print(f"  IP_{p['id']} | {p['grade']:8s} | {p['title'][:60]} | {p['org'][:20]}")

print(f"\nFILTERED/FAILED:")
for f in all_failed:
    print(f"  IP_{f['id']} | {f.get('reason','')[:30]} | {f.get('title','')[:50]}")

# Save manifest
manifest = {"passed": all_passed, "failed": all_failed}
(RAW_DIR.parent / "impactpool_a2_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
print(f"\nManifest saved to impactpool_a2_manifest.json")