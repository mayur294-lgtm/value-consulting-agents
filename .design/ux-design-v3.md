---
version: 3
prd: prd-v3.md
status: draft
date: 2026-07-24
author: Mariam Titus George
previous: ux-design-v1.md
---

<!-- Version note: v2 is intentionally skipped — PR #97 (feat/ctp-critty) carries
     .design/*-v2.md. See prd-v3.md for the same convention. -->

# UX Design v3 — Skill-First Phase 1: Mode-Scoped Agent Contracts

There is no visual UI in this change. The "users" are (a) consultants invoking an agent standalone, (b) the orchestrator invoking the same agent inside the pipeline, and (c) the developer performing each extraction. The UX is the invocation experience: what each caller must provide, what happens when inputs are missing, and what guarantees hold on the way out.

## User Flows

### Flow 1 — Consultant invokes an agent standalone (the flow this PRD makes real)

```
Consultant invokes agent/skill (no phase directive)
        │
        ▼
Agent resolves mode = standalone (its default mode section)
        │
        ▼
Input check against the mode's declared inputs
        │
        ├──[all required inputs present]──▶ Full run per mode contract
        │                                        │
        │                                        ▼
        │                              In-session consultant checkpoint
        │                              (interactive — no CHECKPOINT_*.md
        │                               handshake wait)
        │                                        │
        │                                        ▼
        │                              Writes ONLY the mode's declared outputs
        │
        └──[required input missing]──▶ Degraded path per mode contract:
                                       agent states what's missing, what it
                                       can still produce, and asks the
                                       consultant to supply the gap inline
                                       (paste content / point at a file / skip)
        │
        ▼
Artifact gates run on declared outputs where applicable
(ROI capping for roi_config.json; validation + de-anonymization
 when output lands in an engagement outputs/ dir)
        │
        ▼
Consultant sees: outputs written + one-line gate report
("roi_config.json: backbase_impact capped 0.72 → 0.60 on L3")
```

### Flow 2 — Orchestrator invokes the same agent (pipeline mode)

```
orchestrate.py step reaches agent N
        │
        ▼
Composer: parse agent .md → select mode section named in the DAG
(e.g. mode: pipeline) → strip all other mode sections
        │
        ▼
System prompt = core identity + selected mode + runtime params
(outputs_dir, domain, engagement paths — values only, no instructions)
        │
        ▼
Agent runs the mode contract: file checkpoint protocol
(CHECKPOINT_x.md → _APPROVED.md), declared outputs only
        │
        ▼
Same artifact gates as Flow 1 — now invoked by the orchestrator
at the same boundary, not as private step logic
        │
        ├──[gates pass]──▶ next DAG step
        └──[gate caps/fails]──▶ logged to run output + checkpoint trail,
                                identical treatment to standalone
```

### Flow 3 — Developer extracts one agent (repeated 10×)

```
Pick next agent in the extraction order
        │
        ▼
Diff agent .md vs orchestrate.py's injected prompt(s) for that agent
        │
        ▼
Resolve contradictions (log each resolution; escalate ambiguous
calls to the Architect — never decide silently)
        │
        ▼
Write mode sections into the .md; replace the f-string in
orchestrate.py with a composer call (mode + params)
        │
        ▼
Verify: test_agent.py → component eval ≥ 0.80 → pipeline eval ≥ 0.90
        │
        ├──[green]──▶ commit; next agent
        └──[red, can't fix forward]──▶ revert this agent's commits;
                                       legacy inline path still intact
```

## Screen & Component States

No screens. The interactive component is the agent invocation itself:

| State | Trigger | What the caller sees |
| --- | --- | --- |
| Mode resolved | Invocation starts | Which mode is running and why (directive present → named mode; absent → standalone) |
| Inputs satisfied | All required inputs found | Normal run; no noise |
| Degraded | Required input missing (standalone) | What's missing, what can still be produced, inline options to supply or skip |
| Blocked | Required input missing (pipeline) | Step fails fast with the missing path — no silent skip of a required artifact |
| Checkpoint pending | Mode reaches its checkpoint | Standalone: in-session question. Pipeline: CHECKPOINT_*.md written, waiting on _APPROVED.md |
| Gated | Artifact gate modified/flagged an output | One-line report of exactly what was capped/fixed/flagged and why |
| Done | Declared outputs written | List of files written — and nothing not declared by the mode |

## Error States

| Error | Cause | User-facing message | Recovery |
| --- | --- | --- | --- |
| Missing mode section | Agent .md lacks the mode the caller requested | `Agent <name> has no mode '<mode>'. Available: standalone, pipeline.` (CI preflight makes this unreachable in a merged state) | Developer adds the mode section; caller picks an available mode |
| Required input absent (standalone) | Consultant invoked cold without upstream artifact | `<mode> needs <artifact>. I can proceed without it by <degraded behavior>, or paste/point me at it.` | Supply inline, point at file, or accept degraded output |
| Required input absent (pipeline) | Upstream step failed or was skipped | Step error naming the missing path and the producing step | Re-run producing step (`--resume-from`) |
| ROI config over cap | Modeled impact exceeds reasonableness bounds | `backbase_impact on <lever> capped <x> → 0.60; 5-yr ROI recomputed. See gate report.` | None needed — capped output is the deliverable; consultant can revisit lever assumptions |
| De-anonymization mapping missing | Output in engagement dir but no `.pii_mapping.json` | `Outputs still contain placeholders — no PII mapping found. Deliverable is NOT client-ready.` | Run the anonymization round-trip or confirm placeholders are intended |
| Checkpoint approval never arrives (pipeline) | `_APPROVED.md` not produced | Existing orchestrator timeout behavior — unchanged by this PRD | Consultant approves or run resumes in non-interactive mode |
