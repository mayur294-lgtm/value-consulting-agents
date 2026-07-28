#!/usr/bin/env python3
"""
Artifact boundary gates — shared by the pipeline (orchestrate.py) and
standalone skill callers (/build-roi, /generate-roi-excel, /publish).

Three gates, one module, two callers:
  - cap_roi_config(path)          ROI reasonableness gate (impact caps + benchmarks)
  - deanonymize_dir(dir)          restore client names from .pii_mapping.json
  - validate_outputs(dir, type)   thin wrapper over validate_engagement_outputs.sh

This module MUST stay importable by plain python3 (3.9+): no claude_agent_sdk,
no orchestrate.py imports (dependency direction is orchestrate -> artifact_boundary),
no 3.10+ syntax.

CLI (what skills call):
    python3 scripts/artifact_boundary.py cap <roi_config.json>
    python3 scripts/artifact_boundary.py deanon <engagement_or_outputs_dir>
    python3 scripts/artifact_boundary.py validate <engagement_dir> [engagement_type]
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

# ─── Colors for terminal output (matches orchestrate.py style) ────────────────

class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def log(msg: str, color: str = ""):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.DIM}{ts}{C.RESET} {color}{msg}{C.RESET}")


# ─── ROI Reasonableness Gate (moved from orchestrate.py) ─────────────────────

MAX_BACKBASE_IMPACT = 0.60

# Segment benchmark ranges for ROI validation (from roi_calibrator.py)
SEGMENT_ROI_RANGES = {
    "Retail Banking": (100, 150),
    "Wealth Management": (120, 200),
    "Commercial Banking": (80, 140),
    "SME Banking": (70, 130),
    "Corporate Banking": (100, 150),
    "Investing": (100, 150),
}


def _compute_5yr_roi(config: dict) -> Optional[float]:
    """Compute 5-year ROI from config using curves (matching Excel logic)."""
    groups = config.get('value_lever_groups', config.get('journeys', {}))
    bl = config.get('backbase_loading', {})
    impl_curve = bl.get('implementation_curve', [0.3, 0.7, 0.8, 1.0, 1.0])
    eff_curve = bl.get('effectiveness_curve', [0.15, 0.35, 0.6, 0.85, 1.0])

    # Sum steady-state annual benefit across all drivers
    total_steady_state = 0
    for group in groups.values():
        for dtype in ('revenue_drivers', 'cost_drivers'):
            for driver in (group.get(dtype) or {}).values():
                baseline = driver.get('baseline_annual', 0)
                bi = driver.get('inputs', {}).get('backbase_impact', {})
                impact = bi.get('value', 0) if isinstance(bi, dict) else bi if isinstance(bi, (int, float)) else 0
                total_steady_state += baseline * impact
        # Add servicing analysis totals
        sa = group.get('servicing_analysis')
        if isinstance(sa, dict):
            for channel in sa.values():
                if isinstance(channel, dict):
                    for task in channel.get('tasks', []):
                        if isinstance(task, dict):
                            total_steady_state += task.get('total_saved', 0)

    # Apply curves year by year (matching Excel logic)
    total_5yr_benefit = 0
    for yr in range(5):
        impl = impl_curve[yr] if yr < len(impl_curve) else 1.0
        eff = eff_curve[yr] if yr < len(eff_curve) else 1.0
        total_5yr_benefit += total_steady_state * impl * eff

    # Sum investment
    inv = config.get('investment', {})
    total_investment = 0
    for inv_type in ('license', 'implementation'):
        inv_data = inv.get(inv_type, {})
        if isinstance(inv_data, dict):
            for yr_key in ('year_1', 'year_2', 'year_3', 'year_4', 'year_5'):
                total_investment += inv_data.get(yr_key, 0)
        elif isinstance(inv_data, (int, float)):
            total_investment += inv_data

    if total_investment <= 0:
        return None

    return (total_5yr_benefit - total_investment) / total_investment * 100


def cap_roi_config(config_path) -> dict:
    """Validate roi_config.json for unreasonable values. Caps impacts and warns.

    Moved from orchestrate.py `_validate_roi_config` — math unchanged.
    Writes the capped config back in place and returns a gate-report dict.
    """
    config_path = Path(config_path)
    report = {
        "gate": "cap_roi_config",
        "config": str(config_path),
        "exists": config_path.exists(),
        "parse_error": None,
        "warnings": [],
        "modified": False,
        "curve_roi": None,
        "segment": None,
        "benchmark_range": None,
        "passed": False,
    }
    if not config_path.exists():
        return report
    try:
        config = json.loads(config_path.read_text())
    except Exception as e:
        log(f"  ⚠ Could not parse roi_config.json: {type(e).__name__}", C.YELLOW)
        report["parse_error"] = type(e).__name__
        return report

    warnings = []
    modified = False
    total_benefit = 0
    client_revenue = config.get('bank_profile', {}).get('total_revenue', 0)

    groups = config.get('value_lever_groups', config.get('journeys', {}))
    for group_key, group in groups.items():
        for driver_type in ('revenue_drivers', 'cost_drivers'):
            for drv_key, driver in (group.get(driver_type) or {}).items():
                bi = driver.get('inputs', {}).get('backbase_impact', {})
                val = bi.get('value', 0) if isinstance(bi, dict) else bi if isinstance(bi, (int, float)) else 0
                if isinstance(val, (int, float)) and val > MAX_BACKBASE_IMPACT:
                    warnings.append(
                        f"    {drv_key}: backbase_impact {val:.0%} → capped to {MAX_BACKBASE_IMPACT:.0%}"
                    )
                    if isinstance(bi, dict):
                        bi['value'] = MAX_BACKBASE_IMPACT
                    modified = True
                baseline = driver.get('baseline_annual', 0)
                impact = bi.get('value', 0.30) if isinstance(bi, dict) else bi if isinstance(bi, (int, float)) else 0.30
                total_benefit += baseline * impact

    # Cap scenario-level impacts
    for sc_name, sc in (config.get('scenarios') or {}).items():
        if not isinstance(sc, dict):
            continue
        for imp_key, imp_val in (sc.get('backbase_impacts') or {}).items():
            if isinstance(imp_val, (int, float)) and imp_val > MAX_BACKBASE_IMPACT:
                warnings.append(
                    f"    Scenario '{sc_name}' impact '{imp_key}': {imp_val:.0%} → capped to {MAX_BACKBASE_IMPACT:.0%}"
                )
                sc['backbase_impacts'][imp_key] = MAX_BACKBASE_IMPACT
                modified = True

    # --- OVERESTIMATION CHECKS ---
    investment = config.get('total_investment', 0)
    if investment > 0 and total_benefit > 0:
        five_yr_roi_simple = (total_benefit * 5 - investment) / investment * 100
        if five_yr_roi_simple > 500:
            warnings.append(
                f"    5-year ROI (simple) = {five_yr_roi_simple:.0f}% — exceeds 500% threshold, review baselines"
            )

    if client_revenue > 0 and total_benefit > client_revenue * 0.05:
        warnings.append(
            f"    Total annual benefit ${total_benefit:,.0f} exceeds 5% of client revenue ${client_revenue:,.0f}"
        )

    # --- UNDERESTIMATION CHECK (NEW) ---
    # Compute curve-adjusted ROI (matches Excel logic)
    curve_roi = _compute_5yr_roi(config)
    if curve_roi is not None:
        # Detect segment
        industry = config.get('industry', '').lower()
        segment = "Retail Banking"  # default
        for seg_name in SEGMENT_ROI_RANGES:
            if seg_name.lower().replace(' ', '') in industry.replace(' ', '').lower():
                segment = seg_name
                break
        if 'wealth' in industry:
            segment = "Wealth Management"
        elif 'invest' in industry:
            segment = "Investing"
        elif 'commercial' in industry:
            segment = "Commercial Banking"
        elif 'sme' in industry or 'small' in industry:
            segment = "SME Banking"
        elif 'corporate' in industry:
            segment = "Corporate Banking"

        low, high = SEGMENT_ROI_RANGES.get(segment, (60, 150))
        log(f"  📊 Curve-adjusted 5-year ROI: {curve_roi:.0f}% (segment: {segment}, benchmark: {low}-{high}%)", C.CYAN)
        report["curve_roi"] = curve_roi
        report["segment"] = segment
        report["benchmark_range"] = [low, high]

        if curve_roi < low:
            warnings.append(
                f"    ⚠ ROI {curve_roi:.0f}% is BELOW {segment} benchmark range ({low}-{high}%). "
                f"Consider: (1) review backbase_impact values — may be too conservative, "
                f"(2) check if implementation/effectiveness curves are too slow, "
                f"(3) run roi_calibrator.py --config roi_config.json for expansion proposals, "
                f"(4) verify investment isn't over-estimated."
            )
        elif curve_roi > high:
            warnings.append(
                f"    ⚠ ROI {curve_roi:.0f}% is ABOVE {segment} benchmark range ({low}-{high}%). "
                f"A consultant presenting {curve_roi:.0f}% ROI will lose credibility. "
                f"Review: (1) attribution — are top levers genuinely Backbase-driven or bank strategic decisions? "
                f"(2) baselines — is the full customer base addressable or only digitally active subset? "
                f"(3) backbase_impact — any P3 assumptions above 0.40 should be reduced, "
                f"(4) investment — is it adequate for a bank this size? "
                f"(5) interdependency — apply 10-20% haircut if multiple levers share the same customer base."
            )

    if warnings:
        log("  ⚠ ROI VALIDATION WARNINGS:", C.YELLOW)
        for w in warnings:
            log(w, C.YELLOW)

    if modified:
        config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
        log(f"  ✓ roi_config.json updated — impacts capped at {MAX_BACKBASE_IMPACT:.0%}", C.GREEN)
    elif not warnings:
        log("  ✓ roi_config.json passed reasonableness checks", C.GREEN)

    report["warnings"] = warnings
    report["modified"] = modified
    report["passed"] = not warnings
    return report


# ─── De-anonymization Gate (moved from orchestrate.py run_pipeline step 6b) ──

def deanonymize_dir(outputs_dir, mapping_file=None) -> dict:
    """Restore client names in final outputs using .pii_mapping.json.

    Moved from orchestrate.py run_pipeline step 6b. A missing mapping is
    reported LOUDLY as "NOT client-ready" — never silently skipped — and no
    file is modified in that case.

    mapping_file defaults to <outputs_dir parent>/.pii_mapping.json (the
    pipeline layout, where outputs_dir = engagement_dir/outputs), falling
    back to <outputs_dir>/.pii_mapping.json for standalone callers.
    """
    outputs_dir = Path(outputs_dir)
    if mapping_file is None:
        candidate = outputs_dir.parent / ".pii_mapping.json"
        if not candidate.exists():
            local = outputs_dir / ".pii_mapping.json"
            candidate = local if local.exists() else candidate
        mapping_file = candidate
    mapping_file = Path(mapping_file)

    report = {
        "gate": "deanonymize_dir",
        "outputs_dir": str(outputs_dir),
        "mapping_file": str(mapping_file),
        "client_ready": False,
        "files_restored": 0,
        "error": None,
    }

    if not mapping_file.exists():
        log(f"  ✗ NO PII MAPPING FOUND ({mapping_file.name}) — outputs are NOT client-ready.", C.RED)
        log("    Outputs may still contain anonymization placeholders. "
            "Run the pipeline's anonymization step or supply the mapping file "
            "before sharing anything with the client.", C.RED)
        report["error"] = "missing_pii_mapping"
        return report

    log("  Restoring client names in final outputs...", C.CYAN)
    try:
        from anonymize_transcript import deanonymize_text
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from anonymize_transcript import deanonymize_text

    try:
        pii_mapping = json.loads(mapping_file.read_text())
        if pii_mapping:
            deanon_count = 0
            for out_file in outputs_dir.iterdir():
                if out_file.suffix in ('.md', '.html', '.json', '.txt') and not out_file.name.startswith('interim'):
                    content = out_file.read_text()
                    restored = deanonymize_text(content, pii_mapping)
                    if restored != content:
                        out_file.write_text(restored)
                        deanon_count += 1
            log(f"  ✓ De-anonymized {deanon_count} output file(s)")
            report["files_restored"] = deanon_count
        report["client_ready"] = True
    except Exception as e:
        log(f"  ⚠ De-anonymization failed: {type(e).__name__} — outputs may contain placeholders", C.YELLOW)
        report["error"] = type(e).__name__
    return report


# ─── Output Validation Gate (moved from orchestrate.py step_validate) ────────

def validate_outputs(engagement_dir, engagement_type: str = "assessment") -> dict:
    """Run the validation gate script (thin wrapper over validate_engagement_outputs.sh)."""
    engagement_dir = Path(engagement_dir)
    script = REPO_ROOT / "scripts" / "validate_engagement_outputs.sh"
    report = {
        "gate": "validate_outputs",
        "engagement_dir": str(engagement_dir),
        "engagement_type": engagement_type,
        "passed": False,
        "skipped": False,
    }
    if not script.exists():
        log("  ⚠ validate_engagement_outputs.sh not found — skipping", C.YELLOW)
        report["passed"] = True
        report["skipped"] = True
        return report

    result = subprocess.run(
        ["bash", str(script), str(engagement_dir), engagement_type],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        log("  ✓ Validation gate PASSED", C.GREEN)
        report["passed"] = True
    else:
        log(f"  ✗ Validation gate FAILED:\n{result.stdout}\n{result.stderr}", C.RED)
    return report


# ─── Minimal CLI for skill callers ────────────────────────────────────────────

def _usage() -> str:
    return (
        "Usage:\n"
        "  python3 scripts/artifact_boundary.py cap <roi_config.json>\n"
        "  python3 scripts/artifact_boundary.py deanon <engagement_or_outputs_dir>\n"
        "  python3 scripts/artifact_boundary.py validate <engagement_dir> [engagement_type]\n"
    )


def main(argv) -> int:
    if len(argv) < 2:
        print(_usage(), file=sys.stderr)
        return 2

    cmd = argv[0]
    if cmd == "cap":
        report = cap_roi_config(argv[1])
        print(json.dumps(report, indent=2))
        if not report["exists"] or report["parse_error"]:
            return 1
        return 0
    elif cmd == "deanon":
        target = Path(argv[1])
        # Accept either an engagement dir (containing outputs/) or an outputs dir
        outputs_dir = target / "outputs" if (target / "outputs").is_dir() else target
        report = deanonymize_dir(outputs_dir)
        print(json.dumps(report, indent=2))
        return 0 if report["client_ready"] else 1
    elif cmd == "validate":
        engagement_type = argv[2] if len(argv) > 2 else "assessment"
        report = validate_outputs(argv[1], engagement_type)
        print(json.dumps(report, indent=2))
        return 0 if report["passed"] else 1
    else:
        print(_usage(), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
