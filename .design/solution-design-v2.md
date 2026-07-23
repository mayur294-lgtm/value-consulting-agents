---
version: 2
prd: prd-v2.md
status: draft
date: 2026-07-23
author: Mariam Titus George
previous: solution-design-v1.md
---

# Solution Design — Critical Thought Partner + `/critty`

Stack: Claude Code prompt components (Markdown) + Python eval rubrics. No app runtime. The "solution" is prose + governance wiring + deterministic eval checks. All changes are **additive and backward-compatible** — no existing component's behaviour or output shape changes.

## Component Structure

```
CLAUDE.md                                              — MODIFIED: add lean "You Are a Critical Thought
                                                         Partner, Not a Typist" section (after "Reason from
                                                         Evidence"); add CTP row to the Mandatory Governance
                                                         Standards table.
knowledge/standards/
  critical_thought_partner_protocol.md                 — NEW: the depth. Governing principle, the Governor
                                                         (triggers T1–T5 + suppression S1–S4 + form/depth),
                                                         the five functions, detection mechanisms, worked
                                                         example, v1 limits, related-standards pointer.
.claude/commands/
  critty.md                                            — NEW: the on-demand escalation command. 7 steps:
                                                         load full protocol → scope → align → hunt (5 fns) →
                                                         proactive provenance → challenge register → flag
                                                         where independence bites harder.
evals/
  registry.yaml                                        — MODIFIED: add two component cases (`critty`,
                                                         `critical-thought-partner`).
  rubrics/component/
    critty.py                                          — NEW: deterministic evaluate(target) for critty.md.
    critical_thought_partner.py                        — NEW: deterministic evaluate(target) for the standard
                                                         + CLAUDE.md wiring.
tests/quality_metrics.yaml                             — MODIFIED (optional): add structural rules so
                                                         test_agent.py recognises the new command/standard.
```

Contribution tier: all paths (CLAUDE.md, `.claude/commands/`, `knowledge/standards/`, `evals/`) are **Architect-tier**. Author (Mariam) is an Architect — clears `enforce-contribution-scope.yml`.

## Data & Contract Model

There are no engagement-data contracts here — the "contract" is the required structure each artifact must contain, which the eval checks enforce.

```yaml
# critty.md — command contract
name: critty
description: "on-demand hard critical pressure-test"   # frontmatter required by test_agent.py
required_behaviours:                                   # each = one deterministic eval check
  - load_full_protocol            # Step 1 reads the standard file in full (+ fallback if absent)
  - scope_target                  # Step 2 resolves what to critique
  - align_before_critique         # Step 3 confirms framing first (Function 1)
  - five_function_hunt            # Step 4 runs all five functions regardless of triggers
  - proactive_provenance_split    # Step 5 "I can challenge" vs "I can't verify without source data"
  - challenge_register            # Step 6 ranked table w/ calibrated confidence
  - independence_flag             # Step 7 names where a fresh-context critic bites harder
```

```yaml
# critical_thought_partner_protocol.md — standard contract
required_sections:
  - governing_principle           # "challenge everything is as useless as challenge nothing"
  - governor_triggers             # T1–T5 (materiality, contradiction, load-bearing assumption,
                                  #        framing mismatch, consequential gap)
  - governor_suppression          # S1–S4 (already-decided, cosmetic, closed, low-impact)
  - five_functions                # problem def, context completeness, input exam, direction, correction
  - detection_mechanisms          # structural / mechanism / procedural / inconsistency / domain-template
  - worked_example
  - v1_limits                     # "sharpener not oracle" + "instruction not independence"
# CLAUDE.md wiring (checked by the same evaluator):
claude_md_wiring:
  - core_section_present          # "Critical Thought Partner, Not a Typist" heading
  - governance_table_row          # CTP row in the Mandatory Governance Standards table
  - zero_challenges_framing       # "most turns need no challenge" governing principle stated in core
  - limits_present                # both v1 limits stated in core
```

Rationale for the two-artifact split (lean core + deep standard): mirrors the existing governance pattern (Security/Auditability/Context each have a lean CLAUDE.md pointer + a full `knowledge/standards/*.md`). Keeps CLAUDE.md scannable; puts the exact rules where an agent that needs depth can load them; `/critty` force-loads the depth.

## Agent / Pipeline Steps

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `critty` | command (skill) | consultant invocation (± target) | challenge register in-chat | On-demand hard pressure-test |
| CTP behaviour | governance prose | every turn's context | zero-or-one batched challenge | Always-on governed challenge |
| `rubrics.component.critty` | eval evaluator | `.claude/commands/critty.md` | `list[CheckResult]` | Verify command completeness |
| `rubrics.component.critical_thought_partner` | eval evaluator | `knowledge/standards/critical_thought_partner_protocol.md` (+ reads CLAUDE.md) | `list[CheckResult]` | Verify standard + wiring |

No agent invocations, no pipeline steps, no model calls added. The eval evaluators follow the existing `rubrics/component/*.py` convention: `evaluate(target)` where target is the resolved file path, returning soft `CheckResult`s with a small number of `hard_fail=True` on genuinely load-bearing structure (e.g. frontmatter, protocol-load step).

## Integration Points

| Existing component / step | How it's touched | Risk |
| --- | --- | --- |
| `CLAUDE.md` | Additive: one new core section + one governance-table row. No existing rule changed. | Low |
| Mandatory Governance Standards contract | New standard becomes binding on all agents *by reference* — but v1 is behavioural, no per-agent edits, so no agent output changes | Low |
| `evals/registry.yaml` | Two new component cases appended; existing cases untouched | Low |
| `evals/run_experiment.py` | No change — new cases use the default `rubrics.component.{name}` evaluator resolution already in place | Low |
| `scripts/test_agent.py` / `tests/quality_metrics.yaml` | New command/standard must pass structural checks; may need a rule so they're recognised | Low |
| `require-harness.py` hook | Edits to component paths are permitted because this bb-* cycle is active | Low |
| Pipeline altitude (`--altitude pipeline`) | Must stay green; change is additive governance with no data-flow effect | Low |
| Every downstream agent | None consume CTP output as data — behavioural only | Low |

## Technical Decisions

**Decision:** Two artifacts — a lean CLAUDE.md core section + a full `knowledge/standards/` protocol — rather than one.
**Alternatives considered:** (a) Everything inline in CLAUDE.md; (b) standard only, no core section.
**Rationale:** Matches the established governance pattern (Security/Auditability/Context). The core must be self-sufficient for the common case; depth is loaded on demand by `/critty`. (a) bloats CLAUDE.md; (b) leaves the always-on behaviour without a home in the file every agent reads.
**Trade-offs:** Two files to keep in sync — the eval's cross-link + limits-present checks guard drift.

**Decision:** Eval gate is structural presence + protocol completeness, not a live-behaviour LLM judge.
**Alternatives considered:** An LLM-judge scoring real transcripts for good/bad challenges.
**Rationale:** CTP's own v1 limit — it's the same model over the same context; a credible quality judge needs a fresh-context critic, which is out of scope. Deterministic checks are honest about what they verify (the artifacts say the right things) vs. what they can't (runtime behaviour). Consistent with this cycle's "deterministic checks only, judges skipped" precedent (PRD v1).
**Trade-offs:** The gate can't catch a well-worded-but-behaviourally-inert protocol. Accepted and named as a v1 limit; fresh-context-critic eval is the planned evolution.

**Decision:** No per-agent prompt edits this cycle; CTP binds via the mandatory-standards contract.
**Alternatives considered:** Inject a CTP block into all ~22 agent prompts now.
**Rationale:** Keeps the change additive and low-risk (zero existing-output change → all current evals stay green). Broad per-agent embedding is a larger, separately-testable cycle.
**Trade-offs:** Uptake relies on the standards-contract inheritance rather than explicit per-agent text; flagged in PRD Out of Scope.

**Decision:** `/critty` degrades gracefully when the protocol file is absent (fallback to CLAUDE.md summary, with a stated limitation).
**Alternatives considered:** Hard-fail if the file is missing.
**Rationale:** The command may be run on a branch that predates the standard; a useful degraded mode beats a dead command, and honesty about the limitation matches the "instruction not independence" ethos.
**Trade-offs:** Slightly more prose in the command; worth it for robustness.
