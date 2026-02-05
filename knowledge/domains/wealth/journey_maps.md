# Wealth Management Journey Maps

## Journey Mapping Methodology

### End-to-End Journey Analysis (Channel to Back Office)

Every journey should be mapped using swimlane diagrams that show:

1. **Actors/Swimlanes:**
   - Prospect/Client
   - Relationship Manager (RM)
   - RM Assistant
   - Back Office / Operations
   - Compliance / Risk

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
   - **Front Layer** (Experience Plane): What the client or RM sees and interacts with
   - **Middle Layer** (Capability Plane): What orchestrates, decides, and controls behind the scenes
   - **Back Layer** (Integration Plane + Systems of Record): What connects, stores, and processes

5. **Problem Statement Linkage:**
   Each journey links to problems (considered + unconsidered) and capabilities:
   - **Problem IDs**: CN-XX (considered needs), UN-XX (unconsidered needs)
   - **Capability IDs**: CAP-W-XX-NN from `knowledge/standards/capability_taxonomy.md`
   - **Strategic Theme**: Which business objective this journey serves (Acquire/Activate/Expand/Retain)

---

## Customer Lifecycle: Acquire → Activate → Expand → Retain

### Summary View

| Stage | Key Journeys | Critical Metrics | Typical Friction |
|-------|-------------|------------------|------------------|
| **Acquire** | Prospecting, Onboarding | Conversion rate, Onboarding TAT | Manual lead tracking, Paper-heavy onboarding |
| **Activate** | First Investment, Early Engagement | Time to first trade, AUM activation | No guided journey, Delayed portfolio setup |
| **Expand** | Cross-sell, Wallet Share Growth | Product penetration, AUM growth | No 360° view, Manual research |
| **Retain** | Servicing, Portfolio Review | NPS, Churn rate, Cost to serve | Fragmented systems, Manual reporting |

---

## Acquire Stage Journeys

### J1: Prospecting - Events

**Lifecycle Stage:** Acquire
**Strategic Theme:** Improve lead conversion, reduce cost of acquisition
**Linked Capabilities:** CAP-W-CE-03 (Referral & Lead Management), CAP-W-CL-03 (Client Behavioral Intelligence), CAP-W-AI-01 (Conversational AI)
**Linked Problems:** [Map during assessment — e.g., UN-W-04: Referral decay]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Pre-Event & Invitation | Email platform, WhatsApp broadcast | Campaign orchestration, target audience selection, compliance review | CRM, client data, marketing automation |
| Event Execution | Event registration, check-in | Attendance tracking, engagement scoring | Event platform, CRM update |
| Post-Event Lead Capture | Lead capture form, RM notification | Lead scoring, auto-assignment, pipeline creation | CRM, core banking (existing client check) |
| Follow-up | RM workspace, communication templates | Follow-up workflow, SLA management, nurture sequencing | CRM, correspondence system, audit trail |

#### Current State Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Pre-Event & Invitation │ Event Execution │ Post-Event Lead Capture │ Follow-up │
├───────────────┼────────────────────────┼─────────────────┼─────────────────────────┼───────────┤
│ PROSPECT/     │                        │ ○ Attends event │ ○ May show interest     │ ○ Engages │
│ CLIENT        │                        │   20-30 per     │   in follow-up          │   with RM │
│               │                        │   event typical │                         │   if      │
│               │                        │   1-2 hours     │                         │   contacted│
├───────────────┼────────────────────────┼─────────────────┼─────────────────────────┼───────────┤
│ RM            │ ○ Defines theme        │ ○ Hosts event   │ ○ Manually tracks       │ ○ Conducts│
│               │   1-2 hours            │   manages leads │   warm leads in         │   pitch   │
│               │ ○ Identifies           │   1-2 hours     │   notebooks/Excel       │   1-2 hrs │
│               │   attendees from       │                 │   30-60 min             │           │
│               │   personal list        │                 │                         │           │
│               │   0.5-1 day            │                 │                         │           │
├───────────────┼────────────────────────┼─────────────────┼─────────────────────────┼───────────┤
│ MARKETING     │ ○ Creates invitations  │                 │                         │           │
│               │   & messaging          │                 │                         │           │
│               │   0.5-1 day            │                 │                         │           │
├───────────────┼────────────────────────┼─────────────────┼─────────────────────────┼───────────┤
│ COMPLIANCE    │ ○ Reviews messaging    │                 │                         │           │
│               │   1-2 hours            │                 │                         │           │
└───────────────┴────────────────────────┴─────────────────┴─────────────────────────┴───────────┘
```

**Applications Involved:**
- RM: RM Portal/CRM, Excel, Personal Notes
- Marketing: Email platform, WhatsApp Broadcast
- Compliance: Document review (manual)
- Lead tracking: Notebooks, Excel, WhatsApp

**Key Friction Points:**

| Friction Type | Description | Impact | Evidence |
|--------------|-------------|--------|----------|
| Employee | Event themes driven by intuition, not data | Suboptimal targeting | E1 |
| Employee | Invitees pulled from Excel/personal lists | High-value clients missed | E2 |
| Employee | No campaign tracking (opens, registrations) | Cannot measure effectiveness | E3 |
| Employee | Warm leads captured in notebooks/WhatsApp | Leads lost, no pipeline visibility | E4 |
| Customer | No structured follow-up journey | Delayed contact, inconsistent experience | E5 |

---

### J2: Prospecting - Referrals

**Lifecycle Stage:** Acquire
**Strategic Theme:** Reduce referral decay, improve speed-to-contact
**Linked Capabilities:** CAP-W-CE-03 (Referral & Lead Management), CAP-W-CE-02 (RM/Advisor Workspace), CAP-W-PO-01 (Workflow & BPM)
**Linked Problems:** [Map during assessment — e.g., UN-W-04: Referral decay, UN-W-01: Advisors spend more time on admin]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Opportunity ID | Branch referral form, RM notification | Referral intake, duplicate check, auto-routing | CRM, core banking (existing relationship check) |
| Lead Qualification | RM workspace with lead details | Lead scoring, qualification rules, SLA triggers | CRM, external data enrichment |
| Lead Management | RM task list, engagement tracker | Nurture workflow, activity tracking | CRM, correspondence, audit trail |
| Conversion | Onboarding initiation in workspace | Conversion workflow, handoff to onboarding | CRM, core banking, KYC systems |

#### Current State Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Opportunity ID │ Lead Qualification │ Lead Management │ Conversion │
├───────────────┼────────────────┼────────────────────┼─────────────────┼────────────┤
│ PROSPECT      │ ○ Referred by  │ ○ Attends periodic │ ○ May have 1-1  │ ○ If interested,│
│               │   existing     │   events           │   meetings/calls│   proceeds to  │
│               │   client       │                    │                 │   onboarding   │
├───────────────┼────────────────┼────────────────────┼─────────────────┼────────────┤
│ RM            │ ○ Identifies   │ ○ Checks for       │ ○ Maintains     │ ○ Makes formal│
│               │   prospect via │   existing HNB     │   relationship  │   pitch       │
│               │   network      │   relationship     │   30-60 min/mo  │   1-2 hours   │
│               │   5-10 min     │   5-10 min         │                 │              │
│               │ ○ Collects     │ ○ Reaches out for  │                 │ ○ Initiates  │
│               │   basic info   │   introduction     │                 │   onboarding │
│               │   in personal  │   5-10 min         │                 │   30-60 min  │
│               │   notes        │                    │                 │              │
│               │   5-10 min     │                    │                 │              │
├───────────────┼────────────────┼────────────────────┼─────────────────┼────────────┤
│ BACK OFFICE   │                │ ○ Checks core      │                 │            │
│               │                │   banking for      │                 │            │
│               │                │   existing rel.    │                 │            │
│               │                │   5-10 min         │                 │            │
└───────────────┴────────────────┴────────────────────┴─────────────────┴────────────┘
```

**Applications Involved:**
- RM: Personal Notes, Excel, WhatsApp, Call, Email
- Back Office: Core Banking (Finacle)
- Engagement: WhatsApp, Call, Email

**Key Friction Points:**

| Friction Type | Description | Impact | Evidence |
|--------------|-------------|--------|----------|
| Employee | Referrals in personal notes/WhatsApp, not CRM | No pipeline visibility | E1 |
| Employee | Manual check for existing relationships | Time wasted, potential duplicates | E2 |
| Employee | No SLA or trigger for quick follow-up | Referred prospects go cold | E3 |
| Employee | Ongoing engagement is opportunistic | No structured nurture | E4 |
| Customer | Same slow onboarding as any other client | Poor experience for warm leads | E5 |

---

### J3: Onboarding - Primarily Existing Customer Upgrade

**Lifecycle Stage:** Acquire / Activate
**Strategic Theme:** Reduce onboarding time, improve client experience
**Linked Capabilities:** CAP-W-CL-01 (Client Onboarding), CAP-W-RC-01 (KYC/AML), CAP-W-PO-01 (Workflow & BPM), CAP-W-CE-02 (RM Workspace)
**Linked Problems:** [Map during assessment — e.g., UN-W-01: Advisors spend more time on admin than clients]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Confirmation | RM workspace — eligibility check | Eligibility rules, AUM threshold validation | Core banking (balance inquiry) |
| Form Filling & Doc Collection | Digital forms (or paper), document upload | Form validation, document classification, pre-fill from existing data | Document management, CRM, core banking |
| Processing | Status tracking (RM view, client view) | KYC workflow, account creation orchestration, STP rules | Core banking, KYC vendor, AML screening, regulatory reporting |
| Audit | RM re-check workspace | Audit workflow, compliance review rules | Document management, compliance systems |
| Activation | Welcome experience, card delivery tracking | Activation workflow, card issuance orchestration | Card processor, core posting, digital wallet |

#### Current State Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Confirmation │ Form Filling & Doc Collection │ Processing │ Audit │ Activation │
├───────────────┼──────────────┼───────────────────────────────┼────────────┼───────┼────────────┤
│ PROSPECT/     │ ○ Eligibility│ ○ Fills paper forms           │ ○ Waits    │ ○ Waits│○ Receives │
│ CLIENT        │   confirmed  │   75-90 min                   │   for      │       │   welcome  │
│               │   AUM > 10M  │ ○ Provides documents          │   processing│      │   pack     │
│               │              │   (may need multiple visits)  │   1-2 days │       │   4-5 days │
├───────────────┼──────────────┼───────────────────────────────┼────────────┼───────┼────────────┤
│ RM            │ ○ Assists    │ ○ Collects documents          │ ○ Checks   │ ○ Re- │ ○ Delivers │
│               │   customer   │   may need multiple           │   status   │ checks│   welcome  │
│               │   with form  │   visits/interactions         │   with BO  │ docs  │   pack     │
│               │   5-10 min   │   depending on complexity     │   40-60 min│ 15-20 │ Up to 3-4  │
│               │              │                               │   total    │ min   │   days     │
├───────────────┼──────────────┼───────────────────────────────┼────────────┼───────┼────────────┤
│ RM ASSISTANT  │              │ ○ Checks forms & documents    │            │       │            │
│               │              │ ○ Updates CBS with mandates   │            │       │            │
│               │              │ ○ Prepares upgrade pack       │            │       │            │
│               │              │   0.5-1 day, 10-20 min active │            │       │            │
├───────────────┼──────────────┼───────────────────────────────┼────────────┼───────┼────────────┤
│ BACK OFFICE   │              │                               │ ○ COD      │ ○ COOD│ ○ Cards    │
│ (COD/COOD)    │              │                               │   receives │ re-   │   dept     │
│               │              │                               │   package  │ checks│   processes│
│               │              │                               │ ○ Checks   │ docs  │   card     │
│               │              │                               │   KYC docs │ 15-30 │   4-5 days │
│               │              │                               │ ○ Creates  │ min   │            │
│               │              │                               │   accounts │       │            │
│               │              │                               │   1-2 days │       │            │
│               │              │                               │   10-20 min│       │            │
│               │              │                               │   active   │       │            │
└───────────────┴──────────────┴───────────────────────────────┴────────────┴───────┴────────────┘
```

**Applications Involved:**
- RM: Core Banking (Finacle), Paper Forms
- RM Assistant: Core Banking, Document Package
- Back Office: Core Banking, Document Management
- Communication: Call, Email, WhatsApp

**Key Friction Points:**

| Friction Type | Description | Impact | Evidence |
|--------------|-------------|--------|----------|
| Employee | Paper-based forms and manual data entry | 3-5 hours per onboarding | E1 |
| Employee | Eligibility not embedded in channels | RM manually checks balances | E2 |
| Employee | Complex cases require multiple visits | Extended cycle times | E3 |
| Employee | RM time on admin vs. advising client | Low productivity | E4 |
| Customer | No digital status tracking | Relies on RM for updates | E5 |
| Customer | Errors discovered late, bounced back | Frustration, delays | E6 |
| System | Multiple teams re-check same documents | Duplication, inefficiency | E7 |

---

## Expand Stage Journeys

### J4: Portfolio Review / Client Servicing

**Lifecycle Stage:** Expand / Retain
**Strategic Theme:** Increase RM productivity, improve client engagement quality
**Linked Capabilities:** CAP-W-WI-01 (Portfolio Management), CAP-W-CE-02 (RM Workspace), CAP-W-DI-01 (Data Foundation), CAP-W-AI-02 (AI Copilots), CAP-W-AI-04 (Advice Copilot)
**Linked Problems:** [Map during assessment — e.g., UN-W-01: Advisors on admin, UN-W-03: Client assets leaking undetected]

#### Front-to-Back Layer View

| Journey Phase | Front Layer | Middle Layer | Back Layer |
|--------------|-------------|-------------|------------|
| Request | Client portal/app, WhatsApp, call | Request routing, SLA trigger | CRM, case management |
| Data Collation | RM workspace with client 360 | Data aggregation from multiple sources, portfolio calculation | Core banking, securities system, insurance system, custody |
| Report Prep | Auto-generated portfolio report | Report engine, performance calculation, benchmark comparison | Data warehouse, analytics engine |
| Client Update | Client portal (self-serve), RM presentation | Meeting scheduling, document sharing, secure messaging | CRM, document management, correspondence |
| Clarifications | Secure messaging, follow-up tracker | Follow-up workflow, action tracking | CRM, case management, audit trail |

#### Current State Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Request │ Data Collation │ Report Prep │ Client Update │ Clarifications │
├───────────────┼─────────┼────────────────┼─────────────┼───────────────┼────────────────┤
│ CLIENT        │ ○ Requests│              │             │ ○ Receives    │ ○ May have     │
│               │   update │               │             │   update via  │   follow-up    │
│               │   5-10 min│              │             │   email/call  │   questions    │
│               │          │               │             │   20-30 min   │   30-60 min    │
├───────────────┼─────────┼────────────────┼─────────────┼───────────────┼────────────────┤
│ RM            │ ○ Receives│ ○ Manually   │ ○ Consoli-  │ ○ Presents to │ ○ Handles      │
│               │   request│   consolidates│   dates in  │   client      │   additional   │
│               │          │   info from   │   Excel/PPT │               │   requests     │
│               │ Often    │   multiple    │   45-60 min │               │   30-60 min    │
│               │ 0.5-1 day│   sources     │   over 0.5- │               │   over 1-2     │
│               │ elapsed  │   20-40 min   │   1 day     │               │   days         │
│               │          │   active      │             │               │                │
├───────────────┼─────────┼────────────────┼─────────────┼───────────────┼────────────────┤
│ RM ASSISTANT  │          │ ○ Helps with  │             │               │                │
│               │          │   data        │             │               │                │
│               │          │   gathering   │             │               │                │
│               │          │   15-25 min   │             │               │                │
├───────────────┼─────────┼────────────────┼─────────────┼───────────────┼────────────────┤
│ BACK OFFICE / │          │ ○ BO provides │             │               │                │
│ SUBSIDIARIES  │          │   statements  │             │               │                │
│ (HNB Securities,│        │ ○ Securities  │             │               │                │
│ HNB Assurance) │         │   advisor for │             │               │                │
│               │          │   stock data  │             │               │                │
│               │          │ ○ Assurance   │             │               │                │
│               │          │   for insurance│            │               │                │
└───────────────┴─────────┴────────────────┴─────────────┴───────────────┴────────────────┘
```

**Applications Involved:**
- Client request: Call, WhatsApp, Email
- Data gathering: Core Banking, Securities systems, Insurance systems
- Communication: Call, WhatsApp, Email
- Output: PDF, Email, WhatsApp message

**Key Friction Points:**

| Friction Type | Description | Impact | Evidence |
|--------------|-------------|--------|----------|
| Employee | 1-2 hours prep for key clients | Time on admin, not advice | E1 |
| Employee | Pull positions from multiple systems | Fragmented data | E2 |
| Employee | Data via email/WhatsApp from teams | Manual reconciliation needed | E3 |
| Customer | Static summaries, quickly outdated | No real-time view | E4 |
| Customer | Follow-up questions = another round | Delayed responses | E5 |

---

## Retain Stage Journeys

### J5: Customer Servicing Summary

**Lifecycle Stage:** Retain
**Strategic Theme:** Reduce cost-to-serve, shift RM time from admin to advice
**Linked Capabilities:** CAP-W-CE-02 (RM Workspace), CAP-W-EE-01 (Advisor Productivity), CAP-W-AI-02 (AI Copilots), CAP-W-AI-04 (Advice Copilot), CAP-W-DI-01 (Data Foundation)
**Linked Problems:** [Map during assessment — e.g., UN-W-01: Admin vs. client time, UN-W-05: Complexity mismatch]

#### Servicing Task Analysis

| Servicing Task | RM Time | RM Asst Time | BO Time | Employee Friction | Customer Friction | Linked Capabilities |
|---------------|---------|--------------|---------|-------------------|-------------------|---------------------|
| **Portfolio Review** | ⬤ High | ⬤ Medium | ⬤ Low | RMs stitch data from multiple systems | No consolidated view | CAP-W-WI-01, CAP-W-DI-01, CAP-W-CE-02 |
| **Relationship Maintenance** | ⬤ High | ⬤ Low | ⬤ Low | Follow-ups rely on RM memory | Inconsistent service | CAP-W-CL-03, CAP-W-CE-02, CAP-W-AI-04 |
| **Sales & Advisory** | ⬤ High | ⬤ Medium | ⬤ Low | Manual research, no digital catalog | Wait for RM suggestions | CAP-W-WI-02, CAP-W-AI-02, CAP-W-CL-03 |
| **Customer Queries** | ⬤ High | ⬤ Medium | ⬤ Low | RMs are first line, no case tracking | No clear route if RM busy | CAP-W-EE-01, CAP-W-AI-01, CAP-W-CE-02 |
| **Transaction Support** | ⬤ Medium | ⬤ High | ⬤ High | Paper mandates, manual checks | Re-sign forms, no visibility | CAP-W-WI-03, CAP-W-PO-01 |
| **Reporting & Statements** | ⬤ High | ⬤ Medium | ⬤ Medium | Manual data pull from multiple systems | Fragmented statements | CAP-W-DI-01, CAP-W-DI-02, CAP-W-CE-01 |
| **Meeting Prep** | ⬤ High | ⬤ Low | ⬤ Low | Significant data collection time | Quality varies by prep time | CAP-W-AI-04, CAP-W-DI-01, CAP-W-CE-02 |
| **Internal Coordination** | ⬤ High | ⬤ Medium | ⬤ Medium | Chase teams via calls/emails | Slow, opaque processes | CAP-W-PO-01, CAP-W-EE-01 |
| **Compliance & Consent** | ⬤ Medium | ⬤ High | ⬤ High | Paper-heavy KYC, repeated rework | Long doc lists, re-submissions | CAP-W-RC-01, CAP-W-CL-01, CAP-W-AI-03 |
| **Wealth Planning / Fact-Finding** | ⬤ High | ⬤ Low | ⬤ Low | 90 min per session (Schroders: 4.5x benchmark) | Manual data entry, delayed plans | CAP-W-WI-02, CAP-W-AI-04, CAP-W-DI-01 |
| **Reasons-Why / Annual Review Letters** | ⬤ High | ⬤ Medium | ⬤ Low | 3 hrs per letter (Schroders: 6x benchmark) | Long wait for documentation | CAP-W-AI-04, CAP-W-AI-02, CAP-W-DI-01 |
| **Corporate Actions Processing** | ⬤ Low | ⬤ Medium | ⬤ High | Manual booking, cross-system reconciliation | No visibility on corporate events | CAP-W-WI-03, CAP-W-PO-01, CAP-W-DI-01 |
| **Trade Execution & Settlement** | ⬤ Medium | ⬤ Medium | ⬤ High | Manual order entry, reconciliation | No self-service trading | CAP-W-WI-03, CAP-W-CE-01 |
| **Suitability Reassessment** | ⬤ Medium | ⬤ High | ⬤ Medium | Periodic review manual and paper-based | Repeated questionnaires | CAP-W-RC-01, CAP-W-CL-02, CAP-W-AI-03 |
| **Fee Disclosure & Reporting** | ⬤ Low | ⬤ Medium | ⬤ High | Fee reports manually compiled | Lack of transparency | CAP-W-DI-02, CAP-W-CE-01 |

Legend: ⬤ High = Significant time/friction | ⬤ Medium = Moderate | ⬤ Low = Minimal

### Engagement Benchmarks (From Past Engagements)

These benchmarks from actual Backbase engagements provide reference points for capability assessment:

| Metric | Schroders (UK) | ISPWM (Luxembourg) | HNB (Sri Lanka) | Goodbody (Ireland) |
|--------|---------------|--------------------|-----------------|--------------------|
| RM effort per onboarding | 4.5 hrs (benchmark: 1 hr) | N/A | 3 hrs | N/A |
| Ops effort per onboarding | 5 hrs (benchmark: 1 hr) | N/A | 1 hr | N/A |
| Onboarding rejection rate | 35% (benchmark: 5%) | N/A | N/A | N/A |
| Review prep time | 4-6 hrs (benchmark: 1.5 hrs) | N/A | 1-2 hrs | N/A |
| Data sources for review | 6-7 systems | Multiple | Multiple | Multiple |
| Fact-finding time | 90 min (benchmark: 20 min) | N/A | N/A | N/A |
| Annual review letter | 3 hrs (benchmark: 30 min) | N/A | N/A | N/A |
| Non-value task time | N/A | 65% of RM time | 5.4 hrs/day | N/A |
| Digital adoption | N/A | <30% (target: >80%) | 15% initial | 44% paperless |
| Churn rate | 4% (target: 3%) | >10% (target: <5%) | N/A | N/A |

### Regional Considerations for Wealth

#### US Market
| Task | Description | Regulatory |
|------|-------------|------------|
| Tax-Loss Harvesting | Periodic portfolio review for tax optimization | IRS rules, wash sale |
| 1099/K-1 Reporting | Year-end tax document preparation and delivery | IRS reporting |
| RMD (Required Minimum Distribution) | Retirement account mandatory distributions | IRS age-based rules |
| Form ADV / CRS Delivery | Annual regulatory disclosure delivery | SEC/FINRA |
| Beneficiary Designation Updates | Estate planning document updates | State law variations |
| DOL Fiduciary Compliance | Best interest documentation for retirement accounts | DOL rules |

#### EMEA Market
| Task | Description | Regulatory |
|------|-------------|------------|
| MiFID II Suitability | Periodic suitability assessment and documentation | MiFID II |
| Cost & Charges Disclosure | Annual ex-post cost disclosure to clients | MiFID II Art 50 |
| ESG Preference Assessment | Sustainability preference questionnaire | SFDR / MiFID II |
| Cross-Border Tax Reporting | CRS/FATCA reporting for multi-jurisdiction clients | CRS, FATCA |
| PRIIPs KID Delivery | Key Information Document for packaged products | PRIIPs Regulation |

#### APAC / Emerging Markets
| Task | Description | Context |
|------|-------------|---------|
| Multi-Currency Portfolio | Multi-currency consolidation and FX management | Common in HK, SG |
| Islamic Banking Compliance | Shariah-compliant investment screening | GCC, Malaysia, Indonesia |
| NRI/NRE Account Management | Non-resident investment account servicing | India-specific |
| Family Office Services | Multi-generational wealth structure management | Growing APAC segment |

---

## Backbase-Enabled Future State

### Prospecting & Onboarding

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Lead Capture (Digital) │ Qualification │ Hybrid Onboarding │ Activation │
├───────────────┼────────────────────────┼───────────────┼───────────────────┼────────────┤
│ PROSPECT      │ ○ Responds to          │ ○ Self-        │ ○ Guided digital  │ ○ Instant  │
│               │   digital campaign     │   qualifies    │   onboarding with │   account  │
│               │   2-3 min              │   via Prospect │   RM support      │   access   │
│               │                        │   Lounge       │   15-20 min       │            │
│               │                        │   5-10 min     │                   │            │
├───────────────┼────────────────────────┼───────────────┼───────────────────┼────────────┤
│ SYSTEM        │ ○ Campaign tracking    │ ○ Lead scoring │ ○ Pre-fill from   │ ○ Auto     │
│ (Backbase)    │ ○ Lead auto-capture    │ ○ Auto-assign  │   existing data   │   account  │
│               │   <1 min               │   to RM        │ ○ Digital KYC     │   creation │
│               │                        │   <1 min       │ ○ eSignature      │   <1 min   │
│               │                        │                │   5-10 min        │            │
├───────────────┼────────────────────────┼───────────────┼───────────────────┼────────────┤
│ RM            │                        │ ○ Reviews      │ ○ Exception       │ ○ Welcome  │
│               │                        │   assigned     │   handling only   │   message  │
│               │                        │   leads        │   (10% of cases)  │   2-3 min  │
│               │                        │   5-10 min     │   15-20 min       │            │
└───────────────┴────────────────────────┴───────────────┴───────────────────┴────────────┘
```

### Benefits Summary

| Journey | Current State | Future State | Benefit |
|---------|--------------|--------------|---------|
| **Prospecting** | Manual lead tracking | Digital pipeline | +20-30% conversion |
| **Onboarding** | 3-5 hrs, 5+ days | <30 min, same day | 40% effort reduction |
| **Servicing** | 60% admin time | 80% client time | 30-40% cost avoidance |
| **Portfolio Review** | 1-2 hrs prep | <5 min auto-generated | 70% time saved |

---

## Journey Mapping Legend

### Actors
- **Prospect/Client**: End user of wealth services
- **RM**: Relationship Manager - primary advisor
- **RM Assistant**: Administrative support for RM
- **Back Office**: Operations, Processing, Subsidiaries
- **Compliance**: KYC, AML, Suitability teams
- **System**: Automated processes (Backbase platform)

### Time Notation
- **Active time**: Actual work/engagement time (e.g., "15 min")
- **Elapsed time**: Total calendar time including waits (e.g., "2-3 days")

### Friction Indicators
- ⬤ **High**: Significant time/impact
- ⬤ **Medium**: Moderate impact
- ⬤ **Low**: Minimal impact

### Impact Categories
- **Revenue**: Lost AUM, reduced conversion, missed cross-sell
- **Cost**: RM time, rework, manual processing
- **Risk**: Compliance exposure, error rates
- **Experience**: Client satisfaction, relationship quality
