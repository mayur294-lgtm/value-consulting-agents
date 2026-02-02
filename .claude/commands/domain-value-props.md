# Domain Value Propositions Query

Retrieve Backbase value propositions and differentiation for a specific banking domain.

## Usage
`/domain-value-props [domain] [theme]`

Where:
- `[domain]` is: `retail`, `commercial`, `sme`, `wealth`, or `corporate`
- `[theme]` (optional) filters by value theme

## Value Themes by Domain

**Retail:** digital-adoption, cost-reduction, digital-sales, cx, time-to-market
**Commercial:** onboarding, self-service, treasury, payments, relationships
**SME:** acquisition, credit-access, cost-to-serve, engagement, ecosystem
**Wealth:** advisor-productivity, client-experience, next-gen, hybrid-advisory, cost
**Corporate:** onboarding, real-time-treasury, apis, cost, share-of-wallet

## Instructions

When this skill is invoked:

1. **Load the value propositions file** from `knowledge/domains/[domain]/value_propositions.md`

2. **Filter by theme** if specified

3. **Present value propositions** with:
   - The problem/challenge
   - Backbase solution
   - Proof points / references
   - Quantified value (typical improvements)

4. **Include competitive differentiation** - how Backbase wins against alternatives

5. **Provide objection handling** for common pushback

6. **Link to reference customers** where available

## Example

```
User: /domain-value-props retail digital-adoption
Assistant: Loading Retail Banking digital adoption value proposition...

## Accelerate Digital Adoption

**The Problem:**
Banks struggle to migrate customers from branch to digital channels. Legacy systems create fragmented experiences. Digital engagement remains low despite investments.

**Backbase Solution:**
- Unified engagement platform across web, mobile, assisted
- Modern UX that rivals fintech competitors
- Progressive feature adoption through personalization
- Branch-to-digital migration tools

**Proof Points:**
- [Customer X]: Increased digital active rate from 45% to 78% in 18 months
- [Customer Y]: Mobile adoption grew 3x post-launch

**Quantified Value:**
| Metric | Typical Improvement |
|--------|---------------------|
| Digital active rate | +20-40 percentage points |
| Mobile adoption | 2-3x increase |
| Digital transactions | +50-100% |

**Competitive Differentiation:**
vs. Build in-house: Faster time to market, proven platform
vs. Core vendor: Better UX, more flexible, faster innovation

**Objection Handling:**
"We've already invested in digital" → Backbase complements and modernizes existing investments
```

## Notes
- Value props should be backed by customer evidence
- Quantification should be defensible
- Tailor to client's specific situation
