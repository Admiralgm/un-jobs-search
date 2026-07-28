# UN Compensation Calculator — P-1 to D-2 (Professional & Higher Categories)

## Source Data

**Salary scale:** ICSC "Salaries and Allowances Booklet" (PDF) — Annex I
- Latest: https://icsc.un.org/Resources/SAD/Booklets/sabeng.pdf
- Contains gross + net base salary for P-1 through D-2, Steps I–XIII

**Post Adjustment (PA) multiplier per duty station:**
- ICSC Data page: https://icsc.un.org/Home/DataPostAdjustment
- XML (all duty stations): https://icsc.un.org/Resources/COLD/PostAdjustmentReports/Classifications/pac_DSID_xml.xml
- Switzerland (Geneva) code: `SWI001`
- PA multiplier as of May 2026: **90.7%** for Geneva

**Pensionable Remuneration:**
- ICSC booklet Annex XI — P-1 to D-2, Steps I–XIII
- Staff contribution: ~7.9%, Organization: ~15.8%

**Hardship/Mobility allowances:**
- ICSC booklet Annex VI, Table 2
- H (HQ/EU) duty stations = no hardship allowance
- A = no hardship, B–E = increasing hardship

---

## Formula

```
Net Remuneration = Net Base Salary × (1 + PA_Multiplier / 100)

Example (P-4 Step VI, Geneva, PA=90.7):
  Net Base = $93,882
  Post Adj = $93,882 × 0.907 = $85,151
  Net Remuneration = $93,882 + $85,151 = $179,033/yr
  Monthly take-home = $179,033 ÷ 12 = $14,919/mo
```

---

## P-4 Salary Scale (effective 1 Jan 2025, USD)

| Step | Gross/yr | Net Base/yr | PA @ 90.7% | Net Remun/yr | Monthly |
|------|----------|-------------|------------|--------------|---------|
| I    | $107,389 | $84,672     | $76,798    | $161,470     | $13,456 |
| II   | $110,020 | $86,514     | $78,468    | $164,982     | $13,749 |
| III  | $112,653 | $88,357     | $80,139    | $168,496     | $14,041 |
| IV   | $115,283 | $90,198     | $81,810    | $172,008     | $14,334 |
| V    | $117,914 | $92,040     | $83,480    | $175,520     | $14,627 |
| VI   | $120,546 | $93,882     | $85,151    | $179,033     | $14,919 |
| VII  | $123,181 | $95,727     | $86,824    | $182,551     | $15,213 |
| VIII | $125,813 | $97,569     | $88,495    | $186,064     | $15,505 |
| IX   | $128,444 | $99,411     | $90,166    | $189,577     | $15,798 |
| X    | $131,071 | $101,250    | $91,834    | $193,084     | $16,090 |
| XI   | $133,709 | $103,096    | $93,508    | $196,604     | $16,384 |
| XII  | $136,334 | $104,934    | $95,175    | $200,109     | $16,676 |
| XIII | $138,967 | $106,777    | $96,847    | $203,624     | $16,969 |

---

## Estimating Step for New Hires

Typical step placement for new P-4:
- **Step I–IV:** 8–10 yrs experience, standard match
- **Step V–VII:** 10–14 yrs, strong match, some leadership
- **Step VIII–X:** 15+ yrs, senior specialist or team lead
- **Step XI–XIII:** rare for new hires; reserved for internal promotions or exceptional candidates

**Rule of thumb:** If candidate matches the minimum 8 yrs and is a strong fit, assume Step VI–X for the estimate range.

---

## Hardship Allowance (if applicable)

Only for B–E duty stations. P-4 falls in "Group 2":

| Category | Annual |
|----------|--------|
| A        | $0     |
| B        | $7,330 |
| C        | $13,440 |
| D        | $17,130 |
| E        | $22,000 |

Geneva = H = no hardship.

---

## Other Notable Benefits (add to "total package" narrative, not cash estimate)

| Benefit | Approx Value |
|---------|-------------|
| Education grant | Up to ~$31,500/child/yr (sliding scale) |
| Children's allowance | ~$2,929/child/yr |
| Spouse allowance | ~6% of net remuneration |
| UN pension (employer) | ~15.8% of pensionable remuneration |
| Health insurance subsidy | ~$8,000–10,000/yr |
| Home leave travel | Round-trip every 2 yrs for family |
| Rental subsidy | 80% of rent above 30% of net remuneration threshold |
| Repatriation grant | 2–4 months salary on separation |

---

## UNJSPF Pension — Contribution & Projection

### Contribution Rate
Total to UNJSPF: **23.7%** of pensionable remuneration.
- **Staff member pays 7.9%** (deducted monthly)
- **Employer pays 15.8%**

### Accumulation Rates (post-1983 participants)

| Years of Service | Rate per Year |
|-----------------|-------------|
| 1–5 | 1.50% |
| 6–10 | 1.75% |
| 11–35 | 2.00% |
| 36+ | 1.00% |
| **Cap** | **70% of FAR** |

### Eligibility
- **Auto-enrollment:** Mandatory at appointment ≥6 months or after 6 months continuous service
- **Minimum for any pension:** 5 years contributory service
- **Normal retirement age:** 65
- **Early retirement age:** 55 (benefit reduced 6%/yr before 65)
- **With less than 5 years:** Withdrawal settlement only (contributions + 3.25% interest back; employer share stays in Fund)

### Pension Formula
> **Annual pension = FAR × Accumulation Rate × Years of Service**

Where **FAR** = Final Average Remuneration = average of highest 36 months pensionable remuneration in last 5 years.

### Deferred Retirement Benefit (≥5 years, leave before 65)
- Pension starts at age 65 (or early at 55+ with reduction)
- Grows with ~2%/yr COLA between separation and payout
- Includes survivor benefit for spouse (50% of accrued)
- No child benefit once deferred (only when beneficiary reaches NRA)

### Early Retirement (≥5 years, separate at 55+)
- Immediate pension, reduced by 6% for each year before 65
- Can commute up to 1/3 into lump sum
- Includes survivor + child benefits

### Withdrawal Settlement (lump sum)
Available as alternative to deferred/early pension:
- Contributions back + 3.25% compound interest
- Plus 10% boost per year of service beyond 5 (max +100% at 15 yrs)
- After cash-out: no future pension or survivor benefits

### Projection Example: P-4 Step VI Start, Promoted to P-5 ~yr 8

| Years Served | Accum % | Est FAR | Deferred at 65/yr | At 65 Monthly | Lump Sum |
|-------------|--------|--------|------------------|--------------|---------|
| 5 | 7.50% | $228K | ~$25K/yr | ~$2,100/mo | ~$96K |
| 7 | 11.00% | $228K | ~$36K/yr | ~$3,000/mo | ~$166K |
| 10 | 16.25% | $238K | ~$52K/yr | ~$4,300/mo | ~$318K |
| 15 | 26.25% | $247K | ~$79K/yr | ~$6,600/mo | ~$703K |

**Early retirement at 55 (15yr):** ~$26K/yr (~$2,200/mo, reduced ~60%)

### P-4 Contribution Table (Pensionable Remuneration, Feb 2025 scale)

| Step | Pensionable Remuneration | Your 7.9%/yr | Monthly | Employer 15.8%/yr |
|------|------------------------|-------------|--------|-----------------|
| I | $196,274 | $15,506 | $1,292 | $31,011 |
| VI | $219,034 | $17,304 | $1,442 | $34,607 |
| X | $237,242 | $18,742 | $1,562 | $37,484 |

### Key Notes
- Pension is **defined benefit** (guaranteed, not market-dependent)
- Contributions earn 3.25% interest while active (only matters for withdrawal settlement)
- Pension payments ARE taxable in country of residence (unlike salary which is tax-free)
- The COLA (~2%/yr) between separation and payment can significantly increase the real benefit
- **The deferred pension almost always beats the lump sum if the recipient lives past 78–80**

---

## How to Get the PA Multiplier

```bash
# Download the current post adjustment XML
curl -s "https://icsc.un.org/Resources/COLD/PostAdjustmentReports/Classifications/pac_DSID_xml.xml" \
  | grep -A8 "SWI001"  # replace SWI001 with the duty station code
```

**Known duty station codes:** SWI001 (Geneva), USA001 (New York), VIE001 (Vienna), ITA001 (Rome), GBR001 (London), FRA001 (Paris), NLD001 (The Hague), THA001 (Bangkok), ETH001 (Addis Ababa), KEN001 (Nairobi).

---

## Pensionable Remuneration Scale — P-1 to P-5 (Feb 2025)

| Grade | Step I | Step VI | Step X | Step XIII |
|-------|--------|--------|--------|---------|
| P-5 | $237,959 | $261,544 | $280,416 | $294,573 |
| P-4 | $196,274 | $219,034 | $237,242 | $250,899 |
| P-3 | $160,870 | $181,643 | $198,461 | $211,111 |
| P-2 | $124,571 | $142,781 | $157,641 | $168,795 |
| P-1 | $96,074 | $111,424 | $123,701 | $132,905 |

---

## Quick Reference: All P-Grades (Net Base, Step VI)

| Grade | Net Base/yr (Step VI) | Geneva Net Remun (×1.907) | Monthly |
|-------|----------------------|--------------------------|---------|
| P-1   | $49,618              | $94,621                  | $7,885  |
| P-2   | $62,789              | $119,738                 | $9,978  |
| P-3   | $78,737              | $150,151                 | $12,513 |
| P-4   | $93,882              | $179,033                 | $14,919 |
| P-5   | $111,084             | $211,837                 | $17,653 |
| D-1   | $127,317             | $242,793                 | $20,233 |
| D-2   | $141,201             | $269,270                 | $22,439 |
