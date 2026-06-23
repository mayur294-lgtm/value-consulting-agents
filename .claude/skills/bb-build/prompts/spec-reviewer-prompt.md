# Spec Compliance Review Prompt Template

Use this template when `/bb-build` dispatches a spec reviewer after implementation.

## Prompt

> ## Spec Compliance Review
>
> ### Ticket Spec
> [Paste full ticket body]
>
> ### Implementer Report
> [Paste implementer's status report]
>
> **CRITICAL: Do not trust the implementer's self-report.** Verify independently by reading the actual code.
>
> Check three things:
> 1. **Missing requirements** — Did they implement everything? Any requirements skipped or claimed but not built?
> 2. **Extra work** — Did they build things not requested? Over-engineer?
> 3. **Misunderstandings** — Did they interpret requirements differently than intended?
>
> Read the changed files. Compare against the ticket spec. Report:
> - **PASS** — code matches spec (brief confirmation)
> - **FAIL** — [specific issues with file:line references]

## Model

Always sonnet. This is a comparison task, not a judgment task.

## Fix Loop

If FAIL: re-dispatch the implementer with the review feedback, then re-run this review. Max 2 re-dispatches (3 total attempts including initial).
