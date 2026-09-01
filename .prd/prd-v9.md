---
version: 9
status: draft
date: 2026-08-27
author: Mariam
previous: prd-v5.md
---

> **On the version number.** This worktree's own sequence would make this v6,
> but the main stack already holds `prd-v6` (Presidio), `prd-v7` (eval gate) and
> `prd-v8`. When this branch merges, a `prd-v6.md` here would collide add/add
> with a different document of the same name. v9 is chosen so the two `.prd/`
> directories reconcile cleanly.

# PRD v9 — Make the proposal skill safe to point at a real deal

## 1. Problem

`/proposal-builder` and `/proposal-longform` went through their first real
engagement (BDO managed hosting, 2026-08-20). The skills produced a usable
document. What the run exposed is that **nothing in the skill checks the two
things that decide whether a commercial proposal is right**: whether the
numbers have a basis in the signed contract, and whether the arithmetic handed
to it holds.

- **Three of the four pricing lines quoted to the client had no basis in the
  signed order form.** Three metered rates quoted to the client appear nowhere
  in the order form; the order form states two usage limits and prices neither,
  and it prices one of the same line items at roughly 2.3x below what was being
  asked. (Figures and the order-form reference are deliberately omitted — this
  repo is public; they are in the engagement directory, which is gitignored.) This
  surfaced on the **fourth revision**, and only because the consultant happened
  to supply the contract. Nothing asked for it.
- **Six arithmetic errors sat in material the bank already held** — a deck total
  omitting one of its own rows, a bundle-count convention that changes mid-series,
  an 18-vs-17-month mismatch, a flat average applied across a 9.4× ramp. The
  skill assumes its inputs are sound.
- **Forecasting is absent entirely.** This deal needed multi-period forecasting,
  growth-rate selection, and the fact that banded pricing is a step function
  (so `mean(f(x)) ≠ f(mean(x))` — which bit us and confused the client-facing
  reconciliation).
- **The leak scan that protects live legal claims is naive substring matching.**
  `CRO` matches "across"; `anchor` matches `text-anchor`. And `absorb`,
  `written off` and `waived` are not on the list at all — on this deal those
  words would have conceded a live recovery claim **in writing**.

Behind that, the PR #153 review parked ten defects, four of which were
re-measured for this PRD and confirmed:

- **The template consultants copy from fails its own gate.** Measured:
  `templates/proposal-longform/template.html` scores **0.778** against the
  `proposal` rubric (threshold 0.85) and hard-fails `exactly_2_scenarios` (it
  ships 3 scenario cards) and `story_model_matches_deal_type` (no
  `<meta name="deal-type">`).
- **The Arabic disclaimer check fails open.** Bilingual detection matches
  `lang="ar"` literally; a document declaring `lang="ar-SA"` is treated as
  monolingual, and the check then **defaults to pass** without ever looking for
  the disclaimer.
- **`pof_backsolve`'s discount is unclamped** — a mistyped target silently
  yields a >100% discount or negative uplift rows.
- **The pricing engine has zero CI wiring.** No registry row, no selftest in the
  workflow. The review called this the "root enabler of shipped math bugs", and
  it is still true: no rubric in the suite reads `tools/pricing_model.py`.

If this is not solved, the next real deal repeats the BDO run: four revisions to
discover the contract, arithmetic taken on trust, and a leak scan that would
pass wording which waives a live claim.

## 2. Solution

Put a gate in front of every number before it reaches a client, and make the
skill's own artifacts pass the gates it already has.

ACT 0 gains a **contract-review step** that requires the order form / master
agreement and checks every quoted rate against it — a proposal cannot be
generated with an unsourced rate. A separate **arithmetic audit** runs over the
material handed in, before the deal brief. The single-headline / two-scenario
mandate generalises to "exactly two options across N agreed periods", so a
settlement-plus-forecast deal fits. The leak scan moves to word-boundary
matching and gains the three claim-waiving verbs.

`/proposal-longform` gains the **internal AE briefing HTML** as a second
rendered output — the consultant's request, and the answer to seven internal
Markdown files an AE will not read. It carries four things: what the proposal
says and why it is shaped that way, the decisions the AE must make before it can
be sent, what to hold and what must not be said in the room, and the commercial
step-downs expressed in the currency the AE actually negotiates in. The Markdown
internals stay as the audit trail.

The rest is repair: the template made to pass its own rubric, the bilingual
check made to fail closed, the discount clamped, and the pricing engine brought
under CI with its own row.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| ACT 0 contract-review gate — order form required, every quoted rate checked | Deal Desk pack / GM data (phased out of Cortex by PRD v5) |
| Arithmetic audit of upstream material, before the deal brief | Automated extraction of rates from arbitrary contract PDFs |
| Forecasting knowledge: per-driver rates, intensity anchors, step-function banded pricing, optimisation as a level cut | A general forecasting engine |
| Generalise ACT 1 Gate 6 to "exactly two options across N agreed periods" | Changing the two-option mandate itself |
| Internal AE briefing HTML as a second rendered ACT 4 output | Retiring the Markdown internals — they stay as the audit trail |
| Word-boundary leak scan + `absorb` / `written off` / `waived` | Rewriting CHECKPOINT 3 as a whole |
| Per-lever optimisation in `/proposal-longform`, money-weighted roll-up in % and currency | |
| Chart component (small multiples + crosshair), table view behind a disclosure | A charting library dependency |
| House style sheet + audience register as brief inputs | Per-consultant style storage outside the brief |
| Elasticity: support derived drivers, document when to open the dial | |
| Template made to pass the `proposal` rubric; conventions documented in the authoring guide | |
| Bilingual detection fails closed (Arabic-script detection, not a literal lang tag) | |
| `pof_backsolve` discount clamped with a hard error | |
| NEW `pricing-model` eval row + selftest in CI | |
| Footer reads "Prepared by Backbase" | |
| Version on every generate; `round` kept separate | |
| Genericise the real client + real deal ID pairing in prd-v5 | |
| Dead documentation paths (7+ citations to a nonexistent knowledge file) | |
| `ladder_position` emits a stable `key` per row | |
| Reconcile the two goldens' fixture independence | |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Quoted rates with no basis in the signed contract | 0 — generation refuses |
| Revisions needed to discover a contract discrepancy | 1 (ACT 0), not 4 |
| Arithmetic errors in upstream material reaching the client document | 0 — audited and flagged before the brief |
| `templates/proposal-longform/template.html` against the `proposal` rubric | ≥ 0.85, no hard-fails (currently 0.778, two hard-fails) |
| `lang="ar-SA"` document missing an Arabic disclaimer | FAILS (currently passes) |
| Claim-waiving verbs reaching a client document | 0 — `absorb`, `written off`, `waived` blocked at CHECKPOINT 3 |
| False positives from substring leak matching (`across`, `text-anchor`) | 0 |
| `pof_backsolve` with a mistyped target | Hard error, never a >100% discount |
| `tools/pricing_model.py` CI coverage | From none to a registry row with mutation-proven checks |
| Internal artifacts an AE must read | 1 briefing, not 7 files |

## 5. Eval Acceptance Criteria

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `proposal` (deliverable) | golden stays PASS, all 7 negatives stay FAIL; **add** negatives `proposal_lang_ar_sa.html` (bilingual fail-open) and `proposal_waiver_language.html` | 0.85 | deliverable |
| `proposal-engine` | existing 8 checks stay green; **add** `ladder_position_emits_key` | 1.00 | unit |
| `proposal-loop` | existing 9 checks stay green; **add** `version_independent_of_round` | 1.00 | unit |
| `pricing-model` (**NEW**) | fresh row required — the review named its absence the root enabler of shipped math bugs. Checks to author: `selftest_passes`, `pof_backsolve_clamps_discount`, `hard_error_on_impossible_target`, `step_function_not_averaged`, `deterministic_output`, `per_driver_rates_recomputed` | 1.00 | unit |
| `contract-review-gate` (**NEW**) | fresh row: `refuses_unsourced_rate`, `requires_order_form`, `flags_rate_contradicting_contract` | 1.00 | unit |
| `templates/proposal-longform/template.html` | scored by the `proposal` deliverable row as a second golden — the artifact consultants copy must pass the gate it will be measured by | 0.85 | deliverable |

**This worktree runs the PRE-v7 harness.** There is no `--mutate`, no
`--calibration`, no mutation law, and `run_experiment.py` still accepts the
retired `--altitude pipeline`. Every row above must therefore be authored twice
over: correct here, and **carrying `mutations:` entries when this branch merges
onto the v7 stack**, or they land straight into that stack's DEBT count. A new
row starts covered, not in debt.

**Already wired on the v7 side:** `tools/proposal_builder.py` is mapped to
`proposal-engine` in the v7 workflow's derive step, and the deliverable list
there is now derived from the registry — so `proposal` will be gated
automatically on merge. `tools/pricing_model.py` was **deliberately not mapped**,
because no rubric reads it; the `pricing-model` row above is what makes that
mapping honest rather than a false green.

**Downstream consumers:** yes. The render contract changes (deal-type meta,
scenario markers, a second HTML output), so any structural lint over proposal
outputs must stay green.

## 6. Out of Scope

- Merging this branch. It is 192 commits behind the v7 stack and carries four
  known doc/config conflicts (`registry.yaml`, `README.md`, `evals.yml`,
  `backlog.md`) — no code conflicts. Merge is its own decision.
- Real-deal fixtures. The two real-deal parity sets stay local-only; repo goldens are
  the synthetic Meridian set. **This repo is public.**
- Audience-cuts model (roadmap, per PRD v5).
- Deal Desk pack with GM data.
- Automated contract parsing. The gate requires the order form and checks rates
  against what the consultant confirms it says; it does not read PDFs unaided.

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| Contract gate blocks generation when no order form exists | A renewal with a missing/unavailable contract cannot produce a proposal | Gate requires an explicit consultant override that is LOGGED and surfaces in the AE briefing as an open decision — never a silent skip |
| Arithmetic audit produces false positives on legitimate conventions | Consultant loses trust and skips it | Audit reports findings with the arithmetic shown, never blocks; only unsourced *rates* block |
| Forecasting knowledge is the largest item here | Scope drift during build | Sequence it last; the contract gate and leak scan are the two that carry real deal risk and ship first |
| Template becoming a scored golden freezes its bytes | Cosmetic edits start failing the gate | Score it as a golden for structure only; the calibration-anchor rule (goldens are frozen) applies from the moment it lands |
| Branch is 192 commits behind | Everything here is authored against an older harness | Stated in Eval Acceptance Criteria; rows must be re-authored with mutations on merge |

## Privacy & Security

- **The repo is public.** No real deal data, no real pricing, no client+deal-ID
  pairing. PRD v5 currently pairs a real client with a real deal ID
  (a named client paired with that deal's real quote ID) — genericising it is in
  scope here. The pairing is NOT restated in this document, for the same reason.
- **Pricing is always fresh consultant input, never stored.** Unchanged from v5.
- **The `INTERNAL_` prefix wall stays.** The new AE briefing HTML is an internal
  artifact and must carry the prefix and be excluded by `/publish`, exactly as
  the Markdown internals are.
- **The leak scan is a client-facing legal control, not hygiene.** Its failure
  mode on the BDO run was conceding a live recovery claim in writing. Word-
  boundary matching and the three verbs are the highest-value change in this PRD.
