#!/usr/bin/env python3
"""IMO scraper using Playwright.

Portal: recruit.imo.org/vacancies
"""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_IMO"
DIR.mkdir(exist_ok=True)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "computer", "database", "infrastructure", "security",
    "geospatial", "gis", "api ", "automation", "analytics", "information management",
]

HARD_REJECT = re.compile(
    r"(\bintern\b|\binternship\b|stagiaire|volunteer|unpaid|chauffeur|driver|"
    r"cleaner|cook|nutrition|agricultur|medical|doctor|nurse|midwife|teacher|pedagog|"
    r"child protection|gender|accountant|finance|budget|audit|\bhr\b|human resources|"
    r"admin|logistics|supply|security|interpreter|translator|procurement|admin assistant|"
    r"administrative|midwifery|maternal|health systems\b|communication|policy|legal|"
    r"programme officer|research officer|analyst|clerk|assistant|"
    r"maritime|safety|marine|navigation|port|ship|seafarer)",
    re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"IMO scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        page.goto("https://recruit.imo.org/vacancies", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        jobs = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href || '';
                const text = a.innerText.trim();
                if (href && text.length > 5 && !seen.has(href) && 
                    (href.includes('job') || href.includes('vacanc') || href.includes('detail') || href.includes('opening'))) {
                    seen.add(href);
                    results.push({href: href, title: text});
                }
            });
            return results;
        }
        """)
        
        print(f"Jobs found: {len(jobs)}")
        
        ict_jobs = [j for j in jobs if is_ict_title(j['title'])]
        print(f"ICT jobs: {len(ict_jobs)}")
        
        saved = 0
        for job in ict_jobs:
            title = job['title']
            href = job['href']
            job_id_m = re.search(r'/(\d{5,})/', href)
            job_id = job_id_m.group(1) if job_id_m else sanitize(title)[:20]
            
            out = DIR / f"IMO_{job_id}_{sanitize(title)[:50]}.md"
            if out.exists(): continue
            
            try:
                detail = browser.new_page()
                detail.set_default_timeout(60000)
                detail.goto(href, wait_until="domcontentloaded")
                detail.wait_for_timeout(5000)
                dtext = detail.inner_text("body")
                lines = [l.strip() for l in dtext.split('\n') if l.strip()]
                jd_text = '\n'.join(lines)
                
                header = (f"# {title}\n\n**Job ID:** {job_id}\n**Organization:** IMO\n"
                          f"**URL:** {href}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("IMO_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
