# Getting Started

This guide gets you from `git clone` to running your first engagement.

## Prerequisites

You need **two things** installed:

1. **Claude Code** — the AI that powers this system
   - **Option A (recommended):** Install the [Claude Code VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)
   - **Option B:** Install the CLI: `npm install -g @anthropic-ai/claude-code`
   - You need access via Anthropic API key or your organization's SSO

2. **Python 3.9+** (only if you need Excel ROI exports)
   ```bash
   pip install -r requirements.txt
   ```

That's it. No other dependencies.

## Setup (2 minutes)

```bash
# 1. Clone the repo
git clone <repo-url>
cd claudevc

# 2. Open in VS Code (if using the extension)
code .

# 3. Or start the CLI directly
claude
```

When Claude Code opens in this directory, it automatically loads:
- The `.claude/` folder with **10 specialized agents** and **11 slash commands**
- The `CLAUDE.md` file that makes Claude behave as a senior Value Consultant
- All knowledge, templates, and methodologies in the repo

There is nothing else to configure. The repo IS the system.

## Your First Run

Open Claude Code and try one of these:

### Quick test — load domain knowledge
```
/domain-context retail
```
This loads the complete retail banking knowledge pack (personas, journeys, pain points, benchmarks, use cases). You'll see Claude ingest the domain and confirm it's ready.

### Quick test — see an example output
```
Read the example engagement in examples/test_runs/retail_test/.
Walk me through what was produced and how.
```

### Real engagement — process a transcript
```
I have a discovery transcript from a retail bank in Southeast Asia.
Here's the transcript:

[paste your transcript, or reference a file path]

Run the full Value Assessment: evidence register, capability assessment,
ROI model, roadmap, and executive summary.
```

Claude will route this through the agent pipeline: Discovery → Capability → ROI → Roadmap → Assembly.

## Two Engagement Types

Choose your path based on what you're doing:

### Path A: Value Assessment (evidence-based)

**When:** You have discovery transcripts, financial data, or interview notes and need to produce an assessment package.

**What you provide:**
- Business context (industry, geography, strategy)
- Stakeholder interview transcripts (3-5 recommended)
- Pain points with business impact
- Financial data (costs, volumes, revenue — actual or estimated)

**What you get:**
- Evidence register with sourced findings
- Capability maturity assessment with gap analysis
- ROI business case with sensitivity analysis
- Phased implementation roadmap
- Executive summary

**Start with:**
```
Run a full Value Assessment engagement for [client].
Here are my inputs: [provide transcripts, data, context]
```

### Path B: Ignite Inspire (workshop-driven)

**When:** You're facilitating workshops with a prospect and need preparation materials, then synthesis of workshop outputs.

**Workshop sequence:**
1. Strategy Workshop — business priorities and digital vision
2. Member/Customer Experience Workshop — personas, journeys, pain points
3. Employee Experience Workshop — staff workflows and transformation
4. Architecture Workshop — technology landscape and integration approach

**Start with:**
```
Prepare an Ignite engagement for [client name].
They are a [type] in [region]. Here's what I know: [context].
Start with the Strategy Workshop preparation.
```

### Path C: Hybrid

Combine both. Run workshops first, then feed the outputs into a Value Assessment for quantified deliverables.

## Available Slash Commands

These are shortcuts you can type directly in Claude Code:

### Domain Knowledge (load context before analysis)

| Command | What it does |
|---------|-------------|
| `/domain-context` | Load complete domain knowledge for a banking vertical (retail, SME, commercial, wealth, corporate) |
| `/domain-benchmarks` | Query industry benchmarks and KPIs for a specific domain |
| `/domain-pain-points` | Retrieve common pain points from customer and bank perspectives |
| `/domain-journeys` | Get customer and operational journey maps |
| `/domain-usecases` | Retrieve Backbase use cases for a domain |
| `/domain-value-props` | Get value propositions and differentiation by theme |

### Deliverable Generators

| Command | What it does |
|---------|-------------|
| `/presentation` | Transform any content into an interactive Prezi-style HTML presentation |
| `/generate-roi-excel` | Generate a professional Excel ROI model with scenarios and implementation curves |
| `/prototype` | Create interactive HTML mockups for Backbase use cases |
| `/usecase-doc` | Generate a structured 10-section use case specification document |

### Utilities

| Command | What it does |
|---------|-------------|
| `/chunk-document` | Break large documents (PDF, CSV, text) into manageable chunks for processing |

## Setting Up a New Engagement

### Step 1: Create a workspace

Each engagement gets its own folder:

```bash
mkdir -p engagements/acme-bank/{inputs,outputs}
```

Your folder will look like this when ready:

```
engagements/acme-bank/
├── ENGAGEMENT_JOURNAL.md             # Auto-created: decision log & system memory
├── inputs/
│   ├── engagement_intake.md          # Client context (required)
│   ├── transcript_cto.md             # Interview transcript
│   ├── transcript_head_digital.md    # Interview transcript
│   ├── transcript_ops_lead.md        # Interview transcript
│   ├── financial_data.md             # Costs, volumes, revenue (if available)
│   └── annual_report.pdf             # Any supporting documents
└── outputs/                          # System generates outputs here
```

### Step 2: Prepare your transcripts

This is the most important input. The system extracts all evidence from your transcripts — pain points, metrics, constraints, stakeholder priorities.

**One file per interview.** If you had 5 discovery calls, create 5 transcript files. Name them by stakeholder role so it's clear who said what.

| File name | Content |
|-----------|---------|
| `transcript_cto.md` | CTO interview |
| `transcript_head_retail.md` | Head of Retail interview |
| `transcript_ops_lead.md` | Operations Lead interview |
| `transcript_digital_lead.md` | Digital Lead interview |
| `transcript_workshop_day1.md` | Group workshop notes |

**What formats work:**
- **Markdown or plain text** — best option, paste or type directly
- **Word / Google Docs** — copy-paste the content into a `.md` file
- **PDF** — drop the file into `inputs/` and Claude can read it directly
- **Raw messy notes** — that's fine too, the system handles unstructured input

**What to include in each transcript file:**

```markdown
# Discovery Transcript — [Stakeholder Name]

**Role:** Head of Retail Banking
**Date:** 2026-01-15
**Engagement:** Acme Bank Assessment
**Interviewer:** [Your name]

---

Q: How would you describe the current state of your onboarding process?

A: "Our onboarding completion rate is low. A lot of customers drop off
when documents are required. It can take more than a week in some cases."

Q: What's the business impact of that?

A: "We estimate we lose 30-40% of applicants during onboarding.
That's thousands of potential customers per month."

---

[Continue with all questions and answers]
```

**Don't worry about perfection.** The system is designed to handle:
- Rough notes with bullet points instead of full sentences
- Combined notes from multiple people in one session
- Missing questions (just the answers)
- Audio transcription output (from Otter.ai, Fireflies, etc.)
- Mix of verbatim quotes and paraphrased notes

The Discovery agent will extract what it can and flag what's missing.

**Large transcripts and many files — don't worry about size.** The system handles this automatically:
- Long transcripts (2-hour calls, 50+ pages) are read in chunks — the agent processes sections, writes interim findings to disk, and consolidates
- Multiple transcripts are processed one at a time — the system never tries to load everything into memory at once
- Each downstream agent (Capability, ROI, Roadmap) receives only the consolidated findings, not the raw transcripts

You don't need to pre-split files or use `/chunk-document` manually. Just drop your files in `inputs/` at whatever size they are, and the pipeline manages it.

**If you have one big transcript with multiple stakeholders**, that works too. Just make sure each speaker is clearly identified:

```markdown
## Interview: Head of Retail
> "Our onboarding completion rate is low..."

## Interview: Operations Lead
> "Servicing is expensive. Simple requests still come through the call center..."

## Interview: Digital Lead
> "We launched digital onboarding, but it hasn't scaled well..."
```

### Step 3: Create the engagement intake

This gives the system context about the client. Create `inputs/engagement_intake.md`:

```markdown
# Engagement Intake

## Domain
- **Domain:** retail | sme | commercial | corporate | wealth
- **Engagement type:** assessment | ignite | hybrid
- **Primary journeys:** onboarding, lending, servicing, etc.

## Client Context
- **Client Name:** [Name]
- **Industry:** [e.g., Retail Banking]
- **Geography:** [e.g., Southeast Asia]
- **Engagement Date:** [Date]

## Engagement Scope
### Objectives
- [What are we trying to achieve?]

### Key Stakeholders
- [Who did we talk to? List roles and names]

### Known Pain Points
- [What problems surfaced?]

### Constraints
- [Budget, timeline, regulatory, organizational]
```

### Step 4: Add financial data (if available)

If you have cost, volume, or revenue data, add it as `inputs/financial_data.md`. This makes the ROI model much stronger. If you don't have it, the system will use industry benchmarks and flag assumptions.

### Step 5: Run the engagement

```
I'm starting a Value Assessment for Acme Bank.
Inputs are in engagements/acme-bank/inputs/.
Read the engagement intake and all transcripts, then run the full pipeline.
Save outputs to engagements/acme-bank/outputs/.
```

**For a single transcript** (quick analysis):
```
Here's a transcript from my discovery call with the CTO at Acme Bank.
[paste transcript or: Read engagements/acme-bank/inputs/transcript_cto.md]
Extract the evidence register: pain points, metrics, constraints, and priorities.
```

**For multiple transcripts** (full engagement):
```
I have 4 discovery transcripts in engagements/acme-bank/inputs/.
Read all of them plus the engagement intake.
Run the complete Value Assessment pipeline and save outputs to
engagements/acme-bank/outputs/.
```

**To add a transcript later** (incremental processing):
```
I have a new transcript from a follow-up call with the CFO.
Read engagements/acme-bank/inputs/transcript_cfo.md.
Update the evidence register and ROI model with any new findings.
```

## The Engagement Journal

Every engagement automatically gets a journal file at `engagements/[client]/ENGAGEMENT_JOURNAL.md`. This is the system's persistent memory.

### What it records

Every time an agent runs, it writes an entry:
- What it did and which files it read/produced
- Key decisions and their rationale
- Assumptions made and why
- What the consultant asked for or approved
- Current status and what's next

### Why it matters

1. **Pick up where you left off.** Close your laptop, come back in 3 months, and the journal tells you exactly what happened and where the engagement stands.
2. **Audit trail.** Every decision is traceable. If a client asks "why did you assume 500K customers?" — it's in the journal.
3. **Context efficiency.** When resuming, Claude reads the journal instead of re-reading all raw transcripts. Faster, cheaper, and avoids context limits.

### Resuming a paused engagement

```
I'm picking up the Acme Bank engagement.
Read the engagement journal at engagements/acme-bank/ENGAGEMENT_JOURNAL.md
and tell me where we left off.
```

Claude will read the journal, summarize the status, and ask what you want to work on next — without needing to re-process the original transcripts.

### Reviewing decisions

```
Show me all the assumptions we made in the Acme Bank engagement
and which ones still need validation.
```

The journal's cumulative assumptions register tracks every assumption across all agents.

## Reference Example

The repo includes a complete worked example at:

```
examples/test_runs/retail_test/
├── inputs/
│   ├── engagement_intake.md      # Client context
│   └── transcript.md             # Discovery call transcript
└── outputs/
    ├── evidence_register.md      # Extracted findings
    ├── capability_assessment.md  # Maturity scoring
    ├── roi_report.md             # Financial business case
    ├── roadmap.md                # Implementation plan
    ├── executive_summary.md      # Decision document
    ├── assessment_report.md      # Full assessment
    ├── roi_model.xlsx            # Excel ROI model
    └── *.html                    # Presentations and dashboards
```

Review this example to understand what the system produces and the quality standard it targets.

## How the Agent System Works

You don't need to invoke agents directly — Claude routes automatically. But here's what's happening under the hood:

```
Your input (transcripts, data, context)
        │
        ▼
┌─────────────────────┐
│    Orchestrator      │  Routes to the right agents based on your request
└─────────┬───────────┘
          │
    ┌─────┼──────┬──────────┬──────────┐
    ▼     ▼      ▼          ▼          ▼
Discovery  Capability  ROI Builder  Roadmap   Workshop Prep
Agent      Agent       Agent        Agent     Agent
    │      │           │            │         │
    ▼      ▼           ▼            ▼         ▼
Evidence   Maturity    Business     Phased    Facilitation
Register   Assessment  Case         Plan      Materials
    │      │           │            │         │
    └──────┴───────────┴────────────┘         │
                       │                      │
                       ▼                      ▼
              Executive Narrative      Workshop Synthesis
              Assembler Agent          Agent
                       │                      │
                       ▼                      ▼
              Final Deliverable        Prioritized Use Cases
              Package                  & Recommendations
```

### Specialized agents

| Agent | Role |
|-------|------|
| **Orchestrator** | Routes requests, coordinates workflow |
| **Discovery** | Extracts evidence from transcripts and raw inputs |
| **Capability Assessment** | Scores maturity, identifies gaps |
| **ROI Builder** | Builds financial models with sensitivity analysis |
| **Roadmap** | Sequences initiatives by value, feasibility, dependencies |
| **Executive Assembler** | Packages everything into decision-ready deliverables |
| **Workshop Prep** | Prepares facilitation materials for Ignite workshops |
| **Workshop Synthesizer** | Consolidates findings across all workshops |
| **Use Case Designer** | Designs detailed use cases validated against Backbase portfolio |
| **Benchmark Librarian** | Curates and validates industry benchmarks |

## Key Principles

Every output from this system must be:

1. **Evidence-based** — grounded in provided data, not invented
2. **Conservative** — assumptions err on the side of caution
3. **Transparent** — all assumptions documented, methodology visible
4. **Executive-ready** — written for C-level decision-makers
5. **Actionable** — clear recommendations with next steps

When data is missing, the system makes conservative assumptions, documents them explicitly, and flags them for validation.

## Common Workflows

### "I just finished a discovery call"
```
Here's the transcript from my discovery call with [Client].
Extract the evidence register: pain points, metrics, constraints,
and stakeholder priorities. Flag any data gaps.
```

### "I need a presentation for the client"
```
/presentation
Transform the executive summary at engagements/acme-bank/outputs/executive_summary.md
into an interactive presentation for the CTO meeting.
```

### "I need the ROI in Excel"
```
/generate-roi-excel
Build an Excel ROI model from the roi_report.md in engagements/acme-bank/outputs/.
```

### "What benchmarks should I use?"
```
/domain-benchmarks retail
I need onboarding completion rates and cost-to-serve benchmarks
for retail banks in Asia Pacific.
```

### "I need a prototype to show the client"
```
/prototype
Create an interactive mockup for the digital account opening use case
based on the use case doc at engagements/acme-bank/outputs/usecase_digital_onboarding.md
```

## Troubleshooting

### "Claude isn't acting like a consultant"
Make sure you opened Claude Code from the `claudevc/` directory. The `CLAUDE.md` and `.claude/` folder must be in the working directory for the system to activate.

### "Commands like /presentation aren't available"
Slash commands come from `.claude/commands/`. Ensure you're in the repo root and using Claude Code (not regular Claude chat).

### "Excel generation fails"
Install the Python dependencies:
```bash
pip install -r requirements.txt
```

### "I want to add a new domain vertical"
Create files in `knowledge/domains/[new-domain]/` following the pattern of existing domains (retail, sme, etc.). Each domain needs: personas, journeys, pain_points, benchmarks, use_cases, and value_propositions files.

## Further Reading

- [README.md](README.md) — Value Consulting philosophy and standards
- [CLAUDE.md](CLAUDE.md) — How Claude operates as a consultant in this repo
- [STRUCTURE.md](STRUCTURE.md) — Detailed repository organization
- [agents/README.md](agents/README.md) — Agent system design
- [knowledge/Ignite Inspire/README.md](knowledge/Ignite%20Inspire/README.md) — Workshop system documentation
