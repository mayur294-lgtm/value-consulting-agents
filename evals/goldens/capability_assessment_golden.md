# Digital Banking Capability Assessment — Meridian Mutual Bank

> **Synthetic golden fixture.** This document exists only to exercise the
> `capability-assessment` component eval (`evals/rubrics/component/specifics.py`
> → `_capability`). Meridian Mutual Bank and "Northland" are fictional; every
> capability ID, score, and evidence reference below is fabricated for test
> purposes and must never be reused in a real engagement.

## 1. Executive Summary

Meridian Mutual Bank's retail capabilities are strongest in the Back-office
layer (core ledger, payments settlement) and weakest in the Front-office
layer (digital onboarding, self-service servicing), with the Middle-office
layer (case management, workflow orchestration) trailing just behind. Using
the standard 0-4 maturity scale, six capabilities were scored across all
three layers against evidence from the Discovery Evidence Register (E01–E06).
The two lowest-scoring capabilities — digital identity verification and
self-service servicing — account for the majority of the onboarding and
contact-centre gaps sized in the companion ROI model. One capability,
proactive fraud-pattern detection, was flagged as an **Unconsidered Need**:
Meridian had not raised it during discovery, but evidence from the
architecture review implies it is a material gap.

## 2. Methodology

Each capability below is scored 0–4 on the standard maturity scale (0 = Absent,
1 = Ad Hoc, 2 = Defined, 3 = Managed, 4 = Optimized) and traced to at least
one Evidence Register item (E01–E06) and a taxonomy Capability ID (CAP-R-*).
Capabilities are organized into the Front-office (customer-facing), Middle-
office (case management and orchestration), and Back-office (core processing
and settlement) layers, consistent with the standard capability taxonomy.

## 3. Maturity Heatmap — Front / Middle / Back

| Capability ID | Capability | Layer | Current State | Target State | Evidence |
|---|---|---|---|---|---|
| CAP-R-ON-01 | Digital identity verification | Front | 1 | 3 | E01, E04 |
| CAP-R-SV-02 | Self-service servicing (balance/limit changes) | Front | 1 | 3 | E02, E05 |
| CAP-R-CM-03 | Case management & workflow orchestration | Middle | 2 | 3 | E03 |
| CAP-R-FR-04 | Fraud case triage | Middle | 2 | 3 | E06 |
| CAP-R-PY-05 | Core payments settlement | Back | 4 | 4 | E03 |
| CAP-R-LD-06 | Core ledger & account servicing | Back | 3 | 4 | E03 |

The heatmap above scores every capability on the 0-4 scale defined in
Section 2, with Front-office capabilities showing the widest current-to-
target gap.

## 4. Front-Office Layer — Detail

### CAP-R-ON-01: Digital identity verification

- **Current State: 1** (Ad Hoc) — manual document review with no
  straight-through processing; evidenced by E01 (62% completion vs. 78%
  regional peer benchmark) and E04 (drop-off concentrated at the
  identity-verification step, cited in 6 of 9 stakeholder interviews).
- **Target State: 3** (Managed) — automated document + liveness check with
  defined exception handling.
- **Gap consequence:** each point of onboarding completion left on the
  table is a foregone-funded-account, per the companion ROI model.

### CAP-R-SV-02: Self-service servicing

- **Current State: 1** (Ad Hoc) — no self-service balance-transfer or
  limit-change capability in the current online banking platform,
  evidenced by E02 (41% of ~150,000 annual contact-centre calls are
  low-complexity servicing) and E05 (platform capability inventory
  confirms the gap).
- **Target State: 3** (Managed).

## 5. Middle-Office Layer — Detail

### CAP-R-CM-03: Case management & workflow orchestration

- **Current State: 2** (Defined) — documented workflows exist but are not
  systematically enforced; evidenced by E03 (funded-account activation
  tracked but not actively nudged post-opening).
- **Target State: 3** (Managed).

### CAP-R-FR-04: Fraud case triage

- **Current State: 2** (Defined), evidenced by E06 (fraud alerts routed
  manually to a shared queue, per the architecture review).
- **Target State: 3** (Managed).

## 6. Back-Office Layer — Detail

### CAP-R-PY-05: Core payments settlement

- **Current State: 4** (Optimized) — same-day settlement with no
  exceptions logged in the review period; evidenced by E03.
- **Target State: 4** — maintain.

### CAP-R-LD-06: Core ledger & account servicing

- **Current State: 3** (Managed), evidenced by E03.
- **Target State: 4** (Optimized) — stretch target, not required to close
  the near-term onboarding/servicing gaps.

## 7. Unconsidered Needs

**Proactive fraud-pattern detection** is an Unconsidered Need: Meridian's
stakeholders did not raise it as a priority during discovery, but the
architecture review (source of E06) shows fraud case triage is entirely
manual, with no pattern-matching or anomaly scoring ahead of the queue. This
matters because the two funded initiatives above (onboarding, servicing)
will increase digital transaction volume, which — absent proactive
detection — would increase manual fraud-review load rather than reduce it.
We flag this as a scope question for Meridian's risk team, not as a scored
gap in this assessment, since no current-state evidence establishes a
maturity baseline for it.

## 8. Assumptions and Confidence

| # | Assumption | Confidence |
|---|---|---|
| 1 | Regional peer benchmark (78% onboarding completion) is an appropriate comparator for Meridian's Northland retail segment | Medium |
| 2 | Fraud case triage (CAP-R-FR-04) current-state score of 2 generalizes from the single architecture-review evidence item (E06) | Low |

Assumption 2 should be validated with Meridian's risk team before this
score is used to size any fraud-related initiative.

## 9. Next Steps

1. Validate the Unconsidered Need (proactive fraud-pattern detection) with
   Meridian's risk team and, if confirmed material, add it as a scored
   capability in a follow-up pass.
2. Carry CAP-R-ON-01 and CAP-R-SV-02 (the two lowest-scoring Front-office
   capabilities) into the Roadmap agent as the primary gap-closure targets.
3. Re-score CAP-R-FR-04 once a second evidence source is available, per
   Assumption 2 above.

---

**Provenance** — Generated by capability-assessment agent (synthetic
fixture run) on 2026-06-24. Source: Discovery Evidence Register E01–E06.
This is a synthetic fixture; none of the figures, scores, or evidence IDs
above are real.
