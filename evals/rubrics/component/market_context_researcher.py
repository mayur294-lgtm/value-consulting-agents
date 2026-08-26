"""market-context-researcher component evaluator — deterministic code checks only.

Thin adapter (same pattern as roi_financial_modeler.py): run_experiment.py
resolves the evaluator as `rubrics.component.market_context_researcher` and calls `evaluate(target)`
with a single arg. The check logic lives in `specifics._market_context`. Judges are NOT
run here — the component gate is the deterministic `code:` checks declared in
the registry; the semantic judges run through the agent-style path.
"""
from __future__ import annotations

from rubrics.base import CheckResult  # noqa: F401  (re-exported type for callers)
from rubrics.component._calibration import RUBRIC_ROW_DOC, calibration_banner
from rubrics.component.specifics import _read, _market_context


# --- rubric_calibration tier (#201) ---------------------------------------
RUBRIC_ROW = 'market-context-rubric'          # the registry key; `--calibration market-context-rubric`
COVERS_AGENT = 'market-context-researcher'   # INERT DOCUMENTATION — not a verification claim
GOLDEN = 'evals/goldens/market_context_golden.md'
__doc__ = (__doc__ or "") + RUBRIC_ROW_DOC.format(row=RUBRIC_ROW, agent=COVERS_AGENT)


def evaluate(target: str) -> list[CheckResult]:
    calibration_banner(RUBRIC_ROW, COVERS_AGENT, GOLDEN)
    return _market_context(_read(target))
