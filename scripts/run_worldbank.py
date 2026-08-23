#!/usr/bin/env python3
"""World Bank CSOD scraper — API interception + detail pages.

API: us.api.csod.com/rec-job-search/external/jobs
Detail: csod.com/ux/ats/careersite/1/home/requisition/<id>
"""
import re, html as html_mod, json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_WORLDBANK"
DIR.mkdir(exist_ok=True)

ICT_TITLE_KW = [
    "digital", "ict", "information technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "genai", "generative ai", "connectivity", "platform", "technical", "engineer",
    "developer", "database", "computer", "web", "infrastructure", "security",
    "automation", "analytics", "data analyst", "data scientist", "data engineer",
    "information systems", "machine learning", "ml engineer", "ai engineer",
    "technology", "tech", "service delivery", "sdlc", "agentic",
    "junior service delivery analyst",
]

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|accounting|environmental|water|"
    r"social development|transport|urban|education|health specialist|poverty|"
    r"governance|communications|public|external|investment officer|"
    r"investment analyst|mining|financial management|operations officer|"
    r"operations analyst|senior accounting|country office|skilled trade)", re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_TITLE_KW)


def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def fetch_detail(browser, url, job_id, title, location, posted, DIR):
    out = DIR / f"WB_{job_id}_{sanitize(title)[:50]}.md"
    if out.exists():
        return False
    
    print(f"  Fetching: {title[:60]}...")
    try:
        detail = browser.new_page()
        detail.set_default_timeout(60000)
        detail.goto(url, wait_until="networkidle")
        detail.wait_for_timeout(5000)
        
        dtext = detail.inner_text("body")
        lines = [l.strip() for l in dtext.split('\n') if l.strip()]
        jd_start = 0
        for i, line in enumerate(lines):
            if any(m in line.lower() for m in ['description', 'responsibilities', 'requirements',
                'qualifications', 'duties', 'overview', 'job info', 'background', 'objective',
                'about this role', 'key responsibilities', 'what you\'ll do', 'your role',
                'business purpose', 'job description', 'duties and responsibilities',
                'organizational context']):
                jd_start = i
                break
        jd_text = '\n'.join(lines[jd_start:]) if jd_start > 0 else dtext
        
        if len(jd_text) < 300:
            print(f"    SHORT ({len(jd_text)} chars), using full page text")
            jd_text = dtext
        
        if not is_ict_body(jd_text):
            print(f"    SKIP: body not ICT ({title[:40]})")
            detail.close()
            return False

        header = (f"# {title}\n\n**Job ID:** {job_id}\n**Organization:** World Bank\n"
                  f"**Location:** {location}\n**Posted:** {posted}\n"
                  f"**URL:** {url}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
        out.write_text(header + jd_text, encoding="utf-8")
        print(f"    SAVED: {len(jd_text)} chars")
        detail.close()
        return True
    except Exception as e:
        print(f"    ERROR: {str(e)[:60]}")
        return False

def main():
    print(f"World Bank CSOD scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    all_jobs = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        
        for page_num in range(3):  # Get up to 75 jobs (25 per page)
            page = browser.new_page()
            page.set_default_timeout(60000)
            
            api_data = []
            def handle_response(response, data=api_data):
                if 'rec-job-search/external/jobs' in response.url:
                    try:
                        data.append(response.json())
                    except:
                        pass
            
            page.on("response", handle_response)
            offset = page_num * 25
            page.goto(f"https://worldbankgroup.csod.com/ux/ats/careersite/1/home?offset={offset}",
                      wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            for resp in api_data:
                if 'data' in resp and 'requisitions' in resp['data']:
                    for r in resp['data']['requisitions']:
                        loc_str = ''
                        if r.get('locations'):
                            loc_str = ', '.join([
                                f"{loc.get('city', '')}, {loc.get('country', '')}".strip(', ')
                                for loc in r['locations']
                            ])
                        all_jobs.append({
                            'id': r.get('requisitionId', ''),
                            'title': r.get('displayJobTitle', ''),
                            'location': loc_str,
                            'posted': r.get('postingEffectiveDate', ''),
                            'url': f"https://worldbankgroup.csod.com/ux/ats/careersite/1/home/requisition/{r.get('requisitionId', '')}",
                        })
            
            page.close()
        
        # Deduplicate
        seen_ids = set()
        unique_jobs = []
        for j in all_jobs:
            if j['id'] not in seen_ids and j['title']:
                seen_ids.add(j['id'])
                unique_jobs.append(j)
        
        print(f"Total unique jobs: {len(unique_jobs)}")
        
        ict_jobs = [j for j in unique_jobs if is_ict_title(j['title']) or not HARD_REJECT.search(j['title'])]
        print(f"Non-rejected jobs: {len(ict_jobs)}")
        for j in ict_jobs:
            print(f"  ICT: {j['title'][:70]}")
        
        saved = 0
        for job in ict_jobs:
            if fetch_detail(browser, job['url'], job['id'], job['title'], job['location'], job['posted'], DIR):
                saved += 1
        
        browser.close()
    
    total = len(list(DIR.glob("WB_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
