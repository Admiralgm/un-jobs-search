# INSPIRA (UN Secretariat / careers.un.org) Extraction Protocol

Updated: 2026-05-28

## Portal Overview
- URL: https://careers.un.org/jobopening
- Platform: Angular SPA with Cloudflare WAF
- All API endpoints (careers.un.org/api/*) return 403 to curl — Cloudflare blocked
- Browser-based extraction is MANDATORY

## Access Method
**browser_navigate + browser_console JS extraction (ONLY reliable method)**

### Step 1: Navigate
```
browser_navigate(url="https://careers.un.org/jobopening")
```

### Step 2: Enter keyword
```
browser_type(ref=e3, text="INFORMATION TECHNOLOGY")  # ref for search box
browser_click(ref=e4)  # Search Jobs button
```

### Step 3: Wait for results to render, then extract
```
browser_console(expression="let c = document.querySelector('.content'); c ? c.innerText : 'No content'")
```

The results render inside a `<div class="content">` element that contains all job listings with:
- Job title
- Job ID (6-digit numeric)
- Job Network/Family
- Category & Level (Grade)
- Duty Station
- Department/Office
- Date Posted
- Deadline
- "View Job Description" link

## Mandatory Keywords (use ALL 7)

| Keyword | Typical Results | Best For |
|---------|----------------|----------|
| **Information Technology** | ~29 | BEST — catches IS Officer, IT Specialist, P-level roles |
| **Digital** | ~7 | UI/UX, digital consultants, Digital Communications Officer |
| **Artificial Intelligence** | ~3-5 | AI strategy, AI engineering consultant roles |
| **ICT** | ~1 | Narrow — mostly false positives |
| **Telecom** | ~3 | Chief Broadcast, Telecom Assistants |
| **ISP** | ~0 | No current use |
| **connectivity** | ~0 | No current use |

**Keyword strategy:** Always start with "Information Technology" — it yields the most P-level roles. Use "Digital" and "Artificial Intelligence" for consultant/specialist roles. Skip "ISP" and "connectivity" unless searching for specific known vacancies.

## Bug Workaround (CRITICAL)
- Use the **keyword textbox only** to search
- Do NOT use filter checkboxes (Job Network, Job Family, Category, Level, Duty Station)
- Clicking "Search Jobs" after selecting checkboxes **resets the page** to empty results
- Only the keyword search box triggers a proper API call that returns results

## Vacancy ID Format
- Official 6-digit numeric ID (e.g., 278175, 275606, 277807)
- ID is in the URL: `https://careers.un.org/jobSearchDescription/{6-digit-id}?language=en`

## Deadline Verification (CRITICAL PITFALL)
- Listing pages show the deadline in the `.content` div — this is reliable
- Detail page URL: `https://careers.un.org/jobSearchDescription/{ID}?language=en`
- If the detail page is EMPTY, the role has expired (also Cloudflare-blocked on direct load)
- The listing page deadline is usually sufficient — only visit detail page if deadline is ambiguous

## Exclusion Filter for INSPIRA Results
Most INSPIRA results at P-3+ level are either:
- **CON (Consultants)** — temporary, short-term contracts
- **TJO (Temporary Job Opening)** — limited duration
- **G-level** — General Service (admin/assistant roles, G-4 to G-7)
- **Internships** — I-1 level, excluded

The few Professional roles (P-2, P-3, P-4+) are worth tracking. P-3 and above that are fixed-term are the highest priority.

## Pagination
- Results are paginated at 10 per page
- URL parameter: `start=10` for page 2, `start=20` for page 3
- Example page 2 URL: `https://careers.un.org/jobopening?language=en&data=%7B%22keyword%22%3A%22Information%20Technology%22%2C%22start%22%3A10%7D`
- Maximum 3 pages (29-30 results for top keyword)

## Apply Link Pattern
```
https://inspira.un.org/psp/PUNA1J/EMPLOYEE/HRMS/c/UN_CUSTOMIZATIONS.UN_JOB_DETAIL.GBL?Action=A&UNAction=Apply&JobOpeningId={6-digit-id}&languageCd=ENG
```

## Departments Covered by INSPIRA
All UN Secretariat entities including:
- OICT (Office of Information and Communications Technology)
- UNOV, UNON, UNOG (Vienna, Nairobi, Geneva offices)
- OCHA, UNDRR, UNEP, UNCTAD, ESCAP, ESCWA, ECA, ECE, ECLAC
- UNRWA, ICJ, UNICRI, UNODC, DSS, DPO, DPPA
- UNJSPF, DOS, DMSPC
- UN-Habitat, UN Environment Programme

**Note:** INSPIRA covers UN Secretariat departments only. Specialized agencies (UNICEF, UNDP, WFP, WHO, ILO, ITU, etc.) have their own separate portals.
