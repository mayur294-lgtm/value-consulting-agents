# Review Agent Dispatch Prompt

Template for dispatching specialist review agents. The main model fills in the bracketed sections.

---

## Review: [agent role]

### PR Context
- **PR:** #[number] — [title]
- **Repository:** [owner/repo]
- **Branch:** [head] → [base]
- **Description:** [PR summary — what was built and why]

### Changed Files
[List of files with change type: added/modified/deleted]

### Platform Context

{{platform_context}}

If no platform context is provided, skip this section.

### Diff
[The relevant portion of the diff for this agent's focus area. For focused agents like silent-failure-hunter, include only files with error handling. For broad agents like code-quality-reviewer, include the full diff.]

### Instructions
Review ONLY what the PR changed. Do not flag:
- Pre-existing issues on unchanged lines
- Issues the structural agent checks (`scripts/test_agent.py`) or the eval harness (`evals/run_experiment.py`) would catch
- Style or formatting preferences
- General observations that aren't actionable

For each finding, include:
- File path and line number
- Code snippet showing the issue
- Evidence explaining why this is a real issue
- Specific suggestion for fixing it

If no issues found, say so clearly.

---

The confidence-scoring rubric lives in `scoring-prompt.md` — it is dispatched as a separate scoring agent in `/bb-pr-review` Phase 4, not by these specialist agents.
