#!/usr/bin/env python3
"""UNESCO v4 — Scrapling StealthyFetcher with .body + script/style stripping.

Key discovery: response.body has full HTML (116KB), .text returns None for JS pages.
Must strip <script> and <style> tags (they contain tracking code, NOT job content).
After stripping, JD content is 6-10KB of clean text.

Search strategy: 25+ ICT keyword queries, deduplicate by job ID, filter ICT titles,
apply body check. Result: 9 ICT JDs.
"""
import asyncio, re, html as html_mod, urllib.parse
from datetime import datetime
from pathlib import Path
from scrapling.fetchers import StealthyFetcher

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_UNESCO"
DIR.mkdir(exist_ok=True)

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|junior professional|jpo|education|lawyer|"
    r"adviser|director.*division|programme officer|programme assistant|"
    r"project officer|project assistant|national.*officer.*education|"
    r"community engagement|transformative|curriculum|heritage.*unit|documentary|"
    r"water.*cooperation|groundwater|carpentry|joinery|consultant.*education|"
    r"consultant.*culture|graphic.*novel)", re.I)

ICT_TITLE_KW = [
    " it ", "it,", "it.", "ict", "information systems", "information technology",
    "information management", "digital", "software", "data", "cloud", "network",
    "system administrator", "system engineer", "systems engineer",
    "telecom", "cyber", "ai ", " ai", "artificial intelligence", "machine learning",
    "web developer", "web development", "full stack", "fullstack", "frontend",
    "backend", "devops", "devsecops", "database", "infrastructure", "security",
    "geospatial", "gis", "metadata", "api ", "microservices", "blockchain",
    "iot ", "automation", "robotics", "middleware", "erp ", "crm ",
    "business intelligence", "bi developer", "etl", "data warehouse", "data lake",
    "site reliability", "noc ", "isp ", "telecommunications", "broadband",
    "fiber", "fibre", "satellite", "mobile", "wireless", "help desk",
    "technical support", "it support", "it manager", "it director", "it officer",
    "it specialist", "it coordinator", "it project", "it governance", "it strategy",
    "chief information", "chief technology", "chief digital", "cto", "cio",
    "head of it", "head of digital", "head of technology",
    "knowledge management", "learning solutions", "edtech", "educational technology",
    "agentic ai", "mcp", "generative ai", "llm", "prompt engineering",
    "vector database", "digital ecosystem", "digital inclusion",
    "geospatial data science", "ai geospatial", "data science", "data engineer",
    "data architect", "data management", "data officer", "data analyst",
    "platform solution", "cloud engineer", "cloud architect", "solution architect",
    "enterprise architecture", "technical architect", "statistics", "statistical",
    "statistician", "computer", "computing", "programmer", "programming",
    "developer", "technology", "technical",
]

ICT_BODY_KW = [
    "digital",
    "python", "java", "javascript", "sql", "nosql", "react", "angular", "vue",
    "node.js", "typescript", "html", "css", "rest api", "graphql", "azure", "aws", "gcp",
    "terraform", "ansible", "jenkins", "gitlab", "github", "ci/cd", "linux", "unix",
    "firewall", "vpn", "siem", "zero trust", "identity and access", "iam ",
    "encryption", "deep learning", "neural network", "nlp", "computer vision",
    "power bi", "tableau", "qlik", "data pipeline", "data integration",
    "data quality", "data governance", "digital transformation",
    "artificial intelligence", "generative ai", "agentic ai",
    "api integration", "system integration", "infrastructure as code",
    "containerization", "site reliability engineering", "observability",
    "agile", "scrum", "devops", "microservices", "kubernetes", "docker",
    "desktop administration", "server administration", "lan ", "wan ",
    "network support", "it support", "help desk", "service desk",
    "software distribution", "scripting", "backup", "disaster recovery",
    "antivirus", "password management", "security incident",
]

def clean_html_to_text(raw):
    """Strip script/style tags, then extract clean text from HTML."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.S|re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S|re.I)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = html_mod.unescape(text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    jd_start = 0
    for i, line in enumerate(lines):
        if any(m in line.lower() for m in [
            'long description', 'main tasks', 'org. setting', 'responsibilities',
            'qualifications', 'competencies', 'key duties', 'functions',
            'objective', 'scope of work', 'deliverservic',
        ]):
            jd_start = i
            break
    if jd_start == 0:
        jd_start = min(20, len(lines))
    
    END_MARKERS = [
        'similar jobs', 'share this job', 'apply now', 'back to results',
        'disclaimer', 'copyright 20', 'faq', 'privacy notice',
        'environmental and social', 'career site company'
    ]
    jd_end = len(lines)
    for i, line in enumerate(lines):
        if any(m in line.lower() for m in END_MARKERS) and i > jd_start + 5:
            jd_end = i
            break
    
    return '\n'.join(lines[jd_start:jd_end])

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    tl = text.lower()
    return any(kw in tl for kw in ICT_BODY_KW)

def sanitize(name):
    name = urllib.parse.unquote(name)
    name = re.sub(r'[%\d]+$', '', name)
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def load_existing_ids():
    ids = set()
    for f in DIR.glob("UNESCO_*.md"):
        parts = f.stem.split("_", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            ids.add(parts[1])
    return ids

SEARCH_QUERIES = [
    "information", "technology", "digital", "data", "ict",
    "software", "computer", "network", "cloud", "artificial intelligence",
    "ai", "cyber", "web developer", "it officer", "information systems",
    "telecom", "geospatial", "database", "infrastructure", "technical",
    "frontend", "backend", "fullstack", "machine learning", "devops",
    "automation", "platform", "statistics", "system", "security",
]

async def fetch_search_page(query):
    url = f"https://careers.unesco.org/search/?createNewAlert=false&q={urllib.parse.quote_plus(query)}&locale=en_GB&alljobs=true"
    try:
        resp = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=4000, timeout=60000)
        html_str = str(resp.body)
        job_links = re.findall(r'href="(/job/[^"]+?/(\d{6,})/?)[" ][^>]*>(.*?)</a>', html_str, re.S)
        results = []
        for href, jid, raw_title in job_links:
            title = re.sub(r'<[^>]+>', '', raw_title).strip()
            if title:
                results.append((jid, title, href))
        return results
    except Exception as e:
        print(f"  ERROR query '{query}': {str(e)[:60]}")
        return []

async def fetch_job_detail(url_path):
    url = f"https://careers.unesco.org{url_path}"
    try:
        resp = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=4000, timeout=60000)
        text = clean_html_to_text(str(resp.body))
        return text if len(text) >= 200 else None
    except Exception as e:
        print(f"    ERROR detail: {str(e)[:60]}")
        return None

async def main():
    print(f"UNESCO v4 — {datetime.now():%Y-%m-%d %H:%M:%S}")
    existing = load_existing_ids()
    print(f"Existing: {len(existing)}")
    
    all_jobs = {}
    for query in SEARCH_QUERIES:
        results = await fetch_search_page(query)
        new = 0
        for jid, title, href in results:
            if jid not in all_jobs:
                all_jobs[jid] = (title, href)
                new += 1
        print(f"  [{query:>25s}] +{new:>2} (total: {len(all_jobs)})")
        await asyncio.sleep(0.2)
    
    print(f"\nTotal unique: {len(all_jobs)}")
    
    ict_jobs = [(j, t, h) for j, (t, h) in all_jobs.items() if is_ict_title(t) or not HARD_REJECT.search(t)]
    print(f"ICT-title: {len(ict_jobs)}")
    for j, t, h in ict_jobs:
        print(f"  {j}: {t[:65]}")
    
    saved = 0
    for jid, title, href in ict_jobs:
        if jid in existing:
            continue
        text = await fetch_job_detail(href)
        if not text:
            print(f"  SKIP {jid}: no content")
            continue
        if not is_ict_body(text):
            print(f"  SKIP {jid}: body not ICT ({title[:40]})")
            continue
        
        actual_title = urllib.parse.unquote(title)
        out = DIR / f"UNESCO_{jid}_{sanitize(actual_title)[:60]}.md"
        if out.exists():
            continue
        
        header = (f"# {actual_title}\n\n"
                  f"**Job ID:** {jid}\n"
                  f"**URL:** https://careers.unesco.org{href}\n"
                  f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
        out.write_text(header + text, encoding="utf-8")
        saved += 1
        print(f"  SAVED: {jid} — {actual_title[:55]} ({len(text)//1024}KB)")
        await asyncio.sleep(0.3)
    
    total = len(list(DIR.glob("UNESCO_*.md")))
    print(f"\nDONE: {saved} new, total: {total}")

if __name__ == "__main__":
    asyncio.run(main())
