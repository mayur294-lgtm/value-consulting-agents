# Implementer Prompt Template

Use this template when `/bb-build` dispatches an implementer subagent for a ticket.

## Prompt

> ## Implement: [TICKET TITLE]
>
> ### Ticket
> [Paste full ticket body — objective, context, requirements, acceptance criteria, constraints, dependencies]
>
> ### Context
> This is ticket [N] of [TOTAL] in the build sequence. Previous tickets already completed: [list titles]. The codebase reflects all prior work.
>
> ### The ticket is the spec
> Implement the ticket exactly as written — it is the approved plan. Do not re-design, re-scope, or re-confirm it. Start immediately. Stop only if faithful execution is *impossible*: a file, symbol, or dependency the ticket references does not exist, or two requirements directly contradict — then report NEEDS_CONTEXT with the specific blocker. A question whose answer is "yes, as the ticket says" is noise; don't ask it.
>
> ### Coding Standards
>
> {{coding_standards}}
>
> If coding standards are provided above, follow them. They reflect the participant's own conventions. If the slot is empty, follow existing codebase patterns only.
>
> ### Design Guide
>
> {{design_guide}}
>
> If a design guide is provided above, this ticket touches a visual deliverable (HTML dashboard/deck, PPTX, or output template) — follow it so the output stays on the Frontline-2026 design system. If the slot is empty, this ticket only touches agent prompts, pipeline code, or rubrics with no visual output; ignore this section.
>
> ### Your Job
> You are editing a cortex component — an agent definition (`.claude/agents/*.md`), a skill (`.claude/skills/*/SKILL.md`), a slash command (`.claude/commands/*.md`), an output template (`templates/**`, `presentations/**`), or rubric/eval code. There is no TypeScript/`.tsx` source, no `package.json`, no `tsc`/`pnpm`.
> 1. **Implement** the ticket spec exactly — edit the agent / skill / command / template / rubric as specified. Follow existing component patterns and any coding standards above.
> 2. **Author eval cases** if the ticket adds or changes a component's expected behaviour (and especially for a NEW component): add/adjust the relevant cases and thresholds in `evals/registry.yaml` per the ticket's Eval Acceptance Criteria.
> 3. **Verify** — run the verification commands from the acceptance criteria: `python scripts/test_agent.py` (structural) and `python evals/run_experiment.py --component <component> --altitude unit` (and `--altitude deliverable-structural` where the ticket touches a chained agent).
> 4. **Commit** — granular commits per logical unit. Good commit messages, conventional-commits style. End every commit message with the trailer:
>    `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
>    - If a commit fails (pre-commit hook, governance hook, anonymize-guard), fix the issue and retry ONCE. If the second commit also fails, report BLOCKED with the exact error. Do not retry further.
> 5. **Self-review** — before reporting, review your own work:
>    - Did you implement everything in Requirements?
>    - Did you meet all Acceptance Criteria?
>    - Did you respect all Constraints?
>    - Did you overbuild anything not requested?
> 6. **Report** your status:
>    - **DONE** — all requirements met, tests pass, self-review clean
>    - **DONE_WITH_CONCERNS** — implemented but [specific concerns]
>    - **NEEDS_CONTEXT** — need clarification on [specific question]
>    - **BLOCKED** — cannot proceed because [specific blocker]

## Model Selection

- **S** (small) → sonnet
- **M** (medium) → sonnet
- **L** (large) → inherit (Opus)

## Handling Results

- **DONE** → proceed to spec review
- **DONE_WITH_CONCERNS** → assess concerns, then proceed to spec review
- **NEEDS_CONTEXT** → provide context, re-dispatch same model
- **BLOCKED** → provide more context, escalate model, break ticket down, or escalate to user
