"""`synthetic-knowledge-guard` component evaluator — the knowledge-base
contamination backstop.

SUBJECT: `.claude/hooks/synthetic-knowledge-guard.py`, the PreToolUse(Edit|Write)
hook that stops synthetic/fictional engagement material from landing in
`knowledge/`.

Why it matters: `knowledge/` is read by every downstream engagement (domain-*
retrievers, benchmark-librarian, …) and everything in it is treated as real,
citable ground truth. Synthetic fixtures live under `tests/engagements/`
precisely so they never mix. This hook is the content backstop behind that
convention, and it is the only enforcement the quarantine has that does not
depend on someone remembering it.

DELIBERATELY NARROW — AND THE CHECKS PIN THAT NARROWNESS
---------------------------------------------------------
Two content markers, one path prefix, and one asymmetry:

  `Harborlight`      anywhere under `knowledge/`     -> deny
  `[Synthetic-Test]` under `knowledge/domains/` ONLY -> deny
                     (legal under `knowledge/learnings/` and
                      `knowledge/standards/`, where it documents the tier
                      itself)

That asymmetry is the whole design, so it is checked from both sides:
`denies_synthetic_tag_under_knowledge_domains` and
`allows_synthetic_tag_outside_domains` are two checks, not one. Collapsing the
tag rule to "deny anywhere under knowledge/" would break the standards files
that describe the tier; dropping the domains scope entirely would let synthetic
benchmarks be read as real ones.

THE INPUT FIELD IS PART OF THE CONTRACT
----------------------------------------
Write carries its content in `tool_input.content`, Edit in
`tool_input.new_string`. Those are different fields, and reading only one is a
silent half-gate — so `inspects_edit_new_string_not_write_content` exists
specifically to cover the Edit field with a fixture the Write path cannot
satisfy.

RELATIVE vs ABSOLUTE PATHS ARE CHOSEN PER CHECK, ON PURPOSE
------------------------------------------------------------
The hook classifies a path by `_resolve` (relative -> PROJECT_DIR-relative) then
`_rel` (back to a repo-relative posix string, falling through to the absolute
path when it cannot). The content checks below pass RELATIVE paths, which behave
identically under any project root; `invoked_as_subprocess_not_import` passes an
ABSOLUTE one, which is exactly the case whose answer DEPENDS on the project root
— an in-scope `knowledge/` write under root A and an unrecognised absolute path
under root B. That split is what its mutation bites, and keeping the other
checks on relative paths keeps them out of its blast radius.

Fail-OPEN is this hook's contract ("a guard must never wedge the session"), so
the fault check is `fails_open_under_injected_fault`. threshold 1.00. No
`judge:` entries.
"""
from __future__ import annotations

import json
from pathlib import Path

from rubrics.base import CheckResult, repo_root
from rubrics._harness import (
    HookRun,
    check_runs_under_registered_interpreter,
    pretooluse_payload,
    run_hook_subprocess,
)
from rubrics.component.hooks._common import (
    HOOK_TIMEOUT_S,
    bool_check,
    check_invoked_as_subprocess_not_import,
    crashed,
    edit_payload,
    missing_hook_check,
    run_in_tmp,
    write_payload,
)

HOOK_REL_PATH = Path(".claude") / "hooks" / "synthetic-knowledge-guard.py"
TMP_PREFIX = "synthetic_knowledge_guard_row_"

# The two markers the hook looks for, written out here rather than imported
# from the hook: a rubric that read its expected values out of its subject
# would agree with any change the subject made to them.
FICTIONAL_NAME = "Harborlight"
SYNTHETIC_TAG = "[Synthetic-Test]"

FICTIONAL_BODY = (
    "# Retail onboarding learnings\n\n"
    f"During the {FICTIONAL_NAME} engagement, drop-off fell from 38% to 21%.\n"
)
TAGGED_BODY = (
    "# Retail benchmarks\n\n"
    f"{SYNTHETIC_TAG} median time-to-account 4.2 minutes.\n"
)
CLEAN_BODY = "# Retail benchmarks\n\nMedian time-to-account 4.2 minutes.\n"

DENY_BANNER = "Synthetic-knowledge guard"


def _hook_path() -> Path:
    """Resolved through `repo_root()` so the mutation harness reaches its SHADOW
    copy of the hook."""
    return repo_root() / HOOK_REL_PATH


def _run_hook(project_dir: Path, stdin_bytes: bytes) -> HookRun:
    """This row's ONE subprocess entry point."""
    return run_hook_subprocess(_hook_path(), stdin_bytes,
                               project_dir=project_dir, timeout=HOOK_TIMEOUT_S)


def _denied_text(result: HookRun) -> bool:
    """"The write was refused", asserted WITHOUT reading the decision envelope,
    so `deny_decision_shape_matches_hook_contract` stays the only check a change
    to that envelope reddens."""
    return result.returncode == 0 and DENY_BANNER in result.stdout_text


def _allowed(result: HookRun) -> bool:
    return result.returncode == 0 and result.silent and not crashed(result)


# --- the two markers -----------------------------------------------------------

def _denies_fictional_name_written_under_knowledge(root: Path) -> CheckResult:
    """`Harborlight` is the fictional bank used across the repo's synthetic
    fixtures and demos. As of the synthetic-quarantine cleanup no legitimate
    `knowledge/` file contains the word, so the check has zero standing
    false-positive surface — and a learnings file that mentions it is a
    synthetic engagement being written up as real."""
    name = "denies_fictional_name_written_under_knowledge"
    result = _run_hook(root, write_payload("knowledge/learnings/retail_onboarding.md",
                                           content=FICTIONAL_BODY))
    ok = (
        _denied_text(result)
        and FICTIONAL_NAME in result.stdout_text
        and "tests/engagements/README.md" in result.stdout_text
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} stdout={result.stdout_text[:220]!r}"))


def _denies_synthetic_tag_under_knowledge_domains(root: Path) -> CheckResult:
    """`knowledge/domains/**` is read as real benchmark and pattern data, so the
    explicit synthetic tier tag must never land there."""
    name = "denies_synthetic_tag_under_knowledge_domains"
    result = _run_hook(root, write_payload("knowledge/domains/retail/benchmarks.md",
                                           content=TAGGED_BODY))
    ok = _denied_text(result) and SYNTHETIC_TAG in result.stdout_text
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} stdout={result.stdout_text[:220]!r}"))


def _allows_synthetic_tag_outside_domains(root: Path) -> CheckResult:
    """The other side of the asymmetry, and the reason the tag rule is scoped
    at all: under `knowledge/learnings/` and `knowledge/standards/` the tag
    DOCUMENTS the tier rather than claiming synthetic data is real. A guard that
    denied it everywhere would make the quarantine model impossible to write
    down."""
    name = "allows_synthetic_tag_outside_domains"
    result = _run_hook(root, write_payload("knowledge/learnings/evidence_tiers.md",
                                           content=TAGGED_BODY))
    ok = _allowed(result)
    return bool_check(name, ok, detail=(
        f"{SYNTHETIC_TAG} under knowledge/learnings/ -> rc={result.returncode} "
        f"stdout={result.stdout_text[:160]!r}"))


def _allows_markers_outside_knowledge_tree(root: Path) -> CheckResult:
    """Scope is `knowledge/**` and nothing else. `tests/engagements/` is where
    synthetic fixtures are SUPPOSED to live — both markers together must be
    writable there, or the quarantine has nowhere to put the material it
    quarantines."""
    name = "allows_markers_outside_knowledge_tree"
    body = FICTIONAL_BODY + "\n" + TAGGED_BODY
    result = _run_hook(root, write_payload("tests/engagements/zzzsynthetic/notes.md",
                                           content=body))
    ok = _allowed(result)
    return bool_check(name, ok, detail=(
        f"both markers under tests/engagements/ -> rc={result.returncode} "
        f"stdout={result.stdout_text[:160]!r}"))


def _inspects_edit_new_string_not_write_content(root: Path) -> CheckResult:
    """Write carries incoming content in `tool_input.content`; Edit carries it
    in `tool_input.new_string`. Reading only the Write field would leave Edit a
    silent bypass into the same files — this fixture sends the marker through
    the Edit field alone, with no `content` key at all, so it can only pass if
    that branch is really read."""
    name = "inspects_edit_new_string_not_write_content"
    result = _run_hook(root, edit_payload("knowledge/learnings/retail_onboarding.md",
                                          new_string=FICTIONAL_BODY))
    ok = _denied_text(result) and FICTIONAL_NAME in result.stdout_text
    return bool_check(name, ok, detail=(
        f"Edit.new_string carrying {FICTIONAL_NAME!r} -> rc={result.returncode} "
        f"stdout={result.stdout_text[:220]!r}"))


def _ignores_tools_other_than_write_and_edit(root: Path) -> CheckResult:
    """Scope is Write and Edit — the two tools that put content on disk. The
    hook is registered on `Edit|Write` only, and its own tool guard must agree:
    a tool it was never registered for arriving through some other path must be
    allowed, not decided on with a field it does not understand."""
    name = "ignores_tools_other_than_write_and_edit"
    payload = pretooluse_payload("NotebookEdit", {
        "file_path": "knowledge/learnings/retail_onboarding.ipynb",
        "new_string": FICTIONAL_BODY,
    })
    result = _run_hook(root, payload)
    ok = _allowed(result)
    return bool_check(name, ok, detail=(
        f"NotebookEdit under knowledge/ carrying {FICTIONAL_NAME!r} -> "
        f"rc={result.returncode} stdout={result.stdout_text[:160]!r}"))


def _deny_decision_shape_matches_hook_contract(root: Path) -> CheckResult:
    """The PreToolUse envelope, and the ONLY check here that reads it: exit 0
    (never a non-zero exit) with
    `hookSpecificOutput.permissionDecision == "deny"` and a non-empty reason.
    Get this wrong and every deny above becomes a silent allow no matter how
    correct the marker logic is."""
    name = "deny_decision_shape_matches_hook_contract"
    result = _run_hook(root, write_payload("knowledge/learnings/retail_onboarding.md",
                                           content=FICTIONAL_BODY))
    parsed = result.stdout_json
    block = parsed.get("hookSpecificOutput") if isinstance(parsed, dict) else None
    ok = (
        result.returncode == 0
        and isinstance(block, dict)
        and block.get("hookEventName") == "PreToolUse"
        and block.get("permissionDecision") == "deny"
        and isinstance(block.get("permissionDecisionReason"), str)
        and block.get("permissionDecisionReason") != ""
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} hookSpecificOutput="
        f"{ {k: str(v)[:40] for k, v in block.items()} if isinstance(block, dict) else block}"))


# --- fail-open contract ---------------------------------------------------------

def _fails_open_on_malformed_payload(root: Path) -> CheckResult:
    """Unparseable stdin must ALLOW. Proved as a SPLIT: the same hook denies a
    well-formed contaminating Write, so the allow is attributable to the
    payload rather than to a guard that has stopped denying."""
    name = "fails_open_on_malformed_payload"
    control = _run_hook(root, write_payload("knowledge/learnings/retail_onboarding.md",
                                            content=FICTIONAL_BODY))
    result = _run_hook(root, b"{ not json at all")
    ok = _denied_text(control) and _allowed(result)
    return bool_check(name, ok, detail=(
        f"well-formed contaminating write denied={_denied_text(control)}; malformed "
        f"payload rc={result.returncode} stdout={result.stdout_text[:160]!r}"))


def _fails_open_under_injected_fault(root: Path) -> CheckResult:
    """A real, unhandled exception raised INSIDE `main()` must still allow —
    the module's outermost `except Exception: sys.exit(0)` backstop.

    The fault: a payload whose `tool_input` is a STRING rather than an object.
    `payload.get("tool_input", {}) or {}` keeps the truthy string as-is and the
    next line calls `.get` on it, raising `AttributeError` from the middle of
    `main()` — a genuine unhandled fault in the hook's own logic, not a
    simulated one, and one no `try/except` inside `main()` covers.

    Proved as a SPLIT: the identical hook denies a well-formed contaminating
    Write (control), so the allow comes from the backstop. Chosen over a
    filesystem permission fault because this hook performs no filesystem reads
    at all — its only I/O is stdin — so there is nothing to chmod, and
    inventing a fault it cannot encounter would prove nothing about it.
    """
    name = "fails_open_under_injected_fault"
    control = _run_hook(root, write_payload("knowledge/domains/retail/benchmarks.md",
                                            content=TAGGED_BODY))
    malformed = json.dumps({"tool_name": "Write",
                            "tool_input": "not-an-object"}).encode("utf-8")
    faulted = _run_hook(root, malformed)
    ok = _denied_text(control) and _allowed(faulted)
    return bool_check(name, ok, detail=(
        f"control (well-formed contaminating write) denied={_denied_text(control)}; "
        f"tool_input as a string -> rc={faulted.returncode} "
        f"stdout={faulted.stdout_text[:120]!r} crashed={crashed(faulted)}"))


# --- process contract -------------------------------------------------------------

def _invoked_as_subprocess_not_import(root: Path) -> CheckResult:
    """Two invocations of the SAME ABSOLUTE path under two different
    `CLAUDE_PROJECT_DIR` roots — see `_common.py` for why the differential is
    the real proof, and this module's docstring for why this is the one check
    here that uses an absolute path. Under root A the file is
    `knowledge/learnings/…` and the marker denies; under root B `_rel` cannot
    make it repo-relative, so it is not under `knowledge/` at all and the
    identical bytes are allowed."""
    a_root = root / "project_a"
    b_root = root / "project_b"
    a_root.mkdir(parents=True, exist_ok=True)
    b_root.mkdir(parents=True, exist_ok=True)
    target = str(a_root / "knowledge" / "learnings" / "retail_onboarding.md")

    return check_invoked_as_subprocess_not_import(
        _hook_path(),
        hook_label="synthetic-knowledge-guard.py",
        observe_a=lambda: _denied_text(_run_hook(a_root, write_payload(target, content=FICTIONAL_BODY))),
        observe_b=lambda: _denied_text(_run_hook(b_root, write_payload(target, content=FICTIONAL_BODY))),
        what="denied",
    )


def _runs_under_registered_interpreter(root: Path) -> CheckResult:
    """#192/backlog :116 — spawned under the interpreter
    `.claude/settings.json` registers (bare `python3`), never the eval runner's
    `sys.executable`. `spawn` goes through this row's own `_run_hook` with a
    clean, allowed payload; only the argv matters."""
    return check_runs_under_registered_interpreter(
        _hook_path(),
        hook_label="synthetic-knowledge-guard.py",
        spawn=lambda: _run_hook(root, write_payload("knowledge/domains/retail/probe.md",
                                                    content=CLEAN_BODY)),
    )


def evaluate(target: str) -> list:  # noqa: ARG001 - self-contained, ignores target
    missing = missing_hook_check(_hook_path())
    if missing is not None:
        return [missing]
    return [
        run_in_tmp(_denies_fictional_name_written_under_knowledge, prefix=TMP_PREFIX),
        run_in_tmp(_denies_synthetic_tag_under_knowledge_domains, prefix=TMP_PREFIX),
        run_in_tmp(_allows_synthetic_tag_outside_domains, prefix=TMP_PREFIX),
        run_in_tmp(_allows_markers_outside_knowledge_tree, prefix=TMP_PREFIX),
        run_in_tmp(_inspects_edit_new_string_not_write_content, prefix=TMP_PREFIX),
        run_in_tmp(_ignores_tools_other_than_write_and_edit, prefix=TMP_PREFIX),
        run_in_tmp(_deny_decision_shape_matches_hook_contract, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_on_malformed_payload, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_under_injected_fault, prefix=TMP_PREFIX),
        run_in_tmp(_invoked_as_subprocess_not_import, prefix=TMP_PREFIX),
        run_in_tmp(_runs_under_registered_interpreter, prefix=TMP_PREFIX),
    ]
