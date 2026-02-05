# Retail Banking Journey Maps

## Journey Mapping Methodology

### End-to-End Journey Analysis (Channel to Back Office)

Every journey should be mapped using swimlane diagrams that show:

1. **Actors/Swimlanes:**
   - Customer/Prospect
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
   - Customer friction (customer pain points)
   - System friction (integration issues)

4. **Front / Middle / Back Layer Indicators:**
   Each journey step involves one or more architectural layers:
   - **Front Layer** (Experience Plane): What the customer or employee sees and interacts with
   - **Middle Layer** (Capability Plane): What orchestrates, decides, and controls behind the scenes
   - **Back Layer** (Integration Plane + Systems of Record): What connects, stores, and processes

5. **Problem Statement Linkage:**
   Each journey links to problems (considered + unconsidered) and capabilities:
   - **Problem IDs**: CN-XX (considered needs), UN-XX (unconsidered needs)
   - **Capability IDs**: CAP-R-XX-NN from `knowledge/standards/capability_taxonomy.md`
   - **Strategic Theme**: Which business objective this journey serves (Acquire/Activate/Expand/Retain)

---

## Customer Acquisition Journeys

### J1: Account Opening Journey (Digital + Branch)

**Lifecycle Stage:** Acquire
**Strategic Theme:** Reduce acquisition cost, improve conversion
**Linked Capabilities:** CAP-R-CL-01 (Digital Onboarding), CAP-R-RC-01 (KYC/AML), CAP-R-PO-01 (Workflow & BPM)
**Linked Problems:** [Map during assessment — e.g., CN-01: Slow onboarding, UN-R-03: No front-to-back visibility]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Research & Apply | Website, mobile app, branch UI | Application workflow, feature flagging | API gateway, session management |
| Document Collection | Upload UI, camera capture, branch scanner | OCR validation, document classification, workflow routing | Document management system, KYC vendor integration |
| Processing | Status tracking in app | Decision engine (auto-approve/refer/decline), STP rules | Core banking account creation, AML screening, credit bureau |
| Activation | Welcome experience, digital card | Notification orchestration, activation workflow | Card processor, core posting, regulatory reporting |

#### Current State Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Research & Apply │ Document Collection │ Processing │ Activation │ Funding │
├───────────────┼──────────────────┼────────────────────┼────────────┼────────────┼─────────┤
│ CUSTOMER      │ ○ Searches online│ ○ Uploads documents│ ○ Waits    │ ○ Receives │○ Funds  │
│               │   5-10 min       │   10-30 min        │   2-5 days │   welcome  │  account│
│               │ ○ Starts app     │ ○ Visits branch if │            │   pack     │         │
│               │   15-20 min      │   docs rejected    │            │   5 min    │  5 min  │
├───────────────┼──────────────────┼────────────────────┼────────────┼────────────┼─────────┤
│ FRONTLINE     │ ○ N/A (digital)  │ ○ Helps with docs  │ ○ Checks   │ ○ Sends    │         │
│ (Branch/RM)   │   OR             │   if branch visit  │   status   │   welcome  │         │
│               │ ○ Initiates app  │   30-60 min        │   10-20 min│   message  │         │
│               │   if in-branch   │                    │   per day  │            │         │
│               │   20-30 min      │                    │            │            │         │
├───────────────┼──────────────────┼────────────────────┼────────────┼────────────┼─────────┤
│ BACK OFFICE   │                  │ ○ Reviews docs     │ ○ Creates  │ ○ Generates│         │
│               │                  │   manually         │   account  │   card     │         │
│               │                  │   15-30 min/app    │   in core  │   request  │         │
│               │                  │ ○ Requests re-     │   10-15 min│   5 min    │         │
│               │                  │   submission if    │            │            │         │
│               │                  │   issues           │            │            │         │
│               │                  │   10-20 min        │            │            │         │
├───────────────┼──────────────────┼────────────────────┼────────────┼────────────┼─────────┤
│ COMPLIANCE    │                  │ ○ KYC verification │            │            │         │
│               │                  │   20-30 min/app    │            │            │         │
│               │                  │ ○ AML screening    │            │            │         │
│               │                  │   5-10 min/app     │            │            │         │
└───────────────┴──────────────────┴────────────────────┴────────────┴────────────┴─────────┘
```

**Applications Involved:**
- Customer: Mobile App, Website, Branch systems
- Frontline: CRM, Core Banking (view only), Document scanner
- Back Office: Core Banking, Document Management System, KYC platform
- Compliance: AML system, ID verification platform

**Key Friction Points:**

| Friction Type | Description | Impact | Evidence |
|--------------|-------------|--------|----------|
| Customer | Document upload failures, unclear requirements | High drop-off (30-50%) | E1, E2 |
| Customer | No visibility into application status | Increased call center load | E3 |
| Employee | Manual document review process | 15-30 min per application | E4 |
| Employee | Re-keying data from paper forms | 10-15 min per application | E5 |
| System | No straight-through processing | 2-5 day cycle time | E6 |
| System | Multiple system logins required | Staff inefficiency | E7 |

**Backbase-Enabled Future State:**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Apply & Verify (Digital)│ Processing (Automated) │ Activation │
├───────────────┼─────────────────────────┼───────────────────────┼────────────┤
│ CUSTOMER      │ ○ Guided onboarding     │ ○ Real-time status    │ ○ Instant  │
│               │   flow with ID&V        │   tracking in app     │   card     │
│               │   8-12 min              │   N/A (automated)     │   3-5 min  │
├───────────────┼─────────────────────────┼───────────────────────┼────────────┤
│ SYSTEM        │ ○ Digital ID verify     │ ○ Auto-decisioning    │ ○ Digital  │
│ (Backbase)    │   <1 min                │   for low-risk        │   card     │
│               │ ○ Doc OCR & validation  │   <1 min              │   instant  │
│               │   <1 min                │ ○ Account creation    │            │
│               │ ○ AML screening         │   <1 min              │            │
│               │   <1 min                │                       │            │
├───────────────┼─────────────────────────┼───────────────────────┼────────────┤
│ BACK OFFICE   │ ○ Exception handling    │ ○ Exception handling  │            │
│               │   only (10% of apps)    │   only                │            │
│               │   15-20 min             │   15-20 min           │            │
└───────────────┴─────────────────────────┴───────────────────────┴────────────┘
```

**Target Metrics:**
- Time to open: <15 minutes (from 2-5 days)
- Completion rate: >80% (from 50-60%)
- Straight-through rate: >70%
- Staff time per app: <5 min avg (from 60+ min)

---

### J2: Card Acquisition Journey

**Lifecycle Stage:** Acquire
**Strategic Theme:** Reduce card-to-hand time, improve activation rates
**Linked Capabilities:** CAP-R-RB-02 (Card Management), CAP-R-DL-01 (Consumer Loan Origination — if credit card), CAP-R-RC-01 (KYC/AML)
**Linked Problems:** [Map during assessment]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Application | Online/branch application form | Application workflow, eligibility rules | CRM, core banking |
| Verification | Document upload UI | Verification workflow, income validation | Credit bureau, document management |
| Decisioning | Decision notification | Credit scoring engine, underwriting rules | Risk scoring system, regulatory reporting |
| Production | Tracking UI | Card lifecycle orchestration | Card processor, payment network (Visa/MC) |
| Activation | Digital activation, wallet provisioning | Activation workflow, PIN management | Card processor, digital wallet API |

#### Current State Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Application │ Verification │ Decisioning │ Production │ Activation │
├───────────────┼─────────────┼──────────────┼─────────────┼────────────┼────────────┤
│ CUSTOMER      │ ○ Applies   │ ○ Provides   │ ○ Waits     │ ○ Receives │ ○ Activates│
│               │   online/   │   income     │   2-7 days  │   card     │   card     │
│               │   branch    │   docs       │             │   5-7 days │   5-10 min │
│               │   10-20 min │   15-30 min  │             │   delivery │            │
├───────────────┼─────────────┼──────────────┼─────────────┼────────────┼────────────┤
│ FRONTLINE     │ ○ Assists   │ ○ Collects   │ ○ Communicates│           │ ○ Assists  │
│               │   if branch │   docs       │   decision  │            │   if needed│
│               │   15-20 min │   10-15 min  │   5-10 min  │            │   5-10 min │
├───────────────┼─────────────┼──────────────┼─────────────┼────────────┼────────────┤
│ BACK OFFICE   │             │ ○ Verifies   │             │ ○ Produces │            │
│               │             │   documents  │             │   card     │            │
│               │             │   20-30 min  │             │   2-3 days │            │
├───────────────┼─────────────┼──────────────┼─────────────┼────────────┼────────────┤
│ CREDIT/RISK   │             │              │ ○ Credit    │            │            │
│               │             │              │   decisioning│           │            │
│               │             │              │   30-60 min │            │            │
│               │             │              │   per app   │            │            │
└───────────────┴─────────────┴──────────────┴─────────────┴────────────┴────────────┘
```

---

## Servicing Journeys

### J3: Money Movement Journey (Transfers & Payments)

**Lifecycle Stage:** Activate / Expand
**Strategic Theme:** Reduce cost-to-serve, improve digital adoption
**Linked Capabilities:** CAP-R-PT-01 (Domestic Payments), CAP-R-CE-01 (Digital Channel Availability)
**Linked Problems:** [Map during assessment]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Initiate | Mobile/web payment form, beneficiary picker | Payment type routing, limits checking | API gateway, account inquiry |
| Authorize | OTP/biometric, step-up authentication | Fraud rules, authorization logic | Authentication service, fraud detection |
| Process | Loading/confirmation screen | Payment orchestration, scheduling, STP rules | Payment network (ACH/RTP/SEPA), core posting, AML screening |
| Confirm | Receipt, notification | Notification engine, reconciliation | Core banking confirmation, regulatory reporting |

#### Current State Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Initiate │ Authorize │ Process │ Confirm │
├───────────────┼──────────┼───────────┼─────────┼─────────┤
│ CUSTOMER      │ ○ Logs in│ ○ Enters  │ ○ Waits │ ○ Checks│
│ (Digital)     │   to app │   OTP     │   (varies│  status │
│               │   1-2 min│   1-2 min │   by type)│  1 min │
├───────────────┼──────────┼───────────┼─────────┼─────────┤
│ CUSTOMER      │ ○ Visits │ ○ Signs   │ ○ Waits │ ○ Receives│
│ (Branch)      │   branch │   form    │   1-3 days│ SMS    │
│               │   20-30  │   5-10 min│         │  N/A    │
│               │   min    │           │         │         │
│               │   wait   │           │         │         │
├───────────────┼──────────┼───────────┼─────────┼─────────┤
│ BACK OFFICE   │          │           │ ○ Manual│         │
│               │          │           │   release│        │
│               │          │           │   for high│        │
│               │          │           │   value  │        │
│               │          │           │   5-15 min│       │
└───────────────┴──────────┴───────────┴─────────┴─────────┘
```

**Applications Involved:**
- Customer: Mobile Banking App, Internet Banking
- Branch: Core Banking Terminal, Payment Gateway
- Back Office: Core Banking, Payment Hub, SWIFT/RTGS

**Friction Points:**

| Channel | Friction | Impact |
|---------|----------|--------|
| Digital | Multiple OTPs for single transaction | Customer frustration |
| Digital | Limited international transfer capability | Lost revenue |
| Branch | Paper forms required for high-value | Staff time, errors |
| Branch | Long queue times for simple transactions | Customer dissatisfaction |

---

### J4: Issue Resolution / Dispute Journey

**Lifecycle Stage:** Retain
**Strategic Theme:** Reduce cost-to-serve, improve customer satisfaction
**Linked Capabilities:** CAP-R-EE-01 (Case Management), CAP-R-CE-02 (Employee Workspace), CAP-R-CE-03 (Contact Center), CAP-R-AI-01 (Conversational AI)
**Linked Problems:** [Map during assessment — e.g., UN-R-02: Employee context-switching tax]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Report Issue | Mobile/web dispute form, call center | Case creation, classification, routing | Case management system, CRM |
| Investigation | Status tracking for customer, case workspace for staff | Investigation workflow, evidence collection, SLA monitoring | Transaction systems, fraud detection, correspondence |
| Resolution | Resolution notification | Resolution workflow, refund orchestration, approval rules | Core banking adjustment, regulatory complaint tracking |
| Communication | In-app notification, email/SMS | Notification orchestration | Correspondence system, audit trail |

#### Current State Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Report Issue │ Investigation │ Resolution │ Communication │
├───────────────┼──────────────┼───────────────┼────────────┼───────────────┤
│ CUSTOMER      │ ○ Calls CC or│ ○ Provides    │ ○ Waits    │ ○ Receives    │
│               │   visits     │   evidence    │   5-30 days│   outcome     │
│               │   branch     │   if requested│            │   notification│
│               │   15-30 min  │   varies      │            │               │
├───────────────┼──────────────┼───────────────┼────────────┼───────────────┤
│ CALL CENTER   │ ○ Logs case  │ ○ Escalates   │            │ ○ Calls to    │
│               │   10-15 min  │   to relevant │            │   communicate │
│               │              │   team        │            │   outcome     │
│               │              │   5 min       │            │   5-10 min    │
├───────────────┼──────────────┼───────────────┼────────────┼───────────────┤
│ BACK OFFICE   │              │ ○ Investigates│ ○ Processes│               │
│               │              │   case        │   refund/  │               │
│               │              │   30-60 min   │   adjustment│              │
│               │              │               │   15-30 min│               │
├───────────────┼──────────────┼───────────────┼────────────┼───────────────┤
│ COMPLIANCE    │              │ ○ Reviews     │ ○ Approves │               │
│               │              │   for fraud   │   if high  │               │
│               │              │   15-30 min   │   value    │               │
│               │              │               │   10-15 min│               │
└───────────────┴──────────────┴───────────────┴────────────┴───────────────┘
```

---

## Servicing Task Analysis

### Summary Table: Time per Servicing Task

| Servicing Task | Yearly Volume | Branch Time (hrs) | Call Center Time (hrs) | Back Office Time (hrs) | Backbase Impact | Linked Capabilities |
|---------------|---------------|-------------------|----------------------|----------------------|-----------------|---------------------|
| Balance Inquiry | 500,000 | 0.08 | 0.08 | - | 70% ↓ | CAP-R-RB-01, CAP-R-CE-01 |
| Statement Request | 200,000 | 0.17 | 0.17 | - | 80% ↓ | CAP-R-RB-01, CAP-R-CE-01 |
| Card Block/Unblock | 50,000 | 0.17 | 0.08 | - | 90% ↓ | CAP-R-RB-02, CAP-R-CE-01 |
| PIN Reset | 30,000 | 0.25 | 0.17 | - | 80% ↓ | CAP-R-RB-02, CAP-R-CE-01 |
| Address/Details Change | 100,000 | 0.25 | 0.17 | 0.17 | 50% ↓ | CAP-R-CL-02, CAP-R-PO-01 |
| Transaction Dispute | 20,000 | 0.33 | 0.25 | 0.75 | 30% ↓ | CAP-R-EE-01, CAP-R-CE-02 |
| Standing Order Setup | 40,000 | 0.25 | 0.17 | - | 70% ↓ | CAP-R-PT-01, CAP-R-CE-01 |
| Cheque Book Request | 25,000 | 0.17 | 0.08 | 0.08 | 80% ↓ | CAP-R-RB-01, CAP-R-CE-01 |
| Loan Inquiry | 80,000 | 0.33 | 0.25 | - | 40% ↓ | CAP-R-DL-01, CAP-R-AI-01 |
| Account Closure | 15,000 | 0.50 | - | 0.33 | 20% ↓ | CAP-R-CL-01, CAP-R-PO-01 |
| Beneficiary Management | 60,000 | 0.17 | 0.08 | - | 70% ↓ | CAP-R-PT-01, CAP-R-CE-01 |
| Direct Debit Management | 45,000 | 0.17 | 0.08 | 0.08 | 60% ↓ | CAP-R-PT-01, CAP-R-PO-01 |
| Travel Notification | 35,000 | 0.08 | 0.08 | - | 90% ↓ | CAP-R-RB-02, CAP-R-CE-01 |
| Limit Increase Request | 40,000 | 0.25 | 0.17 | 0.17 | 50% ↓ | CAP-R-RB-02, CAP-R-DL-01 |
| KYC Periodic Review | 20,000 | 0.50 | - | 0.75 | 40% ↓ | CAP-R-RC-01, CAP-R-PO-01 |
| Loan Modification/Forbearance | 10,000 | 0.50 | 0.25 | 0.50 | 25% ↓ | CAP-R-DL-01, CAP-R-PO-01 |

### Regional Servicing Variations

Volumes and task types vary by market. The assessment agent should adapt based on the client's region:

#### US Market
| Regional Task | Description | Linked Capabilities |
|--------------|-------------|---------------------|
| Mobile Check Deposit | Remote deposit capture via mobile camera | CAP-R-CE-01, CAP-R-PT-01 |
| Zelle / P2P Disputes | Real-time payment disputes (Reg E) | CAP-R-EE-01, CAP-R-PT-01 |
| Wire Transfer Requests | Domestic/international wire initiation | CAP-R-PT-01, CAP-R-RC-01 |
| Tax Form Requests (1099/W-9) | Year-end tax document generation and delivery | CAP-R-DI-02, CAP-R-CE-01 |
| Overdraft Protection Management | Opt-in/opt-out, linked account setup | CAP-R-RB-01, CAP-R-CE-01 |
| ACH Dispute / Return | ACH origination disputes and returns | CAP-R-EE-01, CAP-R-PT-01 |
| eStatement Enrollment | Paper-to-digital statement migration | CAP-R-RB-01, CAP-R-CE-01 |

**US-Specific Regulatory Context:** Reg E (electronic transfers), Reg CC (check holds), TILA (lending disclosures), CRA (community reinvestment), Dodd-Frank, CFPB oversight. Assessment should check for compliance automation maturity.

#### EMEA Market
| Regional Task | Description | Linked Capabilities |
|--------------|-------------|---------------------|
| SEPA Direct Debit Management | Mandate management, R-transactions | CAP-R-PT-01, CAP-R-PO-01 |
| Open Banking Consent Management | PSD2/AISP/PISP consent lifecycle | CAP-R-RC-01, CAP-R-CE-01 |
| Verification of Payee | Confirmation of payee before payment execution | CAP-R-PT-01, CAP-R-RC-01 |
| GDPR Data Requests (SAR/DSAR) | Subject access requests, right to erasure | CAP-R-CL-02, CAP-R-RC-01 |
| Instant Payment (SCT Inst / Faster Payments) | Real-time payment with immediate confirmation | CAP-R-PT-01 |

**EMEA-Specific Regulatory Context:** PSD2/PSD3 (open banking), GDPR (data protection), DORA (digital resilience), MiCA (crypto). Assessment should check for open banking readiness and consent management.

#### APAC Market
| Regional Task | Description | Linked Capabilities |
|--------------|-------------|---------------------|
| QR Payment Setup | PayNow/PromptPay/UPI QR code generation | CAP-R-PT-01, CAP-R-CE-01 |
| E-Wallet Linkage | Link/delink digital wallets (GoPay, GrabPay, etc.) | CAP-R-PT-01, CAP-R-CE-01 |
| Mobile Number Transfer | Transfer money by mobile number (UPI, PayNow) | CAP-R-PT-01 |
| Remittance Services | Cross-border worker remittances | CAP-R-PT-01, CAP-R-RC-01 |

**APAC-Specific Context:** Mobile-first markets, QR payment adoption high, super-app integration common, varying KYC regimes. Assessment should check for mobile-first readiness and real-time payment support.

#### LATAM Market
| Regional Task | Description | Linked Capabilities |
|--------------|-------------|---------------------|
| Pix Payments (Brazil) | Instant payment system management | CAP-R-PT-01 |
| Boleto Management (Brazil) | Boleto issuance and tracking | CAP-R-PT-01, CAP-R-RB-01 |
| Currency Controls | FX and remittance regulatory compliance | CAP-R-PT-01, CAP-R-RC-01 |

---

## Cross-Sell & Expansion Journeys

### J5: Cross-Sell / Product Expansion Journey

**Lifecycle Stage:** Expand
**Strategic Theme:** Grow share of wallet, increase product penetration
**Linked Capabilities:** CAP-R-CL-03 (Customer Behavioral Insights), CAP-R-DI-01 (Data Foundation), CAP-R-AI-02 (AI Copilots), CAP-R-CE-02 (Employee Workspace)
**Linked Problems:** [Map during assessment — e.g., UN-R-01: Silent churn, UN-R-04: Data exists but isn't used]

**From Seabank engagement:** CLO (Cross-Lending Origination) was the single largest value lever at $7.7M over 5 years, demonstrating that cross-sell is a primary revenue driver when done well.

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Trigger Detection | In-app banner, push notification, RM alert | Propensity model, event detection, next-best-action engine | Customer data, transaction history, behavioral analytics |
| Offer Presentation | Personalized offer in app/web, RM conversation | Offer orchestration, eligibility rules, pricing engine | Product catalog, credit scoring, regulatory rules |
| Application | Pre-filled application form | Application workflow (pre-approved = shortened), cross-product rules | Core banking, credit bureau, document management |
| Fulfillment | Confirmation, product activation | Product activation workflow, welcome sequence | Core banking, card processor, LMS |

---

### J6: Loyalty & Retention Journey

**Lifecycle Stage:** Retain
**Strategic Theme:** Reduce churn, deepen engagement
**Linked Capabilities:** CAP-R-CL-03 (Behavioral Insights), CAP-R-AI-01 (Conversational AI), CAP-R-CE-01 (Digital Channels)
**Linked Problems:** [Map during assessment — e.g., UN-R-01: Silent customer churn]

**From Seabank engagement:** Loyalty & Retention was the second largest value lever at $6.38M over 5 years.

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Engagement Monitoring | Financial wellness dashboard, spending insights | Engagement scoring, churn prediction model | Transaction analytics, behavioral data |
| Proactive Intervention | Personalized nudges, savings goals, rewards | Trigger engine, campaign orchestration, NBO | CRM, marketing automation, loyalty platform |
| Win-Back | Special offer, RM outreach | Win-back workflow, escalation to RM for high-value | CRM, product catalog, core banking |

---

## Journey Mapping Legend

### Actors
- **Customer/Prospect**: End user of banking services
- **Frontline**: Branch staff, Relationship Managers, Call Center agents
- **Back Office**: Operations, Processing, Administration
- **Compliance/Risk**: KYC, AML, Credit, Fraud teams
- **System**: Automated processes, integrations

### Time Notation
- **Active time**: Actual work/engagement time (e.g., "15 min")
- **Elapsed time**: Total calendar time including waits (e.g., "2-3 days")

### Friction Indicators
- 🔴 **High**: Significant customer/employee impact, major cost/risk
- 🟡 **Medium**: Moderate impact, improvement opportunity
- 🟢 **Low**: Minor friction, optimization opportunity

### Impact Categories
- **Revenue**: Lost sales, reduced conversion, missed cross-sell
- **Cost**: Staff time, rework, manual processing
- **Risk**: Compliance exposure, error rates, fraud vulnerability
- **Experience**: NPS impact, complaints, churn risk
