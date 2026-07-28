# IOM Oracle Cloud Extraction Guide

## Access
- URL: `https://fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs`
- **No login required** for search and browse
- JS-rendered Oracle Cloud SPA
- Previously blocked at `iom.int/careers` (bot detection) — use this URL instead
- Total jobs: ~174

## Extraction via Browser

### Step 1: Navigate (no login needed)
```javascript
browser_navigate(url="https://fa-evlj-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs")
```

### Step 2: Search for ICT keywords
The page has a search combobox. Type keywords and click search:
```javascript
browser_type(ref="e15", text="information technology")  // or "ICT", "digital", etc.
browser_click(ref="e12")  // Search for Jobs button
```

### Step 3: Extract job results
After search, job cards containing title, location, grade, deadline are rendered:
```javascript
// Extract all job titles containing ICT keywords
var text = document.body.innerText;
var lines = text.split('\n');
var jobs = [];
for (var i = 0; i < lines.length; i++) {
  var line = lines[i].trim();
  if (line.length > 20 && line.length < 300 && 
      /Officer|Specialist|Analyst|Manager|Director|Coordinator|Advisor|Engineer|Technician|Consultant/i.test(line) &&
      !/search|filter|keyword|location|how to|welcome|important|failure|technical assistance|talentpool|manage|menu|skip|apply now|previously|profile|notice|step|guide|warning/i.test(line)) {
    jobs.push(line);
  }
}
```

## Known ICT Job Titles Found (validated):
- Information and Communications Technology (ICT) Officer (P)
- CFA - ICT Officer (Solution Technology) (P)
- National Information and Communications Technology Officer (NO.A)
- Graphic Designer (Consultant)
- Various consultant roles

## Pagination
The Oracle Cloud portal is JS-rendered with client-side pagination. The total count (174) is visible but only ~15 jobs render per page. Browser search with keywords is the most effective way to narrow results.
