#!/usr/bin/env python3
"""
Presidio detection + reversible pseudonymisation — the PII engine.

WHAT THIS IS
  The detection and anonymisation core described in PRD v6 §2 and
  solution-design-v6.md D1/D2/D3. `scripts/anonymize_transcript.py` keeps its
  CLI and its four public signatures and delegates here (D1) — that is what
  makes rollback a single revert.

WHAT DETECTS THE CLIENT'S NAME (read this before describing the system)
  **The deny-list does. Not Presidio.** (D3.)

  Presidio has no reliable ORGANIZATION recogniser, and the client's own name
  is the single most important entity we have to hide. So `scripts/pii/
  denylist.py` resolves client-identity terms out of the engagement's own
  documents and they are wired in here as a Presidio deny-list recogniser
  emitting a `CLIENT` entity at score 1.0. Presidio contributes NER for
  people and validated patterns for emails/phones/IDs — real, and a large
  improvement on five hand-rolled regexes — but it does not find the client.

  Never describe this internally as "Presidio detects PII for us." The
  observed failure this PRD exists to fix was an empty name list silently
  producing vacuous scrubbing, and that failure lives entirely on the
  deny-list side. Hence the mandatory, loud, NON-BLOCKING warning when the
  deny-list resolves empty (see `_warn_empty_deny_list`).

PLACEHOLDER CONVENTION — `<ENTITY_N>`, never `[CLIENT]` (D2)
  `[CLIENT]` was simultaneously a PII placeholder AND a filename/prose
  template token: `[CLIENT]_Business_Case_Questionnaire.xlsx` appears in five
  components, `"[Client]'s path from X to Y"` in `narrative-assembler`,
  `| [Client] |` in `market-context-researcher`. De-anonymisation is an
  unguarded string replace, so the old convention actively rewrote those
  templates. Angle brackets end the collision.

  Legacy `[X-REDACTED]` placeholders and flat `{placeholder: value}` mappings
  still restore, indefinitely — see `flatten_mapping`. Mappings on disk are
  data, and a consultant with a six-month-old engagement must still be able
  to produce a client-ready deliverable. We READ both shapes and WRITE only
  the v2 nested-by-entity-type shape.

NUMBERING IS PRESIDIO'S, NOT OURS
  Same value -> same placeholder, consistently, across every file in a run.
  That comes from Presidio's own pseudonymisation sample: the
  `InstanceCounterAnonymizer` / `InstanceCounterDeanonymizer` operator pair
  below, sharing one `entity_mapping` dict. PR #129 hand-built this and was
  closed for exactly that reason — it reimplemented an upstream-supported
  feature. The `encrypt` operator is deliberately NOT used: it emits
  ciphertext blobs the model cannot reason about, which breaks intent I2
  (agents must be able to work in placeholders).

  ⚠️ **NOT THREAD-SAFE.** The shared `entity_mapping` dict is mutated during
  `operate()` with no locking — this is documented upstream and is why PRD
  v6 §8 records the constraint. Anonymisation must stay SEQUENTIAL.
  `orchestrate.py`'s `step_discovery` is sequential today, and Block A's five
  parallel agents operate on already-anonymised text, so nothing currently
  violates this. Do not parallelise anonymisation without replacing the
  operator with a locked or per-worker variant.

MEASURED DETECTION LIMITS (know these before quoting coverage)
  Deny-list entities (the client's name and short forms) and validated
  patterns (email, phone, account/ID numbers, IBAN, card) score 8/8 on the
  build fixture set and are model-independent.

  PERSON is different, and the shape of the document matters more than the
  model. Measured on 30 names x 5 document shapes with `en_core_web_lg`:

      prose 30/30 · speaker-line 30/30 · attendee-bullet 26/30 ·
      "**Primary Contact:**" label 26/30 · markdown table 25/30

  The misses are spaCy's, not this module's: in a markdown table cell
  `| Aisha Rahman | CFO |` the name is not tagged PERSON, and in
  `- Aisha Rahman, Head of ...` it is not tagged at all.

  ⚠️ CORRECTION (#209). This note used to say spaCy tags the table-cell name
  ORG, and that enabling ORGANIZATION would therefore catch it at the cost of
  stripping "Backbase"/"Temenos" — an unaffordable trade, but a trade. That
  was repeated verbatim into `:222` below, into the eval rubric and into the
  backlog, and it was FALSE IN BOTH HALVES. Measured on the eval fixture with
  `en_core_web_lg`:
    - spaCy tags "Aisha Rahman" in that table row **EVENT**, not ORG (in the
      row read in isolation it is even tagged PERSON — the miss comes from
      whole-document context, which is why single-line probes disagree);
    - enabling ORGANIZATION does **not** catch the name at all, and DOES
      strip "Backbase" and "Salesforce".
  So there was never a trade-off: ORGANIZATION is full cost, zero benefit.
  It stays out of DEFAULT_ENTITIES, but for that reason — not for a
  detection benefit it does not have.

  The real fix — the one this note has always named — is STAKEHOLDER names on
  the deny-list the way client names already are, which is what the
  empty-list warning below promises ("No client or stakeholder names
  found ..."). #209 implements it: `denylist.extract_stakeholder_terms`
  mines them from CLIENT_PROFILE.md / engagement_intake.md /
  ENGAGEMENT_CONTEXT.md, they arrive here through the same deny-list
  recogniser at score 1.0, and a deny-list term is model- and
  shape-independent — so it fires in a table cell, a bullet, prose and a
  speaker label alike. The extraction is phrase-only (a person contributes
  their full name, never its individual words) precisely so it cannot
  reintroduce the false-positive classes the MCP gate acquired the first
  time; see that function's own rationale.

INTERNAL-DOMAIN EMAILS — WHY THERE ARE TWO EMAIL RECOGNIZERS (#181 leak fix)
  Presidio's built-in `EmailRecognizer` validates the matched domain with
  `tldextract`, which checks against the real, registered public-suffix
  list. That is correct for the open internet and wrong for engagement
  material: `.internal`, `.corp`, `.local`, `.lan`, `.intranet`, `.priv`,
  `.home` are the standard internal domains at essentially every bank, and
  `.test` / `.example` / `.invalid` are the RFC 2606 reserved names people
  paste into a screenshot or a Word doc. None of those resolve on the real
  DNS root, so `tldextract` rejects them, `validate_result` returns False,
  and the built-in recognizer silently drops the match — an internal staff
  address then reaches the API in cleartext with zero warning. This was
  found on a REAL document (an internal-domain email survived a DOCX ingest
  that correctly redacted the person's name next to it).

  The fix is `_InternalDomainEmailRecognizer`, a second PatternRecognizer
  also emitting `EMAIL_ADDRESS`, that detects on SHAPE
  (`local-part@domain.tld-like-token`) instead of TLD registration. It
  reuses `EmailRecognizer.PATTERNS` — the built-in's own regex, unmodified,
  imported not copied — so it only ever proposes a span the built-in would
  also have proposed; it changes which spans are ACCEPTED, never which are
  found. `validate_result` accepts when the final dot-label reads as a
  plausible TLD token (`^[A-Za-z]{2,24}$`) — alphabetic, no digits. That one
  condition is deliberately narrow:
    - it catches every internal/reserved TLD above (all pure alphabetic)
      and real multi-label suffixes like `.co.uk` (final label "uk" is
      alphabetic) with no separate case needed;
    - it REJECTS `pkg@1.2.3` (npm-style version pin — final label "3" is
      numeric) and IP-shaped hosts, which is what keeps this a PII
      recognizer and not a generic "any @ and a dot" matcher. A denylist
      that blocked the word "all" is exactly the failure class this guards
      against — see evals'
      `internal_domain_email_redacted_no_over_detection` check.
    - it does NOT try to distinguish "person@host.example" appearing after
      `scp` in a shell one-liner from a real address — that string is
      shape-identical to an internal-domain email and Presidio has no way
      to know it followed `scp`. Redacting it is the conservative, correct
      call for a PII scrubber (a false positive there costs nothing — the
      placeholder round-trips back to the exact original text — while a
      false negative on a real staff email is the leak this exists to
      close).

  Both recognizers are registered on the SAME shared AnalyzerEngine (see
  `_get_analyzer`), so on a real-TLD address they both fire on the identical
  span with identical score (Presidio bumps a validated pattern's score to
  1.0 — see `PatternRecognizer.__analyze_patterns`), and Presidio's own
  `EntityRecognizer.remove_duplicates` — same entity type, same start/end —
  collapses them to ONE result before `analyze()` ever returns. There is no
  double placeholder, no second pass, and no anonymizer-side special
  casing: this is standard Presidio overlap resolution, not something this
  module implements. Verified empirically (not just reasoned about) against
  every case in the module's leak report before this landed.

LOCAL ONLY
  In-process, no network at analysis time. Presidio's Docker/HTTP deployment
  mode is explicitly rejected (PRD §6): a synchronous PreToolUse guard cannot
  depend on a container being up.

INTERPRETER
  Presidio needs Python 3.10-3.13 and lives in `.venv` (see
  `scripts/setup_pii.sh`, solution-design-v6.md D8/D12). The system
  interpreter here is 3.9.6. Importing THIS module under 3.9 fails, by
  design — which is why `scripts/pii/__init__.py` resolves it lazily and
  `scripts/pii/denylist.py` is stdlib-only.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import EmailRecognizer
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import Operator, OperatorType

from . import denylist as _denylist

__all__ = [
    "CLIENT_ENTITY",
    "DEFAULT_ENTITIES",
    "DEFAULT_SPACY_MODEL",
    "PLACEHOLDER_RE",
    "LEGACY_PLACEHOLDER_RE",
    "EMPTY_DENY_LIST_WARNING",
    "InstanceCounterAnonymizer",
    "InstanceCounterDeanonymizer",
    "PIISession",
    "anonymize_text",
    "deanonymize_text",
    "build_mapping_file",
    "flatten_mapping",
    "resolve_spacy_model",
]

# The entity type the engagement deny-list recogniser emits. Distinct from
# Presidio's own ORGANIZATION (which we do not enable — see DEFAULT_ENTITIES)
# so a client match is always attributable to the deny-list, never to NER.
CLIENT_ENTITY = "CLIENT"

# spaCy model. D10 asked whether ~12 MB `en_core_web_sm` could replace the
# ~400 MB `en_core_web_lg` — because D3 means the DENY-LIST, not the NER
# model, carries client identity, so the model only has to find people. It
# was decided on measurement, not on the plausibility of that argument.
#
# Same 30 person names x 5 realistic document shapes (prose, attendee bullet,
# markdown table, speaker line, "**Primary Contact:**" label), plus the same
# 8 identifier/deny-list cases and 6 over-redaction guards:
#
#   model            prose  bullet table  speaker label  PERSON total  ID/CLIENT
#   en_core_web_sm   26/30  11/30  25/30  26/30   20/30  108/150 (72%)   8/8
#   en_core_web_lg   30/30  26/30  25/30  30/30   26/30  137/150 (91%)   8/8
#
# `sm` misses 42 person names to `lg`'s 13 — worst on the attendee-bullet
# shape (11/30 vs 26/30), which is exactly how discovery transcripts and
# intake documents list stakeholders. Identifier patterns and the deny-list
# are model-independent, as predicted: both score 8/8, and neither
# over-redacts. First-load cost is 0.23s vs 0.68s; per-document scan time is
# identical (0.79s for the corpus). So the download size is the only thing
# `sm` wins, and a privacy control that lets one stakeholder name in three
# through is not a trade worth 380 MB.
#
# DECISION: stay on en_core_web_lg. requirements.txt and setup_pii.sh are
# unchanged. Revisit only with a new measurement.
#
# Override for a one-off experiment with CORTEX_SPACY_MODEL — that is how the
# comparison above was run.
DEFAULT_SPACY_MODEL = "en_core_web_lg"

# Entity types we anonymise. This is an explicit ALLOW-set, not "everything
# Presidio supports", because several supported entities are load-bearing
# business content in a value-consulting deliverable and redacting them would
# destroy the analysis:
#
#   ORGANIZATION - MEASURED (#209), not assumed: enabling it strips
#                  "Backbase" and "Salesforce" — which README standards
#                  explicitly KEEP — and catches the table-cell person name
#                  it was long believed to catch NOT AT ALL (spaCy tags that
#                  name EVENT, not ORG; "Temenos" survives either way). Full
#                  cost, zero benefit. Per D3 the client's own name comes
#                  from the deny-list, and per #209 so do stakeholder names,
#                  so there is nothing left for an ORG recogniser to buy.
#                  See MEASURED DETECTION LIMITS above for the correction.
#   DATE_TIME    - dates and periods drive every ROI model.
#   LOCATION     - "South Asia", "Australia" are the market context; spaCy
#                  flags every country and city mentioned.
#   NRP / AGE    - demographic context used in segment analysis.
#   URL          - the URL recogniser partial-matches inside email local
#                  parts (it reads "p.na" out of "p.nair@..."), which would
#                  leave the rest of the address in cleartext. Client domains
#                  are covered anyway: the deny-list matches the client's
#                  name inside "zzzclient.com" on a \\W boundary.
#
# Everything below is either an identity or a validated identifier pattern.
DEFAULT_ENTITIES: Tuple[str, ...] = (
    CLIENT_ENTITY,
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "IBAN_CODE",
    "CRYPTO",
    "IP_ADDRESS",
    "MEDICAL_LICENSE",
    "UK_NHS",
    "US_SSN",
    "US_ITIN",
    "US_PASSPORT",
    "US_BANK_NUMBER",
    "US_DRIVER_LICENSE",
)

# Below this, Presidio emits pure noise (US_DRIVER_LICENSE fires at 0.01 on
# any 10-digit number). Presidio filters with `>=`, so 0.35 keeps the
# lowest-confidence signal we actually want (an un-contextualised phone
# number scores 0.4) and drops the rest.
DEFAULT_SCORE_THRESHOLD = 0.35

# v2 placeholders: <PERSON_1>, <EMAIL_ADDRESS_12>, <CLIENT_2>.
PLACEHOLDER_RE = re.compile(r"<[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_\d+>")
# v1/legacy placeholders: [CLIENT], [CLIENT-ABBR], [PERSON-1], [EMAIL-REDACTED].
LEGACY_PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*\]")

# ux-design-v6.md "Error States" -> "No names configured". Copy rules apply:
# no tool names, consequence before instruction, say whether they're blocked.
# This WARNS. It must never block — a vacuous scrub with a visible warning is
# strictly better than a wedged consultant, and the generic detectors still
# ran.
EMPTY_DENY_LIST_WARNING = (
    "⚠️  No client or stakeholder names found in `inputs/engagement_intake.md` "
    "or `ENGAGEMENT_CONTEXT.md`. Only generic details (emails, phones, ID "
    "numbers) were removed — the client's own name may still reach Claude. "
    "Add the names and run this again."
)


# --- Presidio operator pair (upstream pseudonymisation sample) -------------

class InstanceCounterAnonymizer(Operator):
    """Replace each distinct value with `<ENTITY_TYPE_N>`, reusing the same
    placeholder every time that value reappears.

    This is Presidio's documented pseudonymisation sample operator, with one
    change: indices start at 1 rather than 0, to match the mapping shape in
    solution-design-v6.md's Data & Contract Model.

    State lives in the caller-supplied `entity_mapping` dict, which is how
    the same value gets the same placeholder across every file in a run.
    That shared mutable state is also why this is not thread-safe — see the
    module docstring.
    """

    REPLACING_FORMAT = "<{entity_type}_{index}>"

    def operate(self, text: str, params: Optional[Dict] = None) -> str:
        entity_type: str = params["entity_type"]
        # entity_mapping is a dict of dicts, one inner dict per entity type,
        # each mapping original value -> placeholder.
        entity_mapping: Dict[str, Dict[str, str]] = params["entity_mapping"]
        entity_mapping_for_type = entity_mapping.get(entity_type)
        if not entity_mapping_for_type:
            new_text = self.REPLACING_FORMAT.format(entity_type=entity_type, index=1)
            entity_mapping[entity_type] = {}
        else:
            if text in entity_mapping_for_type:
                return entity_mapping_for_type[text]
            previous_index = self._get_last_index(entity_mapping_for_type)
            new_text = self.REPLACING_FORMAT.format(
                entity_type=entity_type, index=previous_index + 1
            )
        entity_mapping[entity_type][text] = new_text
        return new_text

    @staticmethod
    def _get_last_index(entity_mapping_for_type: Dict[str, str]) -> int:
        """Highest index already issued for this entity type. Parsing the
        trailing "_<n>>" is safe for multi-underscore types like
        EMAIL_ADDRESS: "<EMAIL_ADDRESS_3>".split("_")[-1][:-1] == "3"."""

        def get_index(value: str) -> int:
            return int(value.split("_")[-1][:-1])

        return max(get_index(v) for v in entity_mapping_for_type.values())

    def validate(self, params: Optional[Dict] = None) -> None:
        pass

    def operator_name(self) -> str:
        return "entity_counter"

    def operator_type(self) -> OperatorType:
        return OperatorType.Anonymize


class InstanceCounterDeanonymizer(Operator):
    """Inverse of the above, for the in-session path where the caller still
    holds the `OperatorResult`s from the anonymisation that produced the text.

    The production restore path is NOT this — it is `deanonymize_text()`,
    which works from a persisted mapping against arbitrary downstream
    artifacts (agent-written markdown, HTML, workbooks) where no analyzer
    results exist. This operator exists so the round-trip can be verified the
    way upstream intends, and so an in-memory caller has the supported path
    available.
    """

    def operate(self, text: str, params: Optional[Dict] = None) -> str:
        entity_type: str = params["entity_type"]
        entity_mapping: Dict[str, Dict[str, str]] = params["entity_mapping"]
        if entity_type not in entity_mapping:
            raise ValueError(f"Entity Type {entity_type} not found in entity mapping!")
        if text not in entity_mapping[entity_type].values():
            raise ValueError(
                f"Placeholder {text} not found in entity mapping for {entity_type}!"
            )
        return self._find_key_by_value(entity_mapping[entity_type], text)

    @staticmethod
    def _find_key_by_value(entity_mapping: Dict[str, str], value: str) -> Optional[str]:
        for key, val in entity_mapping.items():
            if val == value:
                return key
        return None

    def validate(self, params: Optional[Dict] = None) -> None:
        pass

    def operator_name(self) -> str:
        return "entity_counter_deanonymizer"

    def operator_type(self) -> OperatorType:
        return OperatorType.Deanonymize


# --- engine construction (built once, reused) ------------------------------

# Model load is expensive (seconds, and hundreds of MB resident). These are
# built on FIRST USE, never at import — a module-level construction would
# make `import scripts.pii.engine` pay for a model load even when the caller
# only wanted a constant, and would make the lazy-import contract in
# __init__.py pointless.
_ANALYZERS: Dict[str, AnalyzerEngine] = {}
_ANONYMIZER: Optional[AnonymizerEngine] = None
_DEANONYMIZER: Optional[DeanonymizeEngine] = None


def resolve_spacy_model() -> str:
    """Model name to load. `CORTEX_SPACY_MODEL` overrides for experiments
    (that is how the D10 measurement was run); default is DEFAULT_SPACY_MODEL."""
    return os.environ.get("CORTEX_SPACY_MODEL") or DEFAULT_SPACY_MODEL


def _get_analyzer(model: Optional[str] = None) -> AnalyzerEngine:
    """Shared AnalyzerEngine for `model`, constructed on first use.

    Cached per model name so a caller experimenting with CORTEX_SPACY_MODEL
    doesn't silently reuse the previously loaded one.
    """
    name = model or resolve_spacy_model()
    engine = _ANALYZERS.get(name)
    if engine is None:
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": name}],
        })
        engine = AnalyzerEngine(
            nlp_engine=provider.create_engine(),
            supported_languages=["en"],
        )
        # Second EMAIL_ADDRESS recognizer, additive — the built-in stays as
        # shipped (unmodified, unweakened). See module docstring
        # "INTERNAL-DOMAIN EMAILS" and _InternalDomainEmailRecognizer.
        engine.registry.add_recognizer(_InternalDomainEmailRecognizer())
        _ANALYZERS[name] = engine
    return engine


def _get_anonymizer() -> AnonymizerEngine:
    global _ANONYMIZER
    if _ANONYMIZER is None:
        engine = AnonymizerEngine()
        engine.add_anonymizer(InstanceCounterAnonymizer)
        _ANONYMIZER = engine
    return _ANONYMIZER


def _get_deanonymizer() -> DeanonymizeEngine:
    global _DEANONYMIZER
    if _DEANONYMIZER is None:
        engine = DeanonymizeEngine()
        engine.add_deanonymizer(InstanceCounterDeanonymizer)
        _DEANONYMIZER = engine
    return _DEANONYMIZER


# Shape, not registration: the final dot-label of an email-looking match
# must read as a plausible TLD token — alphabetic only, 2-24 chars. See the
# module docstring's "INTERNAL-DOMAIN EMAILS" section for the full
# rationale, including why this rejects `pkg@1.2.3` and IP-shaped hosts.
_INTERNAL_TLD_SHAPE_RE = re.compile(r"^[A-Za-z]{2,24}$")


class _InternalDomainEmailRecognizer(PatternRecognizer):
    """Catches email-shaped addresses on internal/reserved TLDs that
    Presidio's built-in `EmailRecognizer` legitimately excludes via
    real-registry (`tldextract`) validation — see the module docstring.

    Reuses the built-in's own `PATTERNS` (the exact regex object, imported
    not copied) so this recognizer can never propose a span the built-in
    would not also propose; it only changes which spans are ACCEPTED. That
    is also what guarantees clean overlap resolution on a real-TLD address:
    identical span, identical post-validation score (1.0), so Presidio's
    own `EntityRecognizer.remove_duplicates` collapses the two recognizers'
    results into one.
    """

    PATTERNS = EmailRecognizer.PATTERNS

    def __init__(self):
        super().__init__(
            supported_entity="EMAIL_ADDRESS",
            patterns=self.PATTERNS,
            context=EmailRecognizer.CONTEXT,
            name="internal_domain_email_shape",
        )

    def validate_result(self, pattern_text: str) -> bool:
        domain = pattern_text.rsplit("@", 1)[-1]
        tld = domain.rsplit(".", 1)[-1]
        return bool(_INTERNAL_TLD_SHAPE_RE.match(tld))


def _build_deny_recognizer(deny_terms: Sequence[str]) -> PatternRecognizer:
    """The primary client-identity detector (D3).

    Terms are ordered LONGEST FIRST because Presidio compiles the deny-list
    into a single alternation and regex alternation is leftmost-first: without
    this, a short form ("ZPH") registered before the full name would win and
    the full name would only ever be partially matched.
    """
    ordered = sorted({t for t in deny_terms if t}, key=len, reverse=True)
    return PatternRecognizer(
        supported_entity=CLIENT_ENTITY,
        name="engagement_denylist",
        deny_list=list(ordered),
        deny_list_score=1.0,
    )


def _build_allow_list(deny_terms: Iterable[str]) -> List[str]:
    """Stop generic banking words being redacted when they stand alone.

    "First National Bank" as a peer comparison, "State" in a sentence, "Union"
    in "credit union" — none of those are the client, and redacting them
    turns a readable transcript into noise. Presidio's own `allow_list`
    mechanism does the filtering; these are anchored regexes so the match has
    to be the WHOLE detected span (a multi-word client name containing
    "First" is unaffected).

    A generic word that is genuinely a resolved deny term is excluded from
    the allow-list, so the allow-list can never suppress a real client match.
    This matters for the one path in denylist.py that admits a short word
    unconditionally: a client directory slug is added in its joined form
    without the length/stoplist floor.
    """
    deny_lower = {t.strip().lower() for t in deny_terms if t}
    return [
        r"^" + re.escape(word) + r"$"
        for word in sorted(_denylist.GENERIC_STOPLIST)
        if word not in deny_lower
    ]


def _warn_empty_deny_list(stream) -> None:
    """Loud, visible, and NON-BLOCKING (ux-design-v6.md Error States).

    An empty deny-list is the exact condition under which the old system
    silently produced vacuous scrubbing — a live audit had person names AND
    the client name reach the API in plaintext with no warning at all. It
    must never be silent again, and it must never block: the generic
    detectors still ran, and a wedged consultant is a worse outcome than a
    warned one.
    """
    stream.write(EMPTY_DENY_LIST_WARNING.rstrip("\n") + "\n")
    try:
        stream.flush()
    except Exception:  # noqa: BLE001 - a non-flushable stream must not break a scrub
        pass


# --- session ---------------------------------------------------------------

class PIISession:
    """One anonymisation run.

    Holds the deny-list and the shared `entity_mapping`, so anonymising
    several files through ONE session is what gives cross-file consistency:
    the same email in transcript A and spreadsheet B gets the same
    placeholder, which is the property `deanonymize_dir` depends on when it
    restores the whole outputs/ tree from a single mapping.

    Sequential use only — see the thread-safety note in the module docstring.
    """

    def __init__(
        self,
        deny_terms: Optional[Iterable[str]] = None,
        *,
        entity_mapping: Optional[Dict[str, Dict[str, str]]] = None,
        entities: Optional[Sequence[str]] = None,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
        model: Optional[str] = None,
        warn_stream=None,
        warn_on_empty: bool = True,
    ):
        self.deny_terms = sorted({t.strip() for t in (deny_terms or ()) if t and t.strip()})
        self.entity_mapping: Dict[str, Dict[str, str]] = (
            entity_mapping if entity_mapping is not None else {}
        )
        self.entities = list(entities) if entities is not None else list(DEFAULT_ENTITIES)
        self.score_threshold = score_threshold
        self.model = model
        self._allow_list = _build_allow_list(self.deny_terms)
        self._warned_empty = False

        if warn_on_empty and not self.deny_terms:
            _warn_empty_deny_list(warn_stream if warn_stream is not None else sys.stderr)
            self._warned_empty = True

    # -- construction from an engagement ------------------------------------

    @classmethod
    def for_engagement(
        cls,
        engagement_dir,
        *,
        client_slug: Optional[str] = None,
        extra_terms: Optional[Iterable[str]] = None,
        **kwargs,
    ) -> "PIISession":
        """Resolve the deny-list from the engagement's own documents and open
        a session.

        Read errors PROPAGATE (denylist.py keeps fail-closed read semantics):
        an unreadable CLIENT_PROFILE.md is indistinguishable from an empty one
        if swallowed, and callers depend on being able to fail closed. An
        empty-but-clean resolution is NOT an error — it warns.
        """
        terms = set(_denylist.resolve_engagement_deny_list(
            Path(engagement_dir), client_slug=client_slug
        ))
        if extra_terms:
            terms.update(t for t in extra_terms if t)
        return cls(terms, **kwargs)

    # -- the work ------------------------------------------------------------

    def analyze(self, text: str):
        analyzer = _get_analyzer(self.model)
        recognizers = [_build_deny_recognizer(self.deny_terms)] if self.deny_terms else None
        return analyzer.analyze(
            text=text,
            language="en",
            entities=self.entities,
            score_threshold=self.score_threshold,
            ad_hoc_recognizers=recognizers,
            allow_list=self._allow_list or None,
            allow_list_match="regex",
        )

    def anonymize(self, text: str) -> str:
        """Anonymise one document, extending this session's shared mapping."""
        if not text:
            return text
        results = self.analyze(text)
        if not results:
            return text
        out = _get_anonymizer().anonymize(
            text=text,
            analyzer_results=results,
            operators={"DEFAULT": OperatorConfig(
                "entity_counter", {"entity_mapping": self.entity_mapping}
            )},
        )
        return out.text

    def deanonymize(self, text: str) -> str:
        """Restore using this session's mapping (string replacement — works on
        any downstream artifact, not just the text we anonymised)."""
        return deanonymize_text(text, self.entity_mapping)

    # -- persistence ---------------------------------------------------------

    def mapping_file_dict(self) -> Dict:
        return build_mapping_file(self.entity_mapping)


# --- module-level convenience ---------------------------------------------

def anonymize_text(
    text: str,
    deny_terms: Optional[Iterable[str]] = None,
    *,
    entity_mapping: Optional[Dict[str, Dict[str, str]]] = None,
    **kwargs,
) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """Anonymise one string. Returns (anonymised_text, entity_mapping).

    Pass the returned `entity_mapping` back in for the next file to keep
    placeholders consistent across files; or use a `PIISession` directly,
    which is the same thing with less ceremony.
    """
    session = PIISession(deny_terms, entity_mapping=entity_mapping, **kwargs)
    return session.anonymize(text), session.entity_mapping


def build_mapping_file(entity_mapping: Mapping[str, Mapping[str, str]]) -> Dict:
    """The on-disk shape (v2) — nested by entity type, value -> placeholder.

    Persisted nested on purpose. Flattening on write would recreate the exact
    collision that made the old scheme lossy: one key per category, last value
    wins, so three emails in restored as three copies of the last one.
    """
    return {
        "version": 2,
        "entities": {
            etype: dict(values) for etype, values in sorted(entity_mapping.items())
        },
    }


def flatten_mapping(mapping: Mapping) -> Dict[str, str]:
    """Normalise ANY accepted mapping shape to {placeholder: original_value}.

    Accepted, forever:
      v2 nested  {"version": 2, "entities": {"PERSON": {"Priya Nair": "<PERSON_1>"}}}
      v2 bare    {"PERSON": {"Priya Nair": "<PERSON_1>"}}   (a raw entity_mapping)
      v1 legacy  {"[CLIENT]": "Zzz Holdings", "[EMAIL-REDACTED]": "a@b.com"}

    v1 is the pre-Presidio flat form and is inverted relative to v2 (it is
    placeholder -> value, where v2 is value -> placeholder). Distinguishing
    them structurally rather than by a version field is what lets a
    six-month-old engagement mapping still restore: legacy mappings were
    written with no version key at all.
    """
    if not mapping:
        return {}

    flat: Dict[str, str] = {}

    entities = None
    if isinstance(mapping, Mapping) and isinstance(mapping.get("entities"), Mapping):
        entities = mapping["entities"]
    elif isinstance(mapping, Mapping) and all(
        isinstance(v, Mapping) for k, v in mapping.items() if k != "version"
    ):
        entities = {k: v for k, v in mapping.items() if k != "version"}

    if entities is not None:
        for _etype, values in entities.items():
            if not isinstance(values, Mapping):
                continue
            for original, placeholder in values.items():
                # v2 stores value -> placeholder; invert for replacement.
                flat[str(placeholder)] = str(original)
        return flat

    # v1 legacy: already placeholder -> value.
    for placeholder, original in mapping.items():
        if placeholder == "version":
            continue
        if isinstance(original, (str, int, float)):
            flat[str(placeholder)] = str(original)
    return flat


def deanonymize_text(text: str, mapping: Mapping) -> str:
    """Restore real values into anonymised text.

    Longest placeholder first so a shorter placeholder that is a prefix of a
    longer one cannot partially consume it. `<PERSON_1>` and `<PERSON_10>`
    are already unambiguous thanks to the closing `>`, but legacy placeholders
    are not (`[CLIENT]` is a prefix of `[CLIENT-ABBR]`), and legacy mappings
    must keep restoring correctly forever.
    """
    if not text or not mapping:
        return text
    flat = flatten_mapping(mapping)
    result = text
    for placeholder in sorted(flat.keys(), key=len, reverse=True):
        result = result.replace(placeholder, flat[placeholder])
    return result
