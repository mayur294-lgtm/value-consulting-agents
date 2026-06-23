# Review Finding Format

The `/bb-pr-review` skill posts findings as a top-level PR comment via `gh pr comment`. This is the format to parse:

## Example Review Comment

```markdown
### Code Review

Found 3 issues:

1. **[Critical]** Unhandled promise rejection in webhook handler — found by silent-failure-hunter

   https://github.com/owner/repo/blob/abc123/src/api/webhook.ts#L45-L52

2. **[Important]** Type assertion masks potential null — found by type-design-reviewer

   https://github.com/owner/repo/blob/abc123/src/lib/parser.ts#L23-L25

3. **[Important]** Dead code branch never executes — found by code-quality-reviewer

   https://github.com/owner/repo/blob/abc123/src/utils/validate.ts#L67-L72

---

Reviewed by: silent-failure-hunter, type-design-reviewer, code-quality-reviewer, code-simplifier
Confidence threshold: 65/100 user-facing, 80/100 internal
```

## Parsing Rules

1. Look for the most recent comment starting with `### Code Review`
2. Each finding is a numbered list item with:
   - Severity in brackets: `[Critical]` or `[Important]`
   - Description after the severity
   - Agent name after "found by"
   - GitHub permalink on the next line (extract file path and line range)
3. The permalink format: `https://github.com/{owner}/{repo}/blob/{sha}/{path}#L{start}-L{end}`
4. Extract from permalink: file path = `{path}`, line = `L{start}`

## Clean Review (No Findings)

```markdown
### Code Review

No issues found. Reviewed for: code quality, silent failures, type design, simplification.

Confidence threshold: 65/100 user-facing, 80/100 internal
```

If this format is found, report "Review was clean — nothing to fix."
