---
version: 1
prd: prd-v1.md
status: draft
date: 2026-07-07
author: Mariam Titus George
previous: null
---

# Solution Design v1 — ROI Model Provenance

## 1. Stack alignment

Within the cortex stack: Python pipeline tool (`tools/roi_excel_generator.py`, openpyxl), a Claude Code agent prompt (`.claude/agents/roi-financial-modeler.md`), a command doc (`.claude/commands/generate-roi-excel.md`), and deterministic eval `code` checks (`evals/`). No web/JS stack. No new dependencies (openpyxl already required).

## 2. Component structure

```
tools/
  roi_excel_generator.py          MODIFIED — port of git stash@{1} (+~67 lines):
                                    • new _create_sources_sheet() (renders when config.sources present)
                                    • generate(): call _create_sources_sheet after data-gaps sheet; add "Sources" to tab order
                                    • basic_fields filter: also skip *_confidence keys
                                    • confidence col: explicit `_confidence` wins, heuristic fallback
                                    • operating_costs: live formula when revenue+c2i present
                                    • driver inputs: general `formula`/`fmt` support (live formula + number format)
.claude/agents/
  roi-financial-modeler.md        MODIFIED — output contract (§"Output: roi_config.json Schema"):
                                    • require top-level `sources` array
                                    • require per-field `_source` + `_confidence` on every basic_information field
                                    • emit operating_costs as a formula spec (or literal + provenance if drivers absent)
.claude/commands/
  generate-roi-excel.md           MODIFIED — document provenance + derived-formula config keys;
                                    correct stale schema (levers array → dict-of-dicts) minimally
evals/
  registry.yaml                   MODIFIED — new `roi-excel-generator` row; extend roi-financial-modeler code checks
  rubrics/component/specifics.py  MODIFIED (or new module) — the deterministic code checks
  goldens/
    roi_config_provenance.json    NEW — golden fixture WITH sources + _confidence + derived operating_costs
    roi_config_no_provenance.json NEW — minimal fixture WITHOUT provenance (backward-compat witness)
```

Governance note (CLAUDE.md): agent + skill edits are Architect-tier and require-harness-guarded; all edits occur inside this active bb-* cycle. Author is Architect tier.

## 3. Data & contract model

### 3.1 Top-level `sources` (new, optional)
```json
"sources": [
  { "ref": "client CC actuals",
    "detail": "Call volumes + AHT by wrap-up code, ~182k calls/yr (Nov24–May25); FTE CC 28 / Branch 66.",
    "file": "6 month Data.xlsx · 250512 Follow-up questions.xlsx" }
]
```
Renderer reads `ref` / `detail` / `file` (all strings, all optional-within-entry). Absent list → no sheet.

### 3.2 `basic_information` per-field provenance (new companions)
For each field `X` (e.g. `total_fte`):
```json
"total_fte": 94,
"total_fte_confidence": "HIGH",
"total_fte_source": "Client follow-up (250512): CC 28 + Branch 66 — CLIENT-CONFIRMED"
```
- `_source` already partially supported (filtered from rows on main); `_confidence` is the new companion.
- Confidence vocabulary owned by the agent contract: `HIGH | MEDIUM | LOW | ASSUMPTION`.

### 3.3 Derived `operating_costs`
Generator computes the cell as `=<revenue_cell>*<c2i_cell>` when `annual_revenue`, `cost_to_income_ratio`, and `operating_costs` all exist in `basic_information` (cell refs resolved from the map built while writing those rows). Agent emits `operating_costs` with a `_source` noting it is derived; the numeric value may remain for non-Excel consumers but Excel overrides it with the formula.

### 3.4 Driver input `formula` / `fmt` (new, optional)
```json
"some_derived_input": { "formula": "{driver_a}*{driver_b}", "fmt": "0.0%", "value": 0.12, "confidence": "MEDIUM" }
```
`{token}` → the cell ref already assigned to that input in the same driver block; `fmt` overrides magnitude-inferred number format. No `formula` → literal value as today.

### 3.5 Eval data
| Fixture | Exercises |
| --- | --- |
| `evals/goldens/roi_config_provenance.json` | Sources sheet, no `_confidence` leak, explicit confidence wins, operating_costs formula, driver `formula` |
| `evals/goldens/roi_config_no_provenance.json` | Backward compat: no Sources sheet, heuristic confidence, literal operating_costs, no crash |

## 4. Pipeline / component steps

| Name | Type | Inputs | Outputs | Purpose |
| --- | --- | --- | --- | --- |
| `ROIModelGenerator` | tool (Python) | `roi_config.json` | `*.xlsx` | Render workbook incl. Sources sheet + provenance (MODIFIED) |
| `roi-financial-modeler` | agent | levers, input pack, benchmarks | `roi_config.json` | Emit provenance-complete config (contract MODIFIED) |
| `roi-excel-generator` eval | eval (code) | golden fixtures | check results | Deterministic gate on the 6 generator behaviours (NEW) |

## 5. Integration points

| Touched | Change | Downstream depends? | Risk |
| --- | --- | --- | --- |
| `tools/roi_excel_generator.py` | additive rendering paths | `scripts/orchestrate.py`, `/generate-roi-excel` call it | **Low** — additive; absent keys → prior output |
| `.claude/agents/roi-financial-modeler.md` | richer output contract | Excel generator consumes config; `knowledge-harvester` reads outputs | **Medium** — contract change; mitigated by additive generator + eval |
| `.claude/commands/generate-roi-excel.md` | doc-only | consultants invoking the skill | **Low** — documentation |
| `evals/registry.yaml` + checks | new row + checks | `evals.yml` CI gate | **Low** — new gate, deterministic |

Pipeline-altitude experiment is the backstop: it must stay green to prove no downstream break.

## 6. Technical decisions

| Decision | Alternatives | Why | Trade-off |
| --- | --- | --- | --- |
| Port stash@{1} verbatim as the generator baseline | Re-derive from scratch | It is the proven code that produced the live v5 config; lowest risk | Must review the patch as if new (no blind trust) |
| Explicit `_confidence` wins, heuristic is fallback | Replace heuristic entirely | Backward compat for configs without `_confidence` | Two code paths for confidence |
| Dedicated golden fixtures in `evals/goldens/` (not a live client config) | Point eval at `engagements/outputs/2605_Mystate_Ignite/roi_config.json` | Engagement outputs are mutable/could move; a golden is stable and self-documenting | Must keep the golden representative if the schema evolves |
| Additive-only, absent-key = prior behaviour | Make provenance mandatory in the generator | Can't break existing/historical configs | Provenance quality depends on the agent actually emitting it (enforced upstream via the agent's own eval checks) |
| Generator does not validate confidence vocabulary | Enforce enum in generator | Separation of concerns — vocabulary belongs to the agent contract/eval | A malformed value would render verbatim (caught by agent-side eval) |
| Skill doc: provenance keys + minimal schema correction only | Full `/generate-roi-excel` rewrite | Keeps the cycle scoped; the stale full-rewrite is its own backlog item | Doc remains imperfect outside the provenance area |
