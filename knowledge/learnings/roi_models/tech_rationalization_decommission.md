# Tech Rationalization & Decommissioning ROI Model

## Overview

This document captures patterns for building tech rationalization and platform decommissioning business cases. Data sourced from engagements where Backbase replaced legacy digital banking platforms.

---

## OneAZ Credit Union Reference (NAM, 2025)

**Context:** Arizona Credit Union, 182K retail members, 12K business members, Lumin platform replacement

### Member Metrics

| Metric | Baseline | Notes |
|--------|----------|-------|
| Retail Members | 182,000 | |
| Business Members | 12,000 | |
| Total Digital Users | 134,000 | |
| Retail Digital Adoption | 68.7% | |
| Business Digital Adoption | 75% | |
| Retail Split | 93.8% | Of total membership |
| Business Split | 6.2% | Of total membership |

### Growth Assumptions

| Metric | Year 1 | Year 2 | Year 3 | Year 4 |
|--------|--------|--------|--------|--------|
| Digital User Growth | 10% | 11% | 12% | 20% |
| Business User Growth | 260% | 12% | 14% | 20% |

---

## Legacy Platform Cost Breakdown

### Annual Platform Costs (OneAZ Lumin Stack)

| Category | Annual Cost | Notes |
|----------|-------------|-------|
| **Retail Banking** | $2.05M | Core digital banking |
| **SME Banking** | $148K | Business banking |
| **Retail Origination** | $418K | MeridianLink |
| **Bill Pay (Retail)** | $560K | FIS |
| **P2P (Retail)** | $672K | Early Warning/Zelle |
| **Fraud Management** | $55K | Global Vision Systems |
| **Middleware/iPaaS** | $400K | Informatica |
| **PFM** | $277K | Yodlee/Lumin |
| **Credit Monitoring** | $209K | Yodlee/Lumin |
| **Online Chat** | $253K | LivePerson |
| **RDC** | $147K | Ensenta/JKHY |
| **Digital Wallet** | $32K | PSCU |
| **KYC/AML** | $252K | FIS |
| **ID Capture** | $100K | PreciseID |
| **Case Management** | $26K | Temenos Akcelerant |
| **Total Annual Spend** | **$6.65M** | Baseline |

---

## Marketplace Partner Per-Transaction Costs

### Onboarding Services

| Service | Provider | Cost/Transaction | Notes |
|---------|----------|------------------|-------|
| AML Screening | Comply Advantage | $0.35 | Per new member |
| Address Validation | Smarty | $0.19 | Per verification |
| Identity Verification | Jumio | $1.25 | Per verification |
| SMS/Email OTP | Twilio | $0.25 | Per OTP sent |
| Prefill | Prove | $1.50 | Retail only |
| Instant Account Verification | Yodlee | $0.75 | Retail only |
| Account Funding | Paymentus | $0.55 | Retail only |
| Business ID Verification | Middesk | $6.00 | Business only |

### Digital Banking Services (Per User/Month)

| Service | Provider | Cost/User/Month | Notes |
|---------|----------|-----------------|-------|
| Bill Pay | FIS/Paymentus | $0.27 | Per active user |
| P2P/Zelle | Early Warning | $0.33 | Per active user |
| Fraud Management | Global Vision | $0.23 | Per active user |
| RDC/Mobile Deposit | Ensenta | $0.05 | Per active user |
| Digital Wallet | PSCU | $0.01 | Per active user |
| PFM | Yodlee | $0.10 | Per active user |
| Credit Monitoring | Yodlee | $0.07 | Per active user |
| Online Chat | LivePerson | $0.09 | Per active user |
| Middleware | Informatica | $0.14 | Per active user |

---

## Decommissioning Timeline Pattern

### Typical 4-Phase Approach

| Phase | Duration | Activities | Cost Impact |
|-------|----------|------------|-------------|
| **Phase 1** | 6-12 months | Retail Banking Go-Live | Keep legacy in parallel |
| **Phase 2** | 3-6 months | Business Banking Go-Live | Begin sunset retail legacy |
| **Phase 3** | 3-6 months | Full Migration | Sunset business legacy |
| **Phase 4** | 3-6 months | Decommission | Contract terminations |

### Contract Termination Considerations

- **Early termination penalties:** Typically 50-100% of remaining contract value
- **Notice periods:** 90-180 days for most SaaS contracts
- **Data migration costs:** Budget 5-10% of legacy contract value
- **Parallel run costs:** Budget for 3-6 months overlap

---

## Backbase vs. Legacy Cost Comparison (OneAZ)

| Scenario | Annual Cost | Notes |
|----------|-------------|-------|
| Current Lumin Stack | $6.65M | Baseline |
| With Growth (Year 4) | $11.9M | 20% YoY cost increase |
| Backbase (Full Ramp) | ~$4.3M | Includes marketplace |
| **Annual Savings** | **$2.35M** | At baseline |
| **Year 4 Savings** | **$7.6M** | With growth impact |

### 5-Year NPV Impact

| Component | Value |
|-----------|-------|
| Total Legacy Cost (5yr) | $46M |
| Total Backbase Cost (5yr) | $25M |
| **Net Savings** | **$21M** |

---

## Value Lever Patterns for Tech Rationalization

### 1. Platform Consolidation
- **Driver:** Reduce number of vendor contracts
- **Typical Savings:** 20-40% of legacy spend
- **Timeline:** 18-36 months to full realization

### 2. Per-User Cost Optimization
- **Driver:** Lower per-user licensing with scale
- **Typical Savings:** $2-5 per digital user/month
- **Timeline:** Immediate upon migration

### 3. Integration Simplification
- **Driver:** Replace point-to-point with unified API layer
- **Typical Savings:** 30-50% reduction in middleware costs
- **Timeline:** 12-24 months

### 4. Growth Cost Avoidance
- **Driver:** Avoid legacy per-user cost escalation
- **Typical Savings:** 15-25% of projected growth costs
- **Timeline:** Compounding annually

---

## Sources

1. **OneAZ Credit Union** - Decommissioning Model V1 (2025)
2. **Backbase Consulting** - Tech Rationalization Patterns

---

*Last Updated: 2026-02-06*
*Classification: Internal - Value Consulting Use Only*
