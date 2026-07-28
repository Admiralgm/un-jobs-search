# Portal Extraction Test Results — 2026-05-30

## Tested Portals (all kept in scan rotation)

| Portal | URL | Status | ICT Found |
|--------|-----|--------|-----------|
| UNICEF | jobs.unicef.org | keyword search + DOM extraction | AI Consultant, ICT Policy, Tech for Development |
| WHO | careers.who.int | keyword search + table view | AI Software Eng Lead, Data Eng Developer |
| ITU | jobs.itu.int | View all to table | Green Digital Consultant, Cybersecurity |
| IAEA | iaea.taleo.net | keyword search + table | Data Engineer (P3), QA Engineer (P2) |
| FAO | jobs.fao.org | keyword search + list | Salesforce Marketing Tech Specialist |
| UNESCO | careers.unesco.org | search/?q= URL | Front-end Dev, DevOps Engineer |
| UNOPS | careers.unops.org | keyword search | AI Geospatial Advisor |
| IMF | imf.wd5.myworkdayjobs.com | keyword search | IT Strategist, Data Engineer |
| WFP | wd3.myworkdaysite.com | keyword search + pages | Full-stack developer (Rome) |
| OECD | careers.smartrecruiters.com/OECD | keyword search | Deputy Head Digital Workplace |
| WTO | careers.smartrecruiters.com/WTO | same platform | Low yield |
| INSPIRA | careers.un.org | ITECNET pre-filtered URL | ~15 ICT jobs |
| ILO | jobs.ilo.org | View all jobs link | Director IT Management/CIO |
| UNDP | jobs.undp.org | keyword filter | Enterprise Data Architecture (NPSA-9) |
| UNIDO | careers.unido.org/search/?q= | SuccessFactors | Sr Process Transformation and AI Expert |
| UNITAR | unitar.org/vacancy-announcements | Custom CMS | EdTech/AI Learning roster |
| GICHD | gichd.org | Beehire external | No ICT on first page |
| UNFPA | www.unfpa.org/jobs | Oracle HCM | Low yield (health mandate) |
| ICMPD | careers.icmpd.org | Custom base URL only | HR IS and Automation Officer |
| ICRC | careers.icrc.org | SuccessFactors + RSS | BI Reporting Analyst, Anaplan Model Builder |
| IFAD | www.ifad.org | PeopleSoft | Keep scanning |

## Key Findings
- Camoufox v2.4.5 works with UNICEF (previously blocked in v2.4.3)
- ICRC uses body.innerText (no article tag) — universal fallback confirmed
- INSPIRA alternative URL confirmed working (empty filter arrays)
- User requires ALL portals kept in scan rotation regardless of historical yield

## Extraction Files Produced
- ICRC_1389050633_ANAPLAN_Model_Builder.md (4279 bytes)
- ICRC_1389155933_BI_Reporting_Analyst.md (4082 bytes)