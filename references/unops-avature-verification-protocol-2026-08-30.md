# UNOPS Live Vacancy Verification — Avature Pagination Trap

**Incident:** 2026-08-30 (scan session, UNOPS_4241 deadline re-verification)

## The trap
UNOPS Careers Marketplace (careers.unops.org) is a **JS-rendered Avature portal**.
Two verification attempts fail silently and look authoritative:

1. **curl / plain HTTP fetch** → returns a 60KB CSS/nav shell with **zero job
   data**. Any HTML grep on it yields nothing. Never conclude "vacancy closed"
   from a curl of this portal.
2. **List-pagination clicking** (open search page, click page 2…15, search for
   the title) → the click loop stopped registering after page ~2 (Avature
   re-renders the grid; programmatic clicks stop registering) and the title
   check returned "not found" on every page checked. **A failed pagination
   sweep is NOT evidence a vacancy is gone.**

The programmatic form input also failed: setting `input#search` value +
dispatching `input` events did not register with the Avature widget, and
pressing Enter submitted the unchanged form.

## The reliable protocol (verified working 2026-08-30)

For UNOPS deadline/availability verification, **always use the direct
JobDetail URL** obtained via web search (format):
```
https://careers.unops.org/careersmarketplace/JobDetail/<title-slug>/<jobId>
```
Loading that URL in Camoufox and reading `document.body.innerText` renders
the full job card including:
- `Posting End Date` (canonical deadline — e.g. `01-Sep-2026`)
- `Posting Start Date`, `Contract Type` (ICA/IICA/Retainer), `ICS Level`
- Duty station, duration, job highlight

**Decision rules:**
- Direct URL renders job card → vacancy LIVE; trust the displayed
  `Posting End Date` over any tracker value.
- Direct URL → "No jobs found" / error → vacancy gone (only then).
- Job-slug in URL can be anything (e.g. an old title); Avature routes on
  the numeric ID.

## Session history (do not repeat)
- `SearchJobs/job4241?jobRecordsPerPage=10` → "No jobs found" even though the
  vacancy existed (wrong URL pattern; the job4241 path is not a valid deep link).
- 15-page click sweep → false negative ("NOT_FOUND" on all pages).
- Form-search JS injection → input never registered.
- Direct JobDetail URL → **vacancy found, deadline 01-Sep-2026, live.**