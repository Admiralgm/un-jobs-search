#!/usr/bin/env python3
"""WHO Taleo — use minimal listing fetch + detail pages"""
import asyncio, re
from datetime import datetime
from pathlib import Path
from scrapling.fetchers import StealthyFetcher

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_WHO"

ICT_KW_TITLE = [" ai "," digital "," data "," technology "," innovation "," software ",
    " cyber "," network "," system "," cloud "," engineer "," developer "," analyst ",
    " information "," it "," ict "," artificial "," telecom "," machine learning ",
    " chief technology "," chief information "," cto "," cio "," gis "," geospatial "]

ICT_KW_FULL = ICT_KW_TITLE + [" python "," java "," javascript "," database ",
    " web developer "," full stack "," devsecops "," cloud computing "," deep learning ",
    " natural language processing "," computer vision "," robotics "," blockchain ",
    " microservices "," api developer "," integration engineer "," middleware ",
    " data warehouse "," data lake "," etl "," business intelligence "]

def is_ict_title(title):
    t = " " + title.lower() + " "
    if re.compile(r"(intern|stagiaire|volunteer|unpaid|nutrition|agricultur|civil engineer|"
        r"shelter|procurement|human rights|medical|doctor|nurse|midwife|teacher|pedagog|"
        r"child protection|gender|accountant|finance|budget|audit|hr |human resources|"
        r"admin|logistics|supply|warehouse|fleet|security officer|driver|interpreter|"
        r"translator|cook|cleaner|electrician|plumber|wash|nutritionist|epidemiologist)", re.I).search(title):
        return False
    return any(kw in t for kw in ICT_KW_TITLE)

def is_ict_full(title, body):
    return any(kw in (title + " " + body[:1500]).lower() for kw in ICT_KW_FULL)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:55]

async def fetch_with_retry(url, retries=2):
    for attempt in range(retries):
        try:
            p = await StealthyFetcher.async_fetch(url, headless=True,
                disable_resources=True, wait=4000)
            if p.status == 200 and len(p.get_all_text()) >= 300:
                return p
        except:
            if attempt < retries - 1:
                await asyncio.sleep(2)
    return None

async def main():
    DIR.mkdir(exist_ok=True)
    print(f"WHO v1.1 — {datetime.now():%Y-%m-%d %H:%M:%S}")

    # Use Scrapling to get the listing page (just once)
    all_jobs = []
    seen_ids = set()

    list_url = "https://careers.who.int/careersection/ex/jobsearch.ftl"
    page = await fetch_with_retry(list_url)
    if not page:
        print("ERROR: Cannot fetch WHO listing page")
        return

    html = page.html_content
    links = re.findall(
        r'<a[^>]*href="(/careersection/ex/jobdetail\.ftl\?job=(\d+)[^"]*)"[^>]*>(.*?)</a>',
        html, re.S)

    for url_path, jid, raw in links:
        title = re.sub(r'<[^>]+>', '', raw).strip()
        if jid not in seen_ids and title and len(title) > 5:
            seen_ids.add(jid)
            all_jobs.append((jid, title, url_path))

    print(f"Jobs found: {len(all_jobs)}")

    # Filter by ICT title
    ict_jobs = [(j, t, u) for j, t, u in all_jobs if is_ict_title(t)]
    print(f"ICT: {len(ict_jobs)}")
    for j, t, u in ict_jobs:
        print(f"  {j}: {t[:65]}")

    # Fetch detail pages
    saved = 0
    existing = set(f.stem.split("_", 2)[1] for f in DIR.glob("WHO_*.md")
                   if f.stem.split("_", 2)[1].isdigit())

    for jid, title, url_path in ict_jobs:
        if jid in existing:
            continue
        full_url = f"https://careers.who.int{url_path}"
        p = await fetch_with_retry(full_url)
        if not p:
            print(f"  SKIP {jid}: fetch failed")
            continue
        text = p.get_all_text()
        if len(text) < 500:
            print(f"  SKIP {jid}: too short ({len(text)}b)")
            continue
        if not is_ict_full(title, text):
            continue
        out = DIR / f"WHO_{jid}_{sanitize(title)}.md"
        header = (f"# {title}\n\n**Job ID:** {jid}\n**URL:** {full_url}\n"
                  f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
        out.write_text(header + text, encoding="utf-8")
        saved += 1
        print(f"  SAVED: {title[:60]}")

    print(f"DONE: {saved} saved, total files: {len(list(DIR.glob('WHO_*.md')))}")

if __name__ == "__main__":
    asyncio.run(main())
