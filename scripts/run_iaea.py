#!/usr/bin/env python3
"""IAAEA Taleo scraper using Playwright.

Portal: iaea.taleo.net/careersection/ex/jobsearch.ftl
Detail: iaea.taleo.net/careersection/ex/jobdetail.ftl?job=<id>
"""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_IAEA"
DIR.mkdir(exist_ok=True)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "computer", "database", "infrastructure", "security", "geospatial",
    "gis", "metadata", "api ", "automation", "analytics", "data analyst", "data scientist",
    "data engineer", "information management", "knowledge management",
]

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|project manager|programme officer|research|"
    r"analyst|nuclear safety|radiation|inspector)", re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

ICT_BODY_KW = [
    "digital", "ict", "information technology", "cyber", "software", "data",
    "cloud", "network", "telecom", "telecommunications", "innovation", "ai ",
    "artificial intelligence", "connectivity", "platform", "engineer", "developer",
    "computer", "database", "infrastructure", "security", "geospatial", "gis",
    "metadata", "api ", "automation", "analytics", "information management",
    "knowledge management", "digital transformation", "digitalization",
    "digitalisation", "machine learning", "it systems", "it infrastructure",
    "it services", "information systems", "technology", "technical",
]

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_BODY_KW)


def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"IAEA Taleo scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        page.goto("https://iaea.taleo.net/careersection/ex/jobsearch.ftl", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        # Get job links - Taleo uses JavaScript to load jobs
        jobs = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href*="jobdetail"], a[href*="job="]').forEach(a => {
                const href = a.href || a.getAttribute('href') || '';
                const text = a.innerText.trim();
                if (href && text.length > 5 && !seen.has(href)) {
                    seen.add(href);
                    results.push({href: href, title: text});
                }
            });
            return results;
        }
        """)
        
        # If no links found, try table rows
        if not jobs:
            jobs = page.evaluate("""
            () => {
                const seen = new Set();
                const results = [];
                document.querySelectorAll('tr a, .career-table a, table a').forEach(a => {
                    const href = a.href || a.getAttribute('href') || '';
                    const text = a.innerText.trim();
                    if (href && text.length > 5 && !seen.has(href)) {
                        seen.add(href);
                        results.push({href: href, title: text});
                    }
                });
                return results;
            }
            """)
        
        print(f"Jobs found: {len(jobs)}")
        
        ict_jobs = [j for j in jobs if is_ict_title(j['title']) or not HARD_REJECT.search(j['title'])]
        print(f"Non-rejected jobs: {len(ict_jobs)}")
        
        saved = 0
        for job in ict_jobs:
            title = job['title']
            href = job['href']
            
            job_id_match = re.search(r'[?&]job=(\d+)', href)
            job_id = job_id_match.group(1) if job_id_match else sanitize(title)[:20]
            
            out = DIR / f"IAEA_{job_id}_{sanitize(title)[:50]}.md"
            if out.exists():
                continue
            
            print(f"  Fetching: {title[:60]}...")
            try:
                detail = browser.new_page()
                detail.set_default_timeout(60000)
                detail.goto(href, wait_until="domcontentloaded")
                detail.wait_for_timeout(5000)
                
                dtext = detail.inner_text("body")
                lines = [l.strip() for l in dtext.split('\n') if l.strip()]
                jd_start = 0
                for i, line in enumerate(lines):
                    if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements',
                        'qualifications', 'duties', 'overview', 'about this role']):
                        jd_start = i
                        break
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else dtext
                
                if not is_ict_body(jd_text):
                    print(f"    SKIP: body not ICT ({title[:40]})")
                    detail.close()
                    continue

                header = (f"# {title}\n\n**Job ID:** {job_id}\n**Organization:** IAEA\n"
                          f"**URL:** {href}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"    SAVED: {len(jd_text)} chars")
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("IAEA_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
