#!/usr/bin/env python3
"""UN Tourism (former UNWTO) scraper — server-rendered HTML table + PDF apply notices.

Portal: https://www.untourism.int/work-with-us (Employment Opportunities table, #paragraph-48026)
Apply links are PDFs (Call for Expression of Interest) hosted on S3.
"""
import re, html as html_mod, hashlib, io
from datetime import datetime
from pathlib import Path
import httpx
import fitz  # pymupdf

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_UNTOURISM"
DIR.mkdir(exist_ok=True)

PAGE_URL = "https://www.untourism.int/work-with-us"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ",
    " it", "ict ", " ict", "computer", "database", "infrastructure", "security",
    "geospatial", "gis", "api ", "automation", "analytics", "information management",
    "webmaster", "web ",
]

HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer|statistics|statistician|tourism satellite|"
    r"general administration|team assistant|secretar)", re.I)

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_TITLE_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def strip_html(seg):
    text = re.sub(r'<[^>]+>', ' ', seg)
    text = html_mod.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

def parse_table(html_text):
    """Extract vacancy rows from the Employment Opportunities table."""
    m = re.search(r'id="paragraph-48026".*?</table>', html_text, re.S)
    if not m:
        m = re.search(r'<table[^>]*>.*?Post Title.*?</table>', html_text, re.S)
    if not m:
        return []
    seg = m.group(0)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', seg, re.S)
    jobs = []
    for r in rows[1:]:  # skip header
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)
        if len(cells) < 6:
            continue
        clean = [strip_html(c) for c in cells]
        link_m = re.search(r'href="([^"]+)"', cells[-1])
        apply_url = link_m.group(1).strip() if link_m else ""
        jobs.append({
            "title": clean[0],
            "grade": clean[1],
            "type": clean[2],
            "dept": clean[3],
            "station": clean[4],
            "closing": clean[5],
            "apply_url": apply_url,
        })
    return jobs

def pdf_text(url):
    """Download PDF and extract text via pymupdf."""
    try:
        r = httpx.get(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"}, timeout=60, follow_redirects=True)
        if r.status_code != 200:
            return None
        doc = fitz.open(stream=r.content, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception:
        return None

def main():
    print(f"UN Tourism scraper — {datetime.now():%Y-%m-%d %H:%M:%S}")
    r = httpx.get(PAGE_URL, headers={"User-Agent": UA, "Accept-Encoding": "identity"}, timeout=60, follow_redirects=True)
    if r.status_code != 200:
        print(f"ERROR: page status {r.status_code}")
        return
    jobs = parse_table(r.text)
    print(f"Jobs found: {len(jobs)}")

    existing = set()
    for f in DIR.glob("UNTOURISM_*.md"):
        existing.add(f.stem)
    print(f"Existing: {len(existing)}")

    ict = [j for j in jobs if is_ict_title(j["title"]) and not HARD_REJECT.search(j["title"])]
    print(f"ICT: {len(ict)}")
    for j in ict:
        print(f"  {j['title'][:60]} | {j['station'][:30]} | {j['closing'][:10]}")

    saved = 0
    for j in ict:
        vid = sanitize(j["title"] + "_" + j["station"])[:50]
        out = DIR / f"UNTOURISM_{vid}.md"
        if out.exists():
            continue
        body = pdf_text(j["apply_url"]) if j["apply_url"] else None
        if body and len(body) >= 300 and is_ict_body(body):
            out.write_text(
                f"# {j['title']}\n\n"
                f"**Job ID:** {vid}\n"
                f"**URL:** {PAGE_URL}\n"
                f"**Apply:** {j['apply_url']}\n"
                f"**Grade/Area:** {j['grade']}\n"
                f"**Type:** {j['type']}\n"
                f"**Department:** {j['dept']}\n"
                f"**Duty Station:** {j['station']}\n"
                f"**Closing:** {j['closing']}\n"
                f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n"
                f"---\n\n{body}",
                encoding="utf-8",
            )
            saved += 1
            print(f"SAVED: {vid} — {j['title'][:60]}")
        else:
            print(f"SKIP (no PDF body / not ICT): {j['title'][:60]}")
    print(f"DONE: {saved} saved")

if __name__ == "__main__":
    main()
