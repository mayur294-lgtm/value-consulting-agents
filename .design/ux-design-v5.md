---
version: 5
prd: prd-v5.md
status: draft
date: 2026-08-19
author: Mariam Titus George
previous: ux-design-v4.md
---

# UX Design v5 — Proposal Builder two-skill system

The "UI" here is a consultant conversation plus generated artifacts. States and errors are conversational states and refusal messages.

## User Flows

### Flow A — Round 1: new deal through `/proposal-builder`

```
Consultant: "/proposal-builder for <client>" (or "build the proposal",
            "run this deal through the proposal builder", CPQ file attached)
        │
        ▼
SCAN — read engagement dir (bootstrap via init_engagement.sh <client> <eng>
  deal_strategy if missing), CLIENT_PROFILE.md, ENGAGEMENT_JOURNAL.md,
  outputs/ (upstream ROI model, discovery, prior proposals),
  INTERNAL_deal_state.json (absent on round 1)
        │
        ▼
SUMMARIZE — "Here is what I know about this deal — correct me."
  (client, LOB, history, prior engagement context, what artifacts exist)
        │
        ▼
GATED INTERVIEW (truth-teller, gap-only — never asks what the scan answered)
  1. CPQ ingest: parse lines (product · edition · basis · qty · per-year fees ·
     3rd-party held separate) → echo parsed table → consultant confirms
  2. Deal-type gate [NEW]: new logo / renewal / expansion → story model
     (Why Change/Now vs Why Stay/Pay) proposed with one-line rationale
  3. Demand plan by firmness: validated / projected / pipeline
     (pipeline NEVER priced in — seeded instead)
  4. Economics: GM ARR %, floor GM % ("unknown" allowed → flagged, not defaulted)
  5. The 5 lever families, 1→4 before price; unanswered = recorded OPEN
  6. Two-scenario mandate: anchor (A), lighter alternative (B), client-facing
     reason B is lighter, internal walk-away
  7. Value-rationale hierarchy: "ROI model upstream / value rationale /
     guarded napkin?" (napkin → inputs logged, labeled directional)
  8. ► PRICING pasted fresh from deal desk (source + date recorded)
        │
        ├──[consultant: "just give me a first cut"]──▶ FAST-DRAFT:
        │     conservative defaults, generate, gates surfaced afterward
        │     as "confirm/refine these" on the output
        ▼
DEAL BRIEF CHECKPOINT — one consolidated artifact, approved AS A WHOLE:
  context · story model · section set (from library) · value-rationale flavor ·
  round sections · assumptions+confidence · open items
  → written as outputs/CHECKPOINT_deal_brief_v1.md   [satisfies write-gate hook]
        │
        ▼
ENGINE — deal_config.json → python3 tools/proposal_builder.py
  → strategy.json + strategy brief (numbers used verbatim, never recomputed)
        │
        ▼
COMMERCIAL CHECKPOINT — pricing echoed back; ladder (Anchor→C1→C2→BAFO with
  tiers + extracts); exit-ARR flag if ramped; buffer-play candidate;
  elasticity exposure setting (dial, conservative default); Deal Desk verdict
        │
        ▼
GENERATE — client-safe subset → proposal-longform → outputs/
  {CLIENT}_Proposal_v1.html (+.zip)          [client-facing]
  INTERNAL_strategy_brief_v1.md              [trace: rationale, ledger, hash]
  INTERNAL_negotiation_plan_v1.md            [ladder, extracts, walk-away]
  INTERNAL_deal_state.json                   [machine record, round 1]
  INTERNAL_deal_desk_fields_v1.md            [the fields Cortex has inputs for]
        │
        ▼
VERIFY CHECKPOINT — reconcile: every rendered number == engine output;
  sections == approved brief; INTERNAL leak scan = zero hits; sliders sweep
  clean (per proposal-longform QA list); defects found+fixed enumerated
        │
        ▼
JOURNAL — entry + telemetry + assumptions register + provenance (inputs_hash)
```

### Flow B — Round N: the negotiation loop

```
Client meeting happens → transcript or AE bullets
        │
        ▼
"/deal-notes <transcript>" — anonymize-guard → archive source into inputs/ →
  speaker resolution (ambiguous = low-confidence flag, never guessed) →
  pre-write checkpoint → structured note + strategic reads appended to the
  deal journal → post-write checkpoint
        │
        ▼
"/proposal-builder" — detects round N from INTERNAL_deal_state.json
        │
        ▼
DELTA REPORT (opens the conversation):
  · what changed vs the plan (their counter, new information)
  · newly active levers ("their APIs slip to Q3 → readiness concession open")
  · ORIGINAL STRATEGY re-surfaced verbatim + why it was chosen
  · concession history ("we've moved on X and Y — not on price")
  · SPARRING on drift: "plan says C2 = −3.9%; the ask is −8%. That shortens
    the stem. To take it: extract prepay + expansion commit. Hold or trade?"
        │
        ▼
REVISED DEAL BRIEF CHECKPOINT (v{N}) → engine re-run → commercial checkpoint
  → GENERATE v{N} files (prior versions FROZEN, byte-unchanged)
  → verify → journal.  BAFO round adds the buffer play (price-hold framing,
  give-to-get conditions, "travel story" vs the earlier ramp price).
```

### Flow C — Direct render (no strategy needed)

```
"interactive proposal" / "bilingual proposal with sliders" for content the
consultant already has → /proposal-longform runs standalone (its existing
flow: intake → copy template → replace content → wire PRICING → QA →
deliver). Guardrail unchanged: no negotiation content in this path, ever.
```

## Screen & Component States

| Component | State | Trigger | What the consultant sees |
| --- | --- | --- | --- |
| Scan summary | Populated | Round 1, artifacts found | "Here's what I know" digest + "correct me" |
| Scan summary | Empty | Nothing on disk for client | "New engagement — I'll bootstrap it. Everything comes from you this round." |
| Scan summary | Round N | Deal state exists | Delta report opens instead of blank intake |
| CPQ ingest | Parsed | Recognized export | Line-item table echoed for confirmation |
| CPQ ingest | Unrecognized | Odd format | Parsed-what-I-could table + "confirm before I proceed" |
| Interview gates | Answered / Open | Consultant answers or defers | Answered = recorded; deferred = "OPEN lever (still on the table)" |
| Deal brief | Draft → Approved | Iteration → explicit "approved" | Brief re-presented after each edit; approval required as a whole |
| Engine run | Success | Valid config | Strategy summary: scenarios, ladder, tiers, verdict, ledger |
| Engine run | Blocked | Missing pricing/required input | Hard stop naming the missing field — no defaults for money |
| Engine run | Degraded | GM unknown | Runs; floor headroom omitted; Deal Desk pack flagged "needs Finance" |
| Proposal render | Generated | Post-checkpoints | File paths + QA result + what's client-safe vs INTERNAL |
| Elasticity dial | Conservative (default) / Opened | Consultant sets exposure | Which drivers the client can move, stated in the commercial checkpoint |
| Verify | Clean / Defects | Reconciliation | "N defects found and fixed: …" (honest, enumerated) |

## Error States

| Error | Cause | Consultant-facing message | Recovery |
| --- | --- | --- | --- |
| Missing pricing | No deal-desk numbers supplied | "I can't price this — paste the current deal-desk numbers (with source + date). I never reuse pricing from memory or prior rounds." | Paste pricing; run resumes |
| Engine input invalid | Config field missing/wrong type | Engine's own error, quoted verbatim + which interview answer feeds that field | Fix the answer; re-run |
| Unscrubbed transcript | PII in `/deal-notes` input | Anonymize-guard block + the exact `anonymize_transcript.py` command | Scrub; re-run |
| Write blocked | No checkpoint before deliverable | Hook denial surfaced: "Deal brief not yet approved — that's the missing checkpoint." | Approve brief |
| Martini violated | Consultant override grows a concession | "This breaks the shrinking rule (§1) — it signals more is available. Override requires an explicit note; I'll journal it." | Confirm override or re-pace |
| Pipeline demand priced in | Firmness gate contradiction | "That demand is pipeline-tier — pricing it in violates the demand-plan rule. Seed it instead?" | Reclassify or seed |
| INTERNAL leak detected | Internal string in render input | "Blocked: negotiation content in the client artifact. Removed: [list]. Regenerating." | Automatic; logged |
| Napkin math unsourced | Value claim without logged inputs | "I need your inputs for this figure — I don't invent financials. Give me the basis or the claim comes out." | Supply basis or drop |
| Stale prior version modified | Attempt to edit frozen v{N-1} | "v{N-1} is frozen — changes go in v{N}." | New version |
