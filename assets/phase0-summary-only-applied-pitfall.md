# Phase 0 Pitfall — Applied Entries Without Detail Sections

**Discovered:** 2026-06-25  
**Context:** Tracker cleanup session — 3 applied entries (ICRC_1386003233, IAEA_M365_P3, IAEA_2026_M365_Specialist) existed only as summary rows, not as detail sections.

## Problem

When applied entries only exist as **summary rows** in the tracker (no separate `🔴 RED — Title` detail section below the table), the cleanup code's detail-section detection finds nothing to move to the archive. The summary rows get removed but no archive entry is created.

## Fix

After removing summary rows for applied entries, check if each applied VID has a corresponding detail section by searching for `VACANCY ID: {vid}` in the tracker text below the summary table.

If no detail section exists, create a **compact archive record** (no MATCH ANALYSIS, no Verdict):

```
================================================================================
ARCHIVED: YYYY-MM-DD | APPLIED
Organization: [org]
Title: [full title]
Vacancy ID: [vid]
Deadline: [deadline]
Score: [score emoji + number]
================================================================================
```

Append this compact record to the archive file and verify the VID appears in the archive after write.
