#!/usr/bin/env python3
"""
PreToolUse(mcp__.*) hook — the outbound MCP query guard.

This is the first actual enforcement of security_protocol.md Section 5 ("never
include the client's name in an MCP query"). Section 5 today is a prompt
instruction with zero code behind it: nothing inspects a query before it leaves
the session. The only reason an unguarded, client-named query hasn't already
reached the Backbase Infobank MCP server (https://mcp.backbase.io/mcp) is that
the server requires Backbase SSO and returns nothing when unauthenticated — an
accident of the current environment, not a control. The moment a consultant
authorises Infobank, that silent no-op becomes a live, unguarded outbound query.
This hook is the control that closes the gap.

WHAT IT DOES
  Any tool call whose name matches mcp__.* has its `tool_input` walked
  recursively (MCP args are frequently nested dicts/lists) and every string
  value scanned against a deny-list of client/stakeholder identifiers. A match
  denies the call with a message that names the matched term and shows how to
  rephrase the query generically — never revealing which tool was involved.

DENY-LIST SOURCE (interim — see seam below)
  There is no first-class "which engagement is this session working on"
  signal available to a PreToolUse hook (no session->engagement pointer
  exists yet in this repo). Rather than guess wrong and under-block, this
  hook aggregates identifiers across every engagement present locally under
  `engagements/<client>/...` (that directory is gitignored / machine-local,
  so a checkout typically holds only the engagements one consultant is
  actually working). For each client directory found (excluding the shared
  `engagements/inputs/` and `engagements/outputs/` legacy staging folders)
  it extracts identifier terms from:
    - the client directory slug itself (e.g. "hnb", "peoples_first_bank")
    - CLIENT_PROFILE.md (client-level)
    - ENGAGEMENT_CONTEXT.md and inputs/engagement_intake.md (any engagement
      under that client), read directly per the ticket's interim instruction

  >>> SEAM: a shared deny-list resolver arrives with the engine ticket (#159).
  >>> When it lands, replace `_resolve_deny_list()` below with a call into
  >>> it — the extraction heuristics here (label lines, ALL-CAPS acronyms,
  >>> directory slugs) are a stopgap, not the long-term source of truth.
  >>> A generic "**bold phrase**" heuristic was deliberately tried and
  >>> dropped during testing — see the NOTE in _extract_terms_from_text.

FAIL-CLOSED (the deliberate inversion of anonymize-guard.py's fail-open rule)
  anonymize-guard.py fails OPEN on any exception: it gates a local Read, and a
  wedged session is worse than an occasional missed local file. This hook
  gates an OUTBOUND call to a third-party server. An outbound query that
  cannot be verified as safe must not be sent — so any exception while
  resolving the deny-list, reading engagement files, or scanning the query
  results in DENY, not allow. This is intentional and is the opposite default
  of every other hook in this directory; do not "fix" it into failing open.

  The one case that is NOT an error and DOES allow is: the deny-list
  resolves cleanly but comes back empty (no engagements/ directory, or no
  extractable identifiers in what's there). That's "nothing to check
  against" rather than "the check broke" — it allows, with a stderr warning
  that the query could not be verified against a configured deny-list.

WHAT IT NEVER DOES
  - Never logs query contents. Matched text is used only to build the deny
    message (which names the matched TERM, not the full query) and then
    discarded. Nothing is written to disk or to a log file.
  - Never names a tool in operator-facing text (copy rule).

Decision contract (stdout JSON, exit 0):
  - allow -> emit nothing
  - deny  -> emit {"hookSpecificOutput": {permissionDecision: "deny", ...}}
"""
import json
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))

# Generic banking words that must NOT count as a client identifier on their
# own, even though they show up constantly in bank names ("First National
# Bank", "Pacific Community Credit Union", ...). Matched case-insensitively.
GENERIC_STOPLIST = {
    "bank", "banking", "credit", "union", "first", "national", "federal",
    "united", "community", "citizens", "state", "financial", "savings",
    "trust", "group", "holdings", "capital", "mutual", "valley", "coast",
    "pacific",
}

# Common short all-caps tokens that are NOT client identifiers, so a bare
# acronym scan of engagement docs doesn't drown in false positives.
ACRONYM_STOPLIST = {
    "CEO", "CFO", "CTO", "COO", "CIO", "CMO", "CHRO", "ROI", "KPI", "KPIS",
    "API", "APIS", "SLA", "FAQ", "URL", "USD", "EUR", "GBP", "PDF", "CSV",
    "HTML", "XML", "JSON", "SQL", "ATM", "IVR", "CRM", "ERP", "SDK", "SSO",
    "PII", "MCP", "LLM", "AI", "ML", "UX", "UI", "IT", "HR", "PR", "QA",
    "US", "UK", "EU", "VP", "SVP", "EVP", "YOY", "QOQ", "TBD", "NA", "RFP",
    "RFI", "POC", "MVP", "SAAS", "B2B", "B2C", "KYC", "AML", "GDPR", "OK",
    "CX", "UAT", "SOW", "NDA", "CAC", "LTV", "ARR", "ARPU", "COO's",
}

ENGAGEMENT_DOC_NAMES = ("ENGAGEMENT_CONTEXT.md", "engagement_intake.md")
CLIENT_PROFILE_NAME = "CLIENT_PROFILE.md"
SKIP_CLIENT_DIRS = {"inputs", "outputs"}  # shared legacy staging, not clients
MAX_FILE_BYTES = 200_000  # bound reads; these are markdown docs, not logs
MAX_FILES_SCANNED = 200   # bound total work regardless of engagements/ size


def _allow():
    sys.exit(0)


def _deny(reason: str):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def _deny_gate_broken(detail: str):
    """Fail-closed path: the deny-list could not be verified, so the query is
    not sent. Distinct from a normal deny (a name matched) — nothing matched,
    the gate itself could not run."""
    _deny(
        "🛑 Infobank query gate could not verify this search\n\n"
        f"   The client-identifier check could not run ({detail}). An "
        "outbound query that\n"
        "   cannot be verified against the deny-list is not sent — this is "
        "a fail-closed\n"
        "   control, not a false positive.\n\n"
        "   Retry once the underlying issue is fixed, or ask the consultant "
        "how to proceed.\n\n"
        "   (Security protocol §5)"
    )


# --- term extraction -----------------------------------------------------

_LABEL_LINE_RE = re.compile(
    r"^\s*[-*#]{0,3}\s*\**\s*"
    r"(?:client(?:\s+name)?|bank(?:\s+name)?|institution|company|organi[sz]ation)"
    r"\s*\**\s*:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)
_PAREN_ACRONYM_RE = re.compile(r"\(([A-Z]{2,8})\)")
_ALLCAPS_TOKEN_RE = re.compile(r"\b[A-Z]{2,8}\b")
_HEADING_RE = re.compile(r"^\s*#{1,3}\s+(.+)$", re.MULTILINE)
_WORD_RE = re.compile(r"[A-Za-z]+")


def _single_word_ok(word):
    w = word.strip()
    if len(w) < 4:
        return False
    if w.lower() in GENERIC_STOPLIST:
        return False
    return True


def _add_term(terms, raw):
    t = (raw or "").strip().strip(".,;:()’'\"")
    if not t:
        return
    terms.add(t)


def _extract_terms_from_text(text, terms):
    # Explicit "Client:"/"Bank Name:"/... label lines.
    for m in _LABEL_LINE_RE.finditer(text):
        value = m.group(1).strip()
        for acr in _PAREN_ACRONYM_RE.findall(value):
            if acr not in ACRONYM_STOPLIST:
                _add_term(terms, acr)
        cleaned = _PAREN_ACRONYM_RE.sub(" ", value)
        for w in _WORD_RE.findall(cleaned):
            if _single_word_ok(w):
                _add_term(terms, w)
        phrase = cleaned.strip()
        if phrase and len(phrase.split()) >= 2:
            _add_term(terms, phrase)

    # Bare ALL-CAPS acronyms anywhere (bank short codes like "HNB", "BECU").
    for tok in _ALLCAPS_TOKEN_RE.findall(text):
        if tok in ACRONYM_STOPLIST:
            continue
        if tok.lower() in GENERIC_STOPLIST:
            continue
        _add_term(terms, tok)

    # NOTE: a generic "**bold phrase**" heuristic was tried and dropped —
    # engagement docs bold topic/section headings just as often as names
    # (e.g. "**Digital Onboarding**" as a section title), and that produced
    # a real false positive that would have blocked every query mentioning
    # a common domain term. Bold text alone is not a reliable name signal;
    # only the explicitly-labelled fields below and bare acronyms are used.

    # First heading of the doc often carries the client name.
    m = _HEADING_RE.search(text)
    if m:
        heading = m.group(1).strip()
        for acr in _PAREN_ACRONYM_RE.findall(heading):
            if acr not in ACRONYM_STOPLIST:
                _add_term(terms, acr)


def _extract_terms_from_slug(slug, terms):
    # Individual parts go through the SAME generic-word guard as prose
    # extraction. Without this, a slug like "bank_australia" would add the
    # bare word "bank" to the deny-list and block nearly every banking
    # query anyone locally checked out that engagement ever sends.
    for part in re.split(r"[_\-]+", slug):
        if _single_word_ok(part):
            _add_term(terms, part)
    # The joined form (e.g. "hnb", "bankaustralia") is added unconditionally
    # and without the length floor: concatenating removes the "common
    # English word" collision risk that the length/stoplist guard exists
    # for, and this is also how a short bare-acronym client slug (e.g. a
    # directory literally named "hnb") becomes a deny-list term even with
    # no markdown docs present yet.
    joined = slug.replace("_", "").replace("-", "")
    if len(joined) >= 2:
        _add_term(terms, joined)


_read_count = [0]


def _read_bounded(path):
    if _read_count[0] >= MAX_FILES_SCANNED:
        return ""
    _read_count[0] += 1
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            return fh.read(MAX_FILE_BYTES)
    except OSError:
        return ""


def _resolve_deny_list():
    """Aggregate client/stakeholder identifier terms across every engagement
    found locally under engagements/. Returns a set of terms (strings).
    Raises on any unexpected error so the caller can fail closed."""
    terms = set()
    root = PROJECT_DIR / "engagements"
    if not root.is_dir():
        return terms

    for client_dir in sorted(root.iterdir()):
        if not client_dir.is_dir():
            continue
        if client_dir.name.startswith("."):
            continue
        if client_dir.name.lower() in SKIP_CLIENT_DIRS:
            continue

        _extract_terms_from_slug(client_dir.name, terms)

        profile = client_dir / CLIENT_PROFILE_NAME
        if profile.is_file():
            _extract_terms_from_text(_read_bounded(profile), terms)

        for doc_name in ENGAGEMENT_DOC_NAMES:
            for doc_path in client_dir.rglob(doc_name):
                if _read_count[0] >= MAX_FILES_SCANNED:
                    break
                _extract_terms_from_text(_read_bounded(doc_path), terms)

    return terms


# --- query scanning --------------------------------------------------------

def _iter_strings(obj):
    """Recursively yield every string leaf value out of a (possibly nested)
    MCP tool_input structure — dicts, lists, and scalars."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            for s in _iter_strings(v):
                yield s
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            for s in _iter_strings(v):
                yield s
    # numbers / bools / None: nothing to scan


def _term_pattern(term):
    escaped = re.escape(term)
    return re.compile(r"(?<![A-Za-z0-9])" + escaped + r"(?![A-Za-z0-9])", re.IGNORECASE)


def _find_match(strings, deny_terms):
    # Longer terms first so a full client name matches before a generic
    # single word that happens to be a substring of it.
    ordered = sorted(deny_terms, key=len, reverse=True)
    patterns = [(term, _term_pattern(term)) for term in ordered]
    for blob in strings:
        if not blob:
            continue
        for term, pattern in patterns:
            m = pattern.search(blob)
            if m:
                return m.group(0)  # surface the text as it appeared in the query
    return None


def _deny_message(matched_term):
    return (
        "🛑 That Infobank search names the client\n\n"
        f"   Your search contained \"{matched_term}\". Infobank sits outside "
        "Cortex, so client\n"
        "   names must not go into it.\n\n"
        "   Ask the same question generically:\n"
        "       \"digital onboarding capabilities for a Tier-2 retail bank "
        "in South Asia\"\n\n"
        "   (Security protocol §5)"
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        _deny_gate_broken("could not read the tool call payload: %s" % exc)
        return

    tool_input = payload.get("tool_input", {}) or {}

    try:
        deny_terms = _resolve_deny_list()
    except Exception as exc:
        _deny_gate_broken("deny-list could not be resolved: %s" % exc)
        return

    if not deny_terms:
        sys.stderr.write(
            "mcp-query-guard: no client deny-list configured for any local "
            "engagement — allowing this query WITHOUT verification. If you "
            "are working a real engagement, confirm CLIENT_PROFILE.md / "
            "ENGAGEMENT_CONTEXT.md exist so this gate can check future "
            "queries.\n"
        )
        _allow()
        return

    try:
        strings = list(_iter_strings(tool_input))
        matched = _find_match(strings, deny_terms)
    except Exception as exc:
        _deny_gate_broken("query scan raised an error: %s" % exc)
        return

    if matched:
        _deny(_deny_message(matched))
        return

    _allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        # Fail CLOSED — the opposite default of the other hooks in this
        # directory. This gates an outbound call to a third-party server;
        # an unverifiable query must not be sent.
        _deny_gate_broken("unexpected guard error: %s" % exc)
