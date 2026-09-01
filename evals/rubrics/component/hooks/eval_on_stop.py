"""`eval-on-stop` component evaluator — the runtime scoring Stop hook.

SUBJECT: `.claude/hooks/eval-on-stop.py`, the STOP hook that scores an
engagement a consultant touched during an INTERACTIVE session — agent outputs,
deliverables and the deliverable-structural contracts — writes
`.pipeline_run_report.json`, and flags anything below threshold. It complements
`orchestrate.py`'s end-of-run scoring, which only covers the CLI pipeline.

It is the one hook here whose job is to DO something rather than to refuse
something, and its contract is unusually strict about what it must NOT do:
non-blocking, fail-open, code-only (`CORTEX_EVAL_NO_JUDGE=1`, so no judge and no
spend), and scoped to engagements touched in the last 30 minutes. Every one of
those is a way it can fail silently — a session that ends with no report looks
exactly like a session with nothing to report — which is why this row exists.

WHAT MAKES THIS ROW DIFFERENT FROM THE OTHER FIVE
--------------------------------------------------
1. It is the only hook here that IMPORTS the eval engine, from
   `PROJECT_DIR / "evals"`. The fixtures therefore symlink `repo_root()/evals`
   into the tempdir project root — `repo_root()` so that under the mutation
   harness the symlink lands on the SHADOW's `evals/`, not the real one.
2. `_common.isolated_hook_env()` strips `PYTHONPATH` around every invocation.
   Without it, the mutation harness's scoring child puts the shadow's `evals/`
   on `PYTHONPATH`, the hook subprocess inherits it, and `from runtime import
   ...` succeeds regardless of `CLAUDE_PROJECT_DIR` — which would make
   `fails_open_when_eval_engine_unavailable` unprovable. It also blanks the
   Langfuse and Anthropic keys, keeping the row offline, silent and $0.
3. Its fault check needs a fault kind `_harness.inject_fault` does not have.
   `chmod 000` on outputs/ injects nothing observable here, because
   `Path.glob` swallows `PermissionError` internally (measured under 3.9.6) and
   the run degrades into an ordinary "nothing recent" early exit. The reachable
   fail-open handler is the `except Exception: pass` around
   `score_engagement`/`write_report`, so the fault is a READ-ONLY engagement
   directory (`_common.inject_readonly`, chmod 0o555): every read still
   succeeds, only the report write fails.

SAFETY: this hook globs `PROJECT_DIR/engagements/*/*/outputs` and SCORES what it
finds. Every fixture is a tempdir and `CLAUDE_PROJECT_DIR` always points at it,
so the real, gitignored `engagements/` tree is never reached — including under
the mutation harness, whose shadow root does not contain `engagements/` at all
(it is excluded from `SHADOW_SUBTREES`). Nothing in this module may ever be
changed in a way that lets `PROJECT_DIR` default to the real checkout.

threshold 1.00. No `judge:` entries — the hook itself disables the judge, and so
does this row.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from rubrics.base import CheckResult, repo_root
from rubrics._harness import (
    HookRun,
    build_fixture_engagement,
    check_runs_under_registered_interpreter,
    fault_injection_skip,
    run_hook_subprocess,
)
from rubrics.component.hooks._common import (
    SLOW_HOOK_TIMEOUT_S,
    bool_check,
    check_invoked_as_subprocess_not_import,
    crashed,
    inject_readonly,
    isolated_hook_env,
    missing_hook_check,
    run_in_tmp,
    set_mtime,
    stop_blocked,
    stop_payload,
)

HOOK_REL_PATH = Path(".claude") / "hooks" / "eval-on-stop.py"
TMP_PREFIX = "eval_on_stop_row_"

SLUG = "zzzplaceholderclient"
ENGAGEMENT = "2026-01_test_engagement"
REPORT_NAME = ".pipeline_run_report.json"

# Deliberately thin: routed by `runtime._DELIVERABLE_ROUTES` to
# `rubrics.deliverable.report`, and thin enough that it scores below threshold
# and therefore produces a flag. What is asserted is that scoring HAPPENED and
# was recorded — never a particular score, which would couple this row to
# another row's rubric.
THIN_DELIVERABLE = "# Executive Summary\n\nplaceholder\n"


def _hook_path() -> Path:
    """Resolved through `repo_root()` so the mutation harness reaches its SHADOW
    copy of the hook."""
    return repo_root() / HOOK_REL_PATH


def _run_hook(project_dir: Path) -> HookRun:
    """This row's ONE subprocess entry point. `isolated_hook_env()` wraps every
    invocation — see the module docstring, point 2."""
    with isolated_hook_env():
        return run_hook_subprocess(_hook_path(), stop_payload(),
                                   project_dir=project_dir,
                                   timeout=SLOW_HOOK_TIMEOUT_S)


def _seed(root: Path, *, outputs_age_s: float = 5.0, with_evals: bool = True) -> Path:
    """A project root holding one engagement with one recent deliverable, and
    (optionally) the eval engine the hook imports.

    The `evals` symlink is taken from `repo_root()`, never from an absolute
    literal: under the mutation harness `repo_root()` is the shadow, so the
    hook imports the SHADOW's `runtime.py` and a mutation to it would actually
    be exercised.
    """
    fixture = build_fixture_engagement(root, slug=SLUG, engagement=ENGAGEMENT,
                                       subdirs=("outputs",),
                                       documents={"outputs/executive_summary.md":
                                                  THIN_DELIVERABLE})
    assert fixture.engagement_dir is not None
    set_mtime(fixture.engagement_dir / "outputs" / "executive_summary.md", outputs_age_s)
    if with_evals:
        link = root / "evals"
        if not link.exists():
            os.symlink(repo_root() / "evals", link)
    return fixture.engagement_dir


def _report_path(engagement_dir: Path) -> Path:
    return engagement_dir / REPORT_NAME


def _report_written(engagement_dir: Path) -> bool:
    path = _report_path(engagement_dir)
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    evals = data.get("evals")
    return isinstance(evals, dict) and evals.get("schema") == "pipeline_run_report/eval/v2"


# --- what the hook is for ------------------------------------------------------

def _scores_recently_touched_engagement_and_writes_report(root: Path) -> CheckResult:
    """The hook's whole purpose. A deliverable written seconds ago must be
    scored and the result persisted to `.pipeline_run_report.json` under the
    engagement, carrying the v2 report schema.

    Asserts that scoring HAPPENED and was recorded — the schema key, the
    presence of the deliverable/agents/contract blocks — never a particular
    score. Pinning a score here would couple this row to whatever
    `rubrics.deliverable.report` happens to weigh today and would go red for
    reasons that have nothing to do with this hook.
    """
    name = "scores_recently_touched_engagement_and_writes_report"
    eng = _seed(root)
    result = _run_hook(root)
    report = _report_path(eng)
    blocks = []
    if report.is_file():
        try:
            blocks = sorted(json.loads(report.read_text(encoding="utf-8"))
                            .get("evals", {}))
        except (OSError, json.JSONDecodeError):
            blocks = []
    ok = (
        result.returncode == 0
        and not crashed(result)
        and _report_written(eng)
        and {"deliverables", "agents", "deliverable_structural", "flags"} <= set(blocks)
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} report_written={_report_written(eng)} "
        f"evals_blocks={blocks} stderr={result.stderr_text[-160:]!r}"))


def _ignores_engagement_outside_window(root: Path) -> CheckResult:
    """Scope is the last 30 minutes (`WINDOW_S`). An engagement whose outputs
    have not changed since then is not this session's work: re-scoring the
    whole `engagements/` tree at every Stop would make the hook cost grow with
    the repo and stall the session it promises never to stall."""
    name = "ignores_engagement_outside_window"
    eng = _seed(root, outputs_age_s=2 * 1800)
    result = _run_hook(root)
    ok = (
        result.returncode == 0
        and not crashed(result)
        and not _report_path(eng).exists()
    )
    return bool_check(name, ok, detail=(
        f"outputs 3600s old (window 1800s) -> rc={result.returncode} "
        f"report_exists={_report_path(eng).exists()}"))


def _never_blocks_the_stop(root: Path) -> CheckResult:
    """NON-BLOCKING is the hardest half of this hook's contract to notice
    breaking. It scores the engagement, finds flags, and must still let the turn
    end — flags go to stderr, never to a `{"decision": "block"}` envelope on
    stdout. A scoring hook that could block would turn any rubric regression
    anywhere in the repo into a session the consultant cannot finish."""
    name = "never_blocks_the_stop"
    eng = _seed(root)
    result = _run_hook(root)
    ok = (
        result.returncode == 0
        and not stop_blocked(result)
        and b'"decision"' not in result.stdout
        and _report_written(eng)          # it really did run; the allow is not vacuous
    )
    return bool_check(name, ok, detail=(
        f"scored an engagement with flags -> rc={result.returncode} "
        f"blocked={stop_blocked(result)} stdout={result.stdout_text[:160]!r} "
        f"report_written={_report_written(eng)}"))


# --- fail-open contract ---------------------------------------------------------

def _fails_open_when_eval_engine_unavailable(root: Path) -> CheckResult:
    """No `evals/` under the project root — the "evals absent / import issue"
    case the hook names in its own comment. It must exit 0 silently, not
    traceback: this is the state of every checkout where the hook is installed
    but the eval engine is not, and a crash there would put a stack trace at the
    end of every single turn.

    `isolated_hook_env()` strips `PYTHONPATH` so the absence is real — see the
    module docstring, point 2.
    """
    name = "fails_open_when_eval_engine_unavailable"
    eng = _seed(root, with_evals=False)
    result = _run_hook(root)
    ok = (
        result.returncode == 0
        and not crashed(result)
        and not _report_path(eng).exists()
        and not stop_blocked(result)
    )
    return bool_check(name, ok, detail=(
        f"no evals/ under CLAUDE_PROJECT_DIR -> rc={result.returncode} "
        f"crashed={crashed(result)} report_exists={_report_path(eng).exists()} "
        f"stderr={result.stderr_text[-200:]!r}"))


def _fails_open_under_injected_fault(root: Path) -> CheckResult:
    """A real, unmocked `PermissionError` while WRITING the report must not
    block or crash — the `except Exception: pass  # fail-open` around
    `score_engagement`/`write_report`.

    The fault is a READ-ONLY engagement directory (chmod 0o555), not an
    unreadable one: everything the hook reads still succeeds, so it reaches the
    scoring path and fails only on the write. `chmod 000` would have injected
    nothing observable — `Path.glob` swallows `PermissionError` internally
    (measured under 3.9.6), so the run would degrade into an ordinary "nothing
    recent" early exit and the check would pass for the wrong reason. That is
    why this row adds `_common.inject_readonly` rather than reusing
    `_harness.inject_fault(kind="unreadable")`.

    Proved as a SPLIT: the same fixture writes a report when the directory is
    writable, and writes none — silently, exit 0, no traceback — when it is not.

    Skips under root, which bypasses permission bits entirely.
    """
    name = "fails_open_under_injected_fault"
    skip = fault_injection_skip(name, perms="directory")
    if skip is not None:
        return skip

    eng = _seed(root)
    control = _run_hook(root)
    control_ok = _report_written(eng)
    _report_path(eng).unlink(missing_ok=True)

    with inject_readonly(eng):
        faulted = _run_hook(root)
        wrote_under_fault = _report_path(eng).exists()

    ok = (
        control.returncode == 0 and control_ok
        and faulted.returncode == 0 and not crashed(faulted)
        and not wrote_under_fault and not stop_blocked(faulted)
    )
    return bool_check(name, ok, detail=(
        f"writable engagement dir: rc={control.returncode} report_written={control_ok}; "
        f"engagement dir chmod 0555: rc={faulted.returncode} "
        f"report_written={wrote_under_fault} crashed={crashed(faulted)} "
        f"blocked={stop_blocked(faulted)}"))


# --- process contract -----------------------------------------------------------

def _invoked_as_subprocess_not_import(root: Path) -> CheckResult:
    """Two invocations against two different `CLAUDE_PROJECT_DIR` roots — see
    `_common.py`. Like `enforce-journal`, this hook takes no argument at all:
    `PROJECT_DIR` IS its entire input, so an import-once hook would keep scoring
    root A's engagements forever. Root A holds a freshly touched engagement (a
    report appears); root B is empty (nothing to score, no report)."""
    a_root = root / "project_a"
    b_root = root / "project_b"
    b_root.mkdir(parents=True, exist_ok=True)
    a_eng = _seed(a_root)
    b_eng = b_root / "engagements" / SLUG / ENGAGEMENT

    def _observe(project_root: Path, eng: Path) -> bool:
        _run_hook(project_root)
        return _report_path(eng).is_file()

    return check_invoked_as_subprocess_not_import(
        _hook_path(),
        hook_label="eval-on-stop.py",
        observe_a=lambda: _observe(a_root, a_eng),
        observe_b=lambda: _observe(b_root, b_eng),
        what="a run report was written",
    )


def _runs_under_registered_interpreter(root: Path) -> CheckResult:
    """#192/backlog :116 — spawned under the interpreter
    `.claude/settings.json` registers (bare `python3`, 3.9.6 on most consultant
    machines), never the eval runner's `sys.executable`. That matters more here
    than anywhere else on these six rows: this hook imports the whole eval
    engine, so certifying it under CI's 3.11 would say nothing about whether
    `evals/runtime.py` even imports on the interpreter a consultant session
    actually runs it with. `spawn` uses an EMPTY project root so the probe
    exits early and costs nothing; only the argv matters."""
    return check_runs_under_registered_interpreter(
        _hook_path(),
        hook_label="eval-on-stop.py",
        spawn=lambda: _run_hook(root),
    )


def evaluate(target: str) -> list:  # noqa: ARG001 - self-contained, ignores target
    missing = missing_hook_check(_hook_path())
    if missing is not None:
        return [missing]
    return [
        run_in_tmp(_scores_recently_touched_engagement_and_writes_report, prefix=TMP_PREFIX),
        run_in_tmp(_ignores_engagement_outside_window, prefix=TMP_PREFIX),
        run_in_tmp(_never_blocks_the_stop, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_when_eval_engine_unavailable, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_under_injected_fault, prefix=TMP_PREFIX),
        run_in_tmp(_invoked_as_subprocess_not_import, prefix=TMP_PREFIX),
        run_in_tmp(_runs_under_registered_interpreter, prefix=TMP_PREFIX),
    ]
