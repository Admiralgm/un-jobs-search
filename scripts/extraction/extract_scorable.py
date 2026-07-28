#!/usr/bin/env python3
"""Strip cookie banners and score top candidates. Pipe through grep to find real content."""
import sys
base = "~/Downloads/DATA_REPOSITORY/JOBS-RAW-EXTRACT"

# List files and their real JD content (skip cookie consent sections)
files = {
    "IP_1213548": "ECMWF Team Leader ML Engineering (A3 grade)",
    "IP_1213133": "EMBL AI Engineer",
    "IP_1214260": "CERN DevOps Engineer GitLab (GRAE)",
    "IP_1214787": "NATO Software Development Engineer",
    "IP_1215512": "NATO Sr Concept Dev Cyberspace Operationalisation",
    "IP_1215305": "NATO Head Service Management Branch",
    "IP_1214311": "World Bank Associate Product Owner GF",
    "IP_1214619": "World Bank Ops Analyst Data Scientist",
    "IP_1214327": "UNICEF Behavioural Data Science Consultant",
    "IP_1212579": "UNJSPF IS Officer Platform Solution Architect P-4",
    "IP_1215257": "ESA Earth Observation Service Manager",
    "IP_1211193": "UNDP check",
    "IP_1193626": "Interpol Cloud Architect EC2",
    "IP_1200445": "EMBL Senior Full-stack Web Developer",
    "IP_1175924": "EBRD Azure Infrastructure Quality Engineer",
}

import os
for vid, desc in sorted(files.items()):
    for fname in os.listdir(f"{base}/impactpool"):
        if fname.startswith(vid):
            fpath = f"{base}/impactpool/{fname}"
            with open(fpath) as f:
                text = f.read()
            # Find real content after cookie banner
            idx = text.find("Application deadline")
            if idx == -1:
                idx = text.find("Salary and Grade")
            if idx == -1:
                idx = text.find("About the")
            if idx == -1:
                idx = text.find("Duties")
            if idx == -1:
                idx = text.find("Key Responsibilities")
            if idx == -1:
                idx = len(text) // 2  # middle of file
            
            # Get 30 lines from the relevant section
            lines = text[idx:idx+3000].split('\n')[:30]
            content = '\n'.join(l for l in lines if l.strip())
            
            print(f"\n{'='*60}")
            print(f"{vid}: {desc}")
            print(f"{'='*60}")
            print(f"{content[:2000]}")
            break