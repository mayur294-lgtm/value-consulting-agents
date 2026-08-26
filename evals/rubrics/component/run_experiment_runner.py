"""run-experiment-runner component evaluator — the SELF-GATE for
`evals/run_experiment.py` (#183, closing PR 1 of the eval-gate-v7 epic).

Every prior component row in this registry proves that some piece of Cortex
(a hook, an agent's output shape, a generator) behaves correctly. This row
proves the RUNNER that grades all of those rows behaves correctly — that
`run_experiment.py`'s own gating contracts (negatives, missing targets,
declared-checks, judge skips) actually hold, not just that they read as if
they hold.

Every check here invokes the REAL `evals/run_experiment.py` as a subprocess
against a SYNTHETIC `registry.yaml` (+ synthetic evaluator modules) built
fresh inside a `tempfile.TemporaryDirectory()` — never the repo's real
`evals/registry.yaml`, and never an import-and-call of `run_experiment.main()`
in-process. The exit code is the contract being proven: CI treats this
runner as a pass/fail gate purely via its process exit code, so that is what
every assertion here is anchored to (with report-text assertions where the
exit code alone can't discriminate correct from silently-wrong behaviour —
see `_skipped_judge_does_not_pass`).

The synthetic registry is wired via the `CORTEX_EVAL_REGISTRY` env var
`_load_registry()` in run_experiment.py reads (added by this ticket) —
see that function's docstring for the "cannot weaken the real gate" contract.
Synthetic evaluator modules are plain top-level .py files dropped in the
tempdir and made importable via a prepended `PYTHONPATH` entry; they `import
rubrics.base.CheckResult` from the REAL evals/ tree (already on the
subprocess's sys.path via run_experiment.py's own `sys.path.insert`), so
every CheckResult they hand back is the real dataclass with real semantics —
only the fixture content is synthetic, never the types.

Follows the mcp-query-guard / pii-anonymizer precedent: fixtures resemble
what could plausibly appear in the real registry (a component row with
`code:`/`judge:`/`negatives:`), not a two-line stub — see D-notes inline on
each `_seed_*` helper for what regression each shape guards against.

threshold: 1.00 in the registry — this row certifies the harness that gates
every other row; "mostly correct" is not an acceptable bar for the thing that
decides pass/fail for everything else. No `judge:` entries — every check here
is deterministic, $0, no LLM, and must stay green with ANTHROPIC_API_KEY unset
(the synthetic "skipped judge" case simulates what a real judge integration
does on a missing key — it never calls one).

NOT covered here (see registry.yaml comment on this row): `path1_refuses_in_ci`
is authored by #204, once Path-1's CI guard exists to test. Authoring it now
would only ever produce `[SKIP*]` — noise, not signal — under #181's
skip-that-cannot-pass rendering, which is exactly the "absence reads as
success" pattern this epic is removing.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import yaml

from rubrics.base import CheckResult, repo_root

RUNNER_REL_PATH = Path("evals") / "run_experiment.py"
BASE_MODULE_REL_PATH = Path("evals") / "rubrics" / "base.py"

SUBPROCESS_TIMEOUT_S = 30.0


def _runner_path() -> Path:
    return repo_root() / RUNNER_REL_PATH


def _bool_check(name: str, ok: bool, *, detail: str = "", exercised: str | None = None,
                 hard_fail: bool = True) -> CheckResult:
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=hard_fail, detail=detail,
                        exercised=exercised)


def _run_runner(registry_path: Path, pythonpath_dir: Path, args: list[str]) -> subprocess.CompletedProcess:
    """Invoke the REAL evals/run_experiment.py as a subprocess, pointed at a
    synthetic registry via CORTEX_EVAL_REGISTRY and able to import synthetic
    evaluator modules via a prepended PYTHONPATH entry. ANTHROPIC_API_KEY and
    the Langfuse keys are explicitly stripped so this is deterministic and
    network-free regardless of what a consultant's shell or evals/.env carry —
    every synthetic evaluator below is self-contained and never calls a real
    judge, so this is belt-and-braces, not load-bearing."""
    env = dict(os.environ)
    for k in ("ANTHROPIC_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"):
        env.pop(k, None)
    env["CORTEX_EVAL_REGISTRY"] = str(registry_path)
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(pythonpath_dir) + (os.pathsep + existing_pp if existing_pp else "")
    cmd = [sys.executable, str(_runner_path()), *args]
    return subprocess.run(
        cmd, capture_output=True, timeout=SUBPROCESS_TIMEOUT_S, env=env,
        cwd=str(repo_root()),
    )


def _write_registry(root: Path, components: dict) -> Path:
    path = root / "registry.yaml"
    path.write_text(yaml.safe_dump({"components": components}, sort_keys=False), encoding="utf-8")
    return path


def _out(result: subprocess.CompletedProcess) -> str:
    return (result.stdout.decode("utf-8", errors="replace")
            + result.stderr.decode("utf-8", errors="replace"))


def _run_in_tmp(fn) -> CheckResult:
    """Run a check body inside a fresh tempdir, converting any unexpected
    exception (subprocess timeout, missing interpreter, ...) into a failing
    CheckResult instead of crashing the whole eval run."""
    try:
        with tempfile.TemporaryDirectory(prefix="run_experiment_runner_eval_") as td:
            return fn(Path(td))
    except Exception as exc:  # noqa: BLE001 - convert to a reportable failure
        return _bool_check(fn.__name__.lstrip("_"), False,
                            detail=f"check raised {type(exc).__name__}: {exc}")


# --- case 1: component_negatives_honoured -----------------------------------

def _component_negatives_honoured(root: Path) -> CheckResult:
    """Regression guard for the `--negatives` contract in `_evaluate_targets`:
    a negative fixture that correctly FAILS its check must make `--negatives`
    exit 0 (the gate did its job); a "negative" that WRONGLY passes its check
    must make `--negatives` exit 1 (a negative that can't fail proves nothing,
    same principle as this whole epic). Both directions are exercised so this
    can't pass by the runner simply ignoring `--negatives` altogether — that
    bug would make BOTH scenarios exit 0, and only the second assertion below
    would catch it.

    One synthetic evaluator module decides pass/fail by reading a marker
    string out of the target file's content (not its filename), so the two
    scenarios below are driven purely by fixture content, exactly as the
    ticket requires."""
    name = "component_negatives_honoured"
    mod_src = textwrap.dedent("""
        from rubrics.base import CheckResult
        def evaluate(target):
            text = open(target, encoding="utf-8").read()
            if "GOOD_NEGATIVE" in text:
                # a well-behaved negative: it correctly FAILS its own check
                return [CheckResult("always_check", 0.0, False)]
            # GOLDEN or BAD_NEGATIVE: the check PASSES
            return [CheckResult("always_check", 1.0, True)]
    """).strip() + "\n"
    (root / "synth_negatives_mod.py").write_text(mod_src, encoding="utf-8")

    golden = root / "golden.txt"
    golden.write_text("GOLDEN fixture\n", encoding="utf-8")
    good_negative = root / "good_negative.txt"
    good_negative.write_text("GOOD_NEGATIVE fixture\n", encoding="utf-8")
    bad_negative = root / "bad_negative.txt"
    bad_negative.write_text("BAD_NEGATIVE fixture (wrongly passes)\n", encoding="utf-8")

    # Scenario A: negative correctly fails -> --negatives must exit 0.
    reg_a = _write_registry(root, {
        "well-behaved-negative": {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_negatives_mod",
            "input": str(golden), "negatives": [str(good_negative)],
            "code": ["always_check"],
        },
    })
    result_a = _run_runner(reg_a, root, ["--component", "well-behaved-negative", "--negatives"])

    # Scenario B: the "negative" wrongly passes -> --negatives must exit 1.
    reg_b = _write_registry(root, {
        "broken-negative": {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_negatives_mod",
            "input": str(golden), "negatives": [str(bad_negative)],
            "code": ["always_check"],
        },
    })
    result_b = _run_runner(reg_b, root, ["--component", "broken-negative", "--negatives"])

    ok = result_a.returncode == 0 and result_b.returncode == 1
    return _bool_check(name, ok, exercised=f"evals/run_experiment.py via {sys.executable}", detail=(
        f"scenario_a(well-behaved negative) rc={result_a.returncode} (want 0); "
        f"scenario_b(broken negative) rc={result_b.returncode} (want 1); "
        f"a_out={_out(result_a)[-300:]!r} b_out={_out(result_b)[-300:]!r}"
    ))


# --- case 2: missing_target_fails_not_skips ----------------------------------

def _missing_target_fails_not_skips(root: Path) -> CheckResult:
    """Regression guard for #181: a component `input:` that does not resolve
    on disk must make the run FAIL (exit 1) with the "Failing rather than
    skipping" message, not silently SKIP-as-PASS (exit 0). The evaluator
    module is written but deliberately never valid to call (it isn't — the
    missing-target check in `_evaluate_targets` must short-circuit before
    ever importing it), which doubles as proof the runner doesn't fall
    through to scoring a target it just declared missing."""
    name = "missing_target_fails_not_skips"
    mod_src = textwrap.dedent("""
        from rubrics.base import CheckResult
        def evaluate(target):
            raise AssertionError(
                "evaluate() must never be called for a target that does not "
                "exist on disk -- the missing-target check must short-circuit first"
            )
    """).strip() + "\n"
    (root / "synth_missing_target_mod.py").write_text(mod_src, encoding="utf-8")

    missing_input = root / "does_not_exist.md"   # never created
    reg = _write_registry(root, {
        "missing-input-row": {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_missing_target_mod",
            "input": str(missing_input),
            "code": ["never_reached"],
        },
    })
    result = _run_runner(reg, root, ["--component", "missing-input-row"])
    out = _out(result)
    ok = (
        result.returncode == 1
        and "does not exist" in out
        and "failing rather than skipping" in out.lower()
        and "AssertionError" not in out   # would prove evaluate() got called anyway
    )
    return _bool_check(name, ok, exercised=f"evals/run_experiment.py via {sys.executable}", detail=(
        f"rc={result.returncode} (want 1); out_tail={out[-400:]!r}"
    ))


# --- case 3: declared_checks_all_executed ------------------------------------

def _declared_checks_all_executed(root: Path) -> CheckResult:
    """Regression guard for #182's `_assert_declared_checks_executed`: a row
    that declares `code: [check_a, check_b]` but whose evaluator only ever
    returns `check_a` must FAIL the run naming `check_b` as undeclared-but-
    missing, exactly like a check that silently never ran. A second, fully
    well-formed row (evaluator returns everything it declares) must still
    PASS cleanly — proving the assertion isn't just failing every row."""
    name = "declared_checks_all_executed"
    input_file = root / "input.txt"
    input_file.write_text("synthetic input\n", encoding="utf-8")

    under_mod_src = textwrap.dedent("""
        from rubrics.base import CheckResult
        def evaluate(target):
            # Declares check_a AND check_b in the registry but only returns
            # check_a -- simulates a rubric silently dropping a declared check.
            return [CheckResult("check_a", 1.0, True)]
    """).strip() + "\n"
    (root / "synth_under_declared_mod.py").write_text(under_mod_src, encoding="utf-8")

    complete_mod_src = textwrap.dedent("""
        from rubrics.base import CheckResult
        def evaluate(target):
            return [CheckResult("check_a", 1.0, True), CheckResult("check_b", 1.0, True)]
    """).strip() + "\n"
    (root / "synth_complete_mod.py").write_text(complete_mod_src, encoding="utf-8")

    reg = _write_registry(root, {
        "under-declared-row": {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_under_declared_mod",
            "input": str(input_file), "code": ["check_a", "check_b"],
        },
        "complete-row": {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_complete_mod",
            "input": str(input_file), "code": ["check_a", "check_b"],
        },
    })
    result_under = _run_runner(reg, root, ["--component", "under-declared-row"])
    result_complete = _run_runner(reg, root, ["--component", "complete-row"])

    out_under = _out(result_under)
    ok = (
        result_under.returncode == 1
        and "declares `check_b` but it did not execute" in out_under
        and result_complete.returncode == 0
    )
    return _bool_check(name, ok, exercised=f"evals/run_experiment.py via {sys.executable}", detail=(
        f"under_declared rc={result_under.returncode} (want 1); "
        f"complete rc={result_complete.returncode} (want 0); "
        f"under_out_tail={out_under[-400:]!r}"
    ))


# --- case 4: skipped_judge_does_not_pass --------------------------------------

def _skipped_judge_does_not_pass(root: Path) -> CheckResult:
    """Regression guard for #181's judge-skip rendering: a gating `judge:`
    check (not `path1_judge:`, which never gates at all) that legitimately
    skips (no ANTHROPIC_API_KEY -- exactly what rubrics/judge/judge.py does)
    must (a) NOT drag the row to a silent PASS via `RubricResult.score`
    excluding it from the mean with nothing else to average, and (b) render
    as `[SKIP*]` with the "checks skipped — unverified" header caveat, never
    as a plain `[SKIP]` that reads as "this ran fine and was intentionally
    skipped." (a) alone can't discriminate a correctly- from an incorrectly-
    behaved skip here (an all-skipped RubricResult scores 0.0 regardless of
    each check's own `.passed`), so this case also asserts on the report
    text, and does so by varying only the synthetic evaluator's own return
    value -- not by touching the real report()/CheckResult code -- exactly
    per the ticket's "wrong in the synthetic fixture" instruction.

    The name in the registry's `judge:` list is `maybe_flaky`; the check name
    that must appear in output is `judge:maybe_flaky`, per
    `_assert_declared_checks_executed`'s `{f"judge:{j}" ...}` convention."""
    name = "skipped_judge_does_not_pass"
    input_file = root / "input.txt"
    input_file.write_text("synthetic input\n", encoding="utf-8")

    # (a) honest skip: passed=False, as #181 requires a judge-skip to report.
    honest_mod_src = textwrap.dedent("""
        from rubrics.base import CheckResult
        def evaluate(target):
            return [CheckResult("judge:maybe_flaky", 0.0, False, skipped=True,
                                 detail="no ANTHROPIC_API_KEY -- simulated judge skip")]
    """).strip() + "\n"
    (root / "synth_honest_skip_mod.py").write_text(honest_mod_src, encoding="utf-8")

    # (b) the pre-#181 shape: a skip that claims passed=True. Nothing in
    # production code is touched to make this -- it's a synthetic evaluator
    # simulating the bug this case exists to catch if it ever came back.
    dishonest_mod_src = textwrap.dedent("""
        from rubrics.base import CheckResult
        def evaluate(target):
            return [CheckResult("judge:maybe_flaky", 0.0, True, skipped=True,
                                 detail="no ANTHROPIC_API_KEY -- but wrongly claims passed=True")]
    """).strip() + "\n"
    (root / "synth_dishonest_skip_mod.py").write_text(dishonest_mod_src, encoding="utf-8")

    reg = _write_registry(root, {
        "honest-skip-row": {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_honest_skip_mod",
            "input": str(input_file), "judge": ["maybe_flaky"],
        },
        "dishonest-skip-row": {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_dishonest_skip_mod",
            "input": str(input_file), "judge": ["maybe_flaky"],
        },
    })
    result_honest = _run_runner(reg, root, ["--component", "honest-skip-row"])
    result_dishonest = _run_runner(reg, root, ["--component", "dishonest-skip-row"])
    out_honest = _out(result_honest)
    out_dishonest = _out(result_dishonest)

    ok = (
        # A row whose only declared check is a skip has nothing to score ->
        # RubricResult.score == 0.0 -> FAILs the gate either way (exit 1);
        # asserted on both so a future scoring change that lets an all-skipped
        # row exit 0 is caught here too, not just the text assertions below.
        result_honest.returncode == 1
        and result_dishonest.returncode == 1
        and "SKIP*" in out_honest
        and "unverified" in out_honest.lower()
        # the dishonest simulation must NOT get the "verified skip" framing --
        # if it did, this case would fail to distinguish the two, which is
        # the entire point of asserting on report text instead of exit code.
        and "SKIP*" not in out_dishonest
        and "unverified" not in out_dishonest.lower()
    )
    return _bool_check(name, ok, exercised=f"evals/run_experiment.py via {sys.executable}", detail=(
        f"honest rc={result_honest.returncode} (want 1) has_SKIP*={'SKIP*' in out_honest} "
        f"has_unverified={'unverified' in out_honest.lower()}; "
        f"dishonest rc={result_dishonest.returncode} (want 1) has_SKIP*={'SKIP*' in out_dishonest}; "
        f"honest_out_tail={out_honest[-400:]!r}"
    ))


def evaluate(target: str) -> list[CheckResult]:  # noqa: ARG001 - self-contained, ignores target
    runner = _runner_path()
    if not runner.exists():
        missing = CheckResult(
            "runner_script_present", 0.0, False, hard_fail=True,
            detail=f"{runner} not found — cannot run any subprocess check",
        )
        return [missing]

    return [
        _run_in_tmp(_component_negatives_honoured),
        _run_in_tmp(_missing_target_fails_not_skips),
        _run_in_tmp(_declared_checks_all_executed),
        _run_in_tmp(_skipped_judge_does_not_pass),
    ]
