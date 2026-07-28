# Entry Format Template — UN Job Vacancy Tracker

## Mandatory Output Format

Every vacancy entry in the tracker files MUST follow this exact format. The MATCH ANALYSIS section uses the 3-dimension scoring model: Technical Relevance (60%) + Seniority Alignment (20%) + Strategic Alignment (20%).

### Complete Example

```
🔴 RED — AI Centre of Excellence Lead
================================================================================
- Title: AI Centre of Excellence Lead
- VACANCY ID: 3059
- REF NUMBER: (Ref number if different from VACANCY ID, e.g. #00136822 — otherwise same as VACANCY ID)
- Organization: UNOPS
- Grade: ICS 11 (IICA 3)
- Location: Remote | Copenhagen, Home based
- Deadline: 2026-05-24
- Contract type: ICA - IICA - Regular
- Estimated compensation (USD): $110K-$140K
- HYPERLINK: https://careers.unops.org/careersmarketplace/JobDetail/AI-Centre-of-Excellence-Lead/3059
- SCORE: 97/100
- APPLIED: NO

MATCH ANALYSIS:
- Technical Relevance (60%): 60 — Strategic lead for new AI Centre of Excellence. Direct match with AI/LLM expertise, AI agent frameworks, and AI governance experience.
- Seniority Alignment (20%): 19 — ICS 11 (IICA 3) matches P-4/P-5 seniority. 26-year executive profile with COO and director-level experience.
- Strategic Alignment (20%): 18 — Reports to CIO; manages AI pipeline and team. Exceptional strategic fit.

-
🚀 Positioning Advice:
- Lead with hands-on AI/LLM deployment experience
- Emphasize AI governance and responsible AI framework knowledge
- Highlight UNICEF GIGA/LP experience as proof of international delivery
- Frame MVNO/MVNE platform build as evidence of leading complex tech initiatives

📊 Verdict: STRONG FIT (97%)
Confidence Level: HIGH
================================================================================
```

### Scoring Calculation

The scores in each dimension represent the WEIGHTED contribution (already multiplied by the weight):
- Technical Relevance: raw 100/100 × 60% = 60 shown
- Seniority Alignment: raw 95/100 × 20% = 19 shown
- Strategic Alignment: raw 90/100 × 20% = 18 shown
- Total: 60 + 19 + 18 = 97/100

### Color Coding Rules

- 🔴 RED for STRONG FIT (85-100)
- 🟠 ORANGE for COMPETITIVE (70-84)
- 🟡 YELLOW for STRETCH (55-69)
- 🟢 GREEN for LOW FIT (<55)

### File Locations

- Primary tracker: `~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt`
- Aggregator tracker: `~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_IMPACTPOOL.txt`
- Archive: `~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES_ARCHIVE.txt`

### Summary Table Regeneration

After every file write (add/remove/modify entries), the Vacancy Summary Table at the top of each active file must be regenerated. Use `execute_code` Python to:
1. Parse all entries from the file
2. Sort by deadline date (nearest first, TBD at end)
3. Build table: #, Organization, Position Title, Deadline, Score (color-coded), Vacancy ID
4. Prepend after the header block
