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

---

## Customer Acquisition Journeys

### J1: Account Opening Journey (Digital + Branch)

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

| Servicing Task | Yearly Volume | Branch Time (hrs) | Call Center Time (hrs) | Back Office Time (hrs) | Backbase Impact |
|---------------|---------------|-------------------|----------------------|----------------------|-----------------|
| Balance Inquiry | 500,000 | 0.08 | 0.08 | - | 70% ↓ |
| Statement Request | 200,000 | 0.17 | 0.17 | - | 80% ↓ |
| Card Block/Unblock | 50,000 | 0.17 | 0.08 | - | 90% ↓ |
| PIN Reset | 30,000 | 0.25 | 0.17 | - | 80% ↓ |
| Address/Details Change | 100,000 | 0.25 | 0.17 | 0.17 | 50% ↓ |
| Transaction Dispute | 20,000 | 0.33 | 0.25 | 0.75 | 30% ↓ |
| Standing Order Setup | 40,000 | 0.25 | 0.17 | - | 70% ↓ |
| Cheque Book Request | 25,000 | 0.17 | 0.08 | 0.08 | 80% ↓ |
| Loan Inquiry | 80,000 | 0.33 | 0.25 | - | 40% ↓ |
| Account Closure | 15,000 | 0.50 | - | 0.33 | 20% ↓ |

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
