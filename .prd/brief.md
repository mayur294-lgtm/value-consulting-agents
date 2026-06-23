---
last_reviewed: 2026-06-22
---

# Cortex (Value Consulting AgenticOS) — Brief

## Vision
An agentic operating system that produces senior-grade, evidence-traceable value-consulting deliverables and gets smarter with every engagement.

## Problem
Value consulting is bottlenecked by scarce senior expertise: capability assessments, ROI models, and roadmaps are slow to produce, inconsistent between consultants, and start near-cold each time because nothing institutional accumulates. Quality depends on who happens to be staffed, and every executive deliverable must be defensible under scrutiny it rarely gets before it ships.

## Target users
Backbase value consultants — *architects* who build and evolve the system and *consultants* who run client engagements — producing executive-ready business cases for banks and credit unions.

## Value proposition
Senior-consultant-quality deliverables generated from real engagement evidence in hours instead of weeks, where every number traces to a source and a shared knowledge graph makes each engagement benefit from all the ones before it.

## Principles
- **Evidence over assertion** — every claim traces to a source (transcript quote, benchmark, client data); a guess is never presented as fact.
- **Conservative over optimistic** — ROI uses downside-aware, defensible math; optimism without a downside case is a defect, not a courtesy.
- **Auditable over fast** — every deliverable records its provenance, assumptions, and consultant checkpoints; an output that can't be audited is not done.
- **Outcome-led over vendor-led** — start from the business problem; technology is the means, never the headline.
- **Fail-closed on client data** — PII and anonymization abort rather than leak; we never trade a client's confidentiality for throughput.

## North-star metric
**Decision-ready engagements** — the share of engagements whose generated deliverables an executive can act on without senior rework. It is the one number that captures whether the system actually replaces senior effort rather than merely accelerating drafts.
Guardrails (must not regress while chasing it): evidence-traceability rate of quantified claims; conservative-bias of ROI models; zero un-anonymized PII reaching an external API.

## Quality goals
- **Reliability** — a full pipeline run completes and reports its outcome; no silent missing or corrupt outputs.
- **Traceability** — every quantified claim links to evidence or a benchmark.
- **Reproducibility** — a run can be resumed or re-run without losing prior good work.
- **Security** — client PII never reaches an external service un-anonymized.
- **Maintainability** — the agent and orchestration layer stays simple enough for a 3-architect team to evolve.

## Non-goals
- **Not a CRM** — Salesforce remains the source of truth for deal stage, won/lost, and contract value; Cortex references CRM IDs, it does not replace them.
- **Not a replacement for consultant judgment** — the system augments the consultant; it never automates the consultant away.
- **Not a general-purpose BI / dashboarding tool** — it produces consulting deliverables, not ad-hoc analytics.
- **Not a client-facing self-serve product** — it is an internal tool operated by consultants.

## Definition of Done
A unit of work is done when:
1. **Output complies with Value Consulting standards** — evidence-traced, assumptions explicit with confidence levels, conservative math, executive-ready (per `README.md`).
2. **Governance is satisfied** — journal entry + telemetry block + dual consultant checkpoints + output provenance recorded (per `knowledge/standards/auditability_protocol.md`).
3. **Code meets the coding standards** — passes `.claude/skills/coding-standards/checklists/before-committing.md` (types, pathlib, fail-closed security); new `tools/`/`scripts/` logic carries pytest coverage.
4. **A full run is trustworthy** — the pipeline produces every expected artifact for its mode, each validated, with a run report certifying the outcome.
5. **Change lands cleanly** — via a feature branch and PR within the contributor's role scope; never committed directly to `main`.
