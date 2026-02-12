# Benchmark Evolution Model

## Purpose

Benchmarks are living data. They improve with every engagement. This standard defines how benchmarks enter the system, gain confidence, and evolve — ensuring that new domains (like investing) start useful and get better, and mature domains (like retail) never regress.

---

## Confidence Tiers

Every benchmark value carries a confidence tier. The tier determines how the value can be used in ROI models and reports.

| Tier | Label | Meaning | Use in ROI | Display |
|------|-------|---------|-----------|---------|
| **1** | `[Industry]` | Published by a reputable source (analyst firm, regulator, industry body). Sample size >50, recency <3 years. | Direct use. Full weight in calculations. | "Industry benchmark: [value] ([source], [year])" |
| **2** | `[Proxy]` | From an adjacent domain, region, or time period. Reasonable but not exact. | Use with 20% conservative haircut. Flag in assumptions. | "Proxy benchmark: [value] (adjusted from [original context])" |
| **3** | `[Estimated]` | Derived from logic, analogies, or expert judgment. No direct empirical source. | Use as directional only. Wide confidence interval (±30-50%). | "Estimated: [range] (basis: [reasoning])" |
| **4** | `[Client-Validated]` | Confirmed by actual client data during an engagement. The gold standard. | Direct use. Highest confidence. | "Client-validated: [value] ([anonymized engagement ref])" |

---

## Evolution Rules

### Rule 1: Benchmarks are append-only

Never delete or overwrite a benchmark value. New data is appended alongside existing values. The system accumulates evidence over time.

**Why:** A benchmark from 2024 and a benchmark from 2026 are both useful — they show trend direction. Overwriting destroys the trend.

### Rule 2: Tiers promote, never demote

A benchmark can only move UP the confidence ladder:
- `[Estimated]` → `[Proxy]` (when a related industry source is found)
- `[Proxy]` → `[Industry]` (when a direct source is published)
- Any tier → `[Client-Validated]` (when a real engagement confirms it)

A `[Client-Validated]` value can NEVER be demoted by a later `[Estimated]` or `[Proxy]` value. If new data conflicts with validated data, both are kept — the conflict is flagged for investigation.

### Rule 3: Field observations accumulate

When consultants adjust a benchmark during an engagement (because the default doesn't fit their client), this is recorded as a "field observation":

```
## Field Observations for [Benchmark Name]
| Date | Domain | Region | Published Value | Adjusted Value | Reason | Engagement Ref |
|------|--------|--------|-----------------|----------------|--------|----------------|
```

After 3+ consistent corrections in the same direction:
- The published range is widened to include the field-observed range
- The original value is preserved
- A note is added: "Field observations from N engagements suggest [range] for [context]"

### Rule 4: Regional patterns emerge from data

Do NOT create regional templates ("APAC benchmarks are X"). Instead, let regional patterns emerge from accumulated field observations. When 3+ engagements in a region show consistent adjustment, note it as a pattern — but keep it descriptive, not prescriptive.

### Rule 5: New domains start with [Estimated] and [Proxy]

When bootstrapping a new domain (e.g., investing):
1. Start with `[Industry]` benchmarks where published data exists (Schwab, Fidelity, Robinhood public data)
2. Use `[Proxy]` for benchmarks borrowed from adjacent domains (retail banking onboarding → investment account opening)
3. Use `[Estimated]` for values derived from logic or expert judgment
4. Mark everything clearly and wait for engagement data to promote to `[Client-Validated]`

---

## Benchmark Lifecycle for New Domains

```
Day 0: Domain bootstrapped
  → [Industry]: Public data from industry leaders, regulators, analysts
  → [Proxy]: Adjacent domain benchmarks with documented adjustment rationale
  → [Estimated]: Expert judgment with explicit reasoning and wide ranges

First engagement:
  → Some [Estimated] → [Client-Validated] (actual client data confirms or refutes)
  → Some [Proxy] → [Client-Validated] (proxy proves accurate in practice)
  → New field observations recorded for values that needed adjustment

3+ engagements:
  → Field observation patterns emerge (regional, size-tier, model-type)
  → Benchmark ranges tighten based on accumulated data
  → New [Industry] sources found and added (analysts publish domain research)

10+ engagements:
  → Domain benchmarks approach maturity similar to established domains
  → Most critical values are [Client-Validated] or [Industry]
  → Regional patterns are well-documented
```

---

## How Agents Use This Model

### Discovery Agent
- Extracts actual metric values from transcripts → becomes raw material for `[Client-Validated]` benchmarks

### Benchmark Librarian
- Selects benchmarks respecting confidence tiers
- Surfaces field observations alongside published values
- Applies 20% haircut to `[Proxy]` values automatically

### ROI Agent
- Uses tier to determine confidence level in calculations
- `[Estimated]` benchmarks trigger wider sensitivity analysis (±30-50%)
- `[Client-Validated]` benchmarks allow tighter sensitivity ranges (±10-20%)

### Knowledge Harvest (Orchestrator Step 9)
- After every engagement, extracts validated metrics
- Promotes benchmarks from `[Estimated]` → `[Client-Validated]` when confirmed
- Records field observations for values that were adjusted

---

## Domain Benchmark Maturity Rating

Each domain carries a data maturity rating that signals overall benchmark reliability:

| Rating | Criteria | Domains |
|--------|----------|---------|
| **Mature** | >80% of critical benchmarks are `[Industry]` or `[Client-Validated]` | Retail |
| **Developing** | 40-80% of critical benchmarks have empirical backing | SME, Wealth |
| **Emerging** | <40% of critical benchmarks have empirical backing | Investing, Commercial, Corporate |

The maturity rating is displayed in domain `_index.md` files and surfaced by the Orchestrator when setting benchmark confidence mode.

---

*Last Updated: 2026-02-09*
*Status: Active standard — applies to all domains*
