# Conversational Banking — Solution Deep-Dive

**Status:** ⭐ CURRENT — June 2026
**Sources:** Banking OS · Conversational Banking deck (June 2026); Conversational Banking PM Session transcript (2026-06-05)
**Parent:** This solution is one of the 4 solutions of the AI-native Banking OS. For umbrella positioning, see `knowledge/banking_os.md`.
**Internal use only** — pricing details are not for external distribution.

---

## What it is

Conversational Banking is **the next interface** for banking — a natural language interaction surface, for customers and employees, governed by Banking OS guardrails.

> *"Banking OS · Conversational Banking turns natural language into governed banking services and fast resolutions — for customers and employees."*

Backbase's positioning of conversational banking is **NOT chatbot**, **NOT copilot**, **NOT virtual assistant** — those are deflective, answer-only categories.

**The market shift Backbase positions against:**

```
"Press-1" IVR     →    Answer Bot      →    AI Agents
─────────────          ─────────────         ─────────────
Rigid, menu-           Understands             Understands, ACTS,
driven                 words, answers          and RESOLVES
                       simple questions
─────────────          ─────────────         ─────────────
Value:                 Value:                  Value:
Deflects               Answers                 Acts and Resolves
& Frustrates          & Informs              (Backbase position)
```

The standard for customer automation is no longer just answering questions — **it is taking action and resolving issues.**

---

## The acquisition context — Kasisto

In **June 2026, Backbase acquired Kasisto** (closing Jun 15, 2026). Kasisto is a US-based conversational banking specialist with **10 years of heritage** in the domain.

- Originally founded by Cornell University NLP professor (pre-LLM era)
- Pivoted from NLP to LLM-based agentic platform when GPT made traditional NLP obsolete
- Result: **KAIgentic platform** — an agentic framework that leverages any LLM
- Multiple form factors: text chat, voice (speech-to-speech), API, outbound phone calls

### Kasisto reference customers (instant credibility)

- **BMO** (BMO Bot): 81% request containment
- **Nedbank** (Enbi): 70% chat volume reduction in contact centre
- **First Financial** (Gabby): 26% product line increases — 27% in new CODs, 35% in mortgages, 38% in personal loans, 5% in vehicle loans
- **Standard Chartered** (Asia)
- **Westpac**
- **A Tier-1 US national bank** (in flight)
- **Emirates NBD** (Olivia)
- **US Bank**
- **China Bank** (Backbase joint customer — FAQ engine on public website)
- **50M+ customers globally served by KAI**
- **90% of inquiries** answered by KAI

> **How Cortex should treat these proof points:** These are Backbase-cited customer outcomes attributed to named banks — more defensible than the unattributed directional ranges in `banking_os.md` Section 10, but still customer-cited (not Cortex-validated). When using them in a client deliverable:
> - Quote with attribution: *"BMO's deployment reports 81% request containment"* — not *"Backbase Conversational Banking delivers 81% containment"*
> - Treat as a comparable, not as a projection — "comparable banks using similar approaches have seen X" is fine; "you will see X" is not
> - Confirm the source before quoting in a high-stakes output (CS or Solution Engineering should be able to point to the underlying case study or interview)
> - Never use these as load-bearing inputs to an ROI model without bank-specific validation

### Acquisition rationale

- Backbase has the **brand + distribution power** of 120+ banks
- Kasisto has **10 years of conversational banking IP** + reference customers
- Combined: faster route to market, broader credibility
- Strategic fit: Kasisto integrates with **any digital banking platform** — perfect for the wedge strategy

### Candescent context

Kasisto has a reseller relationship with **Candescent**, Backbase's US competitor in the down-market (small credit unions, ~$500M assets). **Backbase will continue Candescent partnership for small CUs (not the target market) but won't double down.** Backbase target: upsell into install base of 120+ existing Backbase customers + new logos.

---

## Solution architecture — How it works

### The customer + employee dual surface

Conversational Banking serves **both sides** of the unified frontline simultaneously:

```
FOR CUSTOMERS                        FOR EMPLOYEES
─────────────────────────            ─────────────────────────
Natural language that helps          Natural language that delivers
customers get outcomes.              execution intelligence.

Assist → Transact → Resolve → Grow   Call Center → Employee Workspace
                                     (CSR · RM · Branch) → Execute Work

                          ↓
                          ↓
          CONVERSATION → INTENT → GOVERNED ACTION → RESOLUTION
              Powered by Banking OS: customer state,
              orchestration, Sentinel governance, fulfillment status

Shared foundations:
Conversation Studio · Banking Intent Library · Human Handoff ·
Conversation Intelligence · Governance & Safety · Voice (speech-to-speech)
```

### Customer-side capabilities — 4 modes

| Capability | What it does | Example |
|---|---|---|
| **Assist** | Helps customers ask questions, find information, navigate digital banking | "How do I increase my card limit?" / "Where can I find my statements?" |
| **Transact** | Lets customers complete routine authenticated actions through conversation | "Freeze my card." / "Download my statement." / "Update my contact details." / "Book an appointment." / "Check payment status." |
| **Resolve** | Turn customer needs into governed resolution loops that execute faster — across cases, workflows, fulfillment, and status updates. *(Linked with Customer Resolution Loops solution.)* | "Start a dispute." / "Report a missing payment." / "Submit a complaint." / "Provide missing onboarding documents." / "Track the progress of a service request." |
| **Grow** | Identify timely moments where the bank can help customers make financial progress while deepening the relationship — without positioning as formal advice. *(Linked with Relationship Intelligence solution.)* | "Help me complete a savings goal." / "Improve cash-flow visibility." / "Finish an application." / "Prepare for a life event." / "Reduce avoidable fees." / "Consider a relevant next-best action." |

### 3-stage processing flow

Every customer interaction passes through 3 stages, governed by Banking OS guardrails at each step:

```
1. UNDERSTAND (Pre-process)        2. ORCHESTRATE (Engine)        3. ASSURE (Post-process)
   ─────────────────────              ───────────────────              ───────────────────
   Identity & verification            Knowledge & RAG                  Quality
   - Authenticate the user            - Bank's SOPs                    - Relevance & accuracy
                                      - Banking Intent Library
   Intent & entities                                                   Safety
   - Understand the request           AI agents & skills               - No hallucinations
                                      - Reason and take action         - Secure
                                      
                                      Integration & APIs
                                      - Connect core systems & data

                          ─────────────────────────────────
                          GENERATIVE GUARDRAILS (Sentinel)
                          Security · Risk · Fraud · Compliance
                          Fully auditable at every step
                          ─────────────────────────────────
                                          ↓
                                      RESOLVED
                                Governed answer or action
```

### Core technical concepts

| Concept | Description |
|---|---|
| **Chat AI** | Intelligent digital assistant resolving account inquiries, transfers, service requests instantly |
| **Voice AI** | Natural language understanding for phone banking with context retention across conversation turns |
| **Seamless Handoff** | Context-aware escalation to live agents with full conversation history and customer intent |
| **Conversational Studio (KAIgentic)** | Low-code/no-code Studio for configuring conversational workflows, agents, knowledge bases — non-technical bank staff can configure |
| **Banking Intent Library** | Pre-built library of banking intents and journeys |
| **Live Response Validation** | Backbase USP — a second LLM (e.g. GPT-5.4) runs at runtime as hallucination detector, validating each agent response before delivery |

### Connection to the wider Banking OS

Conversational Banking sits in the **Interaction Layer** of the Banking OS. It is connected to:

- **Nexus** (Semantic Layer) — for customer state and context
- **Orchestration Layer** — for workflow execution
- **Sentinel** (Authority Layer) — for governance on every conversation turn
- **Intelligence Layer** — for the underlying LLMs and banking-optimized SLMs
- **Connectivity Layer** (Grand Central) — for integration into bank systems

---

## Backbase's Banking SLM — FinRAG-12B

Backbase has built a banking-optimized small language model (12B parameters):

- **Paper:** *FinRAG-12B: A Production-Validated Recipe for Grounded Question Answering in Banking* (arXiv:2605.05482, ACL 2026)
- Authors: Denys Katerenchuk, Pablo Duboue, Keelan Evanini, David Gondek, Nithin Govindugari, Olivier Allauzen, Joshua Baptiste, David J More, Joshua Schechter
- **Deployed at 40+ financial institutions**
- **3-5x faster** responses, **20-50x lower cost** than GPT-4.1
- **7.1 percentage point improvement** in query resolution (p < 0.001) vs GPT-4.1
- Calibrated refusal mechanism — 12% "I don't know" rate (vs base model's unsafe 4.3% and GPT-4.1's over-refusal 20.2%)
- Citation grounding outperforms GPT-4.1

**Why this matters:** Token costs from commercial LLMs become prohibitive at scale (a navy with 12M active customers using conversational banking as the predominant interface = uncapped token spend). Banking-optimized SLMs are dramatically cheaper, faster, and more accurate for banking-specific tasks.

---

## Implementation — From pilot to production

```
Digital Banking implementation        →  Go-live: 12+ months
Build · Integrate · Test · Deploy
                                          
                                          ────────────────────
Conversational Banking implementation  →  Go-live: 6-12 weeks
Land with small use cases, expand           ~10 months sooner to
from there                                  upsell & cross-sell
                                          ────────────────────
                                          Operated by Backbase
                                          AI Consultants
                                          (small ~2 FTE team)
```

### The formula — Ignite Lite + Mission Sprint

```
IGNITE LITE                          MISSION SPRINT
(4 hours)                            (6-12 weeks)

VC works with senior bankers         Bank picks one use case.
to identify high-ROI but             SE + FDE work together with
risk-free use cases.                 customer + Product team
                                     to specify and prototype outcomes.
Prioritize for a Mission Sprint.
```

### Land & Expand sequence

Conversational Banking is the **landing zone**:

```
LAND                            EXPAND
────                            ──────
Conversational Banking          1. Relationship Intelligence
                                   - Add the intelligence layer
                                   - Proactive nudges & insight
                                   - Financial wellness & upsell

                                2. Customer Operations - Resolution Loops
                                   - Query/case from the chat
                                   - Lands employee-side
                                   - Faster Resolution Times
```

### Implementation team

- 1-2 Backbase AI Consultants (typically 1 SE + 1 FDE)
- 1-2 domain experts from the bank (call center expert, lending expert, etc.)
- Configuration consultant + subject matter experts from the bank
- Non-technical bank staff can configure agents in the Studio
- Domain experts populate the system with the bank's products, knowledge, policies, SOPs

---

## Pricing — Conversational Banking

**Simple and predictable:** Platform fee + LOB fee + Per-interaction rate. LLM compute billed at cost (pass-through).

### 1. Platform fee (per year)

| Tier | Price | What it includes |
|---|---|---|
| **Entry** | from **€350K** | Controlled use, limited risk. One business domain included. |
| **Critical** | **€700K** | Mission-critical, advisory, 24×7 SLA |
| **Enterprise** | **€1.5M** | Bank-wide, all domains included (LOB fee waived) |

Pricing logic: "lock in the €350K and then everything is consumption-based per interaction" — start at Entry, automatically lift to Critical when it gets critical (highest SLA, 24×7), then Enterprise for bank-wide deployment.

### 2. LOB fee (per year)

**€350K per business domain** activated. NOT per customer, NOT per channel.

Domains: Retail · SME · Commercial · Wealth

One business domain is included in the Platform fee. Additional domains charged separately. **Waived on Enterprise tier.**

### 3. Per-interaction fee

| Volume / month | Rate |
|---|---|
| First 500K | €0.070 |
| 1M – 1.5M | €0.063 |
| 2M+ | €0.057 |

Pay for outcomes, not infrastructure. Rate drops with volume.

### 4. LLM tokens

Billed as **transparent pass-through** at cost. No markup. No lock-in.

Customers can:
- Use commercial models (Anthropic, OpenAI, Google) at cost
- Use open-source models (DeepSeek, Gemma, etc.) at cost
- Use Backbase's banking-optimized SLM (FinRAG-12B) at significantly lower cost

Backbase routes dynamically — open-source for simple intents, commercial for complex, SLMs for repetitive high-volume tasks.

### Contract structure

- **1-year contract** — wedge play, low risk
- Auto-upgrade from Entry → Critical → Enterprise as the deployment scales
- For deals > $20M, on-premise deployment is possible (default = cloud)

---

## Positioning vs the build-vs-buy question

Many banks ask: *"How is this better than just using ChatGPT/Claude directly, or building it ourselves with the OpenAI API?"*

Backbase's answer:
- We are **not selling layers** — we are selling solutions
- The challenge is NOT the LLM. The challenge is the **operating layer** wrapped around the LLM: unified context (Nexus), governed authority (Sentinel), banking-specific knowledge (Banking Intent Library), and runtime guardrails (Live Response Validation)
- A bank's own AI team building this from scratch will spend 12-24 months in pilots that never reach production because of governance gaps
- Backbase is **Swiss neutral** — works on any digital banking platform (Backbase or competitor)

---

## Strategic context — why this matters now

### The relationship layer threat

Banks face a strategic threat: customers are starting to do financial conversations in ChatGPT, Claude, and other consumer AI engines. If GPT Plus connects to bank accounts via Plaid (announcement from OpenAI), **GPT becomes the customer's financial advisor**. The bank becomes the back-end utility.

> *"It is really a horrible nightmare scenario if people will do everything inside GPT and they will not go to the commerce platform anymore. They will not go to the travel website anymore. And they will not go to the banking platform anymore. The world is moving in that direction."* — Jouk Pleiter, May 2026

The fight-back: bring the AI relationship INSIDE the bank's mobile app. Conversational Banking is the form factor. Relationship Intelligence is the proactive layer on top.

### The form factor wave

- **20 years ago**: every bank had to add online banking
- **10 years ago**: every bank had to add mobile banking
- **Now**: every bank has to add conversational banking

> *"Everybody who has a 5-star mobile banking app in the next 3 years needs to add this form factor."* — Jouk Pleiter

This drives massive demand. Backbase wedge: 90% upsell into 120+ install base + new logo strategy with non-Backbase install base (3,000+ target banks globally).

---

## Common questions answered

### Channel applicability — is it just consumer?

**No. It's truly unified frontline.** Independent of form factor:
- Consumer, commercial, private banking
- Customer-facing AND employee-facing
- Can also interact in non-mobile channels — Facebook Messenger, WhatsApp, Slack
- It runs Omni

### Language support

Backbase routes dynamically to any LLM via **semantic routing** — automatically detects which model is best for the intent/language. Fintechs managing local dialects can be integrated.

### Cloud dependency

In line with Backbase cloud policy. For deals > $20M, on-premise is possible.

### Overlap with Backbase's Agentic Studio

Yes, there's overlap. **Backbase is likely going to retire its own Agentic Studio and standardize on KAIgentic (Kasisto's Studio).** Decision pending from CTO office. Nexus, Sentinel, and the microservices at the lower layers stay.

### How does it differ from Backbase Flow?

Flow is a product workflow engine for process orchestration. **The Kasisto Studio is NOT Flow.** Don't combine them in customer conversations — keep them distinct. Kasisto Studio configures the *conversation* and its guardrails; Flow configures *deterministic business processes*.

### How does it understand intent on day 1?

LLMs do the first intent detection. Backbase routes inside. New low-code modeling capabilities for intent + knowledge bases ship late June 2026.

### Co-existence with call centers

**Coexist — do not compete with the call center.**

- When agent doesn't know the answer or needs to escalate → seamless handoff to call center solution with full conversation context
- When the customer is on Backbase Workspaces (CSR/Teller/Operations) → workspace becomes conversational by definition
- "Swiss neutral" positioning with any contact center provider

---

## Acceptance criteria for Cortex agents producing Conversational Banking content

- [ ] Frame Conversational Banking as the **next interface**, not as a chatbot/copilot
- [ ] Use **Assist / Transact / Resolve / Grow** as the customer capability framework
- [ ] Include the **3-stage flow** (Understand → Orchestrate → Assure) when describing how it works
- [ ] Anchor to **Banking OS** as the underlying control plane
- [ ] Reference the **3 actors** (Customers, Employees, AI Agents) — don't focus on just one
- [ ] When mentioning customer proof points, source them: BMO 81%, Nedbank 70%, First Financial 26%
- [ ] Mention the **Kasisto acquisition** when establishing credibility (10 years of heritage)
- [ ] Use the **"Live Response Validation"** USP when discussing safety
- [ ] When discussing pricing, use the layered model (Platform fee + LOB fee + Per-interaction + LLM pass-through)
- [ ] Position as a **wedge** that works on any digital banking environment (not a rip-and-replace)
- [ ] Time-to-value: **6-12 weeks** (vs. 12+ months for full digital banking replacement)
- [ ] Apply the language rules from `banking_os.md` Section 17 — never say "chatbot," "virtual assistant," "agent desktop," etc.
