# Batch 13 Scan Results — Impactpool & UNJobNet (2026-05-23)

## New Entries Found (7)

| ID | Org | Role | Deadline | Score | Source |
|----|-----|------|----------|-------|--------|
| IP-1210959 | WIPO | Senior Business & Project Analyst P-4 | 2026-05-28 | 🟠74 | Impactpool |
| UJN-1779298377841 | WHO | AI Software Engineer Lead P-4 | 2026-06-16 | 🟡78 | UNJobNet |
| IP-1213923 | UNFCCC | Info Systems Officer Cybersecurity P-4 | 2026-06-14 | 🟡73 | Impactpool |
| IP-1212571 | UNJSPF | Info Systems Officer P-3 | 2026-06-20 | 🟡65 | Impactpool |
| IP-1212854 | Interpol | Security Architect | 2026-06-06 | 🟢64 | Impactpool |
| UJN-1779332112240 | OSCE | Cyber Security Officer | 2026-06-17 | 🟢62 | UNJobNet |
| UJN-1779482332410 | ITU | Roster Consultants Telecom/ICT | 2026-09-09 | 🟢61 | UNJobNet |

## Already in Tracker
- ILO Director/CITO D-2 (IP-1213333, Jun 15, 🟡72)

## Excluded
- IFRC Telecom Budapest (local), UNOPS Valencia (EU-only), Interpol SOC (local), NATO YPP (junior), UNDP NO-A (junior)

## Scraping Patterns

### Impactpool.org
- `https://www.impactpool.org/search/<keyword>` — broad category
- `https://www.impactpool.org/search?keyword=<term>` — keyword search
- Detail: `/jobs/<numeric-id>` → prefix `IP-` for vacancy IDs
- JS extraction: `document.querySelectorAll('a[href*="/jobs/"]')`
- Filter OUT: Internship, GS-grade, NPSA, Entry Level

### UNJobNet.org
- `/jobs` page broken (IndexError) — use `/skills/ict`, `/themes/artificial-intelligence`, `/skills/telecommunication`, `/skills/digital-connectivity`
- Detail: `/vacancies/<long-numeric-id>` → prefix `UJN-` for vacancy IDs
- JS: `document.querySelectorAll('a[href*="/vacancies/"]')`

## ⚠️ Critical Dedup Pitfall
Impactpool IDs use `IP-` prefix, UNJobNet use `UJN-`. Raw numeric IDs won't match prefixed IDs in dedup checks. Always use the prefixed form when checking against tracker files.

## Standard Keywords (mandatory)
ICT, IT, Digital, AI, ISP, Telecom, Connectivity, Information Technology, Artificial Intelligence, Information Systems, Data

## File State
- IMPACTPOOL: 40 entries (was 33, +7)
- Main tracker: 75 entries (unchanged)
- Archive: 43 entries (unchanged)
