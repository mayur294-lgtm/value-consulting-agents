# Value Lever Framework

## Purpose

This document defines what a value lever is in the context of Backbase Value Consulting, how to identify one, and how to validate it. It is the foundational reference for anyone building or reviewing ROI models — human or agent.

This is a **consultant-facing document**. The agent receives a compact version of these rules in its prompt; this document provides the full reasoning, examples, and validation criteria behind those rules.

---

## Definition

A value lever is a quantifiable causal chain that connects a Backbase platform capability to a financial outcome for a bank.

It is NOT an initiative ("implement digital onboarding"), NOT an outcome ("save $500K"), and NOT a feature ("save-and-resume"). It is the **mechanism** linking a bank's current problem to a measurable financial result through a specific Backbase-enabled change.

Every value lever must articulate four links:

```
Root Driver → Operational Change → Volume/Rate Impact → Financial Impact
```

If any link is missing, it is not a lever.

### Link 1: Root Driver

The underlying problem, inefficiency, or missed opportunity in the bank's current operations. This must be **observable** — sourced from client evidence (transcripts, questionnaires, data, annual reports) or benchmarks, not assumed.

Questions it answers:
- What is broken or suboptimal today?
- How do we know? (What is the evidence?)
- Who told us, or where did we measure it?

**Good:** "[Client-creditunion-NAM-2025] has a 26.1% digital application abandonment rate (source: Questionnaire, 2025). Of 197,738 digital app starts, only 73.9% complete. Members drop off at manual form entry and ID upload steps requiring 20 min processing across 3-4 disconnected systems."

**Bad:** "Banks typically have high abandonment rates in digital onboarding."

### Link 2: Operational Change

The specific change in how the bank operates, enabled by a named Backbase capability. This must describe what **concretely changes** in the bank's process or workflow — not just name a product.

Questions it answers:
- What Backbase capability makes this possible? (Name it specifically — DOL, RB.15.3, BB.17, Flow Foundation, etc.)
- What does the bank's process look like AFTER implementation?
- Why does this capability produce the change? (The "HOW" narrative)

**Good:** "Backbase Digital Onboarding Lifecycle (DOL.1-DOL.5) replaces the fragmented web form with a guided mobile-first flow: progressive data capture with save-and-resume, real-time identity verification (Jumio/Onfido integration via marketplace), core system pre-fill (IPS integration eliminates manual data re-entry), and instant account provisioning. Processing drops from 20 min to 5 min as manual steps are eliminated."

**Bad:** "Backbase Digital Onboarding improves the process."

### Link 3: Volume/Rate Impact

The measurable metric that moves as a result of the operational change. This is a **quantity** (customers, transactions, hours, FTEs) or a **rate** (conversion %, completion %, deflection %) — expressed as a delta from current state to target state.

The target state must be derived, not asserted:
- **Gap-based method:** (Best-in-Class − Client Current) / Best-in-Class × Capture Rate (typically 0.30-0.50)
- **Client-stated target:** The bank has declared a specific target (e.g., "[Client-creditunion-NAM-2025] target: 5 min processing, 61K hrs/year saved")
- **Benchmark range:** Published industry data with source citation

Questions it answers:
- What metric moves?
- By how much? (Current value → target value, with delta)
- How do we know this is achievable? (Gap-based calc, benchmark source, or client target)

**Good:** "Digital leakage rate improves from 26.1% to ~19% (7.2pp improvement). Method: 26.1% current vs 8% best-in-class (Chime/neobanks) = 18.1pp gap. Backbase capture rate 40% (conservative). 18.1pp × 0.40 = 7.2pp improvement."

**Bad:** "Abandonment rate improves by 30%."

### Link 4: Financial Impact

The dollar value produced by the volume/rate impact. This must be a **calculation using the bank's own data** (volumes, rates, costs) — not an assertion or industry average when client data is available.

Questions it answers:
- What is this worth in dollars per year?
- Show the math — every number traceable to an input
- What is the confidence level and what would change the estimate?

**Good:** "7.2% conversion uplift on 197,738 app starts = 14,237 additional completions. At $350 first-year revenue per member = $4.98M annual revenue uplift."

**Bad:** "This lever is worth approximately $5M per year."

---

## Real Examples

### Retail Banking — [Client-creditunion-NAM-2025] (Credit Union, USA, 1.5M members)

**Lever: Debit Card Activation Uplift**

| Link | Content |
|------|---------|
| **Root Driver** | Debit cards issued to new members but not activated — lost interchange revenue. Current activation rate not at best-in-class. Source: [Client-creditunion-NAM-2025] Questionnaire + annual report data. |
| **Operational Change** | Backbase Self-Service Card Management (RB.15): instant digital card issuance (virtual card in <60 seconds), push-to-wallet provisioning for Apple Pay/Google Pay (RB.15.3), real-time card activation via mobile app. Replaces mailed physical card with activation delay. |
| **Volume/Rate Impact** | 25% activation uplift on baseline annual debit cards issued. Source: BCG Digital Banking Study 2023 + Mercator Advisory Debit Issuer Study 2024 — instant digital issuance drives 20-30% uplift in activation rates for institutions >$10B. |
| **Financial Impact** | Additional activated cards × $126 interchange revenue per active card per year. Source: Pulse Debit Study 2024. |

**Lever: Back Office Card Dispute Processing Efficiency**

| Link | Content |
|------|---------|
| **Root Driver** | 290,000 card disputes/year processed at 10 min avg (source: Sarah Slonsky, VP Servicing Ops, Mar 2026). Only 25% achieve STP via current Quavo system. Remaining 75% require manual processing across multiple systems. 98 FTE in servicing operations. |
| **Operational Change** | Backbase Digital Assist with integrated dispute workflow: automated dispute categorization, pre-populated forms from transaction data, straight-through processing for standard dispute types (provisional credit, chargeback initiation), exception-only routing for complex cases. |
| **Volume/Rate Impact** | STP rate improvement from 25% to target (scenario-dependent). Volume deflection rate applied to 290K annual disputes. Time reduction on remaining manual disputes. Dual-dimension: volume deflection + time-per-task reduction. |
| **Financial Impact** | (Deflected volume × baseline cost per task) + (remaining volume × time reduction × $46.15/hr blended rate). Source: [Client-creditunion-NAM-2025] Questionnaire blended FTE rate. |


### Digital Investing — [Client-investing-NAM-2026] (USA)

**Lever: DI-to-FA Tier Upgrade — Automated Threshold Routing**

| Link | Content |
|------|---------|
| **Root Driver** | Self-directed investing (DI) clients accumulate AUM over time, crossing thresholds that qualify them for full-service advisor (FA) management at higher fee rates. No automated detection exists — upgrades rely on the client calling in or an advisor manually reviewing accounts. Eligible clients go unnoticed; revenue left on the table. |
| **Operational Change** | Backbase platform monitors AUM thresholds in real-time. When a DI client crosses the FA-eligible threshold: (1) advisor receives automated notification with pre-populated client profile, (2) digital suitability reassessment triggers for the client, (3) one-click upgrade workflow (no re-KYC required — existing profile carries over). |
| **Volume/Rate Impact** | X% of DI clients crossing threshold are captured that previously went unnoticed. Conversion from DI (low/zero advisory fee) to FA (higher advisory fee). Implementation ramps with standard curve. |
| **Financial Impact** | Upgraded clients × AUM per client × fee rate delta (FA rate − DI rate) = $831K annual steady-state benefit. |

**Lever: ACAT / Asset Consolidation (Held-Away AUM Capture)**

| Link | Content |
|------|---------|
| **Root Driver** | [Client-investing-NAM-2026] members hold investment assets at competitor platforms (Schwab, Fidelity, Vanguard). No streamlined in-app mechanism to initiate asset transfers. Current ACAT process is paper-based and advisor-mediated, creating friction that discourages consolidation. |
| **Operational Change** | Backbase Digital Onboarding with guided ACAT flow: in-app firm lookup, real-time transfer status tracking, digital authorization (no physical forms). Proactive "consolidate your accounts" campaigns via Digital Engage. Integration with clearing firm for seamless transfers. |
| **Volume/Rate Impact** | ACAT initiation volume increases. Completion rate improves from current baseline. Average transfer AUM × improved completion rate. **Delayed curve: 0 impact in Y1-Y2** (platform must be established before consolidation campaigns launch), starts at 30% in Y3, ramps to 95% by Y5. |
| **Financial Impact** | Transferred AUM × blended fee rate = $114K annual steady-state (Y5). Cumulative: $216.6K over 5 years. Smaller lever but compounds as transferred AUM is sticky. |


### Wealth Management — [Client-wealth-APAC-2025] (19K wealth clients)

**Lever: Cross-Subsidiary Revenue Synergy**

| Link | Content |
|------|---------|
| **Root Driver** | [Client-wealth-APAC-2025] has 4 subsidiaries on completely separate systems: banking, investment bank, securities, insurance. RMs cannot see a client's full relationship — getting a consolidated view requires calling different departments, taking ~1 hour per client. Inter-company referrals happen via ad-hoc calls and emails. Source: Transcript S3-4, S5-6. |
| **Operational Change** | Backbase Digital Assist provides unified RM workspace with Client 360 across all 4 entities via API integrations (Grand Central). RM sees banking balances, investment positions, securities holdings, and insurance policies in one screen. Automated referral routing replaces manual calls. |
| **Volume/Rate Impact** | 3% AUM uplift from improved cross-sell across entities. On $1.82B total wealth AUM. Conservative estimate given 4 separate entities currently fully siloed. Source: Estimate — validated against wealth cross-sell benchmarks (5-8% typical for unified platforms). |
| **Financial Impact** | $1.82B × 3% uplift × 1.0% blended revenue rate on AUM = $546K incremental annual revenue. Source: Client data — wealth revenue $18.15M / $1.82B AUM = ~1.0% blended rate. |

**Lever: RM Admin Time Liberation**

| Link | Content |
|------|---------|
| **Root Driver** | 45 RMs spend 60% of time on non-value-adding admin: manual Excel reporting (twice monthly per RM), calling subsidiaries for cross-entity data consolidation (~1 hr per client view), WhatsApp-based client communication (compliance risk), physical document handling via courier. No CRM — fixed income RMs use Excel spreadsheets. Source: Transcript S1 ("RMs spend about 60% of their time on non-value-adding tasks"), S3-4, S5-6. |
| **Operational Change** | Backbase Digital Assist: unified RM workspace eliminates toggling between 5-8 systems. Automated portfolio reporting replaces manual Excel (55% of standard reports auto-generated). Compliant in-app messaging replaces WhatsApp (80% of manual message effort eliminated). Digital document vault with e-signatures replaces physical courier (75% of handling eliminated). Integrated calendar with automated reminders replaces manual follow-up tracking. |
| **Volume/Rate Impact** | Admin time drops from 60% to ~33% of RM day. Quantified across 13 specific servicing tasks in 3 categories (portfolio reporting: 8,280 tasks/yr, client communications: 50,400 tasks/yr, operations/compliance: 13,800 tasks/yr). Each task has volume, multi-role time (RM + assistant + back office), and Backbase impact rate. Total: 72,480 annual tasks, $449K baseline cost, $276K cost saved. |
| **Financial Impact** | Direct servicing savings: $276K/yr. Plus RM capacity redeployment: 45 RMs × $8K incremental revenue per RM from deeper relationships and improved hunting ratio = $360K. Plus cost avoidance framing: freed capacity equivalent to 12 FTEs not hired × $23,069/yr = $277K. Total lever value: $556K/yr (servicing savings + capacity redeployment). |


### Retail Banking — SeABank (Vietnam, 3.6M customers)

**Lever: Cross-Lending Origination — Pre-Approved Digital Offers**

| Link | Content |
|------|---------|
| **Root Driver** | SeABank has a large retail customer base with pre-approved lending eligibility data, but no digital channel for pre-approved offer presentation. Customers must visit branches to learn about loan eligibility. Digital lending conversion is low; branch-dependent origination limits volume. Source: Workshop data (June 2025) + Data Request Responses. |
| **Operational Change** | Backbase Digital Lending with pre-approved offer engine: customers see personalized loan offers with pre-approved rates within the digital banking app (Product Explorer). Instant credit decisioning via integration with existing scoring systems. Single-session digital application with e-signature. Income verification via digital bank statement analysis. |
| **Volume/Rate Impact** | Monthly pre-approved base × digital conversion rate uplift × average loan ticket. Conversion uplift benchmarked against LATAM digital lending data (Banco Caja Social, Banesco). STP rate improvement reduces origination processing time. |
| **Financial Impact** | Additional funded loans × average ticket × net margin (interest spread − provision expense + origination fee) = $2.63M annual benefit. |

---

## Validation Criteria

A lever passes review when every link is present and survives scrutiny:

| Link | Pass | Fail |
|------|------|------|
| **Root Driver** | Observable in evidence with named source (person, document, data point) | "Banks typically have this problem" — no client-specific evidence |
| **Operational Change** | Names a specific Backbase capability (product ID or feature name) and describes what concretely changes in the process | "Digital transformation improves the process" — no capability named, no process change described |
| **Volume/Rate Impact** | Metric identified, current and target values stated, derivation shown (gap-based, client target, or cited benchmark) | "50% improvement" with no derivation or benchmark support |
| **Financial Impact** | Calculation shown using bank's actual volumes/rates/costs, units consistent, inputs traceable | Round number asserted without visible math, or industry averages used when client data exists |

### Confidence Levels

| Level | Root Driver | Operational Change | Volume/Rate | Financial Impact |
|-------|------------|-------------------|-------------|-----------------|
| **HIGH** | Client data or named source from transcript/questionnaire | Verified via MCP Infobank or product directory (capability ID confirmed) | Client-specific metric with stated current value; target from client or gap-based calc with benchmark | Uses client financials (revenue, FTE cost, volumes) |
| **MEDIUM** | Transcript evidence (inferred, not directly stated) | From domain roi_levers.md (capability known but not verified against current release) | Industry benchmark as proxy for current state; improvement within published ranges | Mix of client data and benchmark proxies |
| **LOW** | Inferred from analogous engagement or general industry knowledge | Plausible but not verified — flag for consultant | Estimated — no client data, no directly applicable benchmark | Benchmark proxies throughout — flag for validation |

### Common Failure Modes

| Failure | Example | Fix |
|---------|---------|-----|
| **Missing operational change** | "Digital onboarding → $500K revenue uplift" — what specifically changes? | Add the HOW: which capability, what process changes, why it produces the impact |
| **Ungrounded volume/rate** | "30% improvement in conversion" — says who? | Add derivation: gap-based calc with cited best-in-class, or client target with source |
| **Double-counting** | Retention lever AND cross-sell lever both claiming revenue from the same retained customers | Check: does removing one lever change the other's calculation? If yes, they're interdependent — note it |
| **Wrong level of abstraction** | "Customer Servicing" as a single lever | Break into channel-specific or task-specific sub-levers with their own four-link chains (see [Client-creditunion-NAM-2025] back office: 5 task categories, each sized independently) |
| **Assumed root driver** | "High call center volume is typical for banks this size" | Find the actual evidence: questionnaire data, transcript quote, annual report figure |

---

## Relationship to Other Framework Components

### Hypothesis Trees → Value Levers

Value levers are **outputs** of hypothesis tree analysis, not inputs:

```
Problem Statement
  → Hypothesis Tree (MECE decomposition with KPIs at each node)
    → Gap Analysis (client current vs. benchmark at each node)
      → Value Levers (nodes where gap exists + Backbase capability applies)
        → ROI Model (levers quantified and assembled)
```

A hypothesis tree node becomes a value lever candidate when:
1. The KPI at that node shows a measurable gap (this becomes the Root Driver)
2. A Backbase capability can influence that gap (this becomes the Operational Change)
3. The improvement can be estimated (this becomes the Volume/Rate Impact)
4. The financial value can be calculated (this becomes the Financial Impact)

### Lifecycle Alignment

Levers map to the Backbase customer lifecycle flywheel, but a single lever can span stages:

| Stage | Revenue Levers | Cost Levers |
|-------|---------------|-------------|
| **Acquire** | Onboarding conversion, application leakage recovery, lending origination | Onboarding processing cost, KYC automation |
| **Activate** | Account funding, card activation, digital enrollment | Channel migration (branch→digital, call center deflection) |
| **Expand** | Cross-sell, product penetration, AUM consolidation, tier upgrades | RM productivity, advisor capacity redeployment |
| **Retain** | Churn reduction, retention campaigns, competitive defense | Servicing cost reduction, compliance automation |
| **Operating Model** | Time to market (revenue acceleration) | IT rationalization, platform consolidation, managed hosting |

Some levers span stages — tag them accordingly (e.g., [Client-investing-NAM-2026] "Advisor Referral Pipeline" is "Acquire → Expand").

---

*Status: DRAFT — requires validation with consulting team*
*Created: 2026-04-03*
*Sources: [Client-creditunion-NAM-2025] ROI Model v7 (Raghu-validated), [Client-investing-NAM-2026] ROI v5, [Client-wealth-APAC-2025] roi_config_calibrated.json, SeABank roi_config.json*
