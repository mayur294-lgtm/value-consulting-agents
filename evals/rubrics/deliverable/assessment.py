"""Assessment-dashboard deliverable code-evaluators (objective, no LLM).

Reuses the deck palette/gradient/CDN helpers (same design system) and adds
assessment-specific structural checks. Every check maps to a documented defect:
  - deprecated hex / gradient text / external CDN  (design-system, shared)
  - leftover {{PLACEHOLDER}} markers                (unfinished generation)
  - missing trace-IDs                                (traceability rule)
  - not all 7 acts present                           (template completeness)
  - dark body base                                   (must be light base theme)
Semantic checks (arc threaded across 7 acts, lifecycle coherence) are the
LLM-judge rubrics in rubrics/judge.
"""
from __future__ import annotations

import re
from pathlib import Path

from rubrics.base import CheckResult
from rubrics.deliverable.decks import DEPRECATED_HEXES, _HEX_RE, _norm

_TRACE_RE = re.compile(r'data-trace-id\s*=\s*["\'](PP|CAP|UC|BEN|INI|PERSONA)-', re.I)


def evaluate(target: str) -> list[CheckResult]:
    html = Path(target).read_text(errors="replace")
    low = html.lower()
    checks: list[CheckResult] = []

    # --- shared design-system hard gates ---------------------------------------
    dep = sorted({h for h in (_norm(m.group(0)) for m in _HEX_RE.finditer(html)) if h in DEPRECATED_HEXES})
    checks.append(CheckResult("no_deprecated_hexes", 0.0 if dep else 1.0, not dep, hard_fail=True,
                              detail=f"{len(dep)} deprecated hex(es)" if dep else "none",
                              evidence=[f"#{h}" for h in dep]))

    grad = re.findall(r"(?:-webkit-)?background-clip\s*:\s*text", low)
    checks.append(CheckResult("no_gradient_text", 0.0 if grad else 1.0, not grad, hard_fail=True,
                              detail=f"{len(grad)} background-clip:text" if grad else "none"))

    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)["\']', html, re.I)
    bad = [u for u in ext if not re.search(r"fonts\.(googleapis|gstatic)\.com", u, re.I)]
    checks.append(CheckResult("self_contained_no_cdn", 0.0 if bad else 1.0, not bad, hard_fail=True,
                              detail=f"{len(bad)} external resource(s)" if bad else "self-contained", evidence=bad))

    # --- assessment-specific ---------------------------------------------------
    placeholders = re.findall(r"\{\{[A-Z0-9_]+\}\}", html)
    checks.append(CheckResult("no_unfilled_placeholders", 0.0 if placeholders else 1.0, not placeholders, hard_fail=True,
                              detail=f"{len(placeholders)} {{{{PLACEHOLDER}}}} marker(s)" if placeholders else "none"))

    traces = len(_TRACE_RE.findall(html))
    checks.append(CheckResult("traceability_ids_present", 1.0 if traces >= 10 else traces / 10.0, traces >= 10,
                              detail=f"{traces} data-trace-id attributes (PP/CAP/UC/BEN/INI/PERSONA)"))

    acts = len(set(re.findall(r"act\s*([1-7])\b", low)))
    checks.append(CheckResult("seven_acts_present", acts / 7.0, acts >= 7,
                              detail=f"{acts}/7 acts referenced"))

    light_base = bool(re.search(r"body\s*\{[^}]*background[^;}]*(#fff|#ffffff|white)", low))
    checks.append(CheckResult("light_base_theme", 1.0 if light_base else 0.5, light_base,
                              detail="light body background" if light_base else "could not confirm white body background"))

    # Semantic judge: arc threaded across all 7 acts (auto-skips without API key).
    from rubrics.judge.judge import run_judges
    checks += run_judges(target, [("arc_threaded_7_acts", "design-system-frozen.md")], threshold=0.8)

    return checks
