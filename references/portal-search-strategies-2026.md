# UN Portal Search Strategy Analysis (May 2026)

## Observations on Query Sensitivity

During the May 15, 2026 scan, a significant difference was noted in result yields between combined and single-keyword searches.

### Portal: WHO (Taleo)
- **Query: "AI ICT Digital"** -> 0 results.
- **Query: "Digital"** -> 6 results (including Technical Officer roles).
- **Takeaway**: Taleo's search engine on the WHO instance appears to treat spaces as strict "AND" operators or fails to rank results with partial keyword matches.

### Portal: IAEA (Taleo)
- **Query: "Digital AI ICT"** -> 0 results.
- **Query: "Digital"** -> 1 result (Chief Information Officer, D-1).
- **Takeaway**: High-seniority ICT roles often do not use the term "AI" in their titles or metadata, even if the role involves AI strategy.

### Portal: UNHCR (Workday)
- **Query: "Digital AI ICT"** -> 0 results.
- **Behavior**: Workday portals often require session-level interaction (like accepting cookies) to 'unlock' the search result list effectively.

## Recommended Triage for 0 Results
1.  Verify cookie/session state (browser).
2.  Split multi-term queries into individual terms.
3.  Priority order: "Digital" > "ICT" > "AI" (for senior roles).
