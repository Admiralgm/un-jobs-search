#!/usr/bin/env python3
"""Impactpool + UNJobNet concurrent extraction via Scrapling. Clean version."""

import asyncio, json, re, sys, time
from pathlib import Path

sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages')
from scrapling.fetchers import StealthyFetcher

RAW_IP = Path("~/Downloads/DATA_REPOSITORY/JOBS-RAW-EXTRACT/impactpool")
RAW_IP.mkdir(parents=True, exist_ok=True)
RAW_UNJN = Path("~/Downloads/DATA_REPOSITORY/JOBS-RAW-EXTRACT/UNjobsnet")
RAW_UNJN.mkdir(parents=True, exist_ok=True)
TRACKER = Path("~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_IMPACTPOOL.txt")

# Load existing IDs
existing_ip = set()
for f in RAW_IP.glob("IP_*.md"):
    m = re.match(r'IP_(\d+)', f.name)
    if m and f.stat().st_size >= 2000:
        existing_ip.add(int(m.group(1)))
if TRACKER.exists():
    for m in re.finditer(r'IP_(\d+)', TRACKER.read_text()):
        existing_ip.add(int(m.group(1)))

existing_unjn = set()
for f in RAW_UNJN.glob("UNJN_*.md"):
    m = re.match(r'UNJN_(\d+)', f.name)
    if m and f.stat().st_size >= 2000:
        existing_unjn.add(int(m.group(1)))
if TRACKER.exists():
    for m in re.finditer(r'UNJN_(\d+)', TRACKER.read_text()):
        existing_unjn.add(int(m.group(1)))

print(f"Existing: IP={len(existing_ip)}, UNJN={len(existing_unjn)}")

HARD_EXCLUDE = ["intern", "volunteer", "junior", "driver", "clerk", "receptionist",
                "assistant", "accounting", "administrative", "national officer",
                "npo", "security officer", "courier"]

async def fetch_ip(jid, sem):
    async with sem:
        try:
            p = await StealthyFetcher.async_fetch(f"https://www.impactpool.org/jobs/{jid}", headless=True, disable_resources=True, wait=3000)
            text = p.get_all_text() if hasattr(p, 'get_all_text') else p.html_content
            if not text or len(text) < 500:
                return ("skip", jid)
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = lines[0] if lines else "?"
            tl = title.lower()
            for kw in HARD_EXCLUDE:
                if kw in tl:
                    return ("filtered", jid, f"{kw}: {title[:60]}")
            if "ukraine" in text.lower() or "nationals only" in text.lower() or "npsa" in text.lower():
                return ("filtered", jid, f"national/ukraine: {title[:60]}")
            gm = re.search(r'(P-[3456]|D-[12]|IP[345]|GG|GF|EC2|PSA[6789]|IPS[AI])', text)
            grade = gm.group(1) if gm else "?"
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', title[:40]).strip('_')[:40]
            om = re.search(r'Organization[\s:\n]+([^\n]+)', text)
            org = om.group(1).strip()[:15] if om else "?"
            oslug = re.sub(r'[^a-zA-Z0-9]+', '_', org).strip('_')
            fname = f"IP_{jid}_{oslug}_{slug}.md"
            (RAW_IP / fname).write_text(text)
            return ("saved", jid, f"{grade:6s} | {title[:55]} | {org[:12]} | {len(text)}B")
        except Exception as e:
            return ("error", jid, str(e)[:60])

async def fetch_unjn(jid, sem):
    async with sem:
        try:
            p = await StealthyFetcher.async_fetch(f"https://www.unjobnet.org/jobs/detail/{jid}", headless=True, disable_resources=True, wait=2000)
            text = p.get_all_text() if hasattr(p, 'get_all_text') else p.html_content
            if not text or len(text) < 500:
                return ("skip", jid)
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = lines[0] if lines else "?"
            tl = title.lower()
            for kw in HARD_EXCLUDE:
                if kw in tl:
                    return ("filtered", jid, f"{kw}: {title[:55]}")
            gm = re.search(r'(P-[3456]|D-[12]|IP[345]|GG|GF|Consultant|PSA)', text)
            grade = gm.group(1) if gm else "?"
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', title[:40]).strip('_')[:40]
            fname = f"UNJN_{jid}_{slug}.md"
            (RAW_UNJN / fname).write_text(text)
            return ("saved", jid, f"{grade:6s} | {title[:55]} | {len(text)}B")
        except Exception as e:
            return ("error", jid, str(e)[:60])

async def main():
    sem = asyncio.Semaphore(4)
    
    # Impactpool: 88 new IDs
    ip_ids = [656133, 660185, 660301, 662683, 663402, 691539, 1149062, 1173444, 1173856,
              1175924, 1180873, 1187863, 1193626, 1195463, 1196082, 1196689, 1200445,
              1202312, 1206018, 1206894, 1207312, 1210016, 1210169, 1211165, 1211232,
              1211344, 1211567, 1211816, 1212116, 1212383, 1212579, 1212683, 1212868,
              1213132, 1213133, 1213235, 1213548, 1213557, 1213565, 1213603, 1213724,
              1213934, 1214048, 1214092, 1214172, 1214241, 1214260, 1214311, 1214312,
              1214327, 1214385, 1214459, 1214541, 1214544, 1214619, 1214703, 1214759,
              1214784, 1214787, 1214843, 1214858, 1214893, 1214944, 1214961, 1215040,
              1215152, 1215257, 1215305, 1215326, 1215432, 1215512, 1215528, 1215660,
              1215785, 1215794, 1215823, 1215828, 1215830, 1215925, 1215986, 1216097,
              1216120, 1216279, 1216331, 1216558, 1216615, 1216685, 1216706]
    ip_to_fetch = sorted(set(ip_ids) - existing_ip)
    print(f"Impactpool: {len(ip_to_fetch)} to fetch")
    
    # UNJobNet: listing pages
    print(f"\nFetching UNJobNet categories...")
    unjn_ids = set()
    for cp, cn in [("occupations[]=6","ICT"),("occupations[]=70","Innovation"),
                   ("occupations[]=16","Data Science"),("occupations[]=28","Engineering"),
                   ("occupations[]=71","FinTech"),("occupations[]=25","Info Mgmt")]:
        try:
            p = await StealthyFetcher.async_fetch(f"https://www.unjobnet.org/jobs?{cp}&size=200", headless=True, disable_resources=True, wait=4000)
            html = p.html_content if hasattr(p, 'html_content') else ""
            ids = re.findall(r'/jobs/detail/(\d{7,8})', html)
            for jid in ids: unjn_ids.add(int(jid))
            print(f"  {cn}: {len(ids)}")
        except Exception as e:
            print(f"  {cn}: ERROR {e}")
    
    unjn_to_fetch = sorted(unjn_ids - existing_unjn)
    print(f"UNJobNet: {len(unjn_to_fetch)} to fetch")
    
    # Extract both concurrently
    print(f"\nExtracting {len(ip_to_fetch)+len(unjn_to_fetch)} jobs (4 concurrent)...")
    start = time.time()
    results = await asyncio.gather(
        *(fetch_ip(jid, sem) for jid in ip_to_fetch),
        *(fetch_unjn(jid, sem) for jid in unjn_to_fetch)
    )
    elapsed = time.time() - start
    
    saved = [r for r in results if r[0]=="saved"]
    filtered = [r for r in results if r[0]=="filtered"]
    errors = [r for r in results if r[0]=="error"]
    skipped = [r for r in results if r[0]=="skip"]
    
    print(f"\n{'='*60}")
    print(f"DONE in {elapsed:.1f}s ({elapsed/max(len(results),1):.1f}s/job)")
    print(f"Saved: {len(saved)}")
    print(f"Filtered: {len(filtered)}")
    print(f"Errors: {len(errors)}")
    print(f"Skipped: {len(skipped)}")
    print(f"{'='*60}")
    
    print("\nSAVED:")
    for r in sorted(saved, key=lambda x: x[1]):
        print(f"  {r[2]}")
    
    if filtered:
        print("\nFILTERED:")
        for r in filtered: print(f"  {r[2]}")
    if errors:
        print("\nERRORS:")
        for r in errors: print(f"  {r[2]}")

asyncio.run(main())