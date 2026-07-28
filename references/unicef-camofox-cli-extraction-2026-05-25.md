# UNICEF Extraction via Camofox CLI (2026-05-25)

## Key finding: npm Camofox CLI works on UNICEF

The camoufox-browser skill lists UNICEF as "❌ Crashes (Internal Server Error)".
This is true for `browser_type` via Hermes browser tools, but the **Camofox CLI**
(`camofox open` + `camofox get-text`) works correctly on UNICEF via the npm
server on port 9377.

## Working pattern

```bash
# Open search page
camofox open "https://jobs.unicef.org/en-us/search/?search-keyword=digital" --format json
sleep 8
# Get page text (returns JSON-escaped string with \\n line separators)
camofox get-text --format json > /tmp/unicef_digital_raw.txt
```

Repeat for all 3 keywords: digital, AI, ICT.

## Parsing the output

`camofox get-text` returns a JSON-quoted string. Parse with:
```python
import json
text = json.loads(open('/tmp/unicef_digital_raw.txt').read())
# text now has \\n as line separators and \\" for quotes
```

Job entries have this structure:
```
Job Title With #ID, Location
\n Description text...
\n Location: City, Country
\n Deadline: DD Month YYYY 11:55 PM
```

## Extraction regex

```python
# Find all Location: / Deadline: pairs
locs = re.findall(r'Location:\s*([^\\]+)', text)
dls = re.findall(r'Deadline:\s*(\d{1,2}\s+\w+\s+\d{4})', text)

# Parse deadline to ISO
from datetime import datetime
dl_iso = datetime.strptime(dl_raw, '%d %B %Y').strftime('%Y-%m-%d')
```

## Keywords

| Keyword | Results | Notes |
|---------|---------|-------|
| digital | ~40 | Most productive |
| AI | ~12 | AI Applications Developer, Evaluation Specialist (AI/ML) |
| ICT | ~8 | ICT Policy consultant, Operations (ICT context) |

## Job IDs

UNICEF uses 5-8 digit numeric IDs: #00043597, #593037, Req#593155, Job No #589439.
Construct detail URL: `https://jobs.unicef.org/en-us/job/{vid_num}/`
