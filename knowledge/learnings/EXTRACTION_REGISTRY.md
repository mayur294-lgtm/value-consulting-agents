# Knowledge Extraction Registry

This registry tracks all knowledge extracted from past engagements into the agent system.

## Last Updated
2026-07-28

## Extraction Statistics

| Metric | Count |
|--------|-------|
| Engagements Scanned | 100+ |
| Engagements Extracted | 16 (1 synthetic — quarantined) |
| Benchmark Files | 3 |
| Journey Map Files | 0 |
| ROI Pattern Files | 8 (4 synthetic-origin, marked) |
| Pain Point Pattern Files | 0 |
| Capability Framework Files | 0 |
| Competitor Analysis Files | 0 |
| Engagement Pattern Files | 1 |

---

## Scanned Engagements

| Engagement | Region | Bank Type | Domain | Engagement Type | Scan Date | Status |
|------------|--------|-----------|--------|-----------------|-----------|--------|
| [Client-wealth-NAM-2023] | NAM | Wealth Manager | Wealth | Value Assessment | 2026-02-05 | Extracted |
| OneAZ Credit Union | NAM | Credit Union | Retail | Decommission | 2026-02-05 | Extracted |
| [Client-retail-LATAM-2025] | LATAM (Bolivia) | Retail Bank | Retail | Value Assessment | 2026-02-05 | Extracted |
| [Client-retail-AFRICA-2025] Kenya | Africa (East) | Multi-Country | Multi-Segment | Multi-Country | 2026-02-05 | Extracted |
| [Client-retail-LATAM-2021] | LATAM (Colombia) | Retail Bank | Lending | Value Assessment | 2026-02-05 | Extracted |
| Fifth Third Bank | NAM | Universal | Commercial | Full Engagement | 2026-02-05 | Awaiting Export |
| CRDB Tanzania | Africa (East) | Retail Bank | Retail | Value Assessment | 2026-02-05 | Partial Data |
| BEDC Cameroon | Africa (Central) | Retail Bank | Retail | Value Assessment | 2026-02-05 | Pending |
| Peoples Group | NAM | Regional | Retail | Value Assessment | 2026-02-05 | Pending |
| Fortis Bank | NAM | Regional | Retail | Value Assessment | 2026-02-05 | Pending |
| TD Bank Cards | NAM | Universal | Cards | Pre-Sales | 2026-02-05 | Extracted |
| [Client-creditunion-NAM-2022] | NAM | Credit Union | Retail | Full Engagement | 2026-02-05 | Extracted |
| CIMB Niaga | APAC (Indonesia) | Universal | Retail | Pre-Workshop | 2026-02-05 | Template Only |
| [Client-retail-NAM-2021] | NAM | Regional | Retail | Pre-Sales | 2026-02-05 | Template Only |
| [Client-retail-EMEA-2025] Bank | EMEA (Albania) | Retail Bank | Retail | Pre-Workshop | 2026-02-06 | Extracted |
| Peoples Group | NAM (Canada) | Digital Bank | Retail | Pre-Workshop | 2026-02-06 | Template Only |
| harborlight_synthetic / 2026-07_retail_assessment | NAM | Credit Union | Retail | Pipeline Test (Synthetic) | 2026-07-28 | Quarantined (2026-08-18) |

---

## Extracted Engagements

| Engagement | Region | Domain | Types Extracted | Extraction Date | Files Created |
|------------|--------|--------|-----------------|-----------------|---------------|
| [Client-wealth-NAM-2023] | NAM | Wealth | roi_logic, benchmark | 2026-02-05 | wealth_entitlements_roi.md |
| OneAZ Credit Union | NAM | CU/Retail | tech_rationalization, decommission, marketplace_costs | 2026-02-06 | tech_rationalization_decommission.md |
| [Client-retail-LATAM-2025] | LATAM | Retail | roi_logic, channel_costs | 2026-02-05 | latam_channel_costs.md |
| [Client-retail-AFRICA-2025] Kenya | Africa | Multi-Country | implementation, team_sizing | 2026-02-05 | multi-country-rollout.md |
| [Client-retail-LATAM-2021] | LATAM | Lending | roi_logic, lending_model | 2026-02-05 | digital_lending_roi.md |
| [Client-wealth-APAC-2025] | APAC | Wealth | full_assessment, journey, roi, persona | 2026-02-05 | Updated wealth/benchmarks.md, wealth/journey_maps.md |
| [Client-retail-ANZ-2025] | APAC | Retail | journey_assessment, business_case, process_flows | 2026-02-05 | Updated retail/benchmarks.md |
| BOK Financial | NAM | Commercial/Treasury | discovery_transcript, pain_points, security, integration | 2026-02-05 | Updated commercial/benchmarks.md |
| [Client-creditunion-NAM-2025] | NAM | Credit Union/Retail | client_questionnaire, business_case, digital_metrics, call_center | 2026-02-05 | Updated retail/benchmarks.md |
| [Client-retail-NAM-2025] | NAM | Regional/Consumer+Business | client_questionnaire, digital_metrics, pain_points, business_banking | 2026-02-05 | Updated retail/benchmarks.md |
| [Client-wealth-NAM-2024]/Scotiabank | NAM (Canada) | Wealth | roi_model, business_case, advisor_productivity | 2026-02-05 | Updated wealth/benchmarks.md |
| [Client-creditunion-NAM-2022] | NAM | Credit Union | transaction_costs, channel_economics, fee_income | 2026-02-05 | Updated retail/benchmarks.md |
| TD Bank Cards | NAM | Cards | credit_card_economics, revenue_per_account | 2026-02-05 | Updated retail/benchmarks.md |
| 2026-07_retail_assessment [SYNTHETIC — QUARANTINED 2026-08-18] | NAM | Retail/CU | roi_models (formula patterns only) | 2026-07-28 | KEPT (marked synthetic): roi_models/call_deflection_roi.md, card_controls_roi.md, dispute_management_roi.md, digital_onboarding_completion_roi.md — formulas reusable, all [Synthetic-Test] values fabricated. QUARANTINED to tests/engagements/harborlight_synthetic/2026-07_retail_assessment/outputs/knowledge_harvest/: retail benchmarks (+22 entries, reverted from retail/benchmarks.md), journey map, pain-point patterns, digital_lending NAM data points (reverted append) |

---

## Knowledge Inventory

### Benchmarks (Integrated into Domain Files)

| Domain | File Updated | Data Added | Source Engagement |
|--------|--------------|------------|-------------------|
| Wealth | `knowledge/domains/wealth/benchmarks.md` | Entitlements & Operational Efficiency, RM Admin Load, IT Support, Platform Consolidation | [Client-wealth-NAM-2023] (NAM) |
| Wealth | `knowledge/domains/wealth/benchmarks.md` | [Client-wealth-APAC-2025] ROI Value Levers (APAC) | [Client-wealth-APAC-2025] |
| Wealth | `knowledge/domains/wealth/benchmarks.md` | [Client-wealth-NAM-2024] Digital Wealth ROI Model (Canada) | [Client-wealth-NAM-2024]/Scotiabank |
| Retail | `knowledge/domains/retail/benchmarks.md` | LATAM Channel Costs, Transaction CAGR, Consumer Lending Economics | [Client-retail-LATAM-2025] (LATAM), [Client-retail-LATAM-2021] (LATAM) |
| Retail | `knowledge/domains/retail/benchmarks.md` | Australia/APAC Onboarding Benchmarks, Business Case Value | [Client-retail-ANZ-2025] |
| Retail | `knowledge/domains/retail/benchmarks.md` | NAM Credit Union Benchmarks ([Client-creditunion-NAM-2025], [Client-retail-NAM-2025]) | [Client-creditunion-NAM-2025], [Client-retail-NAM-2025] |
| Retail | `knowledge/domains/retail/benchmarks.md` | Credit Union Transaction Economics ([Client-creditunion-NAM-2022]) | [Client-creditunion-NAM-2022] |
| Retail | `knowledge/domains/retail/benchmarks.md` | Credit Card Economics (TD Bank) | TD Bank Cards |
| Retail | `knowledge/domains/retail/benchmarks.md` | EMEA Retail Benchmarks (Albania) - Digital adoption 7%, Churn 13.5% | [Client-retail-EMEA-2025] Bank |
| Retail | `knowledge/domains/retail/benchmarks.md` | Africa Retail Benchmarks (East Africa) - Multi-country rollout, RM efficiency | [Client-retail-AFRICA-2025] Kenya |
| Commercial | `knowledge/domains/commercial/benchmarks.md` | Commercial Onboarding Benchmarks, Value Levers | Seacoast Bank |
| Commercial | `knowledge/domains/commercial/benchmarks.md` | Treasury Discovery Pain Points, Integration Patterns | BOK Financial |

**Note:** Benchmarks are integrated directly into domain-specific files rather than stored separately. This ensures agents and users find relevant benchmarks in context.

### Journey Maps (`knowledge/learnings/journey_maps/`)

_No journey maps extracted yet._

### ROI Patterns (`knowledge/learnings/roi_models/`)

| File | Description | Source Region | Domain | Confidence |
|------|-------------|---------------|--------|------------|
| `wealth_entitlements_roi.md` | RM time savings, IT support reduction, platform consolidation, client retention | NAM | Wealth | HIGH |
| `latam_transaction_migration_roi.md` | Channel cost migration model, transaction volume analysis | LATAM | Retail | HIGH |
| `digital_lending_origination_roi.md` | Pre-approved lending uplift, portfolio buildup model, cross-sell | LATAM | Retail/Lending | HIGH |
| `tech_rationalization_decommission.md` | Platform consolidation, vendor contract reduction, per-user cost optimization, growth cost avoidance | NAM | Cross-Domain | HIGH |

### Capability Frameworks (`knowledge/learnings/capability_frameworks/`)

_No capability frameworks extracted yet._

### Competitor Analyses (`knowledge/learnings/competitor_analyses/`)

_No competitor analyses extracted yet._

### Engagement Patterns (`knowledge/learnings/engagement_patterns/`)

_No engagement patterns extracted yet._

### External Reports (`knowledge/learnings/external_reports/`)

_No external reports extracted yet._

### Proposals (`knowledge/learnings/proposals/`)

_No proposal patterns extracted yet._

---

## Auto-Harvest Log

> Entries below are written automatically by the Orchestrator's Step 9 at the end of every engagement. No human action required.

| Engagement ID | Domain | Region | Harvest Date | Entries Written (A:B:C:D) | Method |
|---------------|--------|--------|--------------|---------------------------|--------|
| *(auto-populated)* | | | | | auto |
| 2026-07_retail_assessment [SYNTHETIC] | retail | NAM | 2026-07-28 | A:22 B:8 C:0 D:5 — quarantined 2026-08-18 (only D formula patterns kept, marked [Synthetic-Test]) | auto |

**Legend:** A = Benchmarks, B = Pain Points, C = Capability Maturity, D = ROI Patterns

---

## Synthetic / Test Engagement Policy (2026-08-18)

Test engagements live in `tests/engagements/` (never `engagements/`) and carry a `.synthetic`
marker file. Harvest from a test run is **quarantined** to the engagement's own
`outputs/knowledge_harvest/` directory — it must never be written to `knowledge/domains/` or
`knowledge/learnings/`. Values already in shared knowledge tagged `[Synthetic-Test]` are
fabricated test data: reusable for formula/pattern structure, never citable as benchmarks.
See `tests/engagements/README.md` for the full convention. Enforcement in the harvester,
orchestrator, and retrieval skills is tracked in `.prd/backlog.md`.

---

## Pending Extractions

| Engagement | Pending Files | Reason | Action Required |
|------------|---------------|--------|-----------------|
| Fifth Third Bank | Build vs Buy.gsheet, Business Case.gsheet, APR Final.gsheet, Transcripts | Google-native files | Export to PDF/Excel |

---

## Extraction Queue

Priority order for future extractions:

1. **2025 Full Engagements** - Highest value, complete artifact sets
2. **Build vs Buy Analyses** - Reusable competitor frameworks
3. **ROI Models** - Value lever patterns and benchmarks
4. **External Reports** - Industry benchmarks from McKinsey, etc.
5. **Proposals** - Engagement structure patterns

---

## Notes

- All extracted knowledge is anonymized (client names → bank type/region)
- Google-native files (.gslides, .gsheet) require manual PDF export before extraction
- Follow `knowledge/standards/context_management_protocol.md` for large files
- Update this registry after every extraction run
