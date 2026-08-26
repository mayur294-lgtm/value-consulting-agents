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

After spec review passes and BEFORE closing the ticket, confirm what actually got proven — no more, no less. In cortex, **verify = run the eval harness**, not a build/typecheck. There is no `package.json`, `tsc`, or `pnpm`. But the harness proves different things depending on what changed, and this step exists to say which, honestly, every time — a score always carries its tier. You do NOT run the commands yourself — dispatch a subagent for it (the orchestrator-not-implementer rule still holds).

**First, classify the changed component's tier.** `evals/registry.yaml`'s `components:` section currently holds two kinds of row, both still filed under the same `components:` key (re-filing the rubric-scoring ones into an explicit `rubric_calibration:` section is tracked separately and hasn't landed yet, so don't describe that split as already real):

- **Executable** — exactly four rows today: `mcp-query-guard`, `pii-anonymizer`, `run-experiment-runner`, `mutation-harness`. Each builds a fixture at runtime and runs real code against it. A green `--component <row>` here is real evidence about that code.
- **Rubric-calibration** — every other component row, including every `.claude/agents/*.md` prompt (market-context-researcher, roi-financial-modeler, discovery-transcript-interpreter, capability-assessment, roadmap-prioritization, narrative-assembler, journey-builder, benchmark-librarian, usecase-designer, workshop-preparation, knowledge-harvester, ignite-workshop-synthesizer, roi-hypothesis-builder, roi-excel-generator, and more). These score a **frozen golden fixture** in `evals/goldens/` that does not change when you edit the agent's prompt. A green here proves the rubric still accepts a well-formed artifact — **it is not evidence about the prompt you just edited.** (Measured: replacing the entire 45KB `market-context-researcher` prompt with one line of garbage still scored this row 1.000 PASS.)

**Branch A — the ticket changed a `.claude/agents/*.md` prompt, or any other component whose row is rubric-calibration (i.e. not one of the four executable names above): do NOT run `--component` on it and report that as verification.** There is no executable gate for this kind of change. Have the subagent run structural only (it's real evidence — it re-parses the file you actually changed, not a frozen golden), then stop and report the uncovered-prose message verbatim instead of a score:

> "No executable gate covers `.claude/agents/<name>.md`. A component-altitude score against a frozen golden does **not** verify a prompt change — it scores the rubric. Either run `evals/path1.py --agent <name>` locally (uses your Claude subscription, not an API key), or record in the PR that this change is unverified."

`evals/path1.py` requires `--agent <name> --input <golden-or-text>`. It is currently **orphaned** — nothing in CI or this build loop invokes it (wiring it in is tracked separately and hasn't landed), so the only way to actually exercise it today is to run it yourself, locally, outside the subagent. The ticket can still proceed to Step 7, but the PR body and the report to the user MUST say the prompt change is unverified by the automated gate (or paste the local path-1 output if you ran it) — never "verified."

**Branch B — the ticket changed a component whose row IS executable-tier, or touched an output template covered by the deliverable-structural contract check.** Dispatch a **haiku** subagent to run, in order, only the checks that apply, and require the tier to be reported alongside every score:

```
Agent tool call:
  description: "Verify eval after #[number]"
  model: "haiku"
  prompt: "Run exactly these at the repo root, in order, and stop at the first failure:
    1. python scripts/test_agent.py
    2. python evals/run_experiment.py --component <changed-component>
    3. python evals/run_experiment.py --mutate <changed-component>
  (Only if the ticket ALSO touched an output template or the cross-agent assembly
  contract — templates/**, presentations/**, or the assembler's output shape —
  add a 4th check:)
    4. python evals/run_experiment.py --altitude deliverable-structural
  For step 2, report the row's tier from registry.yaml alongside the score —
  'executable' or 'rubric-calibration' — never state a score without its tier.
  For step 4, report it plainly as a frozen-fixture structural lint: it does
  NOT run the pipeline and never invokes the changed agent, so a green there
  proves the downstream file-shape contract still holds, not that the changed
  component works. On all applicable steps passing, report PASS with each
  score + tier + (for step 2 on an executable row) 'exercised: <module> via
  <interpreter>'. On any failure, report FAIL, name which step failed, and
  paste that command's raw output verbatim — do not summarise, and do not fix
  anything."
```

Do not add `--altitude unit` to step 2 — `--component <row>` already runs at `unit` altitude implicitly, and `--altitude unit` passed on its own (without `--component`) does nothing and falls through to the help text.

`run_experiment.py` exits non-zero when a score falls below its threshold, so a non-zero exit is a FAIL. For a ticket that introduces a NEW executable-tier component, the ticket should already have authored its eval cases (enforced by `/bb-prd`); if `evals/registry.yaml` has no row for it, that is a FAIL — escalate.

A ticket is NOT done until every check that actually applies to it passes — but "done" is bounded by what those checks can see. An executable-tier PASS is real evidence about the code that changed. A rubric-calibration or deliverable-structural PASS is real evidence about the rubric or the downstream file contract, never a substitute for verifying the prompt itself.

Handle the result:
- **Branch A (uncovered prose)** → proceed to Step 7. The report to the user and the PR body state the change is unverified by the automated gate, and name the `evals/path1.py` alternative — never assert the prompt was verified.
- **Branch B, PASS** → proceed to Step 7, carrying forward the score, tier, and what was exercised.
- **Branch B, FAIL** → re-dispatch the implementer via the Agent tool with the raw failure output (same dispatch as Step 2), then re-dispatch a single haiku verify subagent. Max 2 re-dispatches. If it still fails after the 2nd retry, escalate to the user. The ticket is not done until verify PASSes.

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
- **Verify honestly, not reflexively** — each ticket runs whatever the eval harness can actually prove about it, inside a cheap subagent, before it's marked done: `python scripts/test_agent.py` (real structural check on the changed file) always, plus — only when the changed component is one of the four executable-tier rows (`mcp-query-guard`, `pii-anonymizer`, `run-experiment-runner`, `mutation-harness`) — `python evals/run_experiment.py --component <component>` and `--mutate <component>`. A ticket that only edited a `.claude/agents/*.md` prompt (or any other rubric-calibration row, scored against a frozen golden) gets no executable score to claim: the report states it's unverified by the automated gate and names the `evals/path1.py --agent <name>` alternative, instead of citing a frozen-golden score as proof the prompt was verified. A ticket whose change fails structural, fails an applicable executable-tier score or mutation proof, or breaks the downstream `deliverable-structural` file contracts isn't done.
- **Autonomous between tickets** — don't ask the user between every ticket. Only pause for blockers or PR splits.
- **Escalate, don't guess** — if an implementer is stuck, escalate rather than proceeding with uncertainty.
- **Size-aware PRs** — split at ~400 lines for reviewability.
- **Draft until reviewed** — the PR ships as a draft with a `needs-review` label. It can't be merged until `/bb-pr-review` reviews it and flips it to ready.
