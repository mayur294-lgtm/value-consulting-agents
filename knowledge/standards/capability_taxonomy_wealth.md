# Capability Taxonomy — Wealth Management

> **Domain slice** auto-generated from `capability_taxonomy.md`
> Generated: 2026-02-17 09:22
> Master file: `knowledge/standards/capability_taxonomy.md` (2,109 lines)
> This slice: ~Wealth Management capabilities only

---

## Part 1: Maturity Scale Definition

### The 0-4 Scale

| Level | Label | RAG Color | Hex | Observable Criteria |
|-------|-------|-----------|-----|---------------------|
| **0** | **Absent** | Red | `#E63946` | Capability doesn't exist. No process, no tool, no person performing this function. If needed, it either doesn't happen or is completely improvised. |
| **1** | **Fragmented** | Amber-Red | `#F4A261` | Capability exists but is ad-hoc. Person-dependent, inconsistent across channels/branches/teams. Manual workarounds. No standardization. Works sometimes, fails often. |
| **2** | **Defined** | Amber | `#E9C46A` | Standardized process exists. Tooling supports it. Roles are clear. Repeatable and consistent execution. But not end-to-end automated — handoffs are manual, measurement is limited. |
| **3** | **Orchestrated** | Green | `#2A9D8F` | End-to-end orchestrated. Automated where possible. Measured with KPIs. Cross-system integration works. Handoffs are seamless. Continuous improvement based on data. |
| **4** | **Intelligent** | Backbase Blue | `#0066FF` | AI-native. Predictive, self-optimizing. Agentic workflows handle routine cases autonomously. Real-time decisioning. Learning from data. Human-in-the-loop for exceptions only. |

### Scoring Rules

1. **Score what you observe, not what's planned.** A roadmap item is Level 0 until it's live.
2. **The overall score = the weakest layer.** A capability with Level 3 front but Level 0 back is scored Level 0 overall — the chain breaks at the weakest link.
3. **Each layer gets its own score** for the drill-down view, but the headline score reflects end-to-end maturity.
4. **Evidence required.** Every score must reference either a workshop observation, stakeholder quote, or documented assumption.
5. **Conservative bias.** When in doubt, score lower. It's better to underscore and be challenged upward than to overscore and lose credibility.

### How Probing Questions Determine the Level

Each capability has 4-5 probing questions, ordered by maturity level:

- **Q1 (Level 0→1 gate):** "Does this capability exist at all?" If no → Level 0.
- **Q2 (Level 1→2 gate):** "Is the process standardized and repeatable, or does it vary by person/location?" If varies → Level 1.
- **Q3 (Level 2→3 gate):** "Is the process automated end-to-end with measured handoffs and STP?" If manual handoffs remain → Level 2.
- **Q4 (Level 3→4 gate):** "Does AI/ML actively drive decisions, predict outcomes, or handle cases autonomously?" If no AI → Level 3.

---

## Part 2: Front / Middle / Back Layer Definitions

Every capability is assessed across three architectural layers, aligned with the Backbase Three-Plane Architecture:

| Layer | Backbase Plane | What It Covers | Example Components |
|-------|---------------|----------------|-------------------|
| **Front Layer** | Experience Plane | What the customer or employee sees and interacts with | Mobile app, web portal, employee workspace, branch UI, chatbot interface |
| **Middle Layer** | Capability Plane | What orchestrates, decides, and controls | HELIX, business rules, workflow engine, process orchestration, AI/ML models, entitlements |
| **Back Layer** | Integration Plane + Systems of Record | What connects, stores, and processes | Grand Central, core banking connectors, data warehouse, compliance systems, payment rails |

### Layer-Level Scoring

| Layer | Level 0 | Level 1 | Level 2 | Level 3 | Level 4 |
|-------|---------|---------|---------|---------|---------|
| **Front** | No channel exists | Basic UI, poor UX, incomplete | Polished UI, multi-channel, consistent | Omnichannel with context continuity | AI-personalized, adaptive, conversational |
| **Middle** | No process/logic | Manual steps, no orchestration | Defined workflows, basic automation | Fully orchestrated, STP, measured | AI decisioning, agentic execution, predictive |
| **Back** | No system integration | Point-to-point, fragile integrations | Managed connectors, data flows defined | Real-time integration, unified data | Data fabric, ML pipelines, semantic graph |


## Part 3: BIAN Business Areas → Backbase Capability Domains

The BIAN Service Landscape defines ~322 service domains across business areas. We map the ones relevant to Backbase engagements into capability domains using Backbase terminology.

### Domain Structure

| BIAN Business Area | Backbase Capability Domain | Backbase Quadrant | Key Service Domains |
|---|---|---|---|
| Sales & Service | **Customer Channels & Engagement** | Digital Banking | Channel Management, Customer Contact, Servicing Order |
| Customer Management | **Customer Lifecycle Management** | Cross-cutting | Customer Profile, Customer Onboarding, Customer Behavioral Insights |
| Products: Consumer Banking | **Retail Banking Services** | Digital Banking - Retail | Current Account, Savings Account, Card Facility |
| Products: Lending | **Digital Lending & Origination** | Onboarding & Origination | Consumer Loan, Mortgage, Corporate Loan |
| Products: Investment | **Wealth & Investment Services** | Digital Banking / Wealth | Investment Portfolio, Securities Trading, Fund Management |
| Operations & Execution: Payments | **Payments & Transfers** | Digital Banking | Payment Execution, Payment Order, Payment Initiation |
| Operations & Execution: Fulfillment | **Process Orchestration & Fulfillment** | Flow Foundation | Account Origination, Product Fulfillment, Service Delivery |
| Risk & Compliance | **Risk, Compliance & Security** | Platform Identity | Regulatory Compliance, Fraud Detection, KYC/AML, Customer Screening |
| Business Support | **Employee Enablement** | Human Assist / Digital Assist | Case Management, Correspondence, Workspace Management |
| Reference Data | **Data Foundation** | Data Foundations | Product Directory, Party Reference, Location Reference |
| *Beyond BIAN* | **Data & Intelligence** | Intelligence Fabric | Customer 360, Analytics, Predictive Models, Data Governance |
| *Beyond BIAN* | **AI & Agentic** | Agentic AI | Conversational AI, AI Copilots, Agent Orchestration, Compliance-Safe AI |

---

## Part 7: Wealth Management Capability Catalog

*Note: Wealth capabilities follow the same structure as Retail. Key differences are in the lifecycle (Prospect → Onboard → Advise → Service → Grow) and the presence of RM/Advisor workflows.*

### Domain: Customer Channels & Engagement (Wealth)

#### CAP-W-CE-01: Client Digital Portal
*Same structure as retail but focused on investment portfolio visibility, document access, secure messaging with advisor.*

#### CAP-W-CE-02: RM/Advisor Workspace
*Unified workspace for relationship managers with client 360, opportunity management, pipeline visibility, and AI copilot.*

#### CAP-W-CE-03: Referral & Lead Management
*Intake, scoring, prioritization, and routing of referrals from branches and digital channels to advisors.*

### Domain: Customer Lifecycle Management (Wealth)

#### CAP-W-CL-01: Client Onboarding (Wealth)
*KYC-heavy onboarding for investment accounts with suitability assessment, risk profiling, and document collection.*

#### CAP-W-CL-02: Client Segmentation & Tiering
*Categorizing clients by AUM, complexity, and engagement level to match them with the right advisor tier.*

#### CAP-W-CL-03: Client Behavioral Intelligence
*Detecting life events, disengagement signals, held-away assets, and cross-sell opportunities from client behavior patterns.*

### Domain: Wealth & Investment Services

#### CAP-W-WI-01: Portfolio Management & Advisory
*Investment portfolio construction, rebalancing, performance reporting, and advisory services.*

#### CAP-W-WI-02: Financial Planning
*Goal-based planning, retirement projections, scenario modeling, and estate planning tools.*

#### CAP-W-WI-03: Trading & Execution
*Order management, trade execution, settlement, and reconciliation for investment products.*

### Domain: Employee Enablement (Wealth)

#### CAP-W-EE-01: Advisor Productivity & Capacity Management
*Workload balancing, task prioritization, book segmentation, and capacity forecasting for advisors.*

### Domain: Data & Intelligence (Wealth)
*Same structure as retail — CAP-W-DI-01 through CAP-W-DI-02*

### Domain: AI & Agentic (Wealth)
*Same structure as retail — CAP-W-AI-01 through CAP-W-AI-03, plus:*

#### CAP-W-AI-04: Advice Copilot
*AI assistant for advisors during and after client meetings — compliance checking, summarization, follow-up generation.*

---


## Unconsidered Needs

Problems the bank has NOT raised but should be assessed:

### Wealth Management Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-W-01 | Advisors spend more time on admin than clients | Accepted as normal; never measured as revenue opportunity cost | CAP-W-EE-01, CAP-W-AI-02 |
| UN-W-02 | No proactive life-event detection | Advisors wait for clients to call; missed intervention windows | CAP-W-CL-03, CAP-W-AI-01 |
| UN-W-03 | Client assets leaking to competitors undetected | Transfer patterns to external brokerages not monitored | CAP-W-DI-01, CAP-W-CL-03 |
| UN-W-04 | Referral decay — leads go cold before advisor contact | No urgency scoring; no speed-to-contact measurement | CAP-W-CE-03, CAP-W-PO-01 |
| UN-W-05 | Complexity mismatch — simple clients overserved, complex clients underserved | No systematic matching of client complexity to advisor tier | CAP-W-CL-02, CAP-W-EE-01 |

## Part 6: Problem Statement Categories

Problems identified in discovery or workshops should be classified as:

### Considered Needs
Problems the bank is **already aware of** and actively trying to solve. These validate existing initiatives and provide cost/impact data.

### Unconsidered Needs
Problems the bank **hasn't thought of** or doesn't realize they have. These are high-value because they create new urgency and differentiate the assessment from what the bank already knows.

Every problem links to capabilities that solve it:

```
Problem Statement: [Title]
├── Type: Considered | Unconsidered
├── Severity: Critical | High | Medium | Low
├── Impact: [Quantified where possible]
├── Metrics: [Observable indicators]
└── Related Capabilities: [CAP-IDs that solve this problem]
```

---

## Part 11: How to Use This Taxonomy

### In a Workshop
1. Start with Problem Statements (considered + unconsidered)
2. For each problem, identify related capabilities from this catalog
3. Score each capability 0-4 using the probing questions
4. Score each layer (Front/Middle/Back) separately
5. Capture notes and evidence for each score
6. Export data for heatmap visualization

### From a Transcript (No Workshop)
1. Extract problem statements from stakeholder quotes
2. Map quotes to capabilities as evidence
3. Infer maturity levels based on descriptions (conservative bias)
4. Flag capabilities with no evidence as "assumed" with validation needed
5. Proactively surface unconsidered needs based on domain patterns

### Per-Domain Application
- **Retail Banking:** Use CAP-R-* capabilities (Part 4)
- **Wealth Management:** Use CAP-W-* capabilities (Part 7)
- **SME/Business Banking:** Use CAP-S-* capabilities (Part 8)
- **Commercial Banking:** Use CAP-C-* capabilities (Part 9)
- **Corporate Banking:** Use CAP-CO-* capabilities (Part 10)

---

*Classification: Internal — Value Consulting Use Only*
*Version: 2.0*
*Last Updated: 2026-02-04*
*Based on: BIAN Service Landscape v13, Backbase Unified Banking Suite*
*Domains: Retail (CAP-R), Wealth (CAP-W), SME (CAP-S), Commercial (CAP-C), Corporate (CAP-CO)*