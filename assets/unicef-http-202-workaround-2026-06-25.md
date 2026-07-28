# UNICEF JD Fetch Workaround — HTTP 202 Pattern

## Problem
The `run_unicef.py` script uses Scrapling to fetch UNICEF PageUp JD detail pages. When UNICEF's server is under load or the job is newly posted, the detail page returns **HTTP 202 (Accepted)** instead of HTTP 200. The script treats this as a fetch error and skips the JD.

## Symptoms
```
JD_!200: 3
```
in the UNICEF scan summary, with 0 JDs saved despite ICT-title candidates being found.

## Workaround
When UNICEF returns HTTP 202 for JD fetches, use the **browser directly** (Camoufox) to get the JD content:

1. Navigate to the job detail URL directly:
   ```
   https://jobs.unicef.org/en-us/job/{JOB_ID}/{slug}
   ```
   or the shorter form:
   ```
   https://jobs.unicef.org/en-us/job/{JOB_ID}
   ```

2. Extract the full JD text via `browser_console` with:
   ```javascript
   document.body.innerText
   ```

3. The UNICEF PageUp portal loads JD content server-side — no JavaScript rendering needed. The browser just needs to handle the cookie consent dialog (click the close button if it appears).

## Known ICT Candidates from Recent Scans
When the script reports ICT-title candidates but 0 saved, these are the JIDs to fetch manually:

| JID | Title Pattern | Category |
|-----|--------------|----------|
| 594029 | Innovation Specialist (Blockchain) P-3 | Innovation/Emerging Tech |
| 593975 | Knowledge Management Consultant | Knowledge Management |
| 593922 | Information Management Consultancy | Information Management |
