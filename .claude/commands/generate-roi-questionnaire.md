# Generate ROI Questionnaire

Generate a customized Business Case Questionnaire for client data collection. The questionnaire arrives **pre-populated** with everything already known from upstream agents — transforming it from a blank data-collection exercise into a validation exercise.

**This is Phase A of the ROI workflow.** Phase B (calculation) is handled by the `roi-business-case-builder` agent when the filled questionnaire returns.

## When to Invoke

- After upstream agents have run (Inspire workshops, Discovery, Journey Builder, etc.) — the more upstream data, the better the pre-population
- Can run early (even pre-workshop) with minimal context — the questionnaire simply has more YELLOW cells
- Before sending the client a data request
- When the consultant says "prepare the questionnaire" or "what data do I need for the ROI?"

## Input Contract — Full Upstream Wiring

This skill is **pipeline-agnostic** — it reads whichever upstream outputs exist, regardless of whether the engagement is Ignite Inspire, Value Assessment, or Hybrid.

### Always Read First (Required)

| Input | Path | Purpose |
|-------|------|---------|
| **ENGAGEMENT_CONTEXT.md** | Engagement directory root | Cumulative state from all prior agents |
| **CLIENT_PROFILE.md** | Parent directory (if exists) | Cross-engagement context for returning clients |

### Then Scan for Upstream Agent Outputs (Read Whichever Exist)

| Source | File(s) to Look For | What to Extract for Pre-Population |
|--------|---------------------|-----------------------------------|
| **Inspire Agent 1 — Strategy Workshop** | Workshop deck HTML, ENGAGEMENT_CONTEXT.md updates | Revenue gap hypotheses ($), competitive benchmarks, strategic priorities, pain point financial impact estimates |
| **Inspire Agent 2 — Member/Customer Experience** | Workshop deck HTML, ENGAGEMENT_CONTEXT.md updates | Digital completion rates by journey, abandonment rates, conversion rates, time-to-complete, acquisition cost, NPS, product penetration rates |
| **Inspire Agent 3 — Employee Experience** | Workshop deck HTML, ENGAGEMENT_CONTEXT.md updates | FTE counts by role, blended hourly cost, systems-per-transaction, call center volumes, average handle time, training time, branch transaction volumes, processing times |
| **Inspire Agent 4 — IT Architecture** | Workshop deck HTML, ENGAGEMENT_CONTEXT.md updates | Total system count, license costs, core banking vendor, integration approach, deployment model, phased timeline, application disposition (retire/replace/retain) |
| **Inspire Agent 5 — Use Case Design** | Use case documents, ENGAGEMENT_CONTEXT.md updates | Prioritized use cases (P1/P2/P3), expected adoption %, conversion improvement % per UC, volume impacted, time savings, Backbase modules required |
| **Discovery Agent** | `evidence_register.md`, `pain_points.md`, `metrics.md`, `stakeholder_intelligence.md` | Pain points mapped to value levers, quantified metrics for baseline assumptions, stakeholder priorities |
| **Market Context Researcher** | `market_context_validated.md` | Published financials (annual report), peer comparisons, industry benchmarks — validates client numbers, fills gaps with external data |
| **Journey Builder** | `journey_maps_summary.md`, `journey_maps.json` | Value leakage funnels ($), step volumes, drop-off rates, FTE involvement per step, friction $ impact, before/after metrics |
| **Capability Assessment** | `capability_assessment.md` | Maturity scores (identifies where uplift is strongest), gap analysis, problem map |

### Fallback (No Upstream Outputs)

If no upstream outputs exist, the questionnaire is generated from basic client info only:
- Client name, Bank or Credit Union, Size (customers, assets), Primary segments (Retail, SME, etc.)
- All cells will be YELLOW (client must fill everything)

## Pre-Population Rules

When upstream data exists, the questionnaire MUST arrive pre-populated:

| Questionnaire Field | Upstream Source | Pre-Population Behavior |
|--------------------|-----------------|-----------------------|
| Customer/Member count | Agent 1 (strategy), Discovery, CLIENT_PROFILE | Pre-fill in GREEN cell, ask to verify |
| Product penetration rates | Agent 2 (member experience), Discovery | Pre-fill in GREEN cell with source note |
| Digital completion rates | Agent 2 (member experience), Journey Builder | Pre-fill in GREEN cell, cite workshop data |
| Abandonment rates | Agent 2, Journey Builder (friction callouts) | Pre-fill in GREEN cell, cite specific journey |
| Branch FTE count | Agent 3 (employee experience) | Pre-fill in GREEN cell |
| Blended hourly rate | Agent 3 (employee experience) | Pre-fill in GREEN cell |
| Call center volumes | Agent 3 (employee experience) | Pre-fill in GREEN cell |
| Systems inventory | Agent 4 (IT architecture) | Pre-fill in GREEN cell |
| License costs | Agent 4 (IT architecture) | Pre-fill in GREEN cell if disclosed |
| Application disposition | Agent 4 (IT architecture) | Pre-fill IT rationalization section |
| Use case scope | Agent 5 (use cases) | Show/hide questionnaire sheets based on P1/P2/P3 selection |
| Value leakage totals | Journey Builder (waterfall) | Pre-fill in GREEN cell, cite journey map |
| Industry benchmarks | Market Context Researcher | Pre-fill benchmark column alongside client data column |
| Annual report financials | Market Context Researcher | Pre-fill revenue, C/I ratio, asset size |

**Color coding:**
- **GREEN** = Pre-filled from upstream agents (verify only — client confirms or corrects)
- **YELLOW** = Required, no upstream data available (client must fill)
- **WHITE** = Optional
- **BLUE** = Pre-filled from industry benchmark (client replaces with actuals if available)

**Source annotation:** Every pre-filled cell MUST include a cell comment noting the source:
- `"Source: Workshop 2 — Member Experience (Feb 2026)"`
- `"Source: Journey Builder — Account Opening friction analysis"`
- `"Source: Industry benchmark — NCUA 2024 Q4 data"`

## Questionnaire Customization Logic

The questionnaire is tailored based on engagement context:

### From Client Type
| Context | Questionnaire Impact |
|---------|---------------------|
| Client Type = Credit Union | Terminology: "Member"; Pre-fill CU-specific products |
| Client Type = Bank | Terminology: "Customer"; Include SME/Corporate sections |
| Size < 100K customers | Simplified questionnaire; Fewer channel breakdown Qs |
| Size > 1M customers | Full questionnaire; Detailed channel analysis |

### From Prioritized Use Cases
| Use Case in Scope | Sections to Include |
|-------------------|-------------------|
| Account Opening | Acquisition funnel metrics, Website/app traffic, Conversion rates |
| Loan Origination | Loan volumes by type, Processing times, Abandonment rates |
| Card Management | Card servicing volumes, Call center card inquiries |
| Employee Enablement | Full branch data section, Back office processing, Employee productivity |
| Contact Center | Full call center section, Handle times by journey |

### From IT Architecture
| Context | Pre-Filled Data |
|---------|----------------|
| Core Banking = Symitar | Pre-fill: Core banking field |
| Digital Channels known | Pre-fill: Channel inventory |
| CRM = Salesforce | Pre-fill: CRM field |

### From Workshop Pain Points
| Pain Point Identified | Custom Question Added |
|----------------------|---------------------|
| "Members abandon loans" | + Loan abandonment rate Q |
| "12 apps per transaction" | + App switching time Q |
| "No cross-sell visibility" | + Product penetration detail Q |

## Questionnaire Structure (8 Sheets)

```
Sheet 1: INSTRUCTIONS
├── Engagement context summary
├── How to fill out the questionnaire
├── Color coding legend (Green/Yellow/White/Blue)
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
└── Technical fitness scores
```

## Consultant Checkpoint — Questionnaire Structure Review (MANDATORY)

**STOP before generating the questionnaire. Present your plan to the consultant.**

Present:
1. **Questionnaire Scope** — Which of the 8 sheets will be included vs. hidden, based on engagement context
2. **Pre-Filled Data Summary** — How many cells are GREEN (pre-filled) vs. YELLOW (client must fill) vs. BLUE (benchmark)
3. **Custom Questions** — Additional questions derived from workshop pain points
4. **Use Case Coverage** — Which value levers are in scope based on prioritized use cases
5. **Data Gaps** — Any missing context that would affect questionnaire quality

Say: *"Please review the questionnaire structure before I generate it. Are the sections, pre-filled data, and custom questions correct for this engagement?"*

**After presenting this checkpoint, STOP and wait for the consultant's response. Do NOT generate the questionnaire until the consultant explicitly approves.**

## Output

**File Name:** `[CLIENT]_Business_Case_Questionnaire.xlsx`

**Characteristics:**
- Pre-filled cells highlighted in GREEN
- Required cells highlighted in YELLOW
- Optional cells in WHITE
- Benchmark cells in BLUE
- Data validation dropdowns where applicable
- Cell comments with guidance and source annotations on every pre-filled value
- Instructions tab with engagement context
- Hidden sheets for irrelevant sections (based on use case scope)

## Handoff to Phase B

After the client fills (or partially fills) the questionnaire:
1. The filled questionnaire (`[CLIENT]_Business_Case_Questionnaire_FILLED.xlsx`) becomes **input 7b** to the `roi-business-case-builder` agent
2. The `roi-business-case-builder` combines questionnaire data with evidence register, market context, and benchmarks to produce the final ROI model
3. If the questionnaire comes back partially filled, `roi-business-case-builder` falls back to benchmarks for missing fields with appropriate confidence downgrades

## Knowledge Reference

For value lever framework, calculation methodology, adoption curves, and ROI examples that inform questionnaire design, see:
- `knowledge/Ignite Inspire/agent-7-roi.md` — Value lever framework, calculation examples, adoption curves
- `knowledge/domains/{domain}/roi_levers.md` — Domain-specific value levers
- `knowledge/domains/{domain}/benchmarks.md` — Domain-specific benchmarks

## Quality Checklist

Before delivering the questionnaire:
- [ ] Client name and type correct
- [ ] Terminology matches (Member vs Customer)
- [ ] All available upstream data pre-filled (GREEN cells)
- [ ] Required unfilled fields marked (YELLOW cells)
- [ ] Benchmark reference values included (BLUE cells)
- [ ] Irrelevant sections hidden based on use case scope
- [ ] Instructions tab clear and complete
- [ ] Data validation dropdowns in place
- [ ] Every pre-filled cell has a source annotation comment
- [ ] Custom questions added based on identified pain points
- [ ] Consultant checkpoint completed and approved

## Step-by-Step Generation Process

1. **Read ENGAGEMENT_CONTEXT.md** — understand the engagement type, client, and scope
2. **Read CLIENT_PROFILE.md** (if exists) — cross-engagement context
3. **Scan for all upstream outputs** — read whichever files exist from the upstream wiring table above
4. **Determine questionnaire scope** — which sheets to include/hide based on use case priorities
5. **Map upstream data to questionnaire fields** — apply pre-population rules table
6. **Identify custom questions** — from pain points and gaps identified in upstream outputs
7. **Present checkpoint to consultant** — scope, pre-fill summary, custom questions, gaps
8. **Wait for consultant approval** — do NOT proceed without it
9. **Generate the Excel questionnaire** — with all pre-fills, color coding, source annotations, and hidden sheets
10. **Save to engagement outputs directory** — `outputs/[CLIENT]_Business_Case_Questionnaire.xlsx`

## Remember

1. **Pre-fill everything possible** — the goal is to reduce client burden; a mostly-GREEN questionnaire gets filled faster
2. **Source annotations are mandatory** — every GREEN cell needs a comment explaining where the data came from
3. **Hidden sheets reduce overwhelm** — if a use case isn't in scope, hide the sheet entirely
4. **This feeds Phase B** — the questionnaire structure must align with what `roi-business-case-builder` expects as input 7b
5. **Pipeline-agnostic** — works identically whether upstream came from Inspire workshops or Value Assessment agents
