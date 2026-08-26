"""The `rubric_calibration` tier banner (#201).

Eleven rows in `evals/registry.yaml` score a frozen synthetic prose golden with
a deterministic rubric. They were filed under `components:` keyed by AGENT NAME,
which reads — to a reviewer, to CI output, to anyone quoting the number — as
"this row gates that agent". It does not, and never did:

    replacing the entire 45 KB `market-context-researcher` prompt with one line
    of garbage left `--component market-context-researcher` at 1.000 PASS.

The rubric never executes a prompt. It reads a committed `.md` fixture that no
agent run produced. What the score genuinely certifies is that the RUBRIC still
parses that fixture the way it did when the threshold was set — the calibration
anchor that keeps the threshold falsifiable, and the only regression test on
rubric code, which changed in all six of the last eval PRs. That is worth
keeping. The CLAIM attached to it was not.

So the rows are re-filed as `rubric_calibration:`, keyed by RUBRIC, and every
run prints the banner below. `covers_agent:` stays in the row as INERT
DOCUMENTATION — nothing in `run_experiment.py`, `check_registry.py` or
`mutations.py` reads it, and `check_registry.py` asserts that the agent it names
cannot be reached as a gate.

The banner is printed, not returned as a `CheckResult`, on purpose: a check
would be scored into the mean (changing the very calibration it annotates) and
would show up as `[undeclared]` in `_assert_declared_checks_executed`. The
mutation harness reads only its sentinel line from a scoring child's stdout
(`evals/mutations.py`, `_SCORE_CHILD_SRC`: "everything the rubric itself prints
is left alone above it"), so printing here is safe under `--mutate` too.

NOT used by `evals/runtime.py`. Runtime scores live client engagement outputs
through `specifics.evaluate(agent, path)` directly — it never imports these thin
adapters — so live scoring is byte-identical to before this change (design D10).
"""
from __future__ import annotations

import sys

TIER = "rubric_calibration"

_RULE = "─" * 78

# Appended to each thin adapter's module docstring so `help(mod)` and any
# doc-reader carries the same claim boundary the banner prints at runtime.
RUBRIC_ROW_DOC = """
TIER: rubric_calibration (#201). This module IS the `{row}` rubric. It is
invoked as `run_experiment.py --component {row}`; the agent name
`{agent}` no longer resolves to a gate (it keeps a hard-failing redirect row —
see rubrics/component/moved_to_rubric_calibration.py).

A pass certifies that this rubric still parses its frozen synthetic golden the
way it did when the threshold was set. It certifies NOTHING about `{agent}`:
no prompt is executed here, and replacing that agent's prompt entirely would
not move this score. See rubrics/component/_calibration.py.
"""


def banner_text(rubric: str, covers_agent: str, golden: str = "") -> str:
    """The standing tier banner for one calibration row."""
    golden_line = f"  Golden:       {golden}\n" if golden else ""
    return (
        f"\n{_RULE}\n"
        f"  TIER: {TIER} — this row scores the RUBRIC, not the component.\n"
        f"{_RULE}\n"
        f"  Row:          {rubric}\n"
        f"{golden_line}"
        f"  covers_agent: {covers_agent}   [INERT DOCUMENTATION — NOT a verification claim]\n"
        f"\n"
        f"  A pass here means: the rubric still reads its frozen synthetic golden\n"
        f"  the way it did when this threshold was set. It is a calibration anchor\n"
        f"  and a regression test on rubric code.\n"
        f"\n"
        f"  It is NOT evidence about `{covers_agent}`. No prompt is executed by\n"
        f"  this row. Replacing that agent's entire prompt with one line of garbage\n"
        f"  leaves this score exactly where it is. Only path-1 regeneration\n"
        f"  (evals/path1.py) can say anything about the agent's behaviour.\n"
        f"\n"
        f"  The `Altitude:` line below reads `unit` — that is the runner's dispatch\n"
        f"  altitude for `--component`, not this row's tier. The tier is {TIER}.\n"
        f"{_RULE}"
    )


def calibration_banner(rubric: str, covers_agent: str, golden: str = "",
                       stream=sys.stdout) -> None:
    """Print the standing banner. Never raises — a broken stream must not take
    a gate down with it."""
    try:
        print(banner_text(rubric, covers_agent, golden), file=stream, flush=True)
    except Exception:  # noqa: BLE001 - telemetry-grade output, never load-bearing
        pass
