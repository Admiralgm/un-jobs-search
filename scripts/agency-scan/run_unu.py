#!/usr/bin/env python3
"""UNU careers scraper — careers.unu.edu (Indeed-based platform)."""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_UNU"
DIR.mkdir(exist_ok=True)

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|library|assistant|programme assistant|"
    r"adjunct professor|resource nexus)", re.I)

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
    "emerging tech", "risk modelling", "modelling",
]

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_TITLE_KW)


def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"UNU scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto("https://careers.unu.edu", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        try:
            page.get_by_text("AGREE TO ALL").click()
            page.wait_for_timeout(2000)
        except:
            pass
        
        jobs = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a').forEach(a => {
                if (a.href && a.href.includes('/o/') && (a.innerText.includes('VIEW JOB') || a.innerText.includes('View job'))) {
                    if (!seen.has(a.href)) {
                        seen.add(a.href);
                        const card = a.closest('[class*="job-card"], [class*="card"], li, article') || a.parentElement?.parentElement;
                        const lines = (card?.innerText || '').split('\\n').map(l => l.trim()).filter(l => l.length > 3 && l !== 'VIEW JOB' && l !== 'View job' && !l.includes('On-site') && !l.includes('Remote') && !l.includes(','));
                        const title = lines[0] || 'Unknown';
                        results.push({link: a.href, title: title});
                    }
                }
            });
            return results;
        }
        """)
        
        print(f"Jobs found: {len(jobs)}")
        for j in jobs:
            ict = "candidate" if not HARD_REJECT.search(j['title']) else "skip"
            print(f"  [{ict}] {j['title'][:70]}")
        
        ict_jobs = [(j['title'], j['link']) for j in jobs if is_ict_title(j['title']) or not HARD_REJECT.search(j['title'])]
        print(f"\nICT jobs: {len(ict_jobs)}")
        
        saved = 0
        for title, link in ict_jobs:
            job_slug = link.rstrip('/').split('/')[-1]
            safe_title = sanitize(title)[:50]
            out = DIR / f"UNU_{job_slug}_{safe_title}.md"
            if out.exists():
                continue
            
            print(f"  Fetching: {title[:60]}...")
            try:
                detail = browser.new_page()
                detail.set_default_timeout(30000)
                detail.goto(link, wait_until="domcontentloaded")
                detail.wait_for_timeout(3000)
                text = detail.inner_text("body")
                
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                jd_start = 0
                for i, line in enumerate(lines):
                    if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements', 'qualifications', 'duties', 'overview', 'about this role', 'key responsibilities']):
                        jd_start = i
                        break
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else text
                
                if not is_ict_body(jd_text):
                    print(f"    SKIP: body not ICT ({title[:40]})")
                    detail.close()
                    continue

                header = f"# {title}\n\n**URL:** {link}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n"
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"    SAVED: {len(jd_text)} chars")
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("UNU_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
