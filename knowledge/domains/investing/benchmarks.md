# Investing Domain Benchmarks

## Benchmark Confidence System

This is a bootstrapped domain. Every benchmark carries a confidence tag:

| Tag | Meaning | Action |
|-----|---------|--------|
| `[Industry]` | Sourced from public reports (Cerulli, JD Power, Broadridge, Deloitte, SEC filings) | Use directly, cite source |
| `[Proxy]` | Inferred from adjacent domains (retail banking onboarding, wealth management) | Use with caveat, flag for validation |
| `[Estimated]` | Reasonable estimate based on domain logic, no direct source | Flag prominently, validate in first engagement |
| `[Client-Validated]` | Confirmed by actual client engagement data | Highest confidence — promote to permanent benchmark |

**Evolution rule:** Benchmarks start as `[Industry]` or `[Estimated]`. After each engagement, validated data points replace estimates. Never override `[Client-Validated]` with `[Estimated]`.

---

## Account Opening & Onboarding

| Metric | Poor | Average | Good | Best-in-Class | Confidence |
|--------|------|---------|------|---------------|------------|
| Digital Account Opening Time | >30 min | 15-30 min | 5-15 min | <5 min | `[Industry]` — Schwab/Fidelity benchmark |
| Application Abandonment Rate | >70% | 50-70% | 30-50% | <30% | `[Proxy]` — retail banking onboarding |
| Suitability Questionnaire Completion | <60% | 60-75% | 75-90% | >90% | `[Estimated]` |
| Time to Account Funding | >7 days | 3-7 days | 1-3 days | Same day | `[Industry]` — industry standard |
| Funded Account Rate (opened → funded) | <40% | 40-60% | 60-80% | >80% | `[Proxy]` — retail banking funded rates |
| KYC/AML STP Rate | <40% | 40-60% | 60-80% | >80% | `[Proxy]` — retail banking |
| ACAT Transfer-In Completion Rate | <50% | 50-70% | 70-85% | >85% | `[Industry]` — brokerage industry |
| ACAT Transfer Time | >10 days | 6-10 days | 3-6 days | <3 days | `[Industry]` — ACATS standard |

### Reference Points (Public)
- **Schwab:** Account opening in ~10 minutes, same-day funding via ACH `[Industry]`
- **Robinhood:** Approved in minutes, instant deposit up to $1K `[Industry]`
- **Fidelity:** Online account opening ~15 minutes, 1-3 day funding `[Industry]`
- **Vanguard:** 20+ minute process, known for complexity `[Industry]`

---

## Digital Adoption & Engagement

| Metric | Poor | Average | Good | Best-in-Class | Confidence |
|--------|------|---------|------|---------------|------------|
| Digital Active Rate (monthly login) | <30% | 30-50% | 50-70% | >70% | `[Industry]` — JD Power |
| Mobile-First Users | <40% | 40-55% | 55-70% | >70% | `[Industry]` |
| App Store Rating | <3.5 | 3.5-4.0 | 4.0-4.5 | >4.5 | `[Industry]` — public data |
| Average Logins per Month (active) | <4 | 4-8 | 8-15 | >15 | `[Industry]` |
| Self-Service Rate (transactions without human) | <60% | 60-75% | 75-90% | >90% | `[Proxy]` — retail banking |
| Robo-Advisory Enrollment Rate (eligible) | <5% | 5-15% | 15-30% | >30% | `[Estimated]` |

### Reference Points
- **Schwab:** 4.7 iOS rating, 33M+ active brokerage accounts `[Industry]`
- **Fidelity:** 4.8 iOS rating, highest JD Power self-directed investor satisfaction `[Industry]`
- **Robinhood:** 4.2 iOS rating, 24M funded accounts, high engagement younger demographic `[Industry]`

---

## Revenue & AUM Metrics

| Metric | Poor | Average | Good | Best-in-Class | Confidence |
|--------|------|---------|------|---------------|------------|
| Average AUM per Account (self-directed) | <$15K | $15-50K | $50-150K | >$150K | `[Industry]` — varies by segment |
| Average AUM per Account (robo) | <$10K | $10-30K | $30-75K | >$75K | `[Industry]` |
| Fee Rate (advisory/managed) | <25 bps | 25-50 bps | 50-80 bps | >80 bps | `[Industry]` — public fee schedules |
| Fee Rate (robo-advisory) | <15 bps | 15-25 bps | 25-40 bps | >40 bps | `[Industry]` |
| Revenue per Account (self-directed) | <$50 | $50-150 | $150-400 | >$400 | `[Industry]` |
| Revenue per Account (managed/advisory) | <$200 | $200-500 | $500-1000 | >$1000 | `[Industry]` |
| Net New Assets Growth (annual) | <5% | 5-10% | 10-20% | >20% | `[Industry]` |
| Cross-Sell: Banking Client → Investing | <2% | 2-5% | 5-10% | >10% | `[Estimated]` |

### Fee Structure Reference Points
- **Schwab Intelligent Portfolios:** 0 bps (free robo), premium at 30 bps `[Industry]`
- **Betterment:** 25 bps (digital), 40 bps (premium with advisor access) `[Industry]`
- **Wealthfront:** 25 bps `[Industry]`
- **Vanguard Digital Advisor:** 20 bps `[Industry]`
- **Fidelity Go:** 0 bps under $25K, 35 bps above `[Industry]`

### AUM Reference Points
- **Schwab:** Average self-directed account ~$200K (skews older/wealthier) `[Industry]`
- **Robinhood:** Average account ~$4K (skews younger) `[Industry]`
- **Betterment:** Average account ~$40K `[Industry]`
- **Vanguard:** Average account ~$250K `[Industry]`

---

## Operational Efficiency

| Metric | Poor | Average | Good | Best-in-Class | Confidence |
|--------|------|---------|------|---------------|------------|
| Cost per Account Opened (digital) | >$150 | $75-150 | $30-75 | <$30 | `[Estimated]` |
| Cost per Account Opened (advisor-assisted) | >$500 | $250-500 | $100-250 | <$100 | `[Estimated]` |
| Customer Acquisition Cost (full) | >$500 | $200-500 | $100-200 | <$100 | `[Industry]` — varies widely |
| Cost-to-Serve per Account (annual) | >$200 | $100-200 | $50-100 | <$50 | `[Estimated]` |
| Call Center Calls per 1000 Accounts/Month | >50 | 30-50 | 15-30 | <15 | `[Proxy]` — retail banking |
| Advisor-to-Client Ratio (hybrid model) | >500:1 | 300-500:1 | 150-300:1 | <150:1 | `[Industry]` — wealth proxy |
| Trade Error Rate | >0.5% | 0.2-0.5% | 0.05-0.2% | <0.05% | `[Estimated]` |
| Automated Rebalancing Coverage | <20% | 20-50% | 50-80% | >80% | `[Estimated]` |

---

## Customer Experience

| Metric | Poor | Average | Good | Best-in-Class | Confidence |
|--------|------|---------|------|---------------|------------|
| NPS Score | <20 | 20-40 | 40-60 | >60 | `[Industry]` — JD Power |
| Client Retention Rate (annual) | <80% | 80-90% | 90-95% | >95% | `[Industry]` |
| Account Attrition (ACAT out) | >10% | 5-10% | 2-5% | <2% | `[Estimated]` |
| First Trade within 30 Days | <30% | 30-50% | 50-70% | >70% | `[Estimated]` |
| Recurring Investment Setup Rate | <10% | 10-25% | 25-40% | >40% | `[Estimated]` |

### Reference Points
- **Vanguard:** Industry-leading retention >96%, NPS ~60 `[Industry]`
- **Fidelity:** Highest JD Power satisfaction 4 years running `[Industry]`
- **Schwab:** 95%+ retention rate `[Industry]`

---

## Credit Union / Bank-Led Investing Specifics

These benchmarks apply specifically to banks/credit unions offering investing to existing members/clients:

| Metric | Poor | Average | Good | Best-in-Class | Confidence |
|--------|------|---------|------|---------------|------------|
| Member-to-Investor Conversion | <1% | 1-3% | 3-7% | >7% | `[Estimated]` |
| Average First Investment (from banking) | <$1K | $1-5K | $5-15K | >$15K | `[Estimated]` |
| Multi-Product Primacy (banking + investing) | <5% | 5-15% | 15-30% | >30% | `[Estimated]` |
| Retention Uplift (banking + investing vs banking only) | <5% | 5-10% | 10-20% | >20% | `[Proxy]` — cross-sell retention data |

---

## Usage Guidelines

1. **In Discovery:** Use to benchmark prospect's current state. Always cite confidence tag.
2. **In ROI Models:** Use `[Industry]` and `[Client-Validated]` directly. Use `[Estimated]` only with sensitivity analysis.
3. **In Reports:** `[Estimated]` benchmarks must carry a footnote: "Industry estimate — to be validated with client data."
4. **After Engagement:** Promote validated data points to `[Client-Validated]`. Append to this file with source.

---

*Last Updated: 2026-02-09*
*Sources: Cerulli Associates, JD Power Self-Directed Investor Studies, Broadridge, SEC filings (public fee schedules), Deloitte Investment Management Outlook, public company disclosures (Schwab, Robinhood, Vanguard)*
*Classification: Internal - Value Consulting Use Only*
