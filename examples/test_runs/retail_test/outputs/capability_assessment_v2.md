# Capability Assessment: Retail Bank SEA — Digital Banking Assessment (v2)

**Date:** 2026-02-04
**Client:** Retail Bank — SEA Region
**Prepared by:** Value Consulting Team
**Operating Mode:** Transcript Inference
**Domain:** Retail Banking (CAP-R-*)
**Scale:** 0-4 Maturity (Absent → Fragmented → Defined → Orchestrated → Intelligent)

---

## 1. Executive Summary

### Key Findings

1. **Onboarding exists but is fundamentally broken front-to-back.** The digital channel is live (Front = 1), but orchestration behind it is manual (Middle = 1) and back-end integration is fragmented (Back = 1). The overall maturity of the onboarding capability is **1 — Fragmented**. The bank has invested in digital but has not realized the value.

2. **Servicing cost problem is a channel strategy problem.** Simple requests consume expensive channels because no self-service capability exists and no data explains why customers choose branch/call over digital. The bank cannot fix what it cannot measure.

3. **Data & Intelligence is the silent blocker.** The bank has no customer behavioral analytics (0 — Absent), no journey visibility (0 — Absent), and no data foundation to power optimization. Without this, every improvement is a guess.

4. **AI readiness is at zero.** No conversational AI, no employee copilots, no AI governance. The bank has no runway for AI-native banking. This is an unconsidered need — leadership has not raised it.

5. **The bank has 3 considered problems and we surface 4 unconsidered needs** that multiply the urgency for transformation.

### Overall Maturity Snapshot

| Domain | Average Score | Range |
|--------|--------------|-------|
| Customer Channels & Engagement | 1.0 | 0 – 1 |
| Customer Lifecycle Management | 1.0 | 0 – 1 |
| Retail Banking Services | 1.5 | 1 – 2 |
| Payments & Transfers | 2.0 | 2 |
| Risk, Compliance & Security | 1.0 | 1 |
| Process Orchestration | 1.0 | 1 |
| Employee Enablement | 1.0 | 1 |
| Data & Intelligence | 0.0 | 0 |
| AI & Agentic | 0.0 | 0 |
| **Weighted Overall** | **0.9** | **0 – 2** |

### Critical Gaps (Top 5)

1. **CAP-R-CL-01: Digital Onboarding** — Score 1. Low completion, document friction, 7+ day cycle time. Directly blocking customer acquisition.
2. **CAP-R-DI-01: Data Foundation** — Score 0. No unified data layer. Blocks all analytics, personalization, and AI capabilities.
3. **CAP-R-CE-01: Digital Channel Availability** — Score 1. Digital exists but incomplete, not self-service capable for routine transactions.
4. **CAP-R-CL-03: Customer Behavioral Insights** — Score 0. No visibility into why customers choose channels. Cannot optimize without this.
5. **CAP-R-PO-01: Workflow & BPM** — Score 1. Manual workarounds indicate no orchestration. Foundation for all process improvement.

### Unconsidered Needs Surfaced

- **UN-R-01: Silent customer churn** — bank likely losing customers without detection
- **UN-R-03: No front-to-back journey visibility** — process breaks are invisible
- **UN-R-04: Data exists but isn't used** — customer insights trapped in silos
- **UN-R-06: No AI strategy** — no roadmap for embedding intelligence

---

## 2. Problem Map

### Considered Needs (Problems the bank knows about)

| ID | Problem | Severity | Evidence | Impact | Related Capabilities |
|----|---------|----------|----------|--------|---------------------|
| CN-01 | Low onboarding completion — customers drop off at document stage | Critical | E1: "Our onboarding completion rate is low", E2: "A lot of customers drop off when documents are required" | Lost customer acquisition; estimated 35-50% of pipeline lost | CAP-R-CL-01, CAP-R-RC-01 |
| CN-02 | Expensive servicing — simple requests still go through call center | High | E4: "Servicing is expensive", E5: "Simple requests still come through the call center" | High cost-to-serve; operational scalability constrained | CAP-R-CE-01, CAP-R-EE-01, CAP-R-CE-02 |
| CN-03 | Digital hasn't scaled — manual workarounds persist | High | E7: "We launched digital onboarding, but it hasn't scaled well", E8: "Teams still rely on manual workarounds" | Technology investment not delivering ROI; workaround culture | CAP-R-PO-01, CAP-R-CL-01 |

### Unconsidered Needs (Problems the bank hasn't raised)

| ID | Problem | Severity | Why They Miss It | Indicators Present | Related Capabilities |
|----|---------|----------|------------------|-------------------|---------------------|
| UN-R-01 | Silent customer churn — customers disengage gradually with no detection | High | Bank measures churn as account closure, not behavioral disengagement | No behavioral analytics (E6 implies no customer behavior tracking); if they can't see channel choice, they definitely can't see engagement decline | CAP-R-CL-03, CAP-R-DI-01 |
| UN-R-03 | No front-to-back journey visibility — process breaks are invisible | High | Each department sees only their part; no end-to-end view | Three stakeholders describe three different parts of the problem (E1=onboarding, E4=servicing, E7=digital); no one described the end-to-end picture | CAP-R-PO-01, CAP-R-DI-02 |
| UN-R-04 | Data exists but isn't used — customer insights trapped in silos | High | Banks have data but no intelligence layer to act on it | E6: "We don't have a clear view of why customers choose branch or call over digital" — they have the transaction data, they just can't analyze it | CAP-R-DI-01, CAP-R-CL-03 |
| UN-R-06 | No AI strategy — bank has no roadmap for embedding intelligence | Medium | AI is either ignored or stuck in pilot purgatory | No mention of AI, chatbots, or automation intelligence in any stakeholder interview. In a market with GXS, Trust Bank, and DBS competing with AI, this is a strategic gap | CAP-R-AI-01, CAP-R-AI-02, CAP-R-AI-03 |

---

## 3. Capability Heatmap (RAG)

### Domain: Customer Channels & Engagement

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-CE-01: Digital Channel Availability | 🟠 1 | 🟠 1 | 🟠 1 | 🟠 **1** | Digital exists but incomplete self-service | CN-02 |
| CAP-R-CE-02: Employee Workspace | 🟠 1 | 🟠 1 | 🟠 1 | 🟠 **1** | No unified customer view for staff | CN-02 |
| CAP-R-CE-03: Contact Center | 🟠 1 | 🟠 1 | 🟠 1 | 🟠 **1** | No channel deflection, no context passing | CN-02 |

### Domain: Customer Lifecycle Management

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-CL-01: Digital Onboarding | 🟠 1 | 🟠 1 | 🟠 1 | 🟠 **1** | Low completion, document friction, 7+ day cycle | CN-01, CN-03 |
| CAP-R-CL-02: Customer Profile & 360 | 🔴 0 | 🔴 0 | 🔴 0 | 🔴 **0** | No unified profile; no evidence of any 360 view | UN-R-04 |
| CAP-R-CL-03: Customer Behavioral Insights | 🔴 0 | 🔴 0 | 🔴 0 | 🔴 **0** | No behavioral analytics at all | UN-R-01, UN-R-04 |

### Domain: Retail Banking Services

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-RB-01: Account Management | 🟡 2 | 🟠 1 | 🟡 2 | 🟠 **1** | Basic digital access, no rich features | CN-02 |
| CAP-R-RB-02: Card Management | 🟠 1 | 🟠 1 | 🟡 2 | 🟠 **1** | Limited self-service card controls | CN-02 |

### Domain: Payments & Transfers

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-PT-01: Domestic Payments | 🟡 2 | 🟡 2 | 🟡 2 | 🟡 **2** | Functional but not optimized | — |

### Domain: Risk, Compliance & Security

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-RC-01: KYC/AML | 🟠 1 | 🟠 1 | 🟠 1 | 🟠 **1** | Manual KYC causing onboarding friction | CN-01 |

### Domain: Process Orchestration

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-PO-01: Workflow & BPM | 🟠 1 | 🟠 1 | 🟠 1 | 🟠 **1** | No end-to-end orchestration; manual workarounds | CN-03, UN-R-03 |

### Domain: Employee Enablement

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-EE-01: Case Management | 🟠 1 | 🟠 1 | 🟠 1 | 🟠 **1** | No formal case management; requests tracked informally | CN-02 |

### Domain: Data & Intelligence

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-DI-01: Data Foundation | 🔴 0 | 🔴 0 | 🔴 0 | 🔴 **0** | No centralized data; completely siloed | UN-R-04 |
| CAP-R-DI-02: Analytics & Reporting | 🔴 0 | 🔴 0 | 🔴 0 | 🔴 **0** | No analytics beyond basic core banking reports | UN-R-03 |

### Domain: AI & Agentic

| Capability | Front | Middle | Back | Overall | Key Gap | Problems |
|------------|-------|--------|------|---------|---------|----------|
| CAP-R-AI-01: Conversational AI | 🔴 0 | 🔴 0 | 🔴 0 | 🔴 **0** | No chatbot or virtual assistant | UN-R-06 |
| CAP-R-AI-02: AI Copilots | 🔴 0 | 🔴 0 | 🔴 0 | 🔴 **0** | No AI assistance for employees | UN-R-06 |
| CAP-R-AI-03: AI Governance | 🔴 0 | 🔴 0 | 🔴 0 | 🔴 **0** | No AI policy or framework | UN-R-06 |

---

## 4. Detailed Capability Assessments

### CAP-R-CL-01: Digital Onboarding

**Overall Score: 1 — Fragmented** | Confidence: High

| Layer | Score | Evidence | Notes |
|-------|-------|----------|-------|
| Front | 1 | E1, E2, E7 | Digital application form exists ("we launched digital onboarding") but customer experience causes drop-off at document stage. Not a Level 2 front because the experience is clearly broken — customers abandon it. |
| Middle | 1 | E3, E8 | Workflow exists but is person-dependent. "Teams rely on manual workarounds" = no automated orchestration. Cycle time >7 days confirms no STP. |
| Back | 1 | E2, E3 (inferred) | KYC/document verification is manual (implied by document-stage drop-off and 7+ day processing). Core banking integration likely exists at basic level. |

**Probing Question Results:**
- Q1 (0→1): Can customers open an account through a digital channel? → **Pass** (E7: "We launched digital onboarding")
- Q2 (1→2): Is the process standardized with defined SLAs and documented workflows? → **Fail** (E8: "Teams still rely on manual workarounds" = not standardized)
- Q3 (2→3): Does STP exist for low-risk applicants? → **Fail** (E3: 7+ day cycle time = no STP)
- Q4 (3→4): Does AI predict drop-off and intervene? → **Fail** (No evidence of any AI)

**Assumptions:**
- A1: "Low completion rate" assumed to mean <50% (industry benchmark for similar banks: 60-75%). Confidence: Medium. Validate with client data.
- A2: Document stage drop-off implies manual KYC with no eKYC or OCR automation. Confidence: Medium.

**Linked Problems:** CN-01, CN-03

---

### CAP-R-CE-01: Digital Channel Availability

**Overall Score: 1 — Fragmented** | Confidence: Medium

| Layer | Score | Evidence | Notes |
|-------|-------|----------|-------|
| Front | 1 | E5, E7 | Digital channel exists (onboarding was launched on it) but "simple requests still come through the call center" suggests self-service is limited or non-existent for servicing. |
| Middle | 1 | E6 (inferred) | No channel orchestration — "no clear view of why customers choose branch or call over digital" implies no context continuity or personalization. |
| Back | 1 | Assumed | API gateway likely exists at basic level (digital onboarding is live). Integration for full self-service not present. |

**Probing Question Results:**
- Q1 (0→1): Do customers have access to digital banking? → **Pass** (E7: digital onboarding exists; basic app implied)
- Q2 (1→2): Is the experience consistent across channels with same features? → **Fail** (E5: simple requests can't be done digitally)
- Q3 (2→3): Can customers start on one channel and continue on another? → **Fail** (No evidence; E6 suggests channels are siloed)
- Q4 (3→4): Does the channel adapt based on behavior? → **Fail** (No evidence of any personalization)

**Assumptions:**
- A3: Mobile app exists with basic functionality (balance, transfers) but limited self-service. Confidence: Low — no direct evidence.

**Linked Problems:** CN-02

---

### CAP-R-DI-01: Data Foundation & Fabric

**Overall Score: 0 — Absent** | Confidence: High

| Layer | Score | Evidence | Notes |
|-------|-------|----------|-------|
| Front | 0 | E6 | No dashboards or analytics visible to business users. Operations Lead has no visibility into customer behavior. |
| Middle | 0 | E6 | No data integration, no quality rules, no governance. The organization cannot answer basic questions about why customers choose channels. |
| Back | 0 | Assumed | No data warehouse or data lake evident. Data exists in individual systems but is not aggregated. |

**Probing Question Results:**
- Q1 (0→1): Is data centralized in any form? → **Fail** (E6: "We don't have a clear view" = data is not aggregated anywhere usable)
- Q2-Q4: All fail — prerequisites not met.

**Assumptions:**
- A4: Individual systems (core banking, CRM) have their own data, but no centralized data layer exists. Confidence: High — E6 is strong evidence.

**Linked Problems:** UN-R-03, UN-R-04

---

### CAP-R-CL-03: Customer Behavioral Insights

**Overall Score: 0 — Absent** | Confidence: High

| Layer | Score | Evidence | Notes |
|-------|-------|----------|-------|
| Front | 0 | E6 | No personalized recommendations or behavioral nudges visible. |
| Middle | 0 | E6 | No behavioral analytics engine. "No clear view of why customers choose branch or call over digital." |
| Back | 0 | Assumed | No clickstream data collection, no data warehouse for behavioral data. |

**Probing Question Results:**
- Q1 (0→1): Does the bank track customer digital behavior? → **Fail** (E6: explicitly stated lack of visibility)
- Q2-Q4: All fail — prerequisites not met.

**Linked Problems:** UN-R-01, UN-R-04

---

### CAP-R-PO-01: Workflow & BPM

**Overall Score: 1 — Fragmented** | Confidence: High

| Layer | Score | Evidence | Notes |
|-------|-------|----------|-------|
| Front | 1 | E8 (inferred) | Staff likely have task queues but no SLA visibility or exception dashboards. |
| Middle | 1 | E8 | "Teams still rely on manual workarounds" = no standardized BPM engine. Process exists but is ad-hoc and person-dependent. |
| Back | 1 | E3, E8 | Limited integration between systems. 7+ day cycle time and manual workarounds indicate broken handoffs. |

**Probing Question Results:**
- Q1 (0→1): Are processes managed through a workflow tool? → **Pass** (some workflow exists — digital onboarding was launched, implying basic tooling)
- Q2 (1→2): Is there a standardized BPM engine? → **Fail** (E8: workarounds = not standardized)
- Q3 (2→3): Are processes measured with SLAs? → **Fail** (No evidence of measurement)
- Q4 (3→4): Does AI optimize routing? → **Fail** (No evidence of AI)

**Linked Problems:** CN-03, UN-R-03

---

### CAP-R-RC-01: KYC/AML & Customer Screening

**Overall Score: 1 — Fragmented** | Confidence: Medium

| Layer | Score | Evidence | Notes |
|-------|-------|----------|-------|
| Front | 1 | E2 | Document upload exists (customers can provide documents digitally) but the experience causes drop-off = poor UX. |
| Middle | 1 | E2, E3 | KYC workflow exists but is manual. No automated eKYC or risk-based processing implied by 7+ day cycles. |
| Back | 1 | Assumed | KYC vendor likely exists but integration is minimal. No automated screening or ongoing monitoring evident. |

**Probing Question Results:**
- Q1 (0→1): Is KYC performed digitally? → **Pass** (E2: document collection is digital, even if manual behind the scenes)
- Q2 (1→2): Is the process standardized with vendor integrations? → **Fail** (E3: 7+ day cycle and manual workarounds suggest no standardized automation)
- Q3 (2→3): Is ongoing monitoring automated? → **Fail** (No evidence)
- Q4 (3→4): Does AI perform continuous risk assessment? → **Fail** (No evidence)

**Linked Problems:** CN-01

---

### CAP-R-AI-01: Conversational AI & Virtual Assistants

**Overall Score: 0 — Absent** | Confidence: High

| Layer | Score | Evidence | Notes |
|-------|-------|----------|-------|
| Front | 0 | No evidence | No chatbot or virtual assistant mentioned by any stakeholder. |
| Middle | 0 | No evidence | No NLU, no dialogue management, no knowledge retrieval. |
| Back | 0 | No evidence | No LLM infrastructure, no conversation logging. |

**Probing Question Results:**
- Q1 (0→1): Does any chatbot exist? → **Fail** (Not mentioned by any stakeholder)
- Q2-Q4: All fail — capability doesn't exist.

**Note:** In a market where DBS, GXS, and Trust Bank all have conversational AI, this is a competitive gap even if the bank hasn't recognized it.

**Linked Problems:** UN-R-06

---

### CAP-R-AI-02: AI Copilots for Employees

**Overall Score: 0 — Absent** | Confidence: High

| Layer | Score | Evidence | Notes |
|-------|-------|----------|-------|
| Front | 0 | No evidence | No AI suggestions in any workspace. |
| Middle | 0 | No evidence | No context-aware AI engine. |
| Back | 0 | No evidence | No LLM infrastructure. |

**Linked Problems:** UN-R-06

---

### CAP-R-AI-03: AI Governance & Trust

**Overall Score: 0 — Absent** | Confidence: Medium

Not assessable from transcript. Scored 0 because no AI capabilities exist, so no governance is needed yet. However, absence of any AI strategy or policy is itself a gap — the bank should have an AI roadmap even if no AI is deployed.

**Linked Problems:** UN-R-06

---

## 5. Problem → Capability Traceability

| Problem | Type | Severity | Related Capabilities | Weakest Score | Readiness | Required Improvement |
|---------|------|----------|---------------------|---------------|-----------|---------------------|
| CN-01: Low onboarding completion | Considered | Critical | CAP-R-CL-01, CAP-R-RC-01 | 1 | At Risk | Automate KYC, build STP, orchestrate E2E |
| CN-02: Expensive servicing | Considered | High | CAP-R-CE-01, CAP-R-CE-02, CAP-R-EE-01 | 1 | At Risk | Enable self-service, deploy channel deflection |
| CN-03: Digital hasn't scaled | Considered | High | CAP-R-PO-01, CAP-R-CL-01 | 1 | At Risk | BPM engine, automated workflows, remove workarounds |
| UN-R-01: Silent customer churn | Unconsidered | High | CAP-R-CL-03, CAP-R-DI-01 | 0 | Blocked | Build behavioral analytics from scratch |
| UN-R-03: No journey visibility | Unconsidered | High | CAP-R-PO-01, CAP-R-DI-02 | 0 | Blocked | Data foundation + analytics platform required |
| UN-R-04: Data trapped in silos | Unconsidered | High | CAP-R-DI-01, CAP-R-CL-03 | 0 | Blocked | Data fabric / warehouse required as foundation |
| UN-R-06: No AI strategy | Unconsidered | Medium | CAP-R-AI-01, CAP-R-AI-02, CAP-R-AI-03 | 0 | Blocked | AI roadmap, governance framework, infrastructure |

---

## 6. Path to Target State

### CAP-R-CL-01: Digital Onboarding — Current 1 → Target 3

**What Level 1 Looks Like Today:**
Digital application form exists but the process is broken behind the screen. Customers drop off at documents (E2), cycle time exceeds 7 days (E3), and staff work around the system instead of through it (E8). Completion rate is "low" (E1). The bank invested in the front door but not the plumbing.

**What Level 3 Looks Like:**
Onboarding is end-to-end orchestrated. Low-risk applicants are auto-approved in <24 hours with STP. Document verification uses eKYC and OCR. Exceptions route to staff with full context. Completion rate >65%. Cycle time <48 hours for digital. Real-time KPIs track every step.

**What Changes:**
- **Front Layer:** Mobile document capture, real-time status tracking, progressive data collection, clear guidance at each step
- **Middle Layer:** Workflow orchestration engine, automated decisioning (risk-based STP), KYC/AML orchestration, exception routing with SLA management
- **Back Layer:** eKYC vendor integration, core banking API for account creation, document management system, credit bureau auto-pull

**Dependencies:** CAP-R-RC-01 (KYC must improve in parallel), CAP-R-PO-01 (workflow foundation needed)
**Business Outcomes:** Customer acquisition uplift (estimated 25-35pp completion improvement), cost per acquisition reduction (40-50%), competitive parity with digital challengers
**Effort:** L (12-18 months)

---

### CAP-R-DI-01: Data Foundation — Current 0 → Target 2

**What Level 0 Looks Like Today:**
Data is completely siloed in individual systems. No one can answer "why do customers choose branch over digital?" (E6). No centralized data store, no quality rules, no governance. Each team sees their own data only.

**What Level 2 Looks Like:**
Defined data architecture exists. Data from core banking, CRM, and digital channels is aggregated into a data warehouse. Quality rules are enforced. Business users have dashboards. Not yet real-time, but reliable and governed.

**What Changes:**
- **Front Layer:** Business dashboards for operations, product, and executives. Self-service basic reporting.
- **Middle Layer:** ETL/ELT pipelines from core systems. Data quality monitoring. Basic governance policies.
- **Back Layer:** Data warehouse deployed. Connectors to core banking, digital platform, CRM, and call center. Privacy and consent framework.

**Dependencies:** None — this is foundational. Everything else depends on it.
**Business Outcomes:** Enables analytics (CAP-R-DI-02), behavioral insights (CAP-R-CL-03), and eventually AI (CAP-R-AI-*). Without this, the bank is flying blind.
**Effort:** M-L (9-15 months)

---

### CAP-R-CE-01: Digital Channel Availability — Current 1 → Target 2

**What Level 1 Looks Like Today:**
Basic digital banking exists (customers can see balances, make some transfers) but most servicing transactions cannot be completed digitally. Simple requests still go to the call center (E5). No feature parity between digital and assisted channels.

**What Level 2 Looks Like:**
Top 20 servicing transactions available in digital. Consistent experience across mobile and web. Feature parity for routine requests. Self-service completion rate >60% for supported transactions.

**What Changes:**
- **Front Layer:** Expand mobile/web banking to include card controls, address changes, statement requests, dispute initiation, standing orders.
- **Middle Layer:** Feature flagging, progressive rollout, basic session management.
- **Back Layer:** API layer connecting digital channel to core banking for all supported transactions.

**Dependencies:** None for initial expansion; CAP-R-PO-01 for orchestrated workflows.
**Business Outcomes:** Servicing cost reduction (shift from $8-12/call to $0.50-1.50/digital). Estimated $3-5M annual savings at scale.
**Effort:** M (6-12 months)

---

### CAP-R-PO-01: Workflow & BPM — Current 1 → Target 2

**What Level 1 Looks Like Today:**
Processes exist but are manual and person-dependent. "Teams still rely on manual workarounds" (E8). No standardized BPM engine. No SLA tracking. Handoffs between teams are informal.

**What Level 2 Looks Like:**
Standardized BPM engine in place. Key processes (onboarding, servicing, KYC) are defined in the workflow tool. Roles and routing rules are documented. SLAs exist even if not yet automated.

**What Changes:**
- **Front Layer:** Task queues for operations staff, basic SLA dashboards.
- **Middle Layer:** BPM engine deployed (Flow Foundation or equivalent). Processes modeled and executable. Basic routing rules.
- **Back Layer:** Integration with core banking and KYC systems. Audit logging.

**Dependencies:** None — this is foundational.
**Business Outcomes:** Enables onboarding improvement (CAP-R-CL-01), servicing efficiency, and eventually E2E orchestration.
**Effort:** M (6-12 months)

---

### CAP-R-RC-01: KYC/AML — Current 1 → Target 2

**What Level 1 Looks Like Today:**
Document-based KYC with manual review. Causes the primary onboarding friction point (E2). Extended cycle times (E3). No automated eKYC or risk-based processing.

**What Level 2 Looks Like:**
Standardized KYC workflow with vendor integration. eKYC for low-risk applicants (biometric + ID verification). Defined SLAs for review. Periodic review scheduling.

**What Changes:**
- **Front Layer:** eKYC flow (biometric capture, ID scan), status visibility.
- **Middle Layer:** KYC orchestration with risk-based routing (auto-approve vs. manual review). Vendor integration for ID&V.
- **Back Layer:** eKYC vendor integration (Jumio, Onfido, etc.), sanctions screening, regulatory reporting.

**Dependencies:** Must improve in parallel with CAP-R-CL-01.
**Business Outcomes:** Directly addresses CN-01 (onboarding drop-off). Reduces document-stage friction. Enables STP.
**Effort:** M (6-12 months, vendor-dependent)

---

## 7. Data & Intelligence Assessment

**Domain Status: ABSENT (0)**

This is the most critical gap in the assessment. The bank has **zero** Data & Intelligence capability maturity:

| Capability | Score | Impact |
|------------|-------|--------|
| CAP-R-DI-01: Data Foundation | 0 | No centralized data. Cannot answer basic questions (E6). |
| CAP-R-DI-02: Analytics & Reporting | 0 | No dashboards, no business intelligence beyond core banking. |

**Why This Matters:**
Every modern banking capability depends on data. Without a Data Foundation:
- Cannot build behavioral analytics → cannot detect churn (UN-R-01)
- Cannot build journey analytics → cannot optimize onboarding or servicing (UN-R-03)
- Cannot power personalization → cannot cross-sell effectively
- Cannot deploy AI → entire AI roadmap blocked (UN-R-06)

**Recommendation:** Data Foundation (CAP-R-DI-01) should be treated as **Phase 0 infrastructure** — start immediately, in parallel with onboarding and servicing improvements. Target Level 2 within 12 months.

---

## 8. AI & Agentic Readiness Assessment

**Domain Status: ABSENT (0)**

| Capability | Score | Assessment |
|------------|-------|------------|
| CAP-R-AI-01: Conversational AI | 0 | No chatbot or virtual assistant exists. |
| CAP-R-AI-02: AI Copilots | 0 | No AI assistance for employees. |
| CAP-R-AI-03: AI Governance | 0 | No AI policy, framework, or strategy. |

### AI Readiness Dimensions

| Dimension | Status | Assessment |
|-----------|--------|------------|
| Data Readiness | Not Ready | No data foundation to train or feed AI models |
| Infrastructure | Not Ready | No LLM infrastructure, no ML platform |
| Organizational | Not Ready | No AI team, no AI strategy mentioned |
| Governance | Not Ready | No AI policy or ethics framework |
| Use Cases | Not Ready | No AI use cases identified or piloted |

### Competitive Context
In the SEA market, digital-native banks (GXS, Trust Bank) and regional leaders (DBS, CIMB, Maybank) are deploying:
- Conversational AI for customer service (deflecting 30-50% of queries)
- AI-powered cross-sell and personalization
- Employee copilots for branch and call center staff
- Predictive analytics for churn and credit risk

The bank's zero AI readiness is a growing competitive risk that will compound over time.

### Recommendation
AI should not be Phase 1 — the bank must build Data Foundation first. But an **AI strategy and governance framework** should be developed now (Phase 1 activity) so the organization is ready when data infrastructure enables it. Target: AI Strategy by Month 6, First AI Pilot by Month 18.

---

## 9. Assumptions Register

| # | Assumption | Basis | Sensitivity | Impact on Assessment | Validation Owner |
|---|------------|-------|-------------|---------------------|-----------------|
| A1 | "Low" completion rate = ~40% (vs. industry 60-75%) | Severity of stakeholder language, SEA market context | High — if completion is 55%, gap is smaller | Drives CN-01 severity and onboarding priority | Head of Retail → provide actual completion data |
| A2 | Document drop-off implies manual KYC (no eKYC/OCR) | E2 language + 7+ day cycle time | Medium | Affects KYC capability score | Digital Lead → confirm KYC process |
| A3 | Basic mobile/web banking exists with balance and transfer functionality | Implied by "digital onboarding launched" | Medium | Affects CE-01 score (1 vs 0) | Digital Lead → confirm app feature set |
| A4 | No data warehouse or centralized data exists | E6: "no clear view" implies no unified data | High | If a data warehouse exists, DI-01 would be Level 1 | CTO → confirm data architecture |
| A5 | Digital self-service handles <20% of servicing transactions | E5: simple requests still go to call center | High — affects cost savings estimate | Baseline for servicing ROI | Operations Lead → provide channel volume data |
| A6 | Monthly servicing volume ~100,000 transactions | Typical for SEA regional bank | Medium | Affects total cost savings estimate | Operations Lead → provide actual volumes |
| A7 | No AI capabilities exist in any form | Zero mention by any stakeholder | Low | If chatbot exists, AI scores would change | Digital Lead → confirm |
| A8 | SEA market competitive pressure from digital banks | Public knowledge: GXS, Trust Bank, GoTo Financial active in SEA | Low | Affects urgency framing, not capability scores | N/A — market research |

---

## 10. Journey Impact Summary

### Onboarding Journey — Acquire Stage

**Current State (What We Heard):**
- "Our onboarding completion rate is low. A lot of customers drop off when documents are required. It can take more than a week in some cases." — Head of Retail (E1, E2, E3)
- "We launched digital onboarding, but it hasn't scaled well. Teams still rely on manual workarounds." — Digital Lead (E7, E8)

**Capability Gaps Affecting This Journey:**

| Capability | Current | Target | Gap Impact |
|------------|---------|--------|------------|
| CAP-R-CL-01: Digital Onboarding | 1 | 3 | Core journey capability — drives completion rate and cycle time |
| CAP-R-RC-01: KYC/AML | 1 | 2 | Document friction — primary drop-off point |
| CAP-R-PO-01: Workflow & BPM | 1 | 2 | Manual workarounds — no E2E orchestration |

**Business Impact:**
- Revenue at Risk: If 10,000 monthly applications with 40% completion vs. 65% target = **3,000 lost customers/month** (A1, A3)
- Cost Inefficiency: 7+ day cycle time at estimated $150/manual onboarding vs. $20/automated = significant CAC premium
- Competitive Risk: Digital-first banks in SEA onboard in <24 hours

**Recommendations:**
1. Deploy eKYC to eliminate document-stage friction (addresses E2)
2. Implement workflow orchestration to remove manual handoffs (addresses E8)
3. Build STP for low-risk applicants (addresses E3 cycle time)

---

### Servicing Journey — Activate/Retain Stage

**Current State (What We Heard):**
- "Servicing is expensive. Simple requests still come through the call center. We don't have a clear view of why customers choose branch or call over digital." — Operations Lead (E4, E5, E6)

**Capability Gaps Affecting This Journey:**

| Capability | Current | Target | Gap Impact |
|------------|---------|--------|------------|
| CAP-R-CE-01: Digital Channel | 1 | 2 | Limited self-service forces customers to expensive channels |
| CAP-R-CL-03: Behavioral Insights | 0 | 1 | Cannot understand channel preference drivers |
| CAP-R-EE-01: Case Management | 1 | 2 | No structured service request management |
| CAP-R-DI-01: Data Foundation | 0 | 2 | Cannot measure or optimize anything |

**Business Impact:**
- Cost Inefficiency: Estimated $8-12 per call center transaction vs. $0.50-1.50 digital. At 100K monthly transactions with 80% assisted = **$9.6M-$14.4M annually in addressable cost** (A5, A6)
- Scalability: Cannot grow customer base without proportional cost increase
- Experience: Customers who prefer digital are forced to branch/call

**Recommendations:**
1. Expand digital self-service to cover top 20 servicing transactions
2. Build channel analytics to understand and optimize channel choice (E6)
3. Deploy proactive deflection from call center to digital

---

## Cross-Cutting Themes

### Theme 1: "Glass Front, Broken Back"
The bank has invested in a digital front-end but the middle and back layers are manual. The front layer (Level 1) is undermined by a fragmented middle layer (Level 1) and absent back layer integration (Level 0-1). This is the classic pattern of digital-in-name-only.

### Theme 2: "Data Desert"
No Data & Intelligence capability exists. This blocks every optimization effort — from onboarding improvement measurement to servicing cost analysis to AI deployment. Data Foundation must be treated as infrastructure, not a project.

### Theme 3: "Invisible Problems"
The bank's three stakeholders each see their part of the problem (onboarding, servicing, digital) but no one sees the whole picture. This is evidence of UN-R-03 (no front-to-back journey visibility) and indicates an organizational structure that mirrors system silos.

---

## Handoff for Downstream Agents

### For ROI Agent:
- **Primary value levers:** Onboarding completion uplift (revenue), servicing channel shift (cost), cycle time reduction (efficiency)
- **Baseline assumptions:** A1 (40% completion), A5 (<20% digital containment), A6 (100K monthly transactions)
- **Data gaps requiring validation:** DG1 (actual completion), DG2 (volume data), DG3 (cost per channel)

### For Roadmap Agent:
- **Phase 0 (Foundational):** Data Foundation (CAP-R-DI-01), Workflow/BPM (CAP-R-PO-01)
- **Phase 1 (Quick Impact):** Digital Onboarding fix (CAP-R-CL-01), KYC automation (CAP-R-RC-01), Self-service expansion (CAP-R-CE-01)
- **Phase 2 (Optimize):** Analytics (CAP-R-DI-02), Behavioral Insights (CAP-R-CL-03), Case Management (CAP-R-EE-01)
- **Phase 3 (Differentiate):** AI Strategy, Conversational AI (CAP-R-AI-01), Employee Copilots (CAP-R-AI-02)
- **Dependencies:** Data Foundation blocks Analytics, Behavioral Insights, and all AI. Workflow blocks onboarding STP.

---

*Document Control:*
*Version: 2.0*
*Methodology: 0-4 Scale, BIAN-aligned, Front/Middle/Back Layer Assessment*
*Taxonomy Reference: knowledge/standards/capability_taxonomy.md v2.0*
*Assessment Mode: Transcript Inference — Conservative bias applied*
*Confidence: Medium overall (limited transcript, 3 stakeholders, significant data gaps)*
*Next Review: After data validation with client*
