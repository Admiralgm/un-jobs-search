# UNICEF Job Scraping via Camoufox Browser

## Status
Camoufox v2.4.5+ handles UNICEF (jobs.unicef.org) **successfully**. The page loads, cookie dialog can be closed, and the search box supports `browser_type` + `browser_press(Enter)` to filter listings by keyword. **This is the preferred method.**

The only known Camoufox quirk on UNICEF: `browser_type` occasionally returns 500 Server Error on the first attempt. Recovery: navigate away and back (`browser_navigate(url)` again — no need to restart the server), then retry. The second attempt works consistently.

## Alternative: JavaScript DOM Extraction via browser_console

When `browser_type` repeatedly fails (rare on v2.4.5+), extract all jobs directly via JS from the unfiltered listing page.

### Step 1: Navigate to listing page (no filters)
```
browser_navigate("https://jobs.unicef.org/en-us/listing/")
```
Close cookie dialog if present:
```
browser_click(ref="@e3")  # cookie close button
```

### Step 2: Extract all job titles via JavaScript
```javascript
JSON.stringify(Array.from(document.querySelectorAll('h4')).map(h => {
  const link = h.closest('a') || h.querySelector('a');
  const jobNum = link?.href?.match(/job\/(\d+)/)?.[1] || '';
  return { title: h.innerText.trim(), id: jobNum, url: link?.href || '' };
}).filter(j => j.id))
```

### Step 3: Click "More Jobs" to load next batch
```javascript
document.querySelector('a.more-link.button').click();
```
Wait 2-3 seconds, then repeat Step 2.

### Step 4: Check remaining count
```javascript
document.querySelector('a.more-link.button')?.innerText || 'ALL LOADED'
```

### Step 5: Handle "stuck at 3" problem
The button becomes hidden after ~10-15 clicks. Extract all loaded data at once:
```javascript
JSON.stringify(Array.from(document.querySelectorAll('h4')).map(h => {
  const link = h.closest('a') || h.querySelector('a');
  const jobNum = link?.href?.match(/job\/(\d+)/)?.[1] || '';
  return { title: h.innerText.trim(), id: jobNum };
}).filter(j => j.id))
```

## Search-Driven Extraction (Preferred — Camoufox only)
1. Close cookie dialog: `browser_click(ref="@e3")`
2. Type keyword into search box: `browser_type(ref="@e10", text="Digital")`
3. Press Enter: `browser_press(key="Enter")`
4. Page filters results client-side. Extract with:
   ```javascript
   Array.from(document.querySelectorAll('article h4 a')).map(a => ({
     title: a.innerText.trim(),
     url: a.getAttribute('href'),
     id: a.href.match(/job\/(\d+)/)?.[1] || ''
   }))
   ```
5. Repeat for keywords: IT, ICT, Digital, AI, Artificial Intelligence, Telecom, Innovation, Data, 00137311
6. **Known high-value Digital search hits (June 2026):** Programme Manager Infrastructure Finance P-4 Geneva (Giga), GIS Lead P-4 Florence, Evaluation Specialist AI/ML P-4 Rome, Digital Solutions Engineer Consultant Copenhagen, Solutions Architecture/Data Engineering Consultant Copenhagen

## Key Selectors
- Job title links: `h4 a` elements inside `<article>`
- Search box: `textbox` with placeholder "Search for keywords" (ref @e10)
- Job URL pattern: `/en-us/job/{numeric-id}/...`
- "More Jobs" button: `a.more-link.button`
- Button text: "More Jobs {remaining-count}"

## Pagination Behavior
- Initial page: ~20 jobs
- Each click: ~20 more
- Button becomes hidden after ~10-15 clicks (stuck at ~3 remaining)
- Total extractable: ~200-221 jobs

## Vacancy ID Format
UNICEF uses a dual identifier system:
- **System Job ID (job no):** 5-6 digit numeric (e.g., 593362) — found in URL `/en-us/job/{job_no}/...`
- **Ref Number:** #XXXXXX format in title (e.g., #00137311) — the canonical UNICEF vacancy reference
- Both IDs appear in the listing page `<h4>` headings
- Tracker entry format: `{SystemJobID}/#{RefNumber}` (e.g., `593362/#00137311`)

## Detail Page Extraction
```javascript
document.querySelector('article').innerText
```
Returns complete job description with metadata header. Key fields appear in the first few lines:
- `Job no: {system_id}`
- `Contract type: Temporary Appointment / Fixed Term / Consultant`
- `Duty Station: {city}`
- `Level: P-3 / NO-2 / G-6`
- `Location: {country}`
- `Categories: Innovation / Programme / Supply` etc.

## Detail Page Metadata Parsing
The metadata line after "Apply now" contains: contract type, duty station, level, location, categories.
Example from job #00137311 (Innovation Specialist P-3):
```
Job no: 593362
Contract type: Temporary Appointment
Duty Station: Stockholm
Level: P-3
Location: Sweden
Categories: Innovation
```

## Keywords Yield (June 2026 Scan)
- **"IT" search**: ~40 jobs listed but most are non-ICT (construction, social policy, education). ICT-relevant: GIS Lead P-4, AI/ML Eval Specialist P-4, ICT Intern. Yield: ~3-4 ICT.
- **"Digital" search**: ~18 mostly ICT-relevant jobs. Highest-quality results for Digital Impact Division roles (P-3/P-4 Geneva), Digital Solutions Engineer (Copenhagen), GIS Lead (Florence).
- **"00137311" (Ref number search)**: Finds exact job by reference. Returns single result when job is active.
- **"Innovation" search**: Unknown yield — worth testing for Office of Innovation roles (Stockholm, Valencia hubs).

## Notes
- Deadlines NOT visible in listing page snapshots — must visit individual job pages
- Job detail pages are JS-rendered SPAs — use `browser_navigate` for full details
- Searching by ref number (#XXXXXX) via the keyword box works reliably
- Detail pages contain full TOR with Minimum Requirements, Desirables, and competencies sections