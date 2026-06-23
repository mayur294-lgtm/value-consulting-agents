# FROZEN Backbase platform capability snapshot (judge guardrail) — 2026-06-24

What a use case must be achievable WITH. Snapshot of `knowledge/backbase_platform_lexicon.md`
+ `knowledge/banking_os.md` + `knowledge/domains/product_directory_*.md`. Bump deliberately
when the platform docs change. A use case is achievable if it is delivered **OOTB** by a
product line OR **buildable** on a named platform layer — not if it requires capability the
platform doesn't have.

## OOTB product lines (Unified Banking Suite — four quadrants)
- **Onboarding & Origination** — Digital Onboarding (guided application, doc upload/OCR, eIDV,
  AML, decision engine, eSignature), Digital Lending (loan origination, credit decisioning).
- **Digital Banking** — daily banking: accounts, payments, transfers, cash management, self-service.
- **Engagement & Expansion** — Digital Engage (campaigns, next-best-action, offers, life-event triggers).
- **Human Assist** — Digital Assist (RM/advisor workspace: leads, pipeline, case mgmt).
- **Grand Central** — connectors to cores, CRMs, KYC/AML/credit-bureau vendors, registries.
- **Platform Identity** — biometrics, FIDO2/passkeys, device registration.
(Per-domain specifics: product_directory_{retail,sme,commercial,wealth,investing}.md)

## Buildable platform layers (6-layer Banking OS Runtime + Sentinel)
- **Flow Foundation** — low-code: Journey Orchestrator, Form Builder, Business Rules Engine
  → configure new journeys / forms / rules.
- **Orchestration** — Process Studio (workflows) + Agent Studio (AI agents/missions) +
  Banking Capabilities (reusable microservices) → build new workflows, agents, services.
- **Nexus (Semantic/truth layer)** — Banking Ontology + shared customer truth, decision trail
  → build use cases needing a shared, queryable customer/decision view.
- **Intelligence layer** — Model Registry, banking-optimized models/SLMs → AI/ML use cases.
- **Sentinel (Authority)** — identity, policies, approvals, Decision Tokens → governs/authorizes
  agentic actions (required to take AI from pilot to production).

## How to judge achievability
- ✅ achievable: maps to an OOTB product line, OR a clear build on a named layer
  (e.g. "stalled-application nudge" = Flow Foundation rule + Digital Engage campaign;
  "advisor lead routing" = Digital Assist + Orchestration; "fraud-pattern hold" =
  Intelligence model + Sentinel authority).
- ❌ NOT achievable: requires core-banking replacement, a capability outside these layers,
  or hand-waves "AI will do it" with no layer it would actually run on.
- Generative is GOOD: a use case the client never mentioned is fine — even expected — as
  long as it is platform-achievable. Do NOT penalise use cases for being net-new.
