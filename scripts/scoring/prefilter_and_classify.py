#!/usr/bin/env python3
"""
Pre-filter all 124 JD files for job compatibility scoring.
Reads each JD file, extracts metadata, applies hard filters.
Outputs categorized list: SCOREABLE, DISQUALIFIED, or SKIP (no ICT content).
"""
import os
import re
from pathlib import Path
from datetime import datetime

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
JD_DIR = WORKDIR / "JD_FILES"

# Hard-reject keywords in body content
HARD_REJECT_KEYWORDS = [
    r'\bintern\b', r'\bstagiaire\b', r'\bvolunteer\b', r'\bunpaid\b',
    r'\bnutrition\b', r'\bagricultur\b', r'\bmedical\b', r'\bdoctor\b',
    r'\bnurse\b', r'\bteacher\b', r'\bhr\b', r'\blogistics\b',
    r'\bsupply chain\b', r'\bveterinar\b',
]

# ICT indicator keywords (titles must contain at least one)
ICT_KEYWORDS = [
    'it ', 'ict', 'ai ', 'artificial intelligence', 'telecom', 'connectivity',
    'innovation', 'digital transformation', 'software engineer', 'data scientist',
    'cybersecurity', 'cloud engineer', 'machine learning', 'devops', 'web developer',
    'full stack', 'database', 'data ', 'analytics', 'cirt', 'cyber', 'information systems',
    'platform solution', 'technical engineer', 'solution architect', 'software quality',
    'data engineer', 'instrumentation', 'digital ', 'technology', 'network',
    'automation', 'devops', 'front-end', 'frontend', 'ai-', 'genai', 'gen ai',
    'geospatial', 'gis ', 'remote sensing', 'lms ', 'moodle', 'canvas',
]

results = []

for agency_dir in sorted(JD_DIR.iterdir()):
    if not agency_dir.is_dir():
        continue
    agency_name = agency_dir.name.replace("UN_", "")
    
    for jd_file in sorted(agency_dir.glob("*.md")):
        content = jd_file.read_text(encoding='utf-8', errors='replace')
        body_lower = content.lower()
        title_from_file = jd_file.stem
        
        # Extract key metadata
        # Title - try to extract from first line or filename
        lines = content.split('\n')
        first_line = lines[0].strip().lstrip('#').strip() if lines else ""
        
        metadata = {
            'file': str(jd_file),
            'agency': agency_name,
            'filename': jd_file.name,
            'size_kb': round(len(content) / 1024, 1),
            'has_content': False,
            'ict_relevant': False,
            'disqualified': False,
            'disqualify_reason': '',
            'deadline': 'TBD',
            'grade': '',
            'location': '',
            'title_hint': first_line[:80] if first_line else title_from_file[:80],
        }
        
        # Check if file has actual JD content (duties/responsibilities/qualifications)
        for section_indicator in [
            "responsibilities", "duties", "qualifications",
            "work experience", "education", "job purpose",
            "accountabilities", "competencies", "requirements",
            "key accountabilities", "minimum requirements",
            "description of duties", "purpose of the post",
            "role description", "job description",
            "desired skills", "required qualifications"
        ]:
            if section_indicator in body_lower:
                metadata['has_content'] = True
                break
        
        if not metadata['has_content'] and len(content) < 2000:
            metadata['disqualified'] = True
            metadata['disqualify_reason'] = 'NO_JD_CONTENT'
            results.append(metadata)
            continue
        
        metadata['has_content'] = True
        
        # Extract deadline
        deadline_patterns = [
            r'deadline[:\s]+(\d{4}-\d{2}-\d{2})',
            r'closing date[:\s]+(\d{4}-\d{2}-\d{2})',
            r'application deadline[:\s]+(\d{4}-\d{2}-\d{2})',
            r'date posted[:\s]+.*?deadline[:\s]+(\d{4}-\d{2}-\d{2})',
        ]
        for pat in deadline_patterns:
            m = re.search(pat, content, re.IGNORECASE)
            if m:
                metadata['deadline'] = m.group(1)
                break
        
        # Extract grade
        grade_patterns = [
            r'(P-\d+)', r'(D-\d+)', r'(G-\d+)', r'(NO-\w+)',
            r'(GF|GG|GH)\b', r'(A\d{2})\b',
            r'grade[:\s]+(\S+)',
        ]
        for pat in grade_patterns:
            m = re.search(pat, content, re.IGNORECASE)
            if m:
                g = m.group(1)
                if len(g) < 10:
                    metadata['grade'] = g
                    break
        
        # Extract location/duty station
        loc_patterns = [
            r'duty station[:\s]+([^\n]+)',
            r'location[:\s]+([^\n]+)',
            r'place of assignment[:\s]+([^\n]+)',
        ]
        for pat in loc_patterns:
            m = re.search(pat, content, re.IGNORECASE)
            if m:
                loc = m.group(1).strip()
                if len(loc) < 100:
                    metadata['location'] = loc
                    break
        
        # If can't find from patterns, search body for common locations
        if not metadata['location']:
            for loc_kw in ['Geneva', 'New York', 'Vienna', 'Paris', 'Rome', 'Belgrade',
                          'Nairobi', 'Addis Ababa', 'Bangkok', 'Home Based', 'Remote',
                          'Valencia', 'Kabul', 'Manila', 'Bishkek', 'Apia', 'Samoa',
                          'Lusaka', 'Kampala', 'Dubai', 'Copenhagen', 'Brussels',
                          'London', 'Berlin', 'The Hague', 'Amman', 'Beirut']:
                if loc_kw.lower() in body_lower[:3000]:
                    metadata['location'] = loc_kw
                    break
        
        # Check ICT relevance in title
        title_check = title_from_file.lower().replace('_', ' ')
        ict_match = False
        for kw in ICT_KEYWORDS:
            if kw in title_check:
                ict_match = True
                break
        
        # Also check body for ICT keywords if title doesn't match
        if not ict_match:
            # Look for management-level ICT positions
            mgmt_ict_indicators = ['director', 'chief', 'head of', 'senior officer',
                                   'lead', 'manager', 'advisor']
            is_mgmt = any(ind in title_check for ind in mgmt_ict_indicators)
            
            body_ict_count = sum(1 for kw in ICT_KEYWORDS if kw in body_lower)
            if body_ict_count >= 5:  # Strong ICT signals in body
                ict_match = True
        
        metadata['ict_relevant'] = ict_match
        
        # Apply HARD FILTERS
        # 1. Nationals-only
        if re.search(r'\b(nationals?\s+only|national\s+position|local\s+recruitment)\b', body_lower):
            metadata['disqualified'] = True
            metadata['disqualify_reason'] = 'NATIONALS_ONLY'
            results.append(metadata)
            continue
        
        # 2. Ukraine
        if re.search(r'\bukraine\b', body_lower):
            metadata['disqualified'] = True
            metadata['disqualify_reason'] = 'UKRAINE'
            results.append(metadata)
            continue
        
        # 3. Internships/Traineeships/Volunteers
        if re.search(r'\bintern(?:ship)?\b', title_check, re.IGNORECASE) or \
           re.search(r'\btraineeship\b', title_check, re.IGNORECASE) or \
           re.search(r'\bvolunteer\b', title_check, re.IGNORECASE):
            metadata['disqualified'] = True
            metadata['disqualify_reason'] = 'INTERN_VOLUNTEER'
            results.append(metadata)
            continue
        
        # 4. Junior grades - P-2, G-5, NO-1 etc
        grade = metadata['grade']
        if grade:
            if re.match(r'P-?[12]\b', grade, re.IGNORECASE):
                metadata['disqualified'] = True
                metadata['disqualify_reason'] = 'GRADE_TOO_LOW_P2_OR_BELOW'
                results.append(metadata)
                continue
            if re.match(r'G-?\d\b', grade, re.IGNORECASE):
                metadata['disqualified'] = True
                metadata['disqualify_reason'] = 'GRADE_TOO_LOW_GSERIES'
                results.append(metadata)
                continue
            if re.match(r'NO-?[AB]\b', grade, re.IGNORECASE):
                metadata['disqualified'] = True
                metadata['disqualify_reason'] = 'GRADE_TOO_LOW_NOAB'
                results.append(metadata)
                continue
        
        # 5. Check hard-reject keywords in title
        for pat in HARD_REJECT_KEYWORDS:
            if re.search(pat, title_check, re.IGNORECASE):
                metadata['disqualified'] = True
                metadata['disqualify_reason'] = f'HARD_REJECT_TITLE_{pat.strip("\\b")}'
                break
        
        if metadata['disqualified']:
            results.append(metadata)
            continue
        
        # 6. Expired deadline (only for active vacancies, not rosters)
        if metadata['deadline'] != 'TBD' and 'roster' not in title_check:
            try:
                dl = datetime.strptime(metadata['deadline'], '%Y-%m-%d')
                if dl < datetime(2026, 6, 3):
                    metadata['disqualified'] = True
                    metadata['disqualify_reason'] = f'EXPIRED_{metadata["deadline"]}'
            except ValueError:
                pass
        
        if metadata['disqualified']:
            results.append(metadata)
            continue
        
        # If no ICT relevance and not a management role, skip
        if not ict_match:
            metadata['disqualified'] = True
            metadata['disqualify_reason'] = 'NON_ICT'
        
        results.append(metadata)

# Print summary
print("=" * 100)
print(f"PRE-FILTER RESULTS: {len(results)} files processed")
print("=" * 100)

scoreable = [r for r in results if not r['disqualified']]
disqualified = [r for r in results if r['disqualified']]

print(f"\n--- SCOREABLE: {len(scoreable)} ---")
for r in sorted(scoreable, key=lambda x: (x['agency'], x['deadline'])):
    print(f"  {r['agency']:12s} | G:{r['grade']:8s} | DL:{r['deadline']:12s} | {r['title_hint'][:55]}")

print(f"\n--- DISQUALIFIED: {len(disqualified)} ---")
for r in sorted(disqualified, key=lambda x: (x['disqualify_reason'], x['agency'])):
    reason = r['disqualify_reason'][:25]
    print(f"  [{reason:25s}] {r['agency']:10s} | {r['title_hint'][:55]}")

print(f"\n=== SUMMARY ===")
print(f"Total files: {len(results)}")
print(f"Scoreable:   {len(scoreable)}")
print(f"Disqualified:{len(disqualified)}")