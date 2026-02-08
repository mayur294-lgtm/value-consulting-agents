# Knowledge Extraction Registry

This registry tracks all knowledge extracted from past engagements into the agent system.

## Last Updated
2026-02-06

## Extraction Statistics

| Metric | Count |
|--------|-------|
| Engagements Scanned | 100+ |
| Engagements Extracted | 15 |
| Benchmark Files | 3 |
| Journey Map Files | 0 |
| ROI Pattern Files | 4 |
| Capability Framework Files | 0 |
| Competitor Analysis Files | 0 |
| Engagement Pattern Files | 1 |

---

## Scanned Engagements

| Engagement | Region | Bank Type | Domain | Engagement Type | Scan Date | Status |
|------------|--------|-----------|--------|-----------------|-----------|--------|
| TriState Capital | NAM | Wealth Manager | Wealth | Value Assessment | 2026-02-05 | Extracted |
| OneAZ Credit Union | NAM | Credit Union | Retail | Decommission | 2026-02-05 | Extracted |
| Banesco | LATAM (Bolivia) | Retail Bank | Retail | Value Assessment | 2026-02-05 | Extracted |
| I&M Kenya | Africa (East) | Multi-Country | Multi-Segment | Multi-Country | 2026-02-05 | Extracted |
| Banco Caja Social | LATAM (Colombia) | Retail Bank | Lending | Value Assessment | 2026-02-05 | Extracted |
| Fifth Third Bank | NAM | Universal | Commercial | Full Engagement | 2026-02-05 | Awaiting Export |
| CRDB Tanzania | Africa (East) | Retail Bank | Retail | Value Assessment | 2026-02-05 | Partial Data |
| BEDC Cameroon | Africa (Central) | Retail Bank | Retail | Value Assessment | 2026-02-05 | Pending |
| Peoples Group | NAM | Regional | Retail | Value Assessment | 2026-02-05 | Pending |
| Fortis Bank | NAM | Regional | Retail | Value Assessment | 2026-02-05 | Pending |
| TD Bank Cards | NAM | Universal | Cards | Pre-Sales | 2026-02-05 | Extracted |
| UFCU | NAM | Credit Union | Retail | Full Engagement | 2026-02-05 | Extracted |
| CIMB Niaga | APAC (Indonesia) | Universal | Retail | Pre-Workshop | 2026-02-05 | Template Only |
| Sandy Spring | NAM | Regional | Retail | Pre-Sales | 2026-02-05 | Template Only |
| Credins Bank | EMEA (Albania) | Retail Bank | Retail | Pre-Workshop | 2026-02-06 | Extracted |
| Peoples Group | NAM (Canada) | Digital Bank | Retail | Pre-Workshop | 2026-02-06 | Template Only |

---

## Extracted Engagements

| Engagement | Region | Domain | Types Extracted | Extraction Date | Files Created |
|------------|--------|--------|-----------------|-----------------|---------------|
| TriState Capital | NAM | Wealth | roi_logic, benchmark | 2026-02-05 | wealth_entitlements_roi.md |
| OneAZ Credit Union | NAM | CU/Retail | tech_rationalization, decommission, marketplace_costs | 2026-02-06 | tech_rationalization_decommission.md |
| Banesco | LATAM | Retail | roi_logic, channel_costs | 2026-02-05 | latam_channel_costs.md |
| I&M Kenya | Africa | Multi-Country | implementation, team_sizing | 2026-02-05 | multi-country-rollout.md |
| Banco Caja Social | LATAM | Lending | roi_logic, lending_model | 2026-02-05 | digital_lending_roi.md |
| HNB Sri Lanka | APAC | Wealth | full_assessment, journey, roi, persona | 2026-02-05 | Updated wealth/benchmarks.md, wealth/journey_maps.md |
| MyState Australia | APAC | Retail | journey_assessment, business_case, process_flows | 2026-02-05 | Updated retail/benchmarks.md |
| BOK Financial | NAM | Commercial/Treasury | discovery_transcript, pain_points, security, integration | 2026-02-05 | Updated commercial/benchmarks.md |
| BECU | NAM | Credit Union/Retail | client_questionnaire, business_case, digital_metrics, call_center | 2026-02-05 | Updated retail/benchmarks.md |
| WSFS Bank | NAM | Regional/Consumer+Business | client_questionnaire, digital_metrics, pain_points, business_banking | 2026-02-05 | Updated retail/benchmarks.md |
| Tangerine/Scotiabank | NAM (Canada) | Wealth | roi_model, business_case, advisor_productivity | 2026-02-05 | Updated wealth/benchmarks.md |
| UFCU | NAM | Credit Union | transaction_costs, channel_economics, fee_income | 2026-02-05 | Updated retail/benchmarks.md |
| TD Bank Cards | NAM | Cards | credit_card_economics, revenue_per_account | 2026-02-05 | Updated retail/benchmarks.md |

---

## Knowledge Inventory

### Benchmarks (Integrated into Domain Files)

| Domain | File Updated | Data Added | Source Engagement |
|--------|--------------|------------|-------------------|
| Wealth | `knowledge/domains/wealth/benchmarks.md` | Entitlements & Operational Efficiency, RM Admin Load, IT Support, Platform Consolidation | TriState Capital (NAM) |
| Wealth | `knowledge/domains/wealth/benchmarks.md` | HNB Sri Lanka ROI Value Levers (APAC) | HNB Wealth Management |
| Wealth | `knowledge/domains/wealth/benchmarks.md` | Tangerine Digital Wealth ROI Model (Canada) | Tangerine/Scotiabank |
| Retail | `knowledge/domains/retail/benchmarks.md` | LATAM Channel Costs, Transaction CAGR, Consumer Lending Economics | Banesco (LATAM), Banco Caja Social (LATAM) |
| Retail | `knowledge/domains/retail/benchmarks.md` | Australia/APAC Onboarding Benchmarks, Business Case Value | MyState Australia |
| Retail | `knowledge/domains/retail/benchmarks.md` | NAM Credit Union Benchmarks (BECU, WSFS) | BECU, WSFS Bank |
| Retail | `knowledge/domains/retail/benchmarks.md` | Credit Union Transaction Economics (UFCU) | UFCU |
| Retail | `knowledge/domains/retail/benchmarks.md` | Credit Card Economics (TD Bank) | TD Bank Cards |
| Retail | `knowledge/domains/retail/benchmarks.md` | EMEA Retail Benchmarks (Albania) - Digital adoption 7%, Churn 13.5% | Credins Bank |
| Retail | `knowledge/domains/retail/benchmarks.md` | Africa Retail Benchmarks (East Africa) - Multi-country rollout, RM efficiency | I&M Kenya |
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

**Legend:** A = Benchmarks, B = Pain Points, C = Capability Maturity, D = ROI Patterns

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
