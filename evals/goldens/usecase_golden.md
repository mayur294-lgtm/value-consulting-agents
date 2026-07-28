# Use Case Design Document — Meridian Mutual Bank (Northland)

> **Synthetic golden fixture.** Meridian Mutual Bank, "Northland," and all figures below
> are fictional, created solely to exercise the `usecase-designer` component eval
> (`specifics._usecase`). No client data, transcript content, or real Backbase account
> information is represented here. Do not use as a reference for an actual engagement.

## Context

Meridian Mutual Bank is a fictional retail bank serving the Northland region. Following
the completed Ignite workshops (strategy, member, employee, architecture — all
synthetic), this document designs the prioritized use cases against the Backbase
Product Directory, classifies each by build type, and assigns a priority tier.

Each use case below is linked to a Value Proposition theme, validated against the
Product Directory, and checked against Backbase Architecture guardrails. Where a
capability is not OOTB, the gap is stated conservatively rather than assumed away.

---

## UC-01 — Digital Account Opening (Retail Checking)

- **Value theme:** Reduce time-to-value for new-to-bank members
- **Product Directory mapping:** RB.1.2 (Digital Onboarding), RB.1.4 (Identity Verification)
- **Classification:** OOTB for the core onboarding flow; **config** required for
  Northland-specific KYC document set
- **Priority tier:** Tablestakes / P1
- **Notes:** Evidence from the member workshop indicated onboarding abandonment; this
  is a foundational capability rather than a differentiator, hence Tablestakes.

## UC-02 — Personal Loan Origination

- **Value theme:** Reduce cost-to-serve in lending operations
- **Product Directory mapping:** RB.3.1 (Loan Origination), RB.3.2 (Decisioning
  Integration)
- **Classification:** OOTB for application capture; **custom** integration required to
  Meridian's fictional legacy decisioning engine (no OOTB connector exists for this
  hypothetical core)
- **Priority tier:** Differentiating / P2
- **Notes:** Custom scope flagged conservatively — assumed until a real integration
  assessment is performed, per the assumptions register.

## UC-03 — Small Business Cash Management Dashboard

- **Value theme:** Deepen wallet share with Northland small-business members
- **Product Directory mapping:** WB.2.1 (Cash Management Dashboard), WB.2.3 (Multi-Entity
  Views)
- **Classification:** OOTB — dashboard widgets and entitlements ship as configurable
  out-of-the-box components
- **Priority tier:** Differentiating / P2
- **Notes:** No custom development identified; configuration effort limited to
  widget layout and entitlement rules.

## UC-04 — Card Controls and Instant Lock

- **Value theme:** Reduce fraud-related contact-center volume
- **Product Directory mapping:** RB.4.5 (Card Management)
- **Classification:** OOTB
- **Priority tier:** Tablestakes / P1
- **Notes:** Directly maps to a Product Directory capability already in general
  availability; no gap identified.

## UC-05 — Proactive Savings Nudges

- **Value theme:** Improve member financial wellness engagement
- **Product Directory mapping:** RB.5.2 (Financial Insights Engine)
- **Classification:** config for rule thresholds; **custom** required for the
  fictional Northland-specific nudge content library
- **Priority tier:** Differentiating / P3
- **Notes:** Lower priority — nice-to-have engagement layer, not required for launch.

---

## Summary Table

| ID    | Use Case                          | Product Directory | Classification | Priority Tier         |
|-------|------------------------------------|--------------------|-----------------|------------------------|
| UC-01 | Digital Account Opening            | RB.1.2, RB.1.4      | OOTB / Config   | Tablestakes (P1)       |
| UC-02 | Personal Loan Origination          | RB.3.1, RB.3.2      | OOTB / Custom   | Differentiating (P2)   |
| UC-03 | SMB Cash Management Dashboard      | WB.2.1, WB.2.3      | OOTB            | Differentiating (P2)   |
| UC-04 | Card Controls and Instant Lock     | RB.4.5               | OOTB            | Tablestakes (P1)       |
| UC-05 | Proactive Savings Nudges           | RB.5.2               | Config / Custom | Differentiating (P3)   |

## Assumptions

- Custom-build flags for UC-02 and UC-05 are conservative placeholders pending a real
  architecture deep-dive; they are not derived from an actual Meridian integration.
- Product Directory IDs are illustrative and follow Backbase's `RB.x.x` / `WB.x.x`
  numbering convention for Retail and Business Banking capability areas.
