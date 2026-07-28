#!/usr/bin/env python3
"""WMO Oracle HCM scraper — uses API interception + detail page fetching.

Portal: estm.fa.em2.oraclecloud.com (Oracle HCM / SuccessFactors)
API: /hcmRestApi/resources/latest/recruitingCEJobRequisitions returns job list in requisitionList.
Detail pages: /jobs/preview/<id>
"""
import re, html as html_mod, json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_WMO"
DIR.mkdir(exist_ok=True)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "full stack", "fullstack", "devops", "machine learning",
    "computer", "web", "database", "infrastructure", "security", "geospatial",
    "gis", "metadata", "api ", "microservices", "blockchain", "iot", "automation",
    "robotics", "middleware", "project officer", "early warning", "scientific officer",
]

HARD_REJECT = re.compile(
    r"(human resources|hr officer|consultancy.*météorologie|consultancy.*meteorolog|"
    r"support institutionnel|administrative|executive assistant|driver|cleaner)", re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"WMO Oracle HCM scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        # Get job list via API interception
        api_data = []
        def handle_response(response):
            if 'recruitingCEJobRequisitions' in response.url:
                try:
                    api_data.append(response.json())
                except:
                    pass
        
        page.on("response", handle_response)
        page.goto("https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_5001/jobs", wait_until="networkidle")
        page.wait_for_timeout(5000)
        
        # Extract jobs from API
        jobs = []
        for data in api_data:
            req_list = data.get('items', [{}])[0].get('requisitionList', [])
            for req in req_list:
                jobs.append({
                    'id': req.get('Id', ''),
                    'title': req.get('Title', ''),
                    'location': req.get('PrimaryLocation', ''),
                    'posted': req.get('PostedDate', ''),
                    'description': req.get('ShortDescriptionStr', ''),
                    'dept': req.get('Department', ''),
                })
        
        print(f"Jobs found: {len(jobs)}")
        for j in jobs:
            ict = "ICT" if is_ict_title(j['title']) else "skip"
            print(f"  [{ict}] {j['title'][:70]}")
        
        # Fetch detail pages for ICT jobs
        ict_jobs = [j for j in jobs if is_ict_title(j['title'])]
        print(f"\nICT jobs: {len(ict_jobs)}")
        
        saved = 0
        for job in ict_jobs:
            jid = job['id']
            title = job['title']
            out = DIR / f"WMO_{jid}_{sanitize(title)[:60]}.md"
            if out.exists():
                continue
            
            print(f"  Fetching: {title[:60]}...")
            try:
                detail = browser.new_page()
                detail.set_default_timeout(30000)
                detail.goto(f"https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_5001/jobs/preview/{jid}", wait_until="domcontentloaded")
                detail.wait_for_timeout(3000)
                
                text = detail.inner_text("body")
                
                # Extract JD section
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                jd_start = 0
                for i, line in enumerate(lines):
                    if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements', 'qualifications', 'duties', 'overview', 'about this role', 'key responsibilities', 'job info', 'background']):
                        jd_start = i
                        break
                
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else text
                
                header = (f"# {title}\n\n"
                          f"**Job ID:** {jid}\n"
                          f"**Location:** {job['location']}\n"
                          f"**Posted:** {job['posted']}\n"
                          f"**Department:** {job['dept']}\n"
                          f"**URL:** https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_5001/jobs/preview/{jid}\n"
                          f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"    SAVED: {len(jd_text)} chars")
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("WMO_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
