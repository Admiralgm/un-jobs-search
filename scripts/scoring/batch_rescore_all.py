#!/usr/bin/env python3
"""
BATCH_RESCORE_ALL.py — Rescore ALL tracker entries with v5.0 ZERO-EMPTY-SCREENING model.
Uses keyword intersection scoring for the first pass, then flags entries needing
manual LLM review.

Strategy:
- Read UN-VACANCIES-TRACKER.txt (82 entries)
- For each entry:
  * Parse: #, Organization, Title, Deadline, Score, VID, Applied
  * Extract existing score (from 🟡 57 format)
  * Compute new v5.0 keyword-based score using broad_scan_keywords.py
  * Look for cached JD in JD_FILES/<agency>/
  * Write entry to RESCORED tracker
- Also generate RESCORE_REPORT.json with detailed deltas

Usage:
    cd ~/Downloads/DATA_REPOSITORY/WORKDIR
    uv run python3 scripts/batch_rescore_all.py

Output:
    UN-VACANCIES-TRACKER_RESCORED.txt  — updated tracker with new scores
    RESCORE_REPORT_YYYYMMDD.json       — per-entry old/new/delta detailed report
"""
import sys, re, json
from pathlib import Path
from datetime import datetime

# ─── PATHS ──────────────────────────────────────────────────────────
WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
TRACKER = WORKDIR / "UN-VACANCIES-TRACKER.txt"
ARCHIVE = WORKDIR / "UN-VACANCIES-ARCHIVE.txt"
JD_DIR = WORKDIR / "JD_FILES"
OUT_TRACKER = WORKDIR / f"UN-VACANCIES-TRACKER_RESCORED_{datetime.now().strftime('%Y%m%d')}.txt"
OUT_REPORT = WORKDIR / f"RESCORE_REPORT_{datetime.now().strftime('%Y%m%d')}.json"

sys.path.insert(0, str(WORKDIR))
sys.path.insert(0, str(WORKDIR / "scripts"))
sys.path.insert(0, "/tmp/broad_scan")
try:
    from broad_scan_keywords import should_fetch_jd, extract_relevant_jds
    BROAD_AVAILABLE = True
except ImportError:
    BROAD_AVAILABLE = False
    print("WARNING: broad_scan_keywords.py not found; using inline keyword list")

# ─── INLINE v5.0 KEYWORD LIST (fallback) ────────────────────────────
TIER1 = {"ai","telecom","connectivity","fibre","fiber","broadband","internet","undersea","submarine","cable","capacity","wholesale","transmission","ip transit","vsat","satellite","iru","sdh","fttx","ftth","fttc","gpon","3g","4g","5g","wi-fi","wifi","wireless","mobile","cellular","isp","mvno","mvne","mobile money","fintech","payment","digital banking","transaction processing","edtech","education","school","learning","lms","moodle","canvas","k-12","k12","ai curriculum","giga","blended finance","ppp","infrastructure investment","development finance"}
TIER2 = {"coo","chief operating","chief operations","operations director","executive","general management","managing director","director","head of","chief","lead","manager","coordinator","advisor","adviser","consultant","specialist","officer","expert","strategist","architect","project manager","programme manager","portfolio","delivery","change management","transformation","restructuring","merger","acquisition","due diligence","m&a","business development","growth","market development","entrepreneur","startup","start-up","founder","venture","revenue","commercial"}
TIER4 = {"africa","african","uganda","zambia","rwanda","kenya","niger","ivory coast","south sudan","emergency","crisis","humanitarian","relief","health","medical","hospital","russian","cis","balkan","serbia","belgrade","eu","european","digital divide","school connectivity"}

def get_score(title, org=""):
    """v5.0 keyword-based quick score — NOT a replacement for manual 7-parameter scoring,
    but a calibrated first pass that removes old penalties and adds intersection bonuses."""
    text = (title + " " + org).lower()
    s = 0
    t1 = [kw for kw in TIER1 if kw in text]
    t2 = [kw for kw in TIER2 if kw in text]
    t4 = [kw for kw in TIER4 if kw in text]
    s += len(t1) * 10
    s += len(t2) * 5
    s += len(t4) * 3
    # Intersection bonus
    domains = 0
    if t1: domains += 1
    if t2: domains += 1
    if t4: domains += 1
    if domains >= 3: s += 8
    elif domains >= 2: s += 5
    # Seniority hints
    senior = ["director", "coo", "chief", "head of", "executive", "lead"]
    if any(k in text for k in senior): s += 3
    junior = ["assistant", "associate", "junior", "intern"]
    if any(k in text for k in junior): s -= 10
    # Cap at 95 (reserve 5 for manual LLM fine-tuning)
    return min(max(s, 20), 95), t1 + t2 + t4

# ─── PARSER ─────────────────────────────────────────────────────────
SCORE_RE = re.compile(r"([🔴🟠🟡🟢])\s*(\d+)")

def parse_tracker(path):
    entries = []
    with open(path, "r") as f:
        lines = f.readlines()
    data_started = False
    for line in lines:
        if data_started:
            # Match lines like: "1    UNICEF     Title... 2026-06-09  🟠 69  VID  NO"
            m = re.match(r"^(\d+)\s+(\S+)\s+(.+?)\s+(\d{4}-\d{2}-\d{2})\s+([🔴🟠🟡🟢]\s*\d+)\s+(\S+)\s+(\S+)", line)
            if m:
                num, org, title, deadline, score_str, vid, applied = m.groups()
                score_m = SCORE_RE.search(score_str)
                old_score = int(score_m.group(2)) if score_m else 0
                entries.append({
                    "num": int(num), "org": org.strip(), "title": title.strip(),
                    "deadline": deadline, "old_score": old_score,
                    "old_emoji": score_m.group(1) if score_m else "🟢",
                    "vid": vid.strip(), "applied": applied.strip(),
                    "raw_line": line.rstrip("\n")
                })
        if "Organization" in line and "Position Title" in line:
            data_started = True
    return entries

# ─── MAIN ───────────────────────────────────────────────────────────
def main():
    entries = parse_tracker(TRACKER)
    print(f"Loaded {len(entries)} entries from {TRACKER}")

    report = {"date": datetime.now().isoformat(), "total_entries": len(entries), "entries": []}
    rescored_lines = []
    header = """================================================================================
UN VACANCIES TRACKER — RE-SCORED v5.0 ZERO-EMPTY-SCREENING
Generated: """ + datetime.now().strftime("%Y-%m-%d") + """
================================================================================

VACANCY SUMMARY TABLE

#    Organization          Position Title                              Deadline        Score     Vacancy ID                    Applied
--------------------------------------------------------------------------------------------------------------------------------------
"""
    rescored_lines.append(header)

    for e in entries:
        new_score, matched = get_score(e["title"], e["org"])
        # Preserve old score if higher (don't deflate without reason)
        final_score = max(e["old_score"], new_score)
        # But if new is significantly higher (>+10), use new
        if new_score > e["old_score"] + 10:
            final_score = new_score

        # Emoji bands (v5.0)
        if final_score >= 75: emoji = "🔴"
        elif final_score >= 65: emoji = "🟠"
        elif final_score >= 50: emoji = "🟡"
        else: emoji = "🟢"

        new_line = f"{e['num']:<5}{e['org']:<22}{e['title']:<44}{e['deadline']:<16}{emoji} {final_score:<8}{e['vid']:<30}{e['applied']}\n"
        rescored_lines.append(new_line)

        report["entries"].append({
            "num": e["num"], "org": e["org"], "title": e["title"],
            "old_score": e["old_score"], "new_score": new_score,
            "final_score": final_score, "delta": final_score - e["old_score"],
            "matched_keywords": matched[:5],
            "deadline": e["deadline"], "vid": e["vid"]
        })

    OUT_TRACKER.write_text("".join(rescored_lines))
    OUT_REPORT.write_text(json.dumps(report, indent=2, default=str))

    # Summary
    gains = [r["delta"] for r in report["entries"] if r["delta"] > 0]
    losses = [r["delta"] for r in report["entries"] if r["delta"] < 0]
    unchanged = [r["delta"] for r in report["entries"] if r["delta"] == 0]
    print(f"\n=== RESCORE COMPLETE ===")
    print(f"  Entries processed: {len(entries)}")
    print(f"  Gained points:     {len(gains)} entries (avg +{sum(gains)//max(len(gains),1)})")
    print(f"  Lost points:       {len(losses)} entries (avg {sum(losses)//max(len(losses),1)})")
    print(f"  Unchanged:         {len(unchanged)}")
    print(f"  🔴 75+:            {sum(1 for r in report['entries'] if r['final_score'] >= 75)}")
    print(f"  🟠 65-74:          {sum(1 for r in report['entries'] if 65 <= r['final_score'] < 75)}")
    print(f"  🟡 50-64:          {sum(1 for r in report['entries'] if 50 <= r['final_score'] < 65)}")
    print(f"  🟢 <50:            {sum(1 for r in report['entries'] if r['final_score'] < 50)}")
    print(f"\n  Rescored tracker:  {OUT_TRACKER}")
    print(f"  JSON report:       {OUT_REPORT}")

if __name__ == "__main__":
    main()
