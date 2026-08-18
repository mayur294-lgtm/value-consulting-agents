# ROI Pattern: Call Center Deflection via Digital Self-Service

> ⚠️ **SYNTHETIC-ORIGIN PATTERN — the numbers in this file are NOT real client data.**
> Harvested from a synthetic pipeline-test engagement ("Harborlight", 2026-07 — a fictional NAM credit union invented to validate the assessment pipeline).
> The value-lever structure, formulas, and applicability logic are reusable methodology and may be applied to real engagements.
> Every value tagged [Synthetic-Test] is fabricated. NEVER cite these numbers as benchmarks, baselines, or client-validated data in client work — source real figures from knowledge/domains/ or the Consulting Playbook Master benchmarks instead. (Values tagged [Client-Validated, ref] reference real named Backbase clients and remain valid.)


## Overview

Value model for reducing contact center call volume through digital self-service capabilities — in-app banking hub, account status notifications, self-service transactions — where a gap exists between what members call about and what the digital channel can currently handle.

**Domain Vertical:** Retail Banking, Credit Union

**Applicable To:**
- Banks / CUs where IVR deflection significantly underperforms the self-serviceable call ceiling (>15pp gap)
- Institutions with high per-call variable costs and high agent attrition
- Environments where missing digital features (e.g., card controls) generate structurally avoidable calls

**NOT Applicable To:**
- Complex, advisory-type calls (wealth management, business relationship banking)
- Outbound sales operations
- Call centers where >60% of calls are already deflected (diminishing returns model)

---

## Value Levers

### Lever 1 — Avoidable Call Volume Reduction

**Mechanism:** In-app self-service hub enables members to resolve balance inquiries, status checks, account changes, and transfers without calling. IVR deflection gap closes toward the self-serviceable ceiling.

**Formula:**
```
Annual_Savings = Annual_Non_Card_Calls
                 × (Self_Serviceable_% - Current_IVR_Deflection_%)
                 × Capture_Rate
                 × Variable_Cost_Per_Call
                 × Attribution_%
```

**Gap-Based Sizing Guidelines:**
- Self-serviceable ceiling: typically 35–50% of total call volume
- Current IVR deflection: poor = <15%; average = 20–30%; best-in-class = >50%
- Backbase capture rate at 40% moderate: ~40% of the IVR-to-ceiling gap
- Attribution: 75–85% Backbase-attributable (telephony/IVR investment partly independent)
- **Partition rule:** Remove binary missing-feature calls (e.g., card controls) before calculating this lever — model those separately at near-100% deflection

### Lever 2 — After-Call Work (ACW) Reduction

**Mechanism:** Agents receive pre-authenticated, in-context calls from members who already tried self-service. Average handle time and after-call work decrease.

**Formula:**
```
ACW_Savings = Non_Deflected_Calls_Remaining × AHT_Reduction_% × Current_AHT_min / 60 × FTE_Rate
```

**Typical AHT reduction:** 10–20% on remaining calls when in-app pre-authentication removes agent context assembly work.

---

## Data Points

### [Synthetic-Test-NAM-2026] — NAM Credit Union (2026)
- **Baseline:** 1,152,000 calls/year total; 42% self-serviceable; 11% IVR deflection; $6.40 variable cost/call
- **Call pool for this lever:** 1,070,400 non-card calls/year (card calls modeled separately as L4)
- **Backbase impact applied:** 20% of non-card pool (80% attribution × 12.4pp incremental deflection)
- **Calls deflected:** ~133,800/year
- **Annual savings (moderate scenario):** $1,370K/year
- **Confidence:** High
- **Notes:** 14× call density gap vs. BECU peer (233/1K members vs. 16.7/1K/month). Key sizing input: BECU operates at 16.7 calls/1K members — distance from client's 233/1K sets the theoretical ceiling for improvement. MyState Bank (Backbase) achieved −50% CC call volume as directional comparator.

---

## Benchmarks

| Metric | Poor | Average | Best-in-Class | NAM CU [Synthetic-Test] |
|--------|------|---------|---------------|---------------------------|
| IVR Self-Service Deflection Rate | <15% | 20–35% | >50% | 11% |
| Self-Serviceable Call Share | <25% | 30–45% | >50% | 42% |
| Variable Cost Per Call (NAM CU direct) | — | $5–8 | <$3 | $6.40 |
| Fully-Loaded Cost Per Call (NAM CU) | — | $20–30 | — | ~$25 |
| Calls per 1,000 Members / month | >200 | 50–150 | <20 | 233 |
| BECU peer CU calls / 1K members / month | — | — | 16.7 | [Industry/BECU] |
| Agent Annual Attrition | >25% | 15–25% | <15% | 31% |
| After-Call Work (minutes) | >3 min | 2–3 min | <1 min | 2.8 min |
| Screens Per Agent Per Call | >5 | 3–5 | 1–2 | 5 |

---

## Modeling Checklist

- [ ] Confirm monthly call volume and breakdown by call type/category
- [ ] Identify and separate binary missing-feature calls (model those as Lever: Card Controls)
- [ ] Confirm self-serviceable call share assessment (conduct call categorization audit if needed)
- [ ] Confirm variable cost per call (direct only — not fully loaded, unless doing full-base displacement)
- [ ] Apply 75–85% Backbase attribution; document rationale
- [ ] Confirm FTE absorption strategy (attrition, redeployment, not immediate headcount reduction)
- [ ] Set up call category tracking as measurement baseline before go-live

---

## Key Caveats

1. **FTE displacement vs. redeployment:** Savings should be modeled as cost avoidance via attrition absorption — not immediate headcount reduction. High agent attrition (30%+) supports this.
2. **Ramp time:** 15–18 months to full deflection benefit as member adoption of self-service habits forms.
3. **Pool partitioning is critical:** Including binary missing-feature calls in the general deflection model inflates the baseline and understates the impact of the dedicated feature deployment lever.

---

*Source: [Synthetic-Test-NAM-2026] (NAM CU, 2026) | BECU (NAM, 2025–2026) | MyState Bank (Backbase, APAC)*
*Confidence: HIGH for cost/volume benchmarks; MEDIUM for deflection rate improvement estimates*
*Created: 2026-07-28 | Auto-harvested by knowledge-harvester (pipeline mode)*
