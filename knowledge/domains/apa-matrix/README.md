# APA Domain Matrix — Agentic Process Automation Catalog

> **A reusable module for prescribing AI / agentic use cases across any banking opportunity.**
> Local carbon copy of Shobhit's APA Simulation Catalog so engagements tap a source we own — not the Netlify build.

**Source:** Reproduced from Shobhit's *APA Simulation Catalog* (`apadomainmatrixtoolkit.netlify.app`), Backbase internal collateral, v1.1 (29 Mar 2026). Credit to Shobhit for the framework and simulations.
**Reproduced:** 8 Jun 2026, for Shyam, as a local knowledge module.
**Files:** `apa_simulations.json` (machine-readable backbone — 65 processes, full 6-layer detail) · `apa_domain_matrix_toolkit.html` (self-contained interactive copy) · this guide.

---

## When to use this (standing instruction)

**Any time a task involves identifying, prescribing, prioritising, or sizing AI / agentic use cases for a bank — tap this module first.** It is the default lens for: agentic strategy notes, POC scoping, use-case portfolios, opportunity shaping, ROI hypothesis on automation, and "where can AI help?" conversations. Flex it to the opportunity at hand (Retail / SME / Commercial / Wealth — or a blend).

Workflow:
1. **Identify the LOB(s)** in play (e.g. a building society = Retail + SME).
2. **Read the L1 matrix** (below) → which domains carry the highest automation potential for those LOBs.
3. **Pull the processes** in those HIGH cells from `apa_simulations.json` → these are your candidate use cases.
4. **Apply the per-process method** (Value Bleed → Banking OS Simulation → Elastic Ops Business Case) to prove desirability → feasibility → viability.
5. **Re-base every $/% figure on the client's data** before anything client-facing. The toolkit's numbers are illustrative reference values.

---

## The framework

**Thesis — Elastic Operations:** scale operations *without* linear headcount growth; elastic capacity delivered through **humans + agents + workflows**. Three pillars: **Growth** (acquire · retain · expand) · **Efficiency** (higher throughput · lower cost-to-serve) · **Control** (authority · policy · proof).

**The 6-layer Banking OS** (each process simulation walks these top-to-bottom):

| Layer | Role | Product reality |
|---|---|---|
| **Interaction** | Unified Frontline — composable workspaces, branch, mobile, contact centre | Unified Frontline |
| **Orchestration** | The agents that plan & execute multi-step tasks | Agent Studio + Agent Orchestration |
| **Intelligence** | ML — intent, propensity, outcome prediction, risk scoring | Intelligence Fabric |
| **Sentinel** | Authority Layer — decides what each actor (customer/employee/AI agent) may do; every action checked against bank policy before it executes; immutable audit | **Sentinel** (official Backbase product name) |
| **Semantic (NEXUS)** | Customer State Graph — one real-time customer view + Banking Ontology | NEXUS |
| **Connectivity** | Integration to systems of record | Grand Central (iPaaS) |

> **Sentinel, NEXUS and the Intelligence Fabric are official Backbase product names** — the layers of the AI-Native Banking OS (launched at Backbase ENGAGE, 22 Apr 2026). Use them as-is with any audience, including architects; they are the vendor's own framing.

**The three agentic tiers** — don't call everything "agentic":
- **Assisted (copilot):** AI drafts, human decides.
- **Automated (workflow/STP):** deterministic, rules-based. No reasoning (Flow).
- **Agentic (autonomous):** agent reasons over NEXUS, plans & executes across systems inside Sentinel guardrails; human at the risk gate only. *Spend the word only where autonomy earns its keep — high-volume, context-heavy, judgment-light work.*

**Per-process method — the desirability/viability engine:**

| Artefact | Proves | What it is |
|---|---|---|
| **Value Bleed Analysis** | Desirability | Quantified $ bleed per process step + narrative — the pain, sized |
| **Banking OS Process Simulation** | Feasibility | 6-layer walk-through of the agentic future state |
| **Elastic Operations Business Case** | Viability | Growth Restored · Efficiency Gained · Control Enforced, with recovery math |

---

## Coverage

- **4 Lines of Business:** Retail · SME · Commercial · Wealth & Private
- **4 super-domains / 9 core domains:** Customer Operations (Onboarding, Account Servicing) · Payments & Disputes Ops (Payments & Cash Mgmt, Disputes & Chargebacks) · Lending Operations (Loan Origination, Credit Risk & Decisioning) · Risk & Fraud Operations (KYC & Due Diligence, Financial Crime & Fraud, Regulatory & Compliance)
- **65 process simulations**, each with the full 6-layer agentic walk-through in `apa_simulations.json`.

### L1 Automation-Potential Matrix

Automation potential per LOB × core domain. **HIGH** = strong agentic fit · **MED** = partial · **LOW** = mostly automated / low-leverage.

| LOB | Onboarding | Acct Servicing | Payments & Cash | Disputes | Loan Origination | Credit Risk | KYC & DD | Fin Crime & Fraud | Reg & Compliance |
|---|---|---|---|---|---|---|---|---|---|
| **Retail** | MED | **HIGH** | LOW | **HIGH** | **HIGH** | MED | MED | **HIGH** | MED |
| **SME** | **HIGH** | MED | MED | **HIGH** | **HIGH** | **HIGH** | **HIGH** | MED | MED |
| **Commercial** | **HIGH** | MED | **HIGH** | MED | **HIGH** | **HIGH** | **HIGH** | **HIGH** | **HIGH** |
| **Wealth & Private** | **HIGH** | MED | MED | LOW | MED | MED | **HIGH** | **HIGH** | **HIGH** |

**How to read it for an opportunity:** take the client's LOB row(s), pick the HIGH cells, then pull those processes from the JSON as your priority use-case shortlist. Example — a building society (Retail + SME) → HIGH cells = Account Servicing, Disputes, Loan Origination, Financial Crime (Retail) + Onboarding, Disputes, Loan Origination, Credit Risk, KYC (SME).

---

## Using the data

`apa_simulations.json` structure:
```
meta            — source, attribution, reproduction note
framework       — thesis, pillars, 6 layers, per-process method, agentic tiers
lines_of_business
operational_domains  — super-domain → [domains]
l1_automation_matrix — LOB → [HIGH/MED/LOW per column]
processes{slug} — title, lob, super_domain, domain, steps[]
   steps[]      — each step: name, timeline, customer, agent/agentDesc,
                  intel/intelDesc, sentinel/sentinelDesc, nexus/nexusAttrs, metric
```
Each `steps[]` entry is one stage of the agentic process, mapped to the 6 layers (`customer`=Interaction, `agent`=Orchestration, `intel`=Intelligence, `sentinel`=Sentinel, `nexus`=Semantic). This is the raw material for a tailored Banking OS simulation per engagement.

For visual / interactive browsing (Value Bleed slides, UI prototypes, animated business case), open `apa_domain_matrix_toolkit.html` locally.

---

## Maintenance

This is a point-in-time copy of v1.1. If Shobhit ships updates, re-pull and diff — don't silently overwrite. To formalise as an auto-triggered skill/hook (so it fires on every AI-use-case task without relying on memory), an Architect (Mayur / Shobhit / Mariam) needs to add it under `.claude/` — flagged for a future PR.
