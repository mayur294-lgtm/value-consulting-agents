# Proposal Narrative — Lifecycle Story Models & Section Library

**Status:** CURRENT — August 2026 (v1.0)
**Sources:**
- Corporate Visions / Riesterer simulation research (message-testing studies on story structure, contrast framing, loss framing, and status-quo bias in B2B buying decisions)
- Internal deal structuring & negotiation enablement deck (2511)
- Production proposal evidence (2026) — a small number of real proposal cycles run through this logic, described generically below with no client identifiers

**Internal use only**

**How this file relates to `negotiation-tactics.md`:** that file is *how to negotiate* — the concession ladder, lever families, deal-desk governance. This file is *what story the proposal tells* — which narrative a proposal should open with, which sections it earns, where its financial claims are allowed to come from, and how it should read. The two meet at the concession history and lever sections below, which cross-reference `negotiation-tactics.md` §3/§4 rather than restating them.

---

## 1. Lifecycle story models

A proposal's opening narrative is not a style choice — it is a function of where the deal sits on the customer lifecycle, split at the **customer line**:

- **Before the line (acquisition):** the goal is to **DEFEAT status-quo bias**. The prospect's default is to do nothing; the story has to make inaction feel like the risk.
- **After the line (retention):** the goal is to **REINFORCE status-quo bias**. The customer's default is to stay; the story should make that default feel obviously right, not put it up for debate.

Four story models follow from this split. Deal type is the first branch of every proposal — pick the model from the deal type, not from house style or habit.

### Why Change (new logo)

Lead with **unconsidered needs** — gaps the prospect hasn't yet framed as problems — **before** presenting the solution. In Corporate Visions' simulation testing, unconsidered-needs-first messaging beat a standard solution-first pitch on uniqueness (+50%), quality (+10%), and overall persuasion (+10%).

Two supporting techniques:
- **Create contrast.** Show current state and future state side-by-side rather than describing the future state alone. Testing showed contrast framing lifted product perception +13.4%, willingness to pay +14.1%, and purchase intent +14.6% over a future-state-only description.
- **Frame the status quo as a loss, not a gain.** "Staying as you are costs you X" outperforms "changing gets you X" — loss framing tested ~70% more persuasive, consistent with prospect theory's finding that people weight avoiding a loss 2–3× more heavily than acquiring an equivalent gain.

### Why Now (late-stage urgency / no-decision risk)

The structure that wins late-stage: **Business Issue + Unconsidered Needs + hard-number ROI**. Tested against five other message structures, this combination won on decision confidence, urgency (+2%), and likely-to-purchase-now (+9%). The closing proposal must still answer "why now" explicitly — no-decision (the prospect doing nothing at all) is the dominant late-stage loss mode, not losing to a named competitor.

### Why Stay (renewal)

**Reinforce** the status quo, in this fixed order:
1. Document the results already delivered.
2. Review the original decision process — remind them they ran a thorough selection and it held up.
3. Mention the risk of change.
4. Highlight the cost of change.
5. Detail the competitive advances made since signing.

In head-to-head testing against a provocative challenger message aimed at existing customers, this Reinforce sequence won: attitudes toward the vendor +9.63%, intention to renew +13.27%, and likelihood of switching −10.61%.

### Why Pay (renewal with a price increase)

The Why Stay model, plus the increase itself framed as **new capabilities + an anchor + a "justified" timed discount**. Of six framings tested for introducing a renewal price increase, this combination performed best (attitude spread 18.8%, likely-renew spread 15.5%).

The **worst** tested framing: introducing the increase through an unconsidered-needs challenge — the same technique that works for Why Change backfires here, becoming the framing most likely to trigger switching consideration (16.3% spread) and active competitive shopping. Do not reuse Why Change's opening move inside a Why Pay proposal.

### The hard rule

A renewal or expansion proposal **MUST NOT** open with a challenger / "why change" / transformation narrative. This is not a tone preference — the research above shows it measurably increases switching intent with an existing customer. Deal type is the first branch of every proposal:
- `new_logo` → Why Change / Why Now
- `renewal` / `expansion` → Why Stay / Why Pay

A proposal-building skill or agent that reads `deal_type` from engagement context (see `negotiation-tactics.md` and the pricing engine's `deal_type` field) must route on that value before drafting a single word of narrative.

---

## 2. Section library

There is no fixed table of contents. A proposal is assembled from a **constant set** every deal carries, plus a **situational set** chosen per deal at the brief checkpoint based on deal type and round.

### Constants — every proposal includes these

- **Pricing options.** Exactly **two** scenarios: the client's ask and our recommendation. A third scenario requires an explicit consultant override, logged in the engagement journal — it is never a default.
- **Assumptions on the record.** Every assumption behind the numbers in the proposal, stated plainly, not buried in an appendix.
- **Close plan.** Mutual, dated next steps — not a generic "next steps" slide, a plan both sides can be held to.

### Situational — chosen per deal, with when-to-use rules

| Section | When to use |
|---|---|
| "What we heard — and what's changed" | Round ≥ 2. An opener that shows the proposal actually moved since the last round, not a reprint. |
| Concession history (plain, client-facing) | Round ≥ 2. Stated in language the client reads, not internal terms — e.g. "one reduction, two things we are not charging you for," never internal budget percentages or floor-to-offer math. Cross-reference `negotiation-tactics.md` §3/§4 for what a concession is drawn from; this section reports the moves already made, in client language. |
| Delivered-value recap — "the platform is not the one the agreement was signed against" | Renewals. Documents what shipped since signing as part of the Why Stay sequence (§1, step 1 and step 5). |
| Cost-of-current-state | Expansions. E.g. "six reasons your stack costs more than it looks" — makes the case for the expansion by pricing the cost of not doing it. |
| Value-by-line-of-business | When the buying committee spans multiple LOBs and a single blended value story would flatten real differences between them. |
| Executive readout | One page, print-ready. For the person in the room who will not read the rest. |

### Anti-template rule

A proposal-building skill or agent **proposes a section set per deal at the brief checkpoint** — it does not fill in a fixed template. The classic six-part storyline below is a **jobs list**, not a table of contents: each job can be done by a different section depending on deal type, round, and what the client actually needs to see next.

1. The journey (how we got here / where this deal sits in the relationship)
2. Pricing options
3. Concession history
4. The business case (see §3 below — this job is filled by whichever value-rationale tier applies, not by a fixed "Business Case" chapter)
5. Proof
6. Close plan

---

## 3. Value-rationale hierarchy

There is no fixed "Business Case" chapter. The section that carries the financial argument is filled from a strict hierarchy, checked in order:

1. **An upstream ROI model exists in the engagement.** Import the headline numbers and cite the model as a companion document. Do not re-derive or restate the model's math inside the proposal — point to it.
2. **No ROI model exists — use a value rationale.** Make the case for "why this makes sense in your current situation" without inventing a business case. Two flavors, matched to deal type:
   - **Defend-the-price** (renewals): what's been delivered, what the client is not being charged for, the platform advances made since signing. This is the Why Stay/Why Pay sequence (§1) rendered as the value section.
   - **Cost-of-current-state** (expansions): what staying as-is is quietly costing, mirroring the situational section in §2.
3. **Neither applies — an OPTIONAL guarded back-of-napkin, and only then.** This estimate MUST be built **only** from consultant-confirmed inputs — every input logged in the assumptions register — and the output MUST be labeled **"directional — not a business case."** It is **never silently generated**: no proposal produces a back-of-napkin figure without a consultant having confirmed the specific inputs that went into it.

If none of the three tiers applies — no ROI model, no value rationale can honestly be written, and no consultant-confirmed inputs are available for a back-of-napkin — **the proposal carries no financial-return claims.** A proposal with no numbers is a valid proposal. A proposal with invented numbers is not.

---

## 4. Voice rules

- **Headers are plain declarative statements that carry the message**, not labels. "Why our price holds," "Nothing is removed," "The numbers, in the open," "Built on your numbers, not ours" — not "Executive Summary," "Our Solution," "Pricing."
- **Never use transformation-marketing language.** No "unlock," "reimagine," "journey to the future of banking" — that register belongs to acquisition decks, not proposals, and is actively counterproductive in a renewal (see the Why Pay worst-case framing in §1).
- **Numbers stay in the open, with their formulas visible.** A reader should be able to see how a number was built, not just the result.
- **Understated and factual**, not persuasive-sounding. The persuasion is in the structure (§1), not in adjectives.
- **One idea per section.** Don't let a pricing section quietly also argue value, or a value section quietly also argue urgency.
- **Maximum 4 key points per view**, matching the Frontline design-system rule elsewhere in this repo (`CLAUDE.md` → `/frontline` tone rules) — a proposal view that needs a 5th point needs a second view instead.

---

## 5. Lever discovery question bank

`negotiation-tactics.md` §3 defines the five lever families and the rule to exhaust families 1–4 before touching price. This section is the client-facing question bank for surfacing what a client will actually trade **before** either side names a number — do not restate the family definitions here; only the discovery questions.

**Family 1 — Solution optionality**
- Which of these capabilities must be live in year one, and which are ambitions for later?
- If we phased this into two waves instead of one, what would you want in wave one?
- Is there a "good enough to start" version of this scope you'd sign today?
- Which of these modules would you unbundle if it meant starting sooner?

**Family 2 — Commitment terms**
- If the price of growth were fixed today, what growth would you actually commit to?
- Would a longer term change what you're comfortable committing to now?
- Is there a volume or usage level you're confident you'll hit regardless of how this negotiation ends?
- What would make a multi-year commitment an easy yes rather than a hard one?

**Family 3 — Non-price value**
- What would make your team self-sufficient fastest — training, a sandbox, a named architect?
- Where does your team most need hands-on support in the first six months?
- If we gave you a dedicated point of contact instead of a discount, would that change the decision?
- What's the one thing that, if we included it, would make the price conversation less important?

**Family 4 — Timing / cash-flow readiness**
- Your integration APIs land in Q3 — should the connector fees start when they do, not before?
- Would a smaller first-year invoice unlock this year's budget?
- Does your fiscal calendar make a staggered start easier to approve than a single go-live date?
- If payment terms flexed, would that change the scope you're willing to commit to?

**Family 5 — Price (the questions that DELAY price)**
- Before we talk number — which of the above moved?
- Of everything we've discussed, what's still unresolved besides price?
- If we solved [the open non-price item], would price still be the blocker?
- What number are you anchored to, and where did it come from?

These are discovery questions, asked before or during the concession ladder in `negotiation-tactics.md` §2 — they open space in families 1–4 so that price (family 5) is the last, not the first, thing negotiated.
