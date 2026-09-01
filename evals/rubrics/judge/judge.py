"""LLM-as-judge harness for semantic rubrics (Claude Opus).

Design critique is nuanced, so the judge model is Opus by default. A judge prompt
lives in rubrics/judge/prompts/<name>.md and is scored against a FROZEN snapshot
of the relevant standard (rubrics/judge/standards_snapshot/) so that green scores
don't silently start lying when the live design system drifts.

Judges run through the `claude` CLI (`claude -p ...`), not the Anthropic SDK
(#203, design D9). That routes scoring through the invoking consultant's/CI
runner's Claude subscription instead of a metered ANTHROPIC_API_KEY — the
founding promise (commit 0079500) is "runs locally with no keys," and the SDK
path was the one thing that broke it. `_available()` now gates on the `claude`
binary being on PATH and logged in (`claude auth status`), not on an env var.

Graceful degradation, UNCHANGED from before #203 (#181/#182): with no `claude`
CLI / not authenticated, judge() returns skipped=True, passed=False — never a
silent pass. A judge that's declared in the registry but comes back unavailable
still FAILS the run (run_experiment.py's `_assert_declared_checks_executed`) —
that's enforced there, not here; this module only needs to make sure the
CheckResult is produced (never omitted) so that check fires correctly.

The old metered-API-key path is kept intact behind `_available_sdk()` /
`_run_judge_sdk()` — unused by default, but a revert is switching the two
module-level aliases just below the imports back to the `_sdk` variants.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from rubrics.base import CheckResult

JUDGE_MODEL = os.getenv("CORTEX_JUDGE_MODEL", "claude-opus-4-8")
_HERE = Path(__file__).resolve().parent
PROMPTS = _HERE / "prompts"
SNAPSHOTS = _HERE / "standards_snapshot"

# How long a single `claude -p` judge call may run before we give up on it.
# Generous: Opus scoring a large artifact against a frozen standard is not
# instant, but a hang (e.g. a blocked interactive prompt) must not wedge the gate.
_JUDGE_TIMEOUT_S = int(os.getenv("CORTEX_JUDGE_TIMEOUT_S", "180"))

# Cheap re-check of `claude auth status` (~0.2s) is still a subprocess call, and
# _available() runs before every judge in a rubric — cache it once per process.
_cli_auth_cache: bool | None = None

_UNAVAILABLE_DETAIL_TMPL = (
    "Judge `{name}` is declared but the `claude` CLI is unavailable or not logged in. "
    "Judges run on your Claude subscription — run `claude` once to sign in. "
    "CI rows must not declare judges; CI is key-free by design."
)


def _load_prompt(name: str) -> str | None:
    p = PROMPTS / f"{name}.md"
    return p.read_text() if p.exists() else None


def _load_snapshot(snapshot: str | None) -> str:
    if not snapshot:
        return ""
    p = SNAPSHOTS / snapshot
    return p.read_text() if p.exists() else ""


# Vars that make the `claude` binary itself fall back to metered API-key auth
# (confirmed empirically: `claude auth status` reports {"loggedIn": true,
# "authMethod": "api_key", "apiKeySource": "ANTHROPIC_API_KEY"} whenever this
# is set — even if the key is garbage/expired). evals/.env unconditionally
# `setdefault`s ANTHROPIC_API_KEY into the process env (see run_experiment.py
# `_load_dotenv`), so it WILL be present in the ambient environment this
# module runs in — stripping it here is what actually makes D9 hold, not
# merely not-reading it ourselves.
_KEY_ENV_VARS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")


def _sanitized_env() -> dict:
    """Env for every `claude` subprocess call, with metered-key vars stripped
    so a stray key in the ambient environment can never make the CLI quietly
    bill a metered key instead of using the subscription session."""
    env = dict(os.environ)
    for k in _KEY_ENV_VARS:
        env.pop(k, None)
    return env


def _cli_authenticated() -> bool:
    """Is the `claude` binary on PATH and logged in to a Claude subscription
    (not merely holding an API key)? Cached per process."""
    global _cli_auth_cache
    if _cli_auth_cache is not None:
        return _cli_auth_cache
    claude_bin = shutil.which("claude")
    if not claude_bin:
        _cli_auth_cache = False
        return False
    try:
        r = subprocess.run([claude_bin, "auth", "status"], capture_output=True,
                           text=True, timeout=15, env=_sanitized_env())
        # `claude auth status` prints JSON on stdout and exits non-zero when
        # logged out — parse the body, don't trust the exit code alone.
        data = json.loads(r.stdout or "{}")
        # authMethod == "api_key" means an env var / apiKeyHelper key is doing
        # the authenticating, not a Claude subscription session — that's the
        # metered path D9 removes, so it does not count as "available" here.
        _cli_auth_cache = (bool(data.get("loggedIn"))
                           and data.get("authMethod") != "api_key")
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
        _cli_auth_cache = False
    return _cli_auth_cache


def _available_cli() -> bool:
    if os.getenv("CORTEX_EVAL_NO_JUDGE"):   # fast code-only mode (e.g. interactive Stop hook)
        return False
    return _cli_authenticated()


def _run_judge_cli(system: str, user: str) -> str:
    """Score via `claude -p` (subscription auth — D9, #203).

    Raises on every failure mode (missing binary, non-zero exit, timeout) —
    judge() is the single place that turns those into skipped=True/passed=False,
    so no failure mode here can crash the gate or silently pass. Runs with
    metered-key env vars stripped (see `_sanitized_env`) — belt-and-braces on
    top of the `_available()` gate, so this call itself can never fall back
    to billing a metered key even if one is sitting in the ambient env.
    """
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise RuntimeError("claude CLI not found on PATH")
    cmd = [claude_bin, "-p", user, "--append-system-prompt", system, "--model", JUDGE_MODEL]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=_JUDGE_TIMEOUT_S,
                       env=_sanitized_env())
    if r.returncode != 0:
        detail = (r.stderr or r.stdout or "").strip()[:400]
        raise RuntimeError(f"claude CLI exited {r.returncode}: {detail}")
    return r.stdout


# --- legacy metered-API-key path (pre-#203) — unused by default, kept for a one-line revert ---

def _available_sdk() -> bool:
    if os.getenv("CORTEX_EVAL_NO_JUDGE"):
        return False
    if not os.getenv("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except ImportError:
        return False


def _run_judge_sdk(system: str, user: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=JUDGE_MODEL, max_tokens=1024,
        system=system, messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


# Switch point for a revert: point both aliases at the `_sdk` variants to go
# back to the metered ANTHROPIC_API_KEY path.
_available = _available_cli
_run_judge = _run_judge_cli


def judge(name: str, target_text: str, *, snapshot: str | None = None,
          threshold: float = 0.7, max_chars: int = 60_000, critical: bool = False) -> CheckResult:
    """Score target_text against the judge prompt <name>. Returns a CheckResult.

    The judge MUST return strict JSON: {"score": 0..1, "pass": bool, "reason": str}.
    critical=True: a real (non-skipped) failure HARD-FAILS the whole rubric — used
    for integrity judges (faithfulness, assumption discipline) so a low score can't
    be averaged away to a pass.
    """
    prompt = _load_prompt(name)
    if prompt is None:
        return CheckResult(name=f"judge:{name}", score=0.0, passed=False, skipped=True,
                           detail=f"no judge prompt at prompts/{name}.md")
    if not _available():
        return CheckResult(name=f"judge:{name}", score=0.0, passed=False, skipped=True,
                           detail=_UNAVAILABLE_DETAIL_TMPL.format(name=name))

    standard = _load_snapshot(snapshot)
    system = (
        "You are a strict senior-consulting QA judge. Score the artifact against the "
        "rubric and the FROZEN STANDARD provided. Be conservative: when in doubt, score "
        "lower. Respond with ONLY a JSON object: "
        '{"score": <float 0..1>, "pass": <bool>, "reason": "<one paragraph>"}.'
    )
    user = (
        f"# Rubric\n{prompt}\n\n"
        + (f"# Frozen standard (score against THIS)\n{standard}\n\n" if standard else "")
        + f"# Artifact to score\n{target_text[:max_chars]}"
    )
    try:
        raw = _run_judge(system, user)
        m = re.search(r"\{.*\}", raw, re.S)
        data = json.loads(m.group(0) if m else raw)
        score = float(data.get("score", 0.0))
        passed = bool(data.get("pass", score >= threshold))
        return CheckResult(name=f"judge:{name}", score=score, passed=passed,
                           hard_fail=(critical and not passed),
                           detail=str(data.get("reason", ""))[:300])
    except subprocess.TimeoutExpired:
        return CheckResult(name=f"judge:{name}", score=0.0, passed=False, skipped=True,
                           detail=f"judge timed out after {_JUDGE_TIMEOUT_S}s (skipped)")
    except Exception as e:  # never let a judge error crash the gate
        return CheckResult(name=f"judge:{name}", score=0.0, passed=False, skipped=True,
                           detail=f"judge error (skipped): {e}"[:300])


def run_judges(target: str, names_with_snapshots: list[tuple[str, str | None]],
               threshold: float = 0.7) -> list[CheckResult]:
    text = Path(target).read_text(errors="replace") if Path(target).exists() else target
    return [judge(n, text, snapshot=s, threshold=threshold) for n, s in names_with_snapshots]
