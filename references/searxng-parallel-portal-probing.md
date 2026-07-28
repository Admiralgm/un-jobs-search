# SearXNG Parallel Portal Probing — Token-Efficient Batch Scan

## Why

Browser-based portal scanning (browser_navigate → accept cookies → click search → read listings) costs 5-15 turns per portal. For 25+ portals, that's 125-375 turns just for scanning. SearXNG can probe 5-10 portals simultaneously in a single `curl` call — returning results in ~5 seconds. Use it as a **pre-filter** before deciding which portals deserve full browser attention.

## When to Use

- You need to check 5+ portals for ICT vacancies in a fresh scan cycle
- You want a quick delta check on portals already scanned recently
- You want to verify if a specific role still appears in search results
- Use as the first step in a scan cycle: probe → filter → browser for high-yield

## When NOT to Use

- You need the full job description (SearXNG returns 200-char snippets only)
- The portal requires authentication or JS rendering (SearXNG indexes public pages)
- You need accurate deadline/grade/location data (SearXNG snippets are unreliable for structured fields)
- Portal is poorly indexed (WIPO, IFAD, UNIDO) — browser_navigate is the only reliable method

## Batch Probing Pattern

```bash
# Probe 5 portals simultaneously
for portal in \
  "site:careers.un.org+ICT+OR+Digital+OR+Information+technology+P3+P4+P5" \
  "site:careers.unops.org+ICT+OR+Digital+OR+AI" \
  "site:unhcr.wd3.myworkdayjobs.com+ICT+OR+Digital" \
  "site:imf.wd5.myworkdayjobs.com+IT+OR+Digital+OR+Data" \
  "site:jobs.itu.int+Digital+OR+AI+OR+ICT"
do
  echo "=== $portal ==="
  curl -s "http://localhost:8888/search?q=$portal&format=json" | \
    python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('results',[])[:5]:
    print(f'  {r[\"title\"][:80]}')
"
done
```

## Interpreting Results

| SearXNG Signal | Meaning | Action |
|---------------|---------|--------|
| ICT/AI-relevant job titles found | Portal has live vacancies | browser_navigate for full details |
| Jobs found but all non-ICT (admin, health, etc.) | Portal active but low yield | Note and move on |
| No results / "No results found" | Portal not indexed or 0 total | Use browser_navigate to confirm |
| Results are stale (30+ days old) | Portal may have changed URL | Check portal manually |

## Portal-Specific Search Queries (validated Jun 2026)

| Portal | SearXNG Query | Expected Hits |
|--------|--------------|---------------|
| UNOPS | `site:careers.unops.org+ICT+OR+Digital+OR+AI` | 5-10 |
| INSPIRA/UN Secretariat | `site:careers.un.org+%22information+systems+officer%22+OR+%22information+management+officer%22` | 10-20 ITECNET roles |
| UNHCR Workday | `site:unhcr.wd3.myworkdayjobs.com+ICT+OR+Digital` | 0-2 (historically low yield) |
| IMF Workday | `site:imf.wd5.myworkdayjobs.com+IT+OR+Digital+OR+Data` | 0-2 ICT roles |
| ITU | `site:jobs.itu.int+Digital+OR+AI+OR+ICT` | 3-10 |
| UNICEF | `site:jobs.unicef.org+Digital+OR+ICT+OR+AI+OR+Innovation` | 5-20 matching snippets |
| WHO Taleo | `site:careers.who.int+Digital+OR+AI+OR+ICT` | 3-10 Digital-related |
| ILO | `site:jobs.ilo.org+Information+OR+Technology+OR+Digital` | 1-3 (IT roles rare) |
| WFP Workday | `site:wd3.myworkdaysite.com+Digital+OR+ICT` | 0-3 |
| OECD | `site:careers.smartrecruiters.com/OECD+Digital+OR+AI+OR+Data` | 0-2 (junior only) |

## Pitfalls

- **SearXNG results are NOT authoritative.** A job that appeared 2 weeks ago in SearXNG may now be expired. Always verify deadline on the live page.
- **Some portals are poorly indexed** by SearXNG (WIPO, IFAD, UNIDO). For these, browser_navigate is the only reliable method — SearXNG probing gives false negatives.
- **URL encoding is critical.** Spaces → `+` in query param. Pipe `|` → `%7C`. The `site:` operator is SearXNG's strongest filter.
- **format=json vs format=html:** JSON is terse for probing (titles only). Switch to `format=html` when you need surrounding context (but costs more tokens).
- **SearXNG returns paginated results.** Default is 10 per page. Use `&page=2` for more.
- **Rate limiting:** SearXNG is local — no rate limits. Fire all probes in parallel.