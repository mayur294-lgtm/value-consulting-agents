#!/usr/bin/env python3
"""Registry preflight — every GATING golden must actually resolve in CI.

The eval registry (`evals/registry.yaml`) gates PRs. A gate is only real if the
fixture it scores against is present in a clean checkout. Two ways that silently
broke before:

  1. A `goldens:` / `input:` slot pointed into `engagements/**`, which is
     gitignored (PII). The file is absent in every clean checkout and in CI, so
     `run_experiment.py` [SKIP]s it — and a skip counts as a PASS. The gate was
     vacuously green (see the deliverable-goldens fix in this PR).
  2. A golden path was simply never committed (e.g. a never-created
     `evals/goldens/nfis/roi_config.json`).

This preflight makes both loud instead of silent. It is cheap ($0, no LLM) and
is meant to run FIRST in the eval CI job so a mis-wired registry fails fast with
a precise message, before any rubric runs.

Rules
-----
GATING slots — `deliverables.*.goldens`, `deliverables.*.negatives`,
`components.*.input`, and any `golden_engagement:` written as a PATH (contains
'/') — MUST:
  * exist in the working tree, AND
  * NOT be gitignored (i.e. be reproducible in CI).
A violation is a HARD ERROR (exit 1).

`golden_engagement:` written as a BARE NAME (e.g. `nfis`) resolves into the
gitignored `engagements/**` tree at runtime, so it is vacuous in CI. These are
reported as DEBT (warnings) — visible every run, but non-fatal, so the remaining
legacy cases can be migrated incrementally without blocking the gate today.

`monitor:` entries are real shipped engagement outputs, watched for drift and
never gating — they are allowed to be absent/gitignored and are skipped here.

Usage
-----
    python3 evals/check_registry.py           # exit 1 on any hard error
    python3 evals/check_registry.py --strict   # also fail on DEBT warnings
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent          # evals/
ROOT = HERE.parent                              # repo root


def _resolve(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else (ROOT / q)


def _gitignored(path: Path) -> bool:
    """True if git ignores `path` (so it won't be in a clean checkout / CI)."""
    try:
        r = subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=ROOT, capture_output=True,
        )
        return r.returncode == 0
    except OSError:
        # No git available — can't prove it's ignored; don't hard-fail on that.
        return False


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    reg = yaml.safe_load((HERE / "registry.yaml").read_text())

    errors: list[str] = []   # hard failures — a gate that can't run
    debt: list[str] = []     # warnings — bare-name engagement goldens (vacuous in CI)

    def check_gate(path: str, where: str) -> None:
        rp = _resolve(path)
        if not rp.exists():
            errors.append(f"{where}: golden '{path}' does not exist "
                          f"(gate would [SKIP] → vacuous PASS)")
        elif _gitignored(rp):
            errors.append(f"{where}: golden '{path}' is gitignored — absent in CI. "
                          f"Commit a fixture under evals/goldens/ or move it to monitor:")

    def check_engagement(ge: str, where: str) -> None:
        if "/" in str(ge):                       # an explicit path → must resolve
            check_gate(ge, where)
        else:                                    # a bare name → gitignored engagements/**
            debt.append(f"{where}: golden_engagement '{ge}' is a bare engagement name "
                        f"(resolves into gitignored engagements/** → vacuous in CI)")

    # --- deliverables ---------------------------------------------------------
    for name, spec in (reg.get("deliverables") or {}).items():
        for slot in ("goldens", "negatives"):
            for g in (spec.get(slot) or []):
                check_gate(g, f"deliverables.{name}.{slot}")
        # monitor: intentionally skipped (real engagements, non-gating)

    # --- components -----------------------------------------------------------
    for name, spec in (reg.get("components") or {}).items():
        if spec.get("input"):
            check_gate(spec["input"], f"components.{name}.input")
        if spec.get("golden_engagement"):
            check_engagement(spec["golden_engagement"], f"components.{name}.golden_engagement")

    # --- pipeline -------------------------------------------------------------
    pl = reg.get("pipeline") or {}
    if pl.get("golden_engagement"):
        check_engagement(pl["golden_engagement"], "pipeline.golden_engagement")

    # --- report ---------------------------------------------------------------
    print("Registry preflight — evals/registry.yaml")
    if debt:
        print(f"\nDEBT ({len(debt)}) — non-gating, vacuous in CI, migrate incrementally:")
        for d in debt:
            print(f"  ⚠ {d}")
    if errors:
        print(f"\nERRORS ({len(errors)}) — a gate cannot run in CI:")
        for e in errors:
            print(f"  ✗ {e}")
        print("\nRESULT: FAIL")
        return 1
    if strict and debt:
        print("\nRESULT: FAIL (--strict: DEBT treated as error)")
        return 1
    print(f"\nAll gating goldens resolve and are committed."
          f"{' (' + str(len(debt)) + ' debt warning(s) above)' if debt else ''}")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
