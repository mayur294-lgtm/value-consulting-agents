#!/usr/bin/env python3
"""Registry preflight — every GATING golden must actually resolve in CI.

The eval registry (`evals/registry.yaml`) gates PRs. A gate is only real if the
fixture it scores against is present in a clean checkout. Two ways that silently
broke before:

  1. A `goldens:` / `input:` slot pointed into `engagements/**`, which is
     gitignored (PII). The file is absent in every clean checkout and in CI, so
     `run_experiment.py` [SKIP]s it — and a skip counts as a PASS. The gate was
     vacuously green (see the deliverable-goldens fix in this PR).
  2. A golden path was simply never committed (e.g. a never-created
     `evals/goldens/nfis/roi_config.json`).

This preflight makes both loud instead of silent. It is cheap ($0, no LLM) and
is meant to run FIRST in the eval CI job so a mis-wired registry fails fast with
a precise message, before any rubric runs.

Rules
-----
GATING slots — `deliverables.*.goldens`, `deliverables.*.negatives`,
`components.*.input`, and any `golden_engagement:` written as a PATH (contains
'/') — MUST:
  * exist in the working tree, AND
  * NOT be gitignored (i.e. be reproducible in CI).
A violation is a HARD ERROR (exit 1).

`golden_engagement:` written as a BARE NAME (e.g. `nfis`) resolves into the
gitignored `engagements/**` tree at runtime, so it is vacuous in CI. These are
reported as DEBT (warnings) — visible every run, but non-fatal, so the remaining
legacy cases can be migrated incrementally without blocking the gate today.

`monitor:` entries are real shipped engagement outputs, watched for drift and
never gating — they are allowed to be absent/gitignored and are skipped here.

Usage
-----
    python3 evals/check_registry.py           # exit 1 on any hard error
    python3 evals/check_registry.py --strict   # also fail on DEBT warnings
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent          # evals/
ROOT = HERE.parent                              # repo root
sys.path.insert(0, str(HERE))                   # so `import mutations` resolves regardless of cwd

import mutations  # noqa: E402 - evals/mutations.py; pure metadata reads only (mutations_from_spec()),
                   # no subprocess/shadow-copy work, so this preflight stays fast and dependency-free.

# --- staged enforcement of the mutation proof (#186) --------------------------
# Today only ONE row (`run-experiment-runner`, #185) declares `mutations:`.
# Enforcing "every `code:` check needs a mutation entry" as a hard error
# registry-wide right now would fail preflight on every other row and block
# the remaining tickets of the eval-gate-v7 epic. So enforcement is STAGED:
#
#   * A row that currently declares a `mutations:` key (or a dict-form
#     `negatives:`) is claiming a proof RIGHT NOW, and is hard-enforced
#     immediately — no opt-out required, no PR needed to "turn it on".
#   * A row on MUTATION_PROOF_REQUIRED_ROWS below is hard-enforced no matter
#     what its live YAML looks like — this is what makes "quietly delete the
#     `mutations:` key to dodge the gate" impossible: the row stays
#     hard-enforced even if the key vanishes. Add a row's name here in the
#     SAME PR that adds its first `mutations:` entry; never remove a name
#     once added.
#   * Everything else — a row with a `code:` list and no mutation
#     declaration at all, not on the allow-list — is reported as DEBT: loud,
#     counted, non-fatal, until it's migrated. `.prd/backlog.md` (eval-gate-v7
#     epic) is the single place that tracks which rows still need this.
#
# THE ONE-LINE FLIP: once every row in registry.yaml has been migrated, set
# MUTATIONS_ENFORCED_FOR_ALL_ROWS to True. That turns every remaining
# uncovered check into a hard error, registry-wide, with no other code
# change required.
MUTATION_PROOF_REQUIRED_ROWS: frozenset[str] = frozenset({
    "run-experiment-runner",   # #185 — the worked example; first row migrated
})
MUTATIONS_ENFORCED_FOR_ALL_ROWS = False


def _resolve(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else (ROOT / q)


def _gitignored(path: Path) -> bool:
    """True if git ignores `path` (so it won't be in a clean checkout / CI)."""
    try:
        r = subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=ROOT, capture_output=True,
        )
        return r.returncode == 0
    except OSError:
        # No git available — can't prove it's ignored; don't hard-fail on that.
        return False


def _row_claims_mutation_proof(name: str, spec: dict) -> bool:
    """A row is hard-enforced — no opt-out — if EITHER:
      * it is on the durable MUTATION_PROOF_REQUIRED_ROWS allow-list (stays
        true even if the row's `mutations:` key is later deleted, broken, or
        temporarily commented out — that is the whole point of the
        allow-list: it is not derived from the row's current YAML content),
        or
      * it currently declares a `mutations:` key at all, or a dict-form
        `negatives:` (the fixture-mutation shape consumed by
        `mutations.mutations_from_spec`) — a row claiming coverage right now
        gets no grace period even before anyone remembers to add it to the
        allow-list. A LIST-form `negatives:` is the legacy
        separate-negative-file convention (see roi-financial-modeler) and
        claims nothing about mutation proof.
    """
    if name in MUTATION_PROOF_REQUIRED_ROWS:
        return True
    if "mutations" in spec:
        return True
    return isinstance(spec.get("negatives"), dict)


def check_mutation_coverage(name: str, spec: dict, errors: list[str], debt: list[str]) -> None:
    """Preflight enforcement of the mutation proof (#186): every check name
    in a row's `code:` list must resolve to a `mutations:`/dict-`negatives:`
    entry that would actually prove it — a check with no mutation entry
    certifies nothing. See the MUTATIONS_ENFORCED_FOR_ALL_ROWS staging note
    above for why an uncovered row is DEBT today rather than a hard error.
    """
    code_names = list(spec.get("code") or [])
    if not code_names:
        return
    try:
        mut_list = mutations.mutations_from_spec(spec)
    except mutations.MutationHarnessError as exc:
        errors.append(f"components.{name}.mutations: mutation declarations are malformed — {exc}")
        return
    covered = {m.check for m in mut_list}
    missing = [c for c in code_names if c not in covered]
    if not missing:
        return
    hard = _row_claims_mutation_proof(name, spec) or MUTATIONS_ENFORCED_FOR_ALL_ROWS
    for check in missing:
        msg = (f"components.{name}.code: check `{check}` has no `mutations:` entry — "
               f"a gate that cannot fail certifies nothing. Fix: add a `mutations:` entry "
               f"for `{check}` (see components.run-experiment-runner.mutations for the shape) "
               f"or a dict-form `negatives: {{{check}: {{strip: ...}}}}`.")
        if hard:
            errors.append(msg)
        else:
            debt.append(msg + " Non-fatal DEBT until migrated (row declares no `mutations:` "
                        "key at all yet) — tracked in .prd/backlog.md (eval-gate-v7 epic); "
                        "flip MUTATIONS_ENFORCED_FOR_ALL_ROWS above once every row is covered.")


def _check_pipeline_altitude_name_debt(debt: list[str]) -> None:
    """Grep assertion (#186, supports #188): the eval registry's three-tier
    restructuring (#188) renames the `pipeline` altitude everywhere it
    appears — `registry.yaml`'s `pipeline:` row, `run_experiment.py`'s
    `--altitude pipeline` / `altitude == "pipeline"`, `runtime.py`'s
    `report["pipeline"]`, and the `--altitude pipeline` invocations in the CI
    workflows. Until #188 lands this is expected to be non-zero everywhere,
    so it is reported as DEBT, not a hard error.

    #188 MUST flip this from `debt.append(...)` to `errors.append(...)` once
    the rename ships — that is the one-line flip this assertion exists to
    make obvious. Until then this is a loud, counted reminder, not a gate.
    """
    scope = [
        HERE / "registry.yaml",
        HERE / "run_experiment.py",
        HERE / "runtime.py",
        ROOT / ".github" / "workflows" / "evals.yml",
        ROOT / ".github" / "workflows" / "version-release.yml",
    ]
    pattern = re.compile(r"\bpipeline\b")
    hits = 0
    for f in scope:
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if pattern.search(line):
                hits += 1
    if hits:
        debt.append(
            f"grep: {hits} occurrence(s) of the old `pipeline` altitude name across "
            f"{len(scope)} registry/runner/CI files (supports #188's three-tier registry "
            f"restructuring, which renames it). Non-fatal DEBT until #188 lands — #188 MUST "
            f"flip this check from DEBT to a hard error (0 occurrences required) once the "
            f"rename ships (see this function's docstring in check_registry.py)."
        )


def main(argv: list[str]) -> int:
    # Self-gate escape-hatch guard (#183 follow-up). CORTEX_EVAL_REGISTRY exists
    # solely so evals/rubrics/component/run_experiment_runner.py's own
    # subprocess calls can point run_experiment.py at a synthetic registry.yaml
    # it built in a tempdir — it must never be set on the top-level CI
    # invocation of THIS preflight, or the registry actually gating CI would be
    # silently swapped for something else. Checked first, before any other
    # validation, so a mis-wired CI job fails loud instead of preflighting the
    # wrong file.
    if os.environ.get("CORTEX_EVAL_REGISTRY"):
        print("Registry preflight — evals/registry.yaml")
        print("\nERRORS (1) — a gate cannot run in CI:")
        print("  ✗ CORTEX_EVAL_REGISTRY is set in the environment — refusing: "
              "this override exists only for run_experiment_runner.py's own "
              "internal subprocess calls and must never be set on the "
              "top-level CI invocation.")
        print("\nRESULT: FAIL")
        return 1

    strict = "--strict" in argv
    reg = yaml.safe_load((HERE / "registry.yaml").read_text())

    errors: list[str] = []   # hard failures — a gate that can't run
    debt: list[str] = []     # warnings — bare-name engagement goldens (vacuous in CI)

    def check_gate(path: str, where: str) -> None:
        rp = _resolve(path)
        if not rp.exists():
            errors.append(f"{where}: golden '{path}' does not exist "
                          f"(gate would [SKIP] → vacuous PASS)")
        elif _gitignored(rp):
            errors.append(f"{where}: golden '{path}' is gitignored — absent in CI. "
                          f"Commit a fixture under evals/goldens/ or move it to monitor:")

    def check_engagement(ge: str, where: str) -> None:
        if "/" in str(ge):                       # an explicit path → must resolve
            check_gate(ge, where)
        else:                                    # a bare name → gitignored engagements/**
            debt.append(f"{where}: golden_engagement '{ge}' is a bare engagement name "
                        f"(resolves into gitignored engagements/** → vacuous in CI)")

    # --- deliverables ---------------------------------------------------------
    for name, spec in (reg.get("deliverables") or {}).items():
        for slot in ("goldens", "negatives"):
            for g in (spec.get(slot) or []):
                check_gate(g, f"deliverables.{name}.{slot}")
        # monitor: intentionally skipped (real engagements, non-gating)

    # --- components -----------------------------------------------------------
    for name, spec in (reg.get("components") or {}).items():
        if spec.get("input"):
            check_gate(spec["input"], f"components.{name}.input")
        if spec.get("golden_engagement"):
            check_engagement(spec["golden_engagement"], f"components.{name}.golden_engagement")
        # #182 D5: `code:` is the GATING declaration — a row that declares the key
        # but with nothing in it has nothing for declared_checks_all_executed to
        # require, which is a mis-wired row, not a legitimately empty one. Fail
        # this at preflight, not scoring (an empty declared set silently no-ops
        # in run_experiment.py's assertion — this catches the authoring mistake
        # before that vacuous pass can happen).
        if "code" in spec and not spec.get("code"):
            errors.append(f"components.{name}.code: declared as an empty list — "
                          f"a row must gate on at least one check")
        # #186: every declared `code:` check needs a mutation proof, or staged DEBT.
        check_mutation_coverage(name, spec, errors, debt)

    # --- pipeline -------------------------------------------------------------
    pl = reg.get("pipeline") or {}
    if pl.get("golden_engagement"):
        check_engagement(pl["golden_engagement"], "pipeline.golden_engagement")

    # --- #188 support: old `pipeline` altitude name, DEBT until #188 lands ----
    _check_pipeline_altitude_name_debt(debt)

    # --- report ---------------------------------------------------------------
    print("Registry preflight — evals/registry.yaml")
    if debt:
        print(f"\nDEBT ({len(debt)}) — non-gating, vacuous in CI, migrate incrementally:")
        for d in debt:
            print(f"  ⚠ {d}")
    if errors:
        print(f"\nERRORS ({len(errors)}) — a gate cannot run in CI:")
        for e in errors:
            print(f"  ✗ {e}")
        print("\nRESULT: FAIL")
        return 1
    if strict and debt:
        print("\nRESULT: FAIL (--strict: DEBT treated as error)")
        return 1
    print(f"\nAll gating goldens resolve and are committed."
          f"{' (' + str(len(debt)) + ' debt warning(s) above)' if debt else ''}")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
