# Implementation Roadmap — Meridian Mutual Bank

> **Synthetic golden fixture.** This document is used only to exercise the
> `roadmap-prioritization` component eval
> (`evals/rubrics/component/specifics.py` → `_roadmap`). It contains no real
> client data. Meridian Mutual Bank and "Northland" are fictional; all
> phases, initiative cards, dependencies, gates, and figures below are
> fabricated for test purposes and must never be treated as real roadmap
> output.

## Approach

Initiatives are sequenced by dependency logic and value realization timing,
not by capability gap size alone. Each initiative card below ties back to a
capability gap identified in capability assessment and a value lever
quantified in the ROI model. Sequencing follows a phased model — Phase 1
(foundational), Phase 2 (scale), Phase 3 (optimize) — with explicit
dependencies and decision gates between phases so Meridian can validate value
before committing further investment.

## Phase 1 — Foundational (Months 1–6)

Phase 1 addresses the capability gaps with the highest evidence density and
the fewest upstream dependencies, so early wins fund the business case for
later phases.

### RI-01: Digital Onboarding Document Capture

- **Capability gap:** Manual KYC document upload with no in-line validation
  (capability assessment, Acquire — maturity 1/4).
- **Value lever:** Onboarding completion rate uplift (ROI model, Revenue
  lever).
- **Dependencies:** None — first initiative in sequence; no upstream
  dependency.
- **Owner:** Digital Channels team.

### RI-02: Contact-Centre Self-Service Deflection

- **Capability gap:** Balance and servicing questions routed to live agents
  with no self-service deflection (capability assessment, Activate —
  maturity 1/4).
- **Value lever:** Cost-to-serve reduction (ROI model, Cost lever).
- **Dependencies:** Depends on the identity and entitlements layer delivered
  under RI-01 (shared authentication component); cannot start build until
  RI-01 reaches integration testing.
- **Owner:** Contact-Centre Operations.

### RI-03: Funded-Account Activation Nudges

- **Capability gap:** No automated follow-up between account opening and
  funding (capability assessment, Activate — maturity 1/4).
- **Value lever:** Funded-account activation rate uplift (ROI model, Revenue
  lever).
- **Dependencies:** Depends on RI-01 (requires the onboarding event stream
  RI-01 produces as its trigger).
- **Owner:** Retail Operations.

**Decision Gate DG-1 (end of Phase 1):** Meridian's steering committee
reviews onboarding completion and funded-account activation against the
Phase 1 value realization targets before Phase 2 initiatives are funded. A
below-target result triggers remediation before proceeding, not automatic
continuation.

## Phase 2 — Scale (Months 7–14)

Phase 2 builds on the platform capabilities established in Phase 1 and
extends them into cross-sell and retention journeys.

### RI-04: Cross-Sell Next-Best-Action Engine

- **Capability gap:** CRM investment not translating into attach-rate
  improvement; no propensity-based targeting (capability assessment, Expand
  — maturity 1/4).
- **Value lever:** Cross-sell attach-rate uplift (ROI model, Revenue lever).
- **Dependencies:** Depends on RI-02 (reuses the customer interaction event
  data captured by the self-service deflection layer).
- **Owner:** Marketing & CRM.

### RI-05: Automated Renewal Outreach

- **Capability gap:** Renewal reminders sent as manual spreadsheet
  mail-merge with no lifecycle trigger (capability assessment, Retain —
  maturity 1/4).
- **Value lever:** Retention/attrition risk reduction (ROI model, Risk
  lever).
- **Dependencies:** Depends on RI-03 (reuses the nudge/notification
  infrastructure built for funded-account activation).
- **Owner:** Retail Operations.

**Milestone (mid-Phase 2):** First measured cross-sell attach-rate lift
reported against the Phase 2 baseline — an early value realization
checkpoint ahead of the Phase 2 decision gate, not a phase-closing gate
itself.

**Decision Gate DG-2 (end of Phase 2):** Steering committee reviews
cross-sell attach-rate and renewal-outreach coverage against target before
Phase 3 initiatives are funded.

## Phase 3 — Optimize (Months 15–20)

Phase 3 shifts branch staff capacity toward advisory work now that
low-complexity volume has been reduced upstream.

### RI-06: Branch Advisory Capacity Shift

- **Capability gap:** Teller time concentrated on low-complexity balance
  checks and simple transfers, limiting advisory availability (capability
  assessment, Retain — maturity 2/4).
- **Value lever:** Cost-to-serve reduction and advisory revenue uplift (ROI
  model, Cost and Revenue levers).
- **Dependencies:** Depends on RI-02 and RI-05 (requires deflection and
  renewal-automation volume reduction to be realized first; without those,
  there is no freed staff capacity to reallocate).
- **Owner:** Branch Operations.

**Decision Gate DG-3 (roadmap close):** Steering committee reviews
cumulative value realization across all three phases against the ROI model's
base case before confirming the roadmap as delivered.

## Data Gaps and Assumptions

- Sequencing assumes Phase 1 initiatives complete on the stated 6-month
  timeline; no formal capacity plan from Meridian's delivery team was
  available at time of writing, so phase durations are directional.
- Dependency chains above reflect logical build sequencing (shared
  components, event data reuse); they have not been validated against
  Meridian's actual engineering backlog and should be confirmed before
  Phase 1 kicks off.

## Next Steps

1. Validate Phase 1 sequencing and dependency assumptions with Meridian's
   engineering and delivery leads.
2. Confirm decision-gate criteria and thresholds with the steering committee
   before Phase 1 begins.
3. Route this roadmap to the narrative-assembler agent for inclusion in the
   final deliverable package.
