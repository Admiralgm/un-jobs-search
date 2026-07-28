# UN System Portal Coverage Gap Analysis — May 2026

## Source: Wikipedia "United Nations System" page (May 2026)
## Method: Extracted via browser_console document.body.innerText, compared against un-jobs-search-minimaltoken batch definitions

## Summary

| Metric | Count |
|--------|-------|
| UN System organisations in scope | 49 |
| Currently scraped via direct portal | 32 |
| Covered via Inspira (Batch 7) | 3 |
| Correctly skipped (no ICT roles) | 11 |
| Recommended to add | 3 |

---

## Per-Organisation Assessment

### SPECIALIZED AGENCIES (15)
| Org | Scraped? | Notes |
|-----|----------|-------|
| FAO | ✅ Batch 2 | Camoufox Taleo + RSS |
| ICAO | ✅ Batch 4 | Camoufox / browser |
| IFAD | ❌ **ADD** | Rome-based IFI. Agricultural IT. Portal: ifad.org/en/work-with-us. Moderate yield. |
| ILO | ✅ Batch 4 | Camoufox |
| IMO | ✅ Batch 4 | Camoufox |
| IMF | ✅ Batch 5 | Workday |
| ITU | ✅ Batch 3 | Camoufox |
| UNESCO | ✅ Batch 4 | Camoufox |
| UNIDO | ❌ **ADD** | Vienna-based. Industrial AI/digital transformation. Portal: careers.unido.org. Moderate yield. |
| UPU | ✅ Batch 7 | Inspira |
| WBG | ✅ Batch 6 | CSOD/Scrapling |
| WHO | ✅ Batch 3 | Camoufox Taleo |
| WIPO | ❌ **ADD** | Geneva. ICT-heavy (AI patent tools, IT infrastructure). HIGH priority. Portal: wipo.taleo.net + ungm.org. See wipo-taleo-extraction.md. |
| WMO | ✅ Batch 6 | erecruit.wmo.int |
| UNWTO | ✅ Batch 7 | Inspira |

### FUNDS & PROGRAMMES (11)...[truncated for brevity]

## Action Items
1. **Add Batch 10** with WIPO (Camoufox Taleo), UNIDO (careers.unido.org), IFAD (ifad.org/careers)
2. **Add Inspira org filters** for UNEP, UNODC, OHCHR
3. **Consider dropping** ECB, ICMPD, GICHD from scan rotation
4. **Run audit quarterly** to catch new ICT vacancies at low-yield orgs