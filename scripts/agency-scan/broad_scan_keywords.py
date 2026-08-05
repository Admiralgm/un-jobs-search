# broad_scan_keywords.py
# ZERO-EMPTY-SCREENING keyword list for UN-JOBS-SEARCH v5.0
"""
USAGE:
    from broad_scan_keywords import (
        TIER1_KEYWORDS, TIER2_KEYWORDS, TIER3_KEYWORDS, TIER4_KEYWORDS, TIER5_KEYWORDS,
        ALL_KEYWORDS, should_fetch_jd, get_keyword_tier
    )
"""

TIER1_KEYWORDS = {
    "digital", "ai", "artificial intelligence", "machine learning", "llm", "large language model",
    "agentic", "agent", "mcp", "model context protocol", "digital transformation",
    "telecom", "connectivity", "fibre", "fiber", "broadband", "internet",
    "undersea", "submarine", "cable", "capacity", "wholesale", "transmission",
    "ip transit", "vsat", "satellite", "iru", "sdh", "fttx", "ftth", "fttc",
    "gpon", "3g", "4g", "5g", "wi-fi", "wifi", "wireless", "mobile", "cellular",
    "isp", "mvno", "mvne",
    "mobile money", "fintech", "payment", "digital banking", "transaction processing",
    "edtech", "education tech", "education", "school", "learning",
    "lms", "moodle", "canvas", "k-12", "k12", "ai curriculum", "giga",
    "blended finance", "ppp", "public-private partnership",
    "infrastructure investment", "development finance",
    "connectivity for schools", "education technology", "unicef", "undp", "world bank", "imf", "afdb", "ifi",
}

TIER2_KEYWORDS = {
    "coo", "chief operating", "chief operations", "operations director",
    "executive", "p&l", "p and l", "general management",
    "managing director", "director", "head of", "chief", "lead",
    "manager", "coordinator", "advisor", "adviser", "consultant",
    "specialist", "officer", "expert", "strategist", "architect",
    "project manager", "programme manager", "portfolio", "delivery",
    "change management", "transformation", "restructuring",
    "merger", "acquisition", "due diligence", "m&a",
    "business development", "growth", "market development",
    "entrepreneur", "startup", "start-up", "founder", "venture",
    "revenue", "commercial", "sales",
}

TIER3_KEYWORDS = {
    "cloud", "aws", "azure", "gcp", "kubernetes", "docker", "devops", "sre",
    "platform engineer", "systems", "enterprise",
    "it strategy", "it governance", "information management",
    "data", "analytics", "business intelligence", "data warehouse", "data architecture",
    "gis", "geospatial", "spatial", "remote sensing",
    "monitoring", "evaluation", "m&e", "m and e",
    "security", "cybersecurity", "information security", "infosec",
    "vendor", "procurement", "sourcing", "supply chain",
    "contract", "standard", "policy", "regulation", "itu",
    "regulatory", "compliance", "governance", "audit", "risk",
    "qa", "quality assurance",
}

TIER4_KEYWORDS = {
    "africa", "african", "east africa", "west africa", "southern africa",
    "uganda", "zambia", "rwanda", "kenya", "niger", "ivory coast", "south sudan",
    "emergency", "crisis", "humanitarian", "relief",
    "health", "medical", "hospital", "pharma", "pharmaceutical", "clinical",
    "covid", "pandemic", "disaster", "resilience",
    "russian", "cis", "balkan", "serbia", "belgrade", "eu", "european",
    "digital divide", "school connectivity", "meaningful connectivity",
}

TIER5_KEYWORDS = {
    "stakeholder", "partnership", "private sector", "government", "ministry",
    "public-private", "investment", "finance", "economic", "trade",
    "competitiveness", "innovation", "research", "science", "technology",
    "stem", "digital", "sustainability", "climate", "green", "energy",
    "iot", "internet of things", "sdg", "sustainable development",
}

ALL_KEYWORDS = TIER1_KEYWORDS | TIER2_KEYWORDS | TIER3_KEYWORDS | TIER4_KEYWORDS | TIER5_KEYWORDS


def _normalize(text):
    text = text.lower()
    for ch in ",;:.!?()[]{}|/\\\n\r\t":
        text = text.replace(ch, " ")
    tokens = [t.strip() for t in text.split() if t.strip()]
    unigrams = set(tokens)
    bigrams = set(f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1))
    trigrams = set(f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}" for i in range(len(tokens)-2))
    return unigrams | bigrams | trigrams


def get_keyword_tier(keyword):
    kw = keyword.lower().strip()
    if kw in TIER1_KEYWORDS: return 1
    if kw in TIER2_KEYWORDS: return 2
    if kw in TIER3_KEYWORDS: return 3
    if kw in TIER4_KEYWORDS: return 4
    if kw in TIER5_KEYWORDS: return 5
    return 0


def should_fetch_jd(title, description="", grade=""):
    combined = f"{title} {description} {grade}"
    tokens = _normalize(combined)
    matched = [kw for kw in ALL_KEYWORDS if kw in tokens]
    tiers = {get_keyword_tier(kw) for kw in matched}

    if 1 in tiers:
        t1_matches = [kw for kw in matched if get_keyword_tier(kw) == 1]
        return True, f"TIER 1 match: {t1_matches[:3]}", matched

    has_t1 = bool(tokens & TIER1_KEYWORDS)
    has_t2 = bool(tokens & TIER2_KEYWORDS)
    if has_t1 and has_t2:
        return True, f"Intersection (T1+T2): {matched[:3]}", matched

    if 2 in tiers:
        non_tech_indicators = {"human resources", "hr officer", "hr assistant", "hr coordinator", "payroll", "recruitment"}
        if tokens & non_tech_indicators:
            return False, "Non-technical HR role", matched
        return True, f"TIER 2 match: {matched[:3]}", matched

    if 3 in tiers and 4 in tiers:
        return True, f"TIER 3+4 match: {matched[:3]}", matched

    if 5 in tiers and (has_t1 or has_t2):
        return True, f"TIER 5 + T1/T2: {matched[:3]}", matched

    return False, f"No strong match (tiers: {tiers})", matched


def extract_relevant_jds(jd_text):
    tokens = _normalize(jd_text)
    score = 0
    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for kw in ALL_KEYWORDS:
        if kw in tokens:
            tier = get_keyword_tier(kw)
            tier_counts[tier] += 1
    score += tier_counts[1] * 8
    score += tier_counts[2] * 5
    score += tier_counts[3] * 3
    score += tier_counts[4] * 2
    score += tier_counts[5] * 1
    has_t1 = tier_counts[1] > 0
    has_t2 = tier_counts[2] > 0
    has_t3 = tier_counts[3] > 0
    has_t4 = tier_counts[4] > 0
    domains_present = sum([has_t1, has_t2, has_t3, has_t4])
    if domains_present >= 3: score += 8
    elif domains_present >= 2: score += 5
    preview = min(score, 100)
    return {"score_preview": preview, "tier_counts": tier_counts, "total_keywords_matched": sum(tier_counts.values())}


if __name__ == "__main__":
    import sys
    test_title = sys.argv[1] if len(sys.argv) > 1 else "Programme Officer"
    should, reason, matched = should_fetch_jd(test_title)
    print(f"Title: '{test_title}'")
    print(f"Fetch: {'YES' if should else 'NO'} — {reason}")
    if matched: print(f"Matched: {matched[:5]}")
