# Capability Taxonomy: BIAN-Aligned with Backbase Terminology

**Standard:** BIAN Service Landscape (v13) mapped to Backbase Unified Banking Suite
**Scale:** 0-4 Maturity (Absent → Fragmented → Defined → Orchestrated → Intelligent)
**Structure:** Front Layer / Middle Layer / Back Layer per capability

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

---

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

## Part 5: Unconsidered Needs Library

These are problems that banks typically have NOT raised but should be assessed. The capability assessment agent MUST proactively surface relevant unconsidered needs based on the domain being assessed.

### Retail Banking Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-R-01 | Silent customer churn — customers disengage gradually with no detection | Banks measure churn as account closure, not behavioral disengagement | CAP-R-CL-03, CAP-R-DI-01, CAP-R-AI-01 |
| UN-R-02 | Employee context-switching tax — staff toggle 5+ systems per interaction | Accepted as "how things work," never measured as a cost | CAP-R-CE-02, CAP-R-PO-01 |
| UN-R-03 | No front-to-back journey visibility — process breaks are invisible | Each department sees only their part; no end-to-end view | CAP-R-PO-01, CAP-R-DI-02 |
| UN-R-04 | Data exists but isn't used — customer insights trapped in silos | Banks have data but no intelligence layer to act on it | CAP-R-DI-01, CAP-R-CL-03, CAP-R-AI-02 |
| UN-R-05 | Compliance is cost, not value — KYC/AML treated as overhead, not a trust signal | Banks see compliance as a box-ticking exercise, not a differentiator | CAP-R-RC-01, CAP-R-AI-03 |
| UN-R-06 | No AI strategy — bank has no roadmap for embedding intelligence | AI is either ignored or stuck in pilot purgatory | CAP-R-AI-01, CAP-R-AI-02, CAP-R-AI-03 |

### Wealth Management Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-W-01 | Advisors spend more time on admin than clients | Accepted as normal; never measured as revenue opportunity cost | CAP-W-EE-01, CAP-W-AI-02 |
| UN-W-02 | No proactive life-event detection | Advisors wait for clients to call; missed intervention windows | CAP-W-CL-03, CAP-W-AI-01 |
| UN-W-03 | Client assets leaking to competitors undetected | Transfer patterns to external brokerages not monitored | CAP-W-DI-01, CAP-W-CL-03 |
| UN-W-04 | Referral decay — leads go cold before advisor contact | No urgency scoring; no speed-to-contact measurement | CAP-W-CE-03, CAP-W-PO-01 |
| UN-W-05 | Complexity mismatch — simple clients overserved, complex clients underserved | No systematic matching of client complexity to advisor tier | CAP-W-CL-02, CAP-W-EE-01 |

### SME Banking Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-S-01 | SME treated as "small retail" — no business-specific digital tools | SME is a cost center; investment goes to retail or commercial | CAP-S-CE-01, CAP-S-RB-02 |
| UN-S-02 | Cash flow blindness — business owners can't see forward cash position | Banks provide balances, not forecasts; seen as the business's problem | CAP-S-RB-02, CAP-S-DI-01 |
| UN-S-03 | Onboarding friction kills NTB — 40%+ abandonment on business accounts | Measured by applications started, not by those lost before starting | CAP-S-CL-01, CAP-S-RC-01 |
| UN-S-04 | No cross-sell engine — product penetration is 1.5 products per SME | RMs don't have time or data; digital offers don't exist | CAP-S-CL-03, CAP-S-DI-01, CAP-S-AI-02 |
| UN-S-05 | Lending leakage to fintechs — SMEs get loans elsewhere because bank is too slow | Banks track declined applications but not "never applied because too slow" | CAP-S-DL-01, CAP-S-PO-01 |
| UN-S-06 | RM model unsustainable — SME RMs carry 200+ relationships with no digital leverage | Accepted as normal; RM workload never quantified against revenue per client | CAP-S-CE-02, CAP-S-AI-02 |

### Commercial Banking Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-C-01 | Onboarding takes weeks/months — clients generate zero revenue during setup | Onboarding seen as compliance necessity, not revenue delay | CAP-C-CL-01, CAP-C-PO-01 |
| UN-C-02 | RM can't see share-of-wallet — no visibility into competitor relationships | No multi-bank data; RM relies on client self-reporting | CAP-C-CE-02, CAP-C-DI-01 |
| UN-C-03 | Payment operations are people-heavy — manual repair rates above 10% | "Payment ops has always been manual" — cost never questioned | CAP-C-PT-01, CAP-C-PO-01 |
| UN-C-04 | Trade finance is paper-based — LCs and BGs still require physical documents | Seen as industry norm; digitization efforts haven't reached trade | CAP-C-TF-01, CAP-C-TF-02 |
| UN-C-05 | Entitlement management is a bottleneck — adding/changing users takes days | Buried in IT tickets; never measured as client experience friction | CAP-C-RC-02, CAP-C-PO-01 |
| UN-C-06 | No self-service for corporate clients — every request goes through the RM | Seen as "high-touch service"; actually a cost and speed bottleneck | CAP-C-CE-01, CAP-C-EE-01 |

### Corporate Banking Unconsidered Needs

| ID | Problem | Why Banks Miss It | Related Capabilities |
|----|---------|-------------------|---------------------|
| UN-CO-01 | Treasury visibility gap — treasurers can't see real-time global positions | Bank provides EOD statements; intraday visibility requires manual aggregation | CAP-CO-RB-01, CAP-CO-RB-02, CAP-CO-INT-02 |
| UN-CO-02 | Integration onboarding costs more than the product margin in year 1 | Integration is "the client's problem"; bank doesn't track onboarding cost | CAP-CO-INT-01, CAP-CO-CL-01 |
| UN-CO-03 | Compliance screening false positives consume analyst capacity | High false positive rates accepted as "the cost of compliance" | CAP-CO-RC-02, CAP-CO-AI-01 |
| UN-CO-04 | No predictive treasury — liquidity management is reactive, not anticipatory | Seen as the treasurer's job, not a bank service opportunity | CAP-CO-RB-02, CAP-CO-AI-01 |
| UN-CO-05 | Multi-bank experience is fragmented — clients manage each bank separately | Banks don't incentivize multi-bank views; locks out competitor visibility | CAP-CO-INT-02, CAP-CO-DI-01 |
| UN-CO-06 | Cross-border payment costs are opaque — clients can't compare corridor costs | Fee transparency seen as margin risk; actually a trust and retention issue | CAP-CO-PT-02, CAP-CO-PT-01 |

---

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

## Part 10: Corporate Banking Capability Catalog

*Corporate banking serves the largest and most complex clients — multinationals, financial institutions, sovereigns. Treasury sophistication is high, integration requirements are deep (ERP/TMS/SWIFT), and client expectations for real-time, multi-bank visibility set the bar. Shares many capabilities with Commercial but at greater scale, complexity, and integration depth.*

### Domain: Customer Lifecycle Management (Corporate)
*BIAN: Customer Management → Customer Onboarding*

#### CAP-CO-CL-01: Corporate Client Onboarding
**Description:** Multi-country, multi-entity onboarding for large corporate and multinational clients — complex KYC, legal entity hierarchies, system integration, and user provisioning at scale.

**Front Layer:**
- Digital onboarding portal (client + RM-facing)
- Global entity hierarchy builder
- Multi-country document management
- Onboarding milestone tracker with workstream view

**Middle Layer:**
- Multi-workstream onboarding orchestration (KYC, legal, integration, provisioning in parallel)
- Cross-border KYC coordination
- Multi-country regulatory requirement management
- UAT orchestration and go-live readiness scoring
- Hypercare workflow and issue tracking

**Back Layer:**
- Multi-country company registry integration
- KYC/AML vendor integration (multi-jurisdiction)
- Core banking account creation (multi-entity, multi-currency)
- ERP/TMS integration setup
- SWIFT connectivity and testing

**Probing Questions:**
1. Can any part of the corporate onboarding process be initiated or tracked digitally? *(0→1)*
2. Is the onboarding process standardized with parallel workstreams, defined milestones, and cross-border KYC coordination? *(1→2)*
3. Is onboarding orchestrated end-to-end with automated workstream dependencies, UAT management, and STP for standard entity types? *(2→3)*
4. Does AI predict onboarding timelines, auto-classify cross-border documents, or coordinate multi-jurisdiction KYC autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Risk, Compliance & Security (Corporate)
*BIAN: Risk & Compliance*

#### CAP-CO-RC-01: Corporate KYC/KYB (Complex Entities)
**Description:** KYC/KYB for multinational corporate clients — complex ownership chains, multi-jurisdiction compliance, and enhanced due diligence.

**Front Layer:**
- Global entity structure declaration portal
- Multi-tier beneficial ownership documentation
- EDD document submission
- Review status tracker

**Middle Layer:**
- Multi-jurisdiction KYC orchestration
- Complex beneficial owner chain resolution (10+ levels)
- Enhanced due diligence (EDD) workflow for high-risk entities
- Cross-border regulatory mapping
- Continuous monitoring across jurisdictions

**Back Layer:**
- Multi-country company registry integration
- Multi-vendor KYC integration (jurisdiction-specific)
- Global sanctions and PEP screening
- Regulatory reporting (country-specific)
- Document archive and chain of custody

**Probing Questions:**
1. Is KYC for complex corporate entities (multi-level ownership, multi-jurisdiction) managed digitally? *(0→1)*
2. Is the KYC process standardized with cross-border coordination, EDD protocols, and defined review cycles? *(1→2)*
3. Is KYC orchestrated with automated multi-jurisdiction screening, risk-based review triggers, and centralized oversight? *(2→3)*
4. Does AI resolve complex ownership chains, predict regulatory changes, or perform continuous entity risk assessment across jurisdictions? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-CO-RC-02: Transaction Compliance Screening
**Description:** Real-time compliance screening for corporate transactions — sanctions, embargo, dual-use goods, and counter-terrorism financing.

**Front Layer:**
- Compliance alert dashboard
- Hit resolution interface for analysts
- Screening report generation

**Middle Layer:**
- Real-time transaction screening engine
- Hit scoring and prioritization
- Resolution workflow (auto-clear, review, escalate)
- False positive management
- Regulatory reporting automation

**Back Layer:**
- Sanctions and watch list management
- Transaction monitoring system
- Payment network compliance integration
- Regulatory reporting systems
- Audit trail and evidence management

**Probing Questions:**
1. Is transaction screening performed for all relevant payment and trade flows? *(0→1)*
2. Is screening standardized with defined hit resolution workflows, analyst tools, and SLA tracking? *(1→2)*
3. Is screening real-time with automated scoring, prioritized hit queues, and STP for clear transactions? *(2→3)*
4. Does AI auto-resolve false positives, predict new risk patterns, or adapt screening rules based on evolving typologies? *(3→4)*

**Expected Maturity Hypothesis:** 2

---

### Domain: Corporate Banking Services
*BIAN: Products → Commercial/Corporate Banking*

#### CAP-CO-RB-01: Global Cash Management & Multi-Entity
**Description:** Global cash position management across countries, currencies, entities, and banks — pooling, sweeping, concentration, and intercompany funding.

**Front Layer:**
- Global cash position dashboard (multi-bank, multi-currency)
- Entity hierarchy and account structure visualization
- Intercompany funding request interface
- Cash forecast dashboard with scenario modeling

**Middle Layer:**
- Cross-bank position aggregation
- Multi-currency pooling and conversion logic
- Automated sweeping and concentration rules
- Intercompany loan accounting
- Cash forecast engine (scenario-based)

**Back Layer:**
- Multi-bank connectivity (SWIFT, APIs, screen scraping)
- Core banking (multi-entity, multi-currency ledger)
- FX engine
- Cash pooling system
- Multi-bank statement aggregation (MT940, CAMT.053)

**Probing Questions:**
1. Can corporate clients view consolidated global cash positions across entities and banks digitally? *(0→1)*
2. Are cash management structures (multi-bank pooling, cross-currency sweeping, intercompany funding) configurable through the portal? *(1→2)*
3. Is cash management automated with real-time multi-bank aggregation, automated sweeps, and intraday position updates? *(2→3)*
4. Does AI optimize global cash positions, predict liquidity needs across time zones, and auto-execute intercompany funding? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-CO-RB-02: Liquidity Management
**Description:** Intraday and end-of-day liquidity monitoring, forecasting, and optimization — regulatory (LCR/NSFR) and operational.

**Front Layer:**
- Intraday liquidity dashboard
- LCR/NSFR monitoring view
- Liquidity stress test interface
- Regulatory report generation

**Middle Layer:**
- Intraday liquidity calculation engine
- Liquidity forecast model
- Stress testing scenarios
- Buffer management logic
- Regulatory ratio calculation (LCR, NSFR)

**Back Layer:**
- Real-time payment flow data
- Core banking balance feeds
- Money market system integration
- Central bank reporting
- Historical flow data warehouse

**Probing Questions:**
1. Does intraday liquidity monitoring exist beyond end-of-day balance reports? *(0→1)*
2. Is liquidity monitoring standardized with defined metrics, regulatory ratios, and regular forecasting? *(1→2)*
3. Is liquidity monitored in real-time with automated stress testing, buffer management, and regulatory reporting? *(2→3)*
4. Does AI predict intraday liquidity patterns, optimize buffer allocation, and auto-execute funding actions? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Payments (Corporate)
*BIAN: Operations & Execution → Payment Execution*

#### CAP-CO-PT-01: Corporate Payments
**Description:** High-value, time-critical, and bulk payment processing with complex approval chains, compliance screening, and multi-entity authorization.

**Front Layer:**
- Payment initiation (single, bulk, file-based)
- Complex approval workflows (entity-level, amount-based)
- Real-time payment tracker
- Payment file upload/download (pain.001, MT101)

**Middle Layer:**
- Multi-entity approval engine
- Payment routing optimization (cost, speed, compliance)
- Real-time compliance screening integration
- Cut-off management across time zones
- Exception handling and repair workflows

**Back Layer:**
- SWIFT connectivity (FIN, gpi)
- Payment network integration (local and cross-border)
- Core banking posting (multi-entity)
- Reconciliation engine
- Nostro/vostro management

**Probing Questions:**
1. Can corporate clients initiate high-value payments digitally with multi-entity approval chains? *(0→1)*
2. Are payment workflows configurable per entity with file-based processing, template management, and compliance pre-screening? *(1→2)*
3. Are payments processed with real-time compliance screening, gpi tracking, and automated reconciliation? *(2→3)*
4. Does AI optimize payment routing across corridors, predict settlement timing, or detect anomalous payment patterns? *(3→4)*

**Expected Maturity Hypothesis:** 2

---

#### CAP-CO-PT-02: Cross-Border Payments & FX
**Description:** International payment processing with FX conversion, regulatory compliance, and transparent pricing.

**Front Layer:**
- Cross-border payment initiation with FX rate display
- Beneficiary management (international)
- Payment tracking (SWIFT gpi)
- FX rate locking and comparison

**Middle Layer:**
- FX rate engine and auto-conversion
- Cross-border routing optimization
- Multi-currency compliance screening
- Correspondent bank selection
- Fee transparency and total cost calculation

**Back Layer:**
- SWIFT gpi connectivity
- FX dealing system
- Correspondent banking network
- Sanctions screening (multi-jurisdiction)
- Nostro management and reconciliation

**Probing Questions:**
1. Can corporate clients initiate cross-border payments with FX conversion digitally? *(0→1)*
2. Is cross-border payment processing standardized with transparent FX pricing, compliance screening, and beneficiary validation? *(1→2)*
3. Are cross-border payments processed with real-time FX, gpi tracking, and automated nostro reconciliation? *(2→3)*
4. Does AI optimize FX timing, predict correspondent delays, or route payments for cost/speed optimization? *(3→4)*

**Expected Maturity Hypothesis:** 2

---

### Domain: Trade Finance (Corporate)
*BIAN: Products → Trade Finance*

#### CAP-CO-TF-01: Trade Finance (Corporate)
*Same structure as CAP-C-TF-01 but at multinational scale — multi-country LC/BG programs, global trade limits, cross-border documentary compliance.*

**Probing Questions:**
1. Can corporate clients initiate trade finance requests through a digital channel? *(0→1)*
2. Is trade finance processing standardized with multi-country program support and defined SLAs? *(1→2)*
3. Is trade processing automated with global limit management, STP for standard documents, and real-time status tracking? *(2→3)*
4. Does AI perform cross-border document compliance checking, predict trade flow patterns, or auto-handle routine amendments? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-CO-TF-02: Supply Chain Finance (Corporate)
*Same structure as CAP-C-TF-02 at enterprise scale — multi-program management, global supplier networks, integration with procurement systems.*

**Expected Maturity Hypothesis:** 0

---

### Domain: Integration (Corporate)
*Beyond BIAN — critical for corporate banking differentiation*

#### CAP-CO-INT-01: ERP/TMS Integration
**Description:** Seamless connectivity between the bank's platform and corporate clients' ERP and Treasury Management Systems.

**Front Layer:**
- API developer portal
- Integration documentation and SDKs
- Testing sandbox
- Integration health dashboard

**Middle Layer:**
- API orchestration and transformation layer
- File format conversion (SAP iDoc, Oracle format, generic CSV/XML)
- Connectivity monitoring and alerting
- Version management and backward compatibility
- Rate limiting and SLA management

**Back Layer:**
- API gateway
- ERP connectors (SAP, Oracle, Microsoft Dynamics)
- TMS connectors (Kyriba, ION, FIS)
- Message transformation engine
- Integration logging and audit

**Probing Questions:**
1. Does the bank offer API or file-based connectivity for corporate clients' ERP/TMS systems? *(0→1)*
2. Are integrations standardized with documented APIs, pre-built connectors, and a testing environment? *(1→2)*
3. Are integrations real-time, monitored, with automated alerting, and self-service onboarding for new connectors? *(2→3)*
4. Does an intelligent integration layer auto-detect data format changes, self-heal connectivity issues, or optimize data flow patterns? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

#### CAP-CO-INT-02: Multi-Bank Connectivity
**Description:** Aggregated multi-bank experience — viewing balances, initiating payments, and reconciling across multiple banking relationships.

**Front Layer:**
- Multi-bank balance dashboard
- Unified payment initiation across banks
- Multi-bank statement reconciliation view
- Bank relationship comparison

**Middle Layer:**
- Multi-bank aggregation engine
- Statement normalization and mapping
- Cross-bank payment routing
- Multi-bank reconciliation rules

**Back Layer:**
- SWIFT connectivity (MT940, CAMT.053)
- Open banking APIs (where available)
- Screen scraping / proprietary bank connectors
- Statement storage and archival

**Probing Questions:**
1. Can corporate clients view balances from multiple banks in a single interface? *(0→1)*
2. Is multi-bank data normalized and presented consistently with standardized formats? *(1→2)*
3. Is multi-bank connectivity real-time with automated reconciliation and unified payment initiation? *(2→3)*
4. Does AI optimize which bank to route payments through, predict balance movements across banks, or recommend relationship consolidation? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Process Orchestration (Corporate)

#### CAP-CO-PO-01: Corporate Workflow Management
*Same structure as CAP-C-PO-01 at enterprise scale — multi-country onboarding coordination, cross-border trade workflows, global payment operations.*

**Probing Questions:**
1. Are key corporate processes managed through a workflow tool? *(0→1)*
2. Is there a standardized BPM engine with defined SLAs for corporate operations? *(1→2)*
3. Are corporate workflows orchestrated end-to-end with cross-country coordination, automated handoffs, and real-time monitoring? *(2→3)*
4. Does AI optimize global workflow routing across time zones, predict delays, or handle cross-border exceptions autonomously? *(3→4)*

**Expected Maturity Hypothesis:** 1

---

### Domain: Data & Intelligence (Corporate)

#### CAP-CO-DI-01: Corporate Data Foundation
*Same structure as CAP-R-DI-01 with emphasis on multi-entity data hierarchies, multi-bank data aggregation, trade data, treasury analytics, and global cash flow data.*

**Probing Questions:**
1. Is corporate client data centralized or siloed across country/product systems? *(0→1)*
2. Is there a defined data architecture for corporate data (global entity hierarchies, multi-bank data, trade flows)? *(1→2)*
3. Is corporate data available in real-time for global treasury views, credit monitoring, and RM analytics? *(2→3)*
4. Does a data fabric power global treasury intelligence, cross-entity analytics, and AI-driven corporate insights? *(3→4)*

**Expected Maturity Hypothesis:** 0

---

### Domain: AI & Agentic (Corporate)

#### CAP-CO-AI-01: Treasury Intelligence & Predictive Analytics
**Description:** AI-driven treasury insights — cash flow prediction, liquidity optimization, FX exposure analysis, and anomaly detection.

**Front Layer:**
- Predictive cash flow dashboard
- FX exposure visualization
- Anomaly alerts and recommendations
- Scenario planning interface

**Middle Layer:**
- Cash flow prediction models (ML-based)
- FX exposure analysis engine
- Anomaly detection (payment patterns, balance deviations)
- Scenario simulation engine
- Recommendation generation

**Back Layer:**
- Historical cash flow data
- Market data feeds (FX rates, interest rates)
- ML model training and deployment
- Model governance and versioning
- Feature engineering pipeline

**Probing Questions:**
1. Does any predictive analytics capability exist for treasury operations? *(0→1)*
2. Are forecasting models defined and regularly run (even if manual/spreadsheet-based)? *(1→2)*
3. Are ML models in production for cash flow prediction, FX exposure, or anomaly detection with automated alerting? *(2→3)*
4. Does AI autonomously optimize treasury operations — auto-executing funding, hedging FX, and managing liquidity in real-time? *(3→4)*

**Expected Maturity Hypothesis:** 0

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
