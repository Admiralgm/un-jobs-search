#!/usr/bin/env python3
"""UNDP v4 — Oracle HCM scraper using API interception + detail pages.

Portal: jobs.undp.org/cj_view_jobs.cfm (listing page)
Oracle HCM: estm.fa.em2.oraclecloud.com/sites/CX_1 (detail pages)
API: /hcmRestApi/resources/latest/recruitingCEJobRequisitions returns job list.
Detail pages: /hcmUI/CandidateExperience/en/sites/CX_1/requisitionDetail/<id>
"""
import re, html as html_mod, json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_UNDP"
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
]

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|programme assistant|project associate)", re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_TITLE_KW)


def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"UNDP v4 Oracle HCM scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        # Get job links from listing page
        page.goto("https://jobs.undp.org/cj_view_jobs.cfm", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        # Extract unique job links and titles from the listing page
        all_links = page.evaluate("""
        () => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href*="estm.fa.em2.oraclecloud.com"]').forEach(a => {
                const href = a.href;
                if (!seen.has(href)) {
                    seen.add(href);
                    // Get title from nearby text - the link text or row text
                    const row = a.closest('tr');
                    let title = a.innerText.trim();
                    if (!title || title.length < 5) {
                        title = row?.innerText?.trim()?.substring(0, 150) || '';
                    }
                    results.push({href: href, title: title});
                }
            });
            return results;
        }
        """)
        
        print(f"Jobs found: {len(all_links)}")
        
        # Filter ICT
        ict_jobs = []
        for j in all_links:
            title = j['title']
            # Clean up title - extract just the job title part
            # UNDP titles often have format: "Title\tGrade\tDate\tLocation"
            clean_title = title.split('\t')[0].strip() if '\t' in title else title.split('\n')[0].strip()
            clean_title = re.sub(r'\s+(NPSA-\d+|P-\d+|D-\d+|FS-\d+).*', '', clean_title).strip()
            
            if is_ict_title(clean_title) or not HARD_REJECT.search(clean_title):
                ict_jobs.append({'href': j['href'], 'title': clean_title})
                print(f"  ICT: {clean_title[:70]}")
        
        print(f"\nICT jobs: {len(ict_jobs)}")
        
        # Fetch detail pages for ICT jobs
        saved = 0
        for job in ict_jobs:
            # Extract job ID from URL
            job_id_match = re.search(r'requisitionDetail/(\d+)', job['href'])
            if not job_id_match:
                job_id_match = re.search(r'requisition/(\d+)', job['href'])
            job_id = job_id_match.group(1) if job_id_match else sanitize(job['title'])[:20]
            
            out = DIR / f"UNDP_{job_id}_{sanitize(job['title'])[:50]}.md"
            if out.exists():
                continue
            
            print(f"  Fetching: {job['title'][:60]}...")
            try:
                detail = browser.new_page()
                detail.set_default_timeout(60000)
                detail.goto(job['href'], wait_until="domcontentloaded")
                detail.wait_for_timeout(5000)
                
                text = detail.inner_text("body")
                
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                jd_start = 0
                for i, line in enumerate(lines):
                    if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements', 'qualifications', 'duties', 'overview', 'about this role', 'key responsibilities', 'job info', 'background', 'objectives']):
                        jd_start = i
                        break
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else text
                
                if not is_ict_body(jd_text):
                    print(f"    SKIP: body not ICT ({job['title'][:40]})")
                    detail.close()
                    continue

                header = (f"# {job['title']}\n\n"
                          f"**Job ID:** {job_id}\n"
                          f"**URL:** {job['href']}\n"
                          f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"    SAVED: {len(jd_text)} chars")
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("UNDP_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
