---
name: reconcile
description: "Check all open PRs/branches for conflicts, auto-merge clean ones, and resolve conflicts intelligently."
---

You are executing the `/reconcile` skill. This is the "git janitor" — it keeps the repository clean so consultants never deal with merge conflicts. Follow these steps exactly.

## Step 1: Survey Open PRs

Run these commands to understand the current state:

```
gh pr list --state open --json number,title,author,headRefName,mergeable,updatedAt,reviews
git fetch --all --prune
```

List all open PRs with their status. Present a summary table to the user:

| # | Title | Author | Branch | Mergeable | Last Updated | Reviews |
|---|-------|--------|--------|-----------|--------------|---------|

## Step 2: Classify Each PR

For each open PR, classify it:

- **GREEN — Auto-mergeable:** `mergeable=MERGEABLE` AND has at least 1 approval → can be merged
- **YELLOW — Clean but needs review:** `mergeable=MERGEABLE` but no approvals yet → skip, just report
- **RED — Conflicts:** `mergeable=CONFLICTING` → needs resolution
- **STALE — Old branch:** not updated in >7 days → suggest closing or rebasing

## Step 3: Handle GREEN PRs

For each GREEN PR (mergeable + approved), ask the user:

> "PR #{number} '{title}' by {author} is approved and conflict-free. Merge it to main?"

If the user confirms, merge with:
```
gh pr merge {number} --squash --delete-branch
```

Use `--squash` to keep main history clean. Delete the branch after merge.

## Step 4: Handle RED PRs (Conflicts)

For each RED PR (conflicting), do the following:

1. **Identify the conflict:** Check out the branch locally and attempt a merge:
   ```
   git checkout {branch-name}
   git fetch origin main
   git merge origin/main --no-commit --no-ff
   ```

2. **Analyze conflict files:** Look at which files conflict using `git diff --name-only --diff-filter=U`

3. **For each conflicting file, determine resolution strategy:**

   | File Type | Strategy |
   |-----------|----------|
   | Agent definitions (`.claude/agents/*.md`) | **Manual merge required** — these are sensitive prompt files. Show both versions side-by-side and ask the user which sections to keep. Never auto-resolve agent prompts. |
   | Knowledge files (`knowledge/**/*.md`) | **Additive merge** — if both sides added content to different sections, keep both. If same section was edited, show the diff and ask. |
   | Skills/commands (`.claude/commands/*.md`) | **Manual merge required** — show diff, ask user. |
   | Templates (`templates/**`) | **Manual merge required** — show diff, ask user. |
   | Tools (`tools/**/*.py`) | **Manual merge required** — code conflicts are dangerous. Show diff, ask user. |
   | Config files (`.json`, `.yaml`) | **Smart merge** — usually safe to combine if different keys were changed. Show diff if same keys conflict. |
   | CLAUDE.md | **Manual merge required** — always ask user for root config changes. |

4. **After resolving all conflicts:** Commit the resolution and push:
   ```
   git add {resolved-files}
   git commit -m "reconcile: merge main into {branch-name} — resolved conflicts in {file-list}"
   git push origin {branch-name}
   ```

5. **Verify:** Run `gh pr view {number} --json mergeable` to confirm the PR is now mergeable.

## Step 5: Handle STALE Branches

For branches not updated in >7 days with no PR:
```
git branch -r --sort=-committerdate --format='%(refname:short) %(committerdate:relative) %(authorname)'
```

Report stale branches and ask if the user wants to delete them.

## Step 6: Post-Reconciliation Report

Present a final summary:

```
## Reconciliation Complete

### Merged to main:
- PR #12 "add: investing domain knowledge" by jd ✓

### Conflicts resolved:
- PR #15 "fix: market researcher Module 1" — resolved 1 conflict in market-context-researcher.md ✓

### Needs review (no conflicts):
- PR #18 "add: workshop prep checklist" by ak — waiting for approval

### Stale (>7 days):
- branch "mk/old-experiment" — last updated 12 days ago — suggest delete

### Main branch status:
- {N} commits ahead of last tag
- All merged PRs' branches cleaned up
```

## Branch Ownership & Priority Rules

When two branches conflict on the same files, use these ownership rules to determine whose changes take priority:

| Domain | Priority Owner | Priority Period | Notes |
|--------|---------------|-----------------|-------|
| **Ignite Inspire** (workshop agents, workshop prep, ignite synthesizer) | **Shobhit** (shobhitonnet) | Ongoing | Shobhit's branch takes priority, then Mariam |
| **ROI** (roi-business-case-builder, ROI templates, Excel generator) | **Mariam** (mariamt-coder) | Until Feb 14, 2026 | Mariam owns ROI improvements through this date |
| **Infrastructure** (hooks, settings, CLAUDE.md, CI workflows) | **Mayur** (mayur294-lgtm) | Ongoing | Admin changes |

**How to apply:**
- When resolving conflicts between branches, the priority owner's version wins for files in their domain
- If both contributors are editing the SAME domain file, still show the diff and ask — ownership is a tiebreaker, not a blanket override
- After the priority period expires, revert to standard rules (show diff, ask user)

## Rules

- **NEVER force-push** to any branch
- **NEVER delete branches** without user confirmation
- **NEVER auto-resolve agent prompt conflicts** — always show the diff and ask
- **NEVER merge without approval** — GREEN classification requires at least 1 review
- **Always squash-merge** to keep main history clean
- If you encounter a situation you're unsure about, stop and ask the user. Don't guess.
- The goal is to make git invisible, not to make it dangerous.
