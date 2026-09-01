#!/usr/bin/env python3
"""
PreToolUse(Edit|Write) hook — the synthetic-engagement content guard.

Stops synthetic/fictional engagement material from contaminating the shared
knowledge base. `knowledge/` is read by every downstream engagement (via
domain-*, benchmark-librarian, etc.) — anything written there is treated as
real, citable ground truth. Synthetic engagements (Harborlight, Zenith-style
fixtures, demos) exist under `tests/engagements/` precisely so they never mix
with `knowledge/`. See `tests/engagements/README.md` for the quarantine model.

This hook is the belt-and-braces content backstop behind that convention: it
inspects the CONTENT of an incoming Write/Edit under `knowledge/` for two
markers that should never legitimately land there:
  - `[Synthetic-Test]` under `knowledge/domains/` — the explicit synthetic tier
    tag (legal under `knowledge/learnings/` and `knowledge/standards/`, where
    it documents the tier itself; not legal inside domain content, which is
    read as real benchmark/pattern data).
  - `Harborlight` (case-sensitive) anywhere under `knowledge/` — the fictional
    bank name used across synthetic fixtures/demos. As of the synthetic-
    quarantine cleanup, no legitimate knowledge/ file contains this word, so
    the check has zero standing false-positive surface.

Design rules (mirroring the other hooks in this directory):
  - Deliberately NARROW: only `knowledge/**`, only two content markers. This
    is a content heuristic, not provenance tracing — it cannot catch
    unlabeled synthetic numbers, only these two known contamination markers.
  - FAIL-OPEN on any error. A guard must never wedge the session: on any
    exception we allow, exactly like anonymize-guard.py and require-harness.py.
  - Covers BOTH interactive sessions and the automated pipeline: project
    settings (and therefore PreToolUse hooks) load by default regardless of
    permission mode, so this backstop applies even under a non-interactive
    `bypassPermissions` pipeline run.

Decision contract (stdout JSON, exit 0):
  - allow -> emit nothing
  - deny  -> emit {"hookSpecificOutput": {permissionDecision: "deny", ...}}
"""
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

SYNTHETIC_TAG = "[Synthetic-Test]"
FICTIONAL_NAME = "Harborlight"


def _allow():
    sys.exit(0)


def _deny(reason: str):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def _resolve(raw: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = PROJECT_DIR / p
    try:
        return p.resolve()
    except OSError:
        return p


def _rel(p: Path) -> str:
    try:
        return p.relative_to(PROJECT_DIR.resolve()).as_posix()
    except ValueError:
        try:
            return p.relative_to(PROJECT_DIR).as_posix()
        except ValueError:
            return p.as_posix()


def _deny_message(rel: str, marker: str) -> str:
    return (
        f"🛑 Synthetic-knowledge guard: '{rel}' would write content containing "
        f"'{marker}' into the shared knowledge base. This marker identifies "
        f"synthetic/fictional engagement material, which must stay quarantined "
        f"away from knowledge/ (real engagements read this content as ground "
        f"truth). See tests/engagements/README.md for where synthetic fixtures "
        f"belong and how the quarantine model works."
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _allow()

    tool = payload.get("tool_name")
    if tool not in ("Write", "Edit"):
        _allow()

    tool_input = payload.get("tool_input", {}) or {}
    raw = tool_input.get("file_path")
    if not raw:
        _allow()

    p = _resolve(raw)
    rel = _rel(p)

    # Path prefilter: only knowledge/** is in scope.
    if not (rel == "knowledge" or rel.startswith("knowledge/")):
        _allow()

    if tool == "Write":
        content = tool_input.get("content", "") or ""
    else:  # Edit
        content = tool_input.get("new_string", "") or ""

    if FICTIONAL_NAME in content:
        _deny(_deny_message(rel, FICTIONAL_NAME))

    if SYNTHETIC_TAG in content and (rel == "knowledge/domains" or rel.startswith("knowledge/domains/")):
        _deny(_deny_message(rel, SYNTHETIC_TAG))

    _allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        # Never wedge the session on a guard bug — fail OPEN.
        sys.exit(0)
