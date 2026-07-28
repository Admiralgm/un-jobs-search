# ITU Careers Extraction Guide

## Access
- **Job listings page:** https://jobs.itu.int/go/View-all-categories/8942455/
- **Keyword search:** Use browser search box after navigating to listings
- **No login required** for search and browse
- JS-rendered Taleo-style SPA
- Total jobs: ~34

## Extraction via Browser

### Step 1: Navigate to full listing
```javascript
browser_navigate(url="https://jobs.itu.int/go/View-all-categories/8942455/")
```
Accept cookies if prompted.

### Step 2: Handle pagination
First page shows 25 results. Click "Next" for remaining results (typically 9 more on page 2).
```javascript
browser_click(ref="e24")  // Next page button
```

### Step 3: Extract via browser_console
```javascript
const rows = document.querySelectorAll('table tbody tr, table tr[role="row"], table tr');
const jobs = [];
rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length >= 4) {
        const titleLink = cells[0]?.querySelector('a');
        jobs.push({
            title: titleLink?.textContent?.trim() || cells[0]?.textContent?.trim(),
            url: titleLink?.href || '',
            location: cells[1]?.textContent?.trim() || '',
            date: cells[2]?.textContent?.trim() || '',
            ref: cells[3]?.textContent?.trim() || ''
        });
    }
});
JSON.stringify(jobs, null, 2);
```

## Keyword Results (validated 2026-06-01):
- Full category listing: ~23 results on the /go/ page (down from 34 in May)
- **Majority are roster positions** (open-ended, no fixed deadline)
- Only 2-3 non-roster positions visible at any time (Junior Project Officer, JPO Korea, specialists)
- Vacancy IDs are 10-digit numeric (e.g., 993610255, 1348117555)

## Job Portfolio Character (critical for expectations)
ITU's /go/ page shows mostly **rosters** — not active P-level openings:
- Roster - Green Digital Transformation Consultant
- Roster - Software Developer and Metadata Engineer
- Roster - Senior ICT/Digital Policy Consultant
- Roster - Senior CIRT Technical/Operations/Governance
- Roster for Telecommunication/ICT Statistics Programme
- BDT Digital Ecosystem Consultant Roster
- Disaster Preparedness Consultant (National Emergency Telecom Plans)
- Innovation Ecosystem Consultant

These are pool entries — User can apply to join the roster, not to a specific job.
Non-roster ICT roles at ITU are rare. The actual P-level vacancies (when they appear) are usually on a separate view or posted/removed quickly.

## Known ICT-Relevant Jobs (2026-05-21 scan):
- Senior ICT/Digital Policy, Regulatory, Economic Analyst — P-5, deadline 2026-06-30 (ref: 993610255)
- Emerging Technology Consultant — SSA, deadline 2026-08-30 (ref: 1348117555)
- Roster - Software Developer and Metadata Engineer Consultant for OCI — SSA/Open (ref: 1352319255)
- Various other ICT and radio communication roles

## Notes
- ITU job portal uses Taleo infrastructure similar to IAEA
- web-preclean.py returns empty content for ITU (JS-rendered)
- `jobs.itu.int` main page links may 404 — use the `/go/View-all-categories/8942455/` URL directly
- Job detail URLs follow pattern: `/job/Location-Title/REF_NUMBER/`