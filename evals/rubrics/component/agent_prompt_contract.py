"""Agent PROMPT-contract checks — for agents whose row would otherwise not exist.

WHY THIS MODULE EXISTS
  `evals.yml`'s changed-component derivation hard-fails when a changed
  `.claude/agents/<name>.md` has no `components.<name>` row, and its own comment
  states the intended direction: "extending fail-loud to [uncovered paths], not
  softening the agent rule." Three agents — capability-gap-analyzer,
  upgrade-analysis and value-consulting-orchestrator — had neither a row nor a
  rubric, so any change to them was blocked rather than verified. This is the
  rubric that unblocks them by CHECKING them.

WHAT IT CHECKS, AND WHAT IT DELIBERATELY DOES NOT
  It scores the agent's PROMPT FILE, not the agent's output. That distinction
  matters and is the honest limit of this row: nothing here says the agent
  behaves correctly. What it does say is that the prompt still carries the
  contracts the system depends on — the telemetry marker every journal entry is
  parsed for, and (for the agents that query Infobank) the §5 anonymisation
  constraint that v6 added to seven prompts. Those are exactly the clauses a
  well-meaning edit silently drops.

  `rubrics/component/specifics.py` is the per-agent OUTPUT rubric and is frozen
  this cycle (design D10); `governance.py` is the output baseline. Neither can
  serve here, because there is no output to score — the subject is the prompt.

  Judges are not used: every check is a deterministic property of the file.
"""
from __future__ import annotations

import re
from pathlib import Path

from rubrics.base import CheckResult
from rubrics._harness import bool_check

# Agents that reach the Backbase Infobank over MCP and therefore MUST carry the
# §5 anonymisation constraint (knowledge/standards/security_protocol.md §5, added
# to seven prompts in v6). The orchestrator is deliberately NOT in this set — it
# is a thin router and issues no Infobank queries of its own.
_MCP_QUERYING = {"capability-gap-analyzer", "upgrade-analysis"}


def _read(target: str) -> str:
    p = Path(target)
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else str(target)


def _frontmatter_declares_name_and_description(text: str) -> CheckResult:
    """`name:` and `description:` are what the Task tool dispatches on. An agent
    missing either is unroutable, and the failure shows up as "no such agent"
    far from the edit that caused it."""
    head = "\n".join(text.splitlines()[:8])
    ok = bool(re.search(r"^name:\s*\S", head, re.M)) and bool(
        re.search(r"^description:\s*\S", head, re.M))
    return bool_check("frontmatter_declares_name_and_description", ok,
                      detail=f"head={head[:120]!r}")


def _telemetry_block_marker_present(text: str) -> CheckResult:
    """`<!-- TELEMETRY_START -->` is what `scripts/extract_telemetry.py` parses
    journal entries for. Drop it from the prompt and the agent still runs, still
    writes a journal, and contributes NOTHING to telemetry — a silent loss, which
    is why it is checked rather than assumed."""
    ok = "TELEMETRY_START" in text
    return bool_check("telemetry_block_marker_present", ok,
                      detail=f"occurrences={text.count('TELEMETRY_START')}")


def _mcp_anonymization_constraint_present(text: str) -> CheckResult:
    """The §5 constraint. `mcp-query-guard.py` blocks a query carrying a client
    identifier, but a prompt that never tells the agent to ask generically turns
    every Infobank call into a denial the agent then has to recover from. Prompt
    and hook are the two halves of one control."""
    ok = "Anonymize every MCP query" in text
    return bool_check("mcp_anonymization_constraint_present", ok,
                      detail="§5 constraint present" if ok else "§5 constraint MISSING")


def _journal_and_telemetry_protocol_section(text: str) -> CheckResult:
    """CLAUDE.md's non-negotiable #1 and #2: an agent appends a journal entry on
    completion, with a telemetry block. The heading is what makes that
    obligation legible in the prompt rather than implied."""
    ok = "Journal Entry & Telemetry Protocol" in text
    return bool_check("journal_and_telemetry_protocol_section", ok)


def _routes_all_three_engagement_modes(text: str) -> CheckResult:
    """The orchestrator's entire job is routing. If a mode stops being named, an
    engagement of that type silently falls through to whichever branch matches
    first — the failure is a wrong pipeline, not an error."""
    modes = [m for m in ("Ignite Assess", "Ignite Inspire", "Hybrid") if m in text]
    return bool_check("routes_all_three_engagement_modes", len(modes) == 3,
                      detail=f"named={modes}")


def _delegates_block_a_to_the_script(text: str) -> CheckResult:
    """CLAUDE.md is explicit that Claude does NOT hand-orchestrate the five
    Block-A agents — `scripts/orchestrate.py` does. The prompt has to point at
    the script, or the router starts doing the pipeline's job by hand."""
    ok = "orchestrate.py" in text
    return bool_check("delegates_block_a_to_the_script", ok,
                      detail=f"orchestrate.py refs={text.count('orchestrate.py')}")


def evaluate(target: str) -> list[CheckResult]:
    text = _read(target)
    agent = Path(target).stem

    checks = [
        _frontmatter_declares_name_and_description(text),
        _telemetry_block_marker_present(text),
    ]
    if agent in _MCP_QUERYING:
        checks.append(_mcp_anonymization_constraint_present(text))
    if agent == "value-consulting-orchestrator":
        checks.append(_journal_and_telemetry_protocol_section(text))
        checks.append(_routes_all_three_engagement_modes(text))
        checks.append(_delegates_block_a_to_the_script(text))
    return checks
