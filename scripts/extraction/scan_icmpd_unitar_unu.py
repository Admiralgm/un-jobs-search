#!/usr/bin/env python3
"""Scan ICMPD, UNITAR, UNU for ICT/AI roles using Camoufox Python."""

import json, sys, time, re
from datetime import date
from pathlib import Path

from camoufox import Camoufox

RESULTS_DIR = Path("~/Downloads/DATA_REPOSITORY/scan_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

today = date.today()

def extract_text(page):
    """Get page text robustly."""
    time.sleep(4)
    return page.inner_text("body")

def show_text(text, max_lines=80):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:max_lines]:
        print(f"  {l[:150]}")
    return len(lines)

def scan_icmpd():
    """ICMPD careers.icmpd.org"""
    print("\n" + "=" * 60)
    print("ICMPD - International Centre for Migration Policy Development")
    print("careers.icmpd.org")
    print("=" * 60)
    
    results = []
    
    with Camoufox(headless=True, humanize=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        # Try base URL first
        page.goto("https://careers.icmpd.org/", wait_until="networkidle")
        text = extract_text(page)
        print(f"\nBase URL: {len(text)} chars")
        total_lines = show_text(text)
        
        # Check for search URL variant
        page.goto("https://careers.icmpd.org/search/?q=", wait_until="networkidle")
        text2 = extract_text(page)
        print(f"\nSearch URL: {len(text2)} chars")
        total_lines2 = show_text(text2)
        
        # Try vacancies URL
        page.goto("https://careers.icmpd.org/vacancies", wait_until="networkidle")
        text3 = extract_text(page)
        print(f"\n/vacancies: {len(text3)} chars")
        total_lines3 = show_text(text3)
        
        # Get all links
        links = page.query_selector_all("a")
        print(f"\nAll links ({len(links)}):")
        for a in links:
            href = a.get_attribute("href") or ""
            t = a.inner_text().strip()
            if t and len(t) > 3:
                print(f"  [{t[:80]}] -> {href[:100]}")
        
        results.append({
            "base_text": text[:5000],
            "search_text": text2[:3000],
            "vacancies_text": text3[:5000],
            "base_lines": total_lines,
        })
    
    outfile = RESULTS_DIR / "icmpd_results.json"
    outfile.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved -> {outfile}")
    return results


def scan_unitar():
    """UNITAR unitar.org/vacancy-announcements"""
    print("\n" + "=" * 60)
    print("UNITAR - UN Institute for Training and Research")
    print("unitar.org/vacancy-announcements")
    print("=" * 60)
    
    results = []
    
    with Camoufox(headless=True, humanize=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        page.goto("https://www.unitar.org/vacancy-announcements", wait_until="networkidle")
        text = extract_text(page)
        print(f"\nVacancy page: {len(text)} chars")
        total_lines = show_text(text)
        
        # Get links
        links = page.query_selector_all("a")
        print(f"\nLinks ({len(links)}):")
        for a in links:
            href = a.get_attribute("href") or ""
            t = a.inner_text().strip()
            if t and len(t) > 3:
                print(f"  [{t[:80]}] -> {href[:100]}")
        
        results.append({
            "text": text[:8000],
            "lines": total_lines,
        })
    
    outfile = RESULTS_DIR / "unitar_results.json"
    outfile.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved -> {outfile}")
    return results


def scan_unu():
    """UNU - United Nations University"""
    print("\n" + "=" * 60)
    print("UNU - United Nations University")
    print("=" * 60)
    
    results = []
    urls_to_try = [
        "https://unu.edu/career-opportunities",
        "https://unu.edu/about/unu-careers",
        "https://unu.edu/careers",
        "https://unu.edu/jobs",
    ]
    
    with Camoufox(headless=True, humanize=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        for url in urls_to_try:
            try:
                page.goto(url, wait_until="networkidle")
                text = extract_text(page)
                print(f"\n{url}: {len(text)} chars")
                total_lines = show_text(text, 40)
                
                has_404 = "404" in text or "not found" in text.lower() or "page not found" in text.lower()
                results.append({
                    "url": url,
                    "text": text[:3000],
                    "lines": total_lines,
                    "has_404": has_404,
                })
                
                if not has_404 and len(text) > 500:
                    print(f"  ✅ GOOD PAGE")
                    # Get links
                    links = page.query_selector_all("a")
                    for a in links:
                        href = a.get_attribute("href") or ""
                        t = a.inner_text().strip()
                        if t and len(t) > 3 and ("vacanc" in href.lower() or "job" in href.lower() or "career" in href.lower()):
                            print(f"  [{t[:80]}] -> {href[:100]}")
                    break
            except Exception as e:
                print(f"  {url}: ERROR {e}")
                results.append({"url": url, "error": str(e)})
    
    outfile = RESULTS_DIR / "unu_results.json"
    outfile.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved -> {outfile}")
    return results


if __name__ == "__main__":
    print(f"Date: {today}")
    print("Scanning ICMPD, UNITAR, UNU\n")
    
    icmpd = scan_icmpd()
    unitar = scan_unitar()
    unu = scan_unu()
    
    print("\n" + "=" * 60)
    print("SCAN COMPLETE")
    print(f"ICMPD: {len(icmpd)} results")
    print(f"UNITAR: {len(unitar)} results")
    print(f"UNU: {len(unu)} results")
    print("=" * 60)