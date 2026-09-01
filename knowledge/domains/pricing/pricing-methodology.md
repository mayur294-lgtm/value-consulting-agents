# Backbase Pricing Methodology — by Solution & Line of Business

**Status:** CANONICAL for how we price. **Living / partly TBD** — the defined parts are below; the rest evolve per deal as the product and deals mature.
**The one rule:** Backbase is a **Banking OS platform** that sells across **multiple lines of business (LOB)** and **multiple solutions**. **Pricing basis differs by *both* the solution *and* the LOB.** **Do NOT default to the wealth/PB reference deal's wealth AUM pricing across the board** — the wealth/PB reference deal is *one* methodology for *one* LOB of *one* solution.

---

## The map (Solution × LOB → basis → status)

| Solution | LOB / scope | Pricing basis | Metric | Status |
|---|---|---|---|---|
| **Digital Banking** | **Wealth & Private Banking** | AUM bands | Assets under management (£/€ bn) | ✅ **Defined** — the wealth/PB reference deal; wealth/PB Excel |
| **Digital Banking** | **Retail** | Unit / volume | Customers · accounts · **net assets** | ✅ **Defined** — the retail worked example |
| **Digital Banking** | **SME** | Unit / volume | Users · **onboarding cases** | ✅ **Defined** |
| **Digital Banking** | **Commercial** | Unit / volume | Users · **case managers** · entities | ✅ **Defined** |
| **Conversational Banking** | cross-LOB | Platform + LOB + per-interaction + compute | Platform fee + €/domain + €/interaction + LLM pass-through | ✅ **Defined** — banking-os.md §10 |
| **Relationship Intelligence** | cross-LOB | — | — | 🕓 **TBD** |
| **Customer Operations** (Resolution Loops / generic process automation) | cross-LOB | — | per-resolution? per-case? per-outcome? | 🕓 **TBD** |
| **Agentic / AI** ("how do you charge for AI" · CLO · process automation) | cross-LOB | — | per-agent? per-outcome? per-interaction? | 🕓 **TBD** — prior experiments: the wealth/PB reference deal, **a prior AI-pricing experiment**, others (to absorb) |

> **Scope note:** everything in the **Digital Banking** rows (wealth AUM + retail/SME/commercial unit-based) is **Digital Banking only** — including banking assist / employee workspaces. The other solutions price **separately**.

---

## 1. Digital Banking — the defined space today

- **Wealth & PB → AUM-banded.** Baseline fee scaled by AUM bands, with smoothing on the open top band, and **options per deal** (e.g. the wealth/PB reference deal's A/B/C scenarios). Pricing engine basis: **`band_multiplier`**. Source of truth: the wealth/PB pricing Excel + the wealth/PB reference deal.
- **Retail / SME / Commercial → unit / volume.** A flat platform fee + a per-unit charge that steps down by volume tier. The **metric varies by LOB**: retail tends to **customers / accounts / net assets**; SME leans on **onboarding cases / users**; commercial on **case managers / users / entities**. Pricing engine basis: **`tiered_per_unit`**. Source: **the retail worked example**; Aniket's planner uses non-wealth (Good/Better/Best TCV) for exactly these LOBs.

> **Validated by a real CPQ export (the wealth/PB reference deal):** each product is quoted as a **Base Fee + a usage Fee** (AUM Fee with qty "AUM in Million", or a unit fee — Case Manager = "Number of Case Managers", Onboarding = "Assets Size in Billions"); 3rd-party connectors (Grand Central, Jumio, Twilio, Comply Advantage, Docusign) sit in a **separate pass-through subtotal**. Packaging is three editions — **Essential / Premium / Signature** (Premium ≈ 100% baseline · Essential ≈ 70–80% · Signature ≈ 130–180%) with **localized geo pricing** (Tier-1 100% / others ~70%) — the editions are the Good/Better/Best lever. Cloud-default, **€600K min deal**. Order form (Spotdraft) defines the legal metrics: *Total Assets*, *Total Loan Product Book*, *User*, with overage above committed **caps**. Discount governance: [[negotiation-tactics]] §9.

## 2. Conversational Banking — defined

Platform fee (Entry/Critical/Enterprise) **+** LOB fee (€/domain, one included, waived on Enterprise) **+** per-interaction (volume-tiered, monthly) **+** LLM compute as a transparent pass-through at cost. Pricing engine basis: **`conversational`**. Source: `knowledge/product/banking-os.md` §10.

## 3–5. Relationship Intelligence · Customer Operations · Agentic / AI — TBD

Not yet a single defined basis. Candidate shapes (to firm up per deal): per-Play / per-outcome (Relationship Intelligence), per-resolution / per-case / per-outcome (Customer Operations & process automation), per-agent / per-interaction / per-outcome (Agentic AI). **"How do you charge for AI?"** is an open, deal-led question — we have **prior experience from the wealth/PB reference deal and a prior AI-pricing experiment** to mine when it becomes a key deal characteristic. **Depict as TBD; future-proof now, define at the deal.**

---

## How this maps to the pricing engine (`tools/pricing_model.py`)

| Basis | Use for |
|---|---|
| `band_multiplier` | Digital Banking — **Wealth / PB** (AUM) |
| `tiered_per_unit` | Digital Banking — **Retail / SME / Commercial** (net assets · case managers · onboarding cases · users) |
| `conversational` | **Conversational Banking** (platform + LOB + per-interaction + compute) |
| *(new bases TBD)* | Relationship Intelligence · Customer Operations · Agentic AI — add as the methodology firms up |

## Evolution principle

Pricing **evolves as the product evolves and as deals demand it.** Where a basis is undefined, mark it **TBD explicitly** (here and in any deliverable) and resolve it **at the deal**, not pre-emptively. Build the tooling so a new basis slots in without rework.

## Provenance & related

`knowledge/product/banking-os.md` (the 4 solutions) · `tools/pricing_model.py` (the engine) · the wealth/PB reference deal (wealth AUM) · the retail worked example (retail unit-based) · a prior AI-pricing experiment (AI pricing — to absorb) · Aniket's planner & [[negotiation-tactics]] · the proposal builder (`presentations/gtm-os-proposal-builder/`).
