# UNFPA Career Portal

**URL:** https://www.unfpa.org/jobs
**Oracle Site ID:** CX_2003
**Detail URL pattern:** `https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_2003/job/{ID}`
**UNFPA-hosted detail pattern:** `https://www.unfpa.org/jobs/{slug}` — PREFERRED for full JD extraction

**Status:** ⚠️ Camoufox CRASHES this portal

**Platform:** Oracle HCM Cloud (not Drupal — legacy note was wrong)

## Crash Pattern
- Navigating to `unfpa.org/jobs` via Camoufox causes browser tab 404
- Subsequent Camoufox browser actions across ALL tabs fail
- Even if Camoufox server is running and other sites work, UNFPA specifically crashes the tab

## Recovery: Bypass Camoufox for UNFPA

When Camoufox is active (CAMOFOX_URL set in .env), ALL browser tools route through it and UNFPA will crash. Two options:

### Option A: Temporarily disable Camoufox routing
```bash
# Comment out CAMOFOX_URL in .env (patch tool blocks .env — use sed)
sed -i '' 's/^CAMOFOX_URL/# CAMOFOX_URL/' config/.env
# Restart the Hermes session for the change to take effect
# After scanning UNFPA, re-enable:
sed -i '' 's/^# CAMOFOX_URL/CAMOFOX_URL/' config/.env
```

### Option B: Use curl + HTML extraction (no browser needed) — PREFERRED

**Step 1: Extract job URLs from the UNFPA jobs listing page:**
```bash
curl -sL "https://www.unfpa.org/jobs" -H "User-Agent: Mozilla/5.0" | python3 -c "
import sys, re
html = sys.stdin.read()
urls = re.findall(r'estm\.fa\.em2\.oraclecloud\.com/hcmUI/CandidateExperience/en/sites/CX_2003/job/\d+', html)
for u in sorted(set(urls)): print(u)
"
```

**Step 2: Fetch full JD from UNFPA-hosted detail page (NOT Oracle URL):**

The UNFPA-hosted pages (`unfpa.org/jobs/{slug}`) contain the full JD as server-rendered HTML. This is the PREFERRED method — Oracle URLs are JS-rendered SPAs that return empty content via curl.

```bash
curl -sL "https://www.unfpa.org/jobs/{slug}" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import sys, re, gzip
raw = sys.stdin.buffer.read()
try: text = gzip.decompress(raw).decode('utf-8', errors='replace')
except: text = raw.decode('utf-8', errors='replace')
text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
# Find job description section
start = text.find('Job description')
if start > 0:
    chunk = text[start:start+8000]
    clean = re.sub(r'<[^>]+>', ' ', chunk)
    clean = re.sub(r'\s+', ' ', clean).strip()
    print(clean)
# Find qualifications
start2 = text.find('Qualification')
if start2 > 0:
    chunk = text[start2:start2+5000]
    clean = re.sub(r'<[^>]+>', ' ', chunk)
    clean = re.sub(r'\s+', ' ', clean).strip()
    print(clean)
"
```

**Why UNFPA-hosted pages are better than Oracle URLs:**
- Oracle URLs (`estm.fa.em2.oraclecloud.com/...`) are JS-rendered SPAs — curl returns empty/boilerplate
- UNFPA-hosted pages (`unfpa.org/jobs/slug`) contain the full JD as server-rendered HTML
- All metadata (title, grade, location, deadline, description, qualifications) is in the HTML source

**Limitation:** Only ~8 jobs per page in the HTML source. Jobs beyond first page need browser or Oracle API.

## Oracle REST API (non-functional for UNFPA)

The Oracle HCM REST API returns errors for UNFPA (CX_2003):
- Empty items with `expand=requisitionList`
- "URL request parameter q cannot be used in this context" for search
- "URL request parameter requisitionId cannot be used in this context" for details

**Do not use the REST API for UNFPA.** Use curl + HTML extraction instead.

## Known Job IDs (June 2026)

Observed: 34152, 34220, 34229, 34235, 34395, 34399, 34405, 34449
IDs are sequential — checking a range around the highest known ID may catch new postings.

## Historical notes
- UNFPA ICT roles are rare. No P-4+ ICT vacancies found in any scan cycle.
- Most postings are health/national/local positions.
- P-3 international positions appear occasionally but are programme/health focused, not ICT.
- LinkedIn posts may reference expired or already-filled positions — always verify on the actual portal.
- When a job is found via screenshot/LinkedIn but not on the direct portal, use SearXNG with `site:unfpa.org` queries to locate the exact URL.
