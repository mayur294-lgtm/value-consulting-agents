---
version: 1
status: draft
date: 2026-06-22
author: Mayur Vichare
previous: null
---

# Sprint Plan v1 — Trustworthy Runs

## 1. Goal

This cycle succeeds iff a real engagement runs end-to-end and produces a run report that certifies every expected artifact for the run's mode as present and valid — or names exactly which artifact failed and why.

## 2. Non-goals

- No per-agent timeouts beyond the existing Block A wrapper (deferred backlog item).
- No turn-budget reservation for turn-hungry agents (deferred).
- No interception or atomization of agent-authored SDK writes (out of the local-SDK model — see ADR-001).
- No dead-agent detection, retry, or relaunch logic.
- No cloud/Postgres or knowledge-graph work (that's the KG flywheel roadmap, not this cycle).

## 3. Solution

This cycle makes a full pipeline run *trustworthy*: the big outputs the system writes itself can no longer be left half-written and corrupt, every stage checks that what it produced is real (not empty, not a stub, and parseable), and the run always ends by writing a report that says — artifact by artifact — whether the run is sound or exactly where it broke. The consultant gets a clear, machine-readable verdict on every run instead of discovering a missing or garbled deliverable at the end.

## 4. User-stories slice

- `US-001` — durable writes for the writes we own: the orchestrator's Python writes (shard merge, HTML assembly, `roi_config.json` mutation, de-anonymization pass) and the tool `.save()` methods (Excel/PPTX/HTML).
- `US-002` — per-stage validation upgraded from existence+size to existence + non-stub + parseable (JSON parses; HTML clears size/placeholder; markdown clears a stub heuristic).
- `US-003` — an always-written, machine-readable run report capturing per-stage status, timing, cost, and each expected artifact's verdict.
- `US-004` — the validator is driven by a mode-aware expected-output manifest so intermediates (e.g. non-interactive assembly shards) and skipped checkpoints aren't false-flagged.
- `US-005` — pytest coverage for the new durable-write and validation helpers (first pytest in the repo).

## 5. Scope

| In scope this cycle | Out of scope this cycle |
| --- | --- |
| Durable-write helper (tmp + `os.replace`) for code-owned writes | Atomizing agent SDK Write-tool outputs (ADR-001) |
| Routing tool `.save()` methods (Excel/PPTX/HTML) through atomic save | Streaming/incremental writes for individual files |
| Per-stage content validation (non-stub + parseable) | Full per-artifact schema validation |
| Mode-aware expected-output manifest | New engagement types or output formats |
| `.pipeline_run_report.json` written via try/finally on every run | Per-agent timeouts beyond Block A; turn reservation; retry |
| Halt-dependent-stage-but-always-report failure semantics | Cloud graph, KG validator, coach agent |
| pytest harness + tests for the new helpers | Backfilling tests for the rest of the codebase |
| Encoding-consistency fixup on the writes we touch | Repo-wide encoding sweep |

## 6. Architecture (shape of the change)

Adds a durable-write helper (tmp-file + `os.replace`) that the orchestrator's Python writes and the tool `.save()` methods route through; inserts a per-stage validator backed by a mode-aware expected-output manifest after each `step_*` completes; and adds a `step_report()` that always writes `.pipeline_run_report.json`. No change to agent prompts or the SDK invocation path. (System description to be captured in `.spec/spec.md` at `/sprint-refine` — no spec exists yet.)

## 7. Success metric (target)

North-star (decision-ready engagements, defined in `.brief/brief.md`): this cycle removes *silent failure* as a cause of non-decision-ready runs. Cycle target: across a full validation run, **0 silent missing/corrupt outputs** (every failure surfaced), and a run report emitted on **100%** of runs including failed ones.

## 8. Timebox

One cycle — approximately one focused week.

## 9. Definition of Done

Per the canonical Definition of Done in `.brief/brief.md#definition-of-done`. Cycle-specific exit condition: a real engagement (one interactive and one non-interactive run) completes and its `.pipeline_run_report.json` certifies all expected artifacts valid.

## 10. Dependencies & Risks

| Dependency / Risk | Impact | Tracking |
| --- | --- | --- |
| Agent-authored outputs remain non-atomic by design (ADR-001) — validation, not durability, is their safety net | Corrupt agent-written file is caught after the fact, not prevented | Accepted limitation; revisit per ADR-001 |
| Mode matrix must be encoded correctly or validation false-flags skipped/intermediate outputs | False failures erode trust in the report | Mitigated by US-004; verified by the two-mode DoD run |
