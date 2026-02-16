# Wealth Management Domain ROI Levers

## Overview

This framework defines the value drivers for wealth management domain ROI models. Each lever includes the calculation logic, typical ranges, and the Backbase components that enable it.

**Key difference from retail banking ROI:** Wealth management revenue is relationship-driven and AUM-fee-based. The biggest levers are: free advisor time to deepen relationships, consolidate more client assets onto the platform, retain high-value clients longer, and expand product penetration across the client base. Unlike retail banking (transaction-driven) or investing (self-directed), wealth depends heavily on the RM-client relationship — so every lever either makes that relationship more productive or harder to leave.

---

## Lever 1: RM Productivity — Admin Time Freed (Cost Reduction)

**What it is:** Reducing the time Relationship Managers spend on administrative tasks (data entry, document chasing, compliance paperwork, meeting prep) so they can redirect hours toward client-facing activities.

**Why it matters:** RMs in most wealth firms spend 40-60% of their day on non-client-facing admin. At a loaded cost of $80K-$150K per RM, that is $32K-$90K per RM per year burned on tasks that digital tools can automate. Freed capacity either avoids hiring additional RMs (cost avoidance) or enables each RM to serve more clients (revenue growth).

### Calculation

```
Annual Value = Number of RMs × Annual Loaded RM Cost × Current Admin Time % × Admin Time Reduction %

Example:
50 RMs × $120,000 loaded cost × 50% admin time × 40% reduction
= $1,200,000 annual capacity freed

Revenue upside: 50 RMs × 15 additional clients each × $3,500 avg revenue/client
= $2,625,000 incremental annual revenue from redeployed capacity
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Current admin time (% of RM day) | 40% | 50-55% | 60%+ | `[Industry]` — Goodbody, HNB discovery data |
| Admin time reduction (with digital) | 25% | 35-40% | 50% | `[Industry]` — Backbase implementation benchmarks |
| Annual loaded RM cost | $80K | $100-130K | $150K+ | `[Industry]` — varies by market; NAM $180-220K |
| Additional clients per RM (freed capacity) | 10 | 15-25 | 40 | `[Estimated]` |
| Meeting prep time reduction | 40% | 55-65% | 75% | `[Proxy]` — Goodbody: 2 hrs to 30 min target |

### Backbase Enablers
- Digital Assist: Unified RM workspace with Client 360 view — eliminates toggling between 5-8 systems
- Digital Onboarding: Advisor-assisted but digitally streamlined onboarding — 40% effort reduction per client
- Flow Foundation: Automated workflow orchestration for document collection, follow-ups, and renewals
- AI & Agentic: Auto-generated meeting summaries, pre-populated proposals, next-best-action prompts

---

## Lever 2: Share of Wallet / AUM Consolidation (Revenue Growth)

**What it is:** Capturing a larger portion of existing clients' investable assets — moving money from competitor platforms onto the firm's managed accounts.

**Why it matters:** Wealth clients typically hold 3-4 financial relationships. Average share of wallet is 25-40% for most firms. Moving from 30% to 45% share of wallet on a $1M client at 75 bps means an extra $1,125/year per client. Across a book of 500 clients, that is $562,500 annually — from clients the firm already has.

### Calculation

```
Annual Value = Target Client Base × Avg Total Investable Assets × Share of Wallet Improvement × Fee Rate

Example:
2,000 HNW clients × $1,500,000 avg investable assets × 5% share-of-wallet gain × 0.75% fee rate
= $1,125,000 incremental annual fee revenue
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Current share of wallet | 25% | 30-40% | 45%+ | `[Industry]` — HNB analysis |
| Share of wallet improvement | +3% | +5-8% | +10-15% | `[Estimated]` |
| Average total investable assets (HNW) | $500K | $1-2M | $5M+ | `[Industry]` — segment dependent |
| Fee rate (managed discretionary) | 50 bps | 65-85 bps | 100 bps | `[Industry]` |
| Fee rate (advisory non-discretionary) | 25 bps | 35-45 bps | 50 bps | `[Industry]` |

### Backbase Enablers
- Digital Invest: Consolidated portfolio view across held-away and managed accounts — makes gaps visible
- Digital Engage: Targeted campaigns to prompt asset consolidation ("consolidate your retirement accounts")
- Digital Assist: RM dashboard showing share-of-wallet gaps per client — prioritizes outreach
- Data Foundations: Wealth aggregation feeds, held-away asset detection via Plaid/Yodlee integrations

---

## Lever 3: Client Retention / Churn Reduction (Revenue Growth)

**What it is:** Reducing the rate at which high-value clients leave the firm — protecting the recurring revenue stream from AUM attrition.

**Why it matters:** Wealth client attrition runs 5-12% per year. Losing a $1M client at 75 bps costs $7,500/year in perpetuity. Worse, departing HNW clients often trigger referral network losses. A 2% improvement in retention on a $5B AUM book protects $750,000 in annual fee revenue — and it compounds every year as retained AUM grows.

### Calculation

```
Annual Value = Total AUM × Retention Rate Improvement × Blended Fee Rate

Example:
$5,000,000,000 total AUM × 2% retention improvement × 0.75% fee rate
= $750,000 annual revenue protected (Year 1, compounds thereafter)

Alternative per-client view:
500 at-risk clients × 2% saved × $1,500,000 avg AUM × 0.75% fee rate
= $112,500 annual revenue protected
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Annual client attrition rate | 5% | 7-9% | 12% | `[Proxy]` — industry reports, segment dependent |
| Retention improvement (digital engagement) | 1% | 2-3% | 4% | `[Proxy]` — Tangerine: 3% improvement benchmark |
| Average AUM per departing client | $250K | $750K-1.5M | $3M+ | `[Industry]` — HNW segment |
| Multi-product retention uplift | +10% | +15-20% | +25% | `[Estimated]` — banking + wealth vs. wealth-only |
| Client NPS improvement (digital) | +5 pts | +10-15 pts | +20 pts | `[Proxy]` — industry benchmarks |

### Backbase Enablers
- Digital Invest: Superior digital experience creates switching cost — clients prefer staying
- Digital Engage: Proactive retention campaigns, market volatility communications, life-event triggers
- Digital Banking + Digital Invest: Unified banking-wealth experience — multi-product clients churn 15-25% less
- AI & Agentic: Early churn risk detection, automated RM alerts for at-risk clients

---

## Lever 4: Product Penetration / Cross-Sell (Revenue Growth)

**What it is:** Converting existing banking-only clients into wealth management clients — capturing the investment and planning wallet from the retail base.

**Why it matters:** Most banks with wealth divisions sit on a large retail client base where only 5-15% use wealth services. Converting even a small additional percentage yields outsized revenue: a single retail-to-wealth conversion generating $250K in AUM at 75 bps = $1,875/year — far exceeding the revenue from a typical retail banking relationship.

### Calculation

```
Annual Value = Eligible Banking Clients × Incremental Conversion Rate × Avg Initial AUM × Fee Rate

Example:
200,000 eligible mass affluent banking clients × 1.5% additional conversion × $250,000 avg initial AUM × 0.75% fee rate
= $5,625,000 incremental annual fee revenue
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Retail-to-wealth conversion improvement | +0.5% | +1-2% | +3% | `[Estimated]` |
| Average initial AUM (banking cross-sell) | $100K | $200-350K | $500K+ | `[Estimated]` — segment dependent |
| Fee rate on new wealth accounts | 50 bps | 65-85 bps | 100 bps | `[Industry]` |
| Internal upgrade conversion (mass affluent to affluent) | 12% | 15-18% | 22% | `[Proxy]` — HNB: 15% base, 18% with digital |
| Events/referral conversion uplift | +15% | +20-30% | +40% | `[Proxy]` — HNB prospecting data |

### Backbase Enablers
- Digital Engage: NBA engine identifies banking clients with wealth potential (excess deposits, life events)
- Digital Onboarding: Pre-populated wealth account opening from existing banking profile — eliminates re-KYC
- Digital Banking + Digital Invest: Seamless in-app journey from "open wealth account" to funded portfolio
- Data Foundations: Propensity scoring, income inference, balance threshold triggers

---

## Lever 5: Client Onboarding Efficiency (Revenue Growth)

**What it is:** Reducing the elapsed time and manual effort required to onboard new wealth clients — from first meeting to funded account.

**Why it matters:** Wealth onboarding is notoriously slow. Industry average is 14-30 days; best-in-class is under 5 days. Every day of delay is a day the client's assets sit at a competitor earning fees for someone else. Faster onboarding also reduces drop-off: firms with 30+ day processes see 30-50% abandonment. This is a revenue acceleration lever — the same AUM, captured weeks earlier.

### Calculation

```
Annual Value = New Clients × Drop-Off Reduction × Avg AUM × Fee Rate × (Days Saved / 365)

Revenue acceleration:
500 new clients/year × $1,000,000 avg AUM × 0.75% fee rate × (21 days saved / 365)
= $215,753 revenue acceleration (fees earned sooner)

Drop-off recovery:
500 prospective clients × 15% drop-off reduction × $1,000,000 avg AUM × 0.75% fee rate
= $562,500 annual revenue from recovered clients

Cost savings:
500 new clients × (4 hrs manual - 1.5 hrs digital) × $100/hr RM cost
= $125,000 annual RM time savings
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Current onboarding time | 14 days | 21-30 days | 30+ days | `[Industry]` — Goodbody: 31 days current |
| Target onboarding time (digital) | 7 days | 4-5 days | 2-3 days | `[Industry]` — Goodbody best-in-class: 4 days |
| Application drop-off rate (current) | 30% | 35-45% | 50%+ | `[Industry]` — multi-client analysis |
| Drop-off reduction (digital) | 10% | 15-20% | 25% | `[Estimated]` |
| RM time per onboarding (manual) | 3 hrs | 4-5 hrs | 5+ hrs | `[Industry]` — HNB workshop data |
| RM time per onboarding (digital) | 1.5 hrs | 1-1.5 hrs | <1 hr | `[Industry]` — Backbase target |

### Backbase Enablers
- Digital Onboarding: End-to-end digital with suitability assessment, eSignature, document upload
- Flow Foundation: STP orchestration, parallel processing of KYC/AML and account setup
- Grand Central: Custodian and clearing firm integration for same-day account funding
- Digital Assist: Advisor co-browsing for hybrid onboarding — digital-first with human support when needed

---

## Lever 6: Compliance Cost Avoidance (Cost Reduction)

**What it is:** Automating KYC/AML checks, suitability assessments, periodic reviews, and regulatory reporting to reduce the manual compliance effort that wealth firms carry.

**Why it matters:** Wealth management has heavier compliance requirements than retail banking — suitability checks on every recommendation, periodic KYC refreshes, ongoing monitoring, and complex regulatory reporting. Manual compliance consumes 15-25% of operational headcount. Automation does not eliminate compliance — it makes it faster, more consistent, and auditable.

### Calculation

```
Annual Savings = Compliance FTEs Freed × Loaded Cost per FTE

Example:
8 compliance/ops FTEs × $90,000 loaded cost × 35% effort reduction
= $252,000 annual cost savings

Alternative — per-review calculation:
5,000 annual suitability reviews × (45 min manual - 15 min automated) × $50/hr compliance cost
= $125,000 annual savings on suitability alone
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| AML/KYC review time reduction | 40% | 55-65% | 75% | `[Industry]` — Goodbody: 3.5 days to 0.5 days |
| Suitability check automation | 30% | 45-55% | 65% | `[Estimated]` |
| Compliance FTE effort reduction | 25% | 35-40% | 50% | `[Proxy]` — Backbase implementation data |
| Loaded compliance/ops FTE cost | $70K | $85-100K | $120K | `[Industry]` — market dependent |
| Periodic review cycle reduction | 30% | 40-50% | 60% | `[Estimated]` |

### Backbase Enablers
- Digital Onboarding: Automated KYC/AML with identity verification, PEP/sanctions screening
- Flow Foundation: Rule-based suitability engine, exception-only human review, audit trail
- Digital Assist: Compliance dashboard with risk flags, automated periodic review scheduling
- Data Foundations: Continuous transaction monitoring, regulatory reporting data feeds

---

## Lever 7: Next-Best-Action Revenue (Revenue Growth)

**What it is:** Using AI-driven prompts and behavioral analytics to recommend the right product, at the right time, to the right client — delivered through the RM's workspace or directly to the client via digital channels.

**Why it matters:** Most wealth firms leave money on the table because RMs rely on memory and manual review to identify opportunities. A systematic NBA engine surfaces actionable prompts: rebalancing triggers, tax-loss harvesting windows, insurance gaps, lending opportunities against portfolios. Each acted-upon recommendation generates incremental revenue.

### Calculation

```
Annual Value = NBA Prompts Delivered × RM Action Rate × Avg Revenue per Acted Prompt

Example:
10,000 NBA prompts/year × 25% RM action rate × $500 avg revenue per acted prompt
= $1,250,000 incremental annual revenue

Alternative — per-product view:
2,000 lending-against-portfolio prompts × 15% conversion × $2,000 avg annual interest spread
= $600,000 from one product category alone
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| NBA prompts per RM per month | 10 | 15-25 | 40 | `[Estimated]` |
| RM action rate on prompts | 15% | 20-30% | 40% | `[Estimated]` |
| Avg incremental revenue per acted prompt | $300 | $400-600 | $1,000+ | `[Estimated]` — varies by product |
| Rebalancing/trade prompt conversion | 20% | 30-40% | 50% | `[Estimated]` |
| Cross-product prompt conversion (insurance, lending) | 5% | 10-15% | 20% | `[Estimated]` |

### Backbase Enablers
- AI & Agentic: Machine learning models for propensity scoring, life-event detection, portfolio drift alerts
- Digital Engage: NBA engine triggers personalized prompts in RM workspace and client-facing channels
- Digital Assist: Actionable recommendation cards in RM dashboard with one-click fulfillment workflows
- Data Foundations: Behavioral analytics, transaction pattern analysis, external data enrichment

---

## ROI Model Assembly Guide

When building a wealth management ROI model, select levers based on the client's profile:

| Client Profile | Primary Levers | Secondary Levers |
|---------------|----------------|------------------|
| **Bank with Wealth Division** | Lever 4 (Cross-sell), Lever 1 (RM productivity), Lever 5 (Onboarding) | Lever 3 (Retention), Lever 2 (AUM consolidation) |
| **Pure-Play Wealth / Private Bank** | Lever 1 (RM productivity), Lever 2 (AUM consolidation), Lever 3 (Retention) | Lever 6 (Compliance), Lever 7 (NBA revenue) |
| **Digital-First / Mass Affluent** | Lever 4 (Cross-sell), Lever 5 (Onboarding), Lever 7 (NBA revenue) | Lever 3 (Retention), Lever 1 (RM productivity) |
| **Emerging Market Wealth** | Lever 4 (Cross-sell), Lever 1 (RM productivity), Lever 5 (Onboarding) | Lever 6 (Compliance), Lever 3 (Retention) |

**Conservative bias:** Always use the conservative column for the base case. Use base/aggressive for sensitivity analysis only. Never present aggressive estimates as the base case.

**Ramp schedule (typical):**

| Factor | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
|--------|--------|--------|--------|--------|--------|
| Implementation | 25% | 75% | 100% | 100% | 100% |
| Adoption | 20% | 50% | 75% | 85% | 90% |
| **Effective Impact** | **5%** | **38%** | **75%** | **85%** | **90%** |

**Typical 5-year value range by firm size:**

| Firm Size (AUM) | Conservative 5-Year Value | Base 5-Year Value |
|-----------------|--------------------------|-------------------|
| $1-5B AUM | $2-8M | $5-15M |
| $5-20B AUM | $8-25M | $15-50M |
| $20B+ AUM | $25-80M | $50-150M+ |

**Reference engagements:**
- HNB Wealth (Sri Lanka, 13K clients, $1B+ AUM): $20-25M conservative 5-year value
- Tangerine/Scotiabank (Canada, 138K wealth clients, $7.3B AUM): $107M cumulative 5-year value
- Goodbody (Ireland, HNW brokerage): 8x onboarding time reduction as primary lever

---

*Last Updated: 2026-02-13*
*Status: Production — ranges calibrated against Goodbody, HNB, Tangerine, and NAM wealth engagement data.*
