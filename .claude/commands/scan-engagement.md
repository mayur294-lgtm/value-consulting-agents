# Scan Engagement Folder

Analyze and classify the contents of a past engagement folder to identify extractable knowledge.

## Usage

```
/scan-engagement /path/to/engagement/folder
```

Or provide a partial path like:
```
/scan-engagement 2025/05. Comerica
```

## Base Path

All engagement folders are located under:
```
/Users/mayur@backbase.com/Library/CloudStorage/GoogleDrive-mayur@backbase.com/Shared drives/Customer Advisory/Team Value Consulting/Team Value Consulting /03 - Engagements/
```

## Classification Process

### Step 1: Inventory the Folder

List all files and subfolders. For each item, classify by type:

| File Pattern | Classification |
|--------------|----------------|
| `*BCase*.gsheet`, `*Business Case*.gsheet`, `*ROI*.gsheet` | Business Case / ROI Model |
| `*Assessment*.gslides`, `*Assessment*.gsheet` | Capability Assessment |
| `*Journey*.gslides`, `*Journey*.gsheet`, `*Process*.gslides` | Journey Map |
| `*Final Report*.gslides`, `*Exec Deck*.gslides` | Executive Deliverable |
| `*Engagement Plan*.gslides`, `*Engagement Plan*.gsheet` | Engagement Plan |
| `*Proposal*.gslides`, `*Proposal*.pdf` | Proposal |
| `*Workshop*.gslides`, `*Onsite*.gslides` | Workshop Materials |
| `*Transcript*.gdoc`, `Transcript/`, `Call Reports/` | Discovery Transcripts |
| `*Build vs Buy*.gsheet`, `*Competitor*.gslides` | Competitor Analysis |
| `*McKinsey*`, `*Bain*`, `*BCG*`, `*Deloitte*`, `*Accenture*` | External Consultant Report |
| `*Questionnaire*.gsheet`, `*Survey*.gsheet` | Discovery Inputs |
| `Customer Documents/`, `Received Data/`, `*Data/` | Client-Provided Materials |

### Step 2: Assess Engagement Depth

Based on contents, classify the engagement type:

| Type | Indicators |
|------|------------|
| **Full Engagement** | Has transcripts + assessment + business case + final report |
| **Lite Engagement** | Has business case + exec deck, minimal discovery |
| **Proposal Only** | Has proposal/engagement plan but no delivery artifacts |
| **Competitor Pitch** | Contains competitor analysis, build vs buy |
| **External Report** | Contains third-party consultant deliverables |

### Step 3: Identify Extractable Knowledge

For each file/folder, assess:

1. **Extraction Priority**
   - HIGH: Contains benchmarks, journey maps, ROI logic, capability frameworks
   - MEDIUM: Contains useful patterns, templates, client-specific insights
   - LOW: Administrative, duplicates, or low-value content

2. **Extraction Type**
   - `benchmark`: Numerical data points (costs, times, rates)
   - `journey`: Process flows, pain points, touchpoints
   - `roi_logic`: Value levers, calculation methods, assumptions
   - `capability`: Maturity frameworks, assessment criteria
   - `pattern`: Reusable engagement patterns, templates
   - `competitor`: Competitor positioning, build vs buy arguments

3. **Client Sensitivity**
   - REDACT: Contains client-specific financials, names, contracts
   - ANONYMIZE: Can be generalized with bank type/region
   - SAFE: Generic patterns, public benchmarks

### Step 4: Generate Inventory Report

Output format:

```markdown
# Engagement Scan: [Client Name]

## Metadata
- **Region:** [EMEA/APAC/LATAM/NAM]
- **Bank Type:** [Retail/Commercial/Wealth/Universal]
- **Engagement Type:** [Full/Lite/Proposal/Competitor/External]
- **Year:** [2024/2025/2026]
- **Domain:** [Retail/SME/Corporate/Wealth/Investing]

## Content Inventory

| File/Folder | Type | Priority | Extraction Type | Sensitivity | Notes |
|-------------|------|----------|-----------------|-------------|-------|
| ... | ... | ... | ... | ... | ... |

## Extractable Knowledge Summary

### HIGH Priority
- [List of high-value items with what can be extracted]

### MEDIUM Priority
- [List of medium-value items]

### Recommended Extraction Order
1. [First item to extract]
2. [Second item to extract]
...

## Warnings
- [Any issues: missing files, incomplete engagement, etc.]

## Next Steps
Run `/extract-learnings [engagement_path]` to extract knowledge from this engagement.
```

## Output Location

Save the scan report to:
```
knowledge/learnings/scans/[client_name]_scan.md
```

Create the `scans/` folder if it doesn't exist.

## Example

```
/scan-engagement 2025/38. Fifth Third Engagement Plan Version 2
```

Output:
```markdown
# Engagement Scan: Fifth Third Bank

## Metadata
- **Region:** NAM
- **Bank Type:** Universal
- **Engagement Type:** Full Engagement
- **Year:** 2025
- **Domain:** Commercial

## Content Inventory

| File/Folder | Type | Priority | Extraction Type | Sensitivity | Notes |
|-------------|------|----------|-----------------|-------------|-------|
| 5 3 Build vs Buy Commercial Onboarding.gsheet | Competitor Analysis | HIGH | competitor, roi_logic | ANONYMIZE | Build vs buy framework |
| Onsite Transcript/ | Discovery | HIGH | journey, benchmark | REDACT | Workshop transcripts |
| Output/ | Deliverables | HIGH | capability, pattern | ANONYMIZE | Final outputs |
| Workshop Pack/ | Workshop Materials | MEDIUM | pattern | SAFE | Workshop templates |
| Customer Documents/ | Client Materials | LOW | benchmark | REDACT | Client-provided data |

## Extractable Knowledge Summary

### HIGH Priority
- Build vs Buy analysis framework (from Build vs Buy folder)
- Commercial onboarding journey patterns (from Onsite Transcript)
- Final assessment templates (from Output folder)

### Recommended Extraction Order
1. Build vs Buy analysis - extract comparison framework
2. Commercial onboarding journey - extract pain points and touchpoints
3. Output folder - extract assessment patterns
```

## Notes

- This command ONLY scans and classifies - it does not extract content
- Google-native files (.gslides, .gsheet, .gdoc) cannot be read directly - they require export
- For PDFs, follow the extraction protocol in `knowledge/standards/context_management_protocol.md`
- Run `/extract-learnings` after scanning to pull actual knowledge
