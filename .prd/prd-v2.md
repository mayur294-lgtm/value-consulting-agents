---
version: 2
status: draft
date: 2026-07-23
author: Mariam Titus George
previous: prd-v1.md
---

# PRD v2 — Critical Thought Partner (CTP): governed challenge behaviour + `/critty` on-demand pressure-test

## 1. Problem

Cortex is trusted to produce defensible, evidence-traced consulting deliverables — but today it behaves like a **typist, not a thought partner**. It takes the consultant's inputs largely at face value: it will happily model a value lever off a population number that doesn't fit the lever's mechanics, carry a surface ask that has drifted from the agreed problem, or produce an artifact resting on an uncited, load-bearing assumption. The CLAUDE.md "reason from evidence" rules govern what Cortex *produces*; nothing governs whether Cortex *challenges the input* before producing.

This is a live, expensive failure mode. In the MyState IGNITE engagement a single unexamined population figure (416,649 "all retail customers" used for an *in-app* cross-sell lever, when only 372,160 are active digital users) was a ~$4M overstatement that a thought partner would have caught by asking one question. The system did not ask.

Two things are missing:
1. **An always-on discipline** for *when* and *how* Cortex should challenge — one that does not turn Cortex into a contrarian that questions everything (a partner that challenges everything is as useless as one that challenges nothing). The right number of challenges on most turns is zero; the discipline has to be *governed* by triggers and suppression rules, not volume.
2. **An on-demand escalation** — a way for the consultant to deliberately turn the dial to maximum and say "tear this apart" for a specific piece of work, suspending the silence bias and hunting for weaknesses.

If we don't solve it: Cortex keeps shipping the consultant's blind spots downstream into client-facing deliverables, and the one thing a senior consultant does that a document generator can't — pressure-test the thinking before the client sees it — stays absent.

## 2. Solution

Introduce **Critical Thought Partner (CTP)** as a governed, first-class behaviour in two coordinated layers:

- **(a) Always-on, governor-gated challenge behaviour.** A lean, self-sufficient "You Are a Critical Thought Partner, Not a Typist" section in `CLAUDE.md` core, backed by a new mandatory governance standard `knowledge/standards/critical_thought_partner_protocol.md` (the depth: the Governor's triggers/suppression rules, the five functions, gap-detection mechanisms, a worked example, and honest v1 limits). The protocol is registered in the CLAUDE.md Mandatory Governance Standards table alongside Auditability, Context, Security, and Design. The governing principle: challenge is gated by triggers (materiality, contradiction, load-bearing unsupported assumption, framing mismatch, consequential gap) and suppression rules (already-decided, cosmetic, closed topic, low-impact) — most turns produce zero challenges, and that is the system working.

- **(b) `/critty` — on-demand escalation.** A new `.claude/commands/critty.md` skill the consultant invokes to force a hard pressure-test of the current work regardless of triggers. It force-loads the full protocol, aligns on what it's critiquing before tearing in, runs all five functions in "hunt mode," flags weak/unverifiable figures at the point they appear (separating "I can challenge this" from "I can't verify this without source data"), and returns a structured **challenge register** ranked most-serious-first with calibrated confidence. It is honest about its own ceiling: it is the same model reasoning over the same context, so it names where a genuinely independent check would bite harder.

The design is deliberately **honest about v1 limits**: CTP is a behavioural discipline delivered through prompts. It is a *sharpener, not an oracle* (it raises questions and names gaps; it cannot verify a figure without source data) and *instruction, not independence* (it mitigates sycophancy by instruction, not by a fresh-context critic). The protocol and `/critty` both state these limits rather than overselling.

Reference material already exists as working prototypes on the stale branches `mariamt/20260714-ctp-governance` and `mariamt/20260714-critty-skill` (cut before the ROI-provenance work merged); this PRD re-lands that content cleanly on current `main` through the harness.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| New standard `knowledge/standards/critical_thought_partner_protocol.md` (Governor, five functions, detection mechanisms, worked example, v1 limits) | Re-writing existing standards (Auditability, Context, Security, Design) — CTP *reinforces and points at* them, never replaces |
| Lean "You Are a Critical Thought Partner, Not a Typist" section in `CLAUDE.md` core | Changing the existing "Reason from Evidence" / Handling Missing Data rules (CTP adds input-examination + direction-keeping on top) |
| Register CTP in the CLAUDE.md Mandatory Governance Standards table | Rebuilding the governance table format or the other rows |
| New `/critty` command (`.claude/commands/critty.md`) — force-load protocol, align, hunt, challenge register, independence flag | Per-agent embedding of CTP into every one of the ~22 agent prompts (they inherit via the mandatory-standards contract; individual agent edits are a later cycle) |
| A deterministic eval case for the `/critty` command (structural: required sections/behaviours present) + governance-doc presence checks | An LLM-judge that scores live challenge *quality* on a transcript (a fresh-context critic eval is a planned evolution, explicitly a v1 limit) |
| Verify the change is additive and the pipeline-altitude experiment stays green | Auto-emission of challenge logs into the assumptions register / ENGAGEMENT_JOURNAL wiring (behavioural only in v1) |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| New governance standard present and linked from CLAUDE.md core + governance table | Both links resolve; standard file exists |
| `/critty` command is structurally valid and discoverable | Valid frontmatter (`name`, `description`); `test_agent.py` passes on the changed files |
| `/critty` protocol completeness | Command file contains all required behaviours: load full protocol, align-before-critique, five-function hunt, proactive provenance split, challenge-register output, independence flag |
| Governed (not contrarian) framing is explicit | CLAUDE.md section + protocol both state the "most turns = zero challenges" governing principle and the suppression rules |
| No downstream regression | `--altitude pipeline` experiment stays green; existing component evals unaffected |
| Honesty about v1 limits | Both artifacts explicitly state "sharpener not oracle" and "instruction not independence" |

## 5. Eval Acceptance Criteria

CTP is a behavioural discipline delivered through prompts; per its own v1 limits it cannot be fully verified by deterministic checks (challenge *quality* needs a fresh-context critic, which is out of scope). The gate is therefore **structural presence + protocol completeness + no-downstream-regression**, not a live-behaviour judge.

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `critty` (NEW command) | Author new case `critty`: deterministic `code` checks — frontmatter valid; body contains the required sections (load-full-protocol, scope, align-before-critique, five-function hunt, proactive-provenance split, challenge-register table, independence flag) | 0.80 | unit |
| `critical-thought-partner` governance (NEW) | Author new case `critical-thought-partner`: deterministic `code` checks — standard file exists; CLAUDE.md core contains the CTP section; governance-standards table has the CTP row; both cross-links resolve; the "sharpener not oracle" + "instruction not independence" limits present | 0.80 | unit |
| Structural gate (all changed files) | `python scripts/test_agent.py --branch HEAD --base-branch origin/main` | pass | unit |
| Downstream integrity | `python evals/run_experiment.py --altitude pipeline` must stay green (change is additive governance) | no regression | pipeline |

- **NEW component:** fresh eval cases (`critty`, `critical-thought-partner`) MUST be authored as part of this work, with the deterministic `code` evaluators added under `evals/rubrics/component/`.
- The change is additive and backward-compatible; it must not alter any existing component's output, so all current component + deliverable evals must remain green.

## 6. Out of Scope

- Embedding CTP into each of the ~22 individual agent prompts (inherited via the mandatory-standards contract this cycle; per-agent edits are a future cycle).
- A fresh-context / independent critic that reasons outside the critiqued context (named as a v1 limit and a planned evolution — not built here).
- LLM-judge scoring of live challenge quality on real transcripts.
- Wiring CTP challenges into the assumptions register / ENGAGEMENT_JOURNAL automatically.
- Any change to the ROI provenance work (PRD v1) or other components' behaviour.

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| Over-triggering: CTP becomes a contrarian that challenges everything | Erodes consultant trust; noise buries signal | Governor is the core of the design — triggers + suppression rules + "most turns = zero"; both artifacts lead with this |
| Overselling reliability: consultant treats a challenge as verification | False confidence in un-sourced figures | "Sharpener not oracle" + explicit "I can't verify this without source data" split is mandatory in both artifacts, enforced by eval |
| Un-testable behaviour: prompts don't guarantee runtime behaviour | Eval gate can only check presence, not live challenge quality | Honestly scoped: structural + completeness gate now; fresh-context-critic eval flagged as planned evolution |
| Governance sprawl in CLAUDE.md | CLAUDE.md bloat | Core section is lean and self-sufficient; depth lives in the standard, linked once |
