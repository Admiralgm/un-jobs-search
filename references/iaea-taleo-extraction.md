# IAEA Taleo Extraction Guide

## Access
- **Main portal:** https://iaea.taleo.net/careersection/ex/jobsearch.ftl
- **Keyword search URL:** https://iaea.taleo.net/careersection/ex/jobsearch.ftl?keyword=ICT (or `?keyword=technology`)
- **Job detail URL pattern:** https://iaea.taleo.net/careersection/ex/jobdetail.ftl?job=YYYY/XXXX (e.g., `?job=2026/0169`)
- **No login required** for search and browse
- JS-rendered Taleo SPA
- Total jobs: ~30

## Extraction via Browser

### Step 1: Navigate to search
```javascript
browser_navigate(url="https://iaea.taleo.net/careersection/ex/jobsearch.ftl")
```

### Step 2: Keyword search
Type keywords in the search box and click search:
```javascript
browser_type(ref="e5", text="ICT")     // or "technology", "data"
browser_click(ref="e7")                  // Search button
```

Or use direct URL:
```
browser_navigate(url="https://iaea.taleo.net/careersection/ex/jobsearch.ftl?keyword=technology")
```

### Step 3: Extract results via browser_console
```javascript
const rows = document.querySelectorAll('table tbody tr, table tr');
const jobs = [];
rows.forEach(row => {
    const titleLink = row.querySelector('a[href*="jobdetail"]');
    if (titleLink) {
        const cells = row.querySelectorAll('td');
        jobs.push({
            title: titleLink.textContent.trim(),
            url: titleLink.href,
            location: cells[1]?.textContent?.trim() || '',
            grade: cells[2]?.textContent?.trim() || '',
            deadline: cells[3]?.textContent?.trim() || ''
        });
    }
});
JSON.stringify(jobs, null, 2);
```

## Keyword Results (validated 2026-05-21):
- `ICT` — 1 result (Consultant - ERP Oracle Functional and Technical)
- `technology` — 7+ results (NSIM Officer P-4, Scientific Data Manager P-4, CIO D-1, Associate SWE P-2, etc.)
- `data` — 5+ results (Scientific Data Manager, Statistical Data Analyst, Data Management Officer)
- `digital` — 0 results
- `information` — several results including security/information management roles

## ⚠️ CRITICAL: Deadline Verification
IAEA Taleo has been observed showing DIFFERENT deadlines between scans for the same job:
- **Nuclear Security Information Management Officer (P-4)**: Was recorded as 2026-06-15 in tracker file, but live portal showed 2026-05-24. The earlier date was authoritative.
- Always verify deadlines against the live portal when scanning
- If a live deadline is EARLIER than what's recorded, update immediately and flag as urgent
- This is especially common with IAEA, which may publish corrected deadlines without notice

## Known ICT-Relevant Jobs (2026-05-21 scan):
- Chief Information Officer (CIO), D-1 — deadline 2026-06-20
- Nuclear Security Info Mgmt Officer (Tech Lead), P-4 — deadline 2026-05-24 (CORRECTED from 06-15)
- Information and Computer Security Officer (Tech Lead), P-4 — deadline 2026-06-15
- Scientific Data Manager, P-4 — deadline 2026-06-10
- Statistical Data Analyst, P-3 — deadline 2026-06-10
- Consultant - ERP Oracle Functional and Technical — deadline 2026-06-03
- Associate Software Engineer (SGIS), P-2 — deadline 2026-06-15
- Section Head (INPRO), P-5 — deadline 2026-05-31
- Instrumentation Engineer, P-3 — deadline 2026-06-03