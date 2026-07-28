
import os, re
path = '~/Downloads/DATA_REPOSITORY/UN_SECTOR_VACCANCIES.txt'
with open(path, 'r') as f:
    content = f.read()

def get_actual_id(url):
    # Try finding any segment that is purely digits and > 5 chars (common for job IDs)
    segments = re.findall(r'/(\d{5,})/?', url)
    if segments:
        return segments[-1] # Return the last numeric segment
    
    # Try query parameters
    m = re.search(r'[?&](?:id|jobId|vacancyId|job_id)=(\d+)', url, re.I)
    if m:
        return m.group(1)
        
    # Standard VN/REQ patterns
    m = re.search(r'(REQ-\d+|VN-\d+|VN\s?\d+/\d+)', url, re.I)
    return m.group(1) if m else None

blocks = content.split('================================================================================')
new_blocks = []
count = 0

for i, block in enumerate(blocks):
    if '- VACANCY ID: ' in block:
        url_match = re.search(r'- HYPERLINK: (https?://[^\n]+)', block)
        if url_match:
            actual_id = get_actual_id(url_match.group(1))
            if actual_id:
                old_id_line = re.search(r'- VACANCY ID: (.*)', block)
                if old_id_line:
                    old_id = old_id_line.group(1).strip()
                    if old_id.startswith('VAC-'):
                        block = block.replace(f'- VACANCY ID: {old_id}', f'- VACANCY ID: {actual_id}')
                        count += 1
            else:
                # If no ID in URL, search block for common ID labels
                # e.g., VN 2024/12 or Job Id: 12345
                id_pattern = re.search(r'(?:REQUISITION ID|JOB ID|REFERENCE|JO#|REF#|Vacancy No):?\s*([A-Z0-9_\-/]+)', block, re.I)
                if id_pattern:
                    old_id_line = re.search(r'- VACANCY ID: (VAC-\d+)', block)
                    if old_id_line:
                        block = block.replace(old_id_line.group(1), id_pattern.group(1))
                        count += 1
                    
    new_blocks.append(block)

new_content = '================================================================================'.join(new_blocks)

with open(path, 'w') as f:
    f.write(new_content)
os.system('sync')
print(f'Updated {count} internal IDs to actual IDs.')
