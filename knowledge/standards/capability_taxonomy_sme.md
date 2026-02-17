# Capability Taxonomy — SME Banking

> **Domain slice** auto-generated from `capability_taxonomy.md`
> Generated: 2026-02-17 09:22
> Master file: `knowledge/standards/capability_taxonomy.md` (2,109 lines)
> This slice: ~SME Banking capabilities only

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

## Part 8: SME Banking Capability Catalog

*SME banking sits between Retail and Commercial. Business owners expect retail-like digital experiences but with business-grade features: invoicing, multi-user access, business lending, and accounting integration.*

### Domain: Customer Channels & Engagement (SME)
*BIAN: Sales & Service → Channel Management*

#### CAP-S-CE-01: SME Digital Portal
**Description:** Digital banking portal tailored for business owners — account overview, invoicing, payments, and business tools.

**Front Layer:**
- Business dashboard (cash position, receivables, payables)
- Multi-account and multi-entity view
- Invoice management and payment links
- Business notifications and alerts

**Middle Layer:**
- Session management with business context
- Role-based access for multiple users
- Feature toggling per business tier
- Personalization (industry-specific views)

**Back Layer:**
- API gateway with business-grade SLAs
- Core banking connectivity
- Accounting software integration
- Business analytics telemetry

**Probing Questions:**
1. Do SME customers have a dedicated digital banking experience or do they use the retail platform? *(0→1)*
2. Does the SME portal include business-specific features (invoicing, multi-user, cash flow view) or just basic account access? *(1→2)*
3. Is the portal integrated with accounting platforms (Xero, QuickBooks, Sage) and does it support multi-user workflows? *(2→3)*
4. Does AI provide cash flow forecasting, working capital insights, or proactive business recommendations? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-S-CE-02: SME RM / Employee Workspace
**Description:** Workspace for SME relationship managers and branch staff to serve business clients with full context.

**Front Layer:**
- Business client 360 view (products, transactions, facilities)
- Lending pipeline and opportunity tracker
- Task queue for service requests
- Next-best-action suggestions

**Middle Layer:**
- Business context assembly (aggregating across products)
- Entitlements and role-based access
- Workflow routing for SME service tasks
- RM performance tracking

**Back Layer:**
- CRM integration
- Core banking connectivity (business accounts, lending)
- Interaction logging
- Portfolio analytics

**Probing Questions:**
1. Do SME RMs have a dedicated workspace or use generic retail/branch tools? *(0→1)*
2. Does the workspace show a unified view of the business client (all accounts, facilities, interactions)? *(1→2)*
3. Are SME servicing workflows automated with pipeline tracking, SLAs, and handoff management? *(2→3)*
4. Does AI suggest cross-sell opportunities, predict business client churn, or auto-prioritize the RM's book? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

### Domain: Customer Lifecycle Management (SME)
*BIAN: Customer Management → Customer Onboarding*

#### CAP-S-CL-01: SME Digital Onboarding
**Description:** End-to-end digital account opening for business clients — from application through KYB to active account.

**Front Layer:**
- Digital business application form
- Beneficial owner identification
- Document upload (incorporation docs, financials)
- Application status tracker

**Middle Layer:**
- Business verification workflow (KYB)
- Beneficial owner chain resolution
- Risk scoring for business entities
- Decision engine (auto-approve, refer, decline)
- STP for low-risk businesses

**Back Layer:**
- Company registry integration (Companies House, SEC, ACRA)
- KYC/AML vendor integration
- Core banking account creation
- Credit bureau (business credit)
- Document management

**Probing Questions:**
1. Can businesses open an account digitally without visiting a branch? *(0→1)*
2. Is the KYB process standardized with automated company registry lookups and defined workflows? *(1→2)*
3. Does STP exist for low-risk business applications (auto-approval without manual review)? *(2→3)*
4. Does AI predict application abandonment, auto-classify business types, or handle document exceptions autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-S-CL-02: Business Profile & 360 View
**Description:** Unified business client profile — company structure, directors, products, transaction patterns, and relationship history.

**Front Layer:**
- Business summary visible to RM/staff
- Self-service profile updates for business owners
- Director and authorized signatory management

**Middle Layer:**
- Entity resolution and group structure management
- Multi-signatory relationship tracking
- Business event detection (growth signals, risk signals)
- Segmentation (by revenue, industry, complexity)

**Back Layer:**
- Business master data store
- Company registry refreshes
- Integration with core banking, lending, and CRM
- Data quality and deduplication

**Probing Questions:**
1. Does a unified view of the business client exist (beyond per-product views)? *(0→1)*
2. Is business data aggregated from all products with group/entity structure visible? *(1→2)*
3. Is the profile updated in real-time with automated company registry refreshes? *(2→3)*
4. Does AI detect business lifecycle events (growth, distress, ownership changes) from data patterns? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

#### CAP-S-CL-03: SME Cross-Sell & Product Expansion
**Description:** Identifying and acting on opportunities to deepen the SME relationship — additional products, credit lines, and services.

**Front Layer:**
- Pre-qualified product offers in portal
- Product comparison tools
- One-click applications for pre-approved offers

**Middle Layer:**
- Propensity models (lending, card, merchant services)
- Pre-qualification engine
- Offer orchestration and timing
- Campaign management for SME segment

**Back Layer:**
- Product catalog and eligibility rules
- Credit decisioning integration
- Campaign analytics
- Consent and preference management

**Probing Questions:**
1. Does the bank actively cross-sell to SME clients beyond ad-hoc RM conversations? *(0→1)*
2. Are cross-sell offers based on defined criteria (transaction patterns, business size, product gaps)? *(1→2)*
3. Are offers pre-qualified in real-time and surfaced contextually in the digital portal and RM workspace? *(2→3)*
4. Does AI predict business needs before the client expresses them and trigger autonomous outreach? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

### Domain: SME Banking Services
*BIAN: Products → Consumer Banking (extended for business)*

#### CAP-S-RB-01: Business Account Management
**Description:** Day-to-day management of business current accounts, savings, and cash position visibility.

**Front Layer:**
- Multi-account business dashboard
- Transaction search and categorization
- Business statement generation
- Account settings and alerts

**Middle Layer:**
- Multi-user access with approval workflows
- Business transaction categorization engine
- Cash position aggregation (across accounts)
- Automated reconciliation support

**Back Layer:**
- Core banking (business account ledger)
- Transaction processing
- Statement generation
- Accounting integration (Xero, QuickBooks, Sage)

**Probing Questions:**
1. Can business clients view and manage their accounts digitally? *(0→1)*
2. Does the experience include business-specific features (multi-user access, transaction categorization, cash position)? *(1→2)*
3. Is account management integrated with accounting software with automated reconciliation? *(2→3)*
4. Does AI categorize transactions, forecast cash flow, and alert on anomalies? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-S-RB-02: Invoicing & Cash Flow Tools
**Description:** Integrated invoicing, receivables tracking, and cash flow management tools for SME clients.

**Front Layer:**
- Invoice creation and sending
- Payment link generation
- Receivables tracking dashboard
- Cash flow forecast visualization

**Middle Layer:**
- Invoice lifecycle management
- Payment matching and reconciliation
- Cash flow forecasting engine
- Overdue invoice alerting and follow-up automation

**Back Layer:**
- Payment gateway integration
- Accounting system sync
- Transaction matching engine
- Business analytics data store

**Probing Questions:**
1. Does the bank offer any invoicing or cash flow tools to SME clients? *(0→1)*
2. Are invoicing tools integrated into the banking platform (not standalone third-party)? *(1→2)*
3. Do invoices auto-reconcile with incoming payments, and does cash flow forecasting use real transaction data? *(2→3)*
4. Does AI predict payment collection timing, recommend invoice follow-up actions, or auto-initiate collections? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

#### CAP-S-RB-03: Card & Merchant Services
**Description:** Business debit/credit card management and merchant acquiring services for SME clients.

**Front Layer:**
- Business card management (issuance, limits, controls)
- Expense categorization by cardholder
- Merchant services dashboard (POS, online payments)
- Card-linked offers and rewards

**Middle Layer:**
- Card lifecycle orchestration (issue, activate, suspend, replace)
- Spending controls and limits per cardholder/department
- Expense reporting integration
- Merchant onboarding workflow

**Back Layer:**
- Card processor integration
- Payment network connectivity (Visa/MC)
- Merchant acquiring system
- Fraud detection
- Accounting integration

**Probing Questions:**
1. Can business clients manage cards and merchant services digitally? *(0→1)*
2. Are card controls granular (per-employee limits, category restrictions) with expense categorization? *(1→2)*
3. Are card operations automated with instant issuance, real-time expense integration, and merchant self-onboarding? *(2→3)*
4. Does AI detect anomalous card spend, auto-categorize expenses, or optimize merchant payment acceptance? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Digital Lending & Origination (SME)
*BIAN: Products → Lending → Corporate Loan*

#### CAP-S-DL-01: Business Loan Origination
**Description:** End-to-end digital lending for SME clients — working capital, term loans, asset finance, and credit lines.

**Front Layer:**
- Digital loan application (mobile/web)
- Eligibility checker and rate calculator
- Document upload and financial statement capture
- Application tracking dashboard

**Middle Layer:**
- Loan origination workflow (multi-step)
- Credit decisioning engine (financial statement analysis, scorecard)
- Underwriting automation (spreading, ratio analysis)
- Pricing engine and covenant setup
- Disbursement orchestration

**Back Layer:**
- Credit bureau integration (business credit: D&B, Experian Business)
- Loan management system
- Document management and storage
- Regulatory compliance (fair lending, disclosures)
- Collateral management system

**Probing Questions:**
1. Can SME clients apply for loans through a digital channel? *(0→1)*
2. Is the origination process standardized with defined SLAs and automated financial spreading? *(1→2)*
3. Does auto-decisioning exist for qualifying applications with instant approval for pre-qualified businesses? *(2→3)*
4. Does AI optimize pricing per client, predict default risk from transaction patterns, or handle covenant monitoring autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Payments & Transfers (SME)
*BIAN: Operations & Execution → Payment Execution*

#### CAP-S-PT-01: Business Payments & Transfers
**Description:** Payment initiation, approval workflows, bulk payments, and payroll processing for business clients.

**Front Layer:**
- Single and bulk payment initiation
- Payment approval workflows (multi-level)
- Beneficiary management
- Payment status tracking
- Payroll upload and processing

**Middle Layer:**
- Payment orchestration and routing
- Multi-level approval engine (limits-based)
- Payment scheduling and recurring payments
- STP rate management
- Fraud and sanctions screening

**Back Layer:**
- Payment network connectivity (ACH, SEPA, Faster Payments, SWIFT)
- Core banking posting
- Reconciliation engine
- AML/sanctions screening
- Regulatory reporting

**Probing Questions:**
1. Can business clients initiate payments digitally with multi-user approval? *(0→1)*
2. Are approval workflows configurable (by amount, type, user) with bulk payment and payroll support? *(1→2)*
3. Are payments processed with high STP rates, real-time tracking, and automated reconciliation? *(2→3)*
4. Does AI detect payment anomalies, suggest optimal payment timing, or auto-route for cost optimization? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Risk, Compliance & Security (SME)
*BIAN: Risk & Compliance*

#### CAP-S-RC-01: KYC/KYB & Business Screening
**Description:** Know Your Business — entity verification, beneficial owner identification, and ongoing monitoring for SME clients.

**Front Layer:**
- Business identity verification UX
- Beneficial owner declaration forms
- Periodic review requests to business owners

**Middle Layer:**
- KYB workflow orchestration
- Beneficial owner chain resolution (UBO)
- Business risk scoring
- Periodic review scheduling
- Ongoing monitoring rules

**Back Layer:**
- Company registry integration (country-specific)
- KYC/AML vendor integration
- Sanctions and PEP screening
- Regulatory reporting
- Audit trail

**Probing Questions:**
1. Is KYB performed digitally with automated company registry lookups? *(0→1)*
2. Is the KYB process standardized with beneficial owner chain resolution and defined workflows? *(1→2)*
3. Is ongoing monitoring automated with risk-based triggers and STP for low-risk reviews? *(2→3)*
4. Does AI perform continuous business risk assessment, detect ownership changes, or predict suspicious patterns? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Process Orchestration (SME)
*BIAN: Operations & Execution → Fulfillment*

#### CAP-S-PO-01: SME Workflow & Process Management
*Same structure as CAP-R-PO-01 but applied to SME-specific processes (business onboarding, lending, multi-user provisioning).*

**Probing Questions:**
1. Are key SME business processes (onboarding, lending, servicing) managed through a workflow tool? *(0→1)*
2. Is there a standardized BPM engine used across SME processes? *(1→2)*
3. Are SME processes measured with SLAs, automated handoffs, and exception routing? *(2→3)*
4. Does AI optimize SME process routing, predict bottlenecks, or handle exceptions autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Employee Enablement (SME)
*BIAN: Business Support → Case Management*

#### CAP-S-EE-01: SME Case Management
*Same structure as CAP-R-EE-01 but with business-specific case types (account mandates, user provisioning, business lending queries).*

**Probing Questions:**
1. Is there a formal case management system for SME service requests? *(0→1)*
2. Are SME cases classified with business-specific categories (mandate changes, user access, lending queries)? *(1→2)*
3. Is case handling measured with SLA tracking and automated routing by case type? *(2→3)*
4. Does AI auto-classify SME cases, suggest resolutions, or resolve routine business requests autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Data & Intelligence (SME)

#### CAP-S-DI-01: SME Data Foundation
*Same structure as CAP-R-DI-01 with added emphasis on business financial data, transaction patterns, and accounting integration data.*

**Probing Questions:**
1. Is SME business data (transactions, financials, profiles) centralized or siloed across systems? *(0→1)*
2. Is there a defined data architecture that includes SME-specific data (business financials, entity structures)? *(1→2)*
3. Is SME data available in real-time for RM dashboards, credit monitoring, and business analytics? *(2→3)*
4. Does a data fabric power business intelligence models, cash flow prediction, and AI-driven business insights? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

#### CAP-S-DI-02: SME Analytics & Reporting
*Same structure as CAP-R-DI-02 with SME-specific metrics: SME portfolio health, credit utilization, NTB conversion, cost-to-serve per segment.*

**Expected Maturity Hypothesis:** 0

---

### Domain: AI & Agentic (SME)

#### CAP-S-AI-01: SME Virtual Assistant
*Same structure as CAP-R-AI-01 with business context — understanding invoicing queries, payment status, business account operations.*

**Expected Maturity Hypothesis:** 0

#### CAP-S-AI-02: SME RM AI Copilot
*Same structure as CAP-R-AI-02 applied to SME relationship management — business health alerts, lending opportunity detection, meeting preparation.*

**Expected Maturity Hypothesis:** 0

---


## Unconsidered Needs

Problems the bank has NOT raised but should be assessed:

### SME Banking Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-S-01 | SME treated as "small retail" — no business-specific digital tools | SME is a cost center; investment goes to retail or commercial | CAP-S-CE-01, CAP-S-RB-02 |
| UN-S-02 | Cash flow blindness — business owners can't see forward cash position | Banks provide balances, not forecasts; seen as the business's problem | CAP-S-RB-02, CAP-S-DI-01 |
| UN-S-03 | Onboarding friction kills NTB — 40%+ abandonment on business accounts | Measured by applications started, not by those lost before starting | CAP-S-CL-01, CAP-S-RC-01 |
| UN-S-04 | No cross-sell engine — product penetration is 1.5 products per SME | RMs don't have time or data; digital offers don't exist | CAP-S-CL-03, CAP-S-DI-01, CAP-S-AI-02 |
| UN-S-05 | Lending leakage to fintechs — SMEs get loans elsewhere because bank is too slow | Banks track declined applications but not "never applied because too slow" | CAP-S-DL-01, CAP-S-PO-01 |
| UN-S-06 | RM model unsustainable — SME RMs carry 200+ relationships with no digital leverage | Accepted as normal; RM workload never quantified against revenue per client | CAP-S-CE-02, CAP-S-AI-02 |

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