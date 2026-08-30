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
    "pacific", "fund", "society",
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

# Words that mark a captured phrase as a ROLE, a section label or an
# organisational unit rather than a person's name. Used ONLY by the
# stakeholder path (_extract_stakeholder_terms), because the columns and
# label lines that carry stakeholder names carry job titles just as often
# ("| Name/Role |" literally admits either). Without this, "Head of Digital
# Banking" in a Name/Role cell becomes a client-identity deny term and every
# ordinary query containing that phrase is denied.
#
# Name PARTICLES ("van", "de", "der", "bin", "al", "da", "von") are
# deliberately absent — they are parts of real surnames.
ROLE_WORD_STOPLIST = {
    "and", "at", "for", "of", "the", "to", "with",
    "head", "chief", "officer", "officers", "director", "directors",
    "managing", "manager", "managers", "lead", "leads", "leader", "leaders",
    "president", "vice", "senior", "junior", "principal", "assistant",
    "executive", "executives", "sponsor", "sponsors", "stakeholder",
    "stakeholders", "contact", "contacts", "attendee", "attendees",
    "participant", "participants", "interviewee", "interviewees",
    "team", "teams", "department", "division", "unit", "role", "roles",
    "title", "titles", "name", "names", "unknown", "none", "various",
    "staff", "client", "customer", "customers", "member", "members",
    "board", "committee", "council", "office", "desk", "center", "centre",
    "operations", "technology", "digital", "product", "products",
    "marketing", "sales", "finance", "risk", "compliance", "audit", "legal",
    "strategy", "transformation", "innovation", "data", "engineering",
    "architecture", "security", "channel", "channels", "platform",
    "program", "programme", "project", "portfolio", "branch", "retail",
    "commercial", "corporate", "wealth", "payments", "lending", "deposits",
    "onboarding", "experience", "service", "services", "support",
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

# CLIENT_PROFILE.md-only: templates/client_profile.md's canonical "## Client
# Identity" section stores the client's legal name as a bare "- **Name:**"
# field (not "Client Name:"), e.g. "- **Name:** [Full legal name]". A bare
# "name" label is deliberately NOT added to _LABEL_LINE_RE above, which
# applies to every markdown document this hook reads (ENGAGEMENT_CONTEXT.md,
# engagement_intake.md, and any future doc type): those files use "Name:" as
# a generic section/field label too (e.g. "AE: [Name]", "CS: [Name]"), and
# enabling it everywhere would harvest product names, system names, and
# ordinary headings as deny-list terms — the same over-extraction class as
# finding 1 (711b56c). CLIENT_PROFILE.md is different: it is the
# client-identity document by definition, so its "**Name:**" field IS the
# client's name and nothing else. This regex is therefore only ever passed
# in for that one filename (see _resolve_deny_list).
_CLIENT_PROFILE_LABEL_LINE_RE = re.compile(
    r"^\s*[-*#]{0,3}\s*\**\s*"
    r"(?:name)"
    r"\s*\**\s*:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)
_PAREN_ACRONYM_RE = re.compile(r"\(([A-Z]{2,8})\)")
_ALLCAPS_TOKEN_RE = re.compile(r"\b[A-Z]{2,8}\b")
_HEADING_RE = re.compile(r"^\s*#{1,3}\s+(.+)$", re.MULTILINE)
_WORD_RE = re.compile(r"[A-Za-z]+")

# Unfilled template placeholder segments look like "[Full legal name]" or
# "[slug used in directory names, e.g., `navy_federal`]" — every unfilled
# field across templates/client_profile.md (and other templates) uses this
# convention. A label value that is nothing but a bracketed placeholder (or
# becomes empty once the placeholder text is removed) carries no real
# identifier and must not be mined for words/phrases/acronyms. Without this,
# "- **Name:** [Full legal name]" would harvest "Full", "legal", "name" as
# bare deny-list terms — "name" alone clears _single_word_ok's length floor
# and isn't in GENERIC_STOPLIST, so every query containing the ordinary word
# "name" would be denied (an exact repeat of finding 1).
_BRACKET_SEGMENT_RE = re.compile(r"\[[^\]]*\]")


def _single_word_ok(word):
    w = word.strip()
    if len(w) < 4:
        return False
    if w.lower() in GENERIC_STOPLIST:
        return False
    return True


def _add_term(terms, raw):
    t = (raw or "").strip().strip(".,;:()’'\"*_")
    if not t:
        return
    terms.add(t)


def _extract_terms_from_text(text, terms, label_res=(_LABEL_LINE_RE,)):
    # Explicit "Client:"/"Bank Name:"/... label lines. `label_res` is the
    # tuple of label regexes to run against this document; callers pass an
    # extra, more permissive regex only for CLIENT_PROFILE.md (see
    # _CLIENT_PROFILE_LABEL_LINE_RE above and _resolve_deny_list below) — the
    # default here keeps every other document scoped to the original,
    # narrower label set.
    for label_re in label_res:
        for m in label_re.finditer(text):
            # Strip markdown emphasis (*, _) in addition to whitespace before
            # any further processing. Without this, "- **Client Name:** X"
            # captures "** X" (the regex's own \**\s*:\s* only consumes
            # stars BEFORE the colon; the closing "**" of "**Client Name:**"
            # lands inside the captured value) and every downstream
            # heuristic below operates on junk. str.strip(chars) removes any
            # mix of the given chars from each end regardless of order, so
            # this is safe for a legitimate name that happens to start/end
            # with '*' or '_' — only the leading/trailing run is touched,
            # nothing interior.
            value = m.group(1).strip(" \t*_")

            # Skip unfilled template placeholders. Every unfilled field in
            # this repo's templates (templates/client_profile.md and
            # friends) is written as "[some description]" — e.g.
            # "- **Name:** [Full legal name]". Strip bracketed segments
            # before mining the value for terms; if nothing real is left,
            # this match carries no identifier and is skipped entirely (no
            # acronym, word, phrase, or ALL-CAPS extraction runs on it). This
            # also correctly handles a real value that merely contains an
            # incidental bracketed aside (e.g. "Acme Corp [confidential]")
            # by mining the non-bracketed remainder instead of discarding it.
            value = _BRACKET_SEGMENT_RE.sub(" ", value).strip()
            if not value:
                continue

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

            # Bare ALL-CAPS acronyms *within this label's value* (bank short
            # codes like "HNB", "BECU" written as "**Client:** HNB" with no
            # parentheses). Deliberately scoped to label-line values rather
            # than the whole document: a whole-document sweep of
            # \b[A-Z]{2,8}\b turns ordinary emphasis-caps prose ("ALL",
            # "NOT", "NEVER", "SME", ...) into client identifiers and makes
            # the gate unusable (see the mcp-query-guard finding this
            # fixed). Scoping to text that already passed a label-line gate
            # keeps the same false-positive discipline as the
            # acronym-in-parens path above.
            for tok in _ALLCAPS_TOKEN_RE.findall(cleaned):
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

    # Stakeholder names — the client's PEOPLE, not just its institution
    # (#209). Same document, separate shapes; see _extract_stakeholder_terms.
    _extract_stakeholder_terms(text, terms)


# --- stakeholder names (#209) ----------------------------------------------
#
# HAND-COPIED PARITY BLOCK. `scripts/pii/denylist.py` carries the identical
# logic (STAKEHOLDER_LABEL_LINE_RE / ROLE_WORD_STOPLIST /
# extract_stakeholder_terms) and `scripts/pii/drift_check.py` asserts both
# copies resolve IDENTICAL deny-lists. Change one, change the other.
#
# WHY IT EXISTS: security_protocol.md §5 covers "client/stakeholder
# identifier", and until #209 only the institution half was ever extracted.
# On the anonymisation side the same gap let a person's name in a markdown
# table cell reach the API in cleartext, because Presidio's PERSON recogniser
# is shape-sensitive (measured: `en_core_web_lg` tags "Aisha Rahman" in a
# table row as EVENT). A deny-list term is model- and shape-independent.
#
# WHY PHRASE-ONLY: a person contributes exactly ONE term, the full multi-word
# name as written — never its individual words. Surnames collide with
# ordinary English ("Price", "Cash", "Grant", "Bill", "Long", "Young") far
# harder than bank tokens do, and a bare single-word deny term derived from a
# name is the "denylist blocked the word 'all'" failure class returning. So
# stakeholder names neither bypass GENERIC_STOPLIST nor rely on it — the
# question is moot by construction.

_STAKEHOLDER_LABEL_LINE_RE = re.compile(
    r"^\s*[-*#]{0,3}\s*\**\s*"
    r"(?:(?:primary|key|main|client|executive)\s+contacts?"
    r"|contacts?"
    r"|(?:executive|client)\s+sponsors?"
    r"|sponsors?"
    r"|stakeholders?(?:\s+interviewed)?"
    r"|attendees?|interviewees?|participants?)"
    r"(?:\s*\([^)]*\))?"          # "- **Executive Sponsors (Client-Side):**"
    r"\s*\**\s*:\s*(.*)$",
    re.IGNORECASE,
)

# A markdown table is a person table when its FIRST column header names
# people. Header-driven, not section-driven, so CLIENT_PROFILE.md's
# engagement-history table (first column "Date") is never mistaken for one.
_PERSON_TABLE_HEADER_RE = re.compile(
    r"^(?:name(?:\s*/\s*role)?|full\s+name|stakeholders?|attendees?"
    r"|contacts?|participants?|interviewees?)$",
    re.IGNORECASE,
)
_TABLE_SEPARATOR_RE = re.compile(r"^[\s:\-|]+$")
_SUB_BULLET_RE = re.compile(r"^\s+[-*]\s+(.+)$")

# Splits a captured value at the first separator that introduces a job title
# or an aside. The dash form requires SURROUNDING SPACE so a hyphenated name
# ("Jean-Luc Marchand") is not cut in half.
_NAME_SEGMENT_RE = re.compile(r"[,;|]|\s+[\u2014\u2013-]\s+|\(")
_PERSON_TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z'\u2019.\-]*$")


def _stakeholder_value(raw):
    value = (raw or "").strip().strip(" \t*_")
    value = _BRACKET_SEGMENT_RE.sub(" ", value).strip()
    if not value:
        return ""
    return _NAME_SEGMENT_RE.split(value)[0].strip().strip(" \t*_.")


def _person_name_ok(name):
    if not name or len(name) > 60:
        return False
    tokens = name.split()
    if not 2 <= len(tokens) <= 5:
        return False
    if not (tokens[0][:1].isupper() and tokens[-1][:1].isupper()):
        return False
    for token in tokens:
        if not _PERSON_TOKEN_RE.match(token):
            return False
        word = token.strip(".'\u2019-").lower()
        if not word:
            return False
        if word in ROLE_WORD_STOPLIST or word in GENERIC_STOPLIST:
            return False
        if token.upper() in ACRONYM_STOPLIST:
            return False
    return True


def _add_person_term(terms, raw):
    name = _stakeholder_value(raw)
    if _person_name_ok(name):
        _add_term(terms, name)


def _extract_stakeholder_terms(text, terms):
    """Three shapes, all produced by this repo's own templates:
      1. a label line       - **Primary Contact:** Aisha Rahman, CFO
      2. a person table     | Name/Role | Department |  ->  first column
      3. sub-bullets under a stakeholder label whose own value is empty
    Line-based rather than one whole-document regex because shapes 2 and 3
    are stateful.
    """
    in_person_table = False
    in_sponsor_bullets = False

    for raw_line in text.splitlines():
        if not raw_line.strip():
            in_person_table = False
            in_sponsor_bullets = False
            continue

        match = _STAKEHOLDER_LABEL_LINE_RE.match(raw_line)
        if match:
            in_person_table = False
            value = _stakeholder_value(match.group(1))
            if value:
                _add_person_term(terms, value)
                in_sponsor_bullets = False
            else:
                in_sponsor_bullets = True
            continue

        stripped = raw_line.strip()
        if stripped.startswith("|"):
            in_sponsor_bullets = False
            if _TABLE_SEPARATOR_RE.match(stripped):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            first = cells[0] if cells else ""
            if not in_person_table:
                in_person_table = bool(_PERSON_TABLE_HEADER_RE.match(first))
                continue
            _add_person_term(terms, first)
            continue

        in_person_table = False
        if in_sponsor_bullets:
            bullet = _SUB_BULLET_RE.match(raw_line)
            if bullet:
                _add_person_term(terms, bullet.group(1))
                continue
            in_sponsor_bullets = False


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


class _ScanLimitExceeded(Exception):
    """Raised when MAX_FILES_SCANNED is hit. Past this point the deny-list is
    provably incomplete — some engagement document that could contain a
    client identifier was never read. Treated as fail-closed by the caller,
    same as any other read failure."""


def _read_bounded(path):
    """Read one of the named engagement documents this hook depends on for
    the deny-list (CLIENT_PROFILE.md / ENGAGEMENT_CONTEXT.md /
    engagement_intake.md). Deliberately does NOT catch OSError: an unreadable
    file here (permission-denied, gone mid-scan, ...) is indistinguishable
    from an empty one if swallowed, which would silently drop identifiers
    from a fail-closed gate. Let it propagate — _resolve_deny_list's own
    caller in main() already fails closed on any exception. Scoped
    deliberately to just these three filenames, not every file under
    engagements/, so an unrelated unreadable stray file elsewhere doesn't
    deny every query."""
    if _read_count[0] >= MAX_FILES_SCANNED:
        raise _ScanLimitExceeded(
            "MAX_FILES_SCANNED (%d) reached while scanning engagements/ — "
            "deny-list is incomplete" % MAX_FILES_SCANNED
        )
    _read_count[0] += 1
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        return fh.read(MAX_FILE_BYTES)


def _iter_doc_paths(client_dir, doc_name):
    """Recursively find every file named doc_name under client_dir. Replaces
    Path.rglob(), which silently skips a permission-denied subdirectory
    instead of raising (pathlib's internal scandir swallows OSError). A
    permission error partway through a client's engagement tree means the
    deny-list may be missing a document, so it must surface and fail closed
    rather than be swallowed — os.walk's onerror callback re-raises to make
    that happen."""

    def _onerror(err):
        raise err

    for dirpath, _dirnames, filenames in os.walk(str(client_dir), onerror=_onerror):
        if doc_name in filenames:
            yield Path(dirpath) / doc_name


def _scan_one_dir(client_dir, terms, mine_slug=True):
    """One directory's contribution. Mirrors
    `pii.denylist._scan_client_dir`; drift_check.py asserts parity."""
    if mine_slug:
        _extract_terms_from_slug(client_dir.name, terms)

    profile = client_dir / CLIENT_PROFILE_NAME
    if profile.is_file():
        # CLIENT_PROFILE.md is the one document scanned with the extra
        # bare-"Name:" label regex — see _CLIENT_PROFILE_LABEL_LINE_RE's
        # docstring for why this is scoped to this filename only.
        _extract_terms_from_text(
            _read_bounded(profile), terms,
            label_res=(_LABEL_LINE_RE, _CLIENT_PROFILE_LABEL_LINE_RE),
        )

    for doc_name in ENGAGEMENT_DOC_NAMES:
        for doc_path in _iter_doc_paths(client_dir, doc_name):
            _extract_terms_from_text(_read_bounded(doc_path), terms)


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
        staging = client_dir.name.lower() in SKIP_CLIENT_DIRS
        if staging:
            # `engagements/inputs/` and `engagements/outputs/` are shared
            # legacy staging: the directory itself is not a client and mining
            # its name would put "inputs"/"outputs" on the deny-list. But its
            # SUBDIRECTORIES are per-client, and skipping the whole tree meant
            # four real clients contributed NOTHING here — the gate was not
            # weakened for them, it was absent (2026-08-30 migration dry run).
            # Descend one level, documents only, never the name: those names
            # are `<datecode>_<Client>_<Geography-or-programme>` and mining
            # them drops the acronym clients while harvesting a Backbase
            # programme name. Kept byte-for-byte equivalent to
            # `pii.denylist._scan_client_dir(..., mine_slug=False)` —
            # `scripts/pii/drift_check.py` asserts the two produce identical
            # deny-lists.
            for staged in sorted(client_dir.iterdir()):
                if staged.is_dir() and not staged.name.startswith("."):
                    _scan_one_dir(staged, terms, mine_slug=False)
            continue

        _scan_one_dir(client_dir, terms, mine_slug=True)

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
