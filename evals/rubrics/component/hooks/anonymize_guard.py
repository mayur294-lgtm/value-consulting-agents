"""`anonymize-guard` component evaluator — the PreToolUse(Read|Bash) PII gate.

SUBJECT: `.claude/hooks/anonymize-guard.py`, the hook that stops a raw client
file under `engagements/*/inputs/` from being opened before it has been run
through the anonymizer.

WHY THIS ROW EXISTS SEPARATELY FROM `pii-anonymizer`
----------------------------------------------------
`pii-anonymizer` carries exactly ONE check over this hook
(`guard_fails_closed_on_inputs_path`, #164) — the fail-closed/fail-open split.
Everything else the hook actually decides was ungated: per-format sibling
naming, mtime staleness, the unsupported-format refusal, the `.anon_` passthrough,
the Bash path extraction, and the anonymizer's own carve-out. This row covers
those; the pii row's single check stays where it is (it is that row's #164
acceptance criterion) and is deliberately not deleted from there.

WHAT THE HOOK IS, AND IS NOT (solution-design-v6 D13 — read before "fixing" a
check that looks like it should be about PII detection)
-----------------------------------------------------------------------------
This hook DOES NOT DETECT PII. It was deliberately kept OFF `scripts/pii/
engine.py`: it fires synchronously on every Read and every Bash call, Presidio's
cold start is ~0.7-1.1s against this hook's ~0.04s budget, and a module-level
import failure in a PreToolUse hook fails OPEN — exactly backwards for a guard.
It answers a purely structural question from PATHS AND TIMESTAMPS:

    has this raw file under engagements/*/inputs/ already been scrubbed, and is
    that scrubbed copy still current?

So every check below is about path scope, sibling naming, mtime, and the
process contract. None of them reads file CONTENT, because the hook does not.

THE SPLIT IS THE POINT
----------------------
`fails_closed_under_injected_fault` asserts BOTH halves of the ticket's
acceptance criterion in ONE injection block: the identical, real, unmocked
`PermissionError` must DENY inside `engagements/*/inputs/` and ALLOW outside
it. Asserting only the deny half would be satisfied by a globally fail-closed
guard — which wedged every session once already (PR #82); asserting only the
allow half would be satisfied by a guard that never denies anything.

`degenerate_path_fails_closed_only_inside_inputs` is the SECOND, non-redundant
split. `_evaluate` returns `None` for an out-of-scope path before it touches
the filesystem, so a chmod fault outside inputs/ never actually raises — the
allow there comes from SCOPE, and the hook's fail-OPEN default (the `except`
clause's `_raw_looks_like_inputs` guess) is never exercised by it. That second
check injects a fault that DOES raise on both sides and proves the guess splits
the same way. Their mutations push in opposite directions (allow-everywhere vs
deny-everywhere), so neither can be proven by the other's.

Fixtures are synthesized in a tempdir and reached via `CLAUDE_PROJECT_DIR`;
nothing here touches `engagements/` in the real checkout. threshold 1.00 — a
privacy control is pass/fail, not "mostly correct". No `judge:` entries: every
check is deterministic, offline and $0.
"""
from __future__ import annotations

from pathlib import Path

from rubrics.base import CheckResult, repo_root
from rubrics._harness import (
    HookRun,
    build_fixture_engagement,
    check_runs_under_registered_interpreter,
    fault_injection_skip,
    inject_fault,
    run_hook_subprocess,
)
from rubrics.component.hooks._common import (
    HOOK_TIMEOUT_S,
    bash_payload,
    pretooluse_payload,
    bool_check,
    check_invoked_as_subprocess_not_import,
    missing_hook_check,
    read_payload,
    run_in_tmp,
    set_mtime,
)

HOOK_REL_PATH = Path(".claude") / "hooks" / "anonymize-guard.py"
TMP_PREFIX = "anonymize_guard_row_"

# Obviously-placeholder client identity — never a fictional bank name (the
# repo's synthetic-quarantine programme treats those as contamination).
SLUG = "zzzplaceholderclient"
ENGAGEMENT = "2026-01_test_engagement"

RAW_TEXT = "placeholder transcript body, straight from the client\n"
SCRUBBED_TEXT = "placeholder transcript body, <PERSON_1> redacted\n"


def _hook_path() -> Path:
    """Resolved through `repo_root()`, never a captured cwd or an absolute
    literal — that is what lets the mutation harness point this row at its
    SHADOW copy of the hook (see evals/mutations.py, "What this harness CAN
    mutate", item 2). A rubric that resolves its subject any other way reads
    the real file and reports UNREACHABLE."""
    return repo_root() / HOOK_REL_PATH


def _run_hook(project_dir: Path, stdin_bytes: bytes) -> HookRun:
    """This row's ONE subprocess entry point. Every check goes through it —
    including `runs_under_registered_interpreter` and
    `invoked_as_subprocess_not_import`, so both observe the argv this row
    REALLY spawns rather than a re-implementation written for them."""
    return run_hook_subprocess(_hook_path(), stdin_bytes,
                               project_dir=project_dir, timeout=HOOK_TIMEOUT_S)


def _engagement(root: Path, **kwargs):
    return build_fixture_engagement(root, slug=SLUG, engagement=ENGAGEMENT, **kwargs)


# --- format / sibling contract ----------------------------------------------

def _denies_unscrubbed_text_input(root: Path) -> CheckResult:
    """A plain-text file under inputs/ with no `.anon_` sibling must be DENIED,
    and the refusal must name the TEXT convention (`.anon_<name>` verbatim) and
    the plain-text scrub command — not the document one. Getting the format
    wrong here sends the consultant to a tool that cannot process the file."""
    name = "denies_unscrubbed_text_input"
    fixture = _engagement(root, documents={"inputs/notes.md": RAW_TEXT})
    raw = fixture.inputs_dir / "notes.md"
    result = _run_hook(root, read_payload(str(raw)))
    ok = (
        result.returncode == 0
        and result.denied
        and ".anon_notes.md" in result.reason
        and "anonymize_transcript.py" in result.reason
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:220]!r}"))


def _allows_scrubbed_anon_artifact(root: Path) -> CheckResult:
    """A file whose NAME already starts with `.anon_` is allowed outright — the
    hook never opens it to check which placeholder convention is inside
    (today's `<ENTITY_N>` or a legacy `[CLIENT]`/`[PERSON-N]` form). An
    `.anon_` file is, by construction, never the raw client document. Without
    this passthrough the consultant cannot open the scrubbed copy the hook
    itself just told them to open."""
    name = "allows_scrubbed_anon_artifact"
    fixture = _engagement(root, documents={"inputs/.anon_notes.md": SCRUBBED_TEXT})
    scrubbed = fixture.inputs_dir / ".anon_notes.md"
    result = _run_hook(root, read_payload(str(scrubbed)))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} stdout={result.stdout_text[:160]!r}"))


def _allows_when_sibling_is_current(root: Path) -> CheckResult:
    """Raw file + an `.anon_` sibling that is NOT older than it -> allow. The
    positive half of the staleness rule; `denies_stale_sibling_by_mtime` is the
    negative half and the two mutate the same comparison in opposite
    directions, so neither can pass by the other's logic."""
    name = "allows_when_sibling_is_current"
    fixture = _engagement(root, documents={
        "inputs/notes.md": RAW_TEXT,
        "inputs/.anon_notes.md": SCRUBBED_TEXT,
    })
    raw = fixture.inputs_dir / "notes.md"
    sibling = fixture.inputs_dir / ".anon_notes.md"
    set_mtime(raw, seconds_ago=600)
    set_mtime(sibling, seconds_ago=60)          # scrubbed AFTER the raw file
    result = _run_hook(root, read_payload(str(raw)))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"raw mtime 600s ago, sibling 60s ago -> rc={result.returncode} "
        f"denied={result.denied} stdout={result.stdout_text[:160]!r}"))


def _denies_stale_sibling_by_mtime(root: Path) -> CheckResult:
    """The raw file changed AFTER it was scrubbed, so the `.anon_` sibling no
    longer reflects it. Treated exactly like a missing sibling — denied — never
    silently trusted: a stale scrub is worse than no scrub because it looks
    safe (v6 D13, "SIBLING STALENESS")."""
    name = "denies_stale_sibling_by_mtime"
    fixture = _engagement(root, documents={
        "inputs/notes.md": RAW_TEXT,
        "inputs/.anon_notes.md": SCRUBBED_TEXT,
    })
    raw = fixture.inputs_dir / "notes.md"
    sibling = fixture.inputs_dir / ".anon_notes.md"
    set_mtime(sibling, seconds_ago=600)
    set_mtime(raw, seconds_ago=60)              # raw edited AFTER the scrub
    result = _run_hook(root, read_payload(str(raw)))
    ok = (
        result.returncode == 0
        and result.denied
        and "out of date" in result.reason.lower()
    )
    return bool_check(name, ok, detail=(
        f"sibling mtime 600s ago, raw 60s ago -> rc={result.returncode} "
        f"denied={result.denied} reason={result.reason[:200]!r}"))


def _denies_document_without_md_sidecar(root: Path) -> CheckResult:
    """Per-format sibling naming, the half a single text fixture cannot reach.
    A `.pdf` is scrubbed by `scripts/pii/ingest.py`, whose output is the
    `.anon_<name>.md` TEXT SIDECAR — the source extension is kept so
    `Pricing.pdf` and `Pricing.xlsx` in one folder cannot collide.

    The fixture deliberately plants the WRONG, text-convention sibling
    (`.anon_report.pdf`) and makes it NEWER than the source: if the hook ever
    collapsed both conventions to the bare form, that file would satisfy it and
    an unconverted PDF would sail through. It must still be denied, and told to
    produce `.anon_report.pdf.md`."""
    name = "denies_document_without_md_sidecar"
    fixture = _engagement(root, documents={
        "inputs/report.pdf": "%PDF-1.4 placeholder\n",
        "inputs/.anon_report.pdf": "decoy: text-convention sibling for a DOCUMENT\n",
    })
    raw = fixture.inputs_dir / "report.pdf"
    decoy = fixture.inputs_dir / ".anon_report.pdf"
    set_mtime(raw, seconds_ago=600)
    set_mtime(decoy, seconds_ago=60)
    result = _run_hook(root, read_payload(str(raw)))
    ok = (
        result.returncode == 0
        and result.denied
        and ".anon_report.pdf.md" in result.reason
        and "scripts.pii.ingest" in result.reason
    )
    return bool_check(name, ok, detail=(
        f"decoy .anon_report.pdf present and newer -> rc={result.returncode} "
        f"denied={result.denied} reason={result.reason[:220]!r}"))


def _denies_unsupported_format_outright(root: Path) -> CheckResult:
    """A format with no extractor (`.key`, `.ppt`, no extension) is blocked
    outright and told to export to a supported format — never silently allowed
    through unrecognised. This is the "stricter than content-sniffing" property
    of the #164 rewrite: nothing under inputs/ passes without a scrubbed
    sibling to point at, regardless of what it contains."""
    name = "denies_unsupported_format_outright"
    fixture = _engagement(root, documents={"inputs/deck.key": "placeholder keynote\n"})
    raw = fixture.inputs_dir / "deck.key"
    result = _run_hook(root, read_payload(str(raw)))
    ok = (
        result.returncode == 0
        and result.denied
        and "isn't supported yet" in result.reason
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:200]!r}"))


def _allows_paths_outside_inputs_scope(root: Path) -> CheckResult:
    """Scope is `engagements/**/inputs/**` and NOTHING else. A deliverable under
    the SAME engagement's `outputs/` — unscrubbed, no sibling, identical
    extension — must be allowed unconditionally. Widening this scope by one
    segment is how a guard starts denying the consultant's own deliverables."""
    name = "allows_paths_outside_inputs_scope"
    fixture = _engagement(root, subdirs=("outputs",),
                          documents={"outputs/draft.md": RAW_TEXT})
    assert fixture.engagement_dir is not None
    outside = fixture.engagement_dir / "outputs" / "draft.md"
    result = _run_hook(root, read_payload(str(outside)))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"{outside.name} under outputs/ -> rc={result.returncode} "
        f"denied={result.denied} stdout={result.stdout_text[:160]!r}"))


def _gates_bash_command_reading_raw_input(root: Path) -> CheckResult:
    """A Read is not the only way to open a file. `cat`/`head` of a raw input
    through Bash must be gated identically, or the guard is a speed bump. The
    hook pulls path-like tokens out of the command string for exactly this."""
    name = "gates_bash_command_reading_raw_input"
    fixture = _engagement(root, documents={"inputs/notes.md": RAW_TEXT})
    raw = fixture.inputs_dir / "notes.md"
    result = _run_hook(root, bash_payload(f"head -n 40 {raw}"))
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:200]!r}"))


def _allows_bash_anonymizer_command_itself(root: Path) -> CheckResult:
    """The carve-out that keeps the guard from deadlocking: the scrub command
    NAMES the raw file, so without this the one command the deny message tells
    the consultant to run would itself be blocked."""
    name = "allows_bash_anonymizer_command_itself"
    fixture = _engagement(root, documents={"inputs/notes.md": RAW_TEXT})
    raw = fixture.inputs_dir / "notes.md"
    assert fixture.engagement_dir is not None
    command = (f'.claude/hooks/_resolve_python.sh scripts/anonymize_transcript.py '
               f'--file "{raw}" --engagement-dir {fixture.engagement_dir}')
    result = _run_hook(root, bash_payload(command))
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} stdout={result.stdout_text[:160]!r}"))


# --- the fail-closed / fail-open SPLIT ---------------------------------------

def _fault_split(root: Path):
    """Build the two-sided fault fixture both halves of the split use.

    BOTH files exist and are genuinely unscrubbed (no `.anon_` sibling), so
    absent the fault both would be denied for the ORDINARY reason. That makes
    the injected `PermissionError` the only variable between them, and the only
    difference between the two paths their SCOPE.
    """
    fixture = _engagement(root, documents={"inputs/fault_test.md": RAW_TEXT})
    assert fixture.inputs_dir is not None
    outside_dir = root / "scratch_outside"
    outside_dir.mkdir(parents=True, exist_ok=True)
    (outside_dir / "fault_test.md").write_text(RAW_TEXT, encoding="utf-8")
    return fixture.inputs_dir, outside_dir


def _fails_closed_under_injected_fault(root: Path) -> CheckResult:
    """THE fail-closed half. `chmod 000` on `inputs/` makes every
    `exists()`/`stat()` the hook performs raise a real, unmocked
    `PermissionError` — not a simulated fault. Any unexpected failure while
    evaluating a path that looks like it lives under `engagements/*/inputs/`
    must DENY.

    Asserts the CONTROL half too (the same fault outside inputs/ allows) so the
    detail line carries the whole split, but the mutation that proves this
    check is the fail-OPEN-everywhere one; the opposite direction is proven by
    `fails_open_outside_inputs_under_same_fault`.

    Skips under root, which bypasses directory permission bits entirely — a
    chmod that injects nothing would be a FALSE pass, not a pass.
    """
    name = "fails_closed_under_injected_fault"
    skip = fault_injection_skip(name, perms="directory")
    if skip is not None:
        return skip

    inputs_dir, outside_dir = _fault_split(root)
    with inject_fault(inputs_dir, outside_dir):
        inside = _run_hook(root, read_payload(str(inputs_dir / "fault_test.md")))
        outside = _run_hook(root, read_payload(str(outside_dir / "fault_test.md")))

    ok = (
        inside.returncode == 0 and inside.denied
        and "can't confirm this file is safe" in inside.reason
        and outside.returncode == 0 and not outside.denied
    )
    return bool_check(name, ok, detail=(
        f"SAME PermissionError, two scopes -> inside engagements/*/inputs/: "
        f"rc={inside.returncode} denied={inside.denied}; outside: "
        f"rc={outside.returncode} denied={outside.denied}; "
        f"reason={inside.reason[:140]!r}"))


def _degenerate_path_fails_closed_only_inside_inputs(root: Path) -> CheckResult:
    """The OTHER half of the fail-closed decision, and the one the permission
    fault above structurally cannot reach.

    `_evaluate` returns `None` for an out-of-scope path BEFORE it touches the
    filesystem, so a chmod fault outside `engagements/*/inputs/` never raises at
    all — the allow in the check above comes from SCOPE, not from the fail-open
    default. The fail-open default lives in `_evaluate`'s `except` clause and is
    selected by `_raw_looks_like_inputs(raw)`: a cheap, exception-free guess on
    the RAW path STRING, made before any filesystem access precisely so that
    "the evaluation itself blew up" still has a defined answer.

    Injecting a fault into that branch needs a path string that makes
    evaluation RAISE rather than decide. An embedded NUL byte does exactly
    that: `Path.parts` still splits it (so the raw guess works), but
    `Path.resolve()` raises `ValueError` — which `_resolve`'s `except OSError`
    does not catch, so it reaches `_evaluate`'s `except Exception`. Two such
    paths, identical but for their directory, must split: the one whose raw
    text sits under `engagements/*/inputs/` DENIES ("a truly degenerate input
    is treated as in-scope so it fails CLOSED rather than open"), the one
    outside ALLOWS.

    The mutation for this check forces the guess to True, so the OUTSIDE half
    goes red — the opposite direction from the permission-fault check's
    mutation, which forces the whole clause to allow. Neither can certify the
    other.
    """
    name = "degenerate_path_fails_closed_only_inside_inputs"
    fixture = _engagement(root, documents={"inputs/notes.md": RAW_TEXT})
    assert fixture.inputs_dir is not None
    outside_dir = root / "scratch_outside"
    outside_dir.mkdir(parents=True, exist_ok=True)

    inside_raw = f"{fixture.inputs_dir}/notes\x00.md"
    outside_raw = f"{outside_dir}/notes\x00.md"

    inside = _run_hook(root, read_payload(inside_raw))
    outside = _run_hook(root, read_payload(outside_raw))

    ok = (
        inside.returncode == 0 and inside.denied
        and "can't confirm this file is safe" in inside.reason
        and outside.returncode == 0 and not outside.denied and outside.silent
    )
    return bool_check(name, ok, detail=(
        f"SAME ValueError('embedded null byte'), two raw path shapes -> raw text "
        f"under engagements/*/inputs/: rc={inside.returncode} denied={inside.denied}; "
        f"raw text outside it: rc={outside.returncode} denied={outside.denied} "
        f"stdout={outside.stdout_text[:100]!r}"))


# --- process contract ---------------------------------------------------------

def _invoked_as_subprocess_not_import(root: Path) -> CheckResult:
    """Two invocations, one RELATIVE `file_path`, two different
    `CLAUDE_PROJECT_DIR` roots — see `_common.py`'s docstring for why that
    differential is what actually distinguishes a subprocess from an
    import-and-call. Root A carries the unscrubbed input (deny); root B is
    empty, so the same relative path resolves to nothing on disk (allow)."""
    a_root = root / "project_a"
    b_root = root / "project_b"
    b_root.mkdir(parents=True, exist_ok=True)
    build_fixture_engagement(a_root, slug=SLUG, engagement=ENGAGEMENT,
                             documents={"inputs/notes.md": RAW_TEXT})
    rel = f"engagements/{SLUG}/{ENGAGEMENT}/inputs/notes.md"

    return check_invoked_as_subprocess_not_import(
        _hook_path(),
        hook_label="anonymize-guard.py",
        observe_a=lambda: _run_hook(a_root, read_payload(rel)).denied,
        observe_b=lambda: _run_hook(b_root, read_payload(rel)).denied,
        what="denied",
    )


def _runs_under_registered_interpreter(root: Path) -> CheckResult:
    """#192/backlog :116 — the hook must be spawned under whatever
    `.claude/settings.json` registers for it (bare `python3`, what every
    consultant session runs it under), never a silent fallback to
    `sys.executable` (CI's 3.11 / the local venv). `spawn` goes through this
    row's own production `_run_hook`, so the check observes the argv the row
    really spawns."""
    probe = root / "scratch_outside" / "probe.md"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text(RAW_TEXT, encoding="utf-8")
    return check_runs_under_registered_interpreter(
        _hook_path(),
        hook_label="anonymize-guard.py",
        spawn=lambda: _run_hook(root, read_payload(str(probe))),
    )




def _payload(tool: str, tool_input: dict) -> bytes:
    """Generic PreToolUse payload via the shared builder. `_common` ships only
    Read and Bash builders, which is itself a trace of the gap finding 7
    describes — the harness could not express a Grep payload because nothing
    gated Grep."""
    return pretooluse_payload(tool, tool_input)


def _anonymizer_exemption_is_per_segment(root: Path) -> CheckResult:
    """Mayur's finding 2 (2026-08-30), as a regression test.

    The exemption that lets the scrub command run was matched against the WHOLE
    command line, so any line merely CONTAINING "anonymize_transcript" was waved
    through in full:

        python3 scripts/anonymize_transcript.py --file a.md && cat <raw input>

    handed the raw client file to the model. Not contrived: when this guard
    denies a read its own message tells the consultant to run that scrub, and
    appending "&& show me the file" is the obvious next keystroke. The exemption
    is now scoped to the segment that actually invokes the anonymiser.
    """
    name = "anonymizer_exemption_is_per_segment"
    fixture = _engagement(root, documents={"inputs/notes.md": RAW_TEXT})
    raw = fixture.inputs_dir / "notes.md"
    chained_and = _run_hook(root, bash_payload(
        f"python3 scripts/anonymize_transcript.py --file a.md && cat {raw}"))
    chained_semi = _run_hook(root, bash_payload(
        f"python3 scripts/anonymize_transcript.py --file a.md ; cat {raw}"))
    scrub_alone = _run_hook(root, bash_payload(
        f"python3 scripts/anonymize_transcript.py --file {raw} --engagement-dir x"))
    ok = (chained_and.denied and chained_semi.denied and not scrub_alone.denied)
    return bool_check(name, ok, detail=(
        f"'&& cat raw' denied={chained_and.denied} (want True); "
        f"'; cat raw' denied={chained_semi.denied} (want True); "
        f"scrub alone denied={scrub_alone.denied} (want False)"))


def _gates_quoted_path_containing_spaces(root: Path) -> CheckResult:
    """Mayur's finding 3 (2026-08-30), as a regression test.

    Path extraction split on whitespace, so `cat "…/Meeting Notes.md"` became
    two fragments, neither a real path — nothing was checked and the read was
    allowed, while a Read of the same file was correctly denied. Client files
    are called "Annual Report 2025.pdf"; spaces are the norm, not the exception.
    Also covers the UNBALANCED-quote fallback, which must stay closed: failing
    to parse a command must never mean failing to check it.
    """
    name = "gates_quoted_path_containing_spaces"
    fixture = _engagement(root, documents={"inputs/Meeting Notes.md": RAW_TEXT})
    raw = fixture.inputs_dir / "Meeting Notes.md"
    dq = _run_hook(root, bash_payload(f'cat "{raw}"'))
    sq = _run_hook(root, bash_payload(f"cat '{raw}'"))
    unbalanced = _run_hook(root, bash_payload(f'cat "{raw}'))
    ok = dq.denied and sq.denied and unbalanced.denied
    return bool_check(name, ok, detail=(
        f'double-quoted denied={dq.denied}; single-quoted denied={sq.denied}; '
        f'unbalanced-quote denied={unbalanced.denied} (all want True)'))


def _gates_search_tools_not_only_read_and_bash(root: Path) -> CheckResult:
    """Mayur's finding 7 (2026-08-30), as a regression test.

    Grep RETURNS MATCHING LINES — that is file content, so an ungated Grep into
    `inputs/` hands over real names and emails exactly as a Read would. The hook
    was bound to Read|Bash only, leaving a third door open on a guarantee stated
    as "nothing under inputs/ passes". A DIRECTORY search root is the case that
    matters: `_evaluate` returns None for a directory, which is right for Read
    and wrong for a search that walks everything beneath it.
    """
    name = "gates_search_tools_not_only_read_and_bash"
    fixture = _engagement(root, documents={"inputs/notes.md": RAW_TEXT})
    ing = fixture.inputs_dir
    outs = fixture.engagement_dir / "outputs"
    outs.mkdir(parents=True, exist_ok=True)
    (outs / "report.md").write_text("ordinary output\n", encoding="utf-8")
    grep_dir = _run_hook(root, _payload("Grep", {"pattern": "x", "path": str(ing)}))
    grep_file = _run_hook(root, _payload("Grep", {"pattern": "x", "path": str(ing / "notes.md")}))
    glob_dir = _run_hook(root, _payload("Glob", {"pattern": "*.md", "path": str(ing)}))
    grep_out = _run_hook(root, _payload("Grep", {"pattern": "x", "path": str(outs)}))
    ok = (grep_dir.denied and grep_file.denied and glob_dir.denied and not grep_out.denied)
    return bool_check(name, ok, detail=(
        f"Grep@inputs-dir={grep_dir.denied} Grep@file={grep_file.denied} "
        f"Glob@inputs={glob_dir.denied} (want True) | Grep@outputs={grep_out.denied} (want False)"))


def evaluate(target: str) -> list:  # noqa: ARG001 - self-contained, ignores target
    missing = missing_hook_check(_hook_path())
    if missing is not None:
        return [missing]
    return [
        run_in_tmp(_denies_unscrubbed_text_input, prefix=TMP_PREFIX),
        run_in_tmp(_allows_scrubbed_anon_artifact, prefix=TMP_PREFIX),
        run_in_tmp(_allows_when_sibling_is_current, prefix=TMP_PREFIX),
        run_in_tmp(_denies_stale_sibling_by_mtime, prefix=TMP_PREFIX),
        run_in_tmp(_denies_document_without_md_sidecar, prefix=TMP_PREFIX),
        run_in_tmp(_denies_unsupported_format_outright, prefix=TMP_PREFIX),
        run_in_tmp(_allows_paths_outside_inputs_scope, prefix=TMP_PREFIX),
        run_in_tmp(_gates_bash_command_reading_raw_input, prefix=TMP_PREFIX),
        run_in_tmp(_allows_bash_anonymizer_command_itself, prefix=TMP_PREFIX),
        run_in_tmp(_fails_closed_under_injected_fault, prefix=TMP_PREFIX),
        run_in_tmp(_degenerate_path_fails_closed_only_inside_inputs, prefix=TMP_PREFIX),
        run_in_tmp(_invoked_as_subprocess_not_import, prefix=TMP_PREFIX),
        run_in_tmp(_runs_under_registered_interpreter, prefix=TMP_PREFIX),
        run_in_tmp(_anonymizer_exemption_is_per_segment, prefix=TMP_PREFIX),
        run_in_tmp(_gates_quoted_path_containing_spaces, prefix=TMP_PREFIX),
        run_in_tmp(_gates_search_tools_not_only_read_and_bash, prefix=TMP_PREFIX),
    ]
