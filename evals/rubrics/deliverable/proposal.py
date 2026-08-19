"""Proposal deliverable code-evaluators (objective, no LLM).

Scores a CLIENT-FACING proposal HTML (the artifact `/proposal-longform` renders
from the client-safe contract that `/proposal-builder` hands it). Every check maps
to a rule that is normative somewhere in the repo, not to taste:

  exactly_2_scenarios            proposal-narrative.md §2 "Constants" + /proposal-builder
                                 Gate 6 — exactly two client-facing scenarios (anchor A
                                 and the lighter alternative B). A third is a defect
                                 unless explicitly overridden and journaled.
  zero_internal_content          /proposal-builder ACT 3 render boundary — the negotiation
                                 layer (ladder, floors, walk-away, approval tiers, lever
                                 ledger, Deal Desk verdict, INTERNAL_* files) NEVER crosses
                                 into the client artifact.
  story_model_matches_deal_type  proposal-narrative.md §1 "The hard rule" — a renewal or
                                 expansion MUST NOT open with a challenger / why-change /
                                 transformation narrative (it measurably raises switching
                                 intent); it opens on delivered value / what hasn't changed.
                                 The deal type is DECLARED, never inferred — see the
                                 DEAL-TYPE DECLARATION note below.
  assumptions_section_present    §2 "Constants" — every assumption behind the numbers, on
                                 the record, with who validates it.
  no_unsourced_financial_claims  §3 value-rationale hierarchy — a financial-return claim is
                                 allowed only when it carries its basis (an upstream model,
                                 a stated basis/assumption) or is labelled "directional".
  self_contained_html            client deliverability — a proposal is emailed/zipped and
                                 opened offline; nothing may load from a third-party host
                                 (Google Fonts is the one allowed exception).
  disclaimer_present             /proposal-longform QA — projected / non-binding / not-a-quote
                                 wording, in EVERY language the document renders.
  plain_declarative_headers      §4 voice — headers carry the message ("Why our price holds"),
                                 they are not labels ("Executive Summary", "Our Solution").
  no_transformation_marketing    §4 voice — no "unlock" / "reimagine" / "journey to the future
                                 of banking"; that register belongs to acquisition decks.

VOICE: DETERMINISTIC, NOT A JUDGE. PRD v5 §5 sketches a judge check for
"plain declarative voice". It is implemented here as two deterministic
heuristics instead. Wiring a judge is mechanically easy (rubrics.judge.judge
degrades to skipped without a key) — CALIBRATING one is not: without
ANTHROPIC_API_KEY the judge is skipped locally and would first actually run in
CI, where an uncalibrated semantic score could flip a blocking gate on a golden
that was never scored against it. Header/register patterns are the objectively
checkable part of §4; the subjective part stays out of the gate until a judge
threshold can be calibrated against real scored runs.

DEAL-TYPE DECLARATION: `story_model_matches_deal_type` reads the deal type from
`<meta name="deal-type" content="...">`, which /proposal-builder ACT 3 item 7
emits and /proposal-longform step 4 carries through. There is deliberately NO
fallback that infers the deal type from the document's own prose: the check
scores that same prose, so inference is circular — a renewal opened with a
challenger pitch reads as a new logo and certifies itself, which is precisely
the defect the check exists to catch. An absent tag is a render-contract
violation and fails on that basis.

SCENARIO MARKER CONVENTION: scenario cards carry `data-scenario="..."` (one
attribute per client-facing scenario). When a document carries no such markers
the check falls back to counting `.card` elements inside the scenarios section,
so a proposal rendered before the convention existed is still scored rather
than silently passing.
"""
from __future__ import annotations

import re
from pathlib import Path

from rubrics.base import CheckResult

# ── internal-content patterns (TIGHT) ───────────────────────────────────────
# Deliberately narrow: the /proposal-builder verify scan greps broad terms
# ("floor", "anchor", "extract") because a consultant then eyeballs each hit.
# A blocking eval cannot do that — bare "floor"/"anchor"/"extract" false-positive
# on legitimate client copy ("ground floor", "anchor tenant", "extract value"),
# so each pattern here is either an internal artifact name or a phrase that has
# no innocent reading in a client proposal.
_INTERNAL_PATTERNS = [
    r"INTERNAL_",
    r"\bwalk-?away\b",
    r"\bwalk_away\b",
    r"\bfloor\s+GM\b",
    r"\bfloor_gm\b",
    r"\bfloor\s+gross\s+margin\b",
    r"\bheadroom\s+to\s+(?:the\s+)?floor\b",
    r"\bdiscount[- ]to[- ]floor\b",
    r"\bapproval\s+tier\b",
    r"\blever\s+ledger\b",
    r"\bdeal\s+desk\s+verdict\b",
    r"\bconcession\s+budget\b",
    r"\bcum_discount\b",
    r"\bcum\.?\s+discount\b",
    r"\bBAFO\b",
    r"\bconcession\s+ladder\b",
    r"\bmartini\b",
]

# ── story-model markers (proposal-narrative.md §1) ──────────────────────────
_RENEWAL_OPENING = [
    r"what\s+hasn'?t\s+changed", r"what\s+has\s+not\s+changed",
    r"since\s+(?:you\s+)?sign(?:ing|ed)", r"since\s+the\s+agreement\s+was\s+signed",
    r"already\s+delivered", r"results\s+(?:we'?ve\s+|already\s+)?delivered",
    r"delivered\s+since", r"shipped\s+since", r"we\s+have\s+delivered",
    r"the\s+platform\s+is\s+not\s+the\s+one",
    r"your\s+original\s+(?:decision|selection)", r"the\s+selection\s+you\s+ran",
]
_CHALLENGER_OPENING = [
    r"cost\s+of\s+standing\s+still", r"cost\s+of\s+doing\s+nothing",
    r"cost\s+of\s+inaction", r"why\s+change", r"the\s+status\s+quo\s+is",
    r"standing\s+still\s+is", r"burning\s+platform",
    r"transformation\s+imperative", r"imperative\s+to\s+transform",
    r"reimagine", r"\bunlock\b", r"journey\s+to\s+the\s+future",
    r"future\s+of\s+banking",
]

# ── voice (§4) ──────────────────────────────────────────────────────────────
_LABEL_HEADERS = [
    "executive summary", "our solution", "the solution", "introduction",
    "background", "overview", "about us", "about backbase", "value proposition",
    "conclusion", "pricing", "company profile",
]
_MARKETING_TERMS = [
    r"\bunlock(?:ing|s)?\b", r"\breimagin(?:e|ing|ed)\b",
    r"journey\s+to\s+the\s+future", r"\bfuture[- ]proof\b",
    r"\bbest[- ]in[- ]class\b", r"\bworld[- ]class\b", r"\bgame[- ]chang",
    r"\bparadigm\s+shift\b", r"\brevolutioni[sz]",
]

# ── financial-claim detection (§3) ──────────────────────────────────────────
# A "claim" = a money figure in a sentence that asserts a RETURN (benefit,
# saving, value, ROI, payback). Investment/price figures are not claims.
_MONEY = r"(?:[€£$]\s?\d[\d,.]*\s?(?:–|-|to)?\s?[\d,.]*\s?(?:[KMB]|million|billion|bn|k|m)?)"
_RETURN_WORDS = r"(?:benefit|saving|save|savings|return|ROI|payback|value at stake|" \
                r"value opportunity|upside|uplift|gain|deliver(?:s|ed|ing)?|worth)"
_BASIS_WORDS = r"(?:source|basis|based on|modell?ed|model|assumption|assumed|" \
               r"directional|conservative case|discovery|benchmark|companion|" \
               r"business case|per the|derived from|validated|to validate|" \
               r"your (?:own )?(?:figures|numbers|volumes))"
_CLAIM_WINDOW = 320   # chars of surrounding visible text searched for the basis


# ── html helpers ────────────────────────────────────────────────────────────

def _strip_tags(html: str) -> str:
    no_script = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", no_script)
    text = text.replace("&amp;", "&").replace("&nbsp;", " ").replace("&middot;", "·")
    return re.sub(r"\s+", " ", text)


def _sections(html: str) -> list[tuple[str, str]]:
    """(id, inner_html) for every <section>, in document order."""
    out = []
    for m in re.finditer(r"<section\b([^>]*)>(.*?)</section>", html, re.S | re.I):
        sid = re.search(r'id\s*=\s*"([^"]+)"', m.group(1))
        out.append((sid.group(1) if sid else "", m.group(2)))
    return out


def _opening_html(html: str) -> str:
    """Hero + first section — the 'opening narrative' the story model governs."""
    hero = re.search(r"<header\b.*?</header>", html, re.S | re.I)
    secs = _sections(html)
    return (hero.group(0) if hero else "") + (secs[0][1] if secs else "")


def _headings(html: str) -> list[str]:
    return [_strip_tags(m.group(1)).strip()
            for m in re.finditer(r"<h[1-4]\b[^>]*>(.*?)</h[1-4]>", html, re.S | re.I)]


def _declared_deal_type(html: str) -> str | None:
    """The `<meta name="deal-type">` declaration, or None if the tag is absent.

    Load-bearing: `_check_story_model` hard-fails when this returns None, so the
    match must not be defeated by attribute order or quote style. Accepts
    content-before-name and single-quoted values.
    """
    for m in re.finditer(r"<meta\b([^>]*)>", html, re.I):
        attrs = m.group(1)
        if not re.search(r"""\bname\s*=\s*["']?\s*deal-type\s*["']?""", attrs, re.I):
            continue
        c = re.search(r"""\bcontent\s*=\s*["']([^"']+)["']""", attrs, re.I)
        if c:
            return c.group(1).strip().lower()
    return None


def _bool(name: str, ok: bool, *, hard_fail: bool = False, detail: str = "",
          evidence: list[str] | None = None) -> CheckResult:
    return CheckResult(name, 1.0 if ok else 0.0, ok, hard_fail=hard_fail,
                       detail=detail, evidence=evidence or [])


# ── checks ──────────────────────────────────────────────────────────────────

def _check_scenarios(html: str) -> CheckResult:
    marked = re.findall(r'data-scenario\s*=\s*"([^"]*)"', html, re.I)
    if marked:
        n, how = len(marked), f"data-scenario markers: {marked}"
    else:
        n, how = 0, "no data-scenario markers"
        for sid, inner in _sections(html):
            if "scenario" in sid.lower() or re.search(r"scenarios?</", inner, re.I):
                cards = re.findall(r'class\s*=\s*"[^"]*\bcard\b[^"]*"', inner)
                n, how = len(cards), f"fallback: {len(cards)} .card element(s) in section '{sid}'"
                break
    return CheckResult("exactly_2_scenarios", 1.0 if n == 2 else 0.0, n == 2, hard_fail=True,
                       detail=f"{n} client-facing scenario(s) — {how}")


def _check_internal(html: str) -> CheckResult:
    # HTML comments are invisible on screen but one "view source" away, so a leak
    # parked in a comment is still a leak. `_strip_tags` cannot see them — a whole
    # `<!-- … -->` matches its `<[^>]+>` tag pattern and is deleted body and all —
    # so lift the comment bodies out first and scan them alongside visible text.
    comments = re.findall(r"<!--(.*?)-->", html, re.S)
    text = _strip_tags(html) + " " + " ".join(comments)
    hits: list[str] = []
    for pat in _INTERNAL_PATTERNS:
        # `INTERNAL_` is the on-disk artifact naming convention — scan the RAW html
        # (so it also catches the name inside an attribute or a script string) and
        # case-SENSITIVELY, so identifiers like `zero_internal_content` don't hit.
        raw = pat == r"INTERNAL_"
        src = html if raw else text
        flags = 0 if raw else re.I
        for m in re.finditer(pat, src, flags):
            hits.append(f"{pat} → …{src[max(0, m.start() - 40):m.end() + 40].strip()}…")
    ok = not hits
    return CheckResult("zero_internal_content", 1.0 if ok else 0.0, ok, hard_fail=True,
                       detail="no internal negotiation content" if ok
                       else f"{len(hits)} internal marker hit(s)", evidence=hits[:6])


def _check_story_model(html: str) -> CheckResult:
    # The deal type must be DECLARED, never inferred from the same prose this check
    # then scores — that is circular: a renewal opened with a challenger pitch reads
    # as new_logo and self-validates, i.e. the exact defect the check exists to catch
    # becomes its own alibi. Both producers mandate the tag (/proposal-builder ACT 3
    # item 7, /proposal-longform step 4), so its absence is a contract violation and
    # fails on its own terms.
    declared = _declared_deal_type(html)
    if declared is None:
        return CheckResult("story_model_matches_deal_type", 0.0, False, hard_fail=True,
                           detail='no <meta name="deal-type"> — the render contract '
                                  'requires it; story model cannot be verified')

    opening = _strip_tags(_opening_html(html))
    renewal_hits = [p for p in _RENEWAL_OPENING if re.search(p, opening, re.I)]
    challenger_hits = [p for p in _CHALLENGER_OPENING if re.search(p, opening, re.I)]
    deal_type, how = declared, 'declared via <meta name="deal-type">'

    if deal_type in ("renewal", "expansion"):
        ok = bool(renewal_hits) and not challenger_hits
        detail = (f"{deal_type} ({how}) — reinforce opening: "
                  f"{len(renewal_hits)} delivered-value marker(s), "
                  f"{len(challenger_hits)} challenger marker(s) (must be 0)")
    else:
        ok = bool(challenger_hits)
        detail = (f"{deal_type} ({how}) — challenge opening: "
                  f"{len(challenger_hits)} why-change marker(s) (must be ≥1)")
    return CheckResult("story_model_matches_deal_type", 1.0 if ok else 0.0, ok, hard_fail=True,
                       detail=detail,
                       evidence=[f"renewal: {renewal_hits}", f"challenger: {challenger_hits}"])


def _check_assumptions(html: str) -> CheckResult:
    block = None
    for sid, inner in _sections(html):
        if "assum" in sid.lower() or re.search(r"assumptions?\b", _strip_tags(inner), re.I):
            block = inner
            break
    if block is None:
        return _bool("assumptions_section_present", False, detail="no assumptions section")
    rows = len(re.findall(r"<tr\b", block, re.I))
    has_table = bool(re.search(r"<table\b", block, re.I))
    owner_col = bool(re.search(r"(to\s+validate|valida\w+\s+(with|by)|owner)", _strip_tags(block), re.I))
    data_rows = max(0, rows - 1)          # minus the header row
    ok = has_table and owner_col and data_rows >= 2
    score = 1.0 if ok else (0.5 if has_table else 0.0)
    return CheckResult("assumptions_section_present", score, ok,
                       detail=f"table={has_table}, validation-owner column={owner_col}, "
                              f"{data_rows} assumption row(s)")


def _check_financial_claims(html: str) -> CheckResult:
    text = _strip_tags(html)
    claims, unsourced = 0, []
    for m in re.finditer(_MONEY, text):
        span = text[max(0, m.start() - 120): m.end() + 120]
        if not re.search(_RETURN_WORDS, span, re.I):
            continue                       # a price/investment figure, not a return claim
        claims += 1
        window = text[max(0, m.start() - _CLAIM_WINDOW): m.end() + _CLAIM_WINDOW]
        if not re.search(_BASIS_WORDS, window, re.I):
            unsourced.append("…" + span.strip() + "…")
    ok = not unsourced
    score = 1.0 if ok else max(0.0, 1.0 - len(unsourced) / max(claims, 1))
    return CheckResult("no_unsourced_financial_claims", score, ok, hard_fail=True,
                       detail=f"{claims} financial-return claim(s), {len(unsourced)} without an "
                              f"adjacent basis/source/directional label",
                       evidence=unsourced[:4])


_ALLOWED_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")


def _check_self_contained(html: str) -> CheckResult:
    refs = re.findall(r'(?:src|href)\s*=\s*"(https?://[^"]+)"', html, re.I)
    bad = [u for u in refs if not any(h in u for h in _ALLOWED_HOSTS)]
    ok = not bad
    return CheckResult("self_contained_html", 1.0 if ok else 0.0, ok,
                       detail="no external refs beyond Google Fonts" if ok
                       else f"{len(bad)} external reference(s)", evidence=bad[:5])


_DISCLAIMER_EN = r"(not\s+a\s+quote|non-?binding|projected\s+pricing|for\s+planning\s+purposes|" \
                 r"indicative\s+only)"
# Every alternative must be a NEGATED or hedging form. A bare `ملزم` ("binding")
# is not one: it matches a document asserting the pricing IS binding — the exact
# opposite of the disclaimer — and, being a substring of `غير ملزم`, it shadowed
# the negated alternative so the negation was never actually required.
_DISCLAIMER_AR = r"(ليس\s+عرض|وليس\s+عرض|و?غير\s+ملزم|تسعير\s+متوقع|لأغراض\s+التخطيط)"


def _check_disclaimer(html: str) -> CheckResult:
    text = _strip_tags(html)
    en = bool(re.search(_DISCLAIMER_EN, text, re.I))
    bilingual = bool(re.search(r'lang\s*=\s*"ar"', html, re.I))
    ar = bool(re.search(_DISCLAIMER_AR, text)) if bilingual else True
    ok = en and ar
    score = 1.0 if ok else (0.5 if (en or ar) else 0.0)
    return CheckResult("disclaimer_present", score, ok, hard_fail=True,
                       detail=f"projected/non-binding disclaimer — en={en}"
                              + (f", ar={ar} (bilingual document)" if bilingual else " (monolingual)"))


def _check_headers(html: str) -> CheckResult:
    labels = []
    for h in _headings(html):
        clean = re.sub(r"[^a-z ]", " ", h.lower()).strip()
        clean = re.sub(r"\s+", " ", clean)
        if any(clean == lab or clean.startswith(lab + " ") for lab in _LABEL_HEADERS):
            labels.append(h)
    ok = not labels
    return CheckResult("plain_declarative_headers", 1.0 if ok else 0.0, ok,
                       detail="headings carry the message, not a label" if ok
                       else f"{len(labels)} label-header(s)", evidence=labels[:5])


def _check_marketing(html: str) -> CheckResult:
    text = _strip_tags(html)
    hits = [m.group(0) for pat in _MARKETING_TERMS for m in re.finditer(pat, text, re.I)]
    ok = not hits
    return CheckResult("no_transformation_marketing", 1.0 if ok else 0.0, ok,
                       detail="no transformation-marketing register" if ok
                       else f"{len(hits)} marketing term(s)", evidence=sorted(set(hits))[:5])


CHECKS = (_check_scenarios, _check_internal, _check_story_model, _check_assumptions,
          _check_financial_claims, _check_self_contained, _check_disclaimer,
          _check_headers, _check_marketing)


def evaluate(target: str) -> list[CheckResult]:
    """target: path to a client-facing proposal HTML."""
    p = Path(target)
    if not p.exists():
        return [CheckResult("proposal_html_readable", 0.0, False, hard_fail=True,
                            detail=f"target not found: {target}")]
    html = p.read_text(errors="replace")
    return [fn(html) for fn in CHECKS]
