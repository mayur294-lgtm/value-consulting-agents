---
version: 7
status: archived
date: 2026-08-26
author: Mariam Titus George
previous: prd-v6.md
---

# PRD v7 — The verify gate must be able to fail: executable evals, honest altitudes, calibrated goldens

## 1. Problem

The bb-* harness rests on one claim, from the commit that created it (`0079500`, 23 Jun): *"For a document factory there is no compiler, so the eval suite IS the verify gate."* That claim is currently false, and it has been false for every component change since PR #118.

**Measured, this session:** the entire 45 KB `market-context-researcher` agent prompt was replaced with one line of garbage. Its own gate — `run_experiment.py --component market-context-researcher` — returned **1.000 PASS**. The gate named after an agent cannot see that agent.

This is structural, not a bug in one row. `run_experiment.py` has no concept of "the component under change". Every mode — component, deliverable, pipeline — resolves a **file path** from `registry.yaml` and calls `evaluate(path)`. The registry maps a component *name* to a *frozen committed artifact*, and the checks are regexes over that artifact. A frozen file scored by a fixed regex is a **constant function**; it returns the same value forever, whatever happens to the component.

Four compounding findings:

- **No component gate can fail by construction.** Every one of the 16 component rows has `negatives=0`, and `run_experiment.py`'s component branch never reads a `negatives:` key at all — `--negatives` works *only* for deliverables. The README's stated principle ("every golden scores above and every matched negative below; an eval not calibrated against a real failure is decoration") is unavailable at component altitude.
- **`--altitude pipeline` does not run the pipeline.** It returns 1.000 in ~5 s against `evals/goldens/pipeline_engagement/outputs`, scoring pre-existing fixture files. It never executes an agent. It certified three consecutive v6 tickets whose bytes it had not read — a new PreToolUse hook, a security-standard rewrite, and edits to seven agent prompts.
- **The harness actively instructs people to trust it.** `bb-build/SKILL.md:168` tells the implementer that `run_experiment.py --component <changed-component>` verifies a ticket that changed that component. The frozen golden is inert; *this instruction* is what converts inertness into a false "verified" inside the build loop. It is the most harmful artifact in the system.
- **The same failure recurs in CI wiring.** `evals.yml`'s `paths:` filter omits `.claude/hooks/**`, so a PR editing only a hook skips the blocking gate entirely (backlog :114). The `mcp-query-guard` rubric invokes the hook under `sys.executable` (3.11 in CI) while `settings.json` registers bare `python3` (3.9.6 locally), so the gate can certify under an interpreter no consultant runs (:116). CI runs no `--component` evals for changed components and no `report` deliverable (:15). `visual_render.py` is wired to no registry row (:16).

Two proofs that this is a solvable engineering problem and not a limit of the domain:

1. **The checks that work don't use goldens or API keys.** The `pii-anonymizer` and `mcp-query-guard` rubrics build their fixtures at runtime in temp directories, invoke the real hook **as a subprocess** with a synthesized payload, inject genuine faults (`chmod 000` to raise an unmocked `PermissionError`), and were gate-bites proven by named mutation ("three mutations of `scripts/pii/identity.py`, each 1.000 → 0.944 HARD FAIL and restored"). Cost: **$0, ~5 seconds.**
2. **The failure also runs in the other direction, in production.** `runtime.py` — wired into `orchestrate.py:2242` and the `eval-on-stop` hook registered at `settings.json:74` — routes *live engagement outputs* through the same per-agent check functions on every pipeline run and every consultant session. On Harborlight run 7 the `roi` rubric scored a demonstrably-correct config **0/0**, because its parser does not recognise the current `value_lever_groups` schema (:41). Uncalibrated rubrics produce false reds against real client work, not just false greens in CI.

**If we don't solve it:** every component change from here ships on a rubber stamp, `bb-build` keeps writing "verified" into tickets it did not verify, and the runtime gate keeps flagging good engagements while passing bad ones. The eval suite is not merely unhelpful — it is a false instrument that displaces the human review it claims to replace.

## 2. Solution

Make every gate in the harness capable of failing, and make every altitude's name describe what it actually does. Four coordinated moves: (a) build an **executable property-test tier** over every deterministic component — fixtures constructed at runtime, the real code invoked as a subprocess or import, faults injected, each check proven to fail under a named mutation (the #164–#166 pattern, generalised); (b) **keep the 11 synthetic prose goldens but re-file them honestly** as rubric-calibration cases — they are regression tests for the *rubric* and the calibration anchor for the runtime threshold, not agent gates — and give them the **missing negative half**, teaching `run_experiment.py`'s component branch to honour `negatives:`; (c) **rename `--altitude pipeline` to `deliverable-structural`** so no one can cite a 5-second fixture scan as integration evidence, and correct `bb-build/SKILL.md` so the build loop stops claiming a prompt change was verified; (d) **remove the metered API key from every path** — re-route `judge()` from the `anthropic` SDK to `claude -p` so judges are subscription-funded, and wire path-1 regeneration into `run_experiment.py` as a **local-only** tier that is hard-guarded against ever running in CI.

The CI gate stays $0 and key-free, which is what the harness's founding commit specified: *"Runs locally with no keys."*

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| Executable property-test rubrics for every deterministic component: the 7 hooks, `scripts/pii/*`, `artifact_boundary`, `orchestrate` step + workspace contracts, `init_engagement_identity`, `migrate_engagements`, `roi_calibrator`, `roi_excel_generator`, the `frontline_*` builders | Rewriting the components themselves; this adds tests, not behaviour |
| A mandatory **mutation proof** per check: apply a named mutation, assert the named check goes red, restore, assert green — automated in CI, not a human ritual | Full mutation-testing coverage metrics or a third-party mutation framework |
| `negatives:` support in `run_experiment.py`'s component branch + a malformed counterpart per check on all 16 component rows | Adding negatives to the `roi`/`assessment`/`report` deliverables (they have goldens; only `deck` has a negative) — tracked separately |
| Re-filing the 11 synthetic prose goldens under a `rubric_calibration:` section keyed by rubric, not by agent name | Deleting the goldens or the per-agent check functions in `specifics.py` — both are load-bearing for `runtime.py` |
| Renaming `--altitude pipeline` → `deliverable-structural` across registry, runner, CI, README, and `bb-build` | Making the altitude actually run `orchestrate.py`; a periodic real pipeline run is deferred (see Out of Scope) |
| Correcting `bb-build/SKILL.md`'s verify step so it never claims a frozen-fixture score verifies a prompt change | Redesigning the bb-* lifecycle or its other phases |
| Backlog :114 (`evals.yml` `paths:` omits `.claude/hooks/**`) and :116 (rubric interpreter ≠ registered interpreter) | Backlog :101 (person name in a markdown table cell not redacted) — a product bug, not an eval bug |
| Backlog :15 (CI runs no `--component` evals for changed components, no `report` deliverable) and :16 (`visual_render.py` wired to no row) | Rewriting the deck/design rubrics or the frozen `standards_snapshot/` |
| Backlog :134 — a `pipeline-workspace` property test for #167's "no composed prompt and no `cwd` names the client" guarantee | Re-litigating #167/#168's workspace or opaque-ID design |
| Backlog :41 — recalibrating the `roi` deliverable rubric's parser against the current `value_lever_groups` schema, with a negative | Changing the ROI schema itself, lever math, or scenario curves |
| Re-routing `judge()` from the `anthropic` SDK to `claude -p` (subscription-funded, no metered key) | Judge prompt content, judge model selection, or `standards_snapshot/` bumps |
| Wiring path-1 regeneration into `run_experiment.py` as a local-only tier, with a hard CI guard | Making path-1 a blocking gate, or designing the statistical base-vs-new comparison (deferred — see Out of Scope) |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Component gates that can fail | **16 / 16** — every row has ≥1 negative and a passing mutation proof |
| The v7 regression test: gut an agent prompt, run its gate | Gate no longer claims to verify the agent (row is renamed; `bb-build` no longer cites it for prompt changes) |
| Deterministic components with an executable property-test row | **100%** of the surfaces listed in Scope |
| Mutation proofs automated in CI | Every check in the executable tier; a check with no mutation proof fails the registry preflight |
| Blocking CI gate cost | **$0** — no `ANTHROPIC_API_KEY` on any blocking path; suite completes with the key unset |
| Hook-only PR triggers the eval gate | Yes (`:114` closed) — verified by a PR touching only `.claude/hooks/**` |
| Rubric and registered hook run under the same interpreter | Yes (`:116` closed) — asserted by a check, not convention |
| `--altitude pipeline` referenced anywhere as integration evidence | **0** occurrences in registry, runner, CI, README, `bb-build`, backlog |
| `roi` rubric score on a correct current-schema config | ≥ 0.80 (was 0/0 at runtime on Harborlight run 7) |
| path-1 invoked in CI | **0** — hard-guarded, asserted by a check |

## 5. Eval Acceptance Criteria (mandatory)

**This PRD changes the eval harness itself, so "the eval suite stays green" is circular and is explicitly NOT accepted as evidence.** Acceptance is mutation-based: a gate counts as done only when it has been shown to go red for a named, specific reason and green again on restore. This is the criterion the whole PRD exists to establish, so it applies to the PRD's own work first.

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `run-experiment-runner` (NEW) | `component_negatives_honoured`, `missing_target_fails_not_skips`, `declared_checks_all_executed`, `skipped_judge_does_not_pass`, `path1_refuses_in_ci` | 1.00, all `code` | unit |
| `mutation-harness` (NEW) | `every_registered_check_has_a_mutation`, `mutation_makes_named_check_red`, `restore_makes_it_green`, `check_without_mutation_fails_preflight` | 1.00, all `code` | unit |
| `pipeline-workspace` (NEW, closes :134) | `no_composed_prompt_names_client`, `no_cwd_segment_names_client`, `denylist_nonempty_asserted_first`, `traversal_covers_all_call_sites` | 1.00, all `code` | unit |
| `anonymize-guard`, `require-checkpoint`, `require-harness`, `enforce-journal`, `synthetic-knowledge-guard`, `eval-on-stop` (NEW rows) | per hook: `invoked_as_subprocess_not_import`, `fails_closed_under_injected_fault`, `runs_under_registered_interpreter` (closes :116), + hook-specific contract checks | 1.00, all `code` | unit |
| `artifact-boundary`, `roi-calibrator`, `frontline-builders`, `engagement-identity`, `engagement-migration` (NEW rows) | per component: fixture-at-runtime construction, real invocation, ≥1 negative, ≥1 mutation proof | 1.00, all `code` | unit |
| `mcp-query-guard` (existing) | all current checks stay green **+** `scan_limit_hit_fails_closed` (closes backlog :117) **+** `runs_under_registered_interpreter` | 1.00 | unit |
| `pii-anonymizer` (existing) | all 18 checks stay green **+** a negative per check; fixture extended with a markdown-table row and an attendee-bullet list (closes :107) | 1.00 | unit |
| 11 prose rubrics, re-filed as `rubric_calibration:` | each existing golden stays PASS **+** a NEW malformed negative per rubric that must FAIL | 0.80 golden / negative must fail | rubric-calibration |
| `roi` (deliverable, closes :41) | existing golden stays ≥ 0.80 **+** NEW `value_lever_groups_schema_parsed` **+** a negative fixture the parser must reject | 0.80 | deliverable |
| `deliverable-structural` (renamed from `pipeline`) | existing `rubrics.pipeline.contracts` checks stay green under the new name; no path still called `pipeline` | 0.90 | deliverable-structural |

- **NEW cases authored as part of this work:** every row marked NEW above, plus one negative for each of the 16 existing component rows, plus one mutation proof per check in the executable tier.
- **Downstream:** `specifics.py` and the per-agent check functions are consumed by `runtime.py` at `orchestrate.py:2242` and the `eval-on-stop` hook (`settings.json:74`). Any change to a check function MUST be re-scored against a real past engagement's outputs to confirm no new false red — the :41 failure mode. This is a required verification step, not optional.
- **Explicitly rejected as evidence:** a green `--altitude pipeline` / `deliverable-structural` run, and any component score obtained against a frozen fixture whose check has no mutation proof.

## 6. Out of Scope

- **A periodic real `orchestrate.py` run.** Costed this session at ~$15–25 per run, ~$150–600/month for weekly-to-nightly. Deferred by decision — the renamed structural gate plus the executable tier is this cycle's coverage.
- **Making path-1 a blocking gate, and the statistical design behind it.** Path-1 is wired as a local-only tier here. Turning it into a gate needs finer-grained rubrics (a 3-boolean rubric can only return 0, 0.33, 0.67, 1.0 — too coarse to sample) and a relative base-vs-new comparison across n runs. Both deferred.
- **Rewriting the 11 per-agent check functions to be more discriminating.** Cross-scoring shows `market-context-researcher` scores 0.833 against the *benchmark* golden and `benchmark-librarian` 0.889 against the *market-context* golden — they detect generic consulting prose. Recorded as a follow-up; re-filing plus negatives is this cycle's fix.
- **Deleting the 11 goldens or the `specifics.py` check functions.** Pressure-tested and rejected: they are the calibration anchor for the runtime threshold and the only regression test on rubric code, which changed in all six of the last eval PRs.
- Backlog :101 (markdown-table person names unredacted) — a Presidio/product bug, tracked separately.
- Any change to agent prompts, templates, decks, the design system, or engagement deliverables.

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| **This PRD is the largest cycle in the repo's history** (5 workstreams, ~25+ new eval rows) | Long-lived branch, merge pain, half-finished state | Sequence tickets so each workstream lands independently and green: (1) runner fixes + negatives, (2) rename + `bb-build` correction, (3) CI wiring `:114`/`:116`/`:15`/`:16`, (4) executable tier per component, (5) judge re-route + path-1. Workstreams 1–3 are small and unblock the rest |
| **Circularity** — we are using the eval harness to verify a change to the eval harness | A broken change could certify itself, exactly the failure being fixed | Mutation proof is the acceptance criterion, not the suite's own score; every new check must be demonstrated red-then-green by named mutation before its ticket closes |
| `claude -p` re-route for `judge()` depends on CLI auth, not an env var | Judges silently skip if the CLI isn't logged in — the current `skipped=True, passed=True` bug would hide it | Fold into the runner fix: a skipped judge must never count as a pass; make skip visible and non-passing |
| Max subscription rate limits under parallel path-1 runs | Local dev loop stalls or errors mid-run | Path-1 is local-only and serial by default; document the limit rather than engineering around it |
| Using a personal Max subscription for org CI is a licensing question | Could be non-compliant or fragile (one person's quota) | Hard-guard path-1 and `claude -p` judges out of CI entirely; CI stays $0 and key-free by design, so the question never arises |
| Renaming an altitude touches the runner, registry, CI, README, `bb-build`, and backlog text | A stale reference leaves the misleading name alive | Success metric is **0 occurrences** of the old name outside historical PRDs/commits; assert with a grep check in the preflight |
| `runtime.py` shares rubrics with the dev gate ("one rulebook, two contexts") | Tightening a rubric to bite in CI could start false-flagging live engagements | Every check-function change re-scored against a real past engagement before its ticket closes (see Eval Acceptance Criteria) |

## Testing Strategy

The harness cannot be verified by running itself. Three independent layers:

1. **Mutation proof (primary).** For each check: apply a specific, named source mutation; assert *that named check* — not merely the overall score — goes red; restore; assert green. A check with no mutation proof is treated as unimplemented and fails the registry preflight.
2. **Interpreter parity.** Each hook rubric asserts it invokes the hook under the interpreter `settings.json` actually registers, closing the class of defect where CI certifies a path consultants never execute (:116).
3. **Runtime non-regression.** Any change to a shared check function is re-scored against a real past engagement's committed outputs to confirm no new false red — the failure that scored a correct config 0/0 on Harborlight run 7 (:41).

Explicitly not accepted as evidence: a green suite, a green structural altitude, or a score against a fixture whose check has never been shown to fail.

## Rollback Plan

Additive and reversible in layers. The executable tier and negatives are new registry rows and new rubric modules — reverting the merge removes them with no effect on component behaviour, since no component source changes in this PRD. The altitude rename and the `bb-build/SKILL.md` correction are text changes revertible in isolation. The `judge()` re-route is the only behavioural change to existing code: it keeps the current SDK path available behind the existing `_available()` check, so reverting one function restores present behaviour. No data migration, no engagement-output impact, no change to any deliverable.
