# ICRC (International Committee of the Red Cross) Job Extraction

Updated: 2026-05-28

## Portal Overview
- Careers URL: https://careers.icrc.org
- Platform: SuccessFactors / Taleo-based
- RSS feed available for category-based job listings
- Belgrade Hub roles are **open to Serbian nationals** — do NOT exclude

## Access Method

### Primary: RSS Feed (fastest, curl-based)
```
curl "https://careers.icrc.org/services/rss/category/?catid=3807301" 2>/dev/null
```

The RSS feed returns XML with `<item>` elements containing:
- `<title>` — Job title
- `<link>` — Full URL to job detail page
- `<description>` — Brief text (location, contract type, deadline)
- `<pubDate>` — When it was posted

**Extraction pattern:**
Parse each `<item>` block via Python XML parsing or regex. Vacancy ID is numeric in the URL path (e.g., careers.icrc.org/job/{numeric-id}/).

### Secondary: Browser (for detail pages)
- browser_navigate works on job detail pages
- Some pages at careers.icrc.org may return 500 when accessed directly
- Camoufox browser works for the main careers.icrc.org page (job listing/grid view)

## Keyword Filtering on RSS Feed
The ICRC RSS feed uses category IDs. The main ICT category ID is:
- catid=3807301 — Information Management & Technology / Professional roles

No other known catid produces ICT-relevant results.

## Exclusion Rules
- **Ukraine-restricted roles:** Exclude if title or description mentions Ukraine. ICRC posts roles specifically for the Ukraine delegation.
- **Manila SSC (Shared Services Centre):** Roles restricted to local residents/nationals of the Philippines. Exclude.
- **Kyiv / Ukraine locations:** Exclude always.

## Belgrade Hub
- ICRC has a regional logistics/IT hub in Belgrade
- **Do NOT exclude these roles** — Serbian nationals are eligible
- These appear with location "Belgrade" or "Serbia" in the RSS feed description

## Typical Results Per Scan
- ~5-7 jobs in the ICT category RSS feed
- Most are P-3 or P-4 level
- ~1-2 per scan may be Ukraine-excluded
- ~1 per scan may be Manila SSC-restricted
- ~2-3 genuine P-level ICT roles per scan on average

## Vacancy ID Format
- Numeric ID from URL: `https://careers.icrc.org/job/{numeric-id}/`
- Example: https://careers.icrc.org/job/12607/

## Triplicate Dedup Bug (CRITICAL)
ICRC's SuccessFactors system sometimes lists the same job in multiple categories, resulting in the same job appearing up to 3 times in combined results. **Deduplicate by title + deadline combination** before adding to tracker files.

## Scoring Context
ICRC roles are typically:
- Information Management Officer
- ICT Officer
- Data & Analytics Officer
- Digital Transformation roles
- Cyber Security Officer

Grades: P-3, P-4 (mid-senior level)
Deadlines: Typically 2-4 weeks from posting date
