# Packaging Migration — Upgrade Patterns & Knowledge Base

## Backbase Pricing Tiers

### Essential
The core digital banking foundation. Includes:
- Digital Banking (Retail, Business, or both)
- Core payments and transactions
- Basic self-service capabilities
- Standard onboarding flows

**Who it's for:** Institutions starting their digital transformation or with straightforward digital banking needs.

### Premium
Everything in Essential, plus:
- Financial Insights (PFM) & Pockets (goal-based savings)
- External Account Aggregation (via Yodlee or similar)
- Advanced Card Management
- Digital Engage (proactive engagement, campaigns, notifications)
- Digital Assist (employee-facing tools, case management)

**Who it's for:** Institutions competing on customer experience and engagement. The jump from Essential to Premium is the most common upgrade path.

### Signature
Everything in Premium, plus:
- Family Banking (shared financial management across household members)
- Digital Investing Dashboard (self-directed investing, portfolio overview)
- Wire Transfers (domestic and international)
- Advanced wealth and advisory capabilities

**Who it's for:** Full-service institutions serving affluent, multi-generational, or wealth-adjacent customer segments. The differentiator is lifecycle breadth — Signature covers the complete customer financial journey.

---

## Common Upgrade Triggers

### Essential → Premium Triggers
1. **Engagement gap**: Clients see declining digital adoption or low feature usage — PFM and Pockets drive 15-25% higher engagement
2. **Cost-to-serve pressure**: High call center volume for routine inquiries — Digital Engage and self-service reduce inbound by 20-40%
3. **Competitive pressure**: Fintechs offering PFM and aggregation as standard — clients need feature parity
4. **Employee efficiency**: RMs spending time on administrative tasks — Digital Assist automates workflows

### Premium → Signature Triggers
1. **Affluent segment growth**: Institution expanding into wealth-adjacent services — needs investing and family tools
2. **Household strategy**: Shifting from individual to household relationship management — Family Banking prevents household churn
3. **Fee income growth**: Wire transfers and investing capabilities generate fee revenue beyond deposits
4. **Generational transfer**: $84T wealth transfer requires tools that engage next-gen family members

### Legacy → Any Tier Triggers
1. **Mandate**: "No more deals on old pricing" — organizational decision
2. **Renewal**: Contract renewal is the forcing function — old pricing unavailable
3. **Cloud migration**: Bundling packaging change with infrastructure modernization
4. **Feature request**: Client wants a new capability that's only available in tiered packaging

---

## Upgrade Value Patterns by Domain

### Retail Banking
| Upgrade Path | Primary Value Levers | Typical Benchmarks |
|---|---|---|
| Essential → Premium | PFM adoption → 20% higher engagement; Self-service → 30% call reduction | [Proxy] |
| Premium → Signature | Family Banking → 25% lower household churn; Investing → new fee income stream | [Estimated] |

### SME / Business Banking
| Upgrade Path | Primary Value Levers | Typical Benchmarks |
|---|---|---|
| Essential → Premium | Cash flow insights → deeper SME relationships; Proactive alerts → reduced overdraft risk | [Proxy] |
| Premium → Signature | Business advisory tools → higher wallet share; Multi-entity management | [Estimated] |

### Wealth Management
| Upgrade Path | Primary Value Levers | Typical Benchmarks |
|---|---|---|
| Essential → Premium | Portfolio aggregation → single view of wealth; Advisor tools → 2x more client meetings | [Proxy] |
| Premium → Signature | Full investing dashboard → self-directed + advised; Family office → multi-generational AUM | [Estimated] |

### Credit Unions
| Upgrade Path | Primary Value Levers | Typical Benchmarks |
|---|---|---|
| Essential → Premium | Member engagement → higher loan-to-share ratio; PFM → financial wellness differentiation | [Proxy] |
| Premium → Signature | Family accounts → household membership retention; Investing → compete with retail brokerages | [Estimated] |

---

## Account Size Considerations

### Large Accounts (ARR > $1M)
- Full outside-in analysis with peer comparison
- Dedicated VC engagement expected
- ROI modeling worth the investment
- Cloud + packaging synergy likely relevant
- Multi-product, multi-tier complexity

### Medium Accounts ($200K - $1M)
- Focused outside-in POV
- Tier value articulation critical — they need to see the "why"
- ROI napkin sufficient (not full model)
- Renewal timing is often the best lever

### Small Accounts (< $200K)
- Lightweight analysis — don't over-invest VC time
- Simple re-map where possible
- Exception process if migration doesn't make economic sense
- Group-based approach (batch similar accounts)

---

## Objection Patterns & Responses

### "We're happy with what we have"
**Context:** Legacy client with working implementation, no visible pain.
**Response approach:**
- Acknowledge their success with the current platform
- Introduce outside-in perspective: "Here's what peers in your segment are doing"
- Focus on opportunity cost, not problems: "You're leaving value on the table"
- Show specific untapped capabilities within their effective tier

### "This feels like a forced price increase"
**Context:** Client perceives migration as commercially motivated.
**Response approach:**
- Lead with value, not pricing: "Let me show you what changes for you"
- Quantify the value gap: features they'd gain vs. incremental cost
- Reference the "do not go back" framework transparently
- Emphasize: new capabilities are real, not just repackaged

### "We need time to evaluate"
**Context:** Buying time, possibly hoping it goes away.
**Response approach:**
- Create urgency without pressure: "Renewal timing affects options"
- Offer a structured evaluation: "Let's map your current state in 30 minutes"
- Provide peer examples of successful migration timelines
- Set a specific follow-up, don't leave it open-ended

### "What do we actually get that we don't have?"
**Context:** Skeptical, wants specifics not marketing.
**Response approach:**
- Use the Product Directory gap analysis — exact features they'd gain
- Map new features to their specific business challenges
- Quantify where possible: "X institutions using [feature] saw Y% improvement in Z"
- Show the demo plan (SE contribution) for hands-on proof

### "If you're changing our contract, give us something"
**Context:** Negotiation lever — wants concessions.
**Response approach:**
- This IS the upsell play — lean into it: "Absolutely, here's what the new tier includes"
- Show features in their new tier they're not currently using — free value
- Frame it as: "You're getting more, not paying more for the same"
- Bring in Deal Desk for commercial flexibility if needed

---

## Integration: Migration Co-Pilot → Upgrade Analysis Agent

### Data Flow
```
Migration Co-Pilot (Next.js App)
    │
    ├── Salesforce data (products, contracts, opps, tech stack)
    ├── Product Directory tier mapping
    ├── Effective tier + packaging status
    ├── Play recommendation + signals
    │
    └──→ Upgrade Analysis Agent (claudevc)
            │
            ├── Loads domain knowledge
            ├── Loads peer benchmarks
            ├── Loads competitor intel
            │
            └──→ Produces:
                    ├── Outside-In POV (always)
                    ├── Tier Value Articulation (upgrade plays)
                    ├── ROI Napkin (upgrade plays)
                    ├── Peer Comparison (proactive/upsell)
                    └── Objection Prep (active plays)
```

### How the VC Uses This
1. Migration Co-Pilot flags account for migration
2. AE selects play and assembles team
3. VC is assigned → opens their view in Migration Co-Pilot
4. VC clicks "Generate Analysis" → Migration Co-Pilot calls upgrade-analysis agent
5. Agent produces AI drafts of all relevant deliverables
6. VC reviews, enhances, adds their own insights, approves
7. Approved deliverables feed into the team's meeting prep pack
