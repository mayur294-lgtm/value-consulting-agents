#!/usr/bin/env python3
"""
Engagement deny-list resolution — the client-identity term extractor.

WHY THIS MODULE EXISTS
  `.claude/hooks/mcp-query-guard.py` contains the original implementation of
  this extraction. Its own header marks the seam:

      >>> SEAM: a shared deny-list resolver arrives with the engine ticket
      >>> (#159).

  This is that resolver. `scripts/pii/engine.py` needs exactly the same
  notion of "what counts as a client identifier" that the MCP gate uses —
  solution-design-v6.md D3 makes the deny-list the PRIMARY client-identity
  detector, because Presidio has no reliable ORGANIZATION recognizer and the
  client's name is the single most important entity we have to hide.

  The logic below is a FAITHFUL PORT of the hook's, not a rewrite. Every
  guard here was added in response to a reproduced false positive or leak
  during the hook's adversarial review (711b56c, 7b91758). Read the comments
  before "simplifying" anything — several of them exist specifically to
  explain why a tempting simplification is wrong:

    - No whole-document ALL-CAPS sweep. It turned `ALL`, `NOT`, `NEVER`,
      `SME`, `MEDIUM` into "client identifiers" and denied ordinary queries.
      Acronyms come only from client-name CONTEXT: label-line values, paren
      acronyms in labels and in the first heading, and the directory slug.
    - Markdown emphasis is stripped from a captured label value, or
      `- **Client Name:** First Federal` leaks (the closing `**` lands
      inside the capture).
    - `[...]` segments are removed before mining, or an unfilled template
      field `- **Name:** [Full legal name]` harvests `Full`, `legal`, `name`.
    - Slug parts go through the same generic-word guard as prose, or the
      slug `bank_australia` adds the bare word `bank` to the deny-list.
    - A generic `**bold phrase**` heuristic was tried and DROPPED — it
      matched topic headings like `**Digital Onboarding**`.
    - Reads do not swallow `OSError`. A swallowed read error is
      indistinguishable from an empty file and silently drops identifiers
      from a gate whose whole job is to fail closed.
    - Stakeholder names (#209) are extracted as WHOLE multi-word phrases
      only, never decomposed into words. See `extract_stakeholder_terms`.

WHAT THIS MINES — CLIENT IDENTITY *AND* STAKEHOLDER NAMES
  Two extraction paths, deliberately different in shape:
    - `extract_terms_from_text` — the institution: labelled client/bank/
      organisation lines, paren and bare acronyms inside those values, the
      first heading's acronym. Admits individual WORDS via `_single_word_ok`.
    - `extract_stakeholder_terms` — the people: "Primary Contact:" style
      label lines, the first column of a person table, and sub-bullets under
      an "Executive Sponsors:" label. Admits ONLY the full multi-word name.
  Until #209 only the first existed, and the empty-list warning's promise
  ("no client *or stakeholder* names found") was half true.

WHY THE HOOK STILL HAS ITS OWN COPY
  The hook is deliberately self-contained: a module-level import that failed
  would raise before its `main()`'s try/except, and a PreToolUse hook that
  exits that way is treated as NON-blocking — i.e. fail-open, in a hook whose
  entire purpose is failing closed. Whether the hook adopts this module is a
  separate decision from landing it.

  Two copies that silently diverge is the failure mode that matters, so
  `scripts/pii/drift_check.py` asserts that this module and the hook produce
  IDENTICAL deny-lists for the same fixture. Change one, and that check tells
  you to change the other.

CONSTRAINTS (load-bearing)
  - Standard library only. No Presidio, no spaCy, no third-party imports.
  - Python 3.9 compatible. The system interpreter here is 3.9.6, hooks run
    under it, and `scripts/artifact_boundary.py` must stay importable there.
  - Fail-closed read semantics are preserved: `OSError` propagates and the
    scan limit raises, so callers keep the ability to fail closed.
"""
import os
import re
from pathlib import Path

__all__ = [
    "GENERIC_STOPLIST",
    "ACRONYM_STOPLIST",
    "ROLE_WORD_STOPLIST",
    "STAKEHOLDER_LABEL_LINE_RE",
    "extract_stakeholder_terms",
    "ENGAGEMENT_DOC_NAMES",
    "CLIENT_PROFILE_NAME",
    "SKIP_CLIENT_DIRS",
    "MAX_FILE_BYTES",
    "MAX_FILES_SCANNED",
    "ScanLimitExceeded",
    "LABEL_LINE_RE",
    "CLIENT_PROFILE_LABEL_LINE_RE",
    "extract_terms_from_text",
    "extract_terms_from_slug",
    "resolve_deny_list",
    "resolve_engagement_deny_list",
]

# Generic banking words that must NOT count as a client identifier on their
# own, even though they show up constantly in bank names ("First National
# Bank", "Pacific Community Credit Union", ...). Matched case-insensitively.
#
# This set doubles as the engine's allow-list (solution-design-v6.md §3,
# "Allow-list to stop over-redaction of generic banking words") — see
# engine.py, which passes it to AnalyzerEngine.analyze(allow_list=...).
GENERIC_STOPLIST = {
    "bank", "banking", "credit", "union", "first", "national", "federal",
    "united", "community", "citizens", "state", "financial", "savings",
    "trust", "group", "holdings", "capital", "mutual", "valley", "coast",
    "pacific", "fund", "society",
}

# Common short all-caps tokens that are NOT client identifiers, so an
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
# stakeholder path (`extract_stakeholder_terms`), because the columns and
# label lines that carry stakeholder names carry job titles just as often
# ("| Name/Role |" literally admits either). Without this, "Head of Digital
# Banking" in a Name/Role cell becomes a client-identity deny term and every
# document containing that ordinary phrase is shredded.
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


class ScanLimitExceeded(Exception):
    """Raised when MAX_FILES_SCANNED is hit. Past this point the deny-list is
    provably incomplete — some engagement document that could contain a
    client identifier was never read. Callers treat this as fail-closed, the
    same as any other read failure."""


# --- term extraction -------------------------------------------------------

LABEL_LINE_RE = re.compile(
    r"^\s*[-*#]{0,3}\s*\**\s*"
    r"(?:client(?:\s+name)?|bank(?:\s+name)?|institution|company|organi[sz]ation)"
    r"\s*\**\s*:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)

# CLIENT_PROFILE.md-only: templates/client_profile.md's canonical "## Client
# Identity" section stores the client's legal name as a bare "- **Name:**"
# field (not "Client Name:"), e.g. "- **Name:** [Full legal name]". A bare
# "name" label is deliberately NOT added to LABEL_LINE_RE above, which
# applies to every markdown document scanned (ENGAGEMENT_CONTEXT.md,
# engagement_intake.md, and any future doc type): those files use "Name:" as
# a generic section/field label too (e.g. "AE: [Name]", "CS: [Name]"), and
# enabling it everywhere would harvest product names, system names, and
# ordinary headings as deny-list terms — the same over-extraction class as
# the ALL-CAPS sweep. CLIENT_PROFILE.md is different: it is the
# client-identity document by definition, so its "**Name:**" field IS the
# client's name and nothing else. This regex is therefore only ever passed
# in for that one filename.
CLIENT_PROFILE_LABEL_LINE_RE = re.compile(
    r"^\s*[-*#]{0,3}\s*\**\s*"
    r"(?:name)"
    r"\s*\**\s*:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)
_PAREN_ACRONYM_RE = re.compile(r"\(([A-Z]{2,8})\)")
_ALLCAPS_TOKEN_RE = re.compile(r"\b[A-Z]{2,8}\b")
_HEADING_RE = re.compile(r"^\s*#{1,3}\s+(.+)$", re.MULTILINE)
# Unicode Latin, not ASCII. `[A-Za-z]` silently shreds every accented name:
# measured 2026-08-30 on the real extractors, "Länsförsäkringar" yielded only
# "kringar", "Bagócs" yielded NOTHING, and "Åland" yielded "land" — which
# under-detects the client AND emits a generic term that over-blocks. The client
# name is the single most important entity we hide (solution-design-v6 D3), so an
# ASCII class here is a silent, total miss for a whole class of client.
#
# Explicit ranges rather than \w or a `regex` dependency: this module is
# stdlib-only and 3.9-clean by contract (the hook copy cannot import anything),
# and \w would admit digits and every non-Latin script. Covers Latin-1
# Supplement, Latin Extended-A and Latin Extended-B — French, Spanish, German,
# Portuguese, Nordic, Polish, Czech, Turkish. D7 in the Sinhala/Devanagari sense
# is untouched: non-Latin script remains out of scope.
_LATIN = "A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF\u0100-\u017F\u0180-\u024F"
_WORD_RE = re.compile("[" + _LATIN + "]+")

# Unfilled template placeholder segments look like "[Full legal name]" or
# "[slug used in directory names, e.g., `navy_federal`]" — every unfilled
# field across templates/client_profile.md (and other templates) uses this
# convention. A label value that is nothing but a bracketed placeholder (or
# becomes empty once the placeholder text is removed) carries no real
# identifier and must not be mined for words/phrases/acronyms. Without this,
# "- **Name:** [Full legal name]" would harvest "Full", "legal", "name" as
# bare deny-list terms — "name" alone clears _single_word_ok's length floor
# and isn't in GENERIC_STOPLIST, so every text containing the ordinary word
# "name" would be treated as carrying the client's identity.
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


def extract_terms_from_text(text, terms, label_res=(LABEL_LINE_RE,)):
    """Mine one markdown document for client-identity terms, adding them to
    the `terms` set in place.

    `label_res` is the tuple of label regexes to run against this document.
    Callers pass the extra, more permissive CLIENT_PROFILE_LABEL_LINE_RE only
    for CLIENT_PROFILE.md; the default keeps every other document scoped to
    the original, narrower label set.
    """
    for label_re in label_res:
        for m in label_re.finditer(text):
            # Strip markdown emphasis (*, _) in addition to whitespace before
            # any further processing. Without this, "- **Client Name:** X"
            # captures "** X" (the regex's own \**\s*:\s* only consumes stars
            # BEFORE the colon; the closing "**" of "**Client Name:**" lands
            # inside the captured value) and every downstream heuristic below
            # operates on junk. str.strip(chars) removes any mix of the given
            # chars from each end regardless of order, so this is safe for a
            # legitimate name that happens to start/end with '*' or '_' —
            # only the leading/trailing run is touched, nothing interior.
            value = m.group(1).strip(" \t*_")

            # Skip unfilled template placeholders. Every unfilled field in
            # this repo's templates (templates/client_profile.md and friends)
            # is written as "[some description]" — e.g. "- **Name:** [Full
            # legal name]". Strip bracketed segments before mining the value
            # for terms; if nothing real is left, this match carries no
            # identifier and is skipped entirely (no acronym, word, phrase,
            # or ALL-CAPS extraction runs on it). This also correctly handles
            # a real value that merely contains an incidental bracketed aside
            # (e.g. "Acme Corp [confidential]") by mining the non-bracketed
            # remainder instead of discarding it.
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
            # the gate unusable. Scoping to text that already passed a
            # label-line gate keeps the same false-positive discipline as the
            # acronym-in-parens path above.
            for tok in _ALLCAPS_TOKEN_RE.findall(cleaned):
                if tok in ACRONYM_STOPLIST:
                    continue
                if tok.lower() in GENERIC_STOPLIST:
                    continue
                _add_term(terms, tok)

    # NOTE: a generic "**bold phrase**" heuristic was tried and dropped —
    # engagement docs bold topic/section headings just as often as names
    # (e.g. "**Digital Onboarding**" as a section title), and that produced a
    # real false positive that would have blocked every query mentioning a
    # common domain term. Bold text alone is not a reliable name signal; only
    # explicitly-labelled fields and bare acronyms are used.

    # First heading of the doc often carries the client name.
    m = _HEADING_RE.search(text)
    if m:
        heading = m.group(1).strip()
        for acr in _PAREN_ACRONYM_RE.findall(heading):
            if acr not in ACRONYM_STOPLIST:
                _add_term(terms, acr)

    # Stakeholder names — the client's PEOPLE, not just its institution
    # (#209). Same document, separate shapes; see extract_stakeholder_terms.
    extract_stakeholder_terms(text, terms)


# --- stakeholder names (#209) ----------------------------------------------
#
# WHY THIS PATH EXISTS
#   Presidio's PERSON recogniser is shape-sensitive: measured on the eval
#   fixture, `en_core_web_lg` tags "Aisha Rahman" inside a markdown table row
#   as EVENT — not PERSON, and (contrary to what engine.py and this repo's
#   backlog claimed for three tickets) not ORGANIZATION either. Enabling
#   Presidio's ORGANIZATION entity was MEASURED and does not catch it at all,
#   while it does strip "Backbase" and "Salesforce". So the ORGANIZATION
#   trade-off was never the reason the name leaked, and there is no trade-off
#   to make: the deny-list is the fix, exactly as engine.py's own
#   "MEASURED DETECTION LIMITS" note already called it.
#
#   A deny-list term is model-independent and shape-independent — it fires in
#   a table cell, a bullet, prose and a speaker label alike — which is why
#   this closes the gap in every document shape rather than one of them.
#
# WHY THIS IS PHRASE-ONLY, AND WHY IT DOES NOT BYPASS GENERIC_STOPLIST
#   Prose/label extraction admits individual WORDS above (`_single_word_ok`,
#   length floor + GENERIC_STOPLIST). A person's name must not go through
#   that path, in either direction:
#     - it must not bypass the stoplist, and
#     - it must not use it either.
#   Surnames collide with ordinary consulting English far harder than bank
#   tokens do — "Price", "Cash", "Grant", "Bill", "Long", "Young", "Brown"
#   are all real surnames and all appear in ordinary ROI prose. A single-word
#   deny term derived from a person's name is the "denylist blocked the word
#   'all'" failure class with a new coat of paint. So a stakeholder
#   contributes exactly ONE term: the full multi-word name as written. That
#   is sufficient — the shapes that defeat the NER (table cell, bullet,
#   label line) all carry the full name — and it makes the stoplist question
#   moot by construction rather than by exemption.
#
# LIMITATION, stated rather than hidden: `_PERSON_TOKEN_RE` is ASCII-only,
# like this module's existing `_WORD_RE`. A stakeholder whose name is written
# in a non-Latin script is not extracted here.

STAKEHOLDER_LABEL_LINE_RE = re.compile(
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
# people. `templates/inputs/engagement_intake.md` uses "| Name/Role |";
# `templates/inputs/transcript_interpretation_guide.md` uses "| Stakeholder |".
# Header-driven, not section-driven, so CLIENT_PROFILE.md's engagement-history
# table (first column "Date") is never mistaken for one.
_PERSON_TABLE_HEADER_RE = re.compile(
    r"^(?:name(?:\s*/\s*role)?|full\s+name|stakeholders?|attendees?"
    r"|contacts?|participants?|interviewees?)$",
    re.IGNORECASE,
)
_TABLE_SEPARATOR_RE = re.compile(r"^[\s:\-|]+$")
_SUB_BULLET_RE = re.compile(r"^\s+[-*]\s+(.+)$")

# Splits a captured value at the first separator that introduces a job title
# or an aside: "Aisha Rahman, Chief Financial Officer", "Jane Doe — CFO",
# "Ravi Menon (Group CIO)". The dash form requires SURROUNDING SPACE so a
# hyphenated name ("Jean-Luc Marchand") is not cut in half.
_NAME_SEGMENT_RE = re.compile(r"[,;|]|\s+[\u2014\u2013-]\s+|\(")
_PERSON_TOKEN_RE = re.compile("^[" + _LATIN + "][" + _LATIN + "'\u2019.\\-]*$")


def _stakeholder_value(raw):
    """Reduce one captured cell/bullet/label value to its name segment."""
    value = (raw or "").strip().strip(" \t*_")
    # Unfilled template placeholders carry no identifier — same rule, and the
    # same regex, as the label path above. "| [Name — Title] |" -> nothing.
    value = _BRACKET_SEGMENT_RE.sub(" ", value).strip()
    if not value:
        return ""
    return _NAME_SEGMENT_RE.split(value)[0].strip().strip(" \t*_.")


def _person_name_ok(name):
    """True only for something that reads as a written personal name.

    Multi-word by requirement (see the phrase-only rationale above), so a
    lone token — "TBD", "Finance", a stray heading word — can never become a
    deny term.
    """
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


def extract_stakeholder_terms(text, terms):
    """Mine one markdown document for STAKEHOLDER names, adding them to
    `terms` in place. Three shapes, all of them ones this repo's own
    templates produce:

      1. a label line       - **Primary Contact:** Aisha Rahman, CFO
      2. a person table     | Name/Role | Department |  ->  first column
      3. sub-bullets under a stakeholder label whose own value is empty
                            - **Executive Sponsors (Client-Side):**
                              - Aisha Rahman — CFO

    Line-based rather than one whole-document regex because shapes 2 and 3
    are stateful: a table row only means "person" once its header said so,
    and a sub-bullet only means "person" under a label that opened a list.
    """
    in_person_table = False
    in_sponsor_bullets = False

    for raw_line in text.splitlines():
        if not raw_line.strip():
            in_person_table = False
            in_sponsor_bullets = False
            continue

        match = STAKEHOLDER_LABEL_LINE_RE.match(raw_line)
        if match:
            in_person_table = False
            value = _stakeholder_value(match.group(1))
            if value:
                _add_person_term(terms, value)
                in_sponsor_bullets = False
            else:
                # "- **Executive Sponsors (Client-Side):**" — the names are
                # on the indented bullets that follow.
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
                # A table's first row is its header. Only a header naming
                # people opens the table for extraction; anything else
                # leaves it closed, so an ordinary data table is skipped.
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


def extract_terms_from_slug(slug, terms):
    """Mine a client directory slug (e.g. "hnb", "bank_australia") for terms,
    adding them to `terms` in place."""
    # Individual parts go through the SAME generic-word guard as prose
    # extraction. Without this, a slug like "bank_australia" would add the
    # bare word "bank" to the deny-list and block nearly every banking query
    # anyone locally checked out that engagement ever sends.
    for part in re.split(r"[_\-]+", slug):
        if _single_word_ok(part):
            _add_term(terms, part)
    # The joined form (e.g. "hnb", "bankaustralia") is added unconditionally
    # and without the length floor: concatenating removes the "common English
    # word" collision risk that the length/stoplist guard exists for, and
    # this is also how a short bare-acronym client slug (e.g. a directory
    # literally named "hnb") becomes a deny-list term even with no markdown
    # docs present yet.
    joined = slug.replace("_", "").replace("-", "")
    if len(joined) >= 2:
        _add_term(terms, joined)


# --- bounded, fail-closed reads --------------------------------------------

class _ScanBudget(object):
    """Per-resolve read budget.

    The hook keeps this as a module-level counter because it resolves exactly
    once per process. A library is called repeatedly in one process, so the
    budget is per-call state instead — same semantics (MAX_FILES_SCANNED
    documents per resolution), no cross-call leakage.
    """

    __slots__ = ("count", "limit")

    def __init__(self, limit=MAX_FILES_SCANNED):
        self.count = 0
        self.limit = limit


def _read_bounded(path, budget):
    """Read one of the named engagement documents the deny-list depends on
    (CLIENT_PROFILE.md / ENGAGEMENT_CONTEXT.md / engagement_intake.md).

    Deliberately does NOT catch OSError: an unreadable file here
    (permission-denied, gone mid-scan, ...) is indistinguishable from an empty
    one if swallowed, which would silently drop identifiers from a
    fail-closed gate. Let it propagate — callers that need to fail closed
    depend on seeing it. Scoped deliberately to just these filenames, not
    every file under engagements/, so an unrelated unreadable stray file
    elsewhere doesn't take the whole resolution down.
    """
    if budget.count >= budget.limit:
        raise ScanLimitExceeded(
            "MAX_FILES_SCANNED (%d) reached while scanning engagements/ — "
            "deny-list is incomplete" % budget.limit
        )
    budget.count += 1
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        return fh.read(MAX_FILE_BYTES)


def _iter_doc_paths(client_dir, doc_name):
    """Recursively find every file named doc_name under client_dir.

    Replaces Path.rglob(), which silently skips a permission-denied
    subdirectory instead of raising (pathlib's internal scandir swallows
    OSError). A permission error partway through a client's engagement tree
    means the deny-list may be missing a document, so it must surface rather
    than be swallowed — os.walk's onerror callback re-raises to make that
    happen.
    """

    def _onerror(err):
        raise err

    for dirpath, _dirnames, filenames in os.walk(str(client_dir), onerror=_onerror):
        if doc_name in filenames:
            yield Path(dirpath) / doc_name


def _scan_client_dir(client_dir, terms, budget, mine_slug=True):
    """Extract every identifier term a single client directory contributes:
    its slug, its CLIENT_PROFILE.md, and every ENGAGEMENT_CONTEXT.md /
    inputs/engagement_intake.md anywhere beneath it.

    `mine_slug=False` scans the DOCUMENTS only. Used for the per-client
    subdirectories of the shared staging trees, whose names are not client
    slugs but `<datecode>_<Client>_<Geography-or-programme>` — mining those
    produces the wrong terms in both directions. Measured on the live tree:
    the two acronym clients yield NOTHING (`_single_word_ok` has a four-
    character floor, so `BSP` and `HNB` are dropped), while the harvest DOES
    include `Ignite` — a Backbase programme name, which as a deny term would
    block ordinary product queries — plus geography, `cortex`, `ontology` and
    a consultant's own first name. A profile inside the directory yields the
    acronym correctly and yields nothing else, so that is the supported
    source; see `resolve_deny_list`.
    """
    if mine_slug:
        extract_terms_from_slug(client_dir.name, terms)

    profile = client_dir / CLIENT_PROFILE_NAME
    if profile.is_file():
        # CLIENT_PROFILE.md is the one document scanned with the extra
        # bare-"Name:" label regex — see CLIENT_PROFILE_LABEL_LINE_RE's
        # comment for why this is scoped to this filename only.
        extract_terms_from_text(
            _read_bounded(profile, budget), terms,
            label_res=(LABEL_LINE_RE, CLIENT_PROFILE_LABEL_LINE_RE),
        )

    for doc_name in ENGAGEMENT_DOC_NAMES:
        for doc_path in _iter_doc_paths(client_dir, doc_name):
            extract_terms_from_text(_read_bounded(doc_path, budget), terms)


def resolve_deny_list(project_dir):
    """Aggregate client/stakeholder identifier terms across every engagement
    found locally under <project_dir>/engagements/. Returns a set of terms.

    This is the whole-repo resolution the MCP query gate uses: there is no
    first-class "which engagement is this session working on" signal, so
    every locally-present engagement contributes. `engagements/` is gitignored
    and machine-local, so a checkout typically holds only the engagements one
    consultant is actually working.

    Raises on any unexpected error (OSError from an unreadable document,
    ScanLimitExceeded) so the caller can fail closed. An EMPTY return is not
    an error — it means "nothing to check against", which callers handle by
    warning rather than blocking.
    """
    terms = set()
    root = Path(project_dir) / "engagements"
    if not root.is_dir():
        return terms

    budget = _ScanBudget()
    for client_dir in sorted(root.iterdir()):
        if not client_dir.is_dir():
            continue
        if client_dir.name.startswith("."):
            continue
        if client_dir.name.lower() in SKIP_CLIENT_DIRS:
            # `engagements/inputs/` and `engagements/outputs/` are shared
            # legacy staging, so the directory ITSELF is not a client and must
            # not be mined — that would put the words "inputs" and "outputs"
            # on the deny-list and block most ordinary queries.
            #
            # But their SUBDIRECTORIES are per-client, and skipping the whole
            # tree meant four real clients contributed NOTHING to the
            # deny-list: the outbound MCP gate was not weakened for them, it
            # was absent (found by the 2026-08-30 migration dry run). Descend
            # one level and scan each subdirectory's DOCUMENTS — never its
            # name, for the reasons in `_scan_client_dir`.
            for staged in sorted(client_dir.iterdir()):
                if staged.is_dir() and not staged.name.startswith("."):
                    _scan_client_dir(staged, terms, budget, mine_slug=False)
            continue
        _scan_client_dir(client_dir, terms, budget)

    return terms


def _client_dir_for(engagement_dir):
    """Locate the client-level directory for an engagement directory.

    Layout is engagements/<client>/<YYYY-MM_domain_type>/, so the client
    directory is normally the parent. Two shapes are tolerated:
      - <engagement_dir>'s parent is named "engagements" -> the engagement
        directory IS the client directory (a flat engagement with no
        per-engagement subdirectory)
      - otherwise -> the parent is the client directory
    Returns None when the parent is not a usable directory.
    """
    engagement_dir = Path(engagement_dir)
    parent = engagement_dir.parent
    if parent.name.lower() == "engagements":
        return engagement_dir
    if parent.is_dir():
        return parent
    return None


def resolve_engagement_deny_list(engagement_dir, client_slug=None):
    """Resolve the deny-list for ONE engagement — what the anonymisation
    engine uses (solution-design-v6.md, "Deny-list sources").

    Sources, in the order the design doc lists them:
      - <engagement_dir>/inputs/engagement_intake.md
      - <engagement_dir>/ENGAGEMENT_CONTEXT.md
      - CLIENT_PROFILE.md — at the client level, and at the engagement level
        if one is kept there
      - the client slug (the client directory name, or `client_slug` when the
        caller has a better one — e.g. resolved out of .engagement_map.json
        once opaque engagement IDs land)

    Same fail-closed read semantics as resolve_deny_list: OSError and
    ScanLimitExceeded propagate. Returns a (possibly empty) set of terms.
    """
    engagement_dir = Path(engagement_dir)
    terms = set()
    budget = _ScanBudget()

    client_dir = _client_dir_for(engagement_dir)
    slug = client_slug if client_slug else (client_dir.name if client_dir else engagement_dir.name)
    if slug:
        extract_terms_from_slug(slug, terms)

    profile_candidates = [engagement_dir / CLIENT_PROFILE_NAME]
    if client_dir is not None and client_dir != engagement_dir:
        profile_candidates.append(client_dir / CLIENT_PROFILE_NAME)
    for profile in profile_candidates:
        if profile.is_file():
            extract_terms_from_text(
                _read_bounded(profile, budget), terms,
                label_res=(LABEL_LINE_RE, CLIENT_PROFILE_LABEL_LINE_RE),
            )

    for doc in (
        engagement_dir / "inputs" / "engagement_intake.md",
        engagement_dir / "ENGAGEMENT_CONTEXT.md",
    ):
        if doc.is_file():
            extract_terms_from_text(_read_bounded(doc, budget), terms)

    return terms
