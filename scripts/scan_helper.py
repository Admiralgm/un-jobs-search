#!/usr/bin/env python3
"""
UN Jobs Scanner - Batch extraction using Camoufox Python serverless
Scans multiple UN career portals for ICT/AI job vacancies
"""
import subprocess
import json
import re
import sys
import os
from datetime import datetime

WORKDIR = "~/Downloads/DATA_REPOSITORY/WORKDIR"
TRACKER_FILE = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt"
ARCHIVE_FILE = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_ARCHIVE.txt"

# Load existing IDs from tracker
def load_existing_ids():
    ids = set()
    for fpath in [TRACKER_FILE, ARCHIVE_FILE]:
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r') as f:
            text = f.read()
        # Extract IDs: numeric 4+ digits, or alphanumeric patterns like ICRC-xxx, ITU-xxx
        found = re.findall(r'\b(\d{5,})\b', text)
        ids.update(found)
        found2 = re.findall(r'\b([A-Z]{2,}-[\w-]+)\b', text)
        ids.update(found2)
    return ids

# ICT relevance keywords
ICT_KEYWORDS = [
    'digital', 'data', 'software', 'ict', 'technology', 'innovation',
    'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
    'information systems', 'information management', 'full-stack', 'fullstack',
    'developer', 'engineer', 'telecom', 'telecommunications', 'network',
    'cybersecurity', 'cyber', 'cloud', 'devops', 'platform', 'solutions architect',
    'database', 'big data', 'analytics', 'business intelligence', 'bi ',
    'geospatial', 'gis', 'geographic', 'remote sensing', 'robotics',
    'automation', 'rpa', 'blockchain', 'iot', 'internet of things',
    'web developer', 'frontend', 'front-end', 'backend', 'back-end',
    'system administrator', 'it officer', 'it manager', 'cio', 'cto',
    'data scientist', 'data engineer', 'data analyst',
    'application', 'app developer', 'mobile developer',
    'infrastructure', 'server', 'hosting', 'hosted',
    'erp', 'crm', 'sap', 'salesforce',
    'api', 'microservices', 'agile', 'scrum',
    'computer', 'computing', 'informatics',
    'connectivity', 'broadband', '5g', '4g', 'lte', 'fiber', 'fttx',
    'satellite', 'wireless', 'radio frequency', 'rf ',
    'algorithm', 'natural language', 'nlp', 'computer vision',
    'chatbot', 'conversational', 'generative', 'llm', 'large language',
    'prompt engineer', 'ai engineer', 'ai product',
    'digital transformation', 'digital health', 'digital education',
    'e-government', 'ehealth', 'e-health', 'mhealth', 'm-health',
    'learning management', 'lms', 'knowledge management',
    'sharepoint', 'microsoft 365', 'm365', 'power platform',
    'power bi', 'tableau', 'qlik',
    'python', 'java', 'javascript', 'react', 'angular', 'node',
    'sql', 'nosql', 'postgresql', 'mysql', 'mongodb',
    'docker', 'kubernetes', 'aws', 'azure', 'gcp',
    'linux', 'windows server', 'active directory',
    'security officer', 'information security', 'infosec',
    'technical support', 'help desk', 'service desk',
    'quality assurance', 'qa ', 'testing', 'test automation',
    'project manager it', 'it project', 'scrum master',
    'product owner', 'product manager', 'product management',
    'ux', 'user experience', 'ui ', 'user interface',
    'web design', 'web development',
    'broadcast', 'conferencing', 'video', 'multimedia',
    'statistics', 'statistical', 'statistician',
    'research officer', 'research fellow',  # only if combined with data/tech
    'monitoring and evaluation', 'm&e', 'mne',  # only if data/tech focused
]

# Exclusion keywords (health, admin, finance, etc.)
EXCLUDE_KEYWORDS = [
    'health officer', 'nutrition', 'wash officer', 'education officer',
    'child protection', 'gender', 'human rights', 'legal officer',
    'finance officer', 'treasury', 'budget officer', 'audit',
    'human resources', 'hr officer', 'recruitment', 'staffing',
    'procurement', 'supply chain', 'logistics officer',
    'administrative', 'secretary', 'assistant to',
    'driver', 'cleaner', 'security guard',
    'nurse', 'doctor', 'physician', 'midwife',
    'teacher', 'pedagogy', 'curriculum',
    'agriculture', 'fisheries', 'forestry',
    'shelter', 'camp coordination', 'displacement',
    'safeguarding', 'psea', 'protection officer',
    'fundraising', 'donor', 'partnership officer',
    'communication officer', 'public information', 'media officer',
    'junior professional', 'jpo', 'intern', 'volunteer',
    'nationals only', 'national consultant',
    'ukraine',  # exclude Ukraine-located
]

def is_ict_relevant(title):
    """Check if a job title is ICT-relevant"""
    title_lower = title.lower()
    
    # Check exclusions first
    for kw in EXCLUDE_KEYWORDS:
        if kw in title_lower:
            return False
    
    # Check ICT keywords
    for kw in ICT_KEYWORDS:
        if kw in title_lower:
            return True
    
    return False

def extract_jobs_from_unicef_page(output_text):
    """Extract jobs from UNICEF page text"""
    jobs = []
    # Parse job listings from the text output
    lines = output_text.split('\n')
    current_job = {}
    
    for line in lines:
        line = line.strip()
        if line.startswith('heading "') or line.startswith("- heading"):
            # Save previous job
            if current_job.get('title') and current_job.get('id'):
                jobs.append(current_job)
            # Extract title and ID
            title_match = re.search(r'heading "(.+?)"\s*(?:\[|$)', line)
            if not title_match:
                title_match = re.search(r'"(.+?)"\s*(?:\[|$)', line)
            title = title_match.group(1) if title_match else ''
            # Extract ID from title (#XXXXXX)
            id_match = re.search(r'#(\d{5,})', title)
            jid = id_match.group(1) if id_match else ''
            current_job = {'title': title, 'id': jid, 'url': f'https://jobs.unicef.org/en-us/job/{jid}' if jid else ''}
        elif 'Location:' in line and current_job:
            loc_match = re.search(r'Location:\s*(.+?)(?:\s*\[|$)', line)
            if loc_match:
                current_job['location'] = loc_match.group(1).strip()
        elif 'Deadline:' in line and current_job:
            deadline_match = re.search(r'Deadline:\s*(.+?)(?:\s*\[|$)', line)
            if deadline_match:
                current_job['deadline'] = deadline_match.group(1).strip()
    
    # Don't forget last job
    if current_job.get('title') and current_job.get('id'):
        jobs.append(current_job)
    
    return jobs

def run_camoufox_scrape(url, wait_ms=8000):
    """Run Camoufox Python serverless to scrape a JS-rendered page"""
    script = f'''
import sys
sys.path.insert(0, "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages")
try:
    from camoufox import Camoufox
    import time
    import json
    
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto("{url}")
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep({wait_ms / 1000})
        text = page.inner_text("body")
        print(text[:50000])  # Limit output
except Exception as e:
    print(f"ERROR: {{e}}", file=sys.stderr)
    print("FAILED")
'''
    result = subprocess.run(
        ['/Library/Frameworks/Python.framework/Versions/3.13/bin/python3', '-c', script],
        capture_output=True, text=True, timeout=120
    )
    return result.stdout, result.stderr

def run_web_preclean(url, max_chars=8000):
    """Run web-preclean.py for open-access portals"""
    result = subprocess.run(
        ['/Library/Frameworks/Python.framework/Versions/3.13/bin/python3',
         os.path.expanduser('config/scripts/web-preclean.py'),
         url, str(max_chars)],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout

def run_searxng(query, portal_domain=None):
    """Query SearXNG for cached job listings"""
    q = query
    if portal_domain:
        q = f"site:{portal_domain} {query}"
    url = f"http://localhost:8888/search?q={q}&format=json"
    result = subprocess.run(
        ['curl', '-s', url],
        capture_output=True, text=True, timeout=30
    )
    try:
        data = json.loads(result.stdout)
        return data.get('results', [])
    except:
        return []

if __name__ == '__main__':
    existing_ids = load_existing_ids()
    print(f"Loaded {len(existing_ids)} existing tracker IDs")
    print(f"Starting scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_new_jobs = []
    
    # We'll accumulate results and process them
    # This script is a helper - the main logic is in the agent
    
    print(f"\nExisting IDs sample: {list(existing_ids)[:10]}")
    print("Ready for portal scanning")
