"""ignite-workshop-synthesizer component evaluator — deterministic code checks only.

Thin adapter (same pattern as roi_financial_modeler.py): run_experiment.py
resolves the evaluator as `rubrics.component.ignite_workshop_synthesizer` and calls `evaluate(target)`
with a single arg. The check logic lives in `specifics._ignite_synth`. Judges are NOT
run here — the component gate is the deterministic `code:` checks declared in
the registry; the semantic judges run through the agent-style path.
"""
from __future__ import annotations

from rubrics.base import CheckResult  # noqa: F401  (re-exported type for callers)
from rubrics.component.specifics import _read, _ignite_synth


def evaluate(target: str) -> list[CheckResult]:
    return _ignite_synth(_read(target))
