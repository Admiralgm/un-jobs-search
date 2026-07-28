# File Reformatting Guide

For the complete file reformatting procedure, see the main `un-jobs-search` skill's reference:
`skills/research/un-jobs-search/references/file-reformatting.md`

The procedure is identical for both skills. Key points:

- Always backup first (`cp` with date suffix)
- Parse entries from `- Title:` to next `- Title:` (not by SEP lines)
- Break on SEP lines and orphaned colored headers when parsing OLD format files
- Output in canonical format: `SEP + blank + colored header + blank + SEP + fields + analysis + advice + verdict`
- Write with `execute_code` Python `Path().write_text()` + `sync`
- Verify: `wc -l` + `grep -c '^- Title:'` matching table row count
