#!/usr/bin/env python3
"""UNOPS v4 — fetch all JobDetail pages, check body for ICT relevance.

Fixes from v3 (2026-07-20):
1. Uses SearchJobs URL with pagination (was: homepage root — only got 6 recommended jobs)
2. No title pre-filter gate — fetches ALL non-HARD-REJECT jobs and checks body
   (was: title-only ICT filter that missed ICT-adjacent PM/implementation roles)
3. Added pagination handling for 85+ results (was: single page only)
"""
import asyncio, re, urllib.parse
from datetime import datetime, date
from pathlib import Path
from scrapling.fetchers import StealthyFetcher

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_UNOPS"

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|junior professional|jpo)", re.I)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "full stack", "fullstack", "devops", "devsecops",
    "machine learning", "computer", "web", "database", "infrastructure", "security",
    "geospatial", "gis", "metadata", "ux ", "api ", "microservices", "blockchain",
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
    "technology for development", "tech lead", "technical lead", "enterprise data",
    "data architect", "data engineer", "data analyst", "data scientist",
    "digital transformation", "green digital", "emerging technolog",
    "cadastral", "modernisation", "land administration",
]

ICT_FULL_KW = ICT_TITLE_KW + [
    "python", "java", "javascript", "sql", "nosql", "react", "angular", "vue",
    "node.js", "typescript", "html", "css", "rest api", "graphql", "azure", "aws", "gcp",
    "terraform", "ansible", "jenkins", "gitlab", "github", "ci/cd", "linux", "unix",
    "firewall", "vpn", "siem", "soc ", "zero trust", "identity and access", "iam ",
    "encryption", "machine learning", "deep learning", "neural network", "nlp",
    "computer vision", "power bi", "tableau", "qlik", "etl ", "data pipeline",
    "data integration", "data quality", "data governance", "solution architecture",
    "enterprise architecture", "digital transformation", "e-government", "e-health",
    "e-learning", "artificial intelligence", "generative ai", "agentic ai",
    "computer use", "api integration", "system integration", "infrastructure as code",
    "containerization", "site reliability engineering", "observability", "monitoring",
]

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_FULL_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def load_existing_ids():
    ids = set()
    for f in DIR.glob("UNOPS_*.md"):
        parts = f.stem.split("_", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            ids.add(parts[1])
    return ids

async def fetch_page(url, wait=5000):
    try:
        page = await StealthyFetcher.async_fetch(url, headless=True, disable_resources=True, wait=wait)
        if page.status == 200: return page
    except: pass
    return None

async def main():
    DIR.mkdir(exist_ok=True)
    print(f"UNOPS v4.0 — {datetime.now():%Y-%m-%d %H:%M:%S}")
    existing = load_existing_ids()
    print(f"Existing JDs: {len(existing)}")

    # Fetch all listing pages with pagination
    all_jobs = []
    seen = set()

    for offset in range(0, 300, 6):
        url = f"https://careers.unops.org/careersmarketplace/SearchJobs/?jobRecordsPerPage=6&jobOffset={offset}"
        page = await fetch_page(url, wait=6000)
        if not page:
            print(f"  offset={offset}: fetch failed, stopping")
            break
        html = page.html_content
        links = re.findall(r'href="(https://careers\.unops\.org/careersmarketplace/JobDetail/[^"]+/(\d+))"', html)
        if not links:
            print(f"  offset={offset}: no links, stopping")
            break
        new_on_page = 0
        for url, jid in links:
            if jid in seen or jid in existing: continue
            seen.add(jid)
            new_on_page += 1
            slug_m = re.search(r'/JobDetail/([^/]+)', url)
            if slug_m:
                title = urllib.parse.unquote(slug_m.group(1)).replace('-', ' ').strip().title()
            else:
                title = f"UNOPS-{jid}"
            all_jobs.append((jid, title, url))
        print(f"  offset={offset}: {len(links)} links, {new_on_page} new")
        if new_on_page == 0 and len(links) < 6:
            break  # Last page

    print(f"Total new jobs found: {len(all_jobs)}")

    # HARD_REJECT filter on title only (saves HTTP requests on obvious non-ICT)
    jobs_to_fetch = [(j, t, u) for j, t, u in all_jobs if is_ict_title(t) or not HARD_REJECT.search(t)]
    rejected = len(all_jobs) - len(jobs_to_fetch)
    print(f"Hard-rejected by title: {rejected}")
    print(f"Jobs to fetch (body check): {len(jobs_to_fetch)}")

    # NO title ICT gate — fetch all non-rejected jobs and check body
    # This follows the skill philosophy: "Scrape FIRST, disqualify LATER in scoring"
    saved = 0
    sem = asyncio.Semaphore(3)

    async def fetch_job(jid, title, url):
        try:
            async with sem:
                page = await fetch_page(url, wait=4000)
            if not page: return None
            text = page.get_all_text()
            return text if len(text) >= 500 else None
        except: return None

    for i in range(0, len(jobs_to_fetch), 6):
        batch = jobs_to_fetch[i:i+6]
        tasks = [fetch_job(j, t, u) for j, t, u in batch]
        results = await asyncio.gather(*tasks)
        for idx, text in enumerate(results):
            jid, title, url = batch[idx]
            if not text:
                print(f"  SKIP (no text): {jid} — {title[:50]}")
                continue
            if not is_ict_body(text):
                continue
            out = DIR / f"UNOPS_{jid}_{sanitize(title)[:60]}.md"
            if out.exists(): continue
            header = f"# {title}\n\n**Job ID:** {jid}\n**URL:** {url}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n"
            out.write_text(header + text, encoding="utf-8")
            saved += 1
            print(f"  SAVED: {jid} — {title[:60]}")

    print(f"\nDONE: {saved} new ICT JDs saved, total: {len(list(DIR.glob('UNOPS_*.md')))}")

if __name__ == "__main__":
    asyncio.run(main())