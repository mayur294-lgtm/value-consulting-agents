"""roi-hypothesis-builder component evaluator — deterministic code checks only.

Thin adapter (same pattern as roi_financial_modeler.py): run_experiment.py
resolves the evaluator as `rubrics.component.roi_hypothesis_builder` and calls `evaluate(target)`
with a single arg. The check logic lives in `specifics._roi_hypothesis`. Judges are NOT
run here — the component gate is the deterministic `code:` checks declared in
the registry; the semantic judges run through the agent-style path.
"""
from __future__ import annotations

from rubrics.base import CheckResult  # noqa: F401  (re-exported type for callers)
from rubrics.component._calibration import RUBRIC_ROW_DOC, calibration_banner
from rubrics.component.specifics import _read, _roi_hypothesis


# --- rubric_calibration tier (#201) ---------------------------------------
RUBRIC_ROW = 'roi-hypothesis-rubric'          # the registry key; `--component roi-hypothesis-rubric`
COVERS_AGENT = 'roi-hypothesis-builder'   # INERT DOCUMENTATION — not a verification claim
GOLDEN = 'evals/goldens/roi_hypothesis_golden.md'
__doc__ = (__doc__ or "") + RUBRIC_ROW_DOC.format(row=RUBRIC_ROW, agent=COVERS_AGENT)


def evaluate(target: str) -> list[CheckResult]:
    calibration_banner(RUBRIC_ROW, COVERS_AGENT, GOLDEN)
    return _roi_hypothesis(_read(target))
