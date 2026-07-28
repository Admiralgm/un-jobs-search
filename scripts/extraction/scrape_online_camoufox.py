#!/usr/bin/env python3
"""Scrape deadlines from UN portals via Camoufox REST API."""
import re, json, urllib.request, time
from datetime import datetime
from pathlib import Path

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
CAMOUFOX = "http://localhost:9377"

def request(method, path, data=None):
    """Call Camoufox REST API."""
    url = f"{CAMOUFOX}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def create_tab():
    """Create a new Camoufox tab."""
    t = request("POST", "/tabs", {"userId": "scraping", "sessionKey": "s1", "url": "https://example.com"})
    return t.get("tabId"), t

def navigate(tab_id, url):
    """Navigate to URL, with wait for JS render."""
    request("POST", f"/tabs/{tab_id}/navigate", {"url": url, "userId": "scraping"})
    time.sleep(12)  # Wait for JS render

def get_text(tab_id):
    """Get page innerText."""
    r = request("POST", f"/tabs/{tab_id}/evaluate", {
        "expression": "document.body.innerText",
        "userId": "scraping"
    })
    return r.get("result", "") if "result" in r else ""

def close_tab(tab_id):
    """Close tab."""
    try:
        request("DELETE", f"/tabs/{tab_id}")
    except:
        pass

def parse_date(text):
    """Extract deadline from page text."""
    patterns = [
        r'Closing date[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Deadline[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Apply by[:\s]+(\d{1,2}[/.-]\d{1,2}[/.-]\d{4})',
        r'Application deadline[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4})',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            ds = m.group(1).strip()
            for fmt in ['%d %B %Y', '%d %b %Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(ds, fmt)
                    if 2025 <= dt.year <= 2028:
                        return dt.strftime('%Y-%m-%d')
                except:
                    pass
    return None

# List of URLs to visit
jobs = [
    {"org": "ITU", "vid": "TU_1352319255", "title": "Software Developer and Metadata Engineer Consultant", 
     "url": "https://sbas.itu.int/jobs/1352319255", "priority": 1},
    {"org": "ITU", "vid": "TU_941800455", "title": "Home Based Disaster Preparedness Consultant", 
     "url": "https://sbas.itu.int/jobs/941800455", "priority": 1},
    {"org": "ITU", "vid": "TU_1335797655", "title": "Senior National Cybersecurity Strategy Consultant", 
     "url": "https://sbas.itu.int/jobs/1335797655", "priority": 1},
    {"org": "ITU", "vid": "TU_1335794555", "title": "Senior CIRT Technical and Operations Consultant", 
     "url": "https://sbas.itu.int/jobs/1335794555", "priority": 1},
    {"org": "ITU", "vid": "TU_993659455", "title": "Consultant on Smart Villages and Smart Islands", 
     "url": "https://sbas.itu.int/jobs/993659455", "priority": 1},
    {"org": "ITU", "vid": "TU_1348117555", "title": "Emerging Technology Consultant", 
     "url": "https://sbas.itu.int/jobs/1348117555", "priority": 1},
    {"org": "ITU", "vid": "TU_993610255", "title": "Consultant for Senior ICT/Digital Policy", 
     "url": "https://sbas.itu.int/jobs/993610255", "priority": 1},
    {"org": "ITU", "vid": "TU_1353420555", "title": "Innovation Ecosystem Consultant", 
     "url": "https://sbas.itu.int/jobs/1353420555", "priority": 1},
    {"org": "World Bank", "vid": "B_36827", "title": "AI Service Management Transformation", 
     "url": "https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/36827", "priority": 1},
    {"org": "World Bank", "vid": "WB_37019", "title": "Sr Digital Government Interoperability", 
     "url": "https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/37019", "priority": 1},
    {"org": "World Bank", "vid": "B_36825", "title": "AI Incident and Problem Management", 
     "url": "https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/36825", "priority": 1},
    {"org": "World Bank", "vid": "B_36831", "title": "AI Solutions Analyst", 
     "url": "https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/36831", "priority": 1},
    {"org": "World Bank", "vid": "B_36878", "title": "E T Temporary Junior Service", 
     "url": "https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/36878", "priority": 1},
    {"org": "World Bank", "vid": "WB_37070", "title": "Manager AI Analytics Digital", 
     "url": "https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/37070", "priority": 1},
    {"org": "World Bank", "vid": "WB_36998", "title": "Associate Platform Engineer", 
     "url": "https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/36998", "priority": 1},
    {"org": "ICRC", "vid": "CRC_1396968433", "title": "Belgrade Shared Services Centre Collections", 
     "url": "https://careers.icrc.org/job/BELGRADE-Shared-Services-Centre-Collections-Officer-Finance/1396968433/", "priority": 1},
    {"org": "ICRC", "vid": "CRC_1398855133", "title": "Geneva Executive Assistant", 
     "url": "https://careers.icrc.org/job/Geneva-Executive-Assistant--Information-Management/1398855133/", "priority": 1},
    {"org": "ICRC", "vid": "CRC_1397289933", "title": "Manila Data & Analytics Officer", 
     "url": "https://careers.icrc.org/job/Manila-Data---Analytics-Officer/1397289933/", "priority": 1},
    {"org": "ICRC", "vid": "CRC_1399107733", "title": "Kabul HR Data & Analytics Officer", 
     "url": "https://careers.icrc.org/job/Kabul-HR-Data---Analytics-Officer/1399107733/", "priority": 1},
    {"org": "WTO", "vid": "TO_JR104152-1", "title": "Digital Learning Technology Specialist", 
     "url": "https://careers.smartrecruiters.com/WTO/Digital-Learning-Technology-Specialist", "priority": 2},
    {"org": "UNIDO", "vid": "NIDO_1354561955", "title": "ICT Security Operations Officer P-3", 
     "url": "https://jobs.unido.org/job/1354561955", "priority": 1},
    {"org": "WFP", "vid": "WFP_JR123811", "title": "Senior Cybersecurity Specialist Network Security", 
     "url": "https://career5.successfactors.eu/career?career_ns=job_listing&company=C0000160000P&jobId=123811", "priority": 1},
    {"org": "WFP", "vid": "WFP_JR123812", "title": "Senior Cybersecurity Specialist Vulnerability", 
     "url": "https://career5.successfactors.eu/career?career_ns=job_listing&company=C0000160000P&jobId=123812", "priority": 1},
]

# Scrape
results = {}
failed = []

for i, job in enumerate(jobs):
    print(f"\n[{i+1}/{len(jobs)}] Scraping: {job['org']} — {job['title'][:40]}")
    
    tab_id, _ = create_tab()
    if not tab_id:
        print(f"  ✗ Failed to create tab")
        failed.append(job)
        continue
    
    try:
        navigate(tab_id, job["url"])
        text = get_text(tab_id)
        dl = parse_date(text)
        
        if dl:
            print(f"  ✓ Deadline: {dl}")
            results[job["vid"]] = dl
        else:
            # Try finding date-like text
            if len(text) > 0:
                # Show first 200 chars of text
                preview = text[:200].replace('\n', ' ')
                print(f"  ? No date found. Preview: {preview[:100]}...")
            else:
                print(f"  ✗ Empty page")
            failed.append(job)
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        failed.append(job)
    finally:
        close_tab(tab_id)
        time.sleep(2)

# Save results
print(f"\n\n=== SCRAPING RESULTS ===")
print(f"Success: {len(results)}/{len(jobs)}")
print(f"Failed: {len(failed)}")

print("\nDeadlines found:")
for vid, dl in results.items():
    print(f"  {vid}: {dl}")

if failed:
    print("\nFailed to scrape:")
    for job in failed:
        print(f"  {job['vid']} — {job['org']} — {job['title'][:40]}")

with open(WORKDIR / "online_scraped_deadlines.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {WORKDIR / 'online_scraped_deadlines.json'}")
