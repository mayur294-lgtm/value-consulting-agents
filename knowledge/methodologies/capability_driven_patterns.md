# Capability-Driven Decomposition Patterns (Bottom-Up)

## Purpose

This document provides decomposition patterns for ROI exercises that start from a Backbase platform component or offering — not from a bank's problem statement. Use this when someone asks: "What's the value of Grand Central?" or "Build a business case for Managed Hosting."

These components are 2-3 hops removed from a customer outcome. The methodology traces the value chain FROM the capability UP TO business outcomes, then switches to the problem-driven patterns to decompose and size.

**Companion documents:**
- `value_lever_framework.md` — defines the four-link chain (Root Driver → Operational Change → Volume/Rate Impact → Financial Impact)
- `hypothesis_tree_decomposition.md` — problem-driven (top-down) patterns used once the outcome is identified

---

## Methodology

1. **Define the capability** — what it does, not what it's called
2. **Map business functions supported** — what banking operations depend on this capability
3. **Trace value chains** — for each business function, follow the causal chain to a customer or financial outcome (typically 2-3 hops)
4. **Switch to problem-driven patterns** — at the outcome level, apply the relevant Problem Type from `hypothesis_tree_decomposition.md` to decompose and size
5. **Build levers** — apply the four-link chain from `value_lever_framework.md`

The output is the same `lever_candidates.md` format — the hypothesis builder agent uses this document instead of the top-down patterns when the exercise starts from a component.

---

## Pattern 1: Grand Central (Integration & Orchestration Layer)

**What it does:** Connects the Backbase platform to core banking systems, payment hubs, and third-party services. Manages API routing, service orchestration, data transformation, and core connectivity.

### Business Functions → Outcomes

| Business Function | What Grand Central Enables | Outcome (1-2 hops) | Problem Type | Value Type |
|---|---|---|---|---|
| **API management & routing** | All customer-facing digital journeys depend on it — every transaction, every data fetch | Digital banking availability → digital adoption → revenue/cost | Type 3 | Enabler (underpins other levers) |
| **Core banking connectivity** | Real-time account data, transaction processing | Instant balance visibility, real-time payments → CX → retention | Type 1 (Branch B) | Revenue protection |
| **Service orchestration** | Multi-step workflows: onboarding, lending, payments | STP for complex processes → processing cost reduction | Type 2 (Branch A/B) | Cost avoidance |
| **Integration simplification** | Fewer point-to-point integrations, standardized patterns | Lower IT maintenance burden → IT FTE cost avoidance | Type 2 (Branch D) | Cost avoidance |
| **Marketplace connectivity** | Plugin third-party services (eKYC, credit scoring, payment hubs) | Faster time to market for new capabilities → competitive positioning | Type 3 (Branch C) | Revenue acceleration |

### Direct Value Levers

**Lever: IT Integration Cost Reduction**
- Root Driver: Bank maintains N point-to-point integrations, each requiring dedicated maintenance
- Operational Change: Grand Central consolidates to a single integration layer with standardized API patterns
- Volume/Rate Impact: Integration points reduced from N to 1 hub; maintenance FTEs reduced proportionally
- Financial Impact Direction: IT FTE cost avoidance + reduced vendor middleware licensing

**Lever: Platform Reliability → Digital Channel Uptime**
- Root Driver: Point-to-point integrations create cascading failure risk; outages impact digital channels
- Operational Change: Grand Central provides circuit breakers, retry logic, failover patterns
- Volume/Rate Impact: Reduction in customer-facing outage minutes per year
- Financial Impact Direction: Revenue protection from avoided outages + customer retention

**Lever: Time to Market for New Services**
- Root Driver: Adding a new third-party service (e.g., eKYC provider) requires custom integration work (weeks-months)
- Operational Change: Grand Central marketplace enables plug-in integration (days-weeks)
- Volume/Rate Impact: Integration time reduced from X weeks to Y days per new service
- Financial Impact Direction: Revenue acceleration from earlier launches; IT development cost avoidance

### Sizing Guidance

Grand Central's value is primarily **cost avoidance and enablement** — it doesn't directly generate revenue. When sizing:
- IT integration costs are engagement-specific (requires IT landscape discovery)
- Use the tech rationalization pattern from `knowledge/learnings/roi_models/tech_rationalization_decommission.md` for legacy replacement cases
- Cross-reference with CIO/CTO stakeholder framing from `agents/definitions/roi.md`

---

## Pattern 2: Flow Foundation / APA (Process Automation & Orchestration)

**What it does:** Workflow automation, rules-based decisioning (DMN), straight-through processing, exception routing. APA extends this with agentic/AI-driven process automation.

### Business Functions → Outcomes

| Business Function | What It Enables | Outcome | Problem Type | Value Type |
|---|---|---|---|---|
| **Automated decisioning** | Credit scoring, KYC screening, fraud detection without human intervention | Higher STP rates → lower processing cost | Type 2 (Branch A/B) | Cost avoidance |
| **Workflow orchestration** | Multi-step processes (onboarding, lending) with parallel task execution | Faster cycle times → better CX → conversion | Type 5 (Branch B), Type 1 (Branch A) | Revenue + Cost |
| **Exception routing** | Only complex cases reach human reviewers | FTE productivity gain → hiring avoidance | Type 4 (Branch A/B) | Cost avoidance |
| **Document processing** | Automated classification, data extraction, verification | Back office time reduction | Type 2 (Branch B) | Cost avoidance |
| **Rules engine** | Suitability checks, compliance rules, approval logic | Compliance automation → compliance FTE savings | Type 2 (extend) | Cost avoidance |

### Direct Value Levers

**Lever: STP Rate Improvement**
- Root Driver: Bank's current STP rate is X% — remaining applications require manual processing
- Operational Change: Flow Foundation automates decisioning and routing; only exceptions require human review
- Volume/Rate Impact: STP rate improves from X% to Y% (gap-based: current vs BIC >85%)
- Financial Impact Direction: (Applications shifted to STP) × (manual processing cost per application)
- Benchmark: STP rates Poor <50%, Average 50-70%, BIC >85%

**Lever: Processing Cycle Time Reduction**
- Root Driver: End-to-end processing takes X hours/days due to sequential manual steps
- Operational Change: Flow Foundation enables parallel task execution, automated hand-offs
- Volume/Rate Impact: Processing time reduced from X to Y (typically 40-75% reduction)
- Financial Impact Direction: FTE time saved × hourly rate × annual volume; plus revenue acceleration

**Lever: Compliance Automation**
- Root Driver: Manual compliance checks (KYC/AML, suitability, regulatory) consume X FTEs
- Operational Change: Rules engine automates standard checks; human review for exceptions only
- Volume/Rate Impact: Compliance review time reduced by 40-65% per review
- Financial Impact Direction: Compliance FTE cost avoidance

### Sizing Guidance

Flow Foundation/APA value scales with **transaction volume** — high-volume banks see larger absolute savings. Key inputs needed:
- Annual application/transaction volumes by product
- Current STP rate (or time per application as proxy)
- Back-office FTE count and blended hourly rate
- Current number of manual handoffs per process

---

## Pattern 3: Managed Hosting / Cloud Operations

**What it does:** Infrastructure management, security, compliance (SOC2, ISO27001), availability/DR, deployment/release management — delivered as a managed service.

### Business Functions → Outcomes

| Business Function | What It Enables | Outcome | Problem Type | Value Type |
|---|---|---|---|---|
| **Infrastructure management** | Platform availability without dedicated ops team | IT ops FTE cost avoidance | Type 2 (Branch D) | Cost avoidance |
| **Security & compliance** | Regulatory compliance without in-house security team | Compliance FTE + audit cost avoidance | Type 2 (Branch D) | Cost avoidance |
| **Availability & DR** | Uptime SLAs, disaster recovery, business continuity | Reduced outage risk → revenue protection | Type 1 (Branch B) | Revenue protection |
| **Deployment management** | Continuous delivery of platform updates | Faster time to market, reduced change risk | Type 3 (Branch C) | Revenue acceleration |
| **Predictable cost model** | OpEx vs CapEx, predictable monthly costs | CFO financial planning benefit | Qualitative | Strategic |

### Direct Value Levers

**Lever: IT Operations FTE Avoidance**
- Root Driver: Self-hosted platform requires X dedicated infrastructure/ops staff
- Operational Change: Managed Hosting transfers ops responsibility to Backbase; bank redeploys or avoids hiring
- Volume/Rate Impact: X FTEs no longer needed for platform operations
- Financial Impact Direction: X FTEs × loaded annual cost

**Lever: Compliance & Security Cost Avoidance**
- Root Driver: Meeting SOC2/ISO27001 for self-hosted platform requires dedicated security staff + annual audit costs
- Operational Change: Managed Hosting includes compliance certifications; bank's audit scope reduced
- Volume/Rate Impact: Security FTEs reduced, audit costs reduced
- Financial Impact Direction: FTE cost + audit cost savings

**Lever: Uptime Revenue Protection**
- Root Driver: Self-hosted platform has X hours/year of unplanned downtime → lost digital transactions
- Operational Change: Managed Hosting provides SLA-backed uptime (99.9%+) with failover
- Volume/Rate Impact: Downtime hours reduced from X to Y per year
- Financial Impact Direction: Revenue per digital transaction × transactions lost per hour of downtime × hours saved

### Sizing Guidance

Managed Hosting value depends on **what the bank would otherwise spend** on self-hosting:
- Requires IT infrastructure cost discovery (servers, network, storage, licensing, staff)
- Reference: `tech_rationalization_decommission.md` for comparable infrastructure cost patterns
- Most compelling for mid-size banks without large IT ops teams
- CFO framing: CapEx → OpEx shift, predictable cost model

---

## Pattern 4: Data Foundations (Unified Data & Analytics Layer)

**What it does:** Single customer view across products/channels, behavioral analytics, propensity models, decisioning data infrastructure, reporting.

### Business Functions → Outcomes

| Business Function | What It Enables | Outcome | Problem Type | Value Type |
|---|---|---|---|---|
| **Single customer view** | Unified profile across products, channels, interactions | Better targeting → higher conversion; RM productivity → capacity | Type 1 (Branch A/C), Type 4 | Revenue + Cost |
| **Behavioral analytics** | Propensity models, churn prediction, opportunity detection | Cross-sell uplift, proactive retention | Type 1 (Branch B/C) | Revenue |
| **Decisioning data** | Real-time data for offers, credit scoring, risk assessment | Better offer relevance → higher conversion | Type 1 (Branch C) | Revenue |
| **Reporting & insights** | Operational dashboards, regulatory reporting, performance tracking | Regulatory reporting cost reduction; data-driven decisions | Type 2, Qualitative | Cost + Strategic |
| **Data reconciliation** | Single source of truth eliminates duplicate data, reconciliation errors | Back-office time savings | Type 2 (Branch B) | Cost avoidance |

### Direct Value Levers

**Lever: Cross-Sell Uplift from Propensity Models**
- Root Driver: Bank's cross-sell efforts are untargeted — generic offers to all customers
- Operational Change: Data Foundations provides propensity scoring that identifies which customers are likely to need which products, when
- Volume/Rate Impact: NBA (next-best-action) conversion rate improves from X% to Y%
- Financial Impact Direction: Targeted offers × improved conversion rate × revenue per additional product

**Lever: Churn Prediction → Proactive Retention**
- Root Driver: Bank detects churn only after the customer has left
- Operational Change: Behavioral analytics identifies at-risk customers 30-90 days before churn; triggers proactive retention actions
- Volume/Rate Impact: Retention improvement of 1-3% on at-risk segment
- Financial Impact Direction: Retained customers × annual revenue per customer

**Lever: RM/Advisor Productivity from Single Customer View**
- Root Driver: RM/advisor spends X minutes per client gathering data from multiple systems
- Operational Change: Single customer view provides all data in one screen — eliminates system switching
- Volume/Rate Impact: Data gathering time reduced by 60-80% per client interaction
- Financial Impact Direction: Time saved × interactions/year × RM hourly cost

### Sizing Guidance

Data Foundations value is primarily a **multiplier on other levers** — better data makes onboarding, servicing, cross-sell, and retention levers more effective. When sizing:
- Standalone value (single customer view, data reconciliation) is real but typically smaller
- Multiplier value (enabling better targeting, faster RM prep, smarter retention) is larger but harder to isolate
- Risk: double-counting with levers that already assume Data Foundations is in place
- Best approach: size the direct value (reconciliation savings, RM time savings) as standalone levers; note the multiplier effect qualitatively

---

## Pattern 5: AI & Agentic (Conversational Banking, Intelligence Layer)

**What it does:** Conversational AI for customer self-service, agent assist for call center/branch staff, automated insights generation, next-best-action recommendations.

### Business Functions → Outcomes

| Business Function | What It Enables | Outcome | Problem Type | Value Type |
|---|---|---|---|---|
| **Conversational self-service** | Customers handle inquiries via chat/voice without human agent | Call center deflection → cost avoidance | Type 2 (Branch B) | Cost avoidance |
| **Agent assist** | Real-time suggestions, auto-populated responses, knowledge surfacing for human agents | Handle time reduction → FTE productivity | Type 4 (Branch A) | Cost avoidance |
| **Automated insights** | Meeting summaries, portfolio analysis, anomaly detection for RMs | RM admin time reduction → capacity | Type 4 (Branch A) | Cost avoidance |
| **Next-best-action** | Contextual product recommendations at moments of engagement | Cross-sell conversion uplift | Type 1 (Branch C) | Revenue |
| **Churn prediction** | Early warning signals for at-risk customers | Proactive retention → revenue protection | Type 1 (Branch B) | Revenue |

### Direct Value Levers

**Lever: Conversational Banking Call Deflection**
- Root Driver: X% of call center volume is routine inquiries handleable by AI (balance, transaction history, card status)
- Operational Change: AI & Agentic provides conversational banking — customers get answers without human agent
- Volume/Rate Impact: 20-40% of call volume deflected to AI channel
- Financial Impact Direction: Deflected calls × cost per call
- Benchmark: Call deflection rates 20-60%, cost per call $3-8 (varies by region)

**Lever: Agent Handle Time Reduction**
- Root Driver: Call center agents spend time searching for information, navigating systems
- Operational Change: Agent assist surfaces relevant info, auto-populates responses, suggests resolutions
- Volume/Rate Impact: Average handle time reduced by 15-25%
- Financial Impact Direction: Remaining call volume × time saved per call × agent hourly cost

**Lever: Next-Best-Action Revenue Uplift**
- Root Driver: Cross-sell offers are generic and untimed — low conversion
- Operational Change: AI-driven NBA prompts delivered at contextual moments (in-app, during call, at RM meeting)
- Volume/Rate Impact: NBA prompt conversion rate 5-15% (vs. 1-3% for generic campaigns)
- Financial Impact Direction: Prompts delivered × action rate × revenue per acted prompt
- Benchmark (Wealth): $300-600 avg revenue per acted prompt; 15-30% RM action rate

### Sizing Guidance

AI & Agentic value depends heavily on **channel volumes** and **current automation level**:
- High call volume + low current deflection = large opportunity
- Already have chatbot = incremental improvement, not greenfield
- NBA value requires digital engagement base (customers must be in-app to receive prompts)
- [Client-creditunion-NAM-2025] model reference: AI chatbot engagement valued separately from call center deflection

---

## How to Use These Patterns with the Hypothesis Builder

When the `roi-hypothesis-builder` agent receives a capability-driven exercise:

1. Read this document instead of (or in addition to) `hypothesis_tree_decomposition.md`
2. Select the matching capability pattern
3. Trace the value chains to identify relevant Problem Types
4. For each outcome, switch to the problem-driven patterns to build the MECE tree
5. Build levers using the four-link chain as normal

The output format is the same `lever_candidates.md` — the financial modeler doesn't need to know whether the exercise was problem-driven or capability-driven.

---

*Status: DRAFT — requires validation with consulting team and additional platform component patterns*
*Created: 2026-04-06*
*Components covered: Grand Central, Flow Foundation/APA, Managed Hosting, Data Foundations, AI & Agentic*
*Components not yet covered: Digital Engage (standalone), Identity layer, specific product editions (Essential/Premium/Signature)*
