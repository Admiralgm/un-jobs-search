#!/usr/bin/env python3
"""Targeted online deadline scraper for top-priority UN job portals.
Uses multi-strategy: Scrapling, SearXNG, portal-specific formats.
"""
import re, json, asyncio
from pathlib import Path
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")

async def scrape_who_deadlines(vacancies):
    """Scrape WHO Taleo career pages."""
    results = {}
    base_url = "https://careers.who.int/careersection/ex/jobdetail.ftl?job={}"
    
    for v in vacancies:
        if v["org"] != "WHO":
            continue
        vid = v.get("vid", "")
        who_num = ""
        # Extract WHO number like 2600075 from WHO_2600075_...
        m = re.search(r'WHO[_-](\d+)', vid)
        if m:
            who_num = m.group(1)
        if not who_num:
            continue
        try:
            url = base_url.format(who_num)
            response = StealthyFetcher.async_fetch(url)
            text = response.text
            # Search for closing date
            dl = re.search(r'(?i)closing\s+date\s*[:\n\r]+\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
            if dl:
                date_str = dl.group(1).strip()
                for fmt in ('%b %d, %Y', '%B %d, %Y'):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        results[v["row"]] = dt.strftime('%Y-%m-%d')
                        break
                    except: pass
            # Also try direct ISO in page
            dl2 = re.search(r'(\d{4}-\d{2}-\d{2})', text)
            if v["row"] not in results and dl2:
                dt = datetime.strptime(dl2.group(1), '%Y-%m-%d')
                if 2025 <= dt.year <= 2027:
                    results[v["row"]] = dt.strftime('%Y-%m-%d')
        except Exception as e:
            pass
    return results

async def scrape_unicef_deadlines(vacancies):
    """Scrape UNICEF career pages."""
    results = {}
    # UNICEF jobs format: jobs.unicef.org/en-us/listing/?job=593483
    for v in vacancies:
        if v["org"] != "UNICEF":
            continue
        vid = v.get("vid", "")
        unicef_num = ""
        m = re.search(r'UNICEF[_-]?(\d+)', vid)
        if m:
            unicef_num = m.group(1)
        if not unicef_num:
            continue
        try:
            url = f"https://jobs.unicef.org/en-us/listing/?job={unicef_num}"
            response = StealthyFetcher.async_fetch(url)
            text = response.text
            # UNICEF often has "Closing Date" in body
            dl = re.search(r'(?i)closing\s+date\s*[:\n\r]+\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
            if dl:
                date_str = dl.group(1).strip()
                for fmt in ('%b %d, %Y', '%B %d, %Y'):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        results[v["row"]] = dt.strftime('%Y-%m-%d')
                        break
                    except: pass
        except Exception as e:
            pass
    return results

async def scrape_worldbank_deadlines(vacancies):
    """Scrape World Bank career pages."""
    results = {}
    # WB format: https://wb-1.wd103.myworkdayjobs.com/en-US/External/details/...
    for v in vacancies:
        if v["org"] != "World Bank":
            continue
        vid = v.get("vid", "")
        wb_id = ""
        # Formats: WB_36831_AI_Solutions_Analyst, etc
        m = re.search(r'WB[_-](\d+)', vid)
        if m:
            wb_id = m.group(1)
        if not wb_id:
            continue
        try:
            # Try multiple search formats
            url = f"https://wb-1.wd103.myworkdayjobs.com/en-US/External/details/.../{wb_id}"
            # Fallback: use search via careers page
            pass
        except Exception as e:
            pass
    return results

async def scrape_undp_deadlines(vacancies):
    """Scrape UNDP job pages."""
    results = {}
    # UNDP jobs: https://jobs.undp.org/cj_view_job.cfm?curJobId=...
    for v in vacancies:
        if v["org"] != "UNDP":
            continue
        vid = v.get("vid", "")
        undp_id = ""
        m = re.search(r'UNDP[_-]?(\d+)', vid)
        if m:
            undp_id = m.group(1)
        if not undp_id:
            continue
        try:
            url = f"https://jobs.undp.org/cj_view_job.cfm?curJobId={undp_id}"
            response = StealthyFetcher.async_fetch(url)
            text = response.text
            dl = re.search(r'(?i)application\s+deadline[:\n\r\s]+(\d{2}/\d{2}/\d{4})', text)
            if dl:
                dt = datetime.strptime(dl.group(1), '%m/%d/%Y')
                results[v["row"]] = dt.strftime('%Y-%m-%d')
        except Exception as e:
            pass
    return results

async def scrape_inspira_deadlines(vacancies):
    """Scrape UN Secretariat INSPIRA pages."""
    results = {}
    # INSPIRA: https://careers.un.org/lbw/jobdetail.aspx?id=...
    for v in vacancies:
        if v["org"] != "UN Secretariat":
            continue
        vid = v.get("vid", "")
        # Extract 6+ digit number
        m = re.search(r'(\d{6,})', vid)
        if not m:
            continue
        insp_id = m.group(1)
        try:
            url = f"https://careers.un.org/lbw/jobdetail.aspx?id={insp_id}"
            response = StealthyFetcher.async_fetch(url)
            text = response.text
            # Look for deadline text
            dl = re.search(r'(?i)deadline\s+for\s+applications[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text)
            if dl:
                date_str = dl.group(1).strip()
                for fmt in ('%d %B %Y', '%d %b %Y'):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        results[v["row"]] = dt.strftime('%Y-%m-%d')
                        break
                    except: pass
        except Exception as e:
            pass
    return results

# Main execution
if __name__ == "__main__":
    # Load current state
    with open(WORKDIR / "full_deadline_extraction.json") as f:
        data = json.load(f)
    
    vacancies = data["vacancies"]
    tbd = [v for v in vacancies if v["deadline"] == "TBD" and v["row"] <= 231]
    
    print(f"TBD entries to scrape: {len(tbd)}")
    
    # Run all scrapers
    results = {}
    
    print("\nScraping WHO...")
    who_results = asyncio.run(scrape_who_deadlines(tbd))
    print(f"  Found: {len(who_results)}")
    results.update(who_results)
    
    print("Scraping UNICEF...")
    unicef_results = asyncio.run(scrape_unicef_deadlines(tbd))
    print(f"  Found: {len(unicef_results)}")
    results.update(unicef_results)
    
    print("Scraping UNDP...")
    undp_results = asyncio.run(scrape_undp_deadlines(tbd))
    print(f"  Found: {len(undp_results)}")
    results.update(undp_results)
    
    print("Scraping UN Secretariat...")
    insp_results = asyncio.run(scrape_inspira_deadlines(tbd))
    print(f"  Found: {len(insp_results)}")
    results.update(insp_results)
    
    print(f"\n=== TOTAL NEW DEADLINES: {len(results)} ===")
    for row, dl in results.items():
        print(f"  Row {row}: {dl}")
    
    # Save results
    with open(WORKDIR / "online_scraped_deadlines.json", "w") as f:
        json.dump(results, f, indent=2)
