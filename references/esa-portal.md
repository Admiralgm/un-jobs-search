# ESA Jobs Portal — Access & Extraction Guide

**Portal:** jobs.esa.int
**Status:** CONFIRMED WORKING (2026-05-23)
**Method:** Camoufox with direct keyword URL
**Previous classification:** BLOCKED — JS SPA doesn't render (May 2026) — **OVERTURNED**

## Discovery

Previously classified as inaccessible — browser_navigate to `jobs.esa.int` returned empty JS SPA.
The breakthrough was using a direct keyword search URL:
```
https://jobs.esa.int/search/?createNewAlert=false&q=ICT&locationsearch=
```

This URL bypasses the empty listing page and renders search results directly in Camoufox.

## Search URLs

Use these patterns for targeted searches:
- `jobs.esa.int/search/?q=ICT` — ICT roles (4 results as of 2026-05-23)
- `jobs.esa.int/search/?q=digital` — Digital transformation roles
- `jobs.esa.int/search/?q=AI` — AI/ML roles
- `jobs.esa.int/search/?q=technology` — Broader technology roles

## Results (2026-05-23 scan)

4 results with `?q=ICT`:

| # | Title | Type | Location | Deadline | Grade |
|---|-------|------|----------|----------|-------|
| 1 | Earth Observation Service Manager | 4 years, extendable | Frascati, IT | Jun 12, 2026 | A2-A4 |
| 2 | Ground Operations Cybersecurity and ESTRACK Coordinator | Fixed-Term | Darmstadt, DE | May 28, 2026 | — |
| 3 | IRF PostDoc in AI for Autonomous Cognitive Cloud Computing | Internal Research Fellow | Frascati, IT | Jun 3, 2026 | — |
| 4 | IRF PostDoc in xAI and Decision Intelligence for EO Resilience | Internal Research Fellow | Frascati, IT | Jun 17, 2026 | — |

## Detail Page Extraction

Each job detail page renders fully in Camoufox. Use `browser_snapshot(full=true)` or `browser_console` to extract:
- Title, Requisition ID, Date Posted, Closing Date
- Type of Appointment, Directorate, Workplace
- Grade Band (A2-A6, with link to salary table PDF)
- Full Description, Duties, Technical competencies, Behavioural competencies
- Education requirements

Detail URL pattern: `jobs.esa.int/job/{Location}-{Title-Slug}/{numeric-ID}/`

## Grade System

A2-A6 grades, approximately:
- A2 ≈ P-2
- A3 ≈ P-3
- A4 ≈ P-4
- A5 ≈ P-5
- A6 ≈ D-1

Salary table: `esamultimedia.esa.int/docs/careers/Table_Staff_Salaries.pdf`

## Nationality

ESA is an intergovernmental organization with 22 member states. Candidate eligibility via Czech citizenship (Czech Republic is an ESA member state since 2008). ESA positions are open to nationals of member states — included with nationality eligibility note.

## Filtering Rules

- **PostDocs (Internal Research Fellow):** Exclude unless exceptional AI match directly relevant to candidate's AI/LLM expertise
- **Traineeships:** Exclude
- **Fixed-Term / 4-year extendable:** Include if ICT/AI-relevant and grade A3+

## Pitfalls

- Main listing page (without keyword) renders empty in Camoufox — always use direct keyword URL
- Job titles are space/tech domain specific (Earth Observation, Ground Operations) — may not use "ICT" in title despite being ICT roles
- Search with broader keywords (digital, technology, AI) to catch roles titled differently