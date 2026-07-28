# SearXNG Portal Discovery Reference

## Standard Query Template
```bash
curl -s "http://localhost:8888/search?q=<ORG>+vacancies+careers+jobs+2026+site%3A<domain>&format=json&language=en" | python3 -c "import sys,json; [print(r.get('url','')[:100],'|',r.get('title','')[:60]) for r in json.load(sys.stdin).get('results',[])[:10]]"
```

## Priority Rule
**SearXNG result URL > skill hardcoded URL > guessed URL**

## Discovered URLs (2026-05-23)

| Organization | Broken/Old URL | Correct URL |
|---|---|---|
| WTO | wto.org/careers (404) | wto.wd103.myworkdayjobs.com/External |
| UNESCWA | unescwa.org/careers (404) | unescwa.org/about/jobs |
| UNESCAP | unescap.org/vacancies (404) | unescap.org/jobs |
| UNOV | unov.org/vacancies (404) | careers.un.org (INSPIRA) |
| UNON | unon.org/vacancies (404) | careers.un.org (INSPIRA) |
| OECD | oecd.org/careers (info only) | careers.smartrecruiters.com/OECD/ |
| UNICRI | unicri.org/jobs (404) | unicri.org/institute/join_us/jobs/vacancies |
| UNDRR | undrr.org/jobs (PreventionWeb) | undrr.org/about-undrr/work-us |
| GICHD | gichd.org/jobs (login) | gichd.org/the-gichd/job-opportunities/ |

## INSPIRA Keyword Searches (2026-05-23)

| Keyword | Results | New P-grade ICT |
|---|---|---|
| Information Technology | 22 | 1 (OICT P5) |
| Artificial Intelligence | 11 | 0 |
| Information Systems | 9 | 0 |
| Telecom | 3 | 0 |
