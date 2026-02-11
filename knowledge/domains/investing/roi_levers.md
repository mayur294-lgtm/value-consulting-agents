# Investing Domain ROI Levers

## Overview

This framework defines the value drivers for investing domain ROI models. Each lever includes the calculation logic, typical ranges, and the Backbase components that enable it.

**Key difference from retail banking ROI:** Investing revenue is primarily AUM-driven (recurring fee on assets) rather than transaction-driven. This means the biggest levers are: get more assets on the platform, keep them there longer, and serve them at lower cost.

---

## Lever 1: Banking-to-Investing Cross-Sell (Revenue Growth)

**What it is:** Converting existing banking clients into investing clients — capturing the investment wallet that currently goes to competitors.

**Why it matters:** This is often the single largest value lever for bank-led investing. The bank already has the client; the question is whether the investment dollars stay in-house.

### Calculation

```
Annual Value = Banking Clients Eligible × Conversion Rate Improvement × Average Initial AUM × Fee Rate

Example:
500,000 eligible banking clients × 2% additional conversion × $10,000 avg initial AUM × 0.40% fee rate
= $400,000 incremental annual fee revenue
(Compounds annually as AUM grows and new conversions add)
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Conversion rate improvement | +1% | +2-3% | +5% | `[Estimated]` |
| Average initial AUM (banking cross-sell) | $5K | $10-15K | $25K | `[Estimated]` |
| Fee rate (managed/robo) | 25 bps | 35-50 bps | 75 bps | `[Industry]` |

### Backbase Enablers
- Digital Engage: NBA engine triggers cross-sell prompts in banking app
- Digital Onboarding: Pre-populated account opening from banking profile
- Digital Banking + Digital Invest: Unified experience reduces friction

---

## Lever 2: AUM Growth Through Digital Engagement (Revenue Growth)

**What it is:** Existing investors add more money due to better engagement — recurring investments, prompted top-ups, tax-advantaged contribution reminders.

**Why it matters:** Engaged investors contribute more frequently. A prompted "You have $3K in your savings account earning 0.5% — move to your investment portfolio?" drives incremental AUM.

### Calculation

```
Annual Value = Active Investors × AUM Uplift % × Average AUM × Fee Rate

Example:
50,000 active investors × 15% AUM uplift × $50,000 avg AUM × 0.40% fee rate
= $1,500,000 incremental annual fee revenue
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| AUM uplift (engaged vs. non-engaged) | 10% | 15-20% | 25-30% | `[Proxy]` — McKinsey wealth engagement data |
| Recurring investment setup improvement | +10% | +15-20% | +25% | `[Estimated]` |

### Backbase Enablers
- Digital Engage: Recurring investment prompts, contribution reminders (IRA deadline, etc.)
- Digital Invest: Goal tracking with progress bars and "top up" calls-to-action
- Data Foundations: Behavioral triggers (excess cash in savings, bonus deposits)

---

## Lever 3: Asset Consolidation / ACAT Transfer-In (Revenue Growth)

**What it is:** Making it easy for investors to transfer assets from other institutions — capturing AUM that was previously at competitors.

**Why it matters:** Each successful ACAT transfer brings $50K-$200K+ in AUM. Even small improvements in transfer initiation and completion rates deliver significant value.

### Calculation

```
Annual Value = ACAT Initiations × Completion Rate Improvement × Average Transfer AUM × Fee Rate

Example:
2,000 ACAT attempts × 15% completion rate improvement × $75,000 avg transfer × 0.40% fee rate
= $90,000 incremental annual fee revenue per cohort (cumulative over years)
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| ACAT completion improvement | +10% | +15-20% | +25% | `[Estimated]` |
| Average ACAT transfer value | $50K | $75-100K | $150K | `[Industry]` |

### Backbase Enablers
- Digital Onboarding: Guided ACAT flow, firm lookup, real-time status tracking
- Digital Engage: Proactive "consolidate your accounts" campaigns
- Grand Central: Clearing firm integration for seamless transfers

---

## Lever 4: Onboarding Cost Reduction (Cost Savings)

**What it is:** Reducing the cost of opening and funding investment accounts through digital STP.

**Why it matters:** Manual/advisor-assisted account opening costs $250-500+ per account. Digital STP reduces this to $30-75.

### Calculation

```
Annual Savings = New Accounts × (Cost per Manual Account - Cost per Digital Account) × Digital Shift %

Example:
10,000 new accounts/year × ($300 manual - $50 digital) × 40% digital shift
= $1,000,000 annual cost savings
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Cost per manual account opening | $250 | $300-400 | $500 | `[Estimated]` |
| Cost per digital STP account opening | $50 | $30-50 | $20 | `[Estimated]` |
| Digital shift (% moving from manual to digital) | 25% | 40-50% | 60% | `[Proxy]` — retail banking |

### Backbase Enablers
- Digital Onboarding: End-to-end digital with suitability, KYC, eSignature
- Flow Foundation: STP orchestration, exception-only human review
- Grand Central: Custodian/clearing integration

---

## Lever 5: Cost-to-Serve Reduction (Cost Savings)

**What it is:** Reducing ongoing servicing costs through investor self-service — account maintenance, document access, simple transactions without human assistance.

**Why it matters:** Every call/visit avoided saves $8-15. At scale, self-service shift on routine investing operations delivers significant savings.

### Calculation

```
Annual Savings = Interactions Avoided × Cost per Interaction

Example:
50,000 call center interactions × 30% deflection to self-service × $12 avg cost per call
= $180,000 annual savings
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Call deflection rate | 20% | 30-40% | 50% | `[Proxy]` — retail banking |
| Cost per call (investing) | $10 | $12-15 | $20 | `[Estimated]` |
| Self-service adoption for routine tasks | 40% | 50-65% | 75% | `[Proxy]` — retail banking |

### Backbase Enablers
- Digital Invest: Self-service for account changes, beneficiary updates, tax documents
- AI & Agentic: Conversational support for common questions
- Digital Assist: Advisor workspace for complex escalations

---

## Lever 6: Advisor Productivity (Cost Avoidance — Hybrid Model)

**What it is:** For hybrid advisory models — freeing advisor time from admin so they can serve more clients without adding headcount.

**Why it matters:** Advisors spend 40-60% of time on admin. Digital tools can reclaim 30-50% of that time, enabling each advisor to serve more clients — scaling revenue without proportional cost increase.

### Calculation

```
Annual Value = Advisors × Admin Time Saved × Hourly Cost × Additional Client Revenue

Example:
20 advisors × 30% admin time reduction × $85/hr × 2080 hrs/yr = $1,060,800 capacity freed
Or: Each advisor takes 50 more clients × $500 revenue/client = $500,000 incremental revenue
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Admin time reduction | 25% | 30-40% | 50% | `[Proxy]` — wealth management |
| Advisor loaded cost | $80/hr | $85-105/hr | $120/hr | `[Industry]` — varies by market |
| Additional clients per advisor | 30 | 50-80 | 100 | `[Estimated]` |

### Backbase Enablers
- Digital Assist: Unified advisor workspace, Client 360
- Digital Onboarding: Advisor-assisted but digitally streamlined
- Digital Invest: Client self-service reduces advisor admin burden

---

## Lever 7: Retention & Primacy Lift (Revenue Protection)

**What it is:** Multi-product investors (banking + investing) churn less. Keeping assets on platform protects existing fee revenue.

**Why it matters:** Losing a $100K account at 40 bps = $400/year lost. Preventing 100 such departures = $40K/year protected. Compounds over time as retained AUM grows.

### Calculation

```
Annual Value = At-Risk AUM × Retention Improvement × Fee Rate

Example:
$500M total AUM × 2% retention improvement × 0.40% fee rate
= $40,000 annual revenue protected (Year 1)
(Compounds — retained AUM stays and grows)
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Retention improvement | 1% | 2-3% | 4-5% | `[Proxy]` — wealth management |
| Multi-product retention uplift vs single-product | +10% | +15-20% | +25% | `[Estimated]` |

### Backbase Enablers
- Digital Invest: Superior experience reduces switching motivation
- Digital Engage: Proactive retention campaigns, market volatility communications
- Digital Banking + Digital Invest: Unified experience creates switching cost

---

## Lever 8: Robo-Advisory Revenue Uplift (Revenue Growth)

**What it is:** Converting self-directed (zero/low fee) investors to managed/robo-advisory (fee-generating) accounts.

**Why it matters:** Self-directed may generate $0-50 per account. Robo at 25-40 bps on $50K = $125-200 per account. Material revenue uplift at scale.

### Calculation

```
Annual Value = Self-Directed Accounts × Robo Conversion Rate × Average AUM × (Robo Fee - Self-Directed Fee)

Example:
100,000 self-directed accounts × 5% robo conversion × $40,000 avg AUM × 0.30% incremental fee
= $600,000 incremental annual fee revenue
```

### Typical Ranges

| Parameter | Conservative | Base | Aggressive | Confidence |
|-----------|-------------|------|------------|------------|
| Self-directed → robo conversion | 3% | 5-8% | 10% | `[Estimated]` |
| Incremental fee (robo vs self-directed) | 20 bps | 25-35 bps | 40 bps | `[Industry]` |

### Backbase Enablers
- Digital Invest: Robo-advisory module with goal-based investing
- Digital Engage: Targeted campaigns for eligible self-directed investors
- Data Foundations: Propensity models for robo conversion

---

## ROI Model Assembly Guide

When building an investing ROI model, select levers based on the client's model:

| Client Model | Primary Levers | Secondary Levers |
|-------------|----------------|------------------|
| **Bank-Led Investing** | Lever 1 (Cross-sell), Lever 4 (Onboarding cost), Lever 7 (Retention) | Lever 2 (AUM growth), Lever 5 (Cost-to-serve) |
| **Pure Investing Provider** | Lever 2 (AUM growth), Lever 3 (ACAT consolidation), Lever 5 (Cost-to-serve) | Lever 6 (Advisor productivity), Lever 8 (Robo conversion) |
| **Hybrid Advisory** | Lever 6 (Advisor productivity), Lever 2 (AUM growth), Lever 7 (Retention) | Lever 1 (Cross-sell if bank-backed), Lever 8 (Robo) |

**Conservative bias:** Always use the conservative column for the base case. Use base/aggressive for sensitivity analysis only. Never present aggressive estimates as the base case.

**Ramp schedule (typical):**

| Factor | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
|--------|--------|--------|--------|--------|--------|
| Implementation | 25% | 75% | 100% | 100% | 100% |
| Adoption | 20% | 45% | 65% | 80% | 90% |
| **Effective Impact** | **5%** | **34%** | **65%** | **80%** | **90%** |

---

*Last Updated: 2026-02-09*
*Status: Bootstrapped — lever calculations are framework-ready. Ranges to be refined after first engagement.*
