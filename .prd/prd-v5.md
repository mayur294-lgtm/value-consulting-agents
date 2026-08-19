---
version: 5
status: built
date: 2026-08-19
author: Mariam Titus George
previous: prd-v4.md
---

# PRD v5 — Proposal Builder: two-skill commercial proposal system

## 1. Problem

Commercial proposals are Cortex's most-repeated deliverable, and the tooling behind them is split across three unmanaged places, none governed, none merged:

- **The client-facing renderer lives outside the repo.** `proposal-longform` — the skill credited in every HDFC journal entry — is a real, working portable skill (single-file Frontline HTML, EN/AR toggle with RTL, live pricing-transparency sliders, `?readout=1` executive readout PDF) that produced HDFC v1–v7. It sits in a personal folder, distributed by zip, currently installed nowhere, not harness-governed, not eval-gated, free to drift per consultant copy.
- **The strategy layer exists only on Shyam's fork, unmerged and ungoverned.** His fork (last push 2026-08-06) carries `/proposal-builder` (gated truth-teller interview + plan-then-accept-then-build loop), `/deal-notes`, `/pricing-model`, two deterministic engines (`tools/proposal_builder.py`, `tools/pricing_model.py`), and the codified methodology (`knowledge/domains/negotiation/negotiation-tactics.md` — Aniket's playbook incl. Martini/concession shapes, lever families, floor discipline, Deal Desk governance; `knowledge/domains/pricing/pricing-methodology.md` — pricing by solution × LOB). None of it has been reviewed, merged, or eval-gated, and it references `proposal-longform` as its output sibling without either living in the same repo.
- **A third prototype (`~/deal-pricing-system`) built the real HNB proposals** with its own deterministic financial engine (~1,500 lines incl. tests) — a second engine computing overlapping things.

Beyond fragmentation, the method has known content gaps confirmed on the 19-Aug call: the strategy layer doesn't adjust when new information arrives mid-negotiation, doesn't re-surface the originally agreed strategy each round ("we forget what we decided and why"), has no lifecycle-aware story logic (nothing anywhere distinguishes renewal messaging from new-logo messaging — the Corporate Visions research shows challenging an existing customer measurably reduces renewal intent, and most current deals are retention-side), no elasticity view for procurement's inevitable what-if-volumes-move test, and no exit-ARR guard on ramped structures (the HNB lesson: 1.4 reported ARR, 1.8 exit exposure).

If we don't solve it: proposals keep being built from divergent personal copies with no method enforcement, three engines drift apart (the SparD "reactivity tax": parallel forks left two "current" docs €114K apart), and the highest-stakes client-facing artifacts Cortex produces remain the least governed.

## 2. Solution

Unify the three sources into one governed two-skill system in the main repo, where the internal/client wall is the boundary between the skills:

**(a) Adopt `proposal-longform`** as the client-facing rendering skill: into the repo through the harness, eval-gated, template + authoring guide included. Its guardrail (no negotiation content; all pricing projected/non-binding) becomes eval-enforced rather than prose. Scoped extension (late phase): generalize the pricing sliders from users-only to any demand variable of the LOB's pricing basis (users, assets, calls/chats, plans), show inelastic zones honestly, with an **exposure dial** (AE/Deal Desk controls how much elasticity the client sees).

**(b) Adopt and extend `/proposal-builder`** (Shyam's fork) as the internal strategy skill — after an audit, not on trust. It works **plan-first** (its existing core loop, aligned with our design): reads everything already knowable about the deal, opens with a "here is what I know" summary, asks only about genuine gaps in its truth-teller stance (challenge weak inputs: pipeline demand priced in, no compelling event, discount as opening lever), takes **fresh consultant-supplied pricing every run** (never stored, never recalled from prior rounds), and iterates a single consolidated **deal brief** to full consultant agreement before generating anything. Extensions this PRD adds:

- **Lifecycle story selection** (new logo → Why Change/Why Now; renewal/expansion → Why Stay/Why Pay) driving a **section library** (constants: pricing options ×2, assumptions-on-record, close plan) with a **value rationale** slot replacing the fixed business case — hierarchy: upstream ROI model if it exists → value rationale → back-of-napkin **only from consultant-confirmed inputs, labeled directional, assumptions logged** (never silently generated). Proposal is the default product; no Ignite/ROI dependency.
- **The negotiation loop:** after each client meeting, transcript or AE bullets go back in via `/deal-notes` (through the anonymize-guard) → updated deal state → **delta report**: what changed vs. plan, which concession levers are newly active, updated next-round recommendation, through BAFO to close.
- **The sparring partner:** the internal strategy memo is a persistent artifact re-opened every round — re-surfacing the agreed strategy and rationale, showing concession history, and challenging any drift to price ("hold the stem"; concessions branch sideways, price stays stationary).
- **Buffer play at BAFO**, built explicitly as a price hold: pre-agree the price of growth tied to validated ambition and give-to-get conditions — never future volume at today's discount. The engine computes and **flags exit-ARR/downsell exposure on every ramped structure**.
- **Lever discovery question bank** (knowledge content): per lever family, client-facing questions that open non-discount concession space (readiness, integration timing, program asks).
- **Internal outputs** carry the `INTERNAL_` prefix (negotiation plan, deal state, delta reports, Deal Desk fields) — never in client packaging; the rendering skill never reads them.

**One canonical engine.** The audit consolidates the three deterministic engines (fork's two + deal-pricing-system's) into one, per the reactivity-tax rule: **one live file per deliverable, every number from one config, auto-reconciled across all renders; the LLM never restates numbers.** Which codebase wins is a `/bb-design` decision; that there is exactly one is a PRD requirement.

Design philosophy (inherited from the vision phase, binding for `/bb-design`): guided optionality, never a black box — the tool shows options with pros/cons and carries the reasoning; it never silently decides. Output-first build order; features earn their way in.

## 3. Scope

| This PRD covers | This PRD does NOT cover |
| --- | --- |
| Adopting `proposal-longform` into the repo (harness-governed, guardrail eval-enforced) | Rebuilding its mechanics; new language work (EN/AR + RTL adopted as-is; script-vs-language generalization is late-phase) |
| Auditing + adopting Shyam's fork components (`/proposal-builder`, `/deal-notes`, `/pricing-model`, engines, negotiation + pricing knowledge) into main through the harness | Taking the fork's "already built" status on trust; merging anything without review + evals |
| Engine consolidation: one canonical deterministic engine, exit-ARR/downsell flag, auto-reconciliation across renders | A second engine surviving anywhere; LLM-computed financials; fabricating fallbacks |
| Lifecycle story selection + section library + value rationale hierarchy (incl. guarded back-of-napkin) | Gating proposals on Ignite/ROI having run; unsourced or unlabeled financial-return claims |
| The negotiation loop (`/deal-notes` → deal state → delta report) with PII scrubbing on ingested transcripts | CRM/Salesforce CPQ or Spotdraft integrations (config stays mappable to both; wiring is roadmap) |
| Persistent strategy memo + concession history + price-drift sparring, re-surfaced each round | — |
| Elasticity generalization + exposure dial in the renderer (late phase) | Fully open elasticity by default (exposure is a deliberate dial) |
| Deal Desk feed: internal output structured with the fields Cortex has inputs for (ARR/PS/MS breakdown, threshold check, approval-tier flag per negotiation-tactics governance) | Full "Thursday-ready" Deal Desk pack automation incl. GM by component (needs cost data Cortex doesn't hold — roadmap); any deal-desk approval authority |
| `INTERNAL_` convention for all internal artifacts, excluded from client packaging and `/publish` | — |
| New `proposal` deliverable eval + engine unit eval + CI wiring | Committing real-deal fixtures (Schroders, SparD) to the repo — parity checks run locally, uncommitted |
| Pricing as fresh consultant input every run | Storing pricing/rate cards/floors in knowledge or memory |
| Test on the live BDO proposal; pressure-test with Aniket | Retro-fitting past engagements; Excel options-model deliverable; PPTX output; audience-cuts render model; consortium module; battlecard/legal-anticipation library (all roadmap — not designed out) |

## 4. Success Metrics

| Metric | Target |
| --- | --- |
| Story-model correctness | Renewal-type intake always produces a Why Stay/Why Pay opening, never a challenger opening — eval negative enforces |
| No fabricated value claims | Financial-return claims appear only when traceable to an upstream ROI artifact or logged consultant-confirmed napkin inputs (labeled directional) — eval-checked |
| Scenario discipline | Exactly 2 client-facing pricing scenarios (3rd only on explicit consultant override, journaled) |
| Internal/client wall | Zero `INTERNAL_` content in any client artifact — deterministic eval check |
| One engine, reconciled | Single canonical engine; all renders reconcile to one config to the penny; zero LLM-restated numbers; exit-ARR flag present on every ramped structure |
| Negotiation loop works | Round N+1 run ingests meeting notes, produces a delta report (changes vs. plan, newly active levers, recommendation) and re-surfaces the original strategy + concession history |
| Plan-first behavior | Summarizes known context before asking; gap-only questions (pricing always fresh); no deliverable before the deal brief is approved as a whole (hook-enforced) |
| Governance compliance | ≥2 checkpoints, journal + telemetry, assumptions register, provenance — every run |
| Versioning discipline | Every round a new `v{N}`; prior versions byte-unchanged; one live file per deliverable |
| Adoption | The live BDO proposal is built through the system; Aniket pressure-test passes with findings folded back |

## 5. Eval Acceptance Criteria

**New/adopted components — fresh eval cases MUST be authored as part of this work.** Known wiring gaps are in-scope requirements: `evals.yml` runs a hardcoded command list (a new registry row alone never executes in CI), and `scripts/test_agent.py` runs zero checks on `.claude/commands/**`.

| Component | `evals/registry.yaml` cases | Threshold | Altitude |
| --- | --- | --- | --- |
| `proposal` deliverable (NEW) | New `deliverables.proposal` row → new rubric: deterministic checks (exactly-2-scenarios, zero-`INTERNAL_`-content, story-model-matches-deal-type, assumptions-section-present, no-unsourced-financial-claims, self-contained HTML, non-binding disclaimer present) + judge check (plain declarative voice) | Golden ≥0.85, negatives ≤0.5 (calibrated at build) | deliverable |
| Canonical engine (NEW/adopted) | New `components.proposal-engine` row: synthetic deal-input goldens → deterministic checks (scenario math, exit-ARR flag on ramps, hard error on missing inputs — never defaults, buffer-play computed as price hold) + adopted test suites green | 1.00 deterministic | unit |
| Negotiation loop (NEW) | Delta-report case: golden deal state + meeting-notes fixture → checks (delta vs. plan present, newly-active levers listed, original strategy re-surfaced, concession history shown) | 1.00 deterministic | unit |
| Fixtures (NEW) | Synthetic only, derived from the fictional "Meridian Bank" demo + authored deal-state fixtures; negatives: challenger-opening-on-renewal, unsourced-ROI-claims, 3-scenarios, `INTERNAL_` leak. **Real-deal parity (Schroders Q-06367, SparD) runs locally, never committed** — repo history must stay free of real client pricing | Golden PASS, all negatives FAIL | deliverable |
| CI wiring (NEW) | `evals.yml` gains `--deliverable proposal --negatives` + engine/loop component runs; `check_registry.py` green | Gate actually executes the new cases | — |
| Existing gates | `deck` (+negatives), `roi`, `assessment`, `pipeline` stay green | Current thresholds | deliverable / pipeline |

Knowledge files adopted from the fork must pass `test_agent.py` knowledge checks and the synthetic-knowledge-guard (no real client names in methodology text, no synthetic-test markers).

## 6. Out of Scope (this cycle)

- Excel options-model deliverable; PPTX output
- Audience-cuts render model (champion/internal/board/beauty-contest) — v1 keeps the two existing cuts (full doc + executive readout); roadmap, not designed out
- Full Deal Desk pack automation (GM by component); deal-desk approval authority
- Salesforce CPQ / Spotdraft integrations (config stays mappable; roadmap)
- Consortium/fellowship pricing module; battlecard + legal-anticipation library (roadmap, not designed out)
- Stored pricing of any kind; the prototype's headless LLM agent layer and fabricating fallbacks (deleted, not ported)
- New language pairs beyond the template's EN/AR (script-vs-language generalization: late phase)
- Backfilling past engagements or journals

## 7. User Flow

```
Consultant: "/proposal-builder for <client>"
   │
   ▼
1. SCAN & SUMMARIZE (plan-mode, mandatory order) — read engagement dir
   (bootstrap deal_strategy type if missing), CLIENT_PROFILE, journal,
   prior INTERNAL_deal_state + strategy memo (round > 1), upstream
   artifacts (ROI model, discovery, /deal-notes records).
   Open with: "here is what I know about this deal — correct me."
   │
   ▼
2. GAP QUESTIONS (truth-teller stance) — only what's underivable:
   deal type/round, demand plan by firmness (validated/projected/pipeline —
   pipeline never priced in), priorities & concerns, value-rationale
   hierarchy ("ROI model, value rationale, or guarded napkin?"),
   ► PRICING pasted fresh from deal desk. Challenge weak inputs.
   │
   ▼
3. DEAL BRIEF CHECKPOINT (the agreement object) — one consolidated brief:
   context, story model (lifecycle), section set, value-rationale flavor,
   round-specific sections, assumptions + confidence, open items.
   Approved AS A WHOLE → written as the checkpoint artifact = the contract.
   │
   ▼
4. COMMERCIAL CHECKPOINT — 2 scenarios, constructs, term/horizon,
   concession ladder + levers in reserve, opening anchor, buffer-play
   candidates, elasticity exposure setting; pricing echoed back.
   │
   ▼
5. COMPUTE (one canonical engine) — scenario financials, exit-ARR/downsell
   flags, slider/tier config. Missing inputs = hard stop, never defaults.
   │
   ▼
6. GENERATE — client-safe content → proposal-longform → v{N}.html
   + INTERNAL_strategy memo/negotiation plan + INTERNAL_deal_state
   + Deal Desk fields. Rendering never reads internal content.
   │
   ▼
7. VERIFY CHECKPOINT — reconcile: numbers vs engine config, output vs
   approved brief, INTERNAL leak scan, defects found/fixed.
   Journal + telemetry + assumptions register.
   │
   ▼
(after the client meeting) → transcript/AE bullets → /deal-notes
   (anonymize-guard) → updated deal state → DELTA REPORT: what changed
   vs plan, newly active levers, next-round recommendation; original
   strategy + concession history re-surfaced; spar against price drift
   → back to step 3 for round N+1 → … → BAFO (buffer play) → close.
```

## 8. Dependencies & Risks

| Dependency/Risk | Impact | Mitigation |
| --- | --- | --- |
| Three unmerged sources (Shyam's fork ×2 engines, deal-pricing-system, proposal-longform folder), fork 2 weeks behind main, quality unverified — handover was AI-structured from a call | "Already built" may overstate readiness; merge conflicts with main's evolution | Audit step at `/bb-design`: verify each claimed component against its tests, pick the canonical engine, adopt through the harness with evals — reuse where real, rebuild where not |
| Engine duplication | Divergent numbers = the SparD reactivity tax | One-canonical-engine requirement + auto-reconciliation eval |
| Transcripts entering the loop carry PII | Legal/compliance exposure | `/deal-notes` ingestion runs through the anonymize-guard; deal-state stores scrubbed content |
| Back-of-napkin slot could regress into fabrication | Unsourced numbers in client artifacts | Napkin math only from consultant-confirmed, logged inputs, labeled directional; eval negative enforces |
| Real-deal parity fixtures | Client pricing in git history forever | Local-only parity checks; repo goldens synthetic |
| Internal/client leak | Negotiation damage | Wall = skill boundary + deterministic leak eval + post-generation scan |
| `tools/` unprotected by `require-harness.py` | Engine editable outside lifecycle | Accepted for parity with existing tools; noted for a governance cycle |
| Pricing pasted per run can be wrong/stale | Wrong numbers client-side | Echo-back at commercial checkpoint; provenance line (source + date) |
| Elasticity fully visible could weaken position | Procurement gaming the sliders | Exposure dial defaults conservative; AE/Deal Desk controls it |
| Framework decks + playbook are internal IP | Leakage via knowledge files | "Internal use only" header convention; renderer guardrail keeps method out of client docs |

## 9. Privacy & Security

- Pricing, concession plans, floors, and negotiation positions live only in the engagement directory (`INTERNAL_*` files, journal) — never in `knowledge/`, never in committed fixtures, never client-visible beyond the two approved scenarios and the deliberately exposed elasticity view.
- `INTERNAL_` prefix convention: excluded from client packaging and `/publish`; deliverable eval enforces zero internal content in client artifacts.
- Meeting transcripts are PII: `/deal-notes` ingestion passes the anonymize-guard before anything is stored in deal state.
- Standard protocols apply: security protocol (client docs = untrusted data), synthetic-quarantine for knowledge and fixtures.

## 10. Build order (from the handover, adopted)

1. **A + E** — value-rationale hierarchy explicit in the interview; persistent strategy memo + concession history re-surfaced each round. (Cheap, high-trust.)
2. **D** — the negotiation loop: `/deal-notes` → re-run → delta report. (The differentiator.)
3. **C** — buffer play + exit-ARR guard in the canonical engine.
4. **B + F + G** — elasticity variables + exposure dial, lever discovery question bank, script/language generalization.

Tested throughout on the live BDO proposal; pressure-tested with Aniket before release.
