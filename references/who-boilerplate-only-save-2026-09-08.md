# WHO run_who.py Boilerplate-Only Save (2026-09-08)

## Symptom
`run_who.py` uses StealthyFetcher with `disable_resources=True`. WHO Taleo detail pages are JS-rendered, so saved JDs can contain ONLY the header block + collapsed section names (Grade, Contract, Closing Date, then empty OBJECTIVES/DESCRIPTION OF DUTIES/REQUIRED QUALIFICATIONS/Experience/Skills/Languages).

Detect: JD file ~7KB with section headers but no content under them.

## Fix
Fetch the jobdetail URL via Camoufox REST (port 9377):
1. `POST /tabs` with `{userId, sessionKey, url}` → tabId
2. sleep ~20s for JS render
3. `POST /tabs/{tid}/evaluate` with `document.body.innerText` → full text
4. Overwrite the JD file with the full text (keep header + add full sections)

## Rule
NEVER score from a boilerplate-only JD. If the script's saved JD lacks Description of Duties / Required Qualifications, re-fetch via Camoufox before scoring.

## Tracker edit pitfall (same session)
When inserting a row into UN-VACANCIES-TRACKER.txt, verify the anchor row's actual number first (grep the VID). A failed insertion still renumbers rows — re-running the renumber pass double-shifts numbers. Renumber per-section (OPEN / ROLLING / ROSTER) by counting rows within each section, not by global offsets.
