#!/usr/bin/env python3
"""Path-1 runner + auto-remediation loop.

Path-2 scores artifacts that already exist. Path-1 REGENERATES: it runs an agent
headlessly on a golden input, scores its fresh output, and — with --remediate —
regenerates-with-feedback until it clears threshold or N attempts. That's the EDD
inner loop AND the "score < X → go back and rebuild" capability, at the agent level.

Run agent execution via the `claude` CLI (-p headless), reusing the caller's
ANTHROPIC subscription auth. Scoring reuses the same rubrics as every other
context — and, since #204, the ROW'S REAL rubric: the governance baseline PLUS
this agent's per-agent specifics (rubrics.component.specifics.SPECIFICS) PLUS
every semantic judge the registry row declares under `path1_judge:` (and any
gating `judge:`, though no row currently has one — see registry.yaml's
`components:` header comment). Previously `score()` only ran the governance
baseline, with a TODO noting per-agent specifics "could be appended here from
registry" — that TODO is what this ticket closes.

  python evals/path1.py --agent market-context-researcher --input goldens/nfis/brief.md
  python evals/path1.py --agent roi-financial-modeler --input X --remediate --threshold 0.8

LOCAL ONLY — this is #204's whole point (PRD "Out of Scope": path-1 must never
be a blocking gate this cycle; the statistical base-vs-new comparison is
explicitly deferred). Every entry point below (`main()`, `run_agent()`,
`score()`) hard-refuses under `$CI` / `$GITHUB_ACTIONS` — see `refuse_if_ci()`
and `_in_ci()`. `run_experiment.py --regenerate` is the OTHER route into this
module (evals/run_experiment.py's `--regenerate` dispatch) and refuses via the
same `refuse_if_ci()` rather than reimplementing the check, so the two routes
cannot drift.

`run_agent()`'s `claude -p` call reuses judge.py's #203/D9 helpers VERBATIM
(`_cli_authenticated`, `_sanitized_env`) rather than reimplementing them — the
same "`claude auth status` reports loggedIn:true whenever ANTHROPIC_API_KEY is
merely SET, valid or not" trap #203 found applies here too (path1.py shells to
`claude -p` exactly like judge.py does), and importing the one implementation
is what keeps the two callers from silently diverging. See rubrics/judge/judge.py's
module docstring for the full trap writeup. The metered Anthropic SDK is never
imported anywhere in this module.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from rubrics.base import CheckResult, RubricResult  # noqa: E402
from rubrics.component.governance import evaluate as _gov  # noqa: E402
from rubrics.component import specifics as _specifics  # noqa: E402
from rubrics.judge.judge import judge as _judge  # noqa: E402
from rubrics.judge.judge import _cli_authenticated, _sanitized_env  # noqa: E402 - reuse #203/D9, don't reimplement


# --- CI guard (#204) -----------------------------------------------------------
# Both env vars GitHub Actions itself sets (CI=true and GITHUB_ACTIONS=true),
# checked independently — either one alone must refuse.
_CI_ENV_VARS = ("CI", "GITHUB_ACTIONS")

# Literal text from .design/ux-design-v7.md's Error States table, "Path-1 in
# CI" row. Kept as one literal constant so run_experiment.py's --regenerate
# route and this module's own CLI print byte-identical text.
CI_REFUSAL_MESSAGE = (
    "path-1 regeneration never runs in CI. It costs subscription quota, is "
    "nondeterministic, and CI is $0 by design. Run it locally."
)

# Printed on every path-1 run (CLI and --regenerate alike) so nothing coming
# out of this module can be mistaken for a gate verdict — ux-design-v7.md
# Flow 4's "report + explicit note: single run, nondeterministic — not a gate."
PATH1_BANNER = (
    "\n=== PATH-1 REGENERATION — single run, nondeterministic, NOT A GATE ===\n"
    "This ran the agent once via your Claude subscription and scored the\n"
    "fresh output. It is not reproducible run-to-run, it never runs in CI,\n"
    "and it never blocks a merge — see .design/ux-design-v7.md Flow 4.\n"
)


def _in_ci() -> bool:
    return any(os.environ.get(v) for v in _CI_ENV_VARS)


def refuse_if_ci(stream=sys.stderr) -> bool:
    """Print the CI refusal and return True iff $CI or $GITHUB_ACTIONS is set.
    Callers (this module's own main(), and run_experiment.py's --regenerate
    dispatch) must check this BEFORE doing anything else — it does not raise
    or exit on its own so both call sites can choose their own exit path."""
    if _in_ci():
        print(CI_REFUSAL_MESSAGE, file=stream)
        return True
    return False


def _load_registry(path: Path | None = None) -> dict:
    """Mirrors run_experiment.py's `_load_registry` (including the
    CORTEX_EVAL_REGISTRY test seam) without importing that module — path1.py
    must stay importable BY run_experiment.py, so it cannot import back."""
    import yaml  # PyYAML
    if path is None:
        override = os.environ.get("CORTEX_EVAL_REGISTRY")
        path = Path(override) if override else (HERE / "registry.yaml")
    return yaml.safe_load(path.read_text())


def agent_system_prompt(agent_name: str) -> str:
    md = ROOT / ".claude" / "agents" / f"{agent_name}.md"
    text = md.read_text()
    if text.startswith("---"):           # strip YAML frontmatter
        parts = text.split("---", 2)
        text = parts[2] if len(parts) == 3 else text
    return text.strip()


def run_agent(agent_name: str, input_text: str, model: str = "sonnet", extra: str = "") -> str:
    """Headless agent run via `claude -p`. Returns the agent's output text.

    Refuses under CI (belt-and-braces: main() also checks first, but this is
    the one function every route into path-1 ultimately calls to spend
    subscription quota, so it refuses on its own too). Requires a real Claude
    subscription session — `_cli_authenticated()` (imported from judge.py,
    #203/D9) rejects `authMethod == "api_key"`, which is what a stray
    ANTHROPIC_API_KEY in the env (evals/.env's unconditional `setdefault`,
    see run_experiment.py's `_load_dotenv`) would otherwise silently produce.
    The subprocess itself runs with `_sanitized_env()` (same import), which
    strips ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN regardless — so even if
    the auth check above were ever bypassed, the metered key still could not
    reach the `claude` binary from this call.
    """
    if _in_ci():
        raise RuntimeError(CI_REFUSAL_MESSAGE)
    if not _cli_authenticated():
        raise RuntimeError(
            "the `claude` CLI is unavailable or not logged in to a Claude "
            "subscription session (an ANTHROPIC_API_KEY sitting in the env "
            "does not count — `claude auth status` reports authMethod "
            "'api_key' for that, which judge.py's D9 fix treats as "
            "unavailable; see rubrics/judge/judge.py). Path-1 needs a real "
            "subscription session: run `claude` once to sign in."
        )
    sysp = agent_system_prompt(agent_name)
    if extra:
        sysp += "\n\n## Reviewer feedback to address this attempt\n" + extra
    cmd = ["claude", "-p", input_text, "--append-system-prompt", sysp, "--model", model]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, env=_sanitized_env())
    if r.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {r.stderr[:400]}")
    return r.stdout.strip()


def score(agent_name: str, output_text: str, context: str | None = None,
          registry: dict | None = None) -> tuple[RubricResult, list[str]]:
    """Score output_text against the ROW'S REAL rubric — governance baseline
    + this agent's per-agent specifics + every semantic judge the registry
    row declares under `path1_judge:` (falling back to a gating `judge:`
    list, though no row currently has one). This is what closes the TODO
    that used to leave path-1 scoring only the governance baseline.

    Reads the registry FRESH by default (or takes one via `registry=`, e.g.
    reused by run_experiment.py's --regenerate dispatch which already loaded
    it) rather than caching module-level state — #201 is concurrently
    re-filing registry.yaml's component rows on this same branch, so this
    function depends on nothing about that file's shape beyond
    `components.<agent_name>.{code,judge,path1_judge}` all being optional.

    Returns (RubricResult, judge_names_run) so callers can report exactly
    which checks were assembled for this row.
    """
    if _in_ci():
        raise RuntimeError(CI_REFUSAL_MESSAGE)

    reg = registry if registry is not None else _load_registry()
    spec = ((reg or {}).get("components") or {}).get(agent_name) or {}

    checks: list[CheckResult] = list(_gov(output_text, context=context))

    specifics_fn = _specifics.SPECIFICS.get(agent_name)
    if specifics_fn is not None:
        checks.extend(specifics_fn(output_text))

    # path1_judge is the non-gating list (#182 migrated 12 rows' `judge:` to
    # `path1_judge:` precisely so this function could consume them without
    # ever making them gate CI). A stray gating `judge:` is included too, on
    # the off chance a row ever declares one (registry.yaml's own comment:
    # "if it does, that name is asserted executed too, exactly like `code:`").
    judge_names = list(dict.fromkeys(
        list(spec.get("path1_judge") or []) + list(spec.get("judge") or [])
    ))
    for jname in judge_names:
        critical = jname in _specifics.CRITICAL_JUDGES
        snapshot = _specifics.JUDGE_SNAPSHOTS.get(jname)
        subject = output_text
        if critical and context:
            subject = (f"# INPUT (what the agent worked from)\n{context}\n\n"
                       f"# OUTPUT (the agent's result)\n{output_text}")
        checks.append(_judge(jname, subject, threshold=0.7, critical=critical, snapshot=snapshot))

    return RubricResult(target=agent_name, altitude="component", checks=checks), judge_names


def remediate(agent_name: str, input_text: str, threshold: float = 0.8,
              max_attempts: int = 3, model: str = "opus",
              registry: dict | None = None) -> tuple[str, RubricResult, list[str], int]:
    """Run → score → if below threshold, regenerate WITH the failing-check feedback.
    Returns (output, result, judge_names, attempts). This is the self-healing loop."""
    reg = registry if registry is not None else _load_registry()
    feedback, out, res, judge_names = "", "", None, []
    for attempt in range(1, max_attempts + 1):
        out = run_agent(agent_name, input_text, model=model, extra=feedback)
        res, judge_names = score(agent_name, out, context=input_text, registry=reg)
        if res.passed(threshold):
            return out, res, judge_names, attempt
        fails = [c for c in res.checks if not c.passed and not c.skipped]
        feedback = ("Your previous attempt scored below the quality bar. Fix these:\n"
                    + "\n".join(f"- {c.name}: {c.detail}" for c in fails))
    return out, res, judge_names, max_attempts


def main() -> int:
    # Checked BEFORE argparse, deliberately: a bare `CI=true python evals/path1.py`
    # (no --agent/--input at all) must still refuse with this exact message, not
    # an argparse usage error — the CI guard must be reachable via every route,
    # including a malformed one.
    if refuse_if_ci():
        return 1

    ap = argparse.ArgumentParser(description="Path-1 agent runner + remediation "
                                              "(LOCAL ONLY — never a gate; see module docstring)")
    ap.add_argument("--agent", required=True)
    ap.add_argument("--input", required=True, help="golden input file or literal text")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--threshold", type=float, default=0.8)
    ap.add_argument("--remediate", action="store_true", help="regenerate until >= threshold (max 3)")
    ap.add_argument("--max-attempts", type=int, default=3)
    args = ap.parse_args()

    inp = Path(args.input)
    input_text = inp.read_text() if inp.exists() else args.input

    registry = _load_registry()
    try:
        if args.remediate:
            out, res, judge_names, n = remediate(args.agent, input_text, args.threshold,
                                                  args.max_attempts, args.model, registry=registry)
            print(f"# remediation: {n} attempt(s), final {res.score:.2f} "
                  f"({'PASS' if res.passed(args.threshold) else 'STILL BELOW — escalate'})")
        else:
            out = run_agent(args.agent, input_text, model=args.model)
            res, judge_names = score(args.agent, out, context=input_text, registry=registry)
    except RuntimeError as exc:
        print(f"\n[FAIL] path-1 could not run `{args.agent}`: {exc}", file=sys.stderr)
        return 1

    print(PATH1_BANNER)
    has_specifics = args.agent in _specifics.SPECIFICS
    print(f"checks assembled for `{args.agent}`: governance baseline"
          f"{' + per-agent specifics' if has_specifics else ' (no per-agent specifics registered)'}"
          f" + path1 judges={judge_names}")
    print(res.report(args.threshold))
    return 0 if res.passed(args.threshold) else 1


if __name__ == "__main__":
    raise SystemExit(main())
