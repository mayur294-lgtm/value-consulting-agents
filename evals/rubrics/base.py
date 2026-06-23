"""Shared types for cortex eval rubrics.

A rubric is a function that takes a target (a file path or an in-memory
artifact) and returns a list of CheckResult. Code evaluators are pure Python
(objective, cheap, no LLM); judge evaluators call Claude (semantic). Both
produce CheckResult so run_experiment.py and Langfuse treat them uniformly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def repo_root() -> Path:
    """Walk up from this file to the cortex repo root (the dir holding evals/)."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "evals").is_dir() and (parent / ".claude").is_dir():
            return parent
    # Fallback: two levels up from rubrics/
    return p.parents[2]


@dataclass
class CheckResult:
    name: str
    score: float          # 0.0 .. 1.0
    passed: bool
    hard_fail: bool = False   # if set and not passed -> whole rubric fails regardless of mean score
    skipped: bool = False     # e.g. judge with no API key; excluded from scoring
    detail: str = ""
    evidence: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.score = max(0.0, min(1.0, float(self.score)))


@dataclass
class RubricResult:
    target: str
    altitude: str          # unit | pipeline | deliverable
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def score(self) -> float:
        scored = [c for c in self.checks if not c.skipped]
        if not scored:
            return 0.0
        return sum(c.score for c in scored) / len(scored)

    @property
    def hard_failed(self) -> bool:
        return any(c.hard_fail and not c.passed for c in self.checks)

    def passed(self, threshold: float) -> bool:
        return (self.score >= threshold) and not self.hard_failed

    def report(self, threshold: float) -> str:
        lines = [
            f"Target:   {self.target}",
            f"Altitude: {self.altitude}",
            f"Score:    {self.score:.3f}  (threshold {threshold:.2f})",
            f"Verdict:  {'PASS' if self.passed(threshold) else 'FAIL'}"
            + ("  [HARD FAIL]" if self.hard_failed else ""),
            "",
        ]
        for c in self.checks:
            if c.skipped:
                mark = "SKIP"
            elif c.passed:
                mark = "PASS"
            elif c.hard_fail:
                mark = "HARD-FAIL"
            else:
                mark = "fail"
            lines.append(f"  [{mark:>9}] {c.name}: {c.score:.2f}  {c.detail}")
            for ev in c.evidence[:8]:
                lines.append(f"        - {ev}")
        return "\n".join(lines)
