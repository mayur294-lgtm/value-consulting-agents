---
version: 3
status: built
date: 2026-07-24
author: Mariam Titus George
previous: prd-v1.md
---

<!-- Version note: v2 is intentionally skipped on this branch. PR #97 (feat/ctp-critty)
     already carries .prd/prd-v2.md (Critical Thought Partner). Numbering this PRD v3
     avoids an add/add merge conflict and keeps both change records intact. -->

# PRD v3 — Skill-First Phase 1: Mode-Scoped Agent Contracts

## 1. Problem

Consultants use individual skills far more than the full pipeline — the 2026-07 engagement record (People's First Bank, Bank Australia, HNB, MyState) is almost entirely single-skill invocations, while the docs, agent definitions, and governance all assume the orchestrated pipeline. This mismatch has three concrete costs:

1. **Split-brain contracts.** Each pipeline agent's real operating contract — which files to read and write, phase behavior, output discipline, knowledge whitelist — lives in `orchestrate.py`'s inline prompt strings, while the agent `.md` file describes a different (and in places contradictory) invocation model. Example: agent descriptions instruct Task-tool orchestration; the orchestrator injects a hard ban on it. Standalone invocations of the same agent get undefined behavior — the multi-mode agents (e.g. the assembler's shard / report / HTML-partial behaviors) are selected entirely by injected prompt text a standalone consultant never sends.
2. **Orphaned safety logic.** ROI reasonableness capping, PII de-anonymization, and output validation run only inside the pipeline. A standalone `/build-roi` today produces uncapped numbers and never de-anonymizes — skill-first usage silently ships less defensible output than pipeline usage.
3. **Unscoped context loading.** Blanket "read the domain pack" instructions make agents load knowledge files wholesale. The injected pipeline prompts already scope this per step; standalone runs don't, which costs minutes per invocation.

If we don't solve this, consultants keep defaulting to raw Claude for anything lightweight (the documented adoption killer), and every future skill improvement has to be made twice — once in the `.md`, once in the orchestrator's copy.

## 2. Solution

Make each agent's `.md` file the single source of truth for its operating contract, expressed as **named mode sections** inside the existing file (no new file types — the harness, CI, and eval registry keep treating one file per agent as the component). Each mode section declares: required inputs and degraded behavior when missing, required outputs, knowledge-file whitelist, and phase/checkpoint behavior. `orchestrate.py` stops carrying private prompt copies and instead invokes agents with a mode name plus runtime parameters (paths, domain); an invocation loads only its mode's contract, so per-run context stays small even as files grow. Safety logic that currently exists only inside the pipeline (ROI capping, de-anonymization, output validation) moves to the artifact boundary as utilities invoked by whichever path produces or consumes the artifact — pipeline and standalone runs get identical guarantees.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| The 10 pipeline-invoked agents: discovery-transcript-interpreter, journey-builder, market-context-researcher, capability-assessment, roi-hypothesis-builder, benchmark-librarian, roi-financial-modeler, roadmap-prioritization, narrative-assembler, knowledge-harvester | Governance tiering (light vs engagement mode) — Phase 2 |
| Extracting orchestrate.py's inline agent prompts into mode sections in the agent `.md` files, one agent at a time | Jobs-to-be-done front door / launcher — Phase 3 |
| Resolving every contradiction between an agent `.md` and its injected prompt (each resolution logged, not silent) | Deprecated-file pruning, hardcoded-path fixes — Phase 3 |
| Moving ROI reasonableness capping, de-anonymization, and output validation to artifact-boundary utilities shared by pipeline and standalone paths | The Ignite Inspire workshop subsystem (already Claude-orchestrated) |
| Per-mode knowledge-file whitelists replacing blanket domain-pack reads | The bb-* harness, hooks, eval infrastructure |
| orchestrate.py reduced to composer: DAG, checkpoints, PII round-trip, Python-only merge/assembly steps | Changing what the harness treats as a component (contracts stay inside agent `.md` files) |
| Defined standalone (no-directive) behavior for each of the 10 agents, including degraded behavior when upstream artifacts are absent | New agents or new skills |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Agent instruction text remaining in orchestrate.py | Zero — the script passes mode name + runtime params only |
| Contradictions between agent `.md` and injected prompts | Zero remaining; every resolution decision logged in the change record |
| Standalone invocation behavior | Each of the 10 agents produces its mode-defined outputs when invoked without the orchestrator, with defined degraded behavior on missing inputs |
| Safety parity | Standalone ROI runs produce capped configs identical in treatment to pipeline runs; standalone outputs in engagement dirs get de-anonymization and validation |
| Pipeline regression | Pipeline-altitude eval stays ≥ 0.90 after each agent's extraction (verified incrementally, not big-bang) |
| Per-invocation context | Each mode's knowledge whitelist is explicit; no mode instructs a blanket domain-pack read |

## 5. Eval Acceptance Criteria

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| Each of the 10 extracted agents | Existing component row for that agent (code + judge checks, committed synthetic goldens) | 0.80 | unit |
| Full agent chain | `pipeline` case (golden engagement, inter-agent contracts) | 0.90 | pipeline |
| roi-financial-modeler + capping utility | Existing roi rows PLUS new case: an over-cap `roi_config.json` produced via the standalone path is capped identically to the pipeline path (golden: capped config; negative: uncapped config must fail) | 0.80 | unit |
| Deliverables | `roi`, `assessment`, `report`, `deck` deliverable cases (now pointing at committed fixtures, gate in BLOCKING mode) | 0.80–0.85 | deliverable |

- **Per-ticket verify:** every extraction ticket runs `scripts/test_agent.py` (structural), `run_experiment.py --component <agent> --altitude unit`, and `run_experiment.py --altitude pipeline`. A ticket is not done until all three pass. This is the core safety property of the whole PRD: extraction proceeds one agent at a time, and the pipeline gate must be green before the next agent starts.
- **New eval cases authored in this work:** (a) the standalone-capping parity case above; (b) a structural check (registry preflight or `test_agent.py`) that each of the 10 agent files contains its declared mode sections, so a missing mode fails CI rather than producing undefined behavior.
- **Downstream consumers:** yes, this change affects every downstream consumer by design — the pipeline-altitude experiment is the binding gate throughout.
- **Precondition:** PR #92 (goldens re-pointed to committed fixtures + gate flipped to BLOCKING) must be merged to main before extraction tickets start; this PRD's verify story is meaningless against the old vacuous registry.

## 6. Out of Scope

- Governance tiering, per-skill `governance:` classification, hook changes, telemetry ping for light-tier runs (Phase 2 — separate PRD)
- Front-door launcher, README/QUICKSTART inversion, deprecated-file deletion, duplicate roi-business-case-builder resolution, hardcoded `/Users/mayur@backbase.com` path fixes (Phase 3 — separate PRD)
- Any change to Ignite Inspire agents, workshop templates, or the nested Inspire CLAUDE.md
- Deprecating or replacing orchestrate.py — it survives as the recipe for full assessments
- Changing checkpoint semantics, journal requirements, or telemetry format (Phase 2 decides those)

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| PR #92 unmerged (fixed goldens + BLOCKING gate) | Extraction tickets verify against a vacuous gate | Hard precondition: merge #92 first; this branch is stacked on it |
| Contradiction resolution requires judgment (which behavior was intended: `.md` or injected prompt?) | Silent wrong calls change agent behavior undetected | Every resolution logged in the change record; component eval + pipeline eval must pass per agent; ambiguous cases escalated to the Architect rather than decided in-edit |
| `evals.yml` check not yet marked Required in branch protection | BLOCKING job can fail while merge still proceeds | Repo admin (Mayur) marks the check Required; until then, treat a red evals job as merge-blocking by convention |
| Mode sections grow agent files substantially | None at runtime if invocations stay mode-scoped; risk is only if an invocation loads the whole file | Contract rule: an invocation receives core identity + one mode section only; enforced by the composer and stated in each agent's contract preamble |
| Open PR #97 also touches CLAUDE.md and `.prd/` | Merge conflicts | This PRD numbered v3 to avoid the known prd-v2 add/add conflict; CLAUDE.md untouched by this PRD (its skill-first rewrite is Phase 3) |

## Rollback Plan

Extraction is per-agent and incremental. Each agent's extraction is a self-contained change: if its component or pipeline eval goes red and can't be fixed forward, revert that agent's commits — the orchestrator's injected-prompt path for the remaining agents is untouched until their own extraction lands. No flag-day migration; orchestrate.py supports mixed state (extracted agents invoked by mode, unextracted agents via legacy inline prompts) for the duration of the rollout.
