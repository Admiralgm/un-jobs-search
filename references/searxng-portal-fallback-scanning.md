# SearXNG Portal Fallback Scanning

> **Purpose:** When Camoufox is down (stale tab, server crash, profile corruption),
> use SearXNG as a lightweight fallback to probe UN career portals and discover
> job IDs. Works for any site indexed by SearXNG.
>
> **Limitation:** Only returns what SearXNG has cached — may miss newest jobs.
> Always verify with browser once Camoufox is restored.

## When to Use

- Camoufox tabs are stale and `browser_navigate` returns 404
- Server crash recovery would waste too many turns (restart + /reset cycle)
- Quick probe before committing to a full browser-based scan
- Need to check if a specific portal has *anything* relevant before spending browser turns

## Technique

### Step 1: Site-Restricted Query

```bash
curl -s "http://localhost:8888/search?q=site:careers.un.org+%22information+systems+officer%22+P4&format=json" | \
python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('results',[]):
    title = r['title']
    url = r['url']
    if 'jobSearchDescription' in url:
        print(f'{title[:100]} | {url}')
"
```

This returns cached INSPIRA job listings even when Cloudflare blocks direct web-preclean.py access.

### Step 2: Filter by Job ID Pattern

INSPIRA job IDs are 6-digit numbers in `/jobSearchDescription/{ID}` paths. Extract them:

```bash
curl -s "http://localhost:8888/search?q=site:careers.un.org+%22ITECNET%22+%22P-4%22&format=json" | \
python3 -c "
import json,sys,re
d=json.load(sys.stdin)
for r in d.get('results',[]):
    ids = re.findall(r'jobSearchDescription/(\d+)', r['url'])
    if ids:
        print(f'{ids[0]:>8} | {r[\"title\"][:100]}')
"
```

### Supported Portal Patterns

| Portal | SearXNG Query Pattern | Returns |
|--------|----------------------|---------|
| INSPIRA (careers.un.org) | `site:careers.un.org + "information systems officer" + P4` | Job IDs, titles, some metadata |
| ICRC (careers.icrc.org) | `site:careers.icrc.org + ICT + job` | Direct job detail page URLs |
| IAEA (iaea.taleo.net) | `site:iaea.taleo.net + ICT + OR + Digital` | Job detail URLs with proper `lang=en` |
| UNOPS (careers.unops.org) | `site:careers.unops.org + ICT + OR + Digital` | Job detail URLs with IDs |
| UNFPA / UNDP (estm.fa.em2.oraclecloud.com) | `site:estm.fa.em2.oraclecloud.com + ICT` | Partial job titles |
| IOM (fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com) | `site:fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com + IOM` | Job titles |
| ICAO (icaocareers.icao.int) | `site:icaocareers.icao.int + ICT + OR + Digital` | Page-level results only (low yield) |
| IFAD (job.ifad.org) | `site:ifad.org + OR + site:job.ifad.org + ICT` | Publication links (low yield) |
| WIPO (wipo.int) | `site:wipo.int + OR + site:wipo.taleo.net + ICT` | Page-level results only (low yield) |
| World Bank | `site:worldbankgroup.csod.com + OR + site:worldbank.org` | Publication links (low yield) |
| UNIDO (careers.unido.org) | `site:unido.org + Digital + AI` | Publication links (low yield) |
| WFP (wd3.myworkdaysite.com) | `site:wfp.org + OR + site:wd3.myworkdaysite.com + ICT` | Publication links (low yield) |

### Proven Yields (June 2026 scan)

| Portal | Jobs Found via SearXNG | Quality |
|--------|----------------------|---------|
| INSPIRA (careers.un.org) | 5+ P3-P5 IS/IT jobs | HIGH — multiple P4/P5 |
| IAEA (iaea.taleo.net) | 3-4 P2-P3 jobs (Data Engineer, SW Engineer) | MODERATE |
| ICRC (careers.icrc.org) | 2-3 ICT roles (Engineer, Info Mgmt) | MODERATE |
| UNOPS (careers.unops.org) | 5 ICT roles (Sr Officer, Specialist, Analyst) | HIGH |
| IOM | 1-2 ICT-adjacent roles | LOW |
| UNDP | Mostly internships | LOW |
| UNFPA / WFP / WIPO / IFAD / ICAO / World Bank | No job listings returned | VERY LOW |

## Limitations

- **SearXNG cache lag:** May miss jobs posted in the last 24-48 hours
- **No detail pages:** SearXNG typically caches only the listing page snippet, not the full JD
- **No deadlines:** Deadline extraction rarely works from cached snippets
- **No grades:** Grade info may be missing from cached content
- **Always verify:** Job IDs found via SearXNG should be verified with browser_navigate once Camoufox is restored

## When NOT to Use

- Camoufox is running and healthy — use direct browser scanning (more complete)
- Need full JD text for scoring — browser + preclean.py required
- Portal is too new/niche to be indexed by SearXNG