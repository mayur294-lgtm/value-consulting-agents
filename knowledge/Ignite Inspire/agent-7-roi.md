# ROI BUSINESS CASE — KNOWLEDGE REFERENCE
# ═══════════════════════════════════════════════════════════════════════════════
# Backbase Value Consulting - Value Lever Framework & ROI Methodology
# Version: 2.0 (Reclassified from agent to knowledge reference — Feb 2026)
# ═══════════════════════════════════════════════════════════════════════════════

## PURPOSE OF THIS FILE

This file is a **knowledge reference** — NOT an active agent. It contains:
- Value lever framework and calculation methodology
- Questionnaire structure and customization logic
- ROI calculation examples and adoption curves
- Quality checklists

**Who uses this file:**
- The `/generate-roi-questionnaire` skill reads this for questionnaire structure, value lever categories, and calculation context
- The `roi-business-case-builder` agent references this for value lever framework and calculation methodology
- Consultants reference this for ROI methodology and examples

## Routing

| Phase | Owner | Location |
|-------|-------|----------|
| **Phase A — ROI Questionnaire** | `/generate-roi-questionnaire` skill | `.claude/commands/generate-roi-questionnaire.md` |
| **Phase B — ROI Calculation** | `roi-business-case-builder` agent | `.claude/agents/roi-business-case-builder.md` |

**Workflow:**
1. `/generate-roi-questionnaire` skill generates a pre-populated questionnaire using upstream agent data
2. The consultant sends it to the client for data collection
3. The filled (or partially filled) questionnaire goes to `roi-business-case-builder` as input 7b
4. `roi-business-case-builder` produces the final ROI model, business case, and Excel output

---

---

## PHASE A: QUESTIONNAIRE STRUCTURE (Reference)

> **Note:** Phase A is now executed by the `/generate-roi-questionnaire` skill. This section is retained as reference for the questionnaire structure and customization logic.

### Inputs for Phase A — Full Upstream Wiring

Phase A reads ALL available upstream outputs to pre-populate the questionnaire. The skill is **pipeline-agnostic** — it reads whichever outputs exist, regardless of whether the engagement is Ignite Inspire, Value Assessment, or Hybrid.

**Always read first:**
1. **ENGAGEMENT_CONTEXT.md** (required) — cumulative state from all prior agents
2. **CLIENT_PROFILE.md** (if exists, parent directory) — cross-engagement context for returning clients

**Then scan for upstream agent outputs (read whichever exist):**

| Source | File(s) to Look For | What to Extract for Pre-Population |
|--------|---------------------|-----------------------------------|
| **Inspire Agent 1 — Strategy Workshop** | Workshop deck HTML, ENGAGEMENT_CONTEXT.md updates | Revenue gap hypotheses ($), competitive benchmarks, strategic priorities, pain point financial impact estimates |
| **Inspire Agent 2 — Member/Customer Experience** | Workshop deck HTML, ENGAGEMENT_CONTEXT.md updates | Digital completion rates by journey, abandonment rates, conversion rates, time-to-complete, acquisition cost, NPS, product penetration rates |
| **Inspire Agent 3 — Employee Experience** | Workshop deck HTML, ENGAGEMENT_CONTEXT.md updates | FTE counts by role, blended hourly cost, systems-per-transaction, call center volumes, average handle time, training time, branch transaction volumes, processing times |
| **Inspire Agent 4 — IT Architecture** | Workshop deck HTML, ENGAGEMENT_CONTEXT.md updates | Total system count, license costs, core banking vendor, integration approach, deployment model, phased timeline, application disposition (retire/replace/retain) |
| **Inspire Agent 5 — Use Case Design** | Use case documents, ENGAGEMENT_CONTEXT.md updates | Prioritized use cases (P1/P2/P3), expected adoption %, conversion improvement % per UC, volume impacted, time savings, Backbase modules required |
| **Discovery Agent** | `evidence_register.md`, `pain_points.md`, `metrics.md`, `stakeholder_intelligence.md` | Pain points → value levers, quantified metrics → baseline assumptions, stakeholder priorities |
| **Market Context Researcher** | `market_context_validated.md` | Published financials (annual report), peer comparisons, industry benchmarks → validates client numbers, fills gaps with external data |
| **Journey Builder** | `journey_maps_summary.md`, `journey_maps.json` | Value leakage funnels ($), step volumes, drop-off rates, FTE involvement per step, friction $ impact, before/after metrics |
| **Capability Assessment** | `capability_assessment.md` | Maturity scores (identifies where uplift is strongest), gap analysis, problem map |

**Fallback (if no upstream outputs exist):**
3. **Basic client info** — Client name, Bank or Credit Union, Size (customers, assets), Primary segments (Retail, SME, etc.)

### Pre-Population Rules

When upstream data exists, the questionnaire MUST arrive pre-populated:

| Questionnaire Field | Upstream Source | Pre-Population Behavior |
|--------------------|-----------------|-----------------------|
| Customer/Member count | Agent 1 (strategy), Discovery, CLIENT_PROFILE | Pre-fill → GREEN cell, ask to verify |
| Product penetration rates | Agent 2 (member experience), Discovery | Pre-fill → GREEN cell with source note |
| Digital completion rates | Agent 2 (member experience), Journey Builder | Pre-fill → GREEN cell, cite workshop data |
| Abandonment rates | Agent 2, Journey Builder (friction callouts) | Pre-fill → GREEN cell, cite specific journey |
| Branch FTE count | Agent 3 (employee experience) | Pre-fill → GREEN cell |
| Blended hourly rate | Agent 3 (employee experience) | Pre-fill → GREEN cell |
| Call center volumes | Agent 3 (employee experience) | Pre-fill → GREEN cell |
| Systems inventory | Agent 4 (IT architecture) | Pre-fill → GREEN cell |
| License costs | Agent 4 (IT architecture) | Pre-fill → GREEN cell if disclosed |
| Application disposition | Agent 4 (IT architecture) | Pre-fill IT rationalization section |
| Use case scope | Agent 5 (use cases) | Show/hide questionnaire sheets based on P1/P2/P3 selection |
| Value leakage totals | Journey Builder (waterfall) | Pre-fill → GREEN cell, cite journey map |
| Industry benchmarks | Market Context Researcher | Pre-fill benchmark column alongside client data column |
| Annual report financials | Market Context Researcher | Pre-fill revenue, C/I ratio, asset size |

**Color coding in pre-populated questionnaire:**
- **GREEN** = Pre-filled from upstream agents (verify only — client confirms or corrects)
- **YELLOW** = Required, no upstream data available (client must fill)
- **WHITE** = Optional
- **BLUE** = Pre-filled from industry benchmark (client replaces with actuals if available)

**Source annotation:** Every pre-filled cell MUST include a cell comment noting the source: `"Source: Workshop 2 — Member Experience (Feb 2026)"` or `"Source: Journey Builder — Account Opening friction analysis"` or `"Source: Industry benchmark — NCUA 2024 Q4 data"`

### Questionnaire Customization Logic

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUESTIONNAIRE CUSTOMIZATION RULES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FROM CONTEXT                          QUESTIONNAIRE IMPACT                  │
│  ────────────                          ────────────────────                  │
│                                                                              │
│  Client Type = Credit Union      →     Terminology: "Member"                │
│                                        Pre-fill: CU-specific products       │
│                                                                              │
│  Client Type = Bank              →     Terminology: "Customer"              │
│                                        Include: SME/Corporate sections      │
│                                                                              │
│  Size < 100K customers           →     Simplified questionnaire             │
│                                        Fewer channel breakdown Qs           │
│                                                                              │
│  Size > 1M customers             →     Full questionnaire                   │
│                                        Detailed channel analysis            │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  FROM PRIORITIZED USE CASES            SECTIONS TO INCLUDE                   │
│  ─────────────────────────             ───────────────────                   │
│                                                                              │
│  UC: Account Opening             →     ✓ Acquisition funnel metrics         │
│                                        ✓ Website/app traffic data           │
│                                        ✓ Conversion rates                   │
│                                                                              │
│  UC: Loan Origination            →     ✓ Loan volumes by type               │
│                                        ✓ Processing times                   │
│                                        ✓ Abandonment rates                  │
│                                                                              │
│  UC: Card Management             →     ✓ Card servicing volumes             │
│                                        ✓ Call center card inquiries         │
│                                                                              │
│  UC: Employee Enablement         →     ✓ Full branch data section           │
│                                        ✓ Back office processing             │
│                                        ✓ Employee productivity              │
│                                                                              │
│  UC: Contact Center              →     ✓ Full call center section           │
│                                        ✓ Handle times by journey            │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  FROM IT ARCHITECTURE                  PRE-FILLED DATA                       │
│  ───────────────────                   ───────────────                       │
│                                                                              │
│  Core Banking = Symitar          →     Pre-fill: Core banking field         │
│  Digital Channels known          →     Pre-fill: Channel inventory          │
│  CRM = Salesforce                →     Pre-fill: CRM field                  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  FROM WORKSHOP PAIN POINTS             CUSTOM QUESTIONS ADDED                │
│  ────────────────────────              ─────────────────────                 │
│                                                                              │
│  "Members abandon loans"         →     + Loan abandonment rate Q            │
│  "12 apps per transaction"       →     + App switching time Q               │
│  "No cross-sell visibility"      →     + Product penetration detail Q       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Questionnaire Structure (8 Sheets)

```
QUESTIONNAIRE EXCEL STRUCTURE
=============================

Sheet 1: INSTRUCTIONS
├── Engagement context summary
├── How to fill out the questionnaire
├── Color coding legend
│   ├── Green = Pre-filled (verify only)
│   ├── Yellow = Required (must fill)
│   └── White = Optional
└── Contact for questions

Sheet 2: GENERIC QUESTIONS (~40 questions)
├── Client profile (pre-filled if known)
├── Customer/Member counts by segment
├── Product portfolio and penetration
├── Revenue metrics (income per product)
├── Churn rates
└── Digital vs physical ratios

Sheet 3: DIGITAL USAGE DATA (~50-100 questions)
├── Digital signup and active user rates
├── Digital capability by journey
│   ├── Account Opening
│   ├── Lending
│   ├── Payments
│   ├── Servicing
│   └── Engagement
├── Conversion rates
├── Abandonment rates
└── NPS/satisfaction scores

Sheet 4: BRANCH DATA (~50 questions)
[Include if branch transformation in scope]
├── Branch count and FTE
├── Hourly rates/costs
├── Visit volumes by journey type
├── Transaction volumes
└── Processing times

Sheet 5: CALL CENTER DATA (~50 questions)
[Include if contact center in scope]
├── Center locations and agent count
├── Inbound/outbound volumes
├── Call volumes by journey
├── Handle times
└── Resolution rates

Sheet 6: BACK OFFICE DATA (~50 questions)
[Include if employee enablement in scope]
├── Back office structure
├── Task volumes by type
├── Processing times
├── Error rates
└── Manual vs automated

Sheet 7: IT SYSTEM LANDSCAPE (~30 questions)
├── Core systems inventory
├── Digital channel solutions
├── Integration current state
├── Vendor/version information
└── Deployment model

Sheet 8: IT APPLICATION RATIONALIZATION (~30 questions)
[Include if platform consolidation in scope]
├── TCO by application
├── FTE supporting each
├── Change request volumes
├── Business value assessment
├── Technical fitness scores
```

---

### Phase A Output

**File Name**: `[CLIENT]_Business_Case_Questionnaire.xlsx`
**Generated by:** `/generate-roi-questionnaire` skill

**Characteristics:**
- Pre-filled cells highlighted in GREEN (from upstream agents)
- Required cells highlighted in YELLOW (client must fill)
- Benchmark cells in BLUE (client replaces with actuals)
- Optional cells in WHITE
- Data validation dropdowns where applicable
- Cell comments with source annotations on every pre-filled value
- Instructions tab with context
- Hidden sheets for irrelevant sections

---

## PHASE B: BUSINESS CASE METHODOLOGY (Reference)

> **Note:** Phase B is executed by the `roi-business-case-builder` agent. This section is retained as reference for the value lever framework, calculation methodology, and ROI examples.

### Inputs for Phase B
1. **Completed Questionnaire** (Required)
   - `[CLIENT]_Business_Case_Questionnaire_FILLED.xlsx`

2. **ENGAGEMENT_CONTEXT.md** (Required)
   - All prior agent findings

3. **Backbase Pricing** (Optional)
   - License costs by module
   - Implementation estimates

### Value Lever Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VALUE LEVER FRAMEWORK                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  REVENUE UPLIFT                                                              │
│  ══════════════                                                              │
│                                                                              │
│  1. CUSTOMER ACQUISITION                                                     │
│     ├── Current: [X] applications/year                                      │
│     ├── Conversion improvement: +5% (reduced abandonment)                   │
│     ├── Additional customers: [Calculated]                                  │
│     ├── Revenue per customer: [From questionnaire]                          │
│     └── Annual uplift: $[Calculated]                                        │
│                                                                              │
│  2. LENDING ORIGINATION                                                      │
│     ├── Current loan volume: [X] applications/year                          │
│     ├── Digital conversion improvement: +10%                                │
│     ├── Additional loans: [Calculated]                                      │
│     ├── Average loan income: [From questionnaire]                           │
│     └── Annual uplift: $[Calculated]                                        │
│                                                                              │
│  3. CUSTOMER RETENTION                                                       │
│     ├── Current churn rate: [X]%                                            │
│     ├── Churn reduction: -10% Retail, -50% SME                             │
│     ├── Customers retained: [Calculated]                                    │
│     ├── Lifetime value: [From questionnaire]                                │
│     └── Annual uplift: $[Calculated]                                        │
│                                                                              │
│  4. PRODUCT UPSELL/CROSS-SELL                                               │
│     ├── Current penetration: [X] products/customer                          │
│     ├── Penetration improvement: +5% Retail, +10% SME                       │
│     ├── Additional products: [Calculated]                                   │
│     ├── Revenue per product: [From questionnaire]                           │
│     └── Annual uplift: $[Calculated]                                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  COST AVOIDANCE                                                              │
│  ══════════════                                                              │
│                                                                              │
│  5. BRANCH COST REDUCTION                                                    │
│     ├── Current branch transactions: [X]/year                               │
│     ├── Digital shift: +25% to digital                                      │
│     ├── Transactions shifted: [Calculated]                                  │
│     ├── Cost per branch transaction: [From questionnaire]                   │
│     └── Annual savings: $[Calculated]                                       │
│                                                                              │
│  6. CALL CENTER COST REDUCTION                                               │
│     ├── Current call volume: [X]/year                                       │
│     ├── Digital deflection: -35%                                            │
│     ├── Calls avoided: [Calculated]                                         │
│     ├── Cost per call: [From questionnaire]                                 │
│     └── Annual savings: $[Calculated]                                       │
│                                                                              │
│  7. BACK OFFICE EFFICIENCY                                                   │
│     ├── Current processing volume: [X]/year                                 │
│     ├── Automation improvement: -20%                                        │
│     ├── Processing reduced: [Calculated]                                    │
│     ├── Cost per process: [From questionnaire]                              │
│     └── Annual savings: $[Calculated]                                       │
│                                                                              │
│  8. IT RATIONALIZATION                                                       │
│     ├── Applications retired: [X]                                           │
│     ├── License savings: $[From questionnaire]                              │
│     ├── FTE reallocation: [X] FTEs                                         │
│     └── Annual savings: $[Calculated]                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ROI Calculation Methodology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROI CALCULATION                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INVESTMENT                                                                  │
│  ──────────                                                                  │
│  Backbase Licenses (5-7 years)     = $[X]                                   │
│  Implementation Services           = $[X]                                   │
│  Internal Resources               = $[X]                                    │
│  ─────────────────────────────────────────                                  │
│  TOTAL INVESTMENT                  = $[X]                                   │
│                                                                              │
│  BENEFITS (5-7 Year Projection)                                             │
│  ──────────────────────────────                                             │
│                                                                              │
│  Year 1: [Partial - implementation year]                                    │
│  ├── Revenue uplift:  $[X] × [adoption %]                                  │
│  ├── Cost avoidance:  $[X] × [adoption %]                                  │
│  └── Subtotal:        $[X]                                                 │
│                                                                              │
│  Year 2: [Ramp up]                                                          │
│  ├── Revenue uplift:  $[X] × [adoption %]                                  │
│  ├── Cost avoidance:  $[X] × [adoption %]                                  │
│  └── Subtotal:        $[X]                                                 │
│                                                                              │
│  Year 3-7: [Full adoption]                                                  │
│  └── [Similar structure]                                                    │
│                                                                              │
│  ─────────────────────────────────────────                                  │
│  TOTAL BENEFITS                    = $[X]                                   │
│                                                                              │
│  ROI METRICS                                                                 │
│  ───────────                                                                 │
│  ROI = (Total Benefits - Total Investment) / Total Investment × 100         │
│                                                                              │
│  NPV = Σ [Cash Flow(t) / (1 + WACC)^t]                                     │
│        where WACC = 10% (default, configurable)                             │
│                                                                              │
│  Payback Period = Year when cumulative cash flow becomes positive           │
│                   (discounted to present value)                             │
│                                                                              │
│  IRR = Rate where NPV = 0                                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Adoption Curve Assumptions

```
ADOPTION CURVE (Default)
========================

Implementation Timeline:
├── Phase 1 (Months 1-6):  Digital Banking + Onboarding
├── Phase 2 (Months 7-12): Digital Lending + Assist
└── Phase 3 (Months 13-18): Digital Engage + Optimization

Adoption Percentages:
├── Year 1: 25% (Phase 1 live ~6 months)
├── Year 2: 60% (Phase 2 live, ramping)
├── Year 3: 85% (Phase 3 live, optimizing)
├── Year 4: 95% (Full adoption)
└── Year 5+: 100% (Steady state)

Note: Adjust based on client's change management capacity
```

### Phase B Outputs

**Output 1: Business Case Document**

**File Name**: `[CLIENT]_Business_Case.pdf` or `.pptx`

**Structure:**
```
BUSINESS CASE DOCUMENT STRUCTURE
================================

1. EXECUTIVE SUMMARY (2-3 pages)
   ├── Client Overview
   ├── Engagement Summary
   ├── Key Findings
   ├── Headline Metrics (ROI, NPV, Payback)
   └── Recommendations

2. VALUE LEVERS ANALYSIS (5-8 pages)
   ├── Client Portfolio Overview
   ├── Value Driver Framework
   ├── Scope Definition (in/out)
   └── Assumptions Summary

3. BENEFITS CASE (10-15 pages)
   ├── Customer Acquisition
   │   ├── Current State Analysis
   │   ├── Improvement Opportunity
   │   ├── 5-Year Projection
   │   └── Supporting Charts
   ├── Customer Servicing
   │   ├── Digital Capability Assessment
   │   ├── Channel Shift Opportunity
   │   ├── Cost Avoidance Calculation
   │   └── Supporting Charts
   ├── Customer Retention
   │   ├── Churn Analysis
   │   ├── Retention Improvement
   │   └── Lifetime Value Impact
   └── IT Rationalization
       ├── Application Portfolio Assessment
       ├── Disposition Recommendations
       └── Cost Savings

4. RETURN ON INVESTMENT (5-8 pages)
   ├── Investment Summary
   │   ├── License Costs
   │   └── Implementation Costs
   ├── Benefits Summary
   │   ├── Revenue Uplift Total
   │   └── Cost Avoidance Total
   ├── ROI Calculation
   │   ├── NPV @ 10% WACC
   │   ├── Payback Period
   │   └── IRR
   ├── Cash Flow Projection (Chart)
   └── Sensitivity Analysis

5. IMPLEMENTATION ROADMAP (3-5 pages)
   ├── Phased Approach
   ├── Timeline
   ├── Resource Requirements
   └── Key Milestones

6. RISKS & ASSUMPTIONS (2-3 pages)
   ├── Key Assumptions
   ├── Risks & Mitigations
   └── Sensitivity Factors

APPENDIX
├── Detailed Calculations
├── Data Sources
└── Glossary
```

**Output 2: ROI Model (Excel)**

**File Name**: `[CLIENT]_ROI_Model.xlsx`

**Structure:**
```
ROI MODEL EXCEL STRUCTURE
=========================

Sheet 1: SUMMARY DASHBOARD
├── Key metrics (ROI, NPV, Payback)
├── Investment vs Benefits chart
├── Cash flow chart
└── Value lever breakdown

Sheet 2: ASSUMPTIONS
├── All input parameters
├── Blue text = Hardcoded inputs (from questionnaire)
├── Black text = Calculated
├── WACC (configurable, default 10%)
└── Adoption curve parameters

Sheet 3: REVENUE UPLIFT
├── Customer Acquisition calculations
├── Lending Origination calculations
├── Retention calculations
├── Upsell calculations
└── Subtotals by year

Sheet 4: COST AVOIDANCE
├── Branch cost reduction
├── Call center cost reduction
├── Back office efficiency
├── IT rationalization
└── Subtotals by year

Sheet 5: INVESTMENT
├── Backbase license costs (by module, by year)
├── Implementation costs (by phase)
├── Internal costs
└── Total by year

Sheet 6: CASH FLOW
├── Annual benefits
├── Annual costs
├── Net cash flow
├── Cumulative cash flow
├── Discounted cash flow
└── NPV calculation

Sheet 7: SENSITIVITY
├── WACC sensitivity (+/- 2%)
├── Adoption rate sensitivity
├── Benefit realization sensitivity
└── Tornado chart data

Sheet 8: DATA VALIDATION
├── Error checks (no #REF!, #DIV/0!, etc.)
├── Reasonableness checks
└── Assumption flags
```

**Excel Formatting Standards:**
```
EXCEL FORMATTING RULES
======================

Cell Colors:
├── Blue font = Input (from questionnaire)
├── Black font = Formula/calculated
├── Green fill = Positive variance
├── Red fill = Negative variance
└── Yellow fill = Attention needed

Number Formats:
├── Currency: $#,##0 (no decimals for large numbers)
├── Large currency: $#,##0,,"M" (millions)
├── Percentages: 0.0%
├── Zeros: "-" (not 0)
├── Negatives: (#,##0) in parentheses
└── Years: YYYY

Headers:
├── Include units in headers (e.g., "Revenue ($M)")
├── Freeze panes for navigation
├── Named ranges for key inputs
└── Cell comments for complex formulas

Quality:
├── No formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
├── All cells traceable to source
├── Consistent precision
└── Print areas defined
```

**Output 3: Updated ENGAGEMENT_CONTEXT.md**

Add to context:
- ROI summary (headline metrics)
- Value lever breakdown
- Key assumptions
- Implementation timeline

---

## CALCULATION EXAMPLES

### Customer Acquisition Example

```
CUSTOMER ACQUISITION CALCULATION
================================

Inputs (from questionnaire):
├── Website visitors/year:           1,000,000
├── Account application starts:      50,000 (5% of visitors)
├── Applications completed:          15,000 (30% completion)
├── Accounts opened:                 12,000 (80% approval)
├── Revenue per new account (Y1):    $150

Current Funnel:
├── Visitor → Start:    5.0%
├── Start → Complete:   30.0%
├── Complete → Open:    80.0%
├── End-to-end:         1.2%

With Backbase (assumptions):
├── Visitor → Start:    6.0% (+1pp, better UX)
├── Start → Complete:   55.0% (+25pp, digital completion)
├── Complete → Open:    85.0% (+5pp, faster decisioning)
├── End-to-end:         2.8%

Calculation:
├── Current accounts:    1,000,000 × 1.2% = 12,000
├── Future accounts:     1,000,000 × 2.8% = 28,000
├── Incremental:         28,000 - 12,000 = 16,000
├── Revenue uplift:      16,000 × $150 = $2,400,000/year

Adoption-adjusted (Year 1 @ 25%):
└── Year 1 benefit:      $2,400,000 × 25% = $600,000
```

### Branch Cost Avoidance Example

```
BRANCH COST AVOIDANCE CALCULATION
=================================

Inputs (from questionnaire):
├── Branch locations:                50
├── Total branch FTEs:               400
├── Blended hourly rate:             $45
├── Account inquiries/year:          500,000
├── Avg inquiry handle time:         8 minutes
├── Account opening visits/year:     30,000
├── Avg opening handle time:         45 minutes

Current Cost:
├── Inquiry cost:     500,000 × (8/60) × $45 = $3,000,000
├── Opening cost:     30,000 × (45/60) × $45 = $1,012,500
├── Total:            $4,012,500

With Backbase (assumptions):
├── Digital inquiry shift:   40% (200,000 inquiries avoided)
├── Digital opening shift:   60% (18,000 openings avoided)

Calculation:
├── Inquiry savings:  200,000 × (8/60) × $45 = $1,200,000
├── Opening savings:  18,000 × (45/60) × $45 = $607,500
├── Total savings:    $1,807,500/year

Adoption-adjusted (Year 3 @ 85%):
└── Year 3 benefit:   $1,807,500 × 85% = $1,536,375
```

---

## QUALITY CHECKLIST

### Phase A (Questionnaire):
- [ ] Client name and type correct
- [ ] Terminology matches (Member vs Customer)
- [ ] Known data pre-filled (green)
- [ ] Required fields marked (yellow)
- [ ] Irrelevant sections hidden
- [ ] Instructions clear
- [ ] Data validation in place
- [ ] Custom questions added based on pain points

### Phase B (Business Case):
- [ ] All questionnaire data imported correctly
- [ ] Calculations traceable and correct
- [ ] No Excel formula errors
- [ ] ROI metrics reasonable and defensible
- [ ] Assumptions clearly stated
- [ ] Charts clear and accurate
- [ ] Document professionally formatted
- [ ] Context file updated with summary

---

## ERROR HANDLING

### If questionnaire data is incomplete:
```
"The questionnaire is missing data in these critical areas:
- [List missing fields]

I can proceed with industry benchmarks for these values, but the 
business case will be less accurate. Would you like me to:
1. Proceed with benchmarks (flag as estimates)
2. Wait for the missing data
3. Highlight the sections for client follow-up
```

### If ROI seems unrealistic:
```
"The calculated ROI of [X]% seems [high/low] compared to typical 
Backbase engagements (150-400% range). 

I've identified potential issues:
- [Issue 1]
- [Issue 2]

Would you like me to:
1. Review assumptions for reasonableness
2. Add sensitivity analysis for key variables
3. Proceed with caveats noted
```

---

---

---

## REFERENCE NOTES

1. **Pre-fill everything possible** — the questionnaire should reduce client burden (GREEN > YELLOW)
2. **Defensible numbers** — every calculation must be traceable to evidence or benchmarks
3. **Conservative beats aggressive** — ROI must be believable to CFOs
4. **Excel model is the source of truth** — documents just present it
5. **Assumptions are key** — make them explicit and reasonable
6. **Value lever framework above** — used by both the skill and the agent for consistent methodology

---

*End of ROI Business Case Knowledge Reference*
