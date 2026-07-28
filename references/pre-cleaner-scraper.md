# Pre-Cleaner Scraper Reference

## Purpose
Reduce token burn by 90%+ when scraping job pages without a browser. The `web_extract` tool sends raw HTML to the LLM, burning ~50,000-180,000 tokens per page. Pre-cleaning collapses this to ~5,000-15,000 tokens of readable text.

## Script
`config/scripts/web-clean.py`

- Fetches any URL with a real browser User-Agent
- Strips scripts, styles, nav, footers, SVGs, comments
- Collapses whitespace
- Hard-cuts at 40,000 chars by default (configurable via second arg)

## Usage Patterns

### Basic: clean + truncate at 40k chars
```bash
python3 config/scripts/web-clean.py https://www.impactpool.org/jobs/1210566
```

### Strict: truncate at 15k chars for very low token use
```bash
python3 config/scripts/web-clean.py https://www.impactpool.org/jobs/1210566 15000
```

## When NOT to Use web-clean.py
- **Taleo-based portals** (WHO, IAEA) — returns only session/login page, zero job data
- **ITU careers** — returns only cookie banner + navigation, no job listings
- **World Bank / WFP** — returns marketing content only, no job data
- **UNICEF detail pages** — requires browser session cookies
- **Pages requiring login** (SSO portals: UNDP, IMF, World Bank)

## When web-clean.py DOES Work
- **UNICEF listing page** (jobs.unicef.org/en-us/listing/) — partial HTML with job titles, locations, deadlines; pagination via `?page=N`
- **UNESCO listing** (careers.unesco.org/search/result) — returns structured table data (Title/Location/Type/Grade/Closing date) for 25 results per page; 3 pages total
- **UNDP** (jobs.undp.org/cj_view_jobs.cfm) — full job listings (longest-confirmed working portal)

## Updated Strategy (2026-05-14)
1. Try `web-clean.py` first on UNESCO and UNICEF listing pages (batch extraction of 25+ jobs)
2. For all other portals → use `browser_navigate` directly
3. Never use `web-extract` or `web-extract-plus` for UN job scanning

## Workflow for UN Job Extraction (No Browser Available)

1. Run `web-clean.py` on the target URL
2. Inspect the first 100 lines of output to confirm it contains the job title, deadline, grade, and location
3. If the page is clean, pass the text directly to the model in a simple prompt
4. If `web-clean.py` returns garbled text (dynamic JS-rendered page), fall back to `browser_navigate`

## Token Savings (Real Test on wikipedia.org/wiki/Internet)
- Raw HTML: 722,471 bytes (~180,000 tokens)
- Clean text: 41,007 bytes (~10,000 tokens)
- **Reduction: ~94%**

## Scrapling Stealthy-Fetch (New 2026-05-18)

For JS-rendered SPAs that web-clean.py can't handle, use the scrapling stealthy-fetch CLI.

### Syntax
```bash
scrapling extract stealthy-fetch <URL> <OUTPUT_FILE>
```
**REQUIREMENT**: Output file argument is mandatory. The command will fail without it.

### How It Works
- Uses Playwright-based stealth browser with Google referer
- Renders JavaScript, executes dynamic content
- Fetches full HTML after JS execution
- Saves to specified output file

### What It Gets Past
- Cloudflare (sometimes — works for UNITAR, GICHD, FAO, UNWTO, WMO, UNSSC, UNICRI, UNECA, UNESCAP, UNIDIR)
- JS-rendered SPAs (Workday, CSOD, Taleo initial HTML)
- Cookie consent walls

### What It Can't Get Past
- UNECE (all paths → 403 Cloudflare)
- UNESCWA (all paths → 403 Cloudflare)
- careers.un.org (CloudFront 403)

### Post-Fetch Processing
```bash
# Read the saved HTML file
python3 config/scripts/web-check.py file:///path/to/saved.html 6000
```
**NOTE**: web-check.py does NOT support file:// URLs. Read the file directly with Python instead:
```python
from pathlib import Path
html = Path('/tmp/fao_jobs.html').read_text()
# Then use regex or BeautifulSoup to extract data
```

### Recommended Pattern
1. `scrapling extract stealthy-fetch <URL> /tmp/<site>.html`
2. Read file: `html = Path('/tmp/<site>.html').read_text()`
3. Extract with regex: `re.findall(r'<h[2-4][^>]*>([^<]+)</h[2-4]>', html)`
4. Extract links: `re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', html)`

### Sites Where stealthy-fetch Works Better Than web-clean.py
- UNITAR, GICHD, UNWTO, WMO, UNSSC, UNICRI, FAO, UNECA, UNESCAP, UNIDIR
- World Bank CSOD initial HTML (but search requires browser)

### Sites Where Browser Is Still Needed
- IMF Workday (needs cookie acceptance + search interaction)
- World Bank CSOD (needs search box interaction)
- ITU (needs cookie dismissal + pagination clicks)
- Taleo portals (IAEA, WHO — needs keyword search + table parsing)
- UNHCR Workday (needs cookie acceptance)

## Hard Rule
**Never use `web_extract` or `web_extract_plus` for UN job scanning.** These tools send full raw HTML to the LLM and burn tokens unnecessarily. Always pre-clean first.
