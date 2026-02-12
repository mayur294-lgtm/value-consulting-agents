# Domain Journey Maps Query

Retrieve customer and operational journey maps for a specific banking domain.

## Usage
`/domain-journeys [domain] [journey-type]`

Where:
- `[domain]` is: `retail`, `commercial`, `sme`, `wealth`, `investing`, or `corporate`
- `[journey-type]` (optional) filters by journey category

## Journey Types by Domain

**Retail:** acquisition, servicing, life-event
**Commercial:** onboarding, operations, trade, service
**SME:** acquisition, daily-banking, growth, service
**Wealth:** acquisition, advisory, self-service, life-event, service
**Investing:** account-opening, first-investment, asset-consolidation, robo-enrollment, retention
**Corporate:** lifecycle, treasury, payments, trade, integration

## Instructions

When this skill is invoked:

1. **Load the journey maps file** from `knowledge/domains/[domain]/journey_maps.md`

2. **Filter by journey type** if specified

3. **Present journeys** with:
   - Journey name and ID
   - Stage flow diagram
   - Key touchpoints
   - Current state pain points
   - Future state (Backbase-enabled)
   - Key metrics

4. **Cross-reference** with:
   - Personas (`personas.md`) - who experiences this journey
   - Use cases (`use_cases.md`) - what capabilities improve it
   - Pain points (`pain_points.md`) - what problems exist

5. **Highlight transformation opportunities** - where Backbase makes the biggest impact

## Example

```
User: /domain-journeys retail acquisition
Assistant: Loading Retail Banking acquisition journeys...

## J1: Account Opening Journey

**Current State:**
[Awareness] → [Research] → [Apply] → [Verify] → [Fund] → [Activate] → [Engage]

**Pain Points:**
- Apply: Too many fields, branch visit required
- Verify: Manual KYC, days to complete
- Fund: Friction in initial deposit
- Activate: Separate card/access setup

**Backbase-Enabled Future State:**
[Discover] → [Apply (5 min)] → [Instant Verify] → [Instant Account] → [Digital Card] → [Engage]

**Key Metrics:**
| Metric | Current | Target |
|--------|---------|--------|
| Time to account | 3-7 days | Minutes |
| Abandonment rate | 60%+ | <20% |
| Documents required | 5+ | 1-2 |

**Relevant Personas:** Digital Native, Digital Adopter
**Backbase Capabilities:** UC-R001, UC-R002
```

## Notes
- Journeys are the foundation for capability assessment
- Use in discovery sessions to map client's current state
- Link to process maps for operational detail
