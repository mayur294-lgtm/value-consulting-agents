# Discovery Findings — Meridian Mutual Bank

> **Synthetic golden fixture.** This document is used only to exercise the
> `discovery-transcript-interpreter` component eval
> (`evals/rubrics/component/specifics.py` → `_discovery`). It contains no real
> client data. Meridian Mutual Bank and "Northland" are fictional; all
> figures, evidence IDs, and quotes below are fabricated for test purposes
> and must never be treated as real discovery output.

## 1. Evidence Register

Each item below is a discrete claim traced to a source quote or document,
tagged to the customer lifecycle stage it affects.

| ID | Claim | Quote / Source | Lifecycle Stage | Journey Step | Impact Type | Confidence | Source Type |
|---|---|---|---|---|---|---|---|
| E01 | Digital onboarding completion trails peer benchmark | "We lose about four in ten applicants somewhere in the KYC upload step." — Head of Digital, discovery interview | Acquire | Onboarding | Revenue | H | Interview |
| E02 | Contact-centre volume dominated by low-complexity servicing | "Balance and servicing questions are almost 40% of total call volume." — Contact-Centre Ops Lead, discovery interview | Activate | Servicing | Cost | H | Interview |
| E03 | Funded-account activation lags target | "Under half of new accounts actually get funded in the first 30 days." — Retail Ops Director, discovery interview | Activate | First Transaction | Revenue | M | Interview |
| E04 | Cross-sell attach rate flat despite CRM investment | "We bought the CRM two years ago and attach rate hasn't moved." — Head of Digital, discovery interview | Expand | Cross-sell | Revenue | M | Interview |
| E05 | Renewal/retention outreach is manual and inconsistent | "Renewal reminders still go out as a spreadsheet mail-merge." — Branch Operations Lead, discovery interview | Retain | Renewal | Risk | M | Interview |
| E06 | Teller time skewed toward low-complexity transactions | "A third of teller time is balance checks and simple transfers." — Branch Operations Lead, discovery interview | Retain | Branch Servicing | Cost | L | Interview |

## 2. Pain Point Register

Business problems mapped to customer lifecycle and journeys, each traced back
to the evidence above.

| ID | Pain Point | Business Impact | Lifecycle Stage | Journey Step | Evidence IDs | Severity |
|---|---|---|---|---|---|---|
| PP1 | Applicants abandon digital onboarding during document upload | Estimated lost new-account revenue; not yet quantified with client finance | Acquire | Onboarding | E01 | Critical |
| PP2 | Contact centre absorbs high volume of servicing questions that could self-serve | Elevated cost-to-serve; agent capacity constrained | Activate | Servicing | E02 | High |
| PP3 | New accounts opened but not funded within 30 days | Delayed revenue realization, weaker early-lifecycle engagement | Activate | First Transaction | E03 | High |
| PP4 | Cross-sell offers not converting despite CRM tooling | Missed expansion revenue on existing base | Expand | Cross-sell | E04 | Medium |
| PP5 | Manual renewal process increases attrition risk | Retention risk concentrated at renewal touchpoints | Retain | Renewal | E05 | Medium |
| PP6 | Branch staff time consumed by low-complexity transactions | Opportunity cost — staff unavailable for advisory conversations | Retain | Branch Servicing | E06 | Low |

## 3. Data Gaps and Assumptions

- Financial impact of onboarding abandonment (PP1) has not been quantified by
  Meridian's finance team — treat as a directional pain point pending
  validation, not a modeled dollar figure.
- Cross-sell attach-rate baseline (E04) was described qualitatively; no
  numeric attach-rate figure was provided and should be requested before ROI
  modeling proceeds.
- All evidence above comes from a single round of stakeholder interviews;
  no transaction-level data extract was available at time of writing.

## 4. Next Steps

1. Validate PP1 and PP3 quantification with Meridian's finance and retail
   operations teams before these feed the ROI model.
2. Request the missing cross-sell attach-rate baseline referenced in E04.
3. Route this Evidence Register and Pain Point Register to the
   capability-assessment agent for maturity scoring.
