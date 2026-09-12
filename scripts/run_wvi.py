#!/usr/bin/env python3
"""run_wvi.py — World Vision International (WVI) Workday cxs API scraper v1.0 (2026-09-08).

Portal: https://worldvision.wd1.myworkdayjobs.com/WorldVisionInternational
Pattern: references/workday-cxs-api-pattern.md (in un-jobs-search skill)
Full-portal scan (2026-09-08, 304 JDs): JD_FILES/NGO_WVI/WVI-PORTAL-SCORING-REPORT.md

ELIGIBILITY ARCHITECTURE (do not "fix" this filter without re-reading the report):
  ~90% of postings are "Local Applicants Only" (national recruitment in ~60
  countries). The global IT/digital cluster is additionally gated to "countries
  where WVI is legally registered to operate" — Serbia is NOT a WVI registration
  country. Only roles whose JD footer says
      "Local and International Applicants (IA's) Accepted"
  are potentially reachable → THIS SCRIPT SAVES ONLY THOSE.
  Full-portal dumps happen on explicit deep-scan requests, not on rotation.

Known traps (all verified 2026-09-08):
  - Pagination: offset 0 returns total=N; every later page returns total=0 but
    still returns 20 jobPostings. NEVER break on `total` — paginate until two
    consecutive empty batches (hard cap 600).
  - workerSubType facet tagging is unreliable (Mexico office job tagged
    "International") — eligibility comes ONLY from JD body text.
  - cxs JSON contains NO closing date; deadlines appear only inline in JD text.
  - Roster/Talent Pipeline roles are pre-qualification pools (preference layer,
    not funded vacancies) — they pass the IA filter and are saved; scoring
    flags them via the scoring engine §7.2.
  - Transient 502s occur → retry x5 with backoff.

Output: JD_FILES/NGO_WVI/WVI_{reqId}_{title}.md (only NEW internationally-open JDs)
DONE line: "DONE: N saved (IA-accepted)"
"""
import json
import re
import sys
import time
import urllib.request
import html as html_mod
from pathlib import Path

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
OUTDIR = WORKDIR / "JD_FILES" / "NGO_WVI"
RAWDIR = OUTDIR / "jd_raw"
OUTDIR.mkdir(parents=True, exist_ok=True)
RAWDIR.mkdir(parents=True, exist_ok=True)

TENANT = "worldvision"
SITE = "WorldVisionInternational"
CXSB = f"https://{TENANT}.wd1.myworkdayjobs.com/wday/cxs/{TENANT}/{SITE}"
HDRS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}
IA_OK = re.compile(r"Local and International Applicants", re.I)
DEADLINE_INLINE = re.compile(
    r"(?:application deadline|closing date|apply before|deadline for applications)\s*[:\-]?\s*([A-Za-z0-9, /]+?\d{4})",
    re.I,
)


def req(url, payload=None, attempts=5):
    for a in range(attempts):
        try:
            if payload is None:
                r = __import__("urllib.request", fromlist=["request"]).Request(url, headers=HDRS)
            else:
                r = __import__("urllib.request", fromlist=["request"]).Request(
                    url, data=json.dumps(payload).encode(), headers=HDRS, method="POST"
                )
            with __import__("urllib.request", fromlist=["request"]).urlopen(r, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception:
            if a == attempts - 1:
                raise
            time.sleep(1.5 * (a + 1))


def html_to_text(h):
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"</(p|div|li|h[1-6]|tr)>", "\n", h)
    h = re.sub(r"<li[^>]*>", "- ", h)
    h = re.sub(r"<h[1-6][^>]*>", "\n## ", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = html_mod.unescape(h)
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r"\n\s*\n\s*\n+", "\n\n", h)
    return h.strip()


def existing_jids():
    """Dedupe against ANY prior WVI fetch (JR*.md deep-scan files or WVI_*.md)."""
    ids = set()
    for f in OUTDIR.glob("*.md"):
        m = re.match(r"(?:WVI_)?(JR\d+|R\d{5})", f.name)
        if m:
            ids.add(m.group(1))
    return ids


def main():
    # 1) listings (pagination trap: later pages report total=0)
    all_jobs, empty_streak = [], 0
    for off in range(0, 600, 20):
        d = req(f"{CXSB}/jobs", {"appliedFacets": {}, "limit": 20, "offset": off})
        batch = d.get("jobPostings", [])
        if not batch:
            empty_streak += 1
            if empty_streak >= 2:
                break
            continue
        empty_streak = 0
        all_jobs.extend(batch)
        time.sleep(0.25)

    seen, jobs = set(), []
    for j in all_jobs:
        ep = j.get("externalPath")
        if ep and ep not in seen:
            seen.add(ep)
            jobs.append(j)
    print(f"LISTINGS: {len(jobs)} deduped (portal total field: {all_jobs and d.get('total', '?')})")

    # 2) per-JD: fetch, keep only internationally-open, skip already-saved
    have = existing_jids()
    saved = skipped_existing = skipped_local = errors = 0
    for j in jobs:
        ep = j.get("externalPath", "")
        m = re.search(r"_((?:JR)?R?\d{4,7})(?:-\d+)?$", ep)
        jid = (j.get("bulletFields") or [None])[0] or (m.group(1) if m else ep.rsplit("_", 1)[-1])
        title = j.get("title", "?").strip()
        if jid in have:
            skipped_existing += 1
            continue
        try:
            d = req(CXSB + ep)
        except Exception as e:
            errors += 1
            print(f"ERROR: {jid} {type(e).__name__}")
            continue
        info = d.get("jobPostingInfo", {}) or {}
        body_html = info.get("jobDescription", "") or ""
        body = html_to_text(body_html)
        if not IA_OK.search(body):
            skipped_local += 1
            # keep raw payload for audit, but no markdown
            try:
                (RAWDIR / f"{jid}.json").write_text(json.dumps(d, ensure_ascii=False))
            except Exception:
                pass
            continue
        locs = [info.get("location", "")] + list(info.get("additionalLocations") or [])
        loc = " | ".join(x for x in locs if x)
        dm = DEADLINE_INLINE.search(body)
        ddl = f"**Deadline:** {dm.group(1).strip()}\n\n" if dm else "**Deadline:** Not specified (Workday rolling)\n\n"
        out = OUTDIR / f"WVI_{jid}_{re.sub(r'[^A-Za-z0-9]+', '_', title)[:60]}.md"
        out.write_text(
            f"# {jid} - {title}\n\n"
            f"- **Organisation:** {(d.get('hiringOrganization') or {}).get('name', 'WVI')} (World Vision International - Workday)\n"
            f"- **Location:** {loc}\n"
            f"- **Employment type:** {info.get('timeType', '?')}\n"
            f"- **Posted:** {info.get('postedOn', '?')} | Start: {info.get('startDate', '?')}\n"
            f"- **URL:** {info.get('externalUrl', '')}\n"
            f"- {ddl}"
            f"- **Filter:** internationally open (IA accepted) - saved by run_wvi.py {time.strftime('%Y-%m-%d')}\n\n"
            f"## Job Description\n\n{body}\n",
            encoding="utf-8",
        )
        try:
            (RAWDIR / f"{jid}.json").write_text(json.dumps(d, ensure_ascii=False))
        except Exception:
            pass
        saved += 1
        print(f"SAVED: {jid} - {title[:60]}")

    print(f"WVI: {len(jobs)} listings | {saved} new IA-accepted saved | "
          f"{skipped_local} local-only skipped | {skipped_existing} already saved | {errors} errors")
    print(f"DONE: {saved} saved (IA-accepted)")


if __name__ == "__main__":
    main()