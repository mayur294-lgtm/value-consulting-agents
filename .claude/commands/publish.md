---
name: publish
description: "Publish your changes — commits, pushes, and creates a PR to main. Consultants never need to know git."
---

You are executing the `/publish` skill. This makes git invisible to the consultant. Follow these steps exactly.

## Pre-flight Checks

1. Run `git status` in the project root to see what changed.
2. If there are NO changes (nothing modified, nothing untracked), tell the user "Nothing to publish — no changes detected." and stop.
3. Check the current branch with `git branch --show-current`.
   - If on `main` or `master`: create a new branch first using the naming convention `{username}/{date}-{short-description}`. Derive the short description from the files changed (e.g., `agent-market-researcher-fix`, `knowledge-investing-benchmarks`).
   - If already on a feature branch: continue on it.

## Stage and Commit

4. Review all changes with `git diff` and `git diff --cached` and `git status`.
5. Analyze what changed and group changes into logical commits. For each logical group:
   - Stage the relevant files by name (never use `git add -A` or `git add .`)
   - Write a clear commit message following the repo's convention: `{type}: {description}`
     - Types: `add` (new feature/file), `fix` (bug fix), `update` (enhancement), `refactor`, `docs`
   - Commit with `Co-Authored-By: Claude <noreply@anthropic.com>`
6. If all changes are closely related, a single commit is fine. Don't over-split.

## Push and Create PR

7. Push the branch: `git push -u origin {branch-name}`
8. Create a Pull Request using `gh pr create`:
   - Title: Short summary of ALL changes in the branch (under 70 chars)
   - Body: Use this format:
     ```
     ## What Changed
     - [Bullet list of changes, grouped by area]

     ## Why
     - [Brief explanation of the motivation]

     ## Files Changed
     - [List key files modified/added]

     ## Review Notes
     - [Any context a reviewer should know]

     ---
     Published with `/publish` by {consultant-name}
     ```

## Knowledge Harvest Check

9. Before creating the PR, check if this branch contains engagement output files:
   ```
   git diff --name-only origin/main...HEAD | grep -E "(evidence_register|capability_assessment|roi_report|assessment_report)"
   ```
   - **If engagement outputs ARE present:** Check if knowledge harvest entries also exist:
     ```
     git diff --name-only origin/main...HEAD | grep "knowledge/learnings/"
     ```
     - If `knowledge/learnings/` files are NOT in the diff → **STOP and warn the user:**
       > "This branch contains engagement outputs but no knowledge harvest entries. The orchestrator's Step 9 should have extracted learnings into `knowledge/learnings/`. Please run the knowledge harvest before publishing — just ask me to 'run knowledge harvest for this engagement'. Then try `/publish` again."
     - If `knowledge/learnings/` files ARE present → proceed (harvest was done)
   - **If no engagement outputs:** proceed normally (this is a non-engagement change)

## Conflict Check

10. After creating the PR, run `gh pr checks {pr-number}` to see if there are any CI issues.
11. Run `gh pr view {pr-number} --json mergeable` to check if the PR can be cleanly merged.
    - If `mergeable` is `CONFLICTING`: warn the user that there are conflicts with main, and suggest running `/reconcile` to resolve them.
    - If `mergeable` is `MERGEABLE`: tell the user the PR is clean and ready for review.

## Report to User

Tell the user:
- The PR URL (clickable)
- What was committed (brief summary)
- Whether it's clean or has conflicts
- Remind them: "A team member needs to approve before it merges to main."

**IMPORTANT:** Never force-push. Never push to main directly. Never skip the PR step. The whole point is that every change goes through a reviewable PR.
