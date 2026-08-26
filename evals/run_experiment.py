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

  # component / pipeline altitude (used by bb-build verify)
  python evals/run_experiment.py --component roi-financial-modeler
  python evals/run_experiment.py --altitude pipeline

  # override target / threshold
  python evals/run_experiment.py --deliverable assessment --target some.html --threshold 0.7
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
    # File-path evaluators get the resolved path; key-based evaluators (pipeline)
    # get the raw key to resolve themselves.
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Cortex eval runner")
    ap.add_argument("--deck", help="ad-hoc: run the deck rubric on this HTML file")
    ap.add_argument("--deliverable", help="registry deliverable name (deck|roi|assessment)")
    ap.add_argument("--component", help="registry component name")
    ap.add_argument("--altitude", choices=["unit", "pipeline", "deliverable"])
    ap.add_argument("--target", help="override the target file")
    ap.add_argument("--threshold", type=float, help="override the registry threshold")
    ap.add_argument("--negatives", action="store_true",
                    help="also run negatives; the gate passes only if they correctly FAIL")
    args = ap.parse_args()

    # --- ad-hoc deck mode (no registry needed) ---------------------------------
    if args.deck:
        res = _run_evaluator("rubrics.deliverable.decks", "deliverable", args.deck)
        thr = args.threshold if args.threshold is not None else 0.85
        print(res.report(thr))
        _maybe_log_langfuse("deck", res, thr)
        return 0 if res.passed(thr) else 1

    reg = _load_registry()

    # --- pipeline altitude -----------------------------------------------------
    if args.altitude == "pipeline":
        spec = reg["pipeline"]
        thr = args.threshold if args.threshold is not None else spec["threshold"]
        tgt = args.target or spec.get("golden_engagement", "")
        ok = _evaluate_targets("pipeline", spec["evaluator"], "pipeline", thr, [tgt],
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

    # --- component -------------------------------------------------------------
    if args.component:
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
