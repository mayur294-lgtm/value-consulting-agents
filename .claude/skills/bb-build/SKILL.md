---
name: bb-build
description: "Implement GitHub Issue tickets sequentially with subagent execution, lightweight review, and PR creation. Use when participant has GitHub issues ready, says 'start coding', 'implement this', 'build the tickets', 'start building', or has open tickets that need implementation."
argument-hint: "Milestone, version label, or issue numbers (e.g. 'v4', '#203 #204 #205')"
---

Pipeline: /bb-prd → /bb-design → /bb-tickets → /bb-build → /bb-pr-review → /bb-refine
                                                ^^^ YOU ARE HERE ^^^

# /bb-build — Ticket Implementation

You are implementing GitHub Issue tickets. You look for a build-order artifact from the /bb-tickets phase (or generate a sequence yourself), implement tickets sequentially with subagents, run lightweight review after each ticket, and create PRs optimized for AI review.

You are mostly autonomous — one approval gate (build order) then continuous execution until done.

> **Trust the tickets.** They were already approved — implement them as written. Don't re-litigate scope or re-confirm decisions that are already made. If a ticket genuinely breaks against the real code, adjust and note why; otherwise keep moving.

**Initial request:** $ARGUMENTS

---

## Phase 1: Build Order

**Goal:** Fetch tickets and determine implementation sequence.

### 1. Identify tickets

Determine the GitHub repository from `git remote -v`. Use the `gh` CLI for all GitHub operations.

Based on `$ARGUMENTS`:
- **Version label** (e.g. "v4") → `gh issue list --label v4 --state open --json number,title,body,labels`
- **Milestone** → `gh issue list --milestone "..." --state open --json number,title,body,labels`
- **Issue numbers** (e.g. "#203 #204 #205") → fetch each with `gh issue view [number] --json number,title,body,labels`, batched into a single Bash invocation
- **Empty** → ask the user what to build

**Keep every ticket body you fetch here.** Phase 2 reuses these bodies verbatim when dispatching implementers — do NOT re-fetch each ticket from GitHub later.

### 2. Look for a build-order issue

Search for a build-order artifact from the /bb-tickets phase:

```
gh issue list --label build-order --label [version-or-milestone] --state open --json number,body --limit 1
```

**If found:**
- Parse the dependency graph, build sequence, and PR groupings from the issue body.
- Present to the user with the source noted: "Build order from /bb-tickets:"
- Gate: user approves or adjusts.

**If not found** (tickets created manually, different workflow):
- Read all ticket bodies (already fetched in step 1).
- Read the relevant codebase areas — file structure, key modules, types, schemas.
- Produce a sequence using the same rules as /bb-tickets Phase 4: HARD dependencies first, foundational work first, coupling-based PR grouping.
- Present to the user with the source noted: "Build order (generated — no /bb-tickets artifact found):"
- Gate: user approves or adjusts.

### 3. Present build order

Show the user the proposed sequence (from whichever source):

```
## Build Order: [label/milestone] ([N] tickets)

[Source: /bb-tickets artifact | generated]

1. #203 — [title] [S] blocker — [one-line reason]
2. #204 — [title] [M] blocker — [one-line reason]
3. #205 — [title] [S] important — [one-line reason]
...

PR groupings: #203-#205 (coupling: shared types), #206-#208 (coupling: API layer)
```

**Gate:** User approves or adjusts the build order. Ask: "Ready to build? Any changes to the order?"

---

## Phase 2: Execute

**Goal:** Implement each ticket sequentially with subagent execution and lightweight review.

**HARD RULE — You are the orchestrator, NOT the implementer.**

You MUST NOT edit component files, change agent/skill/command/template/rubric definitions, or run pipeline/eval commands (`python scripts/test_agent.py`, `python evals/run_experiment.py`, `python scripts/orchestrate.py`, etc.) yourself. All implementation work happens inside subagents. If you catch yourself about to use the Edit, Write, or Bash tool for implementation work — STOP. That work belongs to a subagent.

**The implementer edits cortex components, not application source.** A cortex "ticket" changes an agent definition (`.claude/agents/*.md`), a skill (`.claude/skills/*/SKILL.md`), a slash command (`.claude/commands/*.md`), an output template (`templates/**`, `presentations/**`), or rubric/eval code — never `.tsx`/TypeScript source. There is no `package.json`, `tsc`, or `pnpm` in this repo.

**Allowed tools during Phase 2:**

| Tool | Allowed | Purpose |
|------|---------|---------|
| Agent | YES | Dispatch implementer, spec reviewer, verify subagent |
| Bash (`git`, `gh`) | YES | Git operations, GitHub CLI, tracking line counts |
| Bash (pipeline/eval commands) | NO | `python scripts/test_agent.py`, `python evals/run_experiment.py`, etc. belong to the subagent |
| Read | YES | Reading subagent results, component files for prompt enrichment |
| Grep / Glob | YES | Repo queries to inform dispatch prompts |
| Edit / Write | NO | All file modifications happen inside subagents |

### Step 0: Create feature branch

Before the first ticket, create a feature branch:

1. Determine the branch name from the label, milestone, or ticket group name
2. `git checkout -b feat/[label-or-milestone]`

This happens once before the first ticket, not per-ticket.

For each ticket in the approved build order, execute this loop:

### Step 1: Prepare the dispatch prompt

Before dispatching, enrich the implementer prompt with codebase context:
1. Use the full ticket body **already fetched in Phase 1** (the `gh issue list` / `gh issue view --json ...,body,...` payload). Do NOT re-fetch it from GitHub — you already have it. (If tickets were identified interactively via the empty-arguments path, fetch their bodies once here.)
2. Read relevant codebase files the implementer will need (patterns, types, adjacent code)
3. Load the prompt template from `.claude/skills/bb-build/prompts/implementer-prompt.md`
4. Fill in: ticket content, sequence position, prior ticket titles, and relevant file contents
5. **Coding standards injection (once per build session):** Check if `~/.claude/skills/coding-standards/SKILL.md` exists. If it does, read the "Quick Reference — The Non-Negotiables" section, then select 2-3 relevant rule files from `~/.claude/skills/coding-standards/rules/` based on the ticket's areas (e.g., Python pipeline/scripts → `rules/general-quality.md` + `rules/naming-conventions.md`). Inject the Quick Reference plus the relevant rule content into the `{{coding_standards}}` slot in the implementer prompt. If no file exists, leave the slot empty. Do this check once at the start of Phase 2, not per-ticket.
6. **Design guide injection (deliverable-output tickets only):** If the ticket touches a visual deliverable output — an HTML dashboard/deck, PPTX builder, or output template (e.g. `templates/**`, `presentations/**`, `.html` generators) — read `.claude/skills/bb-build/prompts/design-guide.md` and inject its content into the `{{design_guide}}` slot of the implementer prompt. This keeps deliverables on the Frontline-2026 design system. For tickets that only touch agent prompts, pipeline code, or rubrics with no visual output, leave the slot empty.

The goal is to front-load everything into the prompt so the subagent has what it needs without reading dozens of files itself.

### Step 2: Dispatch implementer

You MUST call the Agent tool to dispatch the implementer. Select model based on ticket complexity:
- **S** (small) → `model: "sonnet"`
- **M** (medium) → `model: "sonnet"`
- **L** (large) → `model: "opus"` or omit (inherits Opus)

```
Agent tool call:
  description: "Implement #[number] [short title]"
  model: "sonnet" (or "opus" for L)
  prompt: [enriched implementer prompt]
```

Do NOT implement the ticket yourself. Do NOT "quickly do it" because it seems small. Every ticket gets a subagent.

### Step 3: Handle implementer result

- **DONE** → proceed to review
- **DONE_WITH_CONCERNS** → read the concerns, assess whether they matter, then proceed to review
- **NEEDS_CONTEXT** → provide the missing context from your knowledge of the PRD/codebase, re-dispatch the implementer via the Agent tool with the same model
- **BLOCKED** → assess the blocker:
  1. Can you provide more context? → re-dispatch via Agent tool with context
  2. Would a more capable model help? → re-dispatch via Agent tool with `model: "opus"`
  3. Should the ticket be broken down? → tell the user
  4. Is it a real blocker? → escalate to the user

### Step 4: Lightweight spec review

You MUST call the Agent tool to dispatch a spec reviewer (sonnet). Use the prompt template from `.claude/skills/bb-build/prompts/spec-reviewer-prompt.md`. Paste the ticket spec and implementer report into the Agent prompt.

### Step 5: Fix loop (if needed)

If spec review reports FAIL:
1. Re-dispatch the implementer via the Agent tool with the spec review feedback
2. Re-run the spec review via the Agent tool
3. Max 2 re-dispatches. If the implementer has been dispatched 3 times total for the same ticket (initial + 2 retries) and the spec review still fails, escalate to the user. Do not dispatch again.

### Step 6: Verify the ticket via the eval harness

After spec review passes and BEFORE closing the ticket, confirm the change is actually correct. In cortex, **verify = run the eval experiment**, not a build/typecheck. There is no `package.json`, `tsc`, or `pnpm` — quality is proven by the eval harness and the structural agent checks. You do NOT run the commands yourself — dispatch a subagent for it (the orchestrator-not-implementer rule still holds).

Cortex agents form a chain (Discovery → Block-A agents → Roadmap → Assembly → …), so a change to one component can break a downstream consumer. Verify therefore runs **three** checks, in order:

1. **Structural** — `python scripts/test_agent.py` validates the changed agent/knowledge/template against `tests/quality_metrics.yaml` ($0, no LLM).
2. **Unit experiment** — `python evals/run_experiment.py --component <changed-component> --altitude unit` scores the changed component against its rubric cases in `evals/registry.yaml` via Langfuse. `<changed-component>` is the agent/skill/command/template the ticket modified.
3. **Pipeline experiment** — `python evals/run_experiment.py --altitude pipeline` runs the end-to-end pipeline on a golden engagement and checks the change didn't break downstream consumers.

`run_experiment.py` exits non-zero when a score falls below its threshold, so a non-zero exit is a FAIL.

Determine `<changed-component>` from the ticket's target file(s) (e.g. a ticket editing `.claude/agents/roi-financial-modeler.md` → `--component roi-financial-modeler`). For a ticket that introduces a NEW component, the ticket should already have authored its eval cases (enforced by `/bb-prd`); if `evals/registry.yaml` has no cases for it, that is a FAIL — escalate.

Dispatch a **haiku** subagent to run all three:

```
Agent tool call:
  description: "Verify eval after #[number]"
  model: "haiku"
  prompt: "Run exactly these at the repo root, in order, and stop at the first failure:
    1. python scripts/test_agent.py
    2. python evals/run_experiment.py --component <changed-component> --altitude unit
    3. python evals/run_experiment.py --altitude pipeline
  On all three passing (exit 0 and at/above threshold), report PASS. On any failure, report FAIL, name which step failed, and paste that command's raw output verbatim — do not summarise, and do not fix anything."
```

A ticket is NOT done until **all three** pass: structural passes AND the unit experiment scores at/above its threshold AND the pipeline experiment is green.

Handle the result:
- **PASS** → proceed to Step 7.
- **FAIL** → re-dispatch the implementer via the Agent tool with the raw failure output (same dispatch as Step 2), then re-dispatch a single haiku verify subagent. Max 2 re-dispatches. If it still fails after the 2nd retry, escalate to the user. The ticket is not done until verify PASSes.

### Step 7: Mark done and track size

- Close the ticket on GitHub: `gh issue close [number] --comment "Implemented in [branch]"`
- Track cumulative lines changed: `git diff --stat main..HEAD`
- If cumulative lines > ~400 and there are remaining tickets: suggest a PR split point to the user

### Step 8: Cleanliness check

Before proceeding to the next ticket, verify the working tree is clean:

1. Run `git status --porcelain`
2. If clean → proceed to the next ticket
3. If dirty (uncommitted changes from failed or partial implementation) → run `git stash push -m "stash from #[number]"` and warn the user before continuing

### Between tickets

No gate — proceed to the next ticket automatically. Only pause if:
- An implementer is BLOCKED and you can't resolve it
- Cumulative lines suggest a PR split

---

## Phase 3: Create PR

**Goal:** Create a well-structured PR optimized for AI review.

### 1. Assess change size

Count total lines changed: `git diff --stat main..HEAD` (or the appropriate base branch).

- **≤ 400 lines** → single PR
- **> 400 lines** → split into stacked PRs at the boundaries from the build-order issue's PR groupings (coupling-based boundaries)

### 2. Create the PR (as a draft)

Push the feature branch and create the PR:

```bash
git push -u origin feat/[feature-name]
```

Create the PR as a **draft**. This is the merge gate: a draft PR cannot be merged on GitHub, so the full multi-agent review (`/bb-pr-review`) must run first. `/bb-pr-review` flips it to ready once it has reviewed.

Use `gh pr create --draft`, passing the body via `--body-file` (write the body to a temp file with the Write tool — a heredoc would let the shell execute backticks/`$` in the markdown). Follow the template from `.claude/skills/bb-build/formats/pr-format.md`.

Then tag the PR so `/bb-pr-review` can find it. Add exactly **one** label — `needs-review`. Create the label once if it doesn't exist yet:

```bash
gh label create needs-review --color FBCA04 --description "Ready for /pr-review" 2>/dev/null || true
gh pr edit [number] --add-label needs-review
```

Do NOT add any other cycle labels — `needs-review` is the only label this flow uses.

### 3. Present summary

```
## Built: [Feature Name]

**PR:** [URL] (draft — run /pr-review to unlock merge)
**Tickets closed:** #203, #204, #205
**Lines changed:** [N]

This PR is a draft — it can't be merged until /pr-review reviews it and flips it to ready.
Run /pr-review next — the full multi-agent review will catch anything the lightweight in-build reviews missed.
```

If stacked PRs were created, list all PR URLs with their ticket groupings, and apply the `needs-review` label to each.

### 4. Close build-order issue

If a build-order issue was used in Phase 1:
- If the actual build order matched the plan: close it with a comment linking to the PR(s).

  ```
  gh issue close [number] --comment "Build complete. PR(s): [URLs]"
  ```

- If the build deviated from the plan (reordered tickets, changed PR groupings): update the issue body with the actual order and a note explaining why, then close with a comment linking to the PR(s).

  ```
  gh issue edit [number] --body "[updated body with actual order and deviation notes]"
  gh issue close [number] --comment "Build complete (order deviated — see updated body). PR(s): [URLs]"
  ```

If no build-order issue was used (fallback sequencing), skip this step.

---

## Key Principles

- **You are the orchestrator** — you coordinate, you do not implement. Every ticket and every review gets a subagent via the Agent tool. No exceptions, no "just this small one."
- **Sequential execution** — tickets build on each other. No parallel implementation.
- **Fresh context per implementer** — each subagent gets a clean context window via the Agent tool. The orchestrator ensures the working tree is clean between tickets.
- **Prompt enrichment over file reading** — front-load codebase context into the Agent prompt. The subagent should rarely need to explore the codebase itself.
- **Spec compliance between tickets** — catch missing requirements before the next ticket builds on top. The full quality review happens against the PR.
- **Verify before closing** — each ticket runs the eval harness (`python scripts/test_agent.py` structural + `python evals/run_experiment.py --component <component> --altitude unit` + `python evals/run_experiment.py --altitude pipeline`) inside a cheap subagent before it's marked done. A ticket whose change fails structural, scores below its unit threshold, or breaks the pipeline isn't done.
- **Autonomous between tickets** — don't ask the user between every ticket. Only pause for blockers or PR splits.
- **Escalate, don't guess** — if an implementer is stuck, escalate rather than proceeding with uncertainty.
- **Size-aware PRs** — split at ~400 lines for reviewability.
- **Draft until reviewed** — the PR ships as a draft with a `needs-review` label. It can't be merged until `/bb-pr-review` reviews it and flips it to ready.
