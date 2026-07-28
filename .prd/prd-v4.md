---
version: 4
status: built
date: 2026-07-28
author: Mariam Titus George
previous: prd-v3.md
---

# PRD v4 — Lossless PII Round-Trip: numbered placeholders, full-coverage de-anonymization, mapping hygiene

## 1. Problem

The 2026-07-28 full-system audit (backlog item 1, High severity) found the PII anonymization round-trip **lossy and silently corrupting** for any transcript with more than one value per redaction category. The anonymizer stores exactly one mapping key per category (`[EMAIL-REDACTED]`, `[PHONE-REDACTED]`, `[SSN-REDACTED]`, `[ACCOUNT-REDACTED]`, `[CLIENT-URL-REDACTED]`), so each new match overwrites the previous mapping entry. De-anonymization then restores the **last captured value to every occurrence**: a multi-stakeholder transcript with three attendee emails ships a client-facing deliverable in which all three people are given the same (wrong) email address. Nobody is warned — the round-trip "succeeds".

This is a client-facing correctness and data-protection failure: deliverables attribute one person's contact details, account numbers, or SSN to other people. It affects every multi-stakeholder Ignite Assess engagement (the normal case — discovery calls have several attendees).

Three adjacent gaps in the same round-trip compound it:

1. **`deanonymize_dir` misses files.** It only processes `.md/.html/.json/.txt` at the top level of `outputs/` — generated `.xlsx` ROI models ship to clients still containing `[CLIENT]` placeholders, and anything in a subdirectory is never touched.
2. **Mapping files leak.** Per-transcript `.anon_mapping_*.json` files carry exactly the PII that `.pii_mapping.json` carries, but get no `chmod 600` and are never cleaned up after the combined mapping is written.
3. **Single-word client short forms leak.** `[CLIENT-SHORT]` requires a ≥2-word short form, so "Zenith Bank" is redacted while bare "Zenith" passes to the API in plaintext.

(The audit also flagged that entity scrubbing is silently vacuous when the intake yields no names; a loud warning for that case rides along in this PRD since it is one log path in the same function.)

## 2. Solution

Make the anonymize → de-anonymize round-trip **lossless and one-to-one**: every distinct PII value gets its own numbered placeholder (`[EMAIL-1]`, `[EMAIL-2]`, …), mirroring the existing `[PERSON-N]` pattern, with repeated occurrences of the same value reusing the same placeholder and numbering kept consistent across all transcripts in an engagement run (so the merged engagement-level mapping can never collide). De-anonymization coverage extends to the files that actually ship: recursive traversal of `outputs/` including `.xlsx` workbooks. Mapping files holding PII are permission-restricted at creation and per-transcript mappings are removed once merged into the engagement-level mapping. The client short-form rule additionally redacts distinctive single-word short forms so bare brand names stop leaking. Old mappings already on disk keep working — de-anonymization is driven purely by the mapping keys, whatever their format.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| Numbered, one-to-one placeholders for all multi-value redaction categories (email, phone, SSN, account, client-URL) | Redesigning entity-name discovery (still intake/context-driven; NER is out) |
| Cross-transcript numbering consistency so the engagement-level merged mapping is collision-free | The discovery failure gate (backlog item 2 — separate PRD) |
| De-anonymization of generated `.xlsx` outputs | Anonymizing `.xlsx` *inputs* (transcripts are markdown) |
| Recursive de-anonymization of `outputs/` subdirectories | Re-anonymizing or migrating past engagements' outputs |
| `chmod 600` on every mapping file that carries PII; per-transcript mapping cleanup after merge | Encrypting mappings at rest or moving them out of the engagement dir |
| Single-word client short-form redaction with safeguards against over-redaction | General brand/alias dictionaries |
| Loud warning when the entity-name list is empty (generic PII still stripped) | Blocking the pipeline on an empty entity list |
| Backward compatibility: legacy `[X-REDACTED]` mappings still de-anonymize | Rewriting legacy mapping files to the new format |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Round-trip parity | Multi-value fixture (3+ emails, 2+ phones, 2+ accounts, SSN, client URL, several people) anonymizes and de-anonymizes back **byte-identical** to the original |
| Placeholder integrity | Every distinct PII value ↔ exactly one placeholder; no mapping key is ever overwritten with a different value |
| Merge integrity | Mappings from N transcripts merge into `.pii_mapping.json` with zero key collisions |
| Shipped-file coverage | `.xlsx` and nested files under `outputs/` contain zero placeholders after `deanonymize_dir` |
| Mapping hygiene | All mapping files carrying PII are mode `600`; no `.anon_mapping_*.json` remains after the combined mapping is written |
| Short-form leakage | Distinctive single-word client short forms (e.g. "Zenith" from "Zenith Bank") are redacted; generic words are not over-redacted |
| No silent vacuity | Empty entity list produces a visible warning in the pipeline log |

## 5. Eval Acceptance Criteria

**New component** — `pii-anonymizer` (pipeline code: `scripts/anonymize_transcript.py` + the de-anonymization gate in `scripts/artifact_boundary.py`) gets a fresh registry row and deterministic evaluator, following the `roi-excel-generator` precedent (script component, `code:` checks only, committed synthetic fixtures, temp-copy pattern so committed fixtures are never mutated).

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `pii-anonymizer` (NEW row) | `round_trip_byte_identical` (multi-value fixture in → byte-identical restoration out), `distinct_values_distinct_placeholders`, `repeated_value_reuses_placeholder`, `no_raw_pii_in_anonymized_output`, `cross_transcript_merge_collision_free`, `xlsx_outputs_deanonymized`, `nested_outputs_deanonymized`, `mapping_files_chmod_600_and_cleaned`, `client_short_single_word_redacted`, `legacy_redacted_mapping_still_restores` | 1.00 (all deterministic checks must pass — this is a PII gate) | unit |
| Pipeline regression | Existing `pipeline` case (golden engagement, inter-agent contracts) | 0.90 | pipeline |
| Structural | `scripts/test_agent.py` structural gate on the PR | pass | — |

- **Fixtures authored as part of this work:** a committed **synthetic** multi-stakeholder transcript fixture (3+ emails, 2+ phones, SSN, 2+ account numbers, client URL, multi-word client name with a distinctive single-word short form, 3+ person names — all invented, e.g. "Zenith Bank"-style) plus a minimal synthetic engagement layout for the directory-level checks. No real engagement data — `engagements/**` is gitignored PII and must never appear under `goldens:`.
- **Downstream consumers:** `orchestrate.py` (step_discovery mapping merge, final de-anonymization), `/build-roi`, `/generate-roi-excel`, `/publish` (via `artifact_boundary.py deanon`). The pipeline-altitude experiment must stay green; the `deanon` CLI contract (args, exit codes) must not change.

## 6. Out of Scope

- Backlog items 2–5 from the same audit (discovery failure gate, lost cross-deliverable review, Act 7 contract, scenario label drift) — separate cycles
- NER-based or LLM-based name detection; anonymization stays deterministic and intake-driven
- Any change to which files are *anonymized* on the way in (transcripts only, as today)
- Changes to checkpoint, journal, or telemetry semantics
- Retro-fixing already-delivered engagement outputs (a note in the change record flags that past multi-stakeholder deliverables may carry the defect)

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| This work stacks on the unmerged skill-first Phase 1 stack (`artifact_boundary.py` exists only there) | PR cannot merge to `main` before the stack does | Branch based on the stack tip; PR opened as stacked (base = stack tip) and retargeted to `main` when the stack merges |
| `.xlsx` de-anonymization needs `openpyxl`, but `artifact_boundary.py` must stay importable by plain python3 | Hard import would break skill callers on bare interpreters | Lazy import inside the `.xlsx` branch; if unavailable, report the file loudly as NOT restored (never silently skip) |
| Single-word short-form redaction can over-redact generic words ("First", "National") | False redactions damage transcript utility | Word-boundary matching + minimum length + generic-word stoplist; eval check covers both directions |
| Placeholder format change could confuse downstream consumers that pattern-match `[EMAIL-REDACTED]` | Broken assumptions in prompts/templates | Repo-wide grep for consumers of the literal legacy placeholders as part of the build; de-anonymization remains key-driven so legacy mappings still work |
| Cleanup of `.anon_mapping_*.json` could break `--resume-from` flows | Resume after interruption loses per-transcript mappings | Cleanup happens only **after** the combined `.pii_mapping.json` is written; resume paths read only the combined file |

## Rollback Plan

Single-module changes with a deterministic eval gate. If the gate goes red post-merge or a regression surfaces in an engagement, revert the PR — the legacy behavior returns intact (old mappings continue to work in both directions since de-anonymization is mapping-key-driven). No data migration is performed in either direction.
