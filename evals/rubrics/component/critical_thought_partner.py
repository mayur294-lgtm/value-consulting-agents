"""critical-thought-partner component evaluator (objective, code-only — no LLM).

Verifies TWO things at once — mirroring the sibling rubric.component.critty
in structure but split across two sources:

  1. The STANDARD file itself (`target` =
     knowledge/standards/critical_thought_partner_protocol.md, ticket #93) is
     structurally complete: the governing principle, the Governor's five
     triggers (T1-T5) and four suppression rules (S1-S4), the five CTP
     functions, the five detection mechanisms, a worked example, and both
     documented v1 limits ("sharpener, not oracle" / "instruction, not
     independence").

  2. CLAUDE.md is actually WIRED to that standard (ticket #93's CLAUDE.md
     changes): the CTP core section heading exists, the governance table has
     a row pointing at the standard's path, the "most turns need no
     challenge" / zero-challenge-by-default framing is present, and both v1
     limits are echoed in the core section (not just the deep-dive standard).

CLAUDE.md is resolved via `rubrics.base.repo_root()` — never a hardcoded
absolute path — so this rubric keeps working from any checkout/worktree.

target: path to critical_thought_partner_protocol.md OR raw text (`_read`).
"""
from __future__ import annotations

import re
from pathlib import Path

from rubrics.base import CheckResult, repo_root


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


_CORE_HEADING = r"###\s*You Are a Critical Thought Partner, Not a Typist"


def _section(text: str, heading_pattern: str) -> str:
    """Text from a `### heading` match up to the next `### ` heading (or EOF) —
    scopes a check to one CLAUDE.md subsection for a more discriminating wiring
    check than a whole-file substring search."""
    m = re.search(heading_pattern, text, re.I)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"\n### ", rest)
    return rest[:nxt.start()] if nxt else rest


# --- STANDARD file checks (target) ------------------------------------------

def _check_governing_principle(text: str) -> CheckResult:
    ok = _present(r"right number of challenges is zero", text) and \
         _present(r"gated by triggers and suppression rules", text)
    return _bool_check("governing_principle", ok,
                       detail="governing-principle statement present" if ok
                       else "governing principle ('right number of challenges is zero' / "
                            "'gated by triggers and suppression rules') missing or altered")


def _check_governor_triggers(text: str) -> CheckResult:
    return _ratio_present("governor_triggers_t1_t5",
                          [r"\bT1\b", r"\bT2\b", r"\bT3\b", r"\bT4\b", r"\bT5\b"], text)


def _check_suppression_rules(text: str) -> CheckResult:
    return _ratio_present("suppression_s1_s4",
                          [r"\bS1\b", r"\bS2\b", r"\bS3\b", r"\bS4\b"], text)


_FIVE_FUNCTIONS = [
    r"Problem definition",
    r"Context completeness",
    r"Input examination",
    r"Direction maintenance",
    r"Correction metabolism",
]


def _check_five_functions(text: str) -> CheckResult:
    return _ratio_present("five_functions", _FIVE_FUNCTIONS, text, hard_fail=True)


_FIVE_DETECTION_MECHANISMS = [
    r"\bStructural\b",
    r"Mechanism\s*/\s*first-principles",
    r"\bProcedural\b",
    r"\bInconsistency\b",
    r"Domain-template",
]


def _check_five_detection_mechanisms(text: str) -> CheckResult:
    return _ratio_present("five_detection_mechanisms", _FIVE_DETECTION_MECHANISMS, text)


def _check_worked_example(text: str) -> CheckResult:
    ok = _present(r"Worked example", text) and _present(r"\*\*Consultant:\*\*", text) and \
         _present(r"\*\*Cortex:\*\*", text)
    return _bool_check("worked_example", ok,
                       detail="worked Consultant/Cortex example dialogue present" if ok
                       else "no worked example dialogue found")


def _check_v1_limits_standard(text: str) -> CheckResult:
    sharpener = _present(r"sharpener,?\s*not\s*(an\s*)?oracle", text)
    independence = _present(r"instruction,?\s*not\s*independence", text)
    ok = sharpener and independence
    score = (int(sharpener) + int(independence)) / 2
    return CheckResult("v1_limits_standard", score, ok,
                       detail=f"'sharpener, not oracle'={sharpener}, "
                              f"'instruction, not independence'={independence}")


STANDARD_CHECKS = [
    _check_governing_principle,
    _check_governor_triggers,
    _check_suppression_rules,
    _check_five_functions,
    _check_five_detection_mechanisms,
    _check_worked_example,
    _check_v1_limits_standard,
]


# --- CLAUDE.md wiring checks --------------------------------------------------

def _check_claude_md_core_section(claude_md: str) -> CheckResult:
    ok = _present(_CORE_HEADING, claude_md)
    return _bool_check("claude_md_core_section_heading", ok, hard_fail=True,
                       detail="CTP core section heading present in CLAUDE.md" if ok
                       else "CLAUDE.md is missing the 'You Are a Critical Thought Partner' core section")


def _check_claude_md_governance_table_row(claude_md: str) -> CheckResult:
    ok = _present(r"Critical Thought Partner Protocol.*critical_thought_partner_protocol\.md", claude_md)
    return _bool_check("claude_md_governance_table_row", ok, hard_fail=True,
                       detail="governance table row wires the CTP standard's path" if ok
                       else "governance table has no row pointing at critical_thought_partner_protocol.md")


def _check_claude_md_zero_framing(claude_md: str) -> CheckResult:
    section = _section(claude_md, _CORE_HEADING)
    ok = _present(r"most turns need no challenge", section) or \
         _present(r"right number of challenges is zero", section)
    return _bool_check("claude_md_zero_challenge_framing", ok,
                       detail="'most turns need no challenge' / zero-by-default framing present in core section" if ok
                       else "core section is missing the 'most turns need no challenge' framing")


def _check_claude_md_v1_limits_core(claude_md: str) -> CheckResult:
    section = _section(claude_md, _CORE_HEADING)
    sharpener = _present(r"sharpener,?\s*not\s*(an\s*)?oracle", section)
    independence = _present(r"instruction,?\s*not\s*independence", section)
    ok = sharpener and independence
    score = (int(sharpener) + int(independence)) / 2
    return CheckResult("claude_md_v1_limits_in_core", score, ok,
                       detail=f"'sharpener, not oracle'={sharpener}, "
                              f"'instruction, not independence'={independence} (within CTP core section)")


CLAUDE_MD_CHECKS = [
    _check_claude_md_core_section,
    _check_claude_md_governance_table_row,
    _check_claude_md_zero_framing,
    _check_claude_md_v1_limits_core,
]


def evaluate(target: str) -> list[CheckResult]:
    """target: critical_thought_partner_protocol.md path or raw text. Runs the
    STANDARD checks against `target`, then independently resolves CLAUDE.md via
    repo_root() and runs the WIRING checks against it. A missing CLAUDE.md is a
    hard failure (the whole point of this rubric half is verifying the wiring
    exists), not a silent skip."""
    text = _read(target)
    checks = [fn(text) for fn in STANDARD_CHECKS]

    root = repo_root()
    claude_md_path = root / "CLAUDE.md"
    if not claude_md_path.exists():
        checks.append(CheckResult("claude_md_wiring", 0.0, False, hard_fail=True,
                                  detail=f"CLAUDE.md not found at {claude_md_path}"))
        return checks

    claude_md = claude_md_path.read_text(errors="replace")
    checks += [fn(claude_md) for fn in CLAUDE_MD_CHECKS]
    return checks
