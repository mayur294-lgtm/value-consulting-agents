"""Pipeline (integration) altitude — inter-agent contract checks.

The most important altitude: when ANY component changes, this verifies the change
didn't break the chain. Cortex agents pass data to each other (discovery ->
capability/roi -> assembler), so a local edit can silently break a downstream
consumer. This checks the contracts hold across a golden engagement's outputs.

Today (path-2) it inspects an existing engagement's outputs dir. The path-1 upgrade
(documented in evals/README.md) is to first run `orchestrate.py` end-to-end on the
golden inputs so the check scores freshly regenerated outputs, catching prompt
regressions live.
"""
from __future__ import annotations

import re
from pathlib import Path

from rubrics.base import CheckResult, repo_root

_EID = re.compile(r"\bE\d{2,}\b")
_CAPID = re.compile(r"\bCAP-[A-Z0-9-]+\b")

# Deliverables a complete assessment run is expected to emit.
EXPECTED = ["roi_report.md", "assessment_dashboard.html"]


def _resolve_outputs(target: str) -> Path | None:
    p = Path(target)
    if p.is_dir():
        return p
    root = repo_root()
    if (root / target).is_dir():
        return root / target
    # treat target as an engagement key: pick the outputs dir with the most files
    candidates = list((root / "engagements").glob(f"*{target}*/**/outputs"))
    candidates = [c for c in candidates if c.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda d: len(list(d.glob("*"))))


def evaluate(target: str) -> list[CheckResult]:
    out = _resolve_outputs(target)
    if out is None:
        return [CheckResult("resolve_engagement_outputs", 0.0, False, hard_fail=True,
                            detail=f"could not resolve outputs dir for '{target}'")]
    checks: list[CheckResult] = []
    files = {p.name: p for p in out.glob("*") if p.is_file()}
    blob = "\n".join(p.read_text(errors="replace") for p in files.values()
                     if p.suffix in {".md", ".json", ".html"})

    # --- contract 1: expected deliverables present -----------------------------
    present = [f for f in EXPECTED if any(name == f for name in files)]
    checks.append(CheckResult("expected_deliverables_present", len(present) / len(EXPECTED),
                              len(present) == len(EXPECTED),
                              detail=f"{len(present)}/{len(EXPECTED)} present",
                              evidence=[f for f in EXPECTED if f not in present]))

    # --- contract 2: evidence IDs are defined somewhere ------------------------
    eids = set(_EID.findall(blob))
    checks.append(CheckResult("evidence_ids_present", 1.0 if eids else 0.0, bool(eids),
                              detail=f"{len(eids)} distinct evidence IDs across outputs"))

    # --- contract 3: capability IDs referenced by ROI resolve ------------------
    # The ROI consumes capability gaps; dangling CAP- refs = a broken contract.
    cap_defs = set()
    cap_file = next((files[n] for n in files if "capabilit" in n.lower()), None)
    if cap_file:
        cap_defs = set(_CAPID.findall(cap_file.read_text(errors="replace")))
    roi_file = files.get("roi_report.md")
    if cap_file and roi_file and cap_defs:
        roi_refs = set(_CAPID.findall(roi_file.read_text(errors="replace")))
        dangling = sorted(roi_refs - cap_defs)
        checks.append(CheckResult("roi_capability_refs_resolve",
                                  1.0 if not dangling else max(0.0, 1 - 0.1 * len(dangling)),
                                  not dangling,
                                  detail=f"{len(dangling)} ROI capability ref(s) not defined in capability output"
                                  if dangling else "all ROI capability refs resolve",
                                  evidence=dangling))
    else:
        checks.append(CheckResult("roi_capability_refs_resolve", 0.0, True, skipped=True,
                                  detail="capability or ROI output absent — contract not checkable"))

    # --- contract 4: final deliverables don't violate hard design gates --------
    # Import deliverable evaluators lazily to avoid a hard dep at module load.
    import importlib
    hard_violations = 0
    for name, mod_name in (("assessment_dashboard.html", "rubrics.deliverable.assessment"),):
        if name in files:
            mod = importlib.import_module(mod_name)
            for c in mod.evaluate(str(files[name])):
                if c.hard_fail and not c.passed:
                    hard_violations += 1
    checks.append(CheckResult("deliverables_pass_hard_gates",
                              0.0 if hard_violations else 1.0, hard_violations == 0,
                              detail=f"{hard_violations} hard design-gate violation(s) in deliverables"
                              if hard_violations else "deliverables clear hard gates"))
    return checks
