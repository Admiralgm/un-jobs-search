# Token Optimization Protocol v1.0 — UN Job Scraping

## Decision Tree

```
User gives URL
     │
     ▼
Probe HEAD request → 200 OK?
     │ YES              │ NO (403)
     ▼                  ▼
web-clean.py       browser_navigate
+ grep filter      (Playwright)
     │                  │
     ▼                  ▼
Extract fields     Still 403?
only (title,       → ESCALATE
deadline, grade,     (Impactpool proxy
location, etc.)      ONLY, then verify
                  on official portal)
```

## Hard Token Limits

| Task Type | char_limit | Approx Tokens |
|-----------|-----------|---------------|
| Quick field lookup | 2,000 | ~500 |
| Single job read | 6,000 | ~1,500 |
| Search results | 8,000 | ~2,000 |
| Deep extraction | 15,000 | ~3,750 |

Default is always 6,000. Never exceed 15,000.

## What NEVER to Use

- **`web_extract` / `web_extract_plus`** — sends raw HTML to LLM, burns 50K-180K tokens/page
- **`write_file`** — silently fails, produces 0-byte files
- **`patch` on tracker file** — corrupts multiline inserts
- **Impactpool as primary source** — unreliable aggregator

## web-clean.py Usage

```bash
# Standard job page read (default 40k chars)
python3 config/scripts/web-clean.py URL

# Strict: 6k chars for minimal token use (DEFAULT for job scanning)
python3 config/scripts/web-clean.py URL 6000

# Targeted: extract only relevant fields
python3 config/scripts/web-clean.py URL 6000 | grep -i -E "(title|deadline|grade|location|contract|salary)"

# Pipe to file for inspection
python3 config/scripts/web-clean.py URL > /tmp/job.txt
```

## Benchmark

- Raw HTML: 722,471 bytes (~180,000 tokens)
- Clean text: 41,007 bytes (~10,000 tokens)
- **Reduction: ~94%**
