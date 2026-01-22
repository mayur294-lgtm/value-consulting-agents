# Discovery Output Schema

This document defines the structured output format from Discovery activities. This schema ensures downstream agents (Capability, ROI, Roadmap, Assembly) can consume discovery data consistently.

## Output Format: JSON

All discovery outputs MUST be exported in JSON format for machine consumption, with an optional markdown summary for human review.

---

## Schema Definition

```json
{
  "$schema": "discovery-output-v1",
  "metadata": {
    "engagement_id": "string",
    "engagement_type": "ignite_light | detailed_assessment",
    "sub_engagement": "string (optional)",
    "client_name": "string",
    "industry": "string",
    "region": "string",
    "discovery_date": "ISO-8601 date",
    "discovery_method": "workshop | transcript | hybrid",
    "consultant": "string",
    "version": "1.0"
  },
  "strategic_context": { ... },
  "hypothesis_tree": { ... },
  "evidence_register": [ ... ],
  "pain_point_register": [ ... ],
  "metric_register": [ ... ],
  "stakeholder_map": [ ... ],
  "capability_snapshot": { ... },
  "data_gaps": [ ... ],
  "use_cases": [ ... ],
  "constraints": { ... },
  "next_steps": [ ... ]
}
```

---

## Section Definitions

### 1. Metadata

```json
{
  "metadata": {
    "engagement_id": "ENG-2024-001",
    "engagement_type": "ignite_light",
    "sub_engagement": "customer_experience_workshop",
    "client_name": "Acme Bank",
    "industry": "retail_banking",
    "region": "SEA",
    "discovery_date": "2024-01-15",
    "discovery_method": "workshop",
    "consultant": "Value Consultant Name",
    "version": "1.0",
    "sessions_completed": [
      "strategic_alignment",
      "customer_experience",
      "employee_experience"
    ]
  }
}
```

**Engagement Types:**
- `ignite_light`: Strategic 1.5 day workshop (4 hours client time) - focus on vision, use cases, roadmap
- `detailed_assessment`: 3+ day deep dive with full capability assessment, business case, architecture

**Discovery Methods:**
- `workshop`: Live interactive session using Discovery Toolkit
- `transcript`: Post-call analysis of meeting transcripts/notes
- `hybrid`: Combination of workshops and transcript analysis

---

### 2. Strategic Context

```json
{
  "strategic_context": {
    "vision_statement": "string - client's stated 2-3 year vision",
    "strategic_themes": [
      {
        "theme_id": "ST01",
        "name": "Digital-First Customer Experience",
        "description": "Transform customer interactions to be primarily digital",
        "priority": "high | medium | low",
        "timeframe": "12-24 months",
        "kpis": ["NPS improvement", "Digital adoption rate"],
        "evidence_ids": ["E01", "E02"]
      }
    ],
    "cascading_choices": {
      "winning_aspiration": "string - what does winning look like",
      "where_to_play": {
        "segments": ["Mass Retail", "Affluent", "SME"],
        "products": ["Deposits", "Lending", "Payments"],
        "channels": ["Mobile", "Branch", "Call Center"]
      },
      "how_to_win": {
        "value_propositions": ["Seamless onboarding", "Personalized advice"],
        "differentiators": ["Speed", "Convenience", "Trust"]
      },
      "capabilities_needed": ["Digital onboarding", "Real-time decisioning"],
      "management_systems": ["Agile delivery", "Data governance"]
    },
    "competitive_context": {
      "primary_competitors": ["Neo Bank X", "Traditional Bank Y"],
      "competitive_pressures": ["Customer expectations", "Margin pressure"],
      "market_position": "Challenger | Incumbent | Leader"
    }
  }
}
```

---

### 3. Hypothesis Tree

The hypothesis tree captures strategic assumptions developed BEFORE and DURING discovery. This is critical for executive alignment and drives the discovery conversation.

```json
{
  "hypothesis_tree": {
    "root_hypothesis": "string - primary assumption about client's transformation need",
    "branches": [
      {
        "hypothesis_id": "H01",
        "category": "strategic | operational | technical | financial",
        "statement": "string - hypothesis statement",
        "confidence_before": "low | medium | high",
        "confidence_after": "low | medium | high",
        "status": "validated | invalidated | needs_validation | partially_validated",
        "supporting_evidence": ["E01", "E02"],
        "contradicting_evidence": ["E05"],
        "implications_if_true": "string",
        "implications_if_false": "string",
        "validation_approach": "string - how to test this hypothesis"
      }
    ],
    "validated_hypotheses": ["H01", "H03"],
    "invalidated_hypotheses": ["H02"],
    "pending_validation": ["H04", "H05"]
  }
}
```

**Example Hypothesis Tree:**

```json
{
  "hypothesis_tree": {
    "root_hypothesis": "The bank's digital transformation is stalled due to fragmented customer journeys and legacy integration complexity",
    "branches": [
      {
        "hypothesis_id": "H01",
        "category": "strategic",
        "statement": "Growth is constrained by inability to acquire customers digitally at scale",
        "confidence_before": "medium",
        "confidence_after": "high",
        "status": "validated",
        "supporting_evidence": ["E01", "E02", "E03"],
        "contradicting_evidence": [],
        "implications_if_true": "Digital onboarding must be priority #1",
        "implications_if_false": "Focus on servicing and retention instead"
      },
      {
        "hypothesis_id": "H02",
        "category": "operational",
        "statement": "Call center volumes are driven primarily by onboarding issues",
        "confidence_before": "high",
        "confidence_after": "low",
        "status": "invalidated",
        "supporting_evidence": [],
        "contradicting_evidence": ["E07"],
        "implications_if_true": "Fix onboarding to reduce call volume",
        "implications_if_false": "Investigate servicing and dispute resolution"
      },
      {
        "hypothesis_id": "H03",
        "category": "technical",
        "statement": "Core banking integration is the primary blocker for digital initiatives",
        "confidence_before": "medium",
        "confidence_after": "medium",
        "status": "needs_validation",
        "supporting_evidence": ["E10"],
        "contradicting_evidence": ["E11"],
        "implications_if_true": "Need integration layer / strangler pattern",
        "implications_if_false": "Can proceed with current integration approach",
        "validation_approach": "IT Architecture workshop deep dive"
      }
    ]
  }
}
```

---

### 4. Evidence Register

All claims must be traceable to evidence.

```json
{
  "evidence_register": [
    {
      "evidence_id": "E01",
      "type": "quote | metric | observation | document | benchmark",
      "source": {
        "type": "stakeholder | document | system | benchmark",
        "name": "Head of Digital Banking",
        "role": "Executive Sponsor",
        "session": "strategic_alignment"
      },
      "content": "string - the actual evidence",
      "context": "string - surrounding context",
      "timestamp": "ISO-8601",
      "confidence": "high | medium | low",
      "tags": ["onboarding", "customer_experience", "digital"],
      "linked_pain_points": ["PP01", "PP02"],
      "linked_hypotheses": ["H01"],
      "business_impact": "string - why this matters",
      "follow_up_needed": true | false
    }
  ]
}
```

---

### 5. Pain Point Register

```json
{
  "pain_point_register": [
    {
      "pain_point_id": "PP01",
      "title": "High abandonment in digital onboarding",
      "description": "65% of customers who start digital account opening abandon before completion",
      "category": "customer_experience | operational_efficiency | revenue | risk | technology",
      "severity": "critical | high | medium | low",
      "affected_journeys": ["customer_onboarding", "account_opening"],
      "affected_stakeholders": ["Retail Customers", "Branch Staff", "Digital Team"],
      "current_workaround": "Branch redirect for completion",
      "quantified_impact": {
        "metric": "Abandonment Rate",
        "current_value": "65%",
        "target_value": "20%",
        "financial_impact": "$2.4M annual revenue leakage",
        "calculation": "1000 applications/month × 65% abandonment × $300 CLV = $195K/month",
        "confidence": "medium"
      },
      "root_causes": [
        "Complex KYC requirements",
        "Manual document upload failures",
        "No save and resume capability"
      ],
      "evidence_ids": ["E01", "E02", "E03"],
      "priority_score": 85,
      "linked_use_cases": ["UC01", "UC02"]
    }
  ]
}
```

---

### 6. Metric Register

```json
{
  "metric_register": [
    {
      "metric_id": "M01",
      "name": "Digital Onboarding Completion Rate",
      "category": "customer | operational | financial | risk",
      "current_value": "35%",
      "target_value": "80%",
      "benchmark_value": "72% (industry median)",
      "benchmark_source": "Forrester Digital Banking Report 2024",
      "unit": "percentage",
      "direction": "higher_is_better | lower_is_better",
      "measurement_frequency": "monthly",
      "data_source": "Core banking system",
      "owner": "Head of Digital",
      "evidence_ids": ["E04"],
      "confidence": "high | medium | low",
      "notes": "string"
    }
  ]
}
```

---

### 7. Stakeholder Map

```json
{
  "stakeholder_map": [
    {
      "stakeholder_id": "SH01",
      "name": "Jane Smith",
      "role": "Head of Digital Banking",
      "department": "Digital Transformation",
      "influence": "high | medium | low",
      "decision_authority": "budget_owner | decision_maker | influencer | end_user",
      "priorities": ["Digital acquisition", "Cost reduction", "Customer NPS"],
      "concerns": ["Budget constraints", "Timeline pressure", "Resource availability"],
      "success_criteria": "Achieve 50% digital account origination in 18 months",
      "sentiment": "champion | supportive | neutral | skeptical | blocker",
      "interviewed": true | false,
      "session_participated": ["strategic_alignment", "customer_experience"],
      "quotes": ["E01", "E05"]
    }
  ]
}
```

---

### 8. Capability Snapshot

High-level capability assessment from discovery (feeds into Capability Agent for detailed scoring).

```json
{
  "capability_snapshot": {
    "domains": [
      {
        "domain_name": "Customer Onboarding",
        "current_maturity_estimate": "1-5 scale",
        "key_gaps": ["Digital KYC", "Document verification", "Real-time decisioning"],
        "strengths": ["Strong branch network", "Trusted brand"],
        "evidence_ids": ["E10", "E11"]
      }
    ],
    "technology_landscape": {
      "core_systems": [
        {
          "name": "T24",
          "type": "Core Banking",
          "owner": "IT",
          "pain_points": ["Batch processing", "Limited APIs"],
          "integration_complexity": "high | medium | low"
        }
      ],
      "integration_patterns": "point_to_point | esb | api_gateway | mixed",
      "technical_debt_areas": ["Legacy integrations", "Monolithic apps"],
      "constraints": ["Mainframe dependency", "Vendor lock-in"]
    },
    "channel_maturity": {
      "mobile": { "maturity": 2, "gaps": ["Self-service", "Personalization"] },
      "web": { "maturity": 3, "gaps": ["Journey continuity"] },
      "branch": { "maturity": 4, "gaps": ["Digital integration"] },
      "call_center": { "maturity": 2, "gaps": ["Context awareness", "Self-service deflection"] }
    }
  }
}
```

---

### 9. Use Cases

```json
{
  "use_cases": [
    {
      "use_case_id": "UC01",
      "title": "Digital Account Opening with Real-Time Decisioning",
      "category": "acquisition | servicing | retention | operations | employee_enablement",
      "description": "Enable end-to-end digital account opening with instant approval",
      "personas_impacted": ["Mass Retail Customer", "Branch Staff"],
      "journeys_impacted": ["customer_onboarding"],
      "linked_pain_points": ["PP01", "PP02"],
      "linked_hypotheses": ["H01"],
      "linked_strategic_themes": ["ST01"],
      "expected_outcomes": {
        "primary": "Increase digital onboarding completion to 80%",
        "secondary": ["Reduce branch workload", "Improve time to first product"]
      },
      "success_metrics": ["M01", "M02"],
      "estimated_value": {
        "annual_benefit": "$2.4M",
        "confidence": "medium",
        "calculation_basis": "Revenue recapture from reduced abandonment"
      },
      "complexity": "high | medium | low",
      "priority": "must_have | should_have | nice_to_have",
      "dependencies": ["Core banking API", "KYC service"],
      "backbase_alignment": "high | medium | low | not_applicable",
      "demo_candidate": true | false
    }
  ]
}
```

---

### 10. Constraints

```json
{
  "constraints": {
    "budget": {
      "available": "$X",
      "cycle": "Annual",
      "approval_required_above": "$Y",
      "notes": "string"
    },
    "timeline": {
      "hard_deadline": "2024-12-31",
      "driver": "Regulatory | Competitive | Executive mandate",
      "flexibility": "high | medium | low"
    },
    "resources": {
      "internal_capacity": "limited | moderate | sufficient",
      "key_resource_gaps": ["Solution architects", "Change management"],
      "external_resources_allowed": true | false
    },
    "technical": {
      "constraints": ["Cannot replace core in 2024", "Must integrate with existing CRM"],
      "non_negotiables": ["On-premise hosting", "Data residency"]
    },
    "regulatory": {
      "requirements": ["PDPA compliance", "MAS guidelines"],
      "audit_timeline": "Q4 2024"
    },
    "organizational": {
      "change_capacity": "low | medium | high",
      "political_considerations": "string",
      "blockers": ["Union approval required for automation"]
    }
  }
}
```

---

### 11. Data Gaps

```json
{
  "data_gaps": [
    {
      "gap_id": "DG01",
      "description": "Current customer acquisition cost not provided",
      "criticality": "high | medium | low",
      "impact_on_analysis": "Cannot validate ROI for acquisition initiatives",
      "default_assumption": "Using industry benchmark of $500 CAC",
      "assumption_source": "Forrester Banking Report 2024",
      "validation_approach": "Request from finance team",
      "owner": "Value Consultant",
      "status": "open | pending | resolved"
    }
  ]
}
```

---

### 12. Next Steps

```json
{
  "next_steps": [
    {
      "action": "Validate CAC with finance team",
      "owner": "Client Finance Lead",
      "due_date": "2024-01-25",
      "linked_gap": "DG01"
    },
    {
      "action": "Schedule IT architecture deep dive",
      "owner": "Solution Architect",
      "due_date": "2024-01-22",
      "linked_hypothesis": "H03"
    },
    {
      "action": "Prepare use case demos for Innovation Day",
      "owner": "Solution Engineer",
      "due_date": "2024-02-01",
      "linked_use_cases": ["UC01", "UC02", "UC03"]
    }
  ]
}
```

---

## Engagement-Specific Extensions

### Ignite Light (Strategic Workshop)

For Ignite Light engagements, the following sections are mandatory:
- `metadata` (with `engagement_type: "ignite_light"`)
- `strategic_context` (full cascading choices)
- `hypothesis_tree` (developed pre-workshop, validated during)
- `pain_point_register` (high-level, 5-10 key pain points)
- `use_cases` (prioritized list for Innovation Day)
- `next_steps`

Optional/lighter:
- `capability_snapshot` (high-level only)
- `metric_register` (key metrics only)
- `evidence_register` (key quotes only)

### Detailed Assessment

For Detailed Assessment engagements, ALL sections are mandatory with full depth:
- Complete `evidence_register` with all stakeholder inputs
- Detailed `capability_snapshot` feeding into Capability Agent
- Full `metric_register` with current/target/benchmark
- Comprehensive `pain_point_register` with quantified impacts
- Complete `stakeholder_map`
- Detailed `constraints`
- Full `data_gaps` with assumptions

---

## Downstream Agent Consumption

### Capability Agent Consumes:
- `capability_snapshot`
- `pain_point_register`
- `evidence_register`
- `metric_register`

### ROI Agent Consumes:
- `pain_point_register` (quantified impacts)
- `metric_register` (baselines)
- `use_cases` (estimated values)
- `constraints.budget`

### Roadmap Agent Consumes:
- `use_cases` (priorities, dependencies)
- `constraints`
- `strategic_context.strategic_themes`
- `stakeholder_map` (priorities)

### Assembly Agent Consumes:
- `strategic_context` (vision, themes)
- `hypothesis_tree` (key findings)
- All registers (for executive summary)
- `next_steps`

---

## Validation Rules

Before output is complete:
1. All `evidence_ids` referenced must exist in `evidence_register`
2. All `pain_point_ids` referenced must exist in `pain_point_register`
3. All `hypothesis_ids` referenced must exist in `hypothesis_tree`
4. `metadata.engagement_type` must be valid
5. At least 3 items in `pain_point_register`
6. At least 1 validated or needs_validation hypothesis in `hypothesis_tree`
7. `next_steps` must have at least 2 items with owners and dates
