# Portal Extraction Feasibility — May 30 2026 Update

Systematic extraction test of all UN/international career portals for ICT/AI/Telecom/ISP/connectivity vacancies.
Date: 2026-05-30. Browser: Camoufox v2.4.5 (default).

## ✅ CONFIRMED WORKING (12 portals)

| # | Portal | URL | Platform | Extraction Method | Total Jobs | ICT-Relevant Found |
|---|--------|-----|----------|-------------------|------------|---------------------|
| 1 | UNICEF | jobs.unicef.org | PageUp | browser_type keyword + Enter → DOM extract a[href*="/en-us/job/"] | 200+ | AI strategy consultant, ICT Policy consultant, T4D P3, DPGs Digital |
| 2 | WHO | careers.who.int | Taleo | browser_type keyword + Search button → li a[href*="jobdetail"] | 46 | AI Software Eng Lead P4, DataEng Dev, GIS Spec |
| 3 | ITU | jobs.itu.int | SuccessFactors | Click "View all job openings" → table render | 33 | Green Digital Consultant, Digital Ecosystem, SW Dev, Cyber, Telecom Stats |
| 4 | IAEA | iaea.taleo.net | Taleo | Keyword search + multi-line table | 24 | Data Engineer P3, SW QA P2 |
| 5 | FAO | jobs.fao.org | Taleo | Keyword search + list render | 83 | Salesforce Mktg Automation Tech Specialist, Food Standards Data Mgmt |
| 6 | UNESCO | careers.unesco.org | SuccessFactors | Direct search URL: search/?q=keyword | ~24/search | Front-end Dev (Diya.Engine), DevOps (ePamiatka), IT Assistant |
| 7 | UNOPS | careers.unops.org | Custom ICS | Keyword search → article cards | 21 | AI Geospatial Data Science Advisor, App Mgmt Lead |
| 8 | IMF | imf.wd5.myworkdayjobs.com/IMF | Workday | Keyword search | 13 | IT Strategist, Data Engineer |
| 9 | WFP | wd3.myworkdaysite.com/recruiting/wfp/job_openings | Workday | Accept cookies → keyword → paginate (5 pages) | 100 | Full-stack developer Rome |
| 10 | OECD | careers.smartrecruiters.com/OECD | SmartRecruiters | Keyword search on careers page | ~80 | Deputy Head Digital Workplace Services |
| 11 | INSPIRA | careers.un.org | UN Custom | Pre-filtered ITECNET URL | 10+/page | UNCTAD, OICT, UNJSPF, OCHA ICT roles |
| 12 | ILO | jobs.ilo.org | Custom SPA | Click "View all jobs" → category browse | 12+ | Director IT Management/CIO D2 |

## ⚠️ PARTIALLY WORKING (3 portals)

| Portal | Issue |
|--------|-------|
| WTO | Same SmartRecruiters as OECD, tiny ICT count |
| UNHCR | 0 ICT professional roles consistently |
| ICAO | Small set, Camoufox crash risk on click |

## ❌ CONFIRMED FAILURES (2 portals)

| Portal | Issue | Alternative |
|--------|-------|-------------|
| World Bank CSOD | JS SPA renders empty in browser | Scrapling StealthyFetcher |
| IMO | Camoufox crashes, 8 non-IT jobs | Skip |

## 🔍 NOT TESTED (carry forward)

UNDP (few P-level), WIPO (HIGH priority, ICT-heavy), UNIDO, IFAD, UNFPA, ICMPD, UNITAR, GICHD, UNDRR (via INSPIRA), WMO, UNESCAP/UNECE/UNECA/UNESCWA (via INSPIRA), UNWTO/UPU/UNOV/UNON/UNSSC (via INSPIRA), UNEP/UNODC/OHCHR (via INSPIRA add org filter)

## Key Corrections vs Prior Docs

### OECD URL Changed
- OLD: jobs.smartrecruiters.com/OECD → 404 "gone too far"
- NEW: careers.smartrecruiters.com/OECD ✓
- WTO: careers.smartrecruiters.com/WTO

### UNICEF Search — Broad Keyword Matching
- UNICEF search matches title + description, not just title
- "AI" returns 33 results including internships in Haiti, social policy, etc.
- Must filter in Python after extraction — keyword search alone is not sufficient
- "More Jobs" button gets stuck after ~15 clicks (offsetParent becomes null) — extract what you have

### INSPIRA ITECNET Pre-Filtered URL
https://careers.un.org/jobopening?language=en&data=%7B%22jn%22:[%22ITECNET%22],%22jf%22:[],%22jc%22:[],%22jle%22:[]%7D
Job detail URLs: /jobSearchDescription/{JOB_ID}?language=en
Extract listing: document.querySelectorAll('a[href*="jobSearchDescription"]')
Detail page: click "Expand All" first, then body.innerText

## Extraction Method by Platform Type

### Taleo (WHO/IAEA/FAO)
1. browser_navigate to jobsearch.ftl URL
2. browser_type keyword → browser_click Search button
3. Switch to multi-line view for table
4. WHO: extract li a[href*="jobdetail"] elements
5. IAEA: extract table row rowheader links
6. FAO: extract listitem a[href*="jobdetail"] elements
7. Detail pages: article.innerText (WHO has article tag, IAEA/FAO use body.innerText)

### SuccessFactors (ITU/UNESCO)
1. ITU: navigate → click "View all job openings" → table renders
2. UNESCO: navigate to /search/?q=keyword → table renders
3. Extract from table rows or list items

### Workday (IMF/WFP)
1. Navigate → accept cookies if prompted
2. browser_type keyword → Search
3. Extract from rendered list items
4. WFP: 5 pages, paginate with browser_click on page numbers

### SmartRecruiters (OECD)
1. Navigate to careers.smartrecruiters.com/OECD
2. browser_type keyword → results update
3. Extract from updated job cards

### UNICEF PageUp
1. browser_navigate to jobs.unicef.org/en-us/listing/
2. browser_type keyword in search textbox → Enter
3. Wait for render → extract a[href*="/en-us/job/"] with h4 children
4. Filter results in Python (search is broad)

### INSPIRA
1. Navigate to ITECNET pre-filtered URL
2. Scroll past filter checkboxes to job results
3. Extract a[href*="jobSearchDescription"] links
4. Detail pages: click "Expand All" → body.innerText

### UNOPS Custom ICS
1. Navigate to careers.unops.org
2. Click "Open Positions" / SearchJobs link
3. Accept cookies
4. browser_type keyword → Search
5. Extract from article cards