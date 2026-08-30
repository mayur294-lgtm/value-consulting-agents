# Hypothesis Tree Decomposition Patterns — Problem-Driven (Top-Down)

## Purpose

This document provides the MECE decomposition patterns a consultant or agent uses to build hypothesis trees from a bank's problem statement. It covers 6 problem types with universal Layer 1 math and LOB-specific Layer 2 elaborations.

**Companion documents:**
- `value_lever_framework.md` — defines what a value lever is and how to validate one
- `capability_driven_patterns.md` — bottom-up patterns for platform components (Grand Central, APA, Managed Hosting)

---

## How to Use

1. Identify the bank's problem statement and Backbase's sales objective
2. Match to a **Problem Type** (Section 1) — apply the Layer 1 math decomposition
3. Look up the bank's **LOB** (Section 2) — apply the Layer 2 elaboration for that LOB
4. Attach KPIs from domain benchmarks at each terminal node
5. Nodes with measurable gaps + Backbase capability = value lever candidates (per `value_lever_framework.md`)

---

## Section 1: Problem Type Decompositions (Layer 1 — Universal)

### Type 1: Revenue Growth / Market Share

```
Revenue = Customers × Revenue per Customer

Customers = Existing × (1 − Churn Rate) + New Acquisitions
Revenue per Customer = Products per Customer × Revenue per Product
```

| Branch | Lifecycle Stage | What It Decomposes Into |
|--------|----------------|------------------------|
| New Acquisitions | Acquire | Σ(Channel Applications × Conversion Rate) by channel |
| Churn Reduction | Retain | Customers at Risk × Prevention Rate × Revenue per Customer |
| Products per Customer | Expand | Cross-sell ratio improvement × revenue per additional product |
| Revenue per Product | Activate + Expand | NII + Fee Income + Spread/AUM Fees (varies by LOB) |


### Type 2: Cost Reduction / Cost to Serve

```
Total Operating Cost = Cost to Acquire + Cost to Serve + Cost to Retain + IT/Infrastructure Cost
```

Or channel-based:
```
Total Operating Cost = Σ(Channel Volume × Cost per Interaction) + Fixed Costs
```

| Branch | Lifecycle Stage | What It Decomposes Into |
|--------|----------------|------------------------|
| Cost to Acquire | Acquire | Applications × processing cost per app (staff time + compliance + rework) |
| Cost to Serve | Activate | Σ(Interaction volume × cost per interaction) by channel: branch, call center, digital, back office |
| Cost to Retain | Retain | Retention campaign cost + win-back cost (usually small vs. revenue protection) |
| IT/Infrastructure | Operating Model | Licenses + hosting + support FTEs + integration maintenance + development cost |


### Type 3: Digital Transformation / Channel Adoption

```
Digital Value = Revenue Uplift from Digital + Cost Savings from Channel Migration

Revenue Uplift = Digital Customers × Incremental Revenue vs. Non-Digital
Cost Savings = Migrated Interactions × (Physical Channel Cost − Digital Channel Cost)
```

| Branch | Lifecycle Stage | What It Decomposes Into |
|--------|----------------|------------------------|
| Digital Adoption | Activate | Enrollment → Activation → Active Usage → Feature Utilization (funnel) |
| Channel Migration | Activate | Σ(Transactions migrated × cost delta) by transaction type |
| Digital Revenue | Acquire + Expand | Digital sales volume × revenue per digital sale |
| Experience / Engagement | Retain | Retention uplift from digital engagement + competitive defense |


### Type 4: Operational Efficiency / Productivity

```
Productivity = Output / Input

Where:
  Output = Clients Served (or Transactions Processed, or Revenue Generated)
  Input = FTE Hours Available = Total Hours − Admin Hours − Compliance Hours − System Navigation Hours
```

| Branch | Lifecycle Stage | What It Decomposes Into |
|--------|----------------|------------------------|
| Admin Time Reduction | Activate (employee) | FTEs × current admin % × reduction % — by task category |
| Process Automation | Activate (operations) | Manual processes × time per process × FTE rate × automation rate |
| Capacity Redeployment | Expand | Freed hours → additional clients served → incremental revenue; or FTE hiring avoidance |


### Type 5: Product / Lending Origination

```
Lending Revenue = Applications × Approval Rate × Funded Rate × Average Ticket × Net Margin

Where:
  Net Margin = Interest Spread − Provision Expense + Origination Fee
```

| Branch | Lifecycle Stage | What It Decomposes Into |
|--------|----------------|------------------------|
| Application Volume | Acquire | Branch + digital + pre-approved offers + partner/broker |
| Conversion / Funding | Acquire | Abandonment reduction, faster decisioning, document simplification |
| Portfolio Revenue | Expand | Cross-sell at origination, portfolio quality, refinancing/renewal |


### Type 6: AUM-Based / Advisory Business

```
Revenue = AUM × Blended Fee Rate

Where:
  AUM = Existing AUM × (1 − Attrition) + Net New Assets + Market Appreciation
  Net New Assets = New Client AUM + Existing Client Consolidation
```

| Branch | Lifecycle Stage | What It Decomposes Into |
|--------|----------------|------------------------|
| New Client AUM | Acquire | Prospect pipeline × conversion rate × avg initial AUM |
| Existing Client Consolidation | Expand | Share of wallet improvement × total investable assets × fee rate |
| AUM Retention | Retain | Total AUM × retention improvement × fee rate |
| Advisor/RM Productivity | Activate (employee) | See Type 4 — applied to advisor/RM context |
| Tier Upgrades | Expand | Threshold-eligible clients × upgrade rate × fee rate delta |

---

## Section 2: LOB-Specific Elaborations (Layer 2)

### Retail Banking

**Training data available:** [Client-creditunion-NAM-2025] (USA, Credit Union), SeABank (Vietnam), [Client-retail-ANZ-2025] (Australia), Credins (Albania), [Client-retail-NAM-2025], [Client-creditunion-NAM-2022], Banesco (Bolivia), Banco Caja Social (Colombia)

**Most relevant problem types:** Type 1, Type 2, Type 3, Type 5

**Revenue decomposition:**
```
Retail Revenue = NII on Deposits + NII on Loans + Fee Income + Interchange

NII on Deposits = Deposit Balances × Net Interest Margin (typically 2.0-3.5%)
NII on Loans = Loan Portfolio × Net Spread (consumer: 4-7%, mortgage: 1.5-3%)
Fee Income = Transaction Fees + Overdraft/NSF + Service Charges + Card Fees
Interchange = Active Debit/Credit Cards × Transactions per Card × Interchange Rate
```

**Channel cost structure:**
```
Branch: $4.00-5.00 per interaction (LATAM/APAC lower, NAM higher)
Call Center: $3.00-8.00 per call ($25/hr NAM at 6-7 min AHT; $3-4 LATAM)
Digital: $0.25-0.40 per interaction
Back Office: task-level — volume × time per task × FTE rate
```

**Key KPIs and benchmark ranges:**

| KPI | Poor | Average | Best-in-Class | Source |
|-----|------|---------|--------------|--------|
| Digital active rate | <20% | 25-35% | >60% | benchmarks.md |
| Digital application leakage | >90% | 70-90% | <50% | benchmarks.md |
| Funded account rate | <40% | 40-60% | >80% | benchmarks.md |
| Products per customer | 1.2 | 1.5-2.0 | 2.5-3.2 | roi_levers.md |
| Annual attrition rate | >15% | 10-15% | <5% | roi_levers.md |
| Self-service rate | <40% | 50-65% | >90% | benchmarks.md |
| Onboarding time (digital) | >30 min | 15-30 min | <5 min | benchmarks.md |
| STP rate | <50% | 50-70% | >85% | benchmarks.md |

**Acquisition channels:** Branch walk-in, digital (web + mobile), referral/partner, marketing campaign response

**Product categories:** CASA (checking/savings), term deposits, personal loans, mortgage, credit cards, insurance, investment (if offered)


### SME Banking

**Training data available:** Limited — SME levers referenced in calibrator standard_levers but no full engagement ROI model available.

> **GAP: Need at least 1 complete SME engagement ROI model to validate Layer 2 patterns. Ideally from a bank where SME is primary LOB, not an add-on to retail.**

**Most relevant problem types:** Type 1, Type 2, Type 5

**Revenue decomposition:**
```
SME Revenue = Transaction Banking Fees + Lending Margin + FX/Payments Fees + Merchant Services

Transaction Banking = Active SME Clients × Monthly Fee (typically $200-800/month)
Lending Margin = Working Capital Facilities × Net Spread + Term Loans × Net Spread
```

**How it differs from Retail:**
- Onboarding is fundamentally different: business verification, UBO (Ultimate Beneficial Owner) checks, multi-signatory setup, business document requirements
- Products include working capital, trade finance, merchant acquiring, payroll, invoice financing — not just deposits/loans/cards
- Self-service means different things: payment file uploads, bulk transactions, payroll processing, reconciliation downloads
- Relationship model: typically RM-assisted for larger SMEs, self-service for micro-businesses
- Regulatory: KYB (Know Your Business) requirements add compliance cost layers not present in retail

**Key KPIs (estimated — needs validation with real engagement data):**

| KPI | Poor | Average | Best-in-Class | Confidence |
|-----|------|---------|--------------|------------|
| Digital onboarding time | >30 days | 15-30 days | <7 days | LOW |
| Products per SME client | <3 | 3-5 | >5 | MEDIUM |
| Self-service payment initiation | <40% | 40-60% | >80% | MEDIUM |
| Rework/NIGO rate | >20% | 10-20% | <5% | MEDIUM |
| RM-mediated vs self-service ratio | >70% RM | 50-70% | <40% RM | LOW |


### Commercial Banking

**Training data available:** Seacoast Bank (USA, commercial onboarding), BOK Financial (treasury discovery)

**Most relevant problem types:** Type 1, Type 2, Type 4, Type 5

**Revenue decomposition:**
```
Commercial Revenue = Relationship Revenue per Client × Number of Clients

Relationship Revenue = Transaction Banking + Lending Spread + Treasury Fees + FX + Trade Finance + Advisory

Transaction Banking = Payments Volume × Fee per Payment + Cash Management Monthly Fee
Lending = Committed Facilities × Utilization Rate × Net Spread
Treasury = Services Used × Monthly Fee ($500-2,000/month per service)
```

**How it differs from Retail and SME:**
- Revenue is relationship-driven, not product-count-driven — a single commercial client generates $50K-200K+/year
- Channels are RM relationship + digital portal + API/host-to-host connectivity (not branch/call center)
- Onboarding involves multi-entity structures, complex credit committee approval, legal documentation
- Product penetration means 3-8 products (payments, lending, treasury, trade, FX, escrow, liquidity management)
- Self-service means portal-based payment initiation, balance visibility across entities, user/entitlement management

**Key KPIs:**

| KPI | Poor | Average | Best-in-Class | Source |
|-----|------|---------|--------------|--------|
| Share of wallet | <25% | 25-40% | >60% | benchmarks.md |
| Product penetration | <3 | 3-5 | >8 | benchmarks.md |
| Client retention rate | <85% | 85-92% | >96% | benchmarks.md |
| Portal adoption | <30% | 30-50% | >70% | benchmarks.md |
| Onboarding time (days) | >30 | 15-30 | <7 | benchmarks.md |
| Payment STP rate | <70% | 70-85% | >95% | benchmarks.md |
| Rework/error rate | >20% | 10-20% | <5% | benchmarks.md |
| Revenue per client | <$50K | $50-100K | >$200K | benchmarks.md |

**Seacoast reference data:**
- 1,030 commercial applications/year
- 10 hrs manual onboarding → 6 hrs with Backbase (40% reduction)
- 20% rework rate → 4% target (80% reduction)
- +10% conversion uplift = 103 additional clients × $2,000/month = $2.47M/year


### Corporate Banking

**Training data available:** Minimal — BOK Financial treasury pain points only. No complete ROI model.

> **GAP: Need at least 1 complete corporate banking engagement ROI model. Key differences from commercial: larger, more complex entities, multi-country, syndicated lending, sophisticated treasury. Benchmark data exists in commercial/benchmarks.md but no lever-level models.**

**Most relevant problem types:** Type 1, Type 2, Type 4

**Revenue decomposition:**
```
Corporate Revenue = Lending (syndicated + bilateral) + Transaction Banking + Trade Finance + FX + Capital Markets Advisory

Revenue is concentrated: top 20% of clients typically generate 60-80% of revenue
```

**How it differs from Commercial:**
- Scale: fewer clients (hundreds, not thousands), each worth $500K-5M+/year
- Multi-entity, often multi-country — parent company + subsidiaries across jurisdictions
- Products: syndicated lending, structured trade finance, complex liquidity management (notional pooling, multi-currency sweeps), supply chain finance
- Channels: dedicated senior RM + digital portal + API/SWIFT/host-to-host integration
- Onboarding: months, not days — legal entity verification across jurisdictions, credit committee with board-level approval, complex documentation (ISDA, CSA)
- Self-service: real-time balance visibility across entities/countries, payment initiation with multi-level authorization, trade document upload

**Key KPIs (estimated — needs validation):**

| KPI | Poor | Average | Best-in-Class | Confidence |
|-----|------|---------|--------------|------------|
| Share of wallet | <20% | 20-35% | >50% | LOW |
| Onboarding time | >90 days | 60-90 days | <30 days | LOW |
| Real-time balance visibility | <50% | 50-70% | >90% | MEDIUM |
| Payment STP rate | <70% | 70-85% | >95% | MEDIUM |
| Client retention | <90% | 90-95% | >97% | LOW |
| Revenue per relationship | <$500K | $500K-2M | >$2M | LOW |


### Wealth Management / Private Banking

**Training data available:** [Client-wealth-APAC-2025] (Sri Lanka, 19K wealth clients), Tangerine/Scotiabank (Canada, 138K wealth clients), Goodbody (Ireland), TriState Capital (NAM)

**Most relevant problem types:** Type 6, Type 4, Type 1 (Branch B: churn), Type 2 (compliance costs)

**Revenue decomposition:**
```
Wealth Revenue = AUM × Blended Fee Rate

AUM = Managed (discretionary) + Advisory (non-discretionary) + Execution-only
Fee Rates: Discretionary 65-100 bps | Advisory 35-50 bps | Execution-only 0-25 bps

Also: NII from deposit balances, lending against portfolios, insurance commissions, trust/estate fees
```

**How it differs from Retail:**
- Revenue is AUM-driven, not transaction-driven
- RM productivity is the central cost lever (RMs cost $80K-220K loaded, spend 40-60% on admin)
- Client acquisition is RM-driven or retail-to-wealth upgrade — not branch walk-in
- Retention economics are extreme: losing a $1M client at 75 bps = $7,500/year in perpetuity
- Compliance burden is heavier: suitability checks, periodic KYC refreshes, regulatory reporting
- Multi-entity complexity: banking + investments + insurance + trust (often on separate systems)

**Key KPIs:**

| KPI | Poor | Average | Best-in-Class | Source |
|-----|------|---------|--------------|--------|
| RM admin time % | >55% | 45-55% | <35% | roi_levers.md |
| Share of wallet | <25% | 30-40% | >45% | roi_levers.md |
| Client attrition (annual) | >10% | 5-9% | <5% | roi_levers.md |
| Onboarding time (days) | >30 | 14-30 | <5 | roi_levers.md |
| Onboarding drop-off rate | >40% | 30-45% | <20% | roi_levers.md |
| AUM per departing client | varies | $750K-1.5M | — | roi_levers.md |
| Products per client (banking + wealth) | <2 | 2-3 | >4 | estimated |
| Retail-to-wealth conversion rate | <1% | 1-2% | >3% | roi_levers.md |

**[Client-wealth-APAC-2025] reference data:**
- 19,183 wealth clients, $1.82B AUM, $18.15M revenue (1.0% blended rate)
- 45 RMs, 60% admin time, 41 KYC/AML staff
- 6,000+ unconverted eligible customers (met threshold but not enrolled)
- 4 subsidiaries on separate systems (no unified client view)


### Investing (Digital / Self-Directed)

**Training data available:** [Client-investing-NAM-2026] ([Client-investing-NAM-2026])

**Most relevant problem types:** Type 6, Type 3, Type 1 (Branch C: cross-sell)

**Revenue decomposition:**
```
Investing Revenue = AUM × Fee Rate (managed/robo) + Transaction Commissions (self-directed) + Wrap Fees

Self-directed: low/zero advisory fees, revenue from trading commissions + margin lending
Managed/Robo: 25-50 bps recurring on AUM
Full-service advisor (FA): 65-100 bps on AUM
```

**How it differs from Wealth:**
- Self-directed segment generates little revenue per account — the lever is converting them to managed/advised
- Tier upgrades (DI → FA) are a major lever that doesn't exist in pure wealth
- ACAT (Automated Customer Account Transfer) for asset consolidation is a specific investing mechanism
- Account funding conversion matters more — an unfunded brokerage account generates zero revenue
- Digital engagement directly drives AUM growth (contribution reminders, goal tracking, surplus cash prompts)

**Key KPIs:**

| KPI | Poor | Average | Best-in-Class | Source |
|-----|------|---------|--------------|--------|
| Account funding rate | <50% | 50-70% | >85% | estimated from [Client-investing-NAM-2026] |
| Self-directed → managed conversion | <3% | 5-8% | >10% | roi_levers.md |
| AUM uplift (engaged vs non-engaged) | <10% | 15-20% | >25% | roi_levers.md |
| ACAT completion rate improvement | — | +15-20% | +25% | roi_levers.md |
| Advisor referral cold rate | high | moderate | low | [Client-investing-NAM-2026] evidence |
| DI-to-FA tier upgrade capture rate | low | — | — | [Client-investing-NAM-2026] evidence |
| Chat/call deflection rate | <20% | 30-40% | >50% | [Client-investing-NAM-2026] servicing data |

**[Client-investing-NAM-2026] reference data:**
- 7 lever groups, $23M total 5-year benefits vs $8.8M investment
- ROI: 162%, Payback: 3.0 years, NPV: $9.5M
- Largest lever: In-App Cross-Sell ($2.27M steady-state) — driven by banking app as discovery channel for investment products
- Advisor Referral Pipeline: $1.65M steady-state — speed-to-contact improvement
- ACAT lever has delayed curve (Y1-2 = 0, starts Y3) — platform must be established first

---

## Section 3: Cross-LOB Problem Type Applicability

| Problem Type | Retail | SME | Commercial | Corporate | Wealth | Investing |
|-------------|--------|-----|------------|-----------|--------|-----------|
| **Type 1: Revenue Growth** | Primary | Primary | Primary | Primary | Via Type 6 | Via Type 6 |
| **Type 2: Cost Reduction** | Primary | Primary | Secondary | Secondary | Secondary | Secondary |
| **Type 3: Digital Transformation** | Primary | Secondary | Secondary | Rare | Secondary | Primary |
| **Type 4: Operational Efficiency** | Secondary | Secondary | Primary | Primary | Primary (RM) | Secondary (Advisor) |
| **Type 5: Lending Origination** | Primary | Primary | Primary | Different (syndicated) | Rare | Rare |
| **Type 6: AUM-Based** | Rare | Rare | Rare | Rare | Primary | Primary |

---

## Section 4: Training Data Gaps

| LOB | Status | What's Available | What's Needed |
|-----|--------|-----------------|---------------|
| **Retail** | Strong | [Client-creditunion-NAM-2025], SeABank, [Client-retail-ANZ-2025], Credins, [Client-retail-NAM-2025], [Client-creditunion-NAM-2022], Banesco, Banco Caja Social | Sufficient for now |
| **Wealth** | Strong | [Client-wealth-APAC-2025], Tangerine, Goodbody, TriState Capital | Sufficient for now |
| **Investing** | Moderate | [Client-investing-NAM-2026] (1 engagement) | 1-2 more investing engagements to validate patterns |
| **SME** | Weak | Referenced in calibrator, no full ROI model | Need 1+ complete SME ROI model (ideally SME-primary bank) |
| **Commercial** | Moderate | Seacoast (onboarding only), BOK Financial (treasury discovery) | Need 1 complete commercial ROI model with full lever set |
| **Corporate** | Weak | BOK Financial (discovery only), benchmark data | Need 1+ complete corporate ROI model (multi-entity, treasury-heavy) |

---

## Section 5: Methodology (How to Build the Tree)

### Step 1: Define the Problem
- Bank's desired outcome (in their language)
- Backbase's sales objective (what's being positioned)
- Primary LOB and problem type
- Scope constraints (geography, segments, products in play)

### Step 2: Apply Layer 1 Math
Select the mathematical decomposition from the matching problem type. Write it out. This is the tree's skeleton — MECE is guaranteed by the math.

If the problem spans multiple types (common), identify the primary and note secondaries. Build the primary tree first, then check secondary types for additional branches.

### Step 3: Apply Layer 2 LOB Elaboration
Expand each Layer 1 branch using the LOB-specific patterns. Map each branch to the relevant lifecycle stage (Acquire, Activate, Expand, Retain, Operating Model).

### Step 4: Attach KPIs and Check for Gaps
For each terminal node, identify the measurable KPI. Look up the benchmark range from domain benchmarks. If client data is available, note the client's value. If not, note the benchmark "Average" as proxy (with confidence downgrade).

### Step 5: Identify Value Lever Candidates
Nodes where: measurable gap exists + Backbase capability applies → value lever candidate.
Apply the four-link chain from `value_lever_framework.md` to each candidate.

### Step 6: Coverage Check
- MECE verified at each level (math guarantees Layer 1; check Layer 2 manually)
- At least 2 of 4 lifecycle stages represented
- 5-8 levers typical; <3 suggests missing branches; >12 suggests insufficient prioritization
- Flag excluded branches with rationale

### Step 7: Creative Discovery
After systematic scan, look for opportunities outside standard patterns:
- Cross-LOB adjacency (retail base for a wealth bank, SME for a commercial bank)
- Client-specific structural uniqueness (subsidiaries, multi-country, regulatory changes)
- Second-order effects (one lever amplifying another)
- Stakeholder-specific angles (CIO: tech rationalization; CFO: cost predictability; CDO: time to market)

Flag creative levers as LOW confidence, requiring consultant validation.

### Step 8: Present for Validation
Present the tree with: problem statement, structure, KPIs/gaps, proposed levers (included + excluded + creative), data gaps. Consultant validates before any financial modeling begins.

---

*Status: DRAFT — requires validation with consulting team*
*Created: 2026-04-03*
*Training data gaps: SME (no full model), Corporate (no full model), Investing (1 model only)*
