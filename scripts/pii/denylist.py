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
_WORD_RE = re.compile(r"[A-Za-z]+")

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


def _scan_client_dir(client_dir, terms, budget):
    """Extract every identifier term a single client directory contributes:
    its slug, its CLIENT_PROFILE.md, and every ENGAGEMENT_CONTEXT.md /
    inputs/engagement_intake.md anywhere beneath it."""
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
