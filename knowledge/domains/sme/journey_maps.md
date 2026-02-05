# SME Banking Journey Maps

## Journey Mapping Methodology

### End-to-End Journey Analysis (Channel to Back Office)

Every journey should be mapped using swimlane diagrams that show:

1. **Actors/Swimlanes:**
   - Business Owner / Finance Manager
   - Frontline Staff (RM, Branch Officer, Call Center)
   - Back Office / Operations
   - Compliance / Risk
   - Systems (automated steps)

2. **For Each Step:**
   - Time duration (active time AND elapsed time)
   - Applications/Systems involved
   - Handoff points between actors

3. **Friction Points:**
   - Employee friction (staff pain points)
   - Customer friction (business owner pain points)
   - System friction (integration issues)

4. **Front / Middle / Back Layer Indicators:**
   Each journey step involves one or more architectural layers:
   - **Front Layer** (Experience Plane): What the business owner or employee sees and interacts with
   - **Middle Layer** (Capability Plane): What orchestrates, decides, and controls behind the scenes
   - **Back Layer** (Integration Plane + Systems of Record): What connects, stores, and processes

5. **Problem Statement Linkage:**
   Each journey links to problems (considered + unconsidered) and capabilities:
   - **Problem IDs**: CN-XX (considered needs), UN-XX (unconsidered needs)
   - **Capability IDs**: CAP-S-XX-NN from `knowledge/standards/capability_taxonomy.md`
   - **Strategic Theme**: Which business objective this journey serves (Acquire/Activate/Expand/Retain)

---

## Acquisition Journeys

### J1: Business Account Opening Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Acquire
**Strategic Theme:** Reduce onboarding time, improve conversion
**Linked Capabilities:** [CAP-S-CL-01: Digital Onboarding (SME), CAP-S-RC-01: KYC/KYB]
**Linked Problems:** [Map during assessment]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Business Registration | Online application, document upload | Application workflow, business verification | Company registry API, core banking |
| Research Banks | Website, comparison tools | Product recommendation engine | Product catalog |
| Apply Online | Digital application form | KYB workflow, eligibility rules | Core banking, credit bureau |
| KYC/KYB | Document upload, beneficial owner forms | KYC/KYB orchestration, risk scoring | KYC/AML vendor, sanctions screening |
| Account Active | Welcome dashboard | Account activation workflow | Core banking, card processor |
| First Transaction | Mobile/web banking | Payment orchestration | Payment network, core posting |

```
[Business Registration] → [Research Banks] → [Apply Online] → [KYC/KYB] → [Account Active] → [Card/Access] → [First Transaction]
```

**Current State Pain Points:**
- [TO BE POPULATED from discovery]

**Backbase-Enabled Future State:**
- [TO BE POPULATED]

**Key Metrics:**
- Time to account
- Documents required
- Abandonment rate

---

### J2: SME Loan Application Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Acquire / Expand
**Strategic Theme:** Faster time-to-funding, improve pull-through
**Linked Capabilities:** [CAP-S-DL-01: Business Loan Origination, CAP-S-RC-01: KYC/KYB]
**Linked Problems:** [Map during assessment]

```
[Cash Need] → [Check Eligibility] → [Apply] → [Provide Docs] → [Decision] → [Accept Terms] → [Disbursement]
```

---

## Daily Banking Journeys

### J3: Cash Flow Management Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate / Expand
**Strategic Theme:** Improve digital engagement, reduce branch dependency
**Linked Capabilities:** [CAP-S-RB-01: Business Account Management, CAP-S-DI-01: Data Foundation]
**Linked Problems:** [Map during assessment]

```
[Login] → [View Balance] → [Check Incoming] → [Plan Payments] → [Execute] → [Reconcile]
```

---

### J4: Invoice & Receivables Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Enable SME productivity tools, differentiate
**Linked Capabilities:** [CAP-S-RB-02: Invoicing & Expense, CAP-S-PT-01: Payments]
**Linked Problems:** [Map during assessment]

```
[Create Invoice] → [Send] → [Track] → [Receive Payment] → [Reconcile] → [Report]
```

---

### J5: Supplier Payment Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Reduce cost-to-serve, improve STP
**Linked Capabilities:** [CAP-S-PT-01: Payments, CAP-S-PO-01: Workflow]
**Linked Problems:** [Map during assessment]

```
[Receive Invoice] → [Approve] → [Schedule] → [Pay] → [Confirm] → [Reconcile]
```

---

## Growth Journeys

### J6: Credit Line Increase Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Expand
**Strategic Theme:** Grow share of wallet
**Linked Capabilities:** [CAP-S-DL-01: Business Loan Origination]
**Linked Problems:** [Map during assessment]

### J7: Additional Product (Card/Merchant) Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Expand
**Strategic Theme:** Product penetration
**Linked Capabilities:** [CAP-S-RB-03: Card & Merchant Services, CAP-S-CL-03: Cross-sell]
**Linked Problems:** [Map during assessment]

---

## Service Journeys

### J8: Support Request Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Retain
**Strategic Theme:** Reduce cost-to-serve, improve satisfaction
**Linked Capabilities:** [CAP-S-EE-01: Case Management, CAP-S-CE-02: Employee Workspace]
**Linked Problems:** [Map during assessment]

---

## Journey Mapping Legend
- **Touchpoints:** Mobile App, Web Portal, Branch, Call Center, RM
- **Pain Points:** Friction, manual steps, delays
- **Opportunities:** Automation, self-service, integration
- **Layer Reference:** Front (Experience Plane) / Middle (Capability Plane) / Back (Integration Plane)
