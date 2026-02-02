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
