#!/usr/bin/env python3
"""
PreToolUse(Read|Bash) hook — the PII anonymization guard.

TICKET #164 REWRITE — READ THIS BEFORE "SIMPLIFYING" IT BACK
  The ticket that produced this file asked for the inline PII regexes to be
  replaced with `scripts/pii/engine.py` (Presidio) so detection logic exists
  in exactly one place. That was NOT done, deliberately — see
  .design/solution-design-v6.md D13 for the full decision record. Short
  version: this hook fires SYNCHRONOUSLY on every Read and every Bash call,
  in every session. Measured cold-start cost of importing the Presidio
  engine (spaCy model load + first analyze) is ~0.7-1.1s; this hook's own
  budget, measured before and after this rewrite, is ~0.04s. Paying that on
  every tool call would make every session feel broken, and a module-level
  import failure in a PreToolUse hook raises BEFORE main()'s try/except and
  exits in a way Claude Code treats as non-blocking — i.e. it would fail
  OPEN, which is exactly backwards for a guard whose job is failing closed.

  So: THIS HOOK DOES NOT DETECT PII. It never has content-sniffed reliably
  either (the previous version's 5 regexes covered 3 of 77 real input
  files) — it answers a narrower, purely structural question instead:

      Has this raw file under engagements/*/inputs/ already been run
      through the anonymizer, and is that scrubbed copy still current?

  That is answerable from PATHS AND TIMESTAMPS alone:

      Anything under engagements/*/inputs/ is blocked unless it is itself
      an `.anon_` artifact, or has a CURRENT `.anon_` sibling.

  No content is ever read. No spaCy, no Presidio, no import risk. This is
  also STRICTER than content-sniffing: a raw file whose PII happened not to
  match a hand-rolled regex used to pass through unchallenged; now nothing
  under inputs/ passes without a scrubbed sibling to point at, regardless of
  what it contains.

WHAT COUNTS AS "SCRUBBED", PER FORMAT (mirrors scripts/pii/ingest.py's
OUTPUT NAMING and scripts/anonymize_transcript.py's facade — kept here as a
plain literal copy rather than an import; see "WHY NOT IMPORT" below)

  - Plain text (`.md .txt .text .vtt .srt .json .log`) — scrubbed by
    `scripts/anonymize_transcript.py`. Sibling is `.anon_<name>` verbatim
    (`report.md` -> `.anon_report.md`).
  - Documents (`.pdf .docx .pptx .xlsx .csv`) — scrubbed by
    `scripts/pii/ingest.py` (#162). Sibling is `.anon_<name>.md`
    (`report.pdf` -> `.anon_report.pdf.md`) — the source extension is KEPT
    so `Pricing.pdf` and `Pricing.xlsx` in the same folder can't collide.
  - Images (`.png .jpg .jpeg .gif .bmp .tif .tiff .webp .heic`) — OCR'd by
    `scripts/pii/ingest.py` (#163). Same `.anon_<name>.md` text-sidecar
    naming as documents; a redacted `.anon_<name>.png` is written alongside
    it, but the TEXT SIDECAR is what "carries the round-trip" (ingest.py's
    own module docstring) and is what this guard checks for freshness.
  - Anything else under inputs/ (`.key`, `.ppt`, no extension, ...) has no
    extractor — it is blocked outright and told to export to a supported
    format, never silently allowed through unrecognised.

  Recognising a scrubbed artifact is 100% NAME-based: any file whose name
  already starts with `.anon_` is allowed, full stop — this hook never
  opens it to check WHICH placeholder convention is inside (today's
  `<ENTITY_N>`, or the legacy `[CLIENT]`/`[PERSON-N]`/`[X-REDACTED]` forms
  an engagement scrubbed before this cycle may still carry). Which
  convention produced an `.anon_` file's placeholders is irrelevant to
  whether it is safe to open — an `.anon_` file is, by construction, never
  the raw client document.

SIBLING STALENESS
  If the raw file's mtime is newer than its `.anon_` sibling's, the sibling
  no longer reflects what is in the raw file — it is treated exactly like a
  missing sibling (denied), not silently trusted. A stale scrub is worse
  than no scrub because it looks safe.

WHY NOT IMPORT `scripts/pii/ingest.py`'S CONSTANTS
  `scripts/pii/ingest.py` is itself stdlib-only and fast to import (measured
  ~15-60ms even under the system Python 3.9.6 this hook runs under) — it
  would be technically safe to import its DOCUMENT_SUFFIXES/IMAGE_SUFFIXES/
  anon_path_for instead of hand-copying them below. This hook deliberately
  does NOT, for the same reason `.claude/hooks/mcp-query-guard.py` does not
  import `scripts/pii/denylist.py` despite it existing (see
  `scripts/pii/drift_check.py`'s header): a guard whose job is failing
  closed must stay self-contained, so a change to scripts/pii/ — even an
  innocuous one — can never silently break, or silently widen, what this
  hook allows. The lists below MUST be kept in sync BY HAND with
  scripts/pii/ingest.py's DOCUMENT_SUFFIXES / IMAGE_SUFFIXES / OUTPUT NAMING
  section if either changes.

FAIL-CLOSED, SCOPED TO inputs/ (mirrors the constraint that produced D4)
  A globally fail-closed guard wedged every session once already (PR #82).
  This hook keeps that lesson: ANY unexpected failure while evaluating a
  path that (on its raw, unresolved text) looks like it lives under
  engagements/*/inputs/ denies the call. The same failure evaluating a path
  that does not look like an inputs/ path allows it. See `_evaluate` and
  `_raw_looks_like_inputs`.

Decision contract (stdout JSON, exit 0):
  - allow -> emit nothing
  - deny  -> emit {"hookSpecificOutput": {permissionDecision: "deny", ...}}
"""
import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

ANON_PREFIX = ".anon_"

# Plain-text formats scrubbed by scripts/anonymize_transcript.py. Sibling is
# `.anon_<name>` verbatim — no added extension. MUST mirror the exclusion
# list in scripts/pii/ingest.py's module docstring ("Plain-text inputs ...
# are NOT handled here"). NOTE: `.csv` is deliberately NOT here — it is a
# DOCUMENT format per ingest.py's DOCUMENT_SUFFIXES (see below), not a plain
# text one; its sibling carries the added `.md`.
TEXT_EXTS = {".md", ".txt", ".text", ".vtt", ".srt", ".json", ".log"}

# Document formats scripts/pii/ingest.py converts (#162). MUST mirror
# scripts/pii/ingest.py's `DOCUMENT_SUFFIXES` tuple.
DOCUMENT_EXTS = {".pdf", ".docx", ".pptx", ".xlsx", ".csv"}

# Image formats scripts/pii/ingest.py OCRs (#163). MUST mirror
# scripts/pii/ingest.py's `IMAGE_SUFFIXES` tuple.
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic"}

ALL_GATED_EXTS = TEXT_EXTS | DOCUMENT_EXTS | IMAGE_EXTS

# ux-design-v6.md Flow C, VERBATIM — must match scripts/pii/ingest.py's
# LOGO_NOTICE constant word for word. Hand-copied rather than imported, for
# the same self-containment reason as the extension lists above.
_LOGO_NOTICE = (
    "ℹ️  About screenshots\n\n"
    "   Cortex blanks out any client details it can *read* in an image —\n"
    "   names, emails, account numbers.\n\n"
    "   It cannot blank a logo. A logo is a picture, not text, so it stays\n"
    "   visible and reaches Claude.\n\n"
    "   If a screenshot shows the client's logo, crop it out before adding it."
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


# --- scope + classification --------------------------------------------------

def _in_scope(p: Path) -> bool:
    """True only for a path under an `inputs/` folder inside `engagements/`
    — matched on exact path SEGMENTS (not substring), so e.g.
    `.../engagements-backup/inputs-old/...` does not false-positive. This is
    the ENTIRE scope of this hook; everything else is allowed unconditionally
    and un-gated, exactly as before this rewrite."""
    parts = [part.lower() for part in p.parts]
    return "engagements" in parts and "inputs" in parts


def _raw_looks_like_inputs(raw: str) -> bool:
    """Cheap, exception-free scope pre-check on the RAW path STRING, before
    any filesystem access — used only to pick the fail-open/fail-closed
    default if evaluating the path then raises. Splitting a string into
    Path parts cannot itself fail; a truly degenerate input is treated as
    in-scope so it fails CLOSED rather than open."""
    try:
        parts = [part.lower() for part in Path(raw).parts]
    except Exception:
        return True
    return "engagements" in parts and "inputs" in parts


def _kind_for(p: Path) -> Optional[str]:
    """'text' | 'document' | 'image' | None (format has no extractor)."""
    suffix = p.suffix.lower()
    if suffix in TEXT_EXTS:
        return "text"
    if suffix in DOCUMENT_EXTS:
        return "document"
    if suffix in IMAGE_EXTS:
        return "image"
    return None


def _sibling_for(p: Path, kind: str) -> Path:
    """The `.anon_` artifact that proves `p` has been scrubbed. Text keeps
    the bare `.anon_<name>` convention; documents and images both get the
    `.anon_<name>.md` text-sidecar convention (see module docstring)."""
    if kind == "text":
        return p.with_name(ANON_PREFIX + p.name)
    return p.with_name(ANON_PREFIX + p.name + ".md")


def _resolve(raw: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = PROJECT_DIR / p
    try:
        return p.resolve()
    except OSError:
        return p


def _label_for(p: Path) -> str:
    try:
        return str(p.relative_to(PROJECT_DIR))
    except ValueError:
        return str(p)


def _engagement_dir_for(p: Path) -> Optional[Path]:
    """engagements/<client>/<engagement>/inputs/... -> the <engagement>
    directory (parent of `inputs/`), for the printed command's
    `--engagement-dir`. None if there's no `inputs` segment (shouldn't
    happen — the caller already confirmed one via `_in_scope`)."""
    parts = p.parts
    lowered = [part.lower() for part in parts]
    try:
        idx = lowered.index("inputs")
    except ValueError:
        return None
    if idx == 0:
        return None
    return Path(*parts[:idx])


def _engagement_label_for(p: Path) -> str:
    d = _engagement_dir_for(p)
    if d is None:
        return "<engagement_dir>"
    return _label_for(d)


# --- messages ------------------------------------------------------------
#
# Copy rules (ux-design-v6.md, binding): no tool names in consultant-facing
# prose; consequence before instruction; always say whether they're blocked;
# one command, not a sequence.
#
# The commands below were run VERBATIM against real fixtures before being
# written here (ticket #164 verification). `scripts/pii/ingest.py` cannot be
# invoked as `python3 scripts/pii/ingest.py ...` — its `_main()` does
# `from . import engine`, a package-relative import that raises
# `ImportError: attempted relative import with no known parent package` when
# the file is run directly as a script (confirmed; this module is in the
# excluded scripts/pii/* path so it isn't this ticket's to fix). The working
# invocation, used below, is `python -m scripts.pii.ingest ...` from the repo
# root. `scripts/anonymize_transcript.py` has no such issue and keeps its
# existing `python3 scripts/anonymize_transcript.py` form.

_TEXT_CMD = (
    ".claude/hooks/_resolve_python.sh scripts/anonymize_transcript.py \\\n"
    "           --file \"{label}\" --engagement-dir {eng}"
)
_INGEST_CMD = (
    ".claude/hooks/_resolve_python.sh -m scripts.pii.ingest \\\n"
    "           --file \"{label}\" --engagement-dir {eng}"
)


def _msg_unscrubbed_text(p: Path) -> str:
    label = _label_for(p)
    eng = _engagement_label_for(p)
    command = _TEXT_CMD.format(label=label, eng=eng)
    return (
        "\U0001f6d1 This file hasn't been cleaned yet\n\n"
        f"   {label} is straight from the client. Opening it would send their real\n"
        "   names, emails and account numbers to Claude.\n\n"
        "   Clean it first:\n\n"
        f"       {command}\n\n"
        f"   That creates .anon_{p.name} — open that one instead."
    )


def _msg_unscrubbed_document(p: Path) -> str:
    label = _label_for(p)
    eng = _engagement_label_for(p)
    command = _INGEST_CMD.format(label=label, eng=eng)
    ext = (p.suffix.lstrip(".") or "file").upper()
    return (
        "\U0001f6d1 This file hasn't been cleaned yet\n\n"
        f"   {label} is straight from the client. Opening it would send their real\n"
        "   names, emails and account numbers to Claude.\n\n"
        f"   Clean it first — this also turns the {ext} into readable text:\n\n"
        f"       {command}\n\n"
        f"   That creates .anon_{p.name}.md — open that one instead."
    )


def _msg_unscrubbed_image(p: Path) -> str:
    label = _label_for(p)
    eng = _engagement_label_for(p)
    command = _INGEST_CMD.format(label=label, eng=eng)
    return (
        "\U0001f6d1 This file hasn't been cleaned yet\n\n"
        f"   {label} is straight from the client. Opening it would send their real\n"
        "   names, emails and account numbers to Claude.\n\n"
        "   Clean it first — this also produces a redacted copy of the picture:\n\n"
        f"       {command}\n\n"
        f"   That creates .anon_{p.name}.md (readable text) and .anon_{p.name}.png\n"
        "   (redacted picture) — open those instead.\n\n"
        f"{_LOGO_NOTICE}"
    )


def _msg_unsupported(p: Path) -> str:
    label = _label_for(p)
    ext = p.suffix.lower() or "(no extension)"
    return (
        "\U0001f6d1 This file type isn't supported yet\n\n"
        f"   {label} is a {ext} file. Cortex can't read {ext} files yet, so there's no\n"
        "   way to confirm client details have been removed from it — it must stay\n"
        "   closed.\n\n"
        "   Export it as PDF (or Word, PowerPoint, Excel, CSV, or a picture) and add\n"
        "   that copy to inputs/ instead."
    )


def _msg_stale(p: Path, sibling: Path, kind: str) -> str:
    label = _label_for(p)
    eng = _engagement_label_for(p)
    sibling_name = sibling.name
    command = (_TEXT_CMD if kind == "text" else _INGEST_CMD).format(label=label, eng=eng)
    return (
        "\U0001f6d1 This file's cleaned copy is out of date\n\n"
        f"   {label} has changed since {sibling_name} was created. That older copy can\n"
        "   no longer be trusted to reflect what's in the file now, so neither one\n"
        "   should be opened yet.\n\n"
        "   Clean it again:\n\n"
        f"       {command}\n\n"
        f"   That refreshes {sibling_name} — open that one instead."
    )


def _msg_fault(raw: str) -> str:
    return (
        "\U0001f6d1 Cortex can't confirm this file is safe to open right now\n\n"
        f"   Something went wrong while checking whether {raw} has been cleaned of\n"
        "   client details. Until that's confirmed, it must stay closed.\n\n"
        "   Try again, or ask Claude for help if this keeps happening."
    )


# --- evaluation ------------------------------------------------------------

def _msg_search_root(d) -> str:
    return (
        "🛑 That search reads straight from the client's raw files\n\n"
        "   %s holds material exactly as it came from the client — real names,\n"
        "   emails and account numbers. A search here returns those lines to Claude,\n"
        "   the same as opening the file would.\n\n"
        "   Search the scrubbed copies instead, or clean the folder first:\n\n"
        "       .claude/hooks/_resolve_python.sh scripts/anonymize_transcript.py \\\n"
        "           --file <file> --engagement-dir <engagement_dir>\n"
    ) % d


def _evaluate(raw: str) -> Optional[str]:
    """Returns a deny message, or None to allow. Fails CLOSED (a generic
    fault message) for a raw string that structurally looks like an
    inputs/ path if anything unexpected happens while evaluating it; fails
    OPEN (None) for everything else — see module docstring."""
    in_scope_guess = _raw_looks_like_inputs(raw)
    try:
        p = _resolve(raw)
        if not _in_scope(p):
            return None
        if not p.exists():
            return None  # nothing on disk yet -> nothing to leak
        if not p.is_file():
            return None
        if p.name.startswith(ANON_PREFIX):
            return None  # it IS a scrubbed artifact (any placeholder convention)

        kind = _kind_for(p)
        if kind is None:
            return _msg_unsupported(p)

        sibling = _sibling_for(p, kind)
        if not sibling.is_file():
            if kind == "text":
                return _msg_unscrubbed_text(p)
            if kind == "document":
                return _msg_unscrubbed_document(p)
            return _msg_unscrubbed_image(p)

        if p.stat().st_mtime > sibling.stat().st_mtime:
            return _msg_stale(p, sibling, kind)

        return None
    except Exception:
        if in_scope_guess:
            return _msg_fault(raw)
        return None



def _evaluate_search_root(raw: str) -> Optional[str]:
    """Grep/Glob variant of `_evaluate`, for a path that may be a DIRECTORY.

    `_evaluate` returns None for a directory, which is right for Read (you
    cannot Read a directory) and for Bash (a bare directory token is not a
    read). It is wrong for a search: the directory IS the root, and Grep
    returns matching LINES from everything beneath it.

    Scope is deliberately the same the rest of this guard claims — a path that
    IS, or sits inside, a gated `engagements/*/inputs/` tree. A recursive search
    rooted ABOVE that tree still reaches it, and is NOT covered here: blocking
    every search over any directory that happens to contain an engagement would
    deny grepping the repo itself, and a control that fires on ordinary work is
    one people learn to route around. Recorded in `.prd/backlog.md` rather than
    papered over.
    """
    try:
        p = _resolve(raw)
        if p.is_dir() and _in_scope(p / "probe"):
            return _msg_search_root(p)
    except Exception:
        if _raw_looks_like_inputs(raw):
            return _msg_fault(raw)
        return None
    return _evaluate(raw)

# --- Bash path extraction -----------------------------------------------------
# Best-effort: pull path-like tokens out of a shell command so a `cat`/`head` of
# a raw file is gated the same as a Read. Never raises.
_ANONYMIZER_HINTS = ("anonymize_transcript", "scripts.pii.ingest", "pii/ingest.py", "pii.ingest")

# Shell operators that end one command and begin another. A command line is
# split on these and each SEGMENT is judged on its own.
_SEGMENT_RE = re.compile(r"&&|\|\||;|\||\n")


def _segment_candidates(segment: str):
    """Path-like tokens in ONE shell command segment.

    `shlex` rather than a regex, because a regex that splits on whitespace
    cannot see quoting: `cat "…/Meeting Notes.md"` splits into two fragments,
    neither of which is a real path, so nothing gets checked and the read is
    allowed. Client files are called "Annual Report 2025.pdf" — spaces are the
    norm. Falls back to the old token scan if the line will not lex (an
    unbalanced quote), because failing to parse must not mean failing to check.
    """
    try:
        toks = shlex.split(segment, comments=False, posix=True)
    except ValueError:
        # Unbalanced quote. The OLD fallback split on whitespace, which loses
        # exactly the paths this fix is about — an unterminated
        # `cat "…/Meeting Notes.md` would fragment and sail through. Grab
        # quoted RUNS even when unterminated, so a spaced path survives intact.
        toks = [next(g for g in m if g is not None)
                for m in re.findall(r"""\"([^"]*)\"?|'([^']*)'?|(\S+)""", segment)]
    cands = []
    for tok in toks:
        if tok.startswith("-"):
            continue
        if "/" not in tok and not tok.lower().endswith(tuple(ALL_GATED_EXTS)):
            continue
        cands.append(tok)
    return cands


def _bash_candidates(command: str):
    """Path-like tokens across a whole command line, PER SEGMENT.

    The anonymiser exemption is scoped to the segment that actually invokes it,
    not to the whole line. Previously any line merely CONTAINING the substring
    "anonymize_transcript" was waved through in full, so

        python3 scripts/anonymize_transcript.py --file a.md && cat <raw input>

    handed the raw client file straight to the model. That is not a contrived
    chain: when this guard denies a read, its own message tells the consultant
    to run that scrub command, and appending "&& show me the file" is the
    obvious next keystroke.
    """
    cands = []
    for segment in _SEGMENT_RE.split(command or ""):
        if not segment.strip():
            continue
        if any(hint in segment for hint in _ANONYMIZER_HINTS):
            continue  # THIS segment is the scrub itself — exempt, on its own
        cands.extend(_segment_candidates(segment))
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
        msg = _evaluate(raw)
        if msg:
            _deny(msg)
        _allow()

    elif tool == "Bash":
        command = tool_input.get("command", "") or ""
        for raw in _bash_candidates(command):
            msg = _evaluate(raw)
            if msg:
                _deny(msg)
        _allow()

    elif tool in ("Grep", "Glob"):
        # Grep RETURNS MATCHING LINES — that is file content, so an ungated
        # Grep into `inputs/` hands over real names and emails exactly as a Read
        # would. This guard was bound to Read|Bash only, so the rewrite's
        # "nothing under inputs/ passes" guarantee had a third door standing
        # open. Glob returns paths rather than content and is far weaker, but a
        # client-named FILENAME is itself an identifier this repo spends real
        # effort removing, so it is gated the same way.
        #
        # Both take `path` (a directory OR a file). A directory is evaluated as
        # itself: `_evaluate` resolves whether it sits under a gated
        # `engagements/*/inputs/` tree, which is the question being asked.
        raw = tool_input.get("path") or tool_input.get("file_path")
        if not raw:
            _allow()
        msg = _evaluate_search_root(raw)
        if msg:
            _deny(msg)
        _allow()

    _allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        # Last-resort backstop for a bug in the hook itself (not a specific
        # path's evaluation, which _evaluate already fails closed on inside
        # inputs/) — never wedge the session. Matches the pre-#164 guard's
        # own outermost behaviour.
        sys.exit(0)
