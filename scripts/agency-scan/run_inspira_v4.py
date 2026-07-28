#!/usr/bin/env python3
"""INSPIRA v4.1 — uses the careers.un.org API directly (no browser).
Endpoint: /api/public/opening/jo/list/filteredV2/en
Properly extracts dutyStation, endDate (deadline), dept, jobLevel from listing response.
"""
import json, re, html as html_mod
from datetime import datetime
from pathlib import Path
import urllib.request, urllib.error, http.cookiejar, time

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_INSPIRA"
DIR.mkdir(exist_ok=True)

API_LIST = "https://careers.un.org/api/public/opening/jo/list/filteredV2/en"

HARD_REJECT = re.compile(
    r"(intern|stagiaire|volunteer|unpaid|nutrition|agricultur|wash|civil engineer|"
    r"shelter|procurement|human rights|medical|doctor|nurse|midwife|teacher|pedagog|"
    r"child protection|gender|accountant|finance officer|budget officer|audit|hr officer|"
    r"human resources|admin officer|logistics|supply chain|warehouse|fleet|"
    r"security officer|driver|interpreter|translator|cook|cleaner|maintenance|"
    r"electrician|plumber|junior professional|jpo)", re.I)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "full stack", "fullstack", "devops", "devsecops",
    "machine learning", "computer", "web", "database", "infrastructure", "security",
    "geospatial", "gis", "metadata", "api ", "microservices", "blockchain",
    "iot ", "automation", "robotics", "middleware", "erp ", "crm ", "business intelligence",
    "bi developer", "etl", "data warehouse", "data lake", "site reliability", "noc ", "isp ",
    "telecommunications", "broadband", "fiber", "fibre", "satellite", "mobile", "wireless",
    "help desk", "technical support", "it support", "it manager", "it director",
    "it officer", "it specialist", "it coordinator", "it project",
    "chief information", "chief technology", "chief digital", "cto", "cio",
    "head of it", "head of digital", "head of technology",
    "collaboration tech", "information management", "knowledge management",
    "learning solutions", "edtech", "educational technology", "device expert",
    "school connectivity", "agentic ai", "mcp", "generative ai", "llm",
    "prompt engineering", "vector database", "retrieval augmented", "digital ecosystem",
    "digital inclusion", "geospatial data science", "ai geospatial", "data science",
    "technology for development", "tech lead", "technical lead",
    "information systems", "systems assistant", "systems officer",
    "data management", "data officer", "data architect", "data engineer",
    "platform solution", "cloud engineer", "cloud architect",
]

ICT_FULL_KW = ICT_TITLE_KW + [
    "python", "java", "javascript", "sql", "nosql", "react", "angular", "vue",
    "node.js", "typescript", "html", "css", "rest api", "graphql", "azure", "aws", "gcp",
    "terraform", "ansible", "jenkins", "gitlab", "github", "ci/cd", "linux", "unix",
    "firewall", "vpn", "siem", "soc ", "zero trust", "identity and access", "iam ",
    "encryption", "deep learning", "neural network", "nlp", "computer vision",
    "power bi", "tableau", "qlik", "etl ", "data pipeline", "data integration",
    "data quality", "data governance", "solution architecture", "enterprise architecture",
    "digital transformation", "e-government", "e-health", "e-learning",
    "artificial intelligence", "generative ai", "agentic ai",
    "computer use", "api integration", "system integration", "infrastructure as code",
    "containerization", "site reliability engineering", "observability", "monitoring",
]

def clean_html(raw):
    text = re.sub(r'<br\s*/?>', '\n', raw)
    text = re.sub(r'</(div|p|li|tr|h[1-6])>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html_mod.unescape(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_FULL_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def load_existing_ids():
    ids = set()
    for f in DIR.glob("UN_*.md"):
        parts = f.stem.split("_", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            ids.add(parts[1])
    return ids

def api_post(url, data, opener):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    req.add_header("Referer", "https://careers.un.org/jobopening?language=en")
    req.add_header("Accept", "application/json")
    resp = opener.open(req, timeout=30)
    return json.loads(resp.read())

def extract_duty_station(ds):
    """Extract duty station string from API field."""
    if not ds:
        return ""
    if isinstance(ds, list):
        parts = []
        for item in ds:
            if isinstance(item, dict):
                desc = item.get("description", "")
                if desc and desc.upper() != "OTHER":
                    parts.append(desc)
            elif isinstance(item, str):
                parts.append(item)
        return ", ".join(parts) if parts else ""
    if isinstance(ds, dict):
        return ds.get("description", "")
    return str(ds)

def extract_grade(job_data):
    """Extract grade from jobLevel or postingTitle."""
    # Try jobLevel first (e.g. "G-5", "P-3")
    jl = job_data.get("jobLevel", "")
    if jl:
        m = re.search(r'([A-Z]-\d{1,2})', jl)
        if m:
            return m.group(1)
    # Try postingTitle (e.g. "INFORMATION SYSTEMS ASSISTANT, G5")
    pt = job_data.get("postingTitle", "")
    m = re.search(r',\s*([A-Z]\d{1,2}(?:/[A-Z]\d{1,2})*)\s*$', pt)
    if m:
        return m.group(1)
    return ""

def extract_deadline(job_data):
    """Extract deadline from endDate field."""
    end = job_data.get("endDate", "")
    if end:
        # Format: 2026-06-28T03:59:59.000Z
        m = re.match(r'(\d{4}-\d{2}-\d{2})', end)
        if m:
            return m.group(1)
    return ""

def main():
    print(f"INSPIRA v4.1 API scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    existing = load_existing_ids()
    print(f"Existing files: {len(existing)}")
    
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    
    # Step 1: Get all IST + ITECNET jobs via paginated API
    # CRITICAL: Query BOTH Job Family "IST" AND Job Network "ITECNET" because
    # many Consultant/CON roles are classified under IST job family but have
    # NO Job Network assignment. Querying ITECNET alone misses them.
    # Fix: 2026-07-27 — was missing ~6 Consultant roles posted with jf=IST but jn=empty
    all_jobs_raw = []
    all_jobs_titles = []
    seen_ids = set()
    
    # Query 1: Job Network ITECNET (staff/permanent ICT roles)
    page = 0
    while True:
        result = api_post(API_LIST, {
            "filterConfig": {"jn": ["ITECNET"], "jf": [], "jc": [], "jle": []},
            "pagination": {"page": page, "itemPerPage": 25, "sortBy": "startDate", "sortDirection": -1}
        }, opener)
        
        if result.get("status") != 1:
            print(f"API error: {result}")
            break
        
        data = result["data"]
        jobs = data.get("list", [])
        
        if not jobs:
            break
        
        for j in jobs:
            jid = str(j.get("jobId", ""))
            title = j.get("jobTitle", "") or j.get("postingTitle", "")
            if jid and title and jid not in seen_ids:
                seen_ids.add(jid)
                all_jobs_raw.append(j)
                all_jobs_titles.append((jid, title))
        
        print(f"  Page {page}: {len(jobs)} jobs")
        
        if len(jobs) < 25:
            break
        page += 1
        time.sleep(0.5)
    
    # Query 2: Job Family IST (catches Consultant/CON roles with no Job Network)
    print(f"\n--- Query 2: Job Family IST ---")
    page = 0
    while True:
        result = api_post(API_LIST, {
            "filterConfig": {"jn": [], "jf": ["IST"], "jc": [], "jle": []},
            "pagination": {"page": page, "itemPerPage": 25, "sortBy": "startDate", "sortDirection": -1}
        }, opener)
        
        if result.get("status") != 1:
            print(f"API error: {result}")
            break
        
        data = result["data"]
        jobs = data.get("list", [])
        
        if not jobs:
            break
        
        new_count = 0
        for j in jobs:
            jid = str(j.get("jobId", ""))
            title = j.get("jobTitle", "") or j.get("postingTitle", "")
            if jid and title and jid not in seen_ids:
                seen_ids.add(jid)
                all_jobs_raw.append(j)
                all_jobs_titles.append((jid, title))
                new_count += 1
        
        print(f"  Page {page}: {len(jobs)} jobs ({new_count} new)")
        
        if len(jobs) < 25:
            break
        page += 1
        time.sleep(0.5)
    print(f"\nTotal jobs fetched: {len(all_jobs_titles)}")
    for j, t in all_jobs_titles:
        print(f"  {j}: {t[:70]}")
    
    # Step 2: Filter by title
    ict_jobs = [(j, t) for j, t in all_jobs_titles if is_ict_title(t)]
    print(f"\nICT-title matches: {len(ict_jobs)}")
    
    maybe = [(j, t) for j, t in all_jobs_titles
             if (j, t) not in ict_jobs and not HARD_REJECT.search(t) and len(t) > 15]
    
    # Step 3: Process listing data (already has full descriptions)
    saved = 0
    skipped = 0
    for jid, title in ict_jobs + maybe:
        if jid in existing:
            skipped += 1
            continue
        
        # Find the full job data from listing
        job_data = None
        for j in all_jobs_raw:
            if str(j.get("jobId", "")) == jid:
                job_data = j
                break
        
        if not job_data:
            print(f"  SKIP {jid}: not found in listing data")
            continue
        
        desc_html = job_data.get("jobDescription", "")
        desc_text = clean_html(desc_html) if desc_html else ""
        
        if not desc_text or len(desc_text) < 200:
            print(f"  SKIP {jid}: no description (len={len(desc_text)})")
            continue
        
        if not is_ict_body(desc_text):
            continue
        
        posting_title = job_data.get("postingTitle", title) or title
        category = job_data.get("categoryCode", "")
        duty_station = extract_duty_station(job_data.get("dutyStation", ""))
        dept_obj = job_data.get("dept", {})
        dept = dept_obj.get("name", "") if isinstance(dept_obj, dict) else str(dept_obj)
        deadline = extract_deadline(job_data)
        job_code = job_data.get("jobCodeTitle", "")
        grade = extract_grade(job_data)
        start_date = job_data.get("startDate", "")
        if start_date:
            m = re.match(r'(\d{4}-\d{2}-\d{2})', start_date)
            start_date = m.group(1) if m else start_date
        
        url = f"https://careers.un.org/jobSearchDescription/{jid}?language=en"
        
        out = DIR / f"UN_{jid}_{sanitize(posting_title)[:60]}.md"
        if out.exists():
            skipped += 1
            continue
        
        header = (f"# {posting_title}\n\n"
                  f"**Job ID:** {jid}\n"
                  f"**Job Code:** {job_code}\n"
                  f"**Grade:** {grade}\n"
                  f"**Category:** {category}\n"
                  f"**Duty Station:** {duty_station}\n"
                  f"**Department:** {dept}\n"
                  f"**Deadline:** {deadline}\n"
                  f"**Start Date:** {start_date}\n"
                  f"**URL:** {url}\n"
                  f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
        
        out.write_text(header + desc_text, encoding="utf-8")
        saved += 1
        size_kb = len(desc_text) // 1024
        print(f"  SAVED: {jid} — {posting_title[:60]} ({size_kb}KB)")
    
    total_files = len(list(DIR.glob("UN_*.md")))
    print(f"\nDONE: {saved} new, {skipped} already existed, total: {total_files}")

if __name__ == "__main__":
    main()
