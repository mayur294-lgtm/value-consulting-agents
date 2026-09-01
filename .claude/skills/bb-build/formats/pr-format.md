# PR Description Template

Use this template when `/bb-build` creates a pull request. Optimized for AI review.

## Template

```markdown
## Summary
[1-3 sentences: what was built and why]

## Tickets
- Closes #[number] — [title]
- Closes #[number] — [title]
- Closes #[number] — [title]

## Approach
[Brief strategy: what pattern was followed, key decisions made]

## Focus Areas
[Where reviewers should pay close attention]
- Security: [specific areas]
- Edge cases: [specific scenarios]
- Integration: [how new code connects to existing]

## Risk Flags
- [ ] Breaking changes: [yes/no, details]
- [ ] Migration needed: [yes/no, details]
- [ ] Affects existing behavior: [yes/no, details]

## Skip List
[What reviewers should NOT flag]
- Generated files: [list if any]
- Lock files
- Formatting-only changes

## CI Coverage
[What automated checks already handle]
- Structural agent checks (`scripts/test_agent.py` against `tests/quality_metrics.yaml`)
- Eval harness (`evals/run_experiment.py` — unit + deliverable-structural altitudes via Langfuse)
- Governance hooks (anonymize-guard, checkpoint, journal)

## Testing
- [What was tested]
- [What wasn't tested and why]
```

## Sizing Rules

- **≤ 400 lines** → single PR
- **> 400 lines** → split into stacked PRs at epic/feature boundaries
- Each PR should be independently reviewable

## Why This Structure

- Linked tickets help reviewers understand intent
- Focus areas prevent wasted time on low-risk code
- CI coverage declaration reduces false positives (5-15% industry rate)
- Skip list prevents noise on generated/vendored code
- Risk flags help reviewers prioritize
