# UNICEF Job Detail Page Extraction — Lessons 2026-05-30

## Task
Extract full job details for top N scored UNICEF vacancies, saving one markdown file per vacancy.

## Method (Confirmed Working)

For each job URL:

1. `browser_navigate(url)` — Navigate to `jobs.unicef.org/en-us/job/{id}/...`
2. Wait for page load (snapshot confirms content via `ARTICLE.page` heading)
3. `browser_console(expression="(function(){const article=document.querySelector('ARTICLE.page');return article?article.innerText:document.body.innerText;})()")` — Extracts full text
4. **IMMEDIATELY** `write_file()` the extracted content as markdown
5. Move to next URL

## Critical Rules

- **SAVE IMMEDIATELY**: Write each file right after extraction. Never accumulate 3+ files in memory before writing. Context window is the limiting factor.
- **DON'T CHANGE METHOD**: If `browser_navigate` + `browser_console` works, use it for ALL remaining jobs. Do not try to batch, parallelize, or switch approaches mid-stream.
- **Selector**: `document.querySelector('ARTICLE.page').innerText` — NOT `main article`, NOT `.job-detail`, NOT `body.innerText`
- **Context management**: Save `_PROGRESS.md` tracker after every 5-10 jobs.

## requests+BS4 Approach (Blocked After ~6 Requests)

UNICEF site returns CAPTCHA/JS verification after ~6 requests. Files are either:
- **Good** (14-17KB): Successfully extracted
- **Blocked** (~500 bytes): "JavaScript is disabled / verify you're not a robot"

**Quality check**: Files <1KB need browser re-fetch. Files named `*_Vacancies.md` are duplicates from a script bug — delete them.

## camoufox Restart Procedure

When `browser_navigate` fails with stale tab UUID:
1. `terminal(background=true, command="/usr/local/bin/camofox server start")`
2. Wait 5 seconds
3. Resume from `_PROGRESS.md`

## Subagent Parallelization (BLOCKED)

`delegate_task` ignores `model:` field — all subagents route to Ring-2.6-1T (no longer free).
Tried: minimax-m2.5:free, kimi-k2.6:free, deepseek-v4-flash:free — all HTTP 404.

**Workaround**: User manually assigns batches to separate agent sessions.
Provide each: batch JSON, output directory, save-immediately instructions.

## Results This Session

- 22 high-quality browser-extracted files (top scored jobs)
- 178 Python-scripted: 6 ok, 156 CAPTCHA-blocked, 16 skipped
- ~156 jobs still need browser re-extraction
- Batches: `/tmp/batch_1.json` (52), `/tmp/batch_2.json` (52), `/tmp/batch_3.json` (52)

## Performance

- Browser: ~30-45s per job. User prefers this ("NON NONONO I WANT FULL DETAILS")
- Python: ~3s per job but blocks after ~6 requests — NOT viable for bulk
- User wants save-immediate pattern, not batch accumulation
