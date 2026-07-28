#!/usr/bin/env python3
"""
================================================================================
UNICEF Jobs Scraper v1.0 — jobs.unicef.org
================================================================================
Scrapes ICT/AI/digital/telecom/innovation vacancies from UNICEF careers portal
using Scrapling StealthyFetcher. Two-stage pre-filtering. Skips existing files.

PIPELINE:
  Phase 0 : Clean expired JDs (deadline passed)
  Phase A : Paginate listing pages (?page=N), extract job URLs
            Stage 1: Title pre-filter (no network cost)
            Stage 2: Full-text filter after fetch
  Phase B : Save passing JDs to UNICEF/ subdirectory

Usage:
  python3 run_unicef_scraper.py

Output:
  ~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES/UNICEF/UNICEF_{jobID}_{sanitized_title}.md
================================================================================
"""
import asyncio, re, sys, time
from collections import Counter
from datetime import datetime, date
from pathlib import Path
from scrapling.fetchers import StealthyFetcher

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR    = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
UNICEF_DIR  = BASE_DIR / "UN_UNICEF"
CONCURRENT  = 4
MAX_PAGES   = 15
PER_PAGE    = 20

# ── KEYWORDS (same as untalent-jobs-search) ─────────────────────────────────
HARD_REJECT = re.compile(
    r"(intern|stagiaire|volunteer|unpaid|nutrition|agricultur|wash specialist|"
    r"sanitation engineer|civil engineer|shelter|procurement|human rights|medical|"
    r"doctor|nurse|midwife|teacher|pedagog|child protection|gender|accountant|"
    r"finance officer|budget officer|audit|hr officer|human resources|admin officer|"
    r"logistics|supply chain|warehouse|fleet|security officer|driver|interpreter|"
    r"translator|cook|cleaner|maintenance|electrician|plumber)", re.I)

ICT_KW = [
    " it ", " ict ", " isp ", " ai ", " artificial ", " telecom ", " connectivity ",
    " innovation ", "information technology", "chief technology", " cto ",
    " chief information ", " cio ", " digital transformation ", " digital officer ",
    " systems administrator ", " network engineer ", " network administrator ",
    " software engineer ", " software developer ", " data engineer ", " data scientist ",
    " cybersecurity ", " information security ", " devops ", " cloud engineer ",
    " cloud architect ", " database administrator ", " web developer ",
    " full stack ", " machine learning ", " deep learning ",
    " solutions architect ", " enterprise architect ", " technical lead ",
    "it officer", "it specialist", "it manager",
    "ict officer", "ict specialist", "ict coordinator",
    "ai engineer", "ai research", "telecommunications", "innovation officer",
    "digital specialist", "digital officer", "digital advisor",
    "tech lead", "technology officer", "technology specialist",
    "system administrator", "systems engineer", "platform engineer",
    "fullstack", "front-end developer", "backend developer",
    "cloud computing", "data analyst", "data analytics",
    "business intelligence", "information management", "knowledge management",
    "infrastructure engineer", "site reliability", "devsecops",
    "machine learning engineer", "natural language processing",
    "computer vision", "robotics engineer", "automation engineer",
    "blockchain", "distributed systems", "microservices",
    "api developer", "integration engineer", "middleware",
    "erp consultant", "crm consultant", "business analyst it",
    "it project manager", "it director", "head of it", "head of digital",
    "chief digital", "digital innovation", "emerging technology",
    "technology strategy", "it strategy", "it governance",
    "information systems", "management information",
    "gis specialist", "geospatial", "spatial data",
    "data warehouse", "data lake", "etl developer",
    "bi developer", "business intelligence developer",
    "report developer", "database developer", "sql developer",
    "python developer", "java developer", "javascript developer",
    "web application", "mobile developer", "app developer",
    "ui designer", "ux designer", "product designer digital",
    "technology for development", "digital development",
    "digital health", "e-health", "mhealth", "telemedicine",
    "fintech", "digital finance", "mobile money",
    "internet of things", "iot developer", "embedded systems",
    "firmware engineer", "hardware engineer it",
    "quantum computing", "high performance computing", "hpc",
    "data center", "data centre", "network operations", "noc engineer",
    "it support", "help desk", "technical support it",
    "it procurement", "it asset management",
    "digital platform", "platform developer", "developer platform",
    "open source developer", "freelance developer web",
]

def is_ict_title(title):
    t = " " + title.lower() + " "
    for kw in ICT_KW:
        if kw in t:
            return True, f"ICT-PASS: '{kw.strip()}'"
    return False, f"ICT-FAIL: '{title[:60]}'"

def is_ict_full(title, body):
    return any(kw in (title + " " + body[:1000]).lower() for kw in ICT_KW)

def sanitize(name):
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

class ProblemTracker:
    def __init__(self):
        self.problems = []
        self.stats = Counter()
    def log(self, cat, det, key=None):
        self.problems.append({"category": cat, "detail": det, "key": key})
        self.stats[cat] += 1
    def report(self):
        if not self.problems:
            print("\n  No problems.")
            return
        print(f"\n  PROBLEMS ({len(self.problems)}):")
        for cat, count in self.stats.most_common():
            print(f"    {cat}: {count}")

tracker = ProblemTracker()

DEADLINE_PATTERN = re.compile(
    r'(?:closing|deadline|application\s+deadline|closing\s+on)\s*[:\\s]\s*'
    r'(\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4})', re.I)

MONTHS = {
    'jan': 1,'january': 1,'feb': 2,'february': 2,'mar': 3,'march': 3,
    'apr': 4,'april': 4,'may': 5,'jun': 6,'june': 6,
    'jul': 7,'july': 7,'aug': 8,'august': 8,'sep': 9,'sept': 9,'september': 9,
    'oct': 10,'october': 10,'nov': 11,'november': 11,'dec': 12,'december': 12,
}

def parse_deadline(text):
    m = DEADLINE_PATTERN.search(text)
    if not m:
        return None
    raw = m.group(1)
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        pass
    parts = raw.split()
    if len(parts) == 3:
        try:
            day = int(parts[0])
            month = MONTHS.get(parts[1].lower(), 0)
            year = int(parts[2])
            if month:
                return date(year, month, day)
        except (ValueError, IndexError):
            pass
    return None

def clean_expired():
    print("=" * 70)
    print("PHASE 0 — Clean expired JDs")
    print("=" * 70)
    today = date.today()
    if not UNICEF_DIR.exists():
        print("  UNICEF dir does not exist, skip")
        return 0
    removed = 0
    kept_no_date = 0
    for f in UNICEF_DIR.glob("*.md"):
        try:
            content = f.read_text("utf-8", errors="ignore")
        except Exception:
            continue
        dl = parse_deadline(content)
        if dl is None:
            kept_no_date += 1
        elif dl < today:
            f.unlink()
            removed += 1
    remaining = len(list(UNICEF_DIR.glob("*.md")))
    print(f"  UNICEF: removed {removed} expired, {remaining} remaining ({kept_no_date} no-deadline)")
    return removed

def load_existing_ids():
    ids = set()
    for f in UNICEF_DIR.glob("UNICEF_*.md"):
        parts = f.stem.split("_", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            ids.add(parts[1])
    return ids

def extract_jobs_from_listing(html_content):
    results = {}
    links = re.findall(
        r'<h4[^>]*>\s*<a[^>]*href="(/en-us/job/(\d+)/[^"]*)"[^>]*>(.*?)</a>',
        html_content, re.S
    )
    for url, jid, raw_title in links:
        title = re.sub(r'<[^>]+>', '', raw_title).strip()
        if title and jid not in results:
            results[jid] = (jid, title, url)
    if not results:
        links2 = re.findall(r'href="(/en-us/job/(\d+)/[^"]*)"', html_content)
        for url, jid in links2:
            if jid not in results:
                results[jid] = (jid, "(title from listing)", url)
    return list(results.values())

async def fetch_job(sem, jid, url):
    full_url = f"https://jobs.unicef.org{url}"
    try:
        async with sem:
            page = await StealthyFetcher.async_fetch(
                full_url, headless=True, disable_resources=True, wait=2000)
    except Exception as e:
        tracker.log("JD_ERR", f"{jid}:{e}")
        return None
    if page.status != 200:
        tracker.log("JD_!200", f"{jid}:{page.status}")
        return None
    text = page.get_all_text()
    if len(text) < 500:
        tracker.log("JD_STUB", f"{jid}:{len(text)}b")
        return None
    if len(text) < 1500:
        tracker.log("SMALL", f"{jid}:{len(text)}b")
    return (jid, text)

async def main():
    print("=" * 70)
    print("UNICEF Jobs Scraper v1.0 — jobs.unicef.org")
    print("=" * 70)
    print(f"  Output: {UNICEF_DIR}")
    print(f"  Started: {datetime.now():%Y-%m-%d %H:%M:%S}")

    clean_expired()
    existing_ids = load_existing_ids()
    print(f"\n  Existing files: {len(existing_ids)}")

    print("\n" + "=" * 70)
    print("PHASE A — Listing pages")
    print("=" * 70)

    all_candidates = []
    seen_ids = set(existing_ids)
    total_scanned = 0

    for pn in range(1, MAX_PAGES + 1):
        listing_url = f"https://jobs.unicef.org/en-us/listing/?page={pn}"
        t0 = time.time()
        try:
            page = await StealthyFetcher.async_fetch(
                listing_url, headless=True, disable_resources=True, wait=2000)
        except Exception as e:
            tracker.log("LISTING_ERROR", f"P{pn}:{e}")
            print(f"  Page {pn}: ERROR {e}")
            break
        el = time.time() - t0
        if page.status != 200:
            tracker.log("LISTING_!200", f"P{pn}:{page.status}")
            print(f"  Page {pn}: HTTP {page.status}, stopping")
            break

        jobs = extract_jobs_from_listing(page.html_content)
        unique_on_page = [(jid, t, u) for jid, t, u in jobs if jid not in seen_ids]
        seen_ids.update(jid for jid, _, _ in jobs)

        if not jobs:
            print(f"  Page {pn}: 0 jobs found, stopping")
            break

        total_scanned += len(unique_on_page)

        page_pass = []
        page_skip = 0
        for jid, title, url in unique_on_page:
            ok, reason = is_ict_title(title)
            if ok:
                page_pass.append((jid, title, url))
            else:
                page_skip += 1

        all_candidates.extend(page_pass)
        print(f"  Page {pn}: {len(jobs)} jobs, {len(unique_on_page)} new, "
              f"{len(page_pass)} ICT-title pass, {page_skip} skip ({el:.1f}s)")

        if len(jobs) < PER_PAGE:
            print(f"  (fewer than {PER_PAGE} on page {pn}, last page)")
            break

    print(f"\n  Total scanned: {total_scanned}, ICT-title candidates: {len(all_candidates)}")

    print("\n" + "=" * 70)
    print("PHASE B — Fetch JDs + full-text filter + save")
    print("=" * 70)

    sem = asyncio.Semaphore(CONCURRENT)
    saved = 0
    full_fail = 0
    fetch_errors = 0

    batch_size = CONCURRENT * 2
    for i in range(0, len(all_candidates), batch_size):
        batch = all_candidates[i:i+batch_size]
        tasks = [fetch_job(sem, jid, url) for jid, title, url in batch]
        results = await asyncio.gather(*tasks)
        for idx, result in enumerate(results):
            jid, title, url = batch[idx]
            if result is None:
                fetch_errors += 1
                continue
            _, text = result
            if not is_ict_full(title, text):
                full_fail += 1
                continue
            safe_title = sanitize(title)[:60]
            out_file = UNICEF_DIR / f"UNICEF_{jid}_{safe_title}.md"
            if out_file.exists():
                continue
            header = (f"# {title}\n\n**Job ID:** {jid}\n"
                      f"**URL:** https://jobs.unicef.org{url}\n"
                      f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
            out_file.write_text(header + text, encoding="utf-8")
            saved += 1
            print(f"  SAVED: {jid} — {title[:60]}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Jobs scanned (new):     {total_scanned}")
    print(f"  ICT-title pass (S1):    {len(all_candidates)}")
    print(f"  Saved to disk (S2):     {saved}")
    print(f"  Full-text reject (S2):  {full_fail}")
    print(f"  Fetch errors:           {fetch_errors}")
    tracker.report()
    total_files = len(list(UNICEF_DIR.glob("*.md")))
    print(f"\n  Total UNICEF files on disk: {total_files}")
    print(f"  Finished: {datetime.now():%Y-%m-%d %H:%M:%S}")

if __name__ == "__main__":
    asyncio.run(main())
