# Corporate Banking Journey Maps

## Journey Mapping Methodology

### End-to-End Journey Analysis (Channel to Back Office)

Every journey should be mapped using swimlane diagrams that show:

1. **Actors/Swimlanes:**
   - Corporate Client (Treasurer/CFO/Finance Director)
   - Relationship Manager / Coverage Banker
   - Product Specialist (Trade, Treasury, FX)
   - Operations / Middle Office
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
   - **Capability IDs**: CAP-CO-XX-NN from `knowledge/standards/capability_taxonomy.md`
   - **Strategic Theme**: Which business objective this journey serves (Acquire/Activate/Expand/Retain)

---

## Client Lifecycle Journeys

### J1: Corporate Client Onboarding Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Acquire
**Strategic Theme:** Reduce onboarding time (from months to weeks), improve client experience
**Linked Capabilities:** [CAP-CO-CL-01: Corporate Onboarding, CAP-CO-RC-01: KYC/KYB, CAP-CO-PO-01: Workflow]
**Linked Problems:** [Map during assessment]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| RFP/Selection | Client portal, proposal sharing | Opportunity management, proposal workflow | CRM, product catalog |
| Contract | Digital contract review, eSignature | Contract workflow, multi-party approval | Document management, legal systems |
| Legal/KYC | Document portal, entity hierarchy builder | KYC orchestration, beneficial owner chain, risk scoring | KYC vendor, company registry, AML/sanctions screening |
| Technical Integration | API developer portal, testing sandbox | Integration testing orchestration, connectivity validation | ERP/TMS connectors, SWIFT, host-to-host, API gateway |
| User Setup | Admin portal, role management | Multi-entity user provisioning, entitlement matrix | Identity management, core banking |
| UAT | Client testing environment | Test orchestration, validation checklist | All systems — staging environment |
| Go-Live | Production dashboard | Activation workflow, cutover orchestration | All systems — production switch |
| Hypercare | Support portal, escalation | Hypercare workflow, SLA monitoring | Case management, monitoring |

```
[RFP/Selection] → [Contract] → [Legal/KYC] → [Technical Integration] → [User Setup] → [UAT] → [Go-Live] → [Hypercare]
```

**Current State Pain Points:**
- [TO BE POPULATED from discovery]

**Backbase-Enabled Future State:**
- [TO BE POPULATED]

**Key Metrics:**
- Time to onboard (months)
- Integration effort
- User provisioning time
- Go-live success rate

---

### J2: Subsidiary/Entity Onboarding Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Expand
**Strategic Theme:** Streamline multi-entity management
**Linked Capabilities:** [CAP-CO-CL-01: Corporate Onboarding, CAP-CO-RB-01: Multi-Entity Management]
**Linked Problems:** [Map during assessment]

---

## Treasury Operations Journeys

### J3: Global Cash Visibility Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Real-time global treasury visibility
**Linked Capabilities:** [CAP-CO-RB-01: Cash Management, CAP-CO-DI-01: Data Foundation]
**Linked Problems:** [Map during assessment]

```
[Login] → [Aggregate Positions] → [Multi-bank View] → [Currency Consolidation] → [Report/Decide] → [Act]
```

---

### J4: Intraday Liquidity Management Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Optimize liquidity, reduce idle cash
**Linked Capabilities:** [CAP-CO-RB-02: Liquidity Management, CAP-CO-DI-01: Data Foundation, CAP-CO-AI-01: Predictive Analytics]
**Linked Problems:** [Map during assessment]

```
[Monitor] → [Forecast Flows] → [Identify Gaps] → [Mobilize Liquidity] → [Execute] → [Confirm]
```

---

### J5: Inter-company Funding Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Automate inter-company flows
**Linked Capabilities:** [CAP-CO-PT-01: Corporate Payments, CAP-CO-RB-01: Cash Management]
**Linked Problems:** [Map during assessment]

---

## Payment Journeys

### J6: High-Value Payment Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Reduce payment processing time, improve STP
**Linked Capabilities:** [CAP-CO-PT-01: Corporate Payments, CAP-CO-RC-02: Compliance Screening]
**Linked Problems:** [Map during assessment]

```
[Initiate] → [Validate] → [Multi-Approve] → [Compliance Check] → [Release] → [Track] → [Confirm]
```

---

### J7: Bulk Payment / Treasury Settlement Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Automate bulk processing, reduce manual intervention
**Linked Capabilities:** [CAP-CO-PT-01: Corporate Payments, CAP-CO-PO-01: Workflow]
**Linked Problems:** [Map during assessment]

---

### J8: Cross-Border Payment Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate / Expand
**Strategic Theme:** Reduce cross-border friction, improve transparency
**Linked Capabilities:** [CAP-CO-PT-02: Cross-Border Payments, CAP-CO-RC-02: Compliance Screening]
**Linked Problems:** [Map during assessment]

---

## Trade Finance Journeys

### J9: LC / Documentary Credit Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Expand
**Strategic Theme:** Digitize trade documentation, reduce TAT
**Linked Capabilities:** [CAP-CO-TF-01: Trade Finance, CAP-CO-PO-01: Workflow]
**Linked Problems:** [Map during assessment]

### J10: Supply Chain Finance Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Expand
**Strategic Theme:** Enable supply chain financing, grow revenue
**Linked Capabilities:** [CAP-CO-TF-02: Supply Chain Finance]
**Linked Problems:** [Map during assessment]

---

## Integration Journeys

### J11: ERP/TMS Integration Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Seamless corporate system connectivity
**Linked Capabilities:** [CAP-CO-INT-01: ERP/TMS Integration, CAP-CO-DI-01: Data Foundation]
**Linked Problems:** [Map during assessment]

### J12: Multi-Bank Connectivity Journey
<!-- TO BE POPULATED -->

**Lifecycle Stage:** Activate
**Strategic Theme:** Unified multi-bank experience
**Linked Capabilities:** [CAP-CO-INT-02: Multi-Bank Connectivity]
**Linked Problems:** [Map during assessment]

---

## Journey Mapping Legend
- **Touchpoints:** Portal, API, SWIFT, RM, Operations
- **Compliance Gates:** KYC, AML, Sanctions
- **Integration Points:** ERP, TMS, SWIFT, Core
- **Layer Reference:** Front (Experience Plane) / Middle (Capability Plane) / Back (Integration Plane)
