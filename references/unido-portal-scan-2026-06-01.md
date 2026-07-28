# UNIDO Career Portal — June 1, 2026 Scan

## Portal Details
- **URL:** https://careers.unido.org/ (SuccessFactors)
- **Search URL:** https://careers.unido.org/search/?q={keyword}
- **Job detail URL:** https://careers.unido.org/job/Vienna-{slug}/{RequisitionID}/
- **Platform:** SAP SuccessFactors

## Scan Results (10 keywords: Digital, AI, IT, ICT, Data, Innovation, Technology, Software, Information)
- **11 unique jobs** found across all keywords
- **High-value roles found (2):**

| Req ID | Title | Grade | Location | Deadline | Score |
|--------|-------|-------|----------|----------|-------|
| 1352426455 | Industrial Development Officer (Div of Digital Transf & AI) | P-3 | Vienna | Jun 5 | 🟡 78 |
| 1352440555 | Sr Process Transformation & AI Integration Expert | ISA-P5 | Vienna | Jun 8 | 🟠 82 |

## Key Division: TCS/DAI
- **Division of Digital Transformation and Artificial Intelligence**
- Active recruiting for P-3 Industrial Development Officer and ISA-P5 AI Expert
- Directly relevant to User's AI/ICT profile

## Search Observations
- **"Digital" keyword** returned the most relevant results (11 unique)
- **"AI", "IT", "ICT"** returned 0 additional unique jobs beyond Digital
- Combined queries not necessary on SuccessFactors — single keyword works

## Extraction Pattern
1. Navigate to `/search/?q=Digital`
2. Extract job links from `<a>` elements containing `/job/Vienna-`
3. For each detail page: extract Grade (in `Grade:` field), Deadline (in `Application Deadline:` field), Location
4. Grade field format: `P3`, `ISA-P5`, `G-5` (no dash in P3)