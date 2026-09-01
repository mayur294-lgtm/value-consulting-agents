# Repository Structure

This document provides an overview of the complete folder structure and purpose of each component.

## Root Files

- **[README.md](README.md)** - Authoritative source defining Value Consulting philosophy, methodology, and standards
- **[CLAUDE.md](CLAUDE.md)** - Defines how Claude operates in this repository as a Value Consultant and output generator
- **STRUCTURE.md** - This file, explaining repository organization

## Directory Structure

```
cortex/
├── README.md                          # Value Consulting philosophy & standards
├── CLAUDE.md                          # Claude's role and behavior in this repo
├── STRUCTURE.md                       # Repository structure overview
│
├── engagements/                       # Live engagement work (Client → Engagement hierarchy)
│   └── [client_short_name]/           # One directory per client/bank
│       ├── CLIENT_PROFILE.md          # Persistent client memory (survives across engagements)
│       ├── [YYYY-MM_domain_type]/     # Individual engagement
│       │   ├── inputs/                # Transcripts, intake form, artifacts
│       │   │   └── engagement_intake.md
│       │   ├── outputs/               # Agent-produced deliverables
│       │   ├── ENGAGEMENT_JOURNAL.md  # Engagement-level system memory
│       │   └── .engagement_session_id # Telemetry UUID
│       └── [YYYY-MM_domain_type]/     # Another engagement for same client
│           └── ...
│
├── scripts/                           # Utilities and automation
│   ├── init_engagement.sh             # Bootstrap new engagement (opaque ID + map entry)
│   ├── find_engagement.sh             # Resolve a client name to its engagement path
│   ├── migrate_engagement_ids.sh      # One-time migration to opaque IDs (dry run by default)
│   ├── extract_telemetry.py           # Telemetry extraction
│   └── ...
│
├── knowledge/                         # Consulting knowledge base
│   ├── README.md                      # Knowledge base overview
│   ├── principles/                    # Core consulting principles
│   ├── methodologies/                 # Structured consulting approaches
│   └── standards/                     # Quality criteria and benchmarks
│
├── agents/                            # Agent role definitions
│   ├── README.md                      # Agent system overview
│   ├── definitions/                   # Agent roles and responsibilities
│   │   ├── orchestrator.md            # Orchestrator agent role
│   │   ├── discovery.md               # Discovery agent role
│   │   ├── capability.md              # Capability assessment agent role
│   │   ├── roi.md                     # ROI modeling agent role
│   │   ├── roadmap.md                 # Roadmap agent role
│   │   └── assembly.md                # Output assembly agent role
│   └── instructions/                  # Detailed agent operating instructions
│
├── templates/                         # Input contracts & output templates
│   ├── README.md                      # Templates overview
│   ├── client_profile.md              # Template for CLIENT_PROFILE.md
│   ├── inputs/                        # Input data contracts
│   │   ├── engagement_intake.md       # Engagement intake form (with client reference)
│   │   ├── discovery_input_contract.md
│   │   ├── financial_data_schema.md
│   │   └── transcript_interpretation_guide.md
│   └── outputs/                       # Deliverable templates
│       ├── engagement_journal.md      # Journal template (with cross-engagement awareness)
│       ├── executive_summary.md
│       ├── assessment_report.md
│       ├── capability_assessment.md
│       ├── roi_report.md
│       └── roadmap.md
│
└── examples/                          # Reference engagements
    ├── README.md                      # Examples overview
    ├── engagements/                   # Complete engagement examples
    └── test_runs/                     # Test engagement runs
```

## Component Purposes

### /engagements/ - Client → Engagement Hierarchy

The primary working directory for all engagement work. Organized as a two-level hierarchy:

**Level 1: Engagement ID** (`engagements/[opaque_id]/`)
- One opaque, randomly generated directory per engagement (e.g. `engagements/e7f3a2c1/`)
- Contains `CLIENT_PROFILE.md` — persistent memory, carried forward into each new engagement for the same client
- Tracks strategic context, tech landscape, relationship history, cumulative insights

**Level 2: Engagement** (`engagements/[opaque_id]/[YYYY-MM_domain_type]/`)
- Naming convention: `YYYY-MM_domain_type` (e.g., `2026-01_investing_assessment`, `2026-03_retail_ignite`)
- Contains inputs/, outputs/, journal, and session ID
- Everything *inside* an engagement directory is unchanged — only the top-level name is opaque

**Why the top level is an opaque ID:**
`scripts/orchestrate.py`'s `compose_prompt` renders `engagement_dir` into every agent invocation as a value, and `run_agent` sets `cwd` to it. A directory named after the client therefore tells the model who the client is on every single call, no matter how well the file contents are scrubbed. The ID → client binding lives only in `.engagement_map.json` (repo root, chmod 600, gitignored) and never leaves the machine. See `.design/solution-design-v6.md` D6.

**You never type an ID.** `./scripts/find_engagement.sh <client>` resolves a client name — partial and case-insensitive — to its engagement path(s).

**Why the hierarchy:**
A single bank often has multiple engagements across different domains (retail, wealth, investing) and different types (assessment, ignite, hybrid). Each gets its own ID — deliberately, so one ID never becomes a stable pseudonym for a client across months of unrelated work. `CLIENT_PROFILE.md` is what carries context between them:
- Prior discovery insights carry forward (don't re-discover known context)
- Cross-engagement patterns surface (themes visible only when comparing across domains)
- Relationship history accumulates (stakeholder contacts, communication styles)

`CLIENT_PROFILE.md` also carries the client's written identifier forms, which is what keeps the client's name on the deny-list now that the directory name no longer supplies it.

**Bootstrap:** `./scripts/init_engagement.sh navy_federal 2026-02_retail_assessment assessment`
**Find:** `./scripts/find_engagement.sh navy_federal`
**Migrate existing client-named directories (one time, dry run by default):** `./scripts/migrate_engagement_ids.sh`

### /knowledge/ - Consulting Knowledge Base

Contains the foundational consulting knowledge that powers all agent behavior and output generation.

**Purpose:**
- Define consulting principles and mindsets
- Document methodologies for discovery, assessment, ROI, and roadmapping
- Establish quality standards for outputs
- Provide reference material for agents

**Who uses it:**
- Agents reference this to understand how to perform their work
- Consultants reference this to understand standards
- Quality reviewers use this to validate outputs

### /agents/ - Agent Definitions

Defines the specialized agents that perform consulting work.

**Current Agents:**

1. **Orchestrator Agent** - Routes requests, coordinates agents, assembles final outputs
2. **Discovery Agent** - Interprets transcripts, extracts business context and pain points
3. **Capability Assessment Agent** - Evaluates maturity, identifies gaps, prioritizes improvements
4. **ROI Agent** - Builds financial models, quantifies value, runs sensitivity analysis
5. **Roadmap Agent** - Sequences initiatives, maps dependencies, plans resources
6. **Assembly Agent** - Creates executive summaries and packages deliverables

**Structure:**
- `/definitions/` - High-level role descriptions (WHAT each agent does)
- `/instructions/` - Detailed operating procedures (HOW each agent works)

### /templates/ - Contracts & Templates

Standardized structures for inputs and outputs.

**Input Templates:**
- Define what data is required for each type of analysis
- Specify format and quality standards
- Provide guidance for handling missing data

**Output Templates:**
- Ensure consistency across all deliverables
- Include all required sections
- Follow Value Consulting standards
- Provide executive-ready formatting

**Key Templates:**
- `discovery_input_contract.md` - What data discovery needs
- `financial_data_schema.md` - Financial data structure and requirements
- `transcript_interpretation_guide.md` - How to extract insight from interviews
- `executive_summary.md` - Executive summary structure
- `assessment_report.md` - Capability assessment deliverable
- `capability_assessment.md` - Detailed capability maturity assessment
- `roi_report.md` - Complete ROI business case
- `roadmap.md` - Strategic initiative roadmap

### /examples/ - Reference Engagements

Complete examples of consulting engagements showing inputs, analysis, and outputs.

**Purpose:**
- Demonstrate methodology in practice
- Show quality standards
- Provide training material
- Illustrate handling of real-world complexity

**Future Examples:**
- Digital transformation assessments
- Platform modernization business cases
- Capability maturity assessments
- Strategic roadmap development

## Information Flow

### Typical Engagement Flow

1. **Inputs Received** (transcripts, financial data, context)
   ↓
2. **Orchestrator Agent** routes to appropriate agents
   ↓
3. **Discovery Agent** extracts business context and pain points
   ↓
4. **Capability Agent** assesses maturity and identifies gaps
   ↓
5. **ROI Agent** models financial impact and builds business case
   ↓
6. **Roadmap Agent** sequences initiatives and plans resources
   ↓
7. **Assembly Agent** packages executive-ready deliverables
   ↓
8. **Final Outputs** delivered to client

### Knowledge References

Each agent references:
- `/knowledge/principles/` - For consulting philosophy
- `/knowledge/methodologies/` - For specific approaches
- `/knowledge/standards/` - For quality criteria
- `/templates/inputs/` - For input requirements
- `/templates/outputs/` - For output structure

## Design Principles

### 1. Separation of Concerns

- **Context** (knowledge) vs. **Execution** (agents) vs. **Structure** (templates)
- Knowledge is agent-agnostic (applies to all)
- Agents are specialized (focused responsibilities)
- Templates are standardized (consistency)

### 2. Transparency

- All methodology visible
- All standards documented
- All assumptions explicit
- All reasoning traceable

### 3. Consulting-First

- Focus on generating deliverables, not documentation
- Written for consultants, not developers
- Standards match real consulting practice
- Output quality matches senior consultant work

### 4. Evidence-Based

- All claims require evidence
- Assumptions are explicit and conservative
- Data gaps are documented
- Sources are cited

### 5. Executive-Ready

- All outputs written for C-level audience
- Clear, concise, jargon-free
- Action-oriented
- Decision-focused

## File Naming Conventions

- Use lowercase with underscores: `file_name.md`
- Be descriptive: `discovery_input_contract.md` not `input1.md`
- Group related files with common prefixes
- Use markdown (.md) for all documentation

## Adding New Components

### Adding a New Agent

1. Create `/agents/definitions/[agent-name].md` with role definition
2. Create `/agents/instructions/[agent-name]_instructions.md` with detailed procedures
3. Update `/agents/README.md` to list new agent
4. Reference relevant knowledge and templates
5. Define input/output contracts

### Adding New Templates

1. Create template in appropriate `/templates/inputs/` or `/templates/outputs/`
2. Follow existing template structure
3. Include all required sections from standards
4. Document any new sections in README
5. Provide example usage

### Adding New Knowledge

1. Create in appropriate `/knowledge/` subdirectory
2. Reference from agent definitions
3. Update `/knowledge/README.md`
4. Ensure consistency with existing principles

### Adding Examples

1. Create `/examples/engagements/[engagement-name]/`
2. Include complete inputs, analysis, and outputs
3. Document lessons learned
4. Update `/examples/README.md`

## Quality Standards

All components in this repository must:

1. **Follow Value Consulting principles** defined in README.md
2. **Be consultant-readable** (plain English, not code)
3. **Be actionable** (clear, specific, usable)
4. **Be evidence-based** (cite sources, show methodology)
5. **Be complete** (all required sections present)
6. **Be consistent** (follow established patterns)

## Next Steps for Repository Development

### Immediate Priorities

1. **Populate `/knowledge/` subdirectories**
   - Create specific methodology guides
   - Document quality standards
   - Define maturity frameworks

2. **Create agent instructions**
   - Detailed step-by-step procedures
   - Decision trees and logic
   - Error handling approaches

3. **Build example engagements**
   - End-to-end example with real outputs
   - Demonstrate methodology in practice
   - Show handling of edge cases

### Future Enhancements

- Industry-specific knowledge modules
- Additional agent types for specialized analyses
- Integration with actual data sources
- Automated quality validation
- Output formatting tools

## Getting Started

### For Consultants Using This System

1. Read [README.md](README.md) - Understand Value Consulting philosophy
2. Read [CLAUDE.md](CLAUDE.md) - Understand Claude's role
3. Review `/templates/inputs/` - Understand what data is needed
4. Review `/templates/outputs/` - Understand what outputs will be generated
5. Provide inputs and request deliverables

### For Agent Developers

1. Read [README.md](README.md) - Understand consulting standards
2. Review `/agents/definitions/` - Understand agent roles
3. Reference `/knowledge/` - Understand methodology
4. Use `/templates/` - Follow structured formats
5. Review `/examples/` - Learn from reference work

### For Quality Reviewers

1. Validate against `/knowledge/standards/`
2. Check completeness against templates
3. Verify assumptions are documented
4. Confirm evidence is cited
5. Ensure executive-readiness

---

**This repository is a living system. As methodology evolves and new patterns emerge, this structure will be updated to reflect best practices in Value Consulting.**
