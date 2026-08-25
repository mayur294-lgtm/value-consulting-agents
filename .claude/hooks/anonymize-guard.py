#!/usr/bin/env python3
"""
PreToolUse(Read|Bash) hook — the PII anonymization guard.

Stops UNSCRUBBED client PII from reaching the model's context (and from there an
MCP server / the knowledge graph). Raw client material — discovery transcripts,
engagement intake — lands under `engagements/<client>/<engagement>/inputs/` (and
the shared `engagements/inputs/`) before it is anonymized. The
`scripts/anonymize_transcript.py` tool rewrites a transcript into a sibling
`.anon_<name>` file (real names/emails/phones/accounts replaced by [CLIENT],
[PERSON-N], … placeholders) plus a `.anon_mapping_<stem>.json` for later
de-anonymization of the FINAL deliverable.

This hook blocks a Read (or a Bash `cat`/`head`/… ) of a raw inputs/ text file
that still contains PII and has NOT been anonymized, and points the consultant at
the anonymizer. Once a file carries anonymization placeholders, it is allowed.

Design rules (mirroring the other hooks in this directory):
  - Deliberately NARROW: only text files under an `inputs/` folder inside
    `engagements/`. Everything else — source code, knowledge, docs, the .anon_*
    outputs, binaries (pdf/xlsx/png) — is allowed. This avoids false blocks on
    ordinary files that merely happen to contain an email address.
  - FAIL-OPEN on any error. The original guard was MISSING, so the hook crashed
    and failed CLOSED, wedging every Read/Bash in the session. A guard must never
    do that: on any exception we allow.
  - The anonymizer itself is allow-listed, so the command that scrubs a raw
    transcript is never blocked.

Decision contract (stdout JSON, exit 0):
  - allow -> emit nothing
  - deny  -> emit {"hookSpecificOutput": {permissionDecision: "deny", ...}}
"""
import json
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

# Text formats we can scan; binaries are out of scope (can't regex reliably).
SCANNABLE_EXTS = {".md", ".txt", ".text", ".vtt", ".srt", ".json", ".csv", ".log"}
SAMPLE_BYTES = 256_000  # cap the read; transcripts can be large

# PII patterns — kept in sync with scripts/anonymize_transcript.py.
_PII_RES = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),          # email
    re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),       # phone
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),                                          # SSN
    re.compile(r"\b(?:account|member|acct|ID)[\s#:]*\d{6,}\b", re.IGNORECASE),     # account/member no.
]
# Markers that prove a file has already been anonymized.
_PLACEHOLDER_RE = re.compile(r"\[(?:CLIENT|PERSON-\d+|CLIENT-ABBR|CLIENT-SHORT|REDACTED)[^\]]*\]")


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


def _in_raw_inputs(p: Path) -> bool:
    """True only for a scannable text file that sits under an inputs/ folder
    inside engagements/, and is not itself an anonymized (.anon_*) output."""
    if p.suffix.lower() not in SCANNABLE_EXTS:
        return False
    if p.name.startswith(".anon_"):
        return False
    parts = [part.lower() for part in p.parts]
    return "engagements" in parts and "inputs" in parts


def _is_unscrubbed(p: Path) -> bool:
    """A raw inputs file is 'unscrubbed' if it has no anonymization placeholders
    yet still matches PII patterns. Unreadable -> treat as scrubbed (fail-open)."""
    try:
        text = p.open("r", encoding="utf-8", errors="replace").read(SAMPLE_BYTES)
    except OSError:
        return False
    if _PLACEHOLDER_RE.search(text):
        return False  # already anonymized
    return any(rx.search(text) for rx in _PII_RES)


def _resolve(raw: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = (PROJECT_DIR / p)
    try:
        return p.resolve()
    except OSError:
        return p


def _engagement_dir_for(p: Path):
    """Best-effort: engagements/<client>/<engagement>/inputs/... -> the
    <engagement> directory (parent of `inputs/`), for the deny message's
    `--engagement-dir` argument. None if there's no `inputs` segment
    (shouldn't happen — the caller already confirmed one via _in_raw_inputs)."""
    parts = p.parts
    lowered = [part.lower() for part in parts]
    try:
        idx = lowered.index("inputs")
    except ValueError:
        return None
    if idx == 0:
        return None
    return Path(*parts[:idx])


def _deny_message(p: Path) -> str:
    try:
        label = p.relative_to(PROJECT_DIR)
    except ValueError:
        label = p
    engagement_dir = _engagement_dir_for(p)
    if engagement_dir is not None:
        try:
            engagement_label = engagement_dir.relative_to(PROJECT_DIR)
        except ValueError:
            engagement_label = engagement_dir
    else:
        engagement_label = "<engagement_dir>"
    # scripts/anonymize_transcript.py is now a facade over scripts/pii/engine.py
    # (Presidio), which needs Python 3.10-3.13 — the system `python3` here is
    # 3.9.6 and cannot run it. _resolve_python.sh picks .venv/bin/python when
    # `bash scripts/setup_pii.sh` has been run, and falls back to system
    # python3 otherwise (in which case the command below fails with its own
    # plain-language pointer back to that same setup command — see
    # scripts/anonymize_transcript.py's PIIEngineUnavailable).
    return (
        f"🛑 Anonymization guard: '{label}' looks like RAW client material under "
        f"inputs/ that still contains PII (names/emails/phones/account numbers) and "
        f"has not been anonymized. Reading it would pull unscrubbed PII into context "
        f"where it could reach an MCP server or the knowledge graph.\n"
        f"Scrub it first, then read the anonymized copy:\n"
        f"  .claude/hooks/_resolve_python.sh scripts/anonymize_transcript.py "
        f"--file {label} --engagement-dir {engagement_label}\n"
        f"  # -> writes a sibling .anon_{p.name} (and .anon_mapping_*.json)\n"
        f"Then Read the .anon_ version instead. (Binary inputs like .pdf/.xlsx are "
        f"not gated here — convert/anonymize them before ingesting.)"
    )


# --- Bash path extraction -----------------------------------------------------
# Best-effort: pull path-like tokens out of a shell command so a `cat`/`head` of
# a raw transcript is gated the same as a Read. Never raises.
_ANONYMIZER_HINT = "anonymize_transcript"
_TOKEN_RE = re.compile(r"""['"]?([^\s'";|&><]+)['"]?""")


def _bash_candidates(command: str):
    if _ANONYMIZER_HINT in command:
        return []  # the scrub command itself is always allowed
    cands = []
    for m in _TOKEN_RE.finditer(command):
        tok = m.group(1)
        if "/" not in tok and not tok.lower().endswith(tuple(SCANNABLE_EXTS)):
            continue
        if tok.startswith("-"):
            continue
        cands.append(_resolve(tok))
    return cands


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _allow()

    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input", {}) or {}

    if tool == "Read":
        raw = tool_input.get("file_path")
        if not raw:
            _allow()
        p = _resolve(raw)
        if _in_raw_inputs(p) and p.exists() and _is_unscrubbed(p):
            _deny(_deny_message(p))
        _allow()

    elif tool == "Bash":
        command = tool_input.get("command", "") or ""
        for p in _bash_candidates(command):
            try:
                if _in_raw_inputs(p) and p.exists() and _is_unscrubbed(p):
                    _deny(_deny_message(p))
            except Exception:
                continue  # fail-open per candidate
        _allow()

    _allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        # Never wedge the session on a guard bug — fail OPEN.
        sys.exit(0)
