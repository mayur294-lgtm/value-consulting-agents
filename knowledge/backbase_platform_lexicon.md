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

The Backbase platform orchestrates the entire customer lifecycle:

| Stage | Description | Platform Quadrant |
|-------|-------------|-------------------|
| **Acquire** | Attract and convert prospects | Onboarding & Origination |
| **Activate** | Enable and engage new customers | Digital Banking |
| **Expand** | Grow share of wallet | Engagement & Expansion |
| **Retain** | Prevent churn and deepen loyalty | Human Assist |

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

---

## Part 2: Platform Architecture

### Architecture Layers

The Backbase platform is organized into three primary planes:

#### 1. Experience Plane (System of Engagement)
Customer-facing and employee-facing interfaces:

| Component | Description |
|-----------|-------------|
| **Customer Apps** | Online & Mobile Banking Applications |
| **Employee Workspaces** | CSR, RM/Advisor, Operations workspaces |
| **Prospect Portal** | Pre-customer engagement |
| **Broker Workspace** | Third-party partner access |
| **Agentic AI** | AI-powered assistants and agents |

#### 2. Capability Plane (System of Intelligence)
The intelligence and orchestration layer:

| Component | Description |
|-----------|-------------|
| **HELIX (Customer Brain)** | Unified frontline control plane - single source of truth |
| **Customer State Graph** | Real-time customer truth across channels & systems |
| **Semantic Banking Ontology** | Shared language for every system & model |
| **Entitlements & Policies** | Access control and business rules |
| **Events & Actions** | What can be done exposed to every UI and AI |
| **Business Process Orchestration** | Front-to-back workflow coordination |
| **Data Foundation** | Unified data lakehouse and management |

#### 3. Integration Plane (System of Integration)
Connectivity to systems of record:

| Component | Description |
|-----------|-------------|
| **Grand Central** | Integration Platform-as-a-Service (iPaaS) |
| **Unified Domain Model** | Standardized data model across integrations |
| **API Management** | API gateway and management |
| **100+ Connectors** | Pre-built integrations to core systems, CRM, payments, fintech |
| **Fintech Marketplace** | Ecosystem of partner integrations |

### HELIX - The Customer Brain (2026+)

HELIX is the central intelligence layer that governs frontline operations:

**Core Components:**

| Layer | Function |
|-------|----------|
| **Semantic Banking Ontology** | Shared language for every system & model |
| **Shared Customer State Graph** | One real-time truth across channels & systems |
| **Action & Behavior Layer** | Exposes "what can be done" to every UI and AI |
| **Agentic Intelligence Layer** | Real-time decisions, recommendations, automation |
| **Trust & Control Layer** | Policy enforcement, audit, secure orchestration |
| **Unified Journeys & Workflows** | Consistent operations across channels & systems |

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

### Zero Trust AI Architecture

| Component | Function |
|-----------|----------|
| Guardrails | Input/output validation and safety |
| Human in the Loop | Approval workflows for sensitive actions |
| Evaluate Agents | Quality and safety testing |
| AI Gateway | Centralized AI access control |
| Explainability | Audit trails and reasoning transparency |
| Observability | Monitoring and alerting |

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
| **CLO** | Customer Lifecycle Orchestration |
| **CPS** | Customer Profile Service |
| **CSR** | Customer Service Representative |
| **EBP** | Engagement Banking Platform |
| **FTE** | Full-Time Equivalent |
| **HELIX** | Backbase's Customer Brain - unified frontline control plane |
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
| **Grand Central** | Backbase integration platform (iPaaS) |
| **Flow Foundation** | Low-code journey orchestration engine |
| **Data Fabric** | Unified data layer for reporting, analytics, AI |
| **Unified Frontline** | Vision of single customer operating system |
| **Customer Brain** | HELIX - intelligence layer for customer lifecycle |
| **Semantic Banking Ontology** | Standardized banking domain model |
| **Customer State Graph** | Real-time customer data across all systems |

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

### High-Level Platform Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    EXPERIENCE PLANE                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Customer   │ │  Employee   │ │      Agentic AI         ││
│  │    Apps     │ │ Workspaces  │ │                         ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│                    CAPABILITY PLANE                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    HELIX                                 ││
│  │  Customer State Graph | Ontology | Events & Actions     ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Banking Microservices | Process Orchestration          ││
│  │  Identity & Entitlements | Data Foundation              ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│                    INTEGRATION PLANE                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              GRAND CENTRAL                               ││
│  │  Unified APIs | Connectors | Fintech Marketplace        ││
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
