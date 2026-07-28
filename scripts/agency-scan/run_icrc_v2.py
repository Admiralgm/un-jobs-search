#!/usr/bin/env python3
"""ICRC SuccessFactors — FIXED v2.0 — fetches individual JD pages."""
import asyncio, re
from datetime import datetime, date
from pathlib import Path
from scrapling.fetchers import StealthyFetcher

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_ICRC"

HARD_REJECT = re.compile(
    r"(intern|stagiaire|volunteer|unpaid|nutrition|agricultur|wash|civil engineer|"
    r"shelter|procurement|human rights|medical|doctor|nurse|midwife|teacher|pedagog|"
    r"child protection|gender|accountant|finance officer|budget officer|audit|hr officer|"
    r"human resources|admin officer|logistics|supply chain|warehouse|fleet|"
    r"security officer|driver|interpreter|translator|cook|cleaner|maintenance|"
    r"electrician|plumber|junior professional|jpo)", re.I)

ICT_KW = [
    " it "," ict "," isp "," ai "," artificial "," telecom "," connectivity ",
    " innovation ","information technology","chief technology"," cto "," chief information ",
    " cio "," digital transformation "," digital officer "," systems administrator ",
    " network engineer "," network administrator "," software engineer "," software developer ",
    " data engineer "," data scientist "," cybersecurity "," information security "," devops ",
    " cloud engineer "," cloud architect "," database administrator "," web developer ",
    " full stack "," machine learning "," deep learning "," solutions architect ",
    " enterprise architect "," technical lead ","it officer","it specialist","it manager",
    "ict officer","ict specialist","ict coordinator","ai engineer","ai research",
    "telecommunications","innovation officer","digital specialist","digital officer",
    "digital advisor","tech lead","technology officer","technology specialist",
    "system administrator","systems engineer","platform engineer","fullstack",
    "front-end developer","backend developer","cloud computing","data analyst",
    "data analytics","business intelligence","information management",
    "infrastructure engineer","site reliability","devsecops","machine learning engineer",
    "natural language processing","computer vision","robotics","automation engineer",
    "blockchain","microservices","api developer","integration engineer",
    "middleware","erp consultant","crm consultant","business analyst it","it project manager",
    "it director","head of it","head of digital","chief digital","digital innovation",
    "emerging technology","technology strategy","it strategy","it governance",
    "information systems","gis specialist","geospatial","spatial data",
    "data warehouse","data lake","etl developer","bi developer",
    "database developer","sql developer","python developer","java developer",
    "javascript developer","web application","mobile developer","app developer",
    "technology for development","digital development","digital health","e-health",
    "mhealth","telemedicine","fintech","digital finance","mobile money",
    "internet of things","iot developer","embedded systems","firmware engineer",
    "data center","network operations","noc engineer","it support","help desk",
    "technical support it","digital platform","platform developer","cyber","software","data","cloud","digital","technology"
]

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_KW)

def is_ict_full(title, body):
    return any(kw in (title + " " + body[:1000]).lower() for kw in ICT_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def clean_expired():
    if not DIR.exists(): return 0
    today = date.today(); removed = 0
    for f in DIR.glob("ICRC_*.md"):
        try:
            m = re.search(r'(?:closing|deadline|application\s+deadline)\s*[:\\s]*\s*(\d{4}-\d{2}-\d{2}|\w+\s+\d+,?\s+\d{4})', f.read_text("utf-8", errors="ignore"), re.I)
            if m:
                raw = m.group(1).replace(',', '')
                try:
                    dl = datetime.strptime(raw, "%Y-%m-%d").date()
                    if dl < today: f.unlink(); removed += 1
                except: pass
        except: pass
    return removed

def load_existing_ids():
    ids = set()
    for f in DIR.glob("ICRC_*.md"):
        parts = f.stem.split("_", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            ids.add(parts[1])
    return ids

async def fetch_page(url, wait=5000):
    try:
        page = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=wait)
        if page.status == 200: return page
    except: pass
    return None

async def main():
    DIR.mkdir(exist_ok=True)
    print(f"ICRC v2.0 — {datetime.now():%Y-%m-%d %H:%M:%S}")
    r = clean_expired(); print(f"Expired removed: {r}")
    existing = load_existing_ids(); print(f"Existing: {len(existing)}")

    all_jobs = {}
    KEYWORDS = ["Digital", "IT", "Data", "Innovation", "Technology", "Cyber"]
    
    for kw in KEYWORDS:
        list_url = f"https://careers.icrc.org/search/?q={kw}"
        page = await fetch_page(list_url)
        if not page: print(f"  kw={kw}: fetch failed"); continue
        
        html = page.html_content
        # ICRC SF: /job/Title-slug/123456/
        links = re.findall(r'href="(/job/[^"]+/(\d+)/?)"', html)
        
        new_count = 0
        for url_path, jid in links:
            if jid not in all_jobs and jid not in existing and len(jid) > 3:
                slug_m = re.search(r'/job/([^/]+)', url_path)
                title = slug_m.group(1).replace('-', ' ').strip() if slug_m else f"ICRC-{jid}"
                if len(title) > 10:
                    all_jobs[jid] = (title, url_path)
                    new_count += 1
        print(f"  kw={kw}: {len(links)} links, {new_count} new")
    
    print(f"\nTotal unique jobs: {len(all_jobs)}")
    ict_jobs = [(j, t, u) for j, (t, u) in all_jobs.items() if is_ict_title(t)]
    print(f"ICT-title candidates: {len(ict_jobs)}")
    
    saved = 0
    sem = asyncio.Semaphore(3)
    
    async def fetch_job(jid, title, url):
        full_url = f"https://careers.icrc.org{url}"
        try:
            async with sem:
                page = await fetch_page(full_url, wait=4000)
            if not page: return None
            text = page.get_all_text()
            return text if len(text) >= 500 else None
        except: return None
    
    for i in range(0, len(ict_jobs), 6):
        batch = ict_jobs[i:i+6]
        tasks = [fetch_job(j, t, u) for j, t, u in batch]
        results = await asyncio.gather(*tasks)
        for idx, text in enumerate(results):
            jid, title, url = batch[idx]
            if not text: continue
            if not is_ict_full(title, text): continue
            out = DIR / f"ICRC_{jid}_{sanitize(title)[:60]}.md"
            if out.exists(): continue
            header = f"# {title}\n\n**Job ID:** {jid}\n**URL:** https://careers.icrc.org{url}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n"
            out.write_text(header + text, encoding="utf-8")
            saved += 1; print(f"  SAVED: {jid} — {title[:60]}")
    
    print(f"\nDONE: {saved} new JDs, total: {len(list(DIR.glob('ICRC_*.md')))}")

if __name__ == "__main__":
    asyncio.run(main())
