# SearXNG for UN Job Portal Discovery

Verified working 2026-05-28. SearXNG instance at http://localhost:8888.

## When to Use

Before investing token budget on browser_navigate or web-preclean.py for an unknown portal, hit SearXNG first to:
1. Find the actual career portal URL (many orgs have moved domains — UNWTO → untourism.int)
2. Check if ICT-relevant roles exist before committing to a full scan
3. Verify whether a role is still open or expired (deadline in search snippet)
4. Find alternate aggregator listings (Impactpool, UNJobNet, UN Talent, UNjobs)

## Quick Check Pattern

```bash
curl -s --max-time 10 "http://localhost:8888/search?q=ORG+ICT+digital+job+vacancy+2026&format=json&limit=5" \
  | python3 -c "import sys,json; d=json.load(sys.stdin)
for r in d.get('results',[]):
    t=r.get('title','')[:100]; u=r.get('url','')[:100]
    c=r.get('content','')[:150]
    print(t); print(u); print(c[:100]); print()"
```

## Site-Specific Discovery

Use `site:` operator to target specific portals:
```bash
# Find ICT jobs on a specific portal
site:erecruit.wmo.int ICT
site:careers.unu.edu digital
site:unitar.org vacancy ICT
```

## Common UN Portal Searches

| Query Pattern | Use Case |
|--------------|----------|
| `ORG careers jobs 2026` | Find the career portal URL |
| `site:careers.un.org ORG` | Check if org uses Inspira |
| `site:impactpool.org ORG` | Lead generation for blocked sites |
| `ORG ICT digital AI job vacancy 2026` | Direct ICT job search |
| `"ORG" "P-4" OR "P-5" ICT 2026` | Senior-grade roles |

## Verification Pattern

After finding a promising lead from SearXNG:
1. Extract the direct URL from search results
2. Check HTTP status: `curl -s -o /dev/null -w "%{http_code}" URL`
3. If 200, try web-preclean.py on the direct URL
4. If empty/403, use Camoufox browser

## Deadlines in Snippets

SearXNG often includes deadline text in the `content` field. Scan for:
- "Deadline: YYYY-MM-DD"
- "Date of issue: ..."
- "Closes in N days"
- "Deadline extended"

## Limitations

- SearXNG only returns snippets, not full page content
- Some public SearXNG instances block JSON API — this instance (localhost:8888) is self-hosted
- Results may include expired jobs from aggregators — always verify on official portal
