# ROI Business Case — Meridian Mutual Bank

> **Synthetic golden fixture.** This report is used only to exercise the
> `deliverables.roi` eval rubric (`evals/rubrics/deliverable/roi.py`). It
> contains no real client data. Meridian Mutual Bank and "Northland" are
> fictional; all figures, evidence IDs, and quotes below are fabricated for
> test purposes and must never be treated as a real business case.

## 1. Executive Summary

Meridian Mutual Bank (retail banking, Northland) asked for a business case to
prioritize digital onboarding and servicing-deflection investment. Discovery
evidence (E01–E05) shows onboarding completion trailing peers and a
contact-centre cost base concentrated in low-complexity servicing. This case
models three scenarios — **conservative**, **moderate**, and **aspirational**
— against a top-down baseline drawn from Meridian's most recent annual report
and validated bottom-up against operational data. Headline result (moderate
case): **NPV** of $4.1M over five years, **ROI** of 118%, **payback** in 2.0
years.

## 2. Evidence Base

- **E01** — Digital onboarding completion 61% vs. 78% peer benchmark (client questionnaire, source: Q3 2026 onboarding funnel export).
- **E02** — Contact-centre volume ~145,000 calls/yr; 39% balance and servicing enquiries (client actuals, source: contact-centre ops dashboard).
- **E03** — Funded-account activation at 42% of the active retail base (client data export, source: core banking extract).
- **E04** — Average handle time for servicing calls 6.4 minutes (client actuals, source: workforce management system).
- **E05** — Branch teller transaction mix 34% low-complexity servicing (client interview, source: branch operations lead).

## 3. Top-Down Baseline

Meridian Mutual's FY2025 annual report (statement of income) shows total
retail non-interest expense of $58M and net interest income of $132M. This
top-down baseline is used to sanity-check the bottom-up lever estimates below:
modeled benefits stay under 8% of the retail non-interest expense line in
every scenario, consistent with the conservative-bias standard for this
engagement type.

## 4. Value Levers

| Lever | Evidence | Basis | Direction |
|---|---|---|---|
| Onboarding completion uplift | E01 | Peer-benchmark gap closure | Revenue uplift |
| Servicing deflection to digital | E02, E04 | Call-volume reduction | Cost avoidance |
| Funded-account activation growth | E03 | Balance growth on activated accounts | Revenue uplift (NII) |
| Branch low-complexity transaction shift | E05 | Teller time reallocation | Cost avoidance |

## 5. Scenarios

| Scenario | Description | 5-yr Total Benefit |
|---|---|---|
| Conservative | 25% of the peer-benchmark gap closed; deflection limited to easiest call types | $6.8M |
| Moderate | 45% of the peer-benchmark gap closed; base case adoption curve | $11.2M |
| Aspirational | 65% of the peer-benchmark gap closed; accelerated digital adoption | $15.9M |

## 6. Headline Financials (Moderate Case)

| Metric | Value |
|---|---|
| Total 5-yr benefits | $11.2M |
| Implementation + run cost | $3.4M |
| Net present value (NPV) | $4.1M |
| ROI | 118% |
| Payback period | 2.0 years |

Conservative case NPV: $1.6M, ROI 61%, payback 3.2 years. Aspirational case
NPV: $7.9M, ROI 176%, payback 1.4 years. All figures are pre-tax and
undiscounted for cost, discounted at Meridian's stated 9% hurdle rate for
benefit streams.

## 7. Assumptions Register

Every load-bearing input below carries an explicit source and confidence
rating; none should be treated as fact without validation by Meridian's
finance team.

| # | Assumption | Confidence | Source |
|---|---|---|---|
| 1 | Peer onboarding benchmark of 78% completion holds for Northland retail segment | Medium | source: regional retail banking benchmark report, 2025 |
| 2 | Average deflected call saves $4.10 in fully-loaded contact-centre cost | Medium | source: contact-centre unit cost model, FY2025 |
| 3 | Funded-account activation uplift carries 60bps average balance growth | Low | source: core banking extract + finance team interview |
| 4 | Digital adoption curve reaches 50% of target cohort by month 18 | Medium | source: Meridian digital adoption roadmap, 2026 |

## 8. Risks and Caveats

- Deflection benefit assumes no offsetting increase in digital-channel
  escalations; not yet validated against escalation-rate data.
- Activation-growth lever (E03) has the lowest confidence rating and should
  be re-underwritten once Q4 actuals are available.
- This is a synthetic fixture — none of the figures above should be reused
  in a real Meridian Mutual engagement.

## 9. Next Steps

1. Validate assumptions 1–4 with Meridian finance and operations leads.
2. Confirm hurdle rate and discounting convention with Meridian treasury.
3. Re-run the model once Q4 activation actuals land (see Risk 2).
