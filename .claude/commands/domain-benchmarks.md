# Domain Benchmarks Query

Query domain-specific benchmarks and KPIs from the Consulting Playbook to support capability assessment, ROI analysis, and client conversations.

## Usage
`/domain-benchmarks [domain] [journey]`

Where:
- `[domain]` is: `retail`, `commercial`, `sme`, `wealth`, or `corporate`
- `[journey]` (optional) filters by benchmark journey/category

## Journey Categories (from Consulting Playbook CSV)

| Journey | Applicable Domains | Record Count |
|---------|-------------------|--------------|
| General | All | ~100 |
| Digital Onboarding | Retail, SME | ~600 |
| Loan Origination | Retail, SME | ~490 |
| Cards | Retail, SME | ~410 |
| Online Registration | Retail, SME | ~350 |
| Payments | All | ~220 |
| Deposits & Loans Transactions & Views | Retail, SME | ~210 |
| Transaction Dispute | Retail, Commercial | ~190 |
| Loan Servicing | Retail, SME | ~160 |
| Loan Modification | Retail, SME | ~100 |

## Instructions

When this skill is invoked:

1. **Read the master benchmark file**: `knowledge/Consulting Playbook Metrics Benchmark [Master] - Benchmarks.csv`

2. **Filter by domain-relevant journeys**:
   - **Retail/SME:** General, Digital Onboarding, Loan Origination, Cards, Online Registration, Payments, Deposits & Loans, Transaction Dispute, Loan Servicing
   - **Commercial/Corporate:** General, Payments
   - **Wealth:** General (limited coverage - may need supplementing)

3. **Extract key KPIs** for the requested journey:
   - KPI name (column 6)
   - Description (column 7)
   - Unit (column 11)
   - Data points by customer/country (columns 8-10, 12)

4. **Present benchmarks** in a structured format showing:
   - Metric name
   - Description
   - Sample data points from different customers
   - Derived ranges (Poor/Average/Good/Best-in-Class)

5. **Cross-reference** with domain-specific interpretation in `knowledge/domains/[domain]/benchmarks.md`

## Key KPIs by Journey

### Digital Onboarding
- Time to complete onboarding journey (customer)
- Digital Leakage rate / Abandonment rate
- Branch Leakage rate
- Auto ID & Validation Rate
- First Time Right Application %
- % Funded Accounts
- Internal Handoffs count

### Loan Origination
- Digital Lending Origination %
- Average origination to underwriting time
- Cycle time from underwriting to disbursement
- Application approval rate
- Customer Lead Time

### Cards
- Cards ordered through Digital Channels %
- Customer waiting time to get a card
- Card related CC calls %
- Card related Branch visits %

### Payments
- % transfers processed on Digital channels
- Beneficiary Account Set-up Time
- Average time spent by Branch employee per transfer

## Example

```
User: /domain-benchmarks retail onboarding
Assistant: Loading Retail Banking onboarding benchmarks from Consulting Playbook...

**Digital Onboarding Metrics (from customer data):**

| KPI | Sample Data Points | Range |
|-----|-------------------|-------|
| Time to complete onboarding (digital) | Pichincha: 1:10:00, BSF: varies | 5 min - 70 min |
| Time for branch-assisted onboarding | Pichincha: 0:10:00 | 5-30 min |
| Digital Leakage Rate | Multiple: 20-60% | <20% best |
| Auto ID & Validation Rate | Varies by region | 60-95% |
| First Time Right Application | Target: >80% | 50-90% |

**Customers with data:** Tech CU, Sandy Spring, EWB, Banco Pichincha, BSF, CIH, Letshego, ABK, etc.
```

## Notes
- **Primary Source:** `knowledge/Consulting Playbook Metrics Benchmark [Master] - Benchmarks.csv`
- Data includes actual customer metrics from Backbase implementations
- Regional variations exist (USA, APAC, LATAM, MEA, Europe)
- Use specific customer examples when relevant to prospect geography
- Wealth & Corporate have limited coverage - supplement with industry research
