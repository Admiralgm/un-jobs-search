# Sources Checklist — UN Jobs Scan (All 32 Sources)

## PRIMARY SOURCES (scan every session)

### 1. Impactpool
- **URL:** https://www.impactpool.org/search
- **Access:** Works without login for search results. Cookie consent popup (Accept All via ref=e5).
- **Method:** Browser navigate directly to search URLs. Use `browser_snapshot` + `browser_console` to extract job links.
- **Multi-org combined search (preferred):** `https://www.impactpool.org/search?q=ICT+digital+AI+telecom&orgs=UNICEF%2CUNDP%2CUNOPS%2CITU%2CWorld+Bank%2CFAO%2CWHO%2CUNESCO` — returns ~80 results across all target orgs.
- **Keywords to use:** "ICT", "senior", "digital transformation", "AI", "telecom", "UN", "P-4", "P-5", "D-1"
- **Pitfall:** Full job details require login. Cross-reference with direct org portals. Detail pages still render key fields (deadline, grade, location) without login.

### 2. UNICEF Careers
- **RSS feed:** `https://careers.pageuppeople.com/671/cw/en-us/latest_jobs.rss` — returns 190+ items, ~3.5MB. Namespace: `{http://pageuppeople.com/}`. Fields: refNo, closingDate, location, workType, category, applyLink.
- **Listing page:** `https://careers.pageuppeople.com/671/cw/en-us/listing/` — ~137KB HTML with job data.
- **Detail page pattern:** `https://careers.pageuppeople.com/671/cw/en-us/job/{refNo}`
- **VACANCY ID:** refNo from RSS or URL last path segment.
- **Do NOT use:** `jobs.unicef.org` — Cloudflare + Incapsula block ALL access.
- **Method:** curl + Python to parse RSS/listing HTML. No browser needed.

### 3. ITU Careers
- **URL:** https://jobs.itu.int/search/?q=ICT&locationsearch=
- **Access:** Public, works via curl with browser User-Agent.
- **Method:** curl + Python extraction of `.jobTitle-link` anchors.
- **Search keywords:** "ICT", "Digital Transformation", "Spectrum", "Telecom" (NOT grades).
- **Deadline extraction:** Fetch detail pages for `Closing Date` text. Roster positions have distant deadlines (30 June 2026 or 31 Dec 2026).
- **Roster positions found May 11, 2026:** Senior ICT/Digital Consultant for Americas (VN 2000, deadline Dec 31 2026); Emerging Technologies for Digital Transformation Consultant Asia-Pacific (VN 2172, deadline June 30 2026); Green Digital Transformation Consultant (VN 1970, deadline Dec 31 2026); Senior ICT/Digital Policy Consultant for Africa (VN 1818, deadline June 30 2026); Emerging Technology Consultant (VN 1348117555); Full Stack Engineer Consultant (VN 1327373955)

### 4. UNDP Jobs
- **URL:** https://jobs.undp.org/cj_view_jobs.cfm
- **Access:** Via Impactpool proxy (direct portal may block).
- **Method:** Search Impactpool for UNDP AI Hub / digital roles.

### 5. UNJobNet
- **URL:** https://www.unjobnet.org
- **Access:** USER MUST LOG IN FIRST via browser (CAPTCHA blocks automated login). Credentials stored in skill: your-email@example.com / YOUR_PASSWORD
- **Method (after login):** browser_navigate to `/jobs?orderby=recent`, type keywords in searchbox, click Search. Extract job data via browser_console from Vue.js rendered elements.
- **Alternative (public API):** `https://www.unjobnet.org/api/v1/jobs/search?keywords=ICT&limit=20` — works WITHOUT login! Use curl.
- **RSS:** `https://www.unjobnet.org/rss.xml` — minimal (2-3 items), not useful for full scan.
- **Pitfall:** Automated login always fails. User must manually log in once per browser session.

## SECONDARY SOURCES (scan regularly)

### 6. UN Careers Portal
- **URL:** https://careers.un.org
- **Access:** Public, limited search.

### 7. UNESCO
- **URL:** https://careers.unesco.org/go/All-jobs-openings/784002/ (52 jobs across 3 pages)
- **Access:** Public, SuccessFactors portal.
- **Method:** Browser. Accept cookies, then extract via browser_console table query (HTML table rows with 5 columns: title, location, type, grade, deadline).
- **Pagination:** Click page 2 (ref=e150) and page 3 (ref=e151). Note: SuccessFactors may redirect offset-based URLs back to page 1 — always use in-page click navigation. Page 3 content may not change in DOM — try `?q=&sortby=deadline&limit=20&offset=40` as fallback.
- **Extraction JS:**
  ```js
  Array.from(document.querySelectorAll('table tr')).slice(2).map(row => {
    const cells = row.querySelectorAll('td, th');
    return { title: cells[0]?.textContent?.trim(), loc: cells[1]?.textContent?.trim(),
      type: cells[2]?.textContent?.trim(), grade: cells[3]?.textContent?.trim(),
      deadline: cells[4]?.textContent?.trim() };
  }).filter(x => x.title && !x.title.includes('Title') && !x.title.includes('Filter'))
  ```

### 8. FAO
- **URL:** https://jobs.fao.org/careersection/fao_external/jobsearch.ftl?lang=en
- **Access:** Public Taleo portal.

### 9. WHO
- **URL:** https://careers.who.int/careersection/ex/jobsearch.ftl
- **Access:** Public Taleo portal.

### 10. World Bank Group
- **URL:** https://worldbankgroup.csod.com
- **Access:** SSO may block. Use Impactpool as proxy.

### 11. IMF
- **URL:** https://imf.wd5.myworkdayjobs.com/IMF
- **Access:** Workday portal. SSO may block. Use Impactpool.

### 12. UNHCR
- **URL:** https://unhcr.wd3.myworkdayjobs.com/en-GB/External
- **Access:** Workday portal, public.

### 13. WFP
- **URL:** https://wd3.myworkdaysite.com/en-GB/recruiting/wfp/job_openings
- **Access:** Workday portal, public.

### 14. UNOPS
- **URL:** https://careers.unops.org/careersmarketplace/SearchJobs
- **Access:** Public portal.

### 15. IOM (International Organization for Migration)
- **URL:** https://www.impactpool.org/search?org=IOM&q=ICT+digital+AI (via Impactpool proxy)
- **Access:** Impactpool job detail pages render fully for IOM positions. Verified working 2026-05-11.
- **Method:** Search via Impactpool multi-org URL or direct IOM search.

### 16. IDB (Inter-American Development Bank)
- **URL:** https://www.impactpool.org/search?org=IDB&q=digital+technology (via Impactpool proxy)
- **Access:** Impactpool detail pages render for IDB positions. Verified working 2026-05-11.
- **Note:** Requires IDB member country citizenship. Consultant contract, up to 48 months.

### 17. UNOV (United Nations Office at Vienna)
- **URL:** Via Impactpool or UN Careers portal.
- **Access:** Impactpool job detail pages render for UNOV positions. Verified working 2026-05-11.
- **Key role patterns seen May 11, 2026:** D-1 Chief, IT Service (UNOV Vienna, ref 1211389, deadline May 18); Head of AI and Data Protection Division (COE Strasbourg, ref 1210718, deadline May 20); IDB Technology Alignment Consultant (Washington, ref 1212803, deadline May 15); NATO YPP ICT (Brussels/Brunssum, ref 1210634, deadline May 31); IOM ICT Officer P (Geneva, ref 1212561); ICMPD Modernisation Officer AI (Beirut/Tunis, ref 1209244); IOM ICT Officer P-2 (Bangui, ref 1211796)

### 18. UN WOMEN
- **URL:** https://www.impactpool.org/search?org=UN+Women&q=AI+digital (via Impactpool proxy)
- **Access:** Impactpool detail pages render for UN WOMEN positions. Verified working 2026-05-11.

### 19. ELA (European Labour Authority)
- **URL:** https://www.impactpool.org/search?org=ELA&q=ICT+digital (via Impactpool proxy)
- **Access:** Impactpool detail pages render. Requires EU nationality. AD-8 grade.
- **Key role pattern:** Head of Sector - ICT and Digitalisation Support in Bratislava.

## NEW SOURCES (added May 11, 2026 — all tested accessible)

### 15. ILO
- **URL:** https://jobs.ilo.org/go/All-Jobs/2842101/
- **Access:** Public SuccessFactors portal.

### 16. ICAO
- **URL:** https://icaocareers.icao.int/careers/
- **Access:** Public.

### 17. IMO
- **URL:** https://recruit.imo.org/vacancies
- **Access:** Public.

### 18. WIPO
- **URL:** https://wipo.taleo.net/careersection/wp_2_pd/jobsearch.ftl?lang=en&portal=50305027338
- **Access:** Public Taleo portal.

### 19. WTO
- **URL:** https://wto.wd103.myworkdayjobs.com/External
- **Access:** Public Workday portal.

### 20. IFAD
- **URL:** https://job.ifad.org/psc/IFHRPRDE/CAREERS/JOBS/...
- **Access:** Public Oracle portal.

### 21. UNIDO
- **URL:** https://careers.unido.org/search/
- **Access:** Public.

### 22. IAEA
- **URL:** https://iaea.taleo.net/careersection/ex/jobsearch.ftl
- **Access:** Public Taleo portal.

### 23. UNEP
- **URL:** https://www.unep.org/work-with-us
- **Access:** Public.

### 24. UNFPA
- **URL:** https://www.unfpa.org/jobs
- **Access:** Public.

### 25. UNICRI
- **URL:** https://unicri.org/institute/join_us/jobs/vacancies
- **Access:** Public.

### 26. UNITAR
- **URL:** https://unitar.org/vacancy-announcements
- **Access:** Public.

### 27. UNSSC
- **URL:** https://www.unssc.org/employment-status
- **Access:** Public.

### 28. UNU
- **URL:** https://careers.unu.edu/
- **Access:** Public.

### 29. UNGM
- **URL:** https://www.ungm.org
- **Access:** Public (procurement portal, not primarily jobs).

### 30. GICHD
- **URL:** https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_5001/jobs
- **Access:** Oracle Cloud portal. Limited jobs found. Geneva International Centre for Humanitarian Demining.

### 31. Unidentified UN Agency (Oracle Cloud CX_1001)
- **URL:** https://fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs
- **Access:** Oracle Cloud portal. Organization could not be identified from page content. Generic "Careers Home / Search Jobs" title.

### 32. UNIDIR
- **URL:** https://unidir.org/who-we-are/join-our-team/
- **Access:** Accessible but currently shows "no current job openings". Check future scans.

## Failed Sources (do not retry without user action)
- Most direct SSO portals: WHO, FAO, IMF, World Bank block automated access. Use Impactpool proxy.

## LLM-Wiki Reference
The complete source list is also maintained at:
- `config/wiki/concepts/un-jobs-sources.md`
