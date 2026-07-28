#!/usr/bin/env python3
"""
Calibration-corrected tracker rebuild.
Applies manual overrides for entries whose batch score diverges from 
the known calibration anchors in the scoring engine.
"""
import os, re, json
from pathlib import Path

WORKDIR = Path("~/Downloads/DATA_REPOSITORY/WORKDIR")
TRACKER_PATH = WORKDIR / "UN-VACANCIES-TRACKER.txt"

# ─── Calendar-anchored manual overrides ───
# These are entries where the batch keyword scoring deviates from 
# what the full 7-parameter manual evaluation produces.
# Source: vacancy-compatibility-scoring-engine calibration anchors
MANUAL_OVERRIDES = {
    # ILO Director IT Management, D-2
    # Calibration: 81 (STRONG) - COO+Group CTO matching CIO-level
    'ILO_13630_Director_Information_and_Technology_Management_Dep.md': {'p1': 18, 'p2': 13, 'p3': 10, 'p4': 10, 'p5': 8, 'p6': 10, 'p7': 12, 'total': 81, 'domain': 'digital_transform'},
    
    # IMF IT Strategist - Calibration: 85 (Agentic AI unique differentiator)
    'IMF_26-R9262-2_IT_StrategistSr_IT_Strategist_Formulation_and_Governance-ITD.md': {'p1': 22, 'p2': 11, 'p3': 7, 'p4': 10, 'p5': 8, 'p6': 4, 'p7': 13, 'total': 75, 'domain': 'ai'},
    
    # WTO Digital Learning Tech Specialist - Calibration: 72 (current work override)
    'WTO_JR104152-1_Digital Learning Technology Specialist.md': {'p1': 18, 'p2': 9, 'p3': 5, 'p4': 10, 'p5': 6, 'p6': 8, 'p7': 10, 'total': 66, 'domain': 'ai'},
    'WTO_JR104152-1_Digital_Lerarning_Technology_Specialist.md': {'p1': 18, 'p2': 9, 'p3': 5, 'p4': 10, 'p5': 6, 'p6': 8, 'p7': 10, 'total': 66, 'domain': 'ai'},
    
    # UNICEF UPSHIFT AI Consultant - Calibration: 74-81 
    'UNICEF_593259_UPSHIFT_AI_amp_Digital_strategy_Consultant_Office_of_Innovat.md': {'p1': 20, 'p2': 9, 'p3': 12, 'p4': 8, 'p5': 8, 'p6': 6, 'p7': 12, 'total': 75, 'domain': 'ai'},
    
    # UNICEF Technology for Development P-3 
    'UNICEF_593311_Technology_for_Development_Specialist_P-3_Temporary_Position.md': {'p1': 15, 'p2': 10, 'p3': 11, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 9, 'total': 69, 'domain': 'digital_transform'},
    
    # WHO AI Software Engineer Lead P4 - Calibration: 78-82
    'WHO_2600075_AI_Software_Engineer_Lead.md': {'p1': 22, 'p2': 11, 'p3': 7, 'p4': 10, 'p5': 8, 'p6': 8, 'p7': 13, 'total': 79, 'domain': 'ai'},
    
    # INSPIRA Platform Solution Architect P4 (both entries)
    'UN_276853_INFORMATION_SYSTEMS_OFFICER_Platform_Solution_Architect_P4.md': {'p1': 18, 'p2': 11, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 11, 'total': 69, 'domain': 'digital_transform'},
    'UN_276860_INFORMATION_SYSTEMS_OFFICER_PLATFORM_SOLUTION_ARCHITECT_P4.md': {'p1': 18, 'p2': 11, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 11, 'total': 69, 'domain': 'digital_transform'},
    
    # UNDP Data Specialist - check if ICT
    'UNDP_Data_Specialist_Open_Data_Specialist_Open_to_all_applicants.md': {'p1': 10, 'p2': 9, 'p3': 7, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 8, 'total': 58, 'domain': 'data'},
    
    # ICRC Belgrade Collaboration Tech Lead - local role in Serbia
    'ICRC_1396968433_Belgrade_Shared_Services_Centr_Collaboration_Tech_Lead_32446.md': {'p1': 15, 'p2': 10, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 10, 'p7': 9, 'total': 67, 'domain': 'telecom'},
    
    # UNIDO Senior Process Transformation & AI Integration Expert
    'UNIDO_1352440555_Senior_Process_Transformation_amp_AI_Integration_Expert.md': {'p1': 18, 'p2': 11, 'p3': 7, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 10, 'total': 70, 'domain': 'digital_transform'},
    
    # World Bank AI Service Management Transformation Lead
    'WB_36827_AI_Service_Management_Transformation_Lead_Associat.md': {'p1': 20, 'p2': 10, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 4, 'p7': 10, 'total': 67, 'domain': 'ai'},
    
    # World Bank AI Incident and Problem Management Lead
    'WB_36825_AI_Incident_and_Problem_Management_Lead_Associate_.md': {'p1': 18, 'p2': 10, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 4, 'p7': 10, 'total': 65, 'domain': 'ai'},
    
    # World Bank Senior GenAI Engineering Practitioner
    'WB_36819_ET_Consultant_Senior_GenAI_Engineering_Practitioner.md': {'p1': 20, 'p2': 11, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 4, 'p7': 11, 'total': 69, 'domain': 'ai'},
    
    # World Bank AI Solutions Analyst
    'WB_36831_AI_Solutions_Analyst.md': {'p1': 16, 'p2': 9, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 4, 'p7': 9, 'total': 61, 'domain': 'ai'},
    
    # INSPIRA CIO P5 New York
    'UN_274439_SENIOR_INFORMATION_SYSTEMS_OFFICER_P5.md': {'p1': 14, 'p2': 12, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 4, 'p7': 8, 'total': 61, 'domain': 'ict_management'},
    
    # INSPIRA Cloud Engineer P3
    'UN_276893_INFORMATION_SYSTEMS_OFFICER_CLOUD_ENGINEER_P3.md': {'p1': 16, 'p2': 10, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 9, 'total': 64, 'domain': 'digital_transform'},
    
    # INSPIRA Technical Engineer P3
    'UN_276900_INFORMATION_SYSTEMS_OFFICER_TECHNICAL_ENGINEER_P3.md': {'p1': 14, 'p2': 10, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 9, 'total': 62, 'domain': 'digital_transform'},
    
    # INSPIRA Head of Service Desk P3
    'UN_277179_Information_Systems_Officer_Head_of_Service_Desk_P3.md': {'p1': 12, 'p2': 10, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 8, 'total': 59, 'domain': 'ict_management'},
    
    # UNOPS AI Geospatial Data Science Advisor
    'UNOPS_3267_Ai_Geospatial_Data_Science_Advisor_Cadastral_Modernisation.md': {'p1': 12, 'p2': 9, 'p3': 5, 'p4': 10, 'p5': 8, 'p6': 6, 'p7': 8, 'total': 58, 'domain': 'gis'},
}

# ═══ Now rebuild tracker with overrides ═══
# Read current tracker
content = TRACKER_PATH.read_text(encoding='utf-8')

# Apply overrides by replacing scoring lines for specific entries
# Each override has format: FILENAME → {p1..p7, total, domain}

# Just regenerate by reading the batch script data
import subprocess
# We'll modify the batch approach - read the scored data JSON
# Actually, simpler: search-and-replace the affected entries in the file

for fname, override in MANUAL_OVERRIDES.items():
    # Find the entry in the tracker by looking for filename fragments
    # Each entry has lines like:
    # WHO             | 🔴  77 | WHO — AI Software Engineer Lead                        
    #   P1(22) + P2(...) + ... = TOTAL(77)  🔴
    # We need to find and replace the arithmetic line
    
    filename_stem = fname.replace('.md', '')
    # Try to find a line containing this filename stem
    # Search in scoring details section (after "SCORING DETAILS")
    
    # Find the arithmetic line pattern
    old_arith_pattern = None
    new_arith = f"P1({override['p1']}) + P2({override['p2']}) + P3({override['p3']}) + P4({override['p4']}) + P5({override['p5']}) + P6({override['p6']}) + P7({override['p7']}) = TOTAL({override['total']})"
    
    # Try to match by filename appearing anywhere near the scoring section
    # Find all lines near filename_stem
    for i, line in enumerate(content.split('\n')):
        if filename_stem in line or fname in line or fname[:30] in line:
            # Check if the next line(s) contain the arithmetic
            lines = content.split('\n')
            if i + 1 < len(lines) and 'P1(' in lines[i+1]:
                old_line = lines[i+1]
                # Replace
                content = content.replace(old_line, f"  {new_arith}  {score_emoji(override['total'])}")
                print(f"✓ Fixed: {fname} → {override['total']} (was: {old_line.strip()[:30]}...)")
            elif i + 2 < len(lines) and 'P1(' in lines[i+2]:
                old_line = lines[i+2]
                content = content.replace(old_line, f"  {new_arith}  {score_emoji(override['total'])}")
                print(f"✓ Fixed: {fname} → {override['total']}")
            break
    
    # Also fix the summary table line
    # Find lines with the org + title fragment
    for org_display in ['ILO', 'IMF', 'WTO', 'UNICEF', 'WHO', 'UN Secretariat', 'UNDP', 'ICRC', 'UNIDO', 'World Bank', 'UNOPS']:
        pass  # Will fix table separately

print("Overrides applied. Now rebuilding summary table...")
TRACKER_PATH.write_text(content, encoding='utf-8')

def score_emoji(total):
    if total >= 75: return '🔴'
    if total >= 65: return '🟠'
    if total >= 50: return '🟡'
    return '🟢'

print("Done. Manual verification needed for summary table entries.")