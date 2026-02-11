# Domain Context Loader

Load the complete domain knowledge for a specific banking vertical to inform your analysis, recommendations, and deliverables.

## Usage
`/domain-context [domain]`

Where `[domain]` is one of:
- `retail` - Retail Banking
- `commercial` - Commercial Banking
- `sme` - SME/Business Banking
- `wealth` - Wealth Management
- `investing` - Retail Investing (self-directed, robo-advisory, bank-led investing)
- `corporate` - Corporate/Transaction Banking

## Instructions

When this skill is invoked:

1. **Identify the domain** from the argument provided (default to asking if not specified)

2. **Load all domain files** from `knowledge/domains/[domain]/`:
   - `_index.md` - Domain overview
   - `benchmarks.md` - Industry KPIs and metrics
   - `journey_maps.md` - Customer journeys
   - `process_maps.md` - Bank operational processes
   - `personas.md` - Key user personas
   - `use_cases.md` - Backbase capabilities
   - `pain_points.md` - Common challenges
   - `value_propositions.md` - Backbase solutions

3. **Summarize the domain context** for the user, highlighting:
   - Key themes and focus areas
   - Available benchmarks
   - Number of journeys, use cases, personas defined
   - Any gaps in the knowledge base (TO BE POPULATED sections)

4. **Keep context active** for subsequent analysis work

## Example

```
User: /domain-context retail
Assistant: Loading Retail Banking domain context...

[Reads all retail domain files]

Retail Banking domain loaded. Key context:
- Focus: Digital-first banking, personalization, self-service
- Benchmarks: Digital adoption, operational efficiency, CX metrics
- Journeys: 7 customer journeys mapped
- Personas: 5 customer + 4 employee personas
- Use Cases: 40+ Backbase capabilities mapped
- Pain Points: Onboarding, payments, service categories

Ready to use this context for discovery analysis, capability assessment, or deliverable creation.
```

## Notes
- This skill is foundational - use it at the start of any domain-specific engagement
- Multiple domains can be loaded for universal banks (e.g., retail + wealth)
- Context informs all subsequent agent work (discovery, capability, roadmap, ROI)
