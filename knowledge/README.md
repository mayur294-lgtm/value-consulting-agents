# Knowledge Base

This directory contains the foundational consulting knowledge that powers the Value Consulting Agent System.

---

## ⭐ Canonical positioning narrative

**`banking_os.md`** is the **current canonical positioning narrative** (Banking OS v4.0 — June 2026). All new POVs, ROI models, capability assessments, and roadmaps Cortex generates should use this file as the source for Backbase positioning, language rules, the 4 solutions × 2 blocks framework, persona playbooks, and discovery questions.

**`conversational_banking.md`** is the deep-dive on that specific solution.

### Positioning convention

- **Top-level positioning file = canonical and current.** Cortex agents use it for new work.
- **`positioning_history/` = archive.** When a new positioning version supersedes the current one, the current file moves to `positioning_history/` with a version suffix, and the new version replaces it at the top level.
- **`backbase_platform_lexicon.md`** is the **product capability reference** — product lines, customer lifecycle stages, four quadrants, domain variations. It is stable and slow-changing. It complements (does not compete with) the positioning narrative.

See `positioning_history/README.md` for the full convention.

---

## Structure

### `/principles/`
Core consulting principles and philosophy that guide all analysis and recommendations.

**Contents:**
- Value consulting mindset
- Outcome-led vs. vendor-led thinking
- Evidence-based decision making
- Executive communication standards

### `/methodologies/`
Structured approaches for conducting consulting work.

**Contents:**
- Discovery and interview interpretation
- Capability assessment frameworks
- ROI and financial modeling approaches
- Roadmap construction methods
- Assumption handling procedures

### `/standards/`
Quality criteria and benchmarks for consulting outputs.

**Contents:**
- Output quality checklist
- ROI defensibility standards
- Assumption documentation requirements
- Executive summary best practices

### `/domains/`
Banking domain-specific knowledge organized by vertical.

**Verticals:** retail, commercial, sme, wealth, corporate

**Contents per domain:**
- benchmarks.md - KPIs and operational metrics
- journey_maps.md - Customer/client journeys
- pain_points.md - Common challenges
- use_cases.md - Backbase capabilities
- value_propositions.md - Solutions

### `/learnings/`
Extracted knowledge from past engagements (anonymized).

**Structure:**
- `roi_models/` - ROI calculation patterns and value levers
- `EXTRACTION_REGISTRY.md` - Index of all extracted knowledge

**Key ROI Pattern Files:**
| File | Use Case | Stakeholder Focus |
|------|----------|-------------------|
| `wealth_entitlements_roi.md` | RM productivity, platform consolidation | Business + CIO |
| `latam_transaction_migration_roi.md` | Channel cost migration | Business + CFO |
| `digital_lending_origination_roi.md` | Lending volume uplift | Business |
| `tech_rationalization_decommission.md` | Platform replacement, vendor consolidation | **CIO + CFO** |

**Stakeholder-Specific Guidance:**
- **Business Leaders (CDO, CMO, COO):** Focus on revenue, customer experience, operational efficiency
- **CIO/CTO:** Focus on tech rationalization, platform consolidation, integration simplification
- **CFO:** Focus on cost avoidance, decommissioning savings, total cost of ownership

## Purpose

This knowledge base serves as:
1. **Training material** for agents
2. **Reference documentation** for methodology
3. **Quality standards** for output validation
4. **Source of truth** for consulting best practices

All agents must reference and comply with knowledge in this directory.
