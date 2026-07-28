# COE Talents Career Portal — Extraction Guide
# URL: https://talents.coe.int/en_GB/careersmarketplace/SearchJobs
# Last verified: 2026-05-14

## Access
- Method: browser_navigate (NOT web-clean.py — JS-rendered SPA, web-clean.py only gets page 1)
- No login required for search or viewing job details
- JS-rendered SPA — content loads dynamically
- Returns 13+ job openings (as of May 2026)
- Behind Cloudflare but allows browser access (200 response)

## Old vs New URL
- OLD: coe.int/jobs — Cloudflare-blocked
- NEW: talents.coe.int/en_GB/careersmarketplace/SearchJobs

## Extraction Pattern

### Step 1: Navigate
```
browser_navigate: https://talents.coe.int/en_GB/careersmarketplace/SearchJobs
```

### Step 2: Accept cookies (if banner appears)
```
browser_click: ref=e2 (Accept all button)
```

### Step 3: Extract page 1 job listings via browser_console
```javascript
document.body.innerText
```
- Shows "1-6 of N results" with job title, location, recruitment type, deadline, entity

### Step 4: Paginate via JS click (URL params do NOT work)
The SPA ignores URL page parameters. Must click pagination buttons via IIFE:
```javascript
// Click page N (example: page 2)
(function() { var p = document.querySelector('[class*=pagination]'); if (!p) return 'no pagination'; var btns = p.querySelectorAll('a, button'); var target = Array.from(btns).find(function(a) { return a.textContent.trim() === '2'; }); if (target) { target.click(); return 'clicked'; } return 'not found'; })()
```

### Step 5: Extract after each page click
```javascript
document.body.innerText
```

### Step 6: Navigate to job detail
- Click on job heading link
- Job detail URL pattern: talents.coe.int/en_GB/careersmarketplace/JobDetail?jobId=XXXXX

## Job Fields Available
- Job title
- Vacancy number (e.g., 1234/2026)
- Location (City, Country)
- Recruitment type (Secondment, External recruitment (local/international))
- Posted date and deadline
- Entity (Directorate/Section)
- Grade

## Pagination Details
- 6 jobs per page (default)
- URL params (?page=2) are IGNORED — must use JS click via IIFE
- After JS click, wait 1-2 seconds before extracting innerText

## Notable Roles (May 2026)
- Head of the Artificial Intelligence and Data Protection Division (1234/2026, Strasbourg, External international)

## Recruitment Type Glossary
- Secondment = internal/candidate from member states
- External recruitment (international) = open to all nationalities
- External recruitment (local) = local hire only
