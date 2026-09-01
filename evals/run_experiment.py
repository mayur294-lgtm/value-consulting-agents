#!/usr/bin/env python3
"""Cortex eval runner — the verify gate for the bb-* harness.

Drives the rubrics in evals/registry.yaml over golden references (or an ad-hoc
target) and exits non-zero below threshold, so it can be a CI required check and
the bb-build verify step. Langfuse logging is OPTIONAL: with keys in the env it
logs scores to a Langfuse experiment; without them it runs locally and prints a
report. Code/deck evaluators need only the stdlib + PyYAML.

Usage:
  # ad-hoc deck check (immediate, no registry/Langfuse needed)
  python evals/run_experiment.py --deck path/to/deck.html

  # registry-driven deliverable check over its goldens (+ negatives with --negatives)
  python evals/run_experiment.py --deliverable deck
  python evals/run_experiment.py --deliverable deck --negatives

  # component altitude (used by bb-build verify)
  python evals/run_experiment.py --component roi-financial-modeler

  # rubric_calibration tier (#201) — scores a frozen synthetic prose golden with
  # a deterministic rubric. It calibrates the RUBRIC and regression-tests rubric
  # code; it says NOTHING about the agent in `covers_agent:`. Separate flag on
  # purpose, so `--component X = 1.000` keeps meaning one thing.
  python evals/run_experiment.py --calibration market-context-rubric

  # deliverable-structural altitude — lints inter-agent contracts across output
  # FILES that already exist. It does not run orchestrate.py and never reads the
  # component you changed; a green here is NOT integration evidence (#188).
  python evals/run_experiment.py --altitude deliverable-structural

  # override target / threshold
  python evals/run_experiment.py --deliverable assessment --target some.html --threshold 0.7

  # path-1 regeneration (#204) — LOCAL ONLY, never a gate, refuses under CI.
  # Actually runs the agent via `claude -p` (your Claude subscription) and
  # scores the fresh output against the row's real rubric. See evals/path1.py
  # and .design/ux-design-v7.md Flow 4.
  python evals/run_experiment.py --component roi-financial-modeler --regenerate
"""
from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # evals/
ROOT = HERE.parent                              # cortex repo root
sys.path.insert(0, str(HERE))                   # so `import rubrics.*` resolves


def _load_dotenv() -> None:
    """Load evals/.env into os.environ (no override, no dependency)."""
    env = HERE / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()

from rubrics.base import CheckResult, RubricResult  # noqa: E402
import mutations  # noqa: E402 - evals/mutations.py; the --mutate (#185) harness


def _load_registry() -> dict:
    import yaml  # PyYAML
    # CORTEX_EVAL_REGISTRY: test-only seam for the run-experiment-runner self-gate
    # row (evals/rubrics/component/run_experiment_runner.py, #183) so it can point
    # this runner at a synthetic registry.yaml it built in a tempdir instead of the
    # repo's real one. Unset (the default for every real caller) -> unchanged
    # behaviour: HERE / "registry.yaml". It only selects WHICH file is parsed —
    # it does not skip, weaken, or bypass any assertion below, so it cannot be
    # used to soften the real gate. Guarded on the top-level CI invocation by the
    # "Registry preflight" step, which refuses if this var is set there — see
    # evals/check_registry.py's CORTEX_EVAL_REGISTRY check in main().
    override = os.environ.get("CORTEX_EVAL_REGISTRY")
    path = Path(override) if override else (HERE / "registry.yaml")
    return yaml.safe_load(path.read_text())


def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else (ROOT / p)


def _run_evaluator(module_name: str, altitude: str, target: str) -> RubricResult:
    """Import an evaluator module and run evaluate(target). Missing/stub modules
    degrade gracefully to a single not-implemented check (score 0, soft)."""
    try:
        mod = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return RubricResult(target=target, altitude=altitude, checks=[
            CheckResult(name=f"{module_name}:not_implemented", score=0.0, passed=False,
                        detail="evaluator module not found (stub)")])
    if not hasattr(mod, "evaluate"):
        return RubricResult(target=target, altitude=altitude, checks=[
            CheckResult(name=f"{module_name}:no_evaluate", score=0.0, passed=False,
                        detail="module has no evaluate() (stub)")])
    # File-path evaluators get the resolved path; key-based evaluators
    # (deliverable-structural) get the raw key to resolve themselves.
    resolved = _resolve(target)
    arg = str(resolved) if resolved.exists() else target
    checks = mod.evaluate(arg)
    return RubricResult(target=target, altitude=altitude, checks=checks)


def _maybe_log_langfuse(name: str, result: RubricResult, threshold: float) -> None:
    """Log scores to Langfuse if keys + SDK are present; otherwise silently skip."""
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return
    try:
        from langfuse import Langfuse  # type: ignore
    except ImportError:
        return
    try:
        lf = Langfuse()  # reads LANGFUSE_* from env
        # Langfuse v3/v4 API: create an event (-> trace) then attach scores by trace_id.
        event = lf.create_event(
            name=f"eval:{name}",
            input={"target": result.target},
            metadata={"altitude": result.altitude, "threshold": threshold,
                      "verdict": "PASS" if result.passed(threshold) else "FAIL"},
        )
        tid = getattr(event, "trace_id", None)
        for c in result.checks:
            if c.skipped:
                continue
            lf.create_score(name=c.name, value=float(c.score), trace_id=tid,
                            data_type="NUMERIC",
                            comment=(c.detail + ("  [HARD FAIL]" if c.hard_fail and not c.passed else "")))
        lf.create_score(name="overall", value=float(result.score), trace_id=tid,
                        data_type="NUMERIC",
                        comment=f"{'PASS' if result.passed(threshold) else 'FAIL'} @ {threshold}")
        lf.flush()
        print(f"  (logged to Langfuse: eval:{name} trace={tid})")
    except Exception as e:  # never let telemetry break the gate
        print(f"  (Langfuse logging skipped: {e})")


def _assert_declared_checks_executed(name: str, spec: dict, res: RubricResult) -> bool:
    """Declared means required (#182, D5). The GATING set for a registry row is
    its `code:` list plus any `judge:` names that remain declared — NOT
    `path1_judge:`, which is intentionally non-gating (runs only under path-1
    regeneration, #204; see registry.yaml's `components:` header comment).

    "Executed" means a CheckResult with that exact name is present in the
    RubricResult, regardless of its pass/skip state: a judge that ran and hit
    a live error (e.g. a 401) still produced a CheckResult and counts as
    executed — a check whose adapter never called it produces no CheckResult
    at all and counts as missing. Judge check names carry the `judge:` prefix
    the judge harness stamps on them (rubrics/judge/judge.py).

    A check the rubric RETURNS that the registry does not declare is legal
    (additive checks) and is reported as `[undeclared]`, never failed.
    """
    code_names = set(spec.get("code") or [])
    gating_judge_names = set(spec.get("judge") or [])   # path1_judge: is excluded on purpose
    declared = code_names | {f"judge:{j}" for j in gating_judge_names}
    if not declared:
        return True
    executed = {c.name for c in res.checks}
    for extra in sorted(executed - declared):
        print(f"  [undeclared] {extra}")
    ok = True
    for missing in sorted(declared - executed):
        print(f"\n[FAIL] Row `{name}` declares `{missing}` but it did not execute. "
              f"Declared means required — a check that silently doesn't run is "
              f"indistinguishable from one that passes.")
        ok = False
    return ok


def _evaluate_targets(name: str, evaluator: str, altitude: str, threshold: float,
                      targets: list[str], expect_pass: bool, check_exists: bool = True,
                      spec: dict | None = None) -> bool:
    ok = True
    for tgt in targets:
        if check_exists and not _resolve(tgt).exists():
            print(f"\n[FAIL] Target `{tgt}` for row `{name}` does not exist. "
                  f"Failing rather than skipping — a skipped target previously left the verdict at PASS.")
            ok = False
            continue
        res = _run_evaluator(evaluator, altitude, tgt)
        print("\n" + res.report(threshold))
        _maybe_log_langfuse(name, res, threshold)
        if spec is not None and not _assert_declared_checks_executed(name, spec, res):
            ok = False
            continue
        passed = res.passed(threshold)
        # For negatives we WANT a fail; success of the gate = it correctly failed.
        ok = ok and (passed if expect_pass else (not passed))
    return ok


def _declared_check_names(spec: dict) -> set[str]:
    """The GATING set for a registry row: `code:` plus `judge:` names, prefixed
    exactly as `_assert_declared_checks_executed` expects them (`judge:<name>`).
    `path1_judge:` is excluded on purpose — it never gates (registry.yaml's
    `components:` header comment)."""
    code_names = set(spec.get("code") or [])
    judge_names = set(spec.get("judge") or [])
    return code_names | {f"judge:{j}" for j in judge_names}


def _reachability_canary(mutation: "mutations.Mutation", root: Path, evaluator: str,
                          target: str, before_score: float,
                          row_checks: frozenset[str] | None = None) -> tuple[str, str]:
    """#186: distinguish a genuinely inert check from a mutation that never
    reached the code under test (evals/mutations.py's module docstring,
    "What this harness CANNOT mutate" — this is the wiring that section says
    is #186's job).

    Delete the shadow copy of the mutation's `file` from a FRESH, otherwise
    unmutated shadow (the canary isolates the resolution PATH, not another
    mutation), rescore, and see whether the named check's state moved from
    the pristine baseline at all. There are THREE distinct outcomes — spec
    review on #186 found the original two-state (REACHABLE/UNREACHABLE)
    split conflated two very different kinds of "moved":

      reddened -> REACHABLE:            the check's OWN result changed
                 (score/passed/skipped/unscorable) once its subject file
                 vanished, so the check DOES read the shadow copy. This is
                 DIRECT, targeted proof — whatever became of the original
                 mutation (stale `find`, or applied-but-inert), the check
                 itself is wired to the right file.
      vanished -> REACHABLE_INDIRECT:   the check didn't change state — it
                 disappeared from the evaluator's output entirely. That only
                 proves the EVALUATOR noticed the file's absence, not that
                 THIS check specifically reads it: deleting one file can
                 collapse the whole evaluator (e.g. an early parse failure)
                 and take unrelated checks down with it. This is INDIRECT,
                 weaker proof, so it is reported with the collateral ratio —
                 how many of the row's other declared checks also vanished
                 in the same rescore. A large simultaneous-vanish fraction
                 is the collapse signature, not a wiring proof for any one
                 check.
      unmoved  -> UNREACHABLE:          the check's result is byte-identical
                 whether the shadow's copy of the file exists or not — it
                 never reads the shadow copy at all (a hardcoded absolute
                 path, `Path.cwd()` captured at import, ...). This is a
                 HARNESS LIMITATION, not evidence the check itself is
                 broken: the fix is "make the rubric resolve through
                 repo_root()", never "weaken or delete the mutation".

    `row_checks`, when given, is the full set of check names declared by the
    row under test — used only to compute the vanished-state collateral
    ratio (N of M also vanished). Without it, the vanished case still
    reports REACHABLE_INDIRECT but cannot compute a ratio.

    Returns (verdict, detail). verdict is "REACHABLE", "REACHABLE_INDIRECT",
    "UNREACHABLE", or "INCONCLUSIVE" (the canary itself could not run at
    all, e.g. the file isn't present in a fresh shadow — reported as-is,
    never folded into any of the other three).
    """
    rel = Path(mutation.file)
    try:
        with mutations.shadow_root(root) as shadow:
            shadow_file = shadow / rel
            if not shadow_file.is_file():
                return ("INCONCLUSIVE",
                        f"`{rel}` is not present in a fresh shadow — cannot run the canary")
            shadow_file.unlink()
            after_map = mutations.score(
                shadow, evaluator,
                mutations.shadow_target(root, shadow,
                                         target or (str(rel) if mutation.kind == "fixture" else "")),
                timeout=mutations.DEFAULT_SCORE_TIMEOUT_S, python=sys.executable,
                extra_pythonpath=(),
            )
    except mutations.MutationHarnessError as exc:
        # Deleting the file broke the rubric's own execution outright — that
        # is unambiguous evidence the check DOES resolve into the shadow (it
        # could not even run without the file there), so this is a REACHABLE
        # signal, not an inconclusive one.
        return ("REACHABLE",
                f"deleting `{rel}` broke the rubric's own execution ({exc}) — it reads this file")

    after_check = after_map.get(mutation.check)
    if after_check is None:
        if row_checks:
            vanished = sorted(c for c in row_checks if c not in after_map)
            ratio = f"{len(vanished)} of {len(row_checks)} checks in this row also vanished"
        else:
            vanished = [mutation.check]
            ratio = "row's declared check set was not supplied — cannot compute a collateral ratio"
        return ("REACHABLE_INDIRECT",
                f"{ratio} (executed after deletion: {sorted(after_map)}) — check "
                f"`{mutation.check}` stopped executing entirely once `{rel}` was deleted, which "
                f"proves the EVALUATOR is wired to this file, not that this specific check reads "
                f"it — see the collateral count above; a high simultaneous-vanish fraction means "
                f"the evaluator collapsed rather than this check being confirmed")

    same_state = (
        bool(after_check["passed"]) and not bool(after_check["skipped"])
        and not bool(after_check["unscorable"])
        and abs(float(after_check["score"]) - before_score) < 1e-9
    )
    if not same_state:
        return ("REACHABLE",
                f"deleting `{rel}` changed check `{mutation.check}`'s state "
                f"(score {before_score:.2f} -> {float(after_check['score']):.2f}, "
                f"detail: {after_check.get('detail', '')[:160]!r}) — the check does read the "
                f"shadow copy")
    return ("UNREACHABLE",
            f"deleting `{rel}` had NO effect on check `{mutation.check}` (still score "
            f"{before_score:.2f}, unchanged) — the check never reads the shadow copy of this "
            f"file at all; it resolves its subject through a path outside repo_root(). This is "
            f"a HARNESS LIMITATION (see evals/mutations.py, 'What this harness CANNOT mutate'), "
            f"not evidence the check is broken — fix the rubric to resolve via repo_root(), "
            f"never the mutation.")


def _run_mutate(reg: dict, row: str, target_override: str | None) -> int:
    """`--mutate <row>` (#185, ux-design-v7 Flow 2): prove every check the row
    DECLARES actually goes red under a mutation. A check with no mutation
    entry certifies nothing, so it fails here exactly like an unproven one —
    the same edge case the registry preflight (#186) will later refuse before
    any row even runs."""
    if row in _calibration_rows(reg):
        # rubric_calibration rows are mutation-proven exactly like a component
        # row — per-check dict-form `negatives:` (design D3). Looked up first
        # (and by section, never by alias) so `--mutate <rubric>` keeps working
        # now that the shim is gone; CI derives its mutate-row list from the same
        # three sections (.github/workflows/evals.yml).
        spec = _calibration_rows(reg)[row]
        evaluator = spec.get("evaluator", f"rubrics.component.{row.replace('-', '_')}")
        default_target = spec.get("input", "")
    elif row in reg.get("components", {}):
        spec = reg["components"][row]
        evaluator = spec.get("evaluator", f"rubrics.component.{row.replace('-', '_')}")
        default_target = spec.get("input", spec.get("golden_engagement", ""))
    elif row in reg.get("deliverables", {}):
        spec = reg["deliverables"][row]
        evaluator = spec["evaluator"]
        goldens = spec.get("goldens") or []
        default_target = goldens[0] if goldens else ""
    else:
        print(f"\n[FAIL] `{row}` is not a component, deliverable or "
              f"{_CALIBRATION_KEY} row in registry.yaml.")
        return 2

    target = target_override if target_override is not None else default_target
    declared = _declared_check_names(spec)

    try:
        muts = mutations.mutations_from_spec(spec)
    except mutations.MutationHarnessError as exc:
        print(f"\n[FAIL] Row `{row}`'s mutation declarations are malformed: {exc}")
        return 1

    if not muts:
        print(
            f"\n[FAIL] Row `{row}` has no mutation proof — no `mutations:` entry (a `negatives:` "
            f"LIST, if present, is the legacy separate-negative-file form and does not count as "
            f"one). A gate that cannot fail certifies nothing — add a `mutations:` entry (or "
            f"dict-form `negatives: {{check: {{strip: ...}}}}`) showing what makes each declared "
            f"check go red."
        )
        return 1

    mutation_by_check = {m.check: m for m in muts}
    missing = sorted(declared - mutation_by_check.keys())
    for name in missing:
        print(
            f"\n[FAIL] Check `{name}` on row `{row}` has no mutation proof. A gate that cannot "
            f"fail certifies nothing — add a `mutations:` entry showing what makes it go red."
        )

    print(f"\n=== --mutate {row} ({len(muts)} mutation{'' if len(muts) == 1 else 's'} declared) ===")
    try:
        results = mutations.prove_all(muts, evaluator=evaluator, target=target)
    except mutations.WorkingTreeMutated as exc:
        print(f"\n[FAIL] {exc}")
        return 1
    except mutations.MutationHarnessError as exc:
        print(f"\n[FAIL] mutation harness could not run for row `{row}`: {exc}")
        return 1

    proven = 0
    unreachable = 0
    for r in results:
        print(r.message())
        if r.proven:
            proven += 1
            continue
        # #186 reachability canary — only meaningful once there IS a baseline
        # to compare against (`before` passed) and a real file to delete;
        # detail text naming those states is produced before the mutation's
        # own file/shadow resolution ever runs, so skip the canary there too.
        if r.mutation is None or "BEFORE the mutation" in r.detail:
            continue
        real_file = _resolve(r.mutation.file)
        if not real_file.is_file():
            continue
        verdict, detail = _reachability_canary(r.mutation, ROOT, evaluator, target, r.before,
                                                declared)
        if verdict == "UNREACHABLE":
            unreachable += 1
            print(f"  ⚠ [HARNESS ERROR] reachability canary for `{r.check}`: UNREACHABLE — {detail}")
        elif verdict == "REACHABLE":
            print(f"  · reachability canary for `{r.check}`: REACHABLE (direct — check "
                  f"reddened; not a harness gap, the check/mutation itself needs fixing) — "
                  f"{detail}")
        elif verdict == "REACHABLE_INDIRECT":
            print(f"  · reachability canary for `{r.check}`: REACHABLE (indirect — check "
                  f"vanished; {detail})")
        else:
            print(f"  · reachability canary for `{r.check}`: {verdict} — {detail}")

    total = len(results)
    ok = (proven == total) and not missing
    tail = f", {len(missing)} declared check(s) with no mutation entry" if missing else ""
    if unreachable:
        tail += (f", {unreachable} UNREACHABLE (harness limitation per the canary above — "
                 f"fix the rubric's path resolution, not the mutation)")
    print(f"\nmutations: {proven}/{total} proven{tail}")
    return 0 if ok else 1


# --- BEGIN old-altitude error text (#188 / design D4) -------------------------
# The ONLY place in the runner, registry, runtime or CI where the retired
# altitude name may appear. `check_registry.py`'s grep assertion skips exactly
# this sentinel-delimited region; every other occurrence anywhere in scope is a
# hard error. Keep the literal inside these sentinels — never re-introduce it
# as a `choices=` entry, an alias, or a deprecation shim (D4: an alias preserves
# the misreading perfectly, and warnings get scrolled past).
_RETIRED_ALTITUDE = "pipeline"
_RETIRED_ALTITUDE_ERROR = (
    "`--altitude pipeline` was renamed to `--altitude deliverable-structural`. "
    "It scores frozen fixture files in ~5s and has never run the pipeline; the "
    "old name is what made a 1.000 look like integration evidence. If you want a "
    "real end-to-end run, that is out of scope for the gate — run "
    "`scripts/orchestrate.py` on a synthetic engagement."
)
# --- END old-altitude error text ---------------------------------------------

_DELIVERABLE_STRUCTURAL = "deliverable-structural"   # CLI flag + rendered altitude label
_DELIVERABLE_STRUCTURAL_KEY = "deliverable_structural"  # registry.yaml section key
_ALTITUDES = frozenset({"unit", _DELIVERABLE_STRUCTURAL, "deliverable"})

# --- rubric_calibration dispatch (#201, wired in the epic's closing pass) ------
# #201 re-filed the eleven prose-golden rows out of `components:` into their own
# `rubric_calibration:` section keyed by RUBRIC, because an agent-keyed row reads
# as "this gates that agent" and never did. It could not touch this file at the
# time (concurrent ticket #204 owned it), so it reached dispatch by YAML-aliasing
# the rows back into `components:`. This branch is the real dispatch that note
# asked for; the alias block is gone.
#
# `--calibration` is a SEPARATE flag on purpose, not a `--component` synonym: the
# whole point of the tier is that these rows are not component gates, and a flag
# that says so at the call site is what keeps `--component X = 1.000` meaning one
# thing. The evaluator still runs at the runner's `unit` dispatch altitude (the
# banner every calibration evaluator prints says exactly that, and why).
_CALIBRATION_KEY = "rubric_calibration"


def _calibration_rows(reg: dict) -> dict:
    return reg.get(_CALIBRATION_KEY) or {}


def _calibration_misroute(name: str, rows: dict) -> str:
    """`--component <rubric-row>` no longer resolves (the alias shim is gone).
    Point at the right flag rather than dying on a bare KeyError — the same
    courtesy the retired AGENT names get from
    rubrics/component/moved_to_rubric_calibration.py."""
    return (
        f"\n[FAIL] `{name}` is a `{_CALIBRATION_KEY}:` row, not a component gate — "
        f"nothing was scored.\n"
        f"  Run instead:  --calibration {name}\n\n"
        f"  These rows score a frozen synthetic prose golden with a deterministic "
        f"rubric.\n  They calibrate the RUBRIC; they are not evidence about any agent "
        f"(see\n  evals/rubrics/component/_calibration.py). Keeping them out of "
        f"`--component`\n  is what keeps a component 1.000 meaning one thing.\n\n"
        f"  Calibration rows: {', '.join(sorted(rows))}"
    )


def _unknown_calibration_row(name: str, rows: dict, reg: dict) -> str:
    if name in (reg.get("components") or {}):
        return (f"\n[FAIL] `{name}` is a `components:` row, not a {_CALIBRATION_KEY} row — "
                f"run `--component {name}`.")
    return (f"\n[FAIL] `{name}` is not a row in `{_CALIBRATION_KEY}:`.\n"
            f"  Known rows: {', '.join(sorted(rows)) or '(none)'}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Cortex eval runner")
    ap.add_argument("--deck", help="ad-hoc: run the deck rubric on this HTML file")
    ap.add_argument("--deliverable", help="registry deliverable name (deck|roi|assessment)")
    ap.add_argument("--component", help="registry component name")
    ap.add_argument("--calibration", metavar="ROW",
                    help="registry `rubric_calibration:` row name (#201) — scores a frozen "
                         "synthetic prose golden with a deterministic rubric. It calibrates "
                         "the RUBRIC and is a regression test on rubric code; it is NOT "
                         "evidence about the agent named in `covers_agent:`. Every run prints "
                         "the tier banner saying so.")
    # Not `choices=`: the retired altitude name must reach our own guard below so
    # it gets the rename rationale, not argparse's generic "invalid choice".
    ap.add_argument("--altitude", metavar="{unit,deliverable-structural,deliverable}",
                    help="unit | deliverable-structural | deliverable")
    ap.add_argument("--target", help="override the target file")
    ap.add_argument("--threshold", type=float, help="override the registry threshold")
    ap.add_argument("--negatives", action="store_true",
                    help="also run negatives; the gate passes only if they correctly FAIL")
    ap.add_argument("--mutate", metavar="ROW",
                    help="prove every check declared by this component/deliverable row goes "
                         "red under its `mutations:` entry; exits non-zero if any check is "
                         "unproven or has no mutation entry")
    ap.add_argument("--regenerate", action="store_true",
                    help="LOCAL ONLY (#204): dispatch --component <name> to evals/path1.py and "
                         "actually run that agent via `claude -p`, scoring the fresh output "
                         "against the row's real rubric, instead of scoring an existing target. "
                         "Single run, nondeterministic — NOT a gate. Hard-refuses under CI "
                         "($CI or $GITHUB_ACTIONS set) before touching anything else.")
    args = ap.parse_args()

    # --- path-1 regeneration dispatch (#204) ------------------------------------
    # Checked before the registry even loads, and before altitude validation:
    # this is the SECOND of the two routes into path-1 that must hard-refuse
    # under CI (the first is evals/path1.py's own main() — see that module).
    # Delegates the actual CI check to path1.refuse_if_ci() rather than
    # reimplementing the env-var test and message here, so the two routes
    # cannot drift out of sync with each other or with
    # .design/ux-design-v7.md's Error States table.
    if args.regenerate:
        import path1  # local import: plain gate runs never pay path1's rubric-module import cost
        if path1.refuse_if_ci():
            return 1
        if not args.component:
            ap.error("--regenerate requires --component <name> — path-1 regenerates a single "
                     "agent's output; it has no deliverable-level entry point.")
        reg = _load_registry()
        if args.component in _calibration_rows(reg):
            print(f"\n[FAIL] `{args.component}` is a {_CALIBRATION_KEY} row — it names a "
                  f"RUBRIC, not an agent, and path-1 regenerates an agent. Pass the agent "
                  f"name in that row's `covers_agent:` instead.", file=sys.stderr)
            return 1
        spec = reg["components"][args.component]
        thr = args.threshold if args.threshold is not None else spec["threshold"]
        tgt = args.target or spec.get("input", spec.get("golden_engagement", ""))
        resolved = _resolve(tgt)
        input_text = resolved.read_text() if resolved.exists() else tgt
        try:
            out = path1.run_agent(args.component, input_text)
            res, judge_names = path1.score(args.component, out, context=input_text, registry=reg)
        except RuntimeError as exc:
            print(f"\n[FAIL] path-1 could not run `{args.component}`: {exc}", file=sys.stderr)
            return 1
        print(path1.PATH1_BANNER)
        print(f"checks assembled for `{args.component}`: {[c.name for c in res.checks]}  "
              f"(path1_judge={judge_names})")
        print(res.report(thr))
        # Exit code is a LOCAL dev convenience (did this single run clear the
        # threshold), never a gate verdict — CI can't reach this branch at all
        # (the refusal above), and nothing here is wired into evals.yml.
        return 0 if res.passed(thr) else 1

    # --- altitude validation ---------------------------------------------------
    if args.altitude == _RETIRED_ALTITUDE:
        print(_RETIRED_ALTITUDE_ERROR, file=sys.stderr)
        return 2
    if args.altitude is not None and args.altitude not in _ALTITUDES:
        ap.error(f"argument --altitude: invalid choice: {args.altitude!r} "
                 f"(choose from {', '.join(sorted(_ALTITUDES))})")

    # --- ad-hoc deck mode (no registry needed) ---------------------------------
    if args.deck:
        res = _run_evaluator("rubrics.deliverable.decks", "deliverable", args.deck)
        thr = args.threshold if args.threshold is not None else 0.85
        print(res.report(thr))
        _maybe_log_langfuse("deck", res, thr)
        return 0 if res.passed(thr) else 1

    reg = _load_registry()

    # --- mutation proof (#185) --------------------------------------------------
    if args.mutate:
        return _run_mutate(reg, args.mutate, args.target)

    # --- deliverable-structural altitude ---------------------------------------
    if args.altitude == _DELIVERABLE_STRUCTURAL:
        spec = reg[_DELIVERABLE_STRUCTURAL_KEY]
        thr = args.threshold if args.threshold is not None else spec["threshold"]
        tgt = args.target or spec.get("golden_engagement", "")
        ok = _evaluate_targets(_DELIVERABLE_STRUCTURAL, spec["evaluator"],
                               _DELIVERABLE_STRUCTURAL, thr, [tgt],
                               expect_pass=True, check_exists=False)
        return 0 if ok else 1

    # --- deliverable -----------------------------------------------------------
    if args.deliverable:
        spec = reg["deliverables"][args.deliverable]
        thr = args.threshold if args.threshold is not None else spec["threshold"]
        targets = [args.target] if args.target else list(spec.get("goldens", []))
        ok = _evaluate_targets(args.deliverable, spec["evaluator"], "deliverable", thr, targets,
                               expect_pass=True, spec=spec)
        if args.negatives and not args.target:
            print("\n=== negatives (must FAIL to pass the gate) ===")
            ok = _evaluate_targets(args.deliverable, spec["evaluator"], "deliverable", thr,
                                   list(spec.get("negatives", [])), expect_pass=False, spec=spec) and ok
        return 0 if ok else 1

    # --- rubric_calibration ----------------------------------------------------
    # Its own branch, not a `--component` synonym — see the _CALIBRATION_KEY note
    # above. `--negatives` is refused here on purpose: this tier's `negatives:` is
    # a MAPPING of per-check fixture mutations (design D3), not the legacy list of
    # whole-artifact negative FILES that `--negatives` iterates. Feeding the dict
    # to that loop would iterate its KEYS as if they were paths and report a row
    # of "correctly failed" on files that never existed — a vacuous green, which
    # is the whole failure mode this epic exists to close. `--mutate <row>` is
    # what proves this tier's negatives, and CI runs it on every row.
    if args.calibration:
        rows = _calibration_rows(reg)
        if args.calibration not in rows:
            print(_unknown_calibration_row(args.calibration, rows, reg), file=sys.stderr)
            return 2
        if args.negatives:
            print("\n[FAIL] `--negatives` does not apply to a rubric_calibration row: its "
                  "`negatives:` is a per-check fixture-mutation MAPPING, not a list of "
                  "negative files. Prove it with `--mutate " + args.calibration + "`.",
                  file=sys.stderr)
            return 2
        spec = rows[args.calibration]
        thr = args.threshold if args.threshold is not None else spec["threshold"]
        evaluator = spec["evaluator"]   # preflight requires it explicitly on this tier
        tgt = args.target or spec.get("input", "")
        cal_ok = _evaluate_targets(args.calibration, evaluator, "unit", thr, [tgt],
                                   expect_pass=True, spec=spec)
        return 0 if cal_ok else 1

    # --- component -------------------------------------------------------------
    if args.component:
        if args.component in _calibration_rows(reg):
            print(_calibration_misroute(args.component, _calibration_rows(reg)),
                  file=sys.stderr)
            return 2
        spec = reg["components"][args.component]
        thr = args.threshold if args.threshold is not None else spec["threshold"]
        evaluator = spec.get("evaluator", f"rubrics.component.{args.component.replace('-', '_')}")
        tgt = args.target or spec.get("input", spec.get("golden_engagement", ""))
        ok = _evaluate_targets(args.component, evaluator, "unit", thr, [tgt], expect_pass=True, spec=spec)
        if args.negatives and not args.target:
            print("\n=== negatives (must FAIL to pass the gate) ===")
            ok = _evaluate_targets(args.component, evaluator, "unit", thr,
                                   list(spec.get("negatives", [])), expect_pass=False, spec=spec) and ok
        return 0 if ok else 1

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
