# Backbase Platform Lexicon & Architecture Reference

A comprehensive reference guide for Backbase terminology, platform architecture, and product capabilities. This document serves as the authoritative source for Value Consulting engagements.

---

## Part 1: Strategic Framework

### The Unified Frontline Vision

**Core Problem: Frontline Fragmentation**
Banks typically operate 20-40 disconnected apps, workflows, and tools creating:
- No shared customer truth across channels
- Long fulfillment times (days/weeks instead of minutes/hours)
- Manual steps everywhere driving high cost-to-serve
- Employees juggling multiple screens and systems
- Inconsistent customer experience across channels
- AI stuck in pilots with no orchestration layer

**Solution: Unified Frontline**
A single customer operating system that transforms fragmented frontline systems into a connected growth engine.

### Customer Lifecycle Model

The Backbase platform orchestrates the entire customer lifecycle through four stages. Each stage spans multiple product lines — the quadrant mapping below shows the *primary* quadrant, but products from all quadrants participate in every stage.

| Stage | Definition | Primary Quadrant | What This Stage Covers |
|-------|-----------|------------------|----------------------|
| **Acquire** | Attract prospects, convert them into customers, and complete their onboarding | Onboarding & Origination | Prospecting, lead management, marketing, application, origination, KYC/onboarding, account creation, initial product setup |
| **Activate** | Enable customers to use the platform for daily banking and complete their first key transactions | Digital Banking | Account activation, first transaction, digital channel adoption, daily banking operations (payments, transfers, cash management), initial product usage |
| **Expand** | Grow share of wallet through cross-sell, upsell, and proactive engagement based on customer needs | Engagement & Expansion | Cross-sell/upsell origination, next best action, pre-approved offers, product bundling, engagement campaigns, life-event triggers, AUM growth (wealth) |
| **Retain** | Reduce cost-to-serve through self-service, resolve issues efficiently, and prevent churn through proactive engagement | Human Assist + Digital Banking | Self-service operations, issue resolution, dispute management, portfolio reviews, proactive retention, loyalty programs, churn prediction, cost-to-serve optimization |

### The Unified Banking Suite (Four Quadrants)

```
         ┌─────────────────┬─────────────────┐
         │   Onboarding    │     Digital     │
acquire→ │  & Origination  │    Banking      │ →activate
         ├─────────────────┼─────────────────┤
         │  Engagement     │     Human       │
expand←  │  & Expansion    │     Assist      │ ←retain
         └─────────────────┴─────────────────┘
```

> **Note:** The quadrant model shows primary associations. In practice, Digital Banking serves Activate, Expand, AND Retain (self-service). Human Assist participates in Expand (RM-driven cross-sell) as well as Retain. Engagement & Expansion drives Retain (proactive retention) as well as Expand. The lifecycle stages are *customer outcome-oriented*; the quadrants are *platform architecture-oriented*.

### Lifecycle Stage → Product Lines & Solution Components

#### ACQUIRE — Convert Prospects to Customers

| Product Line | Solution Components | What It Does in This Stage |
|-------------|-------------------|---------------------------|
| **Digital Onboarding** | Guided Application Flow, Document Upload & OCR, eIDV (Jumio/Onfido), AML Screening, Decision Engine (auto-approve/refer/decline), eSignature, Welcome Experience | End-to-end digital account opening with straight-through processing for low-risk applicants |
| **Digital Lending** | Loan Application Flow, Income Verification, Credit Decisioning, Offer Presentation, Loan Booking | Origination of credit products (personal loans, mortgages, credit cards, business loans, credit facilities) |
| **Flow Foundation** | Journey Orchestrator, Form Builder, Business Rules Engine | Low-code configuration of acquisition journeys and business rules |
| **Platform Identity** | Biometric Enrollment, FIDO2/Passkeys, Device Registration | Secure identity establishment during onboarding |
| **Grand Central** | Core Banking Connectors, KYC/AML Vendor Connectors, Credit Bureau Connectors, Company Registry APIs | Integration to systems of record for account creation, verification, and decisioning |
| **Digital Engage** | Campaign Orchestration, Prospect Portal, Lead Capture Forms | Pre-acquisition marketing and prospect engagement |
| **Digital Assist** | RM/Advisor Workspace (Lead Management, Pipeline Visibility, Referral Tracking, Event Manager) | Employee-side tools for prospecting, lead tracking, and onboarding support |

**Domain Variations:**
- **Retail:** Focus on self-service digital onboarding with high STP rates. Key metric: time-to-account, completion rate.
- **Wealth:** RM-assisted hybrid onboarding. Prospect Lounge for self-qualification. Key metric: lead conversion, onboarding TAT.
- **SME:** Business account opening with KYB (beneficial owners, company structure). Key metric: time-to-account, documents required.
- **Commercial:** Complex multi-entity onboarding with user provisioning, entitlements, and system integration (ERP/TMS). Key metric: weeks to go-live.

#### ACTIVATE — Get Customers Transacting

| Product Line | Solution Components | What It Does in This Stage |
|-------------|-------------------|---------------------------|
| **Digital Banking - Retail** | Account Dashboard, Transaction History, Payments (P2P, Bill Pay, Transfers), Card Activation, Card Controls, Notifications, Statements | Core daily banking experience that drives digital adoption |
| **Digital Banking - Business** | Cash Position Dashboard, Payment Initiation (Bulk/Single), Beneficiary Management, User Administration, Multi-Entity Views, Reconciliation | Business banking operations that replace branch/manual processes |
| **Digital Invest** | Portfolio Overview, First Investment Flow, Market Data, Order Execution | Investment platform activation (wealth clients) |
| **Platform Identity** | Biometric Login, Step-Up Authentication, Device Management, Session Management | Secure, frictionless access to banking services |
| **Digital Engage** | Welcome Journey, Onboarding Nudges, Feature Discovery, Push Notifications | Guided activation sequence to drive feature adoption |
| **Grand Central** | Payment Network Connectors (ACH/RTP/SEPA/Faster Payments), Card Processor Connectors | Integration to payment rails and card processors for transaction execution |

**Domain Variations:**
- **Retail:** Mobile-first experience. Key metric: digital adoption rate, active users, transactions per user.
- **Wealth:** First investment / portfolio setup. Key metric: time to first trade, AUM activation rate.
- **SME:** Cash flow management, first invoice, first payment. Key metric: digital payment adoption, monthly active users.
- **Commercial:** Cash visibility, payment operations, user provisioning. Key metric: payment STP rate, digital vs. manual ratio.

#### EXPAND — Grow Share of Wallet

| Product Line | Solution Components | What It Does in This Stage |
|-------------|-------------------|---------------------------|
| **Digital Lending** | Pre-Approved Offers, Cross-Lending Origination (CLO), Limit Increase Flow, Product Bundling | New product origination for existing customers with pre-filled data and shortened workflows |
| **Digital Engage** | Next Best Action (NBA) Engine, Engagement Scoring, Campaign Orchestration, Life-Event Triggers, Behavioral Nudges | Proactive, data-driven engagement to drive cross-sell at the right moment |
| **Digital Invest** | Portfolio Expansion, New Fund Subscription, Robo-Advisory, Goal-Based Investing | Wealth product expansion and AUM growth |
| **Data Foundations** | Customer Behavioral Analytics, Propensity Models, Product Affinity Scoring, Engagement Scoring | Intelligence layer that powers personalized cross-sell and identifies expansion opportunities |
| **Digital Assist** | RM/Advisor Workspace (Client 360, Opportunity Pipeline, Next Best Action Alerts, Pre-Approved Product View) | Employee tools for relationship-driven cross-sell and advisory |
| **Wealth Management** | Advisory Workflow, Investment Proposal, Suitability Assessment, Portfolio Rebalancing | Wealth-specific expansion through advisory and AUM growth |

**Domain Variations:**
- **Retail:** Product cross-sell (savings→loans→cards→investments). Key metric: products per customer, cross-sell conversion. *Seabank example: CLO was the single largest value lever at $7.7M over 5 years.*
- **Wealth:** AUM growth, new asset classes, family wealth. Key metric: NNA (Net New Assets), product penetration.
- **SME:** Credit line increases, merchant services, insurance, trade products. Key metric: revenue per client, product penetration.
- **Commercial:** Trade finance, supply chain finance, FX, structured products. Key metric: fee income, facility utilization.

#### RETAIN — Serve Efficiently and Prevent Churn

| Product Line | Solution Components | What It Does in This Stage |
|-------------|-------------------|---------------------------|
| **Digital Banking - Retail** | Self-Service Hub (Card Block/Unblock, PIN Reset, Address Change, Standing Orders, Statements, Travel Notifications), In-App Support, FAQ/Help | Digital self-service that deflects branch/call center volume and reduces cost-to-serve |
| **Digital Banking - Business** | Self-Service Portal, User Management, Mandate Management, Statement Downloads | Business client self-service that reduces RM/operations overhead |
| **Digital Assist** | CSR Workspace (Customer 360, Case Management, Interaction History, Dispute Handling), RM Workspace (Portfolio Review, Client Health Score, Meeting Prep) | Employee productivity tools for efficient service delivery |
| **Digital Engage** | Retention Campaigns, Churn Risk Alerts, Win-Back Offers, Financial Wellness Nudges, Loyalty Programs | Proactive engagement that prevents silent churn |
| **Data Foundations** | Churn Prediction Models, Customer Health Scoring, Engagement Analytics, Cost-to-Serve Analytics | Intelligence that identifies at-risk customers and measures service efficiency |
| **Wealth Management** | Portfolio Review Automation, Reasons-Why Letter Generation, Suitability Reassessment, Client Reporting | Wealth-specific servicing that shifts RM time from admin to advice |
| **AI & Agentic** | Conversational AI (Chatbot), AI Copilots for CSR/RM, Intelligent Routing, Auto-Resolution | AI-powered service that handles routine queries and assists employees |

**Domain Variations:**
- **Retail:** Self-service digital deflection. Key metric: containment rate, cost-to-serve, NPS. *Target: 20%→60% digital containment.*
- **Wealth:** RM productivity (admin→advice shift). Key metric: non-value task time, review prep time, churn rate. *ISPWM example: 65% non-value time → target 35%.*
- **SME:** Digital self-service + relationship support. Key metric: digital adoption, support ticket volume.
- **Commercial:** Self-service portal + dedicated RM. Key metric: client satisfaction, issue resolution time.

---

## Part 2: Platform Architecture

### Platform Evolution

The Backbase platform has evolved through distinct eras:

| Era | Period | Platform Identity | Key Innovation |
|-----|--------|-------------------|----------------|
| **Bank 2.0 Portal** | 2011-2013 | Widget App Store | Vertical specialization into financial services |
| **CXP** | 2016-2019 | Customer Experience Platform | Omnichannel orchestration |
| **Engagement Banking** | 2022-2023 | Engagement Banking Platform (EBP) | Model Banks, platform economics (€120M funding) |
| **AI-Native** | 2024-2025 | AI-powered Banking Platform | Agentic autonomy, Intelligence Fabric, Agent Studio |
| **Semantic Intelligence** | 2026+ | AI-native Banking Operating System | **NEXUS**, Semantic Fabric, autonomous banking |

### Architecture — Three Fabrics

The current Backbase architecture is organized into **three fabrics** (evolved from the earlier three-plane model):

| Fabric | Assessment Layer | What It Covers | Key Components |
|--------|-----------------|----------------|----------------|
| **Digital Banking Fabric** | **Front Layer** | Customer and employee experiences across channels | Customer Apps (Mobile + Web), Employee Workspaces (CSR, RM/Advisor, Operations), Prospect Portal, AI Co-Pilots, Model Bank Apps |
| **Data + AI Fabric** | **Middle Layer** | Intelligence, orchestration, semantic understanding, and agentic execution | **NEXUS** (Customer State Graph, Semantic Banking Ontology), Agent Studio, Agent Orchestration, Process Automation (Flow), Entitlements & Access Control, Data Foundation, Intelligence Fabric |
| **Integration Fabric** | **Back Layer** | Connectivity to systems of record and third-party services | **Grand Central** (iPaaS), Connector Studio, 100+ Pre-built Connectors, Unified Domain Model, API Management, Fintech Marketplace |

> **Assessment mapping:** For capability assessments, the three fabrics map directly to Front/Middle/Back (F/M/B) scoring layers. The overall capability score = the weakest layer (weakest-link principle).

### Horizontal Service Layers

Across the three fabrics, the platform exposes these horizontal service layers:

| Service Layer | Description | Key Components |
|--------------|-------------|----------------|
| **Presentation Services** | UI frameworks and app shells | Model Bank Apps, AI Co-Pilots, Widget Engine, Design System |
| **Banking Services** | Composable banking microservices | Accounts, Payments, Cards, Lending, Investing |
| **Process Automation Services** | Journey and workflow orchestration | Flow Foundation, Business Rules Engine, Form Builder |
| **Agentic Services** | AI agent development and execution | Agent Studio, Agent Orchestration, Agent Marketplace |
| **Semantic Services** | Customer intelligence and ontology | **NEXUS** — Customer State Graph, Semantic Banking Ontology |
| **Integration Services** | System connectivity | Grand Central, Connector Studio, Unified Domain Model |
| **Entitlements Services** | Access control and permissions | Role-based access, multi-level approvals, limits management |
| **Security Services** | Identity and authentication | Platform Identity, FIDO2, Biometric, Fraud Prevention |
| **Marketplace** | Partner ecosystem | Fintech integrations, add-on connectors |
| **Managed Hosting** | Cloud operations | Banking-as-a-Service (BaaS), cloud infrastructure |
| **Agentic SDLC** | AI-assisted development | Upgrade agents, Knowledge agents (Ask IO), legacy modernization |

### NEXUS — The Semantic Fabric (2026+)

NEXUS is the next evolution of the Customer Brain (previously called HELIX). It provides the semantic intelligence layer that makes autonomous banking possible:

**Core Components:**

| Component | Function |
|-----------|----------|
| **Customer State Graph** | Single real-time truth about every customer — across all channels, products, and systems. This is the "one customer view" that every AI agent and human employee accesses. |
| **Semantic Banking Ontology** | Shared domain language for every system and AI model. Ensures that "savings account" means the same thing to the core banking system, the mobile app, and the AI agent. |
| **Action & Behavior Layer** | Exposes "what can be done" to every UI and AI — a catalog of available actions (open account, make payment, file dispute) that any interface can invoke. |
| **Agentic Intelligence Layer** | Real-time decisioning, recommendations, and automation. Powers next-best-action, risk scoring, churn prediction, and autonomous case handling. |
| **Trust & Control Layer** | Policy enforcement, audit trails, and secure orchestration. Ensures AI agents operate within governance boundaries. |
| **Unified Journeys & Workflows** | Consistent end-to-end operations across channels and systems. A journey started on mobile continues on web, in-branch, or via AI agent with full context. |

> **NEXUS vs. HELIX:** NEXUS is the evolution of the HELIX concept (Customer Brain). While HELIX focused on being a "unified frontline control plane," NEXUS adds the semantic layer that enables true autonomous banking — AI agents that understand banking domain concepts natively.

### Legacy Plane Terminology (for reference)

Earlier Backbase documentation uses a "three plane" model. This maps to the current fabric model:

| Legacy Term | Current Term | Assessment Layer |
|------------|-------------|-----------------|
| Experience Plane (System of Engagement) | Digital Banking Fabric | Front Layer |
| Capability Plane (System of Intelligence) | Data + AI Fabric | Middle Layer |
| Integration Plane (System of Integration) | Integration Fabric | Back Layer |

### Grand Central - Integration Platform

Grand Central provides unified connectivity to:

**System Categories:**
- **Core Systems**: Ledger, Cards, Payments, LMS, Back Office
- **Enablement Systems**: CRM, CDP, KYC, AML, Fraud, Risk Engines, LMS, Decisioning Tools
- **Fintech Ecosystem**: Partner integrations via marketplace

**Core System Connectors:**
| Connector | Region | Description |
|-----------|--------|-------------|
| FiServ DNA | US | Core banking system |
| FiServ Premier | US | Core banking system |
| FiServ Signature | US | Core banking system |
| JackHenry Silverlake | US | Core banking system |
| JackHenry Symitar | US | Credit union core |
| Oracle Flexcube | Global | Universal banking |
| Temenos T24 | Global | Core banking |
| TCS BaNCS | Global | Core banking |
| Mambu | Global | Cloud core |

**KYC/IDV Connectors:**
- Jumio (Global)
- Onfido (Global)
- ComplyAdvantage (AML)
- Smarty (Address validation)
- Prove (US PII validation)

**Payment Connectors:**
- ACH (US)
- Real Time Payments (US)
- Faster Payments (UK)
- CHAPS (UK)
- BACS (UK)
- SEPA (EU)
- Verification of Payee (EU)

---

## Part 3: Product Lines

> **Detailed Feature Reference:** For feature-level product detail (3,117 sub-features with tier availability and platform support), consult `knowledge/domains/Product Directory (1).csv`. The CSV is organized by Journey (e.g., "Payments", "Card Management", "Authentication") and shows each feature's availability across Essential/Premium/Signature tiers and Mobile/Web platforms.

### 13 Product Lines Overview

| Product Line | Description | Primary Value |
|--------------|-------------|---------------|
| **Digital Onboarding** | Customer/business account opening | Reduce acquisition cost, improve conversion |
| **Digital Lending** | Loan origination across products | Faster time-to-funding, higher pull-through |
| **Flow Foundation** | Low-code journey orchestration | Accelerate custom journey development |
| **Digital Banking - Retail** | Consumer banking experience | Mobile-first engagement |
| **Digital Banking - Business** | SME/Commercial banking | Self-service cash management |
| **Digital Investing** | Investment & trading | Enable wealth services |
| **Digital Assist** | Employee workspaces | CSR/RM productivity |
| **Digital Engage** | Communications & marketing | Customer engagement orchestration |
| **Platform Identity** | Authentication & security | FIDO2, biometric, fraud prevention |
| **Developer Platform** | SDK & development tools | Accelerate customization |
| **Grand Central** | Integration platform | Connect to any system |
| **Data Foundations** | Data fabric & analytics | Unified reporting, AI enablement |
| **Wealth Management** | Private banking & advisory | RM productivity, client experience |

### Product Tiers

| Tier | Description |
|------|-------------|
| **Essential** | Core functionality included in base platform |
| **Premium** | Advanced features for differentiated experiences |
| **Signature** | Enterprise-grade capabilities |

### Feature Categories by Journey

**App Foundation:**
- App Shell, Navigation, Dashboard
- Notifications, Search, Accessibility
- Multi-language support

**Authentication:**
- Biometric (Face ID, Touch ID)
- FIDO2/Passkeys
- Step-up authentication
- Device management

**Accounts & Transactions:**
- Account overview, statements
- Transaction search, categorization
- External account aggregation

**Payments:**
- Internal transfers, P2P
- Bill pay, scheduled payments
- International wire transfers
- QR payments (roadmap)

**Card Management:**
- Activate, block, replace
- PIN management
- Spending limits
- Travel notifications

**Financial Insights:**
- Income & expense analysis
- Budgeting tools
- Savings goals
- Financial wellness scores

**Family Banking:**
- Child accounts
- Allowance management
- Parental controls
- Financial education

**Digital Investing:**
- Portfolio overview
- Trading (market orders)
- Investment research
- Robo-advisory integration

---

## Part 4: Employee Workspaces

### Workspace Types

| Workspace | Users | Primary Functions |
|-----------|-------|-------------------|
| **Customer Assist** | Customer Service Representatives | Case management, customer 360, service requests |
| **RM/Advisor** | Relationship Managers, Advisors | Client portfolio, opportunities, onboarding |
| **Operations** | Mid/Back Office | Workflow queues, KYC review, underwriting |
| **Broker** | Third-party partners | Limited customer access |

### Key Capabilities

**Customer 360 View:**
- Unified customer profile
- Product holdings
- Interaction history
- Pending tasks/cases
- Next best actions

**Case Management:**
- Dispute handling
- Service requests
- KYC reviews
- Fraud investigations

**Opportunity Management:**
- Lead tracking
- Pre-approvals
- Cross-sell recommendations
- Pipeline visibility

---

## Part 5: AI & Intelligence

### AI Use Case Categories

| Category | Use Cases |
|----------|-----------|
| **Grow Primacy** | Tailored value propositions, Next best actions, Product holdings, Churn prevention |
| **Customer Engagement** | Holistic advice/coaching, Conversational banking, Employee workspace AI, Financial wellness |
| **Operational Efficiency** | Onboarding automation, Due diligence, Dispute management, Back office productivity |
| **Software Development** | Agentic SDLC, Upgrade agents, Knowledge (Ask IO), Legacy modernization |

### Agentic AI Platform

**Lifecycle Stages:**
1. **Prepare Data, APIs & Models**: Data ingestion, ML Ops, Unified domain APIs
2. **Build Agents**: AI frameworks, Tool catalog (MCP), RAG
3. **Evaluate Agents**: LLM judges, Human annotations, Tracing
4. **Run Agents**: Agent compute, CI/CD, API management
5. **Govern Agents**: AI guardrails, AI Gateway, Red teaming, Observability

### Agentic AI Platform Components

| Component | Description |
|-----------|-------------|
| **Agent Studio** | Development environment for building, testing, and deploying AI agents within the Backbase platform |
| **Agent Orchestration** | Runtime coordination of multiple AI agents working together to complete complex tasks |
| **Agent Marketplace** | Library of pre-built agent templates and partner integrations |
| **MCP (Model Context Protocol)** | Tool catalog standard enabling AI agents to access banking capabilities securely |
| **Intelligence Fabric** | Unified data and intelligence layer that feeds AI models, agents, and decisioning engines |
| **Connector Studio** | Visual integration builder for connecting to external AI services, LLMs, and data sources |
| **Agentic SDLC** | AI-assisted software development lifecycle for building and upgrading Backbase implementations |

### Zero Trust AI Architecture

| Component | Function |
|-----------|----------|
| Guardrails | Input/output validation and safety |
| Human in the Loop | Approval workflows for sensitive actions |
| Evaluate Agents | Quality and safety testing |
| AI Gateway | Centralized AI access control |
| Explainability | Audit trails and reasoning transparency |
| Observability | Monitoring and alerting |
| Red Teaming | Adversarial testing of AI behaviors |
| AI Audit Trail | Complete record of AI decisions and actions for compliance |

---

## Part 6: Value Metrics & ROI Framework

### Typical Business Impact

| Metric | Improvement |
|--------|-------------|
| Customer fulfillment time | 50-90% faster (days/weeks → minutes/hours) |
| Product sales & share of wallet | 2-4x growth |
| Staff productivity | 3x improvement |
| Cost-to-serve | 30-60% reduction |
| Change velocity | 3x faster |

### Value Levers by Category

**Revenue Generation:**
- Customer acquisition improvement
- Loan origination volume
- Cross-sell/upsell conversion
- Fee income growth
- Retention/churn reduction

**Cost Reduction:**
- FTE efficiency gains
- Call/branch deflection
- STP rate improvement
- IT cost reduction
- Process automation

**Risk & Compliance:**
- Fraud reduction
- Compliance efficiency
- Audit trail automation

### ROI Benchmarks (from Engagements)

| Engagement | Investment | Benefits (5yr) | ROI | Payback |
|------------|------------|----------------|-----|---------|
| ISPWM (Luxembourg) | €9.1M | €28.5M | 224% | ~2 years |
| Schroders (UK) | ~£19M | £153M | 8x | ~1.5 years |
| HNB Wealth (Sri Lanka) | $9.6M | $25.7M | 167% | ~2 years |
| Seabank (Philippines) | $11M | $18.3M | 66% | 1.7 years |

---

## Part 7: Implementation Approach

### Progressive Transformation

Backbase advocates a "start small, get a win" approach:

**Phase 1: Unified Front Door**
- Single entry point with entitlements
- Hero journey implementation
- Legacy channel embedding

**Phase 2: Journey Expansion**
- Additional hero journeys
- Progressive legacy replacement
- Cross-segment rollout

**Phase 3: Full Unification**
- Complete journey coverage
- AI enablement
- Full legacy retirement

### IGNITE Workshop Framework

**Business Track:**
- Identify pain points
- Benchmark value drivers
- Map frontline bottlenecks
- Define priority journeys
- Quantify impact (CX, revenue, cost)
- Build business cases

**Technology Track:**
- Assess current architecture
- Map system landscape
- Identify anchor platforms
- Design target architecture
- Define integration strategy
- Set modernization priorities

**Output:**
- Joint, actionable AI-ready roadmap
- Business outcomes + operational improvements + future-proof architecture

---

## Part 8: Segment Solutions

### Consumer/Retail Banking
- Segment-based personalization
- Family banking
- Financial wellness
- Mobile-first experience

### Wealth Management
- Client 360 for advisors
- Digital onboarding
- Portfolio management
- Next-gen wealth transfer

### Small Business Banking
- Fast onboarding
- Invoicing & expense management
- Cash flow forecasting
- Embedded lending

### Commercial Banking
- Treasury management
- Unified payments
- Trade finance
- Multi-entity management

---

## Part 9: Glossary

### Core Terms

| Term | Definition |
|------|------------|
| **AUM** | Assets Under Management |
| **BIAN** | Banking Industry Architecture Network — industry-standard service landscape (~322 service domains). Backbase's capability taxonomy is BIAN-aligned (v13). See `knowledge/standards/capability_taxonomy.md`. |
| **CLO** | (1) Customer Lifecycle Orchestration; (2) Cross-Lending Origination — originating a new lending product for an existing customer using pre-filled data. Context determines meaning. |
| **CPS** | Customer Profile Service |
| **CSR** | Customer Service Representative |
| **EBP** | Engagement Banking Platform |
| **FTE** | Full-Time Equivalent |
| **HELIX** | Legacy name for Backbase's Customer Brain — now evolved into NEXUS |
| **NEXUS** | Backbase's Semantic Fabric (2026+) — Customer State Graph + Semantic Banking Ontology. The intelligence layer enabling autonomous banking. Evolution of HELIX. |
| **NBA** | Next Best Action — AI-driven recommendation of the optimal action for a customer at a given moment |
| **iPaaS** | Integration Platform as a Service |
| **KYB** | Know Your Business |
| **KYC** | Know Your Customer |
| **LOS** | Loan Origination System |
| **MCP** | Model Context Protocol (AI tool catalog) |
| **NNA** | Net New Assets |
| **NPS** | Net Promoter Score |
| **RM** | Relationship Manager |
| **STP** | Straight-Through Processing |
| **TAT** | Turn-Around Time |

### Architecture Terms

| Term | Definition |
|------|------------|
| **Digital Banking Fabric** | Front layer of the three-fabric architecture — customer and employee experiences |
| **Data + AI Fabric** | Middle layer — intelligence, orchestration, NEXUS, Agent Studio, Process Automation |
| **Integration Fabric** | Back layer — Grand Central, connectors, API management |
| **Grand Central** | Backbase integration platform (iPaaS) — industry's first iPaaS designed for banking |
| **Connector Studio** | Visual integration builder enabling non-technical employees to build integrations |
| **Flow Foundation** | Low-code journey orchestration engine |
| **Data Fabric / Data Foundation** | Unified data layer for reporting, analytics, AI |
| **Intelligence Fabric** | AI-ready data and model layer powering agents, decisioning, and intelligence across the platform |
| **Unified Frontline** | Vision of single customer operating system |
| **Customer Brain** | Legacy term for NEXUS/HELIX — intelligence layer for customer lifecycle |
| **Semantic Banking Ontology** | Standardized banking domain model — shared language for every system and AI model |
| **Customer State Graph** | Real-time customer data across all systems — single source of truth |
| **Agent Studio** | Development environment for building and deploying AI agents |
| **Agent Orchestration** | Runtime coordination of multiple AI agents for complex task completion |
| **Agentic SDLC** | AI-assisted software development lifecycle using upgrade agents and knowledge agents |

### Product Terms

| Term | Definition |
|------|------------|
| **Model Bank** | Pre-configured solution for specific segment (Retail, SME, Wealth) |
| **Journey** | End-to-end customer experience flow |
| **Workspace** | Employee-facing application |
| **Widget** | Reusable UI component |
| **Capability** | Platform service or function |
| **Connector** | Pre-built integration to external system |

---

## Part 10: Reference Architecture Diagrams

### High-Level Platform Stack (Three Fabrics)

```
┌─────────────────────────────────────────────────────────────┐
│              DIGITAL BANKING FABRIC (Front Layer)             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Customer   │ │  Employee   │ │    AI Co-Pilots &       ││
│  │    Apps     │ │ Workspaces  │ │    Agentic AI           ││
│  │ (Mobile+Web)│ │ (CSR/RM/Ops)│ │                         ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│              DATA + AI FABRIC (Middle Layer)                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    NEXUS                                  ││
│  │  Customer State Graph | Semantic Ontology | Actions      ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Agent Studio | Flow Engine | Banking Services           ││
│  │  Entitlements | Data Foundation | Intelligence Fabric    ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│              INTEGRATION FABRIC (Back Layer)                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              GRAND CENTRAL                               ││
│  │  Connector Studio | Unified APIs | Fintech Marketplace   ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│                   SYSTEMS OF RECORD                          │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐   │
│  │   Core    │ │    CRM    │ │ Payments  │ │  Fintech  │   │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Front-to-Back Orchestration

```
┌─────────────────────────────────────────────────────────────┐
│ Digital Channels (Primary Interface)                         │
│  ┌─────────┐                           ┌─────────┐          │
│  │ Online  │                           │ Mobile  │          │
│  └────┬────┘                           └────┬────┘          │
├───────┼─────────────────────────────────────┼───────────────┤
│ Front Office (Support, Advice, Sell)        │               │
│  ┌────────────────────┐  ┌──────────────────┴─────────────┐│
│  │ Customer Support   │  │ Relationship Manager / Advisor ││
│  └────────────────────┘  └────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│ Operations (Mid & Back Office)                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │  Customer   │ │   Payment   │ │ Fraud & Fin │ │  Loan  ││
│  │Due Diligence│ │  Disputes   │ │    Crime    │ │Underwrt││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│            AI-ready Banking Platform                         │
└─────────────────────────────────────────────────────────────┘
```

---

*Classification: Internal - Value Consulting Use Only*
*Last Updated: 2026-02-02*
*Version: 1.0*
