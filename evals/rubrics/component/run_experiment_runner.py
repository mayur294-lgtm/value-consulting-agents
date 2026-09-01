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

`path1_refuses_in_ci` (#204) is the sixth check, added once Path-1's CI guard
(evals/path1.py's `refuse_if_ci()` / `_in_ci()`) existed to test. It proves
the CI refusal fires via BOTH routes into path-1 — `evals/path1.py` invoked
directly, and `evals/run_experiment.py --component <row> --regenerate` — under
BOTH `$CI` and `$GITHUB_ACTIONS`, independently, as real subprocess calls to
the actual scripts (never an import-and-monkeypatch). #204 authored this
check but did NOT add it to registry.yaml's `run-experiment-runner` row (that
file is #201's concurrent territory on this branch) — it runs here as an
`[undeclared]` extra until that row's `code:` list and `mutations:` entry are
wired.
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


# --- case 5: retired_altitude_flag_hard_errors -------------------------------

# The retired altitude name, assembled rather than written, so this module holds
# no bare `"pipeline"` literal of the shape check_registry.py's pattern 10 looks
# for. This file is deliberately NOT in `_OLD_NAME_SCOPE` — for the same reason
# check_registry.py isn't: a gate that tests for a token cannot also be forbidden
# from containing it. Assembling it keeps that exemption from ever being needed.
_RETIRED_FLAG_VALUE = "pipe" + "line"

# Fragments of `_RETIRED_ALTITUDE_ERROR` in run_experiment.py (#188 / design D4,
# byte-sourced from .design/ux-design-v7.md:190). Asserted on stderr because the
# EXIT CODE ALONE CANNOT DISCRIMINATE: with the guard deleted, the retired name
# falls through to the `_ALTITUDES` membership test and argparse's `ap.error()`
# also exits 2. Only the rationale text distinguishes "the rename guard fired"
# from "argparse rejected an unknown string".
_RENAME_ERROR_FRAGMENTS = (
    "was renamed to `--altitude deliverable-structural`",
    "scores frozen fixture files in ~5s and has never run the ",
    "run `scripts/orchestrate.py` on a synthetic engagement",
)


def _retired_altitude_flag_hard_errors(root: Path) -> CheckResult:
    """Regression guard for #188's D4 contract: the retired altitude flag must
    HARD-ERROR with the rename rationale, and must never come back as a choice,
    an alias, or a deprecation shim.

    #188 shipped this guard and the `check_registry.py` grep that protects it,
    but registered no check over either — so the epic's own gate ("a gate that
    cannot fail certifies nothing", #186/#187) shipped unproven. This is that
    check. Its `mutations:` entry deletes the three-line guard in
    `run_experiment.py`'s altitude validation; with the guard gone, scenario A
    below loses the rationale text and this check goes red.

    Two scenarios, because exit code 2 is not discriminating on its own:

      A. `--altitude pipeline` -> rc 2 AND the rename rationale on stderr.
      B. `--altitude <unknown>` -> rc 2 AND NO rename rationale (argparse's
         generic invalid-choice path).

    Without B, a runner that printed the rename rationale for every bad
    altitude would pass A and still be wrong. With both, the check pins the
    guard specifically. Neither scenario reaches the registry — the guard runs
    before `_load_registry()` — but a synthetic one is wired anyway so this
    check exercises the same never-touch-the-real-registry path as its four
    siblings.
    """
    name = "retired_altitude_flag_hard_errors"
    reg = _write_registry(root, {
        "unused-row": {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_never_imported_mod",
            "input": str(root / "nothing.txt"), "code": ["never_run"],
        },
    })

    result_retired = _run_runner(reg, root, ["--altitude", _RETIRED_FLAG_VALUE])
    result_unknown = _run_runner(reg, root, ["--altitude", "not-an-altitude-at-all"])
    out_retired = _out(result_retired)
    out_unknown = _out(result_unknown)

    retired_has_rationale = all(frag in out_retired for frag in _RENAME_ERROR_FRAGMENTS)
    unknown_has_rationale = any(frag in out_unknown for frag in _RENAME_ERROR_FRAGMENTS)

    ok = (
        result_retired.returncode != 0
        and retired_has_rationale
        # the retired name must NOT be silently accepted as an alias for the
        # new one: a run that exits 0 here is D4's forbidden deprecation shim.
        and result_unknown.returncode != 0
        and not unknown_has_rationale
    )
    return _bool_check(name, ok, exercised=f"evals/run_experiment.py via {sys.executable}", detail=(
        f"retired-flag rc={result_retired.returncode} (want non-zero) "
        f"rationale={retired_has_rationale} (want True); "
        f"unknown-flag rc={result_unknown.returncode} (want non-zero) "
        f"rationale={unknown_has_rationale} (want False); "
        f"retired_out={out_retired[-400:]!r}"
    ))


# --- case 6: path1_refuses_in_ci ---------------------------------------------

PATH1_REL_PATH = Path("evals") / "path1.py"


def _path1_path() -> Path:
    return repo_root() / PATH1_REL_PATH


# Fragments of path1.CI_REFUSAL_MESSAGE (#204, ux-design-v7.md Error States
# table, "Path-1 in CI" row). Fragment-matched, not the whole literal string,
# for the same reason `_RENAME_ERROR_FRAGMENTS` above is: a trivial rewording
# of the surrounding sentence shouldn't spuriously break this guard.
_PATH1_CI_REFUSAL_FRAGMENTS = (
    "never runs in CI",
    "CI is $0 by design",
)

_REGEN_ROW = "unregenerable-row"


def _run_path1_direct(env_extra: dict) -> subprocess.CompletedProcess:
    """Invoke the REAL evals/path1.py as a subprocess — the first of the two
    routes into path-1 this check proves. `--agent`/`--input` are junk values
    on purpose: the CI guard must refuse BEFORE ever resolving either (a
    guard that fired only after reading the input file or the agent's prompt
    would blow up with an unrelated error here, not the CI refusal)."""
    env = dict(os.environ)
    for k in ("ANTHROPIC_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"):
        env.pop(k, None)
    env.update(env_extra)
    cmd = [sys.executable, str(_path1_path()), "--agent", "does-not-matter",
           "--input", "does-not-matter-either"]
    return subprocess.run(cmd, capture_output=True, timeout=SUBPROCESS_TIMEOUT_S,
                          env=env, cwd=str(repo_root()))


def _run_regenerate(registry_path: Path, pythonpath_dir: Path,
                     env_extra: dict) -> subprocess.CompletedProcess:
    """Invoke the REAL evals/run_experiment.py --regenerate — the second
    route. Same synthetic-registry-via-CORTEX_EVAL_REGISTRY plumbing as
    `_run_runner`, reused rather than duplicated where it's just env/pythonpath
    setup, but built standalone so each of the four scenarios below gets
    exactly one env var set and nothing else mutated between them."""
    env = dict(os.environ)
    for k in ("ANTHROPIC_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"):
        env.pop(k, None)
    env["CORTEX_EVAL_REGISTRY"] = str(registry_path)
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(pythonpath_dir) + (os.pathsep + existing_pp if existing_pp else "")
    env.update(env_extra)
    cmd = [sys.executable, str(_runner_path()), "--component", _REGEN_ROW, "--regenerate"]
    return subprocess.run(cmd, capture_output=True, timeout=SUBPROCESS_TIMEOUT_S,
                          env=env, cwd=str(repo_root()))


def _path1_refuses_in_ci(root: Path) -> CheckResult:
    """Regression guard for #204's hard CI guard: path-1 regeneration must
    refuse (non-zero exit, the documented message) under BOTH `$CI` and
    `$GITHUB_ACTIONS`, via BOTH routes into path-1 — `evals/path1.py`
    invoked directly, and `evals/run_experiment.py --component <row>
    --regenerate`. Four scenarios total (2 env vars x 2 routes), each its
    own clean subprocess so setting one var never leaks into another
    scenario's env.

    None of the four may ever reach a real `claude -p` call: this whole
    check runs with ANTHROPIC_API_KEY stripped and no network, so a guard
    that fired only AFTER trying to shell out would hang or surface an
    unrelated auth/timeout error here instead of cleanly refusing with the
    documented message — that failure mode is exactly what asserting on the
    message fragments (not just the exit code) catches.

    The synthetic registry's row points `input:` at a file that is never
    created and names an evaluator module that is never written — both
    deliberately, to prove the refusal happens BEFORE the runner touches
    either (a guard that only fired after resolving the input or importing
    the evaluator would blow up with an unrelated traceback here instead)."""
    name = "path1_refuses_in_ci"
    reg = _write_registry(root, {
        _REGEN_ROW: {
            "altitude": "component", "threshold": 0.80,
            "evaluator": "synth_never_imported_for_regen",
            "input": str(root / "never_created_input.md"),
            "code": ["never_reached"],
        },
    })

    scenarios: dict[str, subprocess.CompletedProcess] = {}
    for env_var in ("CI", "GITHUB_ACTIONS"):
        scenarios[f"path1_direct[{env_var}]"] = _run_path1_direct({env_var: "true"})
        scenarios[f"run_experiment_regenerate[{env_var}]"] = _run_regenerate(reg, root, {env_var: "true"})

    def _refuses(res: subprocess.CompletedProcess) -> bool:
        out = _out(res)
        return res.returncode != 0 and all(frag in out for frag in _PATH1_CI_REFUSAL_FRAGMENTS)

    ok = all(_refuses(r) for r in scenarios.values())
    detail = "; ".join(f"{k}: rc={r.returncode} refuses={_refuses(r)}" for k, r in scenarios.items())
    return _bool_check(name, ok, exercised=f"evals/path1.py and evals/run_experiment.py via {sys.executable}",
                       detail=detail[:600])


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
        _run_in_tmp(_retired_altitude_flag_hard_errors),
        _run_in_tmp(_path1_refuses_in_ci),
    ]
