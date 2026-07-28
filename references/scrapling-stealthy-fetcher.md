# Scrapling StealthyFetcher — JS-Rendered SPA Extraction

## When to Use
When `browser_navigate` returns empty or partial content for JS-rendered SPAs.
Confirmed working for: World Bank CSOD, IMO Portal, WFP Workday.

## Installation
Already installed on this system:
- Python: /Library/Frameworks/Python.framework/Versions/3.13/bin/python3
- Package: scrapling v0.4.7

Verify:
```
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -c "from scrapling import StealthyFetcher; print('OK')"
```

## Pattern
```python
from scrapling import StealthyFetcher

page = StealthyFetcher.fetch(
    "https://example.com",
    headless=True,
    wait=8000,           # milliseconds — critical for SPAs to render
    block_webrtc=True,   # prevents WebRTC leaks that trigger bot detection
)
text = page.get_all_text()  # use this, NOT .text which may be empty in v0.4.7
html = page.html_content    # raw HTML if needed
```

## Key Parameters
- `wait`: milliseconds to wait after page load (8000-10000 for SPAs)
- `block_webrtc=True`: prevents WebRTC IP leak detection
- `solve_cloudflare=True`: for Cloudflare-protected sites (adds 5-15s)
- `headless=True`: always use headless mode

## Response Object (v0.4.7)
- `.status` — HTTP status code
- `.get_all_text()` — all visible text (USE THIS)
- `.html_content` — full raw HTML
- `.text` — may be empty, do not use
- `.url`, `.headers`, `.cookies`

## Element Selection
```python
page.css('h1::text').get()
page.css('a::attr(href)').getall()
page.find_by_text('Keyword', tag='input')
page.xpath('//div[@class="content"]/text()')
```

## CLI Alternative
```bash
scrapling extract stealthy-fetch 'https://example.com' output.html \
  --solve-cloudflare --block-webrtc
```

## Confirmed Working Sites (2026-05-18)
| Site | URL | Jobs Found |
|------|-----|------------|
| World Bank CSOD | worldbankgroup.csod.com/ux/ats/careersite/1/home?c=worldbankgroup | 24+ |
| IMO | recruit.imo.org | 10 |
| WFP Workday | wd3.myworkdaysite.com/recruiting/wfp/job_openings | 124 |

## Pitfalls
- Use `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` — system python3 doesn't have scrapling
- `wait` is in milliseconds (not seconds) — 30000 default, use 8000-10000 for SPAs
- `solve_cloudflare=True` goes inside `fetch()`, NOT the constructor
- `.get_all_text()` is the reliable text extraction method, not `.text`
