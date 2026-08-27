---
version: 8
status: built
date: 2026-08-27
author: Mariam
previous: prd-v7.md
---

# PRD v8 — Close the direct-skill path to the pipeline's privacy standard

## 1. Problem

Cortex has two ways an engagement's material reaches a model, and only one of
them is protected.

**The pipeline path is closed.** `#167` built a neutral workspace:
`orchestrate.py` copies scrubbed inputs into `.cortex-workspaces/<neutral>/`,
renames every one of them (`identity.py`: "an `.anon_` artifact's filename
embeds the RAW filename … Names become `.anon_input_NN<suffix>`"), points
`cwd` and every composed prompt inside that workspace, and redacts the run
log. No client identifier reaches an agent through a path.

**The direct-skill path is wide open.** When a consultant runs
`/frontline-long-form`, `/generate-roi-questionnaire`, `/proposal-builder`, or
simply asks Claude to open a file, there is no workspace. `cwd` is the repo
root and Claude reads and writes `engagements/<client-slug>/…/<Client>_Renewal_Proposal_v8.html`
by its real name. The filename lands in the tool call and in context.

This is where the exposure actually lives. **125 files under `engagements/`
carry a client name in the basename** — a full board pack, every output of one
IGNITE engagement, six proposal versions on one deal, eight renewal versions on
another. (Clients are not named here: this repo is PUBLIC. The roster is in
`.engagement_map.json`, which is gitignored.) Almost
none are pipeline outputs. They are skill outputs and hand-built work, and the
naming is not accidental: **nine live component files prescribe it**, hardcoding
patterns like `[CLIENT]_Business_Case_Questionnaire.xlsx` and
`[CLIENT]_UC-XXX_[UseCase]_Prototype.html`.

Three further defects were confirmed by measurement during discovery, not
inherited from the backlog's description:

- **The MCP deny-list gate does not scan dictionary keys.** Measured:
  `{"filters": {"x": "Acmeco"}}` is blocked; `{"filters": {"Acmeco": true}}`
  passes with zero strings scanned. A client name used as a key reaches the
  Infobank unopposed.
- **The gate named "No client names" cannot see any of Cortex's clients.** It
  is a hardcoded regex of six generic banks (`Bank of|First National|Wells|
  Chase|HSBC|Barclays`). A real client's short name and full name sit in **six**
  shared knowledge files while the structural suite reports 224/224 PASS. This
  is the v7 failure shape repeating: a gate named after something it cannot
  see. Cleaning those six files without fixing the check only lets it return.
- **The PII engine mistypes and over-redacts.** A US account number resolves to
  `<UK_NHS_1>` (`UK_NHS` is in `DEFAULT_ENTITIES`), and `Temenos T24` resolves
  to `<PERSON_1>` when surrounded by real person names — a vendor name treated
  as a human's.

If this is not solved: every skill-driven engagement — which is most of them —
keeps putting the client's name into model context through filenames, the
knowledge base keeps accumulating real client identifiers behind a check that
cannot detect them, and the outbound MCP gate keeps a bypass that a single
JSON shape opens.

## 2. Solution

Bring the direct-skill path up to the standard the pipeline path already meets,
and repair the three measured gate defects behind it.

New engagement outputs are named with an **opaque engagement-ID prefix**
(`5a057b98_Renewal_Proposal_v8.html`) instead of a client token — the same
identity concept the opaque-directory migration already mints, so a file that
leaves its directory still carries a handle the consultant can resolve through
`find_engagement.sh` and a stranger cannot read. The components that prescribe
client-named outputs are changed to prescribe this instead. A **write-time
guard** enforces it: touch an engagement that still holds client-named files
and the write is refused with one command that renames that engagement's files
— existing deliverables are never rewritten silently. History is otherwise left
alone; `engagements/` is gitignored and never leaves the machine.

Alongside that: the MCP gate learns to scan dictionary keys, the structural
client-name check is re-pointed at the deny-list terms Cortex actually knows
about instead of six hardcoded foreign banks, and the PII engine gains a
phrase-scoped vendor allow-list and a correct account-number typing.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| Opaque-ID-prefixed naming convention for engagement outputs | Renaming the 125 existing files as a bulk operation |
| Changing the nine components that prescribe `[CLIENT]_…` filenames | The `[CLIENT]` → `<CLIENT_N>` PII placeholder migration itself (already done in v6) |
| A write-time guard that blocks a client-named output and names the fixer | Auto-renaming anything without the consultant running the fixer |
| A one-command per-engagement filename fixer, dry-run by default | The live opaque-directory migration (tooling shipped in #168; blocked on real client legal names — an ACTION, not a design problem) |
| MCP gate: scan dictionary keys, not only values | Re-architecting the deny-list resolution |
| MCP gate: correct the bracket-stripping term defect | |
| Structural client-name check re-pointed at real client terms | |
| Removing the real client's name from the six shared knowledge files | Auditing every knowledge file for every past client |
| PII engine: phrase-scoped vendor allow-list | The span-boundary defect (`"Aisha Rahman (COO)"` swallows the bracket and role) |
| PII engine: US account numbers stop resolving to `UK_NHS` | Wiring OCR into PDF page images (scanned PDFs still fail) |
| Authoring mutation entries for every check these changes touch | Flipping `MUTATIONS_ENFORCED_FOR_ALL_ROWS` to `True` |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Client name reaching model context via a filename on the direct-skill path | 0, enforced by a hook that fails closed |
| Dictionary-key deny-list bypass | Blocked; proven by a mutation that makes the check go red |
| Real Cortex client names detectable by the structural knowledge check | All deny-list terms, not 6 hardcoded foreign banks |
| Real-client-name occurrences in shared knowledge | 0, and the check that missed them now catches them |
| US account number entity type | `US_BANK_NUMBER` or unmatched — never `UK_NHS` |
| `Temenos T24` in person-dense context | Survives as plain text |
| New mutation-proven checks | ≥ 36 (the `mcp-query-guard` 17 + `pii-anonymizer` 19 currently counted as DEBT) |
| Repo-wide DEBT count | 65 → ≤ 29 |

## 5. Eval Acceptance Criteria

Every component this PRD touches has a row, or gets one. Two rows carry 36 of
the repo's 65 DEBT checks and are being edited by this work — that makes this
the cycle in which their mutation entries are authored, not a later one.

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `mcp-query-guard` | existing 17 `code:` checks stay green; **add** `scans_dict_keys`, `bracketed_phrase_term_is_balanced`; **author `mutations:` for all 19** | 1.00 | unit |
| `pii-anonymizer` | existing 19 `code:` checks stay green; **add** `vendor_names_survive`, `account_number_not_uk_nhs`; **author `mutations:` for all 21** | 1.00 | unit |
| `engagement-identity` | existing 6 checks stay green (opaque-ID minting is reused, not changed) | 1.00 | unit |
| `output-naming-guard` (**NEW**) | fresh row required. Checks to author: `blocks_client_named_output`, `allows_opaque_prefixed_output`, `fixer_command_named_in_denial`, `fails_closed_on_error`, `exempts_non_engagement_paths`, `never_renames_without_invocation`. Every check needs a `mutations:` entry at authoring time — a new row starts covered, not in DEBT. | 1.00 | unit |
| `knowledge-name-check` (**NEW**, or extend `tests/quality_metrics.yaml`) | the structural check must fail on a real Cortex client term and pass on an anonymised label. Authored as a negative fixture, not a hardcoded list. | 1.00 | unit |
| `deliverable-structural` | must stay green — output filenames change, and the contract lint reads output files by name | 0.80 | deliverable-structural |

**Downstream consumers:** yes. Changing output filenames can move
`deliverable-structural`, which lints inter-agent contracts over output files.
That altitude must stay green — and per its own definition a green there is a
contract lint over files already on disk, **not** integration evidence.

**Honest limitation, stated rather than buried:** four of the nine components
being changed are prompts (`.claude/commands/generate-roi-questionnaire.md`,
`prototype.md`, `usecase-doc.md`, `.claude/agents/roi-financial-modeler.md`).
**No row in this suite verifies an agent or command prompt.** Their filename
prescriptions will be changed and reviewed by hand; the guard is what actually
enforces the outcome, which is why the guard — not the prompt edit — carries
the eval row.

## 6. Out of Scope

- Bulk-renaming the 125 existing client-named files. They are reached only when
  the consultant touches that engagement.
- The live opaque-directory migration. Tooling shipped in `#168`; it is blocked
  on seven real client legal names and is an ACTION item, not a design problem.
- `engagements/inputs/` and `engagements/outputs/` legacy shared staging. Named
  out of scope by the migration tool itself; migrating them is a separate call.
- Wiring OCR into PDF page images. Scanned PDFs still raise
  `EmptyExtractionError`; that is its own ticket.
- The OCR two-column row-grouping defect and short-column-header over-redaction.
- The PERSON span-boundary defect that swallows `(COO)`.
- Flipping `MUTATIONS_ENFORCED_FOR_ALL_ROWS` to `True`. This PRD reduces DEBT
  substantially but does not clear it.

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| Opaque-ID prefix assumes the directory migration has run | Before migration, `find_engagement.sh` resolves the ID but directories are still client-named — the prefix adds a handle without removing the old leak | Naming is independent of the migration; the guard works either way. Ship it, and the migration lands the other half when the names file is supplied. |
| `[CLIENT]` is BOTH a filename template and a legacy PII placeholder | A naive rename could re-enter the v6 collision where restoring a legacy `[CLIENT]` mapping rewrites `[CLIENT]_Business_Case_Questionnaire.xlsx` | The opaque-ID prefix uses no bracket token at all, which is the reason it was chosen over the descriptive-label option |
| A blocking hook can wedge a consultant mid-engagement | Worst case a live client deliverable cannot be written during a call | Fail closed on the *check*, but the denial must always name a working one-line fixer; `require-harness` precedent |
| Vendor allow-list could suppress a real surname | A person named e.g. "Mambu" stops being redacted — a privacy regression introduced by a quality fix | Allow-list is PHRASE-scoped (`Temenos T24`, never `Temenos` alone), and a check must prove a person's name adjacent to a vendor is still redacted |
| Renaming outputs breaks `.html`/`.zip` sibling pairs and in-document links | A client opens a proposal with broken internal links | The fixer renames a pair atomically and rewrites intra-document sibling references; a check must prove it |
| The v6/v7 stack has not merged to `main` | This branches on an already six-deep stack | Accepted; same constraint as the last three cycles |

## Privacy & Security

This PRD is entirely a privacy change, so the usual section is the substance
rather than an addendum.

- **Threat model:** the adversary is inadvertent disclosure to a model provider
  and to the shared knowledge base — not an attacker on the machine.
  `engagements/` is gitignored and local; the exposure is what enters model
  context and what enters `knowledge/`.
- **The deny-list, not Presidio, detects the client's name.** Unchanged and
  load-bearing. Nothing in this PRD should be described as "Presidio detects
  the client for us"; there is no reliable ORGANIZATION recognizer.
- **Fail closed.** The new guard follows `anonymize-guard`: on any internal
  error it denies rather than allows.
- **The fixer never runs itself.** No hook, no session start, no automatic
  invocation — consultant-invoked, dry-run by default. This matches
  `migrate_engagement_ids.sh` and is the reason the "auto-rename on touch"
  option was rejected.

## Backlog items resolved, corrected, or retired by this PRD

Discovery measured all 24 parked items rather than trusting their text. Five
were wrong as written and are corrected here:

- **Filename leak is 125 files, not 3.** The backlog and the migration dry run
  both say 3, because the migration tool excludes `engagements/inputs/` and
  `engagements/outputs/` from its scan.
- **The client name is in 6 files, not 4** — the four Ignite Inspire files plus
  `knowledge/methodologies/hypothesis_tree_decomposition.md` and
  `value_lever_framework.md`.
- **The bracket-stripping term is not "dead".** It matches the exact bracketed
  spelling and only that; three natural renderings of the same client name pass.
  It is masked today by the acronym path. Fixing it against the recorded
  description would have produced the wrong test.
- **The `anonymize-guard` deny-message item is already fixed** — it uses
  `_resolve_python.sh`. To be marked `[done]`, not built.
- **Cross-process entity nondeterminism did not reproduce** — three separate
  processes, identical output. Needs its original repro before it is ticketed;
  not carried into this PRD on the backlog's word.
