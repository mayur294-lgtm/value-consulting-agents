# Financial Data Input Schema

This document defines the structure and requirements for financial data inputs used in ROI analysis and business case development.

## Overview

Financial data is critical for building defensible ROI models. This schema defines:
- What financial data is required
- How it should be structured
- What sources are acceptable
- How to handle missing data

## Required Financial Data

### 1. Current State Costs

**Purpose:** Establish baseline for cost savings and efficiency gains

**Data Required:**

| Data Element | Description | Units | Source | Required? |
|--------------|-------------|-------|--------|-----------|
| **Personnel Costs** | | | | |
| FTE count | Full-time equivalents in scope | Count | HR / Finance | Yes |
| Loaded cost per FTE | Fully loaded annual cost (salary + benefits + overhead) | $/year | Finance | Yes |
| Time allocation | % of time spent on in-scope activities | % | Interviews / Time tracking | Yes |
| **System Costs** | | | | |
| License costs | Annual software license fees | $/year | IT Finance | Yes |
| Infrastructure costs | Hosting, cloud, hardware costs | $/year | IT Finance | Yes |
| Support & maintenance | Annual support contracts | $/year | IT Finance | Yes |
| **Operational Costs** | | | | |
| Transaction costs | Cost per transaction (if applicable) | $/transaction | Finance / Operations | Conditional |
| Service costs | Outsourced or managed service costs | $/year | Procurement | Conditional |
| Rework / error costs | Cost of errors, rework, manual fixes | $/year | Operations | Desired |

### 2. Volume & Activity Metrics

**Purpose:** Quantify scale for unit economics calculations

**Data Required:**

| Metric | Description | Units | Source | Required? |
|--------|-------------|-------|--------|-----------|
| Transaction volume | Monthly/annual transaction count | Count/period | System logs | Yes |
| User count | Active users | Count | System admin | Yes |
| Customer count | Active customers | Count | CRM | Conditional |
| Growth rate | Historical growth trend | % annual | Finance | Desired |

### 3. Performance Metrics

**Purpose:** Baseline for efficiency and quality improvements

**Data Required:**

| Metric | Description | Units | Source | Required? |
|--------|-------------|-------|--------|-----------|
| Processing time | Avg time per transaction/process | Minutes or hours | Observations / Logs | Yes |
| Error rate | % of transactions with errors | % | Operations data | Desired |
| Rework rate | % requiring manual intervention | % | Operations data | Desired |
| Customer satisfaction | NPS, CSAT, or similar | Score | Survey platform | Desired |

### 4. Revenue Metrics

**Purpose:** Baseline for revenue opportunity modeling

**Data Required:**

| Metric | Description | Units | Source | Required? |
|--------|-------------|-------|--------|-----------|
| Annual revenue | Total revenue in scope | $/year | Finance | Conditional |
| Customer lifetime value | Average CLV | $ | Finance / Marketing | Conditional |
| Customer acquisition cost | Average CAC | $ | Marketing / Sales | Conditional |
| Conversion rates | Lead-to-customer conversion | % | CRM / Marketing | Conditional |
| Churn rate | Annual customer churn | % | CRM | Conditional |
| Win rate | Deal win rate (if B2B sales) | % | CRM / Sales | Conditional |
| Average deal size | Revenue per deal | $ | CRM / Sales | Conditional |

### 5. Risk & Compliance Costs

**Purpose:** Quantify risk mitigation value

**Data Required:**

| Metric | Description | Units | Source | Required? |
|--------|-------------|-------|--------|-----------|
| Incident frequency | Security, downtime, or compliance incidents | Count/year | IT / Risk | Conditional |
| Cost per incident | Average cost to resolve | $/incident | Finance / Risk | Conditional |
| Regulatory penalties | Fines or penalties paid | $/year | Legal / Compliance | Conditional |
| Audit costs | Cost of compliance audits | $/year | Compliance | Conditional |

### 6. Budget & Investment Data

**Purpose:** Define available funding and constraints

**Data Required:**

| Data Element | Description | Units | Source | Required? |
|--------------|-------------|-------|--------|-----------|
| Available budget | Approved budget for initiative | $ | Finance | Yes |
| Budget timing | When funds are available | Fiscal period | Finance | Yes |
| Funding source | CapEx vs OpEx, budget owner | Category | Finance | Yes |
| Approval authority | Who approves spending | Role | Finance / Exec | Yes |

## Data Formats

### Preferred Format: Structured Tables

**Example - Current State Cost Breakdown:**

| Cost Category | Item | Annual Cost | Source | Notes |
|---------------|------|-------------|--------|-------|
| Personnel | 5 FTE @ $120K loaded | $600,000 | HR report | Customer support team |
| Systems | CRM license (Salesforce) | $75,000 | IT Finance | Annual contract |
| Systems | Support ticketing tool | $15,000 | IT Finance | Zendesk annual |
| Operations | Outsourced L1 support | $120,000 | Procurement | Contract through 2025 |
| **Total** | | **$810,000** | | |

**Example - Volume Metrics:**

| Metric | Current Value | Period | Source | Date |
|--------|---------------|--------|--------|------|
| Support tickets | 12,000 | Annual | Zendesk report | Q4 2024 |
| Avg tickets/month | 1,000 | Monthly average | Zendesk report | Last 12 months |
| Active customers | 5,000 | Current | CRM | As of Dec 2024 |
| Ticket growth rate | 8% | Annual | Historical data | 2022-2024 trend |

### Acceptable Formats

- Excel/CSV with clear headers and units
- PDF reports with extractable tables
- System exports (with data dictionary)
- Presentation slides with data tables

### Unacceptable Formats

- Narrative text without numbers
- Images of tables (must be extractable)
- Unstructured data dumps
- Data without units or context

## Data Quality Requirements

### Minimum Standards

**Accuracy:**
- Data is from authoritative sources (Finance, HR, system reports)
- Data is recent (within last 6 months)
- Data is validated or cross-checked where possible

**Completeness:**
- All required fields populated
- Missing data is explicitly noted
- Assumptions are documented

**Clarity:**
- Units are specified ($/year, count/month, %, etc.)
- Source is documented
- Date/period is specified
- Scope is clear (which systems, which team, etc.)

### Red Flags

Data quality issues requiring resolution:
- Numbers with no units or context
- "Estimates" with no basis documented
- Conflicting data from multiple sources
- Data older than 12 months
- Critical required data completely missing

## Handling Missing Financial Data

### When Data is Unavailable

Follow this decision tree:

1. **Is this data critical for the analysis?**
   - Yes → Escalate to client, cannot proceed without
   - No → Proceed with documented assumption

2. **Can we use a reasonable proxy?**
   - Industry benchmark
   - Similar company data
   - Calculation from related data points

3. **Make conservative assumption**
   - Document assumption clearly
   - State confidence level (low/medium/high)
   - Flag for validation
   - Show sensitivity to assumption

### Example: Missing Cost per Ticket

**If actual cost unavailable:**

"Cost per support ticket not available from client. Using industry benchmark for B2B SaaS:
- Source: Gartner 2024 Customer Service Report
- Value: $25 per ticket (median for companies $50M-$500M revenue)
- Confidence: Medium
- Validation: Client to validate with Finance team
- Sensitivity: ±25% cost assumption changes NPV by $X"

## Data Privacy & Security

### Handling Sensitive Data

**Acceptable:**
- Aggregated metrics (total cost, average cost)
- Anonymized data
- Public financial data
- Budget ranges

**Requires Special Handling:**
- Individual salaries (use aggregated loaded cost)
- Customer PII (aggregate only)
- Proprietary financials (NDA required)
- Competitive intelligence

**Never Request:**
- Individual compensation details
- Customer identifiable information
- Credentials or access to systems
- Proprietary algorithms or IP

## Financial Data Checklist

Before starting ROI analysis, verify:

### Baseline Costs
- [ ] Current state personnel costs documented
- [ ] Current state system costs documented
- [ ] Current state operational costs estimated
- [ ] All costs have units and sources

### Volume Metrics
- [ ] Transaction or activity volumes known
- [ ] User/customer counts documented
- [ ] Growth trends understood
- [ ] Peak vs. average volumes noted

### Performance Baseline
- [ ] Key performance metrics available
- [ ] Current state inefficiencies quantified
- [ ] Pain point impacts estimated
- [ ] Opportunity size bounded

### Budget Context
- [ ] Available budget confirmed
- [ ] Budget timing understood
- [ ] Approval process clear
- [ ] Funding source identified

### Data Quality
- [ ] All data sources documented
- [ ] Data recency verified (<6 months)
- [ ] Conflicting data resolved
- [ ] Assumptions documented

## Data Gaps & Assumptions Register

When data is incomplete, use this template:

| Data Element | Status | Assumption Made | Basis | Confidence | Validation Plan |
|--------------|--------|-----------------|-------|------------|-----------------|
| Cost per ticket | Missing | Assumed $25 | Gartner benchmark | Medium | Validate with Finance |
| Transaction growth | Incomplete | Assumed 10% annual | Industry average SaaS | Low | Review historical data |
| FTE loaded cost | Provided | $120K | Client Finance | High | Confirmed with HR |

## Sources of Benchmark Data

When client data is unavailable, use industry benchmarks:

**General Business:**
- Gartner research reports
- Forrester research
- McKinsey industry reports
- Public company financials (for comparables)

**Technology:**
- IDC market reports
- G2 / Gartner vendor pricing
- Open-source benchmarking (Cloud Cost reports, etc.)

**Industry-Specific:**
- Trade association reports
- Regulatory filings
- Industry analyst firms

**Always:**
- Cite source and date
- Note when benchmark may not apply
- Use conservative end of range
- Flag for client validation

## Example: Complete Financial Input Package

See `/examples/engagements/[example-name]/inputs/financial-data.xlsx` for a complete example of properly structured financial inputs.
