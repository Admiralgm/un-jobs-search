#!/usr/bin/env python3
"""Impactpool + UNJobNet concurrent extraction via Scrapling.
Run directly in terminal (not sandbox)."""

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

# Load existing
existing_ip = set()
if RAW_IP.exists():
    for f in RAW_IP.glob("IP_*.md"):
        m = re.match(r'IP_(\d+)', f.name)
        if m and f.stat().st_size >= 2000:
            existing_ip.add(int(m.group(1)))
if TRACKER.exists():
    for m in re.finditer(r'IP_(\d+)', TRACKER.read_text()):
        existing_ip.add(int(m.group(1)))

existing_unjn = set()
if RAW_UNJN.exists():
    for f in RAW_UNJN.glob("UNJN_*.md"):
        m = re.match(r'UNJN_(\d+)', f.name)
        if m and f.stat().st_size >= 2000:
            existing_unjn.add(int(m.group(1)))
if TRACKER.exists():
    for m in re.finditer(r'UNJN_(\d+)', TRACKER.read_text()):
        existing_unjn.add(int(m.group(1)))

print(f"Existing: IP={len(existing_ip)}, UNJN={len(existing_unjn)}")

HARD_EXCLUDE_TITLES = ["intern", "volunteer", "junior", "driver", "clerk", "receptionist",
                       "assistant", "accounting assistant", "hr assistant", "administrative",
                       "national officer", "npo", "security officer", "courier"]

async def fetch_ip(jid, sem):
    async with sem:
        url = f"https://www.impactpool.org/jobs/{jid}"
        try:
            page = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=3000)
            text = page.get_all_text() if hasattr(page, 'get_all_text') else page.html_content
            if not text or len(text) < 500:
                return ("skip", jid)
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = lines[0] if lines else "(unknown)"
            tl = title.lower()
            for kw in HARD_EXCLUDE_TITLES:
                if kw in tl:
                    return ("filtered", jid, f"{kw}: {title[:60]}")
            if "ukraine" in text.lower() or "kyiv" in text.lower():
                return ("filtered", jid, f"ukraine: {title[:60]}")
            if "nationals only" in text.lower() or "npsa" in text.lower():
                return ("filtered", jid, f"national: {title[:60]}")
            grade_m = re.search(r'(P-[3456]|D-[12]|IP[345]|GG|GF|EC2|PSA[6789]|IPS[AI])', text)
            grade = grade_m.group(1) if grade_m else "unknown"
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', title[:40]).strip('_')[:40]
            org_m = re.search(r'Organization[\\s:\\n]+([^\\n]+)', text)
            org = org_m.group(1).strip()[:15] if org_m else "Unknown"
            org_slug = re.sub(r'[^a-zA-Z0-9]+', '_', org).strip('_')
            fname = f"IP_{jid}_{org_slug}_{slug}.md"
            (RAW_IP / fname).write_text(text)
            return ("saved", jid, f"{grade:6s} | {title[:55]} | {org[:12]} | {len(text)}B")
        except Exception as e:
            return ("error", jid, str(e)[:60])

async def main():
    sem = asyncio.Semaphore(4)
    
    # Impactpool: 88 new IDs
    ip_ids = [
        656133, 660185, 660301, 662683, 663402, 691539, 1149062, 1173444, 1173856,
        1175924, 1180873, 1187863, 1193626, 1195463, 1196082, 1196689, 1200445,
        1202312, 1206018, 1206894, 1207312, 1210016, 1210169, 1211165, 1211232,
        1211344, 1211567, 1211816, 1212116, 1212383, 1212579, 1212683, 1212868,
        1213132, 1213133, 1213235, 1213548, 1213557, 1213565, 1213603, 1213724,
        1213934, 1214048, 1214092, 1214172, 1214241, 1214260, 1214311, 1214312,
        1214327, 1214385, 1214459, 1214541, 1214544, 1214619, 1214703, 1214759,
        1214784, 1214787, 1214843, 1214858, 1214893, 1214944, 1214961, 1215040,
        1215152, 1215257, 1215305, 1215326, 1215432, 1215512, 1215528, 1215660,
        1215785, 1215794, 1215823, 1215828, 1215830, 1215925, 1215986, 1216097,
        1216120, 1216279, 1216331, 1216558, 1216615, 1216685, 1216706,
    ]
    ip_to_fetch = sorted(set(ip_ids) - existing_ip)
    print(f"Impactpool: {len(ip_to_fetch)} to fetch")
    
    # UNJobNet: fetch listing pages for categories
    print("\nUNJobNet: fetching listing pages...")
    unjn_ids = set()
    categories = {"occupations[]=6": "ICT", "occupations[]=70": "Innovation",
                  "occupations[]=16": "Data Science", "occupations[]=71": "FinTech",
                  "occupations[]=28": "Engineering", "occupations[]=25": "Info Mgmt"}
    for cat_param, cat_name in categories.items():
        url = f"https://www.unjobnet.org/jobs?{cat_param}&size=200"
        try:
            page = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=4000)
            html = page.html_content
            ids = re.findall(r'/jobs/detail/(\d{7,8})', html)
            for jid in ids:
                unjn_ids.add(int(jid))
            print(f"  {cat_name}: {len(ids)} IDs")
        except Exception as e:
            print(f"  {cat_name}: ERROR {e}")
    
    unjn_to_fetch = sorted(unjn_ids - existing_unjn)
    print(f"UNJobNet: {len(unjn_to_fetch)} to fetch")
    for jid in unjn_to_fetch[:5]:
        print(f"  UNJN_{jid}")
    
    # Extract both
    print("\nExtracting...")
    start = time.time()
    ip_tasks = [fetch_ip(jid, sem) for jid in ip_to_fetch]
    unjn_tasks = [fetch_unjn(jid, sem) for jid in unjn_to_fetch]
    
    # Define UNJobNet fetcher inline
    async def fetch_unjn(jid, sem2):
        async with sem2:
            try:
                page = await StealthyFetcher.async_fetch(f"https://www.unjobnet.org/jobs/detail/{jid}", headless=True, disable_resources=True, wait=2000)
                text = page.get_all_text()
                if not text or len(text) < 500:
                    return ("skip", jid)
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                title = lines[0] if lines else "(unknown)"
                tl = title.lower()
                for kw in HARD_EXCLUDE_TITLES:
                    if kw in tl:
                        return ("filtered", jid, f"{kw}: {title[:55]}")
                grade_m = re.search(r'(P-[345]|D-[12]|IP[345]|GG|GF|Consultant|PSA)', text)
                grade = grade_m.group(1) if grade_m else "unknown"
                slug = re.sub(r'[^a-zA-Z0-9]+', '_', title[:40]).strip('_')[:40]
                fname = f"UNJN_{jid}_{slug}.md"
                (RAW_UNJN / fname).write_text(text)
                return ("saved", jid, f"{grade:6s} | {title[:55]} | {len(text)}B")
            except Exception as e:
                return ("error", jid, str(e)[:60])
    
    unjn_tasks2 = [fetch_unjn(jid, sem) for jid in unjn_to_fetch]
    all_results = await asyncio.gather(*(ip_tasks + unjn_tasks2))
    elapsed = time.time() - start
    
    saved_r = [r for r in all_results if r[0] == "saved"]
    filtered_r = [r for r in all_results if r[0] == "filtered"]
    error_r = [r for r in all_results if r[0] == "error"]
    skip_r = [r for r in all_results if r[0] == "skip"]
    
    print(f"\n{'='*60}")
    print(f"DONE in {elapsed:.1f}s")
    print(f"Saved: {len(saved_r)}")
    print(f"Filtered: {len(filtered_r)}")
    print(f"Errors: {len(error_r)}")
    print(f"Skipped: {len(skip_r)}")
    print(f"{'='*60}")
    
    print("\nSAVED:")
    for r in sorted(saved_r, key=lambda x: x[1]):
        print(f"  {r[2]}")
    
    print("\nFILTERED:")
    for r in filtered_r:
        print(f"  {r[2]}")
    
    if error_r:
        print("\nERRORS:")
        for r in error_r:
            print(f"  {r[2]}")
    
    # Save manifest
    (RAW_IP.parent / "impactpool_manifest.json").write_text(json.dumps({
        "saved": [{"id": r[1], "details": r[2]} for r in saved_r],
        "filtered": [{"id": r[1], "reason": r[2]} for r in filtered_r],
        "errors": [{"id": r[1], "error": r[2]} for r in error_r],
    }, indent=2))

asyncio.run(main())