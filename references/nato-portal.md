# NATO Vacancy Extraction Guide

NATO jobs are high-priority for this user (G17/G20 grades).

## Search Strategy
Impactpool is often better than the official NATO Talent Acquisition platform for initial discovery as it bypasses complex session filters.

- **URL**: `https://www.impactpool.org/search?q=NATO+digital+ICT+AI`
- **Seniority Filter**: Add `G17` or `G20` to the search query to isolate executive roles.

## Extraction Patterns

### Job Listing Level
Use `browser_console` to extract senior roles:
```javascript
Array.from(document.querySelectorAll('a[href*="/jobs/"]'))
  .filter(a => /G15|G17|G20/.test(a.innerText))
  .map(a => ({
    text: a.innerText,
    url: a.href,
    id: a.href.split('/').pop()
  }));
```

### Job Detail Level
- **Vacancy ID**: NATO often puts the ID in the title (e.g., "ICT Engineer (800345)"). If not present, use the Impactpool numeric ID.
- **Grades**: 
  - G20: D-2 equivalent (Director)
  - G17: D-1/P-5 equivalent (Staff Officer/Head)
  - G15: P-4 equivalent
- **Location**: Principally Mons (SHAPE), Brussels (HQ), or The Hague (NCIA).

## Pitfalls
- **Closing Soon**: NATO deadlines on Impactpool are usually accurate, but check the "Application deadline:" text on the detail page as it has a high-visibility red highlight.
- **Nationality Requirement**: Most NATO roles require "Open to citizens of a NATO country". User (Serbian/Czech dual or dual eligibility) fits most criteria.
