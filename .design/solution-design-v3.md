---
version: 3
prd: prd-v3.md
status: draft
date: 2026-07-24
author: Mariam Titus George
previous: solution-design-v1.md
---

<!-- Version note: v2 is intentionally skipped — PR #97 (feat/ctp-critty) carries
     .design/*-v2.md. See prd-v3.md for the same convention. -->

# Solution Design v3 — Skill-First Phase 1: Mode-Scoped Agent Contracts

## Component Structure

```
.claude/agents/                          — MODIFIED (10 files, one ticket each)
  discovery-transcript-interpreter.md    — + ## Modes (standalone, pipeline); PII round-trip contract explicit
  journey-builder.md                     — + ## Modes (standalone, pipeline)
  market-context-researcher.md           — + ## Modes (standalone, pipeline)
  capability-assessment.md               — + ## Modes (standalone, pipeline)
  roi-hypothesis-builder.md              — + ## Modes (standalone, pipeline)
  benchmark-librarian.md                 — + ## Modes (standalone, pipeline) — FIRST extraction (lowest risk)
  roi-financial-modeler.md               — + ## Modes (standalone, pipeline, excel-source); capping moves out
  roadmap-prioritization.md              — + ## Modes (standalone, pipeline)
  narrative-assembler.md                 — + ## Modes (standalone, pipeline-shard, pipeline-report, html-partial) — LAST (most complex)
  knowledge-harvester.md                 — + ## Modes (pipeline, backfill)

scripts/
  orchestrate.py                         — MODIFIED: gains parse_agent_modes() + compose_prompt(agent, mode, params);
                                           per-agent f-string prompt bodies deleted as each agent is extracted;
                                           legacy inline path retained for not-yet-extracted agents (mixed state)
  artifact_boundary.py                   — NEW: the artifact gates, shared by pipeline and standalone paths
                                             cap_roi_config(path)      (moved from orchestrate._validate_roi_config)
                                             deanonymize_dir(dir)      (moved from orchestrate step logic)
                                             validate_outputs(dir, t)  (thin wrapper over validate_engagement_outputs.sh)
  test_agent.py                          — MODIFIED: structural check — each extracted agent declares its
                                           expected mode sections; missing/renamed mode fails

.claude/commands/
  build-roi.md                           — MODIFIED: after modeler runs, invoke artifact_boundary.cap_roi_config
  generate-roi-excel.md                  — MODIFIED: refuses/flags an uncapped roi_config.json

tests/quality_metrics.yaml               — MODIFIED: adds mode-section requirement for the 10 extracted agents

evals/
  registry.yaml                          — MODIFIED: + standalone-capping parity case (golden: capped config;
                                           negative: uncapped config must fail); existing rows unchanged
  goldens/roi_config_overcap.json        — NEW negative fixture
```

No new component *types*: contracts live inside the existing agent `.md` files; `require-harness.py`, `test-agents.yml`, and the eval registry continue to see one file per agent.

## Data & Contract Model

### The mode section (the heart of the change)

Each agent `.md` gains one `## Modes` section containing one `### Mode: <name>` block per supported invocation. Structured facts go in a fenced YAML block (parsed by the composer); behavior stays prose (read by the model):

```markdown
## Modes
<!-- Parsed by scripts/orchestrate.py::parse_agent_modes().
     An invocation receives ONLY: core identity (everything above ## Modes)
     + its selected mode block. Other modes are stripped. -->

### Mode: standalone   <!-- default when no phase directive present -->
```yaml
inputs:
  required: []
  optional:
    - outputs/evidence_register.md
    - outputs/pain_points.md
degraded: ask-inline        # ask-inline | proceed-without | refuse
knowledge:                  # exhaustive whitelist — replaces "read the domain pack"
  - knowledge/domains/{domain}/benchmarks.md
  - knowledge/standards/capability_taxonomy_{domain}.md
outputs:
  - outputs/capability_assessment.md
checkpoint: interactive     # interactive | file | none
gates: []                   # artifact_boundary functions to run on outputs
```
Prose: behavior notes specific to this mode.

### Mode: pipeline
```yaml
params: [outputs_dir, domain]   # runtime values injected by the composer
inputs:
  required:
    - "{outputs_dir}/evidence_register.md"
degraded: refuse            # pipeline never silently skips a required artifact
knowledge: [...]
outputs:
  - "{outputs_dir}/capability_assessment.md"
checkpoint: file            # CHECKPOINT_capability.md / _APPROVED.md protocol
phases: single              # single | two-phase
gates: []
```
```

**Rationale for the hybrid YAML-in-markdown shape:** the composer needs machine-readable inputs/outputs/whitelists (it validates required inputs before spending an agent run, and strips unselected modes); the model needs prose for judgment behavior. Pure prose is unparseable; pure YAML can't carry methodology. The YAML keys above are the complete set — no speculative fields.

### Composer contract (orchestrate.py)

```
compose_prompt(agent_name, mode, params) -> system_prompt
  1. parse .claude/agents/<agent_name>.md
  2. core = content above ## Modes (frontmatter stripped)
  3. block = the selected ### Mode section; error if absent
  4. substitute params into {placeholders}; params carry VALUES only
     (paths, domain) — never instructions
  5. return core + block + params table

run_agent(agent_name, mode=..., params=...)   # extracted agents
run_agent(agent_name, prompt=...)             # legacy, during rollout only
```

### Artifact gate contract (scripts/artifact_boundary.py)

| Function | Input | Output | Behavior |
| --- | --- | --- | --- |
| `cap_roi_config(path)` | roi_config.json | same file, capped + gate report dict | Identical math to today's `_validate_roi_config` (impact cap 0.60, segment ROI ranges, curve-adjusted recompute). Moved, not rewritten. |
| `deanonymize_dir(dir)` | outputs dir + `.pii_mapping.json` | outputs de-anonymized, report | Missing mapping → loud "NOT client-ready" flag, never silent |
| `validate_outputs(dir, type)` | outputs dir | pass/fail + missing list | Wraps existing `validate_engagement_outputs.sh` |

Both orchestrate.py steps and skills (`/build-roi`, `/generate-roi-excel`) call these — one implementation, two callers.

## Agent / Pipeline Steps

No new agents, no new DAG steps. Changed invocations only:

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `compose_prompt` | pipeline helper | agent .md + mode + params | system prompt | Single source of truth for what an agent is told |
| `parse_agent_modes` | pipeline helper | agent .md | mode dict | Parse + validate mode sections |
| `cap_roi_config` | artifact gate | roi_config.json | capped config | Same guarantee for pipeline and standalone |
| `deanonymize_dir` | artifact gate | outputs dir | client-ready outputs | Ends pipeline-only de-anonymization |
| `validate_outputs` | artifact gate | outputs dir | pass/fail | Completeness check callable outside the pipeline |
| 10 × agent invocation | agent (modified) | per mode contract | per mode contract | Extracted one at a time, order below |

**Extraction order (risk ascending, one ticket each):** benchmark-librarian → knowledge-harvester → capability-assessment → market-context-researcher → roi-hypothesis-builder → journey-builder → roadmap-prioritization → roi-financial-modeler (with the capping move) → discovery-transcript-interpreter (PII round-trip — needs the most care) → narrative-assembler (4 modes, most complex, last).

## Integration Points

| Existing component / step | How it's touched | Risk |
| --- | --- | --- |
| orchestrate.py step functions | Inline prompt f-strings replaced by composer calls, one agent at a time; mixed state supported throughout | Medium — mitigated by per-agent pipeline-eval gate |
| Checkpoint protocol (CHECKPOINT_*.md / _APPROVED.md) | Unchanged; mode YAML only *names* which protocol applies | Low |
| `_validate_roi_config` in orchestrate.py | Moved to artifact_boundary.py; orchestrate imports it; `/build-roi` + `/generate-roi-excel` gain the same call | Medium — behavior must be move-not-rewrite; parity eval case guards it |
| PII round-trip (anonymize → run → de-anonymize) | Anonymize side untouched (hook + script); de-anonymize side moves to artifact_boundary | High — extracted second-to-last; discovery ticket includes explicit PII regression checks |
| `.claude/agents/*.md` descriptions contradicting injected prompts | Contradictions resolved during extraction; default rule in Technical Decisions | Medium — every resolution logged in ticket + PR |
| evals/registry.yaml component rows | Unchanged rows must stay ≥ 0.80; new parity case added | Low |
| test_agent.py + quality_metrics.yaml | Gain mode-structure checks; must land in the same PR as the first extraction or CI contradicts itself | Medium |
| Inspire subsystem, bb-* harness, hooks | Untouched | — |

## Technical Decisions

**Decision 1: Modes live inside the agent `.md`, parsed by the composer.**
**Alternatives:** separate contract files per agent; a central contracts.yaml.
**Rationale:** Owner decision (2026-07-24): don't change what the harness treats as a component. One file per agent keeps require-harness, test-agents.yml, and the eval registry untouched.
**Trade-offs:** orchestrate.py parses markdown; standalone Task-tool invocations load the whole file including unselected modes (see Decision 6).

**Decision 2: Hybrid contract — YAML block for facts, prose for behavior.**
**Alternatives:** all prose (status quo, unparseable); all YAML (can't carry methodology).
**Rationale:** The composer must validate inputs and strip modes mechanically; the model needs judgment guidance. Each format does what it's good at.
**Trade-offs:** Two syntaxes in one file; the structural check in test_agent.py keeps the YAML honest.

**Decision 3: Mixed-state rollout — legacy inline prompts coexist with extracted modes.**
**Alternatives:** flag-day migration of all 10 agents in one PR.
**Rationale:** Per-agent revert (PRD rollback plan) is only possible if unextracted agents keep working untouched. Also matches the eval gate cadence: pipeline green between every extraction.
**Trade-offs:** orchestrate.py temporarily carries both paths; acceptable because the end state deletes the legacy path.

**Decision 4: Contradiction-resolution default — the injected prompt wins for pipeline modes; the `.md` wins for standalone; ambiguity escalates to the Architect.**
**Alternatives:** always trust the `.md`; always trust the script; decide ad hoc.
**Rationale:** The injected prompts are what production has actually been running — pipeline behavior is *defined* by them today. The `.md`'s standalone descriptions are the only spec standalone mode ever had. Anything genuinely ambiguous is a product call, not an implementation call.
**Trade-offs:** Some `.md` prose that was aspirational-but-never-run gets overwritten by production reality; the log makes each such loss visible and reversible.

**Decision 5: Artifact gates as plain Python functions in one module, called by both paths.**
**Alternatives:** duplicate the logic into skills; make gates an agent; hook-based enforcement.
**Rationale:** These are deterministic checks (capping math, placeholder scans, file presence) — exactly what should NOT be an LLM. One module, two callers ends the pipeline/standalone guarantee gap with the least machinery.
**Trade-offs:** Skills invoke them via Bash — a convention, not an enforcement. Hook-level enforcement is a Phase 2 (governance tiering) question, deliberately not decided here.

**Decision 6: Standalone (Task-tool) invocations tolerate loading all modes; the compactness budget is the mitigation.**
**Alternatives:** a launcher that pre-strips modes for standalone use; splitting files (rejected — Decision 1).
**Rationale:** The harness loads whole agent files; we can't strip per-invocation there. Mode blocks are contracts (~20–40 lines each, 2–4 modes per agent), not methodology — the file-size budget is: no agent file grows more than ~20%, and extraction should *shrink* the largest ones by deleting duplicated/contradictory prose.
**Trade-offs:** A standalone run carries a few hundred stray tokens of other modes' YAML. Negligible against the turns/knowledge-loading costs this design removes.

**Decision 7: Extraction order is risk-ascending with the PII agent second-to-last and the assembler last.**
**Alternatives:** DAG order (discovery first); alphabetical; all-parallel.
**Rationale:** Learn the extraction mechanics on benchmark-librarian (small, already standalone-friendly) where a mistake is cheap; hit the PII round-trip and the 4-mode assembler after the pattern is proven ×8.
**Trade-offs:** The highest-value agents are extracted last; acceptable because every extraction lands value independently.
