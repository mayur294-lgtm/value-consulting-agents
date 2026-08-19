"""proposal-loop component evaluator (objective, code-only — no LLM).

The round-N negotiation loop has no runnable binary: it is a command
(`.claude/commands/proposal-builder.md` ACT 1 "round N") driving two artifacts —
the machine round record `INTERNAL_deal_state.json` and the human deal-notes
entry `/deal-notes` produces. What a gate CAN check deterministically is the
CONTRACT between them: the loop can only re-plan a round if the state carries the
fields it re-plans from, and only pick up what happened if the notes carry the
signals in a detectable shape. That contract is what this evaluator scores,
against the two committed fixtures:

  deal_state_parses                  the round record is valid JSON.
  rounds_schema_present              every entry in rounds[] carries the keys the next round
                                     reads: n, date, inputs_hash, scenarios_shown,
                                     ladder_position, concessions{given,extracted},
                                     meeting_note_refs, open_levers_snapshot, strategy_summary.
                                     inputs_hash + strategy_summary are what let round N quote
                                     the agreed strategy instead of paraphrasing it.
  current_block_schema               current{round, next_planned_stage, elasticity_exposure} —
                                     where the ladder was left and what the sliders may expose.
  pending_meeting_notes_stub_shape   pending_meeting_notes[] stubs carry date + meeting_ref +
                                     headline, so /deal-notes can push a meeting into the loop
                                     without the strategy run re-reading a transcript.
  open_levers_snapshot_per_lever     the snapshot is ONE ENTRY PER LEVER
                                     ("Family N (Name): Lever"), not a per-family grouping —
                                     reserve is counted in levers, so a round-over-round diff
                                     shows exactly which lever got spent.
  state_notes_cross_reference        the pending stub's meeting_ref anchor resolves into the
                                     notes file — the two artifacts are cross-referenced, never
                                     duplicated (design-v5 decision).
  meeting_notes_schema_headings      the notes carry the deal-notes schema headings (state of
                                     play, what was covered, key exchanges, action items,
                                     strategic reads, next milestones).
  meeting_notes_telemetry_block      TELEMETRY_START/END block naming the agent — the
                                     auditability protocol every component inherits.
  planted_signals_detectable         the three planted round-2 signals are machine-detectable
                                     in the notes: the discount ask, the readiness slip, and the
                                     revised volumes. These are what a round-2 re-plan must pick
                                     up; if a rewrite of the fixture buries them in prose, this
                                     check fails and the loop cases stop meaning anything.

target: path to the deal-state JSON golden. The paired notes fixture is loaded by
name (same pattern as rubrics.component.roi_excel_generator's second fixture —
the components altitude wires only one `input:` slot).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from rubrics.base import CheckResult, repo_root

_NOTES_GOLDEN = "evals/goldens/meeting_notes_golden.md"

_ROUND_KEYS = ("n", "date", "inputs_hash", "scenarios_shown", "ladder_position",
               "concessions", "meeting_note_refs", "open_levers_snapshot", "strategy_summary")
_CURRENT_KEYS = ("round", "next_planned_stage", "elasticity_exposure")
_STUB_KEYS = ("date", "meeting_ref", "headline")

_NOTES_HEADINGS = {
    "state of play": r"^##\s+.*state of play",
    "what was covered": r"^##\s+what was covered",
    "key exchanges": r"^##\s+key exchanges",
    "action items": r"^##\s+action items",
    "strategic reads": r"^##\s+strategic reads",
    "next milestones": r"^##\s+next milestones",
}

# The three signals planted in the notes fixture, each detectable without an LLM.
_SIGNALS = {
    "discount_ask": r"\b\d{1,2}\s?%\s?(off|discount)|asking for \d{1,2}\s?%|\b\d{1,2}% off\b",
    "readiness_slip": r"slipp?ed\s+two\s+quarters|Q1\s*2027.{0,40}Q3\s*2027|readiness.{0,60}slip",
    "volume_revision": r"150,?000\s*(?:→|->|to)\s*185,?000|up\s+from\s+(?:the\s+)?150,?000|"
                       r"revised\s+(?:active-user\s+)?volumes?\s+up",
}


def _bool(name: str, ok: bool, *, hard_fail: bool = False, detail: str = "",
          evidence: list[str] | None = None) -> CheckResult:
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=hard_fail,
                       detail=detail, evidence=evidence or [])


def _notes_text() -> tuple[str, str]:
    p = repo_root() / _NOTES_GOLDEN
    if not p.exists():
        return "", f"notes fixture missing: {_NOTES_GOLDEN}"
    return p.read_text(errors="replace"), ""


# ── checks ──────────────────────────────────────────────────────────────────

def _check_rounds(state: dict) -> CheckResult:
    rounds = state.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        return _bool("rounds_schema_present", False, detail="rounds[] missing or empty")
    problems = []
    for r in rounds:
        n = r.get("n", "?")
        for k in _ROUND_KEYS:
            if k not in r:
                problems.append(f"round {n}: missing '{k}'")
        conc = r.get("concessions")
        if isinstance(conc, dict):
            for k in ("given", "extracted"):
                if not isinstance(conc.get(k), list):
                    problems.append(f"round {n}: concessions.{k} is not a list")
        else:
            problems.append(f"round {n}: concessions block missing")
        if not str(r.get("strategy_summary", "")).strip():
            problems.append(f"round {n}: empty strategy_summary (round N+1 has nothing to quote)")
    return _bool("rounds_schema_present", not problems,
                 detail=f"{len(rounds)} round(s), all required keys present" if not problems
                 else f"{len(problems)} schema problem(s)", evidence=problems[:6])


def _check_current(state: dict) -> CheckResult:
    cur = state.get("current")
    if not isinstance(cur, dict):
        return _bool("current_block_schema", False, detail="current{} missing")
    missing = [k for k in _CURRENT_KEYS if k not in cur]
    return _bool("current_block_schema", not missing,
                 detail=(f"round {cur.get('round')} → next stage '{cur.get('next_planned_stage')}', "
                         f"elasticity '{cur.get('elasticity_exposure')}'" if not missing
                         else f"missing: {missing}"))


def _check_stubs(state: dict) -> CheckResult:
    stubs = state.get("pending_meeting_notes")
    if not isinstance(stubs, list):
        return _bool("pending_meeting_notes_stub_shape", False,
                     detail="pending_meeting_notes[] missing (the /deal-notes handoff)")
    problems = [f"stub {i}: missing '{k}'"
                for i, s in enumerate(stubs) for k in _STUB_KEYS if k not in s]
    ok = bool(stubs) and not problems
    return _bool("pending_meeting_notes_stub_shape", ok,
                 detail=f"{len(stubs)} stub(s) with date+meeting_ref+headline" if ok
                 else (problems[0] if problems else "no pending stub to exercise the shape"),
                 evidence=problems[:5])


def _check_open_levers(state: dict) -> CheckResult:
    entries = [e for r in state.get("rounds", []) for e in (r.get("open_levers_snapshot") or [])]
    if not entries:
        return _bool("open_levers_snapshot_per_lever", False, detail="no open_levers_snapshot entries")
    bad = []
    for e in entries:
        m = re.match(r"^Family\s+\d+\s+\([^)]+\):\s*(.+)$", str(e).strip())
        if not m:
            bad.append(f"malformed: {e!r}")
        elif "," in m.group(1):
            bad.append(f"grouped, not one lever per entry: {e!r}")
    return _bool("open_levers_snapshot_per_lever", not bad,
                 detail=f"{len(entries)} entries, one lever each" if not bad
                 else f"{len(bad)} malformed/grouped entry(ies)", evidence=bad[:5])


def _check_cross_reference(state: dict, notes: str) -> CheckResult:
    stubs = state.get("pending_meeting_notes") or []
    refs = [s.get("meeting_ref", "") for s in stubs if s.get("meeting_ref")]
    if not refs:
        return _bool("state_notes_cross_reference", False, detail="no meeting_ref to resolve")
    unresolved = []
    for ref in refs:
        anchor = ref.split("#", 1)[1] if "#" in ref else ""
        if not anchor or anchor not in notes:
            unresolved.append(ref)
    return _bool("state_notes_cross_reference", not unresolved,
                 detail=f"{len(refs)} meeting_ref anchor(s) resolve into the notes fixture"
                 if not unresolved else f"unresolved: {unresolved}", evidence=unresolved[:3])


def _check_headings(notes: str) -> CheckResult:
    missing = [name for name, pat in _NOTES_HEADINGS.items()
               if not re.search(pat, notes, re.I | re.M)]
    return _bool("meeting_notes_schema_headings", not missing,
                 detail=f"all {len(_NOTES_HEADINGS)} deal-notes schema headings present"
                 if not missing else f"missing heading(s): {missing}")


def _check_telemetry(notes: str) -> CheckResult:
    block = re.search(r"<!--\s*TELEMETRY_START\s*-->(.*?)<!--\s*TELEMETRY_END\s*-->", notes, re.S)
    ok = bool(block) and bool(re.search(r"^agent:\s*\S+", block.group(1), re.M))
    return _bool("meeting_notes_telemetry_block", ok,
                 detail="telemetry block present with an agent: line" if ok
                 else "no TELEMETRY_START/END block naming the agent")


def _check_signals(notes: str) -> CheckResult:
    found = {k: bool(re.search(p, notes, re.I)) for k, p in _SIGNALS.items()}
    hit = sum(found.values())
    return CheckResult("planted_signals_detectable", hit / len(_SIGNALS), hit == len(_SIGNALS),
                       detail=f"{hit}/{len(_SIGNALS)} round-2 signals detectable",
                       evidence=[f"{k}: {'found' if v else 'NOT FOUND'}" for k, v in found.items()])


def evaluate(target: str) -> list[CheckResult]:
    """target: path to the deal-state JSON golden."""
    p = Path(target)
    if not p.exists():
        return [CheckResult("deal_state_parses", 0.0, False, hard_fail=True,
                            detail=f"fixture not found: {target}")]
    try:
        state = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return [CheckResult("deal_state_parses", 0.0, False, hard_fail=True,
                            detail=f"invalid JSON: {e}")]
    notes, notes_err = _notes_text()
    checks = [_bool("deal_state_parses", True, detail=f"{len(state.get('rounds', []))} round(s) recorded"),
              _check_rounds(state), _check_current(state), _check_stubs(state),
              _check_open_levers(state)]
    if notes_err:
        checks += [_bool(name, False, detail=notes_err) for name in
                   ("state_notes_cross_reference", "meeting_notes_schema_headings",
                    "meeting_notes_telemetry_block", "planted_signals_detectable")]
    else:
        checks += [_check_cross_reference(state, notes), _check_headings(notes),
                   _check_telemetry(notes), _check_signals(notes)]
    return checks
