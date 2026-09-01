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
    exercised: str | None = None  # e.g. "scripts/pii/engine.py via python3 (3.9.6)" — what actually ran
    unscorable: bool = False      # rubric parser could not read the artifact; excluded from scoring,
                                   # never rendered as 0/0 — a parser gap is not a quality finding

    def __post_init__(self) -> None:
        self.score = max(0.0, min(1.0, float(self.score)))


@dataclass
class RubricResult:
    target: str
    altitude: str          # unit | deliverable-structural | deliverable
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def score(self) -> float:
        scored = [c for c in self.checks if not c.skipped and not c.unscorable]
        if not scored:
            return 0.0
        return sum(c.score for c in scored) / len(scored)

    @property
    def all_unscorable(self) -> bool:
        """True when every non-skipped check came back unscorable (a parser gap,
        not a quality finding) — the aggregate must not read as 0.000 in that case."""
        rated = [c for c in self.checks if not c.skipped]
        return bool(rated) and all(c.unscorable for c in rated)

    @property
    def hard_failed(self) -> bool:
        return any(c.hard_fail and not c.passed for c in self.checks)

    def passed(self, threshold: float) -> bool:
        return (self.score >= threshold) and not self.hard_failed

    def report(self, threshold: float) -> str:
        if self.all_unscorable:
            verdict = "UNSCORABLE"
        elif self.passed(threshold):
            verdict = "PASS"
        else:
            verdict = "FAIL"
        # A check that was skipped AND never passed (e.g. a judge that never
        # ran — no API key, or it raised) certified nothing. That's distinct
        # from a plain skip (e.g. an intentionally absent optional check) and
        # must be visible on the mark and in the header, not silently folded
        # into the same [SKIP] line a clean skip would render.
        unverified_count = sum(1 for c in self.checks if c.skipped and not c.passed)
        verdict_line = f"Verdict:  {verdict}" + ("  [HARD FAIL]" if self.hard_failed else "")
        if unverified_count:
            plural = "" if unverified_count == 1 else "s"
            verdict_line += f"  [{unverified_count} check{plural} skipped — unverified]"
        lines = [
            f"Target:   {self.target}",
            f"Altitude: {self.altitude}",
            f"Score:    {'UNSCORABLE' if self.all_unscorable else f'{self.score:.3f}'}"
            f"  (threshold {threshold:.2f})",
            verdict_line,
            "",
        ]
        for c in self.checks:
            if c.unscorable:
                mark = "UNSCORABLE"
            elif c.skipped and not c.passed:
                mark = "SKIP*"
            elif c.skipped:
                mark = "SKIP"
            elif c.passed:
                mark = "PASS"
            elif c.hard_fail:
                mark = "HARD-FAIL"
            else:
                mark = "fail"
            lines.append(f"  [{mark:>9}] {c.name}: {c.score:.2f}  {c.detail}")
            if c.exercised and not c.skipped:
                lines.append(f"        exercised: {c.exercised}")
            for ev in c.evidence[:8]:
                lines.append(f"        - {ev}")
        return "\n".join(lines)
