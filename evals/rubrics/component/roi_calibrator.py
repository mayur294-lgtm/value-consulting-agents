"""roi-calibrator component evaluator (objective, code-only — no LLM).

`tools/roi_calibrator.py` shapes the scenario curves and expansion proposals
that feed the ROI model, but had no eval row (ticket #200). Every check here
IMPORTS AND CALLS the real `ROICalibrator` class against real fixtures —
never a text/regex scan of the source — matching the executable-tier bar
`rubrics/component/roi_excel_generator.py` sets (generate, then inspect real
values).

  - assess_report_well_formed
        ROICalibrator(config).assess() must run clean and return the
        contract downstream callers rely on (segment/current_roi/status/
        metrics/proposals/projected_roi_with_all, with the expected numeric
        metrics keys). Mutation: a config whose `implementation_curve` is
        explicitly `null` (present, not merely absent — so `.get(key,
        default)` returns None, not the default) must make
        compute_roi_metrics's `impl[yr]` indexing raise; the check must FAIL
        clean on that, not swallow it.
  - scenario_curve_shape_valid
        Every implementation/effectiveness curve — the golden's own
        `backbase_loading`, every `scenarios.*` entry it carries, AND the
        real `SEGMENT_BENCHMARKS` table's `impl_curve_moderate` /
        `eff_curve_moderate` for all 5 segments — must be a 5-element,
        [0,1]-bounded, non-decreasing ramp that plateaus near 1.0. Mutation:
        a non-monotonic dip in effectiveness_curve must be rejected.
  - cap_parity_with_artifact_boundary
        roi_calibrator.py carries NO cap constant of its own — it never caps
        `backbase_impact`. So "parity" with `artifact_boundary.cap_roi_config`
        (MAX_BACKBASE_IMPACT = 0.60) can only be shown behaviorally: (1)
        cap_roi_config caps the committed overcap fixture's 0.75 down to
        exactly 0.60 and leaves the clean golden untouched (no false
        positive); (2) ROICalibrator, run on the CAPPED config, never
        proposes a config_patch whose own `backbase_impact` exceeds that same
        0.60 — the only way the two modules' notion of "the cap" can drift
        apart is via a stray patch on the calibrator side, and none exists
        today. Mutation: the same recursive scanner, given a synthetic
        0.93-impact patch injected alongside the real ones, must flag it —
        proving the detector works independent of what the calibrator
        happens to emit right now.
  - conservative_anchor_invariant
        `_check_scenario_differentiation()` should NOT fire on the golden
        (conservative ≈ 0.79x moderate — well below the 0.85 anchor-violation
        threshold) and SHOULD fire once conservative is pushed to ~95% of
        moderate per lever (anchor violated). Both directions are exercised
        directly against the real method.

target: path to a roi_config.json golden fixture — the SAME shape
roi-excel-generator's `input:` uses (evals/goldens/roi_config_provenance.json
is the intended registry wiring; it already carries `scenarios` and
`value_lever_groups`, so no new fixture file is needed for this row).
cap_parity_with_artifact_boundary additionally loads its own sibling fixture
(evals/goldens/roi_config_overcap.json, already committed for ticket #104's
cap-gate negative) directly, the same pattern roi-excel-generator's
sources_sheet_absent_when_unset check uses for ITS sibling fixture — the
registry only wires one `input:` slot per component, so a check whose
contract is inherently about a SECOND fixture loads it itself.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from rubrics.base import CheckResult, repo_root
from rubrics._harness import bool_check, run_in_tmpdir

_OVERCAP_GOLDEN = "evals/goldens/roi_config_overcap.json"


def _bc(name: str, ok: bool, *, detail: str, exercised: str, hard_fail: bool = True) -> CheckResult:
    result = bool_check(name, ok, detail=detail, hard_fail=hard_fail)
    result.exercised = exercised
    return result


def _ensure_repo_on_path() -> Path:
    root = repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def _load_config(target: str) -> tuple[dict | None, str | None]:
    p = Path(target)
    if not p.exists():
        return None, f"fixture not found: {target}"
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"


# ─────────────────────────────────────────────────────────────────────
# assess_report_well_formed
# ─────────────────────────────────────────────────────────────────────

_REQUIRED_TOP_KEYS = {"segment", "current_roi", "expected_range", "status",
                      "metrics", "proposals", "projected_roi_with_all"}
_REQUIRED_METRICS_KEYS = {"roi_percent", "npv", "payback_years",
                          "total_benefits_5yr", "total_investment_5yr"}


def _assess_report_well_formed(_td: Path, config: dict) -> CheckResult:
    name = "assess_report_well_formed"
    _ensure_repo_on_path()
    try:
        from tools.roi_calibrator import ROICalibrator
    except ImportError as e:
        return _bc(name, False, detail=f"import failed: {e}", exercised="import only (failed)")

    def _assess(cfg: dict) -> dict:
        return ROICalibrator(copy.deepcopy(cfg)).assess()

    try:
        report = _assess(config)
    except Exception as e:  # noqa: BLE001 - a calibrator crash is a clean check failure
        return _bc(name, False, detail=f"assess() raised on golden config: {type(e).__name__}: {e}",
                   exercised="tools.roi_calibrator.ROICalibrator(config).assess()")

    missing = _REQUIRED_TOP_KEYS - set(report)
    metrics = report.get("metrics", {}) if isinstance(report.get("metrics"), dict) else {}
    metrics_missing = _REQUIRED_METRICS_KEYS - set(metrics)
    well_formed = not missing and not metrics_missing and isinstance(report.get("proposals"), list)
    if not well_formed:
        return _bc(name, False,
                   detail=f"missing top-level keys={sorted(missing)}, missing metrics keys={sorted(metrics_missing)}",
                   exercised="tools.roi_calibrator.ROICalibrator(config).assess()")

    # Mutation proof: implementation_curve explicitly null (not absent) must
    # crash compute_roi_metrics's list-indexing — the check must fail clean.
    mutated = copy.deepcopy(config)
    mutated.setdefault("backbase_loading", {})["implementation_curve"] = None
    crashed = False
    crash_detail = ""
    try:
        _assess(mutated)
    except Exception as e:  # noqa: BLE001 - expected: this IS the mutation proof
        crashed = True
        crash_detail = f"{type(e).__name__}: {e}"
    if not crashed:
        return _bc(name, False,
                   detail="mutation proof failed: implementation_curve=None did not raise — "
                          "compute_roi_metrics silently tolerated a null curve",
                   exercised="tools.roi_calibrator.ROICalibrator(mutated).assess()")

    return _bc(name, True,
               detail=f"assess() well-formed on golden (segment={report['segment']}, "
                      f"ROI={report['current_roi']}%); implementation_curve=None mutation "
                      f"correctly raises ({crash_detail})",
               exercised="tools.roi_calibrator.ROICalibrator(config).assess() x2 (golden + mutated)")


# ─────────────────────────────────────────────────────────────────────
# scenario_curve_shape_valid
# ─────────────────────────────────────────────────────────────────────

def _valid_curve(vals, tol: float = 1e-6) -> tuple[bool, str]:
    if not isinstance(vals, list) or len(vals) != 5:
        return False, f"not a 5-element list: {vals!r}"
    for i, v in enumerate(vals):
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            return False, f"index {i} not numeric: {v!r}"
        if v < -tol or v > 1.0 + tol:
            return False, f"index {i} out of [0,1]: {v}"
    for i in range(1, len(vals)):
        if vals[i] < vals[i - 1] - tol:
            return False, f"non-monotonic at index {i}: {vals[i]} < {vals[i - 1]}"
    if vals[-1] < 0.95:
        return False, f"final value {vals[-1]} does not plateau near 1.0"
    return True, "ok"


def _scenario_curve_shape_valid(_td: Path, config: dict) -> CheckResult:
    name = "scenario_curve_shape_valid"
    _ensure_repo_on_path()
    try:
        from tools.roi_calibrator import SEGMENT_BENCHMARKS
    except ImportError as e:
        return _bc(name, False, detail=f"import failed: {e}", exercised="import only (failed)")

    problems: list[str] = []
    bl = config.get("backbase_loading", {})
    for key in ("implementation_curve", "effectiveness_curve"):
        ok, why = _valid_curve(bl.get(key))
        if not ok:
            problems.append(f"backbase_loading.{key}: {why}")

    scenarios = config.get("scenarios") or {}
    for sc_name, sc in scenarios.items():
        if not isinstance(sc, dict):
            continue
        for key in ("implementation_curve", "effectiveness_curve"):
            ok, why = _valid_curve(sc.get(key))
            if not ok:
                problems.append(f"scenarios.{sc_name}.{key}: {why}")

    for seg_name, seg in SEGMENT_BENCHMARKS.items():
        for key in ("impl_curve_moderate", "eff_curve_moderate"):
            ok, why = _valid_curve(seg.get(key))
            if not ok:
                problems.append(f"SEGMENT_BENCHMARKS[{seg_name}].{key}: {why}")

    if problems:
        return _bc(name, False, detail="; ".join(problems[:5]),
                   exercised="tools.roi_calibrator.SEGMENT_BENCHMARKS + golden's backbase_loading/scenarios")

    # Mutation proof: a non-monotonic dip mid-ramp must be rejected.
    dipped = [0.34, 0.10, 0.90, 1.00, 1.00]
    ok, why = _valid_curve(dipped)
    if ok:
        return _bc(name, False,
                   detail=f"mutation proof failed: non-monotonic dip {dipped} was not detected as invalid",
                   exercised="_valid_curve()")

    return _bc(name, True,
               detail=f"{len(SEGMENT_BENCHMARKS)} benchmark segment curve pairs + golden's "
                      f"backbase_loading and {len(scenarios)} scenario curve set(s) all well-shaped; "
                      f"non-monotonic-dip mutation correctly rejected ({why})",
               exercised="tools.roi_calibrator.SEGMENT_BENCHMARKS + golden's backbase_loading/scenarios")


# ─────────────────────────────────────────────────────────────────────
# cap_parity_with_artifact_boundary
# ─────────────────────────────────────────────────────────────────────

def _scan_for_overcap_impacts(obj, cap: float, path: str = "root") -> list[str]:
    """Recursively scan a JSON-like structure for a `backbase_impact` value
    (bare numeric, or {'value': numeric}) exceeding `cap`."""
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "backbase_impact":
                val = v.get("value") if isinstance(v, dict) else v
                if isinstance(val, (int, float)) and not isinstance(val, bool) and val > cap + 1e-9:
                    hits.append(f"{path}.{k}={val}")
            hits.extend(_scan_for_overcap_impacts(v, cap, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(_scan_for_overcap_impacts(v, cap, f"{path}[{i}]"))
    return hits


def _cap_parity_with_artifact_boundary(td: Path, config: dict) -> CheckResult:
    name = "cap_parity_with_artifact_boundary"
    root = _ensure_repo_on_path()
    try:
        from scripts.artifact_boundary import cap_roi_config, MAX_BACKBASE_IMPACT
        from tools.roi_calibrator import ROICalibrator
    except ImportError as e:
        return _bc(name, False, detail=f"import failed: {e}", exercised="import only (failed)")

    overcap_path = root / _OVERCAP_GOLDEN
    if not overcap_path.exists():
        return _bc(name, False, detail=f"sibling fixture not found: {_OVERCAP_GOLDEN}",
                   exercised="filesystem check only")

    exercised = ("scripts.artifact_boundary.cap_roi_config() on evals/goldens/"
                "roi_config_{overcap,provenance}.json + tools.roi_calibrator.ROICalibrator.assess()")

    # 1) cap_roi_config must cap the overcap fixture's 0.75 -> exactly 0.60,
    #    mutating a TEMP COPY (cap_roi_config writes the config back in place).
    overcap_tmp = td / "roi_config_overcap.json"
    overcap_tmp.write_text(overcap_path.read_text())
    report = cap_roi_config(str(overcap_tmp))
    capped = json.loads(overcap_tmp.read_text())
    driver = (capped.get("value_lever_groups", {}).get("L1_deposit_activation", {})
              .get("revenue_drivers", {}).get("funded_balance_nii", {}))
    capped_val = driver.get("inputs", {}).get("backbase_impact", {}).get("value")
    if not report.get("modified") or capped_val is None or abs(capped_val - MAX_BACKBASE_IMPACT) > 1e-9:
        return _bc(name, False,
                   detail=f"cap_roi_config did not cap the overcap fixture to MAX_BACKBASE_IMPACT="
                          f"{MAX_BACKBASE_IMPACT}: modified={report.get('modified')}, capped value={capped_val}",
                   exercised=exercised)

    # 2) negative control: cap_roi_config must NOT touch the clean golden.
    clean_tmp = td / "roi_config_clean.json"
    clean_tmp.write_text(json.dumps(config))
    clean_report = cap_roi_config(str(clean_tmp))
    if clean_report.get("modified"):
        return _bc(name, False,
                   detail="cap_roi_config modified the clean (non-overcap) golden — false positive",
                   exercised=exercised)

    # 3) parity: the calibrator's own proposal config_patches, computed on
    #    the now-CAPPED config, must never independently exceed that cap.
    #    roi_calibrator.py has no cap constant of its own, so this is the
    #    only way the two modules' notion of "the cap" can be shown to agree.
    calibrator = ROICalibrator(copy.deepcopy(capped))
    calibrator.assess()
    patches = [p.config_patch for p in calibrator.proposals]
    over = _scan_for_overcap_impacts(patches, MAX_BACKBASE_IMPACT)
    if over:
        return _bc(name, False,
                   detail=f"calibrator proposal config_patch(es) exceed the boundary's cap: {over}",
                   exercised=exercised)

    # 4) mutation proof: the SAME scanner must catch an injected over-cap
    #    patch — proves detection works, independent of what today's
    #    calibrator happens to emit.
    poisoned = patches + [{"inputs": {"backbase_impact": {"value": 0.93}}}]
    poisoned_hits = _scan_for_overcap_impacts(poisoned, MAX_BACKBASE_IMPACT)
    if not poisoned_hits:
        return _bc(name, False,
                   detail="mutation proof failed: an injected 0.93 backbase_impact (cap=0.60) was not detected",
                   exercised=exercised)

    return _bc(name, True,
               detail=f"MAX_BACKBASE_IMPACT={MAX_BACKBASE_IMPACT}: overcap fixture capped 0.75→{capped_val}; "
                      f"clean golden untouched; calibrator's {len(patches)} proposal patch(es) on the capped "
                      f"config stay within the cap; injected-0.93 mutation correctly caught ({poisoned_hits})",
               exercised=exercised)


# ─────────────────────────────────────────────────────────────────────
# conservative_anchor_invariant
# ─────────────────────────────────────────────────────────────────────

def _conservative_anchor_invariant(_td: Path, config: dict) -> CheckResult:
    name = "conservative_anchor_invariant"
    _ensure_repo_on_path()
    try:
        from tools.roi_calibrator import ROICalibrator
    except ImportError as e:
        return _bc(name, False, detail=f"import failed: {e}", exercised="import only (failed)")

    scenarios = config.get("scenarios") or {}
    if "conservative" not in scenarios or "moderate" not in scenarios:
        return _bc(name, False,
                   detail="golden fixture has no scenarios.conservative/moderate to test the invariant against",
                   exercised="tools.roi_calibrator.ROICalibrator._check_scenario_differentiation()")

    exercised = "tools.roi_calibrator.ROICalibrator._check_scenario_differentiation() x2 (golden + mutated)"

    def _conservative_flagged(cfg: dict) -> bool:
        calibrator = ROICalibrator(copy.deepcopy(cfg))
        calibrator._check_scenario_differentiation()
        return any(p.category == "scenario_calibration" and "Conservative" in p.lever_name
                   for p in calibrator.proposals)

    if _conservative_flagged(config):
        return _bc(name, False,
                   detail="golden fixture's conservative scenario is well below moderate "
                          "(expected ratio well under the 0.85 anchor threshold) yet was flagged anyway "
                          "— false positive",
                   exercised=exercised)

    # Mutation: raise conservative's backbase_impacts to 95% of moderate's,
    # per shared lever key — the anchor invariant (conservative should sit
    # ~40-60% of moderate) is now violated and MUST be flagged.
    mutated = copy.deepcopy(config)
    mod_impacts = mutated["scenarios"]["moderate"].get("backbase_impacts", {})
    mutated["scenarios"]["conservative"]["backbase_impacts"] = {
        k: round(v * 0.95, 4) for k, v in mod_impacts.items()
    }
    if not _conservative_flagged(mutated):
        return _bc(name, False,
                   detail="mutation proof failed: conservative raised to 95% of moderate per lever "
                          "did not trigger the 'Conservative ≈ Moderate' proposal",
                   exercised=exercised)

    return _bc(name, True,
               detail="golden (conservative well below moderate) correctly NOT flagged; "
                      "conservative-raised-to-95%-of-moderate mutation correctly flagged",
               exercised=exercised)


CHECKS = {
    "assess_report_well_formed": _assess_report_well_formed,
    "scenario_curve_shape_valid": _scenario_curve_shape_valid,
    "cap_parity_with_artifact_boundary": _cap_parity_with_artifact_boundary,
    "conservative_anchor_invariant": _conservative_anchor_invariant,
}


def evaluate(target: str) -> list[CheckResult]:
    """target: path to a roi_config.json golden fixture (expected registry
    wiring: evals/goldens/roi_config_provenance.json — already carries
    `scenarios` and `value_lever_groups`, no new fixture needed)."""
    config, err = _load_config(target)
    if err:
        return [CheckResult(name, 0.0, False, hard_fail=True, detail=err) for name in CHECKS]
    return [run_in_tmpdir(fn, config) for fn in CHECKS.values()]
