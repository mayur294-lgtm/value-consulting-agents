# Investing Domain Journey Maps

## Journey 1: Investment Account Opening (Acquire)

### Overview
New investor opens an investment account — either from an existing banking relationship (bank-led) or as a new prospect (pure investing provider).

### Actors
- **Investor** (prospect or existing banking client)
- **Digital Platform** (web/mobile)
- **Compliance/KYC System**
- **Custodian / Clearing Firm**
- **Advisor** (hybrid model only — optional)

### Journey Steps

| Step | Actor | As-Is (Typical Pain) | Friction | Proposed (Digital) |
|------|-------|---------------------|----------|-------------------|
| 1. Discovery | Investor | Finds investing option buried in website, or told about it in branch | Disconnected from banking, hard to find | Contextual prompt in banking app ("Start investing"), NBA-driven |
| 2. Account Selection | Investor | Confusing choice between account types (individual, joint, IRA, custodial) | Financial jargon, no guidance | Guided selector: "What's your goal?" → recommended account type |
| 3. Personal Information | Investor + Platform | Re-enter all personal details even if existing banking client | Duplication, frustration | Pre-populated from banking profile (bank-led model) |
| 4. Suitability Assessment | Investor + Platform | Long paper questionnaire or clunky digital form | 15-20 questions feels like an exam, abandonment spike | Conversational UI, adaptive questions (skip what's not relevant), progress indicator |
| 5. Risk Profiling | Platform | Generic risk categories with no explanation | Investor doesn't understand "moderate aggressive" | Visual risk-return spectrum, portfolio examples per profile |
| 6. KYC / Identity Verification | Investor + Compliance | Upload documents, wait for manual review | Days of delay, status unknown | eIDV (digital identity verification), real-time decisioning, STP |
| 7. Regulatory Disclosures | Investor + Platform | Dense legal documents, checkbox fatigue | Compliance requirement but poor UX | Smart disclosure (highlight key points), eConsent, progressive disclosure |
| 8. Account Approval | Compliance + Custodian | Manual review queue, 1-3 day wait | Investor loses momentum | Automated STP for standard cases, exception-based human review |
| 9. Account Funding | Investor | Separate process to link bank account and transfer money | Another 3-5 day wait for ACH, many never fund | Integrated funding (instant transfer from linked banking account for bank-led), instant deposit credit |
| 10. Confirmation & Activation | Platform + Investor | Email confirmation, login separately | Cold start — investor doesn't know what to do next | Welcome journey: confirmation → guided first steps → first investment prompt |

### Key Metrics for This Journey
- Application start-to-completion rate
- Abandonment rate by step (especially steps 4 and 9)
- Time from application start to funded account
- STP rate (end-to-end without human intervention)
- Funded account rate (opened → actually funded)

---

## Journey 2: First Investment (Activate)

### Overview
Newly funded account makes their first investment — the critical activation moment that determines long-term engagement.

### Journey Steps

| Step | Actor | As-Is (Typical Pain) | Friction | Proposed (Digital) |
|------|-------|---------------------|----------|-------------------|
| 1. Post-Funding Landing | Investor | Generic dashboard with $0 portfolio and no guidance | Intimidating blank slate | Personalized activation screen based on risk profile and goals |
| 2. Investment Selection | Investor | Thousands of options, no curation | Analysis paralysis | Curated recommendations based on suitability profile, "Start with..." suggestions |
| 3. Order Placement | Investor | Complex order forms (market/limit/stop), unfamiliar terminology | Fear of making a mistake | Simplified "Invest $X in [Fund]" flow, educational tooltips, preview before confirm |
| 4. Confirmation | Platform | Dry confirmation email | No celebration, no next step | Milestone celebration + "What's next" prompt (set up recurring, explore more) |
| 5. Recurring Setup | Investor | Buried in settings, requires separate navigation | Most never find it | Prompted immediately: "Want to invest $X every month?" |
| 6. Portfolio Monitoring | Investor | Raw performance numbers with no context | Confusing for beginners | Performance in context (vs. goals, vs. benchmarks), simple language |

### Key Metrics
- Days from funding to first investment
- First-trade completion rate (funded accounts that trade within 30 days)
- Recurring investment setup rate
- Return visit rate (7 days after first trade)

---

## Journey 3: Asset Consolidation / ACAT Transfer-In (Expand)

### Overview
Existing investor transfers assets from another brokerage — highest-value Expand journey because it brings external AUM onto the platform.

### Journey Steps

| Step | Actor | As-Is (Typical Pain) | Friction | Proposed (Digital) |
|------|-------|---------------------|----------|-------------------|
| 1. Transfer Intent | Investor | Investor has to know ACAT exists, find the form | Hidden process, no proactive prompt | NBA-driven: "Consolidate your Schwab/Fidelity accounts here" based on data signals |
| 2. Account Details | Investor | Manual entry of delivering firm details, account number, DTC number | Error-prone, investor may not know their details | Pre-populated firm lookup, OCR of last statement |
| 3. Transfer Type | Investor + Platform | Full vs partial transfer, in-kind vs liquidate — complex choices | Confusing terminology | Guided choice with plain-language explanations |
| 4. Submission | Platform + Clearing Firm | Paper form or clunky digital form submitted to NSCC/ACATS | 3-6 business day standard, no visibility | Digital submission, real-time status tracking |
| 5. Tracking | Investor | No updates, calls support to check status | Anxiety during 1-2 week wait | Real-time ACAT status tracker, proactive notifications at each stage |
| 6. Completion | Platform | Assets appear with no context | Raw positions, no guidance on what to do with transferred assets | Portfolio analysis of transferred assets, rebalancing recommendations |

### Key Metrics
- ACAT initiation rate (existing clients who attempt consolidation)
- ACAT completion rate
- Average transfer time
- AUM transferred in per completion
- Post-transfer engagement (do they stay active?)

---

## Journey 4: Robo-Advisory Enrollment (Activate/Expand)

### Overview
Self-directed investor enrolls in managed/robo-advisory service — monetization upgrade from self-directed.

### Journey Steps

| Step | Actor | As-Is (Typical Pain) | Friction | Proposed (Digital) |
|------|-------|---------------------|----------|-------------------|
| 1. Awareness | Investor | Banner ad or email about robo product | No context for why it's relevant to them | Contextual prompt: "Based on your portfolio, automated management could optimize for tax efficiency" |
| 2. Goal Setting | Investor + Platform | Generic risk questionnaire (again) | Feels repetitive if already done | Smart carry-forward: "We know your profile — let's set your goal" |
| 3. Portfolio Preview | Platform | Black box — "trust us" | Investor wants to see what they're getting | Preview portfolio allocation, projected outcomes (Monte Carlo), fee comparison |
| 4. Fee Consent | Investor | Fine print about advisory fees | Sticker shock if not transparent | Clear fee breakdown: "$X per year on your $Y balance = $Z/month" |
| 5. Funding / Transfer | Investor | Move money from self-directed to managed | Feels like starting over | Seamless in-platform transfer, maintain tax lots where possible |
| 6. Ongoing Management | Platform | Rebalancing happens invisibly | No awareness of value being delivered | Quarterly "here's what we did for you" report — rebalances, tax-loss harvests, drift corrections |

### Key Metrics
- Robo enrollment rate (self-directed → managed)
- Average AUM enrolled in robo
- Fee consent rate (those who see fees and still proceed)
- Retention rate (robo clients vs. self-directed)

---

## Journey 5: Portfolio Review & Retention (Retain)

### Overview
Ongoing engagement that keeps investors on the platform through market cycles, life changes, and competitive pressure.

### Journey Steps

| Step | Actor | As-Is (Typical Pain) | Friction | Proposed (Digital) |
|------|-------|---------------------|----------|-------------------|
| 1. Performance Reporting | Platform → Investor | Monthly PDF statement, hard to understand | Low engagement, investors check 3rd party tools instead | Interactive dashboard, performance vs. goals, benchmarks, peers |
| 2. Market Event Communication | Platform → Investor | No communication OR mass generic email | Panic during volatility, reactive support surge | Automated, segmented communications: "Your portfolio is down 5% — here's context and what we recommend" |
| 3. Life Event Trigger | Investor → Platform | No way to signal life changes (marriage, baby, retirement) | Portfolio stays misaligned with life | Life event prompts: "Had a life change? Let's review your goals" + updated suitability |
| 4. Rebalancing | Platform / Advisor | Manual or infrequent, investor must initiate | Portfolio drift from target allocation | Automated rebalancing with notification, one-click approval |
| 5. Tax Optimization | Platform | Year-end scramble for tax documents, no tax-loss harvesting | Missed savings, poor tax experience | Year-round tax-lot optimization, tax document hub, estimated tax impact |
| 6. Advisor Escalation | Investor → Advisor | Call center, no context, starts from scratch | Frustrating for investor who has been self-service | Seamless escalation with full context: "I see your portfolio and recent activity — how can I help?" |

### Key Metrics
- Annual retention rate
- Net Promoter Score
- Assets retained during market downturns (vs. outflows)
- Advisor escalation rate and resolution satisfaction
- Account closure / ACAT-out rate

---

## Journey Map Gaps (To Be Populated After Engagements)

These journeys are skeletons. After workshop and engagement data:
- Add specific time-per-step measurements
- Add dollar values at each friction point (value leakage)
- Add system-by-system mapping (which systems involved at each step)
- Add regulatory requirements per step per region
- Promote from `[Estimated]` to `[Client-Validated]` benchmarks

---

*Last Updated: 2026-02-09*
*Status: Bootstrapped — journey structures ready for engagement data overlay*
