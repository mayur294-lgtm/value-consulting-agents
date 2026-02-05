# Capability Assessment Agent

> **DEPRECATED:** This file is superseded by `.claude/agents/capability-assessment.md` which contains the authoritative agent definition with the current 0-4 maturity scale, BIAN-aligned capability taxonomy, and Front/Middle/Back layer assessment methodology.
>
> **Authoritative references:**
> - Agent definition: `.claude/agents/capability-assessment.md`
> - Capability taxonomy: `knowledge/standards/capability_taxonomy.md`
> - Output template: `templates/outputs/capability_assessment.md`

## Quick Reference

### Maturity Scale (0-4)

| Level | Label | Description |
|-------|-------|-------------|
| 0 | Absent | Capability doesn't exist |
| 1 | Fragmented | Exists but ad-hoc, person-dependent |
| 2 | Defined | Standardized process, clear roles, repeatable |
| 3 | Orchestrated | End-to-end automated, measured, integrated |
| 4 | Intelligent | AI-native, predictive, self-optimizing |

### Layer Assessment

Each capability is scored across three layers:
- **Front Layer** (Experience Plane): What the customer/employee sees
- **Middle Layer** (Capability Plane): What orchestrates and decides
- **Back Layer** (Integration Plane): What connects, stores, and processes

**Overall score = weakest layer.**

### Domain Prefixes

| Domain | Prefix |
|--------|--------|
| Retail | CAP-R-* |
| Wealth | CAP-W-* |
| SME | CAP-S-* |
| Commercial | CAP-C-* |
| Corporate | CAP-CO-* |

See `.claude/agents/capability-assessment.md` for the full methodology.
