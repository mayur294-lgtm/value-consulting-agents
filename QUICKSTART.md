# Quick Start Guide

Welcome to the Value Consulting Agent System. This guide will get you started generating consulting outputs.

## What This System Does

This system generates executive-ready consulting deliverables including:
- **Value Assessments** - Capability maturity and gap analysis
- **ROI Reports** - Financial business cases with defensible models
- **Roadmaps** - Phased implementation plans
- **Executive Summaries** - Decision-ready output packages

## System Philosophy

This is NOT a documentation system. This is an **output generation system** that:
- Thinks like a senior consultant
- Generates actual deliverables (not explanations)
- Reasons from evidence
- Makes assumptions explicit
- Produces executive-grade work

## How to Use This System

### Step 1: Understand the Foundation

Read these files in order:
1. **[README.md](README.md)** - Value Consulting principles and standards (10 min)
2. **[CLAUDE.md](CLAUDE.md)** - How Claude operates as a consultant (5 min)
3. **[STRUCTURE.md](STRUCTURE.md)** - Repository organization (5 min)

### Step 2: Gather Your Inputs

Consult these guides to understand what data you need:
- **[Discovery Input Contract](templates/inputs/discovery_input_contract.md)** - Business context, interviews, pain points
- **[Financial Data Schema](templates/inputs/financial_data_schema.md)** - Cost, revenue, volume metrics
- **[Transcript Interpretation Guide](templates/inputs/transcript_interpretation_guide.md)** - How to structure interview notes

**Minimum Required Inputs:**
- Business context (industry, strategy, goals)
- 3-5 stakeholder interview transcripts
- Pain points with business impact
- Current state costs (actual or estimated)
- Budget and timeline constraints

### Step 3: Request Outputs

Ask Claude to generate deliverables using the templates:

**Example Request:**
> "I have interview transcripts and financial data from a B2B SaaS company struggling with customer support costs. Generate a complete Value Assessment including:
> - Capability assessment
> - ROI analysis for self-service initiative
> - Phased roadmap
> - Executive summary
>
> Use the templates in /templates/outputs/."

**What Claude Will Do:**
1. Analyze your inputs using Discovery Agent methodology
2. Assess capabilities using Capability Agent framework
3. Build ROI model using ROI Agent standards
4. Create roadmap using Roadmap Agent approach
5. Package executive summary using Assembly Agent guidelines

### Step 4: Review Outputs

All outputs will include:
- Clear recommendations
- Supporting evidence and calculations
- Explicit assumptions register
- Documented data gaps
- Executive-ready formatting

**Quality Check:**
- Are assumptions explicit and conservative?
- Is ROI defensible and transparent?
- Are recommendations clear and actionable?
- Is output executive-readable?

## Example Workflows

### Workflow 1: Generate a Capability Assessment

**Inputs Needed:**
- Interview transcripts with stakeholders
- Business context (industry, strategy)
- Current state process/system documentation

**Request:**
> "Based on the attached interview transcripts, generate a Capability Assessment Report following the template at templates/outputs/capability_assessment.md. Focus on [specific domain, e.g., Customer Experience capabilities]."

**Output:**
- Complete capability assessment with maturity scoring
- Gap analysis with business impact quantification
- Prioritized improvement recommendations

### Workflow 2: Build an ROI Business Case

**Inputs Needed:**
- Current state costs and pain points
- Proposed initiative description
- Volume metrics and baseline data
- Budget constraints

**Request:**
> "Build a complete ROI report for [initiative description] using the template at templates/outputs/roi_report.md. Current state: [describe costs, volumes, pain]. Proposed solution: [describe approach]."

**Output:**
- Multi-year financial model
- Benefit streams with calculations
- Assumptions register
- Sensitivity analysis
- Go/no-go recommendation

### Workflow 3: Create a Strategic Roadmap

**Inputs Needed:**
- List of initiatives with value and effort estimates
- Dependencies between initiatives
- Resource constraints
- Strategic priorities

**Request:**
> "Create a strategic roadmap for the following initiatives: [list]. Sequence them into Now/Next/Later phases using the template at templates/outputs/roadmap.md. Constraints: [budget, timeline, resources]."

**Output:**
- Phased roadmap with initiative cards
- Dependency mapping
- Resource profile over time
- Financial timeline
- Risk register

### Workflow 4: Generate Complete Engagement Package

**Inputs Needed:**
- All discovery inputs (transcripts, data, context)
- Engagement scope and objectives

**Request:**
> "I have a complete discovery package for [company/situation]. Generate a full consulting deliverable package including:
> 1. Capability assessment
> 2. ROI analysis for top 3 priority initiatives
> 3. Phased roadmap
> 4. Executive summary
>
> Follow Value Consulting standards from README.md."

**Output:**
- Complete engagement deliverable package
- All outputs cross-referenced and consistent
- Executive summary that enables decision-making

## Key Principles to Remember

### 1. Evidence-Based
- Provide data wherever possible
- When data is missing, state assumptions explicitly
- Quote sources for all claims

### 2. Conservative
- Use conservative assumptions in ROI models
- Show worst-case scenarios in sensitivity analysis
- Don't oversell the benefits

### 3. Executive-Ready
- Write for C-level audience
- Avoid jargon
- Lead with conclusions
- Make recommendations clear

### 4. Transparent
- Show your methodology
- Document all assumptions
- Acknowledge limitations
- Make uncertainty visible

### 5. Actionable
- Provide specific recommendations
- Define clear next steps
- Identify decision points
- Assign ownership

## Common Questions

### Q: What if I don't have all the required inputs?

**A:** Document what's missing and make conservative assumptions:
1. Explicitly state the data gap
2. Make a conservative assumption based on industry benchmarks
3. Document the assumption in an assumptions register
4. Flag for validation
5. Run sensitivity analysis

**Example:**
> "Customer acquisition cost not provided. Assuming industry median CAC of $500 based on SaaS benchmarks (source: [report]). Confidence: Medium. Recommend validation with Finance team. Sensitivity: ±25% CAC changes NPV by $X."

### Q: How do I know if my outputs are good enough?

**A:** Use this checklist:
- [ ] All assumptions are explicit and documented
- [ ] ROI calculations are conservative and show methodology
- [ ] Recommendations are clear (go/no-go is obvious)
- [ ] Evidence is cited for all claims
- [ ] Gaps and limitations are acknowledged
- [ ] Output is readable by a non-technical executive
- [ ] Next steps are specific and actionable

### Q: Can I customize the templates?

**A:** Yes, but maintain these standards:
- Keep all required sections
- Follow Value Consulting principles
- Document any deviations
- Ensure executive-readiness

### Q: What if stakeholders disagree in interviews?

**A:** Document both perspectives:
- Present both viewpoints
- Note areas of disagreement
- Validate with data where possible
- Recommend resolution approach
- Don't pick sides without evidence

### Q: How conservative should ROI models be?

**A:** Very conservative:
- Use worst-case costs, best-case benefits
- Extend timelines beyond optimistic estimates
- Add contingency (15-25%)
- Show downside scenarios
- If it feels too optimistic, it probably is

## Getting Help

### Reference Materials

- **Value Consulting Philosophy:** [README.md](README.md)
- **Claude's Behavior:** [CLAUDE.md](CLAUDE.md)
- **Repository Structure:** [STRUCTURE.md](STRUCTURE.md)
- **Agent Definitions:** [agents/definitions/](agents/definitions/)
- **Input Guides:** [templates/inputs/](templates/inputs/)
- **Output Templates:** [templates/outputs/](templates/outputs/)

### Agent Roles

When working through complex engagements, understand which agent does what:
- **Orchestrator** - Routes work and assembles outputs
- **Discovery** - Interprets transcripts and extracts context
- **Capability** - Assesses maturity and identifies gaps
- **ROI** - Builds financial models
- **Roadmap** - Sequences initiatives
- **Assembly** - Creates executive summaries

## Next Steps

1. **Review the foundation files** (README.md, CLAUDE.md, STRUCTURE.md)
2. **Gather your inputs** using the input guides
3. **Request your first output** following the example workflows
4. **Iterate and refine** based on feedback
5. **Build your own example** for future reference

---

**Remember:** This system generates consulting outputs, not explanations. When you engage Claude in this repository, expect actual deliverables that meet senior consultant standards.

**Let's create some value.**
