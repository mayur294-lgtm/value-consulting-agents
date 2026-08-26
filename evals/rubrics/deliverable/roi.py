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


def _find_lever_groups(data: dict) -> tuple[object, str | None]:
    """Locate the per-lever driver container under whichever key the current
    (or a still-recognized prior) roi_config contract uses. Returns
    (raw_value, key_name); raw_value may be the WRONG shape (a list where a
    dict is required, etc.) — callers decide malformed vs unscorable from
    that. (None, None) means neither recognized key is present at all.

    `value_lever_groups` is the current roi-financial-modeler contract
    (.claude/agents/roi-financial-modeler.md). `journeys` is the same
    dict-of-dicts shape under the pre-rename key, still seen in committed
    fixtures (e.g. tests/engagements/pbcom_demo) — kept for backward compat,
    matching the same fallback already used by artifact_boundary.py and
    rubrics/component/specifics.py (`data.get("value_lever_groups",
    data.get("journeys", {}))`)."""
    for key in ("value_lever_groups", "journeys"):
        if key in data:
            return data[key], key
    return None, None


def _iter_group_drivers(groups: dict):
    """Yield every revenue_drivers/cost_drivers driver (a dict) inside a
    value_lever_groups/journeys dict-of-dicts container. Silently skips
    entries of the wrong type — callers count parsed-vs-not themselves."""
    for group in groups.values():
        if not isinstance(group, dict):
            continue
        for driver_type in ("revenue_drivers", "cost_drivers"):
            drivers = group.get(driver_type)
            if not isinstance(drivers, dict):
                continue
            for driver in drivers.values():
                if isinstance(driver, dict):
                    yield driver


def _driver_backbase_impact(driver: dict):
    """A driver's Backbase-impact ratio, wherever the current contract puts
    it: `inputs.backbase_impact.value` (the documented shape — roi-financial-
    modeler.md "backbase_impact as an input key"), a bare `inputs.
    backbase_impact` number, or (seen in Managed Hosting commercial configs,
    e.g. tests/roi_pipeline_v2/managed_hosting_commercial_test) a bare
    top-level `backbase_impact` on the driver itself. Returns None if none
    of those parse as a number."""
    inputs = driver.get("inputs")
    bi = inputs.get("backbase_impact") if isinstance(inputs, dict) else None
    val = bi.get("value") if isinstance(bi, dict) else bi
    if isinstance(val, (int, float)):
        return val
    top = driver.get("backbase_impact")
    return top if isinstance(top, (int, float)) else None


def _driver_derivable(driver: dict) -> bool:
    """A driver carries enough for Y1-Y5 dollar values to be DERIVED under
    the current formula-based contract. There is no literal per-lever
    `values: [y1..y5]` array any more (that was the legacy `levers` schema
    this rubric used to require) — Y1-Y5 = baseline_annual x backbase_impact
    x the scenario implementation/effectiveness curves. A driver qualifies
    when it has EITHER (baseline_annual + a backbase_impact), OR — the
    roi_excel_generator.py-documented fallback for when no backbase_impact
    input is carried (real in Seabank/HNB `journeys` configs) — a
    precomputed `potential_annual_benefit` on its own."""
    baseline = driver.get("baseline_annual")
    has_baseline = isinstance(baseline, (int, float)) and baseline > 0
    has_impact = _driver_backbase_impact(driver) is not None
    has_pab = isinstance(driver.get("potential_annual_benefit"), (int, float))
    return (has_baseline and has_impact) or has_pab


def _check_schema_parsed(data: dict) -> CheckResult:
    """NEW (:41) — dedicated structural-shape check. Distinguishes a
    genuinely malformed value_lever_groups (FAILS — a real defect: e.g. an
    array where the contract requires a dict-of-dicts) from a config that
    doesn't carry this key/shape at all (unscorable — nothing to be
    malformed about; per #179 a parser gap must never render as 0/0)."""
    raw, key = _find_lever_groups(data)
    if raw is None:
        return CheckResult("value_lever_groups_schema_parsed", 0.0, False, unscorable=True,
                            detail="expected a `value_lever_groups` (or legacy `journeys`) dict of "
                                   "lever groups, each with revenue_drivers/cost_drivers dicts — "
                                   "neither key is present; unrecognized roi_config schema")
    if not isinstance(raw, dict) or not raw:
        return CheckResult("value_lever_groups_schema_parsed", 0.0, False,
                            detail=f"'{key}' must be a non-empty dict keyed by lever ID "
                                   f"(agent contract: \"MUST be a dict of dicts — NOT an array\"); "
                                   f"got {type(raw).__name__}")
    malformed: list[str] = []
    driver_count = 0
    for gkey, group in raw.items():
        if not isinstance(group, dict):
            malformed.append(f"{gkey}: group is not an object")
            continue
        for driver_type in ("revenue_drivers", "cost_drivers"):
            drivers = group.get(driver_type)
            if drivers is None:
                continue
            if not isinstance(drivers, dict):
                malformed.append(f"{gkey}.{driver_type}: expected a dict keyed by driver ID, "
                                  f"got {type(drivers).__name__} (agent contract: \"NOT an array\")")
                continue
            for dkey, driver in drivers.items():
                if isinstance(driver, dict):
                    driver_count += 1
                else:
                    malformed.append(f"{gkey}.{driver_type}.{dkey}: driver is not an object")
    if driver_count == 0:
        extra = f" ({'; '.join(malformed[:3])})" if malformed else ""
        return CheckResult("value_lever_groups_schema_parsed", 0.0, False,
                            detail=f"'{key}' parsed as a dict but no revenue_drivers/cost_drivers "
                                   f"entries were readable{extra}")
    ok = not malformed
    score = 1.0 if ok else max(0.0, 1 - 0.2 * len(malformed))
    detail = f"{driver_count} driver(s) parsed under '{key}'"
    if malformed:
        detail += f"; {len(malformed)} malformed: {'; '.join(malformed[:3])}"
    return CheckResult("value_lever_groups_schema_parsed", score, ok, detail=detail)


def _check_levers_have_5yr_values(data: dict) -> CheckResult:
    raw, key = _find_lever_groups(data)
    legacy = data.get("levers")
    if raw is None and isinstance(legacy, list) and legacy:
        # Pre-value_lever_groups schema: a flat lever list with an explicit
        # per-lever Y1-Y5 `values` array. Still recognized for backward compat.
        well = sum(1 for l in legacy if isinstance(l, dict)
                   and isinstance(l.get("values"), list) and len(l["values"]) >= 5)
        return CheckResult("levers_have_5yr_values", well / len(legacy), well == len(legacy),
                            detail=f"{well}/{len(legacy)} levers with Y1-Y5 values (legacy `levers` schema)")
    if raw is None:
        return CheckResult("levers_have_5yr_values", 0.0, False, unscorable=True,
                            detail="no value_lever_groups/journeys/levers key present — unrecognized roi_config schema")
    if not isinstance(raw, dict) or not raw:
        return CheckResult("levers_have_5yr_values", 0.0, False,
                            detail=f"'{key}' present but not a non-empty dict — cannot derive Y1-Y5 values")
    drivers = list(_iter_group_drivers(raw))
    if not drivers:
        return CheckResult("levers_have_5yr_values", 0.0, False,
                            detail=f"'{key}' parsed but no revenue_drivers/cost_drivers found")
    well = sum(1 for d in drivers if _driver_derivable(d))
    return CheckResult("levers_have_5yr_values", well / len(drivers), well == len(drivers),
                        detail=f"{well}/{len(drivers)} levers carry baseline_annual+backbase_impact "
                               f"or a precomputed potential_annual_benefit (current `{key}` schema)")


def _check_assumptions_sourced(data: dict) -> CheckResult:
    assumptions = data.get("assumptions_register", data.get("assumptions"))
    if assumptions is None:
        return CheckResult("assumptions_sourced", 0.0, False, unscorable=True,
                            detail="no assumptions_register/assumptions key present — unrecognized roi_config schema")
    if not isinstance(assumptions, list) or not assumptions:
        return CheckResult("assumptions_sourced", 0.0, False,
                            detail=f"assumptions_register present but not a non-empty list (got {type(assumptions).__name__})")

    def _attributed(a) -> bool:
        if not isinstance(a, dict):
            return False
        has_confidence = bool(a.get("confidence"))
        # The current contract's field name is `validation_owner`; `source`,
        # `owner` (older fixtures) and `validation` (workshop-style
        # registers, e.g. tests/engagements/harborlight_synthetic) are also
        # seen in the wild carrying the same attribution role.
        has_attribution = bool(a.get("source") or a.get("validation_owner")
                                or a.get("owner") or a.get("validation"))
        return has_confidence and has_attribution

    sourced = sum(1 for a in assumptions if _attributed(a))
    return CheckResult("assumptions_sourced", sourced / len(assumptions), sourced == len(assumptions),
                        detail=f"{sourced}/{len(assumptions)} assumptions fully attributed (confidence + source/owner)")


def _eval_json(data: dict) -> list[CheckResult]:
    checks: list[CheckResult] = []
    scen = data.get("scenarios", {})
    checks.append(CheckResult("three_scenarios", min(1.0, len(scen) / 3.0), len(scen) >= 3,
                              detail=f"{len(scen)} scenarios"))
    checks.append(_check_levers_have_5yr_values(data))
    checks.append(_check_assumptions_sourced(data))
    inv = data.get("investment", {})
    checks.append(CheckResult("investment_block", 1.0 if inv else 0.0, bool(inv),
                              detail="present" if inv else "no investment block"))
    checks.append(_check_schema_parsed(data))
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
    # Semantic judges (auto-skip without ANTHROPIC_API_KEY). conservative_bias is an
    # integrity judge → critical (a real fail hard-fails, no averaging-away).
    from rubrics.judge.judge import judge
    checks.append(judge("conservative_bias", text, snapshot="design-system-frozen.md",
                        threshold=0.8, critical=True))
    checks.append(judge("topdown_bottomup_correlation", text, snapshot=None, threshold=0.75))
    return checks
