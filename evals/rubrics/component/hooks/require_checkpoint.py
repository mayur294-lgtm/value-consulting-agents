"""`require-checkpoint` component evaluator — the PRE-generation checkpoint gate.

SUBJECT: `.claude/hooks/require-checkpoint.py`, the PreToolUse(Write) hook that
blocks writing a FINAL client deliverable into an engagement's `outputs/` until
a pre-generation consultant checkpoint has been presented and logged.

This is what makes CLAUDE.md's "minimum 2 consultant checkpoints (pre + post)"
deterministic rather than advisory: without it an agent can generate the whole
deliverable and only then (maybe) log a checkpoint — the "agents make unilateral
decisions" failure the NFIS retrospective flagged. Until this row the hook had
no eval at all, so every one of its narrowing conditions could have been widened
or deleted silently.

FAIL-OPEN IS THE CONTRACT HERE, NOT FAIL-CLOSED
------------------------------------------------
Unlike `anonymize-guard` (fail-closed inside raw client material) and
`mcp-query-guard` (fail-closed on an outbound third-party call), this hook is
documented fail-OPEN: "never wedge a session on a hook bug". So the ticket's
`fails_closed_under_injected_fault` is deliberately NOT authored here — the
analogue that asserts this hook's ACTUAL contract is
`fails_open_under_injected_fault`, and it proves a SPLIT rather than "allow
happens somewhere": the same fixture DENIES with no fault and ALLOWS once the
journal becomes unreadable, so the allow provably comes from the fault handler
(`_has_pre_generation_checkpoint`'s `except OSError: return True`) and not from
the fixture simply satisfying the gate.

A KNOWN GAP THIS ROW PINS RATHER THAN FIXES
--------------------------------------------
`write_outside_engagements_tree_is_not_gated` records, as an executable fact,
that the gate keys on a path carrying BOTH an `engagements` and an `outputs`
segment. `.prd/backlog.md:133` already records the consequence — pipeline agents
now write to `<workspace>/outputs/`, which this hook therefore no longer
covers. #197 is a test-only ticket and explicitly must not change hook
behaviour, so the check pins today's scope and the backlog entry stays the
place that tracks closing it. If that scope is ever widened deliberately, this
check is the thing that must be updated in the same change — which is the
point.

Fixtures live in a tempdir reached via `CLAUDE_PROJECT_DIR`; nothing here reads
or writes `engagements/` in the real checkout. threshold 1.00 — a governance
gate is pass/fail. No `judge:` entries: deterministic, offline, $0.
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
    bool_check,
    check_invoked_as_subprocess_not_import,
    crashed,
    edit_payload,
    missing_hook_check,
    run_in_tmp,
    write_payload,
)

HOOK_REL_PATH = Path(".claude") / "hooks" / "require-checkpoint.py"
TMP_PREFIX = "require_checkpoint_row_"

SLUG = "zzzplaceholderclient"
ENGAGEMENT = "2026-01_test_engagement"

JOURNAL_NO_CHECKPOINT = (
    "# Engagement Journal\n\n"
    "## 2026-01-05 — kickoff\n\n"
    "Agent: discovery-transcript-interpreter. Notes captured.\n"
)
JOURNAL_WITH_CHECKPOINT = (
    JOURNAL_NO_CHECKPOINT
    + "\n### Checkpoint: pre-generation (scope, assumptions, value levers)\n\n"
      "Presented to the consultant; approved.\n"
)


def _hook_path() -> Path:
    """Resolved through `repo_root()` so the mutation harness can point this row
    at its SHADOW copy of the hook — see evals/mutations.py."""
    return repo_root() / HOOK_REL_PATH


def _run_hook(project_dir: Path, stdin_bytes: bytes) -> HookRun:
    """This row's ONE subprocess entry point — every check goes through it,
    including the two process-contract checks, so those observe the argv this
    row really spawns."""
    return run_hook_subprocess(_hook_path(), stdin_bytes,
                               project_dir=project_dir, timeout=HOOK_TIMEOUT_S)


def _engagement(root: Path, *, journal: str = JOURNAL_NO_CHECKPOINT, documents=None):
    docs = {"ENGAGEMENT_JOURNAL.md": journal}
    docs.update(documents or {})
    return build_fixture_engagement(root, slug=SLUG, engagement=ENGAGEMENT,
                                    subdirs=("outputs",), documents=docs)


# --- the gate itself ---------------------------------------------------------

def _denies_deliverable_write_without_checkpoint(root: Path) -> CheckResult:
    """The whole point of the hook: a final deliverable into an engagement's
    outputs/ with no pre-generation checkpoint anywhere is refused, and the
    refusal tells the agent the two things that clear it."""
    name = "denies_deliverable_write_without_checkpoint"
    fixture = _engagement(root)
    assert fixture.engagement_dir is not None
    target = fixture.engagement_dir / "outputs" / "assessment_report.md"
    result = _run_hook(root, write_payload(str(target)))
    ok = (
        result.returncode == 0
        and result.denied
        and "Checkpoint gate" in result.reason
        and "CHECKPOINT_" in result.reason
        and "### Checkpoint:" in result.reason
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:200]!r}"))


def _allows_when_checkpoint_file_present(root: Path) -> CheckResult:
    """First of the two satisfying signals: a `CHECKPOINT_*.md` already written
    into the engagement's outputs/. This is the route an agent takes when it
    captures the checkpoint as an artifact rather than a journal block."""
    name = "allows_when_checkpoint_file_present"
    fixture = _engagement(root, documents={
        "outputs/CHECKPOINT_scope.md": "# Checkpoint: scope\n\nApproved.\n"})
    assert fixture.engagement_dir is not None
    target = fixture.engagement_dir / "outputs" / "assessment_report.md"
    result = _run_hook(root, write_payload(str(target)))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"outputs/CHECKPOINT_scope.md present -> rc={result.returncode} "
        f"denied={result.denied} stdout={result.stdout_text[:160]!r}"))


def _allows_when_journal_has_checkpoint_block(root: Path) -> CheckResult:
    """The other satisfying signal — a `### Checkpoint:` block in
    ENGAGEMENT_JOURNAL.md. Authored separately from the file route because
    either alone passing would let the other be deleted unnoticed; the fixture
    here carries NO CHECKPOINT_*.md so it can only pass via the journal scan."""
    name = "allows_when_journal_has_checkpoint_block"
    fixture = _engagement(root, journal=JOURNAL_WITH_CHECKPOINT)
    assert fixture.engagement_dir is not None
    target = fixture.engagement_dir / "outputs" / "assessment_report.md"
    result = _run_hook(root, write_payload(str(target)))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"journal carries '### Checkpoint:' and outputs/ has no CHECKPOINT_*.md -> "
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:160]!r}"))


def _allows_checkpoint_file_itself(root: Path) -> CheckResult:
    """Deadlock guard. The checkpoint the gate demands is itself a `.md` file
    written into the same outputs/ folder — if `CHECKPOINT_*` were gated, the
    one action that clears the gate could never be performed and the hook would
    wedge every deliverable in the repo."""
    name = "allows_checkpoint_file_itself"
    fixture = _engagement(root)
    assert fixture.engagement_dir is not None
    target = fixture.engagement_dir / "outputs" / "CHECKPOINT_scope.md"
    result = _run_hook(root, write_payload(str(target)))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"writing the checkpoint itself, no checkpoint yet logged -> "
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:160]!r}"))


def _allows_non_deliverable_extension(root: Path) -> CheckResult:
    """Scope is FINAL DELIVERABLE file types only. `roi_config.json` is an
    inter-agent artifact the pipeline writes mid-run, not something presented to
    a client — gating it would block the pipeline between its own steps."""
    name = "allows_non_deliverable_extension"
    fixture = _engagement(root)
    assert fixture.engagement_dir is not None
    target = fixture.engagement_dir / "outputs" / "roi_config.json"
    result = _run_hook(root, write_payload(str(target), content="{}\n"))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:160]!r}"))


def _ignores_edit_tool(root: Path) -> CheckResult:
    """Scope is Write (deliverable creation/overwrite), never Edit. The hook's
    own docstring calls this out as deliberate narrowing to avoid false blocks:
    an Edit is a revision of something that already cleared the gate once."""
    name = "ignores_edit_tool"
    fixture = _engagement(root, documents={
        "outputs/assessment_report.md": "# Assessment\n\nplaceholder\n"})
    assert fixture.engagement_dir is not None
    target = fixture.engagement_dir / "outputs" / "assessment_report.md"
    result = _run_hook(root, edit_payload(str(target)))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"Edit on a deliverable with no checkpoint -> rc={result.returncode} "
        f"denied={result.denied} stdout={result.stdout_text[:160]!r}"))


def _write_outside_engagements_tree_is_not_gated(root: Path) -> CheckResult:
    """Pins the gate's SCOPE as it stands today: it keys on a path carrying
    both an `engagements` and an `outputs` segment. An engagement-shaped tree
    somewhere else — same journal, same outputs/ folder, same deliverable, no
    checkpoint — is NOT gated.

    That is `.prd/backlog.md:133` in executable form: pipeline agents now write
    to `<workspace>/outputs/`, which this scope no longer covers. #197 is
    test-only and must not change hook behaviour, so this check records the
    current contract rather than asserting the one we might want. When the
    scope is widened deliberately, this is the check that has to move with it.
    """
    name = "write_outside_engagements_tree_is_not_gated"
    workspace_eng = root / "workspace" / "run_a1b2"
    (workspace_eng / "outputs").mkdir(parents=True, exist_ok=True)
    (workspace_eng / "ENGAGEMENT_JOURNAL.md").write_text(
        JOURNAL_NO_CHECKPOINT, encoding="utf-8")
    target = workspace_eng / "outputs" / "assessment_report.md"
    result = _run_hook(root, write_payload(str(target)))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"engagement-shaped tree with no 'engagements' segment -> "
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:160]!r} (backlog.md:133 — pinned, not endorsed)"))


# --- fail-open contract -------------------------------------------------------

def _fails_open_on_malformed_payload(root: Path) -> CheckResult:
    """Unparseable stdin must ALLOW. The inverse of `mcp-query-guard`, whose
    identical input denies — the difference is deliberate and is exactly what
    this check pins: that hook gates an outbound third-party call, this one
    gates a local write, and a local-write guard that denied on its own bugs
    would wedge the session (PR #82)."""
    name = "fails_open_on_malformed_payload"
    _engagement(root)
    result = _run_hook(root, b"this is not json { at all")
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:160]!r}"))


def _fails_open_under_injected_fault(root: Path) -> CheckResult:
    """A real, unmocked `PermissionError` reading ENGAGEMENT_JOURNAL.md must
    ALLOW — `_has_pre_generation_checkpoint`'s `except OSError: return True`.

    Proves a SPLIT, not "allow happens somewhere": the SAME fixture is run
    twice, once clean and once with the journal chmod'd to 000. Clean must
    DENY (no checkpoint anywhere) and faulted must ALLOW, so the allow can only
    have come from the fault handler. Without the control half, a hook that had
    simply stopped denying would satisfy this check completely.

    Skips under root, which bypasses file permission bits — a chmod that
    injects nothing is a FALSE pass, not a pass.
    """
    name = "fails_open_under_injected_fault"
    skip = fault_injection_skip(name, perms="file")
    if skip is not None:
        return skip

    fixture = _engagement(root)
    assert fixture.engagement_dir is not None
    journal = fixture.engagement_dir / "ENGAGEMENT_JOURNAL.md"
    target = fixture.engagement_dir / "outputs" / "assessment_report.md"

    control = _run_hook(root, write_payload(str(target)))
    with inject_fault(journal):
        faulted = _run_hook(root, write_payload(str(target)))

    ok = (
        control.returncode == 0 and control.denied           # the gate is live
        and faulted.returncode == 0 and not faulted.denied   # ... and yields to the fault
        and faulted.silent and not crashed(faulted)
    )
    return bool_check(name, ok, detail=(
        f"same fixture, journal readable: rc={control.returncode} "
        f"denied={control.denied}; journal chmod 000: rc={faulted.returncode} "
        f"denied={faulted.denied} crashed={crashed(faulted)}"))


# --- process contract ---------------------------------------------------------

def _invoked_as_subprocess_not_import(root: Path) -> CheckResult:
    """Two invocations, one RELATIVE `file_path`, two `CLAUDE_PROJECT_DIR`
    roots — see `_common.py` for why that differential is what actually
    separates a subprocess from an import-and-call. Root A carries the
    engagement (deny, no checkpoint); root B is empty, so the same relative
    path resolves to no recognised engagement at all (allow)."""
    a_root = root / "project_a"
    b_root = root / "project_b"
    b_root.mkdir(parents=True, exist_ok=True)
    _engagement(a_root)
    rel = f"engagements/{SLUG}/{ENGAGEMENT}/outputs/assessment_report.md"

    return check_invoked_as_subprocess_not_import(
        _hook_path(),
        hook_label="require-checkpoint.py",
        observe_a=lambda: _run_hook(a_root, write_payload(rel)).denied,
        observe_b=lambda: _run_hook(b_root, write_payload(rel)).denied,
        what="denied",
    )


def _runs_under_registered_interpreter(root: Path) -> CheckResult:
    """#192/backlog :116 — spawned under whatever `.claude/settings.json`
    registers (bare `python3`, 3.9.6 on most consultant machines), never a
    silent fallback to the eval runner's `sys.executable`. `spawn` goes through
    this row's own `_run_hook`."""
    probe = root / "scratch" / "probe.md"
    probe.parent.mkdir(parents=True, exist_ok=True)
    return check_runs_under_registered_interpreter(
        _hook_path(),
        hook_label="require-checkpoint.py",
        spawn=lambda: _run_hook(root, write_payload(str(probe))),
    )


def evaluate(target: str) -> list:  # noqa: ARG001 - self-contained, ignores target
    missing = missing_hook_check(_hook_path())
    if missing is not None:
        return [missing]
    return [
        run_in_tmp(_denies_deliverable_write_without_checkpoint, prefix=TMP_PREFIX),
        run_in_tmp(_allows_when_checkpoint_file_present, prefix=TMP_PREFIX),
        run_in_tmp(_allows_when_journal_has_checkpoint_block, prefix=TMP_PREFIX),
        run_in_tmp(_allows_checkpoint_file_itself, prefix=TMP_PREFIX),
        run_in_tmp(_allows_non_deliverable_extension, prefix=TMP_PREFIX),
        run_in_tmp(_ignores_edit_tool, prefix=TMP_PREFIX),
        run_in_tmp(_write_outside_engagements_tree_is_not_gated, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_on_malformed_payload, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_under_injected_fault, prefix=TMP_PREFIX),
        run_in_tmp(_invoked_as_subprocess_not_import, prefix=TMP_PREFIX),
        run_in_tmp(_runs_under_registered_interpreter, prefix=TMP_PREFIX),
    ]
