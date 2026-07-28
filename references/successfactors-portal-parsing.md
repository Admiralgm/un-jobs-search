# SuccessFactors Portal Parsing Guide

## Pattern: SuccessFactors (SAP) Job Listing Pages

SuccessFactors portals (ICRC, UNESCO, and others) share a common HTML structure that requires specific parsing approaches.

### Key Characteristics

1. **Each job appears 3x in the HTML** — SuccessFactors renders every job listing 3 times for accessibility. Deduplicate by `title + deadline` tuple.

2. **No clickable links in cleaned output** — trafilatura/web-preclean.py strips markdown links. Job titles appear as plain text.

3. **Concatenated field labels without newlines** — Fields appear on one line:
   `Title FORENSIC DELEGATE Country Global Deployment...`

4. **Field extraction pattern** (Python):
   ```python
   chunks = text.split('Title ')[1:]  # skip preamble
   for chunk in chunks:
       title_end = chunk.find(' Country ')
       title = chunk[:title_end].strip()
       rest = chunk[title_end:]
       country_m = re.search(r'Country\s+(.+?)\s+Location\s+', rest)
       location_m = re.search(r'Location\s+(.+?)\s+Job category\s+', rest)
       category_m = re.search(r'Job category\s+(.+?)\s+Contract type\s+', rest)
       contract_m = re.search(r'Contract type\s+(.+?)\s+Application deadline\s+', rest)
       deadline_m = re.search(r'Application deadline\s+(\d{2}/\d{2}/\d{4})', rest)
       dedup_key = f"{title}|{deadline_m.group(1)}"
   ```

5. **RSS feed available** — `https://careers.<org>.org/services/rss/category/?catid=<id>` — 10 most recent jobs, clean XML. Use web-preclean for full listing.

6. **Pagination** — JS-driven. `?jobOffset=25` often returns same page. Use browser_navigate for multi-page.

### ICRC-Specific Nationality Rules

- **Belgrade Hub roles**: Serbian-nationals-only → User IS eligible. Include.
- **Manila roles**: Philippine-residents-only → EXCLUDE
- **Kyiv roles**: Ukrainian-nationals-only → EXCLUDE
- **Geneva roles**: Usually international → include
- **Always check detail page** for citizenship text. "Resident" type = nationality restriction likely.

### ICRC Grade Context

- B3 ≈ P-3, C1 ≈ P-2 (below User's level)
- Ungraded senior roles likely P-4/P-5 equivalent
- ICRC does not always show grade on listing; check detail page
