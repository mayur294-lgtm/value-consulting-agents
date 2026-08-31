#!/usr/bin/env python3
"""
PreToolUse hook — the bb-* harness auto-trigger gate.

Makes "any change to a component goes through the bb-* lifecycle" deterministic
instead of advisory. Blocks a direct Edit/Write to a CONTENT COMPONENT (an agent,
slash command, output template, presentation engine, or pipeline code) unless a
bb-* change is active (a PRD artifact exists). This is the local enforcement layer
behind the standing CLAUDE.md directive — so even if the recognition is missed, a
raw edit is stopped with a remediation message pointing at /bb-prd.

It deliberately EXEMPTS the harness's own infrastructure (the bb-* skills, hooks,
evals/, .github/, and the .prd/.design planning dirs) so the harness can be built
and maintained without self-deadlock, and EXEMPTS engagement deliverables (those
are gated by require-checkpoint.py instead).

Active-change signal — exactly one, deliberately:
  - .prd/ACTIVE_CHANGE exists. Gitignored, per-machine, never committed.

  A committed PRD is NOT a signal, at any status. Two earlier versions tried to
  make it one and both left the gate open for everybody: first `any(prd-v*.md)`,
  then "any PRD still in flight" — which a committed DRAFT satisfies, so
  shipping a draft re-opened the gate on every clone. Committed state cannot
  express "this machine is mid-cycle"; only a gitignored marker can.

Fail-OPEN on any error — never wedge a session on a hook bug.

Decision contract (stdout JSON, exit 0):
  - allow -> emit nothing
  - deny  -> emit {"hookSpecificOutput": {permissionDecision: "deny", ...}}
"""
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

# Content components — editing these requires an active bb-* change.
PROTECTED_PREFIXES = (
    ".claude/agents/",
    ".claude/commands/",
    "templates/",
    "presentations/",
)
# Pipeline code (the orchestration engine and its scripts).
PROTECTED_PIPELINE_DIR = "scripts/"
PIPELINE_EXTS = {".py"}


# Harness infra + planning dirs + deliverables — always allowed past THIS hook.
EXEMPT_PREFIXES = (
    ".claude/skills/bb-",      # the vendored bb-* skills themselves
    ".claude/skills/coding-standards/",
    ".claude/hooks/",
    "evals/",
    ".github/",
    ".prd/", ".design/", ".brief/", ".sprint/", ".stories/", ".adr/",
)


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


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(PROJECT_DIR.resolve()).as_posix()
    except (ValueError, OSError):
        return p.as_posix()


def _is_protected(rel: str) -> bool:
    if any(rel.startswith(pre) for pre in EXEMPT_PREFIXES):
        return False
    if rel.startswith(PROTECTED_PREFIXES):
        return True
    # any .claude/skills/* that isn't an exempt skill
    if rel.startswith(".claude/skills/"):
        return True
    # pipeline code
    if rel.startswith(PROTECTED_PIPELINE_DIR) and Path(rel).suffix in PIPELINE_EXTS:
        return True
    if rel == "orchestrate.py" or rel.endswith("/orchestrate.py"):
        return True
    return False


def _change_active() -> bool:
    # bb-* uses .prd/ as the planning dir. (The legacy .sprint/ from the prior
    # development-advanced experiment is intentionally NOT a signal — it would
    # leave the gate permanently open; it is retired in the cleanup step.)
    # `.prd/ACTIVE_CHANGE` is the ONLY signal, and it is gitignored on purpose.
    #
    # Two earlier versions of this test were both wrong, in the same direction:
    #
    #   `any(prd-v*.md)`            — every PRD counted, so the gate was open on
    #                                 every clone from the moment the first PRD
    #                                 landed. Measured 2026-08-28: 6 shipped
    #                                 PRDs, gate unable to deny for anyone.
    #   `any(_prd_is_in_flight(p))` — the v7 fix. Better, and still wrong: a
    #                                 DRAFT PRD is committed, so shipping one
    #                                 re-opened the gate for everybody. Measured
    #                                 2026-08-30 on a clean clone containing only
    #                                 `prd-v10.md` (status: draft): an Edit to
    #                                 scripts/orchestrate.py was ALLOWED. Remove
    #                                 that one file and the same Edit was denied.
    #                                 (Mayur's review, finding 1.)
    #
    # The root problem is not which statuses count. It is that COMMITTED STATE
    # CANNOT EXPRESS "this machine is mid-cycle". A draft PRD in the repo says
    # somebody, somewhere, is working — which is not the question this gate asks.
    # Only a gitignored, per-machine marker can answer it, which is precisely
    # what ACTIVE_CHANGE was introduced to be. So the PRD signal is gone rather
    # than re-tuned: any committed artifact used this way reintroduces the same
    # hole the next time one is committed.
    #
    # `/bb-prd` writes ACTIVE_CHANGE when a cycle starts; `/bb-pr-review` clears
    # it. A developer working outside a cycle creates it by hand and deletes it
    # after — which is the acknowledgement, not a loophole.
    return (PROJECT_DIR / ".prd" / "ACTIVE_CHANGE").exists()


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _allow()

    if payload.get("tool_name") not in ("Edit", "Write", "NotebookEdit"):
        _allow()

    raw = (payload.get("tool_input", {}) or {}).get("file_path")
    if not raw:
        _allow()

    rel = _rel(Path(raw))

    if not _is_protected(rel):
        _allow()

    if _change_active():
        _allow()

    _deny(
        f"🛑 Harness gate: '{rel}' is a content component (agent / command / template / "
        f"presentation / pipeline). Per the bb-* development harness, component changes must "
        f"go through the lifecycle — not a direct edit.\n"
        f"Start the change first so the eval gate applies:\n"
        f"  1. Run the bb-prd lifecycle for this change (writes .prd/prd-v*.md with an "
        f"'Eval Acceptance Criteria' section). The agent should do this automatically when a "
        f"change to a component is requested.\n"
        f"  2. Then bb-design → bb-tickets → bb-build (verify = evals) → bb-pr-review.\n"
        f"First time developing here? Run `bash evals/setup_dev.sh` once to configure your "
        f"eval keys (your own Anthropic key + the shared Langfuse keys) — developers only.\n"
        f"If you are intentionally working OUTSIDE a change cycle, create the marker "
        f"`.prd/ACTIVE_CHANGE` to acknowledge it. (Harness infra under .claude/skills/bb-*, "
        f".claude/hooks/, evals/, and .github/ is exempt.)"
    )


if __name__ == "__main__":
    main()
