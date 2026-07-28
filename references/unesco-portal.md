# UNESCO/SuccessFactors Portal Guide

## Access Pattern
- **URL**: `https://careers.unesco.org/go/All-jobs-openings/784002/`
- **Keyword Search**:
  - Input field: `input[title="Search by Keyword"]`
  - Button: `button:contains("Search Jobs")` or typically the button right after the input.
- **Result Table**:
  - Located within a `table` with summary "Search results for...".
  - Rows are `<tr>`.
  - Links are inside `class="jobTitle-link"` or similar.

## Data Points Extraction
- **Job ID (Actual ID)**: Extract using regex from the `href` attribute (e.g., `1359193257`).
- **Grade**: Extracted from `tr.cells[3]`.
- **Deadline**: Extracted from `tr.cells[4]`. Format: `DD/MM/YYYY`. Convert to `YYYY-MM-DD`.

## browser_console Extraction Snippet
```javascript
Array.from(document.querySelectorAll('tr')).slice(2).map(tr => {
    const link = tr.querySelector('a')?.href;
    const actualId = link ? link.split('/').filter(p => p.match(/^\d+$/))[0] : null;
    return {
        title: tr.querySelector('a')?.innerText,
        vacancyId: actualId,
        link: link,
        location: tr.cells[1]?.innerText,
        grade: tr.cells[3]?.innerText,
        deadline: tr.cells[4]?.innerText
    };
}).filter(j => j.title)
```
