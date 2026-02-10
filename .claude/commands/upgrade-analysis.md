# Upgrade Analysis

Analyze a client's packaging migration opportunity and produce VC deliverables for the migration team.

## Usage

```
/upgrade-analysis [account name or context]
```

## What This Skill Does

Produces the Value Consultant's contribution to a packaging migration engagement:

1. **Outside-In POV** — Market context, peer positioning, strategic opportunity (ALWAYS)
2. **Tier Value Articulation** — Why the target tier is the right fit (for upgrade plays)
3. **ROI Napkin** — Back-of-napkin financial perspective (for upgrade plays)
4. **Peer Comparison** — What comparable institutions are doing (for proactive/upsell)
5. **Objection Prep** — Anticipated pushback and responses (for all active plays)

## Required Context

Before running, ensure you have:
- Account name, industry, region, ARR
- Current products (with packaging status — legacy vs new tier)
- Current capabilities in production
- Contract renewal timeline
- Open opportunities (if any)
- Infrastructure (BaaS vs On-Premise)

This data can come from:
- The Migration Co-Pilot application (structured JSON)
- Salesforce MCP queries (direct)
- Consultant-provided briefing

## Instructions

1. **Gather account context** — Load the account data from whatever source is available
2. **Determine effective tier** — Based on current products and capabilities, what tier does the account map to?
3. **Identify the play** — Upsell? Renewal? Cloud+Packaging? Proactive? Re-map? Exception?
4. **Load domain knowledge** — Read `knowledge/domains/<relevant-domain>/*` for industry context
5. **Load Product Directory** — Read `knowledge/domains/Product Directory (1).csv` for tier feature mapping
6. **Load competitor intel** — Read `knowledge/competitor_intelligence.md` for peer positioning
7. **Invoke the upgrade-analysis agent** with the assembled context
8. **Review outputs** — Ensure all deliverables are marked "AI Draft — Needs Review"

## Output

All deliverables are written as markdown, clearly labeled as AI drafts requiring VC review. The VC enhances, validates, and approves before use.

## Integration with Migration Co-Pilot

When called from the Migration Co-Pilot application, this skill acts as the bridge:
- Migration Co-Pilot sends account context + tier mapping + play recommendation
- This skill routes to the upgrade-analysis agent
- Agent produces deliverables per the play-specific output matrix
- Deliverables returned to Migration Co-Pilot for the VC's review tab

## Example

```
/upgrade-analysis Dons Bank - legacy packaging, Premium-equivalent, upsell opportunity for Family Banking
```
