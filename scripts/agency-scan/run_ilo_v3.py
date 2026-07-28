#!/usr/bin/env python3
"""ILO v3 — SuccessFactors JS SPA scraper using Playwright.

Portal: jobs.ilo.org (SuccessFactors)
Listing: /go/All-Jobs/2842101/
Detail: /job/<title>/<id>-en_GB

The listing page loads jobs via JS. Detail pages are also JS-rendered.
Use Playwright with networkidle wait.
"""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_ILO"
DIR.mkdir(exist_ok=True)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "full stack", "fullstack", "devops", "machine learning",
    "computer", "web", "database", "infrastructure", "security", "geospatial",
    "gis", "metadata", "api ", "microservices", "blockchain", "iot", "automation",
    "robotics", "middleware", "erp", "crm", "business intelligence", "bi developer",
    "etl", "data warehouse", "data lake", "site reliability", "statistics",
    "statistician", "data science", "data engineer", "data architect",
    "data management", "data officer", "data analyst", "data governance",
    "digital transformation", "enterprise", "informatics", "informatic",
    "technology", "information management", "knowledge management",
]

HARD_REJECT = re.compile(
    r"(intern|internship|stagiaire|volunteer|unpaid|nutrition|agricultur|"
    r"medical|doctor|nurse|midwife|teacher|pedagog|child protection|gender|"
    r"accountant|finance|budget|audit|hr |human resources|admin|logistics|"
    r"supply|warehouse|fleet|security|driver|interpreter|translator|cook|"
    r"cleaner|electrician|plumber|wash|protocol|programme assistant|project assistant|"
    r"procurement|admin assistant|administrative|labour law|auditor|project coordinator|"
    r"project officer|project assistant|monitoring and evaluation)", re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"ILO v3 Playwright scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        
        # Get listing page
        page = browser.new_page()
        page.set_default_timeout(60000)
        page.goto("https://jobs.ilo.org/go/All-Jobs/2842101/", wait_until="networkidle")
        page.wait_for_timeout(8000)
        
        # Get job links
        jobs = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href*="/job/"]').forEach(a => {
                const href = a.href || a.getAttribute('href') || '';
                if (href && !seen.has(href)) {
                    seen.add(href);
                    results.push({href: href, title: a.innerText.trim()});
                }
            });
            return results;
        }
        """)
        
        print(f"Jobs found: {len(jobs)}")
        for j in jobs:
            ict = "ICT" if is_ict_title(j['title']) else "skip"
            print(f"  [{ict}] {j['title'][:70]}")
        
        ict_jobs = [j for j in jobs if is_ict_title(j['title'])]
        print(f"\nICT jobs: {len(ict_jobs)}")
        
        # Fetch detail pages
        saved = 0
        for job in ict_jobs:
            title = job['title']
            href = job['href']
            
            # Extract job ID from URL
            job_id_match = re.search(r'/(\d+)-en_GB', href)
            job_id = job_id_match.group(1) if job_id_match else sanitize(title)[:20]
            
            out = DIR / f"ILO_{job_id}_{sanitize(title)[:50]}.md"
            if out.exists():
                continue
            
            print(f"  Fetching: {title[:60]}...")
            try:
                detail = browser.new_page()
                detail.set_default_timeout(60000)
                detail.goto(href, wait_until="networkidle")
                detail.wait_for_timeout(5000)
                
                text = detail.inner_text("body")
                
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                jd_start = 0
                for i, line in enumerate(lines):
                    if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements', 'qualifications', 'duties', 'overview', 'about this role', 'key responsibilities', 'job info', 'background', 'objective']):
                        jd_start = i
                        break
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else text
                
                header = (f"# {title}\n\n"
                          f"**Job ID:** {job_id}\n"
                          f"**URL:** {href}\n"
                          f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"    SAVED: {len(jd_text)} chars")
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("ILO_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
