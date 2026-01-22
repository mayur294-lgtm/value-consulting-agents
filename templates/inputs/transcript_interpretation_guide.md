# Transcript Interpretation Guide

This guide explains how to extract business insight from interview transcripts and meeting notes for Value Consulting engagements.

## Purpose

Interview transcripts are unstructured, conversational, and often ambiguous. This guide provides a framework for:
- Extracting business context and priorities
- Identifying pain points and quantifying impact
- Surfacing assumptions and constraints
- Handling vague or conflicting statements
- Documenting evidence and sources

## Transcript Input Requirements

### Minimum Requirements

**Format:**
- Plain text, Word document, or markdown
- Clear speaker attribution (who said what)
- Date and context (what meeting, what purpose)

**Content:**
- At least 3-5 stakeholder interviews
- Mix of business and technical perspectives
- Executive sponsor or decision maker included
- Operational/end-user perspective included

**Quality:**
- Verbatim or detailed paraphrase (not just bullet points)
- Questions and answers preserved
- Follow-up probes captured
- Reactions and tone noted where relevant

### Ideal Additional Context

- Meeting agenda or objectives
- Interviewer questions or interview guide used
- Stakeholder background (role, tenure, responsibilities)
- Prior context or documents reviewed

## Interpretation Framework

### Step 1: Extract Business Context

**Look for:**
- Industry and market description
- Business model and revenue streams
- Strategic goals and priorities
- Competitive landscape
- Recent changes or initiatives

**Example Extraction:**

**Transcript Quote:**
> "We're a B2B SaaS platform serving mid-market manufacturers. ARR is around $50M, growing 25% annually. Our big strategic push this year is moving upmarket to enterprise accounts, but our current infrastructure struggles with the complexity."

**Extracted Context:**
- Industry: B2B SaaS / Manufacturing vertical
- Company size: $50M ARR
- Growth: 25% annually (strong)
- Strategy: Move upmarket to enterprise
- Challenge: Infrastructure not ready for enterprise complexity

### Step 2: Identify Pain Points

**Look for:**
- Complaints or frustrations
- Workarounds and manual processes
- Failures or incidents
- Customer complaints
- Lost opportunities
- Competitive disadvantages

**Signal Words:**
- "Problem", "issue", "challenge"
- "Takes too long", "too manual", "inefficient"
- "Customers complain about", "we're losing deals"
- "Can't", "doesn't", "fails"
- "Wish we could", "if only"

**Example Extraction:**

**Transcript Quote:**
> "Our sales team is constantly frustrated with the demo environment. It takes 3-4 days to spin up a custom demo for an enterprise prospect, and half the time something breaks. We've definitely lost deals because we couldn't show the integration features quickly enough."

**Extracted Pain Point:**
- **Pain Point:** Slow and unreliable demo environment provisioning
- **Impact:** 3-4 day turnaround, 50% failure rate
- **Business Consequence:** Lost sales opportunities (enterprise deals)
- **Affected Stakeholder:** Sales team, prospective customers
- **Root Cause:** Manual provisioning process, brittle configuration

### Step 3: Quantify Business Impact

**Look for:**
- Specific numbers (time, cost, volume, revenue)
- Frequency statements ("daily", "every deal", "50% of the time")
- Comparative statements ("twice as long as", "half of what we need")
- Estimates or rough orders of magnitude

**Signal Phrases:**
- "Costs us $X"
- "Takes Y hours per Z"
- "We process N per month"
- "Lose about X deals per year"
- "Affects Y customers"

**Example Extraction:**

**Transcript Quote:**
> "Customer support is drowning. We're getting about 1,000 tickets a month, and probably 60% of them are basic 'how do I' questions that shouldn't require a human. Each ticket costs us maybe $20-25 in labor. Do the math – that's $12-15K a month on stuff that could be self-service."

**Extracted Quantification:**
- Volume: 1,000 tickets/month (12,000/year)
- Composition: 60% basic how-to questions (600/month)
- Unit cost: $20-25 per ticket (use $25 conservatively)
- Annual cost: 600 tickets/month × $25 × 12 = $180,000/year
- **Business Impact:** $180K/year in unnecessary support costs
- **Opportunity:** Self-service could deflect these tickets

### Step 4: Surface Constraints and Requirements

**Look for:**
- Budget limitations
- Timeline pressures
- Resource constraints
- Technical requirements
- Regulatory/compliance needs
- Organizational politics

**Signal Phrases:**
- "We only have $X budget"
- "Needs to be done by Y"
- "Can't afford to"
- "Must comply with", "regulatory requirement"
- "Leadership wants", "board expects"
- "Team is already stretched"

**Example Extraction:**

**Transcript Quote:**
> "Budget is tight this year. We've got maybe $500K allocated for platform improvements, and that has to cover three initiatives. Also, we're SOC 2 compliant and can't do anything that puts that at risk. And honestly, the engineering team is maxed out – we'd need external help."

**Extracted Constraints:**
- **Budget:** $500K total, split across 3 initiatives (~$150-200K available)
- **Compliance:** SOC 2 requirement (cannot compromise)
- **Resource:** Engineering team at capacity, external resources required
- **Implication:** Solution must be low-touch on internal engineering, fit budget, maintain compliance

### Step 5: Map Stakeholder Priorities

**Look for:**
- Success criteria
- Decision drivers
- Personal or organizational goals
- Concerns or fears
- Political dynamics

**Example Extraction:**

**Transcript Quote:**
> "From my perspective as VP Sales, I need to see faster time-to-demo. If we can cut that from 4 days to same-day, that's a game changer for closing enterprise deals. The CFO cares more about support costs – she's very focused on improving unit economics. CTO is worried about reliability and security – he won't approve anything that's a hack job."

**Extracted Priorities:**
- **VP Sales:** Speed to demo (4 days → same day), enterprise deal closure
- **CFO:** Support cost reduction, unit economics improvement
- **CTO:** Reliability and security (quality bar is high)
- **Implication:** Solution must address speed AND cost AND quality (not just one)

## Handling Ambiguity

### Vague Statements

When stakeholders make vague claims:

**Example:**
> "System performance is terrible and customers are unhappy."

**How to Interpret:**
- **Extract:** There is a performance issue affecting customers
- **Flag:** "Terrible" and "unhappy" are subjective – need specifics
- **Probe (if possible):** Which system? What metrics? How many customers? What's the impact?
- **Document:** "Qualitative complaint about system performance and customer satisfaction. Requires quantification."

**Do NOT:**
- Invent specific metrics
- Assume "terrible" means X seconds or Y complaints
- Fabricate impact numbers

**DO:**
- Note the concern
- Flag for follow-up
- Use qualitative language in output
- Recommend validation questions

### Conflicting Statements

When stakeholders contradict each other:

**Example:**
> VP Ops: "The integration works fine, no issues."
> Engineering Lead: "The integration breaks twice a week and requires manual fixes."

**How to Handle:**
- **Document both perspectives:** Don't pick a side
- **Note the conflict:** "Stakeholders have different views on integration reliability"
- **Investigate:** Check data (incident logs, support tickets)
- **Present:** Show both perspectives in output
- **Recommend:** "Requires resolution – suggest reviewing incident logs with both stakeholders"

### Speculative or Aspirational Statements

Distinguish facts from hopes:

**Example:**
> "If we build this feature, we'll probably close 50% more enterprise deals."

**How to Interpret:**
- **This is:** An optimistic estimate, not a fact
- **Extract:** Stakeholder believes feature will improve enterprise win rate
- **Flag:** "Estimate not substantiated; requires validation"
- **Use conservatively:** If modeling benefit, use lower bound (25%?) with low confidence
- **Document:** "Stakeholder estimate of 50% win rate improvement. Conservative assumption of 25% used pending validation."

## Evidence Grading

Not all transcript data is equally reliable. Grade your evidence:

### High Confidence
- Specific, quantified data points
- Data from authoritative source (Finance, System reports)
- Corroborated by multiple stakeholders
- Recent and current

**Example:**
> "We processed 10,000 transactions last month according to the system logs. Each transaction takes an average of 15 minutes based on our time tracking."

### Medium Confidence
- Estimates from knowledgeable source
- Uncorroborated but specific
- Logical and internally consistent

**Example:**
> "I'd estimate we spend about 20 hours a week on manual data entry. That's probably 3-4 people spending half their time on it."

### Low Confidence
- Vague or imprecise statements
- "Gut feel" estimates
- Aspirational or speculative
- Contradicted by other sources

**Example:**
> "System performance is probably costing us customers, maybe 10-20% churn?"

**Use in Analysis:**
- High confidence → Use directly in models
- Medium confidence → Use with documented assumption, flag for validation
- Low confidence → Note qualitatively, do not use in financial models

## Extraction Output Format

Use this structure when documenting transcript insights:

### Business Context Summary

**Industry & Business Model:**
[Extracted from transcripts]

**Strategic Goals:**
- Goal 1 [Quote source]
- Goal 2 [Quote source]

**Competitive Context:**
[Extracted from transcripts]

### Pain Point Register

| Pain Point | Description | Business Impact | Evidence | Confidence |
|------------|-------------|-----------------|----------|------------|
| [Name] | [What's wrong] | [Quantified impact] | [Quote or source] | [H/M/L] |

### Quantified Impacts

| Impact Area | Current State | Business Consequence | Source | Confidence |
|-------------|---------------|----------------------|--------|------------|
| [e.g., Support Costs] | 1,000 tickets/month at $25/ticket | $300K annual cost | Transcript: Dir of Support | Medium |

### Stakeholder Priorities

| Stakeholder | Role | Key Priorities | Success Criteria | Concerns |
|-------------|------|----------------|------------------|----------|
| [Name] | [Role] | [What they care about] | [How they measure success] | [What they worry about] |

### Constraints

- **Budget:** [Amount and source]
- **Timeline:** [Deadlines or urgency]
- **Technical:** [Requirements or limitations]
- **Organizational:** [Resource, political, capacity constraints]

### Data Gaps & Follow-Up Questions

| Gap | Why It Matters | Recommended Follow-Up |
|-----|----------------|----------------------|
| [Missing data point] | [Impact on analysis] | [Question to ask] |

### Assumptions Made

| Assumption | Basis | Confidence | Validation Needed |
|------------|-------|------------|-------------------|
| [What we assumed] | [Why] | [H/M/L] | [How to confirm] |

## Quality Standards

### Good Transcript Interpretation

- Separates facts from opinions
- Quotes sources for all claims
- Quantifies impact wherever possible
- Acknowledges data gaps explicitly
- Makes conservative assumptions
- Flags low-confidence data
- Documents conflicting viewpoints

### Poor Transcript Interpretation

- Treats speculation as fact
- Invents numbers not stated
- Over-interprets vague statements
- Hides uncertainty
- Picks sides in stakeholder conflicts
- Ignores contradictions
- Makes optimistic assumptions

## Common Pitfalls

### Pitfall 1: Over-Interpreting

**Bad:**
> Stakeholder: "We need better tools."
> Interpretation: "Stakeholder requires a new CRM system costing $100K."

**Good:**
> Stakeholder: "We need better tools."
> Interpretation: "Stakeholder expressed dissatisfaction with current tooling. Specific tools and investment level not specified. Requires follow-up."

### Pitfall 2: Assuming Precision

**Bad:**
> Stakeholder: "It takes forever to process these."
> Interpretation: "Processing time is 4 hours per transaction."

**Good:**
> Stakeholder: "It takes forever to process these."
> Interpretation: "Stakeholder views processing time as excessive. Specific duration not provided. Recommend timing study or system log analysis."

### Pitfall 3: Ignoring Context

**Bad:**
> Stakeholder: "We lose $1M a year on this."
> Interpretation: "$1M annual cost to be eliminated."

**Good:**
> Stakeholder: "We lose $1M a year on this."
> Interpretation: "Stakeholder estimates $1M annual impact. Requires breakdown: is this lost revenue, excess cost, opportunity cost? Basis of estimate unclear. Validate with Finance."

### Pitfall 4: Cherry-Picking

**Bad:**
> Stakeholder A: "This is our #1 priority."
> Stakeholder B: "This is low priority compared to X."
> Interpretation: "Stakeholder consensus this is top priority."

**Good:**
> Stakeholder A: "This is our #1 priority."
> Stakeholder B: "This is low priority compared to X."
> Interpretation: "Stakeholder priorities conflict. A views as critical, B views as lower than X. Requires executive alignment on prioritization."

## Example: Complete Transcript Interpretation

See `/examples/engagements/[example-name]/discovery/transcript-interpretation.md` for a full worked example of transcript analysis.

## Checklist: Before Moving to Assessment

- [ ] Business context is clear (industry, strategy, goals)
- [ ] Pain points are documented with evidence
- [ ] At least 3 pain points have quantified business impact
- [ ] Stakeholder priorities are mapped
- [ ] Constraints and requirements are documented
- [ ] Data gaps are explicitly flagged
- [ ] All assumptions are documented
- [ ] Conflicting viewpoints are noted
- [ ] Sources are cited for all major claims
- [ ] Confidence levels are assigned

If any checklist item is missing, either gather more data or document the limitation and proceed with documented assumptions.
