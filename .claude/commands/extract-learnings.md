# Extract Learnings from Engagement

Extract structured knowledge from a scanned engagement folder into the knowledge base.

## Usage

```
/extract-learnings /path/to/engagement/folder [--type TYPE] [--priority HIGH|MEDIUM|ALL]
```

Or with partial path:
```
/extract-learnings 2025/38. Fifth Third --type roi_logic --priority HIGH
```

## Prerequisites

1. **Run `/scan-engagement` first** to classify folder contents
2. **Check the scan report** at `knowledge/learnings/scans/[client_name]_scan.md`

## Extraction Types

| Type | Target Files | Output Location | What Gets Extracted |
|------|--------------|-----------------|---------------------|
| `benchmark` | Business cases, ROI models | `knowledge/learnings/benchmarks/` | Numerical data points, metrics, baselines |
| `journey` | Journey maps, transcripts | `knowledge/learnings/journey_maps/` | Pain points, touchpoints, process flows |
| `roi_logic` | Business cases, ROI sheets | `knowledge/learnings/roi_models/` | Value levers, calculation methods |
| `capability` | Assessments, frameworks | `knowledge/learnings/capability_frameworks/` | Maturity criteria, scoring rubrics |
| `pattern` | Final reports, templates | `knowledge/learnings/engagement_patterns/` | Report structures, best practices |
| `competitor` | Build vs Buy, competitor docs | `knowledge/learnings/competitor_analyses/` | Positioning, comparison frameworks |
| `proposal` | Proposals, engagement plans | `knowledge/learnings/proposals/` | Engagement structures, pricing patterns |
| `external` | McKinsey/BCG/etc. reports | `knowledge/learnings/external_reports/` | Industry benchmarks, frameworks |

## Extraction Process

### Step 1: Identify Extractable Files

Based on the scan report, identify files matching the requested type and priority.

**CRITICAL: Google-native file handling**

Google files (.gslides, .gsheet, .gdoc) cannot be read directly by Claude. For these files:

1. **Ask the user to export** the specific file to PDF or Excel:
   ```
   Please export the following file to PDF and place it in the engagement folder:
   - [filename].gslides → [filename].pdf
   ```

2. **If user cannot export**, skip with note:
   ```
   SKIPPED: [filename].gslides - requires manual export to PDF
   ```

3. **For .xlsx files** that exist, these CAN be read - use Python pandas or similar.

### Step 2: Extract and Anonymize

For each extractable file:

1. **Read the content** (following context management protocol for large files)

2. **Anonymize sensitive data:**
   - Replace client names with `[BANK_NAME]` or bank type: `[US Regional Bank]`, `[APAC Universal Bank]`
   - Replace specific financials with ranges: `$50M revenue` → `[$40-60M revenue range]`
   - Remove contract terms, pricing, specific dates
   - Keep patterns, structures, logic

3. **Extract structured knowledge:**

   **For Benchmarks:**
   ```markdown
   ## Benchmark: [Metric Name]

   - **Value:** [X]
   - **Context:** [Bank type, region, domain]
   - **Source:** [Engagement name - anonymized]
   - **Year:** [2024/2025]
   - **Confidence:** [HIGH/MEDIUM/LOW]
   - **Notes:** [Any caveats or context]
   ```

   **For Journey Patterns:**
   ```markdown
   ## Journey: [Journey Name]

   ### Context
   - **Bank Type:** [Type]
   - **Region:** [Region]
   - **Domain:** [Retail/SME/Corporate/Wealth/Investing]

   ### Pain Points Identified
   1. [Pain point with evidence]
   2. [Pain point with evidence]

   ### Key Touchpoints
   1. [Touchpoint] → [Friction identified]

   ### Improvement Opportunities
   - [Opportunity]
   ```

   **For ROI Logic:**
   ```markdown
   ## ROI Pattern: [Pattern Name]

   ### Value Lever
   - **Lever:** [Name]
   - **Mechanism:** [How value is created]
   - **Typical Range:** [X-Y%]

   ### Calculation Approach
   [Formula or logic]

   ### Assumptions Required
   - [Assumption 1]
   - [Assumption 2]

   ### Sensitivity
   - Key driver: [What most affects the outcome]
   ```

   **For Capability Patterns:**
   ```markdown
   ## Capability: [Capability Name]

   ### Assessment Criteria
   | Level | Description | Indicators |
   |-------|-------------|------------|
   | 1 | ... | ... |
   | 5 | ... | ... |

   ### Common Gaps Found
   - [Gap pattern]

   ### Typical Improvement Path
   1. [Step 1]
   2. [Step 2]
   ```

   **For Competitor Patterns:**
   ```markdown
   ## Competitor Analysis: [Competitor or "Build vs Buy"]

   ### Comparison Framework
   | Dimension | Backbase | Alternative |
   |-----------|----------|-------------|
   | ... | ... | ... |

   ### Key Differentiators
   - [Differentiator]

   ### Common Objections & Responses
   - Objection: [X]
   - Response: [Y]
   ```

### Step 3: Write to Knowledge Base

1. **Create file** in appropriate `knowledge/learnings/[type]/` folder
2. **Name format:** `[domain]_[pattern_name]_[source_region].md`
   - Example: `commercial_onboarding_journey_nam.md`
   - Example: `build_vs_buy_framework_generic.md`

3. **Update registry** at `knowledge/learnings/EXTRACTION_REGISTRY.md`

### Step 4: Generate Extraction Report

Output format:

```markdown
# Extraction Report: [Client Name]

## Summary
- **Files Processed:** [N]
- **Learnings Extracted:** [N]
- **Files Skipped:** [N]

## Extracted Learnings

| Learning | Type | File Created | Source File |
|----------|------|--------------|-------------|
| Commercial onboarding journey | journey | commercial_onboarding_nam.md | Transcripts/ |
| Build vs Buy framework | competitor | build_vs_buy_generic.md | Build vs Buy.gsheet |

## Skipped Files
| File | Reason |
|------|--------|
| [filename].gslides | Requires manual PDF export |

## Next Steps
- Export pending Google files to PDF
- Review extracted learnings for accuracy
- Run `/scan-engagement` on next folder
```

## Extraction Registry

Maintain a registry at `knowledge/learnings/EXTRACTION_REGISTRY.md`:

```markdown
# Extraction Registry

## Last Updated: [Date]

## Extracted Engagements

| Engagement | Region | Domain | Types Extracted | Date |
|------------|--------|--------|-----------------|------|
| Fifth Third | NAM | Commercial | journey, competitor | 2025-02-05 |
| I&M Kenya | Africa | Retail | roi_logic, journey | 2025-02-05 |

## Knowledge Inventory

### Benchmarks
- [List of benchmark files with brief descriptions]

### Journey Maps
- [List of journey files]

### ROI Patterns
- [List of ROI pattern files]

### Capability Frameworks
- [List of capability files]

### Competitor Analyses
- [List of competitor files]

### External Reports
- [List of external report extractions]

## Pending Extractions
- [Engagement] - awaiting PDF export of [file]
```

## Quality Standards

1. **No raw client data** - Everything must be anonymized
2. **Preserve patterns, not specifics** - Extract the reusable logic
3. **Source attribution** - Always note where learning came from (anonymized)
4. **Confidence levels** - Mark how reliable the data point is
5. **Context preservation** - Include bank type, region, domain for relevance filtering

## Example Usage

```
/extract-learnings 2025/38. Fifth Third --type competitor --priority HIGH
```

This would:
1. Look for Build vs Buy analysis and competitor comparison files
2. Extract the comparison framework and key differentiators
3. Anonymize as "US Universal Bank"
4. Write to `knowledge/learnings/competitor_analyses/build_vs_buy_commercial_onboarding.md`
5. Update the extraction registry

## Notes

- Large files must follow `knowledge/standards/context_management_protocol.md`
- PDFs must be extracted to text first (see Rule 9 in context management)
- Google-native files require manual export - cannot be read directly
- Always verify extracted patterns with the original consultant if possible
