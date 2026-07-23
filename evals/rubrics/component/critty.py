"""critty component evaluator (objective, code-only — no LLM).

Verifies `.claude/commands/critty.md` (the /critty skill, ticket #94) is
structurally complete as the escalation form of the always-on Critical
Thought Partner protocol (tickets #93/#94): it force-loads the full protocol
(with a named fallback when the file is absent), scopes and aligns on the
target before critiquing, runs all five CTP functions in "hunt mode" rather
than waiting for a trigger, splits proactive provenance into what it CAN
challenge vs. what it CAN'T verify without source data, emits a
challenge-register table with the five documented fields, flags where a
genuinely independent check would bite harder (Step 7), and states what
/critty deliberately does NOT do.

target: `.claude/commands/critty.md` path OR raw text (see `_read`).
"""
from __future__ import annotations

import re
from pathlib import Path

from rubrics.base import CheckResult


def _read(x: str) -> str:
    try:
        p = Path(x)
        return p.read_text(errors="replace") if p.exists() else x
    except (OSError, ValueError):
        return x


def _present(pattern: str, text: str, flags: int = re.I) -> bool:
    return bool(re.search(pattern, text, flags))


def _bool_check(name: str, ok: bool, *, hard_fail: bool = False, soft_floor: float = 0.0,
               detail: str = "") -> CheckResult:
    return CheckResult(name, 1.0 if ok else soft_floor, ok, hard_fail=hard_fail, detail=detail)


def _ratio_present(name: str, patterns: list[str], text: str, *, hard_fail: bool = False) -> CheckResult:
    found = [p for p in patterns if _present(p, text)]
    ok = len(found) == len(patterns)
    score = len(found) / len(patterns)
    return CheckResult(name, score, ok, hard_fail=hard_fail,
                       detail=f"{len(found)}/{len(patterns)} present: {found}")


def _check_frontmatter_valid(text: str) -> CheckResult:
    fm = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not fm:
        return _bool_check("frontmatter_valid", False, hard_fail=True,
                           detail="no YAML frontmatter block found at top of file")
    block = fm.group(1)
    has_name = _present(r"^name:\s*critty\s*$", block, re.I | re.M)
    has_desc = _present(r"^description:\s*\S", block, re.I | re.M)
    ok = has_name and has_desc
    return _bool_check("frontmatter_valid", ok, hard_fail=True,
                       detail=f"name: critty present={has_name}, description present={has_desc}")


def _check_protocol_load_step(text: str) -> CheckResult:
    references_file = _present(r"critical_thought_partner_protocol\.md", text)
    reads_in_full = _present(r"\bin full\b", text)
    ok = references_file and reads_in_full
    return _bool_check("protocol_load_step", ok, hard_fail=True,
                       detail="references critical_thought_partner_protocol.md and loads it 'in full'" if ok
                       else f"references_file={references_file}, reads_in_full={reads_in_full} "
                            "(missing explicit full-protocol load step)")


def _check_fallback_when_absent(text: str) -> CheckResult:
    ok = _present(r"does not exist", text) and _present(r"fallback", text)
    return _bool_check("fallback_when_absent", ok,
                       detail="fallback-to-CLAUDE.md-summary path present for a missing protocol file" if ok
                       else "no fallback described for when the protocol file is absent")


def _check_scope_target_step(text: str) -> CheckResult:
    ok = _present(r"Scope the pressure-test", text)
    return _bool_check("scope_target_step", ok,
                       detail="'Scope the pressure-test' step present" if ok else "no target-scoping step found")


def _check_align_before_critique_step(text: str) -> CheckResult:
    ok = _present(r"Align before critiquing", text)
    return _bool_check("align_before_critique_step", ok,
                       detail="'Align before critiquing' step present" if ok else "no pre-critique alignment step found")


_FIVE_FUNCTIONS = [
    r"Problem definition",
    r"Context completeness",
    r"Input examination",
    r"Direction maintenance",
    r"Correction metabolism",
]


def _check_five_functions_hunt(text: str) -> CheckResult:
    return _ratio_present("five_functions_hunt", _FIVE_FUNCTIONS, text)


def _check_proactive_provenance_split(text: str) -> CheckResult:
    can_challenge = _present(r"I can challenge this", text)
    cant_verify = _present(r"I can.t verify this without source data", text)
    ok = can_challenge and cant_verify
    score = (int(can_challenge) + int(cant_verify)) / 2
    return CheckResult("proactive_provenance_split", score, ok,
                       detail=f"\"I can challenge this\"={can_challenge}, "
                              f"\"I can't verify this without source data\"={cant_verify}")


_REGISTER_FIELDS = [
    r"\bIssue\b",
    r"Function\s*/\s*trigger",
    r"\bConfidence\b",
    r"Why it matters",
    r"What would resolve it",
]


def _check_challenge_register_table(text: str) -> CheckResult:
    return _ratio_present("challenge_register_table", _REGISTER_FIELDS, text)


def _check_independence_flag(text: str) -> CheckResult:
    ok = _present(r"Step 7", text) and _present(r"independen", text)
    return _bool_check("independence_flag", ok,
                       detail="Step 7 independence flag present" if ok
                       else "no Step 7 (or no independence framing) found")


def _check_not_do_section(text: str) -> CheckResult:
    ok = _present(r"does NOT do", text)
    return _bool_check("not_do_section", ok,
                       detail="'What /critty does NOT do' section present" if ok
                       else "no explicit 'does NOT do' section found")


CHECKS = {
    "frontmatter_valid": _check_frontmatter_valid,
    "protocol_load_step": _check_protocol_load_step,
    "fallback_when_absent": _check_fallback_when_absent,
    "scope_target_step": _check_scope_target_step,
    "align_before_critique_step": _check_align_before_critique_step,
    "five_functions_hunt": _check_five_functions_hunt,
    "proactive_provenance_split": _check_proactive_provenance_split,
    "challenge_register_table": _check_challenge_register_table,
    "independence_flag": _check_independence_flag,
    "not_do_section": _check_not_do_section,
}


def evaluate(target: str) -> list[CheckResult]:
    """target: `.claude/commands/critty.md` path or raw text. Runs all
    registered structural checks against it (deterministic, no LLM judge)."""
    text = _read(target)
    return [fn(text) for fn in CHECKS.values()]
