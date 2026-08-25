"""mcp-query-guard component evaluator — deterministic regression coverage
for `.claude/hooks/mcp-query-guard.py` (PR #171 hardening cycle, ticket #155
follow-up; a broader `pii-anonymizer` row may fold this in under #161).

`.claude/hooks/mcp-query-guard.py` is the PreToolUse(mcp__.*) hook that blocks
outbound Backbase Infobank MCP queries containing a client/stakeholder
identifier (security_protocol.md §5). It is deliberately FAIL-CLOSED — the
opposite default of every other hook in the directory — because it gates an
outbound call to a third-party server, not a local read. That fail-closed
property is the entire point of the hook: before this file, nothing proved it
actually holds, so a future edit could silently flip it to fail-open and
nothing would notice.

Every check here invokes the REAL hook script as a subprocess, piping a
synthesized PreToolUse payload to its stdin exactly as Claude Code would — no
importing the module and monkeypatching its internals. This is the only way
to prove the process-level contract (stdout JSON shape, exit code) actually
holds, not just that the Python functions behave in-process.

Fixtures are synthesized entirely inside a `tempfile.TemporaryDirectory()` and
pointed to via the `CLAUDE_PROJECT_DIR` env var the hook reads its
`engagements/` deny-list root from (see `PROJECT_DIR` in the hook). Nothing is
ever written inside the repo, and no real `engagements/**` data (gitignored
client PII) is read. Per the repo's active synthetic-quarantine programme, no
fixture uses a fictional bank name — an obviously-placeholder token
(`zzzplaceholderclient`) stands in for "a client identifier" instead.

threshold: 1.00 in the registry (see registry.yaml comment) — a privacy
control is pass/fail, not "mostly correct." No `judge:` entries — every check
here is deterministic and free.
"""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from rubrics.base import CheckResult, repo_root

HOOK_REL_PATH = Path(".claude") / "hooks" / "mcp-query-guard.py"

# Obviously-placeholder token standing in for "a client identifier" in test
# fixtures — NOT a fictional bank name (the repo's synthetic-quarantine
# programme treats those as contamination; see synthetic-knowledge-guard.py).
PLACEHOLDER_CLIENT = "zzzplaceholderclient"

SUBPROCESS_TIMEOUT_S = 15.0


def _hook_path() -> Path:
    return repo_root() / HOOK_REL_PATH


def _payload(tool_input: dict) -> bytes:
    return json.dumps({
        "tool_name": "mcp__backbase-infobank__search",
        "tool_input": tool_input,
    }).encode("utf-8")


def _run_hook(project_dir: Path, stdin_bytes: bytes) -> subprocess.CompletedProcess:
    """Invoke the real hook script as a subprocess, exactly as Claude Code
    does: JSON payload on stdin, CLAUDE_PROJECT_DIR pointing at the fixture
    root, decision read back from stdout/exit code."""
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    return subprocess.run(
        [sys.executable, str(_hook_path())],
        input=stdin_bytes,
        capture_output=True,
        timeout=SUBPROCESS_TIMEOUT_S,
        env=env,
    )


def _parsed_stdout(result: subprocess.CompletedProcess) -> Optional[dict]:
    out = result.stdout.decode("utf-8", errors="replace").strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def _is_deny(result: subprocess.CompletedProcess) -> tuple[bool, Optional[dict]]:
    parsed = _parsed_stdout(result)
    if parsed is None:
        return False, None
    decision = (parsed.get("hookSpecificOutput") or {}).get("permissionDecision")
    return decision == "deny", parsed


def _bool_check(name: str, ok: bool, *, detail: str = "", hard_fail: bool = True) -> CheckResult:
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=hard_fail, detail=detail)


def _seed_denylist_project(root: Path) -> Path:
    """A fixture project root with exactly one engagement, whose slug and
    CLIENT_PROFILE.md both carry PLACEHOLDER_CLIENT as an identifier term —
    mirrors how _resolve_deny_list() aggregates real engagements/**."""
    client_dir = root / "engagements" / PLACEHOLDER_CLIENT
    client_dir.mkdir(parents=True)
    (client_dir / "CLIENT_PROFILE.md").write_text(
        f"# {PLACEHOLDER_CLIENT}\n\nClient: {PLACEHOLDER_CLIENT}\n",
        encoding="utf-8",
    )
    return client_dir


def _run_in_tmp(fn, *args) -> CheckResult:
    """Run a check body inside a fresh tempdir, converting any unexpected
    exception (subprocess timeout, missing interpreter, ...) into a failing
    CheckResult instead of crashing the whole eval run."""
    try:
        with tempfile.TemporaryDirectory(prefix="mcp_guard_eval_") as td:
            return fn(Path(td), *args)
    except Exception as exc:  # noqa: BLE001 - convert to a reportable failure
        return _bool_check(fn.__name__.lstrip("_"), False,
                            detail=f"check raised {type(exc).__name__}: {exc}")


# --- individual checks ------------------------------------------------------

def _denies_query_containing_client_identifier(root: Path) -> CheckResult:
    name = "denies_query_containing_client_identifier"
    _seed_denylist_project(root)
    payload = _payload({"query": f"capabilities for {PLACEHOLDER_CLIENT} digital onboarding"})
    result = _run_hook(root, payload)
    denied, parsed = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r} "
        f"stderr={result.stderr.decode(errors='replace')[:200]!r}"
    ))


def _allows_generic_query(root: Path) -> CheckResult:
    name = "allows_generic_query"
    _seed_denylist_project(root)
    payload = _payload({"query": "digital onboarding capabilities for a Tier-2 retail bank"})
    result = _run_hook(root, payload)
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and not denied and not result.stdout.strip()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} stdout={result.stdout.decode(errors='replace')[:200]!r}"
    ))


def _detects_identifier_nested_in_dict_or_list(root: Path) -> CheckResult:
    name = "detects_identifier_nested_in_dict_or_list"
    _seed_denylist_project(root)
    payload = _payload({
        "filters": {
            "tags": ["general", "onboarding", PLACEHOLDER_CLIENT],
            "meta": {"nested": {"note": "no identifier here"}},
        },
    })
    result = _run_hook(root, payload)
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} stdout={result.stdout.decode(errors='replace')[:200]!r}"
    ))


def _fails_closed_on_unresolvable_denylist(root: Path) -> CheckResult:
    """Force _resolve_deny_list() to raise (not just come back empty) by
    making engagements/ unreadable: PermissionError on os.iterdir() is a
    real, unmocked exception the hook's try/except must catch and turn into
    a deny — proving the fail-closed contract, not just asserting it."""
    name = "fails_closed_on_unresolvable_denylist"
    if hasattr(os, "getuid") and os.getuid() == 0:
        return CheckResult(name, 1.0, True, skipped=True,
                            detail="running as root — chmod-based permission fault injection "
                                   "cannot be exercised (root bypasses directory perms); skipping "
                                   "rather than reporting a false pass or fail")

    engagements_dir = root / "engagements"
    engagements_dir.mkdir(parents=True)
    (engagements_dir / "somefile.md").write_text("placeholder", encoding="utf-8")
    original_mode = engagements_dir.stat().st_mode
    try:
        engagements_dir.chmod(0o000)
        payload = _payload({"query": "digital onboarding capabilities"})
        result = _run_hook(root, payload)
    finally:
        # Restore perms unconditionally so tempdir cleanup (which needs to
        # list/remove engagements_dir) can proceed.
        engagements_dir.chmod(original_mode | stat.S_IRWXU)

    denied, parsed = _is_deny(result)
    reason = ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "")
    ok = result.returncode == 0 and denied and "could not verify" in reason.lower()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} reason={reason[:200]!r}"
    ))


def _fails_closed_on_malformed_payload(root: Path) -> CheckResult:
    name = "fails_closed_on_malformed_payload"
    _seed_denylist_project(root)
    result = _run_hook(root, b"this is not json { at all")
    denied, parsed = _is_deny(result)
    reason = ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "")
    ok = result.returncode == 0 and denied and "could not verify" in reason.lower()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} reason={reason[:200]!r}"
    ))


def _allows_with_warning_when_no_denylist_configured(root: Path) -> CheckResult:
    """No engagements/ directory at all -> _resolve_deny_list() returns an
    empty set with NO exception. This is 'nothing to check against', which
    must allow (with a stderr warning) — distinct from the fail-closed cases
    above, where resolution itself errors."""
    name = "allows_with_warning_when_no_denylist_configured"
    payload = _payload({"query": f"capabilities for {PLACEHOLDER_CLIENT} digital onboarding"})
    result = _run_hook(root, payload)
    denied, _ = _is_deny(result)
    stderr = result.stderr.decode("utf-8", errors="replace")
    ok = (
        result.returncode == 0
        and not denied
        and not result.stdout.strip()
        and "no client deny-list configured" in stderr.lower()
    )
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} stdout={result.stdout.decode(errors='replace')[:120]!r} "
        f"stderr={stderr[:200]!r}"
    ))


def _deny_decision_shape_matches_hook_contract(root: Path) -> CheckResult:
    """stdout JSON must carry hookSpecificOutput.permissionDecision == "deny"
    with exit 0 (never a non-zero exit) — the exact contract PreToolUse hooks
    are required to speak."""
    name = "deny_decision_shape_matches_hook_contract"
    _seed_denylist_project(root)
    payload = _payload({"query": f"info about {PLACEHOLDER_CLIENT}"})
    result = _run_hook(root, payload)
    parsed = _parsed_stdout(result)
    ok = (
        result.returncode == 0
        and parsed is not None
        and isinstance(parsed.get("hookSpecificOutput"), dict)
        and parsed["hookSpecificOutput"].get("hookEventName") == "PreToolUse"
        and parsed["hookSpecificOutput"].get("permissionDecision") == "deny"
        and isinstance(parsed["hookSpecificOutput"].get("permissionDecisionReason"), str)
        and parsed["hookSpecificOutput"]["permissionDecisionReason"] != ""
    )
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} parsed={json.dumps(parsed)[:300] if parsed else None}"
    ))


def evaluate(target: str) -> list[CheckResult]:  # noqa: ARG001 - self-contained, ignores target
    hook = _hook_path()
    if not hook.exists():
        missing = CheckResult(
            "hook_script_present", 0.0, False, hard_fail=True,
            detail=f"{hook} not found — cannot run any subprocess check",
        )
        return [missing]

    return [
        _run_in_tmp(_denies_query_containing_client_identifier),
        _run_in_tmp(_allows_generic_query),
        _run_in_tmp(_detects_identifier_nested_in_dict_or_list),
        _run_in_tmp(_fails_closed_on_unresolvable_denylist),
        _run_in_tmp(_fails_closed_on_malformed_payload),
        _run_in_tmp(_allows_with_warning_when_no_denylist_configured),
        _run_in_tmp(_deny_decision_shape_matches_hook_contract),
    ]
