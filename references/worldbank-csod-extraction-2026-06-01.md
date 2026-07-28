# World Bank CSOD Extraction (2026-06-01)

## Portal

**URL:** `https://worldbankgroup.csod.com/ats/careersite/search.aspx?site=1&c=worldbankgroup`

**Platform:** CSOD (Cornerstone OnDemand). JS SPA — `requests` returns empty, browser needed. Unlike the old advice, Scrapling is NOT required: **Camoufox Python serverless renders the page**, but the job cards are hidden from `body.innerText`.

## Working Extraction Pattern

```python
from camoufox import Camoufox
import time, json

with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.set_default_timeout(30000)
    page.goto("https://worldbankgroup.csod.com/ats/careersite/search.aspx?site=1&c=worldbankgroup")
    time.sleep(8)  # Critical: wait for SPA to hydrate

    # Extract ALL job cards via JS querySelector
    jobs = page.evaluate("""() => {
        // Job cards are <div class="p-panel"> containing <a> with job title + <p> with location + date
        const seen = new Set();
        const results = [];
        const jobLinks = document.querySelectorAll('a[class*="link"]');
        for (const a of jobLinks) {
            const t = a.innerText?.trim();
            if (!t || t.length < 5 || t.length > 150 || seen.has(t)) continue;
            // Filter to actual job titles (not nav links)
            if (/Temporary|Consultant|Analyst|Officer|Specialist|Manager|Engineer|Developer|Advisor|Assistant/.test(t)) {
                seen.add(t);
                const parent = a.closest('div');
                const parentText = parent ? parent.innerText : '';
                results.push({
                    title: t,
                    lines: parentText.split('\\n').map(l => l.trim()).filter(l => l),
                    href: a.getAttribute('href') || ''
                });
            }
        }
        return JSON.stringify(results, null, 2);
    }()""")
```

## What the Listing Reveals

- **Job titles, location, posting date** (MM/DD/YYYY), apply link
- Detail pages at `/ux/ats/careersite/1/home/requisition/{reqid}?c=worldbankgroup` render full JD
- Detail pages contain: Organization, Sector, Grade, Term Duration, Recruitment Type, Location, Required Language, Closing Date, Description
- **Grade band:** GE (≈P-2), GF (≈P-3), GG (≈P-4), EC2 (E T Consultant — senior consultant)
- **Recruitment Type:** "Local Recruitment" is the critical filter — all current ICT roles are Local Recruitment requiring US or India work authorization

## June 2026 ICT Roles Found

| Job # | Title | Grade | Location | Term | Verdict |
|-------|-------|-------|----------|------|---------|
| req36831 | AI Solutions Analyst | GE | Washington DC | 3yr Local | Below P-3, US local |
| req36827 | AI Service Mgmt Transformation Lead | GG | Washington DC | 3yr Local | US local |
| req36825 | AI Incident & Problem Mgmt Lead | GF | Washington DC | 3yr Local | US local |
| req36819 | Sr GenAI Engineering Practitioner (E T Consultant) | EC2 | Chennai, India | 1yr | India local, already tracked |
| req36677 | Database Administrator (E T Consultant) | EC2 | Chennai, India | 1yr | India local, DBA role |

All 5 are Local Recruitment — **only applies if User already holds US/India work authorization**. None are international posts.

## Pitfalls

- Job family filter options visible in DOM (`<option>Information Technology (19)</option>`, `<option>Information & Communication Technology (2)</option>`) but selecting them requires button clicks that are fragile in headless mode
- Camoufox HTTP server crashes on CSOD (500) — use Python serverless mode
- `body.innerText` only shows filter sidebar — hidden job cards require JS extraction
- All ICT roles this cycle are Washington DC or Chennai — no Vienna/Belgium/remote international posts
- Scrapling gives identical results to Camoufox Python for this portal