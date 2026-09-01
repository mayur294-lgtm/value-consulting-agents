"""knowledge-harvester component evaluator — deterministic gate for
scripts.artifact_boundary.synthetic_policy() (ticket #130).

Registers knowledge-harvester as an eval component for the first time. Unlike
the other component evaluators in this package, this one does NOT score agent
prose against a golden markdown transcript — it pins the shared gate function
(synthetic_policy) and the knowledge-harvester agent's quarantine-mode output
contract deterministically, at threshold 1.0, with no judge. `target` is the
resolved `evals/goldens/synthetic_gate/` directory (registry `input:`), which
holds three committed sub-fixtures: quarantine_case/, never_case/, bare_tests_case/.

Four checks (registry.yaml `components.knowledge-harvester.code`):
  - quarantine_policy_detected    synthetic_policy(quarantine_case) == ("quarantine", …)
  - never_policy_detected         synthetic_policy(never_case) == ("never", …)
  - bare_tests_fails_safe         path-based fail-safe: no marker + a `tests`
                                   path segment → "quarantine" (simulated path —
                                   see bare_tests_case/README.md for why the
                                   fixture's own location can't exercise this)
  - quarantine_mode_outputs_local parses .claude/agents/knowledge-harvester.md
                                   for a "### Mode: quarantine" block and checks
                                   every declared `outputs:` path starts with
                                   {engagement_dir} and none are under knowledge/.
                                   That mode does not exist yet (lands in #131),
                                   so this check SKIPs (not fails) until then.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from rubrics.base import CheckResult, repo_root


def _bool_check(name: str, ok: bool, *, hard_fail: bool = True, detail: str = "") -> CheckResult:
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=hard_fail, detail=detail)


def _import_synthetic_policy():
    root = repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from scripts.artifact_boundary import synthetic_policy
    return synthetic_policy


def _check_quarantine_policy_detected(goldens_dir: Path, synthetic_policy) -> CheckResult:
    name = "quarantine_policy_detected"
    case = goldens_dir / "quarantine_case"
    if not case.exists():
        return _bool_check(name, False, detail=f"fixture not found: {case}")
    policy, reason = synthetic_policy(case)
    ok = policy == "quarantine"
    return _bool_check(name, ok, detail=f"synthetic_policy({case}) -> ({policy!r}, {reason!r})")


def _check_never_policy_detected(goldens_dir: Path, synthetic_policy) -> CheckResult:
    name = "never_policy_detected"
    case = goldens_dir / "never_case"
    if not case.exists():
        return _bool_check(name, False, detail=f"fixture not found: {case}")
    policy, reason = synthetic_policy(case)
    ok = policy == "never"
    return _bool_check(name, ok, detail=f"synthetic_policy({case}) -> ({policy!r}, {reason!r})")


def _check_bare_tests_fails_safe(goldens_dir: Path, synthetic_policy) -> CheckResult:
    """No-marker fail-safe: synthetic_policy() on a path with a `tests` segment
    (relative to the repo root) and no `.synthetic` marker anywhere in its walk
    must resolve to "quarantine". The path is simulated — it need not exist on
    disk, since the gate only checks for a `.synthetic` FILE, and a nonexistent
    directory simply has none — because the committed bare_tests_case/ fixture
    intentionally lives OUTSIDE tests/ (see its README.md) and so can't exercise
    this branch by its own location. We still require the committed fixture to
    be present, as a symmetry/documentation check on the goldens set."""
    name = "bare_tests_fails_safe"
    case = goldens_dir / "bare_tests_case"
    if not case.exists():
        return _bool_check(name, False, detail=f"fixture not found: {case}")

    root = repo_root()
    simulated = root / "tests" / "engagements" / "_synthetic_gate_eval_simulated_case"
    policy, reason = synthetic_policy(simulated)
    ok = policy == "quarantine"
    return _bool_check(
        name, ok,
        detail=f"synthetic_policy({simulated}) -> ({policy!r}, {reason!r}); bare_tests_case/ fixture present",
    )


_MODE_HEADING_RE = re.compile(r"^###[ \t]+Mode:[ \t]*quarantine[ \t]*$", re.M)
_NEXT_HEADING_RE = re.compile(r"^(?:###[ \t]+Mode:|##[ \t]+)\S", re.M)
_OUTPUTS_LIST_RE = re.compile(r"^outputs:[ \t]*\n((?:^[ \t]*-[ \t].*\n?)+)", re.M)
_LIST_ITEM_RE = re.compile(r"^[ \t]*-[ \t]*(.+?)[ \t]*$", re.M)


def _check_quarantine_mode_outputs_local(agent_md: Path) -> CheckResult:
    name = "quarantine_mode_outputs_local"
    if not agent_md.exists():
        return _bool_check(name, False, detail=f"{agent_md} not found")

    text = agent_md.read_text(errors="replace")
    heading = _MODE_HEADING_RE.search(text)
    if not heading:
        # The quarantine mode block doesn't exist yet — it lands in ticket #131.
        # Not a failure of this ticket's contract: skip gracefully.
        return CheckResult(
            name, 1.0, True, skipped=True,
            detail="no '### Mode: quarantine' block yet in knowledge-harvester.md — lands in #131",
        )

    rest = text[heading.end():]
    nxt = _NEXT_HEADING_RE.search(rest)
    block = rest[: nxt.start()] if nxt else rest

    outputs_match = _OUTPUTS_LIST_RE.search(block)
    if not outputs_match:
        return _bool_check(name, False, detail="'### Mode: quarantine' block found but has no 'outputs:' list")

    items = [m.group(1).strip().strip('"').strip("'") for m in _LIST_ITEM_RE.finditer(outputs_match.group(1))]
    if not items:
        return _bool_check(name, False, detail="'outputs:' list under quarantine mode is empty")

    bad = [p for p in items if not p.startswith("{engagement_dir}")]
    under_knowledge = [p for p in items if "knowledge/" in p]
    ok = not bad and not under_knowledge
    detail = f"{len(items)} output path(s); not-{{engagement_dir}}-scoped: {bad or 'none'}; under knowledge/: {under_knowledge or 'none'}"
    return _bool_check(name, ok, detail=detail)


def evaluate(target: str) -> list[CheckResult]:
    goldens_dir = Path(target)
    synthetic_policy = _import_synthetic_policy()
    agent_md = repo_root() / ".claude" / "agents" / "knowledge-harvester.md"

    return [
        _check_quarantine_policy_detected(goldens_dir, synthetic_policy),
        _check_never_policy_detected(goldens_dir, synthetic_policy),
        _check_bare_tests_fails_safe(goldens_dir, synthetic_policy),
        _check_quarantine_mode_outputs_local(agent_md),
    ]
