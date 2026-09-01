---
version: 4
prd: prd-v4.md
status: draft
date: 2026-08-18
author: Mariam Titus George
previous: solution-design-v3.md
---

# Solution Design v4 — Synthetic-Engagement Quarantine Enforcement

## Component Structure

```
scripts/
  artifact_boundary.py            — MODIFIED: new synthetic_policy(engagement_dir) gate function
                                    (joins cap_roi_config / deanonymize_dir / validate_outputs —
                                    the shared gate module both orchestrate.py and skills import)
  orchestrate.py                  — MODIFIED: step_harvest calls the gate first; "never" → skip,
                                    "quarantine" → mode="quarantine" + auto-push block skipped
  test_agent.py                   — MODIFIED only if quality_metrics.yaml needs a new check
                                    capability (path-scoped max_matches already exists via applies_to)

.claude/agents/
  knowledge-harvester.md          — MODIFIED: new "### Mode: quarantine" block; Core Rule 0
                                    self-check (all modes) for .synthetic / tests/ before any write
  benchmark-librarian.md          — MODIFIED: exclusion rule (Critical Rules + Quality Checklist);
                                    phantom benchmarks/* whitelist paths removed/repointed
  roi-hypothesis-builder.md       — MODIFIED: exclusion rule where it reads knowledge/learnings
  roi-financial-modeler.md        — MODIFIED: exclusion rule where it reads domain benchmarks
  roi-business-case-builder.md    — MODIFIED: Zenith filename example → neutral placeholder (only)

.claude/commands/
  extract-learnings.md            — MODIFIED: Step 0 self-check (same rule text as harvester)
  domain-benchmarks.md            — MODIFIED: exclusion rule + excluded-count note
  domain-pain-points.md           — MODIFIED: same
  domain-journeys.md              — MODIFIED: same
  domain-context.md               — MODIFIED: same
  domain-usecases.md              — MODIFIED: same
  domain-value-props.md           — MODIFIED: same
  generate-roi-excel.md           — MODIFIED: exclusion rule (reads knowledge/learnings/roi_models)

.claude/hooks/
  synthetic-knowledge-guard.py    — NEW: PreToolUse(Write|Edit) content guard on knowledge/**
.claude/settings.json             — MODIFIED: hook wired in

knowledge/standards/
  benchmark_evolution.md          — MODIFIED: [Synthetic-Test] formalized as excluded tier
                                    (canonical definition all rule text points to)

tests/
  quality_metrics.yaml            — MODIFIED: two new knowledge_files structural checks

evals/
  registry.yaml                   — MODIFIED: knowledge-harvester registered (components:);
                                    benchmark-librarian gains no_synthetic_citations code check
  rubrics/component/
    knowledge_harvester.py        — NEW: deterministic negative-gate evaluator (imports
                                    scripts.artifact_boundary.synthetic_policy)
    specifics.py                  — MODIFIED: no_synthetic_citations check for benchmark fixture
  goldens/synthetic_gate/         — NEW committed fixture: three tiny engagement dirs
    quarantine_case/.synthetic    —   harvest_policy: quarantine
    never_case/.synthetic         —   harvest_policy: never
    bare_tests_case/              —   no marker (path-based fail-safe witness)
  goldens/benchmark_golden.md     — MODIFIED: gains a demonstrated-exclusion line (poisoned-
                                    source note) so the new code check has a positive witness
```

Not touched: Inspire subsystem, discovery/assembly steps, templates, presentations, real-engagement harvest behavior, the four banner-marked `knowledge/learnings/roi_models/` files.

## Data & Contract Model

### `synthetic_policy(engagement_dir: Path) -> tuple[str, str]` (scripts/artifact_boundary.py)

```yaml
input: engagement directory path (absolute or repo-relative)
output: (policy, reason)
  policy: "real" | "quarantine" | "never"
  reason: human-readable one-liner for logging ("marker at <path>, harvest_policy: never",
          "under tests/ with no marker — fail-safe quarantine", "no marker")
resolution order:
  1. Walk engagement_dir and its parents (up to repo root) for a `.synthetic` file.
     First one found wins. Parse `harvest_policy:` line (plain-text YAML-ish; regex, no yaml dep).
     Values: quarantine | never. Marker present but no/unparseable policy → "quarantine".
  2. No marker: if any path segment relative to repo root is `tests` → "quarantine".
  3. Otherwise → "real".
guarantees: never raises (any I/O error → "quarantine" if under tests/, else "real" with
  reason noting the read failure); no filesystem writes.
```

Rationale: one function, three consumers (orchestrate gate, eval witness, future skills). Marker beats location so a `.synthetic` engagement accidentally created under `engagements/` is still protected.

### `.synthetic` marker (existing, now the enforced contract)

```yaml
synthetic: true            # required for human clarity; not parsed
harvest_policy: quarantine # parsed: quarantine (default) | never
# free-text fields (created, purpose, note) ignored by the parser
```

### knowledge-harvester — mode contract changes

```yaml
# NEW ### Mode: quarantine  (params: engagement_dir, outputs_dir, engagement_id)
outputs:                                  # ALL under the engagement, nothing shared
  - "{engagement_dir}/outputs/knowledge_harvest/*"   # benchmarks/journeys/roi/pain-point files
  - "{engagement_dir}/.harvest_summary.txt"
# body: run the same Core Rules extraction, but write every artifact under
# outputs/knowledge_harvest/ using the same filenames it would use in knowledge/;
# do NOT read-modify any file under knowledge/; do NOT update EXTRACTION_REGISTRY.md
# (owner decision: no shared trace — the engagement's .harvest_summary.txt is the record).

# Core Rule 0 (shared body, applies to pipeline AND backfill modes):
# before any write, check for .synthetic in the engagement dir/parents or a tests/
# path segment; policy never → refuse (message per UX spec); quarantine → behave
# exactly as quarantine mode regardless of the invoked mode.
```

Mode-set structural check `tests/quality_metrics.yaml` → `agent_modes: knowledge-harvester: [pipeline, backfill]` must become `[pipeline, backfill, quarantine]` in the same PR, or CI contradicts itself (same coupling noted in solution-design-v3).

Composer constraints honored: no H2 headings and no undeclared bare `{tokens}` inside the mode block.

### Retrieval exclusion rule (single canonical wording, referenced not restated)

Canonical definition added to `knowledge/standards/benchmark_evolution.md` as a tier row:

```
[Synthetic-Test] — fabricated data from synthetic test engagements (tests/engagements/).
Use in ROI / client work: NEVER. Excluded from all retrieval. Not promotable.
```

Each retrieval surface gets the same ~3-line rule block (wording finalized once, in the standard):
exclude `[Synthetic-Test]`-tagged entries and anything sourced from `tests/` paths; when ≥1
entry was excluded, append: `Note: N synthetic-test entries excluded — fabricated pipeline-test
data, never citable in client work (see knowledge/standards/benchmark_evolution.md).`

### CI structural checks (tests/quality_metrics.yaml → knowledge_files.structural)

```yaml
- name: "No [Synthetic-Test] data in domain knowledge"
  pattern: "\\[Synthetic-Test\\]"
  max_matches: 0
  applies_to: "**/domains/**"          # learnings/roi_models banner-marked files stay legal
- name: "No fictional test-bank names in knowledge"
  pattern: "\\bHarborlight\\b"
  max_matches: 0                        # applies to all knowledge/ files
# deliberately NO "Zenith" check — Zenith Bank is a real Nigerian institution
```

### Hook contract (.claude/hooks/synthetic-knowledge-guard.py)

```yaml
event: PreToolUse
matcher: Write|Edit
scope prefilter: target path under knowledge/ (repo-relative); else allow immediately
checks (content of the incoming write/edit payload):
  - "[Synthetic-Test]" AND target under knowledge/domains/  → deny
  - "Harborlight" anywhere under knowledge/                 → deny
deny message: names file, matched marker, and tests/engagements/README.md
failure behavior: fail-open (any exception → allow), matching every existing hook
verified premise: SDK loads project settings by default (setting_sources defaults to
  ["user","project"]; orchestrate.py sets no override) and PreToolUse denials are NOT
  bypassed by bypassPermissions — so this hook also covers the automated pipeline path.
  A live canary (one denied write under the pipeline env) is a bb-build verification step.
```

### Eval contracts (evals/registry.yaml)

```yaml
components:
  knowledge-harvester:
    evaluator: rubrics.component.knowledge_harvester
    threshold: 1.0                     # deterministic — no judge
    input: evals/goldens/synthetic_gate
    code:
      - quarantine_policy_detected     # synthetic_policy(quarantine_case) == ("quarantine", …)
      - never_policy_detected          # synthetic_policy(never_case) == ("never", …)
      - bare_tests_fails_safe          # synthetic_policy(bare_tests_case) == ("quarantine", …)
      - quarantine_mode_outputs_local  # parse agent .md quarantine-mode outputs: every path
                                       # starts with {engagement_dir}; none under knowledge/
  benchmark-librarian:                 # existing case, one check added
    code: [confidence_levels_present, source_attribution_present, no_synthetic_citations]
    # no_synthetic_citations: fixture must contain zero uncommented [Synthetic-Test] citations
    # outside an explicit "excluded" note line
```

Honest caveat (carried from the eval-gate limitation): these cases pin the gate function and the
contract shape deterministically; they do not execute the agent live. The live proof is the
bb-build verification step (one quarantined pipeline test run against harborlight_synthetic).

## Agent / Pipeline Steps

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `synthetic_policy` | pipeline function (artifact_boundary) | engagement dir | (policy, reason) | Single source of truth for synthetic detection |
| `step_harvest` gate | pipeline step (modified) | policy | mode selection / skip | Route real→pipeline, quarantine→quarantine mode, never→skip; suppress auto-push for non-real |
| `knowledge-harvester` quarantine mode | agent mode (new) | engagement outputs | files under `outputs/knowledge_harvest/` | Same extraction, quarantined destination, no shared writes |
| Core Rule 0 self-check | agent+command rule (new) | engagement path | refusal or redirect | Covers backfill mode and `/extract-learnings` (no Python driver) |
| `synthetic-knowledge-guard` | hook (new) | Write/Edit payloads | allow/deny | Content backstop on knowledge/** in ALL sessions incl. SDK pipeline |
| quality-metrics checks | CI structural (new) | PR diff files | pass/fail | Server-side backstop — contamination cannot merge |
| `knowledge_harvester` eval | eval component (new) | committed fixture | pass/fail at 1.0 | Regression net for the gate |

## Integration Points

| Existing component / step | How it's touched | Risk |
| --- | --- | --- |
| `step_harvest` (orchestrate.py) | Gate call + mode routing + push-skip; "real" path byte-identical to today | Low — additive branch, pipeline-altitude eval must stay green |
| `knowledge-harvester.md` | New mode + Core Rule 0; existing pipeline/backfill bodies unchanged | Medium — mode-block composer constraints (no H2, declared tokens only); mode-set check must be updated in the same PR |
| `benchmark-librarian.md` | Exclusion rule + whitelist repoint (folded backlog item) | Medium — whitelists are load-bearing (Rule: "Read ONLY whitelisted paths"); verify `knowledge/learnings/benchmarks/` actually exists before keeping it |
| 6 domain-* + generate-roi-excel + 2 ROI agents | Additive rule text only | Low |
| `.claude/settings.json` | One hook entry appended | Low — fail-open, scoped prefilter |
| `tests/quality_metrics.yaml` | Two additive checks | Low — but must not flag the 4 banner-marked files (scoped via applies_to) |
| `evals/registry.yaml` | New component + one check on existing case | Low — `check_registry.py` preflight validates shape |
| **Open PR stack #116–#123** | Same files (knowledge-harvester, benchmark-librarian) carry mode extractions in flight | **High (sequencing, not correctness)** — build this cycle's branch off the pr8 stack head, or wait for stack merge; decide at /bb-tickets |
| Deprecated `roi-business-case-builder.md` | One example line | Low |

## Technical Decisions

**Decision 1: Detection lives in `artifact_boundary.py`, not `orchestrate.py`.**
**Alternatives:** inline in `step_harvest`; a new `scripts/synthetic_gate.py`.
**Rationale:** `artifact_boundary.py` is the established shared-gate module (cap/deanon/validate) already imported by both the pipeline and skills, and the eval witness pattern (`overcap_negative_gate_witness`) already imports gates from it.
**Trade-offs:** the module accretes another responsibility; acceptable — it is exactly "boundary enforcement".

**Decision 2: A third harvester mode (`quarantine`) rather than a parameterized output root.**
**Alternatives:** thread a `{harvest_root}` param through the existing pipeline mode.
**Rationale:** mode blocks are the repo's contract unit (solution-design-v3 Decision 1); a distinct mode gives the quarantine path its own `outputs:` whitelist that structural checks and evals can verify statically. A parameterized root would make the output contract dynamic and unverifiable.
**Trade-offs:** some body-text duplication between modes; mitigated by the shared Core Rules section.

**Decision 3: Quarantined harvests leave no shared trace (owner decision, 2026-08-18).**
**Alternatives:** annotated `[SYNTHETIC — quarantined]` row in EXTRACTION_REGISTRY's Auto-Harvest Log.
**Rationale:** shared registry counts stay real-clients-only; the engagement's `.harvest_summary.txt` is the audit record.
**Trade-offs:** no single central list of every harvest ever run; accepted.

**Decision 4: Exclusion is visible, not silent (owner decision, 2026-08-18).**
**Rationale:** consultants see the filter working; a rising excluded-count is itself a contamination alarm.
**Trade-offs:** one extra note line in retrieval output when synthetic data is present.

**Decision 5: The hook is built (viability verified), but remains belt-and-braces.**
**Alternatives:** skip hook (CI-only); `can_use_tool` callback in orchestrate.py.
**Rationale:** verified via SDK docs — project settings load by default (`setting_sources` defaults to `["user","project"]`; orchestrate.py sets no override) and PreToolUse denials are NOT bypassed by `bypassPermissions`, so one content-based hook covers interactive AND pipeline sessions. A `can_use_tool` callback would cover only the pipeline.
**Trade-offs:** content-heuristic only (it cannot trace provenance); scoped narrowly (`[Synthetic-Test]` in domains/, "Harborlight" in knowledge/) to keep the false-positive rate at zero; fail-open like every hook in the repo. A live canary write is a bb-build verification step.

**Decision 6: No "Zenith" name check anywhere.**
**Rationale:** Zenith Bank is a real Nigerian institution; a legitimate benchmark citing it would false-positive. The fictional-name check is limited to "Harborlight"; Zenith contamination is covered by the tier tag, the write gate, and the path rules instead.
**Trade-offs:** hypothetical unlabeled Zenith-derived numbers wouldn't be name-caught; accepted (the write gate is the real defense — CI name-matching was never load-bearing).

**Decision 7: Phantom `benchmarks/` paths are removed, not created.**
**Alternatives:** create the `benchmarks/` directory structure the whitelist imagines.
**Rationale:** the paths have never existed and nothing writes to them; repointing the librarian at the real sources (`knowledge/domains/*/benchmarks.md`, `knowledge/learnings/benchmarks/` if present) removes dead references without inventing new structure. Folded backlog item.
**Trade-offs:** if a central benchmark registry is wanted later it's a fresh design, not a resurrection.
