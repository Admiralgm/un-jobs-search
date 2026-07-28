# Vacancy Verification Protocol

After scanning new vacancies into tracker files, verify their existence on the hiring org's live career portal. This catches phantom/draft/expired entries before they become stale data.

## When to Verify

- **On-demand** — user says "verify these vacancies"
- **After any scan batch** — spot-check top-scoring entries
- **Before any application action** — never apply to an unverified vacancy

## Generic Verification Method

1. Find the org's direct job URL pattern from the entry's `HYPERLINK` field
2. Navigate to `https://<org-portal>/en-us/job/<VACANCY_ID>/`
3. Check for title match in the `<h2>` element
4. Check for "Job no:" field matching the expected ID

## Portal URL Patterns (Verified)

| Organization | Pattern | Notes |
|-------------|---------|-------|
| **UNICEF** | `https://jobs.unicef.org/en-us/job/{ID}/` | PageUp SPA. 593xxx IDs = active. 592xxx IDs often "not found" (drafts/expired). |

## UNICEF-Specific Findings (29 May 2026)

**12/22 (55%) confirmed active** — all 593xxx IDs:
`593133`, `593254`, `593241`, `590688`, `584099`, `593259`, `593311`, `593247`, `593264`, `593297`, `593159`, `593075`

**10/22 (45%) returned "not found"** — mostly 592xxx + 593155:
`592902`, `592948`, `593037`, `593033`, `593140`, `593154`, `593155`, `592874`, `592891`, `592958`

**Signals:**
- All confirmed vacancies had **exact title matches** — zero discrepancies
- "Not found" vacancies consistently have "Deadline: TBD" in the tracker — likely pre-publication drafts
- **Exception:** 593075 (Digital Impact Officer AI Applications) has "Deadline: TBD" but IS live on the portal. Some legitimate UNICEF vacancies remain at TBD deadline.
- Key indicator: check the direct job URL `/en-us/job/{ID}/`. If it resolves with "Job no:" matching the ID, it's live regardless of deadline text.
- The UNICEF portal redirects missing IDs to `/en-us/listing/?jobnotfound=true` with "Sorry, we can't provide additional information about this job right now."
- **ID range pattern:** 593xxx IDs = mostly live. 592xxx IDs = mostly drafts/not found.

## Reporting Format

```
🟢 CONFIRMED — ACTIVE ON PORTAL
  | ID: 593133 | Tracker: Programme Manager (Infrastructure Finance), P-4
  | Portal: Programme Manager (Infrastructure Finance), P-4, Geneva
  | Status: ✅ Match

🔴 NOT FOUND
  | ID: 592902 | Tracker: Data Protection and Privacy Manager, P-4, Florence
  | Status: ❌ "jobnotfound" — likely not yet published
```

## Key Rules

1. **Always check title match** — not just HTTP 200. A 200 with the wrong title means URL pattern changed.
2. **User-directed removal** — if entries verified as "not found" on the live portal, the user expects them removed from the tracker file. Do not keep them in the file. Remove the entry blocks and renumber the summary table.
3. **Report the ratio** — e.g., "12/22 confirmed (55%)" — so the user knows the reliability of their tracker data.
