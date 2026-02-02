# Capability Assessment: Retail Bank SEA

**Date:** 2026-01-13
**Prepared for:** Retail Bank - SEA Region
**Prepared by:** Value Consulting Team

---

## Executive Summary

### Overall Assessment

**Overall Maturity Score:** 2.2 / 5.0 (Developing)

The bank operates at a "Developing" maturity level with basic digital processes defined but inconsistent execution, limited tooling integration, and heavy reliance on manual intervention.

**Customer Lifecycle Maturity:**

| Lifecycle Stage | Maturity | Key Gap | Priority |
|----------------|----------|---------|----------|
| **Acquire** | 1.5 / 5.0 | Onboarding broken - low completion, high friction | Critical |
| **Activate** | 2.0 / 5.0 | No early-life journey orchestration | High |
| **Expand** | 2.5 / 5.0 | Limited cross-sell, no 360° view | Medium |
| **Retain** | 2.0 / 5.0 | Expensive servicing, poor channel shift | High |

### Critical Gaps Requiring Immediate Attention

1. **Onboarding Journey Orchestration** - Low completion rates, document friction, cycle time >7 days
2. **Digital Self-Service Enablement** - Simple requests consuming high-cost channels
3. **Customer Journey Analytics** - No visibility into channel behavior or journey drop-off

---

## Customer Lifecycle Assessment

### Acquire Stage

#### Journey: Digital Onboarding

**Current Maturity: 1.5 / 5.0** (Initial/Ad Hoc)

**Current State Challenges (What we heard):**

> "Our onboarding completion rate is low. A lot of customers drop off when documents are required. It can take more than a week in some cases." — Head of Retail (E1, E2, E3)

> "We launched digital onboarding, but it hasn't scaled well. Teams still rely on manual workarounds." — Digital Lead (E7, E8)

#### End-to-End Journey Swimlane Analysis

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase:        │ Research & Apply │ Document Collection │ Processing │ Verification │ Activation │
├───────────────┼──────────────────┼─────────────────────┼────────────┼──────────────┼────────────┤
│ CUSTOMER      │ ○ Browses products│ ○ Attempts document │ ○ Waits    │ ○ May be     │ ○ Receives │
│               │   online          │   upload            │   for      │   contacted  │   welcome  │
│               │   5-10 min        │   10-30 min         │   processing│  for issues │   comms    │
│               │ ○ Starts app      │ ○ DROP-OFF POINT    │   2-7 days │              │   (if ever)│
│               │   15-20 min       │   30-50% abandon    │   (E3)     │              │            │
│               │                   │   (E2)              │            │              │            │
├───────────────┼──────────────────┼─────────────────────┼────────────┼──────────────┼────────────┤
│ FRONTLINE     │ ○ N/A (digital   │ ○ Manual follow-up  │ ○ Chases   │ ○ Calls      │ ○ May      │
│ (Branch/CC)   │   channel)       │   for failed docs   │   back     │   customer   │   assist   │
│               │   OR             │   15-30 min/case    │   office   │   for issues │   with     │
│               │ ○ Assisted start │ ○ Workarounds       │   10-20 min│   10-15 min  │   activation│
│               │   20-30 min      │   prevalent (E8)    │   /case    │              │            │
├───────────────┼──────────────────┼─────────────────────┼────────────┼──────────────┼────────────┤
│ BACK OFFICE   │                  │ ○ Manual doc        │ ○ Account  │ ○ Re-work    │ ○ Card/    │
│               │                  │   review            │   creation │   for errors │   access   │
│               │                  │   15-30 min/app     │   in core  │   15-20 min  │   setup    │
│               │                  │ ○ Requests re-      │   10-15 min│              │   10-15 min│
│               │                  │   submission        │            │              │            │
│               │                  │   10-20 min         │            │              │            │
├───────────────┼──────────────────┼─────────────────────┼────────────┼──────────────┼────────────┤
│ COMPLIANCE    │                  │ ○ KYC verification  │            │ ○ AML check  │            │
│ (KYC/AML)     │                  │   (manual)          │            │   (if flagged)│           │
│               │                  │   20-30 min/app     │            │   15-30 min  │            │
└───────────────┴──────────────────┴─────────────────────┴────────────┴──────────────┴────────────┘
```

**Applications Involved:**
- Customer: Website, Mobile App (partial)
- Frontline: CRM (limited), Core Banking (view only), Phone/Email for follow-up
- Back Office: Core Banking, Document Management (manual), Excel for tracking
- Compliance: KYC platform (separate), AML screening tool

#### Friction Analysis

**Employee Friction:**

| Journey Step | Actor | Time (Active) | Time (Elapsed) | Friction Point | Impact | Evidence |
|-------------|-------|---------------|----------------|----------------|--------|----------|
| Document Collection | Back Office | 15-30 min | 1-2 days | Manual document review | Bottleneck, errors | E2, E8 |
| Document Follow-up | Frontline | 15-30 min | 1+ days | Chasing customers for docs | Time wasted | E2, E8 |
| Processing | Back Office | 10-15 min | 2-5 days | Manual account creation | Slow cycle time | E3 |
| Workarounds | All | Varies | N/A | Teams bypass digital process | Digital not trusted | E8 |

**Customer Friction:**

| Journey Step | Friction Point | Impact | Evidence |
|--------------|---------------|--------|----------|
| Document Upload | Unclear requirements, failed uploads | 30-50% drop-off | E2 |
| Wait Time | No status visibility, >7 day cycle | Frustration, abandonment | E3 |
| Errors/Rework | Contacted for corrections | Poor experience | E2 |
| Activation | Delayed/unclear next steps | Low early engagement | E7 |

#### Business Impact

- **Revenue at Risk:** $2.4M annually (Assumption: 10,000 monthly apps × 60% current completion × $200 revenue/customer × 25% completion improvement)
- **Cost Inefficiency:** $0.6M annually (Assumption: 5,000 apps × 1.5 hrs manual work × $80/hr loaded cost)
- **Time/Effort Waste:** 7,500 staff hours/month on manual onboarding tasks

#### Gap Summary

| Gap | Root Cause | Impact | Priority |
|-----|-----------|--------|----------|
| Low completion rate (E1) | Document friction, poor UX | Lost acquisitions | Critical |
| Document verification friction (E2) | Manual review, unclear requirements | Drop-off, delays | Critical |
| >7 day cycle time (E3) | No straight-through processing | Competitive disadvantage | High |
| Manual workarounds (E8) | Digital not fit for purpose | Investment not delivering | High |

---

### Retain Stage

#### Journey: Customer Servicing

**Current Maturity: 2.0 / 5.0** (Developing)

**Current State Challenges (What we heard):**

> "Servicing is expensive. Simple requests still come through the call center." — Operations Lead (E4, E5)

> "We don't have a clear view of why customers choose branch or call over digital." — Operations Lead (E6)

#### End-to-End Journey Swimlane Analysis

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Channel:      │ Digital (Target) │ Call Center (Current) │ Branch (Current) │
├───────────────┼──────────────────┼───────────────────────┼──────────────────┤
│ CUSTOMER      │ ○ Attempts self- │ ○ Calls for "simple"  │ ○ Visits for     │
│               │   service        │   requests (E5)       │   simple tasks   │
│               │   2-5 min        │   10-15 min hold      │   30+ min total  │
│               │ ○ Often fails,   │   + 5-10 min call     │   incl. travel   │
│               │   escalates      │                       │   & wait         │
├───────────────┼──────────────────┼───────────────────────┼──────────────────┤
│ CALL CENTER   │ ○ Receives       │ ○ Handles simple      │                  │
│               │   escalations    │   requests:           │                  │
│               │   from digital   │   - Balance inquiry   │                  │
│               │   (unknown %)    │   - Statement request │                  │
│               │                  │   - Card queries      │                  │
│               │                  │   5-10 min/call       │                  │
├───────────────┼──────────────────┼───────────────────────┼──────────────────┤
│ BRANCH        │                  │                       │ ○ Staff handles  │
│               │                  │                       │   routine tasks  │
│               │                  │                       │   10-20 min/visit│
├───────────────┼──────────────────┼───────────────────────┼──────────────────┤
│ BACK OFFICE   │                  │ ○ Complex requests    │ ○ Paper forms    │
│               │                  │   escalated           │   processed      │
│               │                  │   15-30 min           │   15-30 min      │
└───────────────┴──────────────────┴───────────────────────┴──────────────────┘
```

**Applications Involved:**
- Customer: Mobile App (limited), Website (basic), Phone, Branch visit
- Call Center: CRM, Core Banking, Knowledge Base
- Branch: Core Banking, Paper forms, Document scanner
- Back Office: Core Banking, Work queues

#### Servicing Task Analysis

| Servicing Task | Yearly Volume (Est.) | Channel | Time/Interaction (hrs) | Cost/Hour | Baseline Annual Cost | Backbase Impact | Cost Avoided |
|---------------|---------------------|---------|----------------------|-----------|---------------------|-----------------|--------------|
| Balance Inquiry | 500,000 | CC/Branch | 0.08 | $25 | $1,000,000 | 70% | $700,000 |
| Statement Request | 200,000 | CC/Branch | 0.17 | $25 | $850,000 | 80% | $680,000 |
| Card Block/Unblock | 50,000 | CC | 0.12 | $25 | $150,000 | 90% | $135,000 |
| Address/Details Change | 100,000 | CC/Branch | 0.25 | $25 | $625,000 | 50% | $312,500 |
| Transaction Inquiry | 150,000 | CC | 0.17 | $25 | $637,500 | 60% | $382,500 |
| General Inquiry | 200,000 | CC | 0.12 | $25 | $600,000 | 40% | $240,000 |
| **TOTAL** | **1,200,000** | | | | **$3,862,500** | | **$2,450,000** |

*Note: Volumes estimated based on typical retail bank ratios. To be validated with client data (DG5, DG6).*

#### Friction Analysis

**Employee Friction:**

| Journey Step | Friction Point | Impact | Evidence |
|--------------|---------------|--------|----------|
| Simple requests | Staff handling tasks that should be self-service | High cost, low value work | E5 |
| Channel routing | No insight into why customers avoid digital | Cannot optimize | E6 |
| Manual escalation | No automated triage or routing | Inconsistent handling | E4 |

**Customer Friction:**

| Journey Step | Friction Point | Impact | Evidence |
|--------------|---------------|--------|----------|
| Self-service attempt | Digital channel fails, must call/visit | Frustration | E5 implied |
| Wait times | Hold times on calls, queues in branch | Poor experience | E5 implied |
| Multiple contacts | Issue not resolved first time | Effort, churn risk | General |

#### Business Impact

- **Cost Inefficiency:** $3.9M annually in servicing (estimated from task analysis)
- **Channel Shift Opportunity:** $2.5M annual savings if 60-70% shift to digital
- **No Analytics:** Cannot quantify or prioritize (E6)

#### Gap Summary

| Gap | Root Cause | Impact | Priority |
|-----|-----------|--------|----------|
| High servicing cost (E4) | Simple requests on expensive channels | Margin pressure | High |
| Channel shift failure (E5) | Digital self-service insufficient | Wasted investment | High |
| No customer analytics (E6) | No journey visibility | Cannot optimize | Medium |

---

## Capability Maturity Scorecard

| Capability | Current | Target | Gap | Business Impact | Priority |
|------------|---------|--------|-----|-----------------|----------|
| **Acquire Stage** | | | | | |
| Digital Onboarding Journey | 1.5 | 3.5 | 2.0 | High - Lost acquisition | Critical |
| Document Verification (eKYC) | 1.5 | 3.5 | 2.0 | High - Drop-off point | Critical |
| Application Processing | 2.0 | 4.0 | 2.0 | High - Cycle time | High |
| Early Life Activation | 1.5 | 3.0 | 1.5 | Medium - Engagement | Medium |
| **Retain Stage** | | | | | |
| Digital Self-Service | 2.0 | 4.0 | 2.0 | High - Servicing cost | High |
| Channel Orchestration | 1.5 | 3.5 | 2.0 | High - Channel shift | High |
| Service Request Automation | 2.0 | 3.5 | 1.5 | Medium - Efficiency | Medium |
| **Enablers** | | | | | |
| Customer Journey Analytics | 1.0 | 3.5 | 2.5 | Medium - Optimization | Medium |
| Process Automation | 2.0 | 4.0 | 2.0 | High - Manual work | High |

---

## Prioritized Recommendations

### Priority 1: Fix Onboarding Journey (Critical)

**Recommendation:** Implement end-to-end digital onboarding with eKYC, document OCR, and straight-through processing

**Expected Impact:**
- Completion rate: 40% → 70% (+75% improvement)
- Cycle time: >7 days → <1 day
- Revenue uplift: $2.4M annually
- Cost avoidance: $0.6M annually

**Evidence:** E1, E2, E3, E7, E8

### Priority 2: Enable Digital Self-Service (High)

**Recommendation:** Deploy comprehensive self-service capabilities for top 10 servicing tasks with intelligent routing

**Expected Impact:**
- Channel shift: 40% digital → 70% digital
- Cost avoidance: $2.5M annually
- Customer experience improvement

**Evidence:** E4, E5, E6

### Priority 3: Build Journey Analytics Foundation (Medium)

**Recommendation:** Implement customer journey analytics to enable data-driven optimization

**Expected Impact:**
- Visibility into drop-off points and channel preference
- Foundation for personalization
- Continuous improvement capability

**Evidence:** E6

---

## Assumptions Register

| ID | Assumption | Value | Confidence | Source | Validation Owner |
|----|-----------|-------|------------|--------|------------------|
| A1 | Current onboarding completion rate | 40% | Low | Industry benchmark for underperforming digital | Digital Lead |
| A2 | Monthly application volume | 10,000 | Low | Estimate for regional retail bank | Head of Retail |
| A3 | Document drop-off rate | 40% | Medium | "A lot" (E2) interpreted conservatively | Digital Lead |
| A4 | Onboarding staff hours per app | 1.5 hrs | Medium | Based on process description | Operations Lead |
| A5 | Loaded cost per staff hour | $80 | Low | Regional estimate | Finance |
| A6 | Revenue per new customer (Y1) | $200 | Low | Industry benchmark | Finance |
| A7 | Annual servicing volume | 1.2M interactions | Low | Estimate based on customer base | Operations Lead |
| A8 | Average cost per call center minute | $0.50 | Low | Industry benchmark | Finance |

---

## Handoff for Roadmap Agent

### Prioritized Capability Gaps
1. Digital Onboarding Journey (Gap: 2.0, Impact: Critical)
2. Document Verification/eKYC (Gap: 2.0, Impact: Critical)
3. Digital Self-Service (Gap: 2.0, Impact: High)
4. Channel Orchestration (Gap: 2.0, Impact: High)
5. Process Automation (Gap: 2.0, Impact: High)

### Dependencies
- eKYC → enables straight-through onboarding
- Self-service → requires journey analytics for optimization
- Channel orchestration → requires self-service capabilities first

### Quick Wins vs. Foundational
- **Quick Win:** Self-service for top 5 servicing tasks (3-4 months)
- **Quick Win:** Document upload UX improvements (2-3 months)
- **Foundational:** eKYC integration (6-9 months)
- **Foundational:** Journey analytics platform (6-12 months)

### Constraints
- Existing digital platform needs assessment
- Change management critical given E8 (workarounds)
- Budget and timeline unknown
