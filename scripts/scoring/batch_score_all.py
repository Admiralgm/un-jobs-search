#!/usr/bin/env python3
"""
UN JOBS BATCH SCORING — Programmatic 7-parameter scoring for 90 JD files.
Uses the validated approach from vacancy-compatibility-scoring-engine v4.1.
Produces scored tracker entries and a full rebuild of UN-VACANCIES-TRACKER.txt.
"""
import os, re, json
from pathlib import Path
from datetime import datetime, timezone

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
JD_DIR = WORKDIR / "JD_FILES"
TRACKER_PATH = WORKDIR / "UN-VACANCIES-TRACKER.txt"

NOW = datetime.now(timezone.utc)
TODAY_STR = "2026-06-03"

# ─── Org normalisation ───
ORG_MAP = {
    "ECB": "ECB", "FAO": "FAO", "IAEA": "IAEA", "ICAO": "ICAO",
    "ICMPD": "ICMPD", "ICRC": "ICRC", "ILO": "ILO", "IMF": "IMF",
    "INSPIRA": "UN Secretariat", "ITU": "ITU", "OECD": "OECD",
    "UNDP": "UNDP", "UNESCO": "UNESCO", "UNFPA": "UNFPA",
    "UNICEF": "UNICEF", "UNICRI": "UNICRI", "UNIDO": "UNIDO",
    "UNITAR": "UNITAR", "UNOPS": "UNOPS", "UNU": "UNU",
    "WFP": "WFP", "WHO": "WHO", "WMO": "WMO",
    "WORLDBANK": "World Bank", "WTO": "WTO",
}

# ─── P3 UN/IFI Fit map ───
ORG_P3_BASE = {
    "UNICEF": 9, "WHO": 7, "ITU": 7, "FAO": 7, "UNIDO": 7, "WFP": 7,
    "IAEA": 5, "ILO": 5, "UNOPS": 5, "INSPIRA": 5,
    "IMF": 4, "WORLDBANK": 4, "UNDP": 4, "ICAO": 4, "UNESCO": 4,
    "UNFPA": 5, "UNITAR": 3, "UNU": 3, "ICMPD": 3, "ICRC": 3,
    "ECB": 1, "OECD": 2, "WMO": 3, "WTO": 2, "UNICRI": 3,
}

# ─── Domain cap map for P1 ───
DOMAIN_P1_CAP = {
    "telecom": 22, "connectivity": 22, "ai": 22, "ml": 22, "agentic": 22,
    "digital_transform": 20, "ict_management": 18,
    "data": 16, "finance": 16,
    "management": 14, "gis": 10, "swe": 8,
}

# ─── P6 Logistics ───
EU_COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
    "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
    "Slovenia", "Spain", "Sweden", "Switzerland", "Norway", "Iceland",
    "Liechtenstein", "Geneva", "Vienna", "Copenhagen", "Brussels",
    "Valencia", "Madrid", "Berlin", "Munich", "Frankfurt", "Amsterdam",
    "Paris", "Rome", "Milan", "Belgrade",
]

# ─── Scored entries ───
entries = []

def extract_metadata(content, fname, agency_dir_name):
    """Extract metadata from JD file content and filename."""
    lines = content.split('\n')
    body_lower = content.lower()
    
    # Title: first heading line or filename
    title = ""
    for line in lines[:5]:
        line = line.strip().lstrip('#').strip()
        if line and len(line) > 10:
            title = line
            break
    if not title:
        title = fname.replace('.md', '').replace('_', ' ')[:60]
    
    # Deadline
    deadline = "TBD"
    dl_patterns = [
        (r'deadline[:\s]+(\d{4}-\d{2}-\d{2})', 1),
        (r'closing date[:\s]+(\d{4}-\d{2}-\d{2})', 1),
        (r'apply before[:\s]+(\d{4}-\d{2}-\d{2})', 1),
        (r'(\w+ \d{1,2},? \d{4})[,\s]*\d', None),
        (r'closing date[:\s]*\n?\s*(\w+ \d{1,2},? \d{4})', 1),
    ]
    for pat, grp in dl_patterns:
        m = re.search(pat, content, re.IGNORECASE)
        if m:
            raw = m.group(1)
            if grp is None:
                raw = m.group(1)
            # Try to parse
            for fmt in ['%Y-%m-%d', '%B %d, %Y', '%B %d %Y', '%b %d, %Y', '%b %d %Y',
                        '%d %B %Y', '%d %b %Y']:
                try:
                    dt = datetime.strptime(raw, fmt)
                    deadline = dt.strftime('%Y-%m-%d')
                    break
                except:
                    pass
            break
    
    # Grade
    grade = ""
    # Look for "Grade [label]" or "P-X" patterns
    for line in lines[:20]:
        line_lower = line.lower()
        gm = re.search(r'(?:grade|level)[:\s]+(\S[\w\-\.\/]*)', line_lower)
        if gm:
            g = gm.group(1).strip().upper()
            if len(g) < 15 and not g.startswith('<'):
                grade = g
    if not grade:
        gm = re.search(r'\b(P-\d+|D-\d+|G-\d+|NO[A-Z]|IPS[A-Z]-\d+|ICSC-\d+)\b', content)
        if gm:
            grade = gm.group(1)
    
    # Location
    location = ""
    loc_patterns = [
        (r'(?:duty station|location|primary location|place of assignment)[:\s]+([^\n]+)', 1),
        (r'locations?\s*\n([A-Za-z\s,]+)', 1),
    ]
    for pat, grp in loc_patterns:
        m = re.search(pat, content, re.IGNORECASE)
        if m:
            loc = m.group(1).strip()
            if len(loc) < 80 and not loc.startswith('<'):
                location = loc
                break
    if not location:
        for loc_kw in ['Geneva', 'New York', 'Vienna', 'Paris', 'Rome', 'Belgrade',
                       'Nairobi', 'Addis Ababa', 'Bangkok', 'Home Based', 'Remote',
                       'Valencia', 'Kabul', 'Manila', 'Bishkek', 'Copenhagen',
                       'Istanbul', 'Brazzaville', 'Lusaka', 'Washington']:
            if loc_kw.lower() in body_lower[:2000]:
                location = loc_kw
                break
    
    # Vacancy ID
    vid = fname.replace('.md','')
    # Extract from content
    vm = re.search(r'(?:vacancy id|job id|opening id|req(?:uisition)? id|id number)[:\s]+(\S+)', content, re.IGNORECASE)
    if vm:
        vid2 = vm.group(1).strip().rstrip('.)')
        if len(vid2) < 30 and not vid2.startswith('<'):
            vid = vid2
    
    # Roster detection
    is_roster = bool(re.search(r'(roster|talent pool|expression of interest)', body_lower))
    
    return {
        'title': title,
        'org_raw': agency_dir_name.replace('UN_',''),
        'deadline': deadline,
        'grade': grade,
        'location': location,
        'vid': vid,
        'is_roster': is_roster,
    }

def score_entry(meta, content):
    """Score one vacancy with all 7 parameters."""
    body_lower = content.lower()
    title_lower = meta['title'].lower()
    
    # ═══ P1: Domain/Technical Fit (max 25, capped by domain) ═══
    p1 = 0
    domain = "general"
    kw_groups = {
        'ai': ['ai ', 'artificial intelligence', 'machine learning', 'llm', 'llm ',
               'genai', 'deep learning', 'neural', 'nlp ', 'chatbot', 'gpt',
               'agentic', 'ai agent', 'ai-enabled', 'ai-assisted', 'ai-powered',
               'openai', 'claude', 'gemini', 'ai/ml', 'ai framework'],
        'telecom': ['telecom', 'connectivity', 'broadband', 'isp ', 'network infrastructure',
                    'undersea', 'fibre', 'satellite', 'vsat', 'ip transit', '5g', '4g',
                    'gpon', 'fttx', 'transmission', 'sdh', 'router'],
        'data': ['data engineering', 'data pipeline', 'etl ', 'data warehouse',
                 'data lake', 'big data', 'data integration', 'data architect',
                 'data platform', 'pyspark', 'spark', 'data quality', 'data governance',
                 'data modelling', 'data catalog'],
        'swe': ['software engineer', 'full stack', 'web developer', 'devops',
                'frontend', 'backend', 'api', 'ci/cd', 'docker', 'kubernetes',
                'code review', 'agile', 'scrum', 'git '],
        'cloud': ['cloud engineer', 'cloud platform', 'aws', 'azure', 'gcp',
                  'infrastructure', 'virtualization', 'vmware', 'container',
                  'oracle cloud', 'saas', 'paas'],
        'digital': ['digital transformation', 'digital strategy', 'digital health',
                    'digital ecosystem', 'digital technology', 'digital solution'],
        'cyber': ['cybersecur', 'cirt', 'incident response', 'security audit',
                  'security policy', 'information security', 'threat'],
        'gis': ['gis ', 'geospatial', 'satellite imagery', 'remote sensing',
                'geonode', 'qgis', 'geoserver', 'spatial analysis', 'dem '],
        'arch': ['solution architect', 'enterprise architect', 'platform architect',
                 'technical architect', 'system design'],
        'pm': ['project manager', 'programme manager', 'product owner',
               'scrum master', 'project management'],
        'innovation': ['innovation', 'edtech', 'digital learning', 'education technology',
                       'instructional design', 'elearning', 'lms ', 'moodle', 'canvas'],
        'finance': ['digital euro', 'market infrastructure', 'payment system',
                    'fintech', 'blockchain', 'payment'],
        'health': ['health', 'public health', 'epidemiology', 'immunization'],
    }
    
    for k, group in kw_groups.items():
        count = sum(1 for kw in group if kw in body_lower)
        if k == 'ai' and count >= 3:
            p1 += 12
            domain = 'ai'
        elif k == 'telecom' and count >= 2:
            p1 += 8
            domain = 'telecom'
        elif k == 'data' and count >= 3:
            p1 += 6
            domain = 'data'
        elif k == 'swe' and count >= 3:
            p1 += 5
        elif k == 'cloud' and count >= 2:
            p1 += 5
        elif k == 'digital' and count >= 2:
            p1 += 5
            if domain == 'general':
                domain = 'digital_transform'
        elif k == 'cyber' and count >= 2:
            p1 += 6
        elif k == 'gis' and count >= 2:
            p1 += 3
            if domain == 'general':
                domain = 'gis'
        elif k == 'arch' and count >= 1:
            p1 += 4
        elif k == 'pm' and count >= 2:
            p1 += 3
        elif k == 'innovation' and count >= 2:
            p1 += 3
        elif k == 'finance' and count >= 2:
            p1 += 3
            if domain == 'general':
                domain = 'finance'
    
    # Title keywords add bonus
    if 'ai ' in title_lower or 'machine learning' in title_lower:
        p1 += 3
        domain = 'ai'
    if 'digital' in title_lower and 'transformation' in title_lower:
        p1 += 2
    if 'data' in title_lower and ('engineer' in title_lower or 'science' in title_lower):
        p1 += 2
    
    # Apply domain cap
    domain_map = {
        'ai': 'ai', 'telecom': 'telecom', 'data': 'data',
        'digital_transform': 'digital_transform', 'gis': 'gis',
        'finance': 'finance', 'swe': 'swe',
    }
    cap_key = domain_map.get(domain, 'general')
    cap = DOMAIN_P1_CAP.get(cap_key, 22)
    p1 = min(p1, cap)
    p1 = max(p1, 0)
    
    # ═══ P2: Seniority & Experience Volume (max 15) ═══
    p2 = 7  # base
    if re.search(r'\b(director|chief|head of|deputy head|d-[12])\b', title_lower):
        p2 = 13
    elif re.search(r'\bsenior\b', title_lower) or re.search(r'\bp-?[45]\b', title_lower):
        p2 = 11
    elif re.search(r'\blead\b|\bmanager\b', title_lower):
        p2 = 10
    elif re.search(r'\bspecialist\b|\bexpert\b|\badvisor\b', title_lower):
        p2 = 9
    elif re.search(r'\bofficer\b|\bconsultant\b|\bengineer\b', title_lower):
        p2 = 8
    
    # Grade boost for P3/P4 roles
    if meta['grade']:
        if re.match(r'P-?[45]', meta['grade']):
            p2 = max(p2, 11)
        elif re.match(r'P-?3', meta['grade']):
            p2 = max(p2, 10)
        elif re.match(r'D-?[12]', meta['grade']):
            p2 = 13
    
    p2 = min(p2, 15)
    
    # ═══ P3: UN/IFI/Development Fit (max 15) ═══
    org_name = meta['org_raw']
    p3 = ORG_P3_BASE.get(org_name, 3)
    
    # UNICEF bonus keywords
    if org_name == "UNICEF":
        if any(kw in body_lower for kw in ['digital', 'ai ', 'innovation', 'education', 
                                            'connectivity', 'ict', 't4d', 'school']):
            p3 += 2
        if any(kw in body_lower for kw in ['giga', 'learning passport', 'school connectivity',
                                            'infrastructure finance']):
            p3 += 3
    
    # General UN context keywords
    if any(kw in body_lower for kw in ['sdg', 'sustainable development', 'un reform',
                                        'inter-agency']):
        p3 += 1
    
    p3 = min(p3, 15)
    
    # ═══ P4: Education & Credentials (max 10) ═══
    p4 = 8  # MSc+MPhil meets any Master's req
    # Check for specific field requirements
    if re.search(r'\b(electrical engineering|computer science|telecom|information technology|engineering)\b', body_lower):
        p4 = 10
    # PhD required
    if re.search(r'\bphd\b|\bdoctorate\b', body_lower):
        p4 = min(p4, 8)  # MSc is fine but not a PhD
    
    p4 = min(p4, 10)
    
    # ═══ P5: Language (max 10) ═══
    p5 = 8  # English + Russian
    if re.search(r'\bfrench\b', body_lower):
        if re.search(r'\bfrench\s+(required|essential|fluent)\b', body_lower):
            p5 = 5
        else:
            p5 = 6  # French desirable
    if re.search(r'\brussian\b', body_lower):
        p5 = min(p5 + 1, 10)
    
    p5 = min(p5, 10)
    
    # ═══ P6: Logistics & Eligibility (max 10) ═══
    loc_lower = meta['location'].lower()
    p6 = 6  # base (non-EU developing country)
    
    # Check if location mentions EU
    if any(eu.lower() in loc_lower or eu.lower() in body_lower[:3000] for eu in EU_COUNTRIES):
        p6 = 10
    elif any(kw in loc_lower or kw in title_lower for kw in ['home based', 'remote', 'multiple']):
        p6 = 10
    elif 'belgrade' in loc_lower or 'belgrade' in body_lower[:1000]:
        p6 = 10  # home base for User
    elif 'istanbul' in loc_lower:
        p6 = 8  # Türkiye is non-EU but serves Europe
    elif any(kw in loc_lower for kw in ['washington', 'dc']):
        p6 = 4  # no US work rights
    elif 'nairobi' in loc_lower:
        p6 = 7
    elif 'brazzaville' in loc_lower:
        p6 = 5  # hardship
    elif 'kabul' in loc_lower:
        p6 = 3  # extreme hardship
    
    p6 = min(p6, 10)
    
    # ═══ P7: Competitive Realism (max 15) ═══
    p7 = 7  # base
    # AI/ML bonus
    ai_count = sum(1 for kw in ['ai ', 'machine learning', 'llm', 'agent', 'genai', 'nlp ']
                   if kw in body_lower)
    if ai_count >= 3:
        p7 += 4
    elif ai_count >= 1:
        p7 += 2
    
    # UNICEF + digital/education
    if org_name == "UNICEF" and any(kw in body_lower for kw in ['digital', 'ai ', 'education', 'technology']):
        p7 += 3
    
    # Telecom/connectivity bonus
    if any(kw in body_lower for kw in ['telecom', 'connectivity', 'broadband', 'isp ']):
        p7 += 2
    
    # Architecture bonus
    if any(kw in title_lower for kw in ['architect', 'solution', 'enterprise']):
        p7 += 2
    
    # Director penalty (very competitive)
    if re.search(r'\b(director|chief|head of)\b', title_lower):
        p7 -= 3
    
    # GIS penalty (unless AI/data angle)
    if domain == 'gis' and ai_count == 0:
        p7 -= 2
    
    p7 = max(p7, 1)
    p7 = min(p7, 15)
    
    # ═══ TOTAL ═══
    total = p1 + p2 + p3 + p4 + p5 + p6 + p7
    
    return {
        'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5, 'p6': p6, 'p7': p7,
        'total': total,
        'domain': domain,
    }


# ═══ MAIN: Process all 124 files ═══
all_scored = []

for agency_dir in sorted(JD_DIR.iterdir()):
    if not agency_dir.is_dir():
        continue
    agency_name = agency_dir.name
    
    for jd_file in sorted(agency_dir.glob("*.md")):
        content = jd_file.read_text(encoding='utf-8', errors='replace')
        
        meta = extract_metadata(content, jd_file.name, agency_name)
        
        # Check for hard disqualifiers
        body_lower = content.lower()
        title_lower = meta['title'].lower()
        
        disqualified = False
        reason = ""
        
        # 1. Nationals-only
        if re.search(r'\b(nationals?\s+only|national\s+position|local\s+recruitment|national consultant|national officer|poste réservé exclusivement)\b', body_lower):
            disqualified = True
            reason = "NATIONALS_ONLY"
        
        # 2. Ukraine
        if not disqualified and re.search(r'\bukraine\b', body_lower):
            disqualified = True
            reason = "UKRAINE"
        
        # 3. Intern/Volunteer/Trainee in title
        if not disqualified and re.search(r'\b(intern(?:ship)?|traineeship|volunteer)\b', title_lower):
            disqualified = True
            reason = "INTERN_VOLUNTEER"
        
        # 4. Grade too low
        if not disqualified and meta['grade']:
            if re.match(r'P-?[12]\b', meta['grade']) or re.match(r'G-\d', meta['grade']) or re.match(r'NO[AB]', meta['grade']):
                disqualified = True
                reason = f"GRADE_TOO_LOW_{meta['grade']}"
        
        # 5. Hard-reject keywords
        if not disqualified:
            for kw in ['hr ', 'human resources', 'nutrition', 'agricultur', 'veterinar',
                       'teacher', 'nurse', 'doctor,', 'medical doctor']:
                if kw in title_lower:
                    disqualified = True
                    reason = f"HARD_REJECT_{kw.strip().upper()}"
                    break
        
        # 6. IT Assistant / IT Support low level
        if not disqualified and re.search(r'\bit\s+(assistant|support|clerk)\b', title_lower):
            disqualified = True
            reason = "IT_ASSISTANT_LOW"
        
        # 7. Expired (unless roster)
        if not disqualified and meta['deadline'] != 'TBD':
            try:
                dl = datetime.strptime(meta['deadline'], '%Y-%m-%d')
                if dl < datetime(2026, 6, 3) and 'roster' not in title_lower and 'rost' not in body_lower[:500]:
                    disqualified = True
                    reason = f"EXPIRED_{meta['deadline']}"
            except ValueError:
                pass
        
        if disqualified:
            all_scored.append({
                'meta': meta,
                'score': None,
                'disqualified': True,
                'reason': reason,
                'content': content,
                'file': str(jd_file),
            })
            continue
        
        # Check if file has real JD content
        has_content = False
        for sec in ["responsibilities", "duties", "qualifications",
                    "work experience", "education", "job purpose",
                    "accountabilities", "competencies"]:
            if sec in body_lower:
                has_content = True
                break
        if not has_content and len(content) < 2000:
            all_scored.append({
                'meta': meta,
                'score': None,
                'disqualified': True,
                'reason': "NO_JD_CONTENT",
                'content': content,
                'file': str(jd_file),
            })
            continue
        
        # ═══ SCORE THIS ENTRY ═══
        score = score_entry(meta, content)
        
        all_scored.append({
            'meta': meta,
            'score': score,
            'disqualified': False,
            'reason': "",
            'content': content,
            'file': str(jd_file),
        })


# ═══ Build Tracker ═══
scored = [e for e in all_scored if not e['disqualified']]
disq = [e for e in all_scored if e['disqualified']]

# Sort by deadline (TBD last), then by score descending
def sort_key(e):
    dl = e['meta']['deadline']
    if dl == 'TBD':
        return (1, '9999-99-99', -e['score']['total'] if e['score'] else 0)
    try:
        return (0, dl, -e['score']['total'] if e['score'] else 0)
    except:
        return (0, dl, 0)

scored.sort(key=sort_key)

# Separate roster from active
active = [e for e in scored if not e['meta']['is_roster']]
roster = [e for e in scored if e['meta']['is_roster']]

def score_emoji(total):
    if total >= 75: return '🔴'
    if total >= 65: return '🟠'
    if total >= 50: return '🟡'
    return '🟢'

def trunc(s, n):
    s = str(s).strip()
    if len(s) > n:
        return s[:n-1] + '…'
    return s.ljust(n)

# Build lines
lines = []
lines.append("=" * 100)
lines.append("UN VACANCIES TRACKER — Full JD Scoring")
lines.append(f"Generated: {TODAY_STR}")
lines.append("=" * 100)
lines.append("")
lines.append("🔵 VACANCY SUMMARY TABLE")
lines.append("")

header = f"{'#':5s}{'Organization':22s}{'Position Title':44s}{'Deadline':16s}{'Score':10s}{'Vacancy ID':30s}{'Applied'}"
lines.append(header)
lines.append('-' * 196)

for i, e in enumerate(active, 1):
    m = e['meta']
    s = e['score']
    org_display = trunc(ORG_MAP.get(m['org_raw'], m['org_raw']), 22)
    title = trunc(m['title'], 44)
    dl = trunc(m['deadline'], 16)
    emoji = score_emoji(s['total']) if s else '🟢'
    score_str = trunc(f"{emoji} {s['total']}", 10) if s else trunc('  0', 10)
    vid = trunc(m['vid'], 30)
    applied = 'NO     '
    
    row = f"{str(i).ljust(5)}{org_display}{title}{dl}{score_str}{vid}{applied}"
    lines.append(row)

lines.append('-' * 196)

# Roster section
if roster:
    lines.append("")
    lines.append("📋 ROSTER / OPEN-ENDED POSITIONS")
    lines.append("")
    for i, e in enumerate(roster, 1):
        m = e['meta']
        s = e['score']
        org_display = trunc(ORG_MAP.get(m['org_raw'], m['org_raw']), 22)
        title = trunc(m['title'], 44)
        dl = trunc("Open (Roster)", 16)
        emoji = score_emoji(s['total']) if s else '🟢'
        score_str = trunc(f"{emoji} {s['total']}", 10) if s else trunc('  0', 10)
        vid = trunc(m['vid'], 30)
        
        row = f"{str(i).ljust(5)}{org_display}{title}{dl}{score_str}{vid}{'NO     '}"
        lines.append(row)

lines.append("")
total_active = len(active)
total_roster = len(roster)
lines.append(f"Total: {total_active} active vacancies + {total_roster} roster positions")
lines.append(f"Last updated: {TODAY_STR} | Last scan: {TODAY_STR}")
lines.append("Color coding: 🔴 75+ STRONG FIT | 🟠 65-74 COMPETITIVE | 🟡 50-64 STRETCH | 🟢 <50 LOW FIT")
lines.append("")

# Scoring Details
lines.append("")
lines.append("=" * 100)
lines.append("SCORING DETAILS — Arithmetic (P1+P2+P3+P4+P5+P6+P7 = TOTAL)")
lines.append("=" * 100)
lines.append("")

for e in active + roster:
    m = e['meta']
    s = e['score']
    if s:
        arith = f"P1({s['p1']}) + P2({s['p2']}) + P3({s['p3']}) + P4({s['p4']}) + P5({s['p5']}) + P6({s['p6']}) + P7({s['p7']}) = TOTAL({s['total']})"
        lines.append(f"{ORG_MAP.get(m['org_raw'], m['org_raw']):15s} | {trunc(m['title'], 50)}")
        lines.append(f"  {arith}  {score_emoji(s['total'])}")
        lines.append(f"  Domain: {s['domain']:20s} | Grade: {m['grade']:10s} | Location: {m['location']:25s} | DL: {m['deadline']:12s}")
        lines.append("")

# Summary
lines.append("")
lines.append("=" * 100)
lines.append("📊 SUMMARY STATISTICS")
lines.append("=" * 100)
lines.append("")

all_scored_list = [e for e in scored if e['score']]
bands = {75: 0, 65: 0, 50: 0, 0: 0}
for e in all_scored_list:
    t = e['score']['total']
    if t >= 75: bands[75] += 1
    elif t >= 65: bands[65] += 1
    elif t >= 50: bands[50] += 1
    else: bands[0] += 1

lines.append(f"🔴 75+  STRONG FIT:   {bands[75]}")
lines.append(f"🟠 65-74 COMPETITIVE: {bands[65]}")
lines.append(f"🟡 50-64 STRETCH:    {bands[50]}")
lines.append(f"🟢 <50  LOW FIT:     {bands[0]}")
lines.append(f"Total scored: {len(all_scored_list)}")
lines.append(f"Disqualified: {len(disq)}")
lines.append("")

# Top 10
lines.append("")
lines.append("🏆 TOP 10 HIGHEST SCORES")
for e in sorted(all_scored_list, key=lambda x: -x['score']['total'])[:10]:
    s = e['score']
    m = e['meta']
    lines.append(f"  {ORG_MAP.get(m['org_raw'], m['org_raw']):15s} | {score_emoji(s['total'])} {s['total']:3d} | {trunc(m['title'], 55)}")

lines.append("")
lines.append("=" * 100)
lines.append("END OF TRACKER")
lines.append("=" * 100)

content = '\n'.join(lines) + '\n'
TRACKER_PATH.write_text(content, encoding='utf-8')

print(f"✅ Tracker written: {len(active)} active + {len(roster)} roster + {len(disq)} disqualified")
print(f"   Bands: STRONG={bands[75]} COMPETITIVE={bands[65]} STRETCH={bands[50]} LOW={bands[0]}")
print(f"   Top score: {all_scored_list[0]['score']['total'] if all_scored_list else 'N/A'}")
print(f"   File size: {len(content)} chars, {len(lines)} lines")

# JSON summary for verification
summary = {
    'active': [{'org': ORG_MAP.get(e['meta']['org_raw'], e['meta']['org_raw']),
                'title': e['meta']['title'][:50],
                'total': e['score']['total'],
                'deadline': e['meta']['deadline']}
               for e in active[:5]],
    'stats': {'strong': bands[75], 'competitive': bands[65], 'stretch': bands[50], 'low': bands[0],
              'total_scored': len(all_scored_list), 'total_disqualified': len(disq)}
}
print(f"\nTop 5 active: {json.dumps(summary['active'], indent=2)}")
print(f"\nStats: {json.dumps(summary['stats'])}")