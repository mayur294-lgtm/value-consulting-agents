# Implementation & Adoption Ramp-Up Models

## Purpose

Ramp-up curves must reflect domain vertical, implementation complexity, and estimated timeline. Using the same static curve for a 6-month retail self-service deployment and a 24-month wealth core-banking transformation produces unreliable projections.

## Step 1: Estimate Implementation Timeline

Before applying curves, estimate the implementation timeline based on:

| Factor | Shorter (6-12 mo) | Medium (12-18 mo) | Longer (18-24+ mo) |
|--------|-------------------|-------------------|---------------------|
| Domain | Retail self-service | Retail branch, SME | Wealth, Commercial |
| Journeys in scope | 1-3 | 4-6 | 7+ |
| Integration complexity | API-only | Middleware | Core banking replacement |
| Regulatory requirements | Low | Medium | High (PSD2, MiFID) |
| Organizational readiness | High (digital-first) | Medium | Low (legacy culture) |

**State the assumption explicitly in the report:**
> "Implementation timeline assumed: [X] months to full deployment based on [domain], [N] journeys in scope, [integration type]. This is a key assumption — validate with implementation team."

## Step 2: Derive Implementation Curve from Timeline

| Timeline | Y1 | Y2 | Y3 | Y4 | Y5 |
|----------|-----|-----|-----|-----|-----|
| 6 months | 50% | 90% | 100% | 100% | 100% |
| 9 months | 40% | 85% | 100% | 100% | 100% |
| 12 months | 30% | 80% | 100% | 100% | 100% |
| 15 months | 20% | 70% | 90% | 100% | 100% |
| 18 months | 15% | 60% | 85% | 100% | 100% |
| 24 months | 10% | 40% | 75% | 95% | 100% |

For timelines between rows, interpolate linearly.

## Step 3: Apply Domain-Specific Adoption Discount

Implementation tracks technical deployment. Adoption (effectiveness) tracks actual business usage and lags implementation. The discount depends on how adoption happens in each domain.

| Domain | Adoption Mechanism | Y1 Multiplier | Y2+ Multiplier | Rationale |
|--------|-------------------|---------------|----------------|-----------|
| Retail (self-service) | Customer self-adoption via app/web | 0.85x | 0.90x | Mass market, network effects, low switching friction |
| Retail (branch) | Staff training + change management | 0.60x | 0.80x | Training rollout, staff resistance |
| Wealth (advisor-led) | Advisor adoption + client migration | 0.50x | 0.70x | Relationship sensitivity, advisor habits, gradual client migration |
| Commercial | Client-by-client onboarding | 0.45x | 0.65x | Enterprise sales cycle, each client needs integration |
| SME | Mix of self-service + assisted | 0.70x | 0.85x | Simpler products, some digital-native SMEs |
| Investing (digital) | Customer self-adoption | 0.80x | 0.90x | Easy to open, hard to transfer AUM |

**Effectiveness curve = Implementation curve × Domain adoption multiplier**

### Example: 18-month Wealth Implementation

| Year | Implementation | Adoption Multiplier | Effectiveness |
|------|---------------|---------------------|--------------|
| Y1 | 15% | 0.50x | 8% |
| Y2 | 60% | 0.70x | 42% |
| Y3 | 85% | 0.85x | 72% |
| Y4 | 100% | 0.95x | 95% |
| Y5 | 100% | 1.00x | 100% |

## Step 4: Scenario Variation

Apply the derived curves to the Moderate scenario. For Conservative and Aggressive:

| Scenario | Implementation Adjustment | Adoption Adjustment |
|----------|--------------------------|---------------------|
| Conservative | -10% Y1-Y3, same Y4-Y5 | Additional -10% Y1-Y2 |
| Moderate | As derived | As derived |
| Aggressive | +10% Y1-Y3, cap at 100% | Additional +10% Y1-Y2, cap at 100% |

## Complexity Multipliers

For engagements with known complexity factors, adjust the timeline estimate:

| Factor | Timeline Extension |
|--------|-------------------|
| Multi-country deployment | +6 months |
| Regulatory approval required | +3-6 months |
| Core banking migration concurrent | +6-12 months |
| >3 third-party integrations | +3 months |
| Organization >10,000 employees | +3 months (change management) |

## When to Override

The consultant should override the model-derived curves when:
- Client has prior digital transformation experience (faster adoption)
- Client has stated aggressive internal deadlines
- Regulatory deadlines force specific timelines
- Client has explicitly provided their own adoption assumptions
