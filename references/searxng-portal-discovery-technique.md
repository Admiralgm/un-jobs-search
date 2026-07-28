# SearXNG as Portal Discovery Tool — Technique 2026-05-23

## Pattern
When a known portal careers page returns 404 or the URL is unknown, use SearXNG to discover the correct careers URL:

```
curl -s "http://localhost:8888/search?q=<ORG>+careers+vacancies+jobs+2026+site%3A<domain>&format=json&language=en" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for r in d.get('results',[])[:10]:
    print(r.get('url','')[:100], '|', r.get('title','')[:60])
"
```

## Successful Applications

### UNESCWA
- **Searched**: `UNESCWA careers vacancies jobs 2026 site:unescwa.org`
- **Found**: `unescwa.org/about/jobs` (not the 404-ing `unescwa.org/careers`)
- **Also found**: `josour.unescwa.org` (job-matching platform, requires login)

### UNESCAP
- **Searched**: `UNESCAP careers vacancies jobs site:unescap.org 2026`
- **Found**: `unescap.org/jobs` (careers home page, previously unknown)
- **Result**: All professional jobs redirect to INSPIRA anyway

### WTO
- **Searched**: `WTO vacancies careers 2026`
- **Found**: `wto.wd103.myworkdayjobs.com/External` (Workday portal)
- **Confirmed**: Full Camoufox rendering, JR-format IDs

## When to Use
1. First attempt at `domain.org/careers` or `domain.org/jobs` returns 404
2. Skill reference has outdated URL or says "no standalone portal"
3. Batch scanning reveals a portal is inaccessible — run SearXNG before skipping

## Query Templates
- Generic: `<ORG_NAME> careers vacancies jobs 2026 site:<domain>`
- For INSPIRA-redirected orgs: `<ORG_NAME> jobs site:un.org`
- For Workday portals: `<ORG_NAME> jobs workday site:myworkdayjobs.com`
- For SmartRecruiters: `<ORG_NAME> jobs site:smartrecruiters.com`
