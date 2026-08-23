#!/usr/bin/env python3
"""UNHCR Workday scraper using Playwright.

Portal: unhcr.wd3.myworkdayjobs.com/en-GB/External
"""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_UNHCR"
DIR.mkdir(exist_ok=True)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "computer", "database", "infrastructure", "security",
    "geospatial", "gis", "api ", "automation", "analytics", "information management",
]

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|programme officer|project manager|research|"
    r"analyst|clerk|assistant|refugee|protection|resettlement|registration|field|"
    r"community|eligibility|camp)", re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_TITLE_KW)


def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"UNHCR Workday scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        page.goto("https://unhcr.wd3.myworkdayjobs.com/en-GB/External", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        jobs = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href || '';
                const text = a.innerText.trim();
                if (href && text.length > 5 && !seen.has(href) && 
                    (href.includes('/job/') || href.includes('requisition') || href.includes('detail'))) {
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
            job_id_m = re.search(r'/job/([^/]+)', href)
            job_id = job_id_m.group(1) if job_id_m else sanitize(title)[:20]
            
            out = DIR / f"UNHCR_{sanitize(job_id)}_{sanitize(title)[:50]}.md"
            if out.exists(): continue
            
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
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else '\n'.join(lines)
                
                if not is_ict_body(jd_text):
                    print(f"    SKIP: body not ICT ({title[:40]})")
                    detail.close()
                    continue

                header = (f"# {title}\n\n**Job ID:** {job_id}\n**Organization:** UNHCR\n"
                          f"**URL:** {href}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("UNHCR_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
