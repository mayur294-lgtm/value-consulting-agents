# Engagement Scan: Fifth Third Bank

## Metadata
- **Region:** NAM (United States)
- **Bank Type:** Universal Bank (Top 20 US)
- **Engagement Type:** Full Engagement
- **Year:** 2025
- **Domain:** Commercial Banking (Onboarding focus)
- **Scan Date:** 2026-02-05

---

## Content Inventory

### Root Level Files

| File | Type | Priority | Extraction Type | Sensitivity | Notes |
|------|------|----------|-----------------|-------------|-------|
| `5 3 Build vs Buy Commercial Onboarding.gsheet` | Competitor Analysis | **HIGH** | competitor, roi_logic | ANONYMIZE | Build vs buy comparison framework |
| `5 3 Commercial & Wealth Consulting Engagement Jun25.gslides` | Engagement Plan | MEDIUM | pattern | SAFE | Engagement structure template |
| `5 3 Commercial onboarding analysis 8Aug25.gslides` | Analysis | **HIGH** | journey, capability | ANONYMIZE | Onboarding analysis findings |
| `5 3 Commercial onboarding workshop - Onsite Jul 28-29.gslides` | Workshop | MEDIUM | pattern | SAFE | Workshop template |
| `5 3 Engagement Plan.gsheet` | Engagement Plan | LOW | pattern | SAFE | Planning template |
| `Fifth Third Bank - Engagement Plan Jun25 V2-V4.gslides` | Engagement Plan | LOW | pattern | SAFE | Version iterations |
| `Meetings and Notes.gdoc` | Discovery | MEDIUM | journey | REDACT | Meeting notes |
| `Shobhit 5 3 rough.gslides` | Working Draft | LOW | - | - | Skip - working draft |
| `CLO Pricing China Bank.gsheet` | Unrelated | LOW | - | - | Skip - different client |

### BUILD VS BUY Subfolder

| File | Type | Priority | Extraction Type | Sensitivity | Notes |
|------|------|----------|-----------------|-------------|-------|
| `Fifth Third Build Vs Buy.gslides` | Competitor Analysis | **HIGH** | competitor | ANONYMIZE | Build vs buy presentation |

### Output Subfolder

| File | Type | Priority | Extraction Type | Sensitivity | Notes |
|------|------|----------|-----------------|-------------|-------|
| `5 3 Business Case Model.gsheet` | ROI Model | **HIGH** | roi_logic, benchmark | ANONYMIZE | Value levers and calculations |
| `5 3 APR Final.gsheet` | Assessment | **HIGH** | capability, benchmark | ANONYMIZE | Final assessment results |
| `5 3 APR Analysis.gsheet` | Analysis | MEDIUM | capability | ANONYMIZE | Supporting analysis |
| `V1 Fifth Third Commercial Onboarding Executive ReadOut.gslides` | Final Report | **HIGH** | pattern, journey | ANONYMIZE | Executive deliverable template |
| `anonymized shareable version.gslides` | Final Report | **HIGH** | pattern | SAFE | Already anonymized - ready for extraction |
| `Fifth Third Agent Library.gslides` | Capability | MEDIUM | capability | ANONYMIZE | Agent/capability mapping |
| `Copy of Luminor_ Vendor_ Comparison.gslides` | Competitor | MEDIUM | competitor | SAFE | Cross-reference from other engagement |
| APR/ subfolder | Assessment | MEDIUM | capability | ANONYMIZE | Assessment artifacts |

### Onsite Transcript Subfolder

| File | Type | Priority | Extraction Type | Sensitivity | Notes |
|------|------|----------|-----------------|-------------|-------|
| `5 3 Onsite Day 1 APR Functional Mapping Transcript.gdoc` | Transcript | **HIGH** | journey, capability | REDACT | Functional requirements |
| `5 3 Onsite Day 2 APR Technical Transcript.gdoc` | Transcript | **HIGH** | capability, benchmark | REDACT | Technical architecture |
| `5 3 Onsite Day 2 Commercial Onboarding Transcript.gdoc` | Transcript | **HIGH** | journey, benchmark | REDACT | Onboarding process deep-dive |
| `Aug 8, 2025 | 5 3 - Backbase Onboarding Executive Summary review.gdoc` | Transcript | MEDIUM | pattern | REDACT | Exec review notes |

### Other Subfolders

| Folder | Type | Priority | Notes |
|--------|------|----------|-------|
| `Customer Documents/` | Client Materials | LOW | Client-provided; extraction unlikely |
| `Questionnaires/` | Discovery | MEDIUM | Pre-engagement questionnaire patterns |
| `Workshop Pack/` | Workshop | MEDIUM | Workshop structure templates |
| `onboarding artefacts/` | Reference | MEDIUM | Onboarding process artifacts |
| `Project Obsidian Comerica/` | Cross-reference | LOW | Different engagement reference |

---

## Extractable Knowledge Summary

### HIGH Priority (Extract First)

1. **Build vs Buy Framework**
   - Files: `5 3 Build vs Buy Commercial Onboarding.gsheet`, `Fifth Third Build Vs Buy.gslides`
   - Extraction: Competitor comparison matrix, decision criteria, cost comparison structure
   - Output: `competitor_analyses/build_vs_buy_commercial_onboarding.md`

2. **ROI Model / Business Case**
   - Files: `5 3 Business Case Model.gsheet`
   - Extraction: Value levers, calculation methodology, assumption framework
   - Output: `roi_models/commercial_onboarding_value_levers.md`

3. **Commercial Onboarding Journey**
   - Files: Onsite transcripts, `5 3 Commercial onboarding analysis 8Aug25.gslides`
   - Extraction: Pain points, touchpoints, process friction, improvement opportunities
   - Output: `journey_maps/commercial_onboarding_journey_nam.md`

4. **Capability Assessment Framework**
   - Files: `5 3 APR Final.gsheet`, transcripts
   - Extraction: Assessment criteria, maturity indicators, gap patterns
   - Output: `capability_frameworks/commercial_onboarding_capabilities.md`

5. **Executive Report Template**
   - Files: `V1 Fifth Third Commercial Onboarding Executive ReadOut.gslides`, `anonymized shareable version.gslides`
   - Extraction: Report structure, narrative flow, visualization patterns
   - Output: `engagement_patterns/commercial_onboarding_exec_report.md`

### MEDIUM Priority

6. **Workshop Structure**
   - Files: `Workshop Pack/`, workshop slides
   - Extraction: Workshop agenda, exercise templates, facilitation guides

7. **Questionnaire Templates**
   - Files: `Questionnaires/`
   - Extraction: Pre-engagement discovery questions

8. **Agent/Capability Library**
   - Files: `Fifth Third Agent Library.gslides`
   - Extraction: Agent role mapping methodology

---

## File Format Challenges

| Format | Count | Action Required |
|--------|-------|-----------------|
| .gslides | 14 | Requires manual PDF export |
| .gsheet | 9 | Requires manual Excel export |
| .gdoc | 5 | Requires manual PDF/text export |

**Note:** Google-native files cannot be read directly. User must export to PDF/Excel before extraction.

---

## Recommended Extraction Order

1. **`anonymized shareable version.gslides`** - Already anonymized, export to PDF first
2. **`5 3 Build vs Buy Commercial Onboarding.gsheet`** - Export to Excel, extract framework
3. **`5 3 Business Case Model.gsheet`** - Export to Excel, extract ROI logic
4. **`5 3 APR Final.gsheet`** - Export to Excel, extract capability framework
5. **Onsite transcripts** - Export to PDF/text, extract journey patterns

---

## Warnings

- Cross-engagement content found: `Project Obsidian Comerica/` folder and `CLO Pricing China Bank.gsheet` - skip these
- Multiple version iterations of engagement plans - only extract final versions
- Some files may contain client-specific pricing - ensure thorough anonymization

---

## Next Steps

1. Export the following files to PDF/Excel and place in the engagement folder:
   - `anonymized shareable version.gslides` → `.pdf`
   - `5 3 Build vs Buy Commercial Onboarding.gsheet` → `.xlsx`
   - `5 3 Business Case Model.gsheet` → `.xlsx`
   - `5 3 APR Final.gsheet` → `.xlsx`
   - Onsite transcripts → `.pdf` or `.txt`

2. Run: `/extract-learnings 2025/38. Fifth Third --priority HIGH`

3. Review extracted learnings for accuracy and completeness
