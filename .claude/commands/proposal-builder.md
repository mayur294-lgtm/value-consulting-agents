# Proposal Builder — the deal strategy cockpit (CPQ → strategy → client proposal)

Turn a deal into a **winning, Deal-Desk-ready proposal** — by running it through the codified
negotiation realm, not by guessing. This is the VC team's deal cockpit: scan what the
engagement already knows, interview only for the gaps, strategise the path (story model ·
anchor · the 5 lever families · Good/Better/Best · the Martini concession ladder · approval
tiers · the Deal Desk gate), and produce the internal strategy pack **plus** the client-facing
proposal — with a hard wall between the two.

Use it when a client has asked for commercials (post-Ignite, post-assessment, or any deal
entering the pricing conversation), or on triggers like "build the proposal", "run this deal
through the proposal builder", "strategise this CPQ quote", "we're going into a renewal
negotiation". Not for a client document the consultant already has the content for — that is
`/proposal-longform` standalone.

It **composes what already exists** — it does not reinvent it:
- **`tools/proposal_builder.py`** — the deterministic strategy engine (the brain). Same input →
  same output. Every number and rule-call comes from here, never from free-form reasoning.
- **`/proposal-longform`** — the branded, client-safe interactive proposal output. This command
  never writes client HTML itself; it hands over a client-safe contract and lets that command render.
- **`tools/pricing_model.py`** (via `/pricing-model` where that command is present) — deep
  scenario / crossover / POF-split pricing maths when a deal needs it.
- **`knowledge/domains/negotiation/negotiation-tactics.md`**,
  **`knowledge/domains/negotiation/proposal-narrative.md`**, and
  **`knowledge/domains/pricing/pricing-methodology.md`** — the codified strategy, narrative and
  pricing rules the engine and the brief encode.

## Design philosophy — Plan-first · Gated · Deterministic · Traceable · Walled

1. **Plan-first, not question-first.** Before asking anything, read what is already on disk and
   open with *"here is what I know about this deal — correct me."* Asking a consultant for
   something the engagement folder already holds burns their trust and their time.
2. **Guided, not a black box.** The tool lays out the realm of moves and recommends one; the
   **consultant decides**. A prescriptive tool that "does your job" gets rejected.
3. **Gated — it is inquisitive.** It does not assume intel only a consultant holds. At each gate
   it asks for what is missing across context, deal type, demand, economics and the **5 lever
   families**. Missing intel is recorded as an **open lever**, never silently invented.
4. **Deterministic.** All numbers, tiers, the concession ladder, the Deal Desk verdict, the
   exit-ARR exposure, the buffer play and the lever ledger come from `proposal_builder.py` — a
   pure function of the inputs. Claude writes the **prose around** the engine's numbers; Claude
   does **not** compute them.
5. **Traceable.** Every run ships a **strategy brief** (the trace): why each scenario/anchor was
   picked (cited to the rule §), levers used vs still open, floor headroom, the `inputs_hash`,
   and the pricing source + date. Plus a journal entry with a telemetry block.
6. **Walled.** Internal strategy and client artifacts are separated by an **allowlist** at the
   render boundary, `INTERNAL_` naming on disk, and a leak scan at the verify checkpoint.

## MANDATORY FIRST READS (before doing anything)

1. `tools/proposal_builder.py` — run `python3 tools/proposal_builder.py --print-schema` to see
   the exact config schema you must fill, including `deal_type`, `round`, `pricing_source`,
   `ramp_schedule` and `strategy.buffer_offer`.
2. `knowledge/domains/negotiation/negotiation-tactics.md` — §1 the Martini (concessions shrink),
   §2 the 4-stage ladder, §3 the 5 lever families, §4 lever types (cheap/costly/resist/extract/
   posture), §5 switching cost → posture, §6 floor economics and deal-size bands, §9 Deal Desk
   thresholds and discount authority. The engine encodes these; you run the interview that feeds them.
3. `knowledge/domains/negotiation/proposal-narrative.md` — §1 lifecycle story models and the
   renewal-challenger prohibition, §2 the section library (constants + situational, anti-template
   rule), §3 the value-rationale hierarchy, §4 voice rules, §5 the lever discovery question bank.
   This file decides what the proposal *says*; tactics decides how the deal is *traded*.
4. `knowledge/domains/pricing/pricing-methodology.md` — pricing **basis × LOB** (wealth = AUM,
   retail/SME/commercial = unit-based, conversational = platform + interaction). Confirm the
   basis with the consultant; do not infer it from the CPQ alone.
5. `.claude/commands/proposal-longform.md` — the render target's workflow, its scope guardrail
   and its `PRICING` contract. Its own mandatory reads (the template, the authoring guide, the
   design tokens) are **its** responsibility — do not duplicate them here.

---

## ACT 0 — SCAN FIRST (plan mode). No questions until this is done.

Run in this order, every time, before the first interview question:

1. **Engagement directory.** Locate `engagements/<client>/<engagement>/`. If it does not exist:
   `./scripts/init_engagement.sh <client_short_name> <YYYY-MM_domain_deal> deal_strategy`
   and say so ("New engagement — I'll bootstrap it. Everything comes from you this round.").
2. **`CLIENT_PROFILE.md`** — the persistent client record (history, LOBs, prior engagements,
   incumbent context, relationships).
3. **`ENGAGEMENT_JOURNAL.md`** — what has already happened on this engagement, including any
   prior checkpoints, overrides and deal-notes entries.
4. **`outputs/`** — upstream artifacts that change the proposal: an ROI model
   (`roi_report.md` / `roi_config.json` / `*_ROI_Model.xlsx`), discovery synthesis, capability
   assessment, journey maps, prior proposals and prior `INTERNAL_*` files.
5. **`outputs/INTERNAL_deal_state.json`** — the machine round record. Absent → this is round 1.
   Present → this is round N; see "Round N" below.

Then **SUMMARIZE and hand control back**:

> Here is what I know about this deal — correct me.
> · Client / LOB / region: …
> · Relationship: (new logo | customer since …, prior engagements …)
> · Upstream artifacts on disk: (ROI model ✓ / discovery ✓ / none)
> · Prior rounds: (none — round 1 | round N, last position …)
> · What I still need from you: (the short gap list)

**Ask only the gaps.** Never ask a question the scan already answered; if the scan answered it
partially, state what you found and ask for confirmation instead of asking from scratch.

**The standing exception — PRICING is ALWAYS asked fresh.** Pricing is never recalled from
memory, from knowledge files, from a prior round, or from a previous proposal on disk. It is
pasted fresh by the consultant every run, with its **source and date**, and recorded in
`deal.pricing_source`. Anything found on disk is treated as historical context to reconcile
against, never as the number to price with.

**Round N (deal state present).** Open with a delta report instead of a blank intake: what
changed vs the plan, newly active levers, the original strategy re-surfaced verbatim with why it
was chosen, and the concession history. Then spar on drift against the ladder before re-running.
*(The full loop is **ACT 0-R** below: detection, the five-part delta report, sparring, version
freezing and the state update. Round 1 writes the state file that loop reads.)*

---

## ACT 0-R — ROUND N (the negotiation loop)

**Detection.** The ACT 0 scan finds `outputs/INTERNAL_deal_state.json` and it carries
`current.round ≥ 1` → **this is round N = `current.round` + 1**. Enter round-N mode: the blank
intake does **not** run, and the **delta report opens the conversation** instead of the
"here is what I know" digest. (No state file, or `current.round` absent → round 1, ACT 0 as written.)

Round-N mode is a *revision* of an agreed plan, not a new deal. Read these before saying anything:

| Source | What you take from it |
| --- | --- |
| `outputs/INTERNAL_deal_state.json` | `rounds[]` (the record), `current{}` (round, next planned stage, elasticity exposure), `pending_meeting_notes[]` (stubs `/deal-notes` pushed) |
| `outputs/DEAL_JOURNAL.md` | The human narrative for every entry dated **after** the last `rounds[]` entry — headline state of play, key exchanges & tensions, strategic reads |
| `outputs/INTERNAL_strategy_brief_v{N-1}.md` | The agreed strategy — story model, anchor, ladder rationale cited to § . **Quote it; never paraphrase it.** |
| `outputs/INTERNAL_negotiation_plan_v{N-1}.md` | The planned ladder, each planned concession paired to its extract, the walk-away |
| `outputs/strategy.json` | Last round's ladder numbers (stage prices, `cum_discount_pct`, `increment_pct`, approval tiers) |

If a `pending_meeting_notes` stub points at a journal entry that does not exist, say so and stop
guessing — the stub is a pointer, the journal is the content.

**Pricing is still asked fresh.** The standing exception survives round N unchanged: pricing is
never carried over from `rounds[]`, from a prior `deal_config.json`, or from a prior proposal on
disk. Gate 8 runs again, pasted fresh, with source and date. The state file stores **hashes and
history only — never pricing**.

---

### The DELTA REPORT — the first thing on screen, in this exact order

Do not ask a question, do not request pricing, do not open a gate until all five elements are
presented. Each element is sourced, and each names the file it came from.

**1 · What changed vs the plan.** The client's counter and the new information — drawn from the
`DEAL_JOURNAL.md` entries and `pending_meeting_notes` stubs recorded **since the last round**.
State each as *fact → source → what it moves*:

> · They asked for −12% on ACV (`DEAL_JOURNAL.md#2026-08-12-procurement-review`) — a **price** ask.
> · Active-user volume revised up 150k → 185k (same entry) — moves the **tier**, not the discount.
> · Core-integration readiness slipped two quarters (same entry) — moves **timing**, not price.

Facts only here. The judgement goes in elements 2 and 5.

**2 · Newly active concession levers.** Diff the new meeting content against the previous round's
`open_levers_snapshot[]` and the five lever families (`negotiation-tactics.md` §3). Name only the
levers that **new facts have opened** — a lever that was already open and is still open is not
news; say "unchanged" for those. Each named lever states the fact that opened it:

> · **Family 4 — Timing & cash flow: staggered activation / stub bill** — newly live, because
>   their readiness slipped two quarters. Their own delay is now *our* non-price give.
> · **Family 1 — Phasing** — newly live for the same reason: the deferred scope is theirs to ask
>   for, so sell it as a phase rather than fund it as a discount.
> · **Family 2 — Volume tier** — the upward volume revision is *their* lever, not ours; do not
>   spend margin on something the tier table already gives them.

A slipped date, a budget cycle, a re-org, a new stakeholder and a revised volume are all
lever-opening facts. A lever nobody has intel on stays **OPEN** — that is reserve, not a gap.

**3 · The ORIGINAL agreed strategy, re-surfaced.** Pull the anchor, the planned ladder and the
rationale straight out of `INTERNAL_strategy_brief_v{N-1}.md` and show them **quoted, not
paraphrased** — this is the anchor the conversation is measured against, and paraphrase is how a
plan quietly drifts:

> **What we agreed at round {N-1}** (quoted from `INTERNAL_strategy_brief_v{N-1}.md`):
> > "Story model: Why Change. Anchor: Best at full scope, 5-yr term, list-anchored, zero discount
> > — §2 stage 1. Discount budget 8% of list, spent on the Martini 0 / 4.8 / 7.2 / 8.0 (§1)."
>
> **Why it was chosen:** …the brief's own rationale lines, cited to their § .

**4 · Concession history — in client-facing phrasing.** What we have actually moved on so far,
stated the way it would be said to the client. **No internal budget percentages, no ladder
internals, no stage names, no extract list, no walk-away** — this element is the sentence the
consultant can say out loud in the room:

> "We have moved on **payment terms** and **the sandbox environment** — we have not moved on price."

Pull the substance from `rounds[].concessions.given[]`; translate it, do not dump it. If nothing
has been given yet, say so plainly: "Nothing conceded yet — the anchor is intact."

**5 · SPARRING — the ask against the plan.** Compare the client's ask to the planned increment at
`current.next_planned_stage` in the prior round's ladder. This is the element that earns the
command its keep, so make it explicit and arithmetic:

| Say | Sourced from |
| --- | --- |
| **The planned figure** — "plan says Counter 1 = −4.8% cumulative (increment 4.8%)" | prior `strategy.json` ladder at `current.next_planned_stage` |
| **The deviation** — "the ask is −12%: 2.5× the planned move, and above the whole 8% budget" | the ask (element 1) vs the plan |
| **The Martini implication** — "**this shortens the stem**: a 12% move here leaves nothing smaller to give at Counter 2 and BAFO, and the shape flips from Martini to Wrecking Ball" | `negotiation-tactics.md` §1 |
| **The extract required to even consider it** — "to take it: year-one prepay **and** a written expansion commitment, plus the 5-yr term signed — §2 stage 3 pricing, pulled forward" | `negotiation-tactics.md` §2 / §4 (every give is traded, never gifted) |
| **The recommendation** | **The default is HOLD** — see below |

**The default recommendation is HOLD.** Say it as a recommendation with its reason, not as a
refusal: hold the planned increment, spend families 1→4 against the newly opened levers first
(§3), and put the price lever back where it belongs — last. Offer the trade as the alternative,
never as the opener.

**Consultant override → journaled.** The consultant can overrule and take the bigger move. Then:
state the §1 consequence once, take the instruction, and **journal the override** in
`ENGAGEMENT_JOURNAL.md` with its reason, the planned figure, the figure actually taken and the
extract secured in return. Record it in the new round's `concessions.given[]` too. An unlogged
override is a defect.

---

### After the delta report — the round-N run

The delta report replaces the intake; everything downstream runs as normal, in revise mode:

1. **Revised DEAL BRIEF checkpoint (v{N})** — CHECKPOINT 1 re-run as a *diff on the approved
   v{N-1} brief*, not a blank brief. It must carry the round-specific sections named at
   Checkpoint 1 item 5 ("what we heard — and what's changed" + the client-language concession
   history), plus what element 5 concluded (hold / trade, and the extract). Written to
   `outputs/CHECKPOINT_deal_brief_v{N}.md` — a **new file**, never an edit of v{N-1}.
2. **Fresh pricing gate** — Gate 8, unchanged, pasted fresh with source and date. Hard stop if
   absent; there are no defaults for money and no carry-over from round N-1.
3. **Engine re-run** — ACT 2 with the revised `deal_config.json` (`deal.round` = N). The engine
   recomputes the ladder for this round; you do not hand-adjust the prior ladder.
4. **Commercial checkpoint** — CHECKPOINT 2, adding the **before/after ladder** (planned vs this
   round's) so the consultant sees the shape is still a Martini after the revision.
5. **Generate v{N} outputs** — the ACT 4 file set at `v{N}`, then CHECKPOINT 3 verify, then the
   journal entry, then the **state update** below.

---

### Version freezing — prior versions are immutable

Every `v{<N}` file in `outputs/` is **frozen**: the deal brief, the proposal HTML and zip, the
strategy brief, the negotiation plan, the Deal Desk fields. They are the record of what was
actually shown and agreed at that round, and the audit value dies if they move.

If anything in this run would write, edit, patch, re-render or "just fix a typo in" a prior
version, **refuse with this exact message**:

> v{N-1} is frozen — changes go in v{N}.

Then do the change in the current version instead. This applies to consultant requests as much as
to your own tidying — the recovery is always a new version, never an in-place edit. (Same rule,
same wording, as the "Frozen version modified" row in Error behaviors.) `deal_config.json`,
`strategy.json` and `INTERNAL_deal_state.json` are the exceptions by design: the first two are
overwritten by the current run and the third is **appended to**, never rewritten.

---

### BAFO round — surface the buffer play

When `current.next_planned_stage` is `bafo`, this round is Best & Final (§2 stage 4: smallest
move, dated, final). Surface the engine's **`buffer` block** as **the closing-give candidate** —
in place of reaching for another price cut:

- **Price-hold framing** — it is a **hold on the price of future growth**, never a discount, and
  never described as one. It costs list-rate upside on volume that has not landed; it does not cut
  the price of volume that has.
- **Give-to-get conditions** — the engine's `buffer.conditions[]`, each stated as a condition of
  the hold, per §4 (extract, not gift). No condition, no hold.
- **The travel story** — `buffer.buffer_price` vs `buffer.ramp_price` and the resulting
  `buffer.saving_vs_ramp`: what the client's number *has travelled* from the earlier ramp price to
  here. This is the closing narrative, and the figures come from the engine verbatim.
- **Gated, not granted** — the price-hold addendum is Deal Desk sign-off, not rep authority (§9).
  Say which approval tier the engine returned, and that the deadline is stated **once**.

If the engine returned no `buffer` block, say so — do not invent a buffer offer to have something
to close with. The BAFO move is then simply the smallest ladder increment, dated and final.

---

### State update — on every generate

After the v{N} outputs are written and verified, append to `outputs/INTERNAL_deal_state.json`.
**Append and update — never rewrite the file, never edit a prior `rounds[]` entry.** Consume the
`pending_meeting_notes[]` stubs: their `meeting_ref` values move into this round's
`meeting_note_refs[]` and the `pending_meeting_notes` array is **cleared** (left as `[]`), so the
same meeting is never counted into two rounds.

```json
{
  "rounds": [
    { "n": 1, "date": "YYYY-MM-DD", "inputs_hash": "<round-1 hash>",
      "scenarios_shown": ["A anchor", "B alternative"],
      "ladder_position": "anchor",
      "concessions": { "given": [], "extracted": ["Reference rights"] },
      "meeting_note_refs": [],
      "open_levers_snapshot": ["<from strategy.json open_levers>"],
      "strategy_summary": "<one line: story model, anchor, why B is lighter>" },

    { "n": 2, "date": "YYYY-MM-DD", "inputs_hash": "<from THIS run's strategy.json>",
      "scenarios_shown": ["A anchor (revised)", "B alternative"],
      "ladder_position": "counter1",
      "concessions": {
        "given":     ["Net 60 payment terms", "Staggered activation to Q3"],
        "extracted": ["Signed 5-yr term", "Reference rights confirmed"]
      },
      "meeting_note_refs": ["DEAL_JOURNAL.md#2026-08-12-procurement-review"],
      "open_levers_snapshot": ["<from THIS run's strategy.json open_levers>"],
      "strategy_summary": "<one line: what this round held, what it traded, and why>" }
  ],
  "current": { "round": 2, "next_planned_stage": "counter2",
               "elasticity_exposure": "conservative" },
  "pending_meeting_notes": []
}
```

Field rules:

- `n` — the round just generated. `current.round` matches it.
- `inputs_hash` — copied from **this run's** `strategy.json`, so the round is reproducible.
- `ladder_position` — the stage this round actually landed on (engine stage keys: `anchor`,
  `counter1`, `counter2`, `bafo`).
- `concessions.given[] / extracted[]` — what was actually moved and actually taken, in plain
  words. This is what element 4 will translate next round; keep it factual, not client-phrased.
- `meeting_note_refs[]` — the consumed `pending_meeting_notes` refs, in date order.
- `open_levers_snapshot[]` — this run's `open_levers` from `strategy.json`. Element 2 next round
  diffs against it, so it must be the engine's list, not a hand-edited one.
- `strategy_summary` — one line, so a later round can re-surface the plan without re-reading
  everything.
- `current.next_planned_stage` — the **next** stage on the ladder, not the one just played.
- **No pricing in this file. Ever.** Hashes, stage names and history only — prices live in
  `strategy.json` and in the pricing pasted fresh each run.

---

## ACT 1 — The gated interview (truth-teller, gap-only)

Work the gates in order. For each: if the consultant supplies it, record it; if not, record it
**OPEN** (still on the table) and move on. Never fill a gap with an invention.

**Gate 1 — CPQ ingest.** Parse the export (Excel/CSV/pasted lines) into line items: product ·
edition · basis (Base Fee + AUM/User/etc. Fee) · qty metric · per-year fees · 3rd-party
pass-through **held separate**. Echo the parsed table back and have the consultant confirm before
proceeding. If the format is unfamiliar, show what you could parse and say so — do not guess the
missing columns. Confirm the **LOB and pricing basis** against `pricing-methodology.md`.

**Gate 2 — Deal type → story model.** *This gate runs before a single word of narrative.*
Ask: **new logo, renewal, or expansion?** Then propose the story model with a one-line rationale,
per `proposal-narrative.md` §1:

| `deal_type` | Story model | Opening move |
| --- | --- | --- |
| `new_logo` | **Why Change** (and **Why Now** late-stage) | Unconsidered needs first, contrast framing, status quo framed as a loss |
| `renewal` | **Why Stay** | Results delivered → original decision process → risk of change → cost of change → advances since signing |
| `renewal` with an increase | **Why Pay** | Why Stay, plus new capabilities + anchor + a justified timed discount |
| `expansion` | **Why Stay / cost-of-current-state** | What staying as-is is quietly costing |

> **MUST NOT:** a renewal or expansion proposal never opens with a challenger / "why change" /
> transformation narrative. It measurably increases switching intent with an existing customer
> (`proposal-narrative.md` §1). This is a hard rule, not a tone preference. An override requires an
> **explicit consultant instruction**, and it is **journaled** as an override with the reason.

Record `deal.deal_type` and `deal.round` in the config.

**Gate 3 — Demand plan by firmness.** Classify the demand behind the volumes: **validated**
(contracted/observed), **projected** (planned, agreed basis), **pipeline** (hoped-for). **Pipeline
demand is NEVER priced in** — it is *seeded* (a tier that exists at list, priced if and when it
lands). Say which tier each volume driver sits in.

**Gate 4 — Economics.** GM ARR %, floor GM %, and where known managed-hosting / managed-services
/ professional-services GM % and first-year ARR %. **"Unknown" is an allowed answer** — it is
flagged, never defaulted: the run continues, floor headroom is omitted, and the Deal Desk pack is
marked "needs Finance". Never invent a margin.

**Gate 5 — The 5 lever families, spent 1→4 before price** (`negotiation-tactics.md` §3; discovery
questions in `proposal-narrative.md` §5). For each family ask "what can you offer, and what do you
take back?" — every give is paired to an **extract**:

1. **Solution optionality** (zero margin cost — *anchor here*): Good/Better/Best TCVs, bundle/
   unbundle, phasing, scope ramp.
2. **Commitment terms** (often margin-accretive): 3/5/10-yr term, volume tier, year-one prepay,
   expansion commit — *and the extract taken for each*.
3. **Non-price value** (capacity cost — price the bench, don't treat as free): sandbox, training
   credits, premium SLA, program architect, dedicated CS.
4. **Timing & cash flow** (cost of capital only): payment terms, stub bill, staggered activation,
   billing cadence.
5. **Price** (last resort, 1:1 margin hit): the target BAFO discount % — and confirm out loud
   that it is the *last* lever, not the first.

Families with no answer are recorded `open` in the ledger — that is a feature: it is reserve.

**Gate 6 — The two-scenario mandate.** Exactly **two** client-facing scenarios: the **anchor (A)**
and a deliberately **lighter alternative (B)**, plus the client-facing **reason B is lighter**, plus
the **walk-away** (internal, never shown). A third scenario requires an explicit consultant
override, logged in the journal (`proposal-narrative.md` §2) — it is never a default.

**Gate 7 — Value-rationale hierarchy** (`proposal-narrative.md` §3). Ask directly:
*"Is there an upstream ROI model, a value rationale, or do we need a guarded napkin?"*

1. **Upstream ROI model exists** (the scan will usually have found it) → import the headline
   numbers, cite the model as a companion document, do not re-derive its math in the proposal.
2. **No model → value rationale.** Defend-the-price (renewals) or cost-of-current-state
   (expansions). No invented business case.
3. **Neither → an OPTIONAL guarded back-of-napkin**, built **only** from consultant-confirmed
   inputs, every input logged in the assumptions register, and the output labelled
   **"directional — not a business case."** Never silently generated.

If none of the three applies, the proposal carries **no financial-return claims**. A proposal with
no numbers is a valid proposal; a proposal with invented numbers is not.

**Gate 8 — PRICING, pasted fresh.** Ask for the current deal-desk numbers, with **source and
date**. Record them in `deal.pricing_source` and echo them back for confirmation at the commercial
checkpoint. If they are not supplied, this is a **hard stop** (see Error behaviors) — there are no
defaults for money.

**Fast-draft mode.** If the consultant says "just give me a first cut" / "use sensible defaults":
fill the config with conservative defaults, generate, and then surface every skipped gate on the
output as "confirm/refine these". Defaults are labelled as defaults in the brief. **Pricing is never
defaulted, even in fast-draft** — Gate 8 still hard-stops. Either way the consultant ends up
applying the strategy.

---

## CHECKPOINT 1 (pre-generation) — the DEAL BRIEF

One consolidated artifact, presented in the conversation and iterated **as a whole** — not a
series of small approvals. It is the contract the rest of the run is measured against.

The brief contains:

1. **Context as understood** — client, LOB, basis, region price list, term, relationship history,
   what the scan found and what the consultant corrected.
2. **Story model** — the chosen model from Gate 2, with its one-line rationale and the deal type
   it follows from.
3. **Section set** — proposed *per deal* from the library in `proposal-narrative.md` §2, never a
   fixed template. Constants always present: **two pricing options · assumptions on the record ·
   close plan**. Situational sections chosen with their when-to-use reason.
4. **Value-rationale flavor** — which tier of §3 applies and what it will be built from.
5. **Round-specific sections** — round ≥ 2 adds "what we heard — and what's changed" and a
   client-language concession history.
6. **Assumptions + confidence** — every assumption stated with a confidence level and a validation
   owner.
7. **Open items** — the levers and facts still OPEN, stated as reserve, not as blockers.

Iterate until the consultant approves it **as a whole**, then write it to
`outputs/CHECKPOINT_deal_brief_v{N}.md` (N = round). This write also satisfies the
`require-checkpoint.py` pre-generation gate for the deliverables that follow.

**Non-interactive runs:** do not pause. Record both this checkpoint and the post-generation
verify checkpoint in `ENGAGEMENT_JOURNAL.md` as `### Checkpoint:` blocks instead — the same
convention `/proposal-longform` uses.

---

## ACT 2 — Run the deterministic engine

Write the assembled config, then run the engine. Use its numbers **verbatim**.

```bash
python3 tools/proposal_builder.py \
    --config engagements/<client>/<engagement>/outputs/deal_config.json \
    --json   engagements/<client>/<engagement>/outputs/strategy.json \
    --out    engagements/<client>/<engagement>/outputs/INTERNAL_strategy_brief_v{N}.md
```

The engine returns: economics (TCV/ACV/floor headroom/deal-size band) · the two scenarios · the
**Martini concession ladder** (per stage: posture, next-best-action, cum/increment %, price,
**approval tier**, extract-in-return) · the **shape** verdict (Martini ✓ vs Avalanche) · the
**Deal Desk** trigger check, pack and verdict · the **lever ledger** (used vs open per family) ·
leverage posture · the **rationale** traced to rule § · `open_levers[]` · `inputs_hash`. When the
config carries a `ramp_schedule` it also returns **`exit_arr`** (reported ARR vs exit ARR and the
downsell exposure, with a flag); when it carries `strategy.buffer_offer` it returns **`buffer`**
(the price hold on future growth — *never* described as a discount).

Do not recompute, round, re-derive or "sanity adjust" any of these. If a number looks wrong, the
**config** is wrong — fix the interview answer and re-run.

For deep scenario projections / crossover / POF back-solve, optionally derive a pricing-model
config from the same deal and fold its tables in.

---

## CHECKPOINT 2 — the COMMERCIAL checkpoint

Walk the consultant through the engine's output before anything is rendered:

- **Pricing echoed back** — the pasted numbers, their source and date, for explicit confirmation.
- **The ladder** — Anchor → Counter 1 → Counter 2 → BAFO, each with its price, its move size, its
  **approval tier** (SVP / CRO / Deal Desk per §9 region authority) and the **extract** taken in
  return. Confirm the shape is a Martini (shrinking), not an Avalanche.
- **Scenario tiers** — A "Recommended" and B "Alternative", with the client-facing reason B is
  lighter. The walk-away is stated here for the consultant and goes no further.
- **Exit-ARR warning** — when the engine flags a ramped structure: reported ARR vs exit ARR and the
  **downsell exposure** (what churn actually costs at the end of the ramp), stated plainly.
- **Buffer-play candidate** — at BAFO, if a buffer offer is configured: the price-hold framing, the
  give-to-get conditions, and the saving vs the ramp price. Framed as a **price hold on future
  growth**, never as a discount.
- **Elasticity exposure setting** — which pricing drivers the client's sliders will expose in the
  rendered proposal. **Conservative by default** (volume and term only). Opening more drivers is a
  deliberate dial the consultant or Deal Desk turns, and the setting is stated here on the record.
- **Deal Desk verdict** — whether this goes to Deal Desk and which threshold triggered it, plus what
  the pack still needs (e.g. "GM unknown — needs Finance").

---

## ACT 3 — Render the client proposal via `/proposal-longform`

The client artifact is produced by **`/proposal-longform`**, not by this command and not by
`/frontline-long-form`. Hand it a **client-safe contract** and nothing else.

**ALLOWLIST — the only things that cross the boundary:**

1. **Sections** per the approved deal brief — story-model-ordered, in the value-rationale flavor
   chosen at Gate 7, written to the voice rules in `proposal-narrative.md` §4.
2. **PRICING config** — currency, base fee, and **published / list tiers only**, plus the scenario
   presets. Published basis only.
3. **Scenario cards** — A "Recommended" and B "Alternative", with the client-facing reason B is
   lighter.
4. **Elasticity exposure setting** — which drivers get sliders, per the commercial checkpoint.
5. **Assumptions table** — every assumed number with its validation owner.
6. **Non-binding disclaimer** — projected, list/published basis, explicitly not a quote, in every
   language rendered.

**PROHIBITED — these NEVER cross to the renderer, in any form, paraphrased or numeric:**

- the **concession ladder** (any stage, price or move size)
- **extracts** / what we take in return
- **floors**, floor gross margin, floor headroom, discount-to-floor
- the **walk-away**
- **approval tiers** and discount authority (SVP / CRO / Deal Desk levels)
- the **lever ledger** (used vs open levers)
- the **Deal Desk verdict**, triggers and pack
- **anything named `INTERNAL_*`** — the renderer never reads those files at all

Treat this as **allowlist-first**: build the handover from the allowlist, item by item. The
prohibited list is the **backstop** the verify scan greps for — not the primary control. If
something is not on the allowlist, it does not cross, whether or not it appears on the blocklist.

---

## ACT 4 — Outputs

All into `engagements/<client>/<engagement>/outputs/`. `{N}` is the negotiation round.
**Never edit a prior version in place** — prior versions are frozen.

| File | Audience | Contents |
| --- | --- | --- |
| `{CLIENT}_Proposal_v{N}.html` | **Client** | The rendered interactive proposal from `/proposal-longform` |
| `{CLIENT}_Proposal_v{N}.zip` | **Client** | Packaging: **client HTML ONLY**, with `index.html` at the zip root |
| `CHECKPOINT_deal_brief_v{N}.md` | Internal | The approved brief (written at Checkpoint 1) |
| `deal_config.json` | Internal | The exact engine input for this run |
| `strategy.json` | Internal | The engine output — the number source of truth |
| `INTERNAL_strategy_brief_v{N}.md` | Internal | The trace: rationale cited to §, lever ledger, floor headroom, posture, pricing source + date, `inputs_hash` |
| `INTERNAL_negotiation_plan_v{N}.md` | Internal | The ladder, planned concessions paired to their extracts, the final exec give, the walk-away |
| `INTERNAL_deal_desk_fields_v{N}.md` | Internal | The Deal Desk pack fields the engine emits: complete commercial model, GM by component, trigger verdict, Digital Solutioning / RFF / Deal-QA placeholders |
| `INTERNAL_deal_state.json` | Internal | The machine round record (see below) |

`INTERNAL_deal_state.json` — round-1 shape (the round-N loop appends to `rounds[]`):

```json
{
  "rounds": [
    { "n": 1, "date": "YYYY-MM-DD", "inputs_hash": "<from strategy.json>",
      "scenarios_shown": ["A anchor", "B alternative"],
      "ladder_position": "anchor",
      "concessions": { "given": [], "extracted": [] },
      "meeting_note_refs": [],
      "open_levers_snapshot": ["<from strategy.json open_levers>"],
      "strategy_summary": "<one paragraph: story model, anchor, why B is lighter>" }
  ],
  "current": { "round": 1, "next_planned_stage": "counter1",
               "elasticity_exposure": "conservative" }
}
```

Round ≥ 2 appends a new `rounds[]` entry and updates `current{}` — the full shape, the field rules
and the `pending_meeting_notes` consumption are in **ACT 0-R → State update**.

**Hand-off note (stub).** Mapping the agreed terms onto the Spotdraft order-form structure
(Parties · Modules · Products · Services · Term table · standard vs special conditions) is
**stubbed** — say so explicitly and flag the dependency on the order-form template. Do not
hand-build field-level mapping.

---

## CHECKPOINT 3 (post-generation) — VERIFY

Reconcile before declaring done, and report honestly:

1. **Numbers.** Every number rendered in the client proposal traces to `strategy.json` — no
   recomputation, no rounding drift, no number that exists only in prose.
2. **Sections.** The rendered section set matches the approved `CHECKPOINT_deal_brief_v{N}.md`
   exactly — additions and omissions are both defects.
3. **INTERNAL leak scan.** Grep the client HTML (and the zip contents) for `INTERNAL_`,
   `walk-away` / `walkaway`, `floor`, `ladder`, `anchor`, `BAFO`, `concession`, `extract`,
   `approval tier`, `Deal Desk`, `SVP`, `CRO`, and the walk-away figure itself.
   **Required result: zero hits.** Any hit auto-blocks delivery, is removed, and the render repeats.
4. **`/proposal-longform` QA checklist** — run it in full: language toggle, slider sweeps with no
   NaN and reconciling totals, presets, the executive readout in each language, the disclaimer
   present everywhere, no internal-only content, assumptions table complete.
5. **Defects enumerated.** State "N defects found and fixed: …" plainly. Do not report a clean run
   you did not get.

---

## Error behaviors (use these messages)

| Error | Cause | Message to the consultant | Recovery |
| --- | --- | --- | --- |
| Missing pricing | No deal-desk numbers supplied | "I can't price this — paste the current deal-desk numbers (with source + date). I never reuse pricing from memory or prior rounds." | Paste pricing; run resumes |
| Engine input invalid | Config field missing / wrong type | Quote the engine's own error **verbatim**, plus which interview answer feeds that field | Fix the answer; re-run |
| Unscrubbed transcript | PII in a `/deal-notes` input | Surface the anonymize-guard block plus the exact `anonymize_transcript.py` command | Scrub; re-run |
| Write blocked | No checkpoint before a deliverable | Surface the hook denial: "Deal brief not yet approved — that's the missing checkpoint." | Approve the brief |
| Martini violated | An override grows a concession | "This breaks the shrinking rule (§1) — it signals more is available. Override requires an explicit note; I'll journal it." | Confirm override or re-pace |
| Pipeline demand priced in | Firmness gate contradiction | "That demand is pipeline-tier — pricing it in violates the demand-plan rule. Seed it instead?" | Reclassify or seed |
| INTERNAL leak detected | Internal string in the render input or output | "Blocked: negotiation content in the client artifact. Removed: [list]. Regenerating." | Automatic; logged |
| Napkin math unsourced | Value claim without logged inputs | "I need your inputs for this figure — I don't invent financials. Give me the basis or the claim comes out." | Supply basis or drop |
| Frozen version modified | Attempt to edit a prior `v{N-1}` | "v{N-1} is frozen — changes go in v{N}." | New version |

Two more standing refusals:

- **Engine degraded, not defaulted.** GM unknown → the run continues, floor headroom is omitted,
  and the Deal Desk pack is flagged "needs Finance". Never substitute a plausible margin.
- **Renewal challenger override.** If the consultant insists on a challenger narrative for a
  renewal or expansion, state the §1 finding, require an explicit instruction, proceed only then,
  and journal the override with its reason.

---

## Governance (mandatory — per CLAUDE.md)

- **Journal** — append an entry to `ENGAGEMENT_JOURNAL.md` on completion, with a
  `<!-- TELEMETRY_START -->` block.
- **Checkpoints** — the deal brief (pre-generation), the commercial checkpoint, and verify
  (post-generation). In non-interactive runs all are recorded in the journal rather than paused on.
- **Provenance** — every output records the generating command, `proposal_builder.py`, the rule
  source, the pricing source + date, and the `inputs_hash`. Re-running the same config reproduces
  the same strategy — say this to the consultant; determinism is the trust argument.
- **No invented data** — missing intel is an *open lever*, never a silent assumption. Conservative
  bias on any pricing. Every assumption carries a confidence level and a validation owner.
- **Anonymization** — any transcript or meeting input passes the anonymize-guard before it is read.

## Anti-patterns

- Asking the consultant questions the engagement folder already answered. → **Scan first**, then ask only gaps.
- Reusing pricing from a prior round, a knowledge file, or memory. → Pricing is pasted fresh, every run, with source + date.
- Computing the ladder, tier, floor headroom, exit ARR or Deal Desk verdict yourself. → Run the engine; it is deterministic and rule-traced.
- Filling missing lever intel with assumptions. → Ask, or mark it **open**.
- Opening on price (Family 5). → Anchor on configuration (Family 1); spend 1→4 first.
- Opening a renewal with a challenger / transformation narrative. → Why Stay / Why Pay (§1). Hard rule.
- A third client-facing scenario "to give them choice". → Exactly two, unless explicitly overridden and journaled.
- Filling a fixed proposal template. → Propose a **section set per deal** at the brief checkpoint.
- Producing a back-of-napkin figure the consultant never confirmed. → Directional napkin only from logged inputs, labelled as directional.
- Showing the walk-away, the floor or the ladder to the client. → Internal only; the allowlist is what crosses.
- Rendering the client proposal yourself, or via `/frontline-long-form`. → `/proposal-longform` renders; you hand it the allowlist.
- Editing a prior version in place. → Prior versions are frozen; changes go in `v{N}`.
- Hand-building the Spotdraft field mapping. → Stub it; flag the template dependency.

## Worked reference run

`python3 tools/proposal_builder.py --selftest` runs the engine's built-in synthetic fixtures
(fictional client, invented numbers) and asserts determinism, the ladder rules, the exit-ARR block
on a ramped structure, the buffer block, and the pricing-provenance line in the brief. Use it to
see the shape of a full engine output before you run a real deal — and to confirm the engine is
healthy if a run looks wrong.
