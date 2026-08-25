#!/usr/bin/env python3
"""
Transcript PII Anonymizer — thin facade over scripts/pii/engine.py (Presidio).

WHAT CHANGED (ticket #160, .prd/prd-v6.md, .design/solution-design-v6.md D1/D2)
  Detection used to be five hand-rolled regexes plus an intake-list scrape,
  with a flat `{placeholder: value}` mapping — one key PER CATEGORY, so three
  emails in restored as three copies of the last one (backlog item 1,
  2026-07-28 audit). That implementation is gone. This module now DELEGATES
  to `scripts/pii/engine.py`: NER (spaCy) + validated identifier patterns +
  the engagement deny-list recognizer (the PRIMARY client-identity detector —
  see engine.py's module docstring, D3), with Presidio's instance-counter
  operator giving every DISTINCT value its own placeholder.

  The CLI surface and all four public function signatures
  (`anonymize_text`, `anonymize_transcript_file`, `deanonymize_text`,
  `deanonymize_file`) are UNCHANGED — that is what makes rollback a single
  `git revert` (D1, PRD §10). Only what happens inside them changed.

  UPDATE (ticket #161, run-global numbering) — `anonymize_text` and
  `anonymize_transcript_file` each gained one ADDITIVE keyword-only
  `entity_mapping=None` param. Default `None` still preserves the exact
  behaviour above; passed a shared dict, a caller can run every transcript
  in an engagement through one growing, collision-free mapping instead of
  N independent ones (see `anonymize_transcript_file`'s docstring — this is
  what `orchestrate.py`'s `step_discovery` now does). Nothing else about
  the four signatures, or the CLI, changed.

  Placeholders are now `<ENTITY_N>` (e.g. `<PERSON_1>`, `<EMAIL_ADDRESS_2>`),
  not `[CLIENT]` / `[PERSON-1]`. `[CLIENT]` was simultaneously a PII
  placeholder AND a filename/prose template token
  (`[CLIENT]_Business_Case_Questionnaire.xlsx` in five components,
  `"[Client]'s path from X to Y"` in narrative-assembler) — angle brackets
  end that collision (D2). Mappings written by this module are now the v2
  nested-by-entity-type shape; legacy v1 flat mappings and `[X-REDACTED]`
  placeholders still restore, forever (see `_flatten_mapping` below).

THE INTERPRETER SPLIT (read this before "simplifying" the imports)
  Presidio needs Python 3.10-3.13 and lives in `.venv`
  (`scripts/setup_pii.sh`); the system interpreter is 3.9.6 here.

  - ANONYMIZATION (`anonymize_text`, `anonymize_transcript_file`) needs the
    engine, so it imports `scripts/pii/engine.py` LAZILY, on first call, and
    turns a failed import into a clear, plain-language error naming
    `bash scripts/setup_pii.sh` instead of a raw `ModuleNotFoundError`
    traceback (see `_load_engine` / `PIIEngineUnavailable`).

  - DE-ANONYMIZATION (`deanonymize_text`, `deanonymize_file`) stays PURE
    STDLIB and must NEVER import `scripts/pii/engine.py` — directly or
    transitively — because `engine.py` does `import presidio_analyzer` at
    MODULE level, so merely importing it would break exactly the callers
    this has to keep working on 3.9:
      - `scripts/artifact_boundary.py` (`deanonymize_dir`) — imports
        `deanonymize_text` lazily, inside a function, inside a try, and must
        stay importable/runnable on plain 3.9 so a consultant can restore a
        deliverable without the Presidio venv.
      - the guard's own deny message below (`_deny_message`-equivalent in
        `.claude/hooks/anonymize-guard.py`), which runs under the system
        interpreter.
    The restore logic (`_flatten_mapping`) is therefore a SELF-CONTAINED
    stdlib copy of `scripts/pii/engine.py`'s `flatten_mapping` /
    `deanonymize_text` — same algorithm, independently maintained, the same
    duplication pattern this repo already uses for
    `scripts/pii/denylist.py` vs `.claude/hooks/mcp-query-guard.py` (see
    `scripts/pii/drift_check.py`'s header for why: a hook/module that must
    keep working when its sibling can't import cannot import that sibling).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Make `scripts/` importable as the package root for `pii` regardless of how
# this file itself was reached (run as a script, or imported after some
# caller did `sys.path.insert(0, 'scripts')` per the discovery-transcript-
# interpreter agent's snippet).
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


class PIIEngineUnavailable(RuntimeError):
    """Raised when scripts/pii/engine.py (Presidio) cannot be imported under
    the current interpreter — e.g. the system Python (3.9.6 here), which
    Presidio does not support (needs 3.10-3.13). Never let the raw
    ModuleNotFoundError reach a consultant; this carries the fix."""


_ENGINE_UNAVAILABLE_MSG = (
    "PII anonymization engine (Presidio) is not available on this Python "
    "interpreter ({version}). Presidio requires Python 3.10-3.13.\n"
    "Fix: run  bash scripts/setup_pii.sh\n"
    "  (creates a virtual environment at .venv with everything anonymization "
    "needs), then re-run this command through that interpreter — "
    "`.venv/bin/python`, or via `.claude/hooks/_resolve_python.sh`."
)


def _load_engine():
    """Lazily import scripts/pii/engine.py. ONLY called from the
    anonymization path (never from deanonymize_text/deanonymize_file — see
    the module docstring's INTERPRETER SPLIT)."""
    try:
        from pii import engine as _engine  # noqa: PLC0415 - intentionally lazy
    except ImportError as exc:
        raise PIIEngineUnavailable(
            _ENGINE_UNAVAILABLE_MSG.format(version=sys.version.split()[0])
        ) from None
    return _engine


# --- de-anonymization: pure stdlib, no engine import, ever ------------------
#
# Self-contained copy of scripts/pii/engine.py's flatten_mapping /
# deanonymize_text. See module docstring for why this can't just import
# engine.py. Keep these two in sync with engine.py's copies by hand — there
# is no drift_check for this pair yet (unlike denylist.py's), so a change to
# one should be mirrored in the other.

def _flatten_mapping(mapping) -> dict:
    """Normalise ANY accepted mapping shape to {placeholder: original_value}.

    Accepted, forever:
      v2 nested  {"version": 2, "entities": {"PERSON": {"Priya Nair": "<PERSON_1>"}}}
      v2 bare    {"PERSON": {"Priya Nair": "<PERSON_1>"}}   (a raw entity_mapping)
      v1 legacy  {"[CLIENT]": "Zzz Holdings", "[EMAIL-REDACTED]": "a@b.com"}

    v1 is the pre-Presidio flat form and is inverted relative to v2 (it is
    placeholder -> value, where v2 is value -> placeholder). Distinguishing
    them structurally (rather than by a version field) is what lets a
    six-month-old engagement mapping still restore: legacy mappings were
    written with no version key at all.
    """
    if not mapping:
        return {}

    flat: dict = {}

    entities = None
    if isinstance(mapping, dict) and isinstance(mapping.get("entities"), dict):
        entities = mapping["entities"]
    elif isinstance(mapping, dict) and all(
        isinstance(v, dict) for k, v in mapping.items() if k != "version"
    ):
        entities = {k: v for k, v in mapping.items() if k != "version"}

    if entities is not None:
        for _etype, values in entities.items():
            if not isinstance(values, dict):
                continue
            for original, placeholder in values.items():
                # v2 stores value -> placeholder; invert for replacement.
                flat[str(placeholder)] = str(original)
        return flat

    # v1 legacy: already placeholder -> value.
    for placeholder, original in mapping.items():
        if placeholder == "version":
            continue
        if isinstance(original, (str, int, float)):
            flat[str(placeholder)] = str(original)
    return flat


def deanonymize_text(text: str, mapping: dict) -> str:
    """Restore original names/PII from anonymized text using the mapping.

    Accepts both the v2 nested-by-entity-type shape this module now writes
    and legacy v1 flat `{placeholder: value}` mappings, indefinitely — a
    consultant with a six-month-old engagement must still be able to produce
    a client-ready deliverable. Longest placeholder first so a placeholder
    that is a textual prefix of another cannot partially consume it
    (`[CLIENT]` is a prefix of `[CLIENT-ABBR]`; `<ENTITY_N>`'s trailing `>`
    already makes v2 placeholders unambiguous, but legacy ones are not).

    Pure stdlib — see module docstring. Must not import scripts/pii/engine.
    """
    if not text or not mapping:
        return text
    flat = _flatten_mapping(mapping)
    result = text
    for placeholder in sorted(flat.keys(), key=len, reverse=True):
        result = result.replace(placeholder, flat[placeholder])
    return result


def deanonymize_file(file_path: Path, mapping_path: Path) -> str:
    """De-anonymize a file using a mapping file. Returns de-anonymized text.

    Pure stdlib — see module docstring. Must not import scripts/pii/engine.
    """
    mapping = json.loads(mapping_path.read_text())
    text = file_path.read_text()
    return deanonymize_text(text, mapping)


# --- anonymization: lazily pulls in the Presidio engine ---------------------

def anonymize_text(
    text: str,
    entity_names: list,
    client_label: str = "[CLIENT]",
    *,
    entity_mapping: Optional[dict] = None,
) -> tuple:
    """Anonymize PII in `text` using scripts/pii/engine.py (Presidio).

    Signature preserved exactly for backward compatibility (ticket #160),
    plus one ADDITIVE keyword-only param (ticket #161, run-global numbering
    fix — see `anonymize_transcript_file` below for the full rationale).
    `entity_names` is used as the deny-list (client/stakeholder terms) —
    the PRIMARY client-identity detector (D3); Presidio's NER and validated
    patterns run alongside it for people, emails, phones, IDs, etc.

    `client_label` is accepted but UNUSED: placeholders are now Presidio's
    `<ENTITY_N>` form, which cannot collide with `[CLIENT]`-style filename
    or prose templates the way the old convention did (D2). Kept only so
    existing call sites that pass it positionally or by keyword don't break.

    `entity_mapping`: optional shared `{entity_type: {value: placeholder}}`
    dict. Default `None` preserves today's behaviour exactly — a fresh
    mapping starting numbering at 1. When supplied, this call CONTINUES
    numbering from its current state and mutates it in place (Presidio's
    instance-counter operator, see `pii/engine.py`), so passing the same
    dict across repeated calls gives every distinct value one placeholder,
    reused, for the whole run — not one flat key per category, and not one
    restarted counter per call. Sequential use only: the shared dict is
    mutated with no locking (engine.py's thread-safety note).

    Returns (anonymized_text, mapping) where `mapping` is the v2
    nested-by-entity-type shape (`{"version": 2, "entities": {...}}`) —
    also accepted directly by `deanonymize_text`. When `entity_mapping` is
    supplied, `mapping` reflects the full accumulated state, not just this
    call's own contributions.
    """
    del client_label  # unused; see docstring
    engine = _load_engine()
    session = engine.PIISession(entity_names, entity_mapping=entity_mapping)
    anonymized = session.anonymize(text)
    return anonymized, session.mapping_file_dict()


def anonymize_transcript_file(
    transcript_path: Path,
    engagement_dir: Path,
    output_dir: Optional[Path] = None,
    *,
    entity_mapping: Optional[dict] = None,
) -> tuple:
    """Anonymize a transcript file, writing the anonymized copy and its
    mapping file alongside it (or under `output_dir`).

    Signature preserved exactly (ticket #160), plus one ADDITIVE
    keyword-only param (ticket #161). The deny-list is resolved
    from the engagement's own documents — `inputs/engagement_intake.md`,
    `ENGAGEMENT_CONTEXT.md`, `CLIENT_PROFILE.md`, and the engagement/client
    directory name (see `scripts/pii/denylist.resolve_engagement_deny_list`)
    — which is broader than the old intake-only scrape and is what makes the
    empty-deny-list warning (engine.py's `EMPTY_DENY_LIST_WARNING`) fire
    correctly when none of those documents name the client.

    `entity_mapping`: optional shared `{entity_type: {value: placeholder}}`
    dict, mutated in place — see `anonymize_text` above. This is what lets
    `orchestrate.py`'s `step_discovery` run every transcript in an
    engagement through ONE growing mapping instead of N independent ones:
    each transcript anonymized standalone restarts Presidio's instance
    counter at 1, so the same email in transcript A and transcript B would
    otherwise get the SAME placeholder (`<EMAIL_ADDRESS_1>`) bound to TWO
    DIFFERENT values — a collision, not a fix, if a later merge just
    concatenated the per-transcript mappings. Passing one shared dict
    through the whole transcript loop keeps numbering continuous and
    reuses a placeholder for a value already seen, so the merged mapping
    is both complete and collision-free. Default `None` preserves today's
    standalone behaviour exactly (numbering restarts at 1, own dict).
    Sequential use only — see `anonymize_text`'s docstring.

    Returns (anonymized_transcript_path, mapping_path). The mapping file is
    written in the v2 nested-by-entity-type shape and chmod'd 0600 — it
    contains real client PII (solution-design-v6.md §9). When
    `entity_mapping` is supplied, the written file reflects the full
    accumulated state at the time of this call (all transcripts processed
    so far through the shared dict, this one included), not just this
    transcript's own entities.
    """
    engine = _load_engine()
    transcript_path = Path(transcript_path)
    engagement_dir = Path(engagement_dir)

    session = engine.PIISession.for_engagement(engagement_dir, entity_mapping=entity_mapping)

    original_text = transcript_path.read_text()
    anonymized_text = session.anonymize(original_text)

    if output_dir is None:
        output_dir = transcript_path.parent
    output_dir = Path(output_dir)

    anon_path = output_dir / f".anon_{transcript_path.name}"
    mapping_path = output_dir / f".anon_mapping_{transcript_path.stem}.json"

    anon_path.write_text(anonymized_text)

    mapping_path.write_text(json.dumps(session.mapping_file_dict(), indent=2))
    mapping_path.chmod(0o600)  # contains real PII — see solution-design-v6.md §9

    return anon_path, mapping_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Anonymize transcript PII')
    parser.add_argument('--file', required=True, help='Path to transcript file')
    parser.add_argument('--engagement-dir', required=True, help='Path to engagement directory')
    parser.add_argument('--deanonymize', action='store_true', help='De-anonymize a file instead')
    parser.add_argument('--mapping', help='Path to mapping file (for --deanonymize)')
    args = parser.parse_args()

    if args.deanonymize:
        if not args.mapping:
            print('Error: --mapping required for --deanonymize', file=sys.stderr)
            sys.exit(1)
        result = deanonymize_file(Path(args.file), Path(args.mapping))
        print(result)
    else:
        try:
            anon_path, mapping_path = anonymize_transcript_file(
                Path(args.file), Path(args.engagement_dir)
            )
        except PIIEngineUnavailable as exc:
            print(f'Error: {exc}', file=sys.stderr)
            sys.exit(1)
        print(f'Anonymized: {anon_path}')
        print(f'Mapping: {mapping_path}')
