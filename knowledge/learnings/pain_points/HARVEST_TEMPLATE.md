# Pain Point Harvest Entry

> Auto-harvested from evidence registers. Tracks recurring pain→impact patterns across engagements.

## Entry Format

```markdown
### [Pain Point Theme] — [Domain] / [Region]

- **Pattern:** [1-sentence description of the pain point]
- **Business Impact:** [How it hurts — revenue loss, cost increase, risk exposure, customer attrition]
- **Frequency:** [How many engagements have surfaced this — incremented on each harvest]
- **Severity Range:** [HIGH | MEDIUM | LOW] — [range across engagements]
- **Typical Evidence:** [What kind of evidence surfaces this — e.g., "Call center volume data", "Customer complaint logs"]
- **Last Seen:** [YYYY-MM-DD]
- **Engagement IDs:** [comma-separated UUIDs]
- **Notes:** [Qualifying context]
```

## Rules

1. **Match before creating** — before adding a new entry, check if an existing pain point matches (same theme + domain). If it does, increment frequency and add the engagement ID.
2. **Anonymize** — no client names, stakeholder names, or internal project names
3. **Only harvest** pain points with evidence IDs (E-IDs) from the evidence register
4. **Track frequency** — this is the key signal. A pain point seen once is anecdotal. Seen 5+ times across engagements, it's a pattern.
5. **Capture the impact chain** — pain → business consequence → measurable loss

## Aggregation Notes

High-frequency pain points (5+ engagements) become "known patterns" that:
- Get pre-loaded into Discovery Agent prompts as hypotheses to test
- Feed ROI model templates as likely value levers
- Inform capability assessment scoring rubrics
