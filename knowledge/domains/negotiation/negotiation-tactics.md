# Negotiation & Commercial Strategy — Tactics Library

**Status:** CANONICAL for commercial negotiation. Reusable across any deal. Feeds the proposal builder and the (Phase-3) negotiation-strategy agent.
**Source:** Aniket's **Negotiation Planner** (`negotiation_planner.html`, Jun 2026) — negotiation IP carried from his Salesforce CPQ days, formalised into a structured planner. Connects to `deal-pricing-system/knowledge_base/templates/negotiation_best_practices.md` and `ai_pricing_playbook.md`, and to a wealth/PB reference deal's "travel" anchoring artefact.
**Maintainer note:** Treat this as a *living* library — **always watch for more negotiation / commercial-strategy intel** (from Aniket, Anton, live deals) and fold it in here.

---

## 1. The one rule — concessions must SHRINK (the Martini)

The *shape* of your concessions across rounds **is a message**. The buyer reads it. Five patterns, ranked:

| Pattern | Rank | Shape (cumulative across 4 rounds) | What it signals |
|---|---|---|---|
| **Martini** | ✅ Best | `0 → 0.60 → 0.90 → 1.0` (strong anchor, then shrinking) | "I'm serious about my first offer, but can concede some." |
| **Ice Cream** | Good | `0.50 → 0.80 → 0.95 → 1.0` (concede at open, largest first, shrinking) | "I'm willing to negotiate, but approaching my floor." |
| **Avalanche** | ❌ Bad | `0.05 → 0.20 → 0.50 → 1.0` (bigger each round) | "If you keep pushing, I'll concede more." — trains the buyer to push. |
| **Wrecking Ball** | ❌ Worst | `0 → 0 → 0 → 1.0` (nothing, then one big drop) | "I'm inflexible / negotiating in bad faith." |
| **Lollipop / Sucker** | ❌ Worst | `1.0 → 1.0 → 1.0 → 1.0` (everything in round 1) | "Take it or leave it." — gives away all leverage instantly. |

**Rule:** make each move **visibly smaller than the last**. Aim for the **Martini**. Never let concessions grow round-on-round.

**Diagnose the counterparty's shape** (and yours) from their offer sequence:
- A *later* offer priced higher than an earlier one → **Inconsistent** → resist.
- Sum ≈ 0 → **No concessions yet** → hold posture.
- All up front → **Lollipop**; nothing-then-one-drop → **Wrecking Ball**; growing each round → **Avalanche** → these are weak/manipulable shapes, respond firmly.
- Shrinking after a real first move → **Martini/Ice Cream** → disciplined counterpart.

---

## 2. The 4-stage concession ladder

| Stage | Posture | Next-best-action | What you ask in return |
|---|---|---|---|
| **1 · Anchor** | Firm. Zero upfront. | Present the **full-scope value case**, state **no discount**, secure agreement in principle as a **reference**. | Set the value baseline; secure willingness to serve as a reference. *(Full scope · 5-yr term · list-anchored value · std renewal cap · reference rights.)* |
| **2 · Counter 1** | **Biggest move, cheap-weighted.** | Make your **largest** concession now, weighted to **cheap** levers (Net 60, sandbox, training), paired to a **signed 5-yr term + reference rights**. | Concede only against a 5-yr term and signed reference rights. |
| **3 · Counter 2** | **Smaller** move, structure + price. | A visibly **smaller** move than Counter 1. Trade the **volume discount only** against **year-one prepay + a written expansion commitment**. | Price only for prepay + written expansion commit. |
| **4 · Best & Final** | **Smallest** move, floor + closer. | Smallest move, **dated and final**. Send the **price-hold addendum to deal desk** (gated). State the **signature deadline once, then stop talking**. | Final & dated. Price-hold addendum needs deal-desk sign-off, not rep authority. |

The ladder *is* a Martini: Anchor (0) → big → smaller → smallest.

---

## 3. The lever families — exhaust 1→4 BEFORE you touch price (5)

Trade in this order. **Never open with price.** Spend the cheap, margin-friendly families first.

| # | Family | Margin cost | Trade rule | Levers |
|---|---|---|---|---|
| 1 | **Solution optionality** | **Zero margin cost** | **Anchor here.** Reframes the deal from a *price* decision to a *configuration* choice. | Good/Better/Best · Bundle/unbundle · Phasing · Scope ramp |
| 2 | **Commitment terms** | Often **margin-accretive** | You *gain* commitment in return for value. Trade these **before any price move**. | 3/5/10-yr term · Volume tier · Year-one prepay · Expansion commit |
| 3 | **Non-price value** | Capacity cost | Cheap in cash, real in delivery hours — **price the bench, don't treat as free**. | Sandbox · Training credits · Premium support/SLA · Program architect · Dedicated CS · Advisory seat |
| 4 | **Timing & cash flow** | Cost of capital only | Eases the buyer's budget, barely touches margin. | Payment terms · Stub bill · Staggered activation · Billing cadence |
| 5 | **Price** | **1:1 margin hit** | **Last resort.** Every point erodes margin **and sets the renewal reference**. | Volume discount · VPA / price hold · Renewal cap |

---

## 4. Lever types — classify every concession before you give it

| Type | Meaning | Examples |
|---|---|---|
| **Cheap** — *give first* | Low margin cost, give early to show movement | Net 60, stub bill, staggered licenses, sandbox + training, swap language, growth tiers, SLA |
| **Costly** — *trade hard* | Real margin cost, only against something | Volume discount, VPA / price hold, discount-to-floor, program architect, dedicated CS |
| **Resist** | Hold the line; gate it | Price-hold addendum (deal-desk gated), flat renewal |
| **Extract** — *what you GET* | Always take something back | Reference rights, case study, press/speaking, expansion commitment |
| **Posture** | Frame, not a giveaway | Full scope, 5-yr term, list-anchored value, signature deadline |

**Golden rule:** every concession is **traded, never gifted** — pair each give with an *extract*.

---

## 5. Read your leverage (switching cost → posture)

| Switching cost | Posture |
|---|---|
| **High** | Anchor firm. The incumbent **lock-in is your leverage**, not a reason to discount. |
| **Medium** | Standard anchor. **Protect price, trade structure.** |
| **Low** | The buyer has real alternatives. **Lead with non-price value, hold the floor tightly.** |

---

## 6. The economics — never cross the floor

Discipline = a **floor gross margin** you do not breach. `maxDiscountToFloor` computes the *maximum* discount before the floor is hit, from: in-scope module list × years-active × (1 − GM) recurring cost, plus services one-time × (1 − GM) less any services credit, plus delivery adds, all grossed up by `1/(1 − floorGM)`. Headroom to that floor sets how much room you actually have.

- **Deal-size bands:** large ≥ **$10M** TCV · mid ≥ **$3M**.
- **Discount headroom bands:** ample ≥ **18%** · moderate ≥ **8%** to the floor. Below moderate → almost no room; lead on value, not price.

---

## 7. Solution optionality — the anchor lever (zero margin cost)

Reframe from "what's your discount?" to "which configuration?". Worked example structure:
- **Good / Better / Best** — Good (Digital Foundation) · Better (Engagement Platform) · **Best = anchor** (Full Engagement + Wealth, dedicated CS, architect, price hold). Anchor on Best.
- **Bundle / unbundle** — full bundle (anchor, simplest to sign) · core + add-ons · à la carte (most flexible, higher unit price).
- **Phasing** — big bang · **two waves (anchor)** · three waves.
- **Scope ramp** — flat · **expanding (anchor)** · pilot-to-platform.

*(Map "Good/Better/Best" tiers onto the current Banking OS 4-solutions where relevant — see `knowledge/product/banking-os.md`.)*

---

## 8. Deploy by scenario (brainstorm aid)

| Scenario | Play |
|---|---|
| Buyer opens with "what's your best price?" | Don't answer price. Anchor on **Solution optionality** (Good/Better/Best); reframe to configuration. |
| Incumbent, high switching cost | Anchor **firm**; lock-in is leverage; trade structure not price. |
| Competitive, low switching cost | Lead **non-price value**; hold floor tightly; smallest viable moves. |
| Buyer keeps pushing each round | You're drifting to **Avalanche** — stop; reset to shrinking moves; make next move smaller + dated. |
| Need to show goodwill early | Give a **cheap** lever (Net 60, sandbox, training) — never price — and **extract** a reference. |
| Approaching the deadline | **Best & Final**: smallest move, dated, signature deadline stated once, price-hold gated to deal desk. |
| Asked for a discount with nothing back | Convert to a **trade** — discount only vs prepay + expansion commit + multi-year term. |

---

## 9. Deal-desk governance (Backbase — CFO framework, June 2026)

**Authoritative.** The enhanced Deal Desk framework (CFO-initiated, Jun 2026) is **cross-functional commercial governance** — Sales + Services + Product, *not* a Finance process; the **Account Team** owns deal success. It is **triggered before pricing is proposed to the client, regardless of the Salesforce stage.** Purpose: protect margins, align Sales/Services/Product, govern custom-dev & roadmap, and make every price/scope/implementation/product commitment with full visibility of its impact on ARR, margins, delivery effort and product strategy. *Decisions: **Approve** (offer shareable, can be conditional / reflect negotiation room) · **Clarify** (update & resubmit) · **Reject** (unhealthy to execute).* Cadence: review every Thursday (90′ max), template submitted COB Tuesday; ad-hoc possible.

**Every deal needs a COMPLETE commercial model:** ARR (recurring) + Professional Services (one-off/implementation) + Managed Services, with **Gross Margin by component** (subscription · managed hosting · managed services · professional services · ecosystems/marketplace). Inputs: **Digital Solutioning Document** (Services pricing source) · **RFF** (Request for Features — product, pre-aligned/validated/locked) · **Deal QA** (delivery-risk review).

**Deal Desk is MANDATORY if any of these "unhealthy" thresholds is breached** (else no Deal Desk needed):

| Metric | Healthy (no DD) | Deal Desk required |
|---|---|---|
| GM ARR | > 83% | **< 83%** |
| Managed Hosting (standalone) GM | > 25% | **< 25%** |
| Managed Services GM | > 45% | **< 45%** |
| Professional Services GM | > 35% | **< 35%** |
| Marketplace GM | > 40% | **< 40%** |
| 1st-year ARR value (ramp-up) | > 60% | **< 60%** |
| ARR ACV | — | **€ +2M** |
| Exceptional pricing metrics (e.g. **AUM**) | — | **applied** |
| ARR discount | within authority (below) | **above authority** |

**Discount approval authority — by region, role & product** (GM-ARR profile is the leading metric):

| Region (price list) | SVP up to | CRO up to | Deal Desk |
|---|---|---|---|
| NAM · NW Europe · Australia (100%) | **≤ 20%** | ≤ 40% | **> 40%** |
| E. Europe · LATAM · Middle East · Africa · Asia (70%) | **≤ 40%** | ≤ 60% | **> 60%** |

> **⚠️ Agentic Banking is EXCLUDED from the discounting framework — always CRO + CEO approval:** Conversational Banking · all APA use cases (outside standard O&O) · Relationship Intelligence · Delivery Factory · Customer Operations · Nexus & other platform components. *(This is why their pricing is TBD, not discountable — see `knowledge/domains/pricing/pricing-methodology.md`.)* Non-cloud deals: CRO (countries without Azure access) / CEO (all other cases).

**Account triangle (every account has 3 leaders):** AE (new + expansion ARR) · CSD (Services-subscription renewal) · RVP Services. ARR commercial ownership sits with the CCO.

**Deploy:** plan within authority; when a move crosses a tier or breaches a GM threshold, the deal goes to Deal Desk — so come with the **complete commercial model + GM-by-component + Digital Solutioning / RFF / Deal-QA summaries** ready. *The proposal builder's job is to produce exactly this pack and flag the tier/threshold before you commit.* *Source: CFO "enhanced Deal Desk framework" email + Deal Desk Process & Template decks (Jun 2026); editions/packaging context from Elevate Rookie Basecamp.*

## 10. Provenance & related

- **Source:** Aniket's Negotiation Planner (Jun 2026). The planner also computes a live offer table, detects the concession shape, and meters discount headroom to floor.
- **Related:** a wealth/PB reference deal's negotiation playbook + "travel" anchoring 1-pager; `deal-pricing-system/knowledge_base/templates/`; the deal-desk codification (`knowledge/learnings/pipeline_gaps/deal_desk_commercial_track.md`); the **proposal builder** (`presentations/gtm-os-proposal-builder/`).
- **A retail fellowship retro** — the real-world sequence of a fellowship commercial — slots alongside this as the *worked example* of these tactics in motion. *(Absorb when accessible.)*
