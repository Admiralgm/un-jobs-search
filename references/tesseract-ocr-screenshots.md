# Tesseract OCR — Screenshot Text Extraction

## When to Use
When browser_navigate renders content but the accessibility tree doesn't capture it,
or when vision_analyze is unavailable (non-vision models like owl-alpha).

## Installation
Pre-installed on this system:
- Binary: /usr/local/bin/tesseract
- Version: 5.5.2
- Languages: eng (English), osd (orientation detection), snum (numbers)

## Workflow
1. Navigate to page: `browser_navigate(url)`
2. Screenshot auto-captured at: `config/cache/screenshots/browser_screenshot_*.png`
3. Run OCR:
```bash
tesseract /path/to/screenshot.png /tmp/ocr_output --psm 6
cat /tmp/ocr_output.txt
```
4. Parse extracted text for job titles, locations, deadlines

## PSM Modes
- `--psm 6`: Assume uniform block of text (best for job listings)
- `--psm 3`: Fully automatic page segmentation
- `--psm 4`: Assume single column of variable text

## Confirmed Working (2026-05-18)
- World Bank CSOD screenshot (494KB PNG) → extracted 24+ job listings including
  Digital Program Analyst, Product Owner, Programming Specialist

## Limitations
- Current model (owl-alpha) does NOT support vision/image input
- `vision_analyze` and `browser_vision` fail with 404 on non-vision models
- Tesseract is the only OCR option without vision model
- Accuracy depends on screenshot quality and text size
- May miss structured data (tables) that Scrapling captures perfectly

## Recommendation
Use Scrapling StealthyFetcher as primary tool for JS-rendered SPAs.
Use Tesseract OCR as fallback when Scrapling is unavailable or for
quick extraction from existing screenshots.
