"""Redirect evaluator for the agent names that no longer name a gate (#201).

`--component market-context-researcher` used to resolve to a row that scored a
frozen prose golden and reported 1.000 PASS — while the agent's prompt could be
replaced with one line of garbage without moving the number. Those rows are now
`rubric_calibration:` rows keyed by RUBRIC (see `_calibration.py` for the full
rationale), so the agent name resolves to nothing that gates.

Deleting the key outright would make `run_experiment.py --component
market-context-researcher` die on a bare `KeyError`, which teaches the reader
nothing. Instead each retired agent name keeps a REDIRECT row in `components:`
(`retired: true`, no `code:`, no `input:`) pointing at this module, which always
HARD-FAILS with the mapping and the distinction. It can never be green, so it
can never be quoted as evidence about anything.

`check_registry.py` enforces the shape of those rows — `retired: true` implies no
`code:`, no `input:`, this evaluator, and a `moved_to:` that names a real
`rubric_calibration` row — so a redirect stub cannot quietly grow back into a
gate. `.github/workflows/evals.yml` reads the same `retired:` flag and skips
these rows instead of running them, so editing one of these agents' prompts
neither hard-errors CI ("no row in registry.yaml") nor runs a rubric that would
have told the reviewer nothing about the prompt they changed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from rubrics.base import CheckResult, repo_root

CHECK_NAME = "component_row_retired_use_rubric_calibration"


def _registry() -> dict:
    try:
        return yaml.safe_load((repo_root() / "evals" / "registry.yaml").read_text()) or {}
    except (OSError, yaml.YAMLError):
        return {}


def _mapping() -> list[tuple[str, str]]:
    """(agent name, rubric row) for every retired redirect row, read live from
    the registry so this module can never drift from it."""
    reg = _registry()
    out = []
    for name, spec in (reg.get("components") or {}).items():
        if isinstance(spec, dict) and spec.get("retired") and spec.get("moved_to"):
            out.append((str(name), str(spec["moved_to"])))
    return sorted(out)


def _requested_name() -> str:
    """The agent name the caller typed, recovered from this process's own argv.

    Best-effort only: the runner resolves an evaluator by module name and hands
    `evaluate()` a target, so there is no other channel. When it cannot be
    recovered the message below still prints the whole mapping table, which is
    the useful part.
    """
    argv = sys.argv
    for i, a in enumerate(argv):
        if a == "--component" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--component="):
            return a.split("=", 1)[1]
    return ""


_RULE = "─" * 78


def message(asked: str, pairs: list[tuple[str, str]]) -> str:
    row = dict(pairs).get(asked, "")
    head = (
        f"`--component {asked}` is RETIRED — an agent name no longer names a gate.\n"
        f"  Run instead:  --calibration {row}   (tier: rubric_calibration)\n"
        if asked and row else
        "This component row is RETIRED — an agent name no longer names a gate.\n"
    )
    table = "\n".join(
        f"    {agent:<34} ->  --calibration {target_row}"
        + ("   <-- you asked for this" if agent == asked else "")
        for agent, target_row in pairs
    )
    return (
        f"\n{_RULE}\n"
        f"  RETIRED COMPONENT ROW — nothing was scored.\n"
        f"{_RULE}\n"
        f"  {head}\n"
        f"  Why: that row never gated the agent. It scored a frozen synthetic prose\n"
        f"  golden with a deterministic rubric — replacing the agent's entire prompt\n"
        f"  with one line of garbage left it at 1.000 PASS. The rows are now\n"
        f"  `rubric_calibration:` rows keyed by RUBRIC: they score the RUBRIC, not\n"
        f"  the component, and say so on every run.\n"
        f"\n"
        f"  Nothing in path 2 verifies an agent PROMPT. If you changed a prompt and\n"
        f"  want evidence, run path-1 regeneration locally:\n"
        f"      python evals/path1.py --agent <agent-name> --input <golden>\n"
        f"\n"
        f"  Retired agent name  ->  calibration row\n"
        f"{table}\n"
        f"{_RULE}"
    )


def evaluate(target: str) -> list[CheckResult]:  # noqa: ARG001 - self-contained
    pairs = _mapping()
    asked = _requested_name()
    row = dict(pairs).get(asked, "")
    try:
        print(message(asked, pairs), flush=True)
    except Exception:  # noqa: BLE001 - the verdict below is what gates, not the print
        pass
    detail = (
        f"RETIRED: `{asked}` is an agent name, not a gate — run `--calibration {row}` "
        f"(tier: rubric_calibration, scores the RUBRIC not the agent). See the block above."
        if asked and row else
        "RETIRED: this agent name no longer names a gate — see the block above for the "
        "agent -> rubric_calibration row mapping."
    )
    return [CheckResult(
        CHECK_NAME, 0.0, False, hard_fail=True,
        detail=detail,
        exercised=f"{Path(__file__).name}: redirect only — no rubric ran, nothing was scored",
    )]
