#!/usr/bin/env python3
"""Camoufox REST API scraper for UNICEF, ICRC, WTO — 2026-06-06 scan."""
import json, urllib.request, urllib.error, time, re, sys
from pathlib import Path
from datetime import datetime

CAMOFOX = "http://localhost:9377"
UID = "hermes-default"
SK = "hermes-scan-20260606"
WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")

def api(method, path, data=None, timeout=120):
    url = f"{CAMOFOX}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body,
          headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"error": str(e)}

def ev(tid, expr):
    r = api("POST", f"/tabs/{tid}/evaluate", {"expression": expr, "userId": UID})
    if isinstance(r, dict) and "error" not in r:
        return str(r.get("result", r.get("value", "")))
    return ""

def nav(tid, url, wait=12):
    api("POST", f"/tabs/{tid}/navigate", {"url": url, "userId": UID})
    time.sleep(wait)

def create_tab(url="https://example.com"):
    t = api("POST", "/tabs", {"userId": UID, "sessionKey": SK, "url": url})
    if "tabId" in t:
        time.sleep(12)
        return t["tabId"]
    print(f"  TAB CREATE FAILED: {t}")
    return None

def close_tab(tid):
    api("DELETE", f"/tabs/{tid}")

def clean_html(html):
    """Strip script/style tags and extract readable text."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_title(html):
    # Try h1
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL|re.IGNORECASE)
    if m:
        t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if t and len(t) > 3:
            return t
    # Try title tag
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL|re.IGNORECASE)
    if m:
        t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if t and len(t) > 3:
            return t
    return "Unknown"

def extract_deadline(text):
    # Common patterns
    patterns = [
        r'[Dd]eadline[^:]*:\s*(\d{1,2}\s+\w+\s+\d{4})',
        r'[Cc]losing\s*[Dd]ate[^:]*:\s*(\d{1,2}\s+\w+\s+\d{4})',
        r'[Aa]pply\s*[Bb]efore[^:]*:\s*(\d{1,2}\s+\w+\s+\d{4})',
        r'[Dd]eadline[^:]*:\s*(\d{4}-\d{2}-\d{2})',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return "TBD"

ICT_KEYWORDS = ['it ', 'ict', 'information technology', 'information systems', 'data', 'digital',
    'ai ', 'artificial intelligence', 'machine learning', 'software', 'cyber', 'cloud',
    'network', 'telecom', 'connectivity', 'platform', 'database', 'devops', 'web developer',
    'full stack', 'system administrator', 'infrastructure', 'technical', 'technology',
    'computer', 'programming', 'automation', 'robotics', 'gis', 'geospatial', 'satellite',
    'statistics', 'statistical', 'analytics', 'big data', 'data science', 'data engineer',
    'security officer', 'information security', 'network engineer', 'it officer',
    'it assistant', 'it manager', 'it director', 'chief information', 'cio ',
    'information management', 'knowledge management', 'data management', 'data governance',
    'enterprise architecture', 'solution architect', 'business intelligence', 'bi ',
    'erp ', 'sap ', 'oracle', 'microsoft', 'aws ', 'azure', 'api ', 'microservice',
    'agile', 'scrum', 'project manager', 'product owner', 'ux ', 'ui ', 'user experience',
    'mobile app', 'web application', 'e-learning', 'edtech', 'education technology',
    'innovation', 'transformation', 'modernization', 'digitization']

def is_ict(text):
    tl = text.lower()
    return any(kw in tl for kw in ICT_KEYWORDS)

def sanitize(title, maxlen=60):
    t = re.sub(r'[^\w\s\-]', '', title)
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:maxlen]

def scrape_unicef():
    """Scrape UNICEF jobs.unicef.org via Camoufox REST API."""
    print("\n=== UNICEF (PageUp) ===")
    org_dir = "UN_UNICEF"
    jd_dir = WORKDIR / "JD_FILES" / org_dir
    jd_dir.mkdir(parents=True, exist_ok=True)
    
    existing = set(f.stem.split('_')[1] for f in jd_dir.glob("*.md") if '_' in f.stem)
    print(f"Existing files: {len(existing)}")
    
    tid = create_tab("https://example.com")
    if not tid:
        return []
    
    new_files = []
    try:
        # Navigate to UNICEF listing
        nav(tid, "https://jobs.unicef.org/en-us/list", wait=15)
        html = ev(tid, "document.documentElement.outerHTML")
        
        if not html or len(html) < 1000:
            print(f"  WARNING: Short HTML ({len(html)} chars), may be blocked")
            # Try with different approach
            nav(tid, "https://jobs.unicef.org/en-us/list?keywords=IT", wait=15)
            html = ev(tid, "document.documentElement.outerHTML")
        
        # Extract job links - PageUp format
        job_links = re.findall(r'/en-us/job/(\d{6})/([^"]*)"', html)
        # Also try data-job-number
        if not job_links:
            job_links = re.findall(r'data-job-number="(\d{6})"', html)
            job_links = [(jid, "") for jid in job_links]
        
        # Deduplicate
        seen = set()
        unique_links = []
        for jid, slug in job_links:
            if jid not in seen:
                seen.add(jid)
                unique_links.append((jid, slug))
        
        print(f"Found {len(unique_links)} unique job links")
        
        for jid, slug in unique_links[:10]:  # Max 10 per portal
            if jid in existing:
                print(f"  SKIP: {jid} exists")
                continue
            
            detail_url = f"https://jobs.unicef.org/en-us/job/{jid}/{slug}" if slug else f"https://jobs.unicef.org/en-us/job/{jid}"
            nav(tid, detail_url, wait=12)
            jd_html = ev(tid, "document.documentElement.outerHTML")
            
            if not jd_html or len(jd_html) < 500:
                print(f"  SKIP: {jid} - empty/short page")
                continue
            
            text = clean_html(jd_html)
            
            if not is_ict(text):
                print(f"  SKIP: {jid} - not ICT")
                continue
            
            title = extract_title(jd_html)
            deadline = extract_deadline(text)
            
            safe = sanitize(title)
            fn = f"UNICEF_{jid}_{safe}.md"
            
            content = f"# {title}\n\n"
            content += f"**Job ID:** {jid}\n"
            content += f"**Deadline:** {deadline}\n"
            content += f"**URL:** {detail_url}\n"
            content += f"**Scraped:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            content += "---\n\n"
            content += text[:15000]  # Cap at 15K chars
            
            (jd_dir / fn).write_text(content, encoding='utf-8')
            new_files.append(fn)
            print(f"  SAVED: {fn} ({len(text)} chars)")
        
        return new_files
    finally:
        close_tab(tid)

def scrape_icrc():
    """Scrape ICRC careers.icrc.org via Camoufox REST API."""
    print("\n=== ICRC (Taleo) ===")
    org_dir = "UN_ICRC"
    jd_dir = WORKDIR / "JD_FILES" / org_dir
    jd_dir.mkdir(parents=True, exist_ok=True)
    
    existing = set()
    for f in jd_dir.glob("*.md"):
        parts = f.stem.split('_')
        if len(parts) >= 2:
            existing.add(parts[1])
    print(f"Existing files: {len(existing)}")
    
    tid = create_tab("https://example.com")
    if not tid:
        return []
    
    new_files = []
    try:
        nav(tid, "https://careers.icrc.org/go/All-Jobs/3807301/", wait=15)
        html = ev(tid, "document.documentElement.outerHTML")
        
        # Extract job links - Taleo format
        job_links = re.findall(r'/job/[^"]+-(\d{9,10})/', html)
        # Deduplicate
        seen = set()
        unique = []
        for jid in job_links:
            if jid not in seen:
                seen.add(jid)
                unique.append(jid)
        
        print(f"Found {len(unique)} unique job links")
        
        for jid in unique[:8]:
            if jid in existing:
                print(f"  SKIP: {jid} exists")
                continue
            
            # Find the full URL from the listing
            m = re.search(r'(/job/[^"]+' + re.escape(jid) + r'/[^"]*)', html)
            if m:
                detail_url = "https://careers.icrc.org" + m.group(1).rstrip('/')
            else:
                detail_url = f"https://careers.icrc.org/job/Unknown-Title/{jid}/"
            
            nav(tid, detail_url, wait=12)
            jd_html = ev(tid, "document.documentElement.outerHTML")
            
            if not jd_html or len(jd_html) < 500:
                print(f"  SKIP: {jid} - empty/short page")
                continue
            
            text = clean_html(jd_html)
            
            if not is_ict(text):
                print(f"  SKIP: {jid} - not ICT")
                continue
            
            title = extract_title(jd_html)
            deadline = extract_deadline(text)
            
            safe = sanitize(title)
            fn = f"ICRC_{jid}_{safe}.md"
            
            content = f"# {title}\n\n"
            content += f"**Job ID:** {jid}\n"
            content += f"**Deadline:** {deadline}\n"
            content += f"**URL:** {detail_url}\n"
            content += f"**Scraped:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            content += "---\n\n"
            content += text[:15000]
            
            (jd_dir / fn).write_text(content, encoding='utf-8')
            new_files.append(fn)
            print(f"  SAVED: {fn} ({len(text)} chars)")
        
        return new_files
    finally:
        close_tab(tid)

def scrape_wto():
    """Scrape WTO Workday via Camoufox REST API."""
    print("\n=== WTO (Workday) ===")
    org_dir = "UN_WTO"
    jd_dir = WORKDIR / "JD_FILES" / org_dir
    jd_dir.mkdir(parents=True, exist_ok=True)
    
    existing = set()
    for f in jd_dir.glob("*.md"):
        parts = f.stem.split('_')
        if len(parts) >= 2:
            existing.add(parts[1])
    print(f"Existing files: {len(existing)}")
    
    tid = create_tab("https://example.com")
    if not tid:
        return []
    
    new_files = []
    try:
        nav(tid, "https://wto.wd103.myworkdayjobs.com/External", wait=15)
        html = ev(tid, "document.documentElement.outerHTML")
        
        # Extract job links - Workday format
        job_links = re.findall(r'/en-US/External/job/[^"]+/([^"]+)_\w+R(\d+)-1', html)
        if not job_links:
            job_links = re.findall(r'/job/[^"]+_JR(\d+)-1"', html)
            job_links = [("", jid) for jid in job_links]
        
        # Deduplicate by JR number
        seen = set()
        unique = []
        for slug, jid in job_links:
            if jid not in seen:
                seen.add(jid)
                unique.append((slug, jid))
        
        print(f"Found {len(unique)} unique job links")
        
        for slug, jid in unique[:8]:
            if jid in existing:
                print(f"  SKIP: {jid} exists")
                continue
            
            detail_url = f"https://wto.wd103.myworkdayjobs.com/en-US/External/job/{slug}_JR{jid}-1"
            nav(tid, detail_url, wait=12)
            jd_html = ev(tid, "document.documentElement.outerHTML")
            
            if not jd_html or len(jd_html) < 500:
                print(f"  SKIP: {jid} - empty/short page")
                continue
            
            text = clean_html(jd_html)
            
            if not is_ict(text):
                print(f"  SKIP: {jid} - not ICT")
                continue
            
            title = extract_title(jd_html)
            deadline = extract_deadline(text)
            
            safe = sanitize(title)
            fn = f"WTO_{jid}_{safe}.md"
            
            content = f"# {title}\n\n"
            content += f"**Job ID:** JR{jid}\n"
            content += f"**Deadline:** {deadline}\n"
            content += f"**URL:** {detail_url}\n"
            content += f"**Scraped:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            content += "---\n\n"
            content += text[:15000]
            
            (jd_dir / fn).write_text(content, encoding='utf-8')
            new_files.append(fn)
            print(f"  SAVED: {fn} ({len(text)} chars)")
        
        return new_files
    finally:
        close_tab(tid)

if __name__ == "__main__":
    print(f"Camoufox REST API Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Camoufox health: {api('GET', '/health')}")
    
    all_new = []
    
    # UNICEF
    try:
        new = scrape_unicef()
        all_new.extend(new)
        print(f"UNICEF: {len(new)} new JDs")
    except Exception as e:
        print(f"UNICEF ERROR: {e}")
    
    # Restart server between portals
    print("\nRestarting Camoufox between portals...")
    api("DELETE", "/tabs")  # Close all tabs
    time.sleep(3)
    
    # ICRC
    try:
        new = scrape_icrc()
        all_new.extend(new)
        print(f"ICRC: {len(new)} new JDs")
    except Exception as e:
        print(f"ICRC ERROR: {e}")
    
    # Restart server between portals
    print("\nRestarting Camoufox between portals...")
    api("DELETE", "/tabs")
    time.sleep(3)
    
    # WTO
    try:
        new = scrape_wto()
        all_new.extend(new)
        print(f"WTO: {len(new)} new JDs")
    except Exception as e:
        print(f"WTO ERROR: {e}")
    
    print(f"\n=== TOTAL NEW JDs: {len(all_new)} ===")
    for f in all_new:
        print(f"  {f}")
