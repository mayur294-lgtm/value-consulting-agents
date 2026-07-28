# Journey Maps — Meridian Mutual Bank

> **Synthetic golden fixture.** This document exists only to exercise the
> `journey-builder` component eval (`evals/rubrics/component/specifics.py`
> → `_journey`). Meridian Mutual Bank and "Northland" are fictional; every
> journey step, metric, and evidence reference below is fabricated for test
> purposes and must never be reused in a real engagement.

## 1. Journey Experience Map — Retail Account Lifecycle

This journey traces a Meridian Mutual Bank retail member from first contact
through renewal, spanning all four lifecycle stages: **Acquire → Activate →
Expand → Retain**. It is built from the companion Discovery Evidence
Register (E01–E07) for the Northland retail segment and is intended to make
the cost of friction visible alongside the moments that work well.

| Stage | Lifecycle Stage | Experience Score (1–10) | Status |
|---|---|---|---|
| Awareness & Application | Acquire | 6 (Amber) | Scored |
| Digital Onboarding | Activate | 3 (Orange) | Scored |
| First 90 Days | Activate | 5 (Amber) | Scored |
| Cross-Sell & Product Expansion | Expand | 4 (Orange) | Scored |
| Servicing & Issue Resolution | Retain | 2 (Red) | Scored |
| Renewal & Loyalty | Retain | 7 (Green) | Scored |

## 2. Stage-by-Stage Narrative

### 2.1 Awareness & Application (Acquire)

A prospective Northland member finds Meridian through a comparison site and
starts the online application. The form itself is straightforward — three
screens, clear copy — and 82% of started applications are completed
(E01). But the application does not pre-fill from the comparison-site
referral, so the member re-enters data they already typed elsewhere. It
works, but it **feels like the bank hasn't met them where they are.**

### 2.2 Digital Onboarding (Activate)

This is the steepest drop in the lifecycle. Identity verification requires a
manual document upload reviewed by a back-office queue, adding 1–3 business
days before the account is usable (E02). Of members who complete the
application, only 61% ever fund the account within 30 days (E03) — the
account exists, but it is **empty, and empty accounts don't generate
revenue.** This is the single largest friction point in the journey.

### 2.3 First 90 Days (Activate)

Once funded, first-transaction experience is functional: debit card
activation and first bill-pay both work without incident (E04). But there
is no proactive nudge toward a second product, so the relationship stalls
at "checking account only" for most members.

### 2.4 Cross-Sell & Product Expansion (Expand)

Contact-centre agents have no unified view of a member's full relationship,
so cross-sell offers are generic rather than needs-based (E05). Only 14% of
eligible members are offered a second product within the first year,
against a 28% regional peer benchmark (E05).

### 2.5 Servicing & Issue Resolution (Retain)

This is the weakest stage in the journey. 41% of the roughly 150,000 annual
contact-centre calls are low-complexity servicing requests — balance
transfers, limit changes — that have no self-service path today (E06).
Members are told to call back or visit a branch, which is **the moment
Meridian loses the trust it spent the first four stages building.**

### 2.6 Renewal & Loyalty (Retain)

For members who make it this far, renewal is smooth: auto-renewal is
opt-out rather than opt-in, and retention rates for tenured members exceed
90% (E07). This stage works — the problem is how few members experience it
without a servicing scar first.

## 3. Friction Callouts

| ID | Stage | Friction | Evidence | Severity |
|---|---|---|---|---|
| F1 | Digital Onboarding | Manual document review adds 1–3 day delay before account is usable | E02 | Critical |
| F2 | Digital Onboarding | No funding prompt after account opening; flow simply ends | E03 | Critical |
| F3 | Cross-Sell & Product Expansion | No unified relationship view for contact-centre agents | E05 | High |
| F4 | Servicing & Issue Resolution | No self-service path for balance/limit changes | E06 | Critical |

Each friction callout above represents a point where the current-state
process — not member intent — is the cause of value leakage, consistent
with the as-is process mapped in Section 4.

## 4. Value Leakage Waterfall — Digital Onboarding

The waterfall below quantifies value leakage across the Digital Onboarding
stage, starting from 10,000 annual applications and tracing where value is
lost before an account becomes revenue-generating.

| Step | Volume | Leakage | % Lost | Evidence |
|---|---|---|---|---|
| Applications started | 10,000 | — | — | E01 |
| Applications completed | 8,200 | 1,800 | 18% | E01 (82% completion rate) |
| Identity verification cleared | 7,380 | 820 | 10% | E02 (manual review queue attrition) |
| Accounts funded within 30 days | 5,002 | 2,378 | 32% | E03 (61% of completed applications fund) |
| **Net funded accounts** | **5,002** | **4,998 total leakage (50%)** | **50%** | E01–E03 |

This value leakage waterfall shows that half of all started applications
never become a funded, revenue-generating account — with the largest single
leak (32%) occurring at the funding step, where no prompt or nudge exists
today.

## 5. As-Is → Future-State Comparison

### 5.1 As-Is (Current State)

- Identity verification: manual document upload, reviewed by a back-office
  queue, 1–3 business day turnaround (E02).
- Funding: no in-app prompt after account opening; member must independently
  remember to transfer funds (E03).
- Servicing: balance/limit changes require a phone call or branch visit; no
  self-service capability exists in the current online banking platform
  (E06).
- Cross-sell: contact-centre agents see only single-product account data,
  not the full member relationship (E05).

### 5.2 Future-State (Backbase-Enabled)

- Identity verification: automated document + liveness check with
  straight-through processing for the majority of applicants, reducing
  turnaround from 1–3 days to minutes.
- Funding: an in-flow funding prompt immediately after account opening,
  closing the largest single leak identified in the Section 4 waterfall.
- Servicing: self-service balance transfers and limit changes available
  in digital channels, removing an estimated 41% of contact-centre call
  volume from the phone queue (per E06).
- Cross-sell: a unified relationship view surfaces needs-based offers to
  contact-centre agents at the point of contact.

The future-state changes above are sized directionally here; the companion
ROI model quantifies the full financial impact of closing the Digital
Onboarding and Servicing gaps.

## 6. Assumptions and Confidence

| # | Assumption | Confidence |
|---|---|---|
| 1 | 10,000 annual applications is a representative base volume for the Northland retail segment | Medium |
| 2 | The 28% regional peer cross-sell benchmark (E05) is an appropriate comparator for Meridian | Low |

Assumption 2 should be validated with Meridian's product team before it is
used to size the cross-sell opportunity in the ROI model.

## 7. Next Steps

1. Validate the Digital Onboarding funding-prompt design with Meridian's
   digital channel team before it is carried into the roadmap.
2. Confirm the 41% self-service-eligible call volume (E06) with the
   contact-centre operations lead.
3. Carry the Digital Onboarding and Servicing friction points into the
   Capability Assessment and Roadmap agents as priority gap-closure targets.

---

**Provenance** — Generated by journey-builder agent (synthetic fixture run)
on 2026-07-24. Source: Discovery Evidence Register E01–E07. This is a
synthetic fixture; none of the journeys, metrics, or evidence IDs above are
real.
