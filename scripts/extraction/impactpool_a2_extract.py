#!/usr/bin/env python3
"""PHASE A2 — Pre-filter 88 new Impactpool IDs by getting title/grade/org.
Batch: grab 4 at a time via Camoufox, extract metadata, hard-filter, save full JDs only for passing ones."""

import json, re, time, sys
from pathlib import Path

sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages')
from camoufox import Camoufox

RAW_DIR = Path("~/Downloads/DATA_REPOSITORY/JOBS-RAW-EXTRACT/impactpool")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# New IDs from search (sorted)
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

HARD_EXCLUDE = ["intern", "volunteer", "ukraine", "national officer", "npsa", "no-", "no-", "gs-", "g-"]
GRADE_MIN = ["p-3", "p-4", "p-5", "d-1", "d-2", "ip3", "ip4", "ip5", "gg", "gf", "ge", "ec2", "consultant", "psa", "ipsa"]

def extract_metadata(text):
    """Extract title, org, grade, location, deadline from Impactpool page text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    title = ""
    org = ""
    grade = ""
    location = ""
    deadline = ""
    
    for i, l in enumerate(lines):
        tl = l.lower()
        if not title and len(l) > 5 and len(l) < 200 and not tl.startswith("http"):
            # First meaningful line that looks like a title
            if any(c.isupper() for c in l[:5]):
                title = l[:120]
                break
    
    # Find key fields
    for i, l in enumerate(lines):
        tl = l.lower()
        if "organization" in tl or "organisation" in tl:
            if i+1 < len(lines):
                org = lines[i+1][:60]
        if "grade" in tl or "level" in tl or "category" in tl:
            if i+1 < len(lines):
                grade = lines[i+1][:40]
        if "location" in tl or "duty station" in tl:
            if i+1 < len(lines):
                location = lines[i+1][:60]
        if "deadline" in tl or "closing" in tl or "close" in tl:
            if i+1 < len(lines):
                deadline = lines[i+1][:40]
    
    # Check for keywords in full text
    text_lower = text.lower()
    country_exclude = any(c in text_lower for c in ["ukraine", "kyiv", "odesa"])
    intern_exclude = "intern" in text_lower
    national_exclude = any(x in text_lower for x in ["nationals only", "national officer", "npsa", "no-a", "no-b", "no-c", "gs-2", "gs-3", "gs-4", "gs-5"])
    junior_exclude = "junior" in title.lower() or ("junior" in text_lower and "p-3" not in grade and "p-4" not in grade)
    
    return {
        "title": title or "(no title found)",
        "org": org,
        "grade": grade,
        "location": location,
        "deadline": deadline,
        "hard_exclude": country_exclude or intern_exclude or national_exclude or junior_exclude,
        "exclude_reason": ("ukraine" if country_exclude else
                          "internship" if intern_exclude else
                          "national/gs" if national_exclude else
                          "junior" if junior_exclude else "")
    }

passed = []
failed = []

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    
    for idx, jid in enumerate(NEW_IDS):
        url = f"https://www.impactpool.org/jobs/{jid}"
        print(f"[{idx+1}/{len(NEW_IDS)}] IP_{jid}...", end=" ", flush=True)
        
        try:
            page.goto(url, wait_until="networkidle")
            time.sleep(3)
            text = page.inner_text("body")
            
            meta = extract_metadata(text)
            meta["id"] = jid
            
            if meta["hard_exclude"]:
                print(f"❌ {meta['exclude_reason']} | {meta['title'][:60]} | {meta['grade'][:20]}")
                failed.append(meta)
            else:
                print(f"✅ | {meta['title'][:60]} | {meta['grade'][:20]} | {meta['org'][:20]}")
                
                # Save full JD
                slug = re.sub(r'[^a-zA-Z0-9]+', '_', meta['title'][:40]).strip('_')
                org_slug = re.sub(r'[^a-zA-Z0-9]+', '_', meta['org'][:15]).strip('_')
                fname = f"IP_{jid}_{org_slug}_{slug}.md"
                (RAW_DIR / fname).write_text(text)
                print(f"    -> saved {fname} ({len(text)} chars)")
                
                passed.append(meta)
        
        except Exception as e:
            print(f"⚠️ ERROR: {e}")
            failed.append({"id": jid, "error": str(e)})
        
        # Restart logic removed - Camoufox handles within-session tab creation
        pass
        
    print(f"\n\n=== RESULTS ===")
    print(f"Total new IDs: {len(NEW_IDS)}")
    print(f"Passed pre-filter: {len(passed)}")
    print(f"Failed/filtered: {len(failed)}")
    
    print(f"\nPASSED JOBS:")
    for p in passed:
        print(f"  IP_{p['id']} | {p['title'][:70]} | {p['grade'][:20]} | {p['org'][:20]}")
    
    print(f"\nFILTERED OUT:")
    for f in failed:
        reason = f.get('exclude_reason', f.get('error', 'unknown'))
        print(f"  IP_{f['id']} | {reason} | {f.get('title', '')[:50]}")