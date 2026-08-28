"""`require-harness` component evaluator — the bb-* lifecycle auto-trigger gate.

SUBJECT: `.claude/hooks/require-harness.py`, the PreToolUse(Edit|Write|
NotebookEdit) hook that blocks a direct edit to a CONTENT COMPONENT (an agent,
slash command, output template, presentation engine, or pipeline script) unless
a bb-* change is active.

It is the local enforcement layer behind CLAUDE.md's standing "route component
changes through `/bb-prd → … → /bb-refine`" directive — the thing that stops a
missed recognition from becoming an ungated component edit, with `evals.yml` as
the server-side backstop. Until this row it had no eval, which means the
protected-prefix list, the exemption list and the active-change signal could all
have been widened silently. Every check below is one of those lists.

TWO LISTS, PULLING IN OPPOSITE DIRECTIONS
------------------------------------------
Half of this hook's risk is under-blocking (a component edited outside the
lifecycle) and half is over-blocking (the harness unable to build itself — the
self-deadlock the EXEMPT_PREFIXES list exists to prevent; this very file lives
under `evals/`, one of those exemptions). So the checks come in pairs that must
split rather than agree: `.claude/skills/custom/` denies while
`.claude/skills/bb-build/` allows; `scripts/x.py` denies while `scripts/x.sh`
allows. A one-sided check would be satisfied by a hook that blocks everything or
one that blocks nothing.

FAIL-OPEN, BUT BY CRASHING — PINNED HERE, FILED IN THE BACKLOG
---------------------------------------------------------------
The hook documents itself "Fail-OPEN on any error", and in effect it is: with
`.prd/` unreadable it raises `PermissionError` out of `_change_active()`, exits
non-zero with a traceback and writes nothing on stdout, and Claude Code treats
any exit code other than 2 as a non-blocking error, so the tool call proceeds.
`fails_open_under_injected_fault` asserts what MATTERS (it does not block) and
records the crash in its detail rather than asserting a clean exit 0 that the
hook does not currently produce. #197 is test-only and must not change hook
behaviour; the gap between "fails open" and "fails open cleanly" is filed in
`.prd/backlog.md` instead.

MUTATION COLLATERAL, STATED UP FRONT
-------------------------------------
Two checks here — `fails_open_under_injected_fault` and
`invoked_as_subprocess_not_import` — turn on code every other check also runs
through (`_change_active()` and `PROJECT_DIR` respectively), so their mutations
redden several checks, not one. That is allowed (the harness inspects only the
NAMED check) but it is worth saying: no more surgical mutation exists for
either, because the fault is injected inside the very lookup the whole hook
depends on.

threshold 1.00 — a governance gate is pass/fail. No `judge:` entries.
"""
from __future__ import annotations

from pathlib import Path

from rubrics.base import CheckResult, repo_root
from rubrics._harness import (
    HookRun,
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
    read_payload,
    run_in_tmp,
    write_payload,
)

HOOK_REL_PATH = Path(".claude") / "hooks" / "require-harness.py"
TMP_PREFIX = "require_harness_row_"


def _hook_path() -> Path:
    """Resolved through `repo_root()` so the mutation harness reaches its SHADOW
    copy of the hook rather than the real one."""
    return repo_root() / HOOK_REL_PATH


def _run_hook(project_dir: Path, stdin_bytes: bytes) -> HookRun:
    """This row's ONE subprocess entry point."""
    return run_hook_subprocess(_hook_path(), stdin_bytes,
                               project_dir=project_dir, timeout=HOOK_TIMEOUT_S)


def _no_change_active(root: Path) -> Path:
    """A project root with NO bb-* change signal: no `.prd/ACTIVE_CHANGE`, no
    `.prd/prd-v*.md`. The hook only reads those two, so nothing else needs to
    exist — including the edited file itself, which the hook never opens."""
    root.mkdir(parents=True, exist_ok=True)
    return root


def _with_prd(root: Path) -> Path:
    prd = root / ".prd"
    prd.mkdir(parents=True, exist_ok=True)
    (prd / "prd-v1.md").write_text(
        "# PRD v1\n\n## Eval Acceptance Criteria\n\nplaceholder\n", encoding="utf-8")
    return root


def _with_marker(root: Path) -> Path:
    prd = root / ".prd"
    prd.mkdir(parents=True, exist_ok=True)
    (prd / "ACTIVE_CHANGE").write_text("acknowledged\n", encoding="utf-8")
    return root


def _prd_text(version: int, status: str | None) -> str:
    """A PRD with the front matter bb-prd actually writes."""
    front = f"---\nversion: {version}\ndate: 2026-08-28\nauthor: t\n"
    if status is not None:
        front = f"---\nversion: {version}\nstatus: {status}\ndate: 2026-08-28\n"
    return front + "---\n\n# PRD\n\n## Eval Acceptance Criteria\n\nplaceholder\n"


def _with_closed_prds(root: Path) -> Path:
    """Only SHIPPED PRDs — the state every clone of `main` is in. This is the
    regression fixture: `_change_active()` used to test `any(prd-v*.md)`, so the
    first PRD ever committed left the gate open on every machine, permanently."""
    prd = root / ".prd"
    prd.mkdir(parents=True, exist_ok=True)
    (prd / "prd-v1.md").write_text(_prd_text(1, "archived"), encoding="utf-8")
    (prd / "prd-v2.md").write_text(_prd_text(2, "built"), encoding="utf-8")
    return root


def _repo_prd_statuses() -> dict[str, str | None]:
    """Front-matter `status:` of every real `.prd/prd-v*.md`, parsed HERE rather
    than by importing the hook's own helper — a deployment check that reused the
    implementation it is checking would agree with itself by construction."""
    out: dict[str, str | None] = {}
    for p in sorted((repo_root() / ".prd").glob("prd-v*.md")):
        status = None
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            out[p.name] = None
            continue
        if lines and lines[0].strip() == "---":
            for line in lines[1:40]:
                if line.strip() == "---":
                    break
                if line.startswith("status:"):
                    status = line.split(":", 1)[1].strip().strip("\"'").lower()
                    break
        out[p.name] = status
    return out


# --- protected components -----------------------------------------------------

def _denies_component_edit_without_active_change(root: Path) -> CheckResult:
    """The core gate: an agent prompt edited with no PRD and no marker is
    refused, and the refusal names the lifecycle rather than just saying no —
    the remediation text is the reason a consultant does not simply give up and
    disable the hook."""
    name = "denies_component_edit_without_active_change"
    _no_change_active(root)
    result = _run_hook(root, edit_payload(str(root / ".claude/agents/roi-financial-modeler.md")))
    ok = (
        result.returncode == 0
        and result.denied
        and "Harness gate" in result.reason
        and "bb-prd" in result.reason
        and ".prd/ACTIVE_CHANGE" in result.reason
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:200]!r}"))


def _allows_when_prd_artifact_present(root: Path) -> CheckResult:
    """First active-change signal: `.prd/prd-v*.md` exists, i.e. `/bb-prd` has
    run for this change and there is an Eval Acceptance Criteria section for the
    build step to verify against."""
    name = "allows_when_prd_artifact_present"
    _with_prd(root)
    result = _run_hook(root, edit_payload(str(root / ".claude/agents/roi-financial-modeler.md")))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f".prd/prd-v1.md present -> rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:160]!r}"))


def _allows_when_active_change_marker_present(root: Path) -> CheckResult:
    """The other signal, authored separately because either alone passing would
    let the other be deleted unnoticed: the explicit `.prd/ACTIVE_CHANGE`
    acknowledgement, for work deliberately done outside a full cycle. This
    fixture carries NO prd-v*.md, so it can only pass via the marker."""
    name = "allows_when_active_change_marker_present"
    _with_marker(root)
    result = _run_hook(root, write_payload(str(root / "templates/outputs/roi_report.md")))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f".prd/ACTIVE_CHANGE present, no prd-v*.md -> rc={result.returncode} "
        f"denied={result.denied} stdout={result.stdout_text[:160]!r}"))


def _exempts_harness_infra_paths(root: Path) -> CheckResult:
    """The anti-deadlock list. The harness's own infrastructure — `evals/`
    (this very file), `.claude/hooks/`, `.github/`, and the vendored
    `coding-standards` skill — must stay editable with NO active change, or the
    gate cannot be built, fixed or gated in the first place. All four probed
    against a project root with no `.prd/` at all.

    WHICH PROBE IS LOAD-BEARING, AND WHY IT MATTERS FOR THE MUTATION: three of
    the four are allowed for TWO independent reasons — they are on
    EXEMPT_PREFIXES *and* they match no PROTECTED prefix. Deleting their
    exemption changes nothing (measured: the mutation came back INERT, check
    still green). That redundancy is fine as defence in depth, but it means no
    single edit can redden the check through them.

    `.claude/skills/coding-standards/SKILL.md` is different: it is caught by
    `_is_protected`'s `.claude/skills/` catch-all and is allowed ONLY because
    the exemption fires first. So the exemption list is genuinely load-bearing
    for it, and that is the probe this check's mutation targets. Distinct from
    `gates_non_exempt_skill_but_not_bb_skill`, which covers the OTHER exempt
    skill prefix (`bb-`) and the catch-all's positive half.
    """
    name = "exempts_harness_infra_paths"
    _no_change_active(root)
    probes = [
        "evals/rubrics/component/hooks/require_harness.py",
        ".claude/hooks/require-harness.py",
        ".github/workflows/evals.yml",
        ".claude/skills/coding-standards/SKILL.md",   # the load-bearing one
    ]
    outcomes = {}
    for rel in probes:
        result = _run_hook(root, write_payload(str(root / rel)))
        outcomes[rel] = (result.returncode, result.denied)
    ok = all(rc == 0 and not denied for rc, denied in outcomes.values())
    return bool_check(name, ok, detail=f"no active change -> {outcomes}")


def _gates_pipeline_python_only_by_extension(root: Path) -> CheckResult:
    """`scripts/` is protected as PIPELINE CODE, which means `.py` and not the
    shell utilities living beside it (`setup_pii.sh`, `init_engagement.sh`,
    `find_engagement.sh`). Both halves in one check because the contract is the
    SPLIT: gating the whole directory would block the setup script a consultant
    runs before the harness works at all."""
    name = "gates_pipeline_python_only_by_extension"
    _no_change_active(root)
    py = _run_hook(root, edit_payload(str(root / "scripts/orchestrate_step.py")))
    sh = _run_hook(root, edit_payload(str(root / "scripts/setup_pii.sh")))
    ok = (
        py.returncode == 0 and py.denied
        and sh.returncode == 0 and not sh.denied and sh.silent
    )
    return bool_check(name, ok, detail=(
        f"scripts/orchestrate_step.py denied={py.denied}; "
        f"scripts/setup_pii.sh denied={sh.denied}"))


def _gates_non_exempt_skill_but_not_bb_skill(root: Path) -> CheckResult:
    """`.claude/skills/**` is protected EXCEPT the vendored `bb-*` skills — the
    lifecycle's own implementation. Same split shape as the pipeline check: a
    hook that gated `bb-*` would make the harness unable to modify itself, and
    one that exempted all of `.claude/skills/` would let any other skill be
    edited outside the lifecycle."""
    name = "gates_non_exempt_skill_but_not_bb_skill"
    _no_change_active(root)
    custom = _run_hook(root, write_payload(str(root / ".claude/skills/custom-thing/SKILL.md")))
    bb = _run_hook(root, write_payload(str(root / ".claude/skills/bb-build/SKILL.md")))
    ok = (
        custom.returncode == 0 and custom.denied
        and bb.returncode == 0 and not bb.denied and bb.silent
    )
    return bool_check(name, ok, detail=(
        f".claude/skills/custom-thing/SKILL.md denied={custom.denied}; "
        f".claude/skills/bb-build/SKILL.md denied={bb.denied}"))


def _gates_root_orchestrate_py(root: Path) -> CheckResult:
    """`orchestrate.py` at the repo ROOT is pipeline code too, and it is the one
    protected path that neither PROTECTED_PREFIXES nor the `scripts/` rule
    reaches — it needs its own clause, so it needs its own check."""
    name = "gates_root_orchestrate_py"
    _no_change_active(root)
    result = _run_hook(root, edit_payload(str(root / "orchestrate.py")))
    ok = result.returncode == 0 and result.denied and "Harness gate" in result.reason
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:160]!r}"))


def _ignores_read_tool(root: Path) -> CheckResult:
    """The gate is on CHANGES, never on reading. Widening it to Read would make
    the component tree unreadable outside a change cycle — the agent could not
    even inspect what it is being asked to modify."""
    name = "ignores_read_tool"
    _no_change_active(root)
    result = _run_hook(root, read_payload(str(root / ".claude/agents/roi-financial-modeler.md")))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"Read on a protected component, no active change -> rc={result.returncode} "
        f"denied={result.denied} stdout={result.stdout_text[:160]!r}"))


# --- fail-open contract -------------------------------------------------------

def _fails_open_on_malformed_payload(root: Path) -> CheckResult:
    """Unparseable stdin allows. A component-edit gate that denied on its own
    parse failures would block every Edit in the repo the moment the payload
    shape changed."""
    name = "fails_open_on_malformed_payload"
    _no_change_active(root)
    result = _run_hook(root, b"{ not json at all")
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:160]!r}"))


def _fails_open_under_injected_fault(root: Path) -> CheckResult:
    """A real, unmocked `PermissionError` inside the active-change lookup must
    not BLOCK the edit.

    Asserts the split: with `.prd/` chmod'd to 000 a PROTECTED path must not be
    blocked, while a path outside the protected set is decided cleanly (the
    hook returns before it ever consults `.prd/`, so the fault cannot reach it).
    Without the second half, "did not block" would also be satisfied by a hook
    that had stopped deciding anything at all.

    What "does not block" means precisely: no deny envelope on stdout, and an
    exit code other than 2 — those are the only two ways a PreToolUse hook can
    stop a tool call. The hook currently achieves this by CRASHING (traceback,
    exit 1) rather than by exiting 0, which is fail-open but not cleanly so;
    that is recorded in the detail and filed in `.prd/backlog.md`, not asserted
    away and not fixed here (#197 is test-only).

    Skips under root, which bypasses directory permission bits entirely.
    """
    name = "fails_open_under_injected_fault"
    skip = fault_injection_skip(name, perms="directory")
    if skip is not None:
        return skip

    _with_prd(root)
    prd_dir = root / ".prd"
    protected = str(root / ".claude/agents/roi-financial-modeler.md")
    unprotected = str(root / "knowledge/domains/retail/benchmarks.md")

    with inject_fault(prd_dir):
        faulted = _run_hook(root, edit_payload(protected))
        control = _run_hook(root, edit_payload(unprotected))

    ok = (
        not faulted.denied and faulted.returncode != 2 and not faulted.stdout.strip()
        and control.returncode == 0 and not control.denied and control.silent
    )
    return bool_check(name, ok, detail=(
        f".prd/ chmod 000 -> protected path: rc={faulted.returncode} "
        f"denied={faulted.denied} crashed={crashed(faulted)} (exit!=2 and no deny "
        f"envelope, so the tool call proceeds — fail-open by crash, see "
        f".prd/backlog.md); unprotected path (fault unreachable): "
        f"rc={control.returncode} denied={control.denied}"))


# --- process contract ---------------------------------------------------------

def _invoked_as_subprocess_not_import(root: Path) -> CheckResult:
    """Two invocations of the SAME absolute path under two different
    `CLAUDE_PROJECT_DIR` roots — see `_common.py` for why the differential is
    the real proof. `require-harness` classifies a path by making it relative to
    PROJECT_DIR, so the identical file is a protected component under root A
    (deny) and an unrecognised absolute path under root B (allow). An
    import-once hook binds PROJECT_DIR at module load and cannot produce both.
    """
    a_root = root / "project_a"
    b_root = root / "project_b"
    _no_change_active(a_root)
    _no_change_active(b_root)
    component = str(a_root / ".claude/agents/roi-financial-modeler.md")

    return check_invoked_as_subprocess_not_import(
        _hook_path(),
        hook_label="require-harness.py",
        observe_a=lambda: _run_hook(a_root, edit_payload(component)).denied,
        observe_b=lambda: _run_hook(b_root, edit_payload(component)).denied,
        what="denied",
    )


def _runs_under_registered_interpreter(root: Path) -> CheckResult:
    """#192/backlog :116 — spawned under the interpreter
    `.claude/settings.json` registers (bare `python3`), never the eval runner's
    `sys.executable`. `spawn` goes through this row's own `_run_hook`."""
    _with_marker(root)
    return check_runs_under_registered_interpreter(
        _hook_path(),
        hook_label="require-harness.py",
        spawn=lambda: _run_hook(root, edit_payload(str(root / "knowledge/probe.md"))),
    )


def _denies_when_every_prd_is_closed(root: Path) -> CheckResult:
    """THE deployment regression, as a fixture: a tree whose only PRDs have
    shipped is NOT a tree with a change running, and the gate must still refuse.
    `_allows_when_prd_artifact_present` alone cannot catch this — it passes
    whether the hook reads statuses or just counts files."""
    name = "denies_when_every_prd_is_closed"
    _with_closed_prds(root)
    result = _run_hook(root, edit_payload(str(root / ".claude/agents/roi-financial-modeler.md")))
    ok = result.returncode == 0 and result.denied and "Harness gate" in result.reason
    return bool_check(name, ok, detail=(
        f"prd-v1(archived)+prd-v2(built), no ACTIVE_CHANGE -> rc={result.returncode} "
        f"denied={result.denied} reason={result.reason[:120]!r}"))


def _allows_when_prd_in_flight(root: Path) -> CheckResult:
    """The other half of the status rule: a PRD that has NOT shipped is exactly
    what an open cycle looks like, and must still open the gate. Authored
    opposite the check above so a hook that denied everything could not pass."""
    name = "allows_when_prd_in_flight"
    prd = root / ".prd"
    prd.mkdir(parents=True, exist_ok=True)
    (prd / "prd-v1.md").write_text(_prd_text(1, "archived"), encoding="utf-8")
    (prd / "prd-v2.md").write_text(_prd_text(2, "draft"), encoding="utf-8")
    result = _run_hook(root, edit_payload(str(root / ".claude/agents/roi-financial-modeler.md")))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"prd-v1(archived)+prd-v2(draft) -> rc={result.returncode} "
        f"denied={result.denied} stdout={result.stdout_text[:120]!r}"))


def _repo_prd_state_matches_gate(root: Path) -> CheckResult:
    """Deployment-level, not synthetic: run the hook over THIS repo's real
    `.prd/prd-v*.md` files and require its verdict to match what those files
    actually say. Every other check in this row builds its own tidy fixture and
    so can stay green while the shipped repo state defeats the gate — which is
    precisely what happened (measured 2026-08-28: 6 shipped PRDs, gate open on
    every clone, this row fully green). `ACTIVE_CHANGE` is deliberately NOT
    copied: it is gitignored and machine-local, so it must not decide what a
    clone of `main` does."""
    name = "repo_prd_state_matches_gate"
    statuses = _repo_prd_statuses()
    if not statuses:
        return bool_check(name, False, detail=(
            "no .prd/prd-v*.md in the repo — this check cannot be vacuous; "
            "if the planning dir moved, retarget it rather than deleting it"))

    closed_set = {"archived", "built", "superseded", "shipped", "done", "abandoned", "merged"}
    in_flight = sorted(f for f, s in statuses.items() if s not in closed_set)
    closed = sorted(f for f, s in statuses.items() if s in closed_set)

    if not closed:
        return bool_check(name, False, detail=(
            f"no SHIPPED PRD among {sorted(statuses)} — the shipped-PRD half of this "
            "check would be vacuous. PRDs are the permanent record; if none is closed, "
            "the statuses are not being maintained"))

    component = ".claude/agents/roi-financial-modeler.md"

    def _verdict(names: list[str], sub: str) -> bool:
        prd = (root / sub / ".prd")
        prd.mkdir(parents=True, exist_ok=True)
        for fname in names:
            (prd / fname).write_bytes((repo_root() / ".prd" / fname).read_bytes())
        return _run_hook(root / sub, edit_payload(str(root / sub / component))).denied

    # (a) The repo exactly as it stands: the hook must agree with what the front
    #     matter says, whichever way that falls.
    got_all = _verdict(sorted(statuses), "as_is")
    want_all = not in_flight

    # (b) The shipped PRDs ALONE — the state a clone of `main` is in once the
    #     in-flight work merges and its PRD is marked built. Asserted separately
    #     because (a) alone stops discriminating the moment one draft PRD exists
    #     locally, which is exactly when this check is most needed.
    got_closed = _verdict(closed, "closed_only")

    ok = got_all == want_all and got_closed is True
    return bool_check(name, ok, detail=(
        f"{len(statuses)} real PRD(s); in-flight={in_flight or 'none'}; "
        f"shipped={len(closed)} -> as-is: want denied={want_all} got {got_all}; "
        f"shipped-only: want denied=True got {got_closed}"))


def evaluate(target: str) -> list:  # noqa: ARG001 - self-contained, ignores target
    missing = missing_hook_check(_hook_path())
    if missing is not None:
        return [missing]
    return [
        run_in_tmp(_denies_component_edit_without_active_change, prefix=TMP_PREFIX),
        run_in_tmp(_allows_when_prd_artifact_present, prefix=TMP_PREFIX),
        run_in_tmp(_denies_when_every_prd_is_closed, prefix=TMP_PREFIX),
        run_in_tmp(_allows_when_prd_in_flight, prefix=TMP_PREFIX),
        run_in_tmp(_repo_prd_state_matches_gate, prefix=TMP_PREFIX),
        run_in_tmp(_allows_when_active_change_marker_present, prefix=TMP_PREFIX),
        run_in_tmp(_exempts_harness_infra_paths, prefix=TMP_PREFIX),
        run_in_tmp(_gates_pipeline_python_only_by_extension, prefix=TMP_PREFIX),
        run_in_tmp(_gates_non_exempt_skill_but_not_bb_skill, prefix=TMP_PREFIX),
        run_in_tmp(_gates_root_orchestrate_py, prefix=TMP_PREFIX),
        run_in_tmp(_ignores_read_tool, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_on_malformed_payload, prefix=TMP_PREFIX),
        run_in_tmp(_fails_open_under_injected_fault, prefix=TMP_PREFIX),
        run_in_tmp(_invoked_as_subprocess_not_import, prefix=TMP_PREFIX),
        run_in_tmp(_runs_under_registered_interpreter, prefix=TMP_PREFIX),
    ]
