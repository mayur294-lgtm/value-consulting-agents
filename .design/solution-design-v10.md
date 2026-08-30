---
version: 10
prd: prd-v10.md
status: draft
date: 2026-08-28
author: Mariam Tahir
previous: solution-design-v8.md
---

# Solution Design v10 — Multilingual PII Detection (Latin-script)

Builds on v6's D1 (facade), D3 (the deny-list is the client detector), D8
(venv + one-command install), D9 (threshold 1.00, gate-bites mandatory) and
D10 (model pinned on measurement). None are reopened. v8's D4 (`UK_NHS` leaves
`DEFAULT_ENTITIES`) is treated as landed for design purposes — see D7 below.

**Build is on hold** until the v8 epic (#212–#223) is pushed. This spec is
written against a post-v8 base deliberately; see D7.

## Component Structure

```
scripts/pii/
  languages.py          NEW  Architect-only. The language registry: code →
                             spaCy model name, pinned wheel URL, script
                             classification, threshold. The single place a
                             language becomes real. No name construction.
  measure_language.py   NEW  Reads a language pack, synthesises the five D10
                             shapes, measures detection, writes the record.
                             The engine never imports this.
  engine.py             MOD  Language becomes a parameter: analyzer cache keyed
                             on (model, language); deny + internal-email
                             recognisers carry the session language; entity
                             coverage computed per language.
  denylist.py           MOD  _PERSON_TOKEN_RE ASCII → Unicode Latin.
                             CLIENT_PROFILE.md gains a language field parser.
  drift_check.py        MOD  Parity fixture gains accented names.

.claude/hooks/
  mcp-query-guard.py    MOD  The Unicode widening, hand-copied. Stdlib only,
                             Python 3.9-valid. NOTHING else changes.

.claude/skills/
  pii-add-language/     NEW  Front door. Wraps measure_language.py.
    SKILL.md

knowledge/languages/
  <code>.yaml           NEW  Consultant-writable language pack + the generated
                             measurement block. One per language.
  README.md             NEW  How to fill a pack.

scripts/
  init_engagement.sh    MOD  --language flag; TTY-conditional prompt.
  setup_pii.sh          MOD  English only, as today. Other models on demand.

evals/
  registry.yaml         MOD  +4 checks on pii-anonymizer.
  rubrics/component/
    pii_anonymizer.py   MOD  The 4 new checks.
  goldens/
    pii_fixture_fr.md   NEW  Non-English round-trip fixture. Synthetic.

.github/workflows/
  evals.yml             MOD  Second language model in CI (see D8).
  enforce-contribution-scope.yml  MOD  Allow ^knowledge/languages/.
  catalog-drift.yml     —    Unchanged, but catalog.yaml + cheat sheet must be
                             regenerated in the same PR as the new skill.
```

## Data & Contract Model

```python
# 1. The language registry — scripts/pii/languages.py  (ARCHITECT-ONLY)
#
# Model names are NOT constructed. spaCy uses en_core_web_lg but
# fr_core_news_lg — an f-string over lang_code silently breaks English, and
# would invent plausible-looking names for languages that have no model.
LANGUAGES = {
    "en": Language(code="en", script="latin",
                   model="en_core_web_lg", wheel="https://.../en_core_web_lg-3.8.0-...whl"),
    "fr": Language(code="fr", script="latin",
                   model="fr_core_news_lg", wheel="https://.../fr_core_news_lg-3.8.0-...whl"),
}
# A language ABSENT from this dict is unusable — that is the point. Adding one
# is a reviewed change, because a wheel URL is a supply-chain decision and an
# unpinned model makes detection vary machine to machine (requirements.txt's
# existing rationale for the en pin, extended).

# 2. The language pack — knowledge/languages/<code>.yaml  (CONSULTANT-WRITABLE)
code: fr
names:            # >= 30, as they would appear in a real document
  - "François Lemaître"
  - "Ángela Muñoz"
prose:            # >= 5 sentences per shape; {name} is substituted
  prose:          ["{name} a confirmé que le délai de traitement ..."]
  attendee_bullet: ["- {name}, Directeur des Opérations"]
  markdown_table:  ["| {name} | Directeur Financier |"]
  speaker_line:    ["{name}: Nous avons trois systèmes ..."]
  label_line:      ["**Contact principal :** {name}"]
do_not_redact:    # over-redaction guards — generic words, never a client
  - "banque"
  - "caisse d'épargne"

measurement:      # WRITTEN BY THE TOOL. Never hand-edited — CI re-derives it.
  status: verified            # verified | provisional
  model: fr_core_news_lg
  model_version: "3.8.0"
  date: "2026-09-04"
  person_detection: {prose: 29, attendee_bullet: 25, markdown_table: 24,
                     speaker_line: 28, label_line: 25, total: 131, of: 150}
  overredaction_guards: {passed: 6, of: 6}

# 3. Engagement declaration — CLIENT_PROFILE.md
#    **PII Language:** fr
#    Absent  => "en". Every existing engagement keeps today's behaviour exactly.
#    Parsed by denylist.py, which already parses this file.

# 4. Session contract — scripts/pii/engine.py
#    PIISession(..., language="en")
#    analyze() passes language= through, and the deny recogniser is built
#    WITH THAT LANGUAGE. Coverage is computed at session open:
#      core     = {CLIENT, PERSON, EMAIL_ADDRESS, PHONE_NUMBER}  -> uncovered = REFUSE
#      non-core = everything else in DEFAULT_ENTITIES            -> uncovered = WARN + journal
```

## Agent / Pipeline Steps

| Name | Type | Inputs | Outputs | Purpose |
| --- | --- | --- | --- | --- |
| `/pii-add-language` | skill | language code | pack stub, or a measurement record | Front door for onboarding a language |
| `measure_language.py` | script | `knowledge/languages/<code>.yaml`, registry entry | measurement block, per-shape report | Does the measuring; the testable unit |
| `resolve_language()` | pipeline fn | `CLIENT_PROFILE.md` | validated language code | Declaration → validated code, or a typed refusal |
| `ensure_model()` | pipeline fn | language code | installed model | On-demand pinned install, at init only |
| `entity_coverage()` | pipeline fn | language, `DEFAULT_ENTITIES` | covered / uncovered split | Turns Presidio's log-warning into a decision |

No new agents. This is pipeline and tooling only — no prompt changes.

## Integration Points

| Touched | What changes | Risk | Why |
| --- | --- | --- | --- |
| `scripts/pii/engine.py` | Language parameterised; recognisers language-tagged; coverage gate | **High** | The client-identity path. A mistake here leaks in cleartext with no error |
| `scripts/pii/denylist.py` | Unicode regex; new profile field parser | **High** | Feeds the deny-list; must stay parity-identical to the hook |
| `.claude/hooks/mcp-query-guard.py` | Unicode regex only | **High** | Fails OPEN on import error. Stdlib only, 3.9-valid, no new imports |
| `scripts/pii/drift_check.py` | Fixture gains accented names | Medium | The thing that catches divergence must itself cover the new ground |
| `scripts/orchestrate.py` `step_discovery` | Resolves and threads the language | Medium | Every pipeline run passes through it |
| `scripts/anonymize_transcript.py` | `--language` passthrough | Low | v6/D1 facade — signatures preserved |
| `scripts/init_engagement.sh` | Flag + TTY-conditional prompt | Medium | Exercised by the `engagement_identity` eval row; must stay scriptable |
| `scripts/setup_pii.sh` | Unchanged for English | Low | Baseline install size is a stated success metric |
| `evals/registry.yaml` + rubric | +4 checks | Medium | Interacts with #222's mutation ratchet — see D7 |
| `.github/workflows/evals.yml` | Second model in CI | Medium | Roughly doubles model install time |
| `enforce-contribution-scope.yml` | Allow `^knowledge/languages/` | Low | Opens a consultant contribution path |
| `docs/rollout/catalog.yaml` + cheat sheet | New skill entry | Low | `catalog-drift.yml` fails the PR otherwise |

**Not touched, deliberately:** `scripts/pii/ingest.py`. OCR stays English-only;
per PRD §6 multilingual OCR is out of scope, and `_MIN_OCR_CONFIDENCE` already
refuses what it cannot read.

## Technical Decisions

**D1 — Language is declared per engagement, not detected per document.**
*Alternatives:* auto-detect with `langdetect`/`lingua`; detect-and-verify against
a declaration; run every installed language and union the hits. *Rationale:*
detection adds a dependency and a new silent failure mode — a mis-detected
document routes to the wrong NER model and misses names with no error, which is
the same failure class as v6's empty deny-list. A declaration is deterministic,
greppable, and reviewable in the profile. *Trade-off:* a genuinely mixed-language
engagement needs a per-file override we are not building. Revisit if that turns
out to be common rather than hypothetical.

**D2 — The deny recogniser is built with the session's language; the
internal-email recogniser is registered once per supported language.**
*Alternatives:* register the deny recogniser for every language too; drop
`ad_hoc_recognizers` and put both in the registry. *Rationale:* they differ in
lifetime. The deny recogniser is ad-hoc, constructed per `analyze()` call, so the
language is already known at construction — it just has to be passed. The
internal-email recogniser is added to the registry once at engine construction,
before any call, so it needs one instance per supported language. *Trade-off:*
two mechanisms rather than one. Mitigated by D3.

**D3 — `analyze()` asserts that its recognisers actually carry its language.**
Before returning, the session asserts the ad-hoc recogniser's
`supported_language` equals the analyze language. *Rationale:* the defect this
PRD exists to prevent is invisible — Presidio drops a mismatched recogniser
silently and returns a clean-looking result. An assertion converts a silent leak
into a crash. *Trade-off:* a runtime check on a hot path; it is a field
comparison, not a scan.

**D4 — Entity coverage is computed and split into core and non-core.**
*Alternatives:* ignore it (today's behaviour); refuse on any uncovered entity.
*Rationale:* measured against `presidio-analyzer==2.2.364`, a mixed request does
not raise — it logs a warning and returns the rest, so `CREDIT_CARD` and `US_SSN`
silently vanish under `fr` while `CREDIT_CARD` survives under `es`, `it` and
`pl`. Refusing on any gap would make French unusable over a credit-card
recogniser that no consulting transcript depends on. Refusing on a *core* gap
(CLIENT, PERSON, EMAIL, PHONE) is non-negotiable. *Trade-off:* a judgement call
about which entities are core, made once and stated in code.

**D5 — Consultants contribute the language pack; the measurement is re-derived in CI.**
*Alternatives:* Architect-only packs under `evals/goldens/`; trust the committed
measurement. *Rationale:* the goal is that someone who speaks the language can
start the process without Architect access — but "run the measurement" and
"certify the result" are different privileges. A hand-edited `status: verified`
would promote an unmeasured language into a privacy control. CI re-runs
`measure_language.py` against the committed pack and fails if the record does not
match, so the pack is contributable and the claim is not forgeable. *Trade-off:*
CI now runs a measurement per changed language pack, which needs that language's
model available.

**D6 — The synthesised fixture's limitation is stated, not hidden.**
The measurement builds documents from the pack's template sentences, so it
measures detection under controlled context, not real client prose. This is the
same limitation English D10 carries — it also used five synthetic shapes — which
is precisely what makes the numbers comparable to English. *Trade-off:* a
language can measure well and still underperform on real documents. The
provisional/verified split is a floor, not a warranty, and the docs must say so.

**D7 — This is designed against a post-v8 base, and the accent fix should be
folded into #218 when build starts.** Every file this PRD touches has an open v8
ticket on it: #220 and #221 on `engine.py`, #218 on `denylist.py` +
`mcp-query-guard.py` + `drift_check.py`, #222 on `registry.yaml`. Two
consequences. First, `UK_NHS` leaves `DEFAULT_ENTITIES` in #221, so the
per-language coverage table must be computed against the post-#221 entity set —
the uncovered-under-`fr` set is `{CREDIT_CARD, US_SSN}`, not the three named in
the PRD. Second, #222 flips the `pii-anonymizer` row's mutation ratchet:
`check_registry.py` adds a row to `MUTATION_PROOF_REQUIRED_ROWS` in the same PR
that gives it a `mutations:` key and never removes it. So v10 checks landing
after #222 must each ship an authored mutation; landing before, they are DEBT and
#222 grows from 21 to 25. *Recommendation when build starts:* fold the Unicode
widening into #218, which already opens all three parity files — doing it
separately means establishing `drift_check` parity twice on a hook that fails
open. *Trade-off:* #218 grows, and the live accented-name leak waits on it.

**D8 — CI carries one real non-English model, not a stub.**
*Alternatives:* stub the NLP engine for the multilingual checks; run them
locally only. *Rationale:* v6/D9 makes gate-bites mandatory, and the failure
being gated is *"the engine loads perfectly and the client's name survives."* A
stub cannot demonstrate that Presidio drops a mismatched recogniser, so a stubbed
check would certify nothing — exactly the "gate that cannot fail" v6/D9 forbids.
*Trade-off:* CI model install roughly doubles. Mitigated the way English already
is — a pinned direct wheel URL, cached by `actions/setup-python`.

**D9 — Non-Latin script is refused explicitly, with the reason.**
*Alternative:* accept the declaration and degrade to English. *Rationale:*
backlog `:92` measured why the halfway position is worse than either end —
OCR language packs without matching NER transcribe the name correctly into the
sidecar in cleartext, where detection still cannot see it, while the image stays
unredacted. A refusal that explains itself is honest; a silent downgrade to
English is the vacuous-scrubbing failure with extra steps. *Trade-off:* non-Latin-script
source material stays manual. Stated in the PRD as out of scope, not
discovered at runtime.

**D10 — The hold narrows from "the v8 epic" to FOUR tickets, and they are not
four of a kind.** *Decided 2026-08-30, superseding D7's "build is on hold until
the v8 epic (#212–#223) is pushed".* D7 was right that every file this spec
touches has an open v8 ticket, but it converted that into a dependency on the
whole epic, which is stronger than the coupling justifies: #213–#217
(output-naming), #219 (mcp-guard mutations), #223 (knowledge check) and #224
(build order) touch nothing this spec plans against. Waiting on them would idle
v10 behind unrelated work while the accented-name leak stays live.

The four that do couple, and they couple differently — this distinction is the
point of the decision, because treating them as one class produces the wrong
build order:

- **#220 and #221 — hard prerequisites.** Both change `engine.py`'s entity set,
  and this spec's per-language coverage table is computed against it. D7 already
  records the consequence: post-#221 the uncovered-under-`fr` set is
  `{CREDIT_CARD, US_SSN}`, not the three the PRD names. Building v10's coverage
  work first means computing a table that is wrong on landing.
- **#218 — a FOLD, not a wait.** D7's own recommendation. It opens
  `denylist.py`, `mcp-query-guard.py` and `drift_check.py` — exactly the three
  files the Unicode widening touches. Doing them separately means establishing
  `drift_check` parity twice on a hook that fails open. Sequencing v10 *after*
  #218 gets the ordering right and the economics wrong.
- **#222 — an ordering consideration, not a blocker.** It flips the
  `pii-anonymizer` mutation ratchet, so v10's four new checks are *required* to
  ship authored mutations if they land after it, and are DEBT if they land
  before. That changes an obligation, not a possibility. And it is close to moot
  here: this spec's own "gate-bites requirement (non-negotiable)" already demands
  mutation proof for `client_redacted_in_non_english_document`, so v10 should
  author mutations for its checks whichever side of #222 it lands on. Ordering
  only decides whether #222 grows from 21 to 25.

*Consequence for build order:* v10 can start once #220 and #221 land, with the
Unicode widening folded into #218 rather than sequenced behind it. It does not
wait for the output-naming cluster, #219, or #223. *Trade-off:* v10 and the
remaining v8 tickets then run concurrently over `evals/registry.yaml`, so
whichever lands second rebases its row edits — cheap, and cheaper than idling.

**D11 — The Unicode widening shipped ALONE on 2026-08-30, ahead of #218, and it
is WIDER than this spec scoped it.** *Overrides D10's "fold into #218" for this
one item; D10 stands for everything else.*

*Why pulled forward:* the leak is live. Measured on the shipped extractors, every
accented Latin name was dropped or corrupted — in ENGLISH engagements, today,
with no error and no failed check. D10's economics argument (fold, don't sequence)
was about avoiding a second `drift_check` parity pass. That cost was accepted
deliberately rather than leaving a live client-identity leak waiting on two
unrelated `engine.py` tickets.

*Why WIDER than §3 scoped:* §3 names only `_PERSON_TOKEN_RE`. That is half the
defect, and the smaller half. `_WORD_RE = [A-Za-z]+` shreds accented CLIENT names
— and the client, not the stakeholder, is D3's single most important entity.
Measured before the change:

    Länsförsäkringar -> ['kringar']    the name itself never becomes a term
    Crédito          -> ['dito']
    Bagócs           -> []             no terms at all
    Åland            -> ['land']       under-detects AND emits a generic over-blocker

A fix to `_PERSON_TOKEN_RE` alone would have looked complete, passed review, and
left the client leaking. Both regexes now derive from one `_LATIN` constant,
hand-copied identically into the hook.

*Scope held:* explicit Latin ranges (Latin-1 Supplement + Extended-A + Extended-B),
NOT `\w` and NOT a `regex` dependency — the hook is stdlib-only and 3.9-clean by
contract. Non-Latin script is untouched and remains out of scope per §6. The
hook's term-matching boundary at `mcp-query-guard.py:599`
(`(?<![A-Za-z0-9])…(?![A-Za-z0-9])`) is deliberately NOT changed: it is the
hook's matching behaviour, which §3 excludes, and its accented failure mode
over-blocks rather than under-blocks. Filed rather than fixed.

*Verification:* `drift_check.py`'s parity fixture gains an accented client and
stakeholder, so a one-sided widening now diverges there. One eval check,
`accented_latin_identity_extracted_whole`, asserts through
`resolve_engagement_deny_list` and is HAND-PROVEN in both directions — reverting
`_WORD_RE` fails it with the client names missing and `kringar` back; reverting
`_PERSON_TOKEN_RE` fails it with the stakeholder gone. It is DEBT rather than
mutation-proven, because `pii-anonymizer` carries no `mutations:` key and adding
one for a single check would hard-enforce the row's other 19. #222 is where that
becomes machine-enforced; this check takes the row from 19 to 20, so #222's
arithmetic moves again.

*What did NOT come forward:* per-language registration, the language registry,
`init_engagement.sh --language`, entity coverage. Those still need #220/#221 and
remain sequenced by D10.

## Open Questions

1. **Threshold for `verified`.** English scores 137/150 (91%). Setting the bar at
   91% may make every other language provisional forever; setting it lower
   certifies worse protection as fine. Decide on the first real `fr` measurement,
   not now — the same way D10 was decided in build rather than in design.
2. **Whether `es` ships alongside `fr` in the first build.** Spanish keeps
   `CREDIT_CARD` where French loses it, so it exercises D4's non-core warning
   path differently. Cheap to include, and it proves the registry is genuinely
   dynamic rather than a two-case special case.

---

## Reconciliation against the 2026-08-30 session

This spec was written 2026-08-28. A long privacy/merge session on 2026-08-30
changed several of the files it plans against. Reconciled before `/bb-tickets`;
**nothing here reopens a decision** — D1–D8 all stand, including D7's hold.

### 1. #218 and #219 now carry stale check counts — correct before ticketing

`mcp-query-guard` went from **17 to 19 checks** on 2026-08-30
(`denies_client_from_staging_subdirectory`,
`staging_directory_names_do_not_become_deny_terms` — the shared staging trees
were skipped wholesale, so four real clients were on no deny-list at all).

Consequences for the v8 tickets D7 sequences against:

| Ticket | Says | Should say |
| --- | --- | --- |
| #218 | "existing **17** checks stay green, +2 new" | existing **19** stay green, +2 → **21** |
| #219 | "author mutations for all **19**" | all **21** |

D7's recommendation — fold the Unicode widening into #218 — is **unaffected and
still right**. Only the arithmetic moved.

`pii-anonymizer` is **19** today and this PRD's acceptance criteria says 19,
which is correct. #222's "21" is a FORWARD number assuming #220/#221 land first
and each add a check; it is not stale and should not be "corrected" to 19.

### 2. The parity surface grew, which makes #218's "change both" instruction bite harder

Both `scripts/pii/denylist.py` and `.claude/hooks/mcp-query-guard.py` changed on
2026-08-30: the resolver now descends one level into `engagements/inputs|outputs`
and reads per-client documents, and the hook gained a `_scan_one_dir()` helper to
keep its hand-copied implementation identical.

This spec's "the Unicode widening, hand-copied. NOTHING else changes" still holds
for v10's own change — verified: `_PERSON_TOKEN_RE` is present in BOTH copies and
still ASCII (`mcp-query-guard.py:364`). But `drift_check.py` now asserts parity
across more surface than it did on 2026-08-28, so a widening applied to one copy
and not the other fails louder and later. Change both in the same commit.

### 3. Fifteen CLIENT_PROFILE.md files now exist and NONE has a language field

On 2026-08-28 there was effectively one profile, unfilled. On 2026-08-30, 14 more
were written — one per live engagement and one per staging client — to carry
"Identifier Forms (deny-list)" through the opaque-ID migration.

This spec adds a language field to `CLIENT_PROFILE.md` and an `init_engagement.sh
--language` flag. The flag only helps NEW engagements; **every profile that
exists today predates the field.** The parser therefore needs an explicit,
documented default for an absent field rather than treating absence as an error
or an empty language — and the default must be `en`, since that is what those
15 engagements were actually scrubbed under.

### 4. A capability this spec could not assume: SHADOW_SUBTREES now takes nested entries

`evals/mutations.py` gained nested-subtree support and a single
`is_shadowed()` definition shared with `check_registry.py` (forced by the CTP
merge: its row gated on a `knowledge/` fixture that mutation shadows did not
copy).

Relevant here because this spec puts language packs in `knowledge/languages/`.
If ANY v10 check takes a language pack as its `input:`, #201's shadow-containment
check hard-errors the registry preflight — the fixture would be absent in every
shadow. Before 2026-08-30 the only fixes were "move the fixture" or "copy all
~250 MB of `knowledge/`". Now `knowledge/languages` can be added to
SHADOW_SUBTREES on its own. The new French fixture is specified under
`evals/goldens/`, which is already shadowed, so this bites only if a coverage
check reads a pack directly.

### 5. D7's hold still stands, unchanged

All eleven v8 tickets (#212–#224) remain OPEN and unbuilt. Nothing on 2026-08-30
advanced v8 itself; the session's work was the privacy scrub, the eval-gate
merge, and CTP. The dependency this spec declares is intact.
