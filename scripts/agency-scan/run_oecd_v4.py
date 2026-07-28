#!/usr/bin/env python3
"""OECD v4 — SmartRecruiters scraper using Playwright.

Portal: careers.smartrecruiters.com/OECD
Detail: smartrecruiters.com/OECD/<id>-<slug>
"""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_OECD"
DIR.mkdir(exist_ok=True)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "intelligence", "connectivity", "platform", "technical", "engineer", "developer",
    "it ", " it", "ict ", " ict", "computer", "web", "database", "infrastructure",
    "security", "geospatial", "gis", "metadata", "api ", "automation", "analytics",
    "analyst", "data analyst", "data scientist", "data engineer", "technology",
    "information systems", "knowledge management",
]

HARD_REJECT = re.compile(
    r"(\bintern\b|\binternship\b|stagiaire|volunteer|unpaid|chauffeur|driver|cleaner|cook|"
    r"nutrition|agricultur|medical|doctor|nurse|midwife|teacher|pedagog|"
    r"child protection|gender|accountant|finance|budget|audit|\bhr\b|human resources|"
    r"admin|logistics|supply|warehouse|fleet|security|interpreter|translator|"
    r"protocol|programme assistant|project associate|procurement|admin assistant|"
    r"administrative|horticulture|gardener|midwifery|maternal|reproductive|"
    r"population|demograph\b|health systems\b|multimedia|event coord|facilities|"
    r"resource management|policy analyst|nuclear energy|gas and coal|markets division|"
    r"communication)", re.I)

def is_ict_title(title):
    # Remove location suffix like "Paris, France"
    clean = re.sub(r'\s*[\-\|]\s*.*$', '', title).strip()
    t = " " + clean.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def extract_job_id(href):
    m = re.search(r'/OECD/(\d{15,})', href)
    return m.group(1) if m else sanitize(href)[:20]

def main():
    print(f"OECD v4 SmartRecruiters scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        page.goto("https://careers.smartrecruiters.com/OECD", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        jobs = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href*="smartrecruiters.com/OECD/"]').forEach(a => {
                const href = a.href;
                if (href && !seen.has(href) && href.includes('/OECD/') && 
                    a.innerText.trim().length > 5 &&
                    !href.includes('careers.smartrecruiters.com/OECD$')) {
                    seen.add(href);
                    results.push({href: href, title: a.innerText.trim()});
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
        
        saved = 0
        for job in ict_jobs:
            title = job['title']
            href = job['href']
            job_id = extract_job_id(href)
            
            out = DIR / f"OECD_{job_id}_{sanitize(title)[:50]}.md"
            if out.exists():
                continue
            
            print(f"  Fetching: {title[:60]}...")
            try:
                detail = browser.new_page()
                detail.set_default_timeout(60000)
                detail.goto(href, wait_until="networkidle")
                detail.wait_for_timeout(5000)
                
                dtext = detail.inner_text("body")
                lines = [l.strip() for l in dtext.split('\n') if l.strip()]
                jd_start = 0
                for i, line in enumerate(lines):
                    if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements',
                        'qualifications', 'duties', 'overview', 'about this role', 'key responsibilities',
                        'job info', 'background', 'objective', 'what you\'ll do', 'your role']):
                        jd_start = i
                        break
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else dtext
                
                header = (f"# {title}\n\n**Job ID:** {job_id}\n**Organization:** OECD\n"
                          f"**URL:** {href}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"    SAVED: {len(jd_text)} chars")
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("OECD_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
