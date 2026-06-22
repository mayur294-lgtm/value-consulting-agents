# Architecture Decision Records

All architectural decisions for this project. One decision per section, numbered sequentially. Decisions are append-only — to reverse a decision, add a new one that supersedes it.

---

## ADR-001: Scope atomic writes to code-owned writes only

> In the context of wanting crash-safe pipeline outputs while running agents through the Claude Agent SDK, facing the fact that agent-authored files are written by the SDK's Write tool which our Python cannot intercept, we decided to make only the orchestrator's own Python writes and the tool `.save()` methods atomic, to achieve real durability where we control the write, accepting that agent-authored markdown is protected by validation rather than atomicity.

**Date:** 2026-06-22

**Context:** The #1 reliability pain is corrupt partial files from interrupted large writes. Exploration confirmed the majority of named outputs are agent-authored via the SDK Write tool; only ~7 writes (shard merge, HTML assembly, `roi_config.json` mutation, de-anon pass) and the tool `.save()` methods are our Python. The "stay in the local-SDK model" constraint rules out wrapping or replacing the SDK.

**Decision:** Introduce a durable-write helper (tmp-file in the same directory + `os.replace`) and route all code-owned writes and tool `.save()` methods through it. Agent-authored files are explicitly out of atomic scope and are covered by per-stage validation (ADR-002).

**Alternatives rejected:**
- Intercept the SDK Write tool via a PreToolUse hook to atomize agent writes — fragile, couples to hook internals, and strains the no-new-infra constraint.
- Validation-only, no atomic writes — leaves the biggest code-owned writes (shard merge, Excel save, de-anon rewrite) able to corrupt on interruption.

**Locks in:** A single durable-write path for everything the pipeline writes in Python; two-tier safety model (atomicity for code-owned, validation for agent-owned).

**Makes harder:** Guaranteeing durability of agent-authored markdown — those can still be left partial by an SDK-level crash and are only caught after the fact.

**Scope:** the pipeline write layer (orchestrator + output-producing tools)

**Revisit when:** the Claude Agent SDK exposes a write hook or atomic-write option, or agent-authored files become the dominant corruption source in run reports.

---

## ADR-002: Drive validation from a mode-aware expected-output manifest

> In the context of validating every stage's outputs, facing expected-output sets that differ by run mode, we decided to centralize them in one mode-aware manifest instead of scattered hardcoded checks, to achieve a single source of truth that won't false-flag skipped or intermediate outputs, accepting one more structure that must track the mode matrix.

**Date:** 2026-06-22

**Context:** Expected outputs vary by mode: non-interactive produces `assembly_shard_A/B/C.md` as throwaway intermediates and skips `CHECKPOINT_assembly_CP2`; the ROI financial model runs in Block A2 (non-interactive) vs a later phase (interactive). Today the truth is split between `assert_file_exists` calls and `validate_engagement_outputs.sh`, with no mode awareness.

**Decision:** Define expected outputs (and their required/optional status) per stage × mode in one manifest that the per-stage validator reads. Validation = existence + min-size + non-stub + parseable, keyed off this manifest.

**Alternatives rejected:**
- Keep expected outputs hardcoded in each `step_*` — already drifting across two locations and blind to mode, which would make a content validator false-flag deliberately-skipped or intermediate files.
- Full per-artifact schema validation — heavier than this cycle warrants and over-engineered against the project's simplicity goal.

**Locks in:** A declarative manifest as the source of truth for "what a run should produce"; the validator and run report both consume it.

**Makes harder:** Adding a new mode or output now requires a manifest update (and forgetting one surfaces as a validation false-positive/negative).

**Scope:** the pipeline validation layer

**Revisit when:** a fourth run mode or a per-engagement-type output set makes a flat manifest unwieldy.

---

## ADR-003: Halt the dependent stage on a missing required output, but always emit the run report

> In the context of a run hitting a missing or stub required output, facing a choice between today's halt-at-first-failure and a never-halt collect-everything approach, we decided to halt the dependent stage while always writing the run report via try/finally, to achieve loud, complete failure reporting without burning cost on doomed downstream stages, accepting that a hard dependency failure still stops the run.

**Date:** 2026-06-22

**Context:** Today `assert_file_exists` raises and stops the pipeline at the first missing file, and the only run record is a stdout summary plus a journal append that may never be reached on failure. The success bar for this cycle is "a full run completes cleanly with a run report" — which requires a report even when the run fails.

**Decision:** A genuinely-missing or stub *required* output still halts its dependent stage (fail-loud), but the run report is written in a `finally` block so it exists for every run, success or failure. Optional-output problems are recorded as warnings and do not halt.

**Alternatives rejected:**
- Hard halt at first failure with no guaranteed report (status quo) — you learn one problem at a time and may get no machine-readable record.
- Never halt; run every stage and fail only at the end — wastes API cost on stages that depend on a missing input and can cascade garbage.

**Locks in:** Fail-loud-on-required + always-report as the run lifecycle's error contract; report-writing must be crash-path-safe (try/finally).

**Makes harder:** "Best-effort, produce whatever you can" runs — a required-output failure is intentionally terminal for its dependents.

**Scope:** the pipeline run lifecycle / error semantics

**Revisit when:** consultants need partial deliverables from a run with a known-failed stage often enough to justify a degraded-mode path.

---

## ADR-004: Emit the run report as a dot-prefixed machine-readable JSON

> In the context of needing a durable record of what a run produced, facing the existing stdout-only summary and a journal append that isn't machine-readable, we decided to write `.pipeline_run_report.json` (dot-prefixed to avoid the journal Stop hook), to achieve a machine-readable per-run verdict, accepting a new artifact contract that downstream tooling may come to depend on.

**Date:** 2026-06-22

**Context:** The only persistent run record today is a journal markdown append (fragile format, only if the journal exists) and a terminal summary. There is no machine-readable manifest of per-stage status and per-artifact validation verdict. The `enforce-journal.py` Stop hook treats new non-dot deliverable files as client deliverables and forces a journal entry.

**Decision:** Write a `.pipeline_run_report.json` capturing per-stage status, elapsed, cost, and each expected artifact's verdict (e.g. REAL / STUB / MISSING) plus any timeouts. Dot-prefixed so the journal hook ignores it (it excludes `.`-prefixed names); not a client deliverable.

**Alternatives rejected:**
- Extend the existing `ENGAGEMENT_JOURNAL.md` timing entry — not machine-readable and the append format is fragile/interruptible.
- A non-dot `run_report.md` deliverable — trips the `enforce-journal` Stop hook and reads as a client-facing artifact, which it isn't.

**Locks in:** A JSON run-report schema as the canonical machine-readable run record; the dot-prefix convention for internal (non-deliverable) run artifacts.

**Makes harder:** Changing the report shape later once other tooling consumes it (it becomes a contract).

**Scope:** the pipeline run-reporting layer

**Revisit when:** a second consumer needs the report (e.g. CI or a dashboard) and the schema needs versioning, or a human-readable companion is required.
