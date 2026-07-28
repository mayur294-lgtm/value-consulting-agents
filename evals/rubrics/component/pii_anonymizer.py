"""pii-anonymizer component evaluator — deterministic code checks only (#127).

This is the PII round-trip parity gate for `scripts/anonymize_transcript.py` +
`scripts/artifact_boundary.py::deanonymize_dir`. It is pipeline CODE, not an
agent, so there is no "specifics._xxx" text-shape check here — every check
actually RUNS the real anonymize/deanonymize functions against a committed
synthetic transcript (`evals/goldens/pii_roundtrip_fixture.md`) inside a
`tempfile.TemporaryDirectory()` and inspects the result. No filesystem writes
ever touch the repo; the committed fixture is only ever read, never mutated.

Threshold is 1.00 (see registry.yaml comment): every check below witnesses a
distinct shipped-PII failure mode, so a soft pass would mean a real PII leak
or a broken round-trip shipped clean.

run_experiment.py resolves this module as `rubrics.component.pii_anonymizer`
(dash -> underscore) and calls `evaluate(target)` with target = the registry
`input:` path (the fixture above).
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

from rubrics.base import CheckResult, repo_root

_ROOT = repo_root()
_SCRIPTS_DIR = _ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from anonymize_transcript import (  # noqa: E402
    anonymize_text,
    anonymize_transcript_file,
    deanonymize_text,
    _EMAIL_RE,
    _PHONE_RE,
    _SSN_RE,
    _ACCOUNT_RE,
    _URL_RE,
)
import artifact_boundary  # noqa: E402


def _bool_check(name: str, ok: bool, *, detail: str = "") -> CheckResult:
    # threshold is 1.00, so every check is hard_fail=True regardless (any miss
    # sinks the mean below 1.00 anyway) — hard_fail makes the failure mode
    # explicit in the report rather than relying on the mean.
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=True, detail=detail)


CLIENT_NAME = "Zenith Bank"
CLIENT_SHORT = "Zenith"
STAKEHOLDERS = ["Maria Chen", "David Cole", "Priya Rao"]
_REPEATED_EMAIL = "jt.moreno@meridianadvisors.example.com"
_SHARED_PHONE_TEXT = "(212) 555-0148"   # matches the fixture's first phone number verbatim


def _build_engagement(tmp_dir: Path, fixture_text: str) -> Path:
    """Synthesize a minimal engagement dir the way the real pipeline lays one
    out: inputs/engagement_intake.md (parsed by `_load_entity_names` for the
    Client: line and Name: lines) + inputs/transcript_1.md (a copy of the
    fixture). Never written inside the repo — always under tmp_dir."""
    engagement_dir = tmp_dir / "engagement"
    inputs_dir = engagement_dir / "inputs"
    inputs_dir.mkdir(parents=True)
    intake = (
        "# Engagement Intake\n\n"
        f"Client: {CLIENT_NAME}\n\n"
        "## Stakeholders\n\n"
        + "".join(f"Name: {n}\nRole: Stakeholder\n\n" for n in STAKEHOLDERS)
    )
    (inputs_dir / "engagement_intake.md").write_text(intake)
    (inputs_dir / "transcript_1.md").write_text(fixture_text)
    return engagement_dir


def _anonymize_fixture(fixture_text: str):
    """Runs the real anonymize_transcript_file() against a synthesized
    engagement dir under a TemporaryDirectory. Returns (anon_text, mapping,
    mapping_file_mode) — all pure Python values, safe to use after the
    TemporaryDirectory is cleaned up."""
    with tempfile.TemporaryDirectory() as td:
        engagement_dir = _build_engagement(Path(td), fixture_text)
        transcript_path = engagement_dir / "inputs" / "transcript_1.md"
        anon_path, mapping_path = anonymize_transcript_file(transcript_path, engagement_dir)
        anon_text = anon_path.read_text()
        mapping = json.loads(mapping_path.read_text())
        mode = mapping_path.stat().st_mode & 0o777
    return anon_text, mapping, mode


# ---------------------------------------------------------------------------
# 1. round_trip_byte_identical
# ---------------------------------------------------------------------------
def _check_round_trip(fixture_text: str) -> CheckResult:
    anon_text, mapping, _mode = _anonymize_fixture(fixture_text)
    restored = deanonymize_text(anon_text, mapping)
    ok = restored == fixture_text
    detail = ("round-trip restored the fixture byte-identical" if ok else
              f"round-trip MISMATCH: restored {len(restored)} chars vs original {len(fixture_text)} chars")
    return _bool_check("round_trip_byte_identical", ok, detail=detail)


# ---------------------------------------------------------------------------
# 2. distinct_values_distinct_placeholders
# ---------------------------------------------------------------------------
def _check_distinct_mapping(fixture_text: str) -> CheckResult:
    _anon_text, mapping, _mode = _anonymize_fixture(fixture_text)
    reverse: dict = {}
    dup_values = []
    for k, v in mapping.items():
        if v in reverse and reverse[v] != k:
            dup_values.append((k, v, reverse[v]))
        else:
            reverse[v] = k
    # A plain dict can't structurally hold two values under one key; this
    # loop documents/protects the invariant rather than finding it live.
    dup_keys = [k for k in mapping if list(mapping.keys()).count(k) > 1]
    email_keys = [k for k in mapping if re.match(r"^\[EMAIL-\d+\]$", k)]
    ok = not dup_values and not dup_keys and len(email_keys) >= 3
    detail = (f"{len(mapping)} mapping entries, {len(email_keys)} distinct [EMAIL-N] keys, "
              f"duplicate values={dup_values}, duplicate keys={dup_keys}")
    return _bool_check("distinct_values_distinct_placeholders", ok, detail=detail)


# ---------------------------------------------------------------------------
# 3. repeated_value_reuses_placeholder
# ---------------------------------------------------------------------------
def _check_repeated_value(fixture_text: str) -> CheckResult:
    anon_text, mapping, _mode = _anonymize_fixture(fixture_text)
    placeholders = [k for k, v in mapping.items() if v == _REPEATED_EMAIL]
    single_placeholder = len(placeholders) == 1
    occurrences = anon_text.count(placeholders[0]) if placeholders else 0
    ok = single_placeholder and occurrences >= 2
    detail = (f"placeholder(s) mapped to the repeated email: {placeholders}, "
              f"occurrences of that placeholder in anon text: {occurrences}")
    return _bool_check("repeated_value_reuses_placeholder", ok, detail=detail)


# ---------------------------------------------------------------------------
# 4. no_raw_pii_in_anonymized_output
# ---------------------------------------------------------------------------
def _known_pii_literals(fixture_text: str) -> set:
    """Derive the exact literals the real regexes would find in the fixture —
    not hand-typed copies — so this check can never drift from actual code
    behavior (e.g. the phone regex's leading-paren quirk, the URL regex
    swallowing a trailing period)."""
    literals = set()
    literals.update(m.group(0) for m in _EMAIL_RE.finditer(fixture_text))
    literals.update(m.group(0) for m in _PHONE_RE.finditer(fixture_text))
    literals.update(m.group(0) for m in _SSN_RE.finditer(fixture_text))
    literals.update(m.group(0) for m in _ACCOUNT_RE.finditer(fixture_text))
    literals.update(m.group(0) for m in _URL_RE.finditer(fixture_text)
                     if "zenithbank" in m.group(0).lower())
    literals.add(CLIENT_NAME)
    literals.update(STAKEHOLDERS)
    return literals


def _check_no_raw_pii(fixture_text: str) -> CheckResult:
    anon_text, _mapping, _mode = _anonymize_fixture(fixture_text)
    leaked = sorted(lit for lit in _known_pii_literals(fixture_text) if lit in anon_text)
    bare_zenith_leak = bool(re.search(r"\bZenith\b", anon_text))
    ok = not leaked and not bare_zenith_leak
    detail = f"leaked literal(s): {leaked}; bare 'Zenith' present outside placeholders: {bare_zenith_leak}"
    return _bool_check("no_raw_pii_in_anonymized_output", ok, detail=detail)


# ---------------------------------------------------------------------------
# 5. cross_transcript_merge_collision_free
# ---------------------------------------------------------------------------
_SECOND_TRANSCRIPT = (
    "# Follow-up Call — Zenith Bank\n\n"
    f"Alex Rivera: Quick follow-up — you can still reach Maria Chen at "
    f"{_REPEATED_EMAIL} or {_SHARED_PHONE_TEXT}.\n\n"
    "Alex Rivera: For anything new on this thread, use "
    "newcontact@partnerhub.example.io instead.\n"
)


def _check_cross_transcript_merge(fixture_text: str) -> CheckResult:
    with tempfile.TemporaryDirectory() as td:
        engagement_dir = _build_engagement(Path(td), fixture_text)
        transcript1_path = engagement_dir / "inputs" / "transcript_1.md"
        anon_path1, mapping_path1 = anonymize_transcript_file(transcript1_path, engagement_dir)
        mapping1 = json.loads(mapping_path1.read_text())
        anon_text1 = anon_path1.read_text()

        transcript2_path = engagement_dir / "inputs" / "transcript_2.md"
        transcript2_path.write_text(_SECOND_TRANSCRIPT)
        anon_path2, mapping_path2 = anonymize_transcript_file(
            transcript2_path, engagement_dir, shared_mapping=mapping1)
        mapping2 = json.loads(mapping_path2.read_text())
        anon_text2 = anon_path2.read_text()

    email_ph1 = next((k for k, v in mapping1.items() if v == _REPEATED_EMAIL), None)
    email_ph2 = next((k for k, v in mapping2.items() if v == _REPEATED_EMAIL), None)
    # The phone regex drops a leading "(" preceded by whitespace (see check 4's
    # docstring) — derive the expected stored value via the real regex instead
    # of guessing the exact stripped form.
    phone_literal = next((m.group(0) for m in _PHONE_RE.finditer(_SHARED_PHONE_TEXT)), None)
    phone_ph1 = next((k for k, v in mapping1.items() if v == phone_literal), None)
    phone_ph2 = next((k for k, v in mapping2.items() if v == phone_literal), None)

    identical_placeholders = (
        email_ph1 is not None and email_ph1 == email_ph2 and
        phone_ph1 is not None and phone_ph1 == phone_ph2
    )

    merged = dict(mapping1)
    conflicts = []
    for k, v in mapping2.items():
        if k in merged and merged[k] != v:
            conflicts.append((k, merged[k], v))
        merged[k] = v

    restored1 = deanonymize_text(anon_text1, merged)
    restored2 = deanonymize_text(anon_text2, merged)
    round_trip_ok = restored1 == fixture_text and restored2 == _SECOND_TRANSCRIPT

    ok = identical_placeholders and not conflicts and round_trip_ok
    detail = (f"shared email placeholders: {email_ph1} / {email_ph2}; "
              f"shared phone placeholders: {phone_ph1} / {phone_ph2}; "
              f"merge conflicts: {conflicts}; merged round-trip ok: {round_trip_ok}")
    return _bool_check("cross_transcript_merge_collision_free", ok, detail=detail)


# ---------------------------------------------------------------------------
# 6. xlsx_outputs_deanonymized
# ---------------------------------------------------------------------------
def _check_xlsx_outputs(fixture_text: str) -> CheckResult:
    import openpyxl

    _anon_text, mapping, _mode = _anonymize_fixture(fixture_text)
    client_ph = "[CLIENT]"
    email_ph = next((k for k in mapping if re.match(r"^\[EMAIL-\d+\]$", k)), None)
    if client_ph not in mapping or not email_ph:
        return _bool_check("xlsx_outputs_deanonymized", False,
                           detail=f"expected placeholders missing from mapping "
                                  f"([CLIENT] present={client_ph in mapping}, email placeholder={email_ph})")

    with tempfile.TemporaryDirectory() as td:
        engagement_dir = Path(td) / "engagement"
        outputs_dir = engagement_dir / "outputs"
        outputs_dir.mkdir(parents=True)
        mapping_file = engagement_dir / ".pii_mapping.json"
        mapping_file.write_text(json.dumps(mapping))

        wb = openpyxl.Workbook()
        ws = wb.active
        # openpyxl forbids '[' ']' in a sheet title outright — verified
        # empirically (even a raw-crafted xlsx with brackets in the title
        # fails to reopen) — so a bracketed placeholder can never legally
        # live in a sheet title. This uses a valid custom (non-default)
        # title to exercise deanonymize_dir's ws.title code path without
        # corrupting it; the two cells below carry the actual
        # placeholder-restoration assertions.
        ws.title = "Engagement Summary"
        ws["A1"] = f"Client: {client_ph}"
        ws["B2"] = f'="Contact us at " & "{email_ph}"'
        xlsx_path = outputs_dir / "summary.xlsx"
        wb.save(xlsx_path)

        report = artifact_boundary.deanonymize_dir(outputs_dir, mapping_file)

        wb2 = openpyxl.load_workbook(xlsx_path)
        ws2 = wb2.active
        a1 = ws2["A1"].value
        b2 = ws2["B2"].value
        title_preserved = ws2.title == "Engagement Summary"

    a1_ok = a1 == f"Client: {mapping[client_ph]}"
    b2_ok = b2 == f'="Contact us at " & "{mapping[email_ph]}"'
    ok = a1_ok and b2_ok and title_preserved and report.get("client_ready") is True
    detail = (f"A1 restored={a1_ok} ({a1!r}); B2 formula restored={b2_ok} ({b2!r}); "
              f"title preserved={title_preserved}; report.client_ready={report.get('client_ready')}")
    return _bool_check("xlsx_outputs_deanonymized", ok, detail=detail)


# ---------------------------------------------------------------------------
# 7. nested_outputs_deanonymized
# ---------------------------------------------------------------------------
def _check_nested_outputs(fixture_text: str) -> CheckResult:
    _anon_text, mapping, _mode = _anonymize_fixture(fixture_text)
    client_ph = "[CLIENT]"
    if client_ph not in mapping:
        return _bool_check("nested_outputs_deanonymized", False, detail="[CLIENT] not present in mapping")
    placeholder_line = f"Prepared for {client_ph}.\n"

    with tempfile.TemporaryDirectory() as td:
        engagement_dir = Path(td) / "engagement"
        outputs_dir = engagement_dir / "outputs"
        subdir = outputs_dir / "subdir"
        subdir.mkdir(parents=True)
        mapping_file = engagement_dir / ".pii_mapping.json"
        mapping_file.write_text(json.dumps(mapping))

        report_path = subdir / "report.md"
        report_path.write_text(placeholder_line)
        interim_path = outputs_dir / "interim_notes.md"
        interim_path.write_text(placeholder_line)
        scratch_path = outputs_dir / ".anon_scratch.md"
        scratch_path.write_text(placeholder_line)

        artifact_boundary.deanonymize_dir(outputs_dir, mapping_file)

        report_after = report_path.read_text()
        interim_after = interim_path.read_text()
        scratch_after = scratch_path.read_text()

    report_ok = report_after == f"Prepared for {mapping[client_ph]}.\n"
    interim_untouched = interim_after == placeholder_line
    scratch_untouched = scratch_after == placeholder_line
    ok = report_ok and interim_untouched and scratch_untouched
    detail = (f"nested outputs/subdir/report.md restored={report_ok}; "
              f"outputs/interim_notes.md untouched={interim_untouched}; "
              f"outputs/.anon_scratch.md untouched={scratch_untouched}")
    return _bool_check("nested_outputs_deanonymized", ok, detail=detail)


# ---------------------------------------------------------------------------
# 8. mapping_files_chmod_600_and_cleaned
# ---------------------------------------------------------------------------
def _anon_block_calls_unlink() -> bool:
    """Grep orchestrate.py's step_discovery PII-anonymization block for the
    per-transcript mapping cleanup call. Not importable standalone (it's an
    async def deep inside orchestrate.py's pipeline), so this asserts the
    SOURCE contains the cleanup call within the anon-mapping section, located
    by its own comment marker."""
    src = (_ROOT / "scripts" / "orchestrate.py").read_text()
    marker = "# --- PII Anonymization"
    idx = src.find(marker)
    if idx == -1:
        return False
    block = src[idx: idx + 4000]
    return "unlink" in block


def _check_mapping_mode_and_cleanup(fixture_text: str) -> CheckResult:
    _anon_text, _mapping, mode = _anonymize_fixture(fixture_text)
    mode_ok = mode == 0o600
    cleanup_ok = _anon_block_calls_unlink()
    ok = mode_ok and cleanup_ok
    detail = (f"per-transcript mapping file mode={oct(mode)} (expected 0o600): {mode_ok}; "
              f"orchestrate.py step_discovery PII-anonymization block calls unlink() on the "
              f"per-transcript mapping once the combined mapping is saved: {cleanup_ok}")
    return _bool_check("mapping_files_chmod_600_and_cleaned", ok, detail=detail)


# ---------------------------------------------------------------------------
# 9. client_short_single_word_redacted
# ---------------------------------------------------------------------------
def _check_client_short_word(fixture_text: str) -> CheckResult:
    anon_text, mapping, _mode = _anonymize_fixture(fixture_text)
    bare_zenith_present = bool(re.search(r"\bZenith\b", anon_text))
    client_short_ok = mapping.get("[CLIENT-SHORT]") == CLIENT_SHORT
    direction_a_ok = (not bare_zenith_present) and client_short_ok

    stoplist_text = "Welcome to First Bank. First has been serving the community for decades."
    stoplist_anon, stoplist_mapping = anonymize_text(stoplist_text, ["First Bank"])
    bare_first_survives = bool(re.search(r"\bFirst\b", stoplist_anon))
    no_short_placeholder_emitted = "[CLIENT-SHORT]" not in stoplist_mapping
    direction_b_ok = bare_first_survives and no_short_placeholder_emitted

    ok = direction_a_ok and direction_b_ok
    detail = (f"[distinctive client short form] bare 'Zenith' present={bare_zenith_present}, "
              f"[CLIENT-SHORT] mapping={mapping.get('[CLIENT-SHORT]')!r} -> ok={direction_a_ok}; "
              f"[generic stoplisted short form] bare 'First' survives={bare_first_survives}, "
              f"no [CLIENT-SHORT] emitted={no_short_placeholder_emitted} -> ok={direction_b_ok}")
    return _bool_check("client_short_single_word_redacted", ok, detail=detail)


# ---------------------------------------------------------------------------
# 10. legacy_redacted_mapping_still_restores
# ---------------------------------------------------------------------------
def _check_legacy_mapping(_fixture_text: str) -> CheckResult:
    text = "Contact [EMAIL-REDACTED] at [CLIENT]"
    mapping = {"[EMAIL-REDACTED]": "old@example.com", "[CLIENT]": "Zenith Bank"}
    restored = deanonymize_text(text, mapping)
    expected = "Contact old@example.com at Zenith Bank"
    ok = restored == expected
    detail = f"restored={restored!r} (expected {expected!r})"
    return _bool_check("legacy_redacted_mapping_still_restores", ok, detail=detail)


CHECKS = {
    "round_trip_byte_identical": _check_round_trip,
    "distinct_values_distinct_placeholders": _check_distinct_mapping,
    "repeated_value_reuses_placeholder": _check_repeated_value,
    "no_raw_pii_in_anonymized_output": _check_no_raw_pii,
    "cross_transcript_merge_collision_free": _check_cross_transcript_merge,
    "xlsx_outputs_deanonymized": _check_xlsx_outputs,
    "nested_outputs_deanonymized": _check_nested_outputs,
    "mapping_files_chmod_600_and_cleaned": _check_mapping_mode_and_cleanup,
    "client_short_single_word_redacted": _check_client_short_word,
    "legacy_redacted_mapping_still_restores": _check_legacy_mapping,
}


def evaluate(target: str) -> list[CheckResult]:
    p = Path(target)
    if not p.exists():
        return [CheckResult(name, 0.0, False, hard_fail=True, detail=f"fixture not found: {target}")
                for name in CHECKS]
    fixture_text = p.read_text()
    results = []
    for name, fn in CHECKS.items():
        try:
            results.append(fn(fixture_text))
        except Exception as e:  # a check crash is a clean check failure, not a harness crash
            results.append(CheckResult(name, 0.0, False, hard_fail=True,
                                       detail=f"check raised {type(e).__name__}: {e}"))
    return results
