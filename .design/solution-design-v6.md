---
version: 6
prd: prd-v6.md
status: draft
date: 2026-08-25
author: Mariam Titus George
previous: solution-design-v5.md
---

# Solution Design v6 — Presidio PII Gate

## Component Structure

```
scripts/
  anonymize_transcript.py       MODIFIED — public facade only. CLI surface and the four
                                public functions (anonymize_text, anonymize_transcript_file,
                                deanonymize_text, deanonymize_file) keep their exact
                                signatures. Implementation delegates to scripts/pii/.
                                Preserving this interface is what makes rollback a revert.
  pii/
    __init__.py                 NEW — lazy exports; importing must not load spaCy
    engine.py                   NEW — Presidio AnalyzerEngine + AnonymizerEngine assembly:
                                recognizer registry, engagement deny-list recognizer,
                                generic-banking allow-list, instance-counter operators,
                                legacy-mapping compatibility shim
    ingest.py                   NEW — document → anonymised text. PDF, DOCX, PPTX, XLSX,
                                CSV, and images (OCR → text sidecar + redacted copy).
                                Images embedded in DOCX/PPTX route through the same path.
    identity.py                 NEW — opaque engagement IDs, the local ID↔client map,
                                and neutral-workspace materialisation for pipeline runs
  artifact_boundary.py          MODIFIED — deanonymize_dir: recursive walk, .xlsx restore,
                                `unrestored` report field, client_ready:false  (salvaged #125)
  orchestrate.py                MODIFIED — step_discovery materialises the neutral
                                workspace; cwd and all path params point at it, never at a
                                client-named directory. Per-transcript mapping hygiene.
  init_engagement.sh            MODIFIED — creates opaque directories, writes the map entry
  find_engagement.sh            NEW — resolve client name → engagement path
  migrate_engagement_ids.sh     NEW — one-shot migration of the 7 existing directories
  setup_pii.sh                  NEW — the single command the preflight prints

.claude/hooks/
  anonymize-guard.py            MODIFIED — Presidio detection, document + image coverage,
                                fail-closed scoped to inputs/, plain-language messages
  pii-preflight.sh              NEW — SessionStart dependency check
  mcp-query-guard.py            NEW — PreToolUse on mcp__* ; §5 enforcement

evals/
  goldens/pii_roundtrip_fixture.md     NEW — synthetic multi-entity transcript
  goldens/pii_fixture_assets/          NEW — synthetic .pdf/.docx/.xlsx/.png
  rubrics/component/pii_anonymizer.py  NEW — 16 deterministic checks
  registry.yaml                        MODIFIED — pii-anonymizer row, threshold 1.00

requirements.txt                MODIFIED — presidio-analyzer, presidio-anonymizer,
                                presidio-structured, spaCy model, pdfminer.six,
                                python-docx, python-pptx, pytesseract, and
                                claude-agent-sdk (imported by orchestrate.py today,
                                declared nowhere)
.claude/settings.json           MODIFIED — register pii-preflight + mcp-query-guard
```

Plus prompt and documentation edits across the 20 rule surfaces catalogued in PRD §3.1.

---

## Data & Contract Model

```yaml
# 1. Mapping file — .pii_mapping.json  (chmod 600, gitignored)
#    Presidio's operator produces a nested structure; we persist it nested and
#    flatten on read so legacy flat mappings restore unchanged.
{
  "version": 2,
  "entities": {
    "PERSON":        {"Priya Nair": "<PERSON_1>"},
    "EMAIL_ADDRESS": {"p.nair@example.test": "<EMAIL_ADDRESS_1>"},
    "CLIENT":        {"Zenith Bank": "<CLIENT_1>", "Zenith": "<CLIENT_1>"}
  }
}
# version 1 (absent key) = legacy flat {placeholder: value} — still restores.
# Both forms are accepted by deanonymize_text forever; only v2 is written.

# 2. Placeholder convention — <ENTITY_N>, not [CLIENT]
#    [CLIENT] is simultaneously a PII placeholder and a filename/prose template
#    token ([CLIENT]_Business_Case_Questionnaire.xlsx; "[Client]'s path from X
#    to Y"). deanonymize_text does an unguarded string replace, so the old
#    convention rewrites templates. Angle brackets end the collision.

# 3. Engagement identity map — .engagement_map.json  (chmod 600, gitignored, repo root)
{
  "e7f3a2c1": {"client": "HDFC", "slug": "hdfc", "created": "2026-08-25"}
}
# The ONLY place the client's real name is bound to a path. Never leaves the machine.

# 4. Deny-list sources (ordered, deduplicated, longest-match-first)
#    inputs/engagement_intake.md · ENGAGEMENT_CONTEXT.md · CLIENT_PROFILE.md
#    · the client slug from .engagement_map.json
#    Single-word terms admitted only when length >= 4 and not in the generic
#    banking stoplist (bank, banking, credit, union, first, national, federal,
#    united, community, citizens, state, financial, savings, trust, group,
#    holdings, capital, mutual, valley, coast, pacific).

# 5. Ingest output contract — for input file X under inputs/
#    text formats  → .anon_X.md
#    images        → .anon_X.md (OCR text, anonymised) + .anon_X.png (redacted copy)
#    Agents read .anon_* only. Raw X is never read by any agent, in any mode.

# 6. Exit-gate report — artifact_boundary.deanonymize_dir
{"gate": "deanonymize_dir", "restored": 12, "unrestored": ["outputs/ROI_Model.xlsx"],
 "client_ready": false}
```

**Non-obvious contract choices.** The mapping is persisted nested because Presidio's operator is entity-typed and flattening on write would recreate the exact collision that made the old scheme lossy (one key per category, last value wins). Reading accepts both shapes forever — mappings on disk are data, and a consultant with a six-month-old engagement must still be able to produce a client-ready deliverable.

---

## Agent / Pipeline Steps

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `pii-preflight.sh` | hook (SessionStart) | environment | notice or silence | Tell the consultant, in plain language, that protection is off and how to fix it |
| `anonymize-guard.py` | hook (PreToolUse: Read, Bash) | tool call | allow / deny | Stop raw client material entering context |
| `mcp-query-guard.py` | hook (PreToolUse: `mcp__*`) | tool call | allow / deny | Stop client identifiers leaving for Infobank (§5) |
| `pii.engine` | module | text + deny-list | anonymised text + mapping | Detection and reversible pseudonymisation |
| `pii.ingest` | module | any input file | `.anon_` artifact(s) | Format coverage, including images and embedded images |
| `pii.identity` | module | engagement dir | opaque ID, workspace | Keep client identity out of paths and prompts |
| `artifact_boundary deanon` | pipeline step | outputs/ + mapping | restored outputs + report | The single point where real names re-enter artifacts |
| `setup_pii.sh` | script | — | working install | One command; absorbs the whole install sequence |
| `migrate_engagement_ids.sh` | script | existing dirs | opaque dirs + map | One-shot migration of the 7 live engagements |

No new agents. Every change is pipeline code, hooks, or prompt edits — consistent with the cortex stack.

---

## Integration Points

| Touched | Change | Downstream | Risk |
| --- | --- | --- | --- |
| `anonymize_transcript.py` | Implementation swapped, interface held | Every agent that reads `.anon_` files | **Medium** — behaviour changes, contract does not |
| `orchestrate.py` `step_discovery` | Workspace materialisation, params repointed | The whole Block-A chain | **High** — every agent's `cwd` and path params change |
| `artifact_boundary.py` | Recursive + xlsx restore | Final deliverables | **Medium** — more files touched than before |
| `.claude/settings.json` | Two new hooks | Every session and pipeline run | **High** — a hook fault affects all work; both fail safe by design |
| Engagement directory names | Opaque IDs | Consultant habits, `CLIENT_PROFILE.md`, docs, journals | **High** — the only consultant-visible breaking change |
| Seven MCP-using agent prompts | §5 rule added | Their outputs | **Low** — additive prompt text |
| `knowledge/platforms/backbase-mcp-integration.md` | §5 added to the snippet source | All *future* agents | **Low**, high leverage — this omission is the root cause |
| `requirements.txt` | Presidio, OCR, document libs, SDK pin | Every consultant machine | **Medium** — install friction is the main adoption risk |
| `evals/registry.yaml`, `evals.yml` | New component row + CI wiring | PR gate | **Low** |

---

## Technical Decisions

**D1 — Presidio behind the existing facade.** `anonymize_transcript.py` keeps its CLI and four public signatures; the engine moves to `scripts/pii/`. *Alternative:* rewrite the module outright. *Why:* rollback becomes a single revert, and no caller — pipeline, agent prompt, or eval — needs to change in lockstep. *Trade-off:* one layer of indirection.

**D2 — `<ENTITY_N>` replaces `[CLIENT]`/`[PERSON-N]`.** *Alternative:* keep the bracket convention. *Why:* `[CLIENT]` is also a filename and prose template token across six components, and `deanonymize_text` string-replaces blindly — the old convention actively corrupts templates. *Trade-off:* a migration note for engagements holding legacy mappings; legacy restore is kept forever.

**D3 — The deny-list is the primary client-identity detector, not Presidio.** Presidio has no reliable ORGANIZATION recognizer, and the client's name is the single most important entity. Sources broaden from `engagement_intake.md` alone to intake + context + profile + the map slug. *Why:* the observed failure was an empty intake list silently producing vacuous scrubbing. *Trade-off:* the system is only as good as the engagement's configured names — hence the mandatory non-blocking warning when the list is empty. **This must never be described internally as "Presidio detects PII for us."**

**D4 — Fail closed on `inputs/`, open everywhere else.** *Alternative:* fail closed globally. *Why:* a globally fail-closed guard wedged every session once already (PR #82); scoping it to raw client material keeps the guarantee where it matters without repeating that failure. *Trade-off:* a Presidio fault leaves non-`inputs/` paths unscanned — acceptable, since those were never in scope.

**D5 — Images always produce both artifacts; no classifier.** One OCR pass yields an anonymised text sidecar and a redacted image copy. *Alternative:* classify each image by text density and route down one branch. *Why:* both branches need OCR anyway, and Presidio's redactor already OCRs → analyses → fills; producing both is nearly free and removes a classifier that would sometimes route a UI screenshot to text-only and destroy its point. *Trade-off:* two artifacts per image. **Accepted limitation:** redaction blanks OCR-detected *text* only — a client **logo** is graphics and reaches the model. This must be stated in the guard message and the rollout instructions.

**D6 — Opaque engagement directories plus a neutral pipeline workspace.** *Alternative:* fix only the pipeline. *Why:* `compose_prompt` renders `engagement_dir` into prompt text on every call and `cwd` is the client-named path, so content scrubbing is defeated by the path envelope on every invocation — in interactive sessions as well as pipeline runs. Fixing only the pipeline would leave the larger surface open. *Trade-off:* the one consultant-visible breaking change; mitigated by `find_engagement.sh`, a migration script, and `engagements/` already being gitignored.

**D7 — Hooks are the enforcement layer, and the SDK gets pinned.** Verified against the Agent SDK docs: `setting_sources` defaults to loading user + project + local settings, `orchestrate.py` passes neither `setting_sources` nor `hooks`, and `permission_mode="bypassPermissions"` bypasses permission checks but **not** hooks. So one hook covers interactive and pipeline alike. *Trade-off:* the guarantee now depends on SDK behaviour, so `claude-agent-sdk` must be declared and version-pinned — it is currently imported by `orchestrate.py` and declared in no requirements file.

**D8 — Hard dependency, venv, one-command install.** Follows Presidio's own guidance (virtual environment, Python 3.10–3.13). *Why one command:* the preflight audience is non-technical; a four-step sequence is where they disengage. *Trade-off:* `setup_pii.sh` becomes a maintained artifact.

**D9 — Eval threshold 1.00 with temp-copy negatives.** A privacy control is pass/fail, not 0.80. Component altitude wires one `input:` per component, so negative cases (over-redaction, fail-closed fault injection, MCP block) use the `overcap_negative_gate_witness` temp-copy pattern. **Gate-bites verification is mandatory:** reverting the detector must make `no_raw_pii_in_anonymized_output` fail, recorded in the PR description. A gate that cannot fail certifies nothing.

**D10 — Start on `en_core_web_lg`, measure `en_core_web_sm` during build.** 382 MB is real install friction, and D3 means the deny-list — not the NER model — carries client identity. If `sm` holds the fixture at 1.00, ship `sm` and cut the download by roughly an order of magnitude. Decide on evidence, in build, not here.

**D11 — `presidio-structured` is 0.0.8; keep a fallback.** For XLSX/CSV, if the pre-1.0 package proves unstable, extract cell strings and run them through the plain text analyzer/anonymizer — the inverse of what `deanonymize_dir` already does for restore. Chosen in build on evidence.

---

## Build Sequence

Four PRs, each independently reviewable and independently valuable.

| PR | Contents | Rationale |
| --- | --- | --- |
| **1** | `mcp-query-guard.py`, `security_protocol.md` §5 rewrite, seven agent prompts, `backbase-mcp-integration.md` snippet source | **Ships first and standalone.** Unblocks authorising Infobank safely — today the only thing preventing unguarded client-named queries to an external server is that the MCP is unauthenticated, which is accidental, not designed |
| **2** | `pii/engine.py`, facade, `requirements.txt`, `setup_pii.sh`, `pii-preflight.sh`, eval gate | The detector swap, landing with its own gate. Nothing downstream proceeds until this is green |
| **3** | `pii/ingest.py` — documents, images, embedded images; guard rewrite | Coverage. Depends on PR 2's engine |
| **4** | `pii/identity.py`, workspace, `init_engagement.sh`, `find_engagement.sh`, migration | Highest consultant impact, so it lands last and can slip without blocking anything else |

**Sequencing note.** PR 1 inverts the usual order deliberately: it is the smallest change and closes the surface that is currently held open by accident rather than by design.

---

## Open Items for Build

1. **`en_core_web_lg` vs `sm`** — decide on measured fixture performance (D10).
2. **`presidio-structured` viability** — pre-1.0; fall back to the text path if unstable (D11).
3. **Migration rehearsal** — `migrate_engagement_ids.sh` must be dry-run against all 7 live directories before it touches any of them.
4. **Rollout content** — install instructions for the team, and the logo limitation stated plainly. Flagged by Mariam as a deliverable she will author; the guard message and README must agree with it.
