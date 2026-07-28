# FAO Taleo — Correct Portal URL (2026-05-25)

## Dead path (removed by FAO)

```
https://jobs.fao.org/careersection/ex/jobsearch.ftl
Returns: "Career Section Unavailable — system may be under maintenance"
Status: PERMANENTLY RETIRED as of May 2026
```

## Live path (discovered via SearXNG)

```
https://jobs.fao.org/careersection/fao_external/jobsearch.ftl
Returns: 101 vacancies (2026-05-25)
```

## Keyword search

Works via `?keyword=` query param. Results by keyword:

| Keyword | Results | Notes |
|---------|---------|-------|
| digital | 17 | Most productive |
| software | 14 | |
| information%20technology | 7 | |
| AI | 3 | |
| ICT | 0 | FAO uses "information technology" not "ICT" |

## Detail pages

```
https://jobs.fao.org/careersection/fao_external/jobdetail.ftl?job={ID}&tz=GMT
```

Job IDs: 7-digit (e.g., 2601132).

## Extraction method

JS-rendered Taleo — use `camofox open` + `sleep 8` + `camofox get-text`.
Python Camoufox context manager also works. Regex fields:
- Title: `[A-Z].*(ID)` pattern
- Location: `Location:\s*([^\n]+)`
- Deadline: `Closure Date:\s*(\d{1,2}/\w+/\d{4})`
- Grade: `Grade\s*(?:Level)?:\s*([^\n]+)`

## ICS roles hidden in non-ICT divisions

As noted in the main skill: OIG (Office of Inspector-General) holds
technology/audit roles using Python/RAG/LLMs. CSI (Digital FAO) holds
Salesforce/Marketing Automation roles. Search keywords, not category filters.
