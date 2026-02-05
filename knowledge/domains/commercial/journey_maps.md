# Commercial Banking Journey Maps

## Journey Mapping Methodology

### End-to-End Journey Analysis (Channel to Back Office)

Every journey should be mapped using swimlane diagrams that show:

1. **Actors/Swimlanes:**
   - Corporate Client (Treasurer/CFO/Finance Manager)
   - Relationship Manager
   - Operations / Trade Finance Team
   - Compliance / Risk
   - Systems (automated steps)

2. **For Each Step:**
   - Time duration (active time AND elapsed time)
   - Applications/Systems involved
   - Handoff points between actors

3. **Friction Points:**
   - Employee friction (staff pain points)
   - Customer friction (client pain points)
   - System friction (integration issues)

4. **Front / Middle / Back Layer Indicators:**
   Each journey step involves one or more architectural layers:
   - **Front Layer** (Experience Plane): What the client or employee sees and interacts with
   - **Middle Layer** (Capability Plane): What orchestrates, decides, and controls behind the scenes
   - **Back Layer** (Integration Plane + Systems of Record): What connects, stores, and processes

5. **Problem Statement Linkage:**
   Each journey links to problems (considered + unconsidered) and capabilities:
   - **Problem IDs**: CN-XX (considered needs), UN-XX (unconsidered needs)
   - **Capability IDs**: CAP-C-XX-NN from `knowledge/standards/capability_taxonomy.md`
   - **Strategic Theme**: Which business objective this journey serves (Acquire/Activate/Expand/Retain)

---

## Client Acquisition Journeys

### J1: Commercial Client Onboarding Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Acquire
**Strategic Theme:** Reduce onboarding time, improve client experience
**Linked Capabilities:** [CAP-C-CL-01: Commercial Client Onboarding, CAP-C-RC-01: KYC/KYB, CAP-C-PO-01: Workflow]
**Linked Problems:** [Map during assessment]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Sales Handoff | RM workspace, opportunity details | Lead-to-onboard handoff workflow | CRM, core banking |
| KYC/KYB | Document portal, entity structure forms | KYC/KYB orchestration, beneficial owner validation | KYC vendor, company registry, AML screening |
| Legal/Docs | Digital contract review, eSignature | Contract workflow, approval routing | Document management, legal systems |
| Account Setup | Client portal preview | Account hierarchy creation, entitlement setup | Core banking, multi-entity management |
| User Provisioning | Admin portal | Role/permission provisioning, multi-signer setup | Identity management, core banking |
| Integration | API onboarding portal | Integration testing, connectivity validation | ERP connectors, SWIFT, host-to-host |
| Go-Live | Client dashboard | Activation workflow, welcome sequence | All systems — production switch |

```
[Sales Handoff] → [KYC/KYB] → [Legal/Docs] → [Account Setup] → [User Provisioning] → [Integration] → [Go-Live]
```

**Current State Pain Points:**
- [TO BE POPULATED from discovery]

**Backbase-Enabled Future State:**
- [TO BE POPULATED]

**Key Metrics:**
- Time to onboard (weeks)
- Documents required
- Manual touchpoints
- Client effort score

---

### J2: Credit/Lending Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Acquire / Expand
**Strategic Theme:** Faster time-to-funding, improve pull-through
**Linked Capabilities:** [CAP-C-DL-01: Commercial Lending, CAP-C-RC-01: KYC/KYB]
**Linked Problems:** [Map during assessment]

```
[Need] → [Request] → [Analysis] → [Proposal] → [Negotiation] → [Documentation] → [Drawdown] → [Monitor]
```

---

## Day-to-Day Operations Journeys

### J3: Cash Position & Forecasting Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Improve treasury visibility, reduce manual reconciliation
**Linked Capabilities:** [CAP-C-RB-01: Cash Management, CAP-C-DI-01: Data Foundation]
**Linked Problems:** [Map during assessment]

```
[Login] → [View Positions] → [Consolidate] → [Forecast] → [Decide] → [Execute] → [Report]
```

---

### J4: Payment Initiation Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Improve STP, reduce manual payment processing
**Linked Capabilities:** [CAP-C-PT-01: Commercial Payments, CAP-C-PO-01: Workflow]
**Linked Problems:** [Map during assessment]

```
[Create/Upload] → [Validate] → [Approve (Multi-level)] → [Submit] → [Track] → [Reconcile]
```

---

### J5: User Administration Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Enable client self-service, reduce admin overhead
**Linked Capabilities:** [CAP-C-CE-01: Client Portal, CAP-C-RC-02: Entitlements]
**Linked Problems:** [Map during assessment]

```
[Request] → [Approve] → [Provision] → [Train] → [Monitor] → [Audit]
```

---

## Trade & Supply Chain Journeys

### J6: Trade Finance Journey (LC/BG)
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Expand
**Strategic Theme:** Digitize trade, reduce paper processing
**Linked Capabilities:** [CAP-C-TF-01: Trade Finance, CAP-C-PO-01: Workflow]
**Linked Problems:** [Map during assessment]

### J7: Supply Chain Finance Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Expand
**Strategic Theme:** Enable supply chain financing, grow revenue
**Linked Capabilities:** [CAP-C-TF-02: Supply Chain Finance]
**Linked Problems:** [Map during assessment]

---

## Service Journeys

### J8: Issue Resolution Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Retain
**Strategic Theme:** Reduce cost-to-serve, improve resolution time
**Linked Capabilities:** [CAP-C-EE-01: Case Management, CAP-C-CE-02: RM Workspace]
**Linked Problems:** [Map during assessment]

### J9: Relationship Review Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Retain / Expand
**Strategic Theme:** Deepen relationship, grow share of wallet
**Linked Capabilities:** [CAP-C-CE-02: RM Workspace, CAP-C-DI-01: Data Foundation, CAP-C-AI-02: AI Copilots]
**Linked Problems:** [Map during assessment]

---

## Journey Mapping Legend
- **Touchpoints:** Portal, Mobile, RM, Operations, API
- **Approval Workflows:** Multi-level, limits-based
- **Integration Points:** ERP, TMS, Core Banking
- **Layer Reference:** Front (Experience Plane) / Middle (Capability Plane) / Back (Integration Plane)
