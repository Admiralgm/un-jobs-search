# Script Location & Symlink Fix — 2026-06-25

## Problem
The `scripts/` directory under `skills/research/un-jobs-search/` is a **self-referencing symlink**:

```
scripts -> skills/research/un-jobs-search/scripts
```

This causes `[Errno 62] Too many levels of symbolic links` when trying to run scripts from that path.

## Actual Script Location
All per-agency scraper scripts live at:

```
skills/experiments/new-jobs-search/scripts/
```

## How to Run Scripts
Use the full path to the experiments directory:

```bash
uv run python3 skills/experiments/new-jobs-search/scripts/run_{portal}.py
```

## Output Directory
All scripts hardcode their output to `~/Downloads/TEST/` (not the workdir). This directory must exist before running:

```bash
mkdir -p ~/Downloads/TEST/UN_WHO ~/Downloads/TEST/UN_ITU
```

## Scripts Available
- run_who.py — WHO Taleo
- run_itu_v4.py — ITU SuccessFactors (Camoufox)
- run_unicef.py — UNICEF PageUp
- run_iaea.py — IAEA Taleo
- run_icao_v3.py — ICAO
- run_icmpd_v3.py — ICMPD
- run_icrc_v2.py — ICRC
- run_ifad.py — IFAD
- run_ilo_v3.py — ILO
- run_imo.py — IMO
- run_inspira_v4.py — UN Secretariat INSPIRA
- run_oecd_v4.py — OECD
- run_undp_v4.py — UNDP
- run_unesco_v4.py — UNESCO
- run_unfpa_v4.py — UNFPA
- run_unhcr.py — UNHCR
- run_unido.py — UNIDO
- run_unitar_v4.py — UNITAR
- run_unops_v3.py — UNOPS
- run_unu.py — UNU
- run_wipo.py — WIPO
- run_wmo.py — WMO
- run_workday.py — WFP/IMF/UNHCR (Workday)
- run_worldbank.py — World Bank
- run_ecb.py — ECB
- run_fao.py — FAO
