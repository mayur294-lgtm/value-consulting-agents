# Capability Taxonomy — Retail Banking

> **Domain slice** auto-generated from `capability_taxonomy.md`
> Generated: 2026-02-17 09:22
> Master file: `knowledge/standards/capability_taxonomy.md` (2,109 lines)
> This slice: ~Retail Banking capabilities only

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

## Part 4: Capability Catalog — Retail Banking

### Domain: Customer Channels & Engagement
*BIAN: Sales & Service → Channel Management*

#### CAP-R-CE-01: Digital Channel Availability
**Description:** Customer-facing digital channels (mobile app, web banking) for self-service banking operations.

**Front Layer:**
- Mobile banking app (iOS/Android)
- Web/online banking portal
- Responsive design, accessibility compliance
- Consistent branding across channels

**Middle Layer:**
- Session management and context continuity
- Feature flagging and progressive rollout
- Channel orchestration (start on mobile, continue on web)
- Personalization engine (content, layout, offers)

**Back Layer:**
- API gateway for channel-to-service connectivity
- Authentication and token management
- Channel analytics and telemetry
- Device management and registration

**Probing Questions:**
1. Do customers have access to both mobile and web digital banking? *(0→1)*
2. Is the experience consistent across channels with the same features available? *(1→2)*
3. Can a customer start a transaction on one channel and complete on another without re-entering data? *(2→3)*
4. Does the channel adapt in real-time based on customer behavior, preferences, or predictive models? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-R-CE-02: Employee Workspace
**Description:** Unified workspace for frontline staff (CSRs, branch officers) to service customers with full context.

**Front Layer:**
- Customer 360 view for CSR/branch staff
- Case management interface
- Unified search across products and customers
- Next-best-action prompts

**Middle Layer:**
- Customer context assembly (aggregating data from multiple systems)
- Entitlements and role-based access control
- Workflow routing and task assignment
- Agent assist / AI suggestions

**Back Layer:**
- CRM integration
- Core banking system connectivity
- Interaction logging and audit trail
- Knowledge base for staff guidance

**Probing Questions:**
1. Do frontline staff have a digital workspace for customer servicing? *(0→1)*
2. Does the workspace show a unified customer view or do staff toggle between systems? *(1→2)*
3. Are servicing workflows automated with SLA tracking and handoff management? *(2→3)*
4. Does AI surface next-best-actions, auto-draft responses, or handle routine queries autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-R-CE-03: Contact Center Operations
**Description:** Multi-channel contact center capability for inbound/outbound customer interactions.

**Front Layer:**
- Phone, chat, email, video channels
- IVR/self-service options
- Queue management and callback scheduling
- Customer authentication at contact

**Middle Layer:**
- Omnichannel routing (skill-based, priority-based)
- Customer identification and context passing
- Interaction recording and quality management
- Workforce scheduling and capacity management

**Back Layer:**
- Telephony/contact center platform integration
- CRM and case management system
- Analytics and reporting
- Compliance recording and retention

**Probing Questions:**
1. Does a multi-channel contact center exist? *(0→1)*
2. Are channels integrated so customer context passes between them (no re-explanation)? *(1→2)*
3. Is routing intelligent (skill-based, priority-based) with measured SLAs? *(2→3)*
4. Does AI handle initial triage, suggest resolutions, or autonomously resolve routine requests? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Customer Lifecycle Management
*BIAN: Customer Management → Customer Profile, Customer Onboarding*

#### CAP-R-CL-01: Digital Onboarding
**Description:** End-to-end digital account opening for new customers, from application to funded account.

**Front Layer:**
- Digital application form (mobile/web)
- Document upload and capture
- Real-time application status tracking
- Welcome and activation experience

**Middle Layer:**
- Application workflow orchestration
- Identity verification (ID&V, biometric)
- KYC/AML screening automation
- Decision engine (auto-approve, refer, decline)
- STP for low-risk applications

**Back Layer:**
- Core banking account creation
- KYC/AML vendor integration (Jumio, Onfido, etc.)
- Document management system
- Regulatory reporting
- Credit bureau integration

**Probing Questions:**
1. Can customers open an account through a digital channel without visiting a branch? *(0→1)*
2. Is the onboarding process standardized with defined SLAs and documented workflows? *(1→2)*
3. Does STP exist for low-risk applicants (auto-decisioning, no manual review)? *(2→3)*
4. Does AI predict application drop-off and intervene? Does an agent handle document exceptions autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-R-CL-02: Customer Profile & 360 View
**Description:** Unified customer data across all products, channels, and interactions — the single source of truth.

**Front Layer:**
- Customer summary visible to staff
- Self-service profile management for customers
- Preference management (communication, channel, product)

**Middle Layer:**
- Data aggregation from multiple systems
- Identity resolution (matching across sources)
- Real-time profile updates
- Consent and preference management
- Customer segmentation engine

**Back Layer:**
- Customer master data store
- Data quality rules and deduplication
- Integration with core banking, CRM, and product systems
- Data lineage and audit trail
- Privacy compliance (GDPR, CCPA)

**Probing Questions:**
1. Does a unified customer view exist anywhere in the organization? *(0→1)*
2. Is customer data aggregated from all product systems into one profile, or are there separate views per product? *(1→2)*
3. Is the profile updated in real-time across all touchpoints (change of address propagates instantly)? *(2→3)*
4. Does a Customer State Graph exist that powers AI decisioning, next-best-actions, and personalization? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

#### CAP-R-CL-03: Customer Behavioral Insights
**Description:** Understanding customer behavior patterns, preferences, and lifecycle stage to drive engagement and retention.

**Front Layer:**
- Personalized product recommendations
- Behavioral nudges and prompts
- Engagement scoring visible to staff

**Middle Layer:**
- Behavioral analytics engine
- Event detection (life events, pattern changes)
- Segmentation and micro-segmentation
- Propensity models (churn, cross-sell, upgrade)
- Campaign orchestration (CLO)

**Back Layer:**
- Clickstream and interaction data collection
- Data warehouse / data lake
- ML model training and deployment pipeline
- A/B testing framework
- Consent tracking for data usage

**Probing Questions:**
1. Does the bank track customer digital behavior beyond basic login counts? *(0→1)*
2. Is behavioral data used to segment customers and trigger targeted communications? *(1→2)*
3. Are propensity models in production (churn prediction, cross-sell likelihood)? *(2→3)*
4. Does real-time behavioral intelligence drive autonomous actions (auto-triggered interventions, agentic engagement)? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

### Domain: Retail Banking Services
*BIAN: Products → Consumer Banking*

#### CAP-R-RB-01: Account Management
**Description:** Day-to-day management of current accounts, savings accounts, and related services.

**Front Layer:**
- Account overview and balance display
- Transaction history and search
- Statement generation and download
- Account settings management

**Middle Layer:**
- Account lifecycle management
- Interest calculation and posting
- Fee management and waiver logic
- Account alerts and notifications
- Spending categorization

**Back Layer:**
- Core banking system (ledger)
- Transaction processing engine
- Statement generation system
- Regulatory reporting

**Probing Questions:**
1. Can customers view accounts and transactions digitally? *(0→1)*
2. Is the experience rich (search, categorization, alerts) or just basic balance/statement? *(1→2)*
3. Are account operations fully automated with real-time processing and proactive alerts? *(2→3)*
4. Does AI provide spending insights, anomaly detection, or predictive cash flow management? *(3→4)*

**Expected Maturity Hypothesis:** 2

---

#### CAP-R-RB-02: Card Management
**Description:** Credit and debit card lifecycle management — issuance, controls, and servicing.

**Front Layer:**
- Digital card issuance and activation
- Card controls (freeze, limits, travel)
- PIN management
- Digital wallet provisioning (Apple Pay, Google Pay)

**Middle Layer:**
- Card lifecycle orchestration
- Fraud rules and transaction monitoring
- Real-time authorization decisions
- Card rewards and loyalty program management

**Back Layer:**
- Card processor integration
- Fraud detection system
- Payment network connectivity (Visa/MC)
- Dispute management system

**Probing Questions:**
1. Can customers manage their cards digitally (freeze, activate, set limits)? *(0→1)*
2. Are card controls comprehensive and consistent across channels? *(1→2)*
3. Is card issuance instant (digital card available immediately)? Is dispute management automated? *(2→3)*
4. Does AI detect fraud in real-time, auto-block suspicious transactions, and resolve disputes autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Digital Lending & Origination
*BIAN: Products → Lending*

#### CAP-R-DL-01: Consumer Loan Origination
**Description:** End-to-end digital lending from application through underwriting to disbursement.

**Front Layer:**
- Digital loan application (mobile/web)
- Rate calculator and pre-qualification
- Document upload
- Application tracking

**Middle Layer:**
- Loan origination workflow
- Credit decisioning engine (rules + scorecard)
- Underwriting automation
- Pricing engine
- Disbursement orchestration

**Back Layer:**
- Credit bureau integration
- Loan management system (LMS)
- Document management
- Regulatory compliance (fair lending, disclosures)
- Fraud detection

**Probing Questions:**
1. Can customers apply for loans through a digital channel? *(0→1)*
2. Is the origination workflow standardized with defined SLAs? *(1→2)*
3. Does auto-decisioning exist for qualifying applications (instant approval without manual review)? *(2→3)*
4. Does AI optimize pricing per customer, predict default risk in real-time, or handle underwriting exceptions autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Payments & Transfers
*BIAN: Operations & Execution → Payment Execution*

#### CAP-R-PT-01: Domestic Payments
**Description:** Internal transfers, bill payments, P2P, and domestic payment processing.

**Front Layer:**
- Fund transfer (internal, external)
- Bill payment and scheduling
- P2P payments
- Payment confirmation and receipts

**Middle Layer:**
- Payment orchestration (routing, scheduling)
- Payment limits and fraud rules
- Recurring payment management
- Payment status tracking
- STP rate management

**Back Layer:**
- Payment network connectivity (ACH, RTP, Faster Payments, SEPA)
- Core banking posting
- Reconciliation
- AML/sanctions screening
- Regulatory reporting

**Probing Questions:**
1. Can customers make transfers and payments digitally? *(0→1)*
2. Are multiple payment types supported (P2P, bill pay, scheduled) with consistent experience? *(1→2)*
3. Are payments processed with high STP rates, real-time confirmation, and automated reconciliation? *(2→3)*
4. Does AI detect payment anomalies, predict cash needs, or auto-schedule payments based on behavior? *(3→4)*

**Expected Maturity Hypothesis:** 2

---

### Domain: Risk, Compliance & Security
*BIAN: Risk & Compliance*

#### CAP-R-RC-01: KYC/AML & Customer Screening
**Description:** Know Your Customer, Anti-Money Laundering, and sanctions screening across the customer lifecycle.

**Front Layer:**
- Identity verification UX (document capture, biometrics)
- Periodic review requests to customers
- Screening status visibility for staff

**Middle Layer:**
- KYC workflow orchestration
- Risk scoring and customer risk rating
- Ongoing monitoring rules
- Periodic review scheduling
- Case management for alerts

**Back Layer:**
- KYC/AML vendor integration (ComplyAdvantage, Onfido, etc.)
- Sanctions list management
- Transaction monitoring system
- Regulatory reporting (SARs, CTRs)
- Audit trail

**Probing Questions:**
1. Is KYC performed digitally or primarily paper-based/in-branch? *(0→1)*
2. Is the KYC process standardized with defined workflows and vendor integrations? *(1→2)*
3. Is ongoing monitoring automated with risk-based trigger rules and STP for low-risk reviews? *(2→3)*
4. Does AI perform continuous customer risk assessment, predict suspicious patterns, or auto-resolve false positives? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Process Orchestration & Fulfillment
*BIAN: Operations & Execution → Fulfillment*

#### CAP-R-PO-01: Workflow & Business Process Management
**Description:** Orchestration of end-to-end business processes across front, middle, and back office.

**Front Layer:**
- Task queues for operations staff
- SLA dashboards and alerts
- Exception handling interfaces

**Middle Layer:**
- Business process engine (BPMN)
- Rules engine for routing and decisions
- SLA monitoring and escalation
- Handoff orchestration between teams
- Process analytics

**Back Layer:**
- Process repository and version control
- Integration with core systems
- Audit logging
- Performance measurement

**Probing Questions:**
1. Are key business processes documented and managed through a workflow tool? *(0→1)*
2. Is there a standardized BPM/workflow engine used across processes? *(1→2)*
3. Are processes measured with SLAs, automated handoffs, and exception routing? *(2→3)*
4. Does AI optimize process routing, predict bottlenecks, or autonomously handle exceptions? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Employee Enablement
*BIAN: Business Support → Case Management*

#### CAP-R-EE-01: Case Management & Service Requests
**Description:** Structured management of customer cases, complaints, disputes, and service requests.

**Front Layer:**
- Case submission (customer self-service)
- Case tracking and status updates
- Staff case management workspace
- Escalation visibility

**Middle Layer:**
- Case classification and routing
- SLA management per case type
- Escalation workflows
- Resolution templates and knowledge base
- Quality assurance sampling

**Back Layer:**
- Case management system
- Knowledge base
- Correspondence system
- Reporting and analytics
- Regulatory complaint tracking

**Probing Questions:**
1. Is there a formal case management system or are issues tracked via email/spreadsheets? *(0→1)*
2. Are cases classified, routed, and tracked with defined SLAs? *(1→2)*
3. Is case handling measured, with automated routing, SLA alerts, and resolution analytics? *(2→3)*
4. Does AI auto-classify cases, suggest resolutions, or resolve routine cases autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Data & Intelligence (Beyond BIAN)

#### CAP-R-DI-01: Data Foundation & Fabric
**Description:** Unified data layer enabling analytics, reporting, and AI across the organization.

**Front Layer:**
- Business dashboards and reports
- Self-service analytics for business users
- Data catalog browsable by non-technical users

**Middle Layer:**
- Data integration and ETL/ELT pipelines
- Data quality rules and monitoring
- Master data management
- Data catalog and metadata management
- Data governance policies

**Back Layer:**
- Data warehouse / data lakehouse
- Real-time data streaming
- Data lineage tracking
- Privacy and consent enforcement
- Data retention policies

**Probing Questions:**
1. Is data centralized in any form (warehouse, lake) or completely siloed in individual systems? *(0→1)*
2. Is there a defined data architecture with quality rules, governance, and a data catalog? *(1→2)*
3. Is data available in real-time, with automated pipelines, quality monitoring, and self-service access? *(2→3)*
4. Does a data fabric power ML models, real-time decisioning, and AI agents with semantic context? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

#### CAP-R-DI-02: Analytics & Reporting
**Description:** Business intelligence, operational reporting, and customer analytics.

**Front Layer:**
- Executive dashboards
- Operational reports
- Customer behavior reports
- Regulatory reports

**Middle Layer:**
- Reporting engine and scheduling
- Ad-hoc query capability
- KPI definition and tracking
- Alerting on threshold breaches

**Back Layer:**
- BI platform (Tableau, Power BI, etc.)
- Data warehouse queries
- Report distribution system
- Archive and audit trail

**Probing Questions:**
1. Does the bank have operational and business dashboards beyond core banking reports? *(0→1)*
2. Are reports standardized, scheduled, and accessible to relevant stakeholders? *(1→2)*
3. Are analytics real-time, with automated alerting on KPI breaches and self-service exploration? *(2→3)*
4. Are analytics predictive (forecasting, trend detection) rather than just descriptive/historical? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: AI & Agentic (Beyond BIAN)

#### CAP-R-AI-01: Conversational AI & Virtual Assistants
**Description:** AI-powered chatbots and virtual assistants for customer and employee interactions.

**Front Layer:**
- Customer-facing chatbot (app, web)
- Employee-facing AI assistant
- Voice-enabled queries
- Multi-turn conversation capability

**Middle Layer:**
- NLU/intent classification
- Dialogue management
- Knowledge retrieval (RAG)
- Escalation to human logic
- Compliance guardrails

**Back Layer:**
- LLM infrastructure
- Knowledge base / vector database
- Conversation logging and audit
- Model versioning and evaluation
- Feedback loop for improvement

**Probing Questions:**
1. Does any AI chatbot or virtual assistant exist for customers or employees? *(0→1)*
2. Can it handle more than FAQs — can it understand context and perform multi-turn conversations? *(1→2)*
3. Can it execute transactions, access customer data, and resolve issues without human intervention? *(2→3)*
4. Does it learn from interactions, adapt to individual users, and coordinate with other AI agents? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

#### CAP-R-AI-02: AI Copilots for Employees
**Description:** AI assistants that augment employee productivity in workspaces (CSR, RM, operations).

**Front Layer:**
- AI suggestions in employee workspace
- Auto-drafted responses and summaries
- Real-time compliance alerts
- Next-best-action recommendations

**Middle Layer:**
- Context-aware AI engine (customer data + conversation)
- Compliance rule checking
- Action recommendation algorithms
- Meeting summarization / note generation
- Task prioritization logic

**Back Layer:**
- CRM and workspace integration
- LLM inference service
- Audit trail of AI suggestions
- Model governance and versioning
- Training data management

**Probing Questions:**
1. Do employees have any AI assistance in their daily workflow? *(0→1)*
2. Does AI assist with specific tasks (drafting, summarizing) or just provide generic information? *(1→2)*
3. Is the copilot context-aware (knows the customer, the conversation, the history) and integrated into the workflow? *(2→3)*
4. Does the copilot autonomously handle routine tasks, learn from advisor behavior, and coordinate across agents? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

#### CAP-R-AI-03: AI Governance & Trust
**Description:** Organizational controls, policies, and infrastructure for safe, compliant AI deployment.

**Front Layer:**
- AI transparency disclosures to customers
- Explainability of AI decisions
- Opt-out options

**Middle Layer:**
- AI guardrails (input/output validation)
- Human-in-the-loop approval workflows
- Bias detection and mitigation
- Model performance monitoring
- A/B testing for AI interventions

**Back Layer:**
- Model registry and version control
- AI audit trail
- Regulatory compliance framework for AI
- Red teaming and safety testing
- Observability and alerting

**Probing Questions:**
1. Are there any policies or guidelines for AI usage in the organization? *(0→1)*
2. Is there a defined AI governance framework with roles, review processes, and documentation? *(1→2)*
3. Are AI models monitored in production with bias detection, performance tracking, and human oversight? *(2→3)*
4. Is there a comprehensive AI trust framework with automated guardrails, real-time monitoring, and continuous evaluation? *(3→4)*

**Expected Maturity Hypothesis:** 0

---


## Unconsidered Needs

Problems the bank has NOT raised but should be assessed:

### Retail Banking Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-R-01 | Silent customer churn — customers disengage gradually with no detection | Banks measure churn as account closure, not behavioral disengagement | CAP-R-CL-03, CAP-R-DI-01, CAP-R-AI-01 |
| UN-R-02 | Employee context-switching tax — staff toggle 5+ systems per interaction | Accepted as "how things work," never measured as a cost | CAP-R-CE-02, CAP-R-PO-01 |
| UN-R-03 | No front-to-back journey visibility — process breaks are invisible | Each department sees only their part; no end-to-end view | CAP-R-PO-01, CAP-R-DI-02 |
| UN-R-04 | Data exists but isn't used — customer insights trapped in silos | Banks have data but no intelligence layer to act on it | CAP-R-DI-01, CAP-R-CL-03, CAP-R-AI-02 |
| UN-R-05 | Compliance is cost, not value — KYC/AML treated as overhead, not a trust signal | Banks see compliance as a box-ticking exercise, not a differentiator | CAP-R-RC-01, CAP-R-AI-03 |
| UN-R-06 | No AI strategy — bank has no roadmap for embedding intelligence | AI is either ignored or stuck in pilot purgatory | CAP-R-AI-01, CAP-R-AI-02, CAP-R-AI-03 |

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