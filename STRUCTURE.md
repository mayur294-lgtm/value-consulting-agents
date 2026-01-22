# Repository Structure

This document provides an overview of the complete folder structure and purpose of each component.

## Root Files

- **[README.md](README.md)** - Authoritative source defining Value Consulting philosophy, methodology, and standards
- **[CLAUDE.md](CLAUDE.md)** - Defines how Claude operates in this repository as a Value Consultant and output generator
- **STRUCTURE.md** - This file, explaining repository organization

## Directory Structure

```
claudevc/
├── README.md                          # Value Consulting philosophy & standards
├── CLAUDE.md                          # Claude's role and behavior in this repo
├── STRUCTURE.md                       # Repository structure overview
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
│   ├── inputs/                        # Input data contracts
│   │   ├── discovery_input_contract.md
│   │   ├── financial_data_schema.md
│   │   └── transcript_interpretation_guide.md
│   └── outputs/                       # Deliverable templates
│       ├── executive_summary.md
│       ├── assessment_report.md
│       ├── capability_assessment.md
│       ├── roi_report.md
│       └── roadmap.md
│
└── examples/                          # Reference engagements
    ├── README.md                      # Examples overview
    └── engagements/                   # Complete engagement examples
```

## Component Purposes

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
