# Impactpool Extraction Patterns

## Broad Search + Console Filter (Primary Pattern)

Impactpool's `&org=` URL parameter does NOT filter by organization. Use this two-step pattern instead:

### Step 1: Navigate to broad search
```
https://www.impactpool.org/search?q=ICT+OR+digital+OR+AI+OR+technology+OR+information
```
This returns 200-700 results from all organizations.

### Step 2: Extract specific org's jobs via browser_console
```javascript
Array.from(document.querySelectorAll('a[href*="/jobs/"]'))
  .filter(a => a.textContent.includes('UNFPA') || a.textContent.includes('UNEP'))
  .map(a => ({href: a.href, text: a.textContent.trim().substring(0,150)}))
```

### Step 3: Navigate to detail page
Each job detail page at `https://www.impactpool.org/jobs/XXXXXX` contains:
- Full title, org, grade, location
- Application deadline (e.g., "Application deadline: May 20, 2026 (9 days)")
- Full job description and requirements
- Direct "Apply" link to the hiring org's portal

## Finding Specific Roles

For roles identified from aggregator listings, use a quoted search:
```
https://www.impactpool.org/search?q=%22Chief%2C+Data+and+Analytics+Branch%22+UNFPA
```

## Job ID Extraction

The numeric ID in the Impactpool URL (e.g., `1211592` from `/jobs/1211592`) serves as the VACANCY ID when no official job number is found on the detail page.

## Org-Specific Notes

- **UNHCR**: Often zero senior ICT/AI roles per cycle. Workday is primary source.
- **WFP**: Often only junior/national digital roles per cycle.
- **UNICEF**: Uses `#XXXXXX` format in title as official Job ID (e.g., `#00133283`).
- **UNFPA**: D-1 and P-5 roles appear regularly. Check Programme Division.
- **UNEP**: Chief Digital Office (CDO) roles are strong matches for digital transformation.
- **UNDP**: Uses tiered applications (Tier 0/1/2/3). Note tier in analysis. NPSA = national consultancy.
