"""Bits the six hook rows share that `rubrics/_harness.py` does not carry.

#196 extracted the general hook kit (`run_hook_subprocess`, `pretooluse_payload`,
`build_fixture_engagement`, `inject_fault`, `bool_check`, `run_in_tmpdir`,
`check_runs_under_registered_interpreter`). Three things #197 needs are NOT in
it, and are deliberately kept HERE rather than added there, because #198-#200
are editing near that file concurrently:

  stop_payload()                      the stdin bytes Claude Code sends a STOP
                                      hook. `_harness` only has the PreToolUse
                                      shape; `enforce-journal.py` and
                                      `eval-on-stop.py` are Stop hooks.
  stop_blocked() / block_reason()     the Stop decision contract
                                      (`{"decision": "block", "reason": ...}`),
                                      which is a different envelope from
                                      PreToolUse's `hookSpecificOutput`.
  check_invoked_as_subprocess_not_import()
                                      the shared "this is really a subprocess"
                                      check — see below.

WHY `invoked_as_subprocess_not_import` IS SHAPED THE WAY IT IS
--------------------------------------------------------------
Asserting "we called subprocess.run" is not a property of the hook, and
asserting "the module is not in sys.modules" is trivially true of code that
never imported it — neither would notice a rubric that quietly switched to
import-and-call, which is the failure mode the ticket names.

Every one of these six hooks binds its project root ONCE, at module import:

    PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

So an imported-once hook can only ever see ONE project root, no matter how many
"invocations" a rubric makes against it: the second fixture would be silently
evaluated against the first one's tree (or, worse, against the real repo). A
fresh PROCESS per invocation is the only way two different `CLAUDE_PROJECT_DIR`
values can produce two different decisions.

The check therefore performs TWO real invocations through the row's own
production helper, with two DIFFERENT `CLAUDE_PROJECT_DIR` roots chosen so the
hook's answer must differ, and asserts:

  1. observation A is True and observation B is False — the decision tracked
     `CLAUDE_PROJECT_DIR` per invocation, which an in-process import cannot do;
  2. at least two invocations were RECORDED (via `_harness`'s
     `record_hook_invocation`), each naming the hook script after its
     interpreter prefix — so the differing answers came from spawns, not from
     two in-process calls that happened to disagree;
  3. no module whose `__file__` is the hook script is in `sys.modules` — the
     rubric never imported the subject at all.

Each of the three is checkable and each is load-bearing; (1) alone would pass
for an import-and-monkeypatch rubric that re-set the module global by hand, and
(3) alone passes vacuously.
"""
from __future__ import annotations

import contextlib
import json
import os
import stat
import sys
from pathlib import Path
from typing import Callable, Iterator, Optional

from rubrics.base import CheckResult
from rubrics._harness import (
    HookRun,
    bool_check,
    capture_hook_invocations,
    pretooluse_payload,
    registered_interpreter,
    run_in_tmpdir,
)

# Generous next to `_harness.DEFAULT_HOOK_TIMEOUT_S` (15s): these hooks are
# ~0.04s each, but `eval-on-stop.py` runs the whole runtime scoring engine in
# its subprocess and legitimately takes several seconds on a cold interpreter.
HOOK_TIMEOUT_S = 15.0
SLOW_HOOK_TIMEOUT_S = 180.0


# ---------------------------------------------------------------------------
# Payloads
# ---------------------------------------------------------------------------

def write_payload(file_path: str, content: str = "placeholder\n") -> bytes:
    """A PreToolUse(Write) payload — `require-checkpoint`, `require-harness`
    and `synthetic-knowledge-guard` all gate this tool."""
    return pretooluse_payload("Write", {"file_path": file_path, "content": content})


def edit_payload(file_path: str, new_string: str = "placeholder\n") -> bytes:
    """A PreToolUse(Edit) payload. `synthetic-knowledge-guard` reads the
    incoming content from `new_string` for Edit, `content` for Write — a
    different field, which is its own regression surface."""
    return pretooluse_payload(
        "Edit", {"file_path": file_path, "old_string": "x", "new_string": new_string})


def read_payload(file_path: str) -> bytes:
    return pretooluse_payload("Read", {"file_path": file_path})


def bash_payload(command: str) -> bytes:
    return pretooluse_payload("Bash", {"command": command})


def stop_payload(*, stop_hook_active: bool = False,
                 session_id: str = "zzz-eval-session") -> bytes:
    """The stdin bytes Claude Code hands a STOP hook.

    `_harness.pretooluse_payload` is the wrong envelope for `enforce-journal.py`
    and `eval-on-stop.py`: a Stop hook receives no `tool_name`/`tool_input`, and
    answers on a different contract (`{"decision": "block", "reason": ...}`
    rather than `hookSpecificOutput.permissionDecision`). `stop_hook_active`
    is the loop-guard flag Claude Code sets when a previous Stop hook already
    blocked this turn; both hooks read the payload, so it must be present and
    well-shaped.
    """
    return json.dumps({
        "session_id": session_id,
        "transcript_path": "/dev/null",
        "hook_event_name": "Stop",
        "stop_hook_active": stop_hook_active,
    }).encode("utf-8")


# ---------------------------------------------------------------------------
# Stop-hook decision contract
# ---------------------------------------------------------------------------

def stop_blocked(result: HookRun) -> bool:
    """True iff the hook emitted the Stop-hook BLOCK envelope."""
    return bool(result.stdout_json) and result.stdout_json.get("decision") == "block"


def block_reason(result: HookRun) -> str:
    value = (result.stdout_json or {}).get("reason", "")
    return value if isinstance(value, str) else ""


def crashed(result: HookRun) -> bool:
    """The hook died on an unhandled exception rather than deciding.

    Used by the fail-OPEN rows: 'did not block' is necessary but not
    sufficient — a hook that traceback'd also did not block, and that is a
    defect, not the contract. Checks that care say so explicitly.
    """
    return b"Traceback (most recent call last)" in result.stderr


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def set_mtime(path: Path, seconds_ago: float) -> None:
    """Backdate (or forward-date, with a negative value) a path's mtime.

    `anonymize-guard`'s staleness rule and `enforce-journal`'s freshness /
    recency rules are both mtime comparisons, so several checks here have to
    control mtimes precisely rather than hope the filesystem's write ordering
    produces the gap they need.
    """
    import time
    when = time.time() - seconds_ago
    os.utime(path, (when, when))


@contextlib.contextmanager
def isolated_hook_env() -> Iterator[None]:
    """Make a hook subprocess offline, $0, and dependent only on
    `CLAUDE_PROJECT_DIR` for the duration of the block.

    `run_hook_subprocess` hands the child a copy of `os.environ`, and
    `eval-on-stop.py` transitively imports `evals/runtime.py`. Two ambient
    variables would otherwise change what the check measures:

      LANGFUSE_* / ANTHROPIC_API_KEY   `runtime.py` loads `evals/.env` with
          `os.environ.setdefault` and POSTs scores to Langfuse if it finds
          keys. Set to the EMPTY STRING rather than deleted, because that is
          what makes it stick: `setdefault` will not overwrite an existing
          empty value, and `_log_langfuse`'s `if not os.getenv(...)` treats it
          as absent.

      PYTHONPATH                       DELETED, not blanked (an empty
          PYTHONPATH still contributes an empty entry, i.e. cwd). The mutation
          harness runs its scoring child with the SHADOW's `evals/` on
          PYTHONPATH, which a hook subprocess would inherit — so
          `from runtime import ...` would succeed no matter what
          `CLAUDE_PROJECT_DIR` points at, and
          `fails_open_when_eval_engine_unavailable` could never observe the
          absence it is named for. The hook's real contract is that it locates
          the eval engine through `PROJECT_DIR / "evals"`; stripping the
          ambient path is what holds it to that.
    """
    blanked = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST",
               "ANTHROPIC_API_KEY")
    removed = ("PYTHONPATH",)
    previous = {k: os.environ.get(k) for k in blanked + removed + ("CORTEX_EVAL_NO_JUDGE",)}
    try:
        for k in blanked:
            os.environ[k] = ""
        for k in removed:
            os.environ.pop(k, None)
        os.environ["CORTEX_EVAL_NO_JUDGE"] = "1"
        yield
    finally:
        for k, v in previous.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@contextlib.contextmanager
def inject_readonly(*paths: Path) -> Iterator[tuple]:
    """A second fault KIND, alongside `_harness.inject_fault(kind="unreadable")`.

    `chmod 0o555`: the directory stays readable and traversable but nothing new
    can be CREATED inside it, so a subject that tries to write a file there gets
    a real, unmocked `PermissionError` while every read it performs still
    succeeds. `eval-on-stop.py` needs exactly that shape and cannot use
    `unreadable`: a `chmod 000` on its outputs/ directory injects NOTHING it can
    see, because `Path.glob` swallows `PermissionError` internally (measured
    under 3.9.6 — the glob simply yields no entries), so the hook's
    `except OSError` branch is unreachable that way and the run looks like an
    ordinary "no recent outputs" early exit.

    Lives here rather than in `rubrics/_harness.py` on purpose: #196 asks new
    kinds to be NAMED rather than hand-rolled, and #198-#200 are editing near
    that file concurrently. If a second row ever needs this, it should move up
    into `inject_fault` as `kind="readonly"`.

    Restoration is unconditional and in a `finally`, like `inject_fault`'s:
    `TemporaryDirectory` cleanup cannot unlink from a 0o555 directory, so
    without it a passing check would become a crashing one on the way out.

    Callers must already have returned `fault_injection_skip(...)` when running
    as root, which bypasses these bits entirely.
    """
    original: list = []
    try:
        for path in paths:
            original.append((path, path.stat().st_mode))
            path.chmod(0o555)
        yield tuple(p for p, _ in original)
    finally:
        for path, mode in original:
            try:
                path.chmod(mode | stat.S_IRWXU)
            except OSError:  # pragma: no cover - best effort; tempdir cleanup reports
                pass


def run_in_tmp(fn: Callable[..., CheckResult], *args, prefix: str) -> CheckResult:
    """Row-local alias for the shared `run_in_tmpdir`, pinning a per-row tempdir
    prefix so a leaked directory is traceable to the rubric that leaked it."""
    return run_in_tmpdir(fn, *args, prefix=prefix)


# ---------------------------------------------------------------------------
# invoked_as_subprocess_not_import
# ---------------------------------------------------------------------------

def hook_module_imported_in_process(hook_path: Path) -> bool:
    """True if any module currently in `sys.modules` was loaded FROM the hook
    script — i.e. the rubric imported its subject instead of spawning it."""
    try:
        target = hook_path.resolve()
    except OSError:  # pragma: no cover - a hook path that cannot resolve
        return False
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        try:
            if Path(f).resolve() == target:
                return True
        except OSError:  # pragma: no cover - unresolvable module path
            continue
    return False


def _argv_names_hook(argv: list, hook_path: Path, prefix_len: int) -> bool:
    try:
        target = hook_path.resolve()
    except OSError:  # pragma: no cover
        return False
    for token in argv[prefix_len:]:
        try:
            if Path(token).resolve() == target:
                return True
        except OSError:
            continue
    return False


def check_invoked_as_subprocess_not_import(
    hook_path: Path,
    *,
    hook_label: str,
    observe_a: Callable[[], bool],
    observe_b: Callable[[], bool],
    what: str,
) -> CheckResult:
    """The shared `invoked_as_subprocess_not_import` check — see this module's
    docstring for why it is shaped as a two-project-root differential rather
    than as an assertion about the rubric's own call site.

    `observe_a` / `observe_b` each perform exactly ONE invocation through the
    row's own production subprocess helper, against DIFFERENT
    `CLAUDE_PROJECT_DIR` roots, and return the boolean the hook's answer turns
    on (denied / blocked / wrote-a-report — whatever this hook's observable
    decision is). A must come back True and B False. `what` names that
    observable for the detail line.
    """
    name = "invoked_as_subprocess_not_import"

    def fail(detail: str) -> CheckResult:
        return CheckResult(name, 0.0, False, hard_fail=True,
                           detail=f"{hook_label}: {detail}")

    try:
        prefix = registered_interpreter(hook_path)
    except Exception as exc:  # noqa: BLE001 - reported, never crashes the rubric
        return fail(f"could not resolve the registered interpreter: "
                    f"{type(exc).__name__}: {exc}")

    try:
        with capture_hook_invocations() as recorded:
            a = observe_a()
            b = observe_b()
    except Exception as exc:  # noqa: BLE001
        return fail(f"an observation raised {type(exc).__name__}: {exc}")

    if len(recorded) < 2:
        return fail(
            f"only {len(recorded)} hook invocation(s) were recorded across two "
            f"observations — a rubric that imported the hook instead of spawning it "
            f"records none, and `record_hook_invocation` is what makes the spawn "
            f"observable at all")
    bad = [argv for argv in recorded if not _argv_names_hook(argv, hook_path, len(prefix))]
    if bad:
        return fail(f"a recorded invocation does not name {hook_path} after its "
                    f"interpreter prefix {prefix!r}: {bad[0]!r}")

    if hook_module_imported_in_process(hook_path):
        return fail(f"{hook_path} is present in sys.modules — the rubric IMPORTED its "
                    f"subject; the process-level contract (stdout JSON shape, exit "
                    f"code) is then never exercised at all")

    if not (a is True and b is False):
        return fail(
            f"the two invocations did not track CLAUDE_PROJECT_DIR: {what} was "
            f"{a!r} under project root A and {b!r} under project root B "
            f"(expected True / False). The hook binds PROJECT_DIR once at module "
            f"import, so only a fresh PROCESS per invocation can produce two "
            f"different answers — this is what distinguishes a subprocess from an "
            f"import-and-call")

    return CheckResult(name, 1.0, True, hard_fail=True, detail=(
        f"{hook_label}: {len(recorded)} spawns recorded, argv[0:{len(prefix)}]="
        f"{prefix!r}; {what} = True under project root A and False under project "
        f"root B (per-invocation CLAUDE_PROJECT_DIR); hook module never imported "
        f"in-process"))


def missing_hook_check(hook_path: Path) -> Optional[CheckResult]:
    """A single hard-failing CheckResult when the hook script is absent, so a
    row reports "the subject is gone" instead of 12 identical subprocess
    errors."""
    if hook_path.exists():
        return None
    return CheckResult("hook_script_present", 0.0, False, hard_fail=True,
                       detail=f"{hook_path} not found — cannot run any subprocess check")


__all__ = [
    "HOOK_TIMEOUT_S", "SLOW_HOOK_TIMEOUT_S", "bash_payload", "block_reason",
    "bool_check", "check_invoked_as_subprocess_not_import", "crashed", "edit_payload",
    "hook_module_imported_in_process", "inject_readonly", "isolated_hook_env",
    "missing_hook_check",
    "read_payload", "run_in_tmp", "set_mtime", "stop_blocked", "stop_payload",
    "write_payload",
]
