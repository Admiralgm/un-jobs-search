#!/usr/bin/env python3
"""Targeted online deadline scraper for top-priority UN portals."""
import re, json, asyncio
from pathlib import Path
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
SEEN = set()
results = {}

def parse_date(date_str):
    """Parse various date formats."""
    date_str = date_str.strip()
    for fmt in ('%d %B %Y', '%d %b %Y', '%B %d, %Y', '%b %d, %Y', 
                '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            continue
    return None

async def scrape_who(vid):
    """Scrape WHO Taleo."""
    m = re.search(r'WHO[_-](\d+)', vid)
    if not m:
        return None
    who_num = m.group(1)
    try:
        url = f"https://careers.who.int/careersection/ex/jobdetail.ftl?job={who_num}"
        response = StealthyFetcher.async_fetch(url)
        text = response.text
        dl = re.search(r'(?i)closing\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
        if dl:
            return parse_date(dl.group(1))
    except Exception as e:
        pass
    return None

async def scrape_undp():
    """Scrape UNDP (direct job listing page)."""
    return None  # UNDP requires manual lookup, no job number in tracker

async def scrape_itu(vid):
    """Scrape ITU."""
    m = re.search(r'ITU[_-](\d+)', vid)
    if not m:
        return None
    itu_num = m.group(1)
    try:
        # ITU jobs: https://tjobs.itu.int/Public/default.aspx
        # Or via their portal
        url = f"https://tjobs.itu.int/Public/default.aspx"
        response = StealthyFetcher.async_fetch(url)
        text = response.text
        # Search for job reference
        # Hard to scrape, return None for now
        return None
    except:
        return None

async def scrape_worldbank(vid, title):
    """Scrape World Bank via search or direct URL."""
    # Try ID-based URL first
    m = re.search(r'WB[_-](\d+)', vid)
    if m:
        wb_id = m.group(1)
        # Try multiple World Bank careers URLs
        urls_to_try = [
            f"https://wb-1.wd103.myworkdayjobs.com/en-US/External/job/{wb_id}",
        ]
        # But Workday requires JS, use scrapling with headless
        for url in urls_to_try:
            try:
                response = StealthyFetcher.async_fetch(url)
                text = response.text
                # Look for deadline
                dl = re.search(r'(?i)(?:closing|application)\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
                if dl:
                    return parse_date(dl.group(1))
            except:
                pass
    return None

async def scrape_unicef(vid):
    """Scrape UNICEF careers."""
    m = re.search(r'UNICEF[_-]?(\d+)', vid)
    if not m:
        # Try bare numbers
        m = re.search(r'(\d{6})', vid)
    if m:
        unicef_num = m.group(1)
        try:
            url = f"https://jobs.unicef.org/en-us/listing/?job={unicef_num}"
            response = StealthyFetcher.async_fetch(url)
            text = response.text
            dl = re.search(r'(?i)closing\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
            if dl:
                return parse_date(dl.group(1))
            # Also try footnote style
            dl2 = re.search(r'(?i)deadline[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text)
            if dl2:
                return parse_date(dl2.group(1))
        except:
            pass
    return None

async def scrape_inspira(vid):
    """Scrape UN Secretariat INSPIRA."""
    m = re.search(r'(\d{6,})', vid)
    if m:
        job_id = m.group(1)
        try:
            url = f"https://careers.un.org/lbw/jobdetail.aspx?id={job_id}"
            response = StealthyFetcher.async_fetch(url)
            text = response.text
            dl = re.search(r'(?i)deadline\s+for\s+applications[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text)
            if dl:
                return parse_date(dl.group(1))
        except:
            pass
    return None

async def scrape_fao(vid):
    """Scrape FAO."""
    # FAO job IDs are long numbers
    m = re.search(r'(\d{5,})', vid)
    if m:
        try:
            url = f"https://jobs.fao.org/careersection/fao_external/jobdetail.ftl?job={m.group(1)}"
            response = StealthyFetcher.async_fetch(url)
            text = response.text
            dl = re.search(r'(?i)closing\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
            if dl:
                return parse_date(dl.group(1))
        except:
            pass
    return None

# ============================================================================
# MAIN: Scrape top TBD entries by priority
# ============================================================================
async def main():
    with open(WORKDIR / "full_deadline_extraction.json") as f:
        data = json.load(f)
    
    # Get TBD entries, highest scored first
    tbd = [v for v in data["vacancies"] if v.get("deadline") == "TBD"]
    tbd.sort(key=lambda v: -v.get("score", 0))
    
    print(f"Total TBD: {len(tbd)}")
    print(f"Scraping top 30...")
    
    for v in tbd[:30]:
        row = v["row"]
        org = v.get("org", "")
        title = v.get("title", "")
        vid = v.get("vid", "")
        score = v.get("score", 0)
        urgency = v.get("mark", "")
        
        print(f"\n[{row}] {urgency} {score} | {org} | {title[:40]} | VID={vid}")
        
        if not vid or vid == "**":
            print("  → No VID, skipping")
            continue
        
        dl = None
        if org == "WHO":
            dl = await scrape_who(vid)
        elif org == "UNICEF":
            dl = await scrape_unicef(vid)
        elif org == "World Bank":
            dl = await scrape_worldbank(vid, title)
        elif org == "UN Secretariat":
            dl = await scrape_inspira(vid)
        elif org == "FAO":
            dl = await scrape_fao(vid)
        
        if dl:
            results[row] = dl
            print(f"  ✓ FOUND: {dl}")
        else:
            print(f"  ✗ Not found")
    
    print(f"\n=== Results: {len(results)} deadlines found ===")
    for row, dl in results.items():
        print(f"  Row {row}: {dl}")
    
    with open(WORKDIR / "online_scraped_v2.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
