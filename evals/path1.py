#!/usr/bin/env python3
"""Path-1 runner + auto-remediation loop.

Path-2 scores artifacts that already exist. Path-1 REGENERATES: it runs an agent
headlessly on a golden input, scores its fresh output, and — with --remediate —
regenerates-with-feedback until it clears threshold or N attempts. That's the EDD
inner loop AND the "score < X → go back and rebuild" capability, at the agent level.

Run agent execution via the `claude` CLI (-p headless), reusing the caller's
ANTHROPIC auth. Scoring reuses the same rubrics as every other context.

  python evals/path1.py --agent market-context-researcher --input goldens/nfis/brief.md
  python evals/path1.py --agent roi-financial-modeler --input X --remediate --threshold 0.8
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from rubrics.base import RubricResult  # noqa: E402
from rubrics.component.governance import evaluate as _gov  # noqa: E402


def agent_system_prompt(agent_name: str) -> str:
    md = ROOT / ".claude" / "agents" / f"{agent_name}.md"
    text = md.read_text()
    if text.startswith("---"):           # strip YAML frontmatter
        parts = text.split("---", 2)
        text = parts[2] if len(parts) == 3 else text
    return text.strip()


def run_agent(agent_name: str, input_text: str, model: str = "sonnet", extra: str = "") -> str:
    """Headless agent run via `claude -p`. Returns the agent's output text."""
    sysp = agent_system_prompt(agent_name)
    if extra:
        sysp += "\n\n## Reviewer feedback to address this attempt\n" + extra
    cmd = ["claude", "-p", input_text, "--append-system-prompt", sysp, "--model", model]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    if r.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {r.stderr[:400]}")
    return r.stdout.strip()


def score(agent_name: str, output_text: str, context: str | None = None) -> RubricResult:
    # governance baseline (+ per-agent specifics could be appended here from registry)
    return RubricResult(target=agent_name, altitude="component",
                        checks=_gov(output_text, context=context))


def remediate(agent_name: str, input_text: str, threshold: float = 0.8,
              max_attempts: int = 3, model: str = "opus") -> tuple[str, RubricResult, int]:
    """Run → score → if below threshold, regenerate WITH the failing-check feedback.
    Returns (output, result, attempts). This is the self-healing loop."""
    feedback, out, res = "", "", None
    for attempt in range(1, max_attempts + 1):
        out = run_agent(agent_name, input_text, model=model, extra=feedback)
        res = score(agent_name, out, context=input_text)
        if res.passed(threshold):
            return out, res, attempt
        fails = [c for c in res.checks if not c.passed and not c.skipped]
        feedback = ("Your previous attempt scored below the quality bar. Fix these:\n"
                    + "\n".join(f"- {c.name}: {c.detail}" for c in fails))
    return out, res, max_attempts


def main() -> int:
    ap = argparse.ArgumentParser(description="Path-1 agent runner + remediation")
    ap.add_argument("--agent", required=True)
    ap.add_argument("--input", required=True, help="golden input file or literal text")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--threshold", type=float, default=0.8)
    ap.add_argument("--remediate", action="store_true", help="regenerate until >= threshold (max 3)")
    ap.add_argument("--max-attempts", type=int, default=3)
    args = ap.parse_args()

    inp = Path(args.input)
    input_text = inp.read_text() if inp.exists() else args.input

    if args.remediate:
        out, res, n = remediate(args.agent, input_text, args.threshold, args.max_attempts, args.model)
        print(f"# remediation: {n} attempt(s), final {res.score:.2f} "
              f"({'PASS' if res.passed(args.threshold) else 'STILL BELOW — escalate'})")
    else:
        out = run_agent(args.agent, input_text, model=args.model)
        res = score(args.agent, out, context=input_text)
    print(res.report(args.threshold))
    return 0 if res.passed(args.threshold) else 1


if __name__ == "__main__":
    raise SystemExit(main())
