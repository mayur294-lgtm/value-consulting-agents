"""mutation-harness component evaluator — the harness proves itself (#187,
closing PR 2 of the eval-gate-v7 epic).

Every other row in this registry certifies some piece of Cortex by claiming
its declared checks would go red under a real regression. `evals/mutations.py`
(#184), `--mutate` (#185, `run_experiment.py`), and the preflight coverage
gate (#186, `check_registry.py`) are the machinery that turns that claim from
a convention into something enforced. This row certifies THAT machinery —
the thing every other row's mutation proof depends on. If this row's checks
were vacuous, every other row's "proven" stamp would rest on an unverified
assumption.

Every check here drives the REAL `evals/mutations.py`, `evals/run_experiment.py`
(`--mutate` mode), and `evals/check_registry.py` as SUBPROCESSES — never an
import-and-call — exactly like `run_experiment_runner.py` (#183), which this
file mirrors in shape. Two subprocess strategies are used, matched to what
each production module allows:

  * `check_registry.py` refuses `CORTEX_EVAL_REGISTRY` outright (its own
    self-gate guard, #183 follow-up) — the only way to drive it against a
    synthetic registry is to copy `check_registry.py` + `mutations.py` (both
    pure-stdlib-import, no other repo files needed) into a fresh tempdir
    alongside a synthetic `registry.yaml`, then run the COPY with that tempdir
    as `cwd`. `HERE`/`ROOT` in the copy resolve relative to itself, so it
    reads the synthetic registry, never the real one.
  * `run_experiment.py --mutate <row>` DOES honour `CORTEX_EVAL_REGISTRY`
    (`_load_registry()`'s documented test-only seam) — driven that way
    directly against the real repo. Because a mutation's `file:` must resolve
    inside the real working tree (`mutations._resolve_mutable` requires the
    file to actually exist there before it can be copied into a shadow), the
    synthetic row used for this ("mh-probe-row") points at a REAL, already-
    committed, cheap, pure-Python evaluator (`rubrics.component.mcp_query_guard`)
    and mutates its REAL subject hook (`.claude/hooks/mcp-query-guard.py`) —
    inside a disposable shadow copy only, per `mutations.py`'s isolation
    contract; nothing here ever touches the working tree.

What "the harness proves itself" means concretely, and WHY each mutation
below is safe to apply for real when this row's OWN `mutations:` entries
(registry.yaml) get bite-proven via `--mutate mutation-harness`: every
mutation targets `evals/check_registry.py`, `evals/mutations.py`, or
`evals/run_experiment.py` — the SUBJECT modules, never this file. Per
`mutations.py`'s own isolation contract, whichever copy of those files is
executing (real, or nested inside however many shadow layers a proof is
running under) always resolves ITS OWN "root" from `__file__`/`ROOT`, so a
mutation can never point outside whatever shadow it is already confined to —
see each mutation's inline rationale in registry.yaml for the specific
reasoning, especially `working_tree_unchanged_after_run`'s (the one mutation
that deliberately breaks isolation, and why that stays safe).

NOT covered here: no `mutations:` are authored for any OTHER row (that is
every other ticket in this epic's job), and `evals/rubrics/specifics.py` is
untouched (design D10 freeze).
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

from rubrics.base import CheckResult, repo_root

CHECK_REGISTRY_REL_PATH = Path("evals") / "check_registry.py"
MUTATIONS_MODULE_REL_PATH = Path("evals") / "mutations.py"
RUN_EXPERIMENT_REL_PATH = Path("evals") / "run_experiment.py"
HOOK_REL_PATH = Path(".claude") / "hooks" / "mcp-query-guard.py"

# The durable allow-list rows (check_registry.py's MUTATION_PROOF_REQUIRED_ROWS)
# as of this ticket. `mutation-harness` is added to that constant by this same
# PR — see the Do NOT / Build notes on the ticket for why that line has to
# land together with this file.
HARD_ENFORCED_ROWS: tuple[str, ...] = ("run-experiment-runner", "mutation-harness")

CHECK_REGISTRY_TIMEOUT_S = 60.0
COMPONENT_RECHECK_TIMEOUT_S = 60.0
MUTATE_PROBE_TIMEOUT_S = 240.0
GIT_STATUS_TIMEOUT_S = 30.0


def _bool_check(name: str, ok: bool, *, detail: str = "", exercised: str | None = None,
                 hard_fail: bool = True) -> CheckResult:
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=hard_fail, detail=detail,
                        exercised=exercised)


def _out(result: subprocess.CompletedProcess) -> str:
    return (result.stdout.decode("utf-8", errors="replace")
            + result.stderr.decode("utf-8", errors="replace"))


def _run_in_tmp(fn):
    """Run a case body inside a fresh tempdir, converting any unexpected
    exception into a failing CheckResult instead of crashing the whole run."""
    try:
        with tempfile.TemporaryDirectory(prefix="mutation_harness_eval_") as td:
            return fn(Path(td))
    except Exception as exc:  # noqa: BLE001 - convert to a reportable failure
        return _bool_check(fn.__name__.lstrip("_"), False,
                            detail=f"check raised {type(exc).__name__}: {exc}")


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def _git_status_lines(root: Path) -> set[str] | None:
    """A SET of `git status --porcelain` lines for `root`, or None if git
    could not be run there at all (never treated as "clean" in that case —
    callers must handle None explicitly rather than let it read as success)."""
    try:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=str(root),
                            capture_output=True, timeout=GIT_STATUS_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    text = r.stdout.decode("utf-8", errors="replace")
    return {line for line in text.splitlines() if line.strip()}


def _write_minimal_check_registry_shadow(root: Path) -> tuple[Path, Path]:
    """Copy the REAL, unmodified check_registry.py + mutations.py into
    `<root>/evals/` so the preflight can be driven against a synthetic
    `registry.yaml` written alongside them. Neither module needs any other
    repo file (both stdlib-only imports), which is exactly why this can be a
    two-file copy instead of the full mutation shadow. Returns
    (check_registry_path, evals_dir)."""
    evals_dir = root / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo_root() / CHECK_REGISTRY_REL_PATH, evals_dir / "check_registry.py")
    shutil.copy2(repo_root() / MUTATIONS_MODULE_REL_PATH, evals_dir / "mutations.py")
    return evals_dir / "check_registry.py", evals_dir


def _run_mutate_subprocess(registry_path: Path, row: str, cwd: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    for k in ("ANTHROPIC_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"):
        env.pop(k, None)
    env["CORTEX_EVAL_REGISTRY"] = str(registry_path)
    cmd = [sys.executable, str(repo_root() / RUN_EXPERIMENT_REL_PATH), "--mutate", row]
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, timeout=MUTATE_PROBE_TIMEOUT_S, env=env)


# --- case 1: every_registered_check_has_a_mutation ---------------------------

_MISSING_MUTATION_RE_TEMPLATE = r"components\.(%s)\.code: check `[^`]+` has no `mutations:` entry"


def _every_registered_check_has_a_mutation(root: Path) -> CheckResult:
    """Two-part regression guard for #186's enforcement contract.

    Part A drives the REAL, committed `evals/check_registry.py` against the
    REAL, committed `evals/registry.yaml` and asserts neither hard-enforced
    row (`HARD_ENFORCED_ROWS`) shows a missing-mutation error TODAY — the
    literal "every registered check has a mutation" claim, verified live.

    Part B proves the ENFORCEMENT MECHANISM behind that claim, not just its
    current outcome: a row named for one of the harness's own self-gates
    (`run-experiment-runner`) must be hard-enforced by preflight even when its
    live YAML declares NO `mutations:` key at all — the exact "quietly delete
    the key to dodge the gate" attempt `MUTATION_PROOF_REQUIRED_ROWS` exists
    to close (check_registry.py's staged-enforcement docstring). Part A alone
    cannot prove this: today's registry is fully covered, so the allow-list
    branch in `_row_claims_mutation_proof` never even executes when scoring
    the real registry — a mutation to that branch would be invisible to Part A
    alone. Part B manufactures the gap Part A's live state doesn't have.
    """
    name = "every_registered_check_has_a_mutation"

    real_result = subprocess.run(
        [sys.executable, str(repo_root() / CHECK_REGISTRY_REL_PATH)],
        cwd=str(repo_root()), capture_output=True, timeout=CHECK_REGISTRY_TIMEOUT_S,
    )
    real_out = _out(real_result)
    missing_pattern = re.compile(_MISSING_MUTATION_RE_TEMPLATE % "|".join(re.escape(r) for r in HARD_ENFORCED_ROWS))
    real_ok = real_result.returncode == 0 and not missing_pattern.search(real_out)

    check_registry_path, evals_dir = _write_minimal_check_registry_shadow(root)
    synthetic = {
        "components": {
            "run-experiment-runner": {
                "altitude": "component", "threshold": 1.00,
                "code": ["some_check_with_no_mutation_entry"],
                # deliberately NO `mutations:` key -- proving enforcement
                # survives the key being absent, not merely present-but-incomplete.
            },
        },
    }
    (evals_dir / "registry.yaml").write_text(yaml.safe_dump(synthetic, sort_keys=False), encoding="utf-8")
    synth_result = subprocess.run([sys.executable, str(check_registry_path)], cwd=str(root),
                                   capture_output=True, timeout=CHECK_REGISTRY_TIMEOUT_S)
    synth_out = _out(synth_result)
    synth_ok = (
        synth_result.returncode == 1
        and "components.run-experiment-runner.code: check `some_check_with_no_mutation_entry` "
            "has no `mutations:` entry" in synth_out
    )

    ok = real_ok and synth_ok
    return _bool_check(name, ok, exercised=f"evals/check_registry.py via {sys.executable}", detail=(
        f"[real registry] rc={real_result.returncode} (want 0), hard-enforced rows "
        f"{HARD_ENFORCED_ROWS} clean={real_ok}; "
        f"[allow-list-survives-missing-key probe] rc={synth_result.returncode} (want 1), "
        f"flagged-as-expected={synth_ok}; "
        f"real_out_tail={real_out[-300:]!r} synth_out_tail={synth_out[-300:]!r}"
    ))


# --- case 4: check_without_mutation_fails_preflight ---------------------------

def _check_without_mutation_fails_preflight(root: Path) -> CheckResult:
    """Regression guard for #186's general preflight enforcement: a row that
    currently claims mutation coverage (declares a `mutations:` key at all —
    the `_row_claims_mutation_proof` "claiming right now" branch, independent
    of the durable allow-list tested by case 1) but is missing an entry for
    one of its `code:` checks must ERROR and exit 1, naming the uncovered
    check. A second, fully-covered row in the SAME synthetic registry must
    pass clean — proving this isn't just "every row errors"."""
    name = "check_without_mutation_fails_preflight"
    check_registry_path, evals_dir = _write_minimal_check_registry_shadow(root)
    dummy_mutation = {"file": "evals/registry.yaml", "find": "components:", "replace": "componentz:"}
    registry = {
        "components": {
            "complete-row": {
                "altitude": "component", "threshold": 0.80,
                "code": ["check_a", "check_b"],
                "mutations": {"check_a": dummy_mutation, "check_b": dummy_mutation},
            },
            "under-covered-row": {
                "altitude": "component", "threshold": 0.80,
                "code": ["check_a", "check_b"],
                "mutations": {"check_a": dummy_mutation},
            },
        },
    }
    (evals_dir / "registry.yaml").write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
    result = subprocess.run([sys.executable, str(check_registry_path)], cwd=str(root),
                             capture_output=True, timeout=CHECK_REGISTRY_TIMEOUT_S)
    out = _out(result)
    ok = (
        result.returncode == 1
        and "components.under-covered-row.code: check `check_b` has no `mutations:` entry" in out
        and "components.complete-row.code: check `check_a`" not in out
        and "components.complete-row.code: check `check_b`" not in out
    )
    return _bool_check(name, ok, exercised=f"evals/check_registry.py via {sys.executable}", detail=(
        f"rc={result.returncode} (want 1); under-covered-row must ERROR naming `check_b`; "
        f"complete-row must pass clean; out_tail={out[-500:]!r}"
    ))


# --- shared probe for cases 2, 3, 5 --------------------------------------------
# All three exercise the SAME real `--mutate` run against a synthetic row
# ("mh-probe-row") pointed at the real, cheap, pure-Python `mcp-query-guard`
# evaluator -- one subprocess invocation instead of three, since each case
# only differs in which observable fact it checks about that one run.

@dataclass
class _ProbeResult:
    result: subprocess.CompletedProcess | None
    hash_before: str | None
    hash_after: str | None
    git_before: set[str] | None
    git_after: set[str] | None
    recheck: subprocess.CompletedProcess | None
    red_check: str
    inert_check: str
    error: str | None = None


def _run_shared_probe(tmp: Path) -> _ProbeResult:
    row = "mh-probe-row"
    red_check = "denies_query_containing_client_identifier"
    inert_check = "allows_generic_query"
    registry = {
        "components": {
            row: {
                "altitude": "component", "threshold": 0.80,
                "evaluator": "rubrics.component.mcp_query_guard",
                "code": [red_check, inert_check],
                "mutations": {
                    # A REAL mutation: flips the hook's one deny-on-match gate
                    # off, so a query that should be denied gets allowed instead.
                    red_check: {
                        "file": str(HOOK_REL_PATH),
                        "find": "if matched:",
                        "replace": "if False:",
                    },
                    # A DELIBERATELY inert mutation: `find` matches nothing in
                    # the real hook, so nothing changes and the check must be
                    # reported NOT PROVEN, never a false pass.
                    inert_check: {
                        "file": str(HOOK_REL_PATH),
                        "find": "__MUTATION_HARNESS_EVAL_STRING_NEVER_PRESENT_1234__",
                        "replace": "irrelevant",
                    },
                },
            },
        },
    }
    reg_path = tmp / "registry.yaml"
    reg_path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")

    root = repo_root()
    real_hook = root / HOOK_REL_PATH
    try:
        hash_before = _sha256_of(real_hook)
        git_before = _git_status_lines(root)
        result = _run_mutate_subprocess(reg_path, row, cwd=root)
        hash_after = _sha256_of(real_hook)
        git_after = _git_status_lines(root)
        recheck = subprocess.run(
            [sys.executable, str(root / RUN_EXPERIMENT_REL_PATH), "--component", "mcp-query-guard"],
            cwd=str(root), capture_output=True, timeout=COMPONENT_RECHECK_TIMEOUT_S,
        )
    except Exception as exc:  # noqa: BLE001 - report, never crash the whole run
        return _ProbeResult(None, None, None, None, None, None, red_check, inert_check,
                             error=f"{type(exc).__name__}: {exc}")
    return _ProbeResult(result, hash_before, hash_after, git_before, git_after, recheck,
                         red_check, inert_check)


# --- case 2: mutation_makes_named_check_red ------------------------------------

def _mutation_makes_named_check_red(probe: _ProbeResult) -> CheckResult:
    """Regression guard for `_prove_one`'s core before/after contract, both
    directions in one probe: a REAL mutation (the hook's deny-on-match gate
    disabled) must be reported `proven` with the named check going red; a
    DELIBERATELY INERT mutation (a `find` that matches nothing) on a
    different declared check in the SAME row must be reported NOT proven —
    "the harness reports not-proven rather than passing" (ticket acceptance).
    Both assertions read the SAME subprocess's combined output, so a runner
    that always prints "proven" regardless of outcome would fail this too."""
    name = "mutation_makes_named_check_red"
    if probe.error or probe.result is None:
        return _bool_check(name, False, detail=f"shared probe did not run: {probe.error}")
    out = _out(probe.result)
    proven_red = (
        f"proven: check `{probe.red_check}` went red" in out
        and "before 1.00 pass, after" in out
    )
    inert_not_proven = (
        f"check `{probe.inert_check}` did not detect mutation" in out
        and "mutation was INERT" in out
    )
    ok = proven_red and inert_not_proven
    return _bool_check(name, ok, exercised=f"evals/run_experiment.py --mutate via {sys.executable}", detail=(
        f"real mutation on `{probe.red_check}` reported proven={proven_red}; "
        f"deliberately inert mutation on `{probe.inert_check}` reported honestly "
        f"not-proven={inert_not_proven}; probe rc={probe.result.returncode}; "
        f"out_tail={out[-700:]!r}"
    ))


# --- case 3: restore_makes_it_green --------------------------------------------

def _restore_makes_it_green(probe: _ProbeResult) -> CheckResult:
    """Regression guard for the "restore" half of the contract: after a
    mutate-and-discard cycle completes, (a) the REAL subject file on disk is
    byte-identical to before -- the shadow was genuinely discarded, never
    written back -- and (b) a plain, unmutated re-score of the same component
    (`--component mcp-query-guard`, no CORTEX_EVAL_REGISTRY) reports PASS
    again. (b) is the check whose OWN mutation entry is provable: it targets
    `run_experiment.py`'s `--component` exit-code line specifically, which
    the `--mutate` code path returns before ever reaching (`args.mutate` is
    checked first in `main()`), so this mutation cannot cross-contaminate
    case 2's or case 5's use of the same probe."""
    name = "restore_makes_it_green"
    if probe.error or probe.result is None or probe.recheck is None:
        return _bool_check(name, False, detail=f"shared probe did not run: {probe.error}")
    hashes_match = probe.hash_before is not None and probe.hash_before == probe.hash_after
    recheck_ok = probe.recheck.returncode == 0
    ok = hashes_match and recheck_ok
    return _bool_check(
        name, ok,
        exercised=f"evals/run_experiment.py --component mcp-query-guard via {sys.executable}",
        detail=(
            f"real {HOOK_REL_PATH} sha256 unchanged after the mutate-and-discard cycle="
            f"{hashes_match} (before={probe.hash_before!r}, after={probe.hash_after!r}); "
            f"post-run recheck rc={probe.recheck.returncode} (want 0); "
            f"recheck_tail={_out(probe.recheck)[-300:]!r}"
        ),
    )


# --- case 5: working_tree_unchanged_after_run ----------------------------------

def _working_tree_unchanged_after_run(probe: _ProbeResult) -> CheckResult:
    """Regression guard for `WorkingTreeGuard`'s entire reason to exist: a
    `git status --porcelain` snapshot taken immediately before and after the
    SAME `--mutate` run (shared probe above) must be byte-set-identical.
    Compared as a DELTA, not against any fixed list -- pre-existing dirty
    files in a consultant's working tree (there are several as of this
    writing: `.prd/prd-v4.md`, `agents/.DS_Store`, `tools/roi_excel_generator.py`,
    `.design/solution-design-v5.md`, `.design/ux-design-v5.md`, `.prd/prd-v5.md`)
    appear identically in BOTH snapshots and cancel out of the delta; only
    lines that appear in one snapshot and not the other are a real finding."""
    name = "working_tree_unchanged_after_run"
    if probe.error or probe.result is None:
        return _bool_check(name, False, detail=f"shared probe did not run: {probe.error}")
    if probe.git_before is None or probe.git_after is None:
        return _bool_check(name, False, detail="could not read `git status --porcelain` around the probe run")
    created = sorted(probe.git_after - probe.git_before)
    removed = sorted(probe.git_before - probe.git_after)
    ok = not created and not removed
    return _bool_check(
        name, ok,
        exercised=f"git status --porcelain around evals/run_experiment.py --mutate via {sys.executable}",
        detail=(
            f"delta vs the pre-run snapshot ({len(probe.git_before)} pre-existing entries "
            f"tolerated by construction, since only the DELTA is compared): "
            f"created={created[:20]!r}, removed={removed[:20]!r}"
        ),
    )


def evaluate(target: str) -> list[CheckResult]:  # noqa: ARG001 - self-contained, ignores target
    checks: list[CheckResult] = [_run_in_tmp(_every_registered_check_has_a_mutation)]

    try:
        with tempfile.TemporaryDirectory(prefix="mutation_harness_eval_probe_") as td:
            probe = _run_shared_probe(Path(td))
    except Exception as exc:  # noqa: BLE001 - never let a probe crash sink the whole run
        probe = _ProbeResult(None, None, None, None, None, None,
                              "denies_query_containing_client_identifier", "allows_generic_query",
                              error=f"{type(exc).__name__}: {exc}")

    checks.append(_mutation_makes_named_check_red(probe))
    checks.append(_restore_makes_it_green(probe))
    checks.append(_run_in_tmp(_check_without_mutation_fails_preflight))
    checks.append(_working_tree_unchanged_after_run(probe))
    return checks
