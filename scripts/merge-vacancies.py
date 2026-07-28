#!/usr/bin/env python3
"""
Merge new job entries into UN_SECTOR_VACCANCIES.txt and regenerate UN_SECTOR_VACCANCIES_ALL.txt
Usage: python3 merge-vacancies.py batch_results.json [--source reliable|unreliable]

If --source is "unreliable", entries go to UN_SECTOR_VACCANCIES_IMPACTPOOL.txt instead.
After every merge, UN_SECTOR_VACCANCIES_ALL.txt is regenerated as consolidated merge.
"""

import os, sys, re, json, hashlib
from datetime import datetime

RELIABLE_FILE = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt"
UNRELIABLE_FILE = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_IMPACTPOOL.txt"
ALL_FILE = "~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_ALL.txt"
BACKUP_DIR = "~/Downloads"


def load_jobs(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)


def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r') as f:
        return f.read()


def get_job_id(job):
    id_keys = ['Vacancy ID', 'Job ID', 'Reference', 'ID', 'JobID', 'VacancyID']
    for key in id_keys:
        if job.get(key):
            return str(job[key]).strip()
    url = job.get('HYPERLINK', '')
    id_match = re.search(r'/(?:job|vacancy|id|posting)/(\d+)', url) or re.search(r'[?&](?:id|jobId)=(\d+)', url)
    if id_match:
        return id_match.group(1)
    hash_input = f"{job.get('Title','')}{job.get('Organization','')}"
    return f"[GEN-{hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()}]"


def is_duplicate(content, job):
    if job.get('HYPERLINK') and job['HYPERLINK'] in content:
        return True
    job_id = get_job_id(job)
    if f"- VACANCY ID: {job_id}" in content:
        return True
    if f"- Title: {job['Title']}" in content and f"- Organization: {job['Organization']}" in content:
        return True
    return False


def get_color(score):
    if score >= 90: return "🔴 RED"
    if score >= 80: return "🟠 ORANGE"
    if score >= 70: return "🟡 YELLOW"
    return "🟢 GREEN"


def format_entry(job, score):
    color = get_color(score)
    lines = [
        f"\n{color} — {job['Title']}",
        "=" * 80,
        f"- Title: {job['Title']}",
        f"- VACANCY ID: {get_job_id(job)}",
        f"- Organization: {job.get('Organization', 'N/A')}",
        f"- Grade: {job.get('Grade', 'N/A')}",
        f"- Location: {job.get('Location', 'N/A')}",
        f"- Deadline: {job.get('Deadline', 'N/A')}",
        f"- Contract type: {job.get('Contract type', 'N/A')}",
    ]
    if job.get('Estimated compensation'):
        lines.append(f"- Estimated compensation (USD): {job['Estimated compensation']}")
    lines.append(f"- HYPERLINK: {job.get('HYPERLINK', 'N/A')}")
    lines.append(f"- SCORE: {score}/100")
    lines.append("- APPLIED: NO\n")
    lines.append("MATCH ANALYSIS:")
    lines.append(f"- Technical Relevance (60%): {job.get('Technical', 'N/A')}")
    lines.append(f"- Seniority Alignment (20%): {job.get('Seniority', 'N/A')}")
    lines.append(f"- Strategic Alignment (20%): {job.get('Strategic', 'N/A')}")
    lines.append("")
    lines.append("🚀 Positioning Advice:")
    for advice in job.get('Positioning_Advice', []):
        lines.append(f"- {advice}")
    lines.append("")
    verdict = job.get('Verdict', 'N/A')
    confidence = job.get('Confidence', 'N/A')
    lines.append(f"📊 Verdict: {verdict}")
    lines.append(f"Confidence Level: {confidence}")
    lines.append("")
    return "\n".join(lines)


def update_footer(content):
    red = len(re.findall(r"🔴 RED", content))
    orange = len(re.findall(r"🟠 ORANGE", content))
    yellow = len(re.findall(r"🟡 YELLOW", content))
    green = len(re.findall(r"🟢 GREEN", content))
    active = red + orange + yellow + green
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "=== FILE FOOTER ===" in content:
        content = re.sub(
            r"Active Entries:.*?\n",
            f"Active Entries: {active} (RED: {red}, ORANGE: {orange}, YELLOW: {yellow}, GREEN: {green})\n",
            content
        )
        content = re.sub(
            r"FILE ENDS:.*",
            f"FILE ENDS: {now_str}",
            content
        )
    return content


def regenerate_consolidated():
    reliable = read_file(RELIABLE_FILE)
    unreliable = read_file(UNRELIABLE_FILE)

    def extract_entries(content):
        entries = []
        current = []
        in_entry = False
        for line in content.splitlines():
            if line.startswith("🟢") or line.startswith("🟡") or line.startswith("🟠") or line.startswith("🔴"):
                if current:
                    entries.append("\n".join(current))
                current = [line]
                in_entry = True
            elif in_entry:
                if line.startswith("=== FILE FOOTER ==="):
                    if current:
                        entries.append("\n".join(current))
                    current = []
                    in_entry = False
                else:
                    current.append(line)
        if current:
            entries.append("\n".join(current))
        return entries

    reliable_entries = extract_entries(reliable)
    unreliable_entries = extract_entries(unreliable)

    reliable_ids = set()
    for entry in reliable_entries:
        for line in entry.splitlines():
            if line.startswith("- VACANCY ID:"):
                reliable_ids.add(line.split(":", 1)[1].strip())
                break

    all_entries = list(reliable_entries)
    pool_added = 0
    for entry in unreliable_entries:
        entry_id = None
        for line in entry.splitlines():
            if line.startswith("- VACANCY ID:"):
                entry_id = line.split(":", 1)[1].strip()
                break
        if entry_id and entry_id not in reliable_ids:
            all_entries.append(entry)
            pool_added += 1

    now_str = datetime.now().strftime("%Y-%m-%d")
    header = f"""================================================================================
CONSOLIDATED UN SECTOR VACANCIES MASTER LIST | GENERATED: {now_str}
CRITERIA: Active Only (>= Today), Sorted by Nearest Deadline
SOURCES: Reliable (direct career portals) + Unreliable (Impactpool/UNJobNet)
SCORING: 3-Dimension Model — Technical Relevance (60%) + Seniority Alignment (20%) + Strategic Alignment (20%)
================================================================================

"""
    footer = f"""
=== FILE FOOTER ===
Active Entries: {len(all_entries)}
  - From reliable sources (direct portals): {len(reliable_entries)}
  - From unreliable sources (Impactpool/UNJobNet): {pool_added}
SCORING MODEL: Technical Relevance (60%) + Seniority Alignment (20%) + Strategic Alignment (20%)
COLOR CODING: RED (90+ STRONG FIT), ORANGE (80-89 COMPETITIVE), YELLOW (70-79 STRETCH), GREEN (<70 LOW FIT)
FILE ENDS: {now_str}
"""
    consolidated = header + "\n".join(all_entries) + footer
    with open(ALL_FILE, 'w') as f:
        f.write(consolidated)
    os.system("sync")
    print(f"  Consolidated file regenerated: {len(all_entries)} entries ({len(reliable_entries)} reliable + {pool_added} unreliable)")


def main():
    if len(sys.argv) < 2:
        print("Usage: merge-vacancies.py <json_results_path> [--source reliable|unreliable]")
        sys.exit(1)

    json_path = sys.argv[1]
    source = "reliable"
    if "--source" in sys.argv:
        idx = sys.argv.index("--source")
        if idx + 1 < len(sys.argv):
            source = sys.argv[idx + 1]

    target_file = UNRELIABLE_FILE if source == "unreliable" else RELIABLE_FILE

    new_jobs = load_jobs(json_path)
    content = read_file(target_file)

    if not content:
        print(f"Error: Target file not found or empty: {target_file}")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.system(f"cp {target_file} {BACKUP_DIR}/BACKUP_{ts}.txt")

    added_count = 0
    for job in new_jobs:
        score = int(job.get('SCORE', 0))
        if is_duplicate(content, job):
            continue
        entry = format_entry(job, score)
        if "=== FILE FOOTER ===" in content:
            content = content.replace("=== FILE FOOTER ===", entry + "=== FILE FOOTER ===")
        else:
            content += entry
        added_count += 1

    content = update_footer(content)

    with open(target_file, 'w') as f:
        f.write(content)
    os.system("sync")

    print(f"Added {added_count} new entries to {target_file}")
    regenerate_consolidated()


if __name__ == "__main__":
    main()
