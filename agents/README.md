# Agent Definitions

This directory defines the roles, responsibilities, and operating instructions for each agent in the Value Consulting system.

## Agent Overview

| Agent | File | Purpose |
|-------|------|---------|
| **Orchestrator** | `orchestrator.md` | Central coordinator, determines engagement type, routes work |
| **Discovery** | `discovery.md` | Extracts context, validates hypotheses, manages evidence |
| **Persona & Use Case** | `persona-usecase.md` | Develops personas, creates use cases (current/future/agentic) |
| **Capability** | `capability.md` | Assesses maturity, identifies gaps, scores capabilities |
| **ROI** | `roi.md` | Builds financial models, quantifies value |
| **Roadmap** | `roadmap.md` | Prioritizes by value/feasibility/CX, sequences initiatives |
| **Assembly** | `assembly.md` | Creates executive deliverables (Assessment or Innovation Day) |

## Agent Flow by Engagement Type

### Ignite Light (Strategic Workshop)
```
Orchestrator → Discovery (Workshop) → Persona/UseCase → Capability (Light) → Roadmap → Assembly (Innovation Day)
```

### Detailed Assessment (Full Analysis)
```
Orchestrator → Discovery (Deep Dive) → Persona/UseCase → Capability (Full) → ROI → Roadmap → Assembly (Assessment Report)
```

## Structure

### `/definitions/`
High-level agent role definitions, responsibilities, and capabilities.

**Contents:**
- Orchestrator Agent - Central coordinator and router
- Discovery Agent - Context extraction and hypothesis validation
- Persona & Use Case Agent - Persona research and use case development
- Capability Assessment Agent - Maturity and gap analysis
- ROI & Financial Modeling Agent - Business case and value quantification
- Roadmap & Prioritization Agent - Initiative sequencing with prioritization framework
- Executive Summary & Output Assembly Agent - Deliverable generation

### `/instructions/`
Detailed operating instructions for each agent, including:
- Input requirements and contracts
- Processing methodology
- Output format and standards
- Handoff protocols to other agents
- Error handling and edge cases

## Agent Design Philosophy

Agents are designed to:
- **Focus on specific consulting tasks** (discovery, assessment, ROI, roadmap)
- **Operate with transparency** (show reasoning, document assumptions)
- **Follow Value Consulting principles** (outcome-led, evidence-based)
- **Produce executive-ready outputs** (clear, actionable, defensible)
- **Handle missing data professionally** (document assumptions, flag for validation)

Agents are NOT:
- Black boxes
- Code generators
- Vendor solution recommenders
- Optimistic estimators

## Agent Interaction

The Orchestrator Agent coordinates the flow:
1. Routes requests to appropriate agents
2. Manages dependencies between agents
3. Ensures output consistency
4. Validates quality standards
5. Assembles final deliverables

All agents communicate through structured inputs/outputs defined in `/templates/`.
