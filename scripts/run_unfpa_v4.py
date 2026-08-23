#!/usr/bin/env python3
"""UNFPA v4 — Oracle HCM scraper using Playwright.

Listing: https://www.unfpa.org/jobs
Detail: estm.fa.em2.oraclecloud.com/sites/CX_2003/ (Oracle HCM)
"""
import re, html as html_mod, urllib.parse
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_UNFPA"
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
    "information management", "data processing", "technical consultant",
    "monitoring and evaluation", "m&e", "evaluation",
]

# Use word boundaries for "intern" to avoid matching "International"
HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|programme assistant|project associate|"
    r"horticulture|gardener|multimedia)", re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_TITLE_KW)


def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"UNFPA v4 Oracle HCM scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        page.goto("https://www.unfpa.org/jobs", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        jobs = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href*="unfpa.org/jobs/"]').forEach(a => {
                const href = a.href;
                if (href && !seen.has(href) && !href.includes('#') && 
                    href !== 'https://www.unfpa.org/jobs' &&
                    a.innerText.trim().length > 5) {
                    seen.add(href);
                    const card = a.closest('[class*="job"], [class*="item"], li, article, div');
                    const applyLink = card?.querySelector('a[href*="estm.fa.em2.oraclecloud.com"]');
                    results.push({
                        title: a.innerText.trim().split('\\n')[0].trim(),
                        unfpaUrl: href,
                        oracleUrl: applyLink?.href || ''
                    });
                }
            });
            return results;
        }
        """)
        
        print(f"Jobs found: {len(jobs)}")
        
        ict_jobs = []
        for j in jobs:
            title = j['title']
            if is_ict_title(title) or not HARD_REJECT.search(title):
                ict_jobs.append({'title': title, 'oracleUrl': j['oracleUrl'], 'unfpaUrl': j['unfpaUrl']})
                print(f"  ICT: {title[:70]}")
            else:
                print(f"  skip: {title[:60]}")
        
        print(f"\nICT jobs: {len(ict_jobs)}")
        
        saved = 0
        for job in ict_jobs:
            title = job['title']
            href = job['oracleUrl'] if job['oracleUrl'] else job['unfpaUrl']
            
            job_id_match = re.search(r'requisitionDetail/(\d+)', href) or re.search(r'requisition/(\d+)', href)
            job_id = job_id_match.group(1) if job_id_match else sanitize(title)[:20]
            
            out = DIR / f"UNFPA_{job_id}_{sanitize(title)[:50]}.md"
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
                    if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements', 'qualifications', 'duties', 'overview', 'job info', 'background', 'objective', 'about this role']):
                        jd_start = i
                        break
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else text
                
                if len(jd_text) < 500:
                    print(f"    SHORT ({len(jd_text)} chars), trying UNFPA URL...")
                    detail.close()
                    if job['unfpaUrl'] and job['unfpaUrl'] != href:
                        detail = browser.new_page()
                        detail.set_default_timeout(60000)
                        detail.goto(job['unfpaUrl'], wait_until="networkidle")
                        detail.wait_for_timeout(5000)
                        text = detail.inner_text("body")
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        jd_text = '\n'.join(lines)
                        if len(jd_text) < 500:
                            print(f"    SHORT ({len(jd_text)} chars), skipping")
                            detail.close()
                            continue
                    else:
                        continue
                
                if not is_ict_body(jd_text):
                    print(f"    SKIP: body not ICT ({title[:40]})")
                    detail.close()
                    continue

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
    
    total = len(list(DIR.glob("UNFPA_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
