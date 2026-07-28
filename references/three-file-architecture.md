# Three-File Architecture — UN Job Vacancy Tracking

## Overview

The UN job vacancy scanning system maintains three files. All three must be loaded and checked during every scan session.

| File | Path | Purpose |
|------|------|---------|
| `UN_SECTOR_VACCANCIES.txt` | `~/Downloads/` | Active vacancies from reliable sources (direct career portals) |
| `UN_SECTOR_VACCANCIES_IMPACTPOOL.txt` | `~/Downloads/` | Active vacancies from unreliable sources (Impactpool, UNJobNet) |
| `UN_SECTOR_VACCANCIES_ARCHIVE.txt` | `~/Downloads/` | Vacancies marked APPLIED: YES or EXPIRED (moved from active files) |

## Archive File Purpose

`UN_SECTOR_VACCANCIES_ARCHIVE.txt` is **NOT** a consolidated merge. It is a **destination for applied/expired entries**:
- When a vacancy is marked `APPLIED: YES`, it is **moved** from the active file to the archive
- When a vacancy passes its deadline (`EXPIRED`), it is **moved** to the archive
- The archive is **loaded during every scan** to prevent re-adding already-applied vacancies
- Entries in the archive are kept for reference and deduplication only

## Deduplication Rule (MANDATORY)

Before adding any new entry, check the Vacancy ID against **ALL three files**:
1. `UN_SECTOR_VACCANCIES.txt` (active reliable)
2. `UN_SECTOR_VACCANCIES_IMPACTPOOL.txt` (active unreliable)
3. `UN_SECTOR_VACCANCIES_ARCHIVE.txt` (applied/expired)

**If a Vacancy ID exists in ANY of the three files, do NOT add it again.**

This prevents:
- Duplication between reliable and unreliable source files
- Re-adding vacancies that have already been applied to
- Confusion with previously tracked vacancies

## Summary Table (Top of Each Active File)

Each active tracker file has a **Vacancy Summary Table** at the top (after the header block).

**Columns:** `# | Organization | Position Title | Deadline | Score (color-coded) | Vacancy ID`

**Sorting:** By deadline (nearest first). TBD deadlines at end.

**Score colors:** 🔴 90+ | 🟠 80-89 | 🟡 70-79 | 🟢 <70

**Regeneration:** Must be rebuilt after every file write (add/remove/modify entries).

## Scoring Model

TOTAL MATCH (%) = (Technical Relevance × 0.60) + (Seniority Alignment × 0.20) + (Strategic Alignment × 0.20)

| Score | Verdict | Color |
|-------|---------|-------|
| 85-100 | STRONG FIT | 🔴 RED |
| 70-84 | COMPETITIVE | 🟠 ORANGE |
| 55-69 | STRETCH | 🟡 YELLOW |
| <55 | LOW FIT | 🟢 GREEN |

## Entry Format

Every entry MUST include:
- MATCH ANALYSIS with all three scoring dimensions (weighted scores shown)
- 🚀 Positioning Advice (bullet points)
- 📊 Verdict with percentage and Confidence Level
