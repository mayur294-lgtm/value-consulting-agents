#!/usr/bin/env python3
"""Self-test for the mode composer in scripts/orchestrate.py (ticket #101).

Run manually from the repo root:
    python3 tests/fixtures/mode_composer_selftest.py

Covers the ticket's acceptance criteria against tests/fixtures/mode_fixture_agent.md:
  - compose_prompt(fixture, "pipeline", params) -> core + pipeline block only,
    {placeholders} substituted
  - missing mode -> clear error naming available modes
  - required-input preflight (degraded: refuse) fails before an agent run
  - unknown {placeholder} raises, never silently passes through
  - parse_agent_modes on a file without ## Modes returns {}
  - run_agent prompt/mode mutual exclusivity

Exit code 0 = all checks pass.
"""
import asyncio
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

# Stub the Claude Agent SDK if absent so orchestrate.py imports in dev
# environments — this self-test never launches an agent.
try:
    import claude_agent_sdk  # noqa: F401
except ImportError:
    stub = types.ModuleType("claude_agent_sdk")
    for name in ("query", "ClaudeAgentOptions", "AssistantMessage",
                 "ResultMessage", "TextBlock", "ToolUseBlock"):
        setattr(stub, name, type(name, (), {}))
    sys.modules["claude_agent_sdk"] = stub

import orchestrate  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "mode_fixture_agent.md"
_failures = []


def check(label: str, cond: bool, detail: str = ""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        _failures.append(label)


def main():
    print(f"Fixture: {FIXTURE}")

    # ── parse_agent_modes ────────────────────────────────────────────────
    modes = orchestrate.parse_agent_modes(FIXTURE)
    check("two modes parsed", set(modes) == {"standalone", "pipeline"}, f"got {set(modes)}")
    pl = modes.get("pipeline", {})
    check("pipeline contract parsed",
          pl.get("contract", {}).get("degraded") == "refuse"
          and pl.get("contract", {}).get("params") == ["outputs_dir", "domain"]
          and pl.get("contract", {}).get("inputs", {}).get("required")
          == ["{outputs_dir}/evidence_register.md"],
          f"got {pl.get('contract')}")
    check("pipeline prose captured", "FIXTURE-PIPELINE-PROSE" in pl.get("prose", ""))
    check("standalone degraded=ask-inline",
          modes.get("standalone", {}).get("contract", {}).get("degraded") == "ask-inline")

    # No ## Modes section -> {} (legacy agent, e.g. any current .claude/agents file)
    legacy = ROOT / ".claude" / "agents" / "benchmark-librarian.md"
    if legacy.exists():
        check("legacy agent (no ## Modes) -> {}", orchestrate.parse_agent_modes(legacy) == {})

    with tempfile.TemporaryDirectory() as td:
        outputs_dir = Path(td) / "outputs"
        outputs_dir.mkdir()
        (outputs_dir / "evidence_register.md").write_text("E01 fixture evidence\n")
        params = {"outputs_dir": str(outputs_dir), "domain": "retail"}

        # ── compose_prompt happy path ────────────────────────────────────
        prompt = orchestrate.compose_prompt(str(FIXTURE), "pipeline", params)
        check("core identity present", "FIXTURE-CORE-IDENTITY" in prompt)
        check("selected mode block present", "FIXTURE-PIPELINE-PROSE" in prompt)
        check("other modes stripped", "FIXTURE-STANDALONE-PROSE" not in prompt)
        check("frontmatter stripped", "color: gray" not in prompt)
        check("placeholders substituted",
              str(outputs_dir) in prompt and "{outputs_dir}" not in prompt
              and "{domain}" not in prompt)
        check("params table present",
              "## Runtime Parameters" in prompt and "| domain | retail |" in prompt)

        # ── missing mode -> error naming available modes ─────────────────
        try:
            orchestrate.compose_prompt(str(FIXTURE), "excel-source", params)
            check("missing mode raises", False)
        except ValueError as e:
            check("missing mode raises, names available modes",
                  "excel-source" in str(e) and "pipeline" in str(e) and "standalone" in str(e),
                  str(e))

        # ── required-input preflight (degraded: refuse) ──────────────────
        (outputs_dir / "evidence_register.md").unlink()
        try:
            orchestrate.compose_prompt(str(FIXTURE), "pipeline", params)
            check("preflight refuses on missing required input", False)
        except RuntimeError as e:
            check("preflight refuses on missing required input",
                  "REQUIRED INPUT MISSING" in str(e) and "evidence_register.md" in str(e), str(e))

        # ── unknown placeholder raises ────────────────────────────────────
        try:
            orchestrate.compose_prompt(str(FIXTURE), "pipeline", {"outputs_dir": str(outputs_dir)})
            check("unknown placeholder raises", False)
        except KeyError as e:
            check("unknown placeholder raises", "domain" in str(e), str(e))

    # ── run_agent signature guards (no SDK call is reached) ──────────────
    for label, kwargs in [
        ("run_agent rejects prompt+mode", dict(prompt="x", mode="pipeline", cwd=ROOT)),
        ("run_agent rejects neither prompt nor mode", dict(cwd=ROOT)),
        ("run_agent rejects params without mode", dict(prompt="x", params={"a": 1}, cwd=ROOT)),
    ]:
        try:
            asyncio.run(orchestrate.run_agent("benchmark-librarian", **kwargs))
            check(label, False)
        except ValueError:
            check(label, True)

    print()
    if _failures:
        print(f"SELF-TEST FAILED — {len(_failures)} failing check(s): {_failures}")
        return 1
    print("SELF-TEST PASSED — all checks green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
