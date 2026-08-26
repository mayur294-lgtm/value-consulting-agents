# GitHub Issue Body Template

Use this template for every ticket created by `/bb-tickets`.

## Template

```markdown
## Objective
[One sentence: what to build and why]

## Context
- Relevant components: `.claude/agents/foo.md`, `templates/bar.html`, `scripts/baz.py`
- Current behavior: [what happens now]
- Expected behavior: [what should happen after]

## Requirements
- [ ] Concrete, verifiable requirement 1
- [ ] Concrete, verifiable requirement 2
- [ ] Concrete, verifiable requirement 3

## Acceptance Criteria
- Given [state], when [action], then [result]
- Edge case: [scenario] → [expected handling]
- Run `python scripts/test_agent.py` — structural checks pass
- Run `python evals/run_experiment.py --component [component] --altitude unit` — scores at/above threshold
- Run `python evals/run_experiment.py --altitude deliverable-structural` — green (no downstream output-contract regression; it does not run the pipeline)

## Eval Acceptance Criteria
- `evals/registry.yaml` cases that define "done": [case ids + thresholds]
- New component? Author fresh eval cases as part of this ticket.

## Constraints
- Do NOT modify: [off-limits files/directories]
- Must use: [specific patterns, libraries]
- Must follow: CLAUDE.md conventions

## Dependencies
- Blocked by: #[issue number]
- Blocks: #[issue number]
```

## Principles

- One ticket = one independently verifiable change = roughly one PR
- Include verification commands so the implementing agent can self-check
- No business justification (that's in the PRD)
- No CLAUDE.md duplication — tickets contain only the delta specific to this task
- Acceptance criteria are testable, not subjective
