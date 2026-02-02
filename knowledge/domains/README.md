# Banking Domain Knowledge Base

This directory contains specialized knowledge for each banking domain vertical to support value consulting engagements.

## Domain Verticals

| Domain | Description | Primary Benchmarks |
|--------|-------------|-------------------|
| [retail/](retail/) | Consumer/personal banking | Digital Onboarding, Cards, Payments, Deposits & Loans |
| [commercial/](commercial/) | Mid-to-large enterprise banking | Payments, Cash Management, Trade Finance |
| [sme/](sme/) | Small & medium business banking | Digital Onboarding, Loan Origination, Payments |
| [wealth/](wealth/) | Wealth management & advisory | Onboarding, Portfolio, Client Engagement |
| [corporate/](corporate/) | Large enterprise & transaction banking | Payments, Treasury, Trade Finance |

## Benchmark Source

All benchmark metrics MUST be sourced from:
- **Primary:** `knowledge/Consulting Playbook Metrics Benchmark [Master] - Benchmarks.csv`
- **Secondary:** Industry reports (cited)

### Benchmark Categories in Master CSV

| Journey Category | Applicable Domains |
|-----------------|-------------------|
| General | All |
| Digital Onboarding | Retail, SME |
| Loan Origination | Retail, SME |
| Cards | Retail, SME |
| Online Registration | Retail, SME |
| Payments | All |
| Deposits & Loans Transactions & Views | Retail, SME |
| Transaction Dispute | Retail, Commercial |
| Loan Servicing | Retail, SME |
| Loan Modification | Retail, SME |

### Key Metrics by Domain

**Retail Banking:**
- Digital Active Rate
- Mobile Adoption
- Digital Onboarding Leakage
- Account Opening Time
- Card Digital Ordering %
- Self-Service Rate

**SME Banking:**
- Digital Onboarding Time
- Loan Origination Time
- Digital Lending Completion
- Branch vs Digital Mix

**Commercial/Corporate:**
- Payment STP Rate
- Onboarding Time
- Self-Service Admin Rate
- Cash Position Visibility

**Wealth:**
- Advisor Productivity
- Client Digital Engagement
- Onboarding Time
- AUM per Advisor

## Structure Per Domain

Each domain contains:

```
[domain]/
  _index.md           # Domain overview and themes
  benchmarks.md       # KPIs from Consulting Playbook
  journey_maps.md     # Customer/client journeys
  process_maps.md     # Bank operational processes
  personas.md         # User personas
  use_cases.md        # Backbase capabilities
  pain_points.md      # Common challenges
  value_propositions.md # Backbase solutions
```

## Usage

1. Use `/domain-context [domain]` to load full domain context
2. Use `/domain-benchmarks [domain]` to query specific metrics
3. Use `/domain-usecases [domain]` to get relevant capabilities
4. Use `/domain-journeys [domain]` to retrieve journey maps
5. Use `/domain-pain-points [domain]` for discovery support
6. Use `/domain-value-props [domain]` for solutioning

## Populating Domain Knowledge

The template files contain `<!-- TO BE POPULATED -->` markers indicating where Backbase-specific content is needed. Sources:

1. **Benchmarks:** Extract from Consulting Playbook CSV
2. **Journeys:** Backbase solution documentation, customer implementations
3. **Use Cases:** Backbase product capabilities, demo scripts
4. **Pain Points:** Discovery interviews, industry research
5. **Value Props:** Customer success stories, ROI evidence
6. **Personas:** Backbase research, implementation experience
