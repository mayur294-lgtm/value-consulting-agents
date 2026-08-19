# Pricing Model — usage-based commercial pricing engine

Build a defensible, multi-scenario **commercial pricing model** for a usage-based deal
(AUM / seats / volume / tier). This is the **price** side of the table — what Backbase
charges and how it scales with the client's growth. It is the complement to
`/generate-roi-excel` (which models the client's *benefit*), not a replacement.

Backed by `tools/pricing_model.py` (regression-tested against real deal-desk maths).

## What This Skill Does

Given a baseline fee schedule and a band/uplift structure, produces:
- **Scenario projection** — 5-yr fee at every growth milestone, per scenario, side by side
- **Crossover analysis** — the growth point where one scenario overtakes another (and where it sits vs the client's ambition)
- **Margin head-to-head** — for two structures hitting a similar headline, which yields more to Backbase across the realistic growth range
- **POF / BAFO split** — apply uplift to **software only**, hold 3rd-party (pass-through) fees **flat**, and **back-solve a proportional discount** so the grand total hits a target
- A multi-tab `.xlsx` (Scenarios · Crossovers · Margin H2H · POF Split · Assumptions)

## When to Use

- Structuring or re-structuring a commercial offer with usage-based pricing
- Any negotiation what-if: "drop the baseline but raise the top band", "where does B beat A", "re-price to £X total", "split software from 3rd-party for the POF"
- Feeding a negotiation deck (the scenario table + crossover come straight from here)

## Usage

```
/pricing-model
```

**Checkpoint 1 (pre-build):** confirm the inputs with the consultant before modelling —
- Baseline fee + the growth point it's quoted at (e.g. £14.19M at £80bn)
- Band schedule (thresholds + uplift % per band; note any *smoothed* top band)
- The scenarios to compare (each = a baseline + band overrides)
- For a POF: the per-year software fees, the per-year 3rd-party fees (held flat), the uplift rate, and the target total

Then write a config JSON (schema below) to the engagement's `outputs/` directory, and run:
```
python3 tools/pricing_model.py --config engagements/<client>/<engagement>/outputs/<model>.json --out engagements/<client>/<engagement>/outputs/<ClientName>_pricing_model.xlsx
python3 tools/pricing_model.py --config engagements/<client>/<engagement>/outputs/<model>.json --crossover A,B   # quick crossover
python3 tools/pricing_model.py --selftest                                                                        # sanity: reproduces reference maths
```

**Checkpoint 2 (post-build):** walk the consultant through the projection + crossover + (if used) the solved POF discount before the model is used in any negotiation.

## Pricing bases (works across deal types)

Each scenario declares a `basis`. The engine handles all three — pick per deal, or mix
scenarios within one model. **Pick the basis by solution AND line of business** — pricing
is not one-size (wealth ≠ retail ≠ conversational); see `knowledge/domains/pricing/pricing-methodology.md`
for the Solution × LOB map and the solutions whose basis is still **TBD** (Relationship
Intelligence, Customer Operations, Agentic-AI — define at the deal, don't default to AUM):

**1. `band_multiplier` (default) — WEALTH / AUM** (e.g. the wealth/PB reference deal)
Baseline fee × `(1+rate)` for each band the growth metric crosses, with an open
top band that compounds and can be *smoothed* to a lower rate.

**2. `tiered_per_unit` — RETAIL / BANKING / LENDING** (e.g. customer-, account-,
or loan-priced deals)
Flat platform fee + a per-unit charge that steps down by volume tier. Lower
per-unit rates in higher tiers are the retail analogue of the wealth reducing-uplift
curve. The growth metric is a count (customers / accounts / loans), not a £ amount —
set `metric_prefix:""`, `metric_suffix:" cust"`, and a `display.divisor` to render
the resulting absolute fees in millions.

**3. `conversational` — CONVERSATIONAL BANKING** (the canonical Banking OS deal shape · `knowledge/product/banking-os.md` §10)
Annual fee = **platform fee** (`platform_fee`: Entry €350K · Critical €700K · Enterprise €1.5M) **+ LOB fee** (`lob_fee_per_domain` €350K × billable `domains`, where `lob_included` are bundled and `lob_waived:true` zeroes it on Enterprise) **+ per-interaction** (`interaction_tiers` `[lo,hi,rate]` on **monthly** volume, from €0.07, dropping with volume, annualised ×12). **LLM compute** (`llm_passthrough_annual`) is a transparent pass-through at cost — echoed in Assumptions, **not** added to the Backbase fee. The growth metric `g` is **monthly interactions** (set `metric_suffix:"/mo"`). *"Pay for outcomes, not infrastructure" — activated per domain, not per customer/channel.* Regression-tested in `--selftest`.

The POF software/3rd-party back-solve, crossover, and margin H2H all work identically
across these bases.

## Config schema

```json
// WEALTH / AUM (band_multiplier)
{
  "client": "Example Wealth", "currency": "£", "unit": "bn", "metric": "AUM",
  "scalar_model": {
    "milestones": [85,100,150,200,250,300,350,400,450,500],
    "scenarios": [
      {"name":"A","basis":"band_multiplier","baseline":14.19,"baseline_at":80,
       "bands":[[80,100,0.08],[100,150,0.06],[150,200,0.05]],
       "top_band":{"from":200,"step":50,"rate":0.04}},
      {"name":"B","basis":"band_multiplier","baseline":15.45,"baseline_at":100,
       "bands":[[100,150,0.06],[150,200,0.05]],
       "top_band":{"from":200,"step":50,"rate":0.03}}
    ]
  },
  "pof": {
    "uplift_rate":0.08, "target_total":15000000,
    "software_by_year":[1892820.4,2597663,3007826.5,3007826.5,3007826.5],
    "thirdparty_by_year":[162400,118240,124664,131730,139503],
    "thirdparty_label":"Marketplace (3rd-party pass-through)"
  }
}
```
```json
// RETAIL / BANKING / LENDING (tiered_per_unit)
{
  "client": "Example Bank", "currency": "€", "metric": "customers",
  "metric_prefix": "", "metric_suffix": " cust",
  "display": {"divisor": 1000000, "suffix": "M"},
  "scalar_model": {
    "milestones": [50000,100000,300000,500000,1000000],
    "scenarios": [
      {"name":"Standard","basis":"tiered_per_unit","flat":2000000,
       "tiers":[[0,100000,40],[100000,500000,30],[500000,null,20]]},
      {"name":"Committed","basis":"tiered_per_unit","flat":3000000,
       "tiers":[[0,100000,32],[100000,500000,24],[500000,null,16]]}
    ]
  }
}
```
```json
// CONVERSATIONAL BANKING (conversational) — g = monthly interactions
{
  "client": "Example Bank", "currency": "€", "metric": "interactions",
  "metric_prefix": "", "metric_suffix": "/mo",
  "display": {"divisor": 1000000, "suffix": "M"},
  "scalar_model": {
    "milestones": [250000,500000,1000000,2000000,3000000],
    "scenarios": [
      {"name":"Critical · 3 domains","basis":"conversational",
       "platform_fee":700000,"lob_fee_per_domain":350000,"domains":3,"lob_included":1,"lob_waived":false,
       "interaction_tiers":[[0,500000,0.070],[500000,2000000,0.063],[2000000,null,0.057]],
       "llm_passthrough_annual":300000},
      {"name":"Enterprise · all domains","basis":"conversational",
       "platform_fee":1500000,"lob_fee_per_domain":350000,"domains":4,"lob_included":4,"lob_waived":true,
       "interaction_tiers":[[0,500000,0.070],[500000,2000000,0.063],[2000000,null,0.057]]}
    ]
  }
}
```
- `band_multiplier`: band `[lo,hi,rate]` × `(1+rate)` once growth crosses `lo`; `top_band` compounds `(1+rate)^((g-from)/step)` above `from` (lower rate = smoothing).
- `tiered_per_unit`: `flat` + Σ over `tiers` `[lo,hi,per_unit]` of `(units in tier × per_unit)`; `hi:null` = open-ended.
- `conversational`: `platform_fee` + LOB (`max(0, domains − lob_included) × lob_fee_per_domain`, or 0 if `lob_waived`) + per-interaction (Σ `interaction_tiers` on monthly volume × 12). `llm_passthrough_annual` echoes in Assumptions only.
- `pof` is optional; include only when you need the software/3rd-party POF split (works on any basis).
- Run `python3 tools/pricing_model.py --print-schema` for a complete worked wealth example; `--selftest` regression-tests all three bases.

## Guardrails (conservative-by-default)

- Every number traces to an input or a stated assumption (the Assumptions tab echoes all inputs).
- Show crossovers and downside honestly — no optimistic rounding.
- Never silently change an approved band schedule; scenario overrides are explicit and labelled.
- Pricing is commercially sensitive: outputs are **internal / deal-desk by default**, not client-facing until a consultant promotes them.

## Governance (mandatory — per CLAUDE.md)

- Append a journal entry to `ENGAGEMENT_JOURNAL.md` on completion, with a `<!-- TELEMETRY_START -->` block.
- Dual checkpoint: assumptions confirmed pre-build, model reviewed post-build.
- Harvest only *anonymised methodology* (band shapes, smoothing tactics, crossover framing) to `knowledge/learnings/` — **never** client prices.

## Output

`engagements/<client>/<engagement>/outputs/<ClientName>_pricing_model.xlsx` — Scenarios · Crossovers · Margin H2H · POF Split · Assumptions.
The return summary (baselines, crossovers, totals) feeds the negotiation-deck kit directly.

## Origin

`knowledge/domains/pricing/pricing-methodology.md` ·
`knowledge/domains/negotiation/negotiation-tactics.md`
