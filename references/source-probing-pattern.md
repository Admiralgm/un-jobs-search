# Source Probing Pattern

## Systematic Site Accessibility Check

Before classifying a site as "blocked", run this probe sequence:

### Step 1: HEAD Request (5 seconds)
```bash
python3 -c "
import requests
r = requests.head('URL', headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, allow_redirects=True)
cf = 'CF' if r.headers.get('cf-ray') else 'NO-CF'
print(r.status_code, cf, r.url)
"
```

### Step 2: GET Request with web-clean.py (10 seconds)
```bash
python3 config/scripts/web-clean.py URL 3000
```
If returns content with job keywords → ACCESSIBLE via web-clean.py

### Step 3: browser_navigate (15 seconds)
If Steps 1-2 fail or return empty:
```
browser_navigate: URL
browser_console: document.body.innerText.substring(0, 2000)
```

### Step 4: Try Alternative URLs
If all above fail, the site may have moved. Try:
- Different path (e.g., /careers → /jobs → /employment)
- Different subdomain (e.g., careers.org.org → jobs.org.org → talents.org.org)
- Workday platform: *.wd<number>.myworkdayjobs.com
- Taleo platform: *.taleo.net/careersection
- SuccessFactors: *.successfactors.com
- Oracle Cloud: *.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience

### Step 4b: Alternate Subdomain Pattern (NEW — May 2026)
When the main agency domain is blocked (Cloudflare/403), try common career subdomains:
- `talents.{agency}.int` — used by COE (talents.coe.int)
- `careers.{agency}.org` / `careers.{agency}.int` — used by WHO (careers.who.int)
- `jobs.{agency}.org` — used by UNICEF, UNDP, ITU
- `{agency}.taleo.net` — used by WHO, IAEA
- `{agency}.wd{N}.myworkdayjobs.com` — used by UNHCR
- `fa-{hash}.fa.ocs.oraclecloud.com` — used by IOM (Oracle Cloud hash varies)

Pattern: if `agency.org/careers` is blocked, probe `talents.agency.org`, `careers.agency.org`, `jobs.agency.org` before giving up.

## Classification Decision Tree

```
HEAD returns 200?
  ├─ YES → GET returns job content?
  │   ├─ YES → ACCESSIBLE (web-clean.py)
  │   └─ NO → JS-rendered? → browser_navigate
  └─ NO → 404?
      ├─ YES → Try alternative URLs → Still 404? → MOVED/404
      └─ NO → 403/CF?
          ├─ YES → browser_navigate works?
          │   ├─ YES → ACCESSIBLE (browser only)
          │   └─ NO → BLOCKED (manual only)
          └─ NO → ERR → Try alternative URLs
```

## Key Insight: Sites Move

Many UN agencies have migrated to new platforms. Always try the actual job board URL:

| Agency | Old URL (broken) | New URL (working) |
|--------|-------------------|-------------------|
| UNHCR | unhcr.org/careers (CF block) | unhcr.wd3.myworkdayjobs.com/en-GB/External |
| WHO | who.int/careers (landing page only) | careers.who.int/careersection/ex/jobsearch.ftl |
| World Bank | worldbank.org/en/about/careers (redirect) | worldbank.org/ext/en/careers |
| IMF | imf.org/en/careers (403) | imf.org/en/about/recruitment |
| IAEA | iaea.org/careers (CF block) | iaea.taleo.net/careersection/ex/jobsearch.ftl |
| IOM | iom.int/careers (bot detection) | fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs |
| COE | coe.int/jobs (CF block) | talents.coe.int/en_GB/careersmarketplace/SearchJobs |

Always try the actual job board URL, not just the /careers landing page.

## Login Not Required for Search

Most UN job portals (WHO Taleo, UNHCR Workday, etc.) allow full job search and viewing without login. Login is only required to apply. When probing a new portal:
1. Try searching without logging in first
2. If credentials are provided but fail with "user does not exist", the account needs to be created separately on that platform
3. Do NOT assume WHO/UN credentials work on Taleo/Workday — they are separate systems
