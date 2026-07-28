# ECB Career Portal Scan (2026-06-01)

## Portal URLs

| Use | URL |
|-----|-----|
| **Live job listing** | https://talent.ecb.europa.eu/careers |
| Dead (404) | https://www.ecb.europa.eu/careers/what-we-offer/current-vacancies/html/index.en.html |
| Dead (404) | https://www.ecb.europa.eu/careers/jobs/html/index.en.html |
| Info page (no jobs) | https://www.ecb.europa.eu/careers/html/index.en.html |

## Platform

SkillBound (not SuccessFactors, Workday, or Taleo). Cookie acceptance required before search/filters work.

## Access Pattern

- Use Camoufox Python serverless (or Camoufox HTTP server) — the `talent.ecb.europa.eu` domain has no Cloudflare
- Navigate to `https://talent.ecb.europa.eu/careers`
- Cookie consent banner appears — click "I understand and I accept the use of all cookies"
- Wait ~5s for job list to render
- Extract with `page.inner_text("body")`
- 10 jobs per page, simple pagination (`?jobOffset=10`)
- Detail pages at `/careers/JobDetail/<slug>` return 404 when accessed directly (JS-rendered); the listing page has enough metadata

## ICT Yield Assessment (June 2026)

**Total jobs: 11.** Zero P-3+ ICT/AI roles.

| Title | Verdict |
|-------|---------|
| Market Infrastructure Experts (offline tech) - Digital Euro | Financial/payments infra, not ICT |
| Market Infrastructure Project Mgmt Specialists - Digital Euro | Project mgmt, not ICT |
| Information Management Specialist (Librarian) | Library/knowledge mgmt, not ICT |
| PhD traineeship (2x) | Traineeship — excluded |
| Research Analysts | Economics, not ICT |

## Extract Metadata Pattern

Listing shows per-job: title, department, sub-department, deadline, Share/Apply buttons.
Deadlines in DD-Mon-YYYY format (e.g., "09-Jun-2026").
No grade/level visible on listing page (ECB uses internal bands).
No Vacancy ID format visible on listing — each job has a numeric jobId in the Apply URL (e.g., `jobId=14130`).

## Pitfalls

- Detail page deep-links always return 404 (SkillBound blocks direct access without session cookie chain)
- The old `/careers/` path returned 404 in June 2026 — always use `talent.ecb.europa.eu/careers`
- ECB is an EU institution, NOT a UN org — nationality rules differ (open to EU nationals)
- ECB roles are paid in EUR, grade bands are AD (Administrator) levels