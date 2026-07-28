# UN Jobs Search

Scans 32+ UN and international organization career portals for ICT, AI, digital transformation, and telecom vacancies. Extracts full job descriptions, scores them against a compatibility engine, and maintains a tracker file.

## Architecture

```
un-jobs-search-github/
├── skill/                    # Operational skills (Hermes Agent format)
│   ├── SKILL.md              # Master skill (128KB) — full scanning procedure
│   └── SKILL-minimaltoken.md # Token-optimized variant (70KB)
├── scripts/
│   ├── agency-scan/          # Per-agency portal scanners (25+ agencies)
│   │   ├── run_who.py        # WHO Taleo
│   │   ├── run_unicef.py     # UNICEF
│   │   ├── run_inspira_v4.py # careers.un.org (INSPIRA)
│   │   ├── run_undp_v4.py    # UNDP
│   │   ├── run_unhcr.py      # UNHCR Workday
│   │   ├── run_ilo_v3.py     # ILO
│   │   ├── run_itu_v4.py     # ITU
│   │   ├── run_unesco_v4.py  # UNESCO
│   │   ├── run_unfpa_v4.py   # UNFPA
│   │   ├── run_unops_v3.py   # UNOPS
│   │   ├── run_wmo.py        # WMO
│   │   ├── run_iaea.py       # IAEA Taleo
│   │   ├── run_icao_v3.py    # ICAO
│   │   ├── run_imo.py        # IMO
│   │   ├── run_ifad.py       # IFAD
│   │   ├── run_oecd_v4.py    # OECD SmartRecruiters
│   │   ├── run_unitar_v4.py  # UNITAR
│   │   ├── run_icmpd_v3.py   # ICMPD
│   │   ├── run_unido.py      # UNIDO
│   │   ├── run_unu.py        # UNU
│   │   ├── run_fao.py        # FAO Taleo
│   │   ├── run_wipo.py       # WIPO
│   │   ├── run_workday.py    # Generic Workday
│   │   ├── run_worldbank.py  # World Bank CSOD
│   │   ├── run_ecb.py        # ECB
│   │   ├── run_icrc_v2.py    # ICRC
│   │   └── run_broad_scan.py # Broad multi-portal scan
│   ├── extraction/           # JD extraction & scraping
│   │   ├── camoufox_fulljd_scraper.py
│   │   ├── camoufox_fulljd_scraper_v2.py
│   │   ├── camoufox_rest_scan.py
│   │   ├── scrape_online_camoufox.py
│   │   ├── scrape_online_v2.py
│   │   ├── scrape_top25.py
│   │   ├── extract_deadlines.py
│   │   ├── extract_jd_deadlines.py
│   │   ├── extract_all_deadlines_v3.py
│   │   ├── deadline_matcher_v2.py
│   │   ├── online_deadline_scraper.py
│   │   ├── linkedin_job_scraper.py
│   │   ├── impactpool_a2_extract.py
│   │   ├── scan_details.py
│   │   ├── extract_csod.py
│   │   └── ...
│   ├── scoring/              # Compatibility scoring
│   │   ├── batch_score_all.py
│   │   ├── batch_score_contextual.py
│   │   ├── calibrate_scores.py
│   │   ├── final_calibrate.py
│   │   ├── prefilter_and_classify.py
│   │   └── broad_scan_keywords.py
│   ├── tracker/              # Tracker file management
│   │   ├── rebuild_tracker.py
│   │   ├── rebuild_tracker_v2.py
│   │   ├── rebuild_v6.py
│   │   ├── rebuild_v7.py
│   │   ├── rebuild_complete.py
│   │   ├── rebuild_v71.py
│   │   ├── cleanup_tracker.py
│   │   ├── parse_tracker.py
│   │   ├── add_new_entries.py
│   │   ├── fix_iaea_row.py
│   │   ├── map_deadlines_to_tracker.py
│   │   ├── final_rebuild.py
│   │   ├── final_rebuild_v5.py
│   │   └── ...
│   ├── web-preclean.py       # Token-optimized HTML pre-cleaner (94-95% reduction)
│   ├── audit-and-verify.py   # Tracker audit
│   ├── merge-vacancies.py    # Merge vacancy lists
│   ├── bulk-add-vacancy-ids.py
│   ├── update-internal-ids.py
│   ├── batch_scan.py         # Batch portal scanning
│   ├── batch_scan_all.py    # Batch all portals
│   └── scan_helper.py       # Scan helper utilities
├── references/              # 100+ technical reference docs
│   ├── portal-directory.md          # All 32+ portal URLs and methods
│   ├── portal-classification-map.md  # Platform type per portal
│   ├── platform-patterns-and-access-status.md
│   ├── extraction-methods-by-platform.md
│   ├── matching-keywords.md          # ICT/AI/telecom keyword filter
│   ├── scoring-guide.md
│   ├── tracker-file-write-technique.md
│   ├── credentials.md               # Portal login info (sanitized)
│   ├── INDEX.md                      # Reference index
│   └── ...
├── assets/                  # Operational notes and pitfall docs
│   ├── tracker-structural-verification.md
│   ├── tracker-update-patch-method.md
│   ├── broad-scan-mode-pitfalls.md
│   ├── pre-scan-readiness-check.md
│   └── ...
├── .gitignore
├── LICENSE
└── README.md
```

## Portals Covered (32+)

| Portal | Platform | Method |
|--------|----------|--------|
| careers.un.org (INSPIRA) | Custom (Oracle) | Browser extraction + SearXNG |
| UNICEF | SuccessFactors | API + browser |
| WHO | Taleo | RSS + browser |
| UNDP | SuccessFactors | API |
| UNHCR | Workday | API + browser |
| ILO | Taleo | Browser |
| ITU | Taleo | Browser |
| UNESCO | Taleo | Browser |
| UNFPA | SuccessFactors | API |
| UNOPS | SuccessFactors | API |
| WMO | Taleo | Browser |
| IAEA | Taleo | Browser (login) |
| ICAO | Taleo | Browser |
| IMO | Taleo | Browser |
| IFAD | SuccessFactors | API |
| UNIDO | Taleo | Browser |
| UNU | SuccessFactors | API |
| FAO | Taleo | Browser |
| WIPO | Taleo | Browser |
| UNITAR | SuccessFactors | API |
| ICMPD | SmartRecruiters | API |
| OECD | SmartRecruiters | API |
| World Bank | CSOD | API + browser |
| ECB | Workday | API |
| ICRC | Custom | RSS + browser |
| IOM | Oracle Cloud | Browser |
| COE Talents | Custom | Browser (JS pagination) |
| IMF | Workday | API |
| NATO | Workday | API |
| ESA | Workday | API |
| CGIAR | Workable | API |
| Impactpool | Custom | Scrapling |
| UNJobNet | Custom | Scrapling |
| UNTalent | Custom | Scrapling |

## Extraction Methods by Platform

| Platform | Extraction Method |
|----------|------------------|
| **Taleo** | RSS feed or `article.innerText` via browser |
| **Workday** | API JSON or `body.innerText` via browser |
| **SuccessFactors** | API JSON (paginated) |
| **Oracle Cloud** | `body.innerText` via browser |
| **SmartRecruiters** | API JSON |
| **CSOD (Cornerstone)** | API JSON |
| **Custom/Other** | SearXNG discovery + browser fallback |

## Token Optimization

The `web-preclean.py` script uses `trafilatura` to strip HTML boilerplate before feeding JD content to LLMs, achieving 94-95% token reduction while preserving job description text.

## Scoring

Vacancies are scored using a 7-parameter compatibility engine:
1. Domain alignment (telecom/AI/ICT/digital transformation)
2. Seniority match
3. Technical skill overlap
4. Language requirements
5. Location/remote eligibility
6. Education equivalence
7. Transferable skills bridge

Scores are domain-capped: ICT/AI max 22pts, data 16pts, finance 16pts, management 14pts, SWE 8pts, GIS 10pts.

## Setup

```bash
# Install dependencies
pip install trafilatura scrapling playwright httpx

# Set up environment
cp .env.example .env  # Fill in your config

# Run a single agency scan
python scripts/agency-scan/run_who.py

# Run broad scan across all portals
python scripts/run_broad_scan.py

# Pre-clean scraped JDs for token-optimized scoring
python scripts/web-preclean.py
```

## License

MIT — see [LICENSE](LICENSE)
