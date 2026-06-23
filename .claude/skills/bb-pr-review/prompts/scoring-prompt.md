# Confidence Scoring Prompt

Used to score each finding after the specialist review agents return. Dispatched as a single scoring agent (see `/bb-pr-review` Phase 4).

## Score This Finding

**Finding from [agent name]:**
[finding text including file, line, evidence, suggestion]

**PR diff context:**
[relevant code snippet from the diff]

Score this finding 0-100 based on:
- Is the evidence specific (file, line, code snippet)? (+20)
- Is the issue in code the PR actually changed? (+20)
- Would a senior engineer flag this in review? (+20)
- Is this a real bug or just a preference? (+20 for real bug)
- Could CI catch this instead? (-20 if yes)

Score bands:
- **0** — false positive, doesn't hold up
- **25** — might be real, might be false positive
- **50** — real but minor, nitpick territory
- **75** — verified real, will impact functionality
- **100** — certain, confirmed with evidence

Return ONLY: `score: [0-100]` and one sentence explaining why.
