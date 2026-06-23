# Code Architect Prompt Template

Use this template when dispatching `code-architect` agents. Launch one per epic/feature from the PRD.

## Prompt

> Design the implementation for [EPIC/FEATURE NAME].
>
> ### PRD Section
> [Paste the relevant PRD section content]
>
> ### Codebase Exploration Findings
> [Paste relevant findings from the codebase-explorer agents]
>
> ### Your Job
> Produce:
> - **Files to create/modify** with exact paths
> - **Creates** — new artefacts this ticket introduces (files, patterns, modules, schemas, types)
> - **Consumes** — artefacts this ticket depends on, each marked HARD (won't compile/run without) or SOFT (works without, better with), referencing the producing ticket
> - **Verifiable requirements** — concrete, testable statements
> - **Acceptance criteria** — Given/When/Then, edge cases, verification commands
> - **Constraints** — files/patterns NOT to modify
> - **Dependencies** between tickets
> - **Complexity estimate** — S (single agent context, few files), M (full session, multiple files), L (multiple sessions, many systems)
>
> Complexity indicates AI resource cost, not human time.

## Usage

Replace `[EPIC/FEATURE NAME]` and paste the relevant PRD section and exploration findings. Each agent gets one epic or feature — don't overload a single agent with the entire PRD.
