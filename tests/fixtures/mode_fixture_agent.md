---
name: mode-fixture-agent
description: Fixture agent for the orchestrate.py mode-composer self-test. NOT a real agent — never invoke in an engagement.
model: sonnet
color: gray
---

You are a fixture agent used only to exercise `parse_agent_modes()` and
`compose_prompt()` in `scripts/orchestrate.py`.

## Core Identity

Core identity marker: FIXTURE-CORE-IDENTITY.

## Modes
<!-- Parsed by scripts/orchestrate.py::parse_agent_modes().
     An invocation receives ONLY: core identity (everything above ## Modes)
     + its selected mode block. Other modes are stripped. -->

### Mode: standalone   <!-- default when no phase directive present -->
```yaml
inputs:
  required: []
  optional:
    - outputs/evidence_register.md
degraded: ask-inline
knowledge:
  - knowledge/domains/{domain}/benchmarks.md
outputs:
  - outputs/fixture_output.md
checkpoint: interactive
gates: []
```
Standalone prose marker: FIXTURE-STANDALONE-PROSE.

### Mode: pipeline
```yaml
params: [outputs_dir, domain]
inputs:
  required:
    - "{outputs_dir}/evidence_register.md"
degraded: refuse
knowledge:
  - knowledge/domains/{domain}/benchmarks.md
outputs:
  - "{outputs_dir}/fixture_output.md"
checkpoint: file
phases: single
gates: []
```
Pipeline prose marker: FIXTURE-PIPELINE-PROSE for domain {domain}.
