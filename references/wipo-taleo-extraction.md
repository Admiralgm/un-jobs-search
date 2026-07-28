# WIPO Career Portal Extraction Guide

## Date: May 2026
## Portal type: Taleo (same family as WHO, IAEA, FAO)

---

## Portal Structure

WIPO has THREE recruitment tracks:

### 1. PD Taleo — Professional & Director Categories
**URL:** https://wipo.taleo.net/careersection/wp_2_pd/jobsearch.ftl?lang=en
**Status:** ✅ Camoufox accessible (JS-rendered Taleo SPA, standard)
**Vacancies found (May 2026):** 7
**Method:** browser_navigate, view All Jobs, search by keyword
**ICT-relevant jobs:** ~1 (EPM Support Manager P-4)
**Keywords to search:** "ICT", "Digital", "AI" — each returns partial subset (Taleo AND logic)
**Typical postings:** Mostly Legal (3), HR/Admin (3), occasional IT (1)

### 2. GS Taleo — General Service
**URL:** https://wipo.taleo.net/careersection/wp_2_gs/jobsearch.ftl?lang=en
**Status:** ✅ Camoufox accessible
**Vacancies found (May 2026):** 0
**No active postings.** Skip in future scans unless specifically checking.

### 3. ICS — Individual Contractor/Consultant Service
**URL:** https://www.wipo.int/en/web/working-at-wipo/individual-contractor-service
**Active ICS vacancies (as of May 2026):** Posted on UNGM
**URL:** https://www.ungm.org/public/notice?organization=wipo&type=IndividualConsultant
**ICS profile areas:** Law, International Relations, Political Science, Economics, Statistics, **Information Technology (IT)**, Technical Cooperation, Project Management, Administration, Translation, Marketing, Communications
**Method:** browser_navigate → filter by Org=WIPO, Type=Call for individual consultants
**May 2026:** 1 active notice (Copyright Law legislative assistance — NOT IT)
**Important:** WIPO states ICS recruitment transitioned from Taleo to UNGM as of May 1, 2026. All future ICS opportunities are on UNGM only.

---

## Extraction Method

### PD Taleo (standard Taleo workflow):
```python
# 1. Navigate to listing
browser_navigate(url="https://wipo.taleo.net/careersection/wp_2_pd/jobsearch.ftl?lang=en")
# 2. Click "View All Jobs" to remove keyword filter
browser_click(ref="e8")  # "View All Jobs" link
# 3. Read all 7 jobs from the snapshot (each listed as link + text block)
# 4. For full JD: navigate to jobdetail.ftl?job=JOBCODE
browser_navigate(url="https://wipo.taleo.net/careersection/wp_2_pd/jobdetail.ftl?job=26152-FT_LT&lang=en")
# 5. Extract full body text
browser_console(expression="document.body.innerText")
```

### Job detail format:
- Title + Job Code: `EPM Support Manager - 26152-FT_LT`
- Grade: P-4 (or P-3, P-2 as posted)
- Duty Station: CH-Geneva (all PD jobs)
- Deadline: local time (applicant's timezone — important for application)
- Full structure: Organizational Context, Purpose Statement, Reporting Lines, Work Relations, Duties, Requirements (Education → Experience → Language → Competencies), Salary
- Salary is included at the bottom: annual + post adjustment in USD

### UNGM ICS extraction:
```python
browser_navigate(url="https://www.ungm.org/public/notice?organization=wipo&type=IndividualConsultant")
# Scroll down past knowledge center sidebar to see results table
browser_scroll(direction="down")
# Extract from browser_console
```

---

## Known Pitfalls

1. **Low ICT yield:** WIPO is primarily a legal/IP organisation. ICT positions are rare (typically 0-1 out of 7 PD jobs). Not worth a dedicated full-batch scan — treat as a quick check.
2. **Taleo standard behaviours apply:** Same as WHO/IAEA Taleo — web-preclean.py returns only cookie banner, requires browser_navigate. Keyword search uses AND logic (multi-word filters aggressively). Always fall back to "View All Jobs" and scan manually.
3. **Camoufox `browser_type` 500 errors** can occur when typing into the keyword search field. If this happens, use URL-param keyword search instead: `?lang=en&keyword=Digital`
4. **No ICT on UNGM currently:** "Information Technology" is listed as an ICS profile area, but as of May 2026 there were no IT consultant notices. Check periodically.
5. **Salary range for P-4:** ~$146,455 total (salary + post adjustment) — Geneva-based. This is competitive for a P-4 role.

---

## May 2026 Scan Results

7 PD vacancies found:
1. EPM Support Manager (P-4) — ICT-relevant ✅
2. Culture, Engagement & Performance Analyst (P-3)
3. Legal Officer, Patent Law (P-3)
4. Legal Officer, PCT Legal (P-3)
5. Talent Business Partner (P-3)
6. Legal Officer, Copyright (P-3)
7. Associate Program Officer (P-2)

**ICT yield: 14%** (1 of 7). WIPO should be scanned but not as a primary source. Given the low yield, a SearXNG quick-check before browser scan is recommended for future cycles.
