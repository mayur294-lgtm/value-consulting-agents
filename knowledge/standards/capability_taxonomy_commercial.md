# Capability Taxonomy — Commercial Banking

> **Domain slice** auto-generated from `capability_taxonomy.md`
> Generated: 2026-02-17 09:22
> Master file: `knowledge/standards/capability_taxonomy.md` (2,109 lines)
> This slice: ~Commercial Banking capabilities only

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

## Part 9: Commercial Banking Capability Catalog

*Commercial banking serves mid-market and upper-mid-market businesses with complex treasury, trade, and multi-entity needs. Relationship management is central. Integration with client ERP/TMS systems is a differentiator.*

### Domain: Customer Channels & Engagement (Commercial)
*BIAN: Sales & Service → Channel Management*

#### CAP-C-CE-01: Commercial Client Portal
**Description:** Digital banking portal for corporate treasurers and finance teams — cash management, payments, trade, and reporting.

**Front Layer:**
- Treasury dashboard (consolidated cash positions)
- Multi-entity account hierarchy
- Payment initiation and tracking
- Trade finance document portal
- Reporting and statement center

**Middle Layer:**
- Session management with corporate entitlement context
- Multi-entity and multi-user access control
- Widget-based configurable dashboard
- White-label / co-brand capability

**Back Layer:**
- API gateway with corporate-grade SLAs
- Core banking connectivity (multi-entity)
- Trade finance system connectivity
- SWIFT message interface
- File upload/download (MT940, BAI2, CAMT)

**Probing Questions:**
1. Do commercial clients have a dedicated digital portal or do they rely on branch/phone/SWIFT messages? *(0→1)*
2. Does the portal provide consolidated multi-entity views with role-based access and comprehensive payment/trade capabilities? *(1→2)*
3. Is the portal integrated end-to-end (initiate → approve → execute → track → report) with real-time data and multi-bank views? *(2→3)*
4. Does the portal adapt to user behavior, provide AI-driven treasury insights, and support conversational interaction? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-C-CE-02: Commercial RM Workspace
**Description:** Relationship manager workspace for managing commercial client portfolios, opportunities, and service delivery.

**Front Layer:**
- Client portfolio view (AUM, revenue, products, utilization)
- Opportunity pipeline and deal tracker
- Meeting preparation and follow-up tools
- Credit facility overview and covenant monitoring

**Middle Layer:**
- Client revenue analytics and share-of-wallet estimation
- Opportunity scoring and prioritization
- Meeting preparation automation (pre-meeting briefs)
- Cross-sell recommendation engine
- Service request routing and tracking

**Back Layer:**
- CRM integration
- Core banking (commercial accounts, facilities)
- Deal management system
- Credit risk system
- Compliance system

**Probing Questions:**
1. Do commercial RMs have a dedicated digital workspace or rely on spreadsheets and email? *(0→1)*
2. Does the workspace provide a unified view of the client relationship (all products, facilities, interactions, revenue)? *(1→2)*
3. Are deal management, meeting preparation, and cross-sell workflows automated with pipeline analytics? *(2→3)*
4. Does AI generate pre-meeting briefs, predict client needs, prioritize the book, and identify at-risk relationships? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Customer Lifecycle Management (Commercial)
*BIAN: Customer Management → Customer Onboarding*

#### CAP-C-CL-01: Commercial Client Onboarding
**Description:** Multi-party, multi-entity onboarding for commercial clients — KYC/KYB, legal documentation, account setup, user provisioning, and system integration.

**Front Layer:**
- Digital onboarding portal (client-facing)
- Entity hierarchy builder
- Document upload and eSignature
- Onboarding progress tracker

**Middle Layer:**
- Multi-entity onboarding workflow (parallel tracks)
- KYC/KYB orchestration with beneficial owner chain
- Legal document workflow and approval routing
- User provisioning and entitlement setup
- Integration readiness assessment

**Back Layer:**
- Company registry integration (multi-country)
- KYC/AML vendor integration
- Core banking account creation (multi-entity)
- Document management system
- Identity management

**Probing Questions:**
1. Can commercial clients be onboarded through any digital channel or is the process entirely manual/paper-based? *(0→1)*
2. Is the onboarding process standardized with defined stages, SLAs, and parallel workstreams (KYC + legal + account setup)? *(1→2)*
3. Are onboarding workstreams orchestrated end-to-end with automated handoffs, STP for document processing, and real-time status visibility? *(2→3)*
4. Does AI predict onboarding delays, auto-classify documents, resolve entity structures, or handle exceptions autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Commercial Banking Services
*BIAN: Products → Commercial Banking*

#### CAP-C-RB-01: Cash Management
**Description:** Multi-entity cash position management, account structures, pooling, sweeping, and cash concentration.

**Front Layer:**
- Consolidated cash position dashboard
- Account hierarchy visualization
- Sweep and pool configuration UI
- Cash forecast view

**Middle Layer:**
- Cash position aggregation engine
- Notional and physical pooling logic
- Sweep rules and execution
- Cash forecast calculation
- Target balance management

**Back Layer:**
- Core banking (multi-entity ledger)
- Real-time balance feeds
- Cash pooling system
- Liquidity management system
- Reporting engine (MT940/CAMT)

**Probing Questions:**
1. Can commercial clients view consolidated cash positions across entities digitally? *(0→1)*
2. Are cash management structures (pooling, sweeping, target balances) configurable and managed through the portal? *(1→2)*
3. Are sweeps and cash concentration automated with real-time execution and intraday position updates? *(2→3)*
4. Does AI optimize cash structures, predict cash needs, and recommend sweep timing based on flow patterns? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Digital Lending & Origination (Commercial)
*BIAN: Products → Lending → Corporate Loan*

#### CAP-C-DL-01: Commercial Lending
**Description:** Origination and lifecycle management of commercial credit facilities — term loans, revolving credit, trade finance facilities.

**Front Layer:**
- Credit facility request portal
- Financial document upload
- Facility overview and utilization dashboard
- Covenant compliance tracker

**Middle Layer:**
- Credit origination workflow (multi-stage)
- Financial spreading and ratio analysis
- Credit decisioning (committee routing)
- Pricing and structuring tools
- Covenant monitoring engine

**Back Layer:**
- Credit risk system
- Loan management system
- Financial spreading tool
- Collateral management
- Regulatory reporting (Basel, CECL/IFRS9)

**Probing Questions:**
1. Can commercial lending requests be submitted through a digital channel? *(0→1)*
2. Is the lending workflow standardized with automated spreading, defined approval stages, and SLA tracking? *(1→2)*
3. Is lending orchestrated end-to-end with automated covenant monitoring, early warning signals, and renewal workflows? *(2→3)*
4. Does AI predict credit risk from transaction patterns, auto-generate credit memos, or optimize facility structures? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Payments & Transfers (Commercial)
*BIAN: Operations & Execution → Payment Execution*

#### CAP-C-PT-01: Commercial Payments
**Description:** High-value, bulk, and multi-currency payment processing with multi-level approval and compliance screening.

**Front Layer:**
- Single and bulk payment initiation
- Multi-level approval dashboard
- Beneficiary management and payment templates
- Payment tracking and audit trail
- File-based payment upload (pain.001, CSV)

**Middle Layer:**
- Multi-level approval engine (amount, type, entity)
- Payment routing optimization
- Compliance and sanctions screening (pre/post)
- STP rate management and exception handling
- Cut-off time management

**Back Layer:**
- Payment network connectivity (SWIFT, SEPA, ACH, RTP, local schemes)
- Core banking posting (multi-entity)
- AML/sanctions screening engine
- Reconciliation engine
- SWIFT messaging (MT103, MT202)

**Probing Questions:**
1. Can commercial clients initiate payments digitally with multi-level approval? *(0→1)*
2. Are payment workflows configurable (by amount, entity, payment type) with bulk processing and template support? *(1→2)*
3. Are payments processed with high STP rates, real-time tracking, automated sanctions screening, and same-day reconciliation? *(2→3)*
4. Does AI optimize payment routing for cost, detect anomalous payments, or predict cash needs for payment timing? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Risk, Compliance & Security (Commercial)
*BIAN: Risk & Compliance*

#### CAP-C-RC-01: Commercial KYC/KYB
**Description:** KYC/KYB for multi-entity commercial clients — complex ownership structures, beneficial owner chains, cross-border compliance.

**Front Layer:**
- Entity structure declaration portal
- Beneficial owner documentation
- Periodic review response portal
- Compliance status visibility

**Middle Layer:**
- KYC/KYB orchestration (multi-entity, multi-country)
- Beneficial owner chain resolution and validation
- Entity risk scoring
- Periodic review scheduling and management
- PEP and sanctions screening workflow

**Back Layer:**
- Company registry integration (multi-jurisdiction)
- KYC/AML vendor integration
- Sanctions list management
- Regulatory reporting (SARs, entity reporting)
- Document management and audit trail

**Probing Questions:**
1. Is KYC/KYB for commercial clients digitized or primarily manual with paper files? *(0→1)*
2. Is the process standardized with multi-entity workflow, beneficial owner resolution, and defined review cycles? *(1→2)*
3. Is KYC/KYB orchestrated with automated screening, risk-based review triggers, and STP for low-risk renewals? *(2→3)*
4. Does AI detect ownership structure changes, predict risk shifts, or auto-resolve false-positive screening alerts? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-C-RC-02: Entitlements & Access Management
**Description:** User provisioning, role management, and access control for commercial banking clients with multi-entity, multi-user requirements.

**Front Layer:**
- Client admin portal for user management
- Role and permission configuration
- Approval matrix setup
- User activity audit view

**Middle Layer:**
- Entitlement engine (role-based, entity-based, product-based)
- Approval matrix management
- User lifecycle management (onboard, modify, offboard)
- Segregation of duties enforcement

**Back Layer:**
- Identity and access management system
- Core banking entitlement integration
- Audit logging and compliance reporting
- Single sign-on and MFA

**Probing Questions:**
1. Can commercial clients self-manage user access and roles through a digital portal? *(0→1)*
2. Is the entitlement model granular (entity-level, product-level, function-level) with defined roles? *(1→2)*
3. Is user provisioning automated with STP, approval workflows, and real-time activation? *(2→3)*
4. Does AI detect access anomalies, recommend role optimizations, or auto-deprovision inactive users? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Trade Finance (Commercial)
*BIAN: Products → Trade Finance*

#### CAP-C-TF-01: Trade Finance (LC / BG / Documentary)
**Description:** Letters of credit, bank guarantees, and documentary collections — application, issuance, amendment, and settlement.

**Front Layer:**
- Trade finance application portal
- LC/BG request forms and amendment workflows
- Document presentation and checking interface
- Trade transaction tracker

**Middle Layer:**
- Trade finance workflow orchestration
- Document compliance checking rules
- Pricing and fee calculation
- Amendment and extension workflows
- Limit management and utilization tracking

**Back Layer:**
- Trade finance back-office system
- SWIFT messaging (MT700, MT760, etc.)
- Document management
- Compliance screening (dual-use goods, embargo)
- Core banking (trade facility ledger)

**Probing Questions:**
1. Can clients initiate trade finance requests (LC/BG) through a digital channel? *(0→1)*
2. Is the trade finance workflow standardized with defined stages, document checklists, and SLA tracking? *(1→2)*
3. Is trade processing automated with STP for compliant documents, integrated pricing, and real-time status tracking? *(2→3)*
4. Does AI perform automated document compliance checking, predict discrepancies, or handle routine amendments autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-C-TF-02: Supply Chain Finance
**Description:** Buyer-led and supplier-led supply chain finance programs — receivables finance, payables finance, and dynamic discounting.

**Front Layer:**
- Supplier onboarding portal
- Invoice approval and financing request interface
- Program dashboard (utilization, savings)
- Supplier self-service portal

**Middle Layer:**
- Supply chain finance program orchestration
- Dynamic discounting engine
- Supplier risk assessment
- Invoice validation and matching
- Program analytics and reporting

**Back Layer:**
- ERP/procurement system integration
- Invoice matching engine
- Payment processing
- Accounting and ledger posting
- Supplier master data management

**Probing Questions:**
1. Does the bank offer supply chain finance programs through a digital platform? *(0→1)*
2. Are programs standardized with supplier onboarding, invoice approval workflows, and defined pricing models? *(1→2)*
3. Is SCF processing automated with ERP integration, auto-matching invoices, and real-time discount optimization? *(2→3)*
4. Does AI predict supplier payment behavior, optimize discount rates dynamically, or detect supply chain risk signals? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

### Domain: Process Orchestration (Commercial)
*BIAN: Operations & Execution → Fulfillment*

#### CAP-C-PO-01: Commercial Workflow Management
*Same structure as CAP-R-PO-01 but applied to commercial-specific processes (complex onboarding, trade operations, multi-entity management).*

**Probing Questions:**
1. Are key commercial processes (onboarding, trade, payments) managed through a workflow tool? *(0→1)*
2. Is there a standardized BPM engine with defined SLAs for commercial operations? *(1→2)*
3. Are commercial workflows orchestrated end-to-end with automated handoffs, exception routing, and real-time SLA monitoring? *(2→3)*
4. Does AI optimize commercial workflow routing, predict operational bottlenecks, or handle exceptions autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Employee Enablement (Commercial)
*BIAN: Business Support → Case Management*

#### CAP-C-EE-01: Commercial Case Management
*Same structure as CAP-R-EE-01 with commercial-specific case types (trade discrepancies, payment investigations, facility amendments, multi-entity queries).*

**Probing Questions:**
1. Is there a formal case management system for commercial service requests? *(0→1)*
2. Are cases classified with commercial-specific categories (trade, payments, facilities, compliance)? *(1→2)*
3. Is case handling measured with SLA tracking, automated routing by complexity, and resolution analytics? *(2→3)*
4. Does AI auto-classify commercial cases, suggest resolutions from historical patterns, or resolve routine queries autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Data & Intelligence (Commercial)

#### CAP-C-DI-01: Commercial Data Foundation
*Same structure as CAP-R-DI-01 with emphasis on multi-entity data, trade data, treasury analytics, and client revenue data.*

**Probing Questions:**
1. Is commercial client data (entities, facilities, trade, payments) centralized or siloed across product systems? *(0→1)*
2. Is there a defined data architecture that includes commercial-specific data (entity hierarchies, trade data, facility utilization)? *(1→2)*
3. Is commercial data available in real-time for RM dashboards, treasury analytics, and credit monitoring? *(2→3)*
4. Does a data fabric power revenue analytics, client intelligence, and AI-driven commercial insights? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

### Domain: AI & Agentic (Commercial)

#### CAP-C-AI-01: Commercial Virtual Assistant
*Same structure as CAP-R-AI-01 with commercial context — understanding payment status queries, trade finance inquiries, facility questions.*

**Expected Maturity Hypothesis:** 0

#### CAP-C-AI-02: Commercial RM AI Copilot
*Same structure as CAP-R-AI-02 applied to commercial relationship management — deal preparation, credit memo drafting, client review automation, cross-sell identification.*

**Expected Maturity Hypothesis:** 0

---


## Unconsidered Needs

Problems the bank has NOT raised but should be assessed:

### Commercial Banking Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-C-01 | Onboarding takes weeks/months — clients generate zero revenue during setup | Onboarding seen as compliance necessity, not revenue delay | CAP-C-CL-01, CAP-C-PO-01 |
| UN-C-02 | RM can't see share-of-wallet — no visibility into competitor relationships | No multi-bank data; RM relies on client self-reporting | CAP-C-CE-02, CAP-C-DI-01 |
| UN-C-03 | Payment operations are people-heavy — manual repair rates above 10% | "Payment ops has always been manual" — cost never questioned | CAP-C-PT-01, CAP-C-PO-01 |
| UN-C-04 | Trade finance is paper-based — LCs and BGs still require physical documents | Seen as industry norm; digitization efforts haven't reached trade | CAP-C-TF-01, CAP-C-TF-02 |
| UN-C-05 | Entitlement management is a bottleneck — adding/changing users takes days | Buried in IT tickets; never measured as client experience friction | CAP-C-RC-02, CAP-C-PO-01 |

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