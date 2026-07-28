# JS-Rendered SPA Extraction Pattern

## Problem
Many UN career portals (Workday, Taleo, SuccessFactors) render content via JavaScript.
Standard DOM selectors return empty results because content is injected after page load.

## Solution: document.body.innerText Fallback

When browser_navigate loads a page but browser_console DOM queries return empty:

1. Try: document.body.innerText
2. If empty: document.documentElement.innerText
3. For Workday: try [data-automation-id="jobTitle"] or [class*="jobTitle"]

## Known JS-Rendered Portals

| Portal | URL Pattern | Extraction Method |
|--------|-------------|-------------------|
| UNHCR Workday | unhcr.wd3.myworkdayjobs.com | document.body.innerText |
| WHO Taleo | careers.who.int/careersection | document.body.innerText + link filter |
| IAEA Taleo | iaea.taleo.net | Under maintenance |
| FAO Taleo | fao.taleo.net | Under maintenance |
| Workday (generic) | *.myworkdayjobs.com | document.body.innerText |
| SuccessFactors | *.successfactors.com | document.body.innerText |

## Workday Job Detail URL Pattern
https://<org>.wd<number>.myworkdayjobs.com/en-GB/External/job/<JobID>

## Taleo Job Detail URL Pattern
https://<org>.taleo.net/careersection/<section>/jobdetail.ftl?job=<JobID>

## innerText Parsing Tips
- Job titles appear as capitalized lines
- Locations follow "locations" keyword
- Dates follow "posted on" keyword
- Job IDs appear as "JR#######"
- Filter out navigation text ("Sign In", "Search", "Filters")
- Each job entry is typically separated by blank lines
