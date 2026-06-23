"""ROI deliverable code-evaluators (objective, no LLM).

Handles both the markdown report (roi_report.md) and the machine-readable
config (roi_config.json). Every check maps to a documented ROI defect:
  - missing annual-report / top-down baseline  (the NFIS Module-1 miss)
  - scenarios incomplete                        (must have 3)
  - assumptions not sourced                      (register rule)
  - leftover (Placeholder) content               (unfinished model)
  - NPV / ROI / payback absent                   (no headline financials)
Semantic checks (conservative bias, top-down<->bottom-up correlation) are the
LLM-judge rubrics in rubrics/judge — not here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from rubrics.base import CheckResult


def _eval_markdown(text: str) -> list[CheckResult]:
    low = text.lower()
    checks: list[CheckResult] = []

    has_exec = bool(re.search(r"##\s*\d*\.?\s*executive summary", low))
    checks.append(CheckResult("executive_summary_present", 1.0 if has_exec else 0.0,
                              has_exec, detail="present" if has_exec else "no Executive Summary section"))

    scenarios = sum(1 for s in ("conservative", "moderate", "aspirational") if s in low)
    checks.append(CheckResult("three_scenarios", scenarios / 3.0, scenarios >= 3,
                              detail=f"{scenarios}/3 named scenarios"))

    has_assump = bool(re.search(r"assumptions? register", low))
    sourced = len(re.findall(r"source\s*:", low))
    checks.append(CheckResult("assumptions_sourced", 1.0 if (has_assump and sourced >= 3) else (0.5 if has_assump else 0.0),
                              has_assump and sourced >= 3,
                              detail=f"register={'yes' if has_assump else 'no'}, {sourced} source: tags"))

    # The documented miss — annual-report / top-down baseline bridged to findings.
    topdown = bool(re.search(r"annual report|statement of income|top-down|10-k|call report|ncua", low))
    checks.append(CheckResult("annual_report_topdown_present", 1.0 if topdown else 0.0, topdown,
                              detail="top-down baseline referenced" if topdown else "no annual-report / top-down baseline"))

    fin = sum(1 for k in ("npv", "roi", "payback") if k in low)
    checks.append(CheckResult("headline_financials", fin / 3.0, fin >= 3,
                              detail=f"{fin}/3 of NPV/ROI/payback present"))

    placeholders = len(re.findall(r"\(placeholder\)|\bTODO\b|\{\{[a-z_]+\}\}", text, re.I))
    checks.append(CheckResult("no_placeholder_content", 1.0 if placeholders == 0 else max(0.0, 1 - 0.25 * placeholders),
                              placeholders == 0, detail=f"{placeholders} placeholder marker(s)" if placeholders else "none"))

    evidence = len(re.findall(r"\bE\d{2,}\b|\bCAP-[A-Z]", text))
    checks.append(CheckResult("evidence_referenced", 1.0 if evidence >= 5 else evidence / 5.0, evidence >= 5,
                              detail=f"{evidence} evidence/capability ID references"))
    return checks


def _eval_json(data: dict) -> list[CheckResult]:
    checks: list[CheckResult] = []
    scen = data.get("scenarios", {})
    checks.append(CheckResult("three_scenarios", min(1.0, len(scen) / 3.0), len(scen) >= 3,
                              detail=f"{len(scen)} scenarios"))
    levers = data.get("levers", [])
    well = sum(1 for l in levers if isinstance(l.get("values"), list) and len(l["values"]) >= 5)
    checks.append(CheckResult("levers_have_5yr_values", (well / len(levers)) if levers else 0.0, bool(levers) and well == len(levers),
                              detail=f"{well}/{len(levers)} levers with Y1-Y5 values"))
    assumptions = data.get("assumptions", [])
    sourced = sum(1 for a in assumptions if a.get("source") and a.get("owner") and a.get("confidence"))
    checks.append(CheckResult("assumptions_sourced", (sourced / len(assumptions)) if assumptions else 0.0,
                              bool(assumptions) and sourced == len(assumptions),
                              detail=f"{sourced}/{len(assumptions)} assumptions fully attributed (source+owner+confidence)"))
    inv = data.get("investment", {})
    checks.append(CheckResult("investment_block", 1.0 if inv else 0.0, bool(inv),
                              detail="present" if inv else "no investment block"))
    return checks


def evaluate(target: str) -> list[CheckResult]:
    p = Path(target)
    if p.suffix == ".json":
        try:
            return _eval_json(json.loads(p.read_text()))
        except json.JSONDecodeError as e:
            return [CheckResult("valid_json", 0.0, False, hard_fail=True, detail=str(e))]
    text = p.read_text(errors="replace")
    checks = _eval_markdown(text)
    # Semantic judges (auto-skip without ANTHROPIC_API_KEY).
    from rubrics.judge.judge import run_judges
    checks += run_judges(target, [("conservative_bias", "design-system-frozen.md"),
                                  ("topdown_bottomup_correlation", None)], threshold=0.75)
    return checks
