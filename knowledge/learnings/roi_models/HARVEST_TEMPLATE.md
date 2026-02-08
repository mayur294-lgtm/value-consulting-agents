# ROI Pattern Harvest Entry

> Auto-harvested from ROI reports. Tracks value lever patterns, payback periods, and benefit ranges across engagements.

## Entry Format

```markdown
### [Value Lever Name] — [Domain] / [Region]

- **Lever Type:** [Revenue Uplift | Cost Reduction | Risk Mitigation | Efficiency Gain]
- **Benefit Range:** [$X – $Y per year] or [X% – Y% improvement]
- **Payback Period:** [months]
- **Key Assumptions:** [Top 2-3 assumptions driving this lever]
- **Scenario:** [Conservative | Base | Aspirational] — [which scenario produced these numbers]
- **Size Tier:** [Tier 1 | Tier 2 | Tier 3]
- **Context:** [Client-{domain}-{region}-{YYYY}]
- **Harvest Date:** [YYYY-MM-DD]
- **Engagement ID:** [UUID]
- **Notes:** [Any qualifying context]
```

## Rules

1. **Append-only** — never overwrite existing patterns
2. **Anonymize** — use `[Client-{domain}-{region}-{YYYY}]`
3. **Only harvest** levers that passed the ROI model's sensitivity test
4. **Capture all three scenarios** when available (conservative/base/aspirational)
5. **Track assumptions** — the assumptions matter as much as the numbers
6. **Normalize to annual values** — convert all benefits to per-year for comparability

## Aggregation Notes

When 3+ entries exist for the same lever type in the same domain:
- Calculate the benefit range across engagements
- Identify common assumptions
- This becomes a "typical value lever" template for new engagements
- Helps consultants set realistic expectations: "Digital onboarding typically saves $X-$Y/year for Tier 2 retail banks"
