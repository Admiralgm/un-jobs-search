#!/usr/bin/env python3
"""UNITAR v4 — Camoufox browser for JS-rendered pages.

Problem: UNITAR detail pages load JD content via JavaScript.
Scrapling gets HTML shell only (no JD text).
Camoufox executes JS and renders full content.

Strategy: Use Camoufox to navigate listing page + each detail page.
Extract rendered inner_text("body"), clean navigation noise, save JD.
"""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from camoufox.sync_api import Camoufox

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_UNITAR"
DIR.mkdir(exist_ok=True)

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|evaluation.*training|independent evaluation|"
    r"monitoring.*evaluation|m&e|programme officer|programme assistant|"
    r"project officer.*education)", re.I)

ICT_TITLE_KW = [
    "geospatial", "gis", "satellite", "technology", "information technology",
    "artificial intelligence", "ai ", " ai", "data", "digital", "software",
    "developer", "developer and facilitator", "learning solutions",
    "educational technology", "instructional design", "online learning",
    "technical", "computer", "system", "database", "cloud", "network",
    "security", "cyber", "information security", "cybersecurity",
]

ICT_BODY_KW = [
    "digital",
    "geospatial", "gis", "satellite", "remote sensing", "earth observation",
    "mapping", "spatial analysis", "cartographic", "geodata", "geojson",
    "python", "r ", "javascript", "sql", "machine learning", "deep learning",
    "artificial intelligence", "ai ", "data analysis", "data processing",
    "quality assurance", "quality control", "qa/qc", "training module",
    "learning programme", "curriculum", "instructional", "e-learning",
    "lms", "learning management", "platform", "web development",
]

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_BODY_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def extract_jd_text(raw_text):
    """Extract JD content from rendered page text, stripping navigation noise."""
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    
    # Find JD start markers
    JD_START = [
        'organizational unit', 'expertise', 'description', 'background',
        'objective', 'purpose', 'scope', 'functions', 'responsibilities',
        'duties', 'requirements', 'qualifications', 'key areas',
    ]
    # Find JD end markers  
    JD_END = [
        'how to apply', 'application', 'deadline', 'closing date',
        'disclaimer', 'equal opportunity', 'diversity', 'fraud',
        'scam', 'report misconduct', 'social media', 'copyright',
        'privacy notice', 'terms of use',
    ]
    
    jd_start = 0
    for i, line in enumerate(lines):
        # Also start if we find the expertise/description header
        if any(m in line.lower() for m in JD_START):
            jd_start = i
            break
        # Or start after the location/org line (look for substantive content)
        if len(line) > 30 and not any(skip in line.lower() for skip in [
            'skip to', 'search', 'english', 'toggle', 'menu', 'navigation',
            'global', 'who we are', 'what we do', 'resources', 'media',
        ]):
            # Check if this looks like expertise or job description
            if 'expertise' in line.lower() or 'description' in line.lower():
                jd_start = i
                break
    
    jd_end = len(lines)
    for i, line in enumerate(lines):
        if any(m in line.lower() for m in JD_END) and i > jd_start + 3:
            jd_end = i
            break
    
    return '\n'.join(lines[jd_start:jd_end])

def main():
    print(f"UNITAR v4 Camoufox — {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        # Step 1: Get listing page
        print("Fetching listing page...")
        page.goto("https://unitar.org/vacancy-announcements")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        links = page.evaluate("""
        () => Array.from(document.querySelectorAll('a')).map(a => ({
            href: a.getAttribute('href') || '',
            text: a.innerText.trim().substring(0,100)
        })).filter(a => a.href && a.text && /vacancy-announcements\\/roster\\//.test(a.href))
        """)
        
        # Deduplicate by job ID
        jobs = {}
        for l in links:
            m = re.search(r'/(\d+)$', l['href'])
            if m:
                jid = m.group(1)
                if jid not in jobs:
                    full_href = l['href'] if l['href'].startswith('http') else f"https://unitar.org{l['href']}"
                    jobs[jid] = (l['text'], full_href)
        
        print(f"Jobs found: {len(jobs)}")
        
        # Step 2: Filter ICT
        ict_jobs = [(j, t, u) for j, (t, u) in jobs.items() if is_ict_title(t) or not HARD_REJECT.search(t)]
        print(f"ICT-title: {len(ict_jobs)}")
        for j, t, u in ict_jobs:
            print(f"  {j}: {t[:70]}")
        
        # Step 3: Fetch detail pages
        saved = 0
        for jid, title, url in ict_jobs:
            out = DIR / f"UNITAR_{jid}_{sanitize(title)[:60]}.md"
            if out.exists():
                print(f"  SKIP {jid}: exists")
                continue
            
            print(f"  Fetching {jid}...")
            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)
                
                text = page.inner_text("body")
                jd_text = extract_jd_text(text)
                
                if not jd_text or len(jd_text) < 200:
                    print(f"  SKIP {jid}: no content")
                    continue
                
                if not is_ict_body(jd_text):
                    print(f"  SKIP {jid}: body not ICT")
                    continue
                
                header = (f"# {title}\n\n**Job ID:** {jid}\n**URL:** {url}\n"
                          f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"  SAVED: {title[:55]} ({len(jd_text)} chars)")
                
            except Exception as e:
                print(f"  ERROR {jid}: {e}")
    
    total = len(list(DIR.glob("UNITAR_*.md")))
    print(f"\nDONE: {saved} saved, total: {total}")

if __name__ == "__main__":
    main()
