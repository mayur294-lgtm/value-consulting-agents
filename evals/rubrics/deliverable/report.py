"""Narrative report deliverable eval (assessment_report.md / executive_summary.md).

This is the prose deliverable — so it's judge-heavy (tone + grounding + assumption
discipline) on top of the governance baseline. Code checks are light (structure);
the quality is qualitative, which is exactly what the judges cover.

evaluate(target, context=None):
  context = the source evidence/transcript, if available → enables grounding judge.
"""
from __future__ import annotations

import re
from pathlib import Path

from rubrics.base import CheckResult
from rubrics.component.governance import evaluate as governance_evaluate


def evaluate(target: str, context: str | None = None) -> list[CheckResult]:
    text = Path(target).read_text(errors="replace") if Path(target).exists() else target
    checks: list[CheckResult] = []

    # --- light structural code checks ------------------------------------------
    has_exec = bool(re.search(r"executive summary", text, re.I))
    checks.append(CheckResult("exec_summary_present", 1.0 if has_exec else 0.0, has_exec,
                              detail="present" if has_exec else "no Executive Summary"))
    has_reco = bool(re.search(r"\b(go|no-go|conditional go|recommendation)\b", text, re.I))
    checks.append(CheckResult("clear_recommendation", 1.0 if has_reco else 0.0, has_reco,
                              detail="recommendation stated" if has_reco else "no clear recommendation"))

    # --- governance baseline (evidence/assumptions/provenance/faithful) --------
    checks += governance_evaluate(target, context=context)

    # --- qualitative judges (auto-skip without ANTHROPIC_API_KEY) --------------
    from rubrics.judge.judge import judge
    checks.append(judge("report_tone", text, snapshot="output-standards-frozen.md", threshold=0.8))
    # integrity judge — critical: a real fail hard-fails the rubric (no averaging-away)
    checks.append(judge("assumption_discipline", text, snapshot="output-standards-frozen.md",
                        threshold=0.8, critical=True))
    if context is not None:
        ctx = Path(context).read_text(errors="replace") if Path(context).exists() else context
        # SOFT (not critical): the report is HYBRID — factual findings (should trace to
        # evidence) plus legitimately generative content (modeled ROI, proposed use cases,
        # benchmarks). A critical transcript-faithfulness judge would over-fire on the
        # generative parts. Unsourced/aggressive assumptions are still hard-caught by the
        # critical assumption_discipline judge above.
        checks.append(judge("evidence_grounding", f"INPUT:\n{ctx[:25000]}\n\nOUTPUT:\n{text[:25000]}",
                            snapshot=None, threshold=0.85, critical=False))
    return checks
