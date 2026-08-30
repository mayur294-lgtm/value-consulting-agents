---
version: 4
status: archived
date: 2026-08-18
author: Mariam Titus George
previous: prd-v3.md
---

# PRD v4 — Synthetic-Engagement Quarantine Enforcement

## 1. Problem

Cortex cannot tell fictional test banks from real clients. Synthetic engagements (Harborlight, Zenith, Bank X and two demo/test engagements named after real institutions) were created purely to test the pipeline, but the system treated them as real:

- **The harvester wrote fiction into shared knowledge.** After the 2026-07-28 Harborlight pipeline test, the knowledge-harvester (which runs automatically after every pipeline run) appended fabricated metrics to the shared knowledge base — and its anonymization rule made them *more* convincing: "Harborlight" became `[Client-retail-NAM-2026]` with tier `[Client-Validated]`, HIGH confidence.
- **Retrieval served the fiction back.** Every retrieval surface (the six `/domain-*` skills, benchmark-librarian, and the ROI agents that read harvested ROI patterns) is provenance-blind: no surface excludes any source tier, and none knows `tests/` or `[Synthetic-Test]` exists.
- **It reached a real client.** A live business-case workbook picked up a synthetic call-volume benchmark ("233 per 1,000 customers, NAM CU") from the harvested files. It was caught in review and is flagged in the deck's governance notes — a documented near-miss, and proof of the leak path end-to-end.

On 2026-08-18 the data was cleaned up and a quarantine **convention** was established: test engagements live in `tests/engagements/` with a `.synthetic` marker file; harvest from test runs must go to the engagement's own `outputs/knowledge_harvest/`; retrieval must never cite `[Synthetic-Test]` values. But the convention is documentation only — **nothing enforces it**. The next pipeline test will contaminate shared knowledge exactly the same way.

If we don't solve it: every future test run re-poisons the knowledge base, consultants unknowingly cite fabricated numbers in client deliverables, and the credibility of the whole evidence-traced ROI methodology — "every claim traces to a source" — is undermined by sources that were never real.

## 2. Solution

Enforce the quarantine convention at every point where synthetic data can enter or leave shared knowledge. On the **write side**, the harvest step detects the `.synthetic` marker (or a `tests/` path) and either redirects all harvest output to the engagement's own quarantine directory (`harvest_policy: quarantine`) or skips harvesting entirely (`harvest_policy: never`) — enforced both in the pipeline code (the automatic path) and in the harvester/extraction prompts (the manual paths that bypass the pipeline). On the **read side**, `[Synthetic-Test]` becomes a formally defined excluded tier in the canonical benchmark-tier standard, and every retrieval surface gains an explicit rule: never source values from `tests/` or cite `[Synthetic-Test]`-tagged data in client work. A **structural backstop** in CI fails any `knowledge/**` PR that carries synthetic contamination, so anything that slips past the gates cannot merge.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| Synthetic-engagement gate in the pipeline's harvest step (detect `.synthetic` / `tests/` path; quarantine-redirect or skip per `harvest_policy`) | The already-completed 2026-08-18 data cleanup and relocation (done, pre-PRD) |
| The same gate as a mandatory self-check in the knowledge-harvester prompt (both modes, covering manual `backfill` runs) and in the `/extract-learnings` command (the second manual pathway) | Fixing that workbook's synthetic benchmark cell (stays an open item in the engagement's own workstream, already documented there) |
| `[Synthetic-Test]` formalized as an excluded tier in the canonical benchmark-tier standard (`benchmark_evolution.md`) | Broader governance tiering of skills (skill-first Phase 2) |
| Retrieval-side exclusion rule added to all readers of shared knowledge: the six `/domain-*` skills, benchmark-librarian, and the three ROI agents that read harvested ROI patterns | Moving/tombstoning the deprecated roi-business-case-builder (parked; skill-first Phase 3 pruning) |
| Zenith example in the deprecated-in-place roi-business-case-builder replaced with a neutral placeholder | A PreToolUse hook backstop — **conditional**: built only if design-phase verification shows hooks fire for SDK-driven pipeline writes; otherwise dropped with the finding recorded |
| CI structural backstop: a $0 check in the existing agent-quality PR gate that fails `knowledge/**` PRs containing synthetic contamination markers or fictional test-bank names | Retroactive audit of other historical deliverables for synthetic citations (one-off task, not component work) |
| **Folded backlog item:** benchmark-librarian's phantom `benchmarks/` registry paths (whitelists reference directories that have never existed) repointed to real paths — same files touched anyway | Any change to what the harvester extracts or how it anonymizes real engagements |
| New eval coverage: knowledge-harvester registered as an eval component with a negative-gate case; benchmark-librarian eval extended with a synthetic-exclusion check | |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Pipeline run against a `.synthetic` engagement writes zero bytes under `knowledge/` | 100% — all harvest output lands in the engagement's `outputs/knowledge_harvest/` (or nothing at all for `harvest_policy: never`) |
| Manual harvest paths (backfill mode, `/extract-learnings`) refuse or redirect when pointed at a `tests/` / `.synthetic` engagement | Verified by eval case + live spot-check |
| Retrieval surfaces exclude synthetic data | benchmark-librarian eval includes a synthetic-poisoned fixture; output must not cite the `[Synthetic-Test]` value |
| CI blocks contaminated PRs | Structural check fails a PR introducing `[Synthetic-Test]` content into `knowledge/domains/**` or fictional test-bank names anywhere in `knowledge/**` |
| No regression in real-engagement harvesting | Pipeline-altitude eval stays green; harvest of a non-synthetic engagement behaves identically to today |
| Convention is self-documenting for future test authors | Creating a test engagement per `tests/engagements/README.md` requires no extra steps for the gate to protect it (marker file is the only requirement, `tests/` path alone fails safe to quarantine) |

## 5. Eval Acceptance Criteria

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| knowledge-harvester (**NEW component registration**) | NEW: `synthetic_gate_witness` — negative-gate case (pattern: roi-financial-modeler's `overcap_negative_gate_witness`): committed synthetic fixture engagement carrying `.synthetic`; assert harvest targets resolve to `outputs/knowledge_harvest/` only, and `harvest_policy: never` yields no harvest. Deterministic code checks, no judge. | 1.0 (deterministic) | unit |
| benchmark-librarian | Existing case (code: `confidence_levels_present`, `source_attribution_present`; judge: `benchmarks_defensible_not_hallucinated`) stays green; NEW code check: `synthetic_exclusion` — poisoned fixture containing a `[Synthetic-Test]` entry; output must exclude it or flag it as non-citable | ≥ 0.80 (unchanged) | unit |
| Pipeline (downstream safety) | Existing pipeline-altitude experiment | unchanged | pipeline |
| Structural (all changed agent/command files) | `scripts/test_agent.py` structural checks incl. mode-block integrity; NEW `knowledge_files` structural check for synthetic markers (scoped so the four banner-marked `knowledge/learnings/roi_models/` files remain legal) | pass | structural |

- Fresh eval cases are authored as part of this work: the knowledge-harvester was the incident's cause and currently has **zero** behavioral eval coverage — the new negative-gate case is the regression net that keeps this fix from rotting.
- Downstream consumers are affected (harvest step runs inside the pipeline): the pipeline-altitude experiment must stay green.
- Fixtures follow the registry's committed-synthetic-fixture rule: no `engagements/**` paths in goldens (gitignored → silent vacuous pass).

## 6. Out of Scope

- The workbook fix (`Assumptions!C23`) — tracked in that engagement's own open items.
- Deprecated roi-business-case-builder relocation/tombstone (only its Zenith example line changes).
- Skill-first Phase 2 (governance tiering) and Phase 3 (pruning, JTBD front door).
- Retroactive sweep of past deliverables for synthetic citations.
- Any change to harvest content/anonymization behavior for real engagements.
- Auditing or restructuring the `[Industry]/[Proxy]/[Estimated]/[Client-Validated]` tiers themselves — `[Synthetic-Test]` is added alongside them, nothing else moves.

## Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| Unknown whether PreToolUse hooks fire for SDK-driven agent writes under the pipeline's `bypassPermissions` mode | If they don't, a hook backstop protects only interactive sessions — could give false confidence | Design phase verifies empirically before any hook is built; the Python gate + CI check carry enforcement either way (hook is belt-and-braces, not load-bearing) |
| Manual paths are prompt-enforced only (no Python driver for `/extract-learnings` or backfill mode) | An agent could ignore prompt rules | CI structural check catches contamination at PR time regardless of how it was written; eval case pins the prompt behavior |
| The structural CI check must not flag the four legitimately-kept `[Synthetic-Test]`-marked ROI pattern files | False-positive gate failures on every knowledge PR | Scope the check (e.g. `[Synthetic-Test]` forbidden in `knowledge/domains/**`; fictional bank names forbidden everywhere in `knowledge/**`) — exact scoping is a design decision |
| Harness churn: ~10 prompt files edited with the same exclusion rule | Drift between copies over time | Single canonical rule text lives in the tier standard; prompt edits reference it rather than restating it (wording per design phase) |
| prd-v3's PR stack (#116–#123) is still open; this cycle edits some of the same agent files (benchmark-librarian, knowledge-harvester) | Merge conflicts if built on main while the stack is unmerged | Build this cycle's branch on top of the pr8 stack branch, or sequence after stack merge — decided at `/bb-tickets` time |

## Rollback Plan

All enforcement is additive and independently revertible: the Python gate is one guarded code path in the harvest step (removing it restores current behavior), prompt rules are text blocks in agent/command files, the CI check is one entry in the quality-metrics config. No data migration, no schema change. The quarantine convention and markers predate this PRD and stand on their own.
