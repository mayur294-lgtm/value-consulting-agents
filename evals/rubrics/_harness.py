"""Shared property-test kit for rubrics whose subject is a `.claude/hooks/*`
script, an engagement tree, or both (tickets #192 + #196, backlog :116).

WHAT IS IN HERE, AND WHY IT IS SHARED
--------------------------------------
`pii_anonymizer.py` and `mcp_query_guard.py` independently grew the same four
things — a synthetic engagement fixture, a hook-subprocess invoker, a
permission-fault injector, and a `CheckResult`-from-bool helper — and the
copies had already started to diverge. #197-#200 author eight more rows on
top of this (six hooks, `artifact_boundary`, `pipeline_workspace`, identity,
migration, calibrator, builders); each would have copied it again. So:

  registered_interpreter()          which interpreter settings.json registers
  record_hook_invocation()          + capture_hook_invocations()
  check_runs_under_registered_interpreter()
  run_hook_subprocess()             -> HookRun (rc, stdout JSON, stdout, stderr)
  pretooluse_payload()              the stdin bytes Claude Code would send
  build_fixture_engagement()        -> FixtureEngagement
  assert_deny_list_non_empty()      the vacuity guard (see below)
  inject_fault()                    + fault_injection_skip()
  bool_check() / run_in_tmpdir()

THE DENY-LIST VACUITY GUARD — read before writing a check that uses one
-----------------------------------------------------------------------
"An empty deny-list makes every other assertion pass vacuously, which is how
this repo twice shipped a gate scoring 1.000 while certifying nothing" (#166:
the path-2-only eval gate, and the two-line mcp-query-guard fixture
pre-711b56c). `assert_deny_list_non_empty()` is therefore not an optional
courtesy a caller may remember to call FIRST — it is wired INSIDE
`FixtureEngagement.resolved_deny_terms()`, the only supported way to get a
resolved deny-list out of a fixture, so a caller cannot obtain the terms
without it having already run. `build_fixture_engagement()` additionally
refuses to hand back a fixture whose declared client identity appears nowhere
in the tree it just wrote.

NARROW vs RESOLVED DENY LISTS ARE NOT INTERCHANGEABLE (#209)
------------------------------------------------------------
A fixture exposes TWO deny lists and deliberately never collapses them:

  .client_deny_terms()    the client identity ONLY (full + short name)
  .resolved_deny_terms()  what `denylist.resolve_engagement_deny_list`
                          actually produces — client identity PLUS the
                          stakeholder names mined from CLIENT_PROFILE.md /
                          engagement_intake.md / ENGAGEMENT_CONTEXT.md

Which one a check takes is a load-bearing decision, not a default. #209:
`pii_anonymizer`'s document- and image-format checks keep the NARROW one
because their whole subject is that `pii.ingest`'s record-per-row table
rendering makes a tabular person name PERSON-detectable; hand them the
stakeholder term and they would score 1.000 even if that rendering regressed
to pipe tables. Only the two checks whose subject IS deny-list coverage take
the resolved one. Do not "unify" them.

THE BUG registered_interpreter() CLOSES
--------------------
`.claude/settings.json` registers every Python hook as bare `python3` — the
interpreter every consultant's session actually runs it under (3.9.6 on most
consultant machines today). But `mcp_query_guard.py` and `pii_anonymizer.py`
invoked their subject hook via `[sys.executable, str(hook_path)]` — CI's
3.11 (`actions/setup-python`) or, locally, whatever interpreter is running
`evals/run_experiment.py` (typically `.venv/bin/python`, itself 3.10-3.13).
So the eval gate could certify a hook green under an interpreter no
consultant machine ever actually invokes it with — a real drift, not a
theoretical one: a hook that only breaks under 3.9.6 (a stdlib API removed
in 3.10+, a syntax feature not yet backported, ...) would sail through this
gate every time.

Bare `python3` is the CORRECT registration for these particular hooks —
see solution-design-v6.md D13: `anonymize-guard.py` was deliberately kept
off the Presidio venv because a ~1s import on every Read/Bash would make
sessions feel broken, and a module-level import failure would make a
PreToolUse hook fail OPEN. The fix here is entirely in the rubric, never in
`.claude/settings.json`.

registered_interpreter()
-------------------------
Parses `.claude/settings.json`, finds the ONE registered "command" hook
entry whose final token (after `$CLAUDE_PROJECT_DIR` substitution) resolves
to the given hook script path, and returns everything BEFORE that final
token as the argv prefix a subprocess call must use in its place.

  - `python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/mcp-query-guard.py`
    -> `["python3"]`
  - a hypothetical hook routed through the venv resolver,
    `"$CLAUDE_PROJECT_DIR"/.claude/hooks/_resolve_python.sh "$CLAUDE_PROJECT_DIR"/.claude/hooks/foo.py`
    -> `[str(repo_root() / ".claude/hooks/_resolve_python.sh")]` — the
    WRAPPER is "the interpreter" from this function's point of view; no
    hook currently routes through it, but a caller that resolves this
    correctly needs no special-casing when one eventually does.
  - a hook registered with no interpreter at all (a shell script invoked
    directly, e.g. `auto-branch.sh`) -> `[]`, meaning "exec it directly,
    relying on its own shebang" — not an error.

Raises `HookNotRegisteredError` — NEVER falls back to `sys.executable` — if
the hook has no registration in settings.json, settings.json is missing or
unparsable, or its shape doesn't match what this parser understands (no
top-level "hooks" dict, a matcher entry missing its "hooks" list, a command
entry with no usable "command" string, ...). A rubric that cannot prove
which interpreter Claude Code actually invokes for a hook must fail loudly,
not silently certify under a different one — that silent-fallback failure
mode is exactly what this module exists to close.

record_hook_invocation() / capture_hook_invocations()
------------------------------------------------------
Resolving the right interpreter is only half the guarantee. The other half
is that the rubric's subprocess helper actually USES it — and no property of
`registered_interpreter()`'s return value can establish that. (Spec-review
FAIL, 2026-08-26: reverting `mcp_query_guard._run_hook` to
`[sys.executable, str(_hook_path())]` — the exact original :116 bug — while
leaving the resolver intact scored 1.000 with the check green, because the
check only asserted `prefix != [sys.executable]`, a fact about the resolver,
never about any argv a subprocess ran.)

So every helper in this repo that spawns a hook subprocess calls
`record_hook_invocation(argv)` immediately before `subprocess.run`, and
`check_runs_under_registered_interpreter` spawns one real invocation through
that helper and asserts the RECORDED argv's head equals the registered
prefix. Recording is a no-op (and costs nothing) outside a capture block.
Deleting the `record_hook_invocation` call doesn't dodge the check either —
a capture that records nothing is itself a hard failure.
"""
from __future__ import annotations

import contextlib
import json
import os
import secrets
import shlex
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Iterator, Mapping, NamedTuple, Optional, Sequence

from rubrics.base import CheckResult, repo_root


class HookNotRegisteredError(RuntimeError):
    """The hook has no resolvable registration in .claude/settings.json, or
    settings.json's shape doesn't match what this parser understands.
    Deliberately a hard error, never caught internally to fall back to
    sys.executable or any other default interpreter."""


def _settings_path() -> Path:
    return repo_root() / ".claude" / "settings.json"


def _iter_hook_commands(settings: dict, settings_file: Path) -> Iterator[str]:
    """Yield every registered command-hook 'command' string, regardless of
    which event (SessionStart/PreToolUse/Stop/...) or matcher it sits
    under. Raises HookNotRegisteredError the moment the shape stops
    matching what this parser understands, rather than silently skipping
    a section it can't read."""
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        raise HookNotRegisteredError(
            f"{settings_file} has no top-level 'hooks' object — settings.json shape changed"
        )
    for event_name, matchers in hooks.items():
        if not isinstance(matchers, list):
            raise HookNotRegisteredError(
                f"{settings_file}: hooks[{event_name!r}] is not a list — settings.json shape changed"
            )
        for matcher_entry in matchers:
            if not isinstance(matcher_entry, dict):
                raise HookNotRegisteredError(
                    f"{settings_file}: hooks[{event_name!r}] contains a non-object "
                    f"matcher entry — settings.json shape changed"
                )
            entries = matcher_entry.get("hooks")
            if not isinstance(entries, list):
                raise HookNotRegisteredError(
                    f"{settings_file}: hooks[{event_name!r}] matcher entry has no "
                    f"'hooks' list — settings.json shape changed"
                )
            for entry in entries:
                if not isinstance(entry, dict) or entry.get("type") != "command":
                    continue
                command = entry.get("command")
                if not isinstance(command, str) or not command.strip():
                    raise HookNotRegisteredError(
                        f"{settings_file}: hooks[{event_name!r}] has a command-type "
                        f"hook entry with no usable 'command' string — settings.json "
                        f"shape changed"
                    )
                yield command


def registered_interpreter(hook_path: Path) -> list[str]:
    """Return the exact argv PREFIX `.claude/settings.json` registers for
    `hook_path` — the interpreter Claude Code actually invokes that hook
    with, in THIS checkout. See module docstring for the return shape and
    examples.

    `hook_path` may be absolute or repo-root-relative (e.g.
    `Path(".claude/hooks/mcp-query-guard.py")`); it is matched against
    registrations by resolved absolute path, so either form works.

    Raises HookNotRegisteredError if the hook isn't registered, or if
    settings.json is missing, unparsable, or shaped in a way this parser
    doesn't understand. Never falls back to sys.executable.
    """
    root = repo_root()
    hook_path = Path(hook_path)
    target = (hook_path if hook_path.is_absolute() else (root / hook_path)).resolve()

    settings_file = _settings_path()
    if not settings_file.is_file():
        raise HookNotRegisteredError(f"{settings_file} not found")
    try:
        raw = settings_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise HookNotRegisteredError(f"could not read {settings_file}: {exc}") from exc
    try:
        settings = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HookNotRegisteredError(f"{settings_file} is not valid JSON: {exc}") from exc
    if not isinstance(settings, dict):
        raise HookNotRegisteredError(f"{settings_file} top level is not a JSON object")

    for command in _iter_hook_commands(settings, settings_file):
        expanded = command.replace("$CLAUDE_PROJECT_DIR", str(root)).replace(
            "${CLAUDE_PROJECT_DIR}", str(root)
        )
        try:
            tokens = shlex.split(expanded)
        except ValueError as exc:
            raise HookNotRegisteredError(
                f"{settings_file}: could not tokenize registered command {command!r}: {exc}"
            ) from exc
        if not tokens:
            continue
        try:
            last_resolved = Path(tokens[-1]).resolve()
        except OSError:
            continue
        if last_resolved == target:
            return tokens[:-1]

    raise HookNotRegisteredError(
        f"{hook_path} ({target}) has no registration in {settings_file} — cannot "
        f"determine the interpreter Claude Code actually invokes it with"
    )


_CAPTURED: list[list[str]] | None = None


def record_hook_invocation(argv: Sequence[str]) -> None:
    """Record the argv a hook-spawning helper is about to hand to
    `subprocess.run`. EVERY such helper in this repo must call this on the
    line immediately before it spawns — that recording is the only thing
    that lets `check_runs_under_registered_interpreter` observe the REAL
    invocation instead of a property of `registered_interpreter()`'s
    return value (see module docstring).

    A no-op outside `capture_hook_invocations()`, so ordinary check runs
    pay nothing for it.
    """
    if _CAPTURED is not None:
        _CAPTURED.append([str(a) for a in argv])


@contextlib.contextmanager
def capture_hook_invocations() -> Iterator[list[list[str]]]:
    """Collect every `record_hook_invocation()` argv spawned inside the
    block. Restores the previous collector on exit, so nesting is safe."""
    global _CAPTURED
    previous = _CAPTURED
    collected: list[list[str]] = []
    _CAPTURED = collected
    try:
        yield collected
    finally:
        _CAPTURED = previous


def check_runs_under_registered_interpreter(
    hook_path: Path, *, spawn: Callable[[], object], hook_label: str | None = None
) -> CheckResult:
    """Shared check for any rubric row whose subject is a PYTHON hook
    invoked as a subprocess: `hook_path` must resolve to a real
    `.claude/settings.json` registration, and the rubric's own subprocess
    helper must ACTUALLY SPAWN under that registered interpreter — never a
    silent fallback to `sys.executable` (the exact drift #192/backlog :116
    exists to kill: the gate ran hooks under 3.11/venv-3.1x while
    consultants run bare `python3`, 3.9.6 on most machines).

    Python-hook-specific, not fully subject-agnostic: an empty registered
    prefix (a shell hook invoked directly via its own shebang, e.g.
    `auto-branch.sh`) is a legitimate `registered_interpreter()` return
    value but a hard failure HERE, because a Python hook must be registered
    with an explicit interpreter. A future shell-hook row needs its own
    check, not this one. Everything else is caller-supplied: each caller
    passes its own `hook_path` (e.g. `.claude/hooks/mcp-query-guard.py`,
    `.claude/hooks/anonymize-guard.py`) and its own `spawn`.

    `spawn` must be a zero-argument callable that performs ONE real
    invocation of `hook_path` through the rubric's own production
    subprocess helper (`_run_hook`, `_run_anonymize_guard`, ...) — not a
    bespoke `subprocess.run` written for this check, which would observe
    nothing about the code paths every other check on the row uses. Its
    return value and the hook's decision are ignored; only the argv the
    helper recorded matters. Give it whatever throwaway fixture root and
    payload are cheapest.

    Fails (hard_fail, red) rather than raising if the hook has no
    registration, if `spawn` raises, or if `spawn` records no invocation —
    HookNotRegisteredError is caught here and reported as a named check
    failure, not a rubric-crashing exception; every OTHER caller of
    `registered_interpreter()` in this codebase (the actual
    subprocess-invoking helpers) is expected to let it propagate.
    """
    name = "runs_under_registered_interpreter"
    label = hook_label or hook_path.name

    def fail(detail: str) -> CheckResult:
        return CheckResult(name, 0.0, False, hard_fail=True, detail=f"{label}: {detail}")

    try:
        prefix = registered_interpreter(hook_path)
    except HookNotRegisteredError as exc:
        return fail(str(exc))

    if not prefix:
        return fail(
            "registered_interpreter() returned an empty interpreter prefix — a "
            "Python hook must be registered with an explicit interpreter (bare "
            "'python3' or a resolver wrapper), not invoked directly via its own "
            "shebang"
        )

    # Assertion 1 (about the RESOLVER): it must not have fallen back to
    # sys.executable — CI's 3.11 / the local venv interpreter — instead of
    # the interpreter settings.json actually registers (bare 'python3').
    # These are essentially never equal in a real checkout: 'python3' is a
    # bare PATH-resolved word, sys.executable an absolute interpreter path.
    # Bites the mutation `registered_interpreter() -> [sys.executable]`.
    if prefix == [sys.executable]:
        return fail(
            f"registered_interpreter() returned the eval-runner's own "
            f"sys.executable ({sys.executable!r}) — that is the silent fallback "
            f"#192 exists to close, not a real settings.json registration"
        )

    # Assertion 2 (about the REAL INVOCATION): spawn once through the
    # rubric's own production helper and inspect the argv it actually
    # handed to subprocess.run. Assertion 1 cannot see this — the
    # spec-review FAIL reverted the call site to [sys.executable, hook]
    # with the resolver untouched and this row still scored 1.000. Bites
    # the mutation `_run_hook argv -> [sys.executable, ...]`.
    try:
        with capture_hook_invocations() as recorded:
            spawn()
    except Exception as exc:  # noqa: BLE001 - report, never crash the rubric
        return fail(f"spawn() raised {type(exc).__name__}: {exc}")

    if not recorded:
        return fail(
            "spawn() recorded no hook invocation — the rubric's subprocess helper "
            "must call rubrics._harness.record_hook_invocation(argv) immediately "
            "before subprocess.run, otherwise nothing observes which interpreter "
            "the hook is really spawned under"
        )

    target = (hook_path if hook_path.is_absolute() else (repo_root() / hook_path)).resolve()
    for argv in recorded:
        if list(argv[: len(prefix)]) != list(prefix):
            return fail(
                f"the helper spawned {argv!r}, whose interpreter prefix is NOT the "
                f"registered {prefix!r} — the hook is being certified under an "
                f"interpreter no consultant session invokes it with"
            )
        if not any(_resolves_to(tok, target) for tok in argv[len(prefix):]):
            return fail(
                f"the helper spawned {argv!r}, which does not name {target} after "
                f"its interpreter prefix — this check observed an invocation of "
                f"something other than the hook under test"
            )

    return CheckResult(name, 1.0, True, hard_fail=True, detail=(
        f"{label}: registered interpreter argv prefix = {prefix!r}; "
        f"eval-runner's sys.executable = {sys.executable!r}; "
        f"actually spawned by the rubric's own helper = {recorded[0]!r}"
    ))


def _resolves_to(token: str, target: Path) -> bool:
    try:
        return Path(token).resolve() == target
    except OSError:
        return False


# ---------------------------------------------------------------------------
# CheckResult helpers
# ---------------------------------------------------------------------------

def bool_check(name: str, ok: bool, *, detail: str = "", hard_fail: bool = True) -> CheckResult:
    """The pass/fail CheckResult both migrated rubrics had their own identical
    copy of. 1.0/0.0, `hard_fail` by default because every row built on this
    kit is a privacy or governance control at threshold 1.00 — a partially
    correct security gate is a failed one."""
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=hard_fail, detail=detail)


def run_in_tmpdir(fn: Callable[..., CheckResult], *args, prefix: str = "cortex_eval_") -> CheckResult:
    """Run a check body inside a fresh tempdir, passing that directory as its
    first argument, and convert ANY unexpected exception (subprocess timeout,
    missing interpreter, a fixture-integrity AssertionError, ...) into a
    FAILING CheckResult rather than letting it crash the whole eval run.

    The check name is derived from `fn.__name__` with leading underscores
    stripped, so a raising check still reports under the name the registry
    declares for it — otherwise `declared_checks_all_executed` (#182) would
    fail with a second, less informative error on top of the first.
    """
    try:
        with tempfile.TemporaryDirectory(prefix=prefix) as td:
            return fn(Path(td), *args)
    except Exception as exc:  # noqa: BLE001 - convert to a reportable failure
        return bool_check(fn.__name__.lstrip("_"), False,
                          detail=f"check raised {type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# Hook subprocesses
# ---------------------------------------------------------------------------

DEFAULT_HOOK_TIMEOUT_S = 15.0


def pretooluse_payload(tool_name: str, tool_input: dict) -> bytes:
    """The stdin bytes Claude Code hands a PreToolUse hook."""
    return json.dumps({"tool_name": tool_name, "tool_input": tool_input}).encode("utf-8")


class HookRun(NamedTuple):
    """What one hook invocation produced.

    Deliberately a superset of the `(rc, stdout_json)` pair #196's ticket
    names: the migrated rows assert on RAW stdout ("an allow writes nothing at
    all", which `stdout_json is None` cannot distinguish from "wrote
    unparsable bytes") and on STDERR (`mcp-query-guard`'s
    "no client deny-list configured" warning). Dropping either would have
    silently weakened two existing checks, which #196 forbids.
    """

    returncode: int
    stdout_json: Optional[dict]
    stdout: bytes
    stderr: bytes
    argv: list

    @property
    def stdout_text(self) -> str:
        return self.stdout.decode("utf-8", errors="replace")

    @property
    def stderr_text(self) -> str:
        return self.stderr.decode("utf-8", errors="replace")

    @property
    def hook_output(self) -> dict:
        block = (self.stdout_json or {}).get("hookSpecificOutput")
        return block if isinstance(block, dict) else {}

    @property
    def decision(self) -> Optional[str]:
        return self.hook_output.get("permissionDecision")

    @property
    def denied(self) -> bool:
        return self.decision == "deny"

    @property
    def reason(self) -> str:
        value = self.hook_output.get("permissionDecisionReason", "")
        return value if isinstance(value, str) else ""

    @property
    def silent(self) -> bool:
        """Wrote NOTHING on stdout — how a PreToolUse hook expresses "no
        opinion, allow". Distinct from `not denied`, which is also true of a
        hook that wrote an explicit `"allow"` or wrote garbage."""
        return not self.stdout.strip()


def run_hook_subprocess(
    hook_path: Path,
    payload: bytes,
    *,
    project_dir: Path,
    timeout: float = DEFAULT_HOOK_TIMEOUT_S,
) -> HookRun:
    """Invoke a real hook SCRIPT as a subprocess, exactly as Claude Code does:
    JSON payload on stdin, `CLAUDE_PROJECT_DIR` pointing at the fixture root,
    decision read back from stdout + exit code.

    Never import-and-monkeypatch the hook module instead. The contract under
    test is the PROCESS one — stdout JSON shape and exit code — and an
    in-process call proves only that some Python functions behave.

    The interpreter is whatever `.claude/settings.json` actually registers for
    this hook (`registered_interpreter()`), NOT `sys.executable`. Every hook
    here is registered as bare `python3`, the interpreter every consultant
    session runs it under (3.9.6 on most machines); building the argv from
    `sys.executable` would certify it under CI's 3.11 or the local venv
    instead — the exact drift #192/backlog :116 exists to close.
    `registered_interpreter()` raises loudly rather than falling back.

    `record_hook_invocation(argv)` below is load-bearing, not telemetry: it is
    the ONLY thing that lets `check_runs_under_registered_interpreter` assert
    against the argv this function REALLY spawned rather than against the
    resolver's return value. Reverting the argv line to `[sys.executable, ...]`
    with the resolver left intact scored 1.000 green once already (spec-review
    FAIL, 2026-08-26). Never spawn a hook here without recording first.
    """
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    argv = registered_interpreter(hook_path) + [str(hook_path)]
    record_hook_invocation(argv)
    completed = subprocess.run(
        argv,
        input=payload,
        capture_output=True,
        timeout=timeout,
        env=env,
    )
    out = completed.stdout.decode("utf-8", errors="replace").strip()
    parsed: Optional[dict] = None
    if out:
        try:
            loaded = json.loads(out)
        except json.JSONDecodeError:
            loaded = None
        parsed = loaded if isinstance(loaded, dict) else None
    return HookRun(completed.returncode, parsed, completed.stdout, completed.stderr, argv)


# ---------------------------------------------------------------------------
# Fixture engagements
# ---------------------------------------------------------------------------

DEFAULT_CLIENT_SLUG = "zzzplaceholderclient"
DEFAULT_CLIENT_NAME = "Zzzplaceholder Meridian Holdings"
DEFAULT_CLIENT_SHORT = "Meridian"
DEFAULT_ENGAGEMENT = "2026-01_test_engagement"

# House rule, enforced by synthetic-knowledge-guard.py and the repo's
# synthetic-quarantine programme: fixtures use obviously-placeholder tokens,
# NEVER a fictional bank name (those get mistaken for real engagements and
# cited back). Everything defaulted above is a `zzz`-prefixed non-word.


class FixtureEngagement(NamedTuple):
    """A synthetic engagement tree, and the two deny lists it can produce.

    `.client_deny_terms()` and `.resolved_deny_terms()` are NOT
    interchangeable — see the module docstring's "#209" section before
    choosing. Both are methods, not fields, so the resolved one stays lazy:
    `mcp_query_guard`'s row never resolves a deny-list in-process (its hook
    does that itself, inside the subprocess) and must not pay for
    `pii.denylist`'s import.
    """

    project_dir: Path      # what CLAUDE_PROJECT_DIR points at
    client_dir: Path       # engagements/<slug>/
    engagement_dir: Optional[Path]
    inputs_dir: Optional[Path]
    client_name: Optional[str]
    short_name: Optional[str]
    stakeholder: Optional[str]

    def client_deny_terms(self) -> list:
        """The client identity ONLY — the narrow list. Correct for any check
        whose subject is something OTHER than deny-list coverage."""
        return [t for t in (self.client_name, self.short_name) if t]

    def resolved_deny_terms(self, *, must_contain: Optional[Sequence[str]] = None) -> list:
        """What PRODUCTION resolves for this engagement — client identity plus
        the stakeholder names `denylist.extract_stakeholder_terms` mines from
        the seeded documents.

        Deliberately not a literal list: `resolve_engagement_deny_list` is the
        function `orchestrate.py` and `anonymize_transcript.py` call, so going
        through it is what makes "the stakeholder name is redacted" a statement
        about the SHIPPED extraction rather than about a rubric's own constant.
        Hard-coding the terms would close the assertion without closing the
        leak, and would survive a revert of the extraction untouched.

        Runs `assert_deny_list_non_empty` before returning — that is the whole
        point of routing through here rather than calling the resolver
        directly, so no caller can obtain terms that were never checked for
        vacuity. Defaults `must_contain` to the fixture's own client name and
        stakeholder.
        """
        if self.engagement_dir is None:
            raise AssertionError(
                "resolved_deny_terms() needs an engagement directory; this "
                "fixture was built with engagement=None"
            )
        scripts_dir = repo_root() / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from pii import denylist  # noqa: PLC0415 - stdlib only, and lazy on purpose

        terms = sorted(denylist.resolve_engagement_deny_list(self.engagement_dir))
        required = (must_contain if must_contain is not None
                    else [t for t in (self.client_name, self.stakeholder) if t])
        return assert_deny_list_non_empty(terms, must_contain=required,
                                          context=str(self.engagement_dir))


def assert_deny_list_non_empty(
    terms: Sequence[str], *, must_contain: Sequence[str] = (), context: str = "",
) -> list:
    """Raise unless `terms` is non-empty AND carries every value in
    `must_contain` (case-insensitively — `resolve_engagement_deny_list`
    normalises case, and the callers that matched case-insensitively before
    this extraction must keep doing so).

    THE ONLY REASON THIS EXISTS: an empty or identity-less deny-list makes
    every downstream assertion — "no client identifier in any path segment",
    "no raw PII in the anonymised output" — pass VACUOUSLY. This repo has
    twice shipped a gate scoring 1.000 while certifying nothing that way
    (#166). Raising is deliberate: `run_in_tmpdir` / `evaluate`'s wrapper turn
    it into a RED check naming the fixture, which is louder than a
    silently-true assertion and impossible to forget to call, because the only
    supported way to get a resolved deny-list out of a fixture goes through
    here.

    Returns `terms` so it can be used inline: `terms = assert_...(terms)`.
    """
    where = f" for {context}" if context else ""
    if not terms:
        raise AssertionError(
            f"deny-list resolved{where} is EMPTY — every assertion built on it "
            f"would pass vacuously; the fixture is broken, not the subject"
        )
    lowered = {t.lower() for t in terms}
    missing = [t for t in must_contain if t and t.lower() not in lowered]
    if missing:
        raise AssertionError(
            f"deny-list resolved{where} is missing {missing!r} (resolved: "
            f"{list(terms)!r}) — every assertion built on it would pass or fail "
            f"for the wrong reason"
        )
    return list(terms)


def opaque_engagement_id() -> str:
    """A random, client-free directory name in the shape `init_engagement.sh`
    mints post-#168 (solution-design-v6 D6: `compose_prompt` renders
    `engagement_dir` into every agent prompt, so a client-named directory
    leaks the client on every call).

    `build_fixture_engagement(slug=None)` uses this. No row today asks for it
    — `pii_anonymizer`'s workspace check deliberately seeds the PRE-migration,
    CLIENT-NAMED shape, because a fixture that arrived already neutral could
    not tell a working neutraliser from a broken one. It is here for the
    identity/migration rows (#199) whose subject IS the opaque id.
    """
    return "e" + secrets.token_hex(6)


def default_client_profile_text(
    client_name: str, *, short_name: Optional[str] = None, stakeholder: Optional[str] = None,
) -> str:
    """`templates/client_profile.md`'s real shape — a bare `- **Name:**` field
    under `## Client Identity`, NOT `- **Client Name:**` (finding 6: the two
    are different label paths and the deny-list extractor has to handle both).

    A caller whose fixture's whole point is a DIFFERENT document shape —
    ALL-CAPS prose emphasis outside a label line, a label value made entirely
    of stoplist words, an unfilled `[Full legal name]` template — passes its
    own `profile_text=` instead. Those shapes are the subject of their checks
    and must not be generated.
    """
    text = (
        "# Client Profile\n\n"
        "## Client Identity\n\n"
        f"- **Name:** {client_name}\n"
    )
    if short_name:
        text += f"- **Short Name:** {short_name}\n"
    if stakeholder:
        text += (
            "\n## Relationship Context\n\n"
            "- **Backbase Relationship:** Prospect\n"
            "- **Executive Sponsors (Client-Side):**\n"
            f"  - {stakeholder} — Chief Financial Officer — prefers written briefs\n"
        )
    return text


def build_fixture_engagement(
    project_dir: Path,
    *,
    slug: Optional[str] = DEFAULT_CLIENT_SLUG,
    client_name: Optional[str] = DEFAULT_CLIENT_NAME,
    short_name: Optional[str] = DEFAULT_CLIENT_SHORT,
    stakeholder: Optional[str] = None,
    engagement: Optional[str] = DEFAULT_ENGAGEMENT,
    profile_text: Optional[str] = None,
    documents: Optional[Mapping[str, str]] = None,
    subdirs: Sequence[str] = (),
) -> FixtureEngagement:
    """Write a synthetic engagement tree under `project_dir` and return a
    handle to it. `project_dir` is what `CLAUDE_PROJECT_DIR` points at; it is
    always a caller-owned tempdir. NOTHING here ever touches `engagements/` in
    the real checkout — that tree is real, gitignored client material.

      engagements/<slug>/CLIENT_PROFILE.md
      engagements/<slug>/<engagement>/inputs/
      engagements/<slug>/<engagement>/<documents keys...>

    Arguments:
      slug          client directory name. `None` mints an opaque id
                    (`opaque_engagement_id()`) — the post-#168 shape.
      client_name / short_name / stakeholder
                    the identity the fixture claims to carry. Drives the
                    generated profile, both deny lists, and the integrity
                    assertion below. `client_name=None` is legal ONLY for a
                    fixture whose point is that no identity is resolvable
                    (an unfilled template) — it disables the assertion, so
                    do not reach for it to silence a failure.
      engagement    per-engagement subdirectory name, or `None` for a
                    client-level-only fixture (CLIENT_PROFILE.md alone).
      profile_text  full CLIENT_PROFILE.md bytes. Defaults to
                    `default_client_profile_text(...)`. Pass explicitly when
                    the document's SHAPE is the subject of the check.
      documents     {path relative to the engagement dir: text} — e.g.
                    `{"ENGAGEMENT_CONTEXT.md": ..., "inputs/x.md": ...}`.
                    Parent directories are created.
      subdirs       extra empty directories to create under the engagement
                    (e.g. `("outputs",)`).

    FIXTURE-INTEGRITY ASSERTION: unless `client_name` is None, the declared
    client identity must actually appear SOMEWHERE in the tree just written —
    the slug, the profile, or a document. A fixture that claims an identity it
    never wrote is the vacuous-gate failure mode one step earlier than an
    empty deny-list, and it is cheaper to catch here than to debug as a
    mysteriously-green privacy check.
    """
    slug = slug or opaque_engagement_id()
    client_dir = project_dir / "engagements" / slug
    client_dir.mkdir(parents=True, exist_ok=True)

    if profile_text is None:
        if client_name is None:
            raise AssertionError(
                "build_fixture_engagement needs either a client_name to generate "
                "CLIENT_PROFILE.md from, or an explicit profile_text"
            )
        profile_text = default_client_profile_text(
            client_name, short_name=short_name, stakeholder=stakeholder)
    (client_dir / "CLIENT_PROFILE.md").write_text(profile_text, encoding="utf-8")

    engagement_dir: Optional[Path] = None
    inputs_dir: Optional[Path] = None
    written: list = []
    if engagement is not None:
        engagement_dir = client_dir / engagement
        engagement_dir.mkdir(parents=True, exist_ok=True)
        inputs_dir = engagement_dir / "inputs"
        inputs_dir.mkdir(parents=True, exist_ok=True)
        for name in subdirs:
            (engagement_dir / name).mkdir(parents=True, exist_ok=True)
        for rel, text in (documents or {}).items():
            path = engagement_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written.append(text)
    elif documents:
        raise AssertionError(
            "build_fixture_engagement was given documents but engagement=None — "
            "there is no engagement directory to write them under"
        )

    if client_name is not None:
        haystack = [slug, profile_text] + written
        if not any(client_name.lower() in blob.lower() for blob in haystack):
            raise AssertionError(
                f"fixture claims client_name={client_name!r} but that identity "
                f"appears nowhere in the tree it wrote (slug={slug!r}, profile, "
                f"{len(written)} document(s)) — every deny-list assertion built "
                f"on this fixture would be measuring the wrong thing"
            )

    return FixtureEngagement(project_dir, client_dir, engagement_dir, inputs_dir,
                             client_name, short_name, stakeholder)


# ---------------------------------------------------------------------------
# Permission-fault injection
# ---------------------------------------------------------------------------

def fault_injection_skip(name: str, *, perms: str = "directory") -> Optional[CheckResult]:
    """A SKIP CheckResult when running as root, else None.

    Root bypasses permission bits entirely, so a `chmod 000` fault injects
    nothing and the subject sails through — which would be a FALSE PASS, not a
    pass. Skipping is the honest outcome; the check must call this before it
    builds anything, and act on a non-None return by returning it.
    """
    if hasattr(os, "getuid") and os.getuid() == 0:
        return CheckResult(name, 1.0, True, skipped=True,
                           detail=f"running as root — chmod-based permission fault injection "
                                  f"cannot be exercised (root bypasses {perms} perms); skipping "
                                  f"rather than reporting a false pass or fail")
    return None


@contextlib.contextmanager
def inject_fault(*paths: Path, kind: str = "unreadable") -> Iterator[tuple]:
    """Make every path in `paths` provoke a REAL, unmocked OS error for the
    duration of the block, then restore it unconditionally on exit.

    `kind="unreadable"` — `chmod 000`, so any `stat()`/`open()`/`iterdir()`
    the subject performs raises `PermissionError`. That is the whole current
    vocabulary; a row that needs another fault adds a named kind here rather
    than hand-rolling one, and an unknown kind is an error, never a silent
    no-op.

    VARIADIC ON PURPOSE. `pii_anonymizer`'s `guard_fails_closed_on_inputs_path`
    faults `inputs/` AND a control directory OUTSIDE `engagements/` in one
    block, because the contract it proves is a SPLIT — the identical fault
    must DENY inside raw client material and ALLOW outside it. A guard that is
    globally fail-closed wedged every session once already (PR #82), and a
    single-path API would have quietly reduced that check to "denial happens
    somewhere".

    RESTORATION is in a `finally` and is not optional: a 000 directory cannot
    be listed or removed, so `TemporaryDirectory` cleanup would raise on the
    way out and turn a passing check into a crashing one. Directories get
    `S_IRWXU` back, files `S_IRUSR|S_IWUSR`, both OR-ed onto the mode observed
    before the fault.

    Callers must have already returned `fault_injection_skip(...)` if running
    as root; this function does not silently no-op there, because a fault that
    quietly does nothing is exactly the false pass that skip exists to avoid.
    """
    if kind != "unreadable":
        raise ValueError(
            f"inject_fault: unknown fault kind {kind!r} (known: 'unreadable'). "
            f"Add a named kind here rather than hand-rolling one in a rubric."
        )
    original: list = []
    try:
        for path in paths:
            mode = path.stat().st_mode
            original.append((path, mode, path.is_dir()))
            path.chmod(0o000)
        yield tuple(p for p, _, _ in original)
    finally:
        for path, mode, is_dir in original:
            restore = stat.S_IRWXU if is_dir else (stat.S_IRUSR | stat.S_IWUSR)
            try:
                path.chmod(mode | restore)
            except OSError:  # pragma: no cover - best effort; tempdir cleanup reports
                pass
