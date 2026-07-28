#!/usr/bin/env python3
"""ICMPD v3 — Custom platform scraper using Playwright.

Portal: careers.icmpd.org
Detail: /Home/JobOpeningDetails?jobOpeningId=<id>
"""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_ICMPD"
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
    "technology officer", "technology analyst", "technology advisor",
    "information systems", "automation", "information management",
    "junior ict officer", "ict officer",
]

# Use word boundaries for "intern" to avoid matching "International"
HARD_REJECT = re.compile(
    r"(\bintern\b|\binternship\b|stagiaire|volunteer|unpaid|chauffeur|driver|cleaner|cook|"
    r"nutrition|agricultur|medical|doctor|nurse|midwife|teacher|pedagog|"
    r"child protection|gender|accountant|finance|budget|audit|\bhr\b|human resources|"
    r"admin|logistics|supply|warehouse|fleet|security|interpreter|translator|"
    r"protocol|programme assistant|project associate|procurement|admin assistant|"
    r"administrative|horticulture|gardener|midwifery|maternal|reproductive|"
    r"population|demograph\b|health systems\b|multimedia|"
    r"project officer|team assistant|executive officer|financial manager|"
    r"communication assistant|junior project officer)", re.I)

def is_ict_title(title):
    # Extract the title part before the vacancy code
    # Format: "VA26P112V01 - HR Information Systems & Automation Officer - IP3"
    clean = re.sub(r'^VA\d+P\d+V\d+\s*-\s*', '', title).strip()
    # Remove grade suffix
    clean = re.sub(r'\s*-\s*(IP\d|S\d|M\d|P\d|D\d|LP|S)$', '', clean).strip()
    t = " " + clean.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"ICMPD v3 Playwright scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        page.goto("https://careers.icmpd.org", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        # Get all job links
        jobs = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href*="JobOpeningDetails"]').forEach(a => {
                const href = a.href;
                if (href && !seen.has(href)) {
                    seen.add(href);
                    // Get the job title from the link text or nearby
                    const text = a.innerText.trim();
                    results.push({href: href, title: text});
                }
            });
            return results;
        }
        """)
        
        print(f"Jobs found: {len(jobs)}")
        
        ict_jobs = []
        for j in jobs:
            title = j['title']
            if is_ict_title(title):
                ict_jobs.append({'href': j['href'], 'title': title})
                print(f"  ICT: {title[:70]}")
            else:
                print(f"  skip: {title[:60]}")
        
        print(f"\nICT jobs: {len(ict_jobs)}")
        
        # Fetch detail pages
        saved = 0
        for job in ict_jobs:
            title = job['title']
            href = job['href']
            
            # Extract job ID
            job_id_match = re.search(r'jobOpeningId=(\d+)', href)
            job_id = job_id_match.group(1) if job_id_match else sanitize(title)[:20]
            
            out = DIR / f"ICMPD_{job_id}_{sanitize(title)[:50]}.md"
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
                    if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements', 'qualifications', 'duties', 'overview', 'about this role', 'key responsibilities', 'job info', 'background', 'objective', 'tasks']):
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
    
    total = len(list(DIR.glob("ICMPD_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
