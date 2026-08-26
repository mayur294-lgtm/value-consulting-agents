"""Shared harness kit for rubrics that invoke a `.claude/hooks/*` script as a
subprocess (ticket #192, backlog :116 — this is the seed #196 grows into the
full kit: build_fixture_engagement, run_hook_subprocess, inject_fault. Only
`registered_interpreter()` and the `runs_under_registered_interpreter` check
are built here; do not add the rest ahead of #196).

THE BUG THIS CLOSES
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
"""
from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Iterator

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


def check_runs_under_registered_interpreter(
    hook_path: Path, *, hook_label: str | None = None
) -> CheckResult:
    """Shared, subject-agnostic check: `hook_path` must resolve to a real
    `.claude/settings.json` registration, and the interpreter this rubric
    resolves for it must be the ACTUAL registered one — never a silent
    fallback to `sys.executable` (the exact drift #192/backlog :116 exists
    to kill: the gate ran hooks under 3.11/venv-3.1x while consultants run
    bare `python3`, 3.9.6 on most machines).

    Reusable across every hook-invoking rubric row: each caller passes its
    own `hook_path` (e.g. `.claude/hooks/mcp-query-guard.py`,
    `.claude/hooks/anonymize-guard.py`) — this function's logic is entirely
    subject-agnostic.

    Fails (hard_fail, red) rather than raising if the hook has no
    registration — HookNotRegisteredError is caught here and reported as a
    named check failure, not a rubric-crashing exception; every OTHER
    caller of `registered_interpreter()` in this codebase (the actual
    subprocess-invoking helpers) is expected to let it propagate.
    """
    name = "runs_under_registered_interpreter"
    label = hook_label or hook_path.name
    try:
        prefix = registered_interpreter(hook_path)
    except HookNotRegisteredError as exc:
        return CheckResult(name, 0.0, False, hard_fail=True, detail=f"{label}: {exc}")

    if not prefix:
        return CheckResult(
            name, 0.0, False, hard_fail=True,
            detail=f"{label}: registered_interpreter() returned an empty interpreter "
                   f"prefix — a Python hook must be registered with an explicit "
                   f"interpreter (bare 'python3' or a resolver wrapper), not invoked "
                   f"directly via its own shebang",
        )

    # The regression this whole ticket exists to prevent: a silent fallback
    # to sys.executable (CI's 3.11 / the local venv interpreter) instead of
    # the interpreter settings.json actually registers (bare 'python3').
    # These are essentially never equal in a real checkout — 'python3' is a
    # bare PATH-resolved word, sys.executable an absolute interpreter path
    # — so this also functions as the mutation-bite assertion: mutate
    # registered_interpreter() to return [sys.executable] and this goes red.
    ok = prefix != [sys.executable]
    detail = (
        f"{label}: registered interpreter argv prefix = {prefix!r}; "
        f"eval-runner's sys.executable = {sys.executable!r}"
    )
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=True, detail=detail)
