# WHO Taleo Career Portal — Extraction Guide
# URL: https://careers.who.int/careersection/ex/jobsearch.ftl
# Last verified: 2026-06-01

## Access
- Method: browser_navigate (NOT web-clean.py — returns 403)
- No login required for search
- JS-rendered SPA — content loads dynamically
- Returns 44+ job openings (as of May 2026)
- Camoufox Python context manager works well: `with Camoufox() as browser:` → `page.goto(url)` → `page.inner_text('body')`

## Scrapling Stealthy-Fetch Note (2026-05-18)
The correct CLI syntax for fetching JS-rendered pages:
```bash
scrapling extract stealthy-fetch <URL> <OUTPUT_FILE>
```
Output file argument is MANDATORY. Works for UNITAR, GICHD, FAO, UNWTO, WMO, UNSSC, UNICRI, UNECA, UNESCAP, UNIDIR. Fails for UNECE, UNESCWA (Cloudflare 403).

## Extraction Pattern

### Step 1: Navigate
```python
page.goto("https://careers.who.int/careersection/ex/jobsearch.ftl")
time.sleep(4)  # JS needs time to render the search form
```

### Step 2: Search for keyword
The Taleo search box is available as `input[type="text"]` or `input[id*="keyword"]`:
```python
search_input = page.query_selector('input[type="text"]')
search_input.fill("Digital")
page.keyboard.press("Enter")
time.sleep(5)
text = page.inner_text("body")
```

### Step 3: Extract job IDs from body text
Job IDs are 7-digit numbers that appear next to the title in the listings:
```python
import re
id_match = re.search(r'\b(\d{7})\b', line)
```

### Step 3a: Switch to multi-line view & extract jobs via browser_console
```javascript
// After clicking the multi-line view switch (ref=e5), the table populates
// Extract job details with:
const jobs = Array.from(document.querySelectorAll('table#jobs tbody tr')).map(row => {
  const a = row.querySelector('a[href*="jobdetail"]');
  if (!a) return null;
  const cells = row.querySelectorAll('td');
  return {
    title: (a.title || a.textContent).trim(),
    href: a.href,
    location: cells[1]?.innerText?.trim() || '',
    date: cells[2]?.innerText?.trim() || '',
    jobNum: (a.href.match(/job=(\d+)/)||[,''])[1]
  };
}).filter(Boolean);
```
**This is the fastest and most reliable extraction method.** The RSS feed workaround is backup if this fails.

### Step 3b (backup): RSS feed extraction
Use `browser_click` on the "Create an RSS feed" button to get the RSS URL:
```javascript
window.location.href
```
Then navigate to the RSS URL in a new tab and fetch with Python XML parsing.

### Step 4: Get detail page info
```python
page.goto(f"https://careers.who.int/careersection/ex/jobdetail.ftl?job={job_id}")
time.sleep(4)
text = page.inner_text("body")
# Key fields to extract: Grade, Contractual Arrangement, Closing Date, Primary Location, Organization
```

### Step 5: Dedup across keywords
Multiple keywords return overlapping results. Build a dict keyed by job ID, then dedup before evaluation.

## Keyword Search Strategy (updated 2026-06-01)
**Use ALL of these keywords — they return DIFFERENT result sets. A single keyword will miss jobs:**

| Keyword | Approx. jobs | Quality |
|---------|-------------|---------|
| `Digital` | 8 | Best ICT yield — AI Software Engineer Lead, Data Engineering, GIS |
| `Data` | 10 | Highest volume — catches Data Engineering, Info Management, health roles |
| `IT` | 9 | Broad — catches Technical Officer, Consultant, National Consultant roles |
| `AI` | 4 | Catches AI-related (AI Software Engineer Lead, Pharmacovigilance, etc.) |
| `Software` | 1 | Only Software-connected roles |
| `Innovation` | 1 | WHE Team Lead |
| `Information` | 3 | National Information Consultant, NPO Health Promotion, etc. |
| `ICT` | 0 | No returns — use `IT` or `Information` instead |
| `Telecom` | 0 | No returns |

**Only ~4 genuine ICT roles exist on WHO at any time** (confirmed across multiple scans May-June 2026):
- AI Software Engineer Lead (P4, Istanbul, Jun 17)
- Consultant - Data Engineering Developer (Brazzaville, Jun 4)
- Consultant GIS Specialist (Brazzaville, Jun 4)
- International Consultant - AI-assisted age friendly environment (Jun 11)

The remaining 30+ results are health officers, national consultants, assistants — not ICT.
Always dedup and filter by job title before reporting.

## Smart Villages and Smart Islands (Asia-Pacific)