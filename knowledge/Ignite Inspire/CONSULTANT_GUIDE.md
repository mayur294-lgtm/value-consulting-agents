# BACKBASE IGNITE AI AGENT SYSTEM
## Consultant Implementation Guide
### Version 1.0 | January 2026

---

# TABLE OF CONTENTS

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Quick Start Guide](#3-quick-start-guide)
4. [Agent Deep Dives](#4-agent-deep-dives)
5. [Engagement Workflows](#5-engagement-workflows)
6. [Context File Management](#6-context-file-management)
7. [Best Practices](#7-best-practices)
8. [Troubleshooting](#8-troubleshooting)
9. [Appendix](#9-appendix)

---

# 1. INTRODUCTION

## What is the Ignite AI Agent System?

The Ignite AI Agent System is a suite of 7 specialized AI agents that automate the creation of Backbase Ignite value consulting deliverables. Each agent is designed to generate specific outputs—from workshop facilitation decks to ROI business cases—while maintaining consistency, quality, and Backbase alignment.

## Why Use This System?

| Benefit | Description |
|---------|-------------|
| **Speed** | Generate draft deliverables in minutes, not hours |
| **Consistency** | Standardized outputs across all engagements |
| **Quality** | Built-in best practices, frameworks, and quality checks |
| **Scalability** | Enable more consultants to deliver high-quality work |
| **Knowledge Capture** | Backbase capabilities and benchmarks embedded |

## Prerequisites

- Claude.ai account (Pro or Team subscription recommended)
- Basic familiarity with Claude Projects
- Access to client strategy documents and engagement materials

---

# 2. SYSTEM ARCHITECTURE

## The 7 Agents

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        IGNITE AI AGENT SYSTEM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│   │   AGENT 1   │───▶│   AGENT 2   │───▶│   AGENT 3   │───▶│   AGENT 4   │ │
│   │  Strategy   │    │   Member    │    │  Employee   │    │     IT      │ │
│   │  Workshop   │    │ Experience  │    │ Experience  │    │Architecture │ │
│   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │                  │         │
│         └──────────────────┴──────────────────┴──────────────────┘         │
│                                    │                                        │
│                                    ▼                                        │
│                        ┌───────────────────────┐                           │
│                        │ ENGAGEMENT_CONTEXT.md │                           │
│                        │   (Shared Context)    │                           │
│                        └───────────────────────┘                           │
│                                    │                                        │
│                    ┌───────────────┼───────────────┐                       │
│                    ▼               ▼               ▼                       │
│            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                 │
│            │   AGENT 5   │ │   AGENT 6   │ │   AGENT 7   │                 │
│            │  Use Case   │ │Presentation │ │     ROI     │                 │
│            │  Design +   │ │  Compiler   │ │  Business   │                 │
│            │ Prototypes  │ │             │ │    Case     │                 │
│            └─────────────┘ └─────────────┘ └─────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Agent Summary

| Agent | Purpose | Primary Output | When to Use |
|-------|---------|----------------|-------------|
| **Agent 1** | Strategy Workshop | HTML facilitation deck with competitive analysis & hypotheses | Pre-workshop |
| **Agent 2** | Member/Customer Experience | HTML facilitation deck with personas & journeys | Pre-workshop |
| **Agent 3** | Employee Experience | HTML facilitation deck with employee personas & systems | Pre-workshop |
| **Agent 4** | IT Architecture | HTML facilitation deck with tech landscape & rationalization | Pre-workshop |
| **Agent 5** | Use Case Design | Use Case Documents + Interactive Prototypes | Post-workshop |
| **Agent 6** | Presentation | Final Ignite Day PPTX/HTML presentation | Post-workshop |
| **Agent 7** | ROI Business Case | Questionnaire (Phase A) + Business Case (Phase B) | Pre/Post |

## How Agents Connect

Agents share information through **ENGAGEMENT_CONTEXT.md** - a standardized file that accumulates findings from each workshop. Each agent:

1. **Reads** the context file (if provided)
2. **Uses** prior findings to inform its output
3. **Updates** the context with new validated information

---

# 3. QUICK START GUIDE

## Option A: Single Unified Project (Recommended)

**Best for:** Most engagements, smaller teams, simpler management

### Step 1: Create the Project
1. Go to claude.ai → Projects → Create Project
2. Name it: `Ignite AI Agent`
3. Description: "Generates Ignite value consulting deliverables"

### Step 2: Upload Agent Instructions
1. In Project Knowledge, upload ALL CLAUDE.md files:
   - `agent-1-strategy/CLAUDE.md`
   - `agent-2-member/CLAUDE.md`
   - `agent-3-employee/CLAUDE.md`
   - `agent-4-architecture/CLAUDE.md`
   - `agent-5-usecase/CLAUDE.md`
   - `agent-6-presentation/CLAUDE.md`
   - `agent-7-roi/CLAUDE.md`
2. Also upload `ENGAGEMENT_CONTEXT_TEMPLATE.md`

### Step 3: Start an Engagement
Start a new conversation and use trigger phrases:

```
"Start a new Ignite engagement for [Client Name]. They are a [bank/credit union] 
with [X] customers/members and [$X] in assets. Generate the Strategy Workshop deck."
```

### Step 4: Progress Through Agents
Use trigger phrases to activate different agents:

| To Generate | Say |
|-------------|-----|
| Strategy deck | "Generate the Strategy Workshop deck" |
| Member Experience deck | "Generate the Member Experience Workshop deck" |
| Employee Experience deck | "Generate the Employee Experience Workshop deck" |
| IT Architecture deck | "Generate the IT Architecture Workshop deck" |
| Use Case Documents | "Create use case design documents and prototypes" |
| ROI Questionnaire | "Generate the ROI questionnaire" |
| Business Case | "Build the business case from this questionnaire" |
| Final Presentation | "Compile the Ignite Day presentation" |

---

## Option B: Separate Projects per Agent

**Best for:** Large teams, sharing specific agents, maximum flexibility

### Setup
Create 7 separate Claude Projects:

| Project Name | Upload |
|--------------|--------|
| Ignite - Strategy Workshop | `agent-1-strategy/CLAUDE.md` |
| Ignite - Member Experience | `agent-2-member/CLAUDE.md` |
| Ignite - Employee Experience | `agent-3-employee/CLAUDE.md` |
| Ignite - IT Architecture | `agent-4-architecture/CLAUDE.md` |
| Ignite - Use Case Design | `agent-5-usecase/CLAUDE.md` |
| Ignite - Presentation | `agent-6-presentation/CLAUDE.md` |
| Ignite - ROI Business Case | `agent-7-roi/CLAUDE.md` |

### Workflow
1. Run Agent 1, download updated ENGAGEMENT_CONTEXT.md
2. Upload context to Agent 2, run, download updated context
3. Continue through agents as needed
4. Pass context file between projects manually

---

# 4. AGENT DEEP DIVES

## Agent 1: Strategy Workshop

### Purpose
Generates a hypothesis-driven facilitation deck for the Strategy Alignment Workshop, including competitive benchmarking and quantified hypotheses.

### Key Features
- **Competitive Analysis**: Automatically searches for competitor data
- **Quantified Hypotheses**: Specific, testable claims with business impact
- **Validation Questions**: Pointed questions to confirm/deny hypotheses
- **Backbase Alignment**: Maps strategic themes to Backbase capabilities

### Required Inputs
- Client name and type (bank vs credit union)
- Client size (customers/members, assets)
- Strategy documents (annual report, digital strategy, etc.)

### Sample Prompt
```
Generate the Strategy Workshop deck for Pacific Northwest Credit Union.
They are a credit union with 500,000 members and $8 billion in assets.
Here is their digital strategy document: [attach file]

Include competitive benchmarking against similar-sized credit unions 
in the Pacific Northwest region.
```

### Output
- HTML facilitation deck (60-90 minutes of content)
- Updated ENGAGEMENT_CONTEXT.md with:
  - Client profile
  - Strategic themes identified
  - Hypotheses and validation status

---

## Agent 2: Member/Customer Experience

### Purpose
Generates a hypothesis-driven facilitation deck for the Member (CU) or Customer (Bank) Experience Workshop.

### Key Features
- **Persona Canvases**: Pre-populated personas based on client segments
- **Journey Mapping**: Stage-by-stage analysis with pain points
- **Digital Capability Assessment**: Gap analysis by journey stage
- **Terminology Aware**: Uses "Member" for CUs, "Customer" for banks

### Required Inputs
- ENGAGEMENT_CONTEXT.md (from Agent 1)
- Persona research or segmentation data (if available)
- Journey research or customer feedback (if available)

### Sample Prompt
```
Generate the Member Experience Workshop deck for BECU.
Use the attached ENGAGEMENT_CONTEXT.md for background.
Here are their customer research findings: [attach file]
```

### Output
- HTML facilitation deck
- Updated ENGAGEMENT_CONTEXT.md with:
  - Validated personas (3-5)
  - Journey priorities
  - Key pain points
  - Experience use case candidates

---

## Agent 3: Employee Experience

### Purpose
Generates a facilitation deck for the Employee Experience Workshop, focused on the Transaction Center → Advisory Hub transformation.

### Key Features
- **Employee Personas**: Role-specific (Teller, Universal Banker, Contact Center)
- **Systems Inventory**: Maps current tools and pain points
- **Day in the Life**: Time-motion analysis hypothesis
- **Digital Assist Alignment**: Maps to Backbase employee capabilities

### Required Inputs
- ENGAGEMENT_CONTEXT.md (from prior agents)
- Employee role information
- Current systems list (if available)

### Sample Prompt
```
Generate the Employee Experience Workshop deck.
Use the attached context file.
Focus on branch and contact center roles.
```

### Output
- HTML facilitation deck
- Updated ENGAGEMENT_CONTEXT.md with:
  - Employee personas (2-4 roles)
  - Systems inventory
  - Productivity opportunities
  - Employee use case candidates

---

## Agent 4: IT Architecture

### Purpose
Generates a facilitation deck for the IT Architecture Workshop, covering technology landscape, integration approach, and application rationalization.

### Key Features
- **Technology Landscape Canvas**: Pre-populated system inventory
- **Core Banking Integration**: Approach recommendations by vendor
- **Application Rationalization**: Retire/Replace/Retain framework
- **Target Architecture Vision**: Backbase integration diagram

### Required Inputs
- ENGAGEMENT_CONTEXT.md (from prior agents)
- Technology landscape documentation
- Core banking system information

### Sample Prompt
```
Generate the IT Architecture Workshop deck.
Their core banking system is Symitar.
Here is their technology landscape diagram: [attach file]
```

### Output
- HTML facilitation deck
- Updated ENGAGEMENT_CONTEXT.md with:
  - Technology landscape summary
  - Core systems and versions
  - Integration approach decisions
  - Application disposition recommendations

---

## Agent 5: Use Case Design + Prototypes

### Purpose
Creates detailed Use Case Design Documents and interactive HTML prototypes based on validated workshop findings.

### Key Features
- **Use Case Documents**: Complete specifications with 10 sections
- **Interactive Prototypes**: Clickable HTML mockups
- **Happy Path Focus**: Prototypes follow documented user flow
- **Backbase Implementation**: Module mapping and approach

### Important Notes
- This agent runs **POST-WORKSHOP** (after workshops are complete)
- Requires **validated** findings, not hypotheses
- Generates **actual deliverables**, not facilitation materials

### Required Inputs
- ENGAGEMENT_CONTEXT.md (fully populated)
- Workshop transcripts or validated findings
- Prioritized use case list

### Sample Prompt
```
Create use case design documents and prototypes for BECU.
Use the attached ENGAGEMENT_CONTEXT.md.
Here are the workshop transcripts: [attach files]

Generate prototypes for P1 use cases:
- Digital Account Opening
- Credit Card Application
- 360° Member View (Employee)
```

### Output
- Member Use Case Design Document (Word/HTML)
- Employee Use Case Design Document (Word/HTML)
- Interactive prototypes for each P1 use case (HTML files)
- Updated ENGAGEMENT_CONTEXT.md

---

## Agent 6: Ignite Presentation

### Purpose
Compiles all engagement findings into a polished, client-ready presentation for Ignite Day.

### Key Features
- **Narrative Flow**: Discovery → Vision → Value → Path Forward
- **Executive Summary**: Key findings and recommendations
- **Use Case Showcase**: Includes prototype screenshots
- **ROI Summary**: Business case highlights

### Required Inputs
- ENGAGEMENT_CONTEXT.md (fully populated)
- Use Case Design Documents (from Agent 5)
- Business Case highlights (from Agent 7)
- Prototype screenshots

### Sample Prompt
```
Compile the Ignite Day presentation for BECU.
Use all attached materials:
- ENGAGEMENT_CONTEXT.md
- Use Case Design Documents
- Business Case summary
- Prototype screenshots
```

### Output
- PPTX or HTML presentation (60-90 slides)
- Executive summary document
- Speaker notes

---

## Agent 7: ROI Business Case (Two-Phase)

### Purpose
Generates ROI analysis through two distinct phases: questionnaire creation and business case generation.

### Phase A: Questionnaire Generation

**Purpose**: Create a customized data collection questionnaire pre-populated with known information.

**Sample Prompt**:
```
Generate the ROI questionnaire for BECU.
Use the attached ENGAGEMENT_CONTEXT.md to pre-populate known data.
Focus on: Account Opening, Lending, Self-Service use cases.
```

**Output**: Excel questionnaire with 8 sheets, pre-filled where possible

### Phase B: Business Case Generation

**Purpose**: Calculate ROI and generate business case document from completed questionnaire.

**Sample Prompt**:
```
Build the business case from this completed questionnaire.
[attach filled questionnaire]
Use the ENGAGEMENT_CONTEXT.md for additional context.
```

**Output**:
- Business Case Document (PDF/PPTX)
- ROI Model (Excel with working formulas)
- Updated ENGAGEMENT_CONTEXT.md with ROI summary

---

# 5. ENGAGEMENT WORKFLOWS

## Full Ignite Engagement (4 Workshops)

```
Week 1-2: Pre-Workshop Preparation
├── Receive client strategy documents
├── Agent 1 → Generate Strategy Workshop deck
├── Conduct Strategy Workshop
├── Update ENGAGEMENT_CONTEXT.md with validated findings
│
Week 3-4: Experience Workshops
├── Agent 2 → Generate Member Experience deck
├── Conduct Member Experience Workshop
├── Agent 3 → Generate Employee Experience deck
├── Conduct Employee Experience Workshop
├── Update ENGAGEMENT_CONTEXT.md
│
Week 5: Architecture Workshop
├── Agent 4 → Generate IT Architecture deck
├── Conduct IT Architecture Workshop
├── Update ENGAGEMENT_CONTEXT.md
│
Week 6-7: Deliverable Creation
├── Agent 5 → Create Use Case Documents + Prototypes
├── Agent 7 Phase A → Generate ROI Questionnaire
├── Collect ROI data from client
├── Agent 7 Phase B → Generate Business Case
│
Week 8: Final Presentation
├── Agent 6 → Compile Ignite Day Presentation
└── Deliver Ignite Day
```

---

## ROI-Only Engagement

```
Day 1: Setup
├── Gather basic client information
├── Agent 7 Phase A → Generate Questionnaire
│
Days 2-5: Data Collection
├── Send questionnaire to client
├── Follow up on missing data
│
Day 6-7: Business Case
├── Agent 7 Phase B → Generate Business Case
└── Present findings
```

---

## Experience Sprint (2 Workshops)

```
Week 1:
├── Agent 2 → Member Experience deck
├── Conduct workshop
│
Week 2:
├── Agent 3 → Employee Experience deck
├── Conduct workshop
│
Week 3:
├── Agent 5 → Use Case Documents + Prototypes
└── Deliver findings
```

---

## Engagement Type Matrix

| Engagement Type | Agents Used | Duration |
|-----------------|-------------|----------|
| **Full Ignite** | 1 → 2 → 3 → 4 → 5 → 7 → 6 | 6-8 weeks |
| **ROI Only** | 7 (Phase A + B) | 1-2 weeks |
| **Experience Sprint** | 2 → 3 → 5 | 3-4 weeks |
| **Strategy + Presentation** | 1 → 6 | 2-3 weeks |
| **Architecture Assessment** | 4 → 5 | 2-3 weeks |
| **Prototype Demo** | 5 only | 1 week |

---

# 6. CONTEXT FILE MANAGEMENT

## ENGAGEMENT_CONTEXT.md Structure

The context file has 10 sections that accumulate information:

```markdown
# ENGAGEMENT CONTEXT: [Client Name]

## 1. CLIENT PROFILE
- Name, type, size, region
- Key contacts
- Engagement timeline

## 2. STRATEGIC CONTEXT (Agent 1)
- North Star vision
- Strategic themes (prioritized)
- Key hypotheses and validation status

## 3. MEMBER/CUSTOMER EXPERIENCE (Agent 2)
- Validated personas
- Journey priorities
- Pain points
- Experience use case candidates

## 4. EMPLOYEE EXPERIENCE (Agent 3)
- Employee personas
- Systems inventory
- Productivity metrics
- Employee use case candidates

## 5. IT ARCHITECTURE (Agent 4)
- Technology landscape
- Core systems
- Integration approach
- Application dispositions

## 6. USE CASES (Agent 5)
- Prioritized use case list
- P1/P2/P3 classification
- Implementation approach

## 7. ROI & BUSINESS CASE (Agent 7)
- Investment summary
- Value levers
- ROI metrics

## 8. ROADMAP
- Phased approach
- Timeline
- Dependencies

## 9. ENGAGEMENT LOG
- Workshop dates
- Key decisions
- Action items

## 10. OPEN ITEMS
- Outstanding questions
- Data requests
- Risks
```

## Best Practices for Context Management

1. **Always start from the template** - Don't create from scratch
2. **Update after each workshop** - Keep context current
3. **Mark hypotheses vs validated** - Distinguish assumptions from facts
4. **Include specific data** - Numbers, percentages, not vague statements
5. **Note sources** - Reference where information came from

---

# 7. BEST PRACTICES

## Prompting Tips

### DO ✅

```
✅ "Generate the Strategy Workshop deck for First National Bank. 
   They are a regional bank with 200,000 customers and $5B in assets, 
   headquartered in Ohio. Their strategic priority is digital transformation 
   of lending. Include competitive analysis against Huntington and KeyBank."

✅ "Create use case documents for these P1 priorities:
   1. Digital Account Opening
   2. Personal Loan Application  
   3. 360° Customer View
   Include prototypes for each."

✅ "Build the business case using the attached completed questionnaire.
   The client has confirmed these value levers are in scope:
   - Account opening (in scope)
   - Lending origination (in scope)
   - Branch transformation (out of scope)"
```

### DON'T ❌

```
❌ "Make me a deck" (too vague)

❌ "Generate everything for BECU" (no specific agent/output)

❌ "Create the business case" (without questionnaire data)
```

## Quality Checklist

Before delivering any output, verify:

### For Workshop Decks (Agents 1-4)
- [ ] Client name used throughout (not generic)
- [ ] Correct terminology (Member vs Customer)
- [ ] Hypotheses are specific and quantified
- [ ] Validation questions included
- [ ] Backbase alignment appropriate (not oversold)
- [ ] Facilitation notes included

### For Use Case Documents (Agent 5)
- [ ] All P1 use cases fully specified
- [ ] Happy path steps clear and numbered
- [ ] Backbase module correctly identified
- [ ] Definition of done is measurable
- [ ] Prototypes match documented flow

### For Business Case (Agent 7)
- [ ] All calculations traceable
- [ ] Assumptions clearly stated
- [ ] ROI metrics reasonable (150-400% typical)
- [ ] No Excel formula errors
- [ ] Sensitivity analysis included

---

## Terminology Rules

| If Client Is | Use | Not |
|--------------|-----|-----|
| Credit Union | Member | Customer |
| Credit Union | Membership | Account Opening |
| Bank | Customer | Member |
| Any | Branch/Financial Center | Store |
| Any | Digital Banking | Online Banking |

---

# 8. TROUBLESHOOTING

## Common Issues

### "The agent isn't using the right terminology"

**Solution**: Be explicit in your prompt:
```
"This is a CREDIT UNION. Use 'Member' terminology throughout, 
never 'Customer'."
```

### "The hypotheses are too generic"

**Solution**: Ask for specifics:
```
"Make hypotheses more specific. Include:
- Quantified claims (percentages, dollar amounts)
- Business impact for each
- Specific validation questions"
```

### "The competitive analysis is missing"

**Solution**: Explicitly request it:
```
"Include competitive benchmarking. Search for:
- [Competitor 1] mobile app rating
- [Competitor 2] digital banking capabilities
Compare against [Client] on key metrics."
```

### "The prototype doesn't match the use case"

**Solution**: Ensure use case is defined first:
```
"First, show me the complete happy path for UC-001 Digital Account Opening.
Then generate the prototype following that exact flow."
```

### "Agent 7 ROI seems too high/low"

**Solution**: Review assumptions:
```
"The ROI of [X]% seems [high/low]. Please:
1. List all assumptions used
2. Show calculation for each value lever
3. Identify which assumptions have highest impact
4. Run sensitivity analysis"
```

---

## Getting Help

1. **Re-read the CLAUDE.md** for the specific agent
2. **Check the example outputs** in this guide
3. **Be more explicit** in your prompts
4. **Provide more context** (documents, prior outputs)

---

# 9. APPENDIX

## A. File Structure

```
ignite-agents/
├── README.md                              # This guide
├── templates/
│   └── ENGAGEMENT_CONTEXT_TEMPLATE.md     # Context file template
├── agent-1-strategy/
│   └── CLAUDE.md                          # Strategy Workshop instructions
├── agent-2-member/
│   └── CLAUDE.md                          # Member Experience instructions
├── agent-3-employee/
│   └── CLAUDE.md                          # Employee Experience instructions
├── agent-4-architecture/
│   └── CLAUDE.md                          # IT Architecture instructions
├── agent-5-usecase/
│   └── CLAUDE.md                          # Use Case Design instructions
├── agent-6-presentation/
│   └── CLAUDE.md                          # Presentation instructions
└── agent-7-roi/
    └── CLAUDE.md                          # ROI Business Case instructions
```

---

## B. Backbase Module Reference

| Module | Description | Typical Use Cases |
|--------|-------------|-------------------|
| **Digital Banking** | Core digital banking experience | Balance, transactions, payments |
| **Digital Onboarding** | Account opening journeys | New customer/member acquisition |
| **Digital Lending** | Loan origination | Personal loans, auto, mortgage |
| **Digital Engage** | Marketing & engagement | Personalization, campaigns |
| **Digital Assist** | Employee enablement | 360° view, guided workflows |

---

## C. Industry Benchmarks

| Metric | Average | Best-in-Class |
|--------|---------|---------------|
| Digital Adoption | 62% | 85%+ |
| Mobile App Rating (iOS) | 4.5 | 4.8+ |
| Digital Account Opening Completion | 35% | 55%+ |
| Loan Application Abandonment | 65% | <40% |
| First Contact Resolution | 65% | 85%+ |
| Cost per Branch Transaction | $4-8 | - |
| Cost per Contact Center Call | $5-12 | - |
| Cost per Digital Transaction | $0.10-0.50 | - |

---

## D. Common Use Cases Library

### Member/Customer Use Cases
| ID | Use Case | Module | Typical Priority |
|----|----------|--------|------------------|
| UC-M01 | Digital Account Opening | Onboarding | P1 |
| UC-M02 | Personal Loan Application | Lending | P1 |
| UC-M03 | Credit Card Application | Lending | P1 |
| UC-M04 | Mortgage Pre-Qualification | Lending | P2 |
| UC-M05 | Card Management | Banking | P1 |
| UC-M06 | Bill Pay | Banking | P1 |
| UC-M07 | P2P Payments | Banking | P2 |
| UC-M08 | External Transfers | Banking | P1 |
| UC-M09 | Dispute Management | Banking | P2 |
| UC-M10 | Secure Messaging | Banking | P2 |

### Employee Use Cases
| ID | Use Case | Module | Typical Priority |
|----|----------|--------|------------------|
| UC-E01 | 360° Member/Customer View | Assist | P1 |
| UC-E02 | Omnichannel Context | Assist | P1 |
| UC-E03 | Guided Workflows | Assist | P2 |
| UC-E04 | Case Management | Assist | P2 |
| UC-E05 | Knowledge Base | Assist | P2 |

---

## E. Quick Reference Card

### Trigger Phrases

| Output Needed | Say This |
|---------------|----------|
| Strategy deck | "Generate Strategy Workshop deck for [Client]" |
| Member Experience deck | "Generate Member Experience Workshop deck" |
| Employee Experience deck | "Generate Employee Experience Workshop deck" |
| IT Architecture deck | "Generate IT Architecture Workshop deck" |
| Use Case Documents | "Create use case design documents" |
| Prototypes | "Generate prototypes for [use cases]" |
| ROI Questionnaire | "Generate ROI questionnaire for [Client]" |
| Business Case | "Build the business case from this questionnaire" |
| Final Presentation | "Compile the Ignite Day presentation" |

### Key Reminders

1. **Start every engagement** with ENGAGEMENT_CONTEXT_TEMPLATE.md
2. **Update context** after each workshop
3. **Be specific** - include client name, type, size, priorities
4. **Provide documents** - strategy docs, transcripts, questionnaire data
5. **Check terminology** - Member vs Customer
6. **Verify outputs** - hypotheses quantified, calculations correct

---

## F. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial release with 7 agents |

---

*End of Consultant Guide*

**Questions?** Contact the Value Consulting team or refer to the individual CLAUDE.md files for detailed agent instructions.
