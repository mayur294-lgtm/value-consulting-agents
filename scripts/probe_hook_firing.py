#!/usr/bin/env python3.11
"""Probe: do project PreToolUse hooks actually fire under an Agent-SDK
session configured exactly like scripts/orchestrate.py's run_agent()?

QUESTION THIS ANSWERS
  scripts/orchestrate.py never talks to a hook directly — it launches agents
  through claude_agent_sdk.query(). Whether `.claude/settings.json`'s
  PreToolUse hooks (anonymize-guard.py, mcp-query-guard.py, ...) fire for
  those SDK-launched sessions is an empirical fact about the SDK's process
  plumbing, not something you can verify by reading orchestrate.py's source.
  This script asks that question directly: launch a session with
  orchestrate.py's exact ClaudeAgentOptions, trigger a tool call a hook is
  registered against, and observe whether the hook actually ran.

WHY THIS MATTERS (see requirements.txt's claude-agent-sdk pin, and the
comment on ClaudeAgentOptions(setting_sources=...) in orchestrate.py's
run_agent())
  orchestrate.py never set `setting_sources` on ClaudeAgentOptions, so the
  SDK defaulted it to None. In claude_agent_sdk 0.1.39 (and every version
  through 0.1.59) an unset setting_sources is serialized to the CLI the same
  way as an explicit empty list, and both are treated as "load user + project
  + local settings" — so project hooks fire. The SDK's own docs say this
  flips after 0.1.59: an empty/unset setting_sources then DISABLES filesystem
  settings, silently turning off every project hook (anonymize-guard.py and
  mcp-query-guard.py included) with no error anywhere. orchestrate.py now
  sets setting_sources explicitly as a fix, and requirements.txt pins the SDK
  version as a second line of defense — but neither of those is a substitute
  for actually observing a hook fire. This script is that observation, made
  repeatable: run it after any claude-agent-sdk version bump, or periodically,
  to reconfirm hooks still fire under orchestrate.py's real options.

PREREQUISITE
  A valid, non-expired CLI session — run `claude auth login` first. This
  script preflights that with `claude auth status` and fails fast with a
  plain-language message (not a stack trace) if it's missing or expired,
  since the SDK call itself would otherwise fail deep inside the transport
  layer with a much less legible error.

WHAT IT DOES
  Uses the existing, already-verified anonymize-guard.py hook (matcher
  "Read|Bash") as the probe. mcp-query-guard.py itself can't be exercised
  end-to-end here (it gates the Backbase Infobank MCP server, which needs
  live Backbase SSO) — but it registers through the exact same
  .claude/settings.json PreToolUse plumbing, with only the tool-name matcher
  differing. If anonymize-guard.py fires under these options, the mechanism
  mcp-query-guard.py depends on is proven to apply to it too.

  Writes a single throwaway fixture file in a SYSTEM TEMPDIR (never inside
  this repo) whose path merely contains "engagements" and "inputs" path
  segments — all anonymize-guard.py's _in_raw_inputs() actually checks — and
  fake-but-PII-shaped content (a made-up email/phone, not real data). Asks
  the agent to Read that exact path and nothing else, then checks whether the
  tool call came back denied with anonymize-guard's message.

  Changes nothing in this repository: it only reads .claude/settings.json
  (to let the SDK discover it) and never writes inside the repo tree.

USAGE
    python3.11 scripts/probe_hook_firing.py
"""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FIXTURE_CONTENT = (
    "# Throwaway discovery-call fixture (probe_hook_firing.py)\n\n"
    "Contact: jane.probe.doe@example-fixture.invalid\n"
    "Phone: 555-010-0199\n\n"
    "This file exists only to give anonymize-guard.py a PII pattern to catch. "
    "It is not real client data and lives entirely in a system tempdir.\n"
)


def _fail(message: str) -> "None":
    print(f"\nFAIL — {message}\n")
    sys.exit(1)


def _check_auth_or_fail() -> None:
    """Fail fast, in plain language, if there is no valid CLI session —
    rather than let the SDK call fail deep in the transport layer."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        _fail(
            "the 'claude' CLI is not on PATH. This probe launches sessions "
            "through the Agent SDK, which shells out to that binary — install "
            "Claude Code / put it on PATH first."
        )

    try:
        result = subprocess.run(
            [claude_bin, "auth", "status"],
            capture_output=True, text=True, timeout=30,
        )
    except Exception as exc:  # noqa: BLE001
        _fail(f"could not run '{claude_bin} auth status' ({type(exc).__name__}: {exc}).")

    try:
        status = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        _fail(
            "'claude auth status' returned output this script couldn't parse — "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        return  # unreachable, keeps type checkers happy

    if not status.get("loggedIn"):
        _fail(
            "no valid CLI session — 'claude auth status' reports loggedIn=false "
            f"(authMethod={status.get('authMethod')!r}). Run `claude auth login` "
            "(or `/login` inside an interactive session) with a valid token, "
            "then re-run this probe."
        )


# Text markers the CLI/SDK is observed to emit when a session's OAuth token
# is missing or expired (see the exception this script replaces catching a
# raw "Not logged in · Please run /login" assistant message and an opaque
# "Command failed with exit code 1" SDK exception). Used as a defense-in-depth
# check on top of _check_auth_or_fail(), in case the token expires between
# the preflight and the actual call.
_AUTH_FAILURE_MARKERS = (
    "not logged in",
    "please run /login",
    "please login",
    "unauthorized",
    "invalid api key",
)


async def _run_probe() -> bool:
    """Returns True if the hook fired (denied the Read), False if it did not
    (the Read was allowed through). Raises only for genuinely unexpected
    errors — auth failures are translated to a plain message before this is
    ever called."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolResultBlock,
        ToolUseBlock,
        UserMessage,
        query,
    )

    with tempfile.TemporaryDirectory(prefix="probe_hook_firing_") as td:
        # Path only needs "engagements" and "inputs" as path segments —
        # that's all anonymize-guard.py's _in_raw_inputs() checks. It does
        # NOT need to live inside this repo, and it never does.
        fixture = Path(td) / "engagements" / "probe_synth" / "inputs" / "fixture.md"
        fixture.parent.mkdir(parents=True)
        fixture.write_text(FIXTURE_CONTENT, encoding="utf-8")

        # Mirrors orchestrate.py's run_agent() ClaudeAgentOptions exactly
        # (including the setting_sources fix from this same PR cycle) —
        # cwd is the repo root (not an engagement subdirectory) so project
        # settings discovery only has one directory to resolve, which is
        # sufficient to prove the mechanism; the CLI walks upward from cwd
        # to find the project root either way.
        options = ClaudeAgentOptions(
            system_prompt=(
                "You are a test harness. Call the Read tool on exactly this "
                f"path and nothing else: {fixture}. Do not explain, just call "
                "the tool."
            ),
            allowed_tools=["Read"],
            permission_mode="bypassPermissions",
            cwd=str(REPO_ROOT),
            model="claude-haiku-4-5-20251001",
            max_turns=3,
            env={"CLAUDECODE": ""},
            setting_sources=["user", "project", "local"],
        )

        saw_tool_call = False
        saw_deny = False
        assistant_text: list[str] = []

        async for message in query(prompt="Read the file now.", options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        saw_tool_call = True
                        print(f"  [tool_use] {block.name} input={block.input}")
                    elif isinstance(block, TextBlock) and block.text.strip():
                        text = block.text.strip()
                        assistant_text.append(text)
                        print(f"  [assistant text] {text[:300]}")
            elif isinstance(message, UserMessage):
                content = message.content if isinstance(message.content, list) else []
                for block in content:
                    if isinstance(block, ToolResultBlock):
                        result_text = str(block.content)
                        print(f"  [tool_result] is_error={block.is_error} content={result_text[:400]}")
                        if "anonymiz" in result_text.lower():
                            saw_deny = True
            elif isinstance(message, ResultMessage):
                print(f"  [result] turns={message.num_turns} cost=${message.total_cost_usd}")

        joined = " ".join(assistant_text).lower()
        if any(marker in joined for marker in _AUTH_FAILURE_MARKERS):
            _fail(
                "the CLI session expired mid-probe (assistant reported an auth "
                "failure after the preflight check passed). Run `claude auth "
                "login` again and retry."
            )

        if not saw_tool_call:
            _fail(
                "the agent never attempted the Read tool call at all — this "
                "probe can't distinguish 'hook fired' from 'model didn't "
                "cooperate'. Re-run; if it persists, inspect the transcript above."
            )

        return saw_deny


def main() -> None:
    _check_auth_or_fail()
    print("Auth OK — launching probe session (this costs a small amount of API spend)...\n")

    try:
        fired = asyncio.run(_run_probe())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        _fail(f"unexpected error running the probe session ({type(exc).__name__}: {exc}).")
        return  # unreachable

    print("\n=== RESULT ===")
    if fired:
        print("PASS — anonymize-guard.py fired: project PreToolUse hooks DO load "
              "and run under orchestrate.py's exact ClaudeAgentOptions.")
        sys.exit(0)
    else:
        print("FAIL — the Read was allowed through: project PreToolUse hooks did "
              "NOT fire under orchestrate.py's exact ClaudeAgentOptions. This is "
              "the silent-hook-disable failure mode the claude-agent-sdk pin and "
              "the setting_sources fix exist to prevent — investigate immediately.")
        sys.exit(1)


if __name__ == "__main__":
    main()
