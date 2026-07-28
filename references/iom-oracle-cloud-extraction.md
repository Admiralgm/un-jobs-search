# IOM Oracle Cloud Career Portal — Extraction Guide
# URL: https://fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs
# Last verified: 2026-05-14

## Access
- Method: browser_navigate (NOT web-clean.py — JS-rendered SPA)
- No login required for search or viewing job details
- JS-rendered SPA — content loads dynamically
- Returns 174+ job openings (as of May 2026)
- OG title meta tag: "IOM Careers" — confirms official IOM recruitment platform
- Hosted on Oracle Cloud (fa.ocs.oraclecloud.com) — third-party platform, not iom.int

## Old vs New URL
- OLD: iom.int/careers — blocked by bot detection (Access Denied)
- NEW: fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs

## Extraction Pattern

### Step 1: Navigate
```
browser_navigate: https://fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs
```

### Step 2: Search for keyword
```
browser_type: ref=e36 (Find Jobs combobox), text="information technology"
browser_click: ref=e14 (Search for Jobs button)
```

### Step 3: Extract job listings via browser_console
```javascript
document.body.innerText
```
- Shows job title, location, grade, recruiting type, deadline
- "SHOW MORE RESULTS" button loads additional results

### Step 4: Navigate to job detail
- Click on job link (listitem with cursor:pointer)
- Job detail URL pattern: .../CX_1001/job/XXXXX

## Job Fields Available
- Job title
- Location (City, Country)
- Grade (P-1 through P-5, NO-A, UG, G-4, etc.)
- Recruiting Type (Professional, National Officer, Consultant, Intern, General Service)
- Apply Before date
- Contract type (from detail page)
- Vacancy type
- Org type

## Notes
- Search for "information technology" returns ~15 ICT-related jobs
- Search for "digital" or "AI" also returns relevant results
- No login required — all jobs visible without authentication
- To apply, candidates must create a profile via "Apply Now" button
- Contact: talentpool@iom.int for technical assistance
