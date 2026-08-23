#!/usr/bin/env python3
"""RUN_BROAD_SCAN.py — Master orchestrator for broad UN scan (v5.0)"""
import subprocess, json, time, sys, os
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

WORKDIR       = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
LOG_DIR       = WORKDIR / "logs"; LOG_DIR.mkdir(exist_ok=True)
DATESTAMP     = datetime.now().strftime("%Y%m%d_%H%M")
REPORT_JSON   = WORKDIR / f"Broad_SCAN_REPORT_{DATESTAMP}.json"
REPORT_MD     = WORKDIR / f"Broad_SCAN_REPORT_{DATESTAMP}.md"

# Broad keyword env — all scripts must check this flag
os.environ["BROAD_SCAN"] = "1"
os.environ["BROAD_KEYWORDS_PATH"] = str(WORKDIR / "broad_scan_keywords.py")

# Agency scripts we actually have available (from /scripts/ dir or skill backup)
AGENCIES = [
    # Camoufox-dependent (sequential — server crashes after ~10 ops)
    ("UNESCO",  "camoufox",  180, "UN_UNESCO"),
    ("WTO",     "camoufox",  150, "UN_WTO"),
    ("WHO",     "camoufox",  180, "UN_WHO"),
    ("ICRC",    "camoufox",  150, "UN_ICRC"),
    # Scrapling-capable (parallel)
    ("ITU",     "scrapling", 120, "UN_ITU"),
    ("UNDP",    "scrapling", 90,  "UN_UNDP"),
    ("UNFPA",   "scrapling", 90,  "UN_UNFPA"),
    ("UNOPS",   "scrapling", 90,  "UN_UNOPS"),
    ("ILO",     "scrapling", 90,  "UN_ILO"),
    ("FAO",     "scrapling", 90,  "UN_FAO"),
    ("WFP",     "scrapling", 90,  "UN_WFP"),
    ("UNIDO",   "scrapling", 90,  "UN_UNIDO"),
    ("UNITAR",  "scrapling", 90,  "UN_UNITAR"),
    ("IMF",     "scrapling", 120, "UN_IMF"),
    ("IAEA",    "scrapling", 120, "UN_IAEA"),
    ("UNU",     "scrapling", 90,  "UN_UNU"),
    ("WMO",     "scrapling", 90,  "UN_WMO"),
    ("WorldBank", "direct",  120, "UN_WORLDBANK"),
    ("ICAO",    "browser",   120, "UN_ICAO"),
    ("IMO",     "scrapling", 90,  "UN_IMO"),
    ("Inspira", "taleo",     120, "UN_INSPIRA"),
]

def run_agency(name, portal_type, timeout, code):
    log = LOG_DIR / f"{code}_{DATESTAMP}.log"
    start = time.time()
    # Stub: real scripts vary by portal type
    # In production this calls run_<name>.py with broad keyword override
    result = {
        "agency": name, "portal": portal_type,
        "status": "PENDING", "jobs_found": 0, "new_saved": 0,
        "elapsed": 0, "log": str(log),
    }
    return result

if __name__ == "__main__":
    print("="*60)
    print("  ZERO-EMPTY-SCREENING BROAD SCAN v5.0")
    print("="*60)
    results = [run_agency(*a) for a in AGENCIES]
    report = {"scan_date": DATESTAMP, "total_agencies": len(AGENCIES), "results": results}
    REPORT_JSON.write_text(json.dumps(report, indent=2, default=str))
    print(f"\n  Report: {REPORT_JSON}")
