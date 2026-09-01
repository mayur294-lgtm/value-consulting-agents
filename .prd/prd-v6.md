---
version: 6
status: archived
date: 2026-08-25
author: Mariam Titus George
previous: prd-v5.md
---

# PRD v6 — Presidio PII Gate: real detection, real coverage, at the boundary consultants actually use

## 1. Problem

Cortex has a PII gate that was designed to stop raw client material from reaching the model. It does not do that.

The gate was built in PR #37 (2026-04-13) with four intents, recorded in the origin commit, `knowledge/standards/security_protocol.md`, and the PII Boundary contract in `discovery-transcript-interpreter`:

- **I1 — raw client PII must never be *sent*.** Scrubbing happens locally, before the API call, in pure-stdlib regex with no network calls. The pipeline is fail-closed: a transcript that cannot be anonymised is skipped, not sent.
- **I2 — the deliverable must still carry the client's real name.** This is pseudonymisation, not redaction: placeholders survive the whole agent chain and real names are restored once, at a single exit gate, by the caller. Agents never de-anonymise.
- **I3 — contain the second hop.** The threat model was never only the Anthropic API. Section 5 of the security protocol exists to keep client names out of Backbase Infobank MCP queries and out of harvested knowledge.
- **I4 — consultants must not have to think about it.** Hence a hook, not a checklist.

Measured against those intents, today:

- **The gate covers 3 of 77 real input files.** The guard scans `.md/.txt/.vtt/.srt/.json/.csv/.log` under `engagements/*/inputs/`. Those directories currently hold 43 PDFs, 10 spreadsheets, 10 images, 8 Word documents, 2 decks — and 3 markdown files. Annual reports, RFPs, client decks and pricing spreadsheets are read into context unscrubbed. The guard's own deny message admits binaries are not gated; nothing acts on it.
- **No real engagement has ever been anonymised.** The only `.pii_mapping.json` on disk belongs to the synthetic Harborlight test engagement. The strong, fail-closed gate lives in `orchestrate.py`, which serves the Assess pipeline; essentially all real work — every live engagement — happens in interactive sessions that path never touches. **We built the strongest gate on the least-used path.**
- **Detection is five hand-rolled regexes plus an intake list.** Person and organisation names are only found if someone typed them into `engagement_intake.md`. When that list is empty the system silently strips generic PII only — a live audit test had person names *and* the client name reach the API in plaintext with no warning.
- **The round-trip is lossy.** One mapping key per category, last value wins: three emails in, the last email restored to all three occurrences on de-anonymisation. Wrong data, in a client deliverable. (Backlog item 1, 2026-07-28 audit.)
- **I3 has zero enforcement.** Section 5 is a prompt instruction. Nothing inspects an MCP query for a client name.
- **The client's name is sent on every call regardless of scrubbing.** Engagement directories *are* the client identity (`engagements/<client-slug>/…`, one per live engagement), `compose_prompt` renders `engagement_dir` / `outputs_dir` / `transcript_path` into the prompt as values, and `cwd` is set to the same client-named directory. Perfect content anonymisation is defeated by the path envelope on every single agent invocation.
- **Infobank is reachable from pipeline runs.** `allowed_tools` is an auto-approve list, not a restrictive allowlist; unlisted tools fall through to `permission_mode`, which is `bypassPermissions`. `.mcp.json` loads automatically (`strict_mcp_config` is never set). The only thing preventing MCP calls today is that the server is unauthenticated — so **authorising Infobank converts a silent no-op into live, unguarded queries carrying whatever client context the model composes.**

If we do not fix this: client names, stakeholder names and financials continue to reach the API and Infobank on every engagement; the "every claim traces to a source" methodology is backed by a privacy control that does not hold; and the near-miss pattern already documented in the synthetic-quarantine incident stays live.

**Why now, and why not the fix we already wrote.** PR #129 fixed the lossy round-trip by hand-building numbered per-value placeholders. That is a reimplementation of Presidio's `InstanceCounterAnonymizer`/`InstanceCounterDeanonymizer` pattern. Landing it would mean maintaining our own version of an upstream-supported feature and still leaving detection, coverage and placement untouched. #129 was closed on 2026-08-25 with its engine-independent parts salvaged into this PRD.

## 2. Solution

Adopt Presidio as the detection and reversible-pseudonymisation engine, install it as a hard dependency the way Presidio itself prescribes, and move the gate from the pipeline to the boundary consultants actually cross. Detection becomes NER + validated patterns + context words instead of five regexes, with the engagement deny-list retained as a first-class recogniser because Presidio has no reliable ORGANIZATION entity and the client's name is the thing we most need to hide. Coverage extends from three markdown files to every text-bearing document under `inputs/` — PDF, Word, PowerPoint, Excel, CSV — each converted to text, anonymised, and surfaced to the model only in its `.anon_` form. Placement extends from `orchestrate.py` to the interactive session: the guard fails closed on `inputs/` paths, and a new gate inspects Backbase Infobank MCP queries so Section 5 is enforced rather than merely asserted. Installation follows Presidio's documented guidance — a virtual environment on Python 3.10–3.13 — surfaced to consultants by a SessionStart preflight and a README section, so the next `git pull` tells them what to do.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| Presidio (`presidio-analyzer`, `presidio-anonymizer`, `presidio-structured`) replaces the hand-rolled regex detection in `anonymize_transcript.py` | Image redaction / OCR — `presidio-image-redactor` is destructive and documented as beta, and irreversible redaction breaks intent I2 (see Out of Scope) |
| Reversible pseudonymisation via Presidio's instance-counter operator pattern, replacing PR #129's hand-built numbered placeholders | Docker deployment of Presidio — a synchronous PreToolUse guard cannot depend on a container being up |
| Compatibility shim: legacy flat `{placeholder: value}` mappings and `[X-REDACTED]` placeholders must still restore | Retroactive anonymisation of engagements already delivered |
| Client-name detection as a Presidio deny-list recogniser, sourced from `engagement_intake.md`, `ENGAGEMENT_CONTEXT.md`, `CLIENT_PROFILE.md` and the engagement directory name — not intake alone | Non-English NER models — English only this cycle; recorded as a risk for the non-English engagements |
| Allow-list to stop over-redaction of generic banking words ("First", "Union", "Capital", "State") | Changing what agents *do* with placeholders — the PII Boundary contract is unchanged |
| Loud, non-blocking warning when the entity list resolves empty (salvaged from #129 / issue #126) | Automating the Python upgrade itself — the preflight instructs, it does not install interpreters |
| Document ingest: PDF, DOCX, PPTX, XLSX, CSV under `inputs/` are converted to text, anonymised, and only the `.anon_` form is readable | Renumbering the orphaned `prd-v4.md` on the retired `feat/pii-roundtrip-v4` branch |
| Images under `inputs/`: one local OCR pass produces an anonymised text sidecar **and** a redacted copy; agents read whichever they need. Applies equally to images embedded in DOCX/PPTX | Extending the gate to WebFetch results (dropped from scope after discovery) |
| Guard fails **closed** on `engagements/*/inputs/` paths, open everywhere else | Any change to `cap_roi_config` or `validate_outputs` |
| New MCP query gate: PreToolUse on `mcp__backbase-infobank__*` scans the query for client identifiers before it leaves the machine — first enforcement of security protocol §5 | The knowledge-harvester's *synthetic-quarantine* gate (v4) — unchanged; only its anonymisation scheme is consolidated here |
| Hard dependency in `requirements.txt`, installed per Presidio's guidance into a virtual environment on Python 3.10–3.13 | Consultant-tier contribution changes — this is Architect-tier work throughout |
| SessionStart preflight that checks Python version, venv, Presidio import and spaCy model, and prints the exact remediation | |
| README gains an Installation section (it currently has none) and CLAUDE.md's incorrect Python claim is corrected | |
| **Salvaged from #129:** recursive + `.xlsx`-capable `deanonymize_dir` with an `unrestored` report field and `client_ready: false` on unrestorable files | |
| **Salvaged from #129:** `chmod 600` on per-transcript `.anon_mapping_*.json` and cleanup after the combined mapping is written | |
| **Folded backlog item:** guard deny message prints CLI flags the script does not accept | |
| **Path anonymisation (both surfaces):** engagement directories become opaque IDs on disk with a local gitignored ID→client map; pipeline agents additionally run in a neutrally-named workspace so no client-named path is ever sent as prompt text | |
| **`claude_agent_sdk` declared and version-pinned** in `requirements.txt` — currently imported by `orchestrate.py` and declared nowhere; the gate now depends on its hook behaviour | |
| **MCP gate covers pipeline runs too** (see §8 correction), plus reconciling the seven agent prompts that instruct Infobank queries, plus the snippet source `knowledge/platforms/backbase-mcp-integration.md` that omits §5 entirely | |
| **`scripts/setup_pii.sh`** — one-command installer (detect Python, create venv, install, download model, verify) so the preflight can print a single line | |
| **Scheme consolidation:** the harvest anonymiser (`knowledge-harvester`, `value-consulting-orchestrator`) and the learnings anonymiser (`/extract-learnings`) are prose-only rules with their own placeholder conventions — both retire in favour of one Presidio-backed tool | |
| **Unenforced assertions retired or backed:** `/sync-telemetry`, `/scan-engagement` ANONYMIZE disposition, `upgrade-analysis`, `evals/README.md` golden-scrubbing instruction | |
| **Placeholder convention change:** adopt Presidio's `<ENTITY_N>` form to end the `[CLIENT]` collision with filename/prose templates | |
| New eval component `pii-anonymizer` at threshold 1.00, wired into the CI PR gate | |

### 3.1 Canonical rule surfaces

This PRD is the single source of truth for PII handling in Cortex. Every surface below states a PII rule today; each must defer to the Presidio path or be retired. **After this cycle, no surface may state an independent anonymisation scheme.**

| Surface | Today | Disposition |
| --- | --- | --- |
| `scripts/anonymize_transcript.py` | Regex detection, `[CLIENT]`/`[PERSON-N]` | **Rewrite** on Presidio |
| `.claude/hooks/anonymize-guard.py` | Narrow text-only guard, fails open | **Rewrite**: Presidio detection, document formats, fail closed on `inputs/` |
| `scripts/artifact_boundary.py` (`deanonymize_dir`) | Top-level only, 4 text formats | **Extend**: recursive + xlsx + `unrestored` (salvaged from #129) |
| `.claude/agents/discovery-transcript-interpreter.md` — PII Boundary | Canonical agent contract; names the tool and placeholders | **Update** to new tool, placeholder form, fail-closed semantics |
| `knowledge/standards/security_protocol.md` §5 | MCP anonymisation, prose only | **Update** — becomes enforced by the MCP gate |
| `.claude/agents/knowledge-harvester.md` + `.claude/agents/value-consulting-orchestrator.md` | Independent scheme `[Client-{domain}-{region}-{year}]`, prose only | **Retire the scheme**; defer to the shared tool |
| `.claude/commands/extract-learnings.md` | Third scheme, free text ("US Universal Bank"), prose only | **Retire the scheme**; defer to the shared tool |
| `.claude/commands/sync-telemetry.md` | Asserts telemetry is anonymised; nothing enforces it | **Back the claim or drop it** |
| `.claude/commands/scan-engagement.md` | `ANONYMIZE` disposition applied by a human | **Point at the tool** |
| `.claude/agents/upgrade-analysis.md` | "Anonymize real client data unless public" | **Point at the tool** |
| `evals/README.md` | Instructs authors to scrub goldens with the old CLI | **Update** to the new command |
| `tests/quality_metrics.yaml` | "No client names (anonymization check)" on knowledge files | **Keep**; verify it fires against the new placeholder form |
| `CLAUDE.md` | Documents old CLI + hook behaviour; states the wrong Python version | **Update** |
| `knowledge/standards/benchmark_evolution.md` | `[anonymized engagement ref]` in the tier table | **Align** to the shared convention |
| `templates/inputs/financial_data_schema.md` | "Anonymized data" / "Customer PII (aggregate only)" | **Align** wording |
| `.claude/commands/deal-notes.md` — **inbound via PR #153** | Hard-codes the old CLI (`anonymize_transcript.py --file … --engagement-dir …`) and the guard's current behaviour, plus two prose harvest-anonymisation rules | **Update on merge** — whichever of #153 / v6 lands second reconciles |
| `.claude/commands/pricing-model.md` — **inbound via PR #153** | "Harvest only anonymised methodology" — prose rule, unenforced | **Point at the tool** |
| `.claude/commands/proposal-builder.md` — **inbound via PR #153** | Error-table row and a governance bullet naming the old CLI and guard | **Update on merge** |

**Merge-order dependency.** PR #153 (Proposal Builder, open) introduces three *new* surfaces that hard-code the current anonymiser CLI and fail-open guard. They are not on `main` yet. Whichever of #153 and this cycle merges second must reconcile them — otherwise #153 ships freshly-written references to a tool this PRD replaces.

**Placeholder collision (defect found during this sweep).** `[CLIENT]` is simultaneously the PII placeholder and a filename/prose template token — `[CLIENT]_Business_Case_Questionnaire.xlsx` in `roi-financial-modeler`, `generate-roi-questionnaire`, `generate-roi-excel`, `usecase-doc`, `prototype`; `"[Client]'s path from X to Y"` in `narrative-assembler`; `| [Client] |` in `market-context-researcher`. `deanonymize_text` performs an unguarded string replace, so any engagement whose mapping contains `[CLIENT]` will rewrite those templates. Presidio's `<ENTITY_N>` convention removes the collision; a migration note must cover engagements holding legacy `[CLIENT]` mappings.

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Text-bearing input formats covered by the gate | 5 of 5 (PDF, DOCX, PPTX, XLSX, CSV) — from 0 today; 67 of the 77 current real input files, vs 3 today |
| Round-trip fidelity on a multi-value fixture | Byte-identical restore, 100% — three distinct emails restore to three distinct emails |
| Raw PII in anonymised output | Zero occurrences of any fixture PII value in the `.anon_` artifact |
| Client name reaching an Infobank MCP query | Zero — MCP gate blocks or rewrites; verified by a negative eval case |
| Empty entity list | Always produces a visible stderr warning; never silent |
| Guard behaviour when Presidio fails to load | Blocks reads under `engagements/*/inputs/`, allows all other paths — verified by fault injection, and must not wedge a session |
| Consultant on Python < 3.10 pulling the repo | Receives actionable install instructions at session start, without reading any docs |
| Legacy mapping restoration | Existing flat `{placeholder: value}` and `[X-REDACTED]` mappings still restore |
| Downstream regression | Pipeline-altitude eval green; no change to agent-visible placeholder semantics |

## 5. Eval Acceptance Criteria

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `pii-anonymizer` (**new**) | `round_trip_byte_identical`, `distinct_values_distinct_placeholders`, `repeated_value_reuses_placeholder`, `no_raw_pii_in_anonymized_output`, `cross_transcript_merge_collision_free`, `xlsx_outputs_deanonymized`, `nested_outputs_deanonymized`, `mapping_files_chmod_600_and_cleaned`, `client_name_redacted_via_denylist`, `allowlist_prevents_generic_overredaction`, `empty_entity_list_warns`, `legacy_flat_mapping_still_restores`, `document_formats_converted_and_scrubbed`, `image_input_blocked_with_message`, `guard_fails_closed_on_inputs_path`, `mcp_query_client_name_blocked` | **1.00** | unit (component) |
| `discovery-transcript-interpreter` | existing row — must stay green (PII Boundary contract unchanged) | 0.80 | unit (component) |
| `knowledge-harvester` | existing row — must stay green; its synthetic-quarantine gate is unchanged, but its anonymisation scheme now defers to the shared tool, so the row must be re-verified rather than assumed | 0.80 | unit (component) |
| pipeline | full pipeline experiment — must stay green | existing | pipeline |

- `pii-anonymizer` is a **new component**; its fixture, rubric module, registry row and CI wiring are authored as part of this work. Threshold is deliberately **1.00**, not the 0.80 house default — a privacy control is pass/fail.
- The fixture must be **synthetic and committed**. `engagements/**` is gitignored PII and must never appear under `goldens:` (registry SLOT RULE).
- Component altitude wires **one** `input:` per component — no `goldens:`/`negatives:` lists. Negative cases (over-redaction, fail-closed fault injection, MCP block) use the temp-copy pattern established by `overcap_negative_gate_witness`.
- **Gate-bites verification is mandatory:** reverting the Presidio detector locally must make `no_raw_pii_in_anonymized_output` fail. Record the result in the PR description. A gate that cannot fail certifies nothing.
- This change affects downstream consumers (every agent reads anonymised text), so the pipeline-altitude experiment must stay green.

## 6. Out of Scope

- **Reversible redaction *inside* image pixels.** Redaction of the image copy is destructive by design and that is accepted: the round-trip is carried by the anonymised **text sidecar**, which holds the placeholders agents write into deliverables. The image copy is never restored and never shipped.
- **Client logos.** Redaction blanks only what OCR reads as *text*; a logo is graphics and will not be detected, so it still reaches the model. This is a stated, accepted limitation and MUST be called out in the rollout instructions and the guard's own message — consultants should avoid logo-bearing screenshots.
- **Docker / containerised Presidio.** Offered upstream, but a PreToolUse hook must answer synchronously and locally.
- **WebFetch scanning.** Considered and dropped — public pages rarely carry client PII, and the cost/benefit does not justify the added scope this cycle.
- **Non-English NER.** English models only; multilingual configuration is a follow-on.
- **Retroactive anonymisation** of already-delivered engagements.
- **Automating the Python interpreter upgrade.** The preflight detects and instructs.
- **The `prd-v4.md` filename collision** on the retired `feat/pii-roundtrip-v4` branch.

## 7. System Flow

**Install (once, on next pull):**

```
git pull  →  SessionStart preflight
                │
                ├─ Python ≥3.10?  ── no ──→ print upgrade instructions, warn, continue
                ├─ venv present?  ── no ──→ print venv + install commands
                ├─ presidio importable? ── no ──→ print pip install commands
                └─ spaCy model present? ── no ──→ print model download command
                        │
                       yes → silent, session proceeds
```

**Ingest (every engagement):**

```
inputs/report.pdf ──→ extract text ──→ Presidio analyze ──→ anonymize ──→ .anon_report.md
                                            │                                    │
                                    deny-list (client)                    model reads THIS
                                    + NER + patterns                             │
                                            │                                    ▼
                                       mapping (chmod 600)  ────────→  outputs/ … ──→ deanonymize_dir
                                                                                          │
                                                                              real names restored, once
```

**Guard (every session):**

```
Read/Bash on engagements/*/inputs/*  →  scrubbed?  ── no ──→ DENY + remediation
Presidio import fails                →  path under inputs/? ── yes ──→ DENY (fail closed)
                                                            ── no  ──→ ALLOW (fail open)
mcp__backbase-infobank__* call       →  client identifier in query? ── yes ──→ DENY
```

## 8. Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| **Python 3.9.6 is the interpreter here**; Presidio requires ≥3.10,<3.15 | Presidio cannot install at all today. CLAUDE.md claims 3.11, so the consultant fleet is an unknown spread | Follow Presidio's own guidance: virtual environment on 3.10–3.13. Preflight detects version and instructs; scripts and hooks resolve the venv interpreter |
| **382 MB `en_core_web_lg` model download** | First install is slow; may surprise consultants on poor connections | Preflight states the size up front. Design phase to evaluate whether `en_core_web_sm` is sufficient given the deny-list carries client-name detection |
| **`presidio-structured` is 0.0.8** (pre-1.0) | The XLSX/CSV path depends on an early-stage package | Fallback: extract cell strings and run them through the plain text analyzer/anonymizer, which is the inverse of what `deanonymize_dir` already does. Design phase picks |
| **No reliable ORGANIZATION recogniser in Presidio** | The single most important entity — the client's name — is not covered by the upgrade | Deny-list recogniser stays load-bearing and is broadened beyond intake to context/profile/directory name. This must not be described internally as "Presidio detects PII for us" |
| **Hooks may not fire for SDK-driven pipeline runs** — flagged unverified in PRD v4 and still unverified; `orchestrate.py` invokes agents in-process via the Agent SDK | Determines whether the MCP gate protects pipeline agents or only interactive sessions | **Design phase must verify this empirically before the MCP gate is specified.** If hooks do not fire, the pipeline path needs an in-code equivalent |
| **Instance-counter operator is documented as not thread-safe** | Shared mapping state across concurrent anonymisation would corrupt | `step_discovery` is sequential; Block A's 5 parallel agents operate on already-anonymised text. Constraint recorded so future parallelisation does not silently break it |
| **Hard dependency raises the failure surface** of a guard that previously wedged every session (PR #82) | A Presidio fault could block work | Fail closed on `inputs/` only, open elsewhere. Fault-injection eval case is mandatory |
| **Non-English engagements** (South Asia, Southeast Asia, LATAM, Nigeria) | English NER will under-detect names in other scripts/languages | Validated patterns (email, phone, IBAN, national IDs) are language-agnostic and country-specific recognisers exist. Deny-list covers the client. Recorded as a known gap |
| **Opaque engagement directories change consultant navigation** | Every consultant's muscle memory, `init_engagement.sh`, `CLIENT_PROFILE.md` conventions and docs examples reference client-named paths; 7 live engagement directories need migrating | Local gitignored ID→client map plus a lookup helper so consultants never hand-type an ID. Migration script for existing directories. `engagements/` is already gitignored, so there is no repo-side impact |
| **Tesseract becomes a second system dependency** (on top of the 382 MB model) | Raises install friction for non-technical consultants — the exact adoption risk flagged for the Python upgrade | `scripts/setup_pii.sh` installs it as part of the single command; preflight verifies it and reports in plain language |
| **Client logos are undetectable** | Redaction blanks OCR-detected *text* only; a logo is graphics and survives into the model's context | Accepted and documented. Guard message and rollout instructions must tell consultants to avoid logo-bearing screenshots. No technical mitigation this cycle |
| **Scope roughly doubled after design-phase discovery** (paths, images, MCP reach, SDK pin) | A single cycle now spans detection, coverage, placement, path identity and installer work | Build order must sequence so the MCP gate can land standalone and early — today's accidental fail-closed on Infobank is the only thing currently holding that surface |
| **Upstream moved:** `microsoft/presidio` now redirects to `data-privacy-stack/presidio` (same repo, 10,605 stars, active 2026-08-11); PyPI `presidio-analyzer` 2.2.364 lists it as homepage | Naming/provenance confusion; supply-chain review question | Not a fork — Microsoft transferred the project. Pin versions explicitly in `requirements.txt` and record the transfer in the design doc so the provenance question is answered once |

## 9. Privacy & Security

- Anonymisation stays **entirely local**. Presidio runs in-process; no analysis leaves the machine. The Docker/HTTP deployment mode is explicitly rejected for this reason.
- Mapping files (`.pii_mapping.json`, `.anon_mapping_*.json`) contain real PII, are `chmod 600`, are gitignored, and per-transcript mappings are deleted once the combined mapping is written.
- The de-anonymisation gate is the **single** point where real names re-enter artifacts, and remains caller-owned. No agent de-anonymises.
- The MCP gate is the first enforcement of security protocol §5. It inspects outbound query strings only; it does not log their contents.
- Fail-closed on `inputs/` means a Presidio fault denies access to raw client material rather than silently passing it through.

## 10. Rollback Plan

The change modifies a production privacy control, so rollback must be a single step.

- Presidio detection lands **behind the existing module interface** — `anonymize_text` / `anonymize_transcript_file` / `deanonymize_text` keep their signatures, so the swap is internal.
- The legacy mapping shim means artifacts produced before the change restore correctly after it, and artifacts produced after it restore correctly if the change is reverted (numbered placeholders are data, not code).
- Rollback = revert the merge commit. The regex detector returns; mappings on disk stay readable in both directions.
- The one-way door is the **hard dependency**: reverting the code does not uninstall Presidio from consultants' venvs, which is harmless. The preflight must therefore be revertible independently of the detector.
