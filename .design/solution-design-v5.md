---
version: 5
prd: prd-v5.md
status: draft
date: 2026-08-19
author: Mariam Titus George
previous: solution-design-v4.md
---

# Solution Design v5 — Proposal Builder two-skill system

Sources being unified: Shyam's fork `shyammohan160489-sys/value-consulting-agents` (audited 2026-08-19 — engine pair adoption-grade, selftests present), the `proposal-longform` folder at `~/VS Code manual inputs/Cortex PM/proposal-longform/`, and `~/deal-pricing-system` (retired to reference — nothing ported except the exit-ARR requirement, implemented fresh).

## Component Structure

```
.claude/commands/
  proposal-builder.md          — ADOPTED from fork + EXTENDED: deal-type/story gate, scan-first
                                 summary, deal-brief checkpoint, round-N delta mode, INTERNAL_
                                 output naming, renders via /proposal-longform (not frontline-long-form),
                                 engagement paths aligned to main (outputs/, ENGAGEMENT_JOURNAL.md)
  proposal-longform.md         — ADOPTED from the skill folder, flattened to native command shape:
                                 SKILL.md content adapted (install story removed, paths repointed);
                                 sibling cross-ref names /proposal-builder
  deal-notes.md                — ADOPTED from fork; paths aligned (inputs/ archive, journal names,
                                 anonymize-guard step made explicit before processing)
  pricing-model.md             — ADOPTED from fork as-is (path alignment only)
templates/proposal-longform/
  template.html                — the working Meridian Bank demo template (mechanics source of truth)
  authoring-guide.md           — content contract, PRICING schema, i18n/RTL, readout hooks
tools/
  proposal_builder.py          — CANONICAL ENGINE (adopted) + NEW: exit-ARR/downsell exposure on
                                 ramped structures, buffer-play-as-price-hold block, deal_type/round
                                 config fields; selftest extended to cover new blocks
  pricing_model.py             — adopted as the engine's pricing-math library (scalar scenarios,
                                 tiered/AUM/conversational bases, POF back-solve, crossover)
knowledge/domains/negotiation/
  negotiation-tactics.md       — ADOPTED VERBATIM (Aniket's playbook; §-numbering is load-bearing —
                                 the engine cites it)
  proposal-narrative.md        — NEW: lifecycle story models (Why Change/Now/Stay/Pay + the
                                 renewal-challenge prohibition), section library (constants: 2
                                 pricing scenarios, assumptions-on-record, close plan), value-
                                 rationale hierarchy incl. guarded-napkin rules, voice rules
                                 (plain declarative headers), lever discovery question bank
knowledge/domains/pricing/
  pricing-methodology.md       — ADOPTED VERBATIM (basis × LOB)
evals/
  registry.yaml                — + deliverables.proposal · components.proposal-engine ·
                                 components.proposal-loop rows
  rubrics/deliverable/proposal.py — NEW evaluator (deterministic checks + voice judge)
  goldens/proposal_valid.html  — synthetic golden derived from the Meridian template
  goldens/deal_config_golden.json + deal_state_golden.json + meeting_notes_golden.md
  goldens/negatives/proposal_*.html — challenger-on-renewal · unsourced-ROI · 3-scenarios ·
                                 INTERNAL-leak
.github/workflows/evals.yml    — + --deliverable proposal --negatives + component runs
```

Not built: any second engine; changes to orchestrate.py, hooks, or existing agents. `require-harness.py` untouched (all new paths either already protected — `.claude/commands/`, `templates/` — or deliberately unprotected like the existing ROI tools).

## Data & Contract Model

```yaml
# 1. deal_config.json — consultant-supplied per run (engine input; NEVER persisted pricing)
#    Engine's existing schema (--print-schema) plus new fields:
deal:
  { client, currency, region_list_pct, term_years, lines[]/software_tcv, thirdparty_tcv,
    exceptional_metric, new_logo, custom_dev,
    deal_type: new_logo|renewal|expansion,        # NEW — drives story model
    round: int,                                    # NEW
    ramp_schedule: {year: fee}? ,                  # NEW — triggers exit-ARR block
    pricing_source: {source, date} }               # NEW — provenance of pasted numbers
economics: { gm_arr_pct?, floor_gm_pct?, managed_*_gm_pct?, first_year_arr_pct? }
scenarios: { good?, better?, best?, *_name? }
strategy:  { anchor, alt, target_bafo_discount_pct,
             buffer_offer?: {commit_units, buffer_units, buffer_price} }   # NEW
levers:    { per-family: {used[], extract[], na[], open[]?} }
context:   { switching_cost, champion?, budget?, competition? }

# 2. strategy.json — engine output (numbers used verbatim downstream, never recomputed)
#    Existing blocks: economics · scenarios · ladder[] (stage, posture, nba, extract,
#    cum/increment %, price, tier) · shape · approval · deal_desk (triggers, pack, verdict)
#    · lever_ledger · posture · rationale[] · open_levers[] · inputs_hash
#    NEW blocks:
exit_arr:  { reported_arr, exit_arr, downsell_exposure, flag: bool }   # on any ramp
buffer:    { ramp_price, buffer_price, saving_vs_ramp, conditions[] }  # price-hold framing

# 3. Client-safe render contract → proposal-longform (the wall: ONLY these cross)
#    sections[] per approved brief (story-model-ordered, value-rationale flavor) ·
#    PRICING config {currency, baseFee, tiers[] (published/list only), presets{}} ·
#    scenario cards (A "Recommended" / B "Alternative" — walk-away NEVER crosses) ·
#    elasticity exposure setting (which drivers get sliders) · assumptions table ·
#    disclaimer (projected/non-binding, all languages)
#    PROHIBITED across the boundary: ladder, extracts, floors, walk-away, tiers-of-
#    authority, lever ledger, deal-desk verdict, anything INTERNAL_*

# 4. INTERNAL_deal_state.json — machine record, accumulates rounds (never client-visible)
rounds[]: { n, date, inputs_hash, scenarios_shown, ladder_position,
            concessions: {given[], extracted[]}, meeting_note_refs[],
            open_levers_snapshot[], strategy_summary }
current:  { round, next_planned_stage, elasticity_exposure }

# 5. Deal journal (from /deal-notes) — human narrative per meeting (existing fork schema:
#    headline state, exchanges, actions, strategic reads, telemetry). References deal
#    state; never duplicates its numbers.
```

Rationale: pricing provenance travels inside the config (source+date) so every artifact can cite it; the client-safe contract is an allowlist (what crosses), not a blocklist — the leak eval then checks the blocklist side as backstop.

## Agent / Pipeline Steps

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `/proposal-builder` | command | engagement scan + interview + CPQ + fresh pricing; round N: deal state + journal | deal brief, deal_config.json, all INTERNAL_ artifacts, render handoff | The strategy cockpit (plan-first, gated, sparring) |
| `proposal_builder.py` | tool (canonical engine) | deal_config.json | strategy.json + brief | All strategy numbers, deterministic |
| `pricing_model.py` | tool (engine library) | model config (derived from same deal) | scenario/crossover/POF tables | Deep pricing maths when needed |
| `/proposal-longform` | command | client-safe render contract | {CLIENT}_Proposal_v{N}.html (+zip) | Client-facing interactive proposal |
| `/deal-notes` | command | scrubbed transcript/AE bullets | deal-journal entry + state-delta | Feed the negotiation loop |
| `/pricing-model` | command | pricing questions on a deal | workbook/tables | Standalone pricing analysis |

## Integration Points

| Existing component / step | How it's touched | Risk |
| --- | --- | --- |
| `require-checkpoint.py` hook | Consumed as-is — deal brief checkpoint file satisfies it | Low |
| `anonymize-guard.py` hook | Consumed as-is — gates `/deal-notes` transcript reads | Low |
| `init_engagement.sh` | Used with existing `deal_strategy` type; no change | Low |
| `evals.yml` + `registry.yaml` + `check_registry.py` | New rows + hardcoded command list gains proposal runs | Medium — the gate must actually execute the new cases; verify in CI on the PR itself |
| `/publish` | Client-packaging guidance gains the INTERNAL_ exclusion rule | Low |
| `test_agent.py` | Knowledge files (2 adopted + 1 new) pass existing knowledge checks; commands remain unchecked by it (known gap, accepted) | Low |
| `synthetic-knowledge-guard.py` | New knowledge files must not trip it (no fictional-bank names in knowledge/) | Low |
| Fork → main path alignment | `Engagement/internal/`, `Input/`/`Output/`, `frontline-tokens.json`, `narrative-spine.md` references all repointed to main conventions | Medium — fiddly, explicit ticket |

Downstream consumers: none in the pipeline chain (net-new paths); `orchestrate.py` untouched.

## Technical Decisions

**Decision:** Canonical engine = Shyam's pair; `proposal_builder.py` is the single entry point, `pricing_model.py` its pricing-math library; `~/deal-pricing-system` fully retired.
**Alternatives:** Port the HNB-proven deal-pricing-system engine and graft the strategy rules on; or bridge both.
**Rationale:** The fork pair has determinism selftests, §-traced rules, and the Deal Desk/lever logic already encoded; deal-pricing-system's only unique requirement (exit-ARR on ramps) is a ~40-line fresh addition. Bridging two engines recreates the SparD reactivity tax.
**Trade-offs:** The HNB deal files stay reproducible only via the retired repo (reference); accepted.

**Decision:** Exit-ARR + buffer play are computed in the engine (new config/output blocks), not by the skill.
**Rationale:** "No LLM in the numbers" — both produce numbers a client or Deal Desk may see; selftest asserts them.
**Trade-offs:** Engine schema change → selftest + `--print-schema` must be updated in the same ticket.

**Decision:** Lifecycle/narrative methodology lives in a NEW `proposal-narrative.md`, sibling to `negotiation-tactics.md`; Aniket's file adopted verbatim.
**Alternatives:** Extend negotiation-tactics.md.
**Rationale:** The engine cites tactics § numbers (load-bearing); Aniket pressure-tests his own file; Corporate Visions material has separate provenance.
**Trade-offs:** Two files to cross-reference; the skill's mandatory-reads list names both.

**Decision:** `proposal-longform` flattens to the native command pattern (`.claude/commands/proposal-longform.md` + `templates/proposal-longform/`); no harness changes, no exemptions; the zip/INSTALL story is retired.
**Alternatives:** Keep the self-contained skill folder under `.claude/skills/`.
**Rationale:** Participant decision — match repo-native patterns; both target paths are already harness-protected with zero hook edits.
**Trade-offs:** Loses the portable-folder install story; acceptable since the repo is now the distribution channel.

**Decision:** The internal/client wall is enforced three ways: (1) the render contract is an allowlist, (2) the rendering step never reads INTERNAL_ files, (3) the deliverable eval fails any client artifact containing internal markers.
**Rationale:** Prompt-level discipline alone is not a guarantee; the PRD requires zero leaks.
**Trade-offs:** A blocked render on a false positive requires a manual pass; acceptable.

**Decision:** Round state = `INTERNAL_deal_state.json` (machine) + the deal journal (human), cross-referenced, never duplicated.
**Alternatives:** Journal-only (parse prose for numbers — fragile) or state-only (loses the narrative/strategic reads).
**Rationale:** Each artifact serves a different reader (engine vs consultant); duplication would drift.
**Trade-offs:** Two files to keep consistent; the verify checkpoint reconciles them.

**Decision:** Repo goldens are synthetic only (Meridian-derived + authored fixtures); Schroders/SparD parity runs locally, uncommitted. His `northgate_wealth.json` sample (de-personalised Schroders shape) is reviewed before adoption — if genuinely de-personalised it may serve as an engine golden; otherwise it stays local too.
**Rationale:** No real client pricing in git history; synthetic-quarantine rules.
**Trade-offs:** CI never exercises real-deal shapes directly; the local parity step is documented in the build tickets.
