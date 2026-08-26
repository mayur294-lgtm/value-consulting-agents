"""Per-agent component specifics — the objective, code-only checks that sit ON TOP
of the governance baseline.

governance.py already covers EVERY agent's cross-cutting rules (evidence tracing,
assumptions + confidence, provenance, faithfulness). This module adds the
agent-SPECIFIC structural checks derived from two authoritative sources:

  1. tests/quality_metrics.yaml — the existing per-agent structural rules
     (e.g. capability-assessment "Uses 0-4 maturity scale", narrative-assembler
     "Has 7 acts"). These are reused verbatim where they exist.
  2. the agent's own contract in .claude/agents/*.md — required sections, ID
     formats, scenario names, lifecycle tags, phase counts, etc.

Every check is OBJECTIVE (pure regex/Python, no LLM — semantic judging lives in
rubrics/judge), CONSERVATIVE (soft scores; hard_fail only for genuinely
load-bearing structural contracts), and GROUNDED (each maps to a yaml rule or a
contract clause — no invented rules).

Public API:
  SPECIFICS: dict[agent_name -> check_fn(text) -> list[CheckResult]]
  evaluate(agent_name, target[, context]) -> list[CheckResult]
      = governance baseline + that agent's specifics (if any).

Follows governance.py's _read(target) convention: target may be a file path or
raw text.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from rubrics.base import CheckResult, repo_root
from rubrics.component import governance
from rubrics.judge.judge import judge


def _read(x: str) -> str:
    try:
        p = Path(x)
        return p.read_text(errors="replace") if p.exists() else x
    except (OSError, ValueError):
        return x


def _count(pattern: str, text: str, flags: int = re.I) -> int:
    return len(re.findall(pattern, text, flags))


def _present(pattern: str, text: str, flags: int = re.I) -> bool:
    return bool(re.search(pattern, text, flags))


def _ratio_check(name: str, found: int, target: int, *, hard_fail: bool = False,
                 detail: str = "") -> CheckResult:
    """A soft check that scores found/target and passes at >= target."""
    score = 1.0 if found >= target else (found / target if target else 0.0)
    return CheckResult(name, score, found >= target, hard_fail=hard_fail,
                       detail=detail or f"{found}/{target}")


def _bool_check(name: str, ok: bool, *, hard_fail: bool = False, soft_floor: float = 0.0,
                detail: str = "") -> CheckResult:
    """A boolean check; when failing, scores soft_floor (default 0.0)."""
    return CheckResult(name, 1.0 if ok else soft_floor, ok, hard_fail=hard_fail, detail=detail)


# ---------------------------------------------------------------------------
# discovery-transcript-interpreter
#   yaml: Evidence Register, E\d+:, Pain Points, Metrics, stakeholder attribution
#   contract: E-IDs (E1..), lifecycle tags Acquire/Activate/Expand/Retain
# ---------------------------------------------------------------------------
def _discovery(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    ev_ids = _count(r"\bE\d+\b", text)
    out.append(_ratio_check("evidence_ids_wellformed", min(ev_ids, 5), 5,
                            detail=f"{ev_ids} well-formed E# evidence IDs"))
    has_reg = _present(r"evidence\s+register|##\s*evidence", text)
    out.append(_bool_check("evidence_register_present", has_reg,
                           detail="Evidence Register section present" if has_reg else "no Evidence Register"))
    lifecycle = sum(1 for t in ("acquire", "activate", "expand", "retain")
                    if _present(rf"\b{t}\b", text))
    out.append(_ratio_check("lifecycle_tags_present", lifecycle, 2,
                            detail=f"{lifecycle}/4 lifecycle stages (Acquire/Activate/Expand/Retain) tagged"))
    has_pain = _present(r"pain\s*point|##\s*pain", text)
    out.append(_bool_check("pain_points_present", has_pain, soft_floor=0.0,
                           detail="Pain Point register present" if has_pain else "no Pain Points"))
    return out


# ---------------------------------------------------------------------------
# capability-assessment
#   yaml: 0-4 scale (| [0-4] |), Exec Summary, Heatmap, Front/Middle/Back,
#         Unconsidered, Data&Intelligence, E\d+
#   contract: CAP-R-/CAP-W- IDs
# ---------------------------------------------------------------------------
def _capability(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    scale = _count(r"\|\s*[0-4]\s*\|", text, re.I)
    out.append(_ratio_check("maturity_scale_0_4", scale, 3,
                            detail=f"{scale} table cells using the 0-4 maturity scale"))
    has_exec = _present(r"##\s*\d*\.?\s*executive summary", text)
    out.append(_bool_check("executive_summary_present", has_exec,
                           detail="Executive Summary present" if has_exec else "no Executive Summary"))
    layers = sum(1 for l in ("front", "middle", "back") if _present(rf"\b{l}\b", text))
    out.append(_ratio_check("front_middle_back_layers", layers, 3,
                            detail=f"{layers}/3 Front/Middle/Back layer references"))
    has_unconsidered = _present(r"unconsidered", text)
    out.append(_bool_check("unconsidered_needs_present", has_unconsidered,
                           detail="Unconsidered Needs present" if has_unconsidered else "no Unconsidered Needs"))
    cap_ids = _count(r"\bCAP-[A-Z0-9-]+\b", text, re.I)
    ev_ids = _count(r"\bE\d+\b", text)
    refs = cap_ids + ev_ids
    out.append(_ratio_check("scores_have_evidence_refs", min(refs, 5), 5,
                            detail=f"{cap_ids} CAP- IDs + {ev_ids} E# refs grounding scores"))
    return out


# ---------------------------------------------------------------------------
# market-context-researcher
#   contract: 4 modules; Module 1 = annual report / financial metrics (the
#             documented NFIS miss); competitor/benchmark section.
# ---------------------------------------------------------------------------
def _market_context(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    # The documented Module-1 miss: annual-report / top-down financial baseline.
    topdown = _present(r"annual report|statement of income|10-k|call report|ncua|"
                       r"top-down|revenue bridge|financial metrics", text)
    out.append(_bool_check("annual_report_attempted", topdown,
                           detail="annual-report / top-down financial baseline referenced"
                           if topdown else "MODULE-1 MISS: no annual-report / top-down metrics"))
    # Module 1 metrics actually present (correlation to findings).
    module1 = _present(r"module\s*1|bottom-up|correlation", text)
    out.append(_bool_check("module1_metrics_present", module1, soft_floor=0.5,
                           detail="Module 1 / bottom-up correlation present" if module1
                           else "no explicit Module 1 / correlation section"))
    competitor = _present(r"competitor|benchmark|peer|module\s*3", text)
    out.append(_bool_check("competitor_benchmark_section", competitor,
                           detail="competitor/benchmark section present" if competitor
                           else "no competitor/benchmark section"))
    return out


# ---------------------------------------------------------------------------
# roi-financial-modeler
#   contract: 3 scenarios (Conservative/Moderate/Aggressive); assumptions
#             register; NPV/ROI/payback headline; gap-based impacts.
#   yaml(roi-business-case-builder): NPV, scenarios, Assumptions, sensitivity.
#   #85 provenance contract: top-level `sources` list; every basic_information
#   value field carries a `<field>_source` + `<field>_confidence` companion
#   (HIGH/MEDIUM/LOW/ASSUMPTION); operating_costs is DERIVED (revenue x
#   cost-to-income) and says so in its `_source` note, not a bare hardcoded
#   number. These are structural, code-only checks on the config JSON that
#   feed tools/roi_excel_generator.py (#83/#84) — see roi_excel_generator.py
#   in this package for the matching GENERATOR-side render checks.
# ---------------------------------------------------------------------------
_VALID_CONFIDENCE = {"HIGH", "MEDIUM", "LOW", "ASSUMPTION"}

# Ticket #104 (A4 — ROI gate wiring in the ROI skills) — parity eval case.
# Standalone /build-roi and /generate-roi-excel runs now run the SAME cap gate
# (scripts/artifact_boundary.py cap_roi_config, ticket #102) that orchestrate.py
# already runs. These checks give the roi-financial-modeler component gate a
# "capped invariant": no backbase_impact value (driver-level in
# value_lever_groups, or scenario-level in scenarios[*].backbase_impacts) may
# exceed MAX_BACKBASE_IMPACT. We deliberately do NOT reuse cap_roi_config's own
# `passed` flag here — that flag also folds in the ROI-range/revenue-ratio
# reasonableness warnings (heuristic, not "capped"), and the wired golden
# (a trimmed fixture with near-zero modeled benefit) trips those unrelated
# warnings regardless of capping. The invariant below isolates exactly what
# the gate is contractually supposed to guarantee: values <= the cap.


def _try_parse_json(text: str) -> dict | None:
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, ValueError):
        return None


def _backbase_impact_values(data: dict) -> list[float]:
    """Collect every backbase_impact-like numeric value from a roi_config,
    walking the exact same paths scripts.artifact_boundary.cap_roi_config caps:
    driver-level `value_lever_groups.*.{revenue,cost}_drivers.*.inputs.backbase_impact`
    and scenario-level `scenarios.*.backbase_impacts.*`."""
    vals: list[float] = []
    groups = data.get("value_lever_groups", data.get("journeys", {}))
    if isinstance(groups, dict):
        for group in groups.values():
            if not isinstance(group, dict):
                continue
            for driver_type in ("revenue_drivers", "cost_drivers"):
                for driver in group.get(driver_type, {}).values():
                    if not isinstance(driver, dict):
                        continue
                    bi = driver.get("inputs", {}).get("backbase_impact", {})
                    val = bi.get("value") if isinstance(bi, dict) else bi if isinstance(bi, (int, float)) else None
                    if isinstance(val, (int, float)):
                        vals.append(float(val))
    scenarios = data.get("scenarios", {})
    if isinstance(scenarios, dict):
        for sc in scenarios.values():
            if not isinstance(sc, dict):
                continue
            for imp_val in sc.get("backbase_impacts", {}).values():
                if isinstance(imp_val, (int, float)):
                    vals.append(float(imp_val))
    return vals


def _max_backbase_impact() -> float:
    """Import the cap constant from the gate itself (scripts/artifact_boundary.py,
    #102) rather than hard-coding a duplicate — if the gate's threshold ever
    changes, this invariant tracks it automatically."""
    root = repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from scripts.artifact_boundary import MAX_BACKBASE_IMPACT
    return MAX_BACKBASE_IMPACT


def _capped_invariant(data: dict) -> tuple[bool, str]:
    """True iff every backbase_impact value in `data` is within the gate's cap."""
    try:
        cap = _max_backbase_impact()
    except ImportError as e:
        return True, f"scripts.artifact_boundary not importable — skipping cap check ({e})"
    vals = _backbase_impact_values(data)
    over = [v for v in vals if v > cap]
    ok = len(over) == 0
    detail = (f"{len(vals)} backbase_impact value(s) checked, all <= {cap:.0%}" if ok
              else f"{len(over)} value(s) exceed the {cap:.0%} cap: {over}")
    return ok, detail


def _roi_modeler(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    # Contract scenario names plus the equivalents used in real reports (Base/Aspirational).
    low = text.lower()
    scen = sum(1 for s in ("conservative", "moderate", "aggressive", "base", "aspirational")
               if s in low)
    out.append(CheckResult("three_scenarios", 1.0 if scen >= 3 else scen / 3.0, scen >= 3,
                           detail=f"{scen} scenario labels (need >=3 of conservative/moderate/aggressive/base/aspirational)"))
    fin = sum(1 for k in ("npv", "payback", "roi") if k in low)
    out.append(_ratio_check("npv_payback_present", fin, 2,
                            detail=f"{fin}/3 headline financials (NPV/payback/ROI)"))
    has_reg = _present(r"assumptions?\s+register|##\s*\d*\.?\s*assumptions", text)
    out.append(_bool_check("assumptions_register_present", has_reg,
                           detail="Assumptions Register present" if has_reg else "no Assumptions Register"))
    has_sens = _present(r"sensitivity", text)
    out.append(_bool_check("sensitivity_analysis_present", has_sens, soft_floor=0.0,
                           detail="sensitivity analysis present" if has_sens else "no sensitivity analysis"))

    # --- #85 provenance contract (structural — requires the config to parse as JSON) ---
    data = _try_parse_json(text)
    if data is None:
        detail = "target is not a parseable JSON config (provenance checks need roi_config.json)"
        out.append(_bool_check("basic_information_has_sources_list", False, detail=detail))
        out.append(_bool_check("basic_fields_have_source_and_confidence", False, detail=detail))
        out.append(_bool_check("operating_costs_emitted_as_formula", False, detail=detail))
        return out

    sources = data.get("sources")
    valid_sources = (isinstance(sources, list) and len(sources) >= 1
                     and all(isinstance(s, dict) and s.get("ref") and s.get("detail") and s.get("file")
                             for s in sources))
    out.append(_bool_check("basic_information_has_sources_list", valid_sources,
                           detail=f"{len(sources) if isinstance(sources, list) else 0} source(s), "
                                  f"each with ref/detail/file={valid_sources}"))

    basic = data.get("basic_information", {}) if isinstance(data.get("basic_information"), dict) else {}
    value_fields = [k for k in basic if not (k.endswith("_source") or k.endswith("_confidence"))]
    fully_attributed = 0
    bad_confidence = []
    for field in value_fields:
        src = basic.get(f"{field}_source")
        conf = basic.get(f"{field}_confidence")
        if src and conf:
            if conf in _VALID_CONFIDENCE:
                fully_attributed += 1
            else:
                bad_confidence.append((field, conf))
    all_attributed = bool(value_fields) and fully_attributed == len(value_fields) and not bad_confidence
    detail = f"{fully_attributed}/{len(value_fields)} basic_information fields have source+valid confidence"
    if bad_confidence:
        detail += f"; invalid confidence values: {bad_confidence}"
    out.append(_bool_check("basic_fields_have_source_and_confidence", all_attributed, detail=detail))

    has_trio = all(k in basic for k in ("annual_revenue", "cost_to_income_ratio", "operating_costs"))
    oc_source = str(basic.get("operating_costs_source", ""))
    notes_derivation = bool(re.search(r"deriv|revenue.*cost.to.income|cost.to.income.*revenue", oc_source, re.I))
    ok_oc = has_trio and notes_derivation
    out.append(_bool_check("operating_costs_emitted_as_formula", ok_oc,
                           detail=f"revenue/cost-to-income/operating_costs trio present={has_trio}, "
                                  f"operating_costs_source notes derivation={notes_derivation} ({oc_source!r})"))

    # --- #104 parity case: standalone /build-roi and /generate-roi-excel now run
    # the same artifact_boundary cap gate the pipeline runs. The wired golden
    # (roi_config_provenance.json) is already capped and must PASS this invariant.
    ok_cap, cap_detail = _capped_invariant(data)
    out.append(_bool_check("backbase_impact_within_cap", ok_cap, detail=cap_detail))
    out.append(_check_overcap_negative_gated())
    return out


_OVERCAP_NEGATIVE_GOLDEN = "evals/goldens/roi_config_overcap.json"


def _check_overcap_negative_gated() -> CheckResult:
    """Witness check (same pattern as roi_excel_generator._check_sources_sheet_absent_when_unset):
    registry.yaml's `components:` altitude wires only ONE `input:` target, so the
    NEGATIVE fixture (evals/goldens/roi_config_overcap.json) is exercised here
    directly rather than through a registry `negatives:` list. Proves both halves
    of the #104 parity contract in one deterministic check:
      1. the negative, AS COMMITTED, FAILS the capped invariant (an over-cap
         backbase_impact value is actually present — the fixture is genuinely bad).
      2. running the real gate (scripts.artifact_boundary.cap_roi_config) on a
         COPY of it (never mutating the committed fixture) produces a config that
         PASSES the same invariant.
    """
    name = "overcap_negative_gate_witness"
    root = repo_root()
    fixture = root / _OVERCAP_NEGATIVE_GOLDEN
    if not fixture.exists():
        return _bool_check(name, False, detail=f"fixture not found: {fixture}")
    try:
        pre_data = json.loads(fixture.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return _bool_check(name, False, detail=f"could not read/parse fixture: {e}")

    pre_ok, pre_detail = _capped_invariant(pre_data)
    if pre_ok:
        return _bool_check(name, False,
                           detail=f"negative fixture did NOT fail pre-gate (expected an over-cap value): {pre_detail}")

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from scripts.artifact_boundary import cap_roi_config
    except ImportError as e:
        return _bool_check(name, False, detail=f"scripts.artifact_boundary not importable: {e}")

    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp_copy = Path(td) / "roi_config_overcap.json"
        shutil.copy(fixture, tmp_copy)
        cap_roi_config(str(tmp_copy))  # gates the COPY in place; committed fixture untouched
        post_data = json.loads(tmp_copy.read_text())

    post_ok, post_detail = _capped_invariant(post_data)
    ok = pre_ok is False and post_ok
    detail = f"pre-gate FAILED as expected ({pre_detail}); post-gate (on a /tmp copy) {'PASSED' if post_ok else 'still FAILED'} ({post_detail})"
    return _bool_check(name, ok, detail=detail)


# ---------------------------------------------------------------------------
# roi-hypothesis-builder
#   contract: lever IDs (L1, L2...); four-link chain (Root Driver / Operational
#             Change / Volume-Rate Impact / Financial Impact); creative levers
#             (CL#) flagged for validation; problem statement.
# ---------------------------------------------------------------------------
def _roi_hypothesis(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    levers = _count(r"\bL\d+\b|^###?\s*L\d", text, re.I | re.M)
    out.append(_ratio_check("lever_ids_present", min(levers, 3), 3,
                            detail=f"{levers} lever references (need >=3 distinct levers)"))
    chain = sum(1 for link in ("root driver", "operational change",
                               "volume", "financial impact")
                if link in text.lower())
    out.append(_ratio_check("four_link_chain_present", chain, 4,
                            detail=f"{chain}/4 four-link-chain elements (Root Driver/Operational Change/Volume-Rate/Financial Impact)"))
    has_problem = _present(r"problem\s+statement|problem\s+type", text)
    out.append(_bool_check("problem_statement_present", has_problem, soft_floor=0.0,
                           detail="problem statement present" if has_problem else "no problem statement"))
    return out


# ---------------------------------------------------------------------------
# roadmap-prioritization
#   yaml: phased (Phase 1-3 | Now/Next/Later), dependencies, milestones.
#   contract: Wave 1/2/3 alt model; initiative cards; decision gates; every
#             initiative maps to a capability gap + value lever.
# ---------------------------------------------------------------------------
def _roadmap(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    phased = _present(r"phase\s*[1-3]|now.*next.*later|wave\s*[1-3]", text)
    out.append(_bool_check("phases_present", phased,
                           detail="phased model present (Phase/Now-Next-Later/Wave)" if phased
                           else "no phased model"))
    # Sequenced initiatives — initiative cards (RI-/initiative) across phases.
    initiatives = _count(r"\bRI-\d+\b|initiative", text)
    out.append(_ratio_check("initiatives_sequenced", min(initiatives, 3), 3,
                            detail=f"{initiatives} initiative references"))
    has_dep = _present(r"dependenc", text)
    out.append(_bool_check("dependencies_present", has_dep, soft_floor=0.0,
                           detail="dependencies present" if has_dep else "no dependencies"))
    has_gate = _present(r"decision gate|\bDG-\d|milestone|value\s*realization", text)
    out.append(_bool_check("gates_or_milestones_present", has_gate, soft_floor=0.0,
                           detail="decision gates / value milestones present" if has_gate
                           else "no gates or value milestones"))
    return out


# ---------------------------------------------------------------------------
# narrative-assembler
#   yaml: 7 acts (Act [1-7]); Exec Summary; transformation; E\d+ refs.
# ---------------------------------------------------------------------------
def _narrative(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    acts = len(set(re.findall(r"\bact\s*([1-7])\b", text, re.I)))
    out.append(CheckResult("seven_acts_present", acts / 7.0, acts >= 7, hard_fail=False,
                           detail=f"{acts}/7 distinct acts present"))
    has_exec = _present(r"executive summary", text)
    out.append(_bool_check("executive_summary_present", has_exec,
                           detail="Executive Summary present" if has_exec else "no Executive Summary"))
    has_transform = _count(r"transformation|from\b.*\bto\b", text) >= 2
    out.append(_bool_check("transformation_arc_present", has_transform, soft_floor=0.5,
                           detail="transformation arc language present" if has_transform
                           else "weak transformation framing"))
    return out


# ---------------------------------------------------------------------------
# journey-builder
#   contract: lifecycle stages; per-journey friction callouts; value leakage
#             waterfall; As-Is / Future-State; PP-/CAP- traceability IDs.
# ---------------------------------------------------------------------------
def _journey(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    stages = sum(1 for s in ("acquire", "activate", "expand", "retain")
                 if _present(rf"\b{s}\b", text))
    out.append(_ratio_check("lifecycle_stages_present", stages, 2,
                            detail=f"{stages}/4 lifecycle stages referenced"))
    has_friction = _present(r"friction|value\s*leakage|leakage\s*waterfall", text)
    out.append(_bool_check("friction_or_leakage_present", has_friction,
                           detail="friction callouts / value leakage present" if has_friction
                           else "no friction / value-leakage analysis"))
    has_states = _present(r"as-is|current state", text) and _present(r"future[- ]state|future state", text)
    out.append(_bool_check("as_is_and_future_state", has_states, soft_floor=0.5,
                           detail="As-Is and Future-State both present" if has_states
                           else "missing As-Is or Future-State"))
    return out


# Canonical excluded-count note format (knowledge/standards/benchmark_evolution.md):
#   "Note: N synthetic-test entr(y/ies) excluded — fabricated pipeline-test
#   data, never citable in client work (see knowledge/standards/benchmark_evolution.md)."
# A line matching this format is the expected way to ACKNOWLEDGE an exclusion
# and is not itself a stray citation.
_SYNTHETIC_NOTE_RE = re.compile(
    r"^note:\s*\d+\s*synthetic-test entr(?:y|ies)\s*excluded\s*.{0,5}"
    r"fabricated pipeline-test data.*benchmark_evolution\.md\)\.?\s*$",
    re.I,
)


def _no_synthetic_citations(text: str) -> CheckResult:
    """Zero [Synthetic-Test] citations outside an explicit excluded-count note line.

    Honest limitation: this pins the FIXTURE's content contract for the eval —
    it does not verify the live agent's retrieval behavior. The eval gate
    scores goldens; it does not execute the agent or its knowledge reads
    (see memory/eval-gate-is-path2-only.md).
    """
    stray = [line.strip() for line in text.splitlines()
             if re.search(r"synthetic[- ]test", line, re.I)
             and not _SYNTHETIC_NOTE_RE.match(line.strip())]
    ok = not stray
    return _bool_check(
        "no_synthetic_citations", ok,
        detail="no stray [Synthetic-Test] citations outside the canonical excluded-count note" if ok
        else f"{len(stray)} line(s) reference synthetic-test data outside the canonical note",
    )


# ---------------------------------------------------------------------------
# benchmark-librarian
#   yaml: confidence levels (High/Medium/Low confidence); source attribution.
#   contract: provenance tags; shortlist with confidence + match type.
# ---------------------------------------------------------------------------
def _benchmark(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    has_conf = _present(r"confidence\s*level|(high|medium|low)\s*confidence|confidence:\s*(high|medium|low)", text)
    out.append(_bool_check("confidence_levels_present", has_conf,
                           detail="confidence levels present" if has_conf else "no confidence levels"))
    sources = _count(r"source\s*:|\[(annual report|investor presentation|regulator|"
                     r"not available|consultant-provided|industry|proxy|estimated)[^\]]*\]", text)
    out.append(_ratio_check("source_attribution_present", min(sources, 3), 3,
                            detail=f"{sources} source: / provenance tags"))
    out.append(_no_synthetic_citations(text))
    return out


# ---------------------------------------------------------------------------
# usecase-designer
#   contract: UC-### IDs; Product Directory Mapping (RB.x.x IDs); priority
#             tiers (Tablestakes/Differentiating, P1/P2/P3); OOTB/Config/Custom.
# ---------------------------------------------------------------------------
def _usecase(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    uc_ids = _count(r"\bUC-\d{2,}\b", text)
    out.append(_ratio_check("usecase_ids_present", min(uc_ids, 1), 1,
                            detail=f"{uc_ids} UC-### identifiers"))
    pd_map = _present(r"product directory|\bRB\.\d|\bWB\.\d", text)
    out.append(_bool_check("product_directory_mapping", pd_map,
                           detail="Product Directory mapping present" if pd_map
                           else "no Product Directory mapping"))
    classification = _present(r"OOTB|out-of-the-box|config(ure|uration)?|custom", text)
    out.append(_bool_check("ootb_config_custom_classification", classification, soft_floor=0.5,
                           detail="OOTB/Config/Custom classification present" if classification
                           else "no build-classification"))
    priority = _present(r"tablestakes|differentiating|\bP[123]\b", text)
    out.append(_bool_check("priority_tiers_present", priority, soft_floor=0.5,
                           detail="priority tiers present" if priority else "no priority tiers"))
    return out


# ---------------------------------------------------------------------------
# workshop-preparation
#   contract: 4 workshop modes; hypotheses (specific + quantified + validation
#             questions); consultant checkpoint.
# ---------------------------------------------------------------------------
def _workshop_prep(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    has_hypothesis = _count(r"hypothesis|hypotheses", text) >= 1
    out.append(_bool_check("hypotheses_present", has_hypothesis,
                           detail="hypotheses present" if has_hypothesis else "no hypotheses"))
    has_validation = _present(r"validation question|questions? to validate|validate", text)
    out.append(_bool_check("validation_questions_present", has_validation, soft_floor=0.5,
                           detail="validation questions present" if has_validation
                           else "no validation questions"))
    has_checkpoint = _present(r"consultant checkpoint|checkpoint", text)
    out.append(_bool_check("checkpoint_present", has_checkpoint, soft_floor=0.5,
                           detail="consultant checkpoint present" if has_checkpoint
                           else "no consultant checkpoint"))
    return out


# ---------------------------------------------------------------------------
# ignite-workshop-synthesizer
#   contract: hypothesis validation matrix with status values (Confirmed /
#             Partially Confirmed / Not Confirmed / Needs More Data); use-case
#             candidate prioritization; classification (Quick Wins / Foundational
#             / Transformational / Defer).
# ---------------------------------------------------------------------------
def _ignite_synth(text: str) -> list[CheckResult]:
    out: list[CheckResult] = []
    statuses = sum(1 for s in ("confirmed", "partially confirmed", "not confirmed",
                               "needs more data")
                   if s in text.lower())
    out.append(_ratio_check("hypothesis_validation_statuses", min(statuses, 2), 2,
                            detail=f"{statuses} validation-status labels (Confirmed/Partially/Not/Needs More Data)"))
    has_usecase = _present(r"use\s*case\s*candidate|use case", text)
    out.append(_bool_check("usecase_candidates_present", has_usecase,
                           detail="use case candidates present" if has_usecase
                           else "no use case candidates"))
    classification = _present(r"quick win|foundational|transformational|defer", text)
    out.append(_bool_check("usecase_classification_present", classification, soft_floor=0.5,
                           detail="use-case classification present" if classification
                           else "no Quick Wins/Foundational/Transformational/Defer classification"))
    return out


# ---------------------------------------------------------------------------
# Per-agent semantic judges (LLM-as-judge). Mirrors registry.yaml
# components[*].judge. These are the SOFT semantic layer on top of the
# code-only checks above; they auto-skip without ANTHROPIC_API_KEY (or with
# CORTEX_EVAL_NO_JUDGE set), so this stays safe offline.
#
# Faithfulness-type judges are CRITICAL (a real low score hard-fails the
# rubric); everything else is soft (averaged in, can't single-handedly fail).
# ---------------------------------------------------------------------------
JUDGES: dict[str, list[str]] = {
    "market-context-researcher": ["sources_credible_not_hallucinated"],
    "roi-hypothesis-builder": ["levers_grounded_in_evidence"],
    "discovery-transcript-interpreter": ["faithful_extraction_no_invention"],
    "capability-assessment": ["scores_justified_by_evidence"],
    "roadmap-prioritization": ["initiatives_traced_to_gaps_and_levers"],
    "narrative-assembler": ["transformation_arc_threaded_7_acts"],
    "journey-builder": ["value_leakage_quantified"],
    "benchmark-librarian": ["benchmarks_defensible_not_hallucinated"],
    "usecase-designer": ["usecases_grounded_in_product_directory"],
    "workshop-preparation": ["hypotheses_specific_and_quantified"],
    "ignite-workshop-synthesizer": ["synthesis_faithful_to_workshops"],
}

# Faithfulness/integrity judges run as critical (hard-fail on real failure).
CRITICAL_JUDGES: set[str] = {"faithful_extraction_no_invention"}

# Per-judge frozen standard. Generative agents (use cases, synthesis) are graded for
# PLATFORM ACHIEVABILITY, not transcript-faithfulness — grounded in the Backbase
# platform snapshot (OOTB product directory + the buildable platform layers).
JUDGE_SNAPSHOTS: dict[str, str] = {
    "usecases_grounded_in_product_directory": "backbase-platform-frozen.md",
    "synthesis_faithful_to_workshops": "backbase-platform-frozen.md",
    "levers_grounded_in_evidence": "backbase-platform-frozen.md",
}


def _run_judges(agent_name: str, text: str, context: str | None = None) -> list[CheckResult]:
    """Run the agent's registered semantic judges (soft, except faithfulness).

    For faithfulness-type judges the agent INPUT (context) is prepended so the
    judge can compare output against what the agent actually worked from.
    """
    names = JUDGES.get(agent_name)
    if not names:
        return []
    out: list[CheckResult] = []
    for name in names:
        critical = name in CRITICAL_JUDGES
        if critical and context:
            target = (f"# INPUT (what the agent worked from)\n{_read(context)}\n\n"
                      f"# OUTPUT (the agent's result)\n{text}")
        else:
            target = text
        out.append(judge(name, target, threshold=0.8, critical=critical,
                         snapshot=JUDGE_SNAPSHOTS.get(name)))
    return out


SPECIFICS = {
    "discovery-transcript-interpreter": _discovery,
    "capability-assessment": _capability,
    "market-context-researcher": _market_context,
    "roi-financial-modeler": _roi_modeler,
    "roi-hypothesis-builder": _roi_hypothesis,
    "roadmap-prioritization": _roadmap,
    "narrative-assembler": _narrative,
    "journey-builder": _journey,
    "benchmark-librarian": _benchmark,
    "usecase-designer": _usecase,
    "workshop-preparation": _workshop_prep,
    "ignite-workshop-synthesizer": _ignite_synth,
}


def evaluate(agent_name: str, target: str, context: str | None = None) -> list[CheckResult]:
    """Governance baseline + this agent's specifics.

    agent_name : the agent whose output `target` is.
    target     : the agent's output (file path or raw text).
    context    : the agent's INPUT (path or text), passed through to the
                 governance faithfulness judge if available.
    If the agent has no specifics, only the governance baseline is returned.
    """
    checks = governance.evaluate(target, context=context)
    text = _read(target)
    fn = SPECIFICS.get(agent_name)
    if fn is not None:
        checks.extend(fn(text))
    checks.extend(_run_judges(agent_name, text, context=context))
    return checks
