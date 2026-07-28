#!/usr/bin/env python3
"""
web-preclean.py — HTML-to-Markdown pre-processor for web_extract pipeline.

Fetches raw HTML from a URL, strips ALL boilerplate (scripts, styles, nav,
footers, headers, inline CSS, JavaScript, base64 images, SVGs, comments),
extracts the main article content using trafilatura, and converts it to
clean, lightweight Markdown using html2text.

This is the PREPROCESSING step that runs BEFORE content reaches the LLM.
It reduces token usage by 90-95% compared to raw HTML.

Usage:
    python3 web-preclean.py <URL> [max_chars]

    max_chars: hard output limit (default: 40000)

Output:
    Clean Markdown text to stdout.

Exit codes:
    0 = success
    1 = usage error
    2 = fetch failed
    3 = extraction failed (empty result)
"""

import sys
import os
import re
import html as html_module

try:
    import requests
except ImportError:
    requests = None

# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch_url(url: str) -> str:
    """Fetch raw HTML from URL with a browser User-Agent."""
    if requests:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        r.raise_for_status()
        return r.text
    else:
        import subprocess
        result = subprocess.run(
            ["curl", "-sL", "-A",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/124.0.0.0 Safari/537.36",
             url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise RuntimeError(f"curl failed with exit code {result.returncode}")
        return result.stdout


# ---------------------------------------------------------------------------
# Step 1: Trafilatura extraction (primary — best quality)
# ---------------------------------------------------------------------------

def extract_with_trafilatura(raw_html: str) -> str | None:
    """
    Use trafilatura to extract main article content and convert to Markdown.
    Returns Markdown string or None if extraction fails / produces empty output.
    """
    try:
        import trafilatura
    except ImportError:
        return None

    result = trafilatura.extract(
        raw_html,
        output_format="markdown",
        include_comments=False,
        include_tables=True,
        include_images=False,       # skip base64 images
        include_links=True,         # keep hyperlinks
        include_formatting=True,    # preserve bold/italic/etc.
        favor_recall=True,          # favor recall — get more content
        deduplicate=False,
    )
    if result and result.strip():
        return result.strip()
    return None


# ---------------------------------------------------------------------------
# Step 2: html2text fallback (if trafilatura unavailable or fails)
# ---------------------------------------------------------------------------

def extract_with_html2text(raw_html: str) -> str | None:
    """
    Use html2text to convert HTML to Markdown.
    First strips script/style/nav/footer/SVG/comment tags via regex.
    Returns Markdown string or None on failure.
    """
    try:
        import html2text
    except ImportError:
        return None

    cleaned = _strip_boilerplate_tags(raw_html)

    h = html2text.HTML2Text()
    h.body_width = 0          # don't wrap — preserve original line breaks
    h.ignore_links = False
    h.ignore_images = True     # skip images (including base64)
    h.ignore_emphasis = False
    h.skip_internal_links = True
    h.inline_links = True
    h.protect_links = True
    h.wrap_links = False
    h.unicode_snob = True
    h.mark_code = True
    h.default_image_alt = ""
    h.images_to_alt = True
    h.images_with_size = False
    h.drop_white_space = False

    result = h.handle(cleaned)
    result = result.strip()
    if result:
        return result
    return None


# ---------------------------------------------------------------------------
# Step 3: BeautifulSoup brute-force fallback (last resort)
# ---------------------------------------------------------------------------

def extract_with_bs4(raw_html: str) -> str | None:
    """
    Last-resort extraction using BeautifulSoup.
    Removes script, style, nav, footer, header, aside, svg, noscript, iframe,
    then gets text and converts basic structure to Markdown-like output.
    """
    try:
        from bs4 import BeautifulSoup, Comment
    except ImportError:
        return None

    soup = BeautifulSoup(raw_html, "html.parser")

    for tag_name in ("script", "style", "nav", "footer", "header", "aside",
                     "svg", "noscript", "iframe", "form", "button", "input",
                     "select", "textarea", "meta", "link"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    boilerplate_patterns = re.compile(
        r"(cookie|consent|popup|modal|overlay|banner|sidebar|widget|"
        r"social|share|related|recommended|newsletter|subscribe|"
        r"breadcrumb|pagination|nav|menu|footer|header|sidebar|"
        r"advertisement|ad-|ads-|sponsor)",
        re.I
    )
    for tag in soup.find_all(attrs={"class": boilerplate_patterns}):
        tag.decompose()
    for tag in soup.find_all(attrs={"id": boilerplate_patterns}):
        tag.decompose()

    main_content = (
        soup.find("main") or
        soup.find("article") or
        soup.find(attrs={"class": re.compile(r"content|article|post|entry|body", re.I)}) or
        soup.find(attrs={"id": re.compile(r"content|article|post|entry|body", re.I)}) or
        soup.find("body") or
        soup
    )

    lines = []
    for elem in main_content.descendants:
        if isinstance(elem, str):
            text = elem.strip()
            if text:
                lines.append(text)
        elif elem.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(elem.name[1])
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"\n{'#' * level} {text}\n")
        elif elem.name == "p":
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"\n{text}\n")
        elif elem.name == "br":
            lines.append("\n")
        elif elem.name == "hr":
            lines.append("\n---\n")
        elif elem.name == "li":
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"  - {text}")
        elif elem.name in ("strong", "b"):
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"**{text}**")
        elif elem.name in ("em", "i"):
            text = elem.get_text(strip=True)
            if text:
                lines.append(f"*{text}*")
        elif elem.name == "a":
            text = elem.get_text(strip=True)
            href = elem.get("href", "")
            if text and href and not href.startswith(("#", "javascript:")):
                lines.append(f"[{text}]({href})")
        elif elem.name == "img":
            alt = elem.get("alt", "")
            src = elem.get("src", "")
            if alt and src and not src.startswith("data:"):
                lines.append(f"![{alt}]({src})")

    result = "\n".join(lines)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    if result:
        return result
    return None


# ---------------------------------------------------------------------------
# Utility: regex-based boilerplate stripping
# ---------------------------------------------------------------------------

def _strip_boilerplate_tags(raw_html: str) -> str:
    for tag in ("script", "style", "svg", "nav", "footer", "aside", "header",
                "noscript", "iframe", "form", "button", "meta", "link"):
        raw_html = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}>",
            " ", raw_html, flags=re.S | re.I
        )
    raw_html = re.sub(r"<!--.*?-->", " ", raw_html, flags=re.S)
    raw_html = re.sub(r"<img[^>]*src=['\"]data:[^'\"]+['\"][^>]*>", " ", raw_html, flags=re.I)
    raw_html = re.sub(r'\s+style="[^"]*"', "", raw_html, flags=re.I)
    raw_html = re.sub(r"\s+style='[^']*'", "", raw_html, flags=re.I)
    raw_html = re.sub(r'\s+class="[^"]*"', "", raw_html, flags=re.I)
    raw_html = re.sub(r"\s+class='[^']*'", "", raw_html, flags=re.I)
    return raw_html


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def preclean(raw_html: str, max_chars: int = 40000) -> str:
    result = extract_with_trafilatura(raw_html)
    if result:
        source = "trafilatura"
    else:
        result = extract_with_html2text(raw_html)
        if result:
            source = "html2text"
        else:
            result = extract_with_bs4(raw_html)
            if result:
                source = "beautifulsoup4"
            else:
                cleaned = _strip_boilerplate_tags(raw_html)
                text = re.sub(r"<[^>]+>", " ", cleaned)
                text = html_module.unescape(text)
                text = re.sub(r"\s+", " ", text).strip()
                result = text
                source = "regex"

    if len(result) > max_chars:
        result = result[:max_chars] + f"\n\n[CONTENT CUT at {max_chars:,} chars — source: {source}]"

    raw_kb = len(raw_html) / 1024
    out_kb = len(result) / 1024
    reduction = (1 - len(result) / max(len(raw_html), 1)) * 100
    print(
        f"[web-preclean] {raw_kb:.0f}KB raw HTML -> {out_kb:.0f}KB clean Markdown "
        f"({reduction:.0f}% reduction, source: {source})",
        file=sys.stderr
    )
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: web-preclean.py <URL> [max_chars]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 40000

    try:
        raw_html = fetch_url(url)
    except Exception as e:
        print(f"[web-preclean] ERROR: fetch failed: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        result = preclean(raw_html, max_chars)
    except Exception as e:
        print(f"[web-preclean] ERROR: extraction failed: {e}", file=sys.stderr)
        sys.exit(3)

    if not result:
        print(f"[web-preclean] WARNING: empty extraction result", file=sys.stderr)
        sys.exit(3)

    print(result)


if __name__ == "__main__":
    main()
