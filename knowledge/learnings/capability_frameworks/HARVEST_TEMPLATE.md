# Capability Maturity Harvest Entry

> Auto-harvested from capability assessments. Tracks maturity patterns across engagements by domain and region.

## Entry Format

```markdown
### [Capability Name] — [Domain] / [Region]

- **Maturity Score:** [1-5]
- **Key Gaps:** [Top 2-3 gaps identified]
- **Evidence Basis:** [Which evidence IDs supported the score]
- **Size Tier:** [Tier 1 (>$10B) | Tier 2 ($1-10B) | Tier 3 (<$1B)]
- **Context:** [Client-{domain}-{region}-{YYYY}]
- **Harvest Date:** [YYYY-MM-DD]
- **Engagement ID:** [UUID]
```

## Rules

1. **Append-only** — never overwrite existing scores
2. **Anonymize** — use `[Client-{domain}-{region}-{YYYY}]`
3. **Only harvest** scores backed by evidence IDs
4. **Group by capability** — all scores for "Digital Onboarding" go under one heading, across engagements
5. **Track the distribution** — over time, this builds a picture of "where most banks score" for each capability

## Aggregation Notes

When 5+ entries exist for the same capability in the same domain:
- Calculate the median maturity score
- Identify the most common gaps
- This becomes the "industry baseline" for that capability
- Feeds the Capability Assessment Agent's scoring rubrics
- Helps consultants say: "Most retail banks in EMEA score 2.3/5 on digital onboarding"
