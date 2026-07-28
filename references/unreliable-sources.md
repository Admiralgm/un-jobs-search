# Unreliability Notice — Impactpool.org and UNJobNet.org

**Last updated:** 2026-05-13

## Classification: UNRELIABLE

Both Impactpool.org and UNJobNet.org (unjobs.org) are **aggregator sites**, not primary
sources. They scrape or accept submissions from UN career portals but do not verify accuracy.

## Known Issues

1. **Expired listings persist** — Jobs long closed on the official portal remain listed
2. **Duplicate entries** — Same job appears multiple times under slightly different titles
3. **Phantom vacancies** — Jobs listed that never existed on the official portal
4. **Deadline drift** — Deadlines shown on aggregator differ from official portal by days/weeks
5. **Title paraphrasing** — Job titles are rewritten, not exact matches
6. **Grade/level errors** — Seniority information may be wrong or missing
7. **Broken links** — HYPERLINK points to old URLs that now 404

## Rules

- These sources are **lead generators ONLY**
- Every entry MUST be verified on the hiring org's official career portal
- If the job cannot be found on the official portal, it MUST NOT be recorded
- NEVER use Impactpool's numeric ID as the Vacancy ID — always use the official org ID
- Batch 12 (Impactpool/UNJobNet) is a separate run with results in a separate file

## Output File

Results from Impactpool/UNJobNet scanning go to:
`~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_IMPACTPOOL.txt`

This file has the same structure as UN_SECTOR_VACCANCIES.txt but with a WARNING header
marking all contents as unreliable until verified.
