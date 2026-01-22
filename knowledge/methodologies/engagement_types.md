# Value Consulting Engagement Types

This document defines the engagement taxonomy for the Value Consulting Agent System. Each engagement type has specific discovery approaches, outputs, and downstream agent workflows.

---

## Engagement Hierarchy

```
Engagement Type
├── Ignite Light (Strategic Workshop)
│   ├── Pre-Ignite Discovery Sessions
│   │   ├── Strategic Alignment
│   │   ├── Customer Experience
│   │   ├── Employee Experience
│   │   ├── IT Architecture
│   │   └── Executive Pre-Readout
│   └── Innovation Day
│       ├── Day 1: Strategy & Customer Use Cases
│       └── Day 2: Employee Use Cases & Roadmap
│
└── Detailed Assessment
    ├── Strategic Alignment (Joint)
    ├── Capability Maturity Mapping
    │   ├── Track: Digital/Customer
    │   └── Track: Advisor/Employee
    ├── Journey Deep Dives
    │   ├── Acquisition/Onboarding
    │   └── Servicing
    ├── Technology Deep Dive
    └── Use Case Validation & Business Value
```

---

## Engagement Type: Ignite Light

### Overview

| Attribute | Value |
|-----------|-------|
| Duration | 1.5 days onsite + 4-6 hours virtual prep |
| Client Time Investment | ~4 hours workshopping |
| Primary Goal | Strategic alignment, use case ideation, roadmap co-creation |
| Deliverables | Use case library, prioritized roadmap, demo showcase |
| Best For | Existing clients, expansion opportunities, strategic re-engagement |

### When to Use

- Client needs strategic alignment on digital transformation priorities
- Want to unlock transformational deals through vision inspiration
- Need to position platform value against 1-3 year strategy
- Client has limited time but high strategic interest
- Expansion opportunity within existing account

### Session Structure

#### Pre-Ignite (Virtual, before onsite)

| Session | Duration | Focus | Key Outputs |
|---------|----------|-------|-------------|
| Kickoff & Planning | 45 min | Align on objectives, stakeholders | Session calendar, confirmed attendees |
| Executive Strategy | 60 min | Vision, KPIs, strategic themes | Cascading Choices alignment |
| Customer Experience | 60 min | Journeys, personas, pain points | "How Might We" statements, use cases |
| Employee Experience | 60 min | Operations, servicing, channels | Servicing use cases, automation opportunities |
| IT Architecture | 90 min | Tech stack, constraints, TCO | Integration feasibility, tech challenges |
| Pre-Readout | 60 min | Synthesize, align on Innovation Day | Demo list, agenda, discussion prompts |

#### Innovation Day (Onsite)

**Day 1 Agenda:**
| Time | Session | Facilitator |
|------|---------|-------------|
| 09:00-09:30 | Welcome & Context | CS & AE |
| 09:30-09:45 | Strategic Themes | Client Executive |
| 09:45-10:15 | Art of Possible | VC |
| 10:15-10:45 | Architecture Overview | SE/SA |
| 10:45-11:00 | Coffee Break | |
| 11:00-13:00 | Customer Use Cases + Demos | VC & SE |
| 13:00-13:15 | Day 1 Wrap | VC |
| 13:15-14:00 | Lunch | All |

**Day 2 Agenda:**
| Time | Session | Facilitator |
|------|---------|-------------|
| 09:00-09:30 | Day 1 Recap | CS & VC |
| 09:30-11:00 | Employee Use Cases + Demos | VC & SE |
| 11:00-11:15 | Coffee Break | |
| 11:15-12:45 | Build/Buy Decisions | SE/SA |
| 12:45-13:30 | Gamified Roadmap Session | VC |
| 13:30-14:00 | Next Steps & Debrief | CS |

### Discovery Toolkit Mode

For Ignite Light, the Discovery Toolkit operates in **Strategic Workshop Mode**:

- Focus on Cascading Choices framework
- Card-based strategic theme selection
- Journey hotspot heat mapping
- Use case prioritization and voting
- High-level pain point capture (not detailed)
- Hypothesis tree validation

### Micro-Engagements (Sub-Sessions)

Each Pre-Ignite session can be run as a standalone micro-engagement:

| Micro-Engagement | Focus | Toolkit Module |
|------------------|-------|----------------|
| `strategic_alignment` | Vision, goals, KPIs | Cascading Choices |
| `customer_experience` | Journey pain points, personas | Journey Heat Map |
| `employee_experience` | Operations, servicing | Operations Canvas |
| `it_architecture` | Tech stack, constraints | Tech Assessment |
| `use_case_validation` | Prioritization, value | Use Case Voting |

---

## Engagement Type: Detailed Assessment

### Overview

| Attribute | Value |
|-----------|-------|
| Duration | 3+ days onsite |
| Client Time Investment | 8-10 hours |
| Primary Goal | Deep current state analysis, full business case, architecture |
| Deliverables | Full assessment report, ROI model, detailed roadmap, architecture |
| Best For | New logos, large transformation deals, complex multi-track engagements |

### When to Use

- New client requiring full business case justification
- Complex multi-track engagement (e.g., Digital + Advisor-led)
- Need detailed capability maturity assessment
- Full journey assessment and application rationalization required
- Budget justification for large investment

### Session Structure

| Session | Duration | Focus | Key Outputs |
|---------|----------|-------|-------------|
| Strategic Alignment (Joint) | 1.5h | Vision, success metrics, growth levers | Strategic problem definition |
| Capability Maturity - Track 1 | 1h | Front-to-back capability assessment | RAG maturity scorecard |
| Capability Maturity - Track 2 | 1h | Front-to-back capability assessment | RAG maturity scorecard |
| Journey Deep Dive - Acquisition | 1h | Onboarding, activation, leakage | Root cause analysis |
| Journey Deep Dive - Servicing | 1.5h | Servicing drivers, operational load | Automation opportunities |
| Technology Deep Dive | 1.5h | Tech stack, constraints, coexistence | Integration feasibility |
| Use Case Validation & Value | 1.5h | Prioritization, KPI linkage, business case | Validated use case library |

### Discovery Toolkit Mode

For Detailed Assessment, the Discovery Toolkit operates in **Deep Dive Mode**:

- Full capability canvas assessment
- RAG scoring per capability
- Detailed metric capture with baselines
- Quantified pain point impacts
- Complete stakeholder mapping
- Full evidence register
- Technical constraint capture

### Micro-Engagements (Sub-Sessions)

| Micro-Engagement | Focus | Toolkit Module |
|------------------|-------|----------------|
| `strategic_alignment_joint` | Joint vision, trade-offs | Cascading Choices + Trade-off Canvas |
| `capability_maturity_digital` | Digital/Customer capabilities | Capability Maturity Canvas |
| `capability_maturity_advisor` | Advisor/Employee capabilities | Capability Maturity Canvas |
| `journey_deep_dive_acquisition` | Onboarding, funding, activation | Journey Deep Dive |
| `journey_deep_dive_servicing` | Servicing, operations | Journey Deep Dive |
| `technology_deep_dive` | Tech stack, integration | Tech Assessment + TCO |
| `use_case_validation` | Prioritization, business value | Use Case Value Mapping |

---

## Discovery Method: Transcript Analysis

### When Workshop Isn't Possible

Sometimes discovery happens through transcript analysis rather than live workshops:

- Client provided meeting recordings/notes
- Post-call synthesis needed
- Consultant debriefing required
- Documentation review

### Process

1. **Receive raw inputs** (transcripts, notes, documents)
2. **Apply hypothesis tree** (same framework as workshops)
3. **Extract structured data** (same output schema)
4. **Flag validation needs** (items requiring follow-up)
5. **Generate discovery output JSON**

### Toolkit Integration

The Discovery Toolkit can import transcript analysis outputs:

1. Consultant processes transcripts manually or with AI assistance
2. Outputs preliminary discovery JSON
3. Toolkit loads JSON and presents for validation
4. Consultant validates/adjusts in toolkit
5. Export final discovery output

---

## Engagement Configuration Schema

```json
{
  "engagement_config": {
    "type": "ignite_light | detailed_assessment",
    "discovery_method": "workshop | transcript | hybrid",
    "tracks": ["digital_investor", "advisor_led"],
    "sessions": [
      {
        "id": "strategic_alignment",
        "name": "Strategic Alignment",
        "duration_minutes": 90,
        "attendees": ["Executive Sponsor", "Product Leads", "CS", "VC"],
        "toolkit_module": "cascading_choices",
        "outputs": ["strategic_themes", "kpis", "success_criteria"]
      }
    ],
    "deliverables": {
      "discovery_output": true,
      "capability_assessment": true,
      "roi_model": true,
      "roadmap": true,
      "executive_summary": true
    }
  }
}
```

---

## Agent Workflow by Engagement Type

### Ignite Light Workflow

```
1. Pre-Work
   └── Discovery Agent: Develop hypothesis tree from research

2. Pre-Ignite Sessions (Workshop Mode)
   └── Discovery Agent: Facilitate sessions, validate hypotheses
   └── Discovery Toolkit: Capture data interactively

3. Between Sessions
   └── Discovery Agent: Synthesize inputs
   └── Benchmark Agent: Curate relevant benchmarks

4. Innovation Day
   └── Use Case Demos (SE-led, informed by discovery)
   └── Roadmap Co-creation (VC-led)

5. Post-Ignite
   └── Discovery Agent: Generate final output JSON
   └── Roadmap Agent: Prioritized initiative list
   └── Assembly Agent: Summary deck
```

### Detailed Assessment Workflow

```
1. Pre-Work
   └── Discovery Agent: Develop hypothesis tree
   └── Benchmark Agent: Curate industry benchmarks

2. Assessment Sessions (Workshop + Deep Dive Mode)
   └── Discovery Agent: Facilitate all sessions
   └── Discovery Toolkit: Capture detailed data

3. Post-Sessions
   └── Discovery Agent: Generate full output JSON
   └── Capability Agent: Full maturity assessment
   └── ROI Agent: Build financial model
   └── Roadmap Agent: Detailed phased roadmap

4. Deliverables
   └── Assembly Agent: Full assessment report
   └── Executive Summary
   └── Business Case Document
```

---

## Toolkit Module Mapping

| Module | Ignite Light | Detailed Assessment |
|--------|--------------|---------------------|
| Engagement Setup | Required | Required |
| Cascading Choices | Full | Full |
| Hypothesis Tree | Validation Only | Development + Validation |
| Journey Heat Map | Quick Capture | Detailed Analysis |
| Pain Point Register | High-Level (5-10) | Comprehensive (15-25) |
| Capability Canvas | Optional | Full RAG Scoring |
| Metric Baseline | Key Metrics Only | Complete Baseline |
| Stakeholder Map | Key Decision Makers | Full Influence Map |
| Use Case Library | Co-Creation | Detailed Specification |
| Tech Assessment | Constraints Only | Full Landscape |
| Summary & Export | JSON + Summary | JSON + Full Report |

---

## Quality Gates by Engagement Type

### Ignite Light Minimum Viable Output

- [ ] Engagement metadata complete
- [ ] 3+ strategic themes validated
- [ ] 5+ pain points with business context
- [ ] 5+ use cases prioritized
- [ ] Hypothesis tree with validation status
- [ ] Next steps with owners and dates

### Detailed Assessment Minimum Viable Output

- [ ] All Ignite Light requirements
- [ ] Full capability maturity scorecard
- [ ] 15+ evidence items with sources
- [ ] All metrics with current/target values
- [ ] Complete stakeholder map
- [ ] All data gaps documented with assumptions
- [ ] Quantified business impact for priority pain points
