# WHO Taleo RSS Extraction Technique

## Problem
WHO Taleo (careers.who.int/careersection/ex/jobsearch.ftl) is a JS-rendered SPA. Job listings appear in a dynamic `<tbody>` that remains empty in snapshots. Job detail pages also return empty via web-preclean.py. Keyword "ICT" and "AI" return 0 results.

## Solution: RSS Feed + Multi-Line View
The Taleo system exposes an RSS feed for any search. Found in session 2026-05-15:

1. Navigate to `https://careers.who.int/careersection/ex/jobsearch.ftl?lang=en`
2. Type "Digital" into the Keyword field and click "Search for jobs" — yields 7 results
3. Click the "Single-line" / "Job list in single line view" link (ref e5 in browser snapshot) to switch to multi-line view
4. This renders the RSS/XML feed inline in the browser DOM as a `<StaticText>` element
5. Use `browser_snapshot(full=true)` to capture the entire page including the inline RSS XML
6. Parse the RSS from the snapshot text — it contains:
   - `<title>` — Job title
   - `<link>` — URL with job number (e.g., `...&job=2601813`)  
   - `<description>` — Brief description (may be truncated)
   - `<pubDate>` — Posting date

## Found in Session 2026-05-15
7 WHO Digital jobs:
- **Roster for IHIP – Web Developer** (job=2601813, New Delhi, closes May 28)
- **International Consultant - AI Governance** (job=2601648, Manila — already in tracker)
- **SSA - Climate Change Health Project Officer** (job=2601712)
- **Information and Knowledge Management Consultant** (job=2601705, Ukraine-located — exclude)
- **National Consultant Childhood Cancer** (job=2601690)
- **National Consultant NCD** (job=2601640)
- **Integrated Service Delivery Officer** (job=2601633, Guinea-Bissau)

## Vacancy ID Convention for WHO
`WHO-<jobnumber>-<SHORTNAME>` (e.g., `WHO-2601813-WEB`, `WHO-EMTECH`)

## Limitations
- Job grade/level and exact deadlines are NOT in the RSS feed — these require browsing job detail pages (which are also JS-rendered SPAs)
- The RSS only includes jobs matching the current search keyword
- Only 7 "Digital" results; WHO Taleo is not the richest source for ICT jobs
