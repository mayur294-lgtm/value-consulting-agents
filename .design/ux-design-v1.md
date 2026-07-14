---
version: 1
prd: prd-v1.md
status: draft
date: 2026-07-07
author: Mariam Titus George
previous: null
---

# UX Design v1 — ROI Model Provenance

The "users" of this change are (a) the **consultant/CFO reading the generated Excel** and (b) the **`roi-financial-modeler` agent authoring `roi_config.json`**. UX here = the output experience in the workbook and the authoring contract. No screen/web UI is involved.

## 1. Flows

### Flow A — Generator renders a config WITH provenance (happy path)

```
roi_config.json (has `sources` list + per-field `_source`/`_confidence` + derived operating_costs)
        │
        ▼
ROIModelGenerator.generate()
        │
        ├─ Model Inputs sheet
        │     ├─ Basic Information rows: `_source`/`_confidence` keys are NOT rendered as rows
        │     ├─ confidence column (D) = explicit `_confidence` value (HIGH/MEDIUM/LOW/ASSUMPTION)
        │     ├─ operating_costs cell = live formula  =<revenue_cell>*<c2i_cell>
        │     └─ derived driver inputs with `formula` = live Excel formula (tokens → cell refs), `fmt` applied
        │
        └─ Sources sheet (created because `sources` present)
              └─ header "Sources & Provenance" + table: Source | What it provides | File / location
```

### Flow B — Generator renders a config WITHOUT provenance (backward compat)

```
roi_config.json (no `sources` key, no `_confidence` fields, operating_costs = literal)
        │
        ▼
ROIModelGenerator.generate()
        ├─ Basic Information: exactly as today (heuristic confidence from source string)
        ├─ operating_costs: literal value as today
        └─ NO Sources sheet created, NO error
```

### Flow C — Agent authors the config (upstream)

```
roi-financial-modeler runs
        │
        ▼
emits roi_config.json
        ├─ top-level `sources`: [ {ref, detail, file}, ... ]
        ├─ each basic_information field X → X, X_source, X_confidence
        └─ operating_costs → {formula} referencing revenue × cost-to-income (or literal + _source if drivers absent)
```

## 2. Output states (workbook)

| Surface | State | What appears |
| --- | --- | --- |
| Sources sheet | `sources` present, ≥1 entry | Sheet "Sources" with title, intro line, one row per source (Source / What it provides / File-location) |
| Sources sheet | `sources` absent or empty | Sheet not created (no blank tab, no error) |
| Model Inputs — Basic Info | explicit `_confidence` present | Confidence col shows that value verbatim; row for the value only (no `_confidence`/`_source` rows) |
| Model Inputs — Basic Info | `_confidence` absent | Confidence col falls back to existing keyword heuristic (HIGH/MED/LOW) |
| Model Inputs — Operating Costs | revenue + c2i + operating_costs all present | Cell = formula `=<rev>*<c2i>`, unfilled style, `#,##0` format |
| Model Inputs — Operating Costs | any of the three missing | Literal value as today |
| Lever driver input | input has `formula` | Cell = live formula with `{token}`→cell-ref substitution; number format from `fmt` or magnitude inference |

## 3. Error / edge states

| Cause | Behaviour | Rationale |
| --- | --- | --- |
| `sources` entry missing `ref`/`detail`/`file` | Renders present keys, blanks the rest — no crash | Provenance is additive; partial is better than failing the whole workbook |
| `formula` references a token with no matching input cell | Token left unsubstituted (Excel shows `#NAME?`) | Surfaces an authoring error visibly rather than silently miscalculating — matches existing `baseline_formula` behaviour in the generator |
| `_confidence` value not in {HIGH, MEDIUM, LOW, ASSUMPTION} | Written verbatim to the confidence column | Generator does not police vocabulary; the agent contract owns the vocabulary |
| Both `_confidence` absent AND source string empty | Heuristic returns LOW (today's behaviour, unchanged) | Backward compatibility |
