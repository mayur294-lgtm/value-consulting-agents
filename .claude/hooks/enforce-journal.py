#!/usr/bin/env python3
"""
Stop hook — the POST-completion auditability gate.

Makes three "MANDATORY" governance rules from CLAUDE.md / auditability_protocol.md
actually deterministic instead of advisory. Before the turn is allowed to end, for
every engagement that produced a final deliverable in this session, this hook checks:

  1. JOURNAL FRESHNESS  — a deliverable exists that is newer than the last
                          ENGAGEMENT_JOURNAL.md update (i.e. work was not logged).
  2. TELEMETRY BLOCK    — the journal contains at least one <!-- TELEMETRY_START -->.
  3. DUAL CHECKPOINTS    — at least 2 checkpoints are logged (pre + post generation),
                          counted as "### Checkpoint:" journal blocks + CHECKPOINT_*.md
                          files in outputs/.

If any rule is violated, the stop is BLOCKED and Claude is told exactly what to add.
The fix (append the journal entry / log the checkpoint) is always within Claude's
power, so the check is self-resolving and the loop terminates on the next stop.

Scope: only engagements/*/*/ (real client work). tests/ and examples/ are exempt.
Fail-OPEN: any internal error allows the stop — a buggy hook must never wedge a session.

Decision contract (stdout JSON, exit 0):
  - allow stop -> emit nothing
  - block stop -> emit {"decision": "block", "reason": "..."}
"""
import glob
import json
import os
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

# Only deliverables this fresh count as "this session's work" worth enforcing.
RECENCY_WINDOW_SECONDS = 12 * 3600
# Grace so a deliverable written seconds before the journal append doesn't false-trip.
JOURNAL_GRACE_SECONDS = 120

DELIVERABLE_EXTS = {".md", ".html", ".xlsx", ".pptx", ".pdf", ".docx", ".csv"}
TELEMETRY_MARKER = "<!-- TELEMETRY_START -->"


def _allow():
    sys.exit(0)


def _block(reason: str):
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def _is_deliverable(p: Path) -> bool:
    if p.suffix.lower() not in DELIVERABLE_EXTS:
        return False
    name = p.name
    if name.startswith((".", "interim_", "CHECKPOINT")):
        return False
    if name in {"ENGAGEMENT_JOURNAL.md", "ENGAGEMENT_CONTEXT.md", "CLIENT_PROFILE.md"}:
        return False
    return True


def _newest_deliverable_mtime(outputs: Path):
    newest = 0.0
    if not outputs.is_dir():
        return newest
    for f in outputs.rglob("*"):
        if f.is_file() and _is_deliverable(f):
            try:
                newest = max(newest, f.stat().st_mtime)
            except OSError:
                pass
    return newest


def _checkpoint_count(journal_text: str, outputs: Path) -> int:
    count = journal_text.count("### Checkpoint:")
    if outputs.is_dir():
        count += len(list(outputs.glob("CHECKPOINT_*.md")))
    return count


def _audit_engagement(journal: Path):
    """Return a (label, [findings]) tuple, or None if nothing to enforce."""
    eng_dir = journal.parent
    outputs = eng_dir / "outputs"
    newest = _newest_deliverable_mtime(outputs)
    if newest == 0.0:
        return None  # no final deliverable produced yet — nothing to gate
    if (time.time() - newest) > RECENCY_WINDOW_SECONDS:
        return None  # stale engagement, not this session's work

    try:
        journal_text = journal.read_text(encoding="utf-8", errors="replace")
        journal_mtime = journal.stat().st_mtime
    except OSError:
        return None

    findings = []
    if newest > journal_mtime + JOURNAL_GRACE_SECONDS:
        findings.append(
            "a deliverable was produced after the last journal update — append a "
            "journal entry (agent, inputs, outputs, decisions) to ENGAGEMENT_JOURNAL.md"
        )
    if TELEMETRY_MARKER not in journal_text:
        findings.append(
            f"the journal has no telemetry block — add a {TELEMETRY_MARKER} … "
            "<!-- TELEMETRY_END --> block (agent, session id, timings, file counts, "
            "quality self-check)"
        )
    cp = _checkpoint_count(journal_text, outputs)
    if cp < 2:
        findings.append(
            f"only {cp} consultant checkpoint(s) logged; the protocol requires 2 "
            "(pre-generation + post-generation) — log them as '### Checkpoint:' entries"
        )

    if not findings:
        return None
    label = str(eng_dir.relative_to(PROJECT_DIR)) if str(eng_dir).startswith(str(PROJECT_DIR)) else str(eng_dir)
    return (label, findings)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _allow()

    # Avoid pathological loops: if we already blocked once this turn and Claude is
    # continuing, still re-evaluate — the check is self-resolving, so a real fix clears it.
    _ = payload.get("stop_hook_active", False)

    try:
        journals = glob.glob(str(PROJECT_DIR / "engagements" / "*" / "*" / "ENGAGEMENT_JOURNAL.md"))
    except Exception:
        _allow()

    problems = []
    for j in journals:
        try:
            result = _audit_engagement(Path(j))
        except Exception:
            result = None  # fail-open per engagement
        if result:
            problems.append(result)

    if not problems:
        _allow()

    lines = [
        "🛑 Auditability gate: an engagement produced deliverables without completing "
        "its MANDATORY governance trail (CLAUDE.md → auditability_protocol.md). "
        "Resolve before finishing:",
        "",
    ]
    for label, findings in problems:
        lines.append(f"• {label}")
        for f in findings:
            lines.append(f"    - {f}")
    lines.append("")
    lines.append(
        "Append the missing journal/telemetry/checkpoint records, then stop. "
        "(If this deliverable is genuinely interim/exploratory and not client work, "
        "tell the user — do not silently bypass.)"
    )
    _block("\n".join(lines))


if __name__ == "__main__":
    main()
