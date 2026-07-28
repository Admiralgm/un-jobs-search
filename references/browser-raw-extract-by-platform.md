# Browser Raw Extract by Platform
## Verified: 2026-05-30 across 16 UN/international career portals + INSPIRA

## Universal Extraction Expression
```javascript
(function(){const a=document.querySelector('article');return a?a.innerText:document.body.innerText;})()
```

## Portal-by-Portal Results

### ✅ article.innerText WORKS (4 portals)
| Portal | Platform | Notes |
|--------|----------|-------|
| WHO Taleo | Taleo (Oracle) | Full with Objectives/Duties/Qualifications/Remuneration sections |
| UNOPS | ICS Custom | Multiple article elements; main content in first one |
| IOM Oracle Cloud | Oracle Cloud | 11K chars typical from detail page |
| UNICEF | PageUp | `document.querySelector('ARTICLE.page').innerText` on detail pages |

### ✅ body.innerText WORKS (14 portals)
| Portal | Platform | Detail Page Quality |
|--------|----------|-------------------|
| ITU | SuccessFactors (SAP) | Full job description, all sections |
| UNESCO | SuccessFactors (SAP) | Full content |
| ILO | SuccessFactors (SAP) | Full content with all headings |
| IAEA | Taleo (Oracle) | Full (no article but body has everything) |
| FAO | Taleo (Oracle) | Full with sections |
| ICRC | SuccessFactors (SAP) | Full content. ⚠️ Triple-rendering bug — dedup results. |
| WFP | Workday | 12K chars, all sections expanded |
| IMF | Workday | 8K chars, full content |
| UNHCR | Workday | Full content |
| OECD | SmartRecruiters | 11K chars |
| UNDP | Oracle HCM | Full content, redirects to estm.fa.em2.oraclecloud.com |
| UNIDO | SuccessFactors | Full content |
| UNFPA | Oracle HCM | Full content, redirects to estm.fa.em2.oraclecloud.com |
| WTO | SmartRecruiters | Same as OE OD |
| UNITAR | Custom CMS | Full content |
| ICMPD | Custom | Full content |
| GICHD | Custom + Beehire | Links to external Beehire |

### ✅ INSPIRA (careers.un.org) — Two-Step Extraction
| Portal | Method | Detail Page Quality |
|--------|--------|-------------------|
| ICAO, UNCTAD, OCHA, OICT, UNJSPF, OIM, ISA, UNON, UPU, UN-Habitat, UNOV, UNON, UNEP, UNODC, OHCHR | **Step 1:** `browser_click` on "Expand All" button (ref e20 by default) | Returns **19K-22K chars** — all sections expanded (Org. Setting, Responsibilities, Competencies, Education, Work Experience, Languages, Special Notice, etc.) |
| | **Step 2:** `browser_console(expression="document.body.innerText")` | Full job content including UN boilerplate sections |

**Key details:**
- No `<article>` tag — always use `document.body.innerText`
- No login required for job description pages
- The "Expand All" button triggers AJAX expansion of all accordion sections
- Before expand: ~6K chars (only metadata + first section)
- After expand: ~22K chars (all sections, including: Org. Setting, Responsibilities, Competencies, Education, Work Experience, Languages, Assessment, Special Notice, UN Considerations, No Fee)

**ITECNET pre-filtered listing URL:**
```
https://careers.un.org/jobopening?language=en&data=%7B%22jn%22:[%22ITECNET%22],%22jf%22:[],%22jc%22:[],%22jle%22:[]%7D
```
This URL pre-applies the "Information and Telecommunication Technology" Job Network filter. Confirmed working 2026-05-30.

**Alternative INSPIRA URL (all jobs, apply ITEC NET filter manually):**
```
https://careers.un.org/jobopening?language=en&data=%257B%2522aoe%2522:%255B%255D,%2522aoi%2522:%255B%255D,%2522el%2522:%255B%255D,%2522ct%2522:%255B%255D,%2522ds%2522:%255B%255D,%2522jn%2522:%255B%255D
```
Loads all jobs with empty filter arrays. Must manually check "Information and Telecommunication Technology" checkbox after page loads. Use if primary ITECNET URL stops working.

**Pagination via JavaScript:**
When `browser_click` on page numbers fails (500 error from Camoufox), use JS fallback:
```javascript
let links = Array.from(document.querySelectorAll('a')).filter(a => a.textContent.trim() === '2');
if(links.length) links[0].click();
```
Then extract with `document.body.innerText` again.

**15 ITECNET jobs found (May 30, 2026):** 10 on page 1, 5 on page 2. Grades: G5(1), G6(2), P2(1), P3(6), P4(2), P5(2). Mostly UNJSPF, OICT, UNCTAD, UNON, OCHA, ISA.

### ❌ Extraction Fails (2 portals)
| Portal | Why | Alternative |
|--------|-----|-----------|
| World Bank CSOD | Empty page in browser | Scrapling StealthyFetcher |
| IMO | Camoufox crashes on click, 8 non-IT jobs | Skip |

## Platform Detection Heuristic
Before extracting, check `document.querySelector('article')` — if truthy, use `article.innerText`, else use `body.innerText`. This handles all portals correctly. **Exception: INSPIRA** — always needs "Expand All" click first before body.innerText.

## Camoufox Fatigue Limit
After 10-15 navigations across detail pages, the Camoufox tab becomes unresponsive. Signal: 500 on browser_navigate. Fix: `pkill -f "camofox server"` → restart. Mitigation: save every file immediately after extraction.
