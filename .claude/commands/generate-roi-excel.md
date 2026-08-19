# Generate ROI Excel Model

Generate a professional ROI Excel model following the Backbase Value Consulting methodology (HNB/Seabank format).

## What This Skill Does

Creates a comprehensive Excel ROI model with:
- Multiple sheets (Cover, Instructions, Dashboard, Inputs, Cashflows, Servicing, Scenarios, Assumptions)
- Scenario-based modeling (Conservative, Moderate, Aggressive)
- Implementation & Effectiveness curves by year
- Lever-by-lever benefit breakdown
- Servicing task analysis with Backbase impact
- All assumptions documented with sources
- **Tech Rationalization tab** (when CIO/CFO are primary stakeholders)

## Usage

```
/generate-roi-excel
```

Then provide:
1. Client name
2. Evidence register or discovery findings
3. Key financial data (customer base, revenue, costs)
4. Specific levers to model

## Example

```
/generate-roi-excel

Client: First National Bank
Region: SEA
Currency: USD

Evidence:
- E1: 13,000 wealth customers
- E2: 250 annual onboardings
- E3: RMs spend 2 hours/day on admin
- E4: Onboarding takes 5+ days
- E5: 40 RMs serving 300 clients each

Levers to model:
- Prospecting improvement
- Digital onboarding
- Servicing efficiency
```

## Output

An Excel file will be generated at the specified path with:
- Working formulas
- Editable input cells (highlighted in blue)
- Calculated outputs
- Charts and visualizations
- Complete assumptions register

## Template Location

The generator script is at: `tools/roi_excel_generator.py`

## Instructions

When this skill is invoked:

1. **Gather Required Inputs:**
   - Client name and basic info
   - Evidence register (if available)
   - Key metrics: customer base, revenue, staff costs
   - Levers to include in the model

2. **Prepare Configuration:**
   - Structure the data into the required JSON format
   - Calculate baseline values for each lever
   - Define three scenarios with different impact assumptions
   - Document all assumptions with sources

3. **Run the Reasonableness Gate (MANDATORY — before generating):**
   - An uncapped `roi_config.json` must never reach Excel, regardless of whether it came from `/build-roi`, the full pipeline, or a config assembled by hand for this skill.
   - Run via Bash, on whatever JSON config file backs this run (write the config to disk first if it was only assembled in-memory):
     ```
     python3 scripts/artifact_boundary.py cap <path-to-roi_config.json>
     ```
   - The gate is idempotent — if `/build-roi` (or the pipeline) already ran it, this is a no-op; running it twice never double-caps.
   - Report a one-line gate summary to the consultant before generating, e.g. *"Gate: backbase_impact capped 0.72 → 0.60 on L3_retention"* or *"Gate: no changes — within bounds."* If the gate reports any other warnings (e.g. curve-adjusted ROI outside the segment benchmark range), surface those too.
   - Re-read the (possibly now-capped) config from disk before proceeding to step 4 — generate from the gated file, not from a pre-gate in-memory copy.

4. **Generate the Model:**
   - Use the ROIModelGenerator class from tools/roi_excel_generator.py
   - Save to the outputs folder with client name in filename

5. **Validate Output:**
   - Open the Excel file and verify formulas work
   - Check that scenarios produce different results
   - Ensure all assumptions are documented

## Configuration Schema

> **Note:** The authoritative schema is defined in `.claude/agents/roi-financial-modeler.md` ("Output: roi_config.json Schema"). The sketch below shows the overall shape; see that agent file for the full, current contract — including the fact that `value_lever_groups` (NOT `levers`) is a **dict of dicts keyed by lever ID**, with `revenue_drivers`/`cost_drivers` as dicts keyed by driver ID (not arrays).

```json
{
  "client_name": "Bank Name",
  "date": "2026-01-15",
  "currency": "USD",
  "analysis_years": 5,
  "discount_rate": 0.12,
  "selected_scenario": "Moderate",
  "primary_stakeholder_types": ["business", "technology", "finance"],
  "sources": [
    {"ref": "Business Case Questionnaire", "detail": "Client-confirmed FTE, revenue, cost-to-income ratio", "file": "[CLIENT]_Business_Case_Questionnaire_FILLED.xlsx"},
    {"ref": "Consulting Playbook Benchmarks", "detail": "Comparable-bank Backbase impact", "file": "knowledge/Consulting Playbook Metrics Benchmark [Master] - Benchmarks.csv"}
  ],
  "basic_information": {
    "annual_revenue": 500000000,
    "cost_to_income_ratio": 0.55,
    "operating_costs": 275000000,
    "operating_costs_source": "Derived: Annual Revenue × Cost-to-Income Ratio",
    "operating_costs_confidence": "MEDIUM",
    "total_fte": 1200,
    "total_fte_confidence": "HIGH",
    "total_fte_source": "Client follow-up — CLIENT-CONFIRMED"
  },
  "scenarios": {
    "conservative": {
      "implementation_curve": [0.1, 0.6, 0.8, 0.9, 1.0],
      "effectiveness_curve": [0.1, 0.25, 0.45, 0.7, 0.85]
    },
    "moderate": {...},
    "aggressive": {...}
  },
  "investment": {
    "license": [yearly_amounts],
    "implementation": [yearly_amounts]
  },
  "value_lever_groups": {
    "L1_prospecting": {
      "group_name": "Prospecting - Prospect Lounge",
      "revenue_drivers": {
        "conversion_uplift": {
          "name": "...",
          "baseline_formula": "{eligible_customers} * {conversion_rate}",
          "baseline_annual": 500000,
          "inputs": {
            "eligible_customers": {"value": 14000, "unit": "customers", "source": "...", "confidence": "HIGH"},
            "conversion_rate": {"value": 0.12, "unit": "ratio", "source": "...", "confidence": "MEDIUM", "formula": "{leads} / {visits}", "fmt": "0.0%"}
          }
        }
      },
      "cost_drivers": {},
      "servicing_analysis": null
    }
  },
  "assumptions_register": [
    {
      "name": "Discount Rate (WACC)",
      "value": 0.12,
      "unit": "ratio",
      "source": "Industry standard",
      "owner": "CFO"
    }
  ]
}
```

### Provenance keys (REQUIRED)

The generator renders provenance when present in the config:
- **`sources`** (top-level array) — one entry per real artifact behind the inputs, each `{ref, detail, file}`. Rendered as a "Sources" sheet.
- **Per-`basic_information`-field provenance** — for every field `X`, companion keys `X_source` (string) and `X_confidence` (`HIGH` | `MEDIUM` | `LOW` | `ASSUMPTION`). The generator excludes these companion keys from rendered rows and uses `X_confidence` for the confidence column (falling back to a keyword heuristic only when absent).
- **`operating_costs` as derived** — when `annual_revenue`, `cost_to_income_ratio`, and `operating_costs` are all present in `basic_information`, the generator renders `operating_costs` as a live Excel formula `=revenue*cost_to_income` instead of a static number. Document it with `operating_costs_source: "Derived: Annual Revenue × Cost-to-Income Ratio"`.
- **Driver-input `formula`/`fmt`** — any input under a driver's `inputs` dict may optionally include a `formula` (template string with `{token}` names matching sibling input keys) and `fmt` (Excel number-format override) to render that input as a live formula.

See `.claude/agents/roi-financial-modeler.md` for the full authoritative schema and worked examples.

---

## Tech Rationalization Tab (CIO/CFO Stakeholders)

**When to Include:** If `primary_stakeholder_types` includes `technology` or `finance`, add a **Tech Rationalization** sheet.

**Reference Data:** `knowledge/learnings/roi_models/tech_rationalization_decommission.md`

> **Synthetic-data exclusion:** exclude any `[Synthetic-Test]`-tagged entry and anything sourced from a `tests/` path (see `knowledge/standards/benchmark_evolution.md`). If ≥1 entry was excluded, append that standard's canonical excluded-count note; if nothing was excluded, add no note.

### Tech Rationalization Sheet Structure

| Section | Content |
|---------|---------|
| **Legacy Cost Stack** | Annual costs by category (core banking, originations, bill pay, P2P, middleware, etc.) |
| **Marketplace Costs** | Per-transaction costs for onboarding services (KYC, identity verification, etc.) |
| **Per-User Costs** | Monthly per-user costs for digital banking services |
| **Growth Projections** | Year-over-year user growth with legacy cost escalation |
| **Backbase TCO** | License + implementation + marketplace + ongoing costs |
| **5-Year Comparison** | Side-by-side NPV: Legacy vs. Backbase |
| **Savings Summary** | Annual savings, cumulative savings, NPV impact |

### Tech Rationalization Configuration Schema

```json
{
  "tech_rationalization": {
    "include": true,
    "legacy_platform": {
      "name": "Lumin Digital",
      "annual_costs": [
        {"category": "Retail Banking", "cost": 2050000},
        {"category": "SME Banking", "cost": 148000},
        {"category": "Bill Pay", "cost": 560000},
        {"category": "P2P/Zelle", "cost": 672000},
        {"category": "Middleware/iPaaS", "cost": 400000},
        {"category": "PFM", "cost": 277000}
      ],
      "total_annual": 6650000,
      "growth_rate": 0.15
    },
    "marketplace_costs": [
      {"service": "AML Screening", "provider": "Comply Advantage", "per_transaction": 0.35},
      {"service": "Identity Verification", "provider": "Jumio", "per_transaction": 1.25},
      {"service": "Business ID Verification", "provider": "Middesk", "per_transaction": 6.00}
    ],
    "per_user_monthly": [
      {"service": "Bill Pay", "cost": 0.27},
      {"service": "P2P/Zelle", "cost": 0.33},
      {"service": "Fraud Management", "cost": 0.23}
    ],
    "decommission_timeline": {
      "parallel_run_months": 6,
      "termination_penalty_percent": 0.5,
      "data_migration_percent": 0.05
    },
    "backbase_tco": {
      "license": [yearly_amounts],
      "implementation": [yearly_amounts],
      "marketplace": [yearly_amounts],
      "total_5yr": 25000000
    },
    "savings": {
      "annual_at_baseline": 2350000,
      "annual_year_4": 7600000,
      "total_5yr_npv": 21000000
    }
  }
}
```

### Example Tech Rationalization Output

When CIO/CFO are stakeholders and tech rationalization data is available:

**Dashboard Summary (additional row):**
| Value Lever | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | Total |
|-------------|--------|--------|--------|--------|--------|-------|
| Tech Rationalization | $0 | $1.2M | $2.4M | $5.8M | $7.6M | $17M |

**Dedicated Tab: "Tech Rationalization"**
- Full legacy cost breakdown
- Backbase TCO breakdown
- Year-by-year comparison chart
- NPV summary with discount rate
- Decommissioning timeline visual
