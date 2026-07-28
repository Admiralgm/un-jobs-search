#!/usr/bin/env python3
"""Full-JD Camoufox REST scraper v2 — ICRC + UNICEF.
Methodical one-by-one extraction with better JS rendering waits."""
import json, urllib.request, urllib.error, time, re, sys
from pathlib import Path
from datetime import datetime

CAMOFOX = "http://localhost:9377"
UID = "hermes-fulljd2"
SK = "hermes-fulljd2-20260606"
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

def nav(tid, url, wait=25):
    """Navigate and wait for full JS render."""
    api("POST", f"/tabs/{tid}/navigate", {"url": url, "userId": UID})
    print(f"    [nav] Waiting {wait}s for JS render...")
    time.sleep(wait)

def create_tab(url="https://example.com"):
    t = api("POST", "/tabs", {"userId": UID, "sessionKey": SK, "url": url})
    if "tabId" in t:
        time.sleep(20)
        return t["tabId"]
    print(f"  TAB CREATE FAILED: {t}")
    return None

def close_tab(tid):
    api("DELETE", f"/tabs/{tid}")

def wait_for_content(tid, min_chars=2000, max_wait=60):
    """Wait until page has meaningful content."""
    for i in range(max_wait // 5):
        text = ev(tid, "document.body.innerText", timeout=15)
        if text and len(text) > min_chars:
            print(f"    [content] {len(text)} chars after {(i+1)*5}s")
            return text
        time.sleep(5)
    text = ev(tid, "document.body.innerText", timeout=15)
    print(f"    [content] Timeout — got {len(text) if text else 0} chars")
    return text or ""

def get_full_text(tid):
    """Extract full page text — try multiple strategies."""
    # Strategy 1: body.innerText after waiting
    text = ev(tid, "document.body.innerText", timeout=30)
    if text and len(text) > 1000:
        return text
    
    # Strategy 2: Try to find main content area
    text = ev(tid, """
    (function(){
        const selectors = ['main', 'article', '#content', '.content', '[role="main"]', 
            '.job-detail', '.job-description', '.posting-content', '.job-content',
            '[data-testid="job-description"]', '.description', '#job-description'];
        for (const s of selectors) {
            const el = document.querySelector(s);
            if (el && el.innerText && el.innerText.length > 500) return el.innerText;
        }
        return document.body ? document.body.innerText : '';
    })()
    """, timeout=30)
    if text and len(text) > 1000:
        return text
    
    # Strategy 3: Strip HTML tags from innerHTML
    html = ev(tid, "document.body.innerHTML", timeout=30)
    if html:
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text
    return ""

def get_full_html(tid):
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
        r'\bP-(\d)',
        r'\bG-(\d)',
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
    return t[:len(title)]  # Don't truncate — keep full title

def save_jd(org_dir, jid, title, text, url, deadline="TBD", grade="TBD", location="TBD"):
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
    content += f"**Source:** Camoufox REST API v2 (full JD)\n\n"
    content += "---\n\n"
    content += text[:30000]
    
    fpath.write_text(content, encoding='utf-8')
    return fn

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
    'api ', 'microservice', 'agile', 'scrum', 'docker', 'kubernetes',
    'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'aws ', 'azure', 'gcp ']

def is_ict(text):
    tl = text.lower()
    return any(kw in tl for kw in ICT_KW)

# ============================================================
# ICRC — Methodical one-by-one
# ============================================================
def scrape_icrc():
    print("\n" + "="*60)
    print("ICRC — Full JD Extraction v2 (methodical)")
    print("="*60)
    
    org_dir = "UN_ICRC"
    jd_dir = WORKDIR / "JD_FILES" / org_dir
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
        print("\n[ICRC] Navigating to listing page...")
        nav(tid, "https://careers.icrc.org/go/All-Jobs/3807301/", wait=25)
        
        # Wait for content
        listing_text = wait_for_content(tid, min_chars=2000, max_wait=60)
        listing_html = get_full_html(tid)
        
        print(f"[ICRC] Listing: {len(listing_text)} text chars, {len(listing_html)} html chars")
        
        # Debug: print first 500 chars of text
        print(f"[ICRC] Text preview: {listing_text[:300]}")
        
        # Extract job links — try multiple patterns
        job_links = []
        
        # Pattern 1: /job/.../9digits/
        links1 = re.findall(r'href="(/job/[^"]+/(\d{9,10})/?)"', listing_html)
        if links1:
            job_links = [(jid, "https://careers.icrc.org" + path) for path, jid in links1]
            print(f"[ICRC] Pattern 1 found {len(job_links)} links")
        
        # Pattern 2: Any href with /job/ and digits
        if not job_links:
            all_job_hrefs = re.findall(r'href="(/job/[^"]+)"', listing_html)
            for href in all_job_hrefs:
                m = re.search(r'(\d{9,10})', href)
                if m:
                    job_links.append((m.group(1), "https://careers.icrc.org" + href))
            print(f"[ICRC] Pattern 2 found {len(job_links)} links")
        
        # Pattern 3: Look for job IDs in data attributes
        if not job_links:
            data_ids = re.findall(r'data-job-id="(\d{9,10})"', listing_html)
            for jid in data_ids:
                job_links.append((jid, f"https://careers.icrc.org/job/{jid}"))
            print(f"[ICRC] Pattern 3 found {len(job_links)} links")
        
        # Pattern 4: Look in text for job URLs
        if not job_links:
            text_urls = re.findall(r'(https?://careers\.icrc\.org/job/[^\s"<>]+)', listing_text)
            for url in text_urls:
                m = re.search(r'(\d{9,10})', url)
                if m:
                    job_links.append((m.group(1), url))
            print(f"[ICRC] Pattern 4 found {len(job_links)} links")
        
        # Deduplicate
        seen = set()
        unique_links = []
        for jid, url in job_links:
            if jid not in seen and len(jid) >= 9:
                seen.add(jid)
                unique_links.append((jid, url))
        
        print(f"[ICRC] {len(unique_links)} unique jobs to check")
        
        for jid, job_url in unique_links[:15]:
            if jid in existing:
                print(f"  SKIP: {jid} exists")
                continue
            
            print(f"\n  [{jid}] Fetching: {job_url}")
            nav(tid, job_url, wait=25)
            
            # Wait for content
            text = wait_for_content(tid, min_chars=2000, max_wait=60)
            html = get_full_html(tid)
            
            combined = (text or "") + " " + (html or "")
            print(f"    Content: {len(text or '')} text + {len(html or '')} html = {len(combined)} total")
            
            if len(combined) < 500:
                print(f"    SKIP: empty/short page")
                continue
            
            # Extract title
            title = ""
            title_m = re.search(r'<h1[^>]*>(.*?)</h1>', html or "", re.DOTALL|re.IGNORECASE)
            if title_m:
                title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
            if not title or len(title) < 3:
                title = f"ICRC Position {jid}"
            print(f"    Title: {title[:60]}")
            
            # Extract metadata
            deadline = extract_deadline(combined)
            grade = extract_grade(combined)
            location = extract_location(combined)
            print(f"    Grade: {grade}, Location: {location}, Deadline: {deadline}")
            
            # Check ICT
            if not is_ict(combined):
                print(f"    SKIP: not ICT")
                continue
            
            fn = save_jd(org_dir, jid, title, text or "", job_url, deadline, grade, location)
            new_files.append(fn)
            print(f"    ✓ SAVED: {fn}")
        
        return new_files
    finally:
        close_tab(tid)

# ============================================================
# UNICEF — Methodical one-by-one
# ============================================================
def scrape_unicef():
    print("\n" + "="*60)
    print("UNICEF — Full JD Extraction v2 (methodical)")
    print("="*60)
    
    org_dir = "UN_UNICEF"
    jd_dir = WORKDIR / "JD_FILES" / org_dir
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
        print("\n[UNICEF] Navigating to listing page...")
        nav(tid, "https://jobs.unicef.org/en-us/listing/", wait=25)
        
        listing_text = wait_for_content(tid, min_chars=2000, max_wait=60)
        listing_html = get_full_html(tid)
        
        print(f"[UNICEF] Listing: {len(listing_text)} text chars, {len(listing_html)} html chars")
        print(f"[UNICEF] Text preview: {listing_text[:300]}")
        
        # Extract job links
        job_links = re.findall(r'href="(/cw/en-us/job/(\d{6})/[^"]*)"', listing_html)
        
        # Deduplicate
        seen = set()
        unique_links = []
        for url_path, jid in job_links:
            if jid not in seen:
                seen.add(jid)
                unique_links.append((jid, "https://jobs.unicef.org" + url_path))
        
        print(f"[UNICEF] {len(unique_links)} unique jobs to check")
        
        for jid, job_url in unique_links[:15]:
            if jid in existing:
                print(f"  SKIP: {jid} exists")
                continue
            
            print(f"\n  [{jid}] Fetching: {job_url}")
            nav(tid, job_url, wait=25)
            
            # Wait for content
            text = wait_for_content(tid, min_chars=2000, max_wait=60)
            html = get_full_html(tid)
            
            combined = (text or "") + " " + (html or "")
            print(f"    Content: {len(text or '')} text + {len(html or '')} html = {len(combined)} total")
            
            if len(combined) < 500:
                print(f"    SKIP: empty/short page")
                continue
            
            # Extract title
            title = ""
            title_m = re.search(r'<h1[^>]*>(.*?)</h1>', html or "", re.DOTALL|re.IGNORECASE)
            if title_m:
                title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
            if not title or len(title) < 3 or title.lower() in ['vacancies', 'current vacancies', 'unicef careers']:
                slug_match = re.search(r'/job/\d+/([^/]+)', job_url)
                if slug_match:
                    title = slug_match.group(1).replace('-', ' ').replace('_', ' ').title()
                else:
                    title = f"UNICEF Position {jid}"
            print(f"    Title: {title[:60]}")
            
            # Extract metadata
            deadline = extract_deadline(combined)
            grade = extract_grade(combined)
            location = extract_location(combined)
            print(f"    Grade: {grade}, Location: {location}, Deadline: {deadline}")
            
            # Check ICT
            if not is_ict(combined):
                print(f"    SKIP: not ICT")
                continue
            
            fn = save_jd(org_dir, jid, title, text or "", job_url, deadline, grade, location)
            new_files.append(fn)
            print(f"    ✓ SAVED: {fn}")
        
        return new_files
    finally:
        close_tab(tid)

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"Full-JD Camoufox REST Scraper v2 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Camoufox health: {api('GET', '/health')}")
    
    all_new = []
    
    # ICRC first
    try:
        new = scrape_icrc()
        all_new.extend(new)
        print(f"\n[ICRC] Done: {len(new)} new full-JD files")
    except Exception as e:
        print(f"\n[ICRC] ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Restart server between portals
    print("\n--- Restarting Camoufox between portals ---")
    api("DELETE", "/tabs")
    time.sleep(5)
    
    # UNICEF
    try:
        new = scrape_unicef()
        all_new.extend(new)
        print(f"\n[UNICEF] Done: {len(new)} new full-JD files")
    except Exception as e:
        print(f"\n[UNICEF] ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"TOTAL NEW FULL-JD FILES: {len(all_new)}")
    for f in all_new:
        print(f"  {f}")
    print(f"{'='*60}")
