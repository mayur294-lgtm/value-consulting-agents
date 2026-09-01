"""engagement-identity component evaluator — deterministic regression coverage
for the opaque-engagement-ID primitives (ticket #199, solution-design-v6.md
D6; `scripts/pii/identity.py` is #166, `scripts/init_engagement_identity.py` +
`scripts/find_engagement.sh` are #168).

WHAT THIS ROW IS FOR
  `engagements/hdfc/...` puts the client's name in `compose_prompt`'s
  `engagement_dir` VALUE on every single agent call, however well the file
  CONTENTS are scrubbed (identity.py's own module docstring). The fix is an
  opaque directory (`engagements/<8-hex-id>/...`) whose binding to a client
  lives ONLY in `.engagement_map.json` (repo root, chmod 600, gitignored).
  That primitive shipped with no eval — this row is it. Backlog:
  "the opaque-ID binding ... carr[ies] no eval."

  Every check here is deterministic and free: subprocesses the REAL scripts
  (`init_engagement_identity.py`, `find_engagement.sh`) against a synthetic
  `CORTEX_ROOT` built fresh in a tempdir, or calls `pii.identity` directly —
  never imports-and-monkeypatches, and NEVER touches the real
  `engagements/` tree or the real `.engagement_map.json`.

WHY find_engagement.sh IS COPIED INTO THE FIXTURE, NOT RUN IN PLACE
  `find_engagement.sh` derives its own `CORTEX_ROOT` from
  `$(dirname "$0")/..` — its OWN location, not an env var. Running the
  repo's copy would therefore read and write the real, chmod-600
  `.engagement_map.json` at the repo root, which every ticket in this cycle
  (and this row's own harness) is required never to touch. So each check
  that needs it copies `find_engagement.sh` plus the `pii` package it
  imports into `<tmpdir>/scripts/`, so `$(dirname "$0")/..` resolves to the
  tempdir instead. The copies are read via `rubrics.base.repo_root()`, so a
  mutation to either script under `--mutate` is picked up (mutations.py:
  "Rubrics that invoke a repo script as a subprocess, resolving it through
  `rubrics.base.repo_root()`").

  `init_engagement_identity.py` takes `CORTEX_ROOT` as an environment
  variable already (by design — see its own docstring: "nothing
  client-named is ever passed on a command line, where it would show up in
  `ps` output"), so it is subprocessed straight from `repo_root()` without
  needing to be copied.

Per the repo's synthetic-quarantine programme, every fixture slug/name below
is an obviously-placeholder `zzz`-prefixed token — never a fictional bank
name.

threshold: 1.00 in the registry (see registry.yaml comment) — an identity
control (client-name leakage into every agent prompt) is pass/fail, same
rationale as mcp-query-guard/pii-anonymizer. No `judge:` entries.
"""
from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from rubrics.base import CheckResult, repo_root
from rubrics._harness import DEFAULT_ENGAGEMENT, bool_check, run_in_tmpdir

SUBPROCESS_TIMEOUT_S = 20.0

# An opaque ID is `secrets.token_hex(ID_BYTES)` — lowercase hex, nothing
# else. `zzz...`-prefixed fixture slugs below are deliberately NOT
# hex-only (they contain non-hex letters like z/g/n/p), so this pattern
# alone is enough to tell "a real opaque ID" from "the slug came through
# unchanged" — which is exactly the regression class this row exists to
# catch (identity.py's directory-name leak).
_HEX_ID_RE = re.compile(r"^[0-9a-f]{4,}$")


def _init_identity_script() -> Path:
    return repo_root() / "scripts" / "init_engagement_identity.py"


def _find_engagement_script() -> Path:
    return repo_root() / "scripts" / "find_engagement.sh"


def _seed_pii_package(root: Path) -> None:
    """`init_engagement_identity.py` does `sys.path.insert(0, str(root /
    "scripts"))` using the CORTEX_ROOT env var — NOT its own file
    location — before `from pii import identity`. In production
    CORTEX_ROOT is the real repo root, where `scripts/pii/` naturally
    exists; here CORTEX_ROOT is a bare fixture root, so the package has
    to be copied in first or EVERY subprocess call below fails with
    ModuleNotFoundError regardless of whether the code under test is
    correct. Idempotent (checked, not re-copied on a second call in the
    same fixture) and resolved through `repo_root()` so a `--mutate` run
    against this row still exercises the shadow's copy of `identity.py`.
    """
    dest_pii = root / "scripts" / "pii"
    if (dest_pii / "identity.py").is_file():
        return
    src_pii = repo_root() / "scripts" / "pii"
    dest_pii.mkdir(parents=True, exist_ok=True)
    for rel in ("__init__.py", "identity.py", "denylist.py"):
        shutil.copy2(str(src_pii / rel), str(dest_pii / rel))


def _run_init_identity(root: Path, slug: str, engagement_name: str) -> subprocess.CompletedProcess:
    """Subprocess `init_engagement_identity.py` exactly as `init_engagement.sh`
    does: inputs arrive as env vars, never as argv (the script's own
    docstring: "nothing client-named is ever passed on a command line").
    """
    _seed_pii_package(root)
    env = dict(os.environ)
    env["CORTEX_ROOT"] = str(root)
    env["CLIENT_SLUG"] = slug
    env["ENGAGEMENT_NAME"] = engagement_name
    return subprocess.run(
        [sys.executable, str(_init_identity_script())],
        capture_output=True, env=env, timeout=SUBPROCESS_TIMEOUT_S,
    )


def _first_stdout_line(result: subprocess.CompletedProcess) -> str:
    text = result.stdout.decode("utf-8", errors="replace").strip()
    return text.splitlines()[0] if text else ""


def _seed_identity_scripts(root: Path) -> Path:
    """Copy `find_engagement.sh` into `<root>/scripts/`, so the script's
    own `$(dirname "$0")/..` self-location trick resolves to the fixture
    root instead of the real repo — see module docstring. Returns the
    copied script's path. `_seed_pii_package` supplies the `pii` package
    it imports (find_engagement.sh's heredoc does the same
    CORTEX_ROOT-relative `sys.path.insert` as init_engagement_identity.py).
    """
    _seed_pii_package(root)
    dest_scripts = root / "scripts"
    src = repo_root() / "scripts" / "find_engagement.sh"
    dst = dest_scripts / "find_engagement.sh"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(dst))
    dst.chmod(dst.stat().st_mode | stat.S_IXUSR)
    return dst


def _run_find_engagement(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess:
    sh = root / "scripts" / "find_engagement.sh"
    return subprocess.run(
        [str(sh), *args], capture_output=True, timeout=SUBPROCESS_TIMEOUT_S,
    )


def _run_in_tmp(fn, *args) -> CheckResult:
    return run_in_tmpdir(fn, *args, prefix="engagement_identity_eval_")


# --- individual checks -------------------------------------------------------

def _mints_opaque_hex_id_not_slug_derived(root: Path) -> CheckResult:
    """The mandate this whole primitive exists for: the engagement ID is a
    RANDOM hex string (`secrets.token_hex`), never the slug or any
    transform of it (identity.py's own docstring: "A hash of 'hdfc' would
    be an opaque-looking string that a dictionary attack reverses in
    milliseconds ... The association is STORED, not computed."). Mutating
    `register_engagement` to hand back the slug itself must fail this."""
    name = "mints_opaque_hex_id_not_slug_derived"
    slug = "zzzidmintstest"
    result = _run_init_identity(root, slug, DEFAULT_ENGAGEMENT)
    engagement_id = _first_stdout_line(result)
    ok = (
        result.returncode == 0
        and bool(_HEX_ID_RE.match(engagement_id))
        and engagement_id != slug
        and slug not in engagement_id.lower()
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} id={engagement_id!r} slug={slug!r} "
        f"stderr={result.stderr.decode('utf-8', errors='replace')[:200]!r}"
    ))


def _map_entry_written_chmod_600(root: Path) -> CheckResult:
    """`.engagement_map.json` is the ONLY thing binding an ID back to a
    client, and it must be owner-read/write-only (identity.py MAP_MODE):
    the file records every client's real name in one place."""
    name = "map_entry_written_chmod_600"
    result = _run_init_identity(root, "zzzidmapmodetest", DEFAULT_ENGAGEMENT)
    map_path = root / ".engagement_map.json"
    exists = map_path.is_file()
    mode = stat.S_IMODE(map_path.stat().st_mode) if exists else None
    ok = result.returncode == 0 and exists and mode == 0o600
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} exists={exists} mode={oct(mode) if mode is not None else None} "
        f"(expected 0o600)"
    ))


def _client_identity_absent_from_directory_path(root: Path) -> CheckResult:
    """The literal acceptance bullet: "the client name appears nowhere in
    the directory path". The engagement holder directory must be NAMED
    after the opaque ID, not the slug — solution-design-v6.md D6, the
    entire reason this module exists (`compose_prompt` renders
    `engagement_dir` as a VALUE into every agent prompt)."""
    name = "client_identity_absent_from_directory_path"
    slug = "zzzpathleaktest"
    result = _run_init_identity(root, slug, DEFAULT_ENGAGEMENT)
    engagement_id = _first_stdout_line(result)
    holder = root / "engagements" / engagement_id
    ok = (
        result.returncode == 0
        and holder.is_dir()
        and holder.name == engagement_id
        and bool(_HEX_ID_RE.match(holder.name))
        and slug not in str(holder).lower()
    )
    return bool_check(name, ok, detail=(
        f"rc={result.returncode} id={engagement_id!r} holder={str(holder)!r} slug={slug!r}"
    ))


def _find_engagement_resolves_partial_match(root: Path) -> CheckResult:
    """`find_engagement.sh`'s whole reason to exist: a consultant types
    what they remember, not the opaque ID. "peoples", "BDO", "hdfc" must
    all resolve (the script's own header comment)."""
    name = "find_engagement_resolves_partial_match"
    _seed_identity_scripts(root)
    slug = "ZzzFindPartialClient"
    init_result = _run_init_identity(root, slug, DEFAULT_ENGAGEMENT)
    find_result = _run_find_engagement(root, ["findpartial"])  # substring of the slug
    stdout = find_result.stdout.decode("utf-8", errors="replace")
    ok = (
        init_result.returncode == 0
        and find_result.returncode == 0
        and slug in stdout
    )
    return bool_check(name, ok, detail=(
        f"init_rc={init_result.returncode} find_rc={find_result.returncode} "
        f"stdout={stdout[:300]!r} stderr={find_result.stderr.decode('utf-8', errors='replace')[:200]!r}"
    ))


def _find_engagement_resolves_case_insensitive_match(root: Path) -> CheckResult:
    """Same script, the other half of its contract: "peoples", "Peoples
    First Bank" and "peoples_first_bank" all resolve (script header) —
    proven here with a query in the OPPOSITE case from how the client was
    registered."""
    name = "find_engagement_resolves_case_insensitive_match"
    _seed_identity_scripts(root)
    slug = "zzzfindcasetest"
    init_result = _run_init_identity(root, slug, DEFAULT_ENGAGEMENT)
    find_result = _run_find_engagement(root, [slug.upper()])
    stdout = find_result.stdout.decode("utf-8", errors="replace")
    ok = (
        init_result.returncode == 0
        and find_result.returncode == 0
        and slug in stdout
    )
    return bool_check(name, ok, detail=(
        f"init_rc={init_result.returncode} find_rc={find_result.returncode} query={slug.upper()!r} "
        f"stdout={stdout[:300]!r}"
    ))


def _duplicate_engagement_refused_not_silently_recreated(root: Path) -> CheckResult:
    """init_engagement_identity.py's own stated contract: "A fresh ID is
    minted per engagement, so the destination can never collide on disk —
    the duplicate has to be caught through the map instead. Without this,
    `init_engagement.sh hdfc ...` run twice would produce two opaque
    directories holding two halves of one engagement." Exit code 3 names
    that specific failure (see the script's docstring)."""
    name = "duplicate_engagement_refused_not_silently_recreated"
    slug = "zzzdupclienttest"
    engagement_name = "2026-01_test_engagement"
    first = _run_init_identity(root, slug, engagement_name)
    first_id = _first_stdout_line(first)
    # init_engagement_identity.py itself only creates the client-level
    # holder + CLIENT_PROFILE.md; init_engagement.sh's subsequent `mkdir`
    # is what actually creates the engagement subdirectory the duplicate
    # check looks for. Simulate that one step so the second run's
    # `(Path(record["path"]) / name).is_dir()` check has something to find.
    (root / "engagements" / first_id / engagement_name).mkdir(parents=True, exist_ok=True)
    second = _run_init_identity(root, slug, engagement_name)
    stderr = second.stderr.decode("utf-8", errors="replace")
    ok = (
        first.returncode == 0
        and bool(_HEX_ID_RE.match(first_id))
        and second.returncode == 3
        and "already exists" in stderr.lower()
    )
    return bool_check(name, ok, detail=(
        f"first_rc={first.returncode} first_id={first_id!r} second_rc={second.returncode} "
        f"second_stderr={stderr[:300]!r}"
    ))



# --- D1: knowledge-label discriminator -------------------------------------
#
# `.design/knowledge-identity-resolution.md` D1. The label written into
# `knowledge/**` was `[Client-{domain}-{region}-{year}]` and nothing else,
# which is MANY-TO-ONE: three institutions in one table of
# EXTRACTION_REGISTRY.md all resolved to `[Client-retail-NAM-2026]`, merging
# their benchmarks into one apparent peer with nothing raising.
#
# These four checks run `pii.identity` in a SUBPROCESS resolved through
# `repo_root()`, not by importing it here — same reason the rest of this file
# subprocesses: an import would bind the real module once and a `--mutate`
# shadow would never be seen. See this module's header.


def _identity_eval(expr: str) -> subprocess.CompletedProcess:
    """Evaluate `expr` against the repo's (or the shadow's) pii.identity."""
    return subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r)\n"
         "from pii import identity as I\n"
         "print(%s)" % (str(repo_root() / "scripts"), expr)],
        capture_output=True, timeout=60,
    )


def _out(result) -> str:
    return result.stdout.decode("utf-8", errors="replace").strip()


def _label_discriminated_by_opaque_engagement_id() -> CheckResult:
    """Two engagements sharing domain, region AND year must not collide. This
    is the defect D1 exists for, stated as a test: same three inputs, two
    different opaque IDs, two different labels."""
    name = "label_discriminated_by_opaque_engagement_id"
    r = _identity_eval(
        "I.client_label('retail','NAM','2026','a3f2beef') + '|' + "
        "I.client_label('retail','NAM','2026','deadbe01')")
    out = _out(r)
    parts = out.split("|") if "|" in out else []
    ok = (
        r.returncode == 0 and len(parts) == 2
        and parts[0] != parts[1]
        and parts[0].endswith("-a3f2]") and parts[1].endswith("-dead]")
    )
    return bool_check(name, ok, detail=f"rc={r.returncode} out={out!r}")


def _label_discriminator_never_derived_from_client_name() -> CheckResult:
    """The discriminator must come from the RANDOM opaque ID, never from the
    client. A name-derived suffix looks anonymous and is not — the candidate
    set is a few thousand banks, so it is brute-forced in milliseconds, which
    would undo the anonymisation for every reader. Enforced two ways: the
    function takes no client parameter at all (it cannot leak what it is never
    given), and a client-shaped string offered as an ID is REFUSED rather than
    coerced into a suffix."""
    name = "label_discriminator_never_derived_from_client_name"
    sig = _identity_eval("__import__('inspect').signature(I.client_label)")
    slug = _identity_eval("repr(I.label_discriminator('zzzplaceholderbank'))")
    initials = _identity_eval("repr(I.label_discriminator('ZPB'))")
    sig_out, slug_out, ini_out = _out(sig), _out(slug), _out(initials)
    ok = (
        sig.returncode == 0 and slug.returncode == 0 and initials.returncode == 0
        and "client" not in sig_out.lower().replace("client_label", "")
        and slug_out == "None" and ini_out == "None"
    )
    return bool_check(name, ok, detail=(
        f"signature={sig_out!r} slug_disc={slug_out!r} initials_disc={ini_out!r}"))


def _label_well_formed_when_id_absent() -> CheckResult:
    """No opaque ID (a legacy client-named directory) must still yield a
    WELL-FORMED, name-free label — undiscriminated and therefore possibly
    colliding, which the caller warns about. Emitting an honest colliding
    label beats fabricating a discriminator; raising here would break a git
    hook."""
    name = "label_well_formed_when_id_absent"
    r = _identity_eval("I.client_label('retail','NAM','2026', None)")
    out = _out(r)
    ok = (
        r.returncode == 0
        and out.startswith("[Client-") and out.endswith("]")
        and out == "[Client-retail-NAM-2026]"
    )
    return bool_check(name, ok, detail=f"rc={r.returncode} out={out!r}")


def _engagement_id_resolved_from_opaque_path_only() -> CheckResult:
    """An opaque ID is only an engagement ID when it sits directly under
    `engagements/`. A random 8-hex directory elsewhere in the tree must not be
    mistaken for one, and a legacy client-named directory must resolve to None
    rather than to something that merely looks plausible."""
    name = "engagement_id_resolved_from_opaque_path_only"
    real = _identity_eval("repr(I.engagement_id_for_path('/tmp/x/engagements/a3f2beef/2026-02_retail'))")
    legacy = _identity_eval("repr(I.engagement_id_for_path('/tmp/x/engagements/zzzclientname/2026-02_retail'))")
    elsewhere = _identity_eval("repr(I.engagement_id_for_path('/tmp/x/cache/a3f2beef/thing'))")
    ro, lo, eo = _out(real), _out(legacy), _out(elsewhere)
    ok = (real.returncode == 0 and ro == "'a3f2beef'" and lo == "None" and eo == "None")
    return bool_check(name, ok, detail=f"opaque={ro!r} legacy={lo!r} elsewhere={eo!r}")


def evaluate(target: str) -> list[CheckResult]:  # noqa: ARG001 - self-contained, ignores target
    script = _init_identity_script()
    finder = _find_engagement_script()
    missing = [p for p in (script, finder) if not p.exists()]
    if missing:
        return [CheckResult(
            "scripts_present", 0.0, False, hard_fail=True,
            detail=f"missing: {[str(p) for p in missing]} — cannot run any subprocess check",
        )]

    return [
        _run_in_tmp(_mints_opaque_hex_id_not_slug_derived),
        _run_in_tmp(_map_entry_written_chmod_600),
        _run_in_tmp(_client_identity_absent_from_directory_path),
        _run_in_tmp(_find_engagement_resolves_partial_match),
        _run_in_tmp(_find_engagement_resolves_case_insensitive_match),
        _run_in_tmp(_duplicate_engagement_refused_not_silently_recreated),
        _label_discriminated_by_opaque_engagement_id(),
        _label_discriminator_never_derived_from_client_name(),
        _label_well_formed_when_id_absent(),
        _engagement_id_resolved_from_opaque_path_only(),
    ]
