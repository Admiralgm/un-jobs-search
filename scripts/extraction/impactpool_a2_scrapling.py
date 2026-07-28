#!/usr/bin/env python3
"""PHASE A2 — Impactpool + UNJobNet concurrent extraction via Scrapling async_fetch.
10-14x faster than browser_navigate. Extracts full JDs for new IDs."""

import asyncio, json, re, sys, time
from pathlib import Path

sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages')
from scrapling.fetchers import StealthyFetcher

RAW_IP = Path("~/Downloads/DATA_REPOSITORY/JOBS-RAW-EXTRACT/impactpool")
RAW_IP.mkdir(parents=True, exist_ok=True)

RAW_UNJN = Path("~/Downloads/DATA_REPOSITORY/JOBS-RAW-EXTRACT/UNjobsnet")
RAW_UNJN.mkdir(parents=True, exist_ok=True)

BASE = Path("~/Downloads/DATA_REPOSITORY")
TRACKER = BASE / "UN_SECTOR_VACCANCIES_IMPACTPOOL.txt"

# Load existing IDs
existing_ids = set()
if RAW_IP.exists():
    for f in RAW_IP.glob("IP_*.md"):
        m = re.match(r'IP_(\d+)', f.name)
        if m and f.stat().st_size >= 2000:
            existing_ids.add(("impactpool", int(m.group(1))))
if RAW_UNJN.exists():
    for f in RAW_UNJN.glob("UNJN_*.md"):
        m = re.match(r'UNJN_(\d+)', f.name)
        if m and f.stat().st_size >= 2000:
            existing_ids.add(("unjobnet", int(m.group(1))))
if TRACKER.exists():
    tc = TRACKER.read_text()
    for m in re.finditer(r'IP_(\d+)', tc):
        existing_ids.add(("impactpool", int(m.group(1))))
    for m in re.finditer(r'UNJN_(\d+)', tc):
        existing_ids.add(("unjobnet", int(m.group(1))))

print(f"Existing Impactpool IDs: {len([x for x in existing_ids if x[0]=='impactpool'])}")
print(f"Existing UNJobNet IDs: {len([x for x in existing_ids if x[0]=='unjobnet'])}")

HARD_EXCLUDE_TITLES = ["intern", "volunteer", "junior", "driver", "clerk", "receptionist",
                       "assistant", "accounting assistant", "hr assistant", "administrative assistant",
                       "national officer", "npo", "security officer"]
HARD_EXCLUDE_TEXT = ["ukraine", "kyiv", "nationals only", "npsa", "no-a", "no-b", "no-c",
                     "gs-2", "gs-3", "gs-4", "gs-5", "gs-6"]

def hard_filter(title, text):
    tl = title.lower()
    for kw in HARD_EXCLUDE_TITLES:
        if kw in tl:
            return f"title:{kw}"
    for kw in HARD_EXCLUDE_TEXT:
        if kw in text.lower():
            return f"text:{kw}"
    return None

async def fetch_and_save_impactpool(jid, sem):
    """Fetch one Impactpool JD, filter, save if passes."""
    async with sem:
        url = f"https://www.impactpool.org/jobs/{jid}"
        try:
            page = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=3000)
            text = page.get_all_text() if hasattr(page, 'get_all_text') else page.html_content
            
            if not text or len(text) < 500:
                return ("skip", jid, "empty")
            
            # Extract title from first meaningful line
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = lines[0] if lines else "(unknown)"
            
            # Hard filter
            hf = hard_filter(title, text)
            if hf:
                return ("filtered", jid, f"{hf} | {title[:60]}")
            
            # Extract grade quickly
            grade_m = re.search(r'(P-[3456]|D-[12]|IP[345]|GG|GF|EC2|PSA[6789]|IPS[AI][0-9]|G[FGHE])', text)
            grade = grade_m.group(1) if grade_m else "unknown"
            
            # Save
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', title[:40]).strip('_')[:40]
            org_m = re.search(r'Organization[\\s:\\n]+([^\\n]+)', text)
            org = org_m.group(1).strip()[:15] if org_m else "Unknown"
            org_slug = re.sub(r'[^a-zA-Z0-9]+', '_', org).strip('_')
            fname = f"IP_{jid}_{org_slug}_{slug}.md"
            (RAW_IP / fname).write_text(text)
            
            return ("saved", jid, f"✅ {grade:6s} | {title[:55]} | {org[:15]} | {len(text)}B -> {fname}")
        
        except Exception as e:
            return ("error", jid, str(e)[:60])

async def fetch_and_save_unjobnet(jid, sem):
    """Fetch one UNJobNet JD concurrently."""
    async with sem:
        url = f"https://www.unjobnet.org/jobs/detail/{jid}"
        try:
            page = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=2000)
            text = page.get_all_text() if hasattr(page, 'get_all_text') else page.html_content
            
            if not text or len(text) < 500:
                return ("skip", jid, "empty")
            
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = lines[0] if lines else "(unknown)"
            
            hf = hard_filter(title, text)
            if hf:
                return ("filtered", jid, f"{hf} | {title[:55]}")
            
            grade_m = re.search(r'(P-[345]|D-[12]|IP[345]|GG|GF|Consultant|PSA)', text)
            grade = grade_m.group(1) if grade_m else "unknown"
            
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', title[:40]).strip('_')[:40]
            fname = f"UNJN_{jid}_{slug}.md"
            (RAW_UNJN / fname).write_text(text)
            
            return ("saved", jid, f"✅ {grade:6s} | {title[:55]} | {len(text)}B -> {fname}")
        
        except Exception as e:
            return ("error", jid, str(e)[:60])


async def main():
    # ── UNJobNet first: get fresh IDs ──
    print("\n=== UNJobNet Phase A3: Fetch job listing pages ===")
    unjn_new_ids = set()
    
    categories = {"occupations[]=6": "ICT", "occupations[]=70": "Innovation",
                  "occupations[]=16": "Data Science", "occupations[]=71": "FinTech"}
    
    for cat_param, cat_name in categories.items():
        url = f"https://www.unjobnet.org/jobs?{cat_param}&size=200"
        try:
            page = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=4000)
            html = page.html_content if hasattr(page, 'html_content') else ""
            ids = re.findall(r'/jobs/detail/(\d{7,8})', html)
            for jid in ids:
                unjn_new_ids.add(int(jid))
            print(f"  {cat_name}: {len(ids)} IDs")
        except Exception as e:
            print(f"  {cat_name}: ERROR {e}")
    
    print(f"\nTotal UNJobNet IDs found: {len(unjn_new_ids)}")
    
    existing_unjn = {x[1] for x in existing_ids if x[0] == 'unjobnet'}
    unjn_to_fetch = sorted(unjn_new_ids - existing_unjn)
    print(f"New UNJobNet IDs to extract: {len(unjn_to_fetch)}")
    for jid in unjn_to_fetch[:10]:
        print(f"  UNJN_{jid}")
    
    # ── Impactpool: 88 new IDs from search ──
    # I already have the 88 IDs from the search. Let me just process them via Scrapling.
    impactpool_new_ids = [
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
    
    existing_ip = {x[1] for x in existing_ids if x[0] == 'impactpool'}
    ip_to_fetch = sorted(set(impactpool_new_ids) - existing_ip)
    print(f"\n=== Impactpool: {len(impactpool_new_ids)} total, {len(ip_to_fetch)} new to extract ===")
    
    # ── Extract both concurrently ──
    sem = asyncio.Semaphore(4)  # 4 concurrent max
    
    print(f"\nStarting Impactpool extraction ({len(ip_to_fetch)} jobs, 4 concurrent)...")
    ip_tasks = [fetch_and_save_impactpool(jid, sem) for jid in ip_to_fetch]
    
    print(f"\nStarting UNJobNet extraction ({len(unjn_to_fetch)} jobs, 4 concurrent)...")
    unjn_tasks = [fetch_and_save_unjobnet(jid, sem) for jid in unjn_to_fetch]
    
    all_tasks = ip_tasks + unjn_tasks
    start = time.time()
    results = await asyncio.gather(*all_tasks)
    elapsed = time.time() - start
    
    # Report
    saved = [r for r in results if r[0] == "saved"]
    filtered = [r for r in results if r[0] == "filtered"]
    skipped = [r for r in results if r[0] == "skip"]
    errors = [r for r in results if r[0] == "error"]
    
    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE in {elapsed:.1f}s ({elapsed/len(all_tasks):.1f}s/job avg)")
    print(f"Saved: {len(saved)}")
    print(f"Filtered: {len(filtered)}")
    print(f"Skipped/Empty: {len(skipped)}")
    print(f"Errors: {len(errors)}")
    print(f"{'='*60}")
    
    print(f"\nSAVED:")
    for r in saved:
        print(f"  {r[2]}")
    
    print(f"\nFILTERED:")
    for r in filtered:
        print(f"  {r[2]}")

asyncio.run(main())