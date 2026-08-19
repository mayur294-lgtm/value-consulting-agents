# ROI Pattern: Digital Membership / Account Onboarding Completion

> ⚠️ **SYNTHETIC-ORIGIN PATTERN — the numbers in this file are NOT real client data.**
> Harvested from a synthetic pipeline-test engagement — a fictional NAM credit union invented to validate the assessment pipeline (2026-07 synthetic test engagement; see tests/engagements/README.md).
> The value-lever structure, formulas, and applicability logic are reusable methodology and may be applied to real engagements.
> Every value tagged [Synthetic-Test] is fabricated. NEVER cite these numbers as benchmarks, baselines, or client-validated data in client work — source real figures from knowledge/domains/ or the Consulting Playbook Master benchmarks instead. (Values tagged [Client-Validated, ref] reference real named Backbase clients and remain valid.)


## Overview

Value model for improving digital application completion rates via streamlined onboarding flows — pre-fill from existing data, instant eIDV, reduced form steps, same-day account provisioning. Distinct from Digital Lending Origination (see `digital_lending_origination_roi.md`) — this applies to membership/deposit account onboarding.

**Domain Vertical:** Retail Banking, Credit Union

**Applicable To:**
- Banks/CUs with digital account application completion rates below 55%
- Institutions where abandonment leads to measurable competitor defection
- Credit unions with per-member profitability economics (rather than per-product margin)
- Institutions where branch acquisition costs significantly exceed digital acquisition costs

**NOT Applicable To:**
- Loan origination (see `digital_lending_origination_roi.md`)
- SME/Business account onboarding (different economics)
- Markets where digital onboarding completion is already above 70%

---

## Value Levers

### Lever 1 — Member Revenue Recovery from Completion Uplift

**Mechanism:** Improving digital application completion rate reduces the pool of applicants who abandon and defect to competitors. Each recovered applicant represents the long-run member relationship value.

**Formula:**
```
Annual_Revenue_Recovery = Total_Annual_Applications
                          × Abandonment_Rate
                          × Competitor_Defection_Rate
                          × Member_Annual_Profitability
                          × Backbase_Impact_%
```

**Key variables to validate:**
- Total application volume: often must be derived (e.g., flagged KYC cases ÷ flag rate) — flag as critical assumption
- Competitor defection rate: % of abandoners who open competitor account; validate via exit survey or CDO data
- Member annual profitability: use net (after costs), not gross revenue; typically $150–$350/year for NAM CUs

### Lever 2 — Account Funding Failure Recovery

**Mechanism:** Instant eIDV removes micro-deposit verification delays, reducing first-attempt funding failures among approved applicants.

**Formula:**
```
Funding_Recovery = Total_Annual_Applications
                   × Completion_Rate
                   × Funding_Failure_Rate
                   × Member_Annual_Profitability
                   × Backbase_Impact_%
```

### Lever 3 — Acquisition Channel Cost Reduction (Companion Lever)

**Mechanism:** As digital completion improves, channel mix shifts from branch ($310/member) toward digital ($95/member). Model as a separate lever with 70–80% attribution (channel shift is partly Backbase-enabled, partly a marketing/strategy decision).

See: Acquisition Channel Cost pattern (companion lever, often L9 in retail engagement framework).

---

## Data Points

### [Synthetic-Test-NAM-2026] — NAM Credit Union (2026)
- **Baseline completion rate:** 38%; abandonment: 62%; competitor defection: 44% within 2 weeks
- **First-attempt funding failure:** 19% (micro-deposit verification, 2-day delay)
- **Member annual profitability:** $212/year (CFO baseline, net of costs)
- **Application volume:** ~92,400/year — DERIVED (2,400 KYC cases/month ÷ 31% flag rate); LOW confidence; validate as OQ01
- **Annual benefit (moderate scenario):**
  - Completion uplift driver: $1,424K/year (14.5% Backbase impact on $9.8M revenue-at-risk pool)
  - Funding recovery driver: $664K/year (47% improvement on $1.4M funding failure pool)
  - **Total L1: $2,088K/year**
- **Confidence:** High (benchmarks and rates) / Low (application volume input — must validate)
- **Sensitivity:** ±25% on application volume = ±$522K/year
- **Comparable reference:** Eastern Bank (USA, Backbase 2023) — 69% funded accounts, 75% STP rate

---

## Benchmarks

| Metric | Poor | Average | Best-in-Class | NAM CU 2026 [Synthetic-Test] |
|--------|------|---------|---------------|-------------------------------|
| Digital Application Completion Rate | <35% | 35–55% | >70% | 38% |
| Abandonment Rate | >65% | 45–65% | <30% | 62% |
| Competitor Defection Rate (abandoners) | — | — | — | 44% within 2 weeks |
| First-Attempt Account Funding Failure | >20% | 10–20% | <5% | 19% |
| Digital Session Time (pre-abandon) | — | — | — | 22 min avg |
| Eastern Bank (Backbase) Funded Accounts | — | — | 69% | [Client-Validated, ref] |
| Eastern Bank STP Rate (Backbase) | — | — | 75% | [Client-Validated, ref] |
| Best-in-Class Completion Target | — | — | 80% | [Industry] |
| Branch Acquisition Cost (NAM CU) | — | — | — | $310/member [Synthetic-Test] |
| Digital Acquisition Cost (NAM CU) | — | — | — | $95/member [Synthetic-Test] |
| Member Annual Profitability (NAM CU) | — | — | — | $212/year [Synthetic-Test] |

---

## Engagement Pattern Notes

**Volume derivation workaround:** When total application volume is not directly available, derive it:
```
Est_Monthly_Applications = Manual_KYC_Cases / KYC_Flag_Rate
```
This is a LOW-confidence input. Flag explicitly and request validation as highest-priority data gap before board presentation. ±25% on this number has HIGH impact on model NPV.

**Competitor defection rate:** The 44% figure (applicants opening competitor account within 2 weeks) is a high-confidence signal. If unavailable, conservative proxy: 25–35% for typical credit union abandoners in competitive markets.

**Attribution note:** Do not apply a Backbase attribution discount to completion uplift — digital onboarding is 100% platform-dependent. Apply attribution discount only to channel shift companion lever.

---

## Modeling Checklist

- [ ] Confirm total digital application volume (highest-impact assumption — flag as critical data gap)
- [ ] Confirm competitor defection rate (exit survey or CDO data preferred)
- [ ] Confirm member annual profitability (net of costs, from CFO/Finance)
- [ ] Confirm first-attempt funding failure rate (digital analytics team)
- [ ] Confirm target completion rate is achievable (benchmark: Eastern Bank 69%; best-in-class 80%)
- [ ] Model Acquisition Channel Cost as companion lever (mutually exclusive populations with Lever 1)
- [ ] Set digital application completion rate as pre-implementation measurement baseline

---

*Source: [Synthetic-Test-NAM-2026] (NAM CU, 2026) | Eastern Bank (Backbase, USA 2023)*
*Confidence: HIGH for rate benchmarks; LOW for application volume inputs*
*Created: 2026-07-28 | Auto-harvested by knowledge-harvester (pipeline mode)*
