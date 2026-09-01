# ROI Pattern: In-App Card Controls Deployment

> ⚠️ **SYNTHETIC-ORIGIN PATTERN — the numbers in this file are NOT real client data.**
> Harvested from a synthetic pipeline-test engagement — a fictional NAM credit union invented to validate the assessment pipeline (2026-07 synthetic test engagement; see tests/engagements/README.md).
> The value-lever structure, formulas, and applicability logic are reusable methodology and may be applied to real engagements.
> Every value tagged [Synthetic-Test] is fabricated. NEVER cite these numbers as benchmarks, baselines, or client-validated data in client work — source real figures from knowledge/domains/ or the Consulting Playbook Master benchmarks instead. (Values tagged [Client-Validated, ref] reference real named Backbase clients and remain valid.)


## Overview

Value model for deploying self-service card management features (freeze/unfreeze, travel notifications, spend controls) when the feature is **entirely absent**. This is a binary deployment lever — not a continuous improvement lever — with near-100% structural deflection of the relevant call category.

**Domain Vertical:** Retail Banking, Credit Union

**Applicable To:**
- Banks/CUs with no in-app card freeze or travel notification capability
- Any institution where card management is 100% call-center-dependent
- High-volume card management call categories with no digital channel

**NOT Applicable To:**
- Institutions that already have basic card controls (improvement/enhancement model differs)
- Cards-as-a-service plays without a primary banking app
- Scenarios where card call volume is <2% of total CC volume (below quick-win threshold)

---

## Value Levers

### Lever 1 — Card Management Call Elimination

**Mechanism:** Binary — deploying in-app card controls eliminates the structural reason for the calls. Natural elimination rate: ~90% (peer CUs with controls report <5% residual card management calls). Model conservatively at 60% cap for conservative/moderate scenarios.

**Formula:**
```
Annual_Savings = Monthly_Card_Control_Calls × 12 × Variable_Cost_Per_Call × Deflection_Rate_Cap
```

**Deflection rate guidance:**
- Conservative/moderate: 60% cap (methodological ceiling for conservative modeling)
- Aggressive: 75–80% (still leaves 20–25% buffer for residual complex cases)
- Natural elimination (peer benchmark): ~90% — use only for qualitative "what good looks like" framing

### Lever 2 — Card Fraud Avoidance

**Mechanism:** Instant card freeze capability reduces the time-to-action when a member spots suspicious activity. Reduces fraud losses attributable to delayed member-initiated reporting.

**Formula:**
```
Fraud_Avoidance = Total_Card_Fraud_Losses × Member_Reportable_Fraction × Freeze_Reduction_Rate
```

**Benchmarks:**
- Industry standard: instant freeze capability reduces member-reportable fraud by 35–45% (Javelin Strategy, 2024)
- Member-reportable fraud as % of total: typically 10–20% of total card fraud losses; validate with client fraud analytics

---

## Data Points

### [Synthetic-Test-NAM-2026] — NAM Credit Union (2026)
- **Call baseline:** 6,800 card freeze/travel calls/month — 100% attributable to absent feature
- **Variable cost:** $6.40/call
- **Annual call cost baseline:** $522,240
- **Card fraud losses:** $2.1M/year total; 14% ($294K) attributable to no in-app freeze (slow member reporting)
- **Annual benefit (moderate, post-60% cap):** $431K/year
  - Card call deflection: $313,344/year (60% cap on $522,240)
  - Fraud avoidance: $117,600/year (40% of $294K attributable fraud)
- **Confidence:** Medium
- **Notes:** Highest-ratio quick win in the engagement (low integration complexity, single missing front-end feature). Recommended Phase 1 deployment. Minimal CoreBank integration required — card hub is primarily a front-end capability.

---

## Benchmarks

| Metric | With In-App Controls | Without Controls | Source |
|--------|----------------------|-----------------|--------|
| Residual card management calls | <5% of card call category | 100% reach live agents | [Client-creditunion-NAM-2025] peer [Industry] |
| Member-reportable fraud reduction | 35–45% | Baseline | Javelin Strategy 2024 [Industry] |
| Attributable fraud % (no freeze) | — | 10–20% of total fraud | [Synthetic-Test-NAM-2026] [Synthetic-Test] |
| Monthly card control calls (absent) | ~0 | 6,800/month | [Synthetic-Test-NAM-2026] [Synthetic-Test] |
| Variable cost per card call | $6.40 | $6.40 | [Synthetic-Test-NAM-2026] [Synthetic-Test] |

---

## Modeling Checklist

- [ ] Confirm monthly card management call volume (freeze + travel + spend limit calls)
- [ ] Confirm variable cost per call (direct only)
- [ ] Confirm total card fraud losses and % attributable to delayed member reporting
- [ ] Apply 60% deflection cap for conservative/moderate scenarios
- [ ] Confirm card hub requires minimal CoreBank integration (qualify as Phase 1 quick win)
- [ ] Separate this call pool from general self-service deflection lever (mutually exclusive populations)
- [ ] Flag as Phase 1 quick win: high ROI, low integration risk, high member satisfaction uplift

---

## Quick Win Qualification Criteria

Card controls deployment qualifies as a **Phase 1 quick win** when:
1. Card management calls are a named, measurable call category (not estimated)
2. Feature is truly absent (not limited/partial)
3. CoreBank integration is light (front-end card state management, not full processing)
4. Volume justifies prioritization: typically >3,000 card calls/month

---

*Source: [Synthetic-Test-NAM-2026] (NAM CU, 2026) | [Client-creditunion-NAM-2025] (NAM peer) | Javelin Strategy 2024*
*Confidence: MEDIUM — binary deployment, limited Backbase CU card controls case study comparator*
*Created: 2026-07-28 | Auto-harvested by knowledge-harvester (pipeline mode)*
