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

Active-change signal (any one):
  - a PRD is IN FLIGHT: some .prd/prd-v*.md whose front-matter `status:` is not
    a closing one (archived / built / superseded / ...). A PRD that has shipped
    is a permanent record, not a running change, and must not hold the gate
    open — see _CLOSED_PRD_STATUSES and _prd_is_in_flight().
  - an explicit marker: .prd/ACTIVE_CHANGE (gitignored — it acknowledges work
    deliberately done outside a cycle on ONE machine; committing it would
    disable the gate for everyone who clones).

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

# PRD front-matter `status:` values meaning the change cycle is CLOSED. A PRD
# carrying one of these is a record of finished work and must NOT hold the
# harness gate open; anything else (including a PRD with no `status:` at all)
# counts as a change still in flight. See _prd_is_in_flight().
_CLOSED_PRD_STATUSES = frozenset({
    "archived", "built", "superseded", "shipped", "done", "abandoned", "merged",
})
# Front matter is a handful of keys; cap the scan so a pathological file can
# never turn a per-edit hook into a full read.
_FRONT_MATTER_MAX_LINES = 40

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


def _prd_is_in_flight(path: Path) -> bool:
    """True when this PRD's front matter does NOT carry a closing `status:`.

    Deliberately a line scan of the front-matter block, not a YAML parse: this
    runs in a PreToolUse hook on every Edit/Write, so it must stay stdlib-only
    and cheap. A PRD whose front matter cannot be read is treated as IN FLIGHT,
    so a parse problem opens the gate rather than wedging the session — the
    fail-OPEN promise in this module's docstring.
    """
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            if fh.readline().strip() != "---":
                return True                      # no front matter -> not closed
            for _ in range(_FRONT_MATTER_MAX_LINES):
                line = fh.readline()
                if not line or line.strip() == "---":
                    return True                  # block ended, no status: key
                if line.startswith("status:"):
                    status = line.split(":", 1)[1].strip().strip("\"'").lower()
                    return status not in _CLOSED_PRD_STATUSES
    except OSError:
        return True
    return True


def _change_active() -> bool:
    # bb-* uses .prd/ as the planning dir. (The legacy .sprint/ from the prior
    # development-advanced experiment is intentionally NOT a signal — it would
    # leave the gate permanently open; it is retired in the cleanup step.)
    if (PROJECT_DIR / ".prd" / "ACTIVE_CHANGE").exists():
        return True
    # Only a PRD still IN FLIGHT signals an active change. `any(prd-v*.md)` was
    # the original test and was wrong in a way that got worse over time: a PRD is
    # the permanent record of a change, not evidence one is running, so once the
    # first PRD was committed the gate was unconditionally open on every clone,
    # forever. Measured 2026-08-28 on the v7 branch: 6 shipped PRDs present, the
    # gate had not been able to deny for anyone since the first of them landed.
    if any(_prd_is_in_flight(p) for p in (PROJECT_DIR / ".prd").glob("prd-v*.md")):
        return True
    return False


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
