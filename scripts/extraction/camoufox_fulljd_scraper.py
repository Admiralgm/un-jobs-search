#!/usr/bin/env python3
"""Full-JD Camoufox REST scraper for ICRC and UNICEF — quality over speed.
Extracts complete JD text, not just titles. Waits for full JS render."""
import json, urllib.request, urllib.error, time, re, sys
from pathlib import Path
from datetime import datetime

CAMOFOX = "http://localhost:9377"
UID = "hermes-fulljd"
SK = "hermes-fulljd-20260606"
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

def ev(tid, expr, timeout=30):
    r = api("POST", f"/tabs/{tid}/evaluate", {"expression": expr, "userId": UID}, timeout=timeout)
    if isinstance(r, dict) and "error" not in r:
        return str(r.get("result", r.get("value", "")))
    return ""

def nav(tid, url, wait=20):
    """Navigate and wait for full JS render."""
    api("POST", f"/tabs/{tid}/navigate", {"url": url, "userId": UID})
    time.sleep(wait)

def create_tab(url="https://example.com"):
    t = api("POST", "/tabs", {"userId": UID, "sessionKey": SK, "url": url})
    if "tabId" in t:
        time.sleep(15)
        return t["tabId"]
    print(f"  TAB CREATE FAILED: {t}")
    return None

def close_tab(tid):
    api("DELETE", f"/tabs/{tid}")

def get_full_text(tid):
    """Extract full page text using multiple strategies."""
    # Strategy 1: body.innerText (best for rendered SPAs)
    text = ev(tid, "document.body.innerText", timeout=30)
    if text and len(text) > 500:
        return text
    
    # Strategy 2: document.body.innerHTML stripped of tags
    html = ev(tid, "document.body.innerHTML", timeout=30)
    if html:
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        if len(text) > 500:
            return text
    
    # Strategy 3: outerHTML of main content area
    text = ev(tid, """
    (function(){
        const selectors = ['main', 'article', '#content', '.content', '[role="main"]', '.job-detail', '.job-description'];
        for (const s of selectors) {
            const el = document.querySelector(s);
            if (el && el.innerText && el.innerText.length > 500) return el.innerText;
        }
        return document.body.innerText || '';
    })()
    """, timeout=30)
    return text

def get_full_html(tid):
    """Get raw HTML for parsing."""
    return ev(tid, "document.documentElement.outerHTML", timeout=30)

def extract_deadline(text):
    patterns = [
        r'[Dd]eadline[^:]*:\s*(\d{1,2}\s+\w+\s+\d{4})',
        r'[Cc]losing\s*[Dd]ate[^:]*:\s*(\d{1,2}\s+\w+\s+\d{4})',
        r'[Aa]pply\s*[Bb]efore[^:]*:\s*(\d{1,2}\s+\w+\s+\d{4})',
        r'[Dd]eadline[^:]*:\s*(\d{4}-\d{2}-\d{2})',
        r'[Aa]pply\s*[Bb]y[^:]*:\s*(\d{4}-\d{2}-\d{2})',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return "TBD"

def extract_grade(text):
    patterns = [
        r'Grade\s*:\s*([A-Z]\d)',
        r'Grade\s+([A-Z]\d)',
        r'Level\s*:\s*([A-Z]\d)',
        r'Category\s*:\s*([A-Z]\d)',
        r'P-(\d)',
        r'G-(\d)',
        r'IP(\d)',
        r'NPSA[-\s]?(\d)',
        r'ICS[-\s]?(\d)',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0).strip()
    return "TBD"

def extract_location(text):
    patterns = [
        r'[Dd]uty\s*[Ss]tation[^:]*:\s*([^\n]+)',
        r'[Ll]ocation[^:]*:\s*([^\n]+)',
        r'[Pp]osition\s*[Ll]ocation[^:]*:\s*([^\n]+)',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip()[:50]
    return "TBD"

def sanitize(title, maxlen=60):
    t = re.sub(r'[^\w\s\-]', '', title)
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:maxlen]

def save_jd(org_dir, jid, title, text, url, deadline="TBD", grade="TBD", location="TBD"):
    """Save full JD to file."""
    jd_dir = WORKDIR / "JD_FILES" / org_dir
    jd_dir.mkdir(parents=True, exist_ok=True)
    
    safe = sanitize(title)
    fn = f"{org_dir}_{jid}_{safe}.md"
    fpath = jd_dir / fn
    
    content = f"# {title}\n\n"
    content += f"**Job ID:** {jid}\n"
    content += f"**Grade:** {grade}\n"
    content += f"**Location:** {location}\n"
    content += f"**Deadline:** {deadline}\n"
    content += f"**URL:** {url}\n"
    content += f"**Scraped:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    content += f"**Source:** Camoufox REST API (full JD)\n\n"
    content += "---\n\n"
    content += text[:30000]  # Cap at 30K chars
    
    fpath.write_text(content, encoding='utf-8')
    return fn

# ============================================================
# ICRC SCRAPER
# ============================================================
def scrape_icrc():
    """Scrape ICRC careers.icrc.org via Camoufox REST API — full JD extraction."""
    print("\n" + "="*60)
    print("ICRC — Full JD Extraction via Camoufox REST")
    print("="*60)
    
    org_dir = "UN_ICRC"
    jd_dir = WORKDIR / "JD_FILES" / org_dir
    jd_dir.mkdir(parents=True, exist_ok=True)
    
    # Get existing job IDs
    existing = set()
    for f in jd_dir.glob("*.md"):
        parts = f.stem.split('_')
        if len(parts) >= 2:
            existing.add(parts[1])
    print(f"Existing ICRC files: {len(existing)}")
    
    tid = create_tab("https://example.com")
    if not tid:
        return []
    
    new_files = []
    try:
        # Navigate to ICRC listing
        print("Navigating to ICRC listing...")
        nav(tid, "https://careers.icrc.org/go/All-Jobs/3807301/", wait=20)
        
        # Get listing page text
        listing_text = get_full_text(tid)
        listing_html = get_full_html(tid)
        
        print(f"Listing page text: {len(listing_text)} chars")
        print(f"Listing page HTML: {len(listing_html)} chars")
        
        # Extract job links from listing
        # ICRC Taleo format: /job/{LOCATION}-{TITLE}-{JOBID}/{9DIGITID}/
        job_links = re.findall(r'href="(/job/[^"]+-(\d{9,10})/?)"', listing_html)
        if not job_links:
            # Try alternative patterns
            job_links = re.findall(r'href="(/job/[^"]+)"', listing_html)
            job_links = [(url, re.search(r'(\d{9,10})', url).group(1) if re.search(r'(\d{9,10})', url) else url.split('/')[-2]) for url in set(u for u, _ in job_links) if re.search(r'(\d{9,10})', url)]
        
        # Deduplicate
        seen = set()
        unique_links = []
        for url_path, jid in job_links:
            if jid not in seen and len(jid) >= 9:
                seen.add(jid)
                full_url = "https://careers.icrc.org" + url_path if not url_path.startswith('http') else url_path
                unique_links.append((jid, full_url))
        
        print(f"Found {len(unique_links)} unique job links")
        
        for jid, job_url in unique_links[:12]:  # Max 12 per portal
            if jid in existing:
                print(f"  SKIP: {jid} exists")
                continue
            
            print(f"  Fetching: {jid}...")
            nav(tid, job_url, wait=20)
            
            # Get full text
            text = get_full_text(tid)
            html = get_full_html(tid)
            
            combined = text + " " + html
            if len(combined) < 500:
                print(f"    SKIP: {jid} - empty/short page ({len(combined)} chars)")
                continue
            
            # Extract title
            title_m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL|re.IGNORECASE)
            title = ""
            if title_m:
                title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
            if not title or len(title) < 3:
                title = f"ICRC Position {jid}"
            
            # Extract metadata
            deadline = extract_deadline(combined)
            grade = extract_grade(combined)
            location = extract_location(combined)
            
            # Check ICT relevance
            ICT_KW = ['it ', 'ict', 'information technology', 'information systems', 'data', 'digital',
                'ai ', 'artificial intelligence', 'machine learning', 'software', 'cyber', 'cloud',
                'network', 'telecom', 'connectivity', 'platform', 'database', 'devops', 'web developer',
                'full stack', 'system administrator', 'infrastructure', 'technical', 'technology',
                'computer', 'programming', 'automation', 'robotics', 'gis', 'geospatial',
                'statistics', 'statistical', 'analytics', 'big data', 'data science', 'data engineer',
                'security officer', 'information security', 'network engineer', 'it officer',
                'it assistant', 'it manager', 'it director', 'chief information', 'cio ',
                'information management', 'knowledge management', 'data management', 'data governance',
                'enterprise architecture', 'solution architect', 'business intelligence',
                'innovation', 'transformation', 'modernization', 'digitization', 'ict ']
            
            combined_lower = combined.lower()
            is_ict = any(kw in combined_lower for kw in ICT_KW)
            
            if not is_ict:
                print(f"    SKIP: {jid} - not ICT ({title[:50]})")
                continue
            
            fn = save_jd(org_dir, jid, title, text, job_url, deadline, grade, location)
            new_files.append(fn)
            print(f"    SAVED: {fn} ({len(text)} chars, grade={grade}, loc={location})")
        
        return new_files
    finally:
        close_tab(tid)

# ============================================================
# UNICEF SCRAPER
# ============================================================
def scrape_unicef():
    """Scrape UNICEF jobs.unicef.org via Camoufox REST API — full JD extraction."""
    print("\n" + "="*60)
    print("UNICEF — Full JD Extraction via Camoufox REST")
    print("="*60)
    
    org_dir = "UN_UNICEF"
    jd_dir = WORKDIR / "JD_FILES" / org_dir
    jd_dir.mkdir(parents=True, exist_ok=True)
    
    # Get existing job IDs
    existing = set()
    for f in jd_dir.glob("*.md"):
        parts = f.stem.split('_')
        if len(parts) >= 2:
            existing.add(parts[1])
    print(f"Existing UNICEF files: {len(existing)}")
    
    tid = create_tab("https://example.com")
    if not tid:
        return []
    
    new_files = []
    try:
        # Navigate to UNICEF listing
        print("Navigating to UNICEF listing...")
        nav(tid, "https://jobs.unicef.org/en-us/list", wait=20)
        
        # Get listing page
        listing_html = get_full_html(tid)
        listing_text = get_full_text(tid)
        
        print(f"Listing page text: {len(listing_text)} chars")
        print(f"Listing page HTML: {len(listing_html)} chars")
        
        # Extract job links - PageUp format: /en-us/job/{6digitID}/{slug}
        job_links = re.findall(r'href="(/en-us/job/(\d{6})/[^"]*)"', listing_html)
        
        # Deduplicate by job ID
        seen = set()
        unique_links = []
        for url_path, jid in job_links:
            if jid not in seen:
                seen.add(jid)
                full_url = "https://jobs.unicef.org" + url_path
                unique_links.append((jid, full_url))
        
        print(f"Found {len(unique_links)} unique job links")
        
        for jid, job_url in unique_links[:12]:  # Max 12 per portal
            if jid in existing:
                print(f"  SKIP: {jid} exists")
                continue
            
            print(f"  Fetching: {jid}...")
            nav(tid, job_url, wait=20)
            
            # Get full text using multiple strategies
            text = get_full_text(tid)
            html = get_full_html(tid)
            
            combined = text + " " + html
            if len(combined) < 500:
                print(f"    SKIP: {jid} - empty/short page ({len(combined)} chars)")
                continue
            
            # Extract title from URL slug or h1
            title_m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL|re.IGNORECASE)
            title = ""
            if title_m:
                title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
            if not title or len(title) < 3 or title.lower() in ['vacancies', 'current vacancies', 'unicef careers']:
                # Extract from URL slug
                slug_match = re.search(r'/job/\d+/([^/]+)', job_url)
                if slug_match:
                    title = slug_match.group(1).replace('-', ' ').title()
                else:
                    title = f"UNICEF Position {jid}"
            
            # Extract metadata
            deadline = extract_deadline(combined)
            grade = extract_grade(combined)
            location = extract_location(combined)
            
            # Check ICT relevance
            ICT_KW = ['it ', 'ict', 'information technology', 'information systems', 'data', 'digital',
                'ai ', 'artificial intelligence', 'machine learning', 'software', 'cyber', 'cloud',
                'network', 'telecom', 'connectivity', 'platform', 'database', 'devops', 'web developer',
                'full stack', 'system administrator', 'infrastructure', 'technical', 'technology',
                'computer', 'programming', 'automation', 'robotics', 'gis', 'geospatial',
                'statistics', 'statistical', 'analytics', 'big data', 'data science', 'data engineer',
                'security officer', 'information security', 'network engineer', 'it officer',
                'it assistant', 'it manager', 'it director', 'chief information', 'cio ',
                'information management', 'knowledge management', 'data management', 'data governance',
                'enterprise architecture', 'solution architect', 'business intelligence',
                'innovation', 'transformation', 'modernization', 'digitization', 'ict ',
                'django', 'python', 'java', 'javascript', 'react', 'angular', 'node.js',
                'api ', 'microservice', 'agile', 'scrum', 'devops', 'ci/cd', 'docker', 'kubernetes',
                'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'aws ', 'azure', 'gcp ']
            
            combined_lower = combined.lower()
            is_ict = any(kw in combined_lower for kw in ICT_KW)
            
            if not is_ict:
                print(f"    SKIP: {jid} - not ICT ({title[:50]})")
                continue
            
            fn = save_jd(org_dir, jid, title, text, job_url, deadline, grade, location)
            new_files.append(fn)
            print(f"    SAVED: {fn} ({len(text)} chars, grade={grade}, loc={location})")
        
        return new_files
    finally:
        close_tab(tid)

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"Full-JD Camoufox REST Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Camoufox health: {api('GET', '/health')}")
    
    all_new = []
    
    # ICRC
    try:
        new = scrape_icrc()
        all_new.extend(new)
        print(f"\nICRC: {len(new)} new full-JD files")
    except Exception as e:
        print(f"\nICRC ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Restart server between portals (stability)
    print("\n--- Restarting Camoufox between portals ---")
    api("DELETE", "/tabs")
    time.sleep(5)
    
    # UNICEF
    try:
        new = scrape_unicef()
        all_new.extend(new)
        print(f"\nUNICEF: {len(new)} new full-JD files")
    except Exception as e:
        print(f"\nUNICEF ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"TOTAL NEW FULL-JD FILES: {len(all_new)}")
    for f in all_new:
        print(f"  {f}")
    print(f"{'='*60}")
