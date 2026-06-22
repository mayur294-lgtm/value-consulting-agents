# Backbase Banking OS — Canonical Positioning Narrative

**Status:** ⭐ CURRENT canonical narrative — June 2026 (v4.0)
**Sources:**
- Banking OS Value Proposition v4.0 (Yashita Arora, Product Marketing) — 2026-06-03
- Banking OS · Conversational Banking deck — June 2026
- Banking OS — Unified Frontline (May 2026) deck
- Banking OS Enablement · Conversational Banking PM Session transcript — 2026-06-05
- Unified Frontline + Sales Plays Continued Enablement AM Session transcript — 2026-05-21 (Jouk Pleiter)

**Added to Cortex:** 2026-06-09 per #67 (knowledge upload) + #66 (solution lines framework)
**Internal use only** — source PDFs marked "Privileged · Not for external distribution"

> **Note on canonical-current convention:** This file is the canonical positioning narrative Cortex agents should use for all new POVs, value lever derivations, ROI models, and consultant deliverables. When a future version of the positioning narrative supersedes this one, this file moves to `knowledge/positioning_history/` and is replaced at the top level. See `knowledge/positioning_history/README.md`.

> **Prior positioning** (pre-June 2026 framing) lives in `knowledge/backbase_platform_lexicon.md` and remains valid as the product capability reference (product lines, customer lifecycle stages, four quadrants, domain variations). The lexicon describes *what Backbase products exist*; this file describes *how Backbase positions its operating model*.

---

## ⚠️ How to treat the numbers in this document

**Most of the numeric claims in this document are Product-Marketing-grade directionals, not defensible benchmarks.** This includes:

- The **"60% of work lives between systems"** framing
- All of the **Section 10 outcomes** ($150–300M+ value unlock, 20–40% cost-to-serve reduction, 10–25% conversion/cross-sell/retention uplift, 3–5x AI cycle acceleration)
- The **"30–60% manual work"** and **"6–12 systems per journey"** figures
- The **"3,000 banks we target globally"** sizing
- Any percentage range presented without a customer name attached

Yashita's source PDF itself flags these as "directional claims from internal sources — validate with CS and customer evidence before any external use." Treat them the same way Backbase's own GTM teams do: **as anchors for C-suite conversation**, not as Cortex's defensible benchmarks.

### Rules for Cortex agents

1. **Use directionals to frame a hypothesis, never to close a business case.** "Banks of your size typically see 20–40% cost-to-serve reduction in this domain — let's pressure-test that against your numbers" is fine. "Backbase delivers 20–40% cost-to-serve reduction" as a load-bearing claim in an ROI model is not.
2. **In Cortex outputs, label these clearly** as "directional benchmarks (Backbase marketing claims, to be validated)" — never present them as Cortex's own analytical findings.
3. **Always run sensitivity** — the conservative case in any ROI model must NOT depend on hitting the top of these ranges.
4. **Cite real customer outcomes when you have them.** The BMO 81% containment, Nedbank 70% chat-volume reduction, and First Financial 26% product-line uplift in `conversational_banking.md` are customer-attributed and more defensible — but still validate against the underlying engagement before quoting.
5. **For business-case-grade benchmarks**, draw from `knowledge/standards/benchmark_evolution.md` and engagement-specific evidence (annual reports, client data, peer comparisons) — not from this document.

---

## 1. Strategic hierarchy (locked structure)

Always present in this hierarchy. **Never reorder. Never collapse.**

| Level | Concept | What it is |
|---|---|---|
| 1 | **Unified Frontline** | The new operating model for banks — the **category** |
| 2 | **Banking OS** | The system that operates and coordinates the Unified Frontline — the **product** |
| 3 | **Control Plane** | The operational brain — Four Operational Powers (Understand · Run · Authorize · Optimize) — the **architecture** |
| 4 | **Elastic Operations** | Scale operations without scaling headcount — the **economic outcome** |

**Critical naming rule:** The Unified Frontline and the Banking OS are always distinct. Never say "Unified Frontline Banking OS" or "Unified Frontline OS." The Unified Frontline is what the bank *becomes*. The Banking OS is the *system that gets them there*.

---

## 2. The 4 Messaging Pillars

These 4 beliefs anchor every Backbase piece of content. Use them in every POV, ROI deck, value lever derivation, capability assessment, and roadmap.

### Pillar 1: Fragmentation is the enemy
Every bank has hundreds of systems. But the real work happens *between* them. **60% of banking work lives in the whitespace** — handoffs, exceptions, coordination that no system owns. Banks don't need more systems. They need a better operating model. AI makes it worse: agents need unified context, shared data, and authorized decision authority. Without it, banks get *AI theater* instead of AI transformation.

### Pillar 2: The next decade is an operating model competition
AI does not fix bad architecture. Better apps do not fix fragmented execution. The banks that win will not win because of better models or better channels. They will win because of **better operating models**. The Banking OS defines the blueprint.

### Pillar 3: The Unified Frontline is the new battleground
The question is no longer how the app looks. It is how the frontline business runs — and how it scales. Banks that unify Customer Engagement and Banking Operations will achieve **Elastic Operations**.

### Pillar 4: Control is not optional
Bank-grade AI requires governance, auditability, and proof. Every agent action must be authorized, traceable, and revocable. **No action executes without a Decision Token.** Sentinel is what moves banks from AI pilots to AI in production.

---

## 3. The problem we solve

### The whitespace between systems
Banks operate dozens of disconnected systems across the frontline — digital channels, contact centers, branch networks, RM portals, and back-office operations for KYC, disputes, fraud, and loan underwriting. Each runs on separate infrastructure with separate data and separate views of the customer.

**A meaningful share of frontline work lives in the whitespace between them:**
- Handoffs · Manual coordination · Exceptions
- Copy/paste · Swivel chair · Spreadsheets · E-mail · Meetings
- Manual review · Evidence gathering · Follow-ups

> **Marketing claim to be aware of:** Backbase's GTM materials frame this as **"60% of frontline work lives in the whitespace."** This is a directional Product Marketing anchor, not a benchmark Cortex has validated. Use it to *frame the conversation* with executives (it tends to land — most banks recognize the pattern even if the exact percentage is unfamiliar). For ROI models, value lever sizing, or any output where the number is load-bearing, **measure the actual share at the specific bank** rather than treating 60% as established truth.

This is the structural problem. Scaling up means hiring more people to bridge the gaps. AI makes it worse — agents need complete customer context, a shared source of truth, and authorized decision authority. On a fragmented foundation, agents operate on partial data, follow inconsistent rules, and write back to different systems. **The result is not automation — it is chaos at higher speed.**

### Today's fragmented frontline — directional symptoms (marketing framing)
- 6–12 systems per customer journey
- 30–60% manual work
- High cost-to-serve
- Slow cycle times
- AI stuck in pilots

*Treat these as conversation anchors, not bank-specific facts. They come from Backbase Product Marketing positioning and have not been independently validated by Cortex.*

### Banks don't need more systems. They need a better operating model.

---

## 4. The solution — AI-native Banking OS

The Backbase AI-native Banking OS closes the loop between what customers want and what banks deliver. Customer intent starts in digital. Fulfillment breaks inside the bank. The Banking OS coordinates execution across digital, front office, mid-office, and back office — using agents, workflows, and humans in the right combination, with governed execution at every step.

**It sits above systems of record.** It does NOT replace cores, CRMs, or data platforms. It is the operating layer that makes everything above the ledger work as one.

### Two operating domains

| Domain | What it is | What it does |
|---|---|---|
| **Banking OS Runtime** | The live execution environment | Where customers interact, employees work, agents execute, and policies enforce. The 6-layer stack of the platform. |
| **Banking OS Factory** | The Transformation Engine | How banks design, build, and deploy AI-native operations. Execution model = **Mission Sprint** (6-12 weeks). Unit of delivery = **Mission Contract** (versioned, declarative package). |

### The 3 actors
Historically banks had **2 actors**: Customers and Employees. Growth meant hiring. AI introduces a **3rd actor**: **AI Agents**. This creates a new imperative — banks must authorize what every agent is entitled to do, under what authority, and with what limits.

---

## 5. The Four Operational Powers

Always present in this sequence. **Each power maps to a named system component.**

| # | Power | Component | What it does |
|---|---|---|---|
| 1 | **Understand** | **Nexus** (Semantic Layer) | The shared source of customer truth across all actors and layers |
| 2 | **Run** | **Orchestration** (Process Studio + Agent Studio) | Executes workflows and missions across employees, AI agents, and systems |
| 3 | **Authorize** | **Sentinel** (Authority Layer) | Identity, policies, approvals, Decision Authority, governance |
| 4 | **Optimize** | **Intelligence Layer** | Data, AI, and operational optimization — including banking-optimized small language models |

### Architecture — 6-layer Banking OS Runtime + Sentinel

```
Layer                Component                  What it provides
───────────────────────────────────────────────────────────────────
Interaction          Composable Banking Apps    Customer-facing experiences
                     Composable Workspaces      Employee operational environments
                     Conversational Interfaces  Natural-language interaction
───────────────────────────────────────────────────────────────────
Orchestration        Banking Capabilities       Reusable microservices
                     Process Studio             Deterministic workflows
                     Agent Studio               Agentic workflows
───────────────────────────────────────────────────────────────────
Intelligence         Model Registry             Pretrained banking models,
                     Training & Serving         custom models, third-party LLMs
                     Operational Learning       Banking-optimized SLMs
                                                EU AI Act compliance built in
───────────────────────────────────────────────────────────────────
Semantic (Nexus)     Banking Ontology           Structured definitions
                     Customer State Graph       Live composite customer view
                     Context Graph              Historical decision memory
                     Action & Behavior Layer    Entitlements and rules
───────────────────────────────────────────────────────────────────
Connectivity         Connectors                 Core banking, CRM, cards,
(Grand Central)      Event Streams              payments, KYC, fraud, docs
                     Marketplace / Fintechs     External integrations
───────────────────────────────────────────────────────────────────
Sentinel (Authority) Identity & Roles           Runs *alongside* every layer.
                     Policy Engine              No action executes — by any
                     Decision Engine            actor — without a Decision Token.
                     Risk & Compliance          Decision Tokens record:
                     Security                   policy applied, actor identity,
                     Governance & Audit         model version, outcome, context.
```

### Nexus — the truth layer (deeper detail)

Nexus is NOT a data lake. NOT a system of record. It is the **operational truth layer** that sits on top of cores and data warehouses and gives every actor a single, consistent, decision-quality view of the customer.

Nexus has two elements (roughly 50/50 split):

1. **Customer State Graph** — what the customer *is today*. Aggregated from all backend systems. Accounts (current $X, savings $X), debt (mortgage $X-$Y/mo), credit (FICO X, on-time %).
2. **Context Graph** — what decisions have been *made about this customer in the past*. Stores: action, applied policy, exception (e.g. DTI 43% override), reasoning trace (8yr relationship, 12% salary growth, 3 clean disputes), monitoring conditions, outcomes, relationship history.

**Why this matters:** For the first time in banking history, banks can store the historical decision trail. KYC/AML decisions, fraud detections, payment disputes — historically, all the reasoning disappeared once the customer was onboarded. With Nexus, decisions and their evidence are preserved, queryable, and reusable for future reasoning.

### Sentinel — the unlock for AI in production

Most AI is stuck in pilots because it cannot meet bank-grade governance. Sentinel is the answer:

- **Set the Rules**: Authority (who may decide) · Policies (under which rules) · Entitlements (multi-entity access rights)
- **Authority Engine**: real-time guard rails wrapped around every LLM/agent action
- **Decision Token**: real-time authorization with scope, constraints, and reason codes
- **Outcomes**: Approve · Review · Decline · Escalate
- **Governance**: Authority Spectrum (recommend → approve → execute) · Observability · Auditability

**The key insight:** Core banking and digital banking are deterministic. If you wire money to B, it is 100% guaranteed based on deterministic logic. Agentic AI is not 100% accurate — LLMs hallucinate. You cannot get an aentic process signed off by Risk & Compliance, and you cannot explain it to the regulator, without a deterministic guard rail and harness around the LLM. **Sentinel is that guard rail.**

---

## 6. The 4 Solutions × 2 Blocks

Always present in this structure when describing solutions.

```
┌─ BLOCK 1: CUSTOMER ENGAGEMENT ─────────────────────────────┐
│  (Coordinate customer lifecycle execution)                  │
│                                                              │
│  1. Digital Banking          — Modernize digital foundation │
│  2. Conversational Banking   — Natural language interface   │
│  3. Relationship Intelligence— Bank-owned AI for growth     │
└──────────────────────────────────────────────────────────────┘
┌─ BLOCK 2: BANKING OPERATIONS ──────────────────────────────┐
│  (Coordinate front-to-back work execution)                  │
│                                                              │
│  4. Customer Resolution Loops— Close the loop on every      │
│                                customer intent              │
│     (also called "Customer Operations" in some materials)    │
└──────────────────────────────────────────────────────────────┘
                       │
              Banking OS Control Plane
              (Governed Execution)
```

### Solution 1: Digital Banking (Replacement Play)

Modernize the digital foundation and move toward the Unified Frontline. Full digital banking stack: online + mobile banking, digital assist, front-office workspaces. **For banks at end of lifecycle on their current platform.** This is the **replacement play** — binary: modernize or don't.

- Primary buyers: CDO, CTO
- Time-to-value: **6-24 months** (typically 12 months)
- Sales motion: Replacement / RFP

### Solution 2: Conversational Banking (Wedge Play)

Give customers and employees a natural language interface. Enables domain agents to resolve complex inquiries through chat and voice — intent detection, policy-bound responses, workflow orchestration, human handoff. **Operationalized in 12 weeks on any digital banking environment** (Backbase OR competitor — Swiss neutral). No rip-and-replace.

- Primary buyers: CDO, Head of Digital
- Time-to-value: **6-12 weeks** (vs. 12+ months for Digital Banking)
- Sales motion: **Wedge** — land in non-Backbase digital banking environments
- Powered by: **Kasisto** acquisition (KAIgentic platform, KAI-GPT model, FinRAG-12B SLM)
- Reference customers: BMO, Standard Chartered, Westpac, Emirates NBD (Olivia), Nedbank (Enbi), BMO Bot, First Financial (Gabby), a Tier-1 US national bank (in flight)
- Customer proof points: 81% request containment (BMO), 70% chat volume reduction (Nedbank), 26% product line increases (First Financial)

See `knowledge/conversational_banking.md` for the full solution detail.

### Solution 3: Relationship Intelligence (Wedge Play — fight-back)

Bank-owned AI for financial progress and relationship growth. Monitors financial behavior, surfaces personalized guidance and product recommendations, embedded directly in the customer's mobile app. **The fight-back play against OpenAI/Claude competing for the AI relationship layer.**

The strategic threat: If customers do their financial conversations in GPT/Claude (e.g., GPT Plus connects to bank accounts via Plaid → GPT becomes the financial advisor), the bank loses the customer relationship layer. Banks need to fight back inside their own mobile app.

- Primary buyers: CDO, Head of Retail
- Time-to-value: Wedge — works on any mobile banking platform
- Combines: Coach + CLO (Cross-Lending Origination) into one product
- Open Banking integrations: Plaid, Salt Edge, Yodlee
- Outcomes: improve financial wellness AND grow share of wallet

### Solution 4: Customer Resolution Loops (Wedge Play)

Close the loop from customer request to resolved outcome. Every significant customer intent (card resolution, dispute, payment inquiry, KYC update, fraud intake, onboarding, loan origination) triggers a workflow loop that the Banking OS coordinates across digital, front office, mid-office, and back office.

The **Customer Intent Leakage Assessment** identifies where loops are broken and prioritizes which to fix first based on customer pain, operational cost, and speed to proof.

- Primary buyers: COO, Head of Operations
- Time-to-value: Wedge — works without changing the digital banking layer
- Formerly called: APA (Agentic Process Automation), Agentic Servicing, BO (Business Process Orchestration). **Now retired — use Customer Resolution Loops.**

---

## 7. Land & Expand sales motion

```
┌───────────────────┐   ┌─────────────────────────────────────────┐
│       LAND        │   │              EXPAND                       │
│                   │   │                                           │
│  Conversational   │ → │  Relationship Intelligence                │
│      Banking      │   │  (financial wellness + product holding)   │
│                   │   │  → proactive nudges → upsell             │
│  (live in 6-12    │   │                                           │
│   weeks on any    │   │  Customer Operations / Resolution Loops   │
│   digital banking │   │  (close the loop on every request)        │
│   platform)       │   │  → faster resolution times                │
└───────────────────┘   └─────────────────────────────────────────┘
                          Next solution lines, same Banking OS
```

**The wedge logic:** Conversational Banking, Relationship Intelligence, and Customer Resolution Loops are sold standalone. They do NOT require Backbase Digital Banking. They are *additive* on any digital banking environment (Backbase or competitor). This makes them a perfect wedge into non-Backbase install bases.

**Backbase's strategy:**
- 90% upsell success rate target into the **install base** of 120+ existing Backbase customers
- Conversational Banking as the icebreaker for **new logos** (3,000+ target banks globally)
- Build credibility: 10 years of Kasisto track record + Backbase brand + distribution

---

## 8. Mission Sprint — the delivery model

The Mission Sprint is the execution model: **6-12 weeks from scoped problem to working AI in production.**

```
DESIGN              BUILD               DEPLOY
─────────           ─────────           ─────────
Define mission      Configure           Launch on
scope and KPIs      workflows and       Banking OS
                    agents
Map workflow                            Monitor and
and workspace       Connect systems     govern execution
                    and data
Model policies                          Prove value
and guardrails      Test with           and optimize
                    simulation and
                    evidence
```

Each Mission Sprint delivers a **Mission Contract** — a versioned, declarative package of Nexus bindings, Sentinel policies, workflows, and agents. The first fixed loop becomes the blueprint for the next.

**"Land fast. Prove value. Expand."**

### Implementation team model

- Small team: **1-2 Backbase AI Consultants** (typically 1 SE + 1 FDE)
- Configuration consultant + subject matter experts from the bank
- Low-code/no-code platform — non-technical bank staff can configure agents in the Studio
- Domain experts from the bank populate the system with their products, knowledge, policies, SOPs
- Typical workflow: pick the use case → 4-hour Ignite Lite workshop → Mission Sprint (6-12 weeks) → live

---

## 9. Progressive Autonomy

Banks do not flip a switch from manual to autonomous. They progress through **3 levels of AI delegation**:

| Level | Description |
|---|---|
| **Assistive** | AI prepares insights, surfaces recommendations, and gathers evidence. Humans review and decide. |
| **Delegated** | AI executes actions with **explicit human approval**. Agents prepare cases, propose resolutions, and execute within guardrails. |
| **Autonomous** | AI executes within predefined guardrails without per-action human approval. Sentinel governs the boundaries. Autonomy is **earned, measured, and revocable**. |

Each domain can operate at a different autonomy level. The model adapts to the bank's risk appetite and regulatory context.

---

## 10. Outcomes — Elastic Operations (directional marketing ranges)

Elastic Operations is the ability for a bank to scale operations without scaling headcount linearly, by combining employees and AI agents under coordinated execution — with full Decision Authority at every step.

> ⚠️ **All numbers in the table below are Product-Marketing-grade directionals**, not Cortex-validated benchmarks. Yashita's source PDF flags them as *"directional claims from internal sources — validate with CS and customer evidence before any external use."* Treat them the same way:
>
> - **Use them as anchors** to frame C-suite conversations and shape executive hypotheses
> - **Do NOT use them as load-bearing inputs** in defensible ROI models, business cases, or client deliverables without bank-specific validation
> - **Always run sensitivity** — the conservative case should never rely on hitting the top of these ranges
> - **In Cortex outputs, label them clearly** as "directional benchmarks (Backbase marketing claims, to be validated)" — never as Cortex's own findings

| Dimension | Outcome | Marketing range *(directional)* |
|---|---|---|
| **Growth** | Conversion, cross-sell, retention uplift via Relationship Intelligence + Customer Resolution Loops | 10–25% uplift |
| **Efficiency** | Cost-to-serve reduction via Customer Resolution Loops + agentic operations | 20–40% reduction |
| **Control** | Authority, policy, and proof at every execution | Full Decision Token audit trail *(qualitative)* |
| **Consistency** | Stateful workflows across digital, branch, contact center | Every actor on same customer state *(qualitative)* |
| **Velocity** | AI approval-to-production cycle acceleration | 3–5x faster |
| **Total value unlock** | Annual, bank-size dependent | **$150M – $300M+** |

### What "validated" looks like for a Cortex output

When Cortex produces a value lever, capability score, or ROI model for a specific bank, it should:

1. **Replace the directional range with a bank-specific calculation** — current cost-to-serve × addressable population × realistic capture rate, etc.
2. **Cite the data source** that produced the number (annual report metric, peer benchmark from `benchmarks/`, client interview evidence, etc.)
3. **Run a conservative case** at the bottom of the marketing range (or lower)
4. **Document the assumption gap** if the bank-specific number isn't yet available — flag for validation in the assumptions register
5. **Never present the marketing range itself** as the projected business case

The Control and Consistency rows above are qualitative outcomes — those are fine to claim. The Growth/Efficiency/Velocity/Value-unlock rows are quantitative and need bank-specific validation before they carry weight.

---

## 11. What Backbase does NOT replace

Backbase does not replace:
- Systems of record
- CRM
- Data platforms

Nexus is NOT Snowflake or Databricks. Those are data lakes for analytical workloads. Nexus is the **operational truth layer** — it sits on top of data lakes and cores, giving every actor a single decision-quality view.

### Capability matrix vs CRM

| Capability | Backbase | CRM |
|---|---|---|
| Customer channels (mobile, web, conversational) | Yes | No |
| Banking logic and domain workflows | Yes | No |
| Onboarding and origination (front-to-back) | Yes | No |
| Financial guidance — Coach | Yes | No |
| Marketing campaigns | Yes | Co-exist |
| Contact center | Yes | Co-exist |
| RM Workspace | Yes | Co-exist |
| Sales pipeline (leads and funnel) | No | Yes |

- **Banks with large CRM investments**: Backbase coexists with CRM
- **Banks with limited CRM investment**: Backbase is the direct alternative for servicing functions

---

## 12. Personas — playbook by role

### Tier 1 — Executive decision-makers

| Persona | Measured on | Primary pain | What lands | The ask |
|---|---|---|---|---|
| **COO** | Cost-to-income, service levels, throughput | High volume manual exceptions. Fragmented systems prevent STP. Scaling means scaling headcount. Operational risk from non-compliant manual workarounds. | Elastic Operations scales without headcount. Customer Resolution Loops target biggest cost center (20-40% cost-to-serve reduction). Progressive autonomy = they control the pace. | Identify one high-volume resolution loop (disputes, KYC, payments). Run a Value Leakage Assessment. Scope a Mission Sprint against a cost-to-serve target. |
| **CTO** | Operational costs, time-to-market, innovation delivery | Bespoke solutions across frontline. Integrating multiple technologies. Delivering innovation on complex legacy stack. | Four Operational Powers with locked interfaces. Factory enforces consistent patterns. Grand Central standardizes connectivity. Composable architecture — each domain reuses the same patterns. | Map the frontline architecture. Scope a first domain deployment to prove architectural value. |
| **CIO** | IT uptime, digital adoption, cybersecurity resilience, cost-to-revenue | High volume manual repetitive IT operations. Resource drain from patching, monitoring, servicing. Rising cyber + regulatory demands. Lack of skilled automation talent. | Progressive transformation via Transformation Engine — domain by domain, no rip-and-replace. Sentinel governance and audit built into every agent action. Banking OS Transformation Engine + Delivery OS standardizes build-test-deploy. | Assess AI readiness across the frontline. Scope a first domain deployment with Transformation Engine and Delivery OS. |
| **CDO** | Customer satisfaction, digital conversion, market share | Siloed digital experiences. Speed of change can't keep up with innovation. Fear of losing the customer relationship layer to AI engines (GPT, Claude). | Conversational Banking in 12 weeks. Relationship Intelligence is the **fight-back** play against AI disintermediation. Unified Frontline turns digital investment into compounding advantage. | Identify the highest-value origination journey with worst drop-off. Scope an Agentic Origination mission. |

### Tier 2 — Influencers and functional leaders

| Persona | Primary pain | What lands | The ask |
|---|---|---|---|
| **Head of Risk / CISO** | Rapid assessment of emerging tech. Navigating compliance. Balancing risk and innovation. | No action executes without a Decision Token. Full evidence bundles. Autonomy governed, graduated, revocable. Sentinel is what moves AI from pilot to production in a compliant way. | Run a governance assessment. Scope a Sentinel deployment for the highest-risk domain. |
| **Head of Data and AI** | AI models that don't drive action. Data silos. High regulatory scrutiny. | Nexus gives agents unified operational context — not a data lake, the operational truth layer on top. Sentinel provides Decision Authority. Intelligence Layer with Model Registry, SLMs, EU AI compliance. | Identify the AI use case closest to production that is stuck. Scope a deployment on Nexus and Sentinel. |
| **Head of Lending** | Drop-off in loan applications. Manual handoffs between application and funding. Slow approvals. | Customer Resolution Loops for origination compress time-to-yes. STP where possible, intelligent exception handling where required. Customer Intent Leakage Assessment identifies where the loop breaks. | Pick the origination journey with highest volume and worst conversion. Scope against cost and conversion targets. |
| **Head of Architecture** | Legacy systems slowing AI. Custom integrations per use case. Fragmented tooling. | Four Operational Powers with locked interfaces. Factory enforces consistent patterns. Grand Central standardizes connectivity. Nexus and Sentinel as reusable infrastructure. | Map integration landscape. Scope a Grand Central deployment to establish the reuse pattern. |
| **Head of Digital Transformation** | Technical debt. End-of-life systems. Waterfall culture. C-level alignment. | Mission Sprint — 6-12 weeks from scoped problem to working AI in production. 1 domain at a time. First mission becomes the blueprint for the next. | Identify the one workflow causing the most pain. Scope a Transformation Engine mission with 3-6 month timeline. |
| **Head of Delivery** | Aging customized infrastructure. High maintenance cost. Talent shortage. | Factory accelerates configuration over coding. Studio, Starter Packs, Delivery OS. Mission Contract as the delivery artifact with clear milestones. | Scope a Starter Pack deployment for the highest-priority domain. Evaluate implementation timeline and resource requirements. |

---

## 13. Pricing model

**Simple and predictable** — Platform fee + LOB fee + Per-interaction rate. LLM compute billed at cost (pass-through, no markup).

### 1. Platform fee (per year)

| Tier | Price | What it includes |
|---|---|---|
| **Entry** | from **€350K** | Controlled use, limited risk. One business domain included. |
| **Critical** | **€700K** | Mission-critical, advisory, 24×7 SLA |
| **Enterprise** | **€1.5M** | Bank-wide, all domains included (LOB fee waived) |

A small entry point — scale up as the platform becomes mission-critical.

### 2. LOB fee (per year)

**€350K / domain** activated per business domain (NOT per customer or channel).

Domains: Retail · SME · Commercial · Wealth

One business domain is included in the Platform fee. Additional domains charged separately. **Waived on Enterprise tier.**

### 3. Per-interaction fee

| Volume / month | Rate |
|---|---|
| First 500K | €0.070 |
| 1M – 1.5M | €0.063 |
| 2M+ | €0.057 |

Pay for outcomes, not infrastructure. Rate drops with volume.

### 4. LLM tokens (compute)

Billed as **transparent pass-through** — at cost, no markup, no lock-in to any model provider.

Customers can:
- Use commercial models (OpenAI, Anthropic, Google) — pass-through at cost
- Use open-source models (DeepSeek, Gemma, etc.) — pass-through at cost
- Use Backbase's **banking-optimized SLMs** (FinRAG-12B, 12B params, banking-tuned) — significantly cheaper, faster, more accurate for domain tasks

Backbase will route dynamically — open-source for simple intents, commercial models where needed, SLMs for repetitive high-volume tasks.

### Contract structure

- **1-year contract** — wedge play, low risk, low commitment
- Can be upgraded from Entry → Critical → Enterprise automatically
- For deals > $20M, on-premise is possible (default = cloud)

---

## 14. Sales toolkit — 60-second pitch

> Every bank has hundreds of systems. But the real work of the bank happens between those systems — and Backbase Product Marketing's framing is that **roughly 60% of frontline work lives in that whitespace**: handoffs, exceptions, coordination that no system owns. AI makes it worse: agents need unified context, authorized decision authority, and a shared source of truth. On a fragmented foundation, they cannot get any of it.
>
> The question is not how to improve the app. It is how to run the frontline business — and how to scale it. The next decade will not be defined by better channels. It will be defined by better operating models.
>
> Backbase is the **Banking OS** — the system that closes the loop between what customers want and what banks deliver. Customer intent starts in digital. Fulfillment breaks inside the bank. We coordinate execution across digital, front office, and operations — with agents, workflows, and humans in the right combination.
>
> The result is **Elastic Operations**: scale throughput without scaling headcount, with full control.

*Note for Cortex: the 60% figure is a Backbase Product Marketing anchor, not a Cortex benchmark. Use it as framing language with executives; never as a load-bearing input to an ROI model. See the warning at the top of this document.*

---

## 15. Discovery questions

The 7 high-signal discovery questions to ask in any banking conversation:

| Question | What it reveals | Where it leads |
|---|---|---|
| "What happens between when a customer submits a request and when it is resolved?" | Loop breakage, whitespace pain | Customer Resolution Loops, Elastic Operations |
| "How many separate systems does your frontline run on today?" | Degree of fragmentation | Unified Frontline value, operating model positioning |
| "What percentage of your operations team's time goes to exception handling?" | Whitespace pain, manual coordination cost | Customer Resolution Loops, Elastic Operations |
| "When your regulator asks how you govern AI decisions, what do you show them?" | Governance maturity | Sentinel, Decision Authority, Decision Tokens |
| "How are you thinking about customers moving their financial conversations to AI engines such ChatGPT or Claude?" | AI relationship threat awareness | Relationship Intelligence, fight-back positioning |
| "What is your drop-off rate between application start and funding?" | Origination friction | Customer Resolution Loops, front-to-back orchestration |
| "Are you scaling operations by adding headcount or by adding capacity?" | Operating model maturity | Elastic Operations, progressive autonomy |

---

## 16. Objection handling

| Objection | Response |
|---|---|
| **"We already have a CRM for this."** | The Banking OS is not CRM. CRM manages the sales pipeline. The Banking OS coordinates execution across banking work — front-to-back workflows, domain logic, AI agents, and governance. For banks with large CRM investments, we coexist and complement. |
| **"We're building our own AI layer."** | Building an AI layer is not the same as building an operating model. The challenge is not the model — it is the unified context layer, the orchestration, and the governed decision authority underneath. The Banking OS provides the shared truth (Nexus) and governed authority (Sentinel) every agent needs, regardless of where it was built. |
| **"This sounds like rip-and-replace."** | Three of our four solutions — Conversational Banking, Relationship Intelligence, and Customer Resolution Loops — land as wedge plays with no rip-and-replace required. We can be live in 12 weeks inside your existing environment. |
| **"How do we know AI is safe?"** | Every action — by any actor — requires a Decision Token from Sentinel before it executes. Full evidence bundles. Deterministic policy enforcement. Autonomy levels are graduated and revocable. |
| **"We're happy with our current digital banking."** | Understood. Conversational Banking, Relationship Intelligence, and Customer Resolution Loops all work on top of your existing digital banking platform. No migration needed. |

---

## 17. Language rules

**Source: Banking OS Value Proposition v4.0, Section "Language rules"**

### Always capitalize
- Backbase
- Banking OS
- AI-native Banking OS
- Nexus
- Sentinel

### Don't say / Say instead

| Don't say | Say instead |
|---|---|
| Chatbot, copilot, virtual assistant | **Conversational Banking** |
| Agent desktop, portal | **Composable Workspace** |
| AI governance, guardrails, permissions | **Decision Authority (Sentinel)** |
| Data layer, Customer 360 | **Semantic Layer (Nexus)** |
| Platform (when meaning the product) | **Operating System (Banking OS)** |
| Middleware, ESB, API gateway | **Connectivity Layer (Grand Central)** |
| APA, Agentic Process Automation | **Banking operations, Customer Resolution Loops** |
| CLO (standalone) | **Relationship Intelligence** |
| Coach (standalone) | **Relationship Intelligence** |
| Agentic Servicing | **Banking operations, Customer Resolution Loops** |
| Agentic Onboarding & Origination | **Customer Resolution Loops** |
| North gate / Northgate | **Customer Engagement** |
| South gate / Southgate | **Banking Operations** |
| DevOps, CI/CD, build pipeline | **Delivery OS (inside Banking OS Factory)** |
| Engagement banking platform | **AI-native Banking OS** |
| EBP | (retired — now part of Banking OS) |

### Naming convention — Workspaces vs Agents

**Roles get Workspaces. Domains provide Agents.**

| Correct | Incorrect |
|---|---|
| CSR Workspace with embedded Servicing Agents | CSR Agent |
| RM Workspace with embedded Relationship Agents | RM Agent |
| Underwriting Workspace with embedded Credit Agents | Underwriting Agent |

### Retired language — never use

- Engagement banking / Engagement Banking Platform / AI-powered Banking Platform / EBP
- APA / Agentic Process Automation
- Agentic Servicing (standalone)
- Agentic Onboarding & Origination (standalone)
- CLO (standalone)
- Coach (standalone)
- Northgate / Southgate
- "3 execution modes" (now 4 solutions across 2 blocks)

### Sentinel framing — always use this when describing AI governance

> **"AI can guide, summarise, classify, and recommend. Sentinel governs execution."**

### Customer Resolution Loops — language guide

| Do say | Don't lead with |
|---|---|
| Customer intent | Generic workflow automation |
| Fulfilment | Case management |
| Resolution loop | AI agents replacing operations |
| Customer-facing execution surface | Digital self-service only |
| Outside-in resolution | Chatbot |
| Governed execution | Internal task management |
| No-rip-and-replace resolution layer | Back-office automation only |
| Customer Resolution Mission | — |
| Customer Intent Leakage Assessment | — |

---

## 18. Customer Intent Leakage Assessment

Cortex's most important tool for Customer Resolution Loops conversations. **Use this to scope the first Mission for any customer engagement.**

### The 5-step assessment process

```
1. CAPTURE CUSTOMER INTENT
   What is the customer trying to resolve?
   Examples: "My card is blocked." "Where is my payment?"
   "I don't recognize this transaction."

2. MAP RESOLUTION LEAKAGE — find where intent gets delayed,
   repeated, reworked, or lost.

   Four leakage types:
   • TIME leakage      — long resolution time
   • CONTACT leakage   — repeat calls, status inquiries
   • EVIDENCE leakage  — missing info, rework
   • OWNERSHIP leakage — handoffs, manual rescue

   Broken loop trace:
   Digital frontline → Operations → Legacy systems → Customer status

3. PRIORITIZE MISSION OPPORTUNITY
   Select the broken loop with best:
   • Customer pain
   • Operational cost
   • Speed to proof

4. LAUNCH CUSTOMER RESOLUTION MISSION
   Fix the loop from digital → operations → back
   Governed by Banking OS

5. PROVE ROI & SCALE
   Turn the first fixed loop into a repeatable mission pattern.
```

### Assessment outputs
- Recommended First Mission
- ROI Estimate
- Pilot Plan

### Whitespace matrix — where to look first

This matrix is the conversation starter for "where do we begin?" Rate each cell HIGH (significant whitespace work), MED (moderate), LOW.

| Domain → / Vertical ↓ | Onboarding Ops | Account Servicing | Disputes & Chargebacks | Payment & Cash Mgmt | Loan Origination | Credit Risk & Decisioning | KYC & Due Diligence | Financial Crime & Fraud | Regulatory & Compliance |
|---|---|---|---|---|---|---|---|---|---|
| **Retail Banking** | MED | HIGH | HIGH | LOW | HIGH | MED | MED | HIGH | MED |
| **SME Banking** | HIGH | MED | HIGH | MED | HIGH | HIGH | MED | MED | MED |
| **Commercial Banking** | HIGH | MED | MED | HIGH | HIGH | MED | HIGH | HIGH | HIGH |
| **Wealth + Private Banking** | HIGH | MED | LOW | MED | MED | MED | HIGH | HIGH | HIGH |

---

## 19. Final-check rubric — before any Cortex output goes out

Apply this checklist to every POV, ROI deck, capability assessment, or roadmap Cortex generates that touches Banking OS positioning:

- [ ] Does it respect the **strategic hierarchy** (Unified Frontline → Banking OS → Control Plane → Elastic Operations)?
- [ ] Is the **operating model** the primary frame (not channels, not apps)?
- [ ] Are the **four operational powers** (Understand / Run / Authorize / Optimize) present?
- [ ] Are the **two domains** (Banking OS Runtime + Transformation Engine) present?
- [ ] Does **Workspace** remain primary over embedded intelligence (not "CSR Agent" — "CSR Workspace with embedded Servicing Agents")?
- [ ] Does everything anchor to the **Unified Frontline as category** and **Elastic Operations as outcome**?
- [ ] Is **fragmentation framed as the enemy**? (The 60% whitespace stat is OK as a conversational anchor — but explicitly labeled as a Backbase marketing directional, **not** as Cortex's own benchmark, and never as a load-bearing input to ROI calculations)
- [ ] Are **directional outcome ranges** (10–25%, 20–40%, $150–300M, 3–5x — see Section 10) used only as framing language, not as the projected business case? Every quantitative claim in the output anchors to a bank-specific source.
- [ ] Is **Sentinel** present whenever AI governance is discussed?
- [ ] Is **Nexus** described as the **operational truth layer** (NOT data lake, NOT system of record)?
- [ ] Is the **3-actor model** (Customers + Employees + AI Agents) used when describing the operating model?
- [ ] Are **customer proof points** sourced (BMO 81%, Nedbank 70%, First Financial 26%, etc.), attributed to the specific customer, and not invented? (These are Backbase-cited customer outcomes — they are more defensible than the directional ranges but still validate before quoting in a client output.)
- [ ] Does it use the language rules (no retired terms — no "chatbot," "APA," "Coach standalone," "Northgate," etc.)?

---

## 20. Backbase company facts (for context)

- **120+ live bank/CU customers**
- **$350M+ revenue**
- **2,000+ global FTEs** (700+ R&D, 900+ FDE)
- Offices: Amsterdam, Atlanta, Mexico, Poland, India, Singapore
- **Forrester Wave Q2 2026:** Leader position (Digital Banking Engagement Platforms)
- **Awards:** Forrester Wave Leader 2025, Customer Favorite 2025
- Global partners: McKinsey, EY, PwC, Kearney, BCG + 28 local

### Analyst quotes
- *"…the Palantir of Banking. An industry-specific, out-of-the-box ontology is a strategic moat that generic semantic graphs cannot replicate."* — Director Analyst: AI, Gartner
- *"I am seeing big players in the market move into this AI operating system space… but Backbase seems to be light years ahead of the traditional banking vendors."* — Senior Research Director, Banking, Gartner

### Reference customers (live or in flight)
Eastern Bank · Danske Bank · EverBank · BECU · Standard Bank · Alliant · MyState Bank · dskbank · Evelyn Partners · ITM Bank · Chinabank · Banco Security · BDO · MCB · SNB · BMO · Nedbank · Westpac · Standard Chartered · Emirates NBD · First Financial

---

## How to use this document by role

| Role | Start here |
|---|---|
| **Sales / CS** | Section 14 (60-second pitch) → Section 15 (Discovery questions) → Section 16 (Objection handling) → Section 12 (Persona playbooks) before any C-suite meeting → full doc when you need substance |
| **Value Consultants & Solution Engineers** | Full doc. Pay particular attention to Section 18 (Value Leakage Assessment) — this is the primary scoping tool. |
| **Cortex agents producing POVs / value levers / ROI** | Section 5 (architecture) + Section 6 (4 solutions × 2 blocks) + Section 12 (personas) + Section 18 (Leakage Assessment) + Section 19 (final-check rubric) |
| **Cortex agents producing capability assessments / roadmaps** | Section 5 (6-layer architecture maps to capability dimensions) + Section 10 (outcomes that ROI ties to) + Section 9 (progressive autonomy = maturity scale) |
| **Content / messaging** | Section 1 (hierarchy) + Section 2 (4 pillars) + Section 17 (language rules) + Section 19 (final check) |

---

## Applying this narrative — the From→To scaffold & per-pipeline guide

*Added June 2026 from the Frontline 2026 narrative spine — the delivery mechanics that complement the substance above. Substance, numbers, and vocabulary remain governed by the earlier sections (esp. §2 pillars, §10 outcomes **with their caveats**, §17 language rules). This section only adds **how to open and apply** the story — do not restate the §10 figures without their caveats.*

### The From→To signature device (open every deliverable on it)

Open every narrative on the pain, resolve to the unified state — then map the client's *own* discovery findings onto the scaffold:

- **FROM — frontline fragmentation.** The client's specific version of the whitespace problem (§3): their handoffs, exceptions, manual coordination, systems-per-journey. Use *their* measured numbers where you have them; fall back to the §3 directional anchors only as conversation framing, never as fact.
- **TO — a Unified Frontline that runs the bank as one.** Customers, employees and AI agents on one shared truth and one execution engine, governed and auditable (§4–§5).
- **The value of crossing over** ties to the §10 outcome ranges — always carried with the §10 caveat, or replaced by the bank-specific business case.

The client's fragmentation becomes the FROM; the Banking OS becomes the TO. The scaffold is engagement-type-agnostic — cold pitch, workshop, assessment, or negotiation deck.

**The wedge (use to reframe "we're already doing AI"):** AI bolted onto a fragmented frontline amplifies the mess — faster and more expensive. The OS underneath comes first: shared truth, an execution engine, explicit authorization (Pillar 1, §4).

### How each Cortex pipeline applies the narrative

| Pipeline / agent | Apply the From→To narrative by… |
|---|---|
| Discovery / transcript interpreter | Cluster findings into the **FROM** picture — name the client's specific fragmentation, handoffs, exceptions |
| Ignite workshops (strategy / member / employee / architecture) | Use **FROM→To** as the workshop arc; Pillar 1's AI-amplifies-fragmentation stance as the AI-readiness framing |
| Capability / value assessment | Maturity = distance from a Unified Frontline; gaps = where the frontline isn't "running as one" (maps to §5 layers, §9 autonomy) |
| Journey builder | Current journeys as fragmented swimlanes (FROM) → unified, orchestrated future state (TO) |
| ROI / business case | Outcomes-first hero; tie levers to "one execution engine" efficiency and lifecycle ownership; size against the bank's measured data, not §10 directionals |
| Narrative assembler / frontline decks / executive briefing / long-form | Open on FROM→To, anchor on the AI-Native Banking OS, close on the mission line; dark/architecture visual language |
| Prototype | Show the Unified Frontline literally — one shared truth, web→mobile continuity, agents + audit trail |
| Deal-desk / negotiation | The Banking OS is *what they're buying*; price defends the OS, not a feature list (§13) |
