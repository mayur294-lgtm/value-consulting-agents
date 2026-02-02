# Domain Use Cases Query

Retrieve Backbase use cases and capabilities relevant to a specific banking domain.

## Usage
`/domain-usecases [domain] [category]`

Where:
- `[domain]` is: `retail`, `commercial`, `sme`, `wealth`, or `corporate`
- `[category]` (optional) filters by use case category

## Categories by Domain

**Retail:** onboarding, self-service, engagement, service, employee
**Commercial:** onboarding, cash, payments, trade, lending, integration
**SME:** onboarding, daily-banking, cashflow, integration, service
**Wealth:** onboarding, portfolio, advisory, engagement, banking, family
**Corporate:** onboarding, liquidity, payments, trade, integration, lending

## Instructions

When this skill is invoked:

1. **Load the use cases file** from `knowledge/domains/[domain]/use_cases.md`

2. **Filter by category** if specified

3. **Present use cases** with:
   - Use Case ID
   - Name and description
   - Backbase capability mapping
   - Value driver
   - Relevant personas

4. **Cross-reference with pain points** from `pain_points.md` to show problem-solution mapping

5. **Highlight priority use cases** based on:
   - Common discovery themes
   - High ROI potential
   - Quick wins vs strategic

## Example

```
User: /domain-usecases retail onboarding
Assistant: Loading Retail Banking onboarding use cases...

## Onboarding & Origination Use Cases

| ID | Use Case | Backbase Capability | Value Driver |
|----|----------|---------------------|--------------|
| UC-R001 | Digital Account Opening | Onboarding Journey | Reduce time-to-account, lower CAC |
| UC-R002 | In-App Card Application | Card Origination | Increase card penetration |
| UC-R003 | Personal Loan Origination | Lending Journey | Digital sales growth |
| UC-R004 | Mortgage Pre-Qualification | Mortgage Journey | Lead generation, CX |
| UC-R005 | Joint Account Opening | Onboarding | Household acquisition |

### Pain Points Addressed:
- Long account opening times → UC-R001
- Branch visit required → UC-R001, UC-R003
- Abandoned applications → UC-R001 through UC-R005

Shall I provide detailed breakdown of any specific use case?
```

## Notes
- Use cases should map to Backbase product capabilities
- Link to relevant demos/references where available
- Prioritize based on client discovery findings
