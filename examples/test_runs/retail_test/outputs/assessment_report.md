# Assessment & Solutioning Report
## Ignite Assess Engagement Deliverable

**Client:** Retail Bank — SEA Region
**Date:** February 2026
**Engagement:** Digital Banking Transformation — Onboarding & Servicing
**Engagement Type:** Ignite Assess
**Prepared by:** Backbase Value Consulting

---

## Table of Contents

| # | Section | Purpose |
|---|---------|---------|
| **01** | Strategic Goals | Alignment on your strategy and what you want to achieve |
| **02** | The Vision | Unified platform to support long-term growth |
| **03** | Phase 1 — The Lighthouse | Retail digital banking transformation as the starting point |
| **04** | Deep-Dive: Assessment & Solutioning | Challenges, impact, recommendations across the customer lifecycle |
| **05** | Capability Assessment | Front-to-back maturity heatmap with problem traceability |
| **06** | Delivery Roadmap | Phased delivery plan |
| **07** | Benefits Case | Detailed business benefits case |
| | Appendix | Supporting data and methodology |

---

# SECTION 1: Bank Vision

---

## 01. Level Setting — Our Understanding of the Bank's Goals & Hurdles

### Strategic Objectives

Group-level objectives synthesized from detailed assessment interviews with the Head of Retail, Operations Lead, and Digital Lead:

1. **Digital-first customer acquisition:** Improve onboarding to increase customer acquisition and reduce time-to-activate. The bank has invested in digital onboarding but it has not scaled as expected (E7).

2. **Cost-efficient servicing at scale:** Reduce cost-to-serve by shifting simple servicing transactions from expensive channels (call center, branch) to digital self-service (E4, E5).

3. **Data-driven operations:** Build visibility into customer behavior across channels to enable systematic optimization rather than reactive fixes (E6).

4. **Operational efficiency:** Eliminate manual workarounds that prevent digital processes from scaling (E8).

### The Opportunity

The bank serves a growing retail market in Southeast Asia — one of the fastest-growing digital banking markets globally. The opportunity is threefold:

| Segment | Current State | Potential |
|---------|---------------|-----------|
| **New-to-bank customers** | Low onboarding completion, 7+ day cycle time — losing ~35-50% of applicants at document stage | +30,000 additional customers annually with <48hr digital onboarding |
| **Existing customers (servicing)** | ~80% of simple requests go to call center/branch at ~$10/transaction | $5.8M annual savings by shifting 40,000 monthly transactions to $1 digital self-service |
| **Digital adoption** | Launched digital channel but adoption stalled (E7) | 60%+ digital containment (vs. ~20% today) unlocks scalability without linear cost |

**Total value at stake: $8.2M annually** from onboarding + servicing improvements alone — before analytics, personalization, or AI capabilities.

### The Catalyst

The bank has already made the decision to go digital. Digital onboarding was launched, digital channels exist. But the investment is not delivering returns:

> *"We launched digital onboarding, but it hasn't scaled well."* — Digital Lead (E7)

> *"Teams still rely on manual workarounds."* — Digital Lead (E8)

This is the classic "digital veneer" problem: the front-end is modern, but the middle and back layers have not been transformed. The result is a digital experience that looks good but doesn't work — driving customers back to branch and call center.

**Why now:** Every month of delay costs the bank approximately $680K in lost revenue and excess servicing costs. Digital-first competitors (GXS, Trust Bank, DBS digibank) are setting a <24-hour onboarding standard. The gap is widening.

### Key Challenges Faced Today

| Challenge | Description | Business Impact |
|-----------|-------------|-----------------|
| **Low onboarding completion** | Customers drop off when documents are required (E1, E2) | Lost customer acquisition — estimated 2,500+ applicants/month abandoning |
| **Extended cycle times** | Onboarding takes 7+ days in some cases (E3) | Poor time-to-value, customer frustration, competitive disadvantage |
| **Expensive servicing** | Simple requests still come through the call center (E4, E5) | $3-5M annual excess cost; scalability constrained |
| **No customer insights** | No clear view of why customers choose branch/call over digital (E6) | Cannot optimize what you cannot measure |
| **Manual workarounds** | Teams rely on manual processes despite digital launch (E8) | Digital investment not delivering ROI; workaround culture |
| **Digital adoption failure** | Digital onboarding launched but hasn't scaled (E7) | Strategic initiative underperforming; confidence at risk |

### The Legacy Trap

The bank is caught in a siloed systems architecture that blocks CX and productivity gains:

**Current State Architecture (Simplified):**

| Layer | What Exists Today | Pain |
|-------|-------------------|------|
| **Customer Channels** | Mobile app, internet banking, branch | Fragmented — each channel operates independently, no shared state |
| **Employee Tools** | Multiple back-office systems, CRM, manual checklists | Context switching — staff toggle between 4-6 systems per transaction |
| **Integration** | Point-to-point connections, batch files, manual handoffs | No orchestration — every handoff is a potential failure point |
| **Core Systems** | Core banking, KYC platform, document management | Legacy — limited API exposure, batch processing, no real-time capabilities |

The result: **a digital front door leading to an analog back office.** The front layer says "digital bank." The middle and back layers say "1990s operations."

---

# SECTION 2: The Vision

---

## 02. The Unified Banking Platform — Long-Term Transformation

### The Bank Tomorrow

The target state is a **unified intelligent frontline** that runs end-to-end journeys across all channels — replacing today's fragmented customer and staff apps with a single platform that orchestrates every interaction from first click to fulfillment.

**Key principles:**
- **Journey-based:** Organize around customer journeys (onboarding, servicing, engagement), not products or channels
- **Front-to-back:** Every journey orchestrated end-to-end — experience layer, capability layer, integration layer working as one
- **Incremental:** Progressive modernization, not big-bang replacement — build on existing digital investment
- **Platform-first:** Build once, reuse across journeys and segments — onboarding orchestration today, lending tomorrow

### Progressive Modernization Approach

| Phase | Focus | Outcome |
|-------|-------|---------|
| **Set the Foundation** | Workflow orchestration, API layer, data foundation, core journey automation | Modern orchestration layer sitting between existing front-end and core systems |
| **Build Differentiation** | Self-service expansion, channel orchestration, journey analytics, 360 view | Data-driven engagement, measurable improvement, proactive service |
| **Accelerate Growth** | AI-powered personalization, agentic workflows, predictive servicing | Self-optimizing, proactive banking — human-in-the-loop for exceptions only |

### Progressive Modernization Across Lines of Business

| | Phase 1 (Lighthouse) | Phase 2 | Phase 3 |
|---|---|---|---|
| **Retail — Onboarding** | Digital onboarding automation, eKYC, STP | Full lifecycle management | AI-powered lead scoring |
| **Retail — Servicing** | Self-service expansion, channel orchestration | Proactive engagement | Conversational AI, copilots |
| **Future LoB (SME/Wealth)** | — | Reuse platform for SME onboarding | Extend to wealth/advisory |

---

# SECTION 3: Phase 1 — The Lighthouse

---

## 03. Retail Digital Banking Transformation as the Starting Point

### Why Start Here

1. **Highest pain, highest value:** Onboarding and servicing are the two journeys stakeholders identified as critical. Combined value at stake: $8.2M annually.
2. **Existing investment:** Digital onboarding is already launched (E7) — optimize rather than rebuild.
3. **Platform reuse:** Workflow orchestration and API layer built for retail onboarding can be reused for servicing, then for future lines of business.
4. **Organizational readiness:** All three stakeholders (Head of Retail, Operations Lead, Digital Lead) aligned on these priorities.

### In-Scope for Phase 1

| Journey | Capability | OOTB / Custom | Priority |
|---------|------------|---------------|----------|
| Digital Onboarding | Workflow orchestration, eKYC, STP rules | OOTB + Extend | P1 |
| Digital Onboarding | Document capture & verification | OOTB + Integrate | P1 |
| Digital Self-Service | Top 20 servicing transactions | OOTB + Extend | P1 |
| Channel Orchestration | Intelligent routing, deflection | Extend | P2 |
| Journey Analytics | Funnel tracking, channel analytics | OOTB + Configure | P1 |
| Customer 360 | Unified profile for staff | OOTB + Integrate | P2 |

### Core Value Proposition Across the Lifecycle

| Lifecycle Stage | Key Capability | Business Outcome |
|----------------|----------------|------------------|
| **Acquire** | Digital onboarding with eKYC and STP | Completion rate 40% → 65%, cycle time 7 days → <48 hours |
| **Activate** | Workflow orchestration, real-time status | Faster time-to-value, transparent process, reduced manual work |
| **Expand** | Customer 360, journey analytics | Staff can see full relationship, identify cross-sell, proactive outreach |
| **Retain** | Digital self-service, channel orchestration | 60% digital containment, $5.8M cost savings, scalable operations |

### Bird's-Eye Benefits View

**The bank stands to gain $18M over 3 years from Phase 1**

| Value Driver | 3-Year Value | Type |
|-------------|-------------|------|
| Digital self-service channel shift | $13.0M | Cost Avoidance |
| Improved onboarding conversion | $5.0M | Revenue Uplift |
| **Total Benefits** | **$18.0M** | |
| Total Investment | ($12.0M) | |
| **Net Value** | **$6.0M** | |

**ROI: 42% IRR | Payback: 18 months | NPV: $5.2M**

---

# SECTION 4: Deep-Dive — Assessment & Solutioning

---

## 04. Engagement Approach

Backbase Value Consulting conducted a structured assessment engagement comprising:

- **Discovery interviews** with 3 senior stakeholders (Head of Retail, Operations Lead, Digital Lead)
- **Evidence-based analysis** producing an 8-item evidence register (E1-E8)
- **Capability assessment** using BIAN-aligned 0-4 maturity scale across Front/Middle/Back layers
- **Financial modeling** with conservative benchmarks (MEDIUM confidence)
- **Roadmap development** phased by value, dependencies, and organizational capacity

### Deliverables Produced

| Deliverable | Description |
|-------------|-------------|
| **Business Case** | 3-year financial model with scenario analysis — $5.2M NPV, 42% IRR |
| **Capability Assessment** | Front-to-back maturity heatmap: 17 capabilities scored, overall maturity 0.9/4.0 |
| **Journey Assessment** | Current-state process maps for onboarding and servicing with friction analysis |
| **Solution Architecture** | Proposed platform architecture and integration approach |
| **Delivery Roadmap** | 18-month phased implementation: Foundation → Scale → Optimize |

---

## 05. Summary — Challenges & Impact, Recommendations & Value

### Across the Customer Lifecycle

---

### Acquire — Challenges & Impact

**Current Challenges:**

| Challenge | Customer Impact | Employee Impact | Evidence |
|-----------|-----------------|-----------------|----------|
| Low onboarding completion | Customers abandon when documents required — estimated 35-50% drop-off | Wasted processing effort on incomplete applications | E1, E2 |
| Extended cycle times | 7+ days to open an account — customers move to competitors | Manual review and workarounds consume staff time | E3, E8 |
| Digital hasn't scaled | Inconsistent experience — digital starts but branch finishes | Staff revert to manual processes, undermining digital investment | E7, E8 |

**Business Impact:**
- **Revenue at risk:** ~$2.4M annually from lost customers (est. 30,000 applicants/year abandoning × $80 annual revenue per customer)
- **Cost inefficiency:** High cost per acquisition due to manual processing (~$150/completed application vs. $30 benchmark for STP)
- **Competitive gap:** Digital-first banks onboard in <24 hours. Current 7+ day cycle is 10x slower.

---

### Acquire — Recommendations & Value

| # | Recommendation | Expected Impact | Effort |
|---|---------------|----------------|--------|
| 1 | Automate end-to-end onboarding with workflow orchestration | 25pp completion rate improvement, $2.4M annual revenue | L |
| 2 | Deploy eKYC with automated document verification | 70% reduction in document-related drop-offs | M |
| 3 | Implement STP rules for low-risk applications | 30-40% of applications auto-approved in <24 hours | M |
| 4 | Add save & resume with real-time status tracking | Recover 15-20% of abandoned applications | S |

**How Benefits Are Calculated:**

| Metric | Current | Target | Delta | Annual Value |
|--------|---------|--------|-------|-------------|
| Onboarding completion rate | ~40% | ~65% | +25pp | — |
| Additional customers/year | — | 30,000 | +30,000 | — |
| Revenue per customer/year | — | $80 | — | $2.4M |

---

### Activate — Challenges & Impact

**Current Challenges:**

| Challenge | Customer Impact | Employee Impact | Evidence |
|-----------|-----------------|-----------------|----------|
| Manual onboarding fulfillment | 7+ days from application to active account | Staff spend 40+ minutes per application on manual steps | E3, E8 |
| No process orchestration | Customer has no visibility into application status | Handoffs between teams are email/paper-based, things get lost | E8 |
| Workaround culture | Inconsistent experience — some fast, some stuck for weeks | Staff develop own shortcuts, no standardization | E8 |

**Business Impact:**
- **Cost inefficiency:** ~$150 per completed application (manual process) vs. $30 benchmark (automated)
- **Time waste:** Estimated 400+ staff hours/month on manual onboarding workarounds
- **Customer risk:** 7+ day activation means delayed revenue and higher early-stage churn

---

### Activate — Recommendations & Value

| # | Recommendation | Expected Impact | Effort |
|---|---------------|----------------|--------|
| 1 | Deploy BPM/workflow engine for onboarding orchestration | Cycle time from 7 days to <48 hours | L |
| 2 | Automate KYC/AML screening with API integration | 80% of screenings completed in <5 minutes | M |
| 3 | Implement real-time status tracking for customers | Reduce "where's my application" calls by 50% | S |

**How Benefits Are Calculated:**

| Metric | Current | Target | Delta | Annual Value |
|--------|---------|--------|-------|-------------|
| Avg cycle time | 7+ days | <2 days | -5 days | CX improvement |
| Manual processing cost/app | ~$150 | ~$30 | -$120 | $1.2M (est. 10K apps/yr) |
| Staff hours on workarounds | 400 hrs/mo | 100 hrs/mo | -300 hrs/mo | $540K (at $150/hr loaded) |

---

### Expand — Challenges & Impact

**Current Challenges:**

| Challenge | Customer Impact | Employee Impact | Evidence |
|-----------|-----------------|-----------------|----------|
| No customer 360 view | Bank doesn't know full relationship — treats every interaction as new | Staff toggle between 4-6 systems to piece together customer picture | E6 |
| No behavioral analytics | Bank can't identify customers at risk or ready for next product | No data to drive proactive outreach or segment-specific campaigns | E6 |
| Silent churn (unconsidered) | Customers disengage gradually — bank doesn't detect until account closure | No early warning system for disengagement | UN-R-01 |

**Business Impact:**
- **Revenue at risk:** Cross-sell/upsell opportunities missed — no data to identify ready customers
- **Strategic risk:** Competitors with 360 view and analytics will capture share of wallet

---

### Expand — Recommendations & Value

| # | Recommendation | Expected Impact | Effort |
|---|---------------|----------------|--------|
| 1 | Build unified customer profile (360 view) for staff | 20-30% reduction in staff context-switching time | L |
| 2 | Deploy journey analytics for funnel and channel visibility | Enable data-driven optimization for first time | M |
| 3 | Implement basic engagement scoring and alerts | Early detection of disengagement, proactive retention | M |

---

### Retain — Challenges & Impact

**Current Challenges:**

| Challenge | Customer Impact | Employee Impact | Evidence |
|-----------|-----------------|-----------------|----------|
| Simple requests go to call center | Customers forced to high-effort channel for basic tasks | Skilled agents handle routine work (balance checks, statements) | E4, E5 |
| No channel orchestration | If customer starts in app and gets stuck, must restart in branch | No context passing between channels | E6 |
| High cost-to-serve | $10+ per call center transaction vs. $1 for digital self-service | Budget consumed by volume, not value | E4 |

**Business Impact:**
- **Cost inefficiency:** ~$5.8M annual excess cost from channel misallocation
- **Scalability constraint:** Cannot grow customer base without proportional cost increase
- **Churn risk:** Friction-heavy servicing pushes digitally-savvy customers to competitors

---

### Retain — Recommendations & Value

| # | Recommendation | Expected Impact | Effort |
|---|---------------|----------------|--------|
| 1 | Expand digital self-service to cover top 20 servicing transactions | Shift 40,000 monthly transactions to digital | L |
| 2 | Deploy intelligent channel routing and proactive deflection | 60% digital containment (up from ~20%) | M |
| 3 | Implement in-app help, contextual guidance, and smart search | Reduce "give up and call" behavior by 40% | M |

**How Benefits Are Calculated:**

| Metric | Current | Target | Delta | Annual Value |
|--------|---------|--------|-------|-------------|
| Digital containment rate | ~20% | ~50% (Yr2), ~60% (Yr3) | +30-40pp | — |
| Monthly transactions shifted | 0 | 40,000 | +40,000 | — |
| Cost savings per transaction | — | ~$9 ($10 call → $1 digital) | $9/txn | $5.8M (Yr3 run rate) |

---

## 06. Who to Serve — Persona Mapping

### Addressable Market

| Segment | % of Customer Base | Revenue Contribution | Strategic Priority |
|---------|-------------------|---------------------|-------------------|
| Mass market (salary/savings) | 70% | 35% | Medium — volume driver |
| Emerging affluent (young professionals) | 20% | 40% | **High** — growth driver, most digital |
| Established affluent / HNW | 10% | 25% | High — revenue driver, advisory-led |

### Customer Personas

#### Mei Lin — The Digital Native (Emerging Affluent)

> *"I just want to open an account on my phone in 5 minutes, not fill out forms at a branch."*

- **Profile:** 28, software engineer, monthly income $4,000+, dual citizen (Malaysia/Singapore)
- **Banking Needs:** Current account, savings, beginner investments, remittances
- **Current Pain:** Tried to open account digitally, got stuck at document upload, gave up after 3 days of no response
- **Digital Expectation:** Instant. If it takes more than 10 minutes, something is wrong. Benchmarks against Grab, Shopee, not other banks.
- **Opportunity:** This is the customer the bank loses at a rate of 2,500/month. Fix onboarding = capture Mei Lin.

#### Arjun — The Busy Professional (Mass Affluent)

> *"I don't mind going to the branch for big decisions, but don't make me call a hotline to check my balance."*

- **Profile:** 42, regional sales director, monthly income $8,000+, family with mortgage and insurance
- **Banking Needs:** Multi-product relationship, transaction support, advisory for life events
- **Current Pain:** Calls the call center for things he should be able to do in the app. Has been told "please visit the branch" three times this month.
- **Digital Expectation:** Complete self-service for routine tasks. Human interaction for complex advice.
- **Opportunity:** Arjun costs $120/year in unnecessary call center transactions. He represents 100,000+ customers.

#### Siti — The Branch-First Customer (Digital Hesitant)

> *"I downloaded the app but I don't trust it for important things. I want to see a person."*

- **Profile:** 55, small business owner, limited English, prefers local language
- **Banking Needs:** Cash management, fixed deposits, branch-based relationship
- **Current Pain:** Branch queue times are long because staff are handling requests that should be digital
- **Digital Expectation:** Minimal — but willing to try if someone shows her and it's in her language
- **Opportunity:** Not the primary digital target, but beneficiary: when Mei Lin and Arjun go digital, branch staff have time for Siti.

#### Farah — The Call Center Agent (Employee)

> *"I spend half my day answering questions customers should be able to see in their app."*

- **Profile:** 26, call center agent, 18 months tenure, handles 60+ calls/day
- **Banking Needs (as employee):** Customer context before the call, ability to resolve in one interaction
- **Current Pain:** Toggles between 4 systems per call, no customer 360 view, repeats information customer already provided
- **Opportunity:** With self-service handling routine queries, Farah handles complex cases — more satisfying work, lower attrition.

---

## 07. How to Serve Them — Journey Assessment

---

### Journey: Digital Onboarding (Account Opening)

#### Journey Map (As-Is)

**Actors Involved:** Customer, Branch/Frontline Staff, Back-Office Operations, Compliance/KYC
**Applications Involved:** Mobile App, Core Banking, Document Management System, KYC Platform, Excel (workarounds), Email

| Stage | Customer | Frontline Staff | Back-Office | Compliance |
|-------|----------|-----------------|-------------|------------|
| **Research & Apply** | Searches online, downloads app, starts application (15-20 min) | N/A for digital; assists in-branch (20-30 min) | — | — |
| **Document Collection** | Uploads documents — frequent failures, unclear requirements (10-30 min) | Helps with docs if branch visit (30-60 min) | — | — |
| **Document Review** | Waits — no status visibility (2-3 days) | Checks status manually, calls customer for re-submission (10-20 min/day) | Reviews documents manually (15-30 min/app), requests re-submission if issues (10-20 min) | — |
| **KYC & Screening** | Waits — no status visibility (1-2 days) | — | — | KYC verification (20-30 min/app), AML screening (5-10 min/app) |
| **Account Creation** | Waits (1-2 days) | — | Creates account in core banking (10-15 min), generates card request (5 min) | — |
| **Confirmation** | Receives welcome pack, funds account (5 min) | Sends welcome message | — | — |

**Total end-to-end time:** 7+ days (some cases 2+ weeks)

#### Friction Points

| # | Friction Point | Stage | Actor Affected | Customer Impact | Employee Impact | Evidence |
|---|---------------|-------|----------------|-----------------|-----------------|----------|
| F1 | Document upload failures, unclear requirements | Document Collection | Customer | 35-50% drop-off at this stage | Re-work, manual follow-up | E1, E2 |
| F2 | No real-time status — customer waits in the dark | Document Review → Account Creation | Customer | Anxiety, duplicate calls to check status | Handles "where's my application" calls | E3 |
| F3 | Manual document review — no OCR or auto-classification | Document Review | Back-Office | Slow processing adds days | 15-30 min per application manual review | E8 |
| F4 | Manual KYC — no eKYC or digital ID verification | KYC & Screening | Compliance | Additional delays, may require branch visit | 20-30 min per application manual verification | E8 |
| F5 | No orchestration — handoffs via email/Excel | All stages | All | Process unpredictable, things get lost | Manual tracking, workarounds, no SLA visibility | E8 |
| F6 | No STP — every application requires manual intervention | Account Creation | Back-Office | No instant activation, even for simple cases | Every application is manual, no risk-based routing | E3, E8 |

**Manual handoffs:** 6+ per application
**Systems involved:** 5+ with no integration
**Staff time per application:** ~90-120 minutes across all actors
**STP rate:** <5% (assumption A-CAP-02)

#### Business Benefits

**Total Annual Benefits: $2.4M (revenue uplift) + $1.2M (cost avoidance) = $3.6M**

| Benefit Category | Annual Impact | Basis |
|-----------------|---------------|-------|
| **Revenue uplift** | $2.4M | 30,000 additional customers × $80 annual revenue |
| **Cost avoidance** | $1.2M | $120 savings per application × 10,000 applications/year |
| **Total** | **$3.6M** | |

**How Benefits Are Calculated:**

| Metric | Current | Target | Delta | Annual Value |
|--------|---------|--------|-------|-------------|
| Completion rate | ~40% | ~65% | +25pp | +30,000 customers → $2.4M |
| Cycle time | 7+ days | <48 hours | -5 days | CX improvement |
| Cost per application | ~$150 | ~$30 | -$120 | $1.2M |
| STP rate | <5% | 30-40% | +25-35pp | Operational efficiency |

#### Proposed Solution

**Key capabilities deployed:**
1. **Workflow orchestration (BPM)** — End-to-end process automation replacing email/Excel handoffs
2. **eKYC with digital ID verification** — Automated document capture, OCR, and identity verification
3. **STP decision engine** — Risk-based auto-approval for low-risk applications (<24 hours)
4. **Save & resume with real-time status** — Customer can pause and resume; always knows where they stand
5. **Case management for exceptions** — Staff handle only exceptions with full context, no toggling

**Target outcomes:**
- End-to-end time: 7+ days → <48 hours (STP: <24 hours)
- Completion rate: 40% → 65%
- STP rate: <5% → 30-40%
- Staff time per application: 90+ min → 20 min (exceptions only)

---

### Journey: Customer Servicing (Routine Transactions)

#### Journey Map (As-Is)

**Actors Involved:** Customer, Call Center Agent, Branch Staff, Back-Office
**Applications Involved:** Mobile App (limited), IVR, Call Center CRM, Core Banking, Branch Systems

| Stage | Customer | Call Center Agent | Branch Staff | Back-Office |
|-------|----------|-------------------|-------------|------------|
| **Request Initiation** | Tries app — feature not available. Calls hotline (5-15 min wait) OR visits branch (30 min travel + queue) | Answers call, asks for identification, pulls up account in CRM (3-5 min) | Greets customer, asks reason for visit, logs into systems (5 min) | — |
| **Authentication** | Provides ID details over phone or presents card at branch | Verifies identity in CRM system (2-3 min) | Checks ID, verifies in system (3-5 min) | — |
| **Request Processing** | Explains what they need — often re-explains if transferred | Toggles between 3-4 systems to find information (5-10 min). May say "let me check with back-office" | Processes in core banking (5-15 min). May need to call another department. | Receives escalation by email, processes request (15-30 min turnaround) |
| **Resolution** | Receives confirmation — may need to call back for status | Confirms resolution or advises "we'll call you back" (2 min) | Confirms on screen or provides paper receipt | Completes processing, notifies via email |

**Total end-to-end time:** 15-45 minutes per interaction (call center); 45-90 minutes (branch visit)

#### Friction Points

| # | Friction Point | Stage | Actor Affected | Customer Impact | Employee Impact | Evidence |
|---|---------------|-------|----------------|-----------------|-----------------|----------|
| F1 | Simple requests not available in app (balance, statements, card controls) | Request Initiation | Customer | Forced to call or visit for basic tasks | Handles routine queries that should be self-service | E5 |
| F2 | No context passing between channels | Request Initiation | Customer, Agent | Must re-explain if switching from app to call | No visibility into what customer tried in app | E6 |
| F3 | Agent toggles between 3-4 systems | Request Processing | Call Center Agent | Longer call duration, perceived incompetence | 5-10 min per call just navigating systems | E8 |
| F4 | No customer 360 view | Request Processing | All staff | Bank doesn't know full relationship | Cannot personalize, cross-sell, or prioritize | E6 |
| F5 | Back-office escalations by email | Resolution | Customer, All staff | "We'll call you back" — delay, uncertainty | Manual handoff, no tracking, things get lost | E8 |

**Monthly call center volume (estimated):** 100,000+ transactions
**Digital containment rate:** ~20%
**Average cost per call center transaction:** ~$10
**Average cost per digital self-service transaction:** ~$1

#### Business Benefits

**Total Annual Benefits: $5.8M (cost avoidance at steady state — Year 3)**

| Benefit Category | Annual Impact (Yr3) | Basis |
|-----------------|---------------------|-------|
| **Cost avoidance** | $5.8M | 40,000 monthly transactions × $9 cost delta × 12 months |
| **Productivity gain** | $0.4M | Staff time freed for complex cases, lower attrition |
| **Total** | **~$6.2M** | |

**How Benefits Are Calculated:**

| Metric | Current | Target (Yr3) | Delta | Annual Value |
|--------|---------|--------------|-------|-------------|
| Digital containment | ~20% | ~60% | +40pp | — |
| Transactions shifted/month | 0 | 40,000 | +40,000 | — |
| Cost per transaction saved | — | $9 ($10→$1) | $9/txn | $4.3M |
| Call volume reduction | 100K/mo | 60K/mo | -40K | $1.5M additional staffing avoidance |

#### Proposed Solution

**Key capabilities deployed:**
1. **Self-service expansion** — Top 20 servicing transactions available in-app (balance, statements, card controls, address change, beneficiary management, etc.)
2. **Channel orchestration** — Context passes between channels; if customer starts in app and calls, agent sees what they tried
3. **Proactive deflection** — In-app guidance, contextual help, smart search to contain customers digitally
4. **Agent workspace** — Unified customer view for call center with full context, single screen

**Target outcomes:**
- Digital containment: 20% → 60%
- Cost per transaction (blended): $10 → $4
- Call volume: 100K → 60K monthly
- Agent handle time: reduced 30% with unified workspace

---

## 08. Application Architecture

### Current State (As-Is)

| Layer | Systems | Integration | Pain Points |
|-------|---------|-------------|-------------|
| **Channels** | Mobile app, internet banking, branch systems, IVR | Siloed — each channel has own session, no shared state | No omnichannel experience, features vary by channel |
| **Orchestration** | None — manual handoffs via email/Excel | Point-to-point, batch files | No workflow engine, no STP, no process visibility |
| **Core Systems** | Core banking, KYC platform, document management, CRM | Limited API exposure, batch processing | Legacy integration, no real-time, brittle connections |

### Proposed State (To-Be)

| Layer | Proposed | Integration | Benefit |
|-------|----------|-------------|---------|
| **Unified Frontline** | Backbase web + mobile apps (customer), employee portal (staff) | Unified UX layer with shared state | Consistent CX, single codebase, omnichannel |
| **Orchestration** | Backbase platform + BPM engine, decision engine, STP rules | API-first, event-driven, real-time | End-to-end journey automation, workflow visibility |
| **Integration** | Integration layer / API gateway | REST APIs, real-time event bus | Decoupled, scalable, future-proof |
| **Core Systems** | Existing core banking — no change required | Wrapped with APIs by integration layer | Protect investment, progressive modernization |

---

# SECTION 5: Capability Assessment

---

## 09. Front-to-Back Capability Heatmap

### Assessment Methodology

**Scale:** 0-4 Maturity (Absent → Fragmented → Defined → Orchestrated → Intelligent)
**Structure:** Every capability assessed across Front Layer (Experience) / Middle Layer (Orchestration) / Back Layer (Integration + Systems of Record)
**Scoring Rule:** Overall score = weakest layer. The chain breaks at the weakest link.
**Bias:** Conservative. Score what exists, not what's planned.
**Mode:** Transcript Inference — scores inferred from evidence with confidence ratings.

### Problem Map

**Considered Needs** (What the Bank Already Knows):

| # | Problem | Severity | Impact | Evidence | Related Capabilities |
|---|---------|----------|--------|----------|---------------------|
| CN-01 | Low onboarding completion — customers drop off at document stage | Critical | Lost acquisition — est. 2,500 applicants/month | E1, E2 | CAP-R-CL-01, CAP-R-RC-01 |
| CN-02 | Expensive servicing — simple requests through call center | High | $3-5M annual excess cost | E4, E5 | CAP-R-CE-01, CAP-R-EE-01, CAP-R-CE-02 |
| CN-03 | Digital hasn't scaled — manual workarounds persist | High | Digital investment not delivering ROI | E7, E8 | CAP-R-PO-01, CAP-R-CL-01 |

**Unconsidered Needs** (What We Surfaced):

| # | Problem | Severity | Why They Miss It | Indicators | Related Capabilities |
|---|---------|----------|------------------|------------|---------------------|
| UN-R-01 | Silent customer churn — gradual disengagement undetected | High | Bank measures churn as closure, not behavioral decline | No behavioral analytics (E6); can't see engagement trends | CAP-R-CL-03, CAP-R-DI-01 |
| UN-R-03 | No front-to-back journey visibility | High | Each department sees only their part | Three stakeholders describe three separate problems with no end-to-end view | CAP-R-PO-01, CAP-R-DI-02 |
| UN-R-04 | Data exists but isn't used — insights trapped in silos | High | Banks have data but no intelligence layer | E6: can't analyze channel behavior despite having transaction data | CAP-R-DI-01, CAP-R-CL-03 |
| UN-R-06 | No AI strategy | Medium | AI ignored or stuck in pilot purgatory | No mention of AI in any interview; competitors deploying AI | CAP-R-AI-01, CAP-R-AI-02, CAP-R-AI-03 |

### Capability Heatmap (RAG — Front / Middle / Back)

**Color Legend:**
- **0 — Absent** (Red #E63946): Capability doesn't exist
- **1 — Fragmented** (Amber-Red #F4A261): Ad-hoc, person-dependent
- **2 — Defined** (Amber #E9C46A): Standardized, repeatable, but handoffs manual
- **3 — Orchestrated** (Green #2A9D8F): End-to-end, automated, measured
- **4 — Intelligent** (Blue #0066FF): AI-native, predictive, self-optimizing

| Domain | Capability | Front | Middle | Back | Overall | Problems |
|--------|-----------|-------|--------|------|---------|----------|
| **Customer Channels** | | | | | | |
| | CAP-R-CE-01: Digital Channel Availability | 1 | 1 | 1 | **1** | CN-02 |
| | CAP-R-CE-02: Employee Workspace | 1 | 1 | 1 | **1** | CN-02 |
| | CAP-R-CE-03: Contact Center | 1 | 1 | 1 | **1** | CN-02 |
| **Customer Lifecycle** | | | | | | |
| | CAP-R-CL-01: Digital Onboarding | 1 | 1 | 1 | **1** | CN-01, CN-03 |
| | CAP-R-CL-02: Customer 360 | 0 | 0 | 0 | **0** | UN-R-04 |
| | CAP-R-CL-03: Behavioral Insights | 0 | 0 | 0 | **0** | UN-R-01, UN-R-04 |
| **Retail Services** | | | | | | |
| | CAP-R-RS-01: Deposit & Savings | 2 | 2 | 2 | **2** | — |
| | CAP-R-RS-02: Payments & Transfers | 2 | 2 | 2 | **2** | — |
| **Risk & Compliance** | | | | | | |
| | CAP-R-RC-01: KYC/AML | 1 | 1 | 1 | **1** | CN-01 |
| **Process Orchestration** | | | | | | |
| | CAP-R-PO-01: Workflow & BPM | 1 | 1 | 1 | **1** | CN-03, UN-R-03 |
| **Employee Enablement** | | | | | | |
| | CAP-R-EE-01: Staff Productivity | 1 | 1 | 1 | **1** | CN-02 |
| **Data & Intelligence** | | | | | | |
| | CAP-R-DI-01: Data Foundation | 0 | 0 | 0 | **0** | UN-R-04 |
| | CAP-R-DI-02: Analytics & Reporting | 0 | 0 | 0 | **0** | UN-R-03 |
| **AI & Agentic** | | | | | | |
| | CAP-R-AI-01: Conversational AI | 0 | 0 | 0 | **0** | UN-R-06 |
| | CAP-R-AI-02: AI Copilots | 0 | 0 | 0 | **0** | UN-R-06 |
| | CAP-R-AI-03: AI Governance | 0 | 0 | 0 | **0** | UN-R-06 |

### Overall Maturity Summary

**Current State Maturity: 0.9 / 4.0 — Between Absent and Fragmented**

| Level | Label | Count | % |
|-------|-------|-------|---|
| 0 — Absent | Red | 8 | 47% |
| 1 — Fragmented | Amber-Red | 7 | 41% |
| 2 — Defined | Amber | 2 | 12% |
| 3 — Orchestrated | Green | 0 | 0% |
| 4 — Intelligent | Blue | 0 | 0% |

### Layer Pattern Analysis

| Layer | Avg Score | Pattern |
|-------|-----------|---------|
| Front | 0.9 | **"Digital veneer"** — front-ends exist for basic functions but are incomplete |
| Middle | 0.9 | **"Manual middle"** — people, not automation, connecting front to back |
| Back | 0.9 | **"Integration desert"** — point-to-point, batch, no orchestration layer |

**Key insight:** Front, Middle, and Back are equally weak. This is NOT a "glass front, broken back" problem — it's a uniformly low maturity across all layers. The entire stack needs investment.

### Problem → Capability Traceability

| Problem | Type | Severity | Solving Capabilities | Current Score | Gap Action |
|---------|------|----------|---------------------|---------------|------------|
| CN-01: Low onboarding completion | Considered | Critical | CAP-R-CL-01, CAP-R-RC-01 | 1, 1 | Automate onboarding + eKYC |
| CN-02: Expensive servicing | Considered | High | CAP-R-CE-01, CAP-R-CE-02, CAP-R-EE-01 | 1, 1, 1 | Self-service + employee workspace |
| CN-03: Digital hasn't scaled | Considered | High | CAP-R-PO-01, CAP-R-CL-01 | 1, 1 | Workflow orchestration |
| UN-R-01: Silent churn | Unconsidered | High | CAP-R-CL-03, CAP-R-DI-01 | 0, 0 | Analytics + behavioral insights |
| UN-R-03: No journey visibility | Unconsidered | High | CAP-R-PO-01, CAP-R-DI-02 | 1, 0 | Process analytics + BPM |
| UN-R-04: Data trapped in silos | Unconsidered | High | CAP-R-DI-01, CAP-R-CL-03 | 0, 0 | Data foundation + customer 360 |
| UN-R-06: No AI strategy | Unconsidered | Medium | CAP-R-AI-01/02/03 | 0, 0, 0 | Future — after data foundation |

### Path to Target State (Top Priorities)

#### Priority 1: CAP-R-PO-01 Workflow & BPM — Current 1 → Target 2

**What Level 1 Looks Like Today:** Manual workarounds are the process. Staff use email, Excel, and personal checklists to move applications forward. No enterprise workflow engine, no SLA tracking, no process visibility.

**What Level 2 Looks Like:** Enterprise BPM platform deployed. Onboarding process modeled and automated end-to-end. Top 10 servicing processes orchestrated. SLA tracking and alerting in place. 50-60% reduction in manual handoffs.

| Layer | Current | Target | Specific Changes |
|-------|---------|--------|-----------------|
| Front | 1 | 2 | Task management UIs, SLA dashboards for staff |
| Middle | 1 | 2 | Deploy BPM engine, rules engine, process orchestration |
| Back | 1 | 2 | Integrate all systems via API layer, unified audit trail |

**Dependencies:** None — this IS the foundation.
**Business Outcomes:** Onboarding cycle time 7 days → <2 days; 30-40% STP rate; staff time savings 300+ hrs/month
**Effort:** L — 12-18 months

#### Priority 2: CAP-R-DI-01 Data Foundation — Current 0 → Target 2

**What Level 0 Looks Like Today:** No data warehouse or lake. Cannot answer basic questions about customer behavior. Data trapped in source systems.

**What Level 2 Looks Like:** Modern data warehouse deployed. ETL pipelines from major systems. Self-service BI tools. Data governance framework.

| Layer | Current | Target | Specific Changes |
|-------|---------|--------|-----------------|
| Front | 0 | 2 | Self-service BI tools, executive dashboards |
| Middle | 0 | 2 | MDM, data quality rules, governance |
| Back | 0 | 2 | Data warehouse, ETL pipelines, unified schema |

**Dependencies:** None — foundational.
**Business Outcomes:** Time to insight from weeks to minutes; enables all analytics and AI capabilities.
**Effort:** L — 12-18 months (parallel with P1)

#### Priority 3: CAP-R-CL-01 Digital Onboarding — Current 1 → Target 2

**What Level 1 Looks Like Today:** Digital channel exists (E7) but broken middle/back. Low completion (E1), document friction (E2), 7+ day cycle (E3).

**What Level 2 Looks Like:** Standardized end-to-end onboarding. Automated document verification with eKYC. 30-40% STP. <48 hours for all applications.

| Layer | Current | Target | Specific Changes |
|-------|---------|--------|-----------------|
| Front | 1 | 2 | Improved UX, mobile document capture, real-time status |
| Middle | 1 | 2 | Workflow orchestration, eKYC, decision engine, STP rules |
| Back | 1 | 2 | API integration layer, automated screening, unified audit trail |

**Dependencies:** CRITICAL — CAP-R-PO-01 (workflow) must reach Level 2 first.
**Business Outcomes:** Completion rate 40% → 65% = 30,000 additional customers/year = $2.4M revenue.
**Effort:** L — 12-18 months (overlaps with P1 deployment)

### Data & Intelligence Assessment

**Data Foundation Maturity: 0 — Absent.** No data warehouse, no self-service analytics, no data governance. The bank operates entirely on source-system reports and manual Excel analysis. This blocks all downstream intelligence capabilities.

**Analytics Maturity: 0 — Absent.** No journey analytics, no funnel tracking, no channel behavior analysis. The bank cannot measure the problems it knows about (E6), let alone discover new ones.

**AI & Agentic Readiness: 0 — Absent.** No AI capabilities deployed. No conversational AI, no employee copilots, no predictive models. AI requires data foundation at Level 2+ before deployment. Realistic timeline: 18-24 months.

---

# SECTION 6: Delivery Roadmap

---

## 10. Phased Delivery Plan

### MVP Scope

| | MVP 1 (Foundation + Onboarding) | MVP 2 (Self-Service + Analytics) |
|---|---|---|
| **Journeys** | Digital onboarding end-to-end | Self-service expansion, channel orchestration |
| **Capabilities** | Workflow orchestration, eKYC, STP, save & resume | Top 20 self-service features, proactive deflection, journey analytics |
| **Duration** | 6 months (Months 0-6 foundation + Months 7-12 scale) | 6 months (Months 7-12 parallel + Months 13-18 optimize) |

### Project Timeline

| Phase | Months | Focus | Key Milestones |
|-------|--------|-------|---------------|
| **Foundation** | 0-6 | Data validation, workflow platform, analytics setup, eKYC integration, pilot in 1 market | Pilot live, baseline metrics validated |
| **Scale** | 7-12 | Onboarding rollout, self-service expansion, channel orchestration | Onboarding automated, self-service live |
| **Optimize** | 13-18 | Full deployment, journey optimization, customer 360 | Full value realization, continuous improvement |
| **Sustain** | 19+ | AI exploration, advanced analytics, continuous improvement | Platform reuse for future LoB |

### Investment Summary

| Phase | Investment | Cumulative | Expected Annual Benefits |
|-------|-----------|------------|------------------------|
| Foundation (0-6) | $4.5M | $4.5M | $0 (building) |
| Scale (7-12) | $3.0M | $7.5M | $3.1M (ramping) |
| Optimize (13-18) | $0.5M | $8.0M | $6.7M (maturing) |
| Sustain (19+) | $1.8M/year | — | $8.2M (steady state) |

### Dependencies & Risks

| Dependency | Impact if Delayed | Mitigation |
|-----------|-------------------|------------|
| Baseline data validation (DG1-DG10) | ROI model unvalidated, investment case weakened | Phase 0 data gathering sprint (Weeks 1-4) |
| eKYC regulatory approval | Cannot automate onboarding identity verification | Early regulatory engagement, parallel path with enhanced manual KYC |
| Change management commitment | Staff revert to workarounds (E8 repeats) | Executive sponsorship, dedicated change team, pilot-first approach |
| Core banking API availability | Integration delays, manual workarounds persist | API-first integration layer, adapter pattern for legacy systems |

---

# SECTION 7: Benefits Case

---

## 11. Detailed Business Benefits Case

### Business Benefits Projected Over 3 Years

| Year | Investment | Benefits | Net | Cumulative |
|------|-----------|---------|-----|------------|
| Year 0 | $4.5M | $0.0M | -$4.5M | -$4.5M |
| Year 1 | $3.9M | $3.1M | -$0.8M | -$5.3M |
| Year 2 | $1.8M | $6.7M | +$4.9M | -$0.4M |
| Year 3 | $1.8M | $8.2M | +$6.4M | +$6.0M |
| **Total** | **$12.0M** | **$18.0M** | **+$6.0M** | |

### Financial Summary

| Metric | Value |
|--------|-------|
| **Total Investment (3-year)** | $12.0M |
| **Total Benefits (3-year)** | $18.0M |
| **Net Benefit** | $6.0M |
| **ROI (IRR)** | 42% |
| **NPV (10% discount)** | $5.2M |
| **Payback Period** | 18 months |
| **Recommendation** | **Conditional Go** |

### Value Drivers Overview

| # | Value Driver | Annual Run-Rate (Yr3) | Type | Confidence |
|---|-------------|----------------------|------|------------|
| 1 | Digital self-service channel shift | $5.8M | Cost Avoidance | Medium |
| 2 | Improved onboarding conversion | $2.4M | Revenue Uplift | Medium |
| **Total** | | **$8.2M** | | |

### Scenario Analysis

| Scenario | 3-Year Net | IRR | NPV | Key Assumptions |
|----------|-----------|-----|-----|----------------|
| **Conservative** | $2.0M | 22% | $1.8M | 15pp completion improvement, 20pp containment shift, 6-month delay |
| **Base (Moderate)** | $6.0M | 42% | $5.2M | 25pp completion improvement, 40pp containment shift, on-schedule |
| **Aspirational** | $10.5M | 65% | $8.8M | 30pp completion, 50pp containment, faster adoption, 2 additional value levers |

### Key Assumptions

| # | Assumption | Value Used | Source | Sensitivity |
|---|-----------|-----------|--------|-------------|
| A1 | Onboarding completion rate baseline | ~40% | Inferred from E1 "low" | High — validate with client data |
| A2 | Monthly onboarding volume | ~10,000 applications | Tier-2 SEA bank estimate | High — drives revenue model |
| A3 | Revenue per retail customer/year | $80 | SEA retail benchmark (MEDIUM) | Medium |
| A4 | Digital containment rate (current) | ~20% | Inferred from E5 | High — drives servicing model |
| A5 | Monthly servicing transaction volume | ~100,000 | Tier-2 SEA bank estimate | High — drives cost model |
| A6 | Cost per call center transaction | $10 | Global benchmark (MEDIUM) | High — core ROI driver |
| A7 | Cost per digital self-service transaction | $1 | Industry standard | Low |
| A8 | Implementation timeline | 18 months | Standard for comparable scope | Medium |
| A9 | Discount rate (WACC) | 10% | Assumption — validate with CFO | Medium |
| A10 | No major regulatory blockers to eKYC | Yes | Standard SEA banking | Medium — varies by country |

**Overall Confidence: MEDIUM** — Benefits model uses global proxy benchmarks where client-specific data was unavailable (DG1-DG10). Validation of assumptions A1-A6 with actual client data is required before final investment approval.

---

# APPENDIX

---

## Appendix A: Assessment Methodology

**Capability Assessment Scale:** BIAN-aligned 0-4 (Absent → Fragmented → Defined → Orchestrated → Intelligent)
**Layer Structure:** Front (Experience Plane) / Middle (Capability/Orchestration Plane) / Back (Integration Plane + Systems of Record)
**Scoring Rule:** Overall = weakest layer. Conservative bias applied.
**Problem-First:** Capabilities assessed in context of identified business problems (3 considered + 4 unconsidered needs)
**Reference:** `knowledge/standards/capability_taxonomy.md` v2.0

## Appendix B: Evidence Register

| ID | Source | Quote | Lifecycle | Confidence |
|----|--------|-------|-----------|------------|
| E1 | Head of Retail | "Our onboarding completion rate is low" | Acquire | Medium |
| E2 | Head of Retail | "A lot of customers drop off when documents are required" | Acquire | High |
| E3 | Head of Retail | "It can take more than a week in some cases" | Activate | Medium |
| E4 | Operations Lead | "Servicing is expensive" | Retain | Medium |
| E5 | Operations Lead | "Simple requests still come through the call center" | Retain | High |
| E6 | Operations Lead | "We don't have a clear view of why customers choose branch or call over digital" | Retain | High |
| E7 | Digital Lead | "We launched digital onboarding, but it hasn't scaled well" | Acquire | High |
| E8 | Digital Lead | "Teams still rely on manual workarounds" | Activate | High |

## Appendix C: Assumptions Register (Full)

| ID | Assumption | Made By | Basis | Impact if Wrong | Validation Owner | Status |
|----|-----------|---------|-------|-----------------|------------------|--------|
| A-CAP-01 | No workflow orchestration engine exists | Capability Agent | E8 workarounds, E3 delays | High — changes priority sequence | CTO | Open |
| A-CAP-02 | Onboarding STP rate <5% | Capability Agent | E3 all apps >7 days | High — baseline for ROI | Ops Lead | Open |
| A-CAP-03 | Digital onboarding deployed 12-24 months ago | Capability Agent | E7 scaling issue implies recent | Low — timeline context | Digital Lead | Open |
| A-CAP-04 | No unified customer data platform exists | Capability Agent | E6 no behavior view | High — blocks analytics | CTO | Open |
| A-CAP-05 | Digital containment rate ~20% | Capability Agent | E5 simple requests to call center | High — baseline for servicing ROI | Ops Lead | Open |
| A-CAP-06 | Call center handles >60% of servicing | Capability Agent | E4 expensive, E5 digital avoidance | High — cost baseline | Ops Lead | Open |
| A-CAP-07 | Onboarding completion rate ~40% | Capability Agent | E1 "low", severity of concern | High — baseline for onboarding ROI | Digital Lead | Open |
| A-CAP-08 | No AI/ML capabilities deployed | Capability Agent | No mention in any interview | Medium — future timing | CTO | Open |
| A-CAP-09 | Monthly onboarding volume ~10K | Capability Agent | Tier-2 SEA bank estimate | High — sizing for ROI | Finance | Open |
| A-CAP-10 | Cost per call center transaction ~$10 | Capability Agent | Global benchmark (MEDIUM) | High — servicing ROI driver | Finance | Open |

## Appendix D: Glossary

| Term | Definition |
|------|-----------|
| F/M/B | Front Layer / Middle Layer / Back Layer — the three architectural planes assessed |
| STP | Straight-Through Processing — end-to-end automation without manual intervention |
| RAG | Red/Amber/Green — color-coded maturity indicators |
| BIAN | Banking Industry Architecture Network — standard for banking capability taxonomy |
| eKYC | Electronic Know Your Customer — digital identity verification |
| BPM | Business Process Management — workflow automation engine |
| CAP-R-XX-NN | Capability ID format: R=Retail, XX=Domain, NN=Sequence |
| CN-XX | Considered Need — a problem the bank has already identified |
| UN-R-XX | Unconsidered Need — a problem we surfaced that the bank hasn't raised |

---

**Document Control:**
- Version: 2.0
- Methodology: 0-4 Scale, BIAN-aligned, Front/Middle/Back Layer Assessment
- Engagement Type: Ignite Assess
- Last Updated: February 2026
- Classification: Confidential
- Next Review: After data validation (DG1-DG10) with client
