# Engagement Intake

> Fill this out when starting a new engagement. The orchestrator reads this to classify and route the engagement.

## Client Reference

- **Client Short Name:** [e.g., `navy_federal` — must match directory name under `engagements/`]
- **Client Profile:** `engagements/[client_short_name]/CLIENT_PROFILE.md`
- **Is New Client?** [Yes | No — if Yes, CLIENT_PROFILE.md will be created by init_engagement.sh]
- **Prior Engagements:** [List any prior engagement dirs, e.g., `2026-01_investing_assessment`]

## Domain Adapter

- **Domain:** [retail | sme | commercial | corporate | wealth | investing]
- **Engagement Type:** [assessment | ignite | hybrid | ROI_only | deal_strategy]
- **Primary Journeys:** [e.g., onboarding, servicing, lending, investing]
- **Domain Pack to Load:** `/knowledge/domains/[domain]/*`

## Benchmark Configuration

- **Benchmark Confidence Mode:** [LOW | MEDIUM | HIGH]
- **Region:** [e.g., north_america, emea, asia_pacific, latam]
- **Benchmark Registry:** `/benchmarks/benchmark_registry.md`

## Client Context

- **Client Name:** [Full name]
- **Industry:** [e.g., Retail Banking, Credit Union, Neobank]
- **Geography:** [Country/region]
- **Engagement Date:** [YYYY-MM-DD]

## Engagement Scope

### Objectives
- [Objective 1]
- [Objective 2]

### Initiative Context
> If this bank has multiple concurrent initiatives, describe how this engagement fits.
- **Initiative Name:** [e.g., "Digital Investor Platform", "Retail Onboarding Transformation"]
- **Relationship to Other Initiatives:** [e.g., "Builds on findings from the Jan 2026 Investing Assessment"]
- **Shared vs. Independent:** [Does this initiative share infrastructure/teams with others?]

### Primary Journeys in Scope
1. **[Journey Name]** — [Brief description]
2. **[Journey Name]** — [Brief description]

### Out of Scope
- [What is explicitly excluded]

## Stakeholders Interviewed

| Name/Role | Department | Perspective |
|-----------|------------|-------------|
| [Name — Title] | [Department] | [Strategic/Business/Operations/Technology] |

## Available Inputs

- [ ] Discovery transcripts
- [ ] Client financial data (Excel)
- [ ] System documentation
- [ ] Market benchmarks
- [ ] Prior engagement outputs (from this client)
- [ ] Annual report / public financials

## Data Gaps (Known)

- [Gap 1 — e.g., "No onboarding volume metrics available"]
- [Gap 2]

## Constraints

- **Budget:** [Specified / Not specified]
- **Timeline:** [e.g., "Board presentation in 6 weeks"]
- **Regulatory:** [Applicable regulations]
- **Resources:** [Team capacity constraints]

## Success Criteria

- [Criterion 1]
- [Criterion 2]

## Cross-Engagement Leverage

> For returning clients only. What should this engagement build on from prior work?

- **Reuse from prior engagements:**
  - [e.g., "Tech landscape from 2026-01 assessment is still current — don't re-discover"]
  - [e.g., "Pain point P3 (manual onboarding) was validated — use as anchor for ROI"]
- **Contradictions to watch for:**
  - [e.g., "Prior assessment said digital adoption was 40% — client now claims 60%, verify"]
- **New ground to cover:**
  - [e.g., "Wealth management was out of scope last time — now it's the primary focus"]
