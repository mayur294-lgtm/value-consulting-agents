# Digital Banking Capability Assessment — Meridian Mutual Bank

> **Synthetic golden fixture.** This report exists only to exercise the
> `deliverables.report` eval rubric (`evals/rubrics/deliverable/report.py`).
> It contains no real client data. Meridian Mutual Bank and "Northland" are
> fictional; every figure, evidence ID, and quote below is fabricated for
> test purposes and must never be reused in a real engagement.

## Client and Engagement

Meridian Mutual Bank is a retail bank operating in Northland. Meridian asked
for an evidence-based assessment of its digital onboarding and servicing
capabilities ahead of a 2026 modernization decision. This report synthesizes
discovery evidence, a current-state capability assessment, and a financial
case into a single recommendation for Meridian's executive committee.

## Executive Summary

Meridian's digital onboarding completion rate trails the regional peer
benchmark by 16 points, and 41% of contact-centre volume is low-complexity
servicing that peers handle through self-service. Both gaps are corroborated
by client-provided operational data (E01, E02, E03) rather than by vendor
assertion. Closing them would move Meridian toward peer parity on cost-to-
serve without requiring a core banking replacement. Our recommendation is a
**Conditional Go**: proceed with a phased digital onboarding and servicing-
deflection investment, conditional on Meridian's finance team validating the
three medium/low-confidence assumptions in Section 5 before funds are
committed. This is a moderate-case, conservatively modeled recommendation —
not a guaranteed outcome.

## 1. Evidence Base

- **E01** — Digital onboarding completion 62% vs. 78% regional peer
  benchmark (client questionnaire, source: Q3 2026 onboarding funnel
  export).
- **E02** — Contact-centre volume ~150,000 calls/yr; 41% balance and
  servicing enquiries (client actuals, source: contact-centre ops
  dashboard).
- **E03** — Funded-account activation at 40% of the active retail base
  (client data export, source: core banking extract).
- **E04** — Average onboarding drop-off concentrated at the identity-
  verification step, cited in 6 of 9 stakeholder interviews (client
  interview notes).
- **E05** — No self-service balance-transfer capability in the current
  online banking platform (architecture review, source: platform capability
  inventory).

## 2. Current-State Capability Assessment

| Capability | Current State | Evidence | Gap vs. Peer Benchmark |
|---|---|---|---|
| Digital onboarding | Manual identity-verification hand-off; no straight-through processing | E01, E04 | 16-point completion gap |
| Self-service servicing | No balance-transfer or limit-change self-service | E02, E05 | 41% of contact-centre volume is deflectable-class |
| Funded-account activation | Activation tracked but not actively nudged post-opening | E03 | 40% activation vs. 55% benchmark median |

Each row above traces to at least one evidence item; none of these gaps are
inferred without a corroborating source. Confidence in the onboarding and
servicing gaps is high (multiple independent sources); confidence in the
activation gap is medium (single data export, not yet cross-checked against
finance).

## 3. Business Impact

The onboarding and servicing gaps are not isolated UX issues — they carry a
recurring cost. Contact-centre volume tied to low-complexity servicing (E02)
is a direct operating-expense line; onboarding drop-off (E01, E04) is a
foregone-revenue line, since incomplete applications do not convert to
funded accounts. We size both in the companion ROI model; this report does
not restate those figures beyond the range in Section 4, to avoid presenting
one number as more precise than the underlying data supports.

## 4. Financial Case (Summary)

| Metric (5-yr, moderate case) | Value |
|---|---|
| Total modeled benefit | $8.4M |
| Net present value | $3.1M |
| Payback | 2.3 years |

These figures come from the companion ROI model, which brackets the moderate
case with conservative and aspirational scenarios (25% and 65% peer-gap
closure respectively). We report the moderate case here because it is the
scenario finance should plan against; the conservative case should be used
for any board-level commitment.

## 5. Recommendation

**Conditional Go.** Meridian should proceed with a phased digital onboarding
and servicing-deflection initiative, gated as follows:

1. Fund a discovery-to-design phase now — the underlying gaps (E01, E02,
   E03) are well-evidenced and low-risk to act on.
2. Withhold full-program funding until Meridian's finance team validates
   Assumptions 2 and 3 below (see Assumptions Register) — both are
   medium/low confidence and load-bearing for the NPV figure.
3. Re-underwrite the activation lever once Q4 activation actuals are
   available, since E03 is a single-source data point.

This is a measured, not an enthusiastic, recommendation: the case clears the
bar for a phased commitment, not for an unconditional large-scale build.

## 6. Assumptions Register

Every assumption below carries an explicit source and confidence rating.
None should be treated as fact without the stated validation step.

| # | Assumption | Source | Confidence |
|---|---|---|---|
| 1 | Regional peer onboarding benchmark of 78% completion applies to Meridian's Northland retail segment | BENCHMARK — regional retail banking benchmark report, 2025 | Medium |
| 2 | Average deflected call saves $4.05 in fully-loaded contact-centre cost | DERIVED — contact-centre unit cost model, FY2025 | Medium |
| 3 | Funded-account activation uplift carries a conservative 55bps average balance growth (below the 70bps peer median, to avoid an optimistic-to-help-the-case estimate) | ESTIMATE — finance team interview, cross-checked against core banking extract | Low |
| 4 | Identity-verification friction (E04) is the dominant onboarding drop-off cause, not a confounding channel issue | CLIENT DATA — 6 of 9 stakeholder interviews | Medium |

Assumption 3 is the most load-bearing and lowest-confidence input in this
report; it should be the first item Meridian's finance team validates before
any funding decision.

## 7. Risks and Caveats

- The servicing-deflection benefit assumes no offsetting increase in
  digital-channel escalations; this has not been validated against
  escalation-rate data and could erode net savings if wrong.
- The activation lever (E03, Assumption 3) rests on a single data export
  and the lowest confidence rating in this report — do not commit
  board-level funding against it until re-underwritten.
- This is a synthetic fixture: none of the figures, evidence IDs, or
  quotes above are real and none should be reused in an actual Meridian
  Mutual engagement.

## 8. Next Steps

1. Validate Assumptions 1–4 with Meridian's finance and operations leads
   before committing full-program funding.
2. Re-run the activation lever once Q4 actuals are available (Risk 2).
3. Confirm the discovery-to-design phase scope and timeline with Meridian's
   digital and contact-centre leads.

---

**Provenance** — Generated by narrative-assembler agent (synthetic fixture
run) on 2026-06-24. Source agents: discovery-transcript-interpreter,
capability-assessment, roi-financial-modeler. Evidence register: E01–E05,
above.
