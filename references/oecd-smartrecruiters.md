# OECD SmartRecruiters Portal

**URL:** `careers.smartrecruiters.com/OECD` ✓ (updated 2026-05-30)

**OLD URL (BROKEN):** `jobs.smartrecruiters.com/OECD` — returns 404 "gone too far"
**WTO URL:** `careers.smartrecruiters.com/WTO`

**Platform:** SmartRecruiters
**~80 jobs total**
**Notable ICT role:** Deputy Head of Digital Workplace Services (Paris, REF3052Q)

## Extraction Method
1. `browser_navigate` to `https://careers.smartrecruiters.com/OECD`
2. `browser_type` keyword in search textbox (ref with placeholder "Search job openings, e.g. manager")
3. Results update in the job list below
4. Extract from rendered job cards: heading (title), paragraph (location), link (URL)
5. Job detail URLs: `https://jobs.smartrecruiters.com/OCD/{job-id}-{slug}`
