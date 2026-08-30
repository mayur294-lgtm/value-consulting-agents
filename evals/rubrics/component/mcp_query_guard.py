"""mcp-query-guard component evaluator — deterministic regression coverage
for `.claude/hooks/mcp-query-guard.py` (PR #171 hardening cycle, ticket #155
follow-up; a broader `pii-anonymizer` row may fold this in under #161).

`.claude/hooks/mcp-query-guard.py` is the PreToolUse(mcp__.*) hook that blocks
outbound Backbase Infobank MCP queries containing a client/stakeholder
identifier (security_protocol.md §5). It is deliberately FAIL-CLOSED — the
opposite default of every other hook in the directory — because it gates an
outbound call to a third-party server, not a local read. That fail-closed
property is the entire point of the hook: before this file, nothing proved it
actually holds, so a future edit could silently flip it to fail-open and
nothing would notice.

Every check here invokes the REAL hook script as a subprocess, piping a
synthesized PreToolUse payload to its stdin exactly as Claude Code would — no
importing the module and monkeypatching its internals. This is the only way
to prove the process-level contract (stdout JSON shape, exit code) actually
holds, not just that the Python functions behave in-process.

#196 moved the mechanics of all of that — the fixture builder, the subprocess
invoker, the permission-fault injector, the pass/fail CheckResult helper — into
`rubrics/_harness.py`, shared with `pii_anonymizer.py` and with the eight rows
#197-#200 add. What stays HERE is the part that is actually about this hook:
which documents each fixture carries, and what each check asserts. The
prose inside those fixtures is passed to the builder verbatim rather than
generated, because those exact document shapes ARE the subject of four of the
checks below.

Fixtures are synthesized entirely inside a `tempfile.TemporaryDirectory()` and
pointed to via the `CLAUDE_PROJECT_DIR` env var the hook reads its
`engagements/` deny-list root from (see `PROJECT_DIR` in the hook). Nothing is
ever written inside the repo, and no real `engagements/**` data (gitignored
client PII) is read. Per the repo's active synthetic-quarantine programme, no
fixture uses a fictional bank name — obviously-placeholder tokens
(`zzzplaceholderclient`, `Placeholder Holdings Group (ZPC)`, and friends)
stand in for "a client identifier" instead.

The shared `_seed_denylist_project` fixture deliberately resembles a real
engagement document, not a two-line stub: it carries ALL-CAPS prose emphasis
that must NOT become deny terms, a bold "- **Client Name:** ... (ACRONYM)"
label line in the repo's actual template form, and a per-engagement
ENGAGEMENT_CONTEXT.md / inputs/engagement_intake.md pair each carrying an
identifier that exists nowhere else in the fixture. This exists because an
earlier, minimal version of this fixture (two lines, one nonsense token)
certified 1.000 on a hook that denied ordinary consultant queries and leaked
client names under two reproducible conditions — see commit 711b56c. A
fixture that never varies case, never puts prose outside a label line, and
never populates ENGAGEMENT_CONTEXT.md/engagement_intake.md cannot catch a
regression in any of those paths; do not simplify it back down.

threshold: 1.00 in the registry (see registry.yaml comment) — a privacy
control is pass/fail, not "mostly correct." No `judge:` entries — every check
here is deterministic and free.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from rubrics.base import CheckResult, repo_root
from rubrics._harness import (
    HookRun,
    bool_check,
    build_fixture_engagement,
    check_runs_under_registered_interpreter,
    fault_injection_skip,
    inject_fault,
    pretooluse_payload,
    run_hook_subprocess,
    run_in_tmpdir,
)

HOOK_REL_PATH = Path(".claude") / "hooks" / "mcp-query-guard.py"

# Obviously-placeholder token standing in for "a client identifier" in test
# fixtures — NOT a fictional bank name (the repo's synthetic-quarantine
# programme treats those as contamination; see synthetic-knowledge-guard.py).
PLACEHOLDER_CLIENT = "zzzplaceholderclient"

# Identifiers that must be extractable ONLY from one specific engagement
# document apiece — never from the client slug, CLIENT_PROFILE.md, or each
# other. That isolation is what makes denies_identifier_from_engagement_
# context_file / _intake_file fail if the corresponding scanning loop in
# _resolve_deny_list() is removed, instead of passing by coincidence via
# some other extraction path.
CONTEXT_ONLY_IDENTIFIER = "placeholdercontextonly"
INTAKE_ONLY_IDENTIFIER = "placeholderintakeonly"

SUBPROCESS_TIMEOUT_S = 15.0


def _hook_path() -> Path:
    return repo_root() / HOOK_REL_PATH


def _payload(tool_input: dict) -> bytes:
    return pretooluse_payload("mcp__backbase-infobank__search", tool_input)


def _run_hook(project_dir: Path, stdin_bytes: bytes) -> HookRun:
    """This row's ONE subprocess entry point — every check goes through it,
    including `runs_under_registered_interpreter`, so that check observes the
    argv this row really spawns rather than a re-implementation written for
    it.

    Everything about the invocation (registered interpreter, argv recording,
    CLAUDE_PROJECT_DIR, timeout, stdout parsing) now lives in
    `rubrics._harness.run_hook_subprocess` — see its docstring for why the
    interpreter must not be `sys.executable` and why the recording is
    load-bearing. Keep this wrapper: it pins the hook path and the timeout for
    the row, so a check never has to name either.
    """
    return run_hook_subprocess(_hook_path(), stdin_bytes,
                               project_dir=project_dir, timeout=SUBPROCESS_TIMEOUT_S)


def _seed_denylist_project(root: Path):
    """A fixture project root with one engagement whose documents resemble a
    real engagement tree, exercising every extraction path
    _resolve_deny_list() depends on:

      - the client directory slug (PLACEHOLDER_CLIENT), unconditionally
        added by _extract_terms_from_slug
      - CLIENT_PROFILE.md, written with ALL-CAPS prose emphasis ("**NEVER**",
        "ALL", "SME", "MEDIUM") OUTSIDE any label line — words that must NOT
        become deny terms — plus a bold "- **Client Name:** ... (ACRONYM)"
        label line in the repo's actual template form, carrying a paren
        acronym. This is the exact shape ("**Client Name:**" with the
        closing stars landing after the colon) that corrupted label-value
        extraction before it was fixed — see _extract_terms_from_text's
        docstring in the hook.
      - ENGAGEMENT_CONTEXT.md and inputs/engagement_intake.md, nested under
        a per-engagement subdirectory the way a real engagement is laid out,
        each carrying an identifier (CONTEXT_ONLY_IDENTIFIER /
        INTAKE_ONLY_IDENTIFIER) that appears NOWHERE else in this fixture —
        not in the slug, not in CLIENT_PROFILE.md — so a check built on one
        of them can only pass via that document's own scanning loop.

    Every document below is passed to `build_fixture_engagement` VERBATIM
    rather than generated from it: these exact shapes — ALL-CAPS prose
    emphasis outside a label line, the paren acronym, the bold-star placement
    — are the SUBJECT of four checks on this row, not incidental scaffolding.
    The harness supplies the tree, the writes and the fixture-integrity
    assertion; it must never supply this prose.
    """
    return build_fixture_engagement(
        root,
        slug=PLACEHOLDER_CLIENT,
        client_name=PLACEHOLDER_CLIENT,   # the identity this fixture carries is the SLUG
        short_name=None,
        engagement="2026-01_test_engagement",
        profile_text=(
            "# CLIENT_PROFILE\n\n"
            "## EXECUTIVE SUMMARY\n\n"
            "**NEVER** share these figures outside the account team. This "
            "profile covers ALL engagement details for the SME segment at "
            "MEDIUM sensitivity — internal use only.\n\n"
            "- **Client Name:** Placeholder Holdings Group (ZPC)\n"
            "- **Primary Contact:** Jane Placeholder, SVP Digital Banking\n"
        ),
        documents={
            "ENGAGEMENT_CONTEXT.md": (
                "# ENGAGEMENT_CONTEXT\n\n"
                f"- **Client Name:** {CONTEXT_ONLY_IDENTIFIER}\n"
            ),
            "inputs/engagement_intake.md": (
                "# Engagement Intake\n\n"
                f"- **Client Name:** {INTAKE_ONLY_IDENTIFIER}\n"
            ),
        },
    )


def _seed_generic_words_label_project(root: Path):
    """A separate, minimal fixture (deliberately isolated from
    _seed_denylist_project so its terms can't leak in) for the bold-label
    regression: a "- **Client Name:** ..." value made ENTIRELY of words that
    are individually on GENERIC_STOPLIST ("First", "National", "Trust" are
    all in it), so the single-word extraction path cannot catch it — only
    the multi-word phrase path can. The slug is unrelated filler so it can't
    accidentally supply the same terms via a different path."""
    return build_fixture_engagement(
        root,
        slug="zzzboldlabeltest",
        client_name="First National Trust",
        short_name=None,
        engagement=None,          # client-level fixture: CLIENT_PROFILE.md alone
        profile_text=(
            "# Engagement Profile\n\n"
            "- **Client Name:** First National Trust\n"
        ),
    )


# Regression coverage for finding 6: templates/client_profile.md's "##
# Client Identity" section stores the client's legal name as a bare
# "- **Name:** ..." field (not "Client Name:"), which _LABEL_LINE_RE never
# matched. PLACEHOLDER_PROFILE_NAME stands in for a populated legal name —
# NOT a fictional bank name (no "Bank"/institution word), per the repo's
# synthetic-quarantine programme.
PLACEHOLDER_PROFILE_NAME = "Zzzplaceholder Fifth Test Holdings"


def _seed_profile_name_label_project(root: Path):
    """A fixture isolated from _seed_denylist_project (different client slug,
    no overlapping terms) with a CLIENT_PROFILE.md shaped exactly like
    templates/client_profile.md's real "## Client Identity" section: a
    populated bare "- **Name:**" field. Used by
    denies_client_name_from_profile_name_label.

    Written out rather than taken from `default_client_profile_text()`: the H1
    here carries a trailing "— Zzzplaceholder" the generated form does not,
    and this row's subject is exactly which label lines the hook's extractor
    sees."""
    return build_fixture_engagement(
        root,
        slug="zzznamelabeltest",
        client_name=PLACEHOLDER_PROFILE_NAME,
        short_name="zzznamelabeltest",
        engagement=None,
        profile_text=(
            "# Client Profile — Zzzplaceholder\n\n"
            "## Client Identity\n\n"
            f"- **Name:** {PLACEHOLDER_PROFILE_NAME}\n"
            "- **Short Name:** zzznamelabeltest\n"
        ),
    )


def _seed_unfilled_profile_template_project(root: Path):
    """A fixture whose CLIENT_PROFILE.md is the literal, unfilled
    templates/client_profile.md — the exact live shape of
    engagements/wsfs/CLIENT_PROFILE.md today: "- **Name:** [Full legal
    name]". Used by ignores_unfilled_template_placeholders (this is the
    trap-1 guard: naively adding "name" to the label alternation would
    harvest "Full"/"legal"/"name" as bare deny-list terms and deny every
    query containing the ordinary word "name").

    `client_name=None` on purpose, and this is the ONLY fixture in the repo
    entitled to it: an unfilled template carries no resolvable identity, which
    is the entire point of the check. It switches off
    `build_fixture_engagement`'s fixture-integrity assertion, so never copy
    this argument to silence that assertion elsewhere."""
    return build_fixture_engagement(
        root,
        slug="zzzunfilledprofiletest",
        client_name=None,
        short_name=None,
        engagement=None,
        profile_text=(
            "# Client Profile — [Client Name]\n\n"
            "## Client Identity\n\n"
            "- **Name:** [Full legal name]\n"
            "- **Short Name:** [slug used in directory names, e.g., `navy_federal`]\n"
        ),
    )


def _run_in_tmp(fn, *args) -> CheckResult:
    """Row-local alias for the shared `run_in_tmpdir`, pinning this row's
    tempdir prefix so a leaked directory is traceable to this rubric."""
    return run_in_tmpdir(fn, *args, prefix="mcp_guard_eval_")


# --- individual checks ------------------------------------------------------

def _denies_query_containing_client_identifier(root: Path) -> CheckResult:
    name = "denies_query_containing_client_identifier"
    _seed_denylist_project(root)
    payload = _payload({"query": f"capabilities for {PLACEHOLDER_CLIENT} digital onboarding"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r} "
        f"stderr={result.stderr_text[:200]!r}"
    ))


def _allows_generic_query(root: Path) -> CheckResult:
    name = "allows_generic_query"
    _seed_denylist_project(root)
    payload = _payload({"query": "digital onboarding capabilities for a Tier-2 retail bank"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} stdout={result.stdout_text[:200]!r}"
    ))


def _detects_identifier_nested_in_dict_or_list(root: Path) -> CheckResult:
    name = "detects_identifier_nested_in_dict_or_list"
    _seed_denylist_project(root)
    payload = _payload({
        "filters": {
            "tags": ["general", "onboarding", PLACEHOLDER_CLIENT],
            "meta": {"nested": {"note": "no identifier here"}},
        },
    })
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} stdout={result.stdout_text[:200]!r}"
    ))


def _fails_closed_on_unresolvable_denylist(root: Path) -> CheckResult:
    """Force _resolve_deny_list() to raise (not just come back empty) by
    making engagements/ unreadable: PermissionError on os.iterdir() is a
    real, unmocked exception the hook's try/except must catch and turn into
    a deny — proving the fail-closed contract, not just asserting it."""
    name = "fails_closed_on_unresolvable_denylist"
    skip = fault_injection_skip(name, perms="directory")
    if skip is not None:
        return skip

    engagements_dir = root / "engagements"
    engagements_dir.mkdir(parents=True)
    (engagements_dir / "somefile.md").write_text("placeholder", encoding="utf-8")
    # `inject_fault` restores the mode on the way out no matter what — a 000
    # directory cannot be listed or removed, so without that the tempdir
    # cleanup would raise and turn this into a crashing check.
    with inject_fault(engagements_dir):
        payload = _payload({"query": "digital onboarding capabilities"})
        result = _run_hook(root, payload)

    ok = result.returncode == 0 and result.denied and "could not verify" in result.reason.lower()
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:200]!r}"
    ))


def _fails_closed_on_malformed_payload(root: Path) -> CheckResult:
    name = "fails_closed_on_malformed_payload"
    _seed_denylist_project(root)
    result = _run_hook(root, b"this is not json { at all")
    ok = result.returncode == 0 and result.denied and "could not verify" in result.reason.lower()
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:200]!r}"
    ))


def _allows_with_warning_when_no_denylist_configured(root: Path) -> CheckResult:
    """No engagements/ directory at all -> _resolve_deny_list() returns an
    empty set with NO exception. This is 'nothing to check against', which
    must allow (with a stderr warning) — distinct from the fail-closed cases
    above, where resolution itself errors."""
    name = "allows_with_warning_when_no_denylist_configured"
    payload = _payload({"query": f"capabilities for {PLACEHOLDER_CLIENT} digital onboarding"})
    result = _run_hook(root, payload)
    stderr = result.stderr_text
    ok = (
        result.returncode == 0
        and not result.denied
        and result.silent
        and "no client deny-list configured" in stderr.lower()
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} stdout={result.stdout_text[:120]!r} "
        f"stderr={stderr[:200]!r}"
    ))


def _deny_decision_shape_matches_hook_contract(root: Path) -> CheckResult:
    """stdout JSON must carry hookSpecificOutput.permissionDecision == "deny"
    with exit 0 (never a non-zero exit) — the exact contract PreToolUse hooks
    are required to speak."""
    name = "deny_decision_shape_matches_hook_contract"
    _seed_denylist_project(root)
    payload = _payload({"query": f"info about {PLACEHOLDER_CLIENT}"})
    result = _run_hook(root, payload)
    parsed = result.stdout_json
    ok = (
        result.returncode == 0
        and parsed is not None
        and isinstance(parsed.get("hookSpecificOutput"), dict)
        and parsed["hookSpecificOutput"].get("hookEventName") == "PreToolUse"
        and parsed["hookSpecificOutput"].get("permissionDecision") == "deny"
        and isinstance(parsed["hookSpecificOutput"].get("permissionDecisionReason"), str)
        and parsed["hookSpecificOutput"]["permissionDecisionReason"] != ""
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} parsed={json.dumps(parsed)[:300] if parsed else None}"
    ))


def _allows_query_with_common_emphasis_words(root: Path) -> CheckResult:
    """Regression guard for finding 1: the shared fixture's CLIENT_PROFILE.md
    carries ALL-CAPS prose emphasis ("NEVER", "ALL", "SME", "MEDIUM")
    OUTSIDE any client/bank/institution label line. A query using those same
    ordinary words generically must be ALLOWED — the ALL-CAPS acronym sweep
    must stay scoped to label-line values, not swept across the whole
    document. This is the exact class of bug that made the gate deny routine
    consultant queries like "list all onboarding capabilities"."""
    name = "allows_query_with_common_emphasis_words"
    _seed_denylist_project(root)
    payload = _payload({"query": "please list all SME digital onboarding options"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r}"
    ))


def _denies_bold_markdown_label_client_name(root: Path) -> CheckResult:
    """Regression guard for finding 3: a "- **Client Name:** ..." value made
    only of GENERIC_STOPLIST words (so single-word extraction can't catch
    it) must still deny via the multi-word phrase path, with markdown
    emphasis fully stripped from the captured value rather than leaking a
    stray "**"/leading-space into the deny term (which would silently break
    matching against ordinary mid-sentence text)."""
    name = "denies_bold_markdown_label_client_name"
    _seed_generic_words_label_project(root)
    payload = _payload({"query": "engagement notes for First National Trust digital onboarding"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r}"
    ))


def _fails_closed_on_unreadable_profile_file(root: Path) -> CheckResult:
    """Regression guard for finding 2: a single-file permission fault on
    CLIENT_PROFILE.md itself — distinct from fails_closed_on_unresolvable_
    denylist, which chmods the top-level engagements/ directory and never
    exercises a per-file read failure — must still deny-closed, even for a
    fully generic query with no identifier in it, because _read_bounded must
    propagate OSError rather than swallow it into an empty string."""
    name = "fails_closed_on_unreadable_profile_file"
    skip = fault_injection_skip(name, perms="file")
    if skip is not None:
        return skip

    # Deliberately NOT `build_fixture_engagement`: the fault must land on a
    # CLIENT_PROFILE.md whose only content is one line, so the failing read is
    # unambiguously THIS file's — and the fixture's shape is irrelevant here,
    # because the file is unreadable before the hook ever opens it.
    client_dir = root / "engagements" / PLACEHOLDER_CLIENT
    client_dir.mkdir(parents=True)
    profile = client_dir / "CLIENT_PROFILE.md"
    profile.write_text(f"Client: {PLACEHOLDER_CLIENT}\n", encoding="utf-8")
    with inject_fault(profile):
        payload = _payload({"query": "digital onboarding capabilities for a Tier-2 retail bank"})
        result = _run_hook(root, payload)

    ok = result.returncode == 0 and result.denied and "could not verify" in result.reason.lower()
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} reason={result.reason[:200]!r}"
    ))


def _matching_is_case_insensitive(root: Path) -> CheckResult:
    """Regression guard for finding 5's first mutation (removing
    re.IGNORECASE from _term_pattern()): the fixture writes PLACEHOLDER_CLIENT
    in lowercase, via the client directory slug. A query using a DIFFERENT
    case must still be DENIED — proving matching is actually
    case-insensitive rather than merely happening to match the fixture's own
    case, which no other check here exercises."""
    name = "matching_is_case_insensitive"
    _seed_denylist_project(root)
    payload = _payload({"query": f"capabilities for {PLACEHOLDER_CLIENT.upper()} digital onboarding"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r}"
    ))


def _denies_identifier_from_engagement_context_file(root: Path) -> CheckResult:
    """Regression guard for finding 5's second mutation: CONTEXT_ONLY_IDENTIFIER
    appears ONLY in ENGAGEMENT_CONTEXT.md — never in the slug or
    CLIENT_PROFILE.md — so this fails if the ENGAGEMENT_CONTEXT.md scanning
    loop in _resolve_deny_list() is removed, and can't pass by coincidence
    via some other extraction path."""
    name = "denies_identifier_from_engagement_context_file"
    _seed_denylist_project(root)
    payload = _payload({"query": f"capabilities for {CONTEXT_ONLY_IDENTIFIER} digital onboarding"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r}"
    ))


def _denies_identifier_from_engagement_intake_file(root: Path) -> CheckResult:
    """Same as above for inputs/engagement_intake.md and
    INTAKE_ONLY_IDENTIFIER — fails if that document's scanning loop is
    removed."""
    name = "denies_identifier_from_engagement_intake_file"
    _seed_denylist_project(root)
    payload = _payload({"query": f"capabilities for {INTAKE_ONLY_IDENTIFIER} digital onboarding"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r}"
    ))


def _denies_client_name_from_profile_name_label(root: Path) -> CheckResult:
    """Regression guard for finding 6: CLIENT_PROFILE.md's canonical "##
    Client Identity" section stores the client's legal name as a bare
    "- **Name:**" field, not "Client Name:". A query containing that
    populated name must be DENIED — proving the CLIENT_PROFILE.md-only
    "Name:" label path (_CLIENT_PROFILE_LABEL_LINE_RE) actually extracts
    it."""
    name = "denies_client_name_from_profile_name_label"
    _seed_profile_name_label_project(root)
    payload = _payload({"query": f"engagement notes for {PLACEHOLDER_PROFILE_NAME}"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r}"
    ))


def _ignores_unfilled_template_placeholders(root: Path) -> CheckResult:
    """Regression guard for finding 6's trap 1: with CLIENT_PROFILE.md's
    "- **Name:**" field still holding the literal unfilled
    "[Full legal name]" placeholder (the exact live shape of
    engagements/wsfs/CLIENT_PROFILE.md), a query containing the ordinary
    word "name" must be ALLOWED. This is the more important of the two new
    checks: naively adding "name" to a label alternation without
    placeholder-skipping would harvest "Full"/"legal"/"name" as bare
    deny-list terms and deny every query that happens to contain the word
    "name"."""
    name = "ignores_unfilled_template_placeholders"
    _seed_unfilled_profile_template_project(root)
    payload = _payload({"query": "what is this customer's account name field used for"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and not result.denied and result.silent
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r}"
    ))


_MAX_FILES_SCANNED_RE = re.compile(r"^MAX_FILES_SCANNED\s*=\s*(\d+)", re.MULTILINE)


def _hook_max_files_scanned() -> int:
    """Read MAX_FILES_SCANNED straight out of the hook's own source rather
    than hardcoding a second copy of the constant here that could silently
    drift out of sync with `.claude/hooks/mcp-query-guard.py` (e.g. someone
    raises the cap there and this check keeps using a stale, too-small
    number, quietly stopping proving anything)."""
    text = _hook_path().read_text(encoding="utf-8")
    m = _MAX_FILES_SCANNED_RE.search(text)
    if not m:
        raise RuntimeError(
            "MAX_FILES_SCANNED constant not found in mcp-query-guard.py source"
        )
    return int(m.group(1))


def _scan_limit_hit_fails_closed(root: Path) -> CheckResult:
    """Backlog :117 — no eval covered whether hitting MAX_FILES_SCANNED
    actually fails closed. `_read_bounded()` raises `_ScanLimitExceeded`
    once `_read_count` reaches the cap (commit 711b56c); `main()` must catch
    that (it's just another exception in the `_resolve_deny_list()` call)
    and deny via `_deny_gate_broken()`, exactly like an unreadable file or a
    malformed payload — NOT silently proceed with whatever partial deny-list
    it collected before the limit hit (the pre-711b56c bug this guards).

    Synthesizes MAX_FILES_SCANNED + 10 separate client directories, each
    with its own minimal CLIENT_PROFILE.md — the exact artifact
    `_read_bounded()` counts against, one read per client — so
    `_resolve_deny_list()` provably crosses the cap for real inside the
    subprocess, rather than asserting the exception path in the abstract.
    The +10 margin (not +1) keeps this robust to `os.walk`/`iterdir`
    ordering and to any incidental extra read the hook adds later, without
    weakening what's being proven."""
    name = "scan_limit_hit_fails_closed"
    limit = _hook_max_files_scanned()
    for i in range(limit + 10):
        build_fixture_engagement(
            root,
            slug=f"zzzscanlimit{i:04d}",
            client_name="Placeholder",
            short_name=None,
            engagement=None,   # ONE counted read per client — CLIENT_PROFILE.md
            profile_text="# Client Profile\n\n- **Client Name:** Placeholder\n",
        )
    payload = _payload({"query": "digital onboarding capabilities for a Tier-2 retail bank"})
    result = _run_hook(root, payload)
    ok = result.returncode == 0 and result.denied and "could not verify" in result.reason.lower()
    return bool_check(name, ok, detail=(
        f"limit={limit} dirs={limit + 10} rc={result.returncode} denied={result.denied} "
        f"reason={result.reason[:200]!r}"
    ))


def _runs_under_registered_interpreter(root: Path) -> CheckResult:
    """#192/backlog :116 — the hook must be invoked under whatever
    interpreter `.claude/settings.json` actually registers for it (bare
    `python3`), never a silent fallback to `sys.executable`. Shared check
    for Python-hook rows — see rubrics/_harness.py.

    `spawn` deliberately goes through this module's own production
    `_run_hook`, the same helper all 15 other checks use, so the check
    observes the argv the row REALLY spawns rather than a re-implementation
    written for it. The payload is a throwaway generic query against an
    empty fixture root; the decision is irrelevant here."""
    return check_runs_under_registered_interpreter(
        _hook_path(),
        hook_label="mcp-query-guard.py",
        spawn=lambda: _run_hook(root, _payload({"query": "generic platform capabilities"})),
    )



def _seed_staging_subdir_project(root: Path):
    """A project whose ONLY client material sits under the shared staging trees
    `engagements/inputs/<datecode>_<Client>_<Geo>/` — the real layout that the
    2026-08-30 migration dry run found uncovered.

    Deliberately builds the adversarial shape, not a friendly one:
      - the staging directory NAME encodes a 3-character acronym, which
        `_single_word_ok`'s four-character floor drops, so slug mining cannot
        recover it — only the profile can;
      - the name also carries a programme word (`Ignite`) and a geography, both
        of which slug mining WOULD harvest and which must never become deny
        terms; a query using them has to stay allowed.
    """
    staged = root / "engagements" / "inputs" / "2602_ZZQ_Ignite_Testland"
    staged.mkdir(parents=True)
    (staged / "CLIENT_PROFILE.md").write_text(
        "# Client Profile — [Client Name]\n\n## Client Identity\n\n"
        "- **Name:** [Full legal name]\n\n"
        "## Identifier Forms (deny-list)\n\n- **Client Name:** ZZQ\n",
        encoding="utf-8")


def _denies_client_from_staging_subdirectory(root: Path) -> CheckResult:
    """`engagements/inputs/` and `outputs/` are skipped as client dirs — the
    directories themselves are shared staging, and mining their names would put
    "inputs"/"outputs" on the deny-list. But skipping the whole TREE left four
    real clients contributing nothing: the gate was not weakened for them, it
    was absent. The resolver now descends one level and reads each per-client
    subdirectory's documents."""
    name = "denies_client_from_staging_subdirectory"
    _seed_staging_subdir_project(root)
    result = _run_hook(root, _payload({"query": "ZZQ digital onboarding capabilities"}))
    ok = result.returncode == 0 and result.denied
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={result.denied} "
        f"stdout={result.stdout_text[:200]!r} stderr={result.stderr_text[:200]!r}"))


def _staging_directory_names_do_not_become_deny_terms(root: Path) -> CheckResult:
    """The other half, and the reason the descent reads DOCUMENTS ONLY. The
    staging subdirectory name is `<datecode>_<Client>_<Geography-or-programme>`;
    mining it would harvest `Ignite` — a Backbase programme name — plus
    geography and the datecode, and blocking those breaks ordinary product
    queries. Mining the parent would be worse still ("inputs"/"outputs")."""
    name = "staging_directory_names_do_not_become_deny_terms"
    _seed_staging_subdir_project(root)
    probes = ["Ignite programme rollout guidance",
              "core banking in Testland",
              "what is in the inputs folder"]
    outcomes = []
    for q in probes:
        r = _run_hook(root, _payload({"query": q}))
        outcomes.append((q, r.returncode, r.denied))
    ok = all(rc == 0 and not denied for _, rc, denied in outcomes)
    return bool_check(name, ok, detail=f"probes={outcomes}")


def evaluate(target: str) -> list[CheckResult]:  # noqa: ARG001 - self-contained, ignores target
    hook = _hook_path()
    if not hook.exists():
        missing = CheckResult(
            "hook_script_present", 0.0, False, hard_fail=True,
            detail=f"{hook} not found — cannot run any subprocess check",
        )
        return [missing]

    return [
        _run_in_tmp(_denies_query_containing_client_identifier),
        _run_in_tmp(_allows_generic_query),
        _run_in_tmp(_detects_identifier_nested_in_dict_or_list),
        _run_in_tmp(_fails_closed_on_unresolvable_denylist),
        _run_in_tmp(_fails_closed_on_malformed_payload),
        _run_in_tmp(_allows_with_warning_when_no_denylist_configured),
        _run_in_tmp(_deny_decision_shape_matches_hook_contract),
        _run_in_tmp(_allows_query_with_common_emphasis_words),
        _run_in_tmp(_denies_bold_markdown_label_client_name),
        _run_in_tmp(_fails_closed_on_unreadable_profile_file),
        _run_in_tmp(_matching_is_case_insensitive),
        _run_in_tmp(_denies_identifier_from_engagement_context_file),
        _run_in_tmp(_denies_identifier_from_engagement_intake_file),
        _run_in_tmp(_denies_client_name_from_profile_name_label),
        _run_in_tmp(_ignores_unfilled_template_placeholders),
        _run_in_tmp(_scan_limit_hit_fails_closed),
        _run_in_tmp(_runs_under_registered_interpreter),
        _run_in_tmp(_denies_client_from_staging_subdirectory),
        _run_in_tmp(_staging_directory_names_do_not_become_deny_terms),
    ]
