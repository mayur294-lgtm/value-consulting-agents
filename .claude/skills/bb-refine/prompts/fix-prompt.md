# Fix Dispatch Prompt Template

Use this template when `/bb-refine` dispatches an implementer subagent for a review finding.

## Prompt

> ## Fix: {FINDING TITLE}
>
> ### Finding
> **File:** {file_path}:{line_number}
> **Agent:** {agent_name} (confidence: {score}/100)
> **Description:** {finding description}
> **Suggested fix:** {suggested fix from review}
>
> ### Code Context
> {Paste the relevant code — the file content around the finding, enough for the implementer to understand the surrounding logic. Typically 20-40 lines centered on the finding.}
>
> ### Your Job
> This finding was already reviewed and scored — fix it, don't re-litigate whether it's real. You are editing a cortex component — an agent definition, skill, command, output template, or pipeline/rubric code — not TypeScript source.
> 1. **Read** the finding and understand what needs to change.
> 2. **Implement** the fix. Follow existing component patterns.
> 3. **Verify** — run the relevant checks if the finding suggests it: `python scripts/test_agent.py` (structural) and/or `python evals/run_experiment.py --component <component> --altitude unit`.
> 4. **Self-review** — before reporting:
>    - Did you fix the specific issue described?
>    - Did you avoid changing unrelated code?
>    - Did you introduce any new issues?
> 5. **Report** your status:
>    - **DONE** — fix applied, verified
>    - **DONE_WITH_CONCERNS** — fixed but {specific concern}
>    - **NEEDS_CONTEXT** — need clarification on {specific question}
>    - **BLOCKED** — cannot fix because {specific reason}

## Model Selection

Always sonnet. Review fixes are scoped and small.

## Handling Results

- **DONE** → proceed to next finding
- **DONE_WITH_CONCERNS** → assess concerns, note for user, proceed
- **NEEDS_CONTEXT** → provide context from the PR/codebase, re-dispatch
- **BLOCKED** → skip this finding, report to user as "could not auto-fix"
