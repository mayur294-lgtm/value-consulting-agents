#!/usr/bin/env python3
"""Runtime eval engine — scores a live engagement's outputs (NON-blocking, flags).

This is the agent + deliverable wiring at RUNTIME. It routes every output an
engagement produced to its eval, runs the deliverable-structural contract check,
and writes scores into `.pipeline_run_report.json` (the "Trustworthy Runs"
report — the file keeps its name: it genuinely reports on a pipeline RUN, which
is a different thing from the eval altitude that was renamed in #188).
It NEVER raises on a low score — it flags. Three callers use it:

  • orchestrate.py        → call score_engagement() at end of a pipeline run
  • eval-on-output hook   → interactive consultant runs (any skill/agent)
  • standalone            → python evals/runtime.py <engagement_dir>

Reuses the same evaluators as the dev-time gate (one rulebook, two contexts).
"""
from __future__ import annotations

import datetime as _dt
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# #188: the inter-agent contract block is the deliverable-structural altitude.
# It reads output FILES; it does not run orchestrate.py. Renamed from `pipeline`
# because that name made a green here read as integration evidence.
_STRUCTURAL_KEY = "deliverable_structural"        # key in .pipeline_run_report.json
_STRUCTURAL_ALTITUDE = "deliverable-structural"   # rendered altitude label
sys.path.insert(0, str(HERE))
from rubrics.base import RubricResult  # noqa: E402

try:                                   # load evals/.env so LANGFUSE_* are available
    from run_experiment import _load_dotenv
    _load_dotenv()
except Exception:
    pass


def _log_langfuse(report: dict) -> None:
    """Build a proper Langfuse TRACE for a real run: a run trace with one child
    observation per agent + per deliverable, each carrying its eval score. Gives the
    dashboard a per-run, per-agent breakdown (not just flat scores). No-op without keys."""
    import os
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return
    try:
        from langfuse import Langfuse
        lf = Langfuse()
        root = lf.create_event(
            name=f"run:{report['engagement']}",
            input={"engagement": report["engagement"]},
            metadata={"flags": len(report.get("flags", [])), "kind": "runtime-eval"},
            level=("WARNING" if report.get("flags") else "DEFAULT"),
        )
        tid = getattr(root, "trace_id", None)

        def _child(kind: str, name: str, v: dict) -> None:
            if "score" not in v:
                return
            obs = lf.create_event(
                name=f"{kind}:{name}",
                trace_context={"trace_id": tid} if tid else None,
                output={"score": v["score"], "pass": v.get("pass")},
                metadata={"altitude": v.get("altitude", kind)},
                level=("WARNING" if v.get("pass") is False else "DEFAULT"),
            )
            lf.create_score(name=f"{kind}/{name}", value=float(v["score"]), trace_id=tid,
                            observation_id=getattr(obs, "id", None), data_type="NUMERIC",
                            comment=("PASS" if v.get("pass") else "FLAG"))

        for k, v in report.get("agents", {}).items():
            _child("agent", k, v)
        for k, v in report.get("deliverables", {}).items():
            _child("deliverable", k, v)
        if "score" in report.get(_STRUCTURAL_KEY, {}):
            lf.create_score(name=_STRUCTURAL_KEY, value=float(report[_STRUCTURAL_KEY]["score"]),
                            trace_id=tid, data_type="NUMERIC")
        lf.flush()
    except Exception:
        pass  # telemetry must never break a run

# deliverable routing: filename (exact or *glob*) -> (evaluator, threshold)
_DELIVERABLE_ROUTES: list[tuple[str, str, float]] = [
    ("assessment_dashboard.html", "rubrics.deliverable.assessment", 0.80),
    ("roi_config.json",           "rubrics.deliverable.roi",        0.80),
    ("roi_report.md",             "rubrics.deliverable.report",     0.80),
    ("assessment_report.md",      "rubrics.deliverable.report",     0.80),
    ("executive_summary.md",      "rubrics.deliverable.report",     0.80),
    ("*deck*.html",               "rubrics.deliverable.decks",      0.85),
    ("*workshop*.html",           "rubrics.deliverable.decks",      0.85),
]

# agent intermediate outputs -> the agent that produced them (governance baseline applies)
_AGENT_OUTPUTS: dict[str, str] = {
    "evidence_register.md":      "discovery-transcript-interpreter",
    "pain_points.md":            "discovery-transcript-interpreter",
    "capability_assessment.md":  "capability-assessment",
    "market_context_validated.md": "market-context-researcher",
    "roadmap.md":                "roadmap-prioritization",
}


def _run(evaluator: str, target: Path, altitude: str) -> RubricResult:
    mod = importlib.import_module(evaluator)
    return RubricResult(target=target.name, altitude=altitude, checks=mod.evaluate(str(target)))


def _match(name: str, pattern: str) -> bool:
    if pattern.startswith("*") and pattern.endswith("*"):
        return pattern.strip("*") in name
    return name == pattern


def log_agent_call(agent_name: str, prompt: str, output: str, model: str = "",
                   cost: float = 0.0, turns: int = 0, elapsed: float = 0.0) -> None:
    """Live per-call trace: emit one Langfuse observation for a single agent run
    (prompt/output/cost/turns/model). Called from orchestrate.py's run_agent.
    No-op without Langfuse keys; never raises."""
    import os
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return
    try:
        from langfuse import Langfuse
        lf = Langfuse()
        lf.create_event(
            name=f"agent:{agent_name}",
            input={"prompt": str(prompt)[:4000]},
            output={"text": str(output)[:4000]},
            metadata={"model": model, "cost_usd": round(cost, 4), "turns": turns,
                      "elapsed_s": round(elapsed, 1), "kind": "agent-call"},
        )
        lf.flush()
    except Exception:
        pass  # tracing must never break a run


def score_engagement(engagement_dir: str | Path) -> dict:
    """Score every output + the deliverable-structural contracts.

    Returns the run-report dict. #188: the contracts block is reported under the
    `deliverable_structural` key (was `pipeline`) and the schema is bumped to v2
    so any out-of-tree reader that pinned v1 fails loudly rather than silently
    finding nothing where `pipeline` used to be."""
    eng = Path(engagement_dir)
    outputs = eng / "outputs" if (eng / "outputs").is_dir() else eng
    report: dict = {
        "schema": "pipeline_run_report/eval/v2",   # v2: `pipeline` key -> `deliverable_structural` (#188)
        "timestamp": _dt.datetime.now().isoformat(timespec="seconds"),
        "engagement": eng.name,
        "deliverables": {}, "agents": {}, _STRUCTURAL_KEY: {}, "flags": [],
    }
    files = {p.name: p for p in outputs.glob("*") if p.is_file()}

    # --- deliverables ----------------------------------------------------------
    for name, p in files.items():
        for pat, evaluator, thr in _DELIVERABLE_ROUTES:
            if _match(name, pat):
                try:
                    r = _run(evaluator, p, "deliverable")
                    if r.all_unscorable:
                        # a parser gap, not a quality finding — never rendered as 0/0,
                        # and never appended to flags.
                        report["deliverables"][name] = {"unscorable": True,
                            "threshold": thr, "altitude": "deliverable"}
                    else:
                        report["deliverables"][name] = {"score": round(r.score, 3),
                            "pass": r.passed(thr), "threshold": thr, "altitude": "deliverable"}
                        if not r.passed(thr):
                            report["flags"].append(f"deliverable {name} {r.score:.2f}<{thr}")
                except Exception as e:
                    report["deliverables"][name] = {"error": str(e)}
                break

    # --- agent-level: FULL per-agent suite (governance baseline + per-agent code
    #     checks + per-agent judges), so the consultant runtime gets the same depth
    #     as the dev-time gate — not just the 3-check baseline. ---------------------
    specifics = importlib.import_module("rubrics.component.specifics")
    for name, agent in _AGENT_OUTPUTS.items():
        if name in files:
            try:
                checks = specifics.evaluate(agent, str(files[name]))
                rr = RubricResult(target=name, altitude="component", checks=checks)
                if rr.all_unscorable:
                    # a parser gap, not a quality finding — never rendered as 0/0,
                    # and never appended to flags.
                    report["agents"][agent] = {"output": name, "unscorable": True,
                        "altitude": "component"}
                else:
                    report["agents"][agent] = {"output": name, "score": round(rr.score, 3),
                        "pass": rr.passed(0.80), "altitude": "component"}
                    if not rr.passed(0.80):
                        report["flags"].append(f"agent {agent} ({name}) {rr.score:.2f}<0.80")
            except Exception as e:
                report["agents"][agent] = {"error": str(e)}

    # --- deliverable-structural contracts --------------------------------------
    try:
        contracts = importlib.import_module("rubrics.structural.contracts")
        rr = RubricResult(target=eng.name, altitude=_STRUCTURAL_ALTITUDE,
                          checks=contracts.evaluate(str(outputs)))
        if rr.all_unscorable:
            # a parser gap, not a quality finding — never rendered as 0/0,
            # and never appended to flags.
            report[_STRUCTURAL_KEY] = {"unscorable": True, "threshold": 0.90}
        else:
            report[_STRUCTURAL_KEY] = {"score": round(rr.score, 3), "pass": rr.passed(0.90),
                                       "threshold": 0.90}
            if not rr.passed(0.90):
                report["flags"].append(f"structural contracts {rr.score:.2f}<0.90")
    except Exception as e:
        report[_STRUCTURAL_KEY] = {"error": str(e)}

    return report


def write_report(engagement_dir: str | Path, report: dict | None = None) -> Path:
    eng = Path(engagement_dir)
    report = report or score_engagement(eng)
    path = eng / ".pipeline_run_report.json"
    # merge: keep any non-eval keys an existing report already has (timings/cost)
    existing = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except json.JSONDecodeError:
            pass
    existing["evals"] = report
    path.write_text(json.dumps(existing, indent=2))
    _log_langfuse(report)   # mirror real-run scores to the Langfuse dashboard (if keys)
    return path


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python evals/runtime.py <engagement_dir>")
        return 2
    eng = sys.argv[1]
    rep = score_engagement(eng)
    path = write_report(eng, rep)
    print(f"Eval run report → {path}")
    d, a = rep["deliverables"], rep["agents"]
    du = sum(v.get("unscorable") is True for v in d.values())
    au = sum(v.get("unscorable") is True for v in a.values())
    print(f"  deliverables: {sum(v.get('pass') is True for v in d.values())}/{len(d)} pass"
          + (f"  ({du} unscorable)" if du else ""))
    print(f"  agents:       {sum(v.get('pass') is True for v in a.values())}/{len(a)} pass"
          + (f"  ({au} unscorable)" if au else ""))
    st = rep[_STRUCTURAL_KEY]
    if st.get("unscorable"):
        print("  structural:   UNSCORABLE (parser gap, not a quality finding)")
    else:
        print(f"  structural:   {st.get('score','?')} "
              f"({'pass' if st.get('pass') else 'FLAG'})   [file contracts only — not an end-to-end run]")
    if rep["flags"]:
        print("  ⚑ FLAGS (non-blocking):")
        for f in rep["flags"]:
            print(f"     - {f}")
    return 0  # never block a run


if __name__ == "__main__":
    raise SystemExit(main())
