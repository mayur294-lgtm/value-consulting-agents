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
and validated bottom-up against operational data. The recommendation is
anchored on the **CONSERVATIVE case**: **NPV** of $1.6M over five years,
**ROI** of 61%, **payback** in 3.2 years — the investment clears Meridian's
9% hurdle rate on conservative assumptions alone. The realistic planning
range is conservative-to-moderate ($1.6M–$4.1M NPV); the moderate case is
upside, not the basis of the recommendation. The bottom-up lever math is
reconciled lever-by-lever against the annual-report expense and income
pools (Section 3), and the conservative case remains NPV-positive even
with its two lowest-confidence assumptions degraded simultaneously
(Section 6.1).

## 2. Evidence Base

- **E01** — Digital onboarding completion 61% vs. 78% peer benchmark (client questionnaire, source: Q3 2026 onboarding funnel export).
- **E02** — Contact-centre volume ~145,000 calls/yr; 39% balance and servicing enquiries (client actuals, source: contact-centre ops dashboard).
- **E03** — Funded-account activation at 42% of the active retail base (client data export, source: core banking extract).
- **E04** — Average handle time for servicing calls 6.4 minutes (client actuals, source: workforce management system).
- **E05** — Branch teller transaction mix 34% low-complexity servicing (client interview, source: branch operations lead).

## 3. Top-Down Baseline and Reconciliation

Meridian Mutual's FY2025 annual report (statement of income) shows total
retail non-interest expense of $58M and net interest income of $132M. These
two lines define the top-down opportunity pools that bound every bottom-up
lever estimate in this case.

### 3.1 Lever-by-lever reconciliation (conservative case, average annual benefit)

Each lever is mapped to the annual-report line it draws from, and its
conservative-case benefit is expressed as a share of that line:

| Lever | Annual-report line (FY2025) | Avg annual benefit | % of line |
|---|---|---|---|
| Servicing deflection to digital | Retail non-interest expense, $58M | $0.55M | 0.9% |
| Branch low-complexity transaction shift | Retail non-interest expense, $58M | $0.25M | 0.4% |
| Onboarding completion uplift | Net interest income, $132M | $0.35M | 0.27% |
| Funded-account activation growth | Net interest income, $132M | $0.21M | 0.16% |
| **Total (conservative)** | | **$1.36M/yr ($6.8M over 5 yrs)** | |

### 3.2 Cross-check: do the two views agree?

- **Top-down envelope:** peer digital-efficiency programs in retail banking
  typically address 3–6% of the non-interest expense base over a five-year
  horizon (source: regional retail banking benchmark report, 2025). The
  cost-side levers here claim $0.80M/yr = **1.4% of the $58M pool** — at the
  low end of that envelope, as a conservative case should be.
- **Bottom-up build:** the same $1.36M/yr is derived independently from
  operational unit math (E02 call volumes × $4.10 unit cost; E01 funnel gap ×
  activation values), not allocated down from the pool.
- **Agreement:** the bottom-up total sits inside the top-down envelope with
  ~2× headroom, and the revenue-side levers claim under 0.5% of the NII line.
  The two estimation directions converge, with the bottom-up figure at the
  conservative end — the case does not depend on either view alone.
- **If they had disagreed:** any lever whose bottom-up estimate exceeded its
  top-down share of the pool would have been capped to the pool-implied
  figure; none required capping.

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

## 6. Headline Financials (CONSERVATIVE Case — recommendation anchor)

| Metric | Value |
|---|---|
| Total 5-yr benefits | $6.8M |
| Implementation + run cost | $3.4M (includes 15% contingency) |
| Net present value (NPV) | $1.6M |
| ROI | 61% |
| Payback period | 3.2 years |

**The go/no-go recommendation rests on these conservative figures alone:**
the investment clears Meridian's 9% hurdle rate without relying on any
upside materializing. Costs carry a 15% contingency; benefits ramp on a
sub-100% adoption curve (50% of target cohort by month 18, Assumption 4)
rather than assuming day-one run-rate.

Upside cases for planning context only — not the basis of the
recommendation: moderate NPV $4.1M (ROI 118%, payback 2.0 years);
aspirational NPV $7.9M (ROI 176%, payback 1.4 years). All figures are
pre-tax and undiscounted for cost, discounted at Meridian's stated 9%
hurdle rate for benefit streams.

### 6.1 Downside sensitivity on the conservative case

The conservative case is itself stress-tested against its two
lowest-confidence inputs:

| Stress | Effect on conservative NPV | Still above zero? |
|---|---|---|
| Deflected-call unit saving $4.10 → $3.10 (−25%, Assumption 2) | $1.6M → $1.1M | Yes |
| Activation balance growth 60bps → 30bps (−50%, Assumption 3) | $1.6M → $1.2M | Yes |
| Both stresses simultaneously | $1.6M → $0.7M | Yes |

Even with both low-confidence assumptions degraded simultaneously, the
conservative case remains NPV-positive at the 9% hurdle rate. If either
stress had driven NPV below zero, the recommendation would have been
deferred pending validation of that assumption — not rescued by citing the
moderate case.

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
