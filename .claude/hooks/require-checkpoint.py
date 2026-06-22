#!/usr/bin/env python3
"""
PreToolUse hook — the PRE-generation checkpoint gate.

Enforces the "checkpoint BEFORE generation" half of the dual-checkpoint rule.
Blocks writing a FINAL client deliverable into an engagement's outputs/ until a
pre-generation checkpoint has been presented and logged. This is what makes
"minimum 2 consultant checkpoints (pre + post)" deterministic instead of advisory:
without this, an agent can generate the whole deliverable and only then (maybe)
log a checkpoint — exactly the "agents make unilateral decisions" failure the
NFIS retrospective flagged.

A pre-generation checkpoint counts as satisfied if EITHER:
  - a CHECKPOINT_*.md file exists in <engagement>/outputs/, OR
  - ENGAGEMENT_JOURNAL.md contains a "### Checkpoint:" block.

Scope (kept deliberately narrow to avoid false blocks):
  - only Write (deliverable creation/overwrite), not Edit
  - only paths under engagements/<client>/<engagement>/outputs/
  - only deliverable file types; CHECKPOINT_*, interim_*, journal/context/dotfiles
    are always allowed so the checkpoint itself can be written first.

Fail-OPEN on parse/lookup errors — never wedge a session on a hook bug.

Decision contract (stdout JSON, exit 0):
  - allow -> emit nothing
  - deny  -> emit {"hookSpecificOutput": {permissionDecision: "deny", ...}}
"""
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

DELIVERABLE_EXTS = {".md", ".html", ".xlsx", ".pptx", ".pdf", ".docx", ".csv"}


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


def _is_final_deliverable(p: Path) -> bool:
    if p.suffix.lower() not in DELIVERABLE_EXTS:
        return False
    name = p.name
    if name.startswith((".", "interim_", "CHECKPOINT")):
        return False
    if name in {"ENGAGEMENT_JOURNAL.md", "ENGAGEMENT_CONTEXT.md", "CLIENT_PROFILE.md"}:
        return False
    parts = {part.lower() for part in p.parts}
    # Only gate real client engagements, and only the outputs/ deliverable folder.
    return "engagements" in parts and "outputs" in parts


def _engagement_dir(p: Path):
    # Deliverables live in <engagement>/outputs/...; the engagement root is the
    # parent of the 'outputs' component. Anchor on that so a stray journal/context
    # copy inside outputs/ can't shadow the real engagement root.
    parts = p.parts
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] == "outputs":
            cand = Path(*parts[:i])
            if (cand / "ENGAGEMENT_JOURNAL.md").exists() or (cand / "ENGAGEMENT_CONTEXT.md").exists():
                return cand
            break
    # Fallback: nearest ancestor (other than outputs/) carrying engagement markers.
    for parent in p.parents:
        if parent.name in {"outputs", "inputs"}:
            continue
        if (parent / "ENGAGEMENT_JOURNAL.md").exists() or (parent / "ENGAGEMENT_CONTEXT.md").exists():
            return parent
    return None


def _has_pre_generation_checkpoint(eng_dir: Path) -> bool:
    outputs = eng_dir / "outputs"
    if outputs.is_dir() and any(outputs.glob("CHECKPOINT_*.md")):
        return True
    journal = eng_dir / "ENGAGEMENT_JOURNAL.md"
    if journal.exists():
        try:
            if "### Checkpoint:" in journal.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            return True  # can't read — fail open
    return False


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _allow()

    if payload.get("tool_name") != "Write":
        _allow()

    raw = (payload.get("tool_input", {}) or {}).get("file_path")
    if not raw:
        _allow()

    p = Path(raw)
    if not p.is_absolute():
        p = (PROJECT_DIR / p).resolve()

    if not _is_final_deliverable(p):
        _allow()

    eng_dir = _engagement_dir(p)
    if eng_dir is None:
        _allow()  # not inside a recognised engagement — don't gate

    if _has_pre_generation_checkpoint(eng_dir):
        _allow()

    label = eng_dir.relative_to(PROJECT_DIR) if str(eng_dir).startswith(str(PROJECT_DIR)) else eng_dir
    _deny(
        f"🛑 Checkpoint gate: about to write the final deliverable '{p.name}' for "
        f"engagement '{label}', but no PRE-generation consultant checkpoint has been "
        f"logged. The auditability protocol requires presenting your plan/assumptions "
        f"to the consultant BEFORE generating.\n"
        f"Do this first:\n"
        f"  1. Present the pre-generation checkpoint (scope, assumptions, value levers) "
        f"to the consultant, OR write outputs/CHECKPOINT_<stage>.md capturing it.\n"
        f"  2. Log it as a '### Checkpoint:' entry in ENGAGEMENT_JOURNAL.md.\n"
        f"Then re-issue this write. (The post-generation checkpoint is enforced "
        f"separately at session end.)"
    )


if __name__ == "__main__":
    main()
