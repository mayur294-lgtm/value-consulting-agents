"""engagement-migration component evaluator — deterministic regression
coverage for `scripts/migrate_engagements.py` (ticket #199; #168 shipped the
tool with no eval — see `.prd/backlog.md` :72 and :74, both reproduced as
checks below).

WHAT THIS ROW IS FOR
  `migrate_engagements.py` moves a client-named engagement directory
  (`engagements/hdfc/...`) to an opaque one (`engagements/<id>/...`). The
  directory slug is ALSO a deny-list source
  (`denylist.extract_terms_from_slug`), so a migration that only renames
  directories would silently disarm `mcp-query-guard.py` for any engagement
  whose deny-list comes from nothing but the slug — measured (the script's
  own docstring) as six of the seven live engagements when this was written.
  The fix is the SUPERSET RULE: resolve the deny-list before and after the
  move, and refuse unless `after` covers `before`.

  Every check here subprocesses the REAL script (`sys.executable
  scripts/migrate_engagements.py --project-dir <tmpdir> ...`) against a
  synthetic tree built with `rubrics._harness.build_fixture_engagement`, or
  calls `pii.identity.uncovered` directly. Nothing here ever touches the
  real `engagements/` tree, the real `.engagement_map.json`, or runs
  `--apply` against anything but a tempdir — per the ticket's own
  constraint, "never invoke the migration against `engagements/`".

BACKLOG :72 — COVERAGE IS A MATCHING QUESTION, NOT A SET-SUBSET ONE
  #168's first cut compared term STRINGS and was wrong in both directions at
  once: it reported `hdfc` as lost when `HDFC` covers it (the gate matches
  case-insensitively), and it would have accepted `Bank Australia` as
  covering `bankaustralia` in a variant where only the joined form
  mattered — the gate's alphanumeric word-boundary matching means the
  spaced form never fires on the concatenated one.
  `_deny_term_coverage_case_insensitive_not_falsely_lost` and
  `_deny_term_coverage_concatenated_not_falsely_retained` reproduce EXACTLY
  those two directions against `identity.uncovered()` directly — not
  through a migration end-to-end, so a regression in either direction is
  caught at its actual source rather than by coincidence.

BACKLOG :74 — THE CONCATENATED SLUG FORM HAS NO PROSE EQUIVALENT
  `denylist.extract_terms_from_slug` adds the joined form of a slug
  (`bank_australia` -> `bankaustralia`) — the shape that appears in email
  domains, subdomains and handles — and nothing in the prose-extraction
  path can produce it once the directory is opaque and the slug is gone.
  `identity._with_identifier_forms` is the mechanism that keeps it alive: it
  writes the joined form into the new CLIENT_PROFILE.md under a label
  `denylist.LABEL_LINE_RE` actually matches.
  `_migration_preserves_concatenated_slug_form` runs a REAL `--apply`
  against an underscore-slug fixture and reads the resulting
  CLIENT_PROFILE.md, so it fails if that write path is ever silently
  dropped — not just if the in-memory prediction is wrong.

Per the repo's synthetic-quarantine programme, every fixture slug/name below
is an obviously-placeholder `zzz`-prefixed token — never a fictional bank
name.

threshold: 1.00 in the registry — same rationale as engagement-identity and
mcp-query-guard/pii-anonymizer: a leak-prevention gate is pass/fail, not
"mostly correct." No `judge:` entries.
"""
from __future__ import annotations

import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from rubrics.base import CheckResult, repo_root
from rubrics._harness import DEFAULT_ENGAGEMENT, bool_check, build_fixture_engagement, run_in_tmpdir

SUBPROCESS_TIMEOUT_S = 30.0

_OPAQUE_ID_RE = re.compile(r"^[0-9a-f]{4,}$")

# The unfilled `templates/client_profile.md` shape (identical to what
# `_seed_unfilled_profile_template_project` in mcp_query_guard.py uses,
# and to the live `engagements/wsfs/CLIENT_PROFILE.md` before it was
# filled in) — a client whose profile carries no real name yet, so its
# ENTIRE deny-list is the directory slug. This is the exact shape that
# makes migration a live hazard rather than a formality.
_UNFILLED_PROFILE_TEXT = (
    "# Client Profile — [Client Name]\n\n"
    "## Client Identity\n\n"
    "- **Name:** [Full legal name]\n"
    "- **Short Name:** [slug used in directory names, e.g., `navy_federal`]\n"
)


def _migrate_script() -> Path:
    return repo_root() / "scripts" / "migrate_engagements.py"


def _run_migrate(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_migrate_script()), "--project-dir", str(root), *args],
        capture_output=True, timeout=SUBPROCESS_TIMEOUT_S,
    )


def _seed_covered_fixture(root: Path, slug: str):
    """A pre-migration client directory whose CLIENT_PROFILE.md already
    carries a real, filled name — so the deny-list superset check passes
    without needing `--name`. Reuses the shared harness fixture builder,
    which writes the exact pre-migration nested shape
    `migrate_engagements.discover()` expects."""
    return build_fixture_engagement(
        root, slug=slug, client_name=f"Zzz {slug.replace('_', ' ').title()} Holdings",
        short_name=slug, engagement=DEFAULT_ENGAGEMENT,
    )


def _seed_unfilled_fixture(root: Path, slug: str):
    """A pre-migration client directory whose profile is the literal,
    unfilled template — no real name resolvable anywhere, so its entire
    deny-list is the directory slug and migrating would drop it. Passes
    `client_name=None`, the one legal use of that argument
    (`build_fixture_engagement`'s own docstring)."""
    return build_fixture_engagement(
        root, slug=slug, client_name=None, short_name=None,
        engagement=DEFAULT_ENGAGEMENT, profile_text=_UNFILLED_PROFILE_TEXT,
    )


def _tree_snapshot(root: Path) -> dict:
    """Full-fidelity snapshot of everything under `root`: path, kind, file
    bytes, and permission bits. Used to assert "nothing was written" by
    COMPARISON, not by trusting an exit code — the ticket's own bar
    ("asserted not assumed")."""
    snap = {}
    for p in sorted(root.rglob("*")):
        rel = str(p.relative_to(root))
        mode = stat.S_IMODE(p.stat().st_mode)
        if p.is_file():
            snap[rel] = ("file", p.read_bytes(), mode)
        elif p.is_dir():
            snap[rel] = ("dir", None, mode)
    return snap


def _engagement_dirs(root: Path) -> set:
    engagements = root / "engagements"
    if not engagements.is_dir():
        return set()
    return {p.name for p in engagements.iterdir() if p.is_dir()}


def _import_identity():
    """Import `pii.identity` resolved through `repo_root()`, so a
    `--mutate` run against this row picks up the SHADOW's copy of the
    module rather than whatever happens to already be on `sys.path` —
    same resolution discipline `_run_migrate` uses for the subprocess
    path (mutations.py, "Rubrics that invoke a repo script ... resolving
    it through `rubrics.base.repo_root()`")."""
    scripts_dir = repo_root() / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from pii import identity  # noqa: PLC0415 - resolved lazily, path set above

    return identity


def _run_in_tmp(fn, *args) -> CheckResult:
    return run_in_tmpdir(fn, *args, prefix="engagement_migration_eval_")


# --- individual checks -------------------------------------------------------

def _dry_run_default_writes_nothing(root: Path) -> CheckResult:
    """"DRY RUN IS THE DEFAULT" (the script's own docstring, in caps).
    Running with NO `--apply` must leave the filesystem byte-for-byte
    unchanged — proven by comparing a full tree snapshot before and after,
    not by trusting the exit code."""
    name = "dry_run_default_writes_nothing"
    slug = "zzzdryrunnothing"
    _seed_covered_fixture(root, slug)
    before = _tree_snapshot(root)
    result = _run_migrate(root, [])  # no --apply
    after = _tree_snapshot(root)
    stdout = result.stdout.decode("utf-8", errors="replace")
    ok = result.returncode == 0 and before == after and "DRY RUN" in stdout
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} unchanged={before == after} "
        f"stdout_has_dry_run={'DRY RUN' in stdout} stdout={stdout[:300]!r}"
    ))


def _apply_flag_required_to_move_directory(root: Path) -> CheckResult:
    """The positive contrast to the dry-run check: WITH `--apply` on a
    covered fixture, the client-named directory is actually replaced by
    exactly one new opaque directory holding the moved engagement."""
    name = "apply_flag_required_to_move_directory"
    slug = "zzzapplymovetest"
    _seed_covered_fixture(root, slug)
    before_dirs = _engagement_dirs(root)
    result = _run_migrate(root, ["--apply"])
    after_dirs = _engagement_dirs(root)
    new_dirs = after_dirs - before_dirs
    new_id = next(iter(new_dirs)) if len(new_dirs) == 1 else ""
    moved = (root / "engagements" / new_id / DEFAULT_ENGAGEMENT).is_dir() if new_id else False
    ok = (
        result.returncode == 0
        and slug not in after_dirs
        and len(new_dirs) == 1
        and bool(_OPAQUE_ID_RE.match(new_id))
        and moved
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} before={sorted(before_dirs)} after={sorted(after_dirs)} "
        f"new_dirs={sorted(new_dirs)} moved={moved} "
        f"stdout={result.stdout.decode('utf-8', errors='replace')[:300]!r}"
    ))


def _refuses_and_writes_nothing_when_deny_term_would_be_lost(root: Path) -> CheckResult:
    """The acceptance bullet, verbatim: "An engagement whose migration
    would drop a deny term -> the script refuses and the check passes."
    Uses the unfilled-profile fixture — the live shape of six of the
    seven real engagements when this tool was written (the script's own
    docstring) — whose ENTIRE deny-list is the directory slug. Passes
    `--apply` too: a refusal must hold even when the consultant asked to
    apply, proven by the SAME before/after tree-snapshot comparison the
    dry-run check uses, not by trusting the exit code alone."""
    name = "refuses_and_writes_nothing_when_deny_term_would_be_lost"
    slug = "zzzrefusalcasetest"
    _seed_unfilled_fixture(root, slug)
    before = _tree_snapshot(root)
    result = _run_migrate(root, ["--apply"])
    after = _tree_snapshot(root)
    stdout = result.stdout.decode("utf-8", errors="replace")
    ok = result.returncode == 1 and before == after and "REFUSED" in stdout
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} unchanged={before == after} "
        f"refused_in_stdout={'REFUSED' in stdout} stdout={stdout[:500]!r}"
    ))


def _proceeds_when_name_override_supplies_missing_coverage(root: Path) -> CheckResult:
    """The complement of the refusal check: the SAME lossy fixture, but
    with `--name <slug>="<Client Name>"` supplying the coverage the
    profile alone lacks, must be ACCEPTED and actually migrated — proving
    `--name` is load-bearing, not decorative."""
    name = "proceeds_when_name_override_supplies_missing_coverage"
    slug = "zzzoverridecasetest"
    _seed_unfilled_fixture(root, slug)
    before_dirs = _engagement_dirs(root)
    result = _run_migrate(root, ["--apply", "--name", f'{slug}=Zzz Override Case Holdings'])
    after_dirs = _engagement_dirs(root)
    new_dirs = after_dirs - before_dirs
    stdout = result.stdout.decode("utf-8", errors="replace")
    ok = (
        result.returncode == 0
        and "REFUSED" not in stdout
        and slug not in after_dirs
        and len(new_dirs) == 1
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} refused_in_stdout={'REFUSED' in stdout} "
        f"before={sorted(before_dirs)} after={sorted(after_dirs)} stdout={stdout[:300]!r}"
    ))


def _migration_preserves_concatenated_slug_form(root: Path) -> CheckResult:
    """Backlog :74, end-to-end: an underscore slug's CONCATENATED form
    (`zzz_bank_australia` -> `zzzbankaustralia`) has no prose equivalent
    and nothing but the slug can produce it. Once the directory is
    opaque, the only place left for it to live is the new
    CLIENT_PROFILE.md's "Identifier Forms" section
    (`identity._with_identifier_forms`). Runs a REAL `--apply` and reads
    that file, rather than asserting on the tool's in-memory prediction —
    it fails if the write path is ever silently dropped, not just if the
    prediction is wrong.

    Uses the UNFILLED-profile fixture plus a `--name` override, not the
    "already covered" one: `render_client_profile` leaves an EXISTING,
    already-filled profile's bytes untouched (identity.py's own docstring
    — "a consultant's accumulated long-term notes ... never discarded"),
    which never reaches `_with_identifier_forms` at all. The unfilled
    profile is also the realistic case — `bdo_apa` in
    migrate_engagements.py's own docstring: "a slug is not a name ...
    supply it with --name"."""
    name = "migration_preserves_concatenated_slug_form"
    slug = "zzz_bank_australia"
    concatenated = slug.replace("_", "").replace("-", "")
    _seed_unfilled_fixture(root, slug)
    before_dirs = _engagement_dirs(root)
    result = _run_migrate(root, ["--apply", "--name", f"{slug}=Zzz Bank Australia Holdings"])
    after_dirs = _engagement_dirs(root)
    new_dirs = after_dirs - before_dirs
    new_id = next(iter(new_dirs)) if len(new_dirs) == 1 else ""
    profile_text = ""
    if new_id:
        profile = root / "engagements" / new_id / "CLIENT_PROFILE.md"
        if profile.is_file():
            profile_text = profile.read_text(encoding="utf-8", errors="replace")
    ok = (
        result.returncode == 0
        and bool(new_id)
        and concatenated in profile_text.lower()
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} slug={slug!r} concatenated={concatenated!r} "
        f"new_id={new_id!r} profile_contains_form={concatenated in profile_text.lower()} "
        f"profile_tail={profile_text[-400:]!r}"
    ))


def _deny_term_coverage_case_insensitive_not_falsely_lost(root: Path) -> CheckResult:  # noqa: ARG001
    """Backlog :72, direction 1: the naive string-set-subset comparison
    reports `hdfc` as LOST when the after-list only has `HDFC` — false,
    because the gate `mcp-query-guard.py`/`_term_pattern` matches
    case-insensitively. `identity.uncovered()` must NOT report this as
    lost."""
    name = "deny_term_coverage_case_insensitive_not_falsely_lost"
    identity = _import_identity()
    lost = identity.uncovered({"hdfc"}, {"HDFC"})
    ok = lost == set()
    return bool_check(name, ok, detail=(
        f"uncovered({{'hdfc'}}, {{'HDFC'}}) = {sorted(lost)!r} (expected: [] — case-insensitive match)"
    ))


def _deny_term_coverage_concatenated_not_falsely_retained(root: Path) -> CheckResult:  # noqa: ARG001
    """Backlog :72, direction 2 — the opposite mistake: a naive
    "contains" comparison would accept `Bank Australia` as covering
    `bankaustralia`, but the gate's alphanumeric word-boundary matching
    means the spaced form never fires on the concatenated one.
    `identity.uncovered()` must STILL report this as lost."""
    name = "deny_term_coverage_concatenated_not_falsely_retained"
    identity = _import_identity()
    lost = identity.uncovered({"bankaustralia"}, {"Bank Australia"})
    ok = lost == {"bankaustralia"}
    return bool_check(name, ok, detail=(
        f"uncovered({{'bankaustralia'}}, {{'Bank Australia'}}) = {sorted(lost)!r} "
        f"(expected: ['bankaustralia'] — the spaced form must NOT cover the concatenated one)"
    ))


def evaluate(target: str) -> list[CheckResult]:  # noqa: ARG001 - self-contained, ignores target
    script = _migrate_script()
    if not script.exists():
        return [CheckResult(
            "script_present", 0.0, False, hard_fail=True,
            detail=f"{script} not found — cannot run any subprocess check",
        )]

    return [
        _run_in_tmp(_dry_run_default_writes_nothing),
        _run_in_tmp(_apply_flag_required_to_move_directory),
        _run_in_tmp(_refuses_and_writes_nothing_when_deny_term_would_be_lost),
        _run_in_tmp(_proceeds_when_name_override_supplies_missing_coverage),
        _run_in_tmp(_migration_preserves_concatenated_slug_form),
        _run_in_tmp(_deny_term_coverage_case_insensitive_not_falsely_lost),
        _run_in_tmp(_deny_term_coverage_concatenated_not_falsely_retained),
    ]
