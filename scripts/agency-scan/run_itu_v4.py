#!/usr/bin/env python3
"""ITU v4 — Camoufox browser for JS-rendered SuccessFactors pages.

Problem: ITU detail pages load JD content via JavaScript.
Scrapling gets HTML shell only (no JD text).
All 30 old files were empty of real JD content.

Strategy: Use Camoufox to render each detail page, extract inner_text,
clean navigation noise, save proper JD content.
"""
import re, html as html_mod
from datetime import datetime
from pathlib import Path
from camoufox.sync_api import Camoufox

BASE_DIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES")
DIR = BASE_DIR / "UN_ITAR"
DIR.mkdir(exist_ok=True)

# Actually ITU:
DIR = BASE_DIR / "UN_ITU"

HARD_REJECT = re.compile(
    r"(travel|voyage|chef.*section|section.*chef|head.*section|junior project officer|"
    r"evaluation.*consultant|independent evaluation)", re.I)

ICT_TITLE_KW = [
    "digital", "ict", "information", "technology", "cyber", "software", "data",
    "cloud", "network", "system", "telecom", "innovation", "ai", "artificial",
    "connectivity", "platform", "technical", "engineer", "developer", "it ", " it",
    "ict ", " ict", "full stack", "fullstack", "devops", "devsecops",
    "machine learning", "computer", "web", "database", "infrastructure", "security",
    "geospatial", "gis", "metadata", "api ", "microservices", "blockchain",
    "iot ", "automation", "robotics", "middleware", "erp ", "crm ",
    "business intelligence", "bi developer", "etl", "data warehouse", "data lake",
    "site reliability", "noc ", "isp ", "telecommunications", "broadband",
    "fiber", "fibre", "satellite", "mobile", "wireless",
    "help desk", "technical support", "it support", "it manager", "it director",
    "it officer", "it specialist", "it coordinator", "it project",
    "chief information", "chief technology", "chief digital", "cto", "cio",
    "head of it", "head of digital", "head of technology",
    "collaboration tech", "information management", "knowledge management",
    "learning solutions", "edtech", "educational technology",
    "agentic ai", "mcp", "generative ai", "llm",
    "prompt engineering", "vector database", "retrieval augmented",
    "digital ecosystem", "digital inclusion", "geospatial data science",
    "ai geospatial", "data science", "data engineer", "data architect",
    "data management", "data officer", "data analyst",
    "platform solution", "cloud engineer", "cloud architect",
    "emerging tech", "emerging technolog", "transformation",
    "cybersecurity", "cirt", "incident response",
    "software developer", "software engineer", "metadata engineer",
    "ux researcher", "ux ", "user experience",
    "child online protection", "disaster preparedness", "emergency telecom",
    "smart villages", "smart islands", "digital skills", "capacity development",
    "statistics", "statistical", "statistician",
    "investigator", "fcdo", "technical support", "coordination",
    "digital policy", "regulatory", "economic and market",
    "consultant", "roster",
]

ICT_BODY_KW = [
    "python", "java", "javascript", "sql", "nosql", "react", "angular", "vue",
    "node.js", "typescript", "html", "css", "rest api", "graphql",
    "azure", "aws", "gcp", "terraform", "ansible", "jenkins", "gitlab", "github",
    "ci/cd", "linux", "unix", "firewall", "vpn", "siem", "zero trust",
    "deep learning", "neural network", "nlp", "computer vision",
    "data pipeline", "data integration", "data quality", "data governance",
    "digital transformation", "artificial intelligence", "generative ai",
    "api integration", "system integration", "infrastructure as code",
    "containerization", "site reliability engineering", "observability",
    "agile", "scrum", "devops", "microservices", "kubernetes", "docker",
    "satellite", "remote sensing", "earth observation", "geospatial", "gis",
    "mapping", "spatial analysis", "cartographic", "geodata",
    "machine learning", "data analysis", "data processing",
    "quality assurance", "quality control", "training module",
    "e-learning", "lms", "learning management",
]

def is_ict_title(title):
    t = " " + title.lower() + " "
    return any(kw in t for kw in ICT_TITLE_KW)

def is_ict_body(text):
    return any(kw in text.lower() for kw in ICT_BODY_KW)

def sanitize(name):
    name = urllib_parse.unquote(name)
    return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\-_\s]', '', name).strip())[:60]

def extract_jd_from_rendered(text):
    """Extract JD content from Camoufox-rendered page text."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # JD start markers
    JD_START = [
        'organizational unit', 'expertise', 'description', 'background',
        'objective', 'purpose', 'scope', 'functions', 'responsibilities',
        'duties', 'requirements', 'qualifications', 'competencies',
        'key areas', 'long description', 'main tasks', 'org. setting',
        'job description', 'about this role', 'position overview',
        'what you will do', 'your responsibilities', 'role overview',
        'assignment', 'contractor will', 'consultant will',
    ]
    JD_END = [
        'how to apply', 'application deadline', 'closing date',
        'equal opportunity', 'diversity and inclusion', 'fraud alert',
        'scam alert', 'report misconduct', 'social media', 'copyright',
        'privacy notice', 'terms of use', 'disclaimer',
        'similar jobs', 'share this job', 'apply now', 'back to',
    ]
    
    jd_start = 0
    for i, line in enumerate(lines):
        if any(m in line.lower() for m in JD_START):
            jd_start = i
            break
    
    jd_end = len(lines)
    for i, line in enumerate(lines):
        if any(m in line.lower() for m in JD_END) and i > jd_start + 3:
            jd_end = i
            break
    
    if jd_start >= jd_end:
        return ""
    
    return '\n'.join(lines[jd_start:jd_end])

import urllib.parse as urllib_parse

# All ITU jobs from the previous scrape
ITU_JOBS = [
    ("957375555", "Home Based Child Online Protection Consultant Roster", "/job/Home-Based-Child-Online-Protection-Consultant-Roster/957375555/"),
    ("1147959055", "Home Based Roster Circular Economy Consultant Latin America", "/job/Home-Based-Roster-Circular-Economy-Consultant-Latin-America/1147959055/"),
    ("1147955155", "Home Based Roster Circular Economy Consultant Africa Region", "/job/Home-Based-Roster-Circular-Economy-Consultant-Africa-Region/1147955155/"),
    ("1327373955", "Home Based Roster Full Stack Engineer Consultant", "/job/Home-Based-Roster-Full-Stack-Engineer-Consultant/1327373955/"),
    ("993610255", "Home Based Roster Consultant for Senior ICT/Digital Policy, Regulatory, Economic and Market for Africa", "/job/Home-Based-Roster-Consultant-for-Senior-ICTDigital-Policy%2C-Regulatory%2C-Economic-and-Market-for-Africa/993610255/"),
    ("1153253155", "Home Based Roster Senior ICT/Digital Consultant for the Americas", "/job/Home-Based-Roster-Senior-ICTDigital-Consultant-for-the-Americas/1153253155/"),
    ("1170425755", "Home Based Roster Consultants for capacity and digital skills development", "/job/Home-Based-Roster-Consultants-for-capacity-and-digital-skills-development/1170425755/"),
    ("1341821555", "Home Based Roster UX Researcher Consultant", "/job/Home-Based-Roster-UX-Researcher-Consultant/1341821555/"),
    ("1147953755", "Home Based Roster Circular Economy Consultant Asia Region", "/job/Home-Based-Roster-Circular-Economy-Consultant-Asia-Region/1147953755/"),
    ("948745855", "Home Based BDT Digital Ecosystem Consultant Roster", "/job/Home-Based-BDT-Digital-Ecosystem-Consultant-Roster/948745855/"),
    ("941800455", "Home Based Disaster Preparedness Consultant National Emergency Telecom Plans and Mobile Early Warning", "/job/Home-Based-Disaster-Preparedness-Consultant-National-Emergency-Telecom-Plans-and-Mobile-Early-Warning/941800455/"),
    ("1341822255", "Home Based Roster Kaizen and Process Improvement Consultant", "/job/Home-Based-Roster-Kaizen-and-Process-Improvement-Consultant/1341822255/"),
    ("1169838155", "Home Based Roster Investigator Consultant", "/job/Home-Based-Roster-Investigator-Consultant/1169838155/"),
    ("1353420555", "Home Based Innovation Ecosystem Consultant", "/job/Home-Based-Innovation-Ecosystem-Consultant/1353420555/"),
    ("1152178755", "Home Based Roster Green Digital transformation Consultant", "/job/Home-Based-Roster-Green-Digital-transformation-Consultant/1152178755/"),
    ("1335756755", "Home Based Roster Senior CIRT Governance and Policy Consultant", "/job/Home-Based-Roster-Senior-CIRT-Governance-and-Policy-Consultant/1335756755/"),
    ("1326634655", "Home Based Roster Emerging Technologies for Digital Transformation Consultant for Asia and the Pacific", "/job/Home-Based-Roster-Emerging-Technologies-for-Digital-Transformation-Consultant-for-Asia-and-the-Pacific/1326634655/"),
    ("1352319255", "Geneva Roster Software Developer and Metadata Engineer Consultant for Open Code Infrastructure (OCI)", "/job/Geneva-Roster-Software-Developer-and-Metadata-Engineer-Consultant-for-Open-Code-Infrastructure-%28OCI%29/1352319255/"),
    ("1337227855", "Home Based Roster ITU FCDO Technical Support and Coordination Consultant", "/job/Home-Based-Roster-ITU-FCDO-Technical-Support-and-Coordination-Consultant/1337227855/"),
    ("993659455", "Multiple duty stations Roster Consultant on Smart Villages and Smart Islands (Asia Pacific)", "/job/Multiple-duty-stations-Roster-Consultant-on-Smart-Villages-and-Smart-Islands-%28Asia-Pacific%29/993659455/"),
    ("935798155", "Home Based Roster for Telecommunication/ICT Statistics Programme", "/job/Home-Based-Roster-for-TelecommunicationICT-Statistics-Programme/935798155/"),
    ("959263055", "Geneva Technical Remote Participation Moderator Roster", "/job/Geneva-Technical-Remote-Participation-Moderator-Roster/959263055/"),
    ("962961855", "Home Based Disaster Preparedness Consultant Roster", "/job/Home-Based-Disaster-Preparedness-Consultant-Roster/962961855/"),
    ("1335794555", "Home Based Roster Senior CIRT Technical and Operations Consultant", "/job/Home-Based-Roster-Senior-CIRT-Technical-and-Operations-Consultant/1335794555/"),
    ("1348117555", "Home Based Roster Emerging Technology Consultant", "/job/Home-Based-Roster-Emerging-Technology-Consultant/1348117555/"),
    ("1352437155", "Geneva Junior Project Officer", "/job/Geneva-Junior-Project-Officer/1352437155/"),
    ("1349955955", "Geneva Chef(fe) de la Section des voyages", "/job/Gen%C3%A8ve-Chef%28fe%29-de-la-Section-des-voyages/1349955955/"),
    ("1335797655", "Home Based Roster Senior National Cybersecurity Strategy Consultant", "/job/Home-Based-Roster-Senior-National-Cybersecurity-Strategy-Consultant/1335797655/"),
    ("1349956055", "Geneva Head Travel Section", "/job/Geneva-Head-Travel-Section/1349956055/"),
    ("1350959255", "Home Based Roster Evaluation Consultant", "/job/Home-Based-Roster-Evaluation-Consultant/1350959255/"),
]

def main():
    print(f"ITU v4 Camoufox — {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Total jobs to process: {len(ITU_JOBS)}")
    
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        saved = 0
        skipped = 0
        errors = 0
        
        for jid, title, url_path in ITU_JOBS:
            url = f"https://jobs.itu.int{url_path}"
            out = DIR / f"ITU_{jid}_{sanitize(title)[:60]}.md"
            
            if out.exists():
                print(f"  SKIP {jid}: exists")
                skipped += 1
                continue
            
            # Check if ICT
            if not is_ict_title(title):
                print(f"  SKIP {jid}: not ICT ({title[:50]})")
                skipped += 1
                continue
            
            print(f"  Fetching {jid}...")
            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                
                text = page.inner_text("body")
                jd_text = extract_jd_from_rendered(text)
                
                if not jd_text or len(jd_text) < 200:
                    print(f"    SKIP {jid}: no JD content")
                    skipped += 1
                    continue
                
                if not is_ict_body(jd_text):
                    print(f"    SKIP {jid}: body not ICT")
                    skipped += 1
                    continue
                
                header = (f"# {title}\n\n**Job ID:** {jid}\n**URL:** {url}\n"
                          f"**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n")
                out.write_text(header + jd_text, encoding="utf-8")
                saved += 1
                print(f"    SAVED: {title[:55]} ({len(jd_text)} chars)")
                
            except Exception as e:
                print(f"    ERROR {jid}: {str(e)[:60]}")
                errors += 1
    
    total = len(list(DIR.glob("ITU_*.md")))
    print(f"\nDONE: {saved} saved, {skipped} skipped, {errors} errors, total: {total}")

if __name__ == "__main__":
    main()
