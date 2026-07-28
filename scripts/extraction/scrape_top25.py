#!/usr/bin/env python3
"""Scrape top 20 TBD entries via Camoufox browser.
Populates online_scraped_top20.json with deadlines.
"""
import re, json, requests
from pathlib import Path
from datetime import datetime

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
CAMOUFOX = "http://localhost:9377"

# Load vacancies
with open(WORKDIR / "full_deadline_extraction.json") as f:
    data = json.load(f)

results = {}

# Get top TBD entries
TBD = [v for v in data["vacancies"] if v.get("deadline") == "TBD"]
TBD.sort(key=lambda v: -v.get("score", 0))
print(f"Total TBD vacancies: {len(TBD)}")

def camoufox_navigate(url):
    """Navigate Camoufox to a URL, return rendered text."""
    try:
        r = requests.post(f"{CAMOUFOX}/navigate", json={"userId": "hermes-default", "url": url}, timeout=30)
        if r.status_code == 200:
            # Get snapshot
            r2 = requests.get(f"{CAMOUFOX}/snapshot", params={"userId": "hermes-default"}, timeout=15)
            if r2.status_code == 200:
                return r2.text
    except Exception as e:
        return f"Error: {e}"
    return None

def parse_date(date_str):
    """Parse date string to YYYY-MM-DD."""
    date_str = re.sub(r'[,.]', '', date_str).strip().replace("  ", " ")
    for fmt in ['%d %B %Y', '%d %b %Y', '%B %d %Y', '%b %d %Y', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(date_str, fmt)
            if 2025 <= dt.year <= 2028:
                return dt.strftime('%Y-%m-%d')
        except:
            continue
    return None

# ====== SCRAPE STRATEGIES BY ORG ======

for v in TBD[:25]:
    row = v["row"]
    org = v.get("org", "")
    title = v.get("title", "")
    vid = v.get("vid", "")
    score = v.get("score", 0)
    urgency = v.get("mark", "")
    
    print(f"\n=== [{row}] {urgency} {score} | {org} | {title[:50]} ===")
    print(f"VID='{vid}'")
    
    dl = None
    
    # ===== WHO =====
    if org == "WHO":
        m = re.search(r'WHO[_-]?(\d+)', vid)
        if m:
            who_num = m.group(1)
            url = f"https://careers.who.int/careersection/ex/jobdetail.ftl?job={who_num}"
            print(f"  Navigating: {url}")
            text = camoufox_navigate(url)
            if text:
                # Search for closing date
                m2 = re.search(r'(?i)closing\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
                if m2:
                    dl = parse_date(m2.group(1))
                    print(f"  ✓ FOUND: {dl}")
                else:
                    m3 = re.search(r'(?i)(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+202[567]', text)
                    if m3:
                        dl = parse_date(m3.group(0))
                        print(f"  ✓ FOUND (generic): {dl}")
                    else:
                        print(f"  ✗ No date found in page")
            else:
                print(f"  ✗ Camoufox returned empty")
    
    # ===== World Bank =====
    elif org == "World Bank":
        m = re.search(r'WB[_-]?(\d+)', vid)
        if m:
            wb_id = m.group(1)
            url = f"https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/{wb_id}"
            print(f"  Navigating: {url}")
            text = camoufox_navigate(url)
            if text:
                # Workday often shows deadline in body
                m2 = re.search(r'(?i)(?:closing|application)\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
                if m2:
                    dl = parse_date(m2.group(1))
                    print(f"  ✓ FOUND: {dl}")
                else:
                    m3 = re.search(r'(?i)(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+202[567]', text)
                    if m3:
                        dl = parse_date(m3.group(0))
                        print(f"  ✓ FOUND (generic): {dl}")
                    else:
                        print(f"  ✗ No date found")
    
    # ===== UNICEF =====
    elif org == "UNICEF":
        m = re.search(r'UNICEF[_-]?(\d{6})', vid)
        if not m:
            m = re.search(r'(\d{6})', vid)
        if m:
            unicef_num = m.group(1)
            url = f"https://jobs.unicef.org/en-us/listing/?job={unicef_num}"
            print(f"  Navigating: {url}")
            text = camoufox_navigate(url)
            if text:
                m2 = re.search(r'(?i)closing\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
                if m2:
                    dl = parse_date(m2.group(1))
                    print(f"  ✓ FOUND: {dl}")
    
    # ===== WFP =====
    elif org == "WFP":
        m = re.search(r'(\d{5,})', vid)
        if m:
            job_id = m.group(1)
            url = f"https://career5.successfactors.eu/career?career_ns=job_listing&company=C0000160000P&navBarLevel=JOB_SEARCH&jobId={job_id}"
            print(f"  Navigating: {url}")
            text = camoufox_navigate(url)
            if text:
                m2 = re.search(r'(?i)closing\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
                if m2:
                    dl = parse_date(m2.group(1))
                    print(f"  ✓ FOUND: {dl}")
    
    # ===== UN Secretariat =====
    elif org == "UN Secretariat":
        m = re.search(r'(\d{6,})', vid)
        if m:
            job_id = m.group(1)
            url = f"https://careers.un.org/lbw/jobdetail.aspx?id={job_id}"
            print(f"  Navigating: {url}")
            text = camoufox_navigate(url)
            if text:
                m2 = re.search(r'(?i)deadline\s+for\s+applications[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text)
                if m2:
                    dl = parse_date(m2.group(1))
                    print(f"  ✓ FOUND: {dl}")
    
    # ===== UNDP =====
    elif org == "UNDP":
        m = re.search(r'UNDP[_-]?(\d{5,})', vid)
        if m:
            undp_id = m.group(1)
            url = f"https://jobs.undp.org/careers/job/{undp_id}"
            print(f"  Navigating: {url}")
            text = camoufox_navigate(url)
            if text:
                m2 = re.search(r'(?i)(?:closing|deadline|apply\s+by)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
                if m2:
                    dl = parse_date(m2.group(1))
                    print(f"  ✓ FOUND: {dl}")
    
    # ===== FAO =====
    elif org == "FAO":
        m = re.search(r'(\d{5,})', vid)
        if m:
            fao_id = m.group(1)
            url = f"https://jobs.fao.org/careersection/fao_external/jobdetail.ftl?job={fao_id}"
            print(f"  Navigating: {url}")
            text = camoufox_navigate(url)
            if text:
                m2 = re.search(r'(?i)closing\s+date[:\n\r\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
                if m2:
                    dl = parse_date(m2.group(1))
                    print(f"  ✓ FOUND: {dl}")
    
    # ===== UNOPS =====
    elif org == "UNOPS":
        # UNOPS uses Workday too
        m = re.search(r'(\d{4,})', vid)
        if m:
            job_id = m.group(1)
            url = f"https://jobs.unops.org/jobs?jobId={job_id}"
            print(f"  Navigating: {url}")
            text = camoufox_navigate(url)
            if text:
                m2 = re.search(r'(?i)(?:closing|deadline)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
                if m2:
                    dl = parse_date(m2.group(1))
                    print(f"  ✓ FOUND: {dl}")
    
    if dl:
        results[row] = dl

# Save results
print(f"\n\n=== SCRAPING COMPLETE ===")
print(f"Deadlines found: {len(results)}")
for row, dl in results.items():
    print(f"  Row {row}: {dl}")

with open(WORKDIR / "online_scraped_top25.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"Saved to {WORKDIR}/online_scraped_top25.json")
