---
version: 7
prd: prd-v7.md
status: draft
date: 2026-08-26
author: Mariam Titus George
previous: ux-design-v6.md
---

# UX Design v7 — The verify gate's honest surface

The "users" here are three, and they experience the gate very differently:

| Who | Where they meet it | What they need from it |
| --- | --- | --- |
| **Developer** running a bb-* cycle | `run_experiment.py` locally, `bb-build`'s verify step | To be told the truth about whether their change was verified — including "it wasn't" |
| **Reviewer** on a PR | the `evals.yml` comment | To know what was actually exercised, not just a score |
| **Consultant** mid-engagement | `eval-on-stop` hook, `.pipeline_run_report.json` | Flags on real deliverables, with **no false reds** on good work |

The whole spec is a messaging problem. v7's defect was never a wrong number — 1.000 was arithmetically correct. It was a **claim attached to a number**. So every state below is specified by the sentence it prints.

---

## User Flows

### Flow 1 — Developer verifies a change (the flow that was lying)

```
developer edits a component
        │
        ▼
run_experiment.py --component <name>
        │
        ├─ row is EXECUTABLE tier ──────────────► builds fixture in tmpdir
        │                                          invokes real code
        │                                          injects fault
        │                                          ▼
        │                                    score + "exercised: <module> via <interpreter>"
        │
        ├─ row is RUBRIC-CALIBRATION tier ─────► scores frozen golden
        │                                          ▼
        │                                    score + BANNER:
        │                                    "This scores the RUBRIC, not the component.
        │                                     It cannot detect a change to <agent>.md."
        │
        └─ row is PROSE and dev changed a prompt ► REFUSES to imply verification:
                                                   "No gate covers <agent>.md.
                                                    Run: evals/path1.py --agent <name> (local, uses your
                                                    Claude subscription), or state in the PR that this
                                                    change is unverified."
```

The third branch is the flow that did not exist and is the reason #118–#123 shipped on a rubber stamp.

### Flow 2 — The mutation proof (new)

```
run_experiment.py --mutate <component>
        │
        ▼
for each declared check:
   copy target module(s) → tmpdir ──► apply named mutation ──► run THAT check
        │                                                            │
        │                                          ┌─────────────────┴──────────────┐
        │                                          ▼                                ▼
        │                                    check went RED                   check stayed GREEN
        │                                          │                                │
        │                                    restore, re-run                  ✗ FAIL THE RUN
        │                                          │                          "check <name> did not
        │                                          ▼                           detect <mutation>.
        │                                    green again → ✓ PROVEN            A gate that cannot fail
        │                                                                      certifies nothing."
        ▼
discard tmpdir (working tree never written to)
```

### Flow 3 — CI gate on a PR

```
PR opened
   │
   ▼
paths filter ── includes .claude/hooks/** (:114 fix) ──► gate runs
   │
   ▼
registry preflight
   ├─ a declared check has no mutation entry ──► FAIL (before any scoring)
   ├─ a gating golden can't resolve ──────────► FAIL
   └─ clean ──► suite runs
        │
        ▼
   for each row: score + assert every DECLARED check executed
        │
        ├─ a declared judge didn't run ──► FAIL ("declared means required")
        └─ all executed ──► verdict
        │
        ▼
   PR comment states, per row: score, tier, what was exercised, mutation-proof status
```

### Flow 4 — Path-1, local only

```
developer: evals/path1.py --agent <name>   (or --component <name> --regenerate)
        │
        ▼
  CI environment detected? ($CI / $GITHUB_ACTIONS set)
        │
        ├─ YES ──► REFUSE, exit non-zero:
        │          "path-1 regeneration never runs in CI. It costs money or
        │           subscription quota and is nondeterministic. CI is $0 by design."
        │
        └─ NO ──► claude -p, subscription-funded, serial
                     │
                     ▼
              score with the row's REAL rubric (not just the governance baseline)
                     │
                     ▼
              report + explicit note: "single run, nondeterministic — not a gate"
```

### Flow 5 — Consultant runtime scoring (unchanged path, corrected content)

```
pipeline run ends / consultant session stops
        │
        ▼
runtime.score_engagement() ──► same rubrics as the dev gate ("one rulebook, two contexts")
        │
        ▼
.pipeline_run_report.json + flags
        │
        ├─ rubric parser doesn't recognise the artifact's schema ──► must NOT emit 0/0
        │                                                            (the :41 false red)
        │                                                            emits: UNSCORABLE + reason
        └─ genuine low score ──► flag with the failing check named
```

---

## Screen & Component States

### `run_experiment.py` output states

| State | Trigger | What is printed |
| --- | --- | --- |
| Executable PASS | tier=executable, all checks green | Score, `tier: executable`, `exercised: <module> via <interpreter from settings.json>`, `mutations: N/N proven` |
| Executable FAIL | any check red | Score, the **named** failing check, its detail, and the mutation that covers it |
| Calibration PASS | tier=rubric-calibration, golden scores ≥ threshold | Score **plus the standing banner**: "scores the RUBRIC, not the component" |
| Calibration FAIL | golden dropped below threshold | "The rubric changed, or the golden did. This is a rubric regression, not an agent regression." |
| Negative correctly failed | fixture mutation applied, named check went red | `✓ negative <check>: correctly FAILED` |
| Negative wrongly passed | fixture mutation applied, check stayed green | `✗ <check> did not detect <mutation> — this check certifies nothing` → run fails |
| Uncovered prose change | dev changed `.claude/agents/*.md`, no executable row covers it | Refusal text from Flow 1, branch 3 |
| Declared-but-unrun check | registry lists a check the run didn't execute | `✗ declared but not executed: <name>` → run fails |
| Missing target | registry `input:` doesn't resolve | **FAIL**, not `[SKIP]` (today it skips and leaves the verdict PASS) |
| Old altitude name | `--altitude pipeline` | Hard error, exit non-zero, with the rename rationale inline |

### Registry preflight states

| State | Trigger | Behaviour |
| --- | --- | --- |
| Clean | every gating golden resolves, every declared check has a mutation | Proceed |
| Unresolvable golden | path missing / gitignored | FAIL (existing behaviour, kept) |
| Check without a mutation | a name in `code:` with no `mutations:` entry | **FAIL** — new; this is what makes the mutation proof non-optional |
| Bare-name engagement golden | legacy `golden_engagement: <name>` | DEBT line (existing behaviour, kept) |

### `.pipeline_run_report.json` states (consultant-facing)

| State | Meaning |
| --- | --- |
| `pass` | scored at or above threshold |
| `flag` | scored below threshold; the failing check is named |
| `unscorable` | **new** — the rubric could not parse the artifact (schema drift). Never rendered as 0/0 |
| `error` | the rubric raised; message captured |

---

## Error States

Every message below is the literal text. This spec exists because vague messages are how the gate lied.

| Error | Cause | Message | Recovery |
| --- | --- | --- | --- |
| Uncovered prose change | Ticket edited an agent prompt; no executable row covers it | "No executable gate covers `.claude/agents/<name>.md`. A component-altitude score against a frozen golden does **not** verify a prompt change — it scores the rubric. Either run `evals/path1.py --agent <name>` locally (uses your Claude subscription, not an API key), or record in the PR that this change is unverified." | Run path-1, or state it plainly in the PR |
| Mutation missing | A declared check has no mutation entry | "Check `<name>` on row `<row>` has no mutation proof. A gate that cannot fail certifies nothing — add a `mutations:` entry showing what makes it go red." | Add the entry |
| Mutation ineffective | Mutation applied, named check stayed green | "Check `<name>` did not detect mutation `<id>` (`<file>`: `<find>` → `<replace>`). Either the check is inert or the mutation is wrong. Both must be resolved before this row can gate." | Fix the check or the mutation |
| Declared check not executed | Registry declares it; the run didn't run it | "Row `<row>` declares `<name>` but it did not execute. Declared means required — a check that silently doesn't run is indistinguishable from one that passes." | Fix the wiring, or remove the declaration |
| Judge unavailable | `claude` CLI absent or not authenticated | "Judge `<name>` is declared but the `claude` CLI is unavailable or not logged in. Judges run on your Claude subscription — run `claude` once to sign in. CI rows must not declare judges; CI is key-free by design." | Sign in, or move the judge off a CI row |
| Path-1 in CI | `$CI` / `$GITHUB_ACTIONS` set | "path-1 regeneration never runs in CI. It costs subscription quota, is nondeterministic, and CI is \$0 by design. Run it locally." | Run locally |
| Old altitude name | `--altitude pipeline` | "`--altitude pipeline` was renamed to `--altitude deliverable-structural`. It scores frozen fixture files in ~5s and has never run the pipeline; the old name is what made a 1.000 look like integration evidence. If you want a real end-to-end run, that is out of scope for the gate — run `scripts/orchestrate.py` on a synthetic engagement." | Use the new name |
| Interpreter drift | Rubric's interpreter ≠ the one `settings.json` registers | "Rubric invokes `<X>` but `.claude/settings.json` registers `<Y>` for this hook. The gate would certify under an interpreter no consultant runs." | Rubric derives the interpreter from `settings.json` |
| Unscorable artifact | Rubric parser doesn't recognise the schema | "Rubric `<name>` could not parse `<artifact>` (expected `<shape>`). Reported as **unscorable**, not 0/0 — a parser gap is not a quality finding." | Update the parser; a golden pins the current schema |
| Missing target | Registry `input:` doesn't resolve | "Target `<path>` for row `<row>` does not exist. Failing rather than skipping — a skipped target previously left the verdict at PASS." | Fix the path |

### Message principles

1. **Never let absence read as success.** Skip, unavailable, unparsed, and not-executed all fail or are labelled — none silently pass.
2. **Name what was exercised, not just the score.** Every pass states the module and interpreter it actually ran.
3. **A score always carries its tier.** "1.000 (rubric-calibration)" cannot be misread as "1.000 (verified the agent)".
4. **The error is the documentation.** The old-altitude error explains the rename; the uncovered-prose error explains the alternative. Nobody should have to read this spec to understand a failure.
