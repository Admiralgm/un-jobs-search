# INSPIRA Extraction Patterns (Updated 2026-05-26)

## Listing Page — Extract Job IDs via JS

After navigating to a keyword search results page on `careers.un.org/jobopening`:

```javascript
// Extract all 6-digit job IDs from listing page
(function() {
  const links = Array.from(document.querySelectorAll('a[href*="jobSearchDescription"]'));
  const ids = links.map(a => {
    const m = (a.href || '').match(/jobSearchDescription\/(\d{6})/);
    return m ? m[1] : '';
  }).filter(v => v);
  return [...new Unique(ids)]; // deduplicated
})()
```

This returns an array of unique 6-digit IDs like `["278250", "278246", ...]`.

**Note:** The listing page shows ~10 results per page. Navigate through pages if more exist.

## Detail Page — Extract Job Data via JS

After navigating to `careers.un.org/jobSearchDescription/{6-digit-id}?language=en`:

```javascript
(function() {
  const text = document.body.innerText;
  const title = document.querySelector('h1')?.innerText?.trim() || '';
  const orgMatch = text.match(/Department\/Office : (.+?)[\s\n]/);
  const gradeMatch = text.match(/Category and Level : (.+?)[\s\n]/);
  const locMatch = text.match(/Duty Station : (.+?)[\s\n]/);
  const dlMatch = text.match(/Deadline : (.+?)[\s\n]/);
  const idMatch = text.match(/Job Opening ID: (\d+)/);
  
  return {
    vid: idMatch?.[1] || '',
    title,
    org: orgMatch?.[1]?.trim() || '',
    grade: gradeMatch?.[1]?.trim() || '',
    location: locMatch?.[1]?.trim() || '',
    deadline: dlMatch?.[1]?.trim() || ''
  };
})()
```

### Detail Page Text Format

```
Job Opening ID: 277213
Job Network : -
Job Family : Information Management Systems and Technology
Category and Level : Consultants, CON
Duty Station : BEIRUT
Department/Office : Economic and Social Commission for Western Asia
Date Posted : May 6, 2026
Deadline : Jun 2, 2026
```

## Keyword Search Results Yield (2026-05-26)

| Keyword | Results | Notes |
|---------|---------|-------|
| Information Technology | ~10 | Mix of CON, P-level, Intern |
| Digital | ~10 | Mix of CON, P-level |
| Artificial Intelligence | 3 | All CON level |
| ICT | 1 | Single result |
| Telecom | 0-1 | Rare |

**Total unique IDs per full scan:** ~25-30

## Batch Fetch Strategy

1. Search each keyword, collect IDs via JS
2. Deduplicate IDs across searches
3. Filter out IDs already in tracker index
4. Fetch detail pages for remaining IDs (navigate → JS extract)
5. Score and add if ≥ 55

**Throughput:** ~10-15 seconds per detail page. Batch of 25 IDs ≈ 4-6 minutes.

## Common Job Patterns on INSPIRA (2026-05-26)

- **ESCWA AI/ICT consultants:** Many CON-level roles for AI strategy, data protection, digital transformation — Beirut-based. Good ICT match but CON grade limits seniority score.
- **P-level ICT officers:** Rare but appear (P-2, P-3) — typically at duty stations like Cox's Bazar, Panama City.
- **Intern positions:** Filter out (I-1 grade).
- **ESCWA = Economic and Social Commission for Western Asia** — most common org for ICT/AI roles.
