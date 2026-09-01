---
version: 10
status: built
date: 2026-08-28
author: Mariam Tahir
previous: prd-v8.md
---

# PRD v10 — Multilingual PII Detection (Latin-script languages)

> **Version note.** This is v10, not v9. `.prd/prd-v9.md` already exists
> uncommitted in the `mariamt/20260819-proposal-builder` worktree; taking v9
> here would collide when both branches merge. `previous:` therefore points at
> v8, the last PRD committed on this lineage.

## 1. Problem

Cortex's PII gate only detects PII in English. `scripts/pii/engine.py` hard-codes
`"en"` in three places — the spaCy model's `lang_code`, `AnalyzerEngine`'s
`supported_languages`, and the `language=` argument of every `analyze()` call.
A French or Spanish transcript therefore gets scrubbed by an English NER model,
which is not a graceful degradation: it is the vacuous-scrubbing failure class
PRD v6 exists to prevent, arriving through a different door.

Three things make this worse than "we only support one language".

**(a) The client's name would stop being redacted, silently.** Per
solution-design-v6 D3, the deny-list — not NER — is what catches the client.
The deny-list recogniser is a `PatternRecognizer` built with no
`supported_language`, so it defaults to `en`. Presidio filters ad-hoc
recognisers by language, so the moment a document is analysed as `fr` the
recogniser is dropped and the single most important entity we hide passes
through in cleartext, with no error and no failed check. The same is true of
the internal-domain email recogniser.

**(b) Accented Latin names are already being dropped today, in English
engagements.** `denylist.py`'s `_PERSON_TOKEN_RE` is `[A-Za-z]` — ASCII, not
Latin. The module comment and backlog `:110` both record this as a *non-Latin
script* limitation, and both understate it. Measured against the real
`_person_name_ok`:

```
OK    Aisha Rahman           DROP  José García
OK    Jean-Luc Marchand      DROP  François Lemaître
                             DROP  Ángela Muñoz
                             DROP  Íñigo Fernández
                             DROP  Sofía Ramírez
```

This is not gated behind multilingual support. It is a live gap on the exact
code path #209 added to close the table-cell leak: a stakeholder with an
accented name, listed in `CLIENT_PROFILE.md`, is silently absent from the
deny-list right now.

**(c) Per-language entity coverage is uneven, and Presidio degrades quietly.**
Measured against `presidio-analyzer==2.2.364`: requesting a mix of supported
and unsupported entities does not raise — it emits a `logger.warning` nobody
reads and returns the remainder. Of the 15 entity types in `DEFAULT_ENTITIES`,
three have no recogniser under `fr` (`CREDIT_CARD`, `US_SSN`, `UK_NHS`) — and
`CREDIT_CARD` *is* supported under `es`, `it` and `pl`. So coverage is not
merely "less than English", it varies language by language in a way no
single blanket statement can describe.

**Who has this problem.** Consultants running engagements whose source material
is not in English. The near-term driver is Latin-script European engagements
(French, Spanish and that family). Non-Latin-script markets — the Sinhala-,
Devanagari- and Tagalog-script engagements — are a real and larger need but are
deliberately excluded here; see §6.

**If we don't solve it:** non-English source documents either cannot be used at
all, or — far worse — get run through the English gate and produce output that
*looks* scrubbed while leaking the client name and stakeholder names.

## 2. Solution

Make the language of PII analysis a declared, per-engagement property rather
than a hard-coded constant. The engagement declares its language in
`CLIENT_PROFILE.md`; the engine resolves that to a spaCy model, fetches the
model on demand if it is not already installed, and analyses in that language.
The set of supported languages is **dynamic** — driven by a language registry,
not a hard-coded list — so a new Latin-script language becomes available by
adding a registry entry and a measurement, not by changing engine logic. The
recognisers that carry client identity are registered for **every** supported
language so they can never be silently filtered out, entity coverage is
computed and asserted per language rather than assumed, and the deny-list's
name extraction is widened from ASCII to Unicode Latin so accented stakeholder
names are captured — in both the module and its hand-copied hook twin.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| Per-engagement language declaration in `CLIENT_PROFILE.md`, and its plumbing through to `PIISession` | Per-document or per-file language override |
| A dynamic language registry (code → spaCy model, script, pinned version, measurement status) | A hard-coded list of supported languages |
| On-demand, version-pinned model install driven by the declared language | Eager install of every model in `setup_pii.sh` |
| Registering the deny-list and internal-email recognisers for all supported languages | Changing what the deny-list *contains* or how terms are resolved |
| Widening `_PERSON_TOKEN_RE` from ASCII to Unicode Latin, in `denylist.py` **and** `.claude/hooks/mcp-query-guard.py`, preserving `drift_check.py` parity | Any other change to the hook's behaviour |
| Per-language entity-coverage computation, with a loud failure when a core entity is uncovered | Writing new recognisers to fill per-language coverage gaps (e.g. a French `CREDIT_CARD`) |
| Adding language-specific ID recognisers already shipped by Presidio (`ES_NIF`, `ES_NIE`, `IT_FISCAL_CODE`, …) to the entity allow-set for their languages | Non-Latin-script ID recognisers (`TH_TNIN`, `KR_RRN`, …) |
| A per-language detection measurement, recorded like D10 | Re-running the D10 `sm`-vs-`lg` tier comparison for English |
| A Latin-script guard that refuses a declared non-Latin language with a clear message | Making non-Latin script work (see §6) |
| Widening `_build_allow_list` where English-only banking vocabulary would over-redact in another language | The unrelated column-header over-redaction in backlog `:93` |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Client name redacted in a French and a Spanish document | 100% — proven by an eval check that fails when the fix is reverted |
| Accented stakeholder names extracted into the deny-list | `José García`, `François Lemaître`, `Ángela Muñoz`, `Íñigo Fernández`, `Sofía Ramírez` all extract |
| `drift_check.py` parity between `denylist.py` and the hook | Passes — identical deny-lists, both copies widened |
| Per-language PERSON detection, measured on the same 5 document shapes as D10 | Recorded per language; a language is "verified" only once measured |
| Entity coverage per declared language | Computed at session open; missing core entity fails closed, missing non-core warns loudly and is journalled |
| Declared non-Latin-script language | Refused with an actionable message, never silently downgraded to English |
| Baseline install size for an English-only consultant | Unchanged from today |
| `pii-anonymizer` eval row | Stays at 1.00 with the new checks added |

## 5. Eval Acceptance Criteria

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `pii-anonymizer` | All 19 existing checks stay green | 1.00 | component (unit) |
| `pii-anonymizer` | **New:** `client_redacted_in_non_english_document` | 1.00 | component (unit) |
| `pii-anonymizer` | **New:** `accented_stakeholder_names_extracted` | 1.00 | component (unit) |
| `pii-anonymizer` | **New:** `declared_language_entity_coverage_asserted` | 1.00 | component (unit) |
| `pii-anonymizer` | **New:** `non_latin_language_declaration_refuses` | 1.00 | component (unit) |
| `mcp-query-guard` | Existing row stays green; `drift_check.py` parity holds after the Unicode widening | 1.00 | component (unit) |
| all deliverable consumers | `--altitude deliverable-structural` stays green | existing | deliverable-structural |

**Gate-bites requirement (non-negotiable).** `client_redacted_in_non_english_document`
must be mutation-proved in both directions: reverting the per-language
registration of the deny-list recogniser must turn it **red**. A check that only
proves "the French engine loads" is explicitly not acceptable — the failure this
PRD exists to prevent is one where the engine loads perfectly and the client's
name survives. The fixture must carry the client name, an accented stakeholder
name, and at least one identifier, in the same five document shapes the English
fixture uses (prose, attendee bullet, markdown table, speaker line, label line).

`accented_stakeholder_names_extracted` must assert through
`denylist.resolve_engagement_deny_list` — not against a hard-coded list — so
that reverting the regex widening turns it red.

**New fixture required:** a non-English sibling to
`evals/goldens/pii_roundtrip_fixture.md`. It must be synthetic and carry no real
client identity, consistent with the synthetic-quarantine programme.

**CI cost note:** the eval gate installs the pinned spaCy model on every run.
Adding a second language model to CI roughly doubles that install. Whether CI
runs the multilingual checks against a real second model or a stub is a
`/bb-design` decision, but the gate-bites proof above must run against a real
model — a stub cannot demonstrate that Presidio drops the recogniser.

## 6. Out of Scope

- **Non-Latin scripts** (Sinhala, Tamil, Devanagari, Arabic, CJK, Cyrillic).
  Backlog `:92` records the measured reason this cannot be done piecemeal:
  installing OCR language packs without matching NER transcribes the name
  correctly into the sidecar in cleartext, where NER still cannot detect it,
  while the image stays unredacted — turning a hidden leak into a plainer one.
  Multilingual OCR and multilingual NER must land together. This PRD adds the
  language *architecture* that a later non-Latin cycle would build on, and
  explicitly refuses non-Latin declarations in the meantime.
- **Multilingual OCR** (`tesseract` language packs) — same reason.
- **Machine translation** of source documents into English as an alternative to
  multilingual NER. It moves cleartext PII through a translation step and
  changes the text the consultant reads.
- **Per-document language auto-detection.** Considered and not chosen: it adds a
  dependency and a silent failure mode (mis-detection routes to the wrong model
  and misses names with no error). Declaration is deterministic and auditable.
  Revisit if mixed-language engagements prove common.
- **Writing new recognisers to close per-language coverage gaps** (e.g. a French
  `CREDIT_CARD`). This PRD surfaces and asserts the gaps; filling them is
  separate work.
- **Backlog `:93`** (column-header over-redaction) and **backlog `:94`** (scanned
  PDFs) — both touch these files but are unrelated problems.
- Re-running the English D10 `sm`-vs-`lg` tier decision.

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| Deny-list recogniser silently filtered under a non-`en` language | **Critical** — client name leaks in cleartext, no error | Register identity-carrying recognisers for every supported language; gate-bites eval check, mutation-proved |
| `_PERSON_TOKEN_RE` is ASCII; accented stakeholders dropped | **Live today**, not just multilingual | Widen to Unicode Latin in both copies; eval check resolving through the real function |
| Two copies of extraction logic (`denylist.py` + `mcp-query-guard.py`) | Divergence silently weakens the hook | `drift_check.py` already asserts parity — must stay green; the widening lands in both |
| Hook must remain stdlib-only and Python 3.9-compatible | A failed import in a `PreToolUse` hook fails **open** | No Presidio/spaCy in the hook; the Unicode widening is a regex change only, and must be 3.9-valid |
| Uneven per-language entity coverage; Presidio warns rather than raises | Silent loss of up to 3 of 15 entity types under `fr` | Compute coverage at session open; fail closed on a missing core entity, warn loudly + journal otherwise |
| On-demand model fetch conflicts with the requirements.txt pinning rationale | An unpinned `spacy download` makes detection quality vary machine to machine, invalidating recorded measurements | The language registry pins each model to a direct wheel URL, as `en_core_web_lg` already is; on-demand fetch installs the pin, never "latest" |
| spaCy model naming is not uniform — `en_core_web_lg` but `fr_core_news_lg` | A naive f-string breaks English | Registry maps language → exact model name; no name construction |
| First run on a newly declared language blocks on a ~400–500MB download | Consultant waits, possibly offline | Fetch at engagement init rather than first document; clear progress and a clear offline failure message |
| A declared language with no recorded measurement | Unverified detection quality certified as passing | Two-tier status: *verified* (measured) vs *provisional* (model loads, unmeasured). Provisional emits the loud non-blocking warning + journal stamp, mirroring `_warn_empty_deny_list` |

## Privacy & Security

This changes a privacy control, so the failure modes matter more than the
features.

- **Fail-closed posture is preserved.** No path added here may cause a document
  to be analysed with the identity recognisers absent. Where the system cannot
  establish that it can scrub a document properly — unknown language, non-Latin
  declaration, missing model, uncovered core entity — it refuses rather than
  producing output that looks scrubbed.
- **No new network egress at analysis time.** Model fetch happens at setup or
  engagement init, never mid-scan, and never sends document content anywhere.
  Detection stays fully local; this is why `presidio-image-redactor` was
  rejected in #163 and that reasoning still binds.
- **The declared language is engagement metadata, not client identity.** It goes
  in `CLIENT_PROFILE.md` alongside existing metadata and must not appear in any
  opaque-ID-protected surface in a way that narrows the client.
- **Widening the name regex widens what becomes a deny term.** The phrase-only
  rule from #209 (a stakeholder contributes their full multi-word name, never
  individual words) must hold under Unicode too, so a widened character class
  cannot turn a common accented word into a bare deny term. The four
  adversarial regressions pinned in `drift_check.py` must still pass.

## Rollback Plan

The change is additive and defaults to today's behaviour: an engagement with no
declared language analyses as English exactly as it does now. Rollback is
therefore staged rather than all-or-nothing —

1. **Disable multilingual** by removing the language declaration from affected
   `CLIENT_PROFILE.md` files. Every engagement returns to the English path with
   no code change.
2. **Revert the engine change** — restores the three hard-coded `"en"` sites.
   The deny-list widening is independent and can stay.
3. **Revert the deny-list widening** only if `drift_check.py` parity breaks. Note
   this re-opens the accented-name gap in §1(b), which is a live leak; prefer
   fixing forward.

Because the accented-name fix is valuable on its own and carries none of the
model-install risk, it should land as its own ticket ahead of the engine work,
so it can ship even if the multilingual work slips.
