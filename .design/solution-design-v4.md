---
version: 4
prd: prd-v4.md
status: draft
date: 2026-07-28
author: Mariam Titus George
previous: solution-design-v3.md
---

# Solution Design v4 — Lossless PII Round-Trip

## Component Structure

```
scripts/
  anonymize_transcript.py    — MODIFIED: numbered per-value placeholders, shared numbering
                               across transcripts, mapping chmod 600, single-word client
                               short forms, empty-entity-list warning
  artifact_boundary.py       — MODIFIED: deanonymize_dir walks outputs/ recursively and
                               restores .xlsx (lazy openpyxl); unrestorable files fail loudly
  orchestrate.py             — MODIFIED (step_discovery only): threads shared mapping through
                               per-transcript anonymization; deletes per-transcript mapping
                               files after .pii_mapping.json is written
evals/
  registry.yaml              — NEW component row: pii-anonymizer (threshold 1.00, code checks only)
  goldens/
    pii_roundtrip_fixture.md — NEW committed SYNTHETIC multi-stakeholder transcript (3 emails,
                               2 phones, SSN, 2 account numbers, client URL, "Zenith Bank" +
                               bare "Zenith", 3 person names; repeated values included)
  rubrics/component/
    pii_anonymizer.py        — NEW deterministic evaluator: evaluate(target) -> list[CheckResult];
                               runs the real code round-trip in a temp dir (roi-excel-generator
                               precedent — committed fixtures never mutated)
.github/workflows/
  evals.yml                  — MODIFIED: add `--component pii-anonymizer` to the PR gate
```

No agent, skill, template, or hook files change.

## Data & Contract Model

### Placeholder scheme (the mapping contract)

```
[CLIENT], [CLIENT-ABBR], [CLIENT-SHORT], [PERSON-N]   — unchanged
[EMAIL-N], [PHONE-N], [SSN-N], [ACCOUNT-N], [CLIENT-URL-N]   — NEW, N = 1,2,3…
```

- One placeholder per **distinct value**, assigned in order of first appearance; every occurrence
  of that value (in any transcript of the run) maps to the same placeholder.
- Mapping files remain flat JSON `{placeholder: original_value}` — unchanged shape, so
  `deanonymize_text` needs no change and **legacy mappings with `[X-REDACTED]` keys keep working**.
- Numbering is engagement-run-global: transcript 2 continues where transcript 1 stopped, and a
  value already seen in transcript 1 reuses its placeholder. This is what makes
  `combined_mapping.update(...)` in `step_discovery` collision-free.

### Function contracts

```python
# anonymize_transcript.py
anonymize_text(text, entity_names, client_label="[CLIENT]", shared_mapping=None)
    -> (anonymized_text, mapping)
    # shared_mapping: read-only dict {placeholder: value} from prior transcripts in the
    # same run. Used to (a) reuse placeholders for already-seen values, (b) continue
    # per-category counters past the max existing index. Returned mapping contains the
    # entries relevant to THIS text (reused + new) so it de-anonymizes standalone.
    # Omitted/None → standalone behavior, numbering starts at 1. Backward compatible.

anonymize_transcript_file(transcript_path, engagement_dir, output_dir=None, shared_mapping=None)
    -> (anon_path, mapping_path)
    # writes mapping with chmod 0o600; warns on stderr when the entity list is empty

# artifact_boundary.py — deanonymize_dir(outputs_dir, mapping_file=None) -> dict
# report gains: "unrestored": [str]  (files that could not be restored, e.g. xlsx
# without openpyxl); client_ready is False whenever unrestored is non-empty.
# CLI surface (args, exit codes) unchanged: exit 1 whenever not client_ready.
```

### Single-word client short form

Accept a 1-word short form (today rejected) when **all** hold: length ≥ 4; not in a generic-word
stoplist (`bank, banking, credit, union, first, national, federal, united, community, citizens,
state, financial, savings, trust, group, holdings, capital, mutual, valley, coast, pacific`);
matched with `\b`-bounded case-insensitive regex (multi-word short forms keep today's behavior).

### Eval contract (registry row)

```yaml
pii-anonymizer:
  altitude: component
  threshold: 1.00        # PII gate — every deterministic check must pass
  input: evals/goldens/pii_roundtrip_fixture.md
  code: [round_trip_byte_identical, distinct_values_distinct_placeholders,
         repeated_value_reuses_placeholder, no_raw_pii_in_anonymized_output,
         cross_transcript_merge_collision_free, xlsx_outputs_deanonymized,
         nested_outputs_deanonymized, mapping_files_chmod_600_and_cleaned,
         client_short_single_word_redacted, legacy_redacted_mapping_still_restores]
```

The evaluator synthesizes the engagement scaffolding (intake file naming the fixture's client +
stakeholders, a temp `outputs/` tree with a small openpyxl-built workbook and a nested subdir)
in a temp dir at run time — only the transcript fixture is committed, and no check ever writes
inside the repo.

## Agent / Pipeline Steps

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `step_discovery` PII pass | pipeline step (existing, modified) | `inputs/transcript_*.md`, intake/context | `.anon_transcript_*.md`, `.pii_mapping.json` (600), no leftover per-transcript mappings | Lossless anonymization before any API call |
| `deanonymize_dir` | boundary gate (existing, modified) | `outputs/**` + `.pii_mapping.json` | restored files incl. `.xlsx`, gate report | Restore real names/PII in everything that ships |
| `pii-anonymizer` eval | eval component (new) | committed fixture | pass/fail per check | The round-trip parity gate (bb-build verify + CI) |

## Integration Points

| Existing component / step | How it's touched | Risk |
| --- | --- | --- |
| `orchestrate.py` step_discovery | Threads `shared_mapping`; deletes per-transcript mappings post-merge | Low — additive param; cleanup runs only after `.pii_mapping.json` is written, so `--resume-from` (which reads only the combined file) is unaffected |
| `/build-roi`, `/generate-roi-excel`, `/publish` → `artifact_boundary.py deanon` | Same CLI, wider coverage (recursive + xlsx) | Low — exit-code semantics unchanged; new failure mode (unrestorable xlsx) maps to the existing exit 1 |
| Downstream prompt/template consumers of literal `[EMAIL-REDACTED]` etc. | Placeholder text changes | Low — repo-wide grep in the build ticket confirms no consumer pattern-matches the legacy literals; de-anonymization is mapping-key-driven either way |
| `evals.yml` PR gate | One added `--component pii-anonymizer` run (deterministic, no LLM cost) | Low |
| Pipeline-altitude eval | Must stay ≥ 0.90 | Low — anonymization output shape unchanged apart from placeholder names |

## Technical Decisions

**D1 — Run-global numbering threaded via `shared_mapping`, not per-file numbering.**
Alternatives: (a) per-file numbering + renumber at merge — rejected: the anonymized transcripts already embed the placeholders, so renumbering desynchronizes text from mapping; (b) namespacing placeholders per transcript (`[T1-EMAIL-1]`) — rejected: leaks structure into agent-visible text and breaks the cross-transcript "same person, same placeholder" property that keeps agent outputs coherent. Trade-off: `anonymize_text` gains an optional param; standalone calls are unaffected.

**D2 — Mapping shape stays flat `{placeholder: value}`.**
Keeps `deanonymize_text`, `deanonymize_file`, and every existing on-disk mapping working unchanged. Legacy `[X-REDACTED]` keys restore exactly as before (still wrong for old multi-value runs — that history is not repairable; the fix is forward-looking, per PRD out-of-scope).

**D3 — Lazy openpyxl import inside the `.xlsx` branch; unrestorable ⇒ loud failure, `client_ready: false`.**
`artifact_boundary.py` must stay importable on plain python3. Silently skipping xlsx is exactly the audit bug, so a missing engine fails the gate rather than shrinking coverage. xlsx restoration replaces placeholders in string cell values (including formula strings) and sheet titles only — headers/footers/charts hold no engagement PII in our templates.

**D4 — Recursive walk via `rglob('*')`, keeping the `interim*` exclusion, adding dotfile exclusion.**
Dotfile exclusion prevents the walker from "restoring" `.anon_*` scratch files or `.pii_mapping.json` itself if a caller passes the engagement dir.

**D5 — Per-transcript mappings deleted only after the combined mapping is written (same transaction order as today's chmod).**
Standalone single-file CLI runs keep their mapping file (their only artifact), now mode 600.

**D6 — Threshold 1.00 for the new eval row.**
Deviates from the 0.80 house default deliberately: every check is deterministic and each one witnesses a distinct shipped-PII failure mode; 9/10 must not pass.

**D7 — Single-word short-form stoplist is a small hardcoded list, not a knowledge file.**
It guards a regex, not consulting knowledge; keeping it in-module keeps `anonymize_transcript.py` dependency-free and testable. Trade-off: additions need a code change — acceptable for a rarely-touched guard.
