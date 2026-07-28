# Table Parsing and Rebuild Pitfalls — Updated 2026-06-06

## CRITICAL: Row Parsing Regex Must Handle Both 6 and 7 Column Formats

**Problem**: Some rows in the tracker file have 6 tab-separated fields, others have 7. The original parser used `len(parts) >= 7` which silently dropped rows with only 6 fields (where the Applied column was missing or merged).

**Fix**: Always use `len(parts) >= 6` for row parsing:

```python
# CORRECT
parts = re.split(r'\s{2,}', line.strip())
if len(parts) >= 6:
    num = int(parts[0])
    org = parts[1].strip()
    title = parts[2].strip()
    deadline = parts[3].strip()
    score = parts[4].strip()
    vid = parts[5].strip()
    applied = parts[6].strip() if len(parts) >= 7 else 'NO'
```

**Root cause**: When the file is written with `r['applied']` always present, all rows should have 7 fields. But if any row is hand-edited or corrupted, it may have only 6. The parser must be defensive.

## Row Count Mismatch After Write

**Symptom**: After writing, `len(verify_rows)` shows fewer rows than `len(rows)`.

**Cause**: The regex `re.split(r'\s{2,}', line.strip())` can produce different column counts depending on the spacing in the title field. Titles with multiple consecutive spaces may split into more or fewer parts.

**Debugging**: Always print both counts after write:
```python
print(f"Written {len(rows)} rows, verified {len(verify_rows)} rows")
if len(verify_rows) < len(rows):
    # Find which rows were dropped
    for r in rows:
        found = any(r['vid'] in vr for vr in verify_rows)
        if not found:
            print(f"DROPPED: {r['vid']} | {r['title'][:50]}")
```

## Emoji Column Shifts Fixed-Width Parsing

**Problem**: The 🟢🟠🔴 emoji in the Score column occupies 2 visual columns but takes 2+ Unicode code points. Positional slicing (e.g., `line[87:97]`) produces misaligned results.

**Fix**: Always use `re.split(r'\s{2,}', line)` or field-count-based parsing, NEVER fixed-width character indices.

## Camoufox Tab Context Switching

**Problem**: `browser_console` runs JavaScript in the CURRENT active tab. If you navigate to a new tab (e.g., IAEA), then try to extract data from a different tab's page (e.g., WHO), the JS runs on the wrong page.

**Fix**: Always navigate to the page FIRST, then immediately run the console extraction before navigating elsewhere.

## ITU Date Format

ITU SuccessFactors displays deadlines as "Jun 5, 2026" not "YYYY-MM-DD". Handle both formats:
```python
for fmt in ['%Y-%m-%d', '%b %d, %Y', '%d/%m/%Y']:
    try:
        d = datetime.strptime(dl, fmt).date()
        break
    except:
        pass
```

## File Write Verification Checklist

After EVERY write to UN_SECTOR_VACCANCIES.txt:
1. `sync` in terminal
2. Count rows: `grep -c "^[0-9]" file.txt`
3. Verify row count matches expected (existing + new - expired)
4. Check first and last rows are correct
5. Verify new entries appear in the file
6. Check no duplicate VIDs exist
