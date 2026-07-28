# SearXNG INSPIRA Deadline Extraction

## When to use
Camoufox is down (`browserConnected: false` after restart), and you need to check whether INSPIRA (careers.un.org) job IDs are still open before committing a browser restart cycle.

## How it works
SearXNG caches snippets from careers.un.org job description pages. The snippet HTML often contains the deadline date even when the JS-rendered page is inaccessible.

## Query pattern
```bash
curl -s "http://localhost:8888/search?q=site:careers.un.org+<job_id>+deadline&format=json" | \
python3 -c "
import json,sys,re
d=json.load(sys.stdin)
for r in d.get('results',[]):
    content = r.get('content','')
    dl = re.search(r'Deadline\s*:\s*([^,]+)', content)
    title = r.get('title','')
    if dl:
        print(f'{title[:80]} | Deadline: {dl.group(1)}')
    else:
        # Fallback: look for date patterns
        dates = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}', content)
        if dates:
            print(f'{title[:80]} | Dates: {dates[0]}')
"
```

## Example
Query `278542 deadline` returns:
```
Deadline: Jul 22
Title: chief of section, information systems and telecommunications, p5
```

## When it fails
- If the job is too new (not yet indexed by SearXNG)
- If the cached snippet doesn't include the deadline metadata
- Fall back to: Camoufox restart cycle + `browser_navigate` to the job page