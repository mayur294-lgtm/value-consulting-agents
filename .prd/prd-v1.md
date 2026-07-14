---
version: 1
status: built
date: 2026-07-07
author: Mariam Titus George
previous: null
---

# PRD v1 — ROI Model Provenance: Sources sheet, honest confidence, live derived formulas

## 1. Problem

The Value Consulting system's reason for existing is defensible, evidence-traced business cases. The ROI Excel is the deliverable a client CFO scrutinises line by line. Today the pipeline has a **silent quality regression** in exactly this dimension.

During the MyState IGNITE engagement, the consultant hand-built a `roi_config.json` carrying full provenance — a top-level `sources` list, a per-field `_source` **and** `_confidence` on every Basic Information input, and a derived `operating_costs` — and locally patched `tools/roi_excel_generator.py` to render it. That produced the clean v5 model (`2606_MyState_ROI_Model_v5.xlsx`: a Sources & Provenance sheet, live `=C10*C12` operating-costs formula, honest confidence flags). The patch was auto-stashed on a branch switch and never merged.

So `main` regresses on any future ROI model:
- A config carrying `sources` is **silently dropped** — no provenance sheet, the one artifact that answers "is this borrowed data again?"
- Every `*_confidence` key **leaks as a junk row** in Model Inputs.
- The confidence column is derived from a keyword heuristic on the source string, which **mis-flags client-confirmed HIGH inputs as LOW** (e.g. MyState `total_fte`, the exact number that fixed last year's "blank ops data" failure, would render LOW and paint red).
- Derived inputs are hard-coded numbers, breaking the "change a cell, the model recalculates" promise.

Separately, even with the generator fixed, **nothing upstream emits provenance automatically** — MyState only had it because it was hand-authored. The `roi-financial-modeler` agent's output contract doesn't require `sources` / `_source` / `_confidence` on `basic_information`, so the next engagement starts from a blank provenance slate.

If we don't solve it: ROI models silently lose provenance and mislabel confidence — reintroducing the precise failure mode (blank/borrowed data, no source trail) that produced last year's rejected −$1.46M MyState case.

## 2. Solution

Land the orphaned generator improvements on `main` and make provenance a first-class, auto-emitted part of the ROI config contract. Two coordinated changes: (a) `tools/roi_excel_generator.py` renders a Sources & Provenance sheet, honours explicit per-field confidence, and emits live Excel formulas for derived inputs — all additive and backward-compatible; (b) the `roi-financial-modeler` agent (and the `/generate-roi-excel` skill doc) require and emit the `sources` list plus `_source` + `_confidence` companions on every Basic Information field, and express derived fields (operating_costs) as a formula rather than a baked number. The MyState v5 config is the reference fixture and the regression's proof.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| Generator: render a "Sources" sheet when config has a top-level `sources` list | Redesigning the Model Inputs or any existing sheet layout |
| Generator: skip `*_confidence` keys from Basic Information rows; use explicit `_confidence`, fall back to the existing keyword heuristic only when absent | Changing the confidence colour thresholds / palette |
| Generator: live Excel formula for `operating_costs` (= revenue × cost-to-income) + general `formula`/`fmt` support for derived driver inputs | Reworking the lever calculation engine or scenario math |
| Agent contract: `roi-financial-modeler` requires + emits `sources`, per-field `_source` + `_confidence`, and derived `operating_costs` as a formula | Auto-emission for `roi-hypothesis-builder` / `roi-business-case-builder` (separate agents) |
| Skill doc: `/generate-roi-excel` documents the provenance + derived-formula config keys and is corrected to the current dict-of-dicts schema | Full rewrite of the stale `/generate-roi-excel` example schema beyond provenance + the structural correction |
| A new deterministic eval row for the generator, using the MyState config as fixture | LLM-judge rubrics (judges skipped this cycle — deterministic checks only) |
| Backward compatibility: all new behaviour is additive (absent keys → prior behaviour) | Backfilling provenance into past engagements' configs |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Generator renders Sources sheet when `sources` present | 1 sheet named "Sources"; 0 when absent, no error |
| `*_confidence` keys leaking as Model Inputs rows | 0 |
| Basic Information confidence matches config's explicit value | 100% of fields (e.g. `total_fte` → HIGH, not LOW) |
| `operating_costs` cell type | Excel formula referencing revenue + cost-to-income cells (not a literal) |
| Future engagement configs carry provenance without hand-authoring | `roi-financial-modeler` output includes `sources` + `_source`+`_confidence` on all `basic_information` fields |
| Downstream pipeline correctness | Pipeline-altitude eval stays green |

## 5. Eval Acceptance Criteria (mandatory)

Judges are skipped this cycle (deterministic checks only, per setup choice). Verification is objective Python `code` checks run against a fixture config; the fixture is the MyState v5 `roi_config.json` (`engagements/outputs/2605_Mystate_Ignite/roi_config.json`), plus a minimal `sources`-absent config to prove backward compatibility.

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `roi-excel-generator` (NEW row — tool) | `sources_sheet_present`, `sources_sheet_absent_when_unset`, `no_confidence_row_leak`, `explicit_confidence_wins`, `operating_costs_is_formula`, `derived_input_formula_renders` | all `code` hard-checks PASS | unit (tool) |
| `roi-financial-modeler` (existing) | existing component checks stay green **+** new `code` checks: `basic_information_has_sources_list`, `basic_fields_have_source_and_confidence`, `operating_costs_emitted_as_formula` | keep existing threshold (0.80); new checks PASS | component |
| `roi` (existing deliverable) | existing `rubrics.deliverable.roi` golden | stays ≥ 0.80 (no regression) | deliverable |
| pipeline | `run_experiment.py --altitude pipeline` | green (no downstream break) | pipeline |

- **NEW cases authored as part of this work:** the six `roi-excel-generator` checks above and the three `roi-financial-modeler` additions, wired into `evals/registry.yaml` with the MyState fixture.
- **Downstream:** the generator is consumed by `orchestrate.py` and `/generate-roi-excel`; changes are additive, but the pipeline-altitude experiment MUST stay green as the backstop.

## 6. Out of Scope

- LLM-judge rubrics for provenance quality (deterministic-only this cycle).
- Auto-emission from `roi-hypothesis-builder` and `roi-business-case-builder`.
- Backfilling provenance into historical engagement configs.
- Any change to lever math, scenario curves, or investment modelling.
- Git housekeeping of the other stale stashes ({0}, {2}, {3}, {6}) — tracked separately, not a component change.

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| Reference implementation lives only in `git stash@{1}` (fragile) | Loss would mean re-deriving the 67-line patch | Diff already preserved to session scratchpad as `roi_excel_generator_stash1_vs_main.patch`; capture into the ticket |
| Agent-prompt change is Architect-tier restricted + guarded by CI | PR could be blocked | Author (Mariam) is Architect tier; change flows through the bb-* harness with the eval gate |
| Contribution-scope / require-harness hooks may block direct edits | Build step friction | All edits happen inside the active bb-* cycle (harness-aware) |
| Existing configs without provenance keys | Must not break | New behaviour is strictly additive — absent `sources`/`_confidence` → exact prior output |

## Rollback Plan

Both changes are additive and isolated to the generator + two prompt/doc files. Rollback = revert the merge commit; configs without provenance keys already behave as before, so no data migration or downstream cleanup is required.
