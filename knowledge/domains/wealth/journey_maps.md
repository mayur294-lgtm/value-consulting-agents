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

#### Servicing Task Analysis

| Servicing Task | RM Time | RM Asst Time | BO Time | Employee Friction | Customer Friction |
|---------------|---------|--------------|---------|-------------------|-------------------|
| **Portfolio Review** | ⬤ High | ⬤ Medium | ⬤ Low | RMs stitch data from multiple systems | No consolidated view |
| **Relationship Maintenance** | ⬤ High | ⬤ Low | ⬤ Low | Follow-ups rely on RM memory | Inconsistent service |
| **Sales & Advisory** | ⬤ High | ⬤ Medium | ⬤ Low | Manual research, no digital catalog | Wait for RM suggestions |
| **Customer Queries** | ⬤ High | ⬤ Medium | ⬤ Low | RMs are first line, no case tracking | No clear route if RM busy |
| **Transaction Support** | ⬤ Medium | ⬤ High | ⬤ High | Paper mandates, manual checks | Re-sign forms, no visibility |
| **Reporting & Statements** | ⬤ High | ⬤ Medium | ⬤ Medium | Manual data pull from multiple systems | Fragmented statements |
| **Meeting Prep** | ⬤ High | ⬤ Low | ⬤ Low | Significant data collection time | Quality varies by prep time |
| **Internal Coordination** | ⬤ High | ⬤ Medium | ⬤ Medium | Chase teams via calls/emails | Slow, opaque processes |
| **Compliance & Consent** | ⬤ Medium | ⬤ High | ⬤ High | Paper-heavy KYC, repeated rework | Long doc lists, re-submissions |

Legend: ⬤ High = Significant time/friction | ⬤ Medium = Moderate | ⬤ Low = Minimal

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
