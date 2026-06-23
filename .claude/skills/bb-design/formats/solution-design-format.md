# Solution Design Spec Template

Use this template when writing the solution design artifact in Phase 3 of `/bb-design`. All sections are written based on what was agreed during Phase 2 (Solution Design).

---

## Frontmatter

```yaml
---
version: {N}
prd: prd-v{N}.md
status: draft
date: {YYYY-MM-DD}
author: {participant name}
previous: solution-design-v{N-1}.md
---
```

Set `previous: null` for the first design spec (v1).

---

## Component Structure

```
directory tree showing new and modified components
.claude/agents/
  feature-agent.md          — [what it does, model, inputs/outputs]
.claude/skills/
  feature-skill/SKILL.md    — [what it does]
templates/
  feature-template.html     — [deliverable scaffold]
scripts/
  feature_step.py           — [pipeline step]
evals/
  registry.yaml             — [cases added for this change]
```

Describe each new component: what it owns, what it depends on.

---

## Data & Contract Model

Input/output contracts and any structured data the change reads or writes:

```yaml
# Agent contract (frontmatter + I/O)
name: feature-agent
model: sonnet
inputs:
  - discovery output (engagement inputs/)
output:
  - feature artifact (engagement outputs/), shape described here
```

Include rationale for non-obvious contract choices.

---

## Agent / Pipeline Steps

For each agent invocation, pipeline step, skill, or command:

| Name | Type | Input | Output | Purpose |
| --- | --- | --- | --- | --- |
| `feature-agent` | agent | discovery output | feature artifact | Produce the feature analysis |
| `feature_step` | pipeline step | feature artifact | assembled section | Fold into the deliverable |

---

## Integration Points

Where this change connects to the rest of the system (note downstream consumers in the agent chain):

| Existing component / step | How it's touched | Risk |
| --- | --- | --- |
| ... | ... | Low / Medium / High |

---

## Technical Decisions

For each non-obvious decision made during design:

**Decision:** [what was decided]
**Alternatives considered:** [what else was considered]
**Rationale:** [why this choice]
**Trade-offs:** [what we're accepting]
