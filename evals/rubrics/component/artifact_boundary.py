"""artifact-boundary component evaluator — executable coverage for the three
`scripts/artifact_boundary.py` gates the rest of the system depends on
(ticket #198, backlog :134).

WHY THIS ROW EXISTS
-------------------
`scripts/artifact_boundary.py` is where four gates live behind one module and
two callers (the pipeline and the standalone `/build-roi`, `/generate-roi-excel`,
`/publish` skills). Three of them are load-bearing for other components:

  cap_roi_config     the ROI reasonableness cap. `roi-financial-modeler`'s row
                     already asserts a "capped invariant" on the config, and
                     `specifics._check_overcap_negative_gated` proves the gate
                     can cap the committed over-cap golden. What NEITHER covers
                     is the gate's own failure contract — a config that does not
                     exist, or does not parse, must come back `passed: False`
                     with the reason named, never silently "fine".
  synthetic_policy   the single source of truth for synthetic-engagement
                     detection. `knowledge-harvester`'s row pins the three
                     COMMITTED fixtures (quarantine_case/, never_case/,
                     bare_tests_case/) — i.e. the happy paths plus the
                     no-marker-under-tests/ fail-safe. This row deliberately
                     covers what that one cannot: MARKER-BEATS-LOCATION (a
                     `.synthetic` file outside tests/ still governs), the
                     parent-directory walk, the two fail-safe branches for a
                     marker whose `harvest_policy:` is missing or unrecognised,
                     the plain "real" verdict, and — with a real chmod fault —
                     an unreadable marker. Complementary by construction; the
                     ticket forbids duplicating that row.
  deanonymize_dir    the EXIT gate where real client names re-enter
                     deliverables. `pii-anonymizer`'s `nested_outputs_
                     deanonymized` / `xlsx_outputs_deanonymized` (#165) cover
                     the recursive walk, the exclusions and the .xlsx branch.
                     This row covers the two REFUSAL contracts they do not: a
                     missing `.pii_mapping.json` must block AND modify nothing,
                     and a file the gate could not restore must surface in
                     `unrestored` with `client_ready: false` — never the silent
                     skip that is the defect #165's ticket was written against.

NEVER MUTATE A COMMITTED FIXTURE
--------------------------------
`cap_roi_config` REWRITES its config in place. Both ROI goldens
(`evals/goldens/roi_config_provenance.json`, capped; `roi_config_overcap.json`,
>0.60) are therefore only ever gated as a `/tmp` COPY, and the checks assert
the committed bytes are unchanged afterwards (sha256 before/after) — the
`overcap_negative_gate_witness` pattern in `rubrics/component/specifics.py`,
kept explicit here because forgetting it silently edits a golden that four
other rows score against.

THRESHOLD 1.00, NO JUDGE
------------------------
Every check is deterministic, pure Python and free. These are governance gates:
a partially correct one is a failed one.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

from rubrics._harness import bool_check, fault_injection_skip, inject_fault, run_in_tmpdir
from rubrics.base import CheckResult, repo_root

OVERCAP_GOLDEN = "roi_config_overcap.json"


def _boundary():
    """Import the SUBJECT the way its own callers do.

    `scripts/` has no `__init__.py`, and `scripts/artifact_boundary.py` is
    imported as a top-level module by `pii_anonymizer`'s rubric and by the
    skills' CLI. Resolving it through `repo_root()` is what makes the mutation
    harness able to reach it: a mutated shadow's `scripts/artifact_boundary.py`
    is picked up because the path is derived from `repo_root()`, never
    hard-coded.
    """
    scripts_dir = repo_root() / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import artifact_boundary as _ab  # noqa: PLC0415 - lazy + path-dependent on purpose
    return _ab


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _impact_values(config: dict) -> tuple[list[float], list[float]]:
    """(driver-level, scenario-level) backbase_impact values, walking exactly
    the two paths `cap_roi_config` caps. Deliberately a local walk and not a
    call into the gate: a check that asked the gate whether the gate worked
    would move with any bug in it."""
    drivers: list[float] = []
    groups = config.get("value_lever_groups", config.get("journeys", {}))
    if isinstance(groups, dict):
        for group in groups.values():
            if not isinstance(group, dict):
                continue
            for driver_type in ("revenue_drivers", "cost_drivers"):
                for driver in (group.get(driver_type) or {}).values():
                    if not isinstance(driver, dict):
                        continue
                    bi = driver.get("inputs", {}).get("backbase_impact", {})
                    val = bi.get("value") if isinstance(bi, dict) else bi
                    if isinstance(val, (int, float)):
                        drivers.append(float(val))
    scenarios: list[float] = []
    for scenario in (config.get("scenarios") or {}).values():
        if not isinstance(scenario, dict):
            continue
        for val in (scenario.get("backbase_impacts") or {}).values():
            if isinstance(val, (int, float)):
                scenarios.append(float(val))
    return drivers, scenarios


# ---------------------------------------------------------------------------
# cap_roi_config
# ---------------------------------------------------------------------------

def _cap_roi_config_caps_driver_and_scenario_impacts(
    tmp: Path, capped_golden: Path, overcap_golden: Path,
) -> CheckResult:
    """Both halves of the cap, on both committed goldens, on /tmp copies.

    1. The over-cap golden is GENUINELY over-cap before the gate runs — at
       DRIVER level (0.75) and at SCENARIO level (0.85). Asserted first: if the
       fixture were already capped, everything below would pass vacuously, and
       the gate could be deleted outright without this check noticing.
    2. Gating a COPY of it caps every value to MAX_BACKBASE_IMPACT, reports
       `modified: True`, and names both cappings in `warnings`.
    3. Gating a COPY of the CAPPED golden changes nothing (`modified: False`)
       and leaves the file byte-identical — the gate must not "fix" a config
       that was already within the cap.
    4. Both COMMITTED goldens are byte-identical afterwards. `cap_roi_config`
       writes in place; four other rows score these files.
    """
    name = "cap_roi_config_caps_driver_and_scenario_impacts"
    ab = _boundary()
    cap = ab.MAX_BACKBASE_IMPACT

    before_hashes = {p: _sha256(p) for p in (capped_golden, overcap_golden)}
    problems: list[str] = []
    evidence: list[str] = []

    pre = json.loads(overcap_golden.read_text())
    pre_drivers, pre_scenarios = _impact_values(pre)
    over_drivers = [v for v in pre_drivers if v > cap]
    over_scenarios = [v for v in pre_scenarios if v > cap]
    if not over_drivers:
        problems.append(
            f"{overcap_golden.name} has NO driver-level backbase_impact above the "
            f"{cap:.0%} cap (values: {pre_drivers}) — the negative fixture is not "
            f"negative, so the driver-level half of this check is vacuous")
    if not over_scenarios:
        problems.append(
            f"{overcap_golden.name} has NO scenario-level backbase_impact above the "
            f"{cap:.0%} cap (values: {sorted(set(pre_scenarios))}) — the scenario-level "
            f"half of this check is vacuous")
    evidence.append(f"pre-gate over-cap: drivers={over_drivers}, scenarios={sorted(set(over_scenarios))}")

    if not problems:
        copy = tmp / OVERCAP_GOLDEN
        shutil.copy(overcap_golden, copy)
        report = ab.cap_roi_config(str(copy))
        post = json.loads(copy.read_text())
        post_drivers, post_scenarios = _impact_values(post)
        still_over = [v for v in post_drivers + post_scenarios if v > cap]
        if still_over:
            problems.append(f"after the gate, {len(still_over)} value(s) still exceed "
                            f"the {cap:.0%} cap: {still_over}")
        if not report.get("modified"):
            problems.append(f"gate reported modified={report.get('modified')!r} on an "
                            f"over-cap config — it did not write the capped values back")
        warned_driver = any("backbase_impact" in w and "capped" in w for w in report.get("warnings", []))
        warned_scenario = any("Scenario" in w and "capped" in w for w in report.get("warnings", []))
        if not (warned_driver and warned_scenario):
            problems.append(
                f"gate did not warn about both cappings (driver warning={warned_driver}, "
                f"scenario warning={warned_scenario}); warnings={report.get('warnings')}")
        evidence.append(f"post-gate: drivers={post_drivers}, scenarios={sorted(set(post_scenarios))}, "
                        f"modified={report.get('modified')}")

    capped_copy = tmp / "roi_config_capped.json"
    shutil.copy(capped_golden, capped_copy)
    capped_before = _sha256(capped_copy)
    capped_report = ab.cap_roi_config(str(capped_copy))
    if capped_report.get("modified"):
        problems.append(f"gate modified the already-capped golden {capped_golden.name} "
                        f"(modified=True) — it must leave a compliant config alone")
    if _sha256(capped_copy) != capped_before:
        problems.append(f"gate rewrote the already-capped copy of {capped_golden.name} "
                        f"even though nothing needed capping")
    evidence.append(f"already-capped golden: modified={capped_report.get('modified')}, "
                    f"bytes unchanged={_sha256(capped_copy) == capped_before}")

    for path, digest in before_hashes.items():
        if _sha256(path) != digest:
            problems.append(f"COMMITTED FIXTURE MUTATED: {path} changed on disk — "
                            f"cap_roi_config must only ever be pointed at a /tmp copy")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"over-cap golden capped at {cap:.0%} at driver AND scenario level on a /tmp "
                f"copy; already-capped golden untouched; both committed goldens byte-identical"),
        evidence=(["issue: " + p for p in problems] if problems else evidence),
    )


def _cap_roi_config_missing_or_unparseable_never_passes(tmp: Path) -> CheckResult:
    """The gate's REFUSAL contract, which no other row covers.

    A config that does not exist, or does not parse, must come back with
    `passed: False` and the reason named (`exists: False` / `parse_error`), and
    must NEVER raise — `orchestrate.py` and the ROI skills call this
    unconditionally and would abort a whole run on an exception. The
    unparseable file must also be left byte-identical: a gate that could not
    read a config has no business writing one.
    """
    name = "cap_roi_config_missing_or_unparseable_never_passes"
    ab = _boundary()
    problems: list[str] = []

    missing = tmp / "does_not_exist.json"
    report = ab.cap_roi_config(str(missing))
    if report.get("exists") is not False:
        problems.append(f"missing config reported exists={report.get('exists')!r}, expected False")
    if report.get("passed"):
        problems.append("missing config reported passed=True")

    broken = tmp / "broken.json"
    broken.write_text('{"value_lever_groups": {,,, not json', encoding="utf-8")
    broken_before = _sha256(broken)
    broken_report = ab.cap_roi_config(str(broken))
    if not broken_report.get("parse_error"):
        problems.append(f"unparseable config reported parse_error="
                        f"{broken_report.get('parse_error')!r}, expected the exception type")
    if broken_report.get("passed"):
        problems.append("unparseable config reported passed=True")
    if broken_report.get("modified"):
        problems.append("unparseable config reported modified=True")
    if _sha256(broken) != broken_before:
        problems.append("the gate rewrote a config it could not parse")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"missing -> exists=False/passed=False; unparseable -> "
                f"parse_error={broken_report.get('parse_error')!r}/passed=False, bytes unchanged; "
                f"neither raised"),
    )


# ---------------------------------------------------------------------------
# synthetic_policy
# ---------------------------------------------------------------------------

def _marker(dir_path: Path, body: str) -> Path:
    dir_path.mkdir(parents=True, exist_ok=True)
    marker = dir_path / ".synthetic"
    marker.write_text(body, encoding="utf-8")
    return marker


def _synthetic_policy_marker_beats_location_and_unknown_policy_fails_safe(tmp: Path) -> CheckResult:
    """The branches `knowledge-harvester`'s row does not reach.

    That row scores the three committed fixtures — a `quarantine` marker, a
    `never` marker, and the no-marker-under-`tests/` fail-safe. Everything
    below is a DIFFERENT branch of the same function, and each one is a
    fail-safe the gate is only useful because of:

      marker beats location   a `.synthetic` marker in a directory with no
                              `tests` segment still governs (the docstring's
                              "an engagement accidentally created under
                              engagements/ stays protected").
      parent walk             a marker one level ABOVE the engagement governs it.
      no harvest_policy line  -> quarantine (fail-safe), not "real".
      unrecognised value      -> quarantine (fail-safe), not the value itself.
      no marker, not tests/   -> "real" — the negative control. Without it every
                              assertion above passes for a gate hard-wired to
                              return "quarantine".
    """
    name = "synthetic_policy_marker_beats_location_and_unknown_policy_fails_safe"
    ab = _boundary()
    problems: list[str] = []
    evidence: list[str] = []

    cases = []

    beats = tmp / "not_under_tests" / "engagement_a"
    _marker(beats, "kind: synthetic\nharvest_policy: never\n")
    cases.append(("marker beats location (never, outside tests/)", beats, "never"))

    parent = tmp / "parent_case"
    _marker(parent, "kind: synthetic\nharvest_policy: quarantine\n")
    child = parent / "2026-01_domain_assessment"
    child.mkdir(parents=True, exist_ok=True)
    cases.append(("parent-directory walk finds the marker", child, "quarantine"))

    no_policy = tmp / "no_policy_case"
    _marker(no_policy, "kind: synthetic\n(no harvest policy line at all)\n")
    cases.append(("marker with no harvest_policy -> fail-safe", no_policy, "quarantine"))

    unknown = tmp / "unknown_policy_case"
    _marker(unknown, "kind: synthetic\nharvest_policy: zzznotapolicy\n")
    cases.append(("unrecognised harvest_policy -> fail-safe", unknown, "quarantine"))

    plain = tmp / "plain_case"
    plain.mkdir(parents=True, exist_ok=True)
    cases.append(("no marker, no tests/ segment -> real (negative control)", plain, "real"))

    for label, path, expected in cases:
        try:
            policy, reason = ab.synthetic_policy(path)
        except Exception as exc:  # noqa: BLE001 - the contract is "never raises"
            problems.append(f"{label}: RAISED {type(exc).__name__}: {exc}")
            continue
        evidence.append(f"{label}: -> ({policy!r}, {reason!r})")
        if policy != expected:
            problems.append(f"{label}: got {policy!r}, expected {expected!r} ({reason})")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems
                else f"{len(cases)} branches complementary to knowledge-harvester's row all "
                     f"resolved as designed (marker-beats-location, parent walk, two fail-safes, "
                     f"and the 'real' negative control)"),
        evidence=evidence,
    )


def _synthetic_policy_unreadable_marker_fails_safe_quarantine(tmp: Path) -> CheckResult:
    """A `.synthetic` marker that EXISTS but cannot be read must fail safe to
    quarantine, and must not raise.

    The fault is real (`chmod 000` via `_harness.inject_fault`), not a mocked
    `read_text`: the branch under test is an `except OSError` around a real
    filesystem read, and a monkeypatched exception would prove only that the
    handler exists, not that the read it wraps is the one that fails. Skipped
    (never silently passed) when running as root, where chmod injects nothing.
    """
    name = "synthetic_policy_unreadable_marker_fails_safe_quarantine"
    skip = fault_injection_skip(name, perms="file")
    if skip is not None:
        return skip

    ab = _boundary()
    case = tmp / "unreadable_case"
    marker = _marker(case, "kind: synthetic\nharvest_policy: never\n")

    problems: list[str] = []
    # Control: readable, the marker's own policy governs. Without this, a gate
    # that always answered "quarantine" would pass the fault half outright.
    policy_before, reason_before = ab.synthetic_policy(case)
    if policy_before != "never":
        problems.append(f"control (readable marker) resolved {policy_before!r}, expected 'never' "
                        f"— the fault half below would not be measuring the read failure")

    with inject_fault(marker):
        try:
            policy, reason = ab.synthetic_policy(case)
        except Exception as exc:  # noqa: BLE001 - the contract is "never raises"
            policy, reason = None, f"RAISED {type(exc).__name__}: {exc}"
            problems.append(f"synthetic_policy RAISED on an unreadable marker: {reason}")
    if policy is not None and policy != "quarantine":
        problems.append(f"unreadable marker resolved {policy!r}, expected the fail-safe "
                        f"'quarantine' ({reason})")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"readable marker -> {policy_before!r}; the same marker chmod 000 -> "
                f"{policy!r} ({reason})"),
    )


# ---------------------------------------------------------------------------
# deanonymize_dir
# ---------------------------------------------------------------------------

_PLACEHOLDER_TEXT = "Prepared for [CLIENT] by the assessment team.\n"
_MAPPING = {"[CLIENT]": "Zzzplaceholder Meridian Holdings"}


def _seed_outputs(engagement: Path) -> Path:
    outputs = engagement / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    (outputs / "executive_summary.md").write_text(_PLACEHOLDER_TEXT, encoding="utf-8")
    (outputs / "assessment_report.md").write_text(_PLACEHOLDER_TEXT, encoding="utf-8")
    return outputs


def _tmp_residue(outputs: Path) -> list[str]:
    """`.tmp-deanon` staging files left behind. `_atomic_write_text` /
    `_deanonymize_xlsx` stage a same-directory temp file and `os.replace` it;
    a leftover means a partially written deliverable is sitting next to a real
    one, which is exactly what the atomic-write contract exists to prevent."""
    return sorted(p.name for p in outputs.rglob("*.tmp-deanon"))


def _deanonymize_dir_missing_mapping_blocks_and_modifies_nothing(tmp: Path) -> CheckResult:
    """No `.pii_mapping.json` -> block loudly and touch nothing.

    `pii-anonymizer`'s #165 checks all supply a mapping; this is the branch
    where there is none. The gate must report `error: missing_pii_mapping` and
    `client_ready: False`, leave every output byte-identical (a half-restored
    deliverable is worse than an unrestored one) and leave no staging residue.
    """
    name = "deanonymize_dir_missing_mapping_blocks_and_modifies_nothing"
    ab = _boundary()
    engagement = tmp / "engagement_no_mapping"
    outputs = _seed_outputs(engagement)
    before = {p: _sha256(p) for p in sorted(outputs.rglob("*")) if p.is_file()}

    report = ab.deanonymize_dir(outputs)

    problems: list[str] = []
    if report.get("client_ready"):
        problems.append("client_ready=True with no mapping file — outputs were declared "
                        "shippable while still holding placeholders")
    if report.get("error") != "missing_pii_mapping":
        problems.append(f"error={report.get('error')!r}, expected 'missing_pii_mapping'")
    if report.get("files_restored"):
        problems.append(f"files_restored={report.get('files_restored')} with no mapping file")
    changed = sorted(p.name for p, digest in before.items() if _sha256(p) != digest)
    if changed:
        problems.append(f"file(s) modified despite the missing mapping: {changed}")
    residue = _tmp_residue(outputs)
    if residue:
        problems.append(f"staging residue left behind: {residue}")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"error={report.get('error')!r}, client_ready={report.get('client_ready')}, "
                f"{len(before)} output file(s) byte-identical, no staging residue"),
    )


def _deanonymize_dir_unreadable_output_reported_unrestored_not_client_ready(tmp: Path) -> CheckResult:
    """A file the gate could not restore must be REPORTED, never skipped.

    The defect this closes (named in #165's backlog entry) is a silent skip: a
    per-file failure swallowed, `client_ready` still true, and a deliverable
    shipped with `[CLIENT]` in it. With a real `chmod 000` on one of two
    outputs the gate must (a) restore the readable one, (b) name the unreadable
    one in `unrestored`, (c) set `client_ready: False`, and (d) surface the
    re-run command. Skipped (never silently passed) when running as root.
    """
    name = "deanonymize_dir_unreadable_output_reported_unrestored_not_client_ready"
    skip = fault_injection_skip(name, perms="file")
    if skip is not None:
        return skip

    ab = _boundary()
    engagement = tmp / "engagement_fault"
    outputs = _seed_outputs(engagement)
    (engagement / ".pii_mapping.json").write_text(json.dumps(_MAPPING), encoding="utf-8")
    readable = outputs / "executive_summary.md"
    unreadable = outputs / "assessment_report.md"

    problems: list[str] = []
    with inject_fault(unreadable):
        report = ab.deanonymize_dir(outputs)
        unrestored = [Path(p).name for p in report.get("unrestored", [])]
        if unreadable.name not in unrestored:
            problems.append(f"the unreadable output is not named in unrestored={unrestored} — "
                            f"a silent skip is exactly the defect this gate exists to close")
        if report.get("client_ready"):
            problems.append("client_ready=True while a file was left unrestored")
        if report.get("files_restored") != 1:
            problems.append(f"files_restored={report.get('files_restored')}, expected 1 "
                            f"(the readable file)")

    restored_text = readable.read_text(encoding="utf-8")
    if _MAPPING["[CLIENT]"] not in restored_text:
        problems.append(f"the readable output was not restored: {restored_text!r}")
    residue = _tmp_residue(outputs)
    if residue:
        problems.append(f"staging residue left behind: {residue}")

    ok = not problems
    return CheckResult(
        name, 1.0 if ok else 0.0, ok, hard_fail=True,
        detail=("; ".join(problems) if problems else
                f"unrestored={[Path(p).name for p in report.get('unrestored', [])]}, "
                f"client_ready={report.get('client_ready')}, files_restored="
                f"{report.get('files_restored')}, readable output restored, no staging residue"),
    )


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

# The row's checks, in the order `evaluate()` runs them. CHECK_NAMES is DERIVED
# from these functions rather than restated, so the "nothing could be evaluated"
# path below can never drift out of sync with what actually runs — a divergence
# there would make `_assert_declared_checks_executed` (#182) report a missing
# check name on top of the real reason and bury it.
_CHECKS = (
    _cap_roi_config_caps_driver_and_scenario_impacts,
    _cap_roi_config_missing_or_unparseable_never_passes,
    _synthetic_policy_marker_beats_location_and_unknown_policy_fails_safe,
    _synthetic_policy_unreadable_marker_fails_safe_quarantine,
    _deanonymize_dir_missing_mapping_blocks_and_modifies_nothing,
    _deanonymize_dir_unreadable_output_reported_unrestored_not_client_ready,
)

CHECK_NAMES = tuple(fn.__name__.lstrip("_") for fn in _CHECKS)


def _all_failed(detail: str) -> list[CheckResult]:
    """Every declared check, reported as a named hard failure with one shared
    reason. Used when the row could not be evaluated AT ALL (a missing fixture,
    an unimportable subject) — reporting a single check instead would leave the
    rest 'not executed', which #182 flags as a second, less informative error."""
    return [CheckResult(n, 0.0, False, hard_fail=True, detail=detail) for n in CHECK_NAMES]


def evaluate(target: str) -> list[CheckResult]:
    """`target` is the registry row's `input:` — the CAPPED ROI golden
    (`evals/goldens/roi_config_provenance.json`). The over-cap golden is
    resolved as its SIBLING rather than from `repo_root()`, so that the
    mutation harness's `shadow_target()` remapping carries both fixtures into
    the shadow together and a `kind: fixture` mutation on either is reachable.
    """
    capped_golden = Path(target)
    if not capped_golden.is_file():
        return _all_failed(f"registry input not found: {capped_golden} — this row's checks "
                           f"need the capped ROI golden; nothing was evaluated")
    overcap_golden = capped_golden.parent / OVERCAP_GOLDEN
    if not overcap_golden.is_file():
        return _all_failed(f"negative fixture not found: {overcap_golden} (expected as a sibling "
                           f"of {capped_golden.name}) — nothing was evaluated")
    try:
        _boundary()
    except Exception as exc:  # noqa: BLE001 - report, never crash the suite
        return _all_failed(f"could not import scripts/artifact_boundary.py "
                           f"({type(exc).__name__}: {exc}) — nothing was evaluated")

    return [
        run_in_tmpdir(_cap_roi_config_caps_driver_and_scenario_impacts,
                      capped_golden, overcap_golden, prefix="cortex_eval_ab_cap_"),
        run_in_tmpdir(_cap_roi_config_missing_or_unparseable_never_passes,
                      prefix="cortex_eval_ab_capfail_"),
        run_in_tmpdir(_synthetic_policy_marker_beats_location_and_unknown_policy_fails_safe,
                      prefix="cortex_eval_ab_synth_"),
        run_in_tmpdir(_synthetic_policy_unreadable_marker_fails_safe_quarantine,
                      prefix="cortex_eval_ab_synthfault_"),
        run_in_tmpdir(_deanonymize_dir_missing_mapping_blocks_and_modifies_nothing,
                      prefix="cortex_eval_ab_deanon_"),
        run_in_tmpdir(_deanonymize_dir_unreadable_output_reported_unrestored_not_client_ready,
                      prefix="cortex_eval_ab_deanonfault_"),
    ]
