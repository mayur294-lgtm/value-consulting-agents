"""`enforce-journal` component evaluator — the POST-completion auditability gate.

SUBJECT: `.claude/hooks/enforce-journal.py`, the STOP hook that refuses to let a
turn end while an engagement that produced a deliverable this session is missing
its governance trail.

It makes three rules CLAUDE.md and `knowledge/standards/auditability_protocol.md`
both call MANDATORY actually deterministic:

  1. JOURNAL FRESHNESS  a deliverable newer than the last ENGAGEMENT_JOURNAL.md
                        update means the work was not logged
  2. TELEMETRY BLOCK    the journal carries at least one `<!-- TELEMETRY_START -->`
  3. DUAL CHECKPOINTS   at least 2 checkpoints, counted as `### Checkpoint:`
                        journal blocks plus `CHECKPOINT_*.md` files in outputs/

Each is a separate `findings` branch, so each gets its own check with its own
fixture: a single "violating engagement blocks" check would stay green after two
of the three branches were deleted.

A STOP HOOK IS A DIFFERENT CONTRACT
------------------------------------
`_harness.pretooluse_payload` is the wrong envelope here. A Stop hook receives no
`tool_name`/`tool_input`, and answers with `{"decision": "block", "reason": ...}`
rather than `hookSpecificOutput.permissionDecision`. `_common.stop_payload()`
builds the right stdin and `_common.stop_blocked()` reads the right envelope.

WHY MOST CHECKS ASSERT ON THE REASON TEXT, NOT THE ENVELOPE
------------------------------------------------------------
Only `block_decision_shape_matches_stop_contract` asserts the JSON envelope.
Every other blocking check asserts `rc == 0` plus its own finding sentence in
raw stdout. That is deliberate: it leaves the envelope check as the ONLY thing a
change to the envelope reddens, so its mutation proves the shape rather than
being drowned in six identical failures — and it keeps each finding check
pinned to ITS finding rather than to "something blocked".

Fail-OPEN is this hook's contract ("a buggy hook must never wedge a session"),
so the fault check is `fails_open_under_injected_fault` and it proves a SPLIT:
the same fixture blocks with a readable journal and allows once the journal
raises `PermissionError`, so the allow provably comes from the fault handler.

Fixtures live in a tempdir reached via `CLAUDE_PROJECT_DIR` — the hook globs
`engagements/*/*/ENGAGEMENT_JOURNAL.md` under it, so nothing here can reach the
real `engagements/` tree. threshold 1.00. No `judge:` entries.
"""
from __future__ import annotations

from pathlib import Path

from rubrics.base import CheckResult, repo_root
from rubrics._harness import (
    HookRun,
    build_fixture_engagement,
    check_runs_under_registered_interpreter,
    fault_injection_skip,
    inject_fault,
    run_hook_subprocess,
)
from rubrics.component.hooks._common import (
    HOOK_TIMEOUT_S,
    block_reason,
    bool_check,
    check_invoked_as_subprocess_not_import,
    crashed,
    missing_hook_check,
    run_in_tmp,
    set_mtime,
    stop_blocked,
    stop_payload,
)

HOOK_REL_PATH = Path(".claude") / "hooks" / "enforce-journal.py"
TMP_PREFIX = "enforce_journal_row_"

SLUG = "zzzplaceholderclient"
ENGAGEMENT = "2026-01_test_engagement"

_TELEMETRY = ("<!-- TELEMETRY_START -->\nagent: narrative-assembler\n"
              "<!-- TELEMETRY_END -->\n")
_CHECKPOINT = "### Checkpoint: {stage}\n\nPresented to the consultant; approved.\n\n"

JOURNAL_COMPLETE = (
    "# Engagement Journal\n\n"
    + _CHECKPOINT.format(stage="pre-generation")
    + _CHECKPOINT.format(stage="post-generation")
    + _TELEMETRY
)
JOURNAL_NO_TELEMETRY = (
    "# Engagement Journal\n\n"
    + _CHECKPOINT.format(stage="pre-generation")
    + _CHECKPOINT.format(stage="post-generation")
)
JOURNAL_ONE_CHECKPOINT = (
    "# Engagement Journal\n\n"
    + _CHECKPOINT.format(stage="pre-generation")
    + _TELEMETRY
)
JOURNAL_BARE = "# Engagement Journal\n\nNothing logged yet.\n"

HOUR = 3600.0


def _hook_path() -> Path:
    """Resolved through `repo_root()` so the mutation harness reaches its SHADOW
    copy of the hook."""
    return repo_root() / HOOK_REL_PATH


def _run_hook(project_dir: Path, stdin_bytes: bytes = None) -> HookRun:
    """This row's ONE subprocess entry point."""
    payload = stop_payload() if stdin_bytes is None else stdin_bytes
    return run_hook_subprocess(_hook_path(), payload,
                               project_dir=project_dir, timeout=HOOK_TIMEOUT_S)


def _blocked_text(result: HookRun) -> bool:
    """"The stop was blocked", asserted WITHOUT reading the JSON envelope — see
    the module docstring. Keeps the envelope's own check the only one a change
    to the envelope reddens."""
    return result.returncode == 0 and "Auditability gate" in result.stdout_text


def _seed(root: Path, *, journal: str, deliverable_age_s: float,
          journal_age_s: float, extra_outputs=None) -> Path:
    """One violating-or-clean engagement, with both mtimes pinned.

    Every finding this hook produces is an mtime or a text comparison, so a
    fixture that lets the filesystem decide the write order cannot target one
    finding at a time. Ages are seconds BEFORE now.
    """
    documents = {"ENGAGEMENT_JOURNAL.md": journal,
                 "outputs/assessment_report.md": "# Assessment\n\nplaceholder\n"}
    documents.update(extra_outputs or {})
    fixture = build_fixture_engagement(root, slug=SLUG, engagement=ENGAGEMENT,
                                       subdirs=("outputs",), documents=documents)
    assert fixture.engagement_dir is not None
    eng = fixture.engagement_dir
    for name in documents:
        if name != "ENGAGEMENT_JOURNAL.md":
            set_mtime(eng / name, deliverable_age_s)
    set_mtime(eng / "ENGAGEMENT_JOURNAL.md", journal_age_s)
    return eng


def _seed_no_deliverable(root: Path, *, journal: str) -> Path:
    """An engagement whose outputs/ holds ONLY non-deliverables — a checkpoint,
    an interim file, a dotfile. `_is_deliverable` excludes all three, so
    `_newest_deliverable_mtime` must come back 0.0 and the whole engagement
    must fall out of scope."""
    fixture = build_fixture_engagement(
        root, slug=SLUG, engagement=ENGAGEMENT, subdirs=("outputs",),
        documents={
            "ENGAGEMENT_JOURNAL.md": journal,
            "outputs/CHECKPOINT_scope.md": "# Checkpoint\n\nApproved.\n",
            "outputs/interim_notes.md": "scratch\n",
            "outputs/.pipeline_run_report.json": "{}\n",
        })
    assert fixture.engagement_dir is not None
    return fixture.engagement_dir


# --- the three MANDATORY rules -----------------------------------------------

def _blocks_stop_when_journal_is_stale(root: Path) -> CheckResult:
    """Rule 1. The journal is otherwise COMPLETE — telemetry block present, two
    checkpoints logged — so staleness is the only finding available, and this
    check cannot pass on one of the other two branches by accident."""
    name = "blocks_stop_when_journal_is_stale"
    _seed(root, journal=JOURNAL_COMPLETE, deliverable_age_s=10, journal_age_s=900)
    result = _run_hook(root)
    ok = (
        _blocked_text(result)
        and "after the last journal update" in result.stdout_text
    )
    return bool_check(name, ok, detail=(
        f"deliverable 10s old, journal 900s old, journal otherwise complete -> "
        f"rc={result.returncode} stdout={result.stdout_text[:220]!r}"))


def _blocks_stop_when_telemetry_block_missing(root: Path) -> CheckResult:
    """Rule 2. Journal is FRESH (newer than the deliverable) and carries two
    checkpoints, so the missing `<!-- TELEMETRY_START -->` block is the only
    finding — this is what the Flywheel's intake reads, and an engagement
    without it is invisible to the backlog."""
    name = "blocks_stop_when_telemetry_block_missing"
    _seed(root, journal=JOURNAL_NO_TELEMETRY, deliverable_age_s=900, journal_age_s=10)
    result = _run_hook(root)
    ok = _blocked_text(result) and "no telemetry block" in result.stdout_text
    return bool_check(name, ok, detail=(
        f"journal fresh + 2 checkpoints, no telemetry marker -> "
        f"rc={result.returncode} stdout={result.stdout_text[:220]!r}"))


def _blocks_stop_when_fewer_than_two_checkpoints(root: Path) -> CheckResult:
    """Rule 3. Journal is FRESH and carries the telemetry block, but only ONE
    `### Checkpoint:` — the dual-checkpoint rule is pre-generation AND
    post-generation, and one of them is the half agents skip."""
    name = "blocks_stop_when_fewer_than_two_checkpoints"
    _seed(root, journal=JOURNAL_ONE_CHECKPOINT, deliverable_age_s=900, journal_age_s=10)
    result = _run_hook(root)
    ok = (
        _blocked_text(result)
        and "consultant checkpoint(s) logged" in result.stdout_text
        and "only 1 " in result.stdout_text
    )
    return bool_check(name, ok, detail=(
        f"journal fresh + telemetry + 1 checkpoint -> rc={result.returncode} "
        f"stdout={result.stdout_text[:220]!r}"))


def _allows_stop_when_governance_trail_complete(root: Path) -> CheckResult:
    """The negative that keeps the three above honest: all three rules
    satisfied at once must ALLOW the stop, silently. A hook that blocked
    unconditionally would satisfy every blocking check on this row and would
    make it impossible to ever finish a turn."""
    name = "allows_stop_when_governance_trail_complete"
    _seed(root, journal=JOURNAL_COMPLETE, deliverable_age_s=900, journal_age_s=10)
    result = _run_hook(root)
    ok = result.returncode == 0 and not result.stdout.strip() and not crashed(result)
    return bool_check(name, ok, detail=(
        f"fresh journal + telemetry + 2 checkpoints -> rc={result.returncode} "
        f"stdout={result.stdout_text[:160]!r}"))


# --- scope ---------------------------------------------------------------------

def _ignores_engagement_outside_recency_window(root: Path) -> CheckResult:
    """Scope is THIS SESSION's work. A past engagement whose newest deliverable
    is older than the 12h window is not audited even with a completely bare
    journal — otherwise every previously-closed engagement in the tree would
    block every stop, forever, and the hook would be disabled within a day."""
    name = "ignores_engagement_outside_recency_window"
    _seed(root, journal=JOURNAL_BARE, deliverable_age_s=13 * HOUR, journal_age_s=13 * HOUR)
    result = _run_hook(root)
    ok = result.returncode == 0 and not result.stdout.strip() and not crashed(result)
    return bool_check(name, ok, detail=(
        f"bare journal but deliverable 13h old (window 12h) -> "
        f"rc={result.returncode} stdout={result.stdout_text[:160]!r}"))


def _ignores_engagement_with_no_deliverable(root: Path) -> CheckResult:
    """Nothing FINAL was produced, so there is nothing to gate. outputs/ here
    holds only a `CHECKPOINT_*.md`, an `interim_*` file and a dotfile — the
    three shapes `_is_deliverable` excludes. If any of those started counting,
    the hook would block on the very checkpoint file it asks agents to write."""
    name = "ignores_engagement_with_no_deliverable"
    _seed_no_deliverable(root, journal=JOURNAL_BARE)
    result = _run_hook(root)
    ok = result.returncode == 0 and not result.stdout.strip() and not crashed(result)
    return bool_check(name, ok, detail=(
        f"outputs/ holds only CHECKPOINT_/interim_/dotfile, bare journal -> "
        f"rc={result.returncode} stdout={result.stdout_text[:160]!r}"))


def _block_decision_shape_matches_stop_contract(root: Path) -> CheckResult:
    """The Stop-hook envelope, and the ONLY check here that reads it: exit 0
    (never a non-zero exit) with `{"decision": "block", "reason": <non-empty
    str>}` on stdout. Get this wrong and every block above becomes a silent
    allow no matter how correct the finding logic is."""
    name = "block_decision_shape_matches_stop_contract"
    _seed(root, journal=JOURNAL_BARE, deliverable_age_s=10, journal_age_s=900)
    result = _run_hook(root)
    parsed = result.stdout_json
    ok = (
        result.returncode == 0
        and parsed is not None
        and stop_blocked(result)
        and isinstance(block_reason(result), str)
        and block_reason(result) != ""
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} stdout_json_keys="
        f"{sorted(parsed) if parsed else None} reason={block_reason(result)[:120]!r}"))


# --- fail-open contract ---------------------------------------------------------

def _fails_open_on_malformed_payload(root: Path) -> CheckResult:
    """Unparseable stdin must ALLOW the stop. Proved as a SPLIT: the same
    fixture blocks on a well-formed Stop payload, so the allow is attributable
    to the payload and not to the fixture being clean."""
    name = "fails_open_on_malformed_payload"
    _seed(root, journal=JOURNAL_BARE, deliverable_age_s=10, journal_age_s=900)
    control = _run_hook(root)
    result = _run_hook(root, b"not json at all {")
    ok = (
        _blocked_text(control)
        and result.returncode == 0 and not result.stdout.strip() and not crashed(result)
    )
    return bool_check(name, ok, detail=(
        f"well-formed payload blocked={_blocked_text(control)}; malformed payload "
        f"rc={result.returncode} stdout={result.stdout_text[:160]!r}"))


def _fails_open_under_injected_fault(root: Path) -> CheckResult:
    """A real, unmocked `PermissionError` reading ENGAGEMENT_JOURNAL.md must
    ALLOW the stop — `_audit_engagement`'s `except OSError: return None`.

    Proved as a SPLIT: the identical fixture blocks with the journal readable
    and allows with it chmod'd to 000. Without the control half, a hook that
    had stopped auditing entirely would satisfy this check.

    Skips under root, which bypasses file permission bits.
    """
    name = "fails_open_under_injected_fault"
    skip = fault_injection_skip(name, perms="file")
    if skip is not None:
        return skip

    eng = _seed(root, journal=JOURNAL_BARE, deliverable_age_s=10, journal_age_s=900)
    journal = eng / "ENGAGEMENT_JOURNAL.md"

    control = _run_hook(root)
    with inject_fault(journal):
        faulted = _run_hook(root)

    ok = (
        _blocked_text(control)
        and faulted.returncode == 0 and not faulted.stdout.strip()
        and not crashed(faulted)
    )
    return bool_check(name, ok, detail=(
        f"journal readable: blocked={_blocked_text(control)}; journal chmod 000: "
        f"rc={faulted.returncode} stdout={faulted.stdout_text[:120]!r} "
        f"crashed={crashed(faulted)}"))


# --- process contract -----------------------------------------------------------

def _invoked_as_subprocess_not_import(root: Path) -> CheckResult:
    """Two invocations against two different `CLAUDE_PROJECT_DIR` roots — see
    `_common.py`. This hook takes no path argument at all: `PROJECT_DIR` IS its
    entire input, so an import-once hook would audit root A's engagements
    forever. Root A carries a violating engagement (block); root B is empty
    (nothing to audit, allow)."""
    a_root = root / "project_a"
    b_root = root / "project_b"
    b_root.mkdir(parents=True, exist_ok=True)
    _seed(a_root, journal=JOURNAL_BARE, deliverable_age_s=10, journal_age_s=900)

    return check_invoked_as_subprocess_not_import(
        _hook_path(),
        hook_label="enforce-journal.py",
        observe_a=lambda: _blocked_text(_run_hook(a_root)),
        observe_b=lambda: _blocked_text(_run_hook(b_root)),
        what="stop blocked",
    )


def _runs_under_registered_interpreter(root: Path) -> CheckResult:
    """#192/backlog :116 — spawned under the interpreter
    `.claude/settings.json` registers (bare `python3`), never the eval runner's
    `sys.executable`. `spawn` goes through this row's own `_run_hook` against
    an empty project root; the decision is irrelevant, only the argv matters."""
    return check_runs_under_registered_interpreter(
        _hook_path(),
        hook_label="enforce-journal.py",
        spawn=lambda: _run_hook(root),
    )


def evaluate(target: str) -> list:  # noqa: ARG001 - self-contained, ignores target
    missing = missing_hook_check(_hook_path())
    if missing is not None:
        return [missing]
    return [
        run_in_tmp(_blocks_stop_when_journal_is_stale, prefix=TMP_PREFIX),
        run_in_tmp(_blocks_stop_when_telemetry_block_missing, prefix=TMP_PREFIX),
        run_in_tmp(_blocks_stop_when_fewer_than_two_checkpoints, prefix=TMP_PREFIX),
        run_in_tmp(_allows_stop_when_governance_trail_complete, prefix=TMP_PREFIX),
        run_in_tmp(_ignores_engagement_outside_recency_window, prefix=TMP_PREFIX),
        run_in_tmp(_ignores_engagement_with_no_deliverable, prefix=TMP_PREFIX),
        run_in_tmp(_block_decision_shape_matches_stop_contract, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_on_malformed_payload, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_under_injected_fault, prefix=TMP_PREFIX),
        run_in_tmp(_invoked_as_subprocess_not_import, prefix=TMP_PREFIX),
        run_in_tmp(_runs_under_registered_interpreter, prefix=TMP_PREFIX),
    ]
