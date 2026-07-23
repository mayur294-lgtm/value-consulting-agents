"""roi-financial-modeler component evaluator — deterministic code checks only.

The check logic lives in `specifics._roi_modeler` (shared with the agent-style
evaluator). The bb-build verify path (`run_experiment.py --component
roi-financial-modeler`) resolves the evaluator as `rubrics.component.<name>` and
calls `evaluate(target)` with a single arg, so this thin module adapts that
interface to the shared logic.

Judges are intentionally NOT run here — this is the deterministic gate declared
in PRD v1 (the `code:` checks in the registry). The governance baseline + judges
are exercised through the agent-style path, not this component gate.
"""
from __future__ import annotations

from rubrics.base import CheckResult  # noqa: F401  (re-exported type for callers)
from rubrics.component.specifics import _read, _roi_modeler


def evaluate(target: str) -> list[CheckResult]:
    return _roi_modeler(_read(target))
