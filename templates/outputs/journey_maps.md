# Journey Maps Output Template

This document defines the output format for the Journey Builder Agent. The agent produces two files: a structured JSON for HTML dashboard consumption and a human-readable markdown summary for the Assembly Agent.

## Output Files

| File | Format | Consumer | Purpose |
|------|--------|----------|---------|
| `journey_maps.json` | JSON | `/generate-assessment-html` skill | Interactive swimlane visualization, friction callouts, value waterfall, before/after toggle, **journey experience map** |
| `journey_maps_summary.md` | Markdown | Assembly Agent (Act 4) | Human-readable journey maps for the assessment report narrative |

---

## JSON Schema: `journey_maps.json`

```json
{
  "$schema": "journey-maps-v2",
  "metadata": {
    "engagement_id": "string — engagement identifier",
    "client_name": "string — client organization name",
    "domain": "retail | wealth | investing | sme | commercial | corporate",
    "region": "string — engagement region",
    "generated_date": "ISO-8601 date",
    "consultant_validated": "boolean — true after Checkpoint #2",
    "journeys_selected_by": "consultant | auto-recommended"
  },

  "journey_experience": {
    "transformation_arc": "string — 'From X to Y' transformation narrative (e.g., 'From Disconnected Investor to Connected Wealth Member')",
    "headline_insights": [
      {
        "severity": "red | amber | blue",
        "icon": "string — single emoji representing the insight",
        "stat": "string — short, punchy insight headline (e.g., '50% Never Fund')",
        "description": "string — 1-2 sentence elaboration"
      }
    ],
    "stages": [
      {
        "stage_id": "number — sequential (1, 2, 3...)",
        "name": "string — stage name (e.g., 'Account Opening')",
        "subtitle": "string — optional sub-label (e.g., '& Entry')",
        "evocative_title": "string — storytelling title (e.g., 'Funding — The Cliff Edge')",
        "evocative_subtitle": "string — what this stage means in plain language",
        "lifecycle_stage": "Acquire | Activate | Expand | Retain",
        "experience_score": "number — 1-10 member experience rating",
        "score_color": "string — hex color for the score display",
        "zone": "string — zone grouping (e.g., 'Digital Self-Service', 'Human Touch & Servicing')",
        "status": "mapped | pending — pending stages have dashed outlines",
        "narrative": "string — 3-5 sentence storytelling paragraph (NOT bullets). Use client language. Make the reader FEEL the experience.",
        "pain_points": [
          {
            "severity": "critical | high | medium",
            "title": "string — short, compelling name",
            "description": "string — 2-3 sentence explanation",
            "impact": "string — quantified impact statement (optional)",
            "evidence_ids": ["E-XX"],
            "pain_point_ids": ["PP-XXX-XX"]
          }
        ],
        "uf_gaps": [
          {
            "title": "string — unified frontline / transformation arc gap",
            "description": "string — how this stage fails the transformation vision",
            "impact": "string — what this gap costs",
            "capability_score": "string — e.g., 'Score: 0 (Absent)'"
          }
        ],
        "evidence_quote": {
          "text": "string — direct stakeholder quote",
          "attribution": "string — who said it and when"
        }
      }
    ],
    "svg_curve": {
      "description": "Coordinates for the emotion curve SVG. The skill generates the SVG from stage scores.",
      "zone_boundary_x": "number — X coordinate where zones split (e.g., 640 for a 1000-wide viewbox)",
      "zone_labels": ["string — zone label names"],
      "viewbox_width": 1000,
      "viewbox_height": 230
    }
  },

  "journeys": [
    {
      "journey_id": "J1 — sequential journey identifier",
      "name": "string — journey name (e.g., Account Opening)",
      "lifecycle_stage": "Acquire | Activate | Expand | Retain",
      "strategic_theme": "string — business objective (e.g., Reduce acquisition cost)",
      "linked_capabilities": ["CAP-XX-YY-ZZ — capability IDs from taxonomy"],
      "linked_problems": ["CN-XX, UN-XX — problem IDs from capability assessment"],

      "actors": [
        {
          "actor_id": "A1",
          "name": "string — actor name (e.g., Customer/Prospect)",
          "type": "customer | frontline | back_office | compliance | system"
        }
      ],

      "as_is": {
        "steps": [
          {
            "step_id": "S1 — sequential step identifier",
            "phase": "string — journey phase name",
            "actor_id": "A1 — which actor performs this step",
            "action": "string — what happens at this step",
            "active_time_minutes": "number — actual work time",
            "elapsed_time": "string — calendar time including waits (e.g., '2-3 days')",
            "systems": ["string — systems involved at this step"],
            "handoff_to": "string — actor_id receiving handoff (null if none)",
            "architectural_layer": "front | middle | back",
            "friction_points": [
              {
                "friction_id": "F1 — sequential friction identifier",
                "type": "customer | employee | system",
                "description": "string — what the friction is",
                "severity": "critical | high | moderate | minor",
                "evidence_ids": ["E1, E2 — from evidence register"],
                "pain_point_ids": ["PP-ACQ-01 — from pain point register"],
                "impact_category": "revenue | cost | risk | experience",
                "drop_off_percent": "number — percentage lost at this step",
                "volume_entering_step": "number — volume/count entering",
                "value_lost_per_unit": "number — dollar value per lost unit",
                "value_lost_total": "number — total annual value lost",
                "value_lost_currency": "string — USD, EUR, etc.",
                "value_lost_period": "annual",
                "data_source": "evidence | benchmark_proxy"
              }
            ]
          }
        ],
        "total_elapsed_time_days": "number",
        "total_active_employee_minutes": "number",
        "completion_rate_percent": "number",
        "total_handoffs": "number",
        "stp_rate_percent": "number",
        "value_leakage_total": "number — total annual value leaked",
        "value_leakage_currency": "string"
      },

      "friction_callouts": [
        {
          "rank": "number — 1 = highest impact",
          "friction_id": "F1 — matches friction_points above",
          "title": "string — short, compelling name",
          "description": "string — 2-3 sentence explanation",
          "evidence_quote": "string — direct stakeholder quote with attribution",
          "evidence_ids": ["E1, E2"],
          "dollar_impact": "number — annual dollar impact",
          "dollar_impact_currency": "string",
          "severity": "critical | high | moderate",
          "impact_category": "revenue | cost | risk | experience",
          "linked_capabilities": ["CAP-XX-YY-ZZ"],
          "proposed_fix": "string — specific Backbase solution description",
          "backbase_products": ["string — Backbase product names"]
        }
      ],

      "future_state": {
        "steps": [
          {
            "step_id": "FS1",
            "phase": "string — future journey phase",
            "actor_id": "A1",
            "action": "string — what happens in the new journey",
            "active_time_minutes": "number",
            "elapsed_time": "string",
            "systems": ["string — new systems involved"],
            "backbase_products": ["string — Backbase products enabling this step"],
            "backbase_layers": ["engagement | orchestration | intelligence | integration"],
            "improvements": "string — what changed vs. current state"
          }
        ],
        "total_elapsed_time_days": "number",
        "total_active_employee_minutes": "number",
        "completion_rate_percent": "number",
        "total_handoffs": "number",
        "stp_rate_percent": "number",
        "value_recovered": "number — annual value recovered",
        "value_recovered_currency": "string"
      },

      "summary_metrics": {
        "elapsed_time": { "current": "string", "target": "string", "improvement": "string" },
        "completion_rate": { "current": "string", "target": "string", "improvement": "string" },
        "employee_time": { "current": "string", "target": "string", "improvement": "string" },
        "stp_rate": { "current": "string", "target": "string", "improvement": "string" },
        "value_leakage": { "current": "string", "recovered": "string", "recovery_rate": "string" },
        "handoffs": { "current": "number", "target": "number", "improvement": "string" }
      }
    }
  ],

  "aggregate_summary": {
    "total_journeys_mapped": "number",
    "total_value_leakage": "number — sum of all journey leakage",
    "total_value_recoverable": "number — sum of all journey recovery",
    "recovery_rate_percent": "number",
    "currency": "string",
    "top_friction_points": [
      {
        "rank": "number",
        "journey": "string — journey name",
        "friction": "string — friction title",
        "impact": "number — dollar impact"
      }
    ]
  }
}
```

---

## Markdown Template: `journey_maps_summary.md`

The human-readable output follows this structure for each journey:

```markdown
# Journey Maps — [Client Name]

**Domain:** [domain] | **Region:** [region] | **Date:** [date]
**Consultant Validated:** Yes/No | **Journeys Selected By:** Consultant / Auto-recommended
**Transformation Arc:** "[From X to Y]"

---

## End-to-End Journey Experience

### Headline Insights

| # | Severity | Insight | Detail |
|---|----------|---------|--------|
| 1 | Critical | [Punchy stat] | [1-2 sentence explanation] |
| 2 | High | [Punchy stat] | [1-2 sentence explanation] |
| 3 | Strategic | [Punchy stat] | [1-2 sentence explanation] |

### Stage-by-Stage Experience

#### Stage [N]: [Evocative Title] — [Score]/10

**[Narrative — 3-5 storytelling sentences. NOT bullets. Make the reader feel the experience.]**

**Pain Points:**
- [Severity] **[Title]** — [Description]. [Impact if quantified]
- ...

**[Transformation Arc] Gaps:**
- **[Gap Title]** — [Description] (Capability Score: [X])

> "[Evidence quote]" — [Attribution]

---

[Repeat for each stage]

---

## J1: [Journey Name] — [Lifecycle Stage]

**Strategic Theme:** [What business objective this journey serves]
**Linked Capabilities:** [CAP-IDs]
**Total Value Leakage:** $X/year | **Recoverable:** $Y/year (Z%)

### Friction Callouts (Top 3-5)

> **#1: [Friction Title]** — $XXX,XXX/year
> "[Evidence quote]" — [Role]
> **Severity:** Critical | **Category:** Revenue
> **Fix:** [Backbase product] — [what it does]
> **Evidence:** E-XX, E-YY | **Capabilities:** CAP-XX-YY

> **#2: [Friction Title]** — $XXX,XXX/year
> ...

### As-Is Journey (Current State)

| Step | Phase | Actor | Action | Active Time | Elapsed Time | Systems | Friction | Value Lost |
|------|-------|-------|--------|-------------|-------------|---------|----------|------------|
| S1 | Research | Customer | Searches online | 15 min | 15-20 min | Website | F1: 30% drop-off | $900K |
| S2 | Apply | Customer | Fills application | 20 min | 20-30 min | Web Form | F2: Complex form | $450K |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Totals:** Elapsed: X days | Employee time: X min | Completion: X% | Handoffs: X | STP: X% | Leakage: $X

### Value Leakage Waterfall

```
Step 1: 10,000 prospects enter → 30% drop-off → 3,000 lost → $900,000 leaked
Step 2:  7,000 continue → 15% drop-off → 1,050 lost → $315,000 leaked
Step 3:  5,950 continue → 20% drop-off → 1,190 lost → $357,000 leaked
...
Cumulative leakage: $2,400,000/year
```

### Future-State Journey (Backbase-Enabled)

| Step | Phase | Actor | Action | Time | Systems | Backbase Products | Layers | Improvement |
|------|-------|-------|--------|------|---------|-------------------|--------|-------------|
| FS1 | Apply & Verify | Customer | Guided digital flow | 10 min | Digital Onboarding | Digital Onboarding, Platform Identity | Engagement, Integration | Replaces 3 manual steps |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Totals:** Elapsed: X min | Employee time: X min | Completion: X% | Handoffs: X | STP: X% | Recovered: $X

### Before / After Summary

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Elapsed time | 2-5 days | <15 min | 99%+ |
| Completion rate | 40% | 80% | +40pp |
| Employee time | 65 min/app | <5 min/app | 92% |
| STP rate | 0% | 70% | +70pp |
| Value leakage | $2.4M/yr | $720K/yr | $1.68M recovered (70%) |
| Handoffs | 8 | 2 | 75% fewer |

---

## J2: [Next Journey Name] — [Lifecycle Stage]
...

---

## Aggregate Summary

| Metric | Value |
|--------|-------|
| Journeys mapped | X |
| Total value leakage | $X/year |
| Total value recoverable | $X/year |
| Recovery rate | X% |

### Top Friction Points (All Journeys)

| Rank | Journey | Friction | Annual Impact |
|------|---------|----------|---------------|
| 1 | Account Opening | Document Upload Failure | $900,000 |
| 2 | ... | ... | ... |
```

---

## Validation Rules

1. **Internal consistency:** `aggregate_summary.total_value_leakage` = sum of all `journey.as_is.value_leakage_total`
2. **Recovery consistency:** `aggregate_summary.total_value_recoverable` = sum of all `journey.future_state.value_recovered`
3. **Evidence backing:** Every friction point has either evidence_ids or explicit "benchmark_proxy" data_source
4. **Product grounding:** Every future state step references specific Backbase products
5. **Minimum depth:** Each journey has at least 5 as-is steps and 3 friction callouts
6. **Consultant validation:** `metadata.consultant_validated` must be `true` before delivery
7. **Journey experience completeness:** `journey_experience` section must have at least 4 stages with experience scores, narratives, and pain points
8. **Journey experience insights:** `journey_experience.headline_insights` must have exactly 3 items (one red, one amber, one blue)
9. **Journey experience narratives:** Every stage narrative must be 3+ sentences in storytelling voice (NOT bullet points)
10. **Transformation arc:** `journey_experience.transformation_arc` must be defined and referenced in stage narratives

---

## Traceability

Journey map elements connect to other deliverables via trace IDs:

| Element | Trace ID Pattern | Links To |
|---------|-----------------|----------|
| Journey experience stages | `JX-{STAGE_NUM}` | Journey experience map in Act 4, SVG emotion curve |
| Friction points | `PP-{LIFECYCLE}-{NUM}` | Pain points in Act 1, Capability gaps in Act 5 |
| Capabilities | `CAP-{LIFECYCLE}-{LAYER}-{NUM}` | Heatmap cells in Act 5, Initiatives in Act 6 |
| Value recovered | `BEN-{NUM}` | ROI levers in Act 7 |
| Personas | `PERSONA-{ID}` | Persona cards in Act 4 |
