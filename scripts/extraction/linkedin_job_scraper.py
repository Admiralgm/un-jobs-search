#!/usr/bin/env python3
"""
LinkedIn Jobs Scraper for User — UN/ICT/AI/Telecom/Director roles.
Targets: Geneva, Vienna, Copenhagen, Brussels, NYC, remote, Belgrade.
Saves full JD markdown files to JD_FILES/LINKEDIN/
"""

import logging, os, json, re, sys
from datetime import datetime
from pathlib import Path
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters, TimeFilters, TypeFilters,
    ExperienceLevelFilters, OnSiteOrRemoteFilters,
)

# ─── CONFIG ───────────────────────────────────────────────
WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
OUTDIR = WORKDIR / "JD_FILES" / "LINKEDIN"
OUTDIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.now().strftime("%Y-%m-%d_%H%M")
LOG_FILE = WORKDIR / "scan_logs" / f"linkedin_scan_{NOW}.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(LOG_FILE)]
)
log = logging.getLogger("li:scraper")
log.setLevel(logging.DEBUG)

# ─── SEARCH QUERIES ───────────────────────────────────────
# (query_string, locations, experience_levels, time_filter, max_results)

# NO location filter — globally open. Belgrade is a primary target.
BELGRADE = ["Belgrade", "Serbia"]
GLOBAL = []  # empty = worldwide

QUERIES = [
    # AI / Artificial Intelligence
    ("Artificial Intelligence Director", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 30),
    ("Artificial Intelligence Consultant", GLOBAL,
     [ExperienceLevelFilters.MID_SENIOR, ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 30),
    ("AI Policy OR AI Governance", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.MONTH, 25),
    ("AI OR Artificial Intelligence", BELGRADE,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.WEEK, 20),

    # Digital Transformation / ICT
    ("Digital Transformation Director", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 25),
    ("ICT Director OR Chief Information Officer", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 25),
    ("Digital Infrastructure", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.MONTH, 20),
    ("Digital Transformation OR ICT", BELGRADE,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.WEEK, 20),

    # Telecom / Connectivity
    ("Telecom Director OR Telecommunications", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 20),
    ("Connectivity OR Broadband", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.MONTH, 20),
    ("Telecom OR Telekomunikacije", BELGRADE,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.WEEK, 15),

    # UN / International Organizations
    ("Digital Innovation", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.MONTH, 20),
    ("Innovation Manager OR Innovation Lead", GLOBAL,
     [ExperienceLevelFilters.MID_SENIOR, ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 20),
    ("EdTech OR Education Technology", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.MONTH, 20),
    ("United Nations OR UN Consultant", GLOBAL,
     [ExperienceLevelFilters.MID_SENIOR, ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 20),

    # Senior Operations / COO — Belgrade first
    ("Chief Operations Officer OR COO", BELGRADE,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 15),
    ("Chief Operations Officer OR COO", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 10),
    ("Director of Operations", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 15),
    ("Direktor OR Izvršni direktor", BELGRADE,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.WEEK, 10),

    # Technology Strategy / Architecture
    ("Technology Strategy Director OR Enterprise Architect", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 15),
    ("Digital Policy OR Technology Policy", GLOBAL,
     [ExperienceLevelFilters.MID_SENIOR, ExperienceLevelFilters.DIRECTOR], TimeFilters.MONTH, 15),

    # FinTech / Payments / MVNO
    ("FinTech OR Payments OR MVNO", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.MONTH, 15),

    # Remote / Home-based
    ("Remote Director OR Remote Consultant", GLOBAL,
     [ExperienceLevelFilters.DIRECTOR, ExperienceLevelFilters.MID_SENIOR], TimeFilters.MONTH, 20),
]

# ─── COUNTER ──────────────────────────────────────────────
stats = {"total": 0, "saved": 0, "errors": 0, "started": datetime.now()}


def on_data(data: EventData):
    stats["total"] += 1
    n = stats["total"]

    # Build safe filename
    title_clean = re.sub(r'[^a-zA-Z0-9\s\-]', '', data.title)[:80].strip()
    company_clean = re.sub(r'[^a-zA-Z0-9\s\-]', '', data.company)[:40].strip()
    job_id = data.job_id
    filename = f"LI_{job_id}_{company_clean}_{title_clean}.md"
    filepath = OUTDIR / filename

    # Skip if already exists
    if filepath.exists():
        log.info(f"[{n}] SKIP (exists): {data.title[:80]} @ {data.company}")
        return

    # Build markdown content
    md = f"""# {data.title}

**Job ID:** {job_id}
**Company:** {data.company}
**Location:** {data.place}
**Date Posted:** {data.date}
**Link:** {data.link}
**Apply Link:** {data.apply_link}

---

## Description
{data.description}

---

## Insights
{json.dumps(data.insights, indent=2) if data.insights else 'N/A'}

---
*Scraped: {NOW} | Source: LinkedIn Jobs*
"""
    try:
        filepath.write_text(md, encoding='utf-8')
        stats["saved"] += 1
        log.info(f"[{n}] SAVED: {data.company} — {data.title[:80]} ({data.place})")
    except Exception as e:
        stats["errors"] += 1
        log.error(f"[{n}] WRITE ERROR: {e}")


def on_error(error):
    stats["errors"] += 1
    log.error(f"SCRAPER ERROR: {error}")


def on_end():
    elapsed = (datetime.now() - stats["started"]).total_seconds()
    print(f"\n{'='*60}")
    print(f"LINKEDIN JOB SCRAPE COMPLETE")
    print(f"  Total fetched: {stats['total']}")
    print(f"  New saved:     {stats['saved']}")
    print(f"  Errors:        {stats['errors']}")
    print(f"  Duration:      {elapsed:.0f}s")
    print(f"  Output:        {OUTDIR}")
    print(f"  Log:           {LOG_FILE}")
    print(f"{'='*60}")


# ─── MAIN ─────────────────────────────────────────────────
def main():
    # Check LI_AT_COOKIE
    if not os.environ.get("LI_AT_COOKIE"):
        log.warning("LI_AT_COOKIE not set — using anonymous mode (may fail on cloud)")

    scraper = LinkedinScraper(
        chrome_executable_path=None,
        chrome_binary_location="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        chrome_options=None,
        headless=True,
        max_workers=1,
        slow_mo=1.5,
        page_load_timeout=40,
    )

    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    queries = []
    for q_str, locations, experience, time_f, limit in QUERIES:
        queries.append(Query(
            query=q_str,
            options=QueryOptions(
                locations=locations,
                apply_link=True,
                skip_promoted_jobs=True,
                limit=limit,
                filters=QueryFilters(
                    time=time_f,
                    type=[TypeFilters.FULL_TIME, TypeFilters.CONTRACT],
                    experience=experience,
                )
            )
        ))

    log.info(f"Starting LinkedIn scrape: {len(queries)} queries, saving to {OUTDIR}")
    scraper.run(queries)


if __name__ == "__main__":
    main()
