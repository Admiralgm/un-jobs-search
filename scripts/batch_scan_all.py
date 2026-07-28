#!/usr/bin/env python3
"""
UN Jobs Scanner - Camoufox Python serverless batch scraper
Scans ALL remaining UN career portals for ICT/AI job vacancies
"""
import subprocess
import json
import re
import sys
import os
import time
from datetime import datetime

WORKDIR = "~/Downloads/DATA_REPOSITORY/WORKDIR"
TRACKER_FILE = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt"
ARCHIVE_FILE = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_ARCHIVE.txt"

def load_existing_ids():
    ids = set()
    for fpath in [TRACKER_FILE, ARCHIVE_FILE]:
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r') as f:
            text = f.read()
        found = re.findall(r'\b(\d{5,})\b', text)
        ids.update(found)
        found2 = re.findall(r'\b([A-Z]{2,}-[\w/-]+)\b', text)
        ids.update(found2)
    return ids

def scrape_portal(name, url, wait_ms=8000):
    """Scrape a single portal using Camoufox Python serverless"""
    script = f'''
import sys, json, time
sys.path.insert(0, "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages")
try:
    from camoufox import Camoufox
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto("{url}")
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep({wait_ms/1000})
        
        # Extract jobs via JS
        jobs = page.evaluate("""
        () => {{
            var results = [];
            
            // Pattern 1: Taleo table rows
            var taleoRows = document.querySelectorAll('tr[valign="top"]');
            for(var r of taleoRows){{
                var link = r.querySelector('a[href*="jobdetail"]');
                if(!link) continue;
                var href = link.getAttribute('href');
                var title = link.textContent.trim();
                var idMatch = href.match(/job=([^&]+)/);
                var id = idMatch ? idMatch[1] : '';
                var cells = r.querySelectorAll('td');
                var loc = cells.length > 1 ? cells[1].textContent.trim() : '';
                var dead = cells.length > 2 ? cells[2].textContent.trim() : '';
                results.push({{title:title, id:id, location:loc, deadline:dead, source:'taleo'}});
            }}
            if(results.length > 0) return results;
            
            // Pattern 2: Article-based listings (UNICEF, UNOPS)
            var articles = document.querySelectorAll('article');
            for(var art of articles){{
                var link = art.querySelector('a[href*="job"], a[href*="JobDetail"], a[href*="vacancy"]');
                if(!link) continue;
                var title = link.textContent.trim();
                var href = link.getAttribute('href');
                var idMatch = href.match(/(\d{4,})/);
                var id = idMatch ? idMatch[1] : '';
                results.push({{title:title, id:id, location:'', deadline:'', source:'article'}});
            }}
            if(results.length > 0) return results;
            
            // Pattern 3: Generic job links
            var links = document.querySelectorAll('a');
            var seen = new Set();
            for(var l of links){{
                var t = l.textContent.trim();
                var h = l.getAttribute('href') || '';
                if(t.length > 20 && t.length < 200 && (h.includes('job') || h.includes('vacancy') || h.includes('career')) && !seen.has(t)){{
                    seen.add(t);
                    var idMatch = h.match(/(\d{4,})/);
                    results.push({{title:t, id: idMatch ? idMatch[1] : '', location:'', deadline:'', source:'generic'}});
                }}
            }}
            return results;
        }}
        """)
        
        # Get total job count from page text
        var bodyText = page.inner_text("body");
        var countMatch = bodyText.match(/(\\d+)\\s*(jobs?|vacancies?|openings?|positions?)/i);
        var totalCount = countMatch ? parseInt(countMatch[1]) : jobs.length;
        
        print(json.dumps({{"jobs": jobs, "total": totalCount, "url": "{url}"}}))
except Exception as e:
    print(json.dumps({{"error": str(e), "jobs": []}}))
'''
    result = subprocess.run(
        ['/Library/Frameworks/Python.framework/Versions/3.13/bin/python3', '-c', script],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        return [], result.stderr
    try:
        data = json.loads(result.stdout)
        return data.get('jobs', []), data.get('error', '')
    except:
        return [], result.stdout[:500]

# All remaining portals to scan
PORTALS = [
    ("WHO_Taleo", "https://careers.who.int/careersection/ex/jobsearch.ftl"),
    ("UNOPS", "https://careers.unops.org/careersmarketplace/SearchJobs"),
    ("ILO", "https://jobs.ilo.org/go/All-Jobs/2842101/"),
    ("ITU", "https://jobs.itu.int"),
    ("ICRC", "https://careers.icrc.org/go/All-Jobs/3807301/"),
    ("FAO_Taleo", "https://jobs.fao.org/careersection/fao_external/jobsearch.ftl"),
    ("UNIDO", "https://careers.unido.org/search/?q=Digital"),
    ("UNESCO", "https://careers.unesco.org/search/?q=Digital"),
    ("UNHCR", "https://unhcr.wd3.myworkdayjobs.com/en-GB/External"),
    ("WFP", "https://wd3.myworkdaysite.com/recruiting/wfp/job_openings"),
    ("IMF", "https://imf.wd5.myworkdayjobs.com/IMF"),
    ("OECD", "https://careers.smartrecruiters.com/OECD"),
    ("WTO", "https://careers.smartrecruiters.com/WTO"),
    ("ICAO", "https://icaocareers.icao.int/careers/Home/Vacancies"),
    ("IMO", "https://recruit.imo.org"),
    ("ICMPD", "https://careers.icmpd.org"),
    ("UNITAR", "https://unitar.org/vacancy-announcements"),
    ("IFAD", "https://job.ifad.org/psc/IFHRPRDE/CAREERS/JOBS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U"),
    ("GICHD", "https://gichd.org/the-gichd/job-opportunities/"),
    ("UNFPA", "https://www.unfpa.org/jobs"),
    ("WIPO", "https://www.wipo.int/en/web/working-at-wipo/wipo-jobs"),
    ("WorldBank", "https://worldbankgroup.csod.com/ux/ats/careersite/1/home?c=worldbankgroup"),
    ("UNDP", "https://jobs.undp.org/cj_view_jobs.cfm"),
    ("UNJSPF", "https://www.unjspf.org/vacancies/"),
    ("OICT", "https://careers.un.org/"),
    ("ESCAP", "https://www.unescap.org/jobs"),
]

if __name__ == '__main__':
    existing_ids = load_existing_ids()
    print(f"Loaded {len(existing_ids)} existing tracker IDs")
    print(f"Starting batch scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scanning {len(PORTALS)} portals...")
    print("=" * 80)
    
    all_results = {}
    all_ict_jobs = []
    
    for idx, (name, url) in enumerate(PORTALS):
        print(f"\n[{idx+1}/{len(PORTALS)}] {name}: {url[:80]}...")
        try:
            jobs, error = scrape_portal(name, url)
            if error:
                print(f"  ERROR: {error[:100]}")
            else:
                print(f"  Found {len(jobs)} jobs")
                all_results[name] = jobs
                
                # Filter ICT jobs
                for j in jobs:
                    title = j.get('title', '').lower()
                    ict_kw = ['digital', 'data', 'software', 'ict', 'technology', 'innovation',
                              'ai', 'artificial intelligence', 'machine learning', 'engineer',
                              'developer', 'information systems', 'information management',
                              'cybersecurity', 'cloud', 'devops', 'platform', 'solutions',
                              'database', 'analytics', 'business intelligence', 'geospatial',
                              'gis', 'telecom', 'network', 'automation', 'robotics',
                              'computer', 'computing', 'informatics', 'connectivity',
                              'broadband', '5g', '4g', 'fiber', 'satellite', 'wireless',
                              'algorithm', 'nlp', 'computer vision', 'chatbot', 'generative',
                              'llm', 'large language', 'prompt engineer', 'ai engineer',
                              'digital transformation', 'e-government', 'ehealth', 'mhealth',
                              'learning management', 'lms', 'knowledge management',
                              'sharepoint', 'microsoft 365', 'm365', 'power platform',
                              'power bi', 'tableau', 'python', 'java', 'javascript',
                              'sql', 'nosql', 'docker', 'kubernetes', 'aws', 'azure',
                              'linux', 'security officer', 'information security', 'infosec',
                              'quality assurance', 'qa ', 'test automation',
                              'product owner', 'product manager', 'ux', 'user experience',
                              'web design', 'web development', 'statistics', 'statistical',
                              'statistician', 'research officer', 'microsoft 365']
                    
                    exclude_kw = ['health officer', 'nutrition', 'wash officer', 'education officer',
                                  'child protection', 'gender', 'human rights', 'legal officer',
                                  'finance officer', 'treasury', 'budget officer', 'audit',
                                  'human resources', 'hr officer', 'recruitment', 'staffing',
                                  'procurement', 'supply chain', 'logistics officer',
                                  'administrative', 'secretary', 'assistant to', 'driver',
                                  'nurse', 'doctor', 'physician', 'midwife', 'teacher',
                                  'agriculture', 'fisheries', 'forestry', 'shelter',
                                  'safeguarding', 'psea', 'protection officer',
                                  'fundraising', 'donor', 'partnership officer',
                                  'communication officer', 'public information', 'media officer',
                                  'junior professional', 'jpo', 'intern', 'volunteer',
                                  'nationals only', 'national consultant', 'ukraine']
                    
                    is_ict = any(k in title for k in ict_kw)
                    is_excluded = any(k in title for k in exclude_kw)
                    
                    if is_ict and not is_excluded:
                        jid = j.get('id', '')
                        is_new = jid not in existing_ids
                        marker = "NEW" if is_new else "known"
                        print(f"  [{marker}] {jid}: {j.get('title','')[:80]}")
                        all_ict_jobs.append({**j, 'portal': name, 'is_new': is_new})
        except Exception as e:
            print(f"  EXCEPTION: {e}")
        
        time.sleep(1)
    
    # Save results
    output_file = os.path.join(WORKDIR, 'batch_scan_results.json')
    with open(output_file, 'w') as f:
        json.dump({
            'scan_time': datetime.now().isoformat(),
            'portals_scanned': len(PORTALS),
            'all_results': all_results,
            'ict_jobs': all_ict_jobs
        }, f, indent=2, default=str)
    
    new_ict = [j for j in all_ict_jobs if j.get('is_new')]
    print(f"\n{'='*80}")
    print(f"SCAN COMPLETE")
    print(f"Total ICT jobs found: {len(all_ict_jobs)}")
    print(f"NEW ICT jobs: {len(new_ict)}")
    print(f"Results saved to: {output_file}")
    
    if new_ict:
        print(f"\nNew ICT jobs:")
        for j in new_ict:
            print(f"  [{j['portal']}] {j.get('id','')}: {j.get('title','')[:80]}")
