# Domain Pain Points Query

Retrieve common pain points and challenges for a specific banking domain to support discovery and solutioning.

## Usage
`/domain-pain-points [domain] [perspective]`

Where:
- `[domain]` is: `retail`, `commercial`, `sme`, `wealth`, or `corporate`
- `[perspective]` (optional) is: `customer`, `bank`, or `all`

## Instructions

When this skill is invoked:

1. **Load the pain points file** from `knowledge/domains/[domain]/pain_points.md`

2. **Filter by perspective** if specified:
   - `customer` - End customer/client pain points
   - `bank` - Internal bank challenges (operational, technology, business)
   - `all` - Complete view

3. **Present pain points** with:
   - Pain point description
   - Impact (quantified where possible)
   - Frequency/prevalence
   - Backbase solution mapping
   - Related use cases

4. **Organize by theme** (e.g., onboarding, payments, service)

5. **Provide discovery questions** to uncover these pain points in client conversations

## Example

```
User: /domain-pain-points retail customer
Assistant: Loading Retail Banking customer pain points...

## Onboarding & Acquisition Pain Points

| Pain Point | Impact | Backbase Solution |
|------------|--------|-------------------|
| Long account opening times | 60%+ abandonment | Digital Onboarding |
| Too many documents required | Poor CX, drop-off | Document capture, eKYC |
| Branch visit required | Limits reach, inconvenience | End-to-end digital |
| No visibility on application status | Anxiety, support calls | Status tracking |

## Discovery Questions:
1. "How long does it take to open an account today?"
2. "What percentage of applications are abandoned?"
3. "What documents do you require, and why?"

## Day-to-Day Banking Pain Points

| Pain Point | Impact | Backbase Solution |
|------------|--------|-------------------|
| Fragmented experience across channels | Frustration, low NPS | Omnichannel platform |
| Limited self-service options | High call center volume | Self-service features |
| Poor mobile app experience | Low engagement, churn | Mobile banking app |

These pain points map to use cases: UC-R001, UC-R010-R015, UC-R030-R034
```

## Notes
- Use in discovery preparation and during interviews
- Pain points should be validated with client data
- Map to value propositions for solutioning
