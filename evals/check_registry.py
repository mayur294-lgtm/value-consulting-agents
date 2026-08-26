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
    python3 evals/check_registry.py            # exit 1 on any hard error
    python3 evals/check_registry.py --strict    # also fail on DEBT warnings
    python3 evals/check_registry.py --verbose   # full per-check DEBT detail (default
                                                 # rendering aggregates to one line per row)
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
    "mutation-harness",        # #187 — the harness proving itself; hard-enforced from birth
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


def check_mutation_coverage(name: str, spec: dict, errors: list[str],
                             mutation_debt_rows: dict[str, dict]) -> None:
    """Preflight enforcement of the mutation proof (#186): every check name
    in a row's `code:` list must resolve to a `mutations:`/dict-`negatives:`
    entry that would actually prove it — a check with no mutation entry
    certifies nothing. See the MUTATIONS_ENFORCED_FOR_ALL_ROWS staging note
    above for why an uncovered row is DEBT today rather than a hard error.

    Non-fatal (DEBT) findings are NOT appended to a flat message list —
    they're grouped into `mutation_debt_rows[name] = {"total": <len(code_names)>,
    "missing": [check, ...], "messages": [full per-check message, ...]}` so
    the caller can render one aggregated line per row by default (#186
    follow-up: a 90-line wall of near-identical per-check DEBT lines is the
    exact failure mode this preflight exists to prevent trained reviewers
    from learning to scroll past) while still keeping full per-check detail
    available behind `--verbose`.
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
    row_debt = mutation_debt_rows.setdefault(
        name, {"total": len(code_names), "missing": [], "messages": []})
    for check in missing:
        msg = (f"components.{name}.code: check `{check}` has no `mutations:` entry — "
               f"a gate that cannot fail certifies nothing. Fix: add a `mutations:` entry "
               f"for `{check}` (see components.run-experiment-runner.mutations for the shape) "
               f"or a dict-form `negatives: {{{check}: {{strip: ...}}}}`.")
        if hard:
            errors.append(msg)
        else:
            row_debt["missing"].append(check)
            row_debt["messages"].append(
                msg + " Non-fatal DEBT until migrated (row declares no `mutations:` "
                "key at all yet) — tracked in .prd/backlog.md (eval-gate-v7 epic); "
                "flip MUTATIONS_ENFORCED_FOR_ALL_ROWS above once every row is covered.")
    if not row_debt["missing"]:
        del mutation_debt_rows[name]


# --- #188: the retired altitude name is now a HARD ERROR ---------------------
# Sentinels around the one deliberate in-tree use of the retired name (the
# rename error text in run_experiment.py). Lines between them are not counted.
#
# HARDENING (#188 correction pass). As first shipped this skip was a bare
# substring test applied to every line of every in-scope file, with no pairing
# and no width bound. The review demonstrated the exploit end-to-end: paste the
# two magic strings into `registry.yaml` as YAML comments, put a real
# reintroduction between them (`altitude: pipeline` AND
# `evaluator: rubrics.pipeline.contracts`), and preflight returned exit 0 PASS.
# The skip is now:
#   • anchored   — honoured ONLY in `evals/run_experiment.py`; in every other
#                  in-scope file the sentinel strings are ordinary text and the
#                  line is scanned like any other,
#   • bounded    — at most `_OLD_NAME_SKIP_MAX_LINES` lines after the open; past
#                  that the region is reported and scanning RESUMES, so a
#                  widened fence cannot swallow the rest of the file,
#   • paired     — at most one region per file, an open with no close in the
#                  same file is an error, and a stray close is an error.
_OLD_NAME_SKIP_OPEN = "BEGIN old-altitude error text"
_OLD_NAME_SKIP_CLOSE = "END old-altitude error text"
# The ONE file whose sentinels are honoured. Anywhere else they are just text.
_OLD_NAME_SKIP_FILE = "evals/run_experiment.py"
# The real region is ~15 lines (the comment + `_RETIRED_ALTITUDE` + the error
# string). The cap leaves headroom for editing the rationale and no more.
_OLD_NAME_SKIP_MAX_LINES = 25

# Files this assertion scans: the registry, the runner, the runtime scorer, both
# CI workflows, and the human-facing docs that told people to run the flag.
_OLD_NAME_SCOPE = (
    "evals/registry.yaml",
    "evals/run_experiment.py",
    "evals/runtime.py",
    "evals/README.md",
    "evals/rubrics/base.py",
    ".github/workflows/evals.yml",
    ".github/workflows/version-release.yml",
    "CLAUDE.md",
    ".claude/skills/bb-build/SKILL.md",
    ".claude/skills/bb-build/prompts/implementer-prompt.md",
    ".claude/skills/bb-build/formats/pr-format.md",
    ".claude/skills/bb-tickets/SKILL.md",
    ".claude/skills/bb-tickets/formats/ticket-format.md",
    ".claude/skills/bb-refine/SKILL.md",
    ".claude/skills/bb-prd/SKILL.md",
    ".claude/skills/bb-prd/formats/prd-format.md",
    # Live in-tree doc that renders a table of the CURRENT check-sets — not a
    # historical PRD. It carried `pipeline contracts` past the #188 rename
    # (review finding 1: acceptance criterion 3 said 0 in-tree occurrences, and
    # only this list's omission hid the violation).
    "docs/EVAL_SYSTEM_REVIEW.html",
)

# THE MATCHING RULE. The bare word "pipeline" is a legitimate, load-bearing term
# in this repo: `scripts/orchestrate.py` really is a pipeline that really runs
# agents, `pipeline_engagement/` is a real fixture directory of a real pipeline
# run's outputs, and `.pipeline_run_report.json` really is a pipeline run report.
# An over-broad `\bpipeline\b` grep (what this assertion used while it was DEBT)
# would force those honest names to be renamed too, which is actively harmful.
# So each pattern below matches the ALTITUDE NAME in a syntactic position where
# it can only mean the altitude:
#
#   1. the CLI flag                       `--altitude pipeline`, `--altitude=pipeline`
#   2. a field/kwarg assignment           `altitude: pipeline`, `altitude="pipeline"`
#   3. an equality test                   `altitude == "pipeline"`
#   4. the prose form                     "the pipeline altitude", "`pipeline`-altitude"
#   5. the evaluator package              `rubrics.pipeline`, `rubrics/pipeline`
#   6. the registry section key           a line that is exactly `pipeline:`
#   7. a registry/report dict key         `["pipeline"]`, `.get("pipeline"`
#   8. a score/label name                 `name="pipeline"`
#   9. the check-set label                "pipeline contracts"
#  10. ANY bare quoted literal            `"pipeline"` / `'pipeline'`
#
# Pattern 10 is the #188 correction pass, and it is the load-bearing one. The
# review wrote 35 must-match forms against patterns 1-9 and TWELVE escaped —
# including a straight revert of #188's own diff:
#
#     choices=["unit", "pipeline", "deliverable"]
#
# Patterns 1-9 all key off a nearby token (`--altitude`, `altitude`, `rubrics.`,
# `name=`, a `[`), so renaming the surrounding variable or moving the literal
# into a collection walked straight through them. The review then proved the
# consequence: delete the runner's guard, add `"pipeline"` back to `_ALTITUDES`,
# make dispatch accept both — preflight exit 0 PASS and `--altitude pipeline`
# green again. A complete alias resurrection, invisible to the gate.
#
# Matching the bare quoted literal in ANY position closes `choices=[...]`,
# `frozenset({...})`, `in ("pipeline", ...)`, an alias dict `{"pipeline": ...}`
# (the alias design-D4 forbids outright), `default="pipeline"`, `alt = "pipeline"`
# and `getattr(args,'altitude')=='pipeline'` in one stroke, and it does not care
# what the variable is called. Patterns 1-9 are kept because they produce a
# far better error message for the form they name, and because several of them
# (the CLI flag, the prose form, the `pipeline:` section key, "pipeline
# contracts") match UNQUOTED text that 10 never sees.
#
# The whole set is matched case-insensitively, so `ALTITUDE: PIPELINE` in a
# workflow or a doc cannot walk past pattern 2.
#
# Deliberately NOT matched: `pipeline_engagement`, `.pipeline_run_report.json`,
# `pipeline_run_report/eval/v2` (an underscore is a word character, so `\bpipeline\b`
# does not fire inside them), and any sentence that merely says the altitude does
# not run the pipeline — that sentence is the point of the rename and must stay
# writable, so prose names the retired flag in BACKTICKS (`pipeline`), which
# pattern 10 does not match. False-positive containment for 10 is the scope list
# above: the honest quoted uses in the repo — `tests/fixtures/
# mode_composer_selftest.py`'s `modes.get("pipeline")`, and everything under
# `evals/goldens/pipeline_engagement/` — are not in it. The one in-scope
# collision found when 10 was added was a rationale comment in `evals/runtime.py`
# that quoted the retired name with straight quotes; it now uses backticks like
# the rest of the prose.
_OLD_ALTITUDE_NAME_PATTERNS = (
    (r"--altitude[=\s]+[\"\']?pipeline\b",                  "CLI flag `--altitude pipeline`"),
    (r"\baltitude\s*[:=]\s*[\"\']?pipeline\b",              "`altitude: pipeline` field/kwarg"),
    (r"\baltitude\s*==\s*[\"\']pipeline[\"\']",             "`altitude == \"pipeline\"` comparison"),
    (r"[`\"\']?\bpipeline\b[`\"\']?[-\s]+altitude\b",       "the prose form \"pipeline altitude\""),
    (r"\brubrics[./]pipeline\b",                            "evaluator package `rubrics.pipeline`"),
    (r"^\s*pipeline:\s*(#.*)?$",                            "registry section key `pipeline:`"),
    (r"\[[\"\']pipeline[\"\']\]|\.get\(\s*[\"\']pipeline[\"\']",  "dict key `[\"pipeline\"]`"),
    (r"\bname\s*=\s*[\"\']pipeline[\"\']",                  "score/label `name=\"pipeline\"`"),
    (r"\bpipeline contracts\b",                             "check-set label \"pipeline contracts\""),
    (r"[\"\']pipeline[\"\']",
     "a bare quoted literal `\"pipeline\"` — a `choices=`/`frozenset`/`in (...)` "
     "member, an alias-dict key, a `default=`, or any renamed variable holding "
     "the retired altitude name"),
)


def _check_old_altitude_name(errors: list[str]) -> None:
    r"""Grep assertion (#186, flipped to a hard error by #188): the retired
    `pipeline` altitude name must not survive anywhere it could be run or
    believed.

    #186 introduced this as DEBT with an over-broad `\bpipeline\b` count (32
    occurrences over 5 files), on the explicit instruction that #188 flip it to
    a hard error at 0 occurrences once the rename shipped. #188 shipped, so this
    now appends to `errors`. It also narrows the match: see
    `_OLD_ALTITUDE_NAME_PATTERNS` above for the rule and for why counting every
    use of the word "pipeline" would have been the wrong assertion.

    Exactly one occurrence is allowed in-tree: the rename error text in
    `run_experiment.py`, which must quote the old flag verbatim to be useful.
    It is fenced by the `_OLD_NAME_SKIP_*` sentinels and skipped here — but only
    in `run_experiment.py` itself, bounded to `_OLD_NAME_SKIP_MAX_LINES`, and at
    most once per file; see the sentinel constants above for the exploit that
    hardening closes. This file itself is not in scope — it holds the patterns,
    so it cannot scan for a token it must contain.
    """
    compiled = [(re.compile(pat, re.IGNORECASE), why)
                for pat, why in _OLD_ALTITUDE_NAME_PATTERNS]
    for rel in _OLD_NAME_SCOPE:
        f = ROOT / rel
        if not f.is_file():
            continue
        # Sentinels are honoured in exactly one file. Everywhere else they are
        # ordinary text and the lines around them are scanned normally.
        honour_sentinels = rel == _OLD_NAME_SKIP_FILE
        skip_open_line = 0      # 0 == no region currently open
        regions_seen = 0
        width_reported = False
        for lineno, line in enumerate(
                f.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if honour_sentinels and _OLD_NAME_SKIP_OPEN in line:
                if skip_open_line:
                    errors.append(
                        f"{rel}:{lineno}: a second `{_OLD_NAME_SKIP_OPEN}` sentinel opened "
                        f"while the region at line {skip_open_line} was still open. "
                        f"The skip fences ONE region; nesting it is how a fence gets widened "
                        f"until it hides a reintroduction.")
                else:
                    regions_seen += 1
                    if regions_seen > 1:
                        errors.append(
                            f"{rel}:{lineno}: a second `{_OLD_NAME_SKIP_OPEN}` region in this "
                            f"file. Exactly one region is permitted — the rename error text.")
                    skip_open_line = lineno
                    width_reported = False
                continue
            if honour_sentinels and _OLD_NAME_SKIP_CLOSE in line:
                if not skip_open_line:
                    errors.append(
                        f"{rel}:{lineno}: `{_OLD_NAME_SKIP_CLOSE}` with no matching "
                        f"`{_OLD_NAME_SKIP_OPEN}` above it.")
                skip_open_line = 0
                continue
            if skip_open_line:
                if lineno - skip_open_line <= _OLD_NAME_SKIP_MAX_LINES:
                    continue
                # Over the cap: report once, then RESUME scanning. A fence that
                # is never closed must not silently swallow the rest of the file.
                if not width_reported:
                    errors.append(
                        f"{rel}:{skip_open_line}: the `{_OLD_NAME_SKIP_OPEN}` region runs past "
                        f"{_OLD_NAME_SKIP_MAX_LINES} lines without a "
                        f"`{_OLD_NAME_SKIP_CLOSE}`. Scanning resumed at line {lineno} — the "
                        f"region fences the rename error text only, not an open-ended block.")
                    width_reported = True
            for rx, why in compiled:
                if rx.search(line):
                    errors.append(
                        f"{rel}:{lineno}: the retired `pipeline` altitude name survives "
                        f"({why}). It was renamed to `deliverable-structural` in #188 "
                        f"because a 5-second fixture scan reading `pipeline` was cited as "
                        f"integration evidence. Fix: use `deliverable-structural` "
                        f"(CLI/label) or `deliverable_structural` (registry/report key). "
                        f"The only permitted occurrence is the rename error text in "
                        f"run_experiment.py, fenced by the "
                        f"`{_OLD_NAME_SKIP_OPEN}` / `{_OLD_NAME_SKIP_CLOSE}` sentinels "
                        f"in {_OLD_NAME_SKIP_FILE} (those sentinels are inert in every "
                        f"other file)."
                    )
                    break
        if skip_open_line:
            errors.append(
                f"{rel}:{skip_open_line}: `{_OLD_NAME_SKIP_OPEN}` is never closed by a "
                f"`{_OLD_NAME_SKIP_CLOSE}` in this file. An unclosed fence would exempt "
                f"everything below it.")


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
    verbose = "--verbose" in argv or "-v" in argv
    reg = yaml.safe_load((HERE / "registry.yaml").read_text())

    errors: list[str] = []   # hard failures — a gate that can't run
    debt: list[str] = []     # warnings — bare-name engagement goldens
    # Per-row mutation-coverage DEBT (#186 follow-up): name -> {total, missing, messages}.
    # Kept separate from `debt` above so the default report can aggregate it to one
    # line per row instead of one line per check (see check_mutation_coverage's docstring).
    mutation_debt_rows: dict[str, dict] = {}

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
        check_mutation_coverage(name, spec, errors, mutation_debt_rows)

    # --- deliverable-structural -----------------------------------------------
    ds = reg.get("deliverable_structural") or {}
    if ds.get("golden_engagement"):
        check_engagement(ds["golden_engagement"], "deliverable_structural.golden_engagement")

    # --- #188: the retired altitude name is a HARD ERROR (0 occurrences) ------
    _check_old_altitude_name(errors)

    # --- report ---------------------------------------------------------------
    # #186 follow-up (spec review): the mutation-coverage DEBT used to print one
    # line per missing check — 90 near-identical lines across 16 rows, exactly
    # the wall-of-warnings failure mode this preflight exists to stop reviewers
    # from learning to scroll past. Default rendering now leads with a
    # PROMINENT TOTAL, then one aggregated line per row; full per-check detail
    # is still available behind --verbose for whoever is doing the migration.
    mutation_debt_count = sum(len(r["missing"]) for r in mutation_debt_rows.values())
    total_debt = len(debt) + mutation_debt_count

    print("Registry preflight — evals/registry.yaml")
    if total_debt:
        mutation_summary = (f" ({mutation_debt_count} uncovered check(s) across "
                             f"{len(mutation_debt_rows)} row(s))" if mutation_debt_rows else "")
        print(f"\nDEBT: {total_debt} warning(s){mutation_summary} — non-gating, vacuous in CI, "
              f"migrate incrementally"
              f"{'' if verbose else ' (pass --verbose for full per-check detail)'}:")
        if verbose:
            for row in mutation_debt_rows.values():
                for msg in row["messages"]:
                    print(f"  ⚠ {msg}")
        else:
            for name, row in mutation_debt_rows.items():
                print(f"  ⚠ {name}: {len(row['missing'])}/{row['total']} code checks "
                      f"uncovered — no mutation entries")
        for d in debt:
            print(f"  ⚠ {d}")
    if errors:
        print(f"\nERRORS ({len(errors)}) — a gate cannot run in CI:")
        for e in errors:
            print(f"  ✗ {e}")
        print("\nRESULT: FAIL")
        return 1
    if strict and total_debt:
        print("\nRESULT: FAIL (--strict: DEBT treated as error)")
        return 1
    print("\nAll gating goldens resolve and are committed."
          + (f" (see {total_debt} DEBT warning(s) above)" if total_debt else ""))
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
