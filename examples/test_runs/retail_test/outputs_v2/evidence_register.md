# Evidence Register

**Engagement:** Retail Bank - SEA Region
**Date:** 2026-01-13
**Prepared by:** Value Consulting Team

---

## Evidence Summary

| ID | Evidence Statement | Source Quote | Lifecycle Stage | Journey | Metric Type | Confidence | Source |
|----|-------------------|--------------|-----------------|---------|-------------|------------|--------|
| E1 | Low onboarding completion rate | "Our onboarding completion rate is low" | Acquire | Onboarding | Volume | Medium | Interview - Head of Retail |
| E2 | Document requirements cause customer drop-off | "A lot of customers drop off when documents are required" | Acquire | Onboarding | Volume | High | Interview - Head of Retail |
| E3 | Onboarding cycle time exceeds 7 days in some cases | "It can take more than a week in some cases" | Acquire | Onboarding | Time | High | Interview - Head of Retail |
| E4 | High servicing costs | "Servicing is expensive" | Retain | Servicing | Cost | Medium | Interview - Operations Lead |
| E5 | Simple requests still handled by high-cost channels | "Simple requests still come through the call center" | Retain | Servicing | Cost | High | Interview - Operations Lead |
| E6 | No visibility into customer channel preference | "We don't have a clear view of why customers choose branch or call over digital" | Retain | Servicing | Quality | High | Interview - Operations Lead |
| E7 | Digital onboarding launched but not scaling | "We launched digital onboarding, but it hasn't scaled well" | Acquire | Onboarding | Quality | High | Interview - Digital Lead |
| E8 | Manual workarounds prevalent | "Teams still rely on manual workarounds" | Acquire | Onboarding | Quality | High | Interview - Digital Lead |

---

## Pain Point Register

| ID | Pain Point | Business Impact | Lifecycle Stage | Journey | Evidence IDs | Severity |
|----|-----------|-----------------|-----------------|---------|--------------|----------|
| PP1 | Low onboarding completion rate | Lost customer acquisition, reduced revenue growth | Acquire | Onboarding | E1, E2 | Critical |
| PP2 | Document verification friction | Customer drop-off at critical conversion point | Acquire | Onboarding | E2 | Critical |
| PP3 | Extended onboarding cycle time | Poor customer experience, competitive disadvantage | Acquire | Onboarding | E3 | High |
| PP4 | Expensive servicing model | High cost-to-serve, margin pressure | Retain | Servicing | E4, E5 | High |
| PP5 | Channel shift failure | Simple requests consume expensive resources | Retain | Servicing | E5 | High |
| PP6 | Lack of customer journey analytics | Cannot optimize channel mix or personalize experience | Retain | Servicing | E6 | Medium |
| PP7 | Digital investment not delivering value | Sunk cost, need for remediation | Acquire | Onboarding | E7, E8 | High |
| PP8 | Process immaturity | Manual workarounds undermine automation | Acquire | Onboarding | E8 | High |

---

## Metric Register

| ID | Metric Name | Current Value | Unit | Source Evidence | Confidence | Notes |
|----|------------|---------------|------|-----------------|------------|-------|
| M1 | Onboarding completion rate | ~40% | % | E1 (implied) | Low | "Low" stated but not quantified; 40% assumed based on industry benchmarks for underperforming digital onboarding |
| M2 | Onboarding cycle time (max) | >7 days | days | E3 | High | Direct statement "more than a week in some cases" |
| M3 | Document drop-off rate | ~30-50% | % | E2 (implied) | Low | "A lot" suggests significant; industry range applied |
| M4 | Digital channel utilization | Unknown | % | E6 | N/A | No visibility into channel preference cited |
| M5 | Call center volume for simple requests | Unknown | volume | E5 | N/A | "Simple requests still come through" but volume not stated |

---

## Constraints & Risks Register

| ID | Constraint/Risk | Type | Impact on Engagement | Evidence IDs | Mitigation Notes |
|----|----------------|------|---------------------|--------------|------------------|
| CR1 | Limited quantitative data | Data | Cannot build precise ROI without baseline metrics | E1, E4, E6 | Use industry benchmarks with conservative assumptions |
| CR2 | Existing digital investment | Technical | May need to work with/around existing platform | E7 | Assess current platform capabilities before recommending |
| CR3 | Process maturity gaps | Organizational | Technology alone won't solve; need change management | E8 | Include adoption/change management in roadmap |
| CR4 | Unknown budget/timeline | Budget/Timeline | Cannot size recommendations appropriately | Intake form | Flag for validation with executive sponsor |

---

## Open Questions / Data Needed for ROI

| ID | Missing Data Point | Why Needed | Suggested Source | Priority for ROI |
|----|-------------------|-----------|------------------|------------------|
| DG1 | Current onboarding completion rate (%) | Baseline for improvement calculation | Digital analytics, onboarding system | Critical |
| DG2 | Monthly application volume | Scale for benefit calculation | Core banking system | Critical |
| DG3 | Average onboarding cycle time | Baseline for time reduction | Process mining or sample analysis | High |
| DG4 | Drop-off rate by step | Identify highest friction points | Funnel analytics | High |
| DG5 | Call center volume by request type | Size channel shift opportunity | Call center reporting | Critical |
| DG6 | Cost per call / branch visit / digital transaction | Calculate cost avoidance | Finance / Operations | Critical |
| DG7 | Digital adoption rate | Baseline for digital shift | Digital analytics | High |
| DG8 | Staff FTE costs | Calculate labor savings | HR / Finance | High |
| DG9 | Revenue per new customer (Year 1) | Value of acquired customers | Finance | High |
| DG10 | Customer lifetime value | Value of retention improvements | Finance / Analytics | Medium |

---

## Interpretation Notes

### Key Themes

1. **Onboarding Journey Broken**: Multiple evidence points (E1, E2, E3, E7, E8) indicate the onboarding journey is fundamentally broken despite digital investment. Document requirements are a major friction point, cycle times are unacceptable, and digital hasn't scaled.

2. **Servicing Inefficiency**: Evidence (E4, E5, E6) points to a costly servicing model where simple requests consume expensive channel resources. Lack of analytics prevents optimization.

3. **Investment Not Delivering**: The bank has invested in digital (E7) but isn't realizing value due to scaling issues and manual workarounds (E8). This is a remediation opportunity, not a greenfield build.

### Evidence Quality Assessment

- **Strong Evidence**: E2, E3, E5, E6, E7, E8 - Direct quotes with clear implications
- **Directional Evidence**: E1, E4 - Qualitative statements without quantification
- **Critical Gaps**: No quantitative baseline metrics provided; will require assumptions or follow-up data collection

### Recommendations for Next Steps

1. Request baseline metrics (DG1-DG10) before finalizing ROI model
2. Conduct journey mapping workshop to detail onboarding friction points
3. Analyze call center data to quantify channel shift opportunity
4. Assess existing digital platform to determine build vs. enhance approach
