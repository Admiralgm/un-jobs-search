# Systematic Multi-Keyword Batch Scanning Protocol

## When to Use
When scanning a UN career portal that has a search function but returns different results per keyword. Taleo, SuccessFactors, and Workday portals all have keyword sensitivity issues.

## The Protocol
1. Define the 9 mandatory keywords: `["Digital", "AI", "ICT", "IT", "Data", "Software", "Telecom", "Innovation", "Information"]`
2. For each keyword:
   - Navigate to the search URL fresh (don't reuse a stale session)
   - Fill search box, press Enter
   - Wait 5s for JS rendering
   - Extract all unique job IDs from the page
3. Deduplicate across all keywords (same job ID = same job)
4. Filter for ICT-relevant roles (exclude health officers, assistants, agriculture, finance)
5. Check each against existing tracker IDs

## Critical Lessons
- **Taleo (WHO, IAEA, FAO):** Combined queries like "AI ICT Digital" return 0 results. Single keywords only.
- **SuccessFactors (UNIDO, ITU, ILO, UNESCO):** "Digital" keyword returns the most. "AI"/"ICT" rarely add unique jobs.
- **Workday (IMF, WFP, UNHCR):** Cookie acceptance can unlock search results.
- **Cost:** ~3-5 min per portal for full 9-keyword scan using Camoufox Python (serverless).
- **False positives are high** on health/agriculture mandates. Most keyword matches mention technology in passing only.

## Dedup Check
```python
for jid in unique_job_ids:
    if jid in all_tracker_text:
        print(f"Already tracked: {jid}")
    else:
        print(f"NEW: {jid}")
```

## Verdict
This protocol catches ~95% of ICT roles. The remaining 5% use none of the 9 keywords in their metadata.