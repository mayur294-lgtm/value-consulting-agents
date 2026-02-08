# Benchmark Harvest Entry

> Auto-harvested from engagement outputs. Append-only — never overwrite existing entries.

## Entry Format

```markdown
### [Metric Name] — [Domain] / [Region]

- **Value:** [number with unit]
- **Context:** [Client-{domain}-{region}-{YYYY}], [size tier]
- **Source:** [Which output file and evidence ID, e.g., roi_report.md → E3]
- **Confidence:** [HIGH | MEDIUM | LOW]
- **Harvest Date:** [YYYY-MM-DD]
- **Engagement ID:** [UUID from .engagement_session_id]
- **Notes:** [Any qualifying context — e.g., "Post-digital transformation", "Pre-migration baseline"]
```

## Rules

1. **Never overwrite** existing entries — always append below
2. **Anonymize** client names: use `[Client-{domain}-{region}-{YYYY}]`
3. **Only harvest** metrics with evidence references (E-IDs)
4. **Skip** metrics with "Low" confidence assumptions from the ROI model
5. **Include context** — a bare number without context is useless
6. **Check for duplicates** — if the same engagement ID already has an entry, skip

## Aggregation Notes

When 3+ entries for the same metric exist in the same region:
- Calculate the range (min–max)
- Note the median
- This becomes a "field-observed range" that supplements published benchmarks
- See `agents/dev-agent.md` → Benchmark Evolution Rules for how the Dev Agent handles these
