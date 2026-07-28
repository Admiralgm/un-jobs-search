#!/usr/bin/env python3
"""ICAO v3 — Oracle HCM scraper using API interception + detail pages.

Portal: estm.fa.em2.oraclecloud.com/sites/CX_3001/
API: /hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList
Detail: /hcmUI/CandidateExperience/en/sites/CX_3001/job/<id>
"""
import re, html as html_mod, json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_ICAO"
DIR.mkdir(exist_ok=True)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "computer", "cns", "atm", "communications", "navigation",
    "surveillance", "aviation safety", "air traffic management",
    "it engineer", "cns systems", "implementation planning",
]

HARD_REJECT = re.compile(
    r"(\bintern\b|\binternship\b|stagiaire|volunteer|unpaid|chauffeur|driver|cleaner|cook|"
    r"nutrition|agricultur|medical|doctor|nurse|midwife|teacher|pedagog|"
    r"child protection|gender|accountant|finance|budget|audit|\bhr\b|human resources|"
    r"admin|logistics|supply|warehouse|fleet|security|interpreter|translator|"
    r"protocol|programme assistant|project associate|procurement|admin assistant|"
    r"administrative|horticulture|gardener|midwifery|maternal|reproductive|"
    r"population|demograph\b|health systems\b|multimedia|communication officer|"
    r"administrative officer|executive assistant|events coordinator|events support|"
    r"auditeur|auditor|primary care|practitioner|air transport|airport financial|"
    r"airline fleet|airline operations|cabin safety|dangerous goods|personnel licensing|"
    r"aviation medicine|rescue and fire|wildlife management)",
    re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def main():
    print(f"ICAO v3 Oracle HCM scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        # Intercept the API to get job list
        api_data = []
        def handle_response(response):
            if 'recruitingCEJobRequisitions' in response.url and 'onlyData=true' in response.url:
                try:
                    api_data.append(response.json())
                except:
                    pass
        
        page.on("response", handle_response)
        page.goto("https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_3001/jobs",
                  wait_until="networkidle")
        page.wait_for_timeout(8000)
        
        # Extract jobs from API
        jobs = []
        for resp in api_data:
            req_list = resp.get('items', [{}])[0].get('requisitionList', [])
            for r in req_list:
                jobs.append({
                    'id': r.get('Id', ''),
                    'title': r.get('Title', ''),
                    'location': r.get('PrimaryLocation', ''),
                    'posted': r.get('PostedDate', ''),
                    'dept': r.get('Department', ''),
                    'oracleUrl': f"https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_3001/job/{r.get('Id', '')}",
                })
        
        print(f"Jobs found: {len(jobs)}")
        
        ict_jobs = [j for j in jobs if is_ict_title(j['title'])]
        print(f"ICT jobs: {len(ict_jobs)}")
        for j in ict_jobs:
            print(f"  ICT: {j['title'][:70]}")
        
        # Fetch detail pages
        saved = 0
        for job in ict_jobs:
            title = job['title']
            href = job['oracleUrl']
            job_id = job['id']
            
            out = DIR / f"ICAO_{job_id}_{sanitize(title)[:50]}.md"
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
                        'qualifications', 'duties', 'overview', 'job info', 'background', 'objective',
                        'about this role', 'key responsibilities']):
                        jd_start = i
                        break
                jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else dtext
                
                if len(jd_text) < 500:
                    # Try the ICAO careers page instead
                    icao_url = f"https://www.icao.int/about-icao/careers/Pages/JobDetail.aspx?JobId={job_id}"
                    print(f"    SHORT ({len(jd_text)} chars), trying ICAO careers page...")
                    detail.close()
                    detail = browser.new_page()
                    detail.set_default_timeout(60000)
                    detail.goto(icao_url, wait_until="networkidle")
                    detail.wait_for_timeout(5000)
                    dtext = detail.inner_text("body")
                    lines = [l.strip() for l in dtext.split('\n') if l.strip()]
                    jd_text = '\n'.join(lines)
                    if len(jd_text) < 500:
                        print(f"    Still SHORT ({len(jd_text)} chars), skipping")
                        detail.close()
                        continue
                
                header = (f"# {title}\n\n**Job ID:** {job_id}\n**Organization:** ICAO\n"
                          f"**Location:** {job['location']}\n**Posted:** {job['posted']}\n"
                          f"**URL:** {href}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"    SAVED: {len(jd_text)} chars")
                detail.close()
            except Exception as e:
                print(f"    ERROR: {str(e)[:60]}")
        
        page.close()
        browser.close()
    
    total = len(list(DIR.glob("ICAO_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
