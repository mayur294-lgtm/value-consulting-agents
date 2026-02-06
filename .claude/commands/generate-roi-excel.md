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

3. **Generate the Model:**
   - Use the ROIModelGenerator class from tools/roi_excel_generator.py
   - Save to the outputs folder with client name in filename

4. **Validate Output:**
   - Open the Excel file and verify formulas work
   - Check that scenarios produce different results
   - Ensure all assumptions are documented

## Configuration Schema

```json
{
  "client_name": "Bank Name",
  "date": "2026-01-15",
  "currency": "USD",
  "analysis_years": 5,
  "discount_rate": 0.12,
  "selected_scenario": "Moderate",
  "primary_stakeholder_types": ["business", "technology", "finance"],
  "scenarios": {
    "conservative": {
      "implementation_curve": [0.1, 0.6, 0.8, 0.9, 1.0],
      "effectiveness_curve": [0.1, 0.25, 0.45, 0.7, 0.85],
      "levers": {}
    },
    "moderate": {...},
    "aggressive": {...}
  },
  "investment": {
    "license": [yearly_amounts],
    "implementation": [yearly_amounts]
  },
  "levers": [
    {
      "id": "L1",
      "name": "Prospecting - Prospect Lounge",
      "type": "revenue_uplift",
      "values": [year1, year2, year3, year4, year5],
      "inputs": {}
    }
  ],
  "servicing": [
    {
      "task": "Portfolio Review",
      "role": "RM",
      "volume": 15700,
      "time": 0.75,
      "rate": 25,
      "impact": 0.3
    }
  ],
  "assumptions": [
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

---

## Tech Rationalization Tab (CIO/CFO Stakeholders)

**When to Include:** If `primary_stakeholder_types` includes `technology` or `finance`, add a **Tech Rationalization** sheet.

**Reference Data:** `knowledge/learnings/roi_models/tech_rationalization_decommission.md`

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
