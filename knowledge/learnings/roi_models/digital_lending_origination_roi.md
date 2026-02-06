# ROI Pattern: Digital Consumer Lending Origination

## Overview

Value model for implementing digital consumer loan origination (personal loans, free investment loans).

**Domain Vertical:** Consumer Lending, Retail Banking

**Applicable To:**
- Retail banks with consumer lending portfolios
- Banks with pre-approved customer bases
- Markets with growing digital lending adoption (LATAM, SEA, Africa)

**NOT Applicable To:**
- Mortgage lending (different model)
- SME/Commercial lending (different economics)
- Buy-now-pay-later (different structure)

---

## Value Levers

### 1. Digital Sales Uplift

**Mechanism:** Pre-approved customers convert at higher rates when offered digital origination vs. branch-only.

**Formula:**
```
Additional Revenue = (Monthly Pre-approvals) × (Digital Uplift %) × (Avg Ticket) × (Net Margin) × 12

Net Margin = Interest Spread - Provision Expense + Origination Fee
```

**Typical Inputs (LATAM):**

| Parameter | Conservative | Moderate | Aggressive |
|-----------|--------------|----------|------------|
| Monthly Pre-approved Base | 300-500 | 500-1000 | 1000+ |
| Digital Sales Uplift | 20% | 40% | 60% |
| Average Ticket (USD) | $3,000-5,000 | $5,000-8,000 | $8,000-15,000 |
| Average Term (months) | 48-60 | 60 | 60-72 |

**Margin Components (LATAM Benchmark):**

| Component | Typical Range |
|-----------|---------------|
| Weighted Average Rate | 18-25% |
| Cost of Funds | 10-15% |
| **Gross Spread** | **7-12%** |
| Provision Expense | 2.5-5% |
| **Net Margin** | **4-7%** |
| Origination Fee | 0.3-0.5% |

---

### 2. Cross-Sell: Credit Cards to Loan Customers

**Mechanism:** Digital lending journey enables card cross-sell at point of loan origination.

**Formula:**
```
Cross-Sell Value = (New Digital Loans) × (Card Offer Rate) × (Acceptance Rate) × (Card Lifetime Value)
```

**Typical Inputs:**

| Segment | Card Offer Rate | Acceptance Rate | Card LTV |
|---------|-----------------|-----------------|----------|
| Premium | 100% | 10% | $400-600 |
| Ascenso/Mass Affluent | 100% | 10% | $300-500 |
| Mass Market | 50% | 5% | $150-300 |

---

### 3. Portfolio Quality Improvement

**Mechanism:** Digital origination with automated decisioning improves portfolio quality.

**Risk Bucket Benchmarks (% of Portfolio):**

| Bucket | Pre-Digital | Post-Digital | Improvement |
|--------|-------------|--------------|-------------|
| A (Current) | 93% | 95-96% | +2-3% |
| B (30 days) | 1.2% | 0.8-1.0% | -0.2-0.4% |
| C (60 days) | 1.0% | 0.7-0.8% | -0.2-0.3% |
| D (90 days) | 1.1% | 0.9-1.0% | -0.1-0.2% |
| E (120+ days) | 3.0% | 2.4-2.7% | -0.3-0.6% |

**Charge-off Rate Improvement:** 0.2-0.4% reduction annually

---

## Portfolio Growth Model

**Monthly Cohort Buildup:**

| Month | New Disbursements | Outstanding Balance | Interest Income |
|-------|-------------------|---------------------|-----------------|
| 1 | Base | Base × 1.0 | Low |
| 6 | Base | Base × 5.5 | Growing |
| 12 | Base | Base × 10.5 | Stabilizing |
| 24 | Base | Base × 18.0 | Mature |
| 36+ | Base | Base × 22.0 | Steady State |

**Paydown Curve (60-month term):**

| Month | % Remaining |
|-------|-------------|
| 12 | 82-85% |
| 24 | 62-68% |
| 36 | 40-48% |
| 48 | 18-25% |
| 60 | 0% |

---

## Ramp-Up Assumptions

### Disbursement Ramp (New Digital Channel)

| Period | Monthly Disbursements |
|--------|----------------------|
| Month 1-3 | 150-300 |
| Month 4-6 | 300-500 |
| Month 7-12 | 750-1000 |
| Month 13-18 | 1000-1500 |
| Month 19-24 | 1200-1500 (steady state) |

---

## Regional Adjustments

### LATAM Specific Factors

| Factor | Adjustment |
|--------|------------|
| Currency Risk | Model in local currency |
| Inflation | Add inflation adjustment to rates |
| Regulatory | Pre-approval rules vary by country |
| Digital Penetration | Higher in Brazil/Chile, lower in Central America |

### Africa Specific Factors

| Factor | Adjustment |
|--------|------------|
| Mobile-First | Higher mobile vs. web ratio |
| Integration | Mobile money integration critical |
| ID Verification | eKYC availability varies |

---

## Sensitivity Analysis

**Key Driver:** Digital Uplift % has highest impact on value.

| Digital Uplift | Year 3 Portfolio | Year 3 Interest Income |
|----------------|------------------|------------------------|
| 20% | Baseline | Baseline |
| 40% | +60% | +55% |
| 60% | +120% | +105% |

---

## Source Reference

Derived from LATAM retail banking implementations (Colombia), anonymized and generalized.
Product type: Créditos de Libre Inversión (Personal/Consumer Loans)
