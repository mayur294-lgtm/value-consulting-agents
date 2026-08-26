"""LLM-as-judge harness for semantic rubrics (Claude Opus).

Design critique is nuanced, so the judge model is Opus by default. A judge prompt
lives in rubrics/judge/prompts/<name>.md and is scored against a FROZEN snapshot
of the relevant standard (rubrics/judge/standards_snapshot/) so that green scores
don't silently start lying when the live design system drifts.

Graceful degradation: with no ANTHROPIC_API_KEY (or no SDK installed) judge() returns
a CheckResult(skipped=True) — excluded from scoring — so the deterministic gate still
runs in shadow/CI without keys. In blocking mode, calibrate thresholds only once keys
are present and judges actually run.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from rubrics.base import CheckResult

JUDGE_MODEL = os.getenv("CORTEX_JUDGE_MODEL", "claude-opus-4-8")
_HERE = Path(__file__).resolve().parent
PROMPTS = _HERE / "prompts"
SNAPSHOTS = _HERE / "standards_snapshot"


def _load_prompt(name: str) -> str | None:
    p = PROMPTS / f"{name}.md"
    return p.read_text() if p.exists() else None


def _load_snapshot(snapshot: str | None) -> str:
    if not snapshot:
        return ""
    p = SNAPSHOTS / snapshot
    return p.read_text() if p.exists() else ""


def _available() -> bool:
    if os.getenv("CORTEX_EVAL_NO_JUDGE"):   # fast code-only mode (e.g. interactive Stop hook)
        return False
    if not os.getenv("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except ImportError:
        return False


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
                           detail="judge skipped (no ANTHROPIC_API_KEY / SDK) — runs in keyed mode")

    import anthropic
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
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=JUDGE_MODEL, max_tokens=1024,
            system=system, messages=[{"role": "user", "content": user}],
        )
        raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        m = re.search(r"\{.*\}", raw, re.S)
        data = json.loads(m.group(0) if m else raw)
        score = float(data.get("score", 0.0))
        passed = bool(data.get("pass", score >= threshold))
        return CheckResult(name=f"judge:{name}", score=score, passed=passed,
                           hard_fail=(critical and not passed),
                           detail=str(data.get("reason", ""))[:300])
    except Exception as e:  # never let a judge error crash the gate
        return CheckResult(name=f"judge:{name}", score=0.0, passed=False, skipped=True,
                           detail=f"judge error (skipped): {e}")


def run_judges(target: str, names_with_snapshots: list[tuple[str, str | None]],
               threshold: float = 0.7) -> list[CheckResult]:
    text = Path(target).read_text(errors="replace") if Path(target).exists() else target
    return [judge(n, text, snapshot=s, threshold=threshold) for n, s in names_with_snapshots]
