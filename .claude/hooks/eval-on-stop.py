#!/usr/bin/env python3
"""Stop hook — runtime evals for INTERACTIVE runs.

When a consultant produces outputs via Claude Code (a single skill OR a full run),
this scores the touched engagement at session end — agent outputs + deliverables +
deliverable-structural contracts — writes .pipeline_run_report.json, and flags
anything below threshold. Code-only (fast) so it doesn't stall the session; the full judge pass
runs in CI / at the CLI pipeline's end. NON-BLOCKING, fail-open: never wedges a
session, never blocks an engagement.

Complements orchestrate.py's end-of-run scoring (which covers the CLI pipeline).
"""
import os
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
WINDOW_S = 1800  # only score engagements whose outputs changed in the last 30 min


def main():
    recent_engagements = []
    now = time.time()
    for outputs in PROJECT_DIR.glob("engagements/*/*/outputs"):
        if not outputs.is_dir():
            continue
        try:
            touched = any((now - p.stat().st_mtime) < WINDOW_S
                          for p in outputs.glob("*") if p.is_file())
        except OSError:
            touched = False
        if touched:
            recent_engagements.append(outputs.parent)

    if not recent_engagements:
        sys.exit(0)  # nothing engagement-related happened this session

    os.environ["CORTEX_EVAL_NO_JUDGE"] = "1"  # fast, code-only at session end
    sys.path.insert(0, str(PROJECT_DIR / "evals"))
    try:
        from runtime import score_engagement, write_report
    except Exception:
        sys.exit(0)  # evals absent / import issue — never block

    for eng in recent_engagements:
        try:
            rep = score_engagement(eng)
            write_report(eng, rep)
            if rep.get("flags"):
                print(f"⚑ Eval: {len(rep['flags'])} flag(s) for {eng.name} "
                      f"(non-blocking; see .pipeline_run_report.json)", file=sys.stderr)
        except Exception:
            pass  # fail-open

    sys.exit(0)


if __name__ == "__main__":
    main()
