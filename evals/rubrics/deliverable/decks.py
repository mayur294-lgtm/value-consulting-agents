"""Deck deliverable code-evaluators (objective, no LLM).

Scores a self-contained Frontline-2026 HTML deck against the design system.
Every check maps to a documented, recurring defect:
  - palette drift (PR #71)            -> deprecated hex = HARD FAIL
  - off-palette colors                -> soft penalty
  - gradient text ban                 -> -webkit-background-clip:text = HARD FAIL
  - self-contained / no external CDNs -> HARD FAIL on non-font external src/href
  - no border-left ribbons on cards   -> soft penalty
  - Libre Franklin present            -> soft penalty if missing
  - <= 4 key points per content slide -> soft penalty per offending slide

The allowed palette is loaded LIVE from presentations/frontline-2026/
design-tokens.json so it never drifts from the source of truth.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from rubrics.base import CheckResult, repo_root

_HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")

# Superseded / wrong-template / ENGAGE-2026 hexes. Provenance: design-tokens.json
# `provenance.supersedes` (#001C3D drift, #1A5AFF drift, #3366FF Theme-2/old-engine)
# plus the deprecated ENGAGE 2026 palette recorded in knowledge/design-system.md.
DEPRECATED_HEXES = {
    "001c3d", "1a5aff", "3366ff",          # drifted / secondary-palette blues & navy
    "0f172a", "ff6b5e", "93c47d", "e8b931",  # ENGAGE 2026 (deprecated)
    "5c6e84", "f5f7f9", "e02020",            # Frontline-2026-v1 drift (muted/bg/red)
}

# Neutrals tolerated outside the named palette (pure black, transparent shorthand).
_TOLERATED = {"000000", "000", "fff", "ffffff"}


# Canonical design-system files. The allowed palette = every hex these actually
# use (minus deprecated). Grounds the check in the REAL design system — including
# the extended tint/shade ramp the official templates rely on — not a partial list.
_CANON_FILES = (
    "presentations/frontline-2026/design-tokens.json",
    "templates/long-form/document-template.html",
    "templates/presentations/assessment-dashboard-template.html",
    "presentations/backbase-slides-app/deck-template.html",
    "presentations/backbase-slides-app/engine.js",
)


def _load_allowed_hexes() -> set[str]:
    root = repo_root()
    allowed: set[str] = set(_TOLERATED)
    # core tokens (explicit, even if the file is absent we still have these below)
    try:
        data = json.loads((root / _CANON_FILES[0]).read_text())
        for spec in data.get("colors", {}).values():
            hx = spec.get("hex", "").lstrip("#").lower()
            if hx:
                allowed.add(hx)
    except (OSError, json.JSONDecodeError):
        pass
    # union of every hex used by the canonical design-system files (the real ramp)
    for rel in _CANON_FILES:
        p = root / rel
        if not p.exists():
            continue
        for m in _HEX_RE.finditer(p.read_text(errors="replace")):
            h = _norm(m.group(0))
            if h not in DEPRECATED_HEXES:   # never allow a deprecated hex via a stray ref
                allowed.add(h)
    allowed.add("d97706")  # tolerated amber variant (knowledge/design-system.md)
    return allowed


def _norm(hx: str) -> str:
    hx = hx.lstrip("#").lower()
    if len(hx) == 3:  # expand shorthand
        hx = "".join(c * 2 for c in hx)
    return hx


def evaluate(target: str) -> list[CheckResult]:
    html = Path(target).read_text(errors="replace")
    low = html.lower()
    allowed = _load_allowed_hexes()
    checks: list[CheckResult] = []

    # --- 1. palette: deprecated hexes (HARD FAIL) -------------------------------
    found = [_norm(m.group(0)) for m in _HEX_RE.finditer(html)]
    dep_hits = sorted({h for h in found if h in DEPRECATED_HEXES})
    checks.append(CheckResult(
        name="no_deprecated_hexes",
        score=0.0 if dep_hits else 1.0,
        passed=not dep_hits,
        hard_fail=True,
        detail=f"{len(dep_hits)} deprecated hex(es)" if dep_hits else "none",
        evidence=[f"#{h}" for h in dep_hits],
    ))

    # --- 2. palette: off-palette colors (soft) ---------------------------------
    off = sorted({h for h in found if h not in allowed and h not in DEPRECATED_HEXES})
    off_score = 1.0 if not off else max(0.0, 1.0 - 0.1 * len(off))
    checks.append(CheckResult(
        name="palette_conformance",
        score=off_score,
        passed=not off,
        detail=f"{len(off)} off-palette color(s)" if off else "all colors on-palette",
        evidence=[f"#{h}" for h in off],
    ))

    # --- 3. gradient text ban (HARD FAIL) --------------------------------------
    grad_text = re.findall(r"(?:-webkit-)?background-clip\s*:\s*text", low)
    checks.append(CheckResult(
        name="no_gradient_text",
        score=0.0 if grad_text else 1.0,
        passed=not grad_text,
        hard_fail=True,
        detail=f"{len(grad_text)} background-clip:text occurrence(s)" if grad_text else "none",
    ))

    # --- 4. self-contained / no external CDNs (HARD FAIL) ----------------------
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)["\']', html, re.I)
    bad_ext = [u for u in ext if not re.search(r"fonts\.(googleapis|gstatic)\.com", u, re.I)]
    checks.append(CheckResult(
        name="self_contained_no_cdn",
        score=0.0 if bad_ext else 1.0,
        passed=not bad_ext,
        hard_fail=True,
        detail=f"{len(bad_ext)} external resource(s)" if bad_ext else "self-contained (Google Fonts only)",
        evidence=bad_ext,
    ))

    # --- 5. no FAT border-left ribbons on cards (soft) -------------------------
    # Thin left accents (<=4px) are legit in the design system (callouts use 3px,
    # sidebar 2px). Only flag fat card-ribbon style (>=5px).
    ribbons = re.findall(r"border-left\s*:\s*[^;}\"']*\b(?:[5-9]|\d{2,})px", low)
    checks.append(CheckResult(
        name="no_border_left_ribbons",
        score=1.0 if not ribbons else max(0.0, 1.0 - 0.2 * len(ribbons)),
        passed=not ribbons,
        detail=f"{len(ribbons)} thick border-left ribbon(s)" if ribbons else "none (top-accent style)",
    ))

    # --- 6. Libre Franklin present (soft) --------------------------------------
    has_font = "libre franklin" in low
    checks.append(CheckResult(
        name="libre_franklin_font",
        score=1.0 if has_font else 0.0,
        passed=has_font,
        detail="present" if has_font else "Libre Franklin not referenced",
    ))

    # --- 7. <= 4 key points per content slide (soft heuristic) -----------------
    # Heuristic: within each <section> (slide), count top-level <li>. Flag >4.
    sections = re.findall(r"<section\b.*?</section>", html, re.S | re.I)
    over = 0
    for sec in sections:
        if len(re.findall(r"<li\b", sec, re.I)) > 4:
            over += 1
    pts_score = 1.0 if over == 0 else max(0.0, 1.0 - 0.15 * over)
    checks.append(CheckResult(
        name="max_4_points_per_slide",
        score=pts_score,
        passed=over == 0,
        detail=(f"{over} slide(s) exceed 4 list items" if over else "all slides <= 4 points")
        + (f" (of {len(sections)} sections)" if sections else " (no <section> slides detected)"),
    ))

    return checks
