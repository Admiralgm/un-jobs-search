# UNJobNet Extraction Patterns

## Access

- **Public jobs page:** `https://www.unjobnet.org/jobs` — returns 200, no Cloudflare
- **DO NOT use:** `/myjobs` (redirects to login), `/search?q=` (returns 404)
- **Total jobs:** ~3,594 at any time

## Method 1: Scrapling Stealth CLI (Recommended)

```bash
# Download page HTML
scrapling extract stealthy-fetch "https://www.unjobnet.org/jobs" /tmp/unjobnet_p1.html \
  --solve-cloudflare --block-webrtc --hide-canvas

# Download additional pages (URL params work for page navigation)
scrapling extract stealthy-fetch "https://www.unjobnet.org/jobs?page=2" /tmp/unjobnet_p2.html \
  --solve-cloudflare --block-webrtc --hide-canvas
```

## Method 3: web-preclean.py (NEW — confirmed 2026-05-15, PREFERRED)

```bash
python3 config/scripts/web-preclean.py "https://www.unjobnet.org/jobs" 15000
```

Returns 75KB raw -> 4KB clean markdown (95% reduction via regex). SSR-rendered HTML with 3,488+ jobs. No scrapling/stealth-fetch needed. Much faster than scrapling.

**Important finding (2026-05-15):** The home page shows ALL recent jobs regardless of search keyword filter. Adding `?search=ICT+OR+AI` to the URL returns the SAME set — the server-side Vue.js SPA doesn't filter on URL params. To find ICT/AI/Digital jobs, parse the full listing with regex/trafilatura output and filter client-side.

**Limitation:** Job detail pages require individual navigation via `web-preclean.py <detail-url>`. The listing page shows title, organization, location, deadline but NO grade info. Deadline format is inconsistent: "Close on 28 May 2026", "Closing soon: 22 May 2026", "Posted 59 minutes ago". No direct Vacancy ID — derive as `UNJN-<numeric-id>` from the job detail URL.

## HTML Parsing (Python)

The page is a Vue.js SPA but renders server-side HTML. Parse with regex:

```python
import re

with open('/tmp/unjobnet_p1.html', 'r') as f:
    html = f.read()

# Split into job cards
parts = re.split(r'(?=<a class="py-2 link-primary h6 fw-bold" href="/jobs/detail/\d+">)', html)

for part in parts[1:]:
    # Job ID
    m = re.search(r'href="/jobs/detail/(\d+)">', part)
    if not m: continue
    job_id = m.group(1)
    
    # Title
    t = re.search(r'href="/jobs/detail/\d+">(.*?)</a>', part, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', t.group(1)).strip().replace('&amp;', '&') if t else ''
    
    # Organization
    o = re.search(r'<a class="link-dark" href="/organizations/[^"]*">(.*?)</a>', part, re.DOTALL)
    org = re.sub(r'<[^>]+>', '', o.group(1)).strip() if o else ''
    
    # Location
    l = re.search(r'<a class="link-darkx" href="/jobs\?locations\[\]=[^"]*">([^<]+)</a>', part)
    loc = l.group(1).strip() if l else ''
    c = re.search(r'<a class="text-darkx" href="/jobs\?locations\[\]=[^"]*">\(?\s*([^)<]+)\s*\)?</a>', part)
    country = c.group(1).strip() if c else ''
    full_loc = f"{loc}, {country}" if loc and country else loc or country
    
    # Grade, date, contract from context block
    ctx = part[:800]
    g = re.search(r'((?:P-\d+|D-\d+|G-\d+|NO-\d+|IPSA-\d+|NPSA-\d+|ICS-\d+|I-\d+)[^<]{0,40})', ctx)
    grade = g.group(1).strip() if g else ''
    d = re.search(r'(Posted \d+ (?:hour|day|week|month)s? ago|Posted Just now|Closing soon|Close on \d+ \w+ \d{4})', ctx)
    date = d.group(1).strip() if d else ''
    ct = re.search(r'(Full-time|Part-time|Consultancy|Temporary|Internship|Fixed Term)', ctx)
    contract = ct.group(1).strip() if ct else ''
```

## Job Detail URLs

- Pattern: `https://www.unjobnet.org/jobs/detail/<numeric-id>`
- Example: `https://www.unjobnet.org/jobs/detail/86214360`

## Vacancy ID Convention

- Format: `UNJN-<numeric-id>` (e.g., `UNJN-86214360`)
- Always prefix with `UNJN-` to distinguish from Impactpool IDs

## Deduplication

- Check against existing `VACANCY ID` and `HYPERLINK` fields in the tracker file
- UNJobNet IDs should not overlap with Impactpool IDs (different prefix)

## Filtering for ICT/AI Jobs

Use this regex pattern on job titles:
```python
ict_pattern = re.compile(
    r'ICT|digital|AI|technology|information|data|cyber|network|software|cloud|platform|'
    r'innovation|transformation|analytics|DevOps|engineer|developer|programmer|technical|'
    r'IT |information technology',
    re.IGNORECASE
)
```

## Known Limitations

- No server-side filtering via URL params (Vue.js SPA)
- Page shows ~20 jobs per page, infinite scroll for more
- Location/country extraction can be inconsistent
- Grade info not always present in card (may need detail page visit)
- All entries are UNRELIABLE (aggregator) — must verify on official portal
- `execute_code` Python regex on 141K HTML can timeout (>300s); use terminal heredoc for large files
