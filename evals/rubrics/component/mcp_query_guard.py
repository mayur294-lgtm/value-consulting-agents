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
import os
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rubrics.base import CheckResult, repo_root
from rubrics._harness import (
    check_runs_under_registered_interpreter,
    record_hook_invocation,
    registered_interpreter,
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
    return json.dumps({
        "tool_name": "mcp__backbase-infobank__search",
        "tool_input": tool_input,
    }).encode("utf-8")


def _run_hook(project_dir: Path, stdin_bytes: bytes) -> subprocess.CompletedProcess:
    """Invoke the real hook script as a subprocess, exactly as Claude Code
    does: JSON payload on stdin, CLAUDE_PROJECT_DIR pointing at the fixture
    root, decision read back from stdout/exit code.

    The interpreter is whatever `.claude/settings.json` actually registers
    for this hook (`registered_interpreter()`, ticket #192/backlog :116) —
    NOT `sys.executable`. Settings.json registers this hook as bare
    `python3`, the interpreter every consultant session runs it under; a
    subprocess call built from `sys.executable` would silently certify the
    hook under CI's/this eval-runner's interpreter instead, which is
    exactly the drift #192 exists to close. `registered_interpreter()`
    raises loudly (never falls back) if the hook isn't registered.

    `record_hook_invocation(argv)` below is load-bearing, not telemetry:
    it is what lets `runs_under_registered_interpreter` assert against the
    argv this helper REALLY spawned. Without it that check can only observe
    the resolver's return value, and reverting this line to
    `[sys.executable, ...]` scores 1.000 green (spec-review FAIL,
    2026-08-26). Never spawn the hook here without recording first."""
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    argv = registered_interpreter(_hook_path()) + [str(_hook_path())]
    record_hook_invocation(argv)
    return subprocess.run(
        argv,
        input=stdin_bytes,
        capture_output=True,
        timeout=SUBPROCESS_TIMEOUT_S,
        env=env,
    )


def _parsed_stdout(result: subprocess.CompletedProcess) -> Optional[dict]:
    out = result.stdout.decode("utf-8", errors="replace").strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def _is_deny(result: subprocess.CompletedProcess) -> tuple[bool, Optional[dict]]:
    parsed = _parsed_stdout(result)
    if parsed is None:
        return False, None
    decision = (parsed.get("hookSpecificOutput") or {}).get("permissionDecision")
    return decision == "deny", parsed


def _bool_check(name: str, ok: bool, *, detail: str = "", hard_fail: bool = True) -> CheckResult:
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=hard_fail, detail=detail)


def _seed_denylist_project(root: Path) -> Path:
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
    """
    client_dir = root / "engagements" / PLACEHOLDER_CLIENT
    client_dir.mkdir(parents=True)
    (client_dir / "CLIENT_PROFILE.md").write_text(
        "# CLIENT_PROFILE\n\n"
        "## EXECUTIVE SUMMARY\n\n"
        "**NEVER** share these figures outside the account team. This "
        "profile covers ALL engagement details for the SME segment at "
        "MEDIUM sensitivity — internal use only.\n\n"
        "- **Client Name:** Placeholder Holdings Group (ZPC)\n"
        "- **Primary Contact:** Jane Placeholder, SVP Digital Banking\n",
        encoding="utf-8",
    )
    engagement_dir = client_dir / "2026-01_test_engagement"
    (engagement_dir / "inputs").mkdir(parents=True)
    (engagement_dir / "ENGAGEMENT_CONTEXT.md").write_text(
        "# ENGAGEMENT_CONTEXT\n\n"
        f"- **Client Name:** {CONTEXT_ONLY_IDENTIFIER}\n",
        encoding="utf-8",
    )
    (engagement_dir / "inputs" / "engagement_intake.md").write_text(
        "# Engagement Intake\n\n"
        f"- **Client Name:** {INTAKE_ONLY_IDENTIFIER}\n",
        encoding="utf-8",
    )
    return client_dir


def _seed_generic_words_label_project(root: Path) -> Path:
    """A separate, minimal fixture (deliberately isolated from
    _seed_denylist_project so its terms can't leak in) for the bold-label
    regression: a "- **Client Name:** ..." value made ENTIRELY of words that
    are individually on GENERIC_STOPLIST ("First", "National", "Trust" are
    all in it), so the single-word extraction path cannot catch it — only
    the multi-word phrase path can. The slug is unrelated filler so it can't
    accidentally supply the same terms via a different path."""
    client_dir = root / "engagements" / "zzzboldlabeltest"
    client_dir.mkdir(parents=True)
    (client_dir / "CLIENT_PROFILE.md").write_text(
        "# Engagement Profile\n\n"
        "- **Client Name:** First National Trust\n",
        encoding="utf-8",
    )
    return client_dir


# Regression coverage for finding 6: templates/client_profile.md's "##
# Client Identity" section stores the client's legal name as a bare
# "- **Name:** ..." field (not "Client Name:"), which _LABEL_LINE_RE never
# matched. PLACEHOLDER_PROFILE_NAME stands in for a populated legal name —
# NOT a fictional bank name (no "Bank"/institution word), per the repo's
# synthetic-quarantine programme.
PLACEHOLDER_PROFILE_NAME = "Zzzplaceholder Fifth Test Holdings"


def _seed_profile_name_label_project(root: Path) -> Path:
    """A fixture isolated from _seed_denylist_project (different client slug,
    no overlapping terms) with a CLIENT_PROFILE.md shaped exactly like
    templates/client_profile.md's real "## Client Identity" section: a
    populated bare "- **Name:**" field. Used by
    denies_client_name_from_profile_name_label."""
    client_dir = root / "engagements" / "zzznamelabeltest"
    client_dir.mkdir(parents=True)
    (client_dir / "CLIENT_PROFILE.md").write_text(
        "# Client Profile — Zzzplaceholder\n\n"
        "## Client Identity\n\n"
        f"- **Name:** {PLACEHOLDER_PROFILE_NAME}\n"
        "- **Short Name:** zzznamelabeltest\n",
        encoding="utf-8",
    )
    return client_dir


def _seed_unfilled_profile_template_project(root: Path) -> Path:
    """A fixture whose CLIENT_PROFILE.md is the literal, unfilled
    templates/client_profile.md — the exact live shape of
    engagements/wsfs/CLIENT_PROFILE.md today: "- **Name:** [Full legal
    name]". Used by ignores_unfilled_template_placeholders (this is the
    trap-1 guard: naively adding "name" to the label alternation would
    harvest "Full"/"legal"/"name" as bare deny-list terms and deny every
    query containing the ordinary word "name")."""
    client_dir = root / "engagements" / "zzzunfilledprofiletest"
    client_dir.mkdir(parents=True)
    (client_dir / "CLIENT_PROFILE.md").write_text(
        "# Client Profile — [Client Name]\n\n"
        "## Client Identity\n\n"
        "- **Name:** [Full legal name]\n"
        "- **Short Name:** [slug used in directory names, e.g., `navy_federal`]\n",
        encoding="utf-8",
    )
    return client_dir


def _run_in_tmp(fn, *args) -> CheckResult:
    """Run a check body inside a fresh tempdir, converting any unexpected
    exception (subprocess timeout, missing interpreter, ...) into a failing
    CheckResult instead of crashing the whole eval run."""
    try:
        with tempfile.TemporaryDirectory(prefix="mcp_guard_eval_") as td:
            return fn(Path(td), *args)
    except Exception as exc:  # noqa: BLE001 - convert to a reportable failure
        return _bool_check(fn.__name__.lstrip("_"), False,
                            detail=f"check raised {type(exc).__name__}: {exc}")


# --- individual checks ------------------------------------------------------

def _denies_query_containing_client_identifier(root: Path) -> CheckResult:
    name = "denies_query_containing_client_identifier"
    _seed_denylist_project(root)
    payload = _payload({"query": f"capabilities for {PLACEHOLDER_CLIENT} digital onboarding"})
    result = _run_hook(root, payload)
    denied, parsed = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r} "
        f"stderr={result.stderr.decode(errors='replace')[:200]!r}"
    ))


def _allows_generic_query(root: Path) -> CheckResult:
    name = "allows_generic_query"
    _seed_denylist_project(root)
    payload = _payload({"query": "digital onboarding capabilities for a Tier-2 retail bank"})
    result = _run_hook(root, payload)
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and not denied and not result.stdout.strip()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} stdout={result.stdout.decode(errors='replace')[:200]!r}"
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
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} stdout={result.stdout.decode(errors='replace')[:200]!r}"
    ))


def _fails_closed_on_unresolvable_denylist(root: Path) -> CheckResult:
    """Force _resolve_deny_list() to raise (not just come back empty) by
    making engagements/ unreadable: PermissionError on os.iterdir() is a
    real, unmocked exception the hook's try/except must catch and turn into
    a deny — proving the fail-closed contract, not just asserting it."""
    name = "fails_closed_on_unresolvable_denylist"
    if hasattr(os, "getuid") and os.getuid() == 0:
        return CheckResult(name, 1.0, True, skipped=True,
                            detail="running as root — chmod-based permission fault injection "
                                   "cannot be exercised (root bypasses directory perms); skipping "
                                   "rather than reporting a false pass or fail")

    engagements_dir = root / "engagements"
    engagements_dir.mkdir(parents=True)
    (engagements_dir / "somefile.md").write_text("placeholder", encoding="utf-8")
    original_mode = engagements_dir.stat().st_mode
    try:
        engagements_dir.chmod(0o000)
        payload = _payload({"query": "digital onboarding capabilities"})
        result = _run_hook(root, payload)
    finally:
        # Restore perms unconditionally so tempdir cleanup (which needs to
        # list/remove engagements_dir) can proceed.
        engagements_dir.chmod(original_mode | stat.S_IRWXU)

    denied, parsed = _is_deny(result)
    reason = ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "")
    ok = result.returncode == 0 and denied and "could not verify" in reason.lower()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} reason={reason[:200]!r}"
    ))


def _fails_closed_on_malformed_payload(root: Path) -> CheckResult:
    name = "fails_closed_on_malformed_payload"
    _seed_denylist_project(root)
    result = _run_hook(root, b"this is not json { at all")
    denied, parsed = _is_deny(result)
    reason = ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "")
    ok = result.returncode == 0 and denied and "could not verify" in reason.lower()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} reason={reason[:200]!r}"
    ))


def _allows_with_warning_when_no_denylist_configured(root: Path) -> CheckResult:
    """No engagements/ directory at all -> _resolve_deny_list() returns an
    empty set with NO exception. This is 'nothing to check against', which
    must allow (with a stderr warning) — distinct from the fail-closed cases
    above, where resolution itself errors."""
    name = "allows_with_warning_when_no_denylist_configured"
    payload = _payload({"query": f"capabilities for {PLACEHOLDER_CLIENT} digital onboarding"})
    result = _run_hook(root, payload)
    denied, _ = _is_deny(result)
    stderr = result.stderr.decode("utf-8", errors="replace")
    ok = (
        result.returncode == 0
        and not denied
        and not result.stdout.strip()
        and "no client deny-list configured" in stderr.lower()
    )
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} stdout={result.stdout.decode(errors='replace')[:120]!r} "
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
    parsed = _parsed_stdout(result)
    ok = (
        result.returncode == 0
        and parsed is not None
        and isinstance(parsed.get("hookSpecificOutput"), dict)
        and parsed["hookSpecificOutput"].get("hookEventName") == "PreToolUse"
        and parsed["hookSpecificOutput"].get("permissionDecision") == "deny"
        and isinstance(parsed["hookSpecificOutput"].get("permissionDecisionReason"), str)
        and parsed["hookSpecificOutput"]["permissionDecisionReason"] != ""
    )
    return _bool_check(name, ok, detail=(
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
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and not denied and not result.stdout.strip()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r}"
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
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r}"
    ))


def _fails_closed_on_unreadable_profile_file(root: Path) -> CheckResult:
    """Regression guard for finding 2: a single-file permission fault on
    CLIENT_PROFILE.md itself — distinct from fails_closed_on_unresolvable_
    denylist, which chmods the top-level engagements/ directory and never
    exercises a per-file read failure — must still deny-closed, even for a
    fully generic query with no identifier in it, because _read_bounded must
    propagate OSError rather than swallow it into an empty string."""
    name = "fails_closed_on_unreadable_profile_file"
    if hasattr(os, "getuid") and os.getuid() == 0:
        return CheckResult(name, 1.0, True, skipped=True,
                            detail="running as root — chmod-based permission fault injection "
                                   "cannot be exercised (root bypasses file perms); skipping "
                                   "rather than reporting a false pass or fail")

    client_dir = root / "engagements" / PLACEHOLDER_CLIENT
    client_dir.mkdir(parents=True)
    profile = client_dir / "CLIENT_PROFILE.md"
    profile.write_text(f"Client: {PLACEHOLDER_CLIENT}\n", encoding="utf-8")
    original_mode = profile.stat().st_mode
    try:
        profile.chmod(0o000)
        payload = _payload({"query": "digital onboarding capabilities for a Tier-2 retail bank"})
        result = _run_hook(root, payload)
    finally:
        # Restore perms unconditionally so tempdir cleanup can remove the file.
        profile.chmod(original_mode | stat.S_IRUSR | stat.S_IWUSR)

    denied, parsed = _is_deny(result)
    reason = ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "")
    ok = result.returncode == 0 and denied and "could not verify" in reason.lower()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} reason={reason[:200]!r}"
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
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r}"
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
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r}"
    ))


def _denies_identifier_from_engagement_intake_file(root: Path) -> CheckResult:
    """Same as above for inputs/engagement_intake.md and
    INTAKE_ONLY_IDENTIFIER — fails if that document's scanning loop is
    removed."""
    name = "denies_identifier_from_engagement_intake_file"
    _seed_denylist_project(root)
    payload = _payload({"query": f"capabilities for {INTAKE_ONLY_IDENTIFIER} digital onboarding"})
    result = _run_hook(root, payload)
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r}"
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
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and denied
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r}"
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
    denied, _ = _is_deny(result)
    ok = result.returncode == 0 and not denied and not result.stdout.strip()
    return _bool_check(name, ok, detail=(
        f"rc={result.returncode} denied={denied} "
        f"stdout={result.stdout.decode(errors='replace')[:200]!r}"
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
        _run_in_tmp(_runs_under_registered_interpreter),
    ]
