# Scoring Calibration — UNICEF Vacancies (May 2026)

These calibrations were produced during a live rescore session against the CV repository.
Use as reference when encountering similar role patterns.

---

## 1. Behavioural Data Science Consultant — 593159 (Score: 63 → STRETCH)

**Before/After:** 73 (COMPETITIVE, generic) → 63 (STRETCH, evidence-grounded)

**Key dimensions that changed the score:**
- **RCT/Bayesian stats gap:** Role required experimental design (RCTs, Bayesian statistics). CV has NO documented RCT or Bayesian experience. Direct hit: -2 on requirements.
- **Africa experience differentiator:** 10 years living/working in Uganda, Zambia, Rwanda. Direct match for desirables. Saved the score from dropping further.
- **Consultant grade:** Below P-grade target but acceptable since candidate has served as UNICEF consultant since 2025.

**Pattern to watch for:** Data science consultant roles at UNICEF often require formal academic data science backgrounds (behavioural economics, experimental design). Candidate's NLP/AI evidence from agent frameworks is directionally aligned but not a direct substitute for academic credentials in these areas.

---

## 2. Digital Impact Officer (AI Applications Developer), P-2 — 593075 (Score: 59 → STRETCH)

**Before/After:** 94 (STRONG FIT, inflated) → 59 (STRETCH, correct)

**Key corrections:**
- **Pure SWE IC penalty (-20):** Role is "AI Applications Developer" — hands-on coding at P-2 grade. No management, no strategy. Candidate is an executive/AI product leader, not a junior developer.
- **P-2 grade:** Requires only 2 years experience. Candidate operates at P-4/P-5/D-2 level. While "too senior is not a penalty" per rules, the role is fundamentally entry-level professional.
- **Strategic alignment saved the score:** UNICEF Digital Impact Division (already consulted there) + AI focus (exact match) + Valencia (EU location) = 90.

**Pattern to watch for:** Any role with "Developer" or "Officer" in title at P-2/P-3 grade at UNICEF is likely a hands-on IC coding role. Apply Pure SWE IC penalty automatically. The only exception is if the JD specifically mentions strategy/leadership responsibilities.

---

## 3. UNICEF ID Range Pattern

During this session, a clear pattern emerged in UNICEF's PageUp job system:

| ID Range | Status | Notes |
|----------|--------|-------|
| **593xxx** | Live | All verified as active vacancies on the portal |
| **592xxx** | Not found | All returned "Sorry, we can't provide additional information about this job" |
| **593155** | Not found | Outlier — 593xxx but not live |

This suggests UNICEF may use the 592xxx range for draft/internal entries that were scanned before publication. The 593xxx range is the "published" range.

**Verification pattern for any TBD deadline:**
```bash
curl -sL "https://jobs.unicef.org/en-us/job/{VID}/" | grep -c "Job no:"
# 0 = not found
# 1+ = active
```

If 0 AND deadline is TBD → remove from tracker (draft, never published).  
If 1+ AND deadline is TBD → extract real deadline from `<span class="close-date"><time datetime="...">`.

---

## 4. Scoring Rules Applied (confirmed working)

These were applied correctly during this session and should be preserved as reference:

- **Pure SWE IC penalty (-20):** Applied to 593075 (AI Applications Developer, P-2). Correct.
- **"Too senior" NOT a penalty:** For 593075 (P-2), the score reflects grade mismatch but explicitly notes "per rules, too senior is not a penalty." The score wasn't reduced below 55 for seniority despite P-2 being 4 grades below candidate's anchor.
- **Evidence-first scoring:** Each dimension score was written with explicit evidence from CV §3 before the score was assigned.
- **Full JD required for scoring:** Both vacancies were scored after reading the full job page, not from the 44-char tracker title.
