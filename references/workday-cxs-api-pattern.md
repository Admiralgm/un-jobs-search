# Workday cxs JSON API Pattern (wd1.myworkdayjobs.com)

Verified 2026-09-08 on worldvision.wd1.myworkdayjobs.com (WVI, 304 jobs). Applies to any Workday tenant.

## Endpoints (no browser needed — plain curl)
- Listings: `POST https://{tenant}.wd1.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs` body `{"appliedFacets":{},"limit":20,"offset":0}`
- JD: `GET https://{tenant}.wd1.myworkdayjobs.com/wday/cxs/{tenant}/{site}{externalPath}` (externalPath from listing)
- Headers: `Content-Type: application/json`, `Accept: application/json`, browser User-Agent.

## Pagination trap
Offset 0 returns `total: N`; every subsequent page returns `total: 0` but still returns 20 jobPostings. NEVER break pagination on `total` — paginate until two consecutive empty batches (hard cap ~600). Facet queries (appliedFacets with facet value IDs) DO return real totals.

## JD JSON shape
- Body HTML: `jobPostingInfo.jobDescription` → convert with li/br/p strip + html.unescape.
- Metadata: `jobPostingInfo.{title,jobReqId,location,additionalLocations,timeType,postedOn,startDate,externalUrl}`; org: `hiringOrganization.name`.
- **No closing date** in Workday cxs — deadline comes only from inline JD text (search body for "deadline").

## Eligibility extraction (WVI-specific, generalize with care)
- `Applicant Types Accepted:` tail = `Local Applicants Only` vs `Local and International Applicants (IA's) Accepted`.
- `IMPORTANT INFORMATION` block in global roles: "open to candidates based in countries where WVI is legally registered" — cross-check against the listing's hiring countries; Serbia is not a WVI registration country.
- `workerSubType` facet IDs unreliable (office jobs tagged International) — never gate on facet alone.
- Christian-identity clause (devotions/chapel) is standard on WV JDs — flag as personal-preference signal.

## Fetch hygiene
- ThreadPoolExecutor ×5, retry ×5 with 1.5s×(n+1) backoff; transient 502s occur.
- ~304 JDs in <60s at 5 workers.
