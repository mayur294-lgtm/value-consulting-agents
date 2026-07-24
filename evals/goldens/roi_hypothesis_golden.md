# ROI Hypothesis Tree — Golden Fixture (Synthetic)

> **Disclaimer:** This is a fully synthetic fixture created for eval testing only.
> "Meridian Mutual Bank" and "Northland" are fictional. All figures, quotes, and
> evidence references are illustrative and MUST NOT be cited, reused, or presented
> to any real client. No real client data, transcripts, or benchmarks were used
> in producing this file.

## Problem Statement

Meridian Mutual Bank, a retail bank serving the Northland region, is losing
value across three linked areas of the retail deposit and lending business:
manual account-opening processing, high-cost contact-center servicing for
routine requests, and slow personal-loan decisioning that depresses funded
volume. The problem type is a **cost-to-serve and growth-leakage problem**
driven by manual, paper-based, and siloed processes rather than a single root
cause — so the hypothesis tree below decomposes it into independently
testable levers rather than assuming one fix.

Success = a defensible, conservative estimate of annual value at stake across
these levers, each traceable to a specific operational root cause with
evidence (or an explicit assumption where evidence is thin).

---

## MECE Lever Tree

The tree below is Mutually Exclusive, Collectively Exhaustive across three
levers: account-opening efficiency (L1), contact-center deflection (L2), and
loan-decisioning speed-to-funding (L3). Each lever is traced through the
required four-link causal chain: **Root Driver → Operational Change →
Volume/Rate Impact → Financial Impact**.

### L1 — Reduce Manual Account-Opening Processing Cost

- **Root Driver:** New retail deposit accounts are opened through a paper
  intake form re-keyed by branch staff into three disconnected systems (core,
  CRM, compliance), with no straight-through processing.
- **Operational Change:** Introduce a digital, guided account-opening flow
  with single data entry and automated KYC checks, removing the re-keying
  step for the majority of applications.
- **Volume/Rate Impact:** Assume ~40,000 new retail accounts opened annually
  (conservative, mid-point of Northland peer range); estimate 70% of these
  shift from manual re-keying (~18 minutes/account) to straight-through
  processing (~4 minutes/account) — a Volume/Rate Impact of roughly
  28,000 accounts x 14 minutes saved.
- **Financial Impact:** ~6,500 processing hours saved annually at a fully
  loaded branch-staff cost of $38/hour ≈ **$247K/year** in labor cost
  avoidance. Conservative case assumes only 50% of the identified time savings
  is realized (staff redeployed rather than headcount reduced), i.e.
  ~$124K/year.

### L2 — Deflect Routine Contact-Center Volume to Self-Service

- **Root Driver:** 45% of contact-center calls are routine, low-complexity
  requests (balance inquiries, card block/unblock, address changes) that
  currently require a live agent because self-service digital channels do not
  cover these intents.
- **Operational Change:** Extend the mobile/online banking app with
  self-service flows for the top five routine intents and add proactive
  in-app guidance to reduce the need to call in the first place.
- **Volume/Rate Impact:** Assume ~600,000 contact-center calls/year at
  Meridian scale; routine-intent calls are ~270,000/year. Assume a
  conservative 35% deflection rate to self-service (below the 45–55% range
  seen in comparable digital deflection programs) — a Volume/Rate Impact of
  ~94,500 calls/year deflected.
- **Financial Impact:** At a fully loaded cost of $6.20 per handled call,
  94,500 deflected calls ≈ **$586K/year** in avoided servicing cost. This is
  the base case; the assumptions register flags the deflection rate as
  unvalidated and recommends confirming with Meridian's contact-center
  vendor before this number is used in a client-facing model.

### L3 — Accelerate Personal-Loan Decisioning to Capture Funded Volume

- **Root Driver:** Personal-loan applications sit in a manual underwriting
  queue with a 4.5-day average decision time, causing an estimated 12%
  applicant drop-off (abandonment to a faster competitor) between
  application and funding.
- **Operational Change:** Introduce automated decisioning for
  low-risk/low-exception applications using existing bureau and internal
  data, reducing decision time for that segment from 4.5 days to same-day.
- **Volume/Rate Impact:** Assume ~14,000 personal-loan applications/year;
  roughly 55% qualify as low-risk/low-exception. Conservatively assume the
  drop-off rate for this segment falls from 12% to 7% (not to zero) once
  decisioning is same-day — a Volume/Rate Impact of ~385 additional funded
  loans/year (7,700 qualifying applications x 5-point drop-off reduction).
- **Financial Impact:** At an average funded loan balance of $9,500 and a net
  interest margin of 4.1%, ~385 incremental funded loans ≈ **$150K/year** in
  incremental net interest income (Year 1 run-rate; excludes any fee income
  as a conservative simplification).

---

## Summary Table

| Lever | Root Driver (short) | Annual Financial Impact (conservative) |
|-------|---------------------|------------------------------------------|
| L1 | Manual re-keying at account opening | ~$124K/year |
| L2 | No self-service for routine call intents | ~$586K/year |
| L3 | Manual underwriting queue delays decisioning | ~$150K/year |

**Total conservative value at stake (pre-financial-modeling scenario work):
~$860K/year.** This hypothesis tree hands off to the financial modeler for
scenario construction (conservative/base/upside), sensitivity testing, and
formal ROI computation — the figures above are directional lever-sizing only,
not a finished business case.

## Assumptions Register

| # | Assumption | Confidence | Validation Needed |
|---|-----------|-----------|--------------------|
| A1 | 40,000 new accounts/year at Meridian | Medium | Confirm with Meridian ops reporting |
| A2 | 35% self-service deflection rate achievable | Low | Validate with contact-center vendor benchmark |
| A3 | Drop-off reduction from 12% to 7% with same-day decisioning | Medium | Validate against Meridian's own funnel data |
