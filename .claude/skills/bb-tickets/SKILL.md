---
name: bb-tickets
description: "Turn an approved PRD and design spec into AI-ready GitHub Issues with implementation detail. Use when participant has an approved PRD and design spec, says 'break this down', 'create issues', 'make tickets', 'turn this into tasks', or is ready to move from design to engineering breakdown."
argument-hint: "Path to PRD or design spec (optional — auto-detects most recent)"
---

Pipeline: /bb-prd → /bb-design → /bb-tickets → /bb-build → /bb-pr-review → /bb-refine
                                  ^^^ YOU ARE HERE ^^^

# /bb-tickets — Design Spec to GitHub Issues

You are turning an approved PRD and design spec into actionable, AI-ready GitHub Issues. You work through six phases: prerequisites, codebase re-exploration, decomposition, issue creation, build ordering, and PRD status update. You are mostly autonomous — one approval gate before creating issues.

> **Trust the spec.** The PRD and design spec are the approved plan — turn them into tickets as written. Don't re-open settled decisions or re-ask things the participant already agreed. If something genuinely doesn't add up, flag it; otherwise keep moving.

**Initial request:** $ARGUMENTS

---

## Phase 0: Prerequisites

**Goal:** Find and confirm the PRD, ensure it's committed.

1. **Find the PRD:**
   - If `$ARGUMENTS` contains a path, use that.
   - Otherwise, check `.prd/` for the most recently modified `.md` file.
   - Confirm with the user: "I found `.prd/prd-v1.md` — is this the one?"

2. **Check git status:**
   - Is the PRD committed? Run `git status` to check.
   - If uncommitted: commit it. PRDs need version history before tickets reference them.
     ```
     git add .prd/prd-v{N}.md
     git commit -m "docs: add PRD for {feature name}"
     ```

3. **Check GitHub remote:**
   - Run `git remote get-url origin` to check if a GitHub remote exists.
   - If no remote:
     - Ask the participant for a repo name (suggest the project folder name).
     - Create the repo: `gh repo create {name} --private --source=. --push`
     - Tell the participant: "I've created a GitHub repository for your project."
   - If remote exists, continue.

4. **Read and parse the PRD and design specs.** Identify:
   - Core features/epics to decompose
   - UX flows and component states from `.design/ux-design-v{N}.md` (if present)
   - Architecture decisions, component structure, and integration points from `.design/solution-design-v{N}.md` (if present — use it as the primary source of implementation detail)
   - Scope boundaries (what's in, what's out)
   - Success metrics (tickets must cover these)

   To find the latest version, check `.design/` for the highest-numbered `ux-design-v*.md` and `solution-design-v*.md` files. Read both — they are complementary halves of the design output.

   If neither design spec exists in `.design/`, proceed with the PRD alone — but note to the participant: "No design specs found. Running `/bb-design` first gives better ticket detail — architecture and UX flows are already worked out. Continuing with the PRD only."

---

## Phase 1: Codebase Re-exploration

**Goal:** Get fresh codebase context. The PRD may have been written days ago — the code may have changed.

**No gate — this phase is autonomous.**

**If `/bb-prd` just ran in this same session, reuse its findings** — you already hold its codebase map in this conversation; skip re-dispatching explorers and go straight to comparing against the PRD. The code can't have changed since planning moments ago.

1. Otherwise, launch 2-3 `codebase-explorer` agents (sonnet, parallel). Use the prompt template from `.claude/skills/bb-tickets/prompts/explorer-prompt.md` — focus agents on areas the PRD touches.

2. Read key files the agents identified.
3. Compare exploration findings against the design spec's component structure and integration points:
   - **Consistent** → proceed silently.
   - **Contradiction** → flag to user. The design spec has priority unless the code reveals an anti-pattern the spec didn't account for.

---

## Phase 2: Decomposition

**Goal:** Break the approved design into right-sized tickets. Architecture decisions are already locked in the design spec — don't re-open them here.

1. Launch `code-architect` agents (inherit, parallel). Each agent takes a different epic/feature from the PRD and design specs. Use the prompt template from `.claude/skills/bb-tickets/prompts/architect-prompt.md`. Pass the relevant sections of `solution-design-v{N}.md` (component structure, contracts, integration points) and `ux-design-v{N}.md` (user flows, error states) into the prompt so agents don't need to rediscover what's already been decided.

2. Read the agents' findings. Assemble the full breakdown.

3. **Decide structure based on size:**
   - **< 8 tickets** → flat structure. All issues at the same level, labels differentiate.
   - **8+ tickets** → hierarchical. Epic issues as parents, feature issues group tasks, task issues are atomic.

4. **Present the breakdown** to the user in a grouped format:

   ```
   ## Breakdown: [Feature Name] ([N] tickets)

   ### Epic: [Name] — [priority]

   **Feature: [Name]** — [priority]
   - [Ticket title] [complexity] — [priority]
   - [Ticket title] [complexity] — [priority]

   **Feature: [Name]** — [priority]
   - [Ticket title] [complexity] — [priority]
   ```

   Include key details: what each ticket covers, dependencies, and anything the user should know.

**Gate:**
The user must approve the breakdown before you create issues. Ask: "Ready to create these as GitHub Issues? Any changes first?"

---

## Phase 3: Create GitHub Issues

**Goal:** Create well-structured GitHub Issues with AI-ready content.

### Determine the repository

Check `git remote -v` to get the GitHub repository. Use the `gh` CLI for all GitHub operations.

### Create the labels this cycle introduces

The standing labels already exist on the repo and don't change between cycles — priority (`blocker`/`important`/`nice-to-have`/`low`), complexity (`S`/`M`/`L`), type (`bug`/`refactor`/`docs`), and `build-order`. Don't re-create or even list them: it's a round-trip per label that changes nothing on an established repo.

The only labels a cycle introduces are the hierarchy labels `epic:{name}` / `feature:{name}` and the version label `v{N}` when the version is new. Create just those, with a curated colour and description so they match the existing set (`--force` keeps a re-run idempotent):

```bash
gh label create "epic:checkout" --color 5319E7 --description "Epic: checkout flow" --force
gh label create "feature:cart"  --color FEF2C0 --description "Feature: cart"        --force
gh label create "v2"            --color 0E8A16 --description "V2 — Checkout & Cart" --force
```

Use the real epic/feature names and version from your breakdown; drop the `v{N}` line if that version label already exists.

### Create issues

For each ticket in the approved breakdown:

**Issue body format:** Use the template from `.claude/skills/bb-tickets/formats/ticket-format.md`.

**Issue creation order:**
1. Create milestone if the PRD warrants one.
2. Create epic issues first (if hierarchical).
3. Create feature issues, referencing epic.
4. Create task issues, referencing feature and adding dependency links.
5. Apply labels: priority + version + complexity (+ hierarchy labels if applicable).

**One issue per `gh issue create` call — never a generated script.** Create them one at a time in dependency order (parents before children). Read each new issue's number from the output and write it into the next ticket's body (`Blocked by #42`) — you carry the numbers between calls, not shell variables. Keep the creates sequential; concurrent ones trip GitHub's rate limit.

**Pass the body with `--body-file`, not a heredoc.** Issue bodies are markdown full of backticks and `$` — characters the shell executes inside a heredoc, breaking the command. Write each body to a temp file with the Write tool, then point `gh` at it:

```bash
gh issue create --title "Add login form" --body-file /tmp/ticket-login.md --label "feature:login,v1,M"
# prints the new issue URL, e.g. .../issues/42 — note the 42 for the next body
```

**STOP and report if a `gh issue create` prints no issue number** (gh failed or prompted for input). Never reference a parent issue that doesn't exist — if #9 fails, #1–8 already exist and you see exactly where it stopped, so report that instead of pressing on and writing `Blocked by #<missing>` into a child.

### Present summary

After all issues are created, present a grouped summary with URLs:

```
## Created: [Feature Name] ([N] tickets)

### Epic: [Name] (#[number])

**Feature: [Name] (#[number])** — [priority]
- #[number] [Title] [complexity] — [priority]
- #[number] [Title] [complexity] — [priority]

**Feature: [Name] (#[number])** — [priority]
- #[number] [Title] [complexity] — [priority]
```

---

## Phase 4: Build Order

**Goal:** Produce a build-order issue so /build knows the implementation sequence.

Using the code-architect findings (file paths, creates/consumes, dependencies, complexity) and the codebase context from Phase 1:

1. **Build the dependency graph.** For each ticket, map what it creates and what it consumes. Use the code-architects' Creates/Consumes fields.

2. **Sequence tickets.** Apply these rules in order:
   - HARD dependencies are inviolable — producer before consumer.
   - Foundational work (types, schemas, shared utilities) before features that use them.
   - Blockers before important before nice-to-have at the same dependency level.
   - Tickets touching the same files should be adjacent (reduces context switching).
   - SOFT dependencies prefer producer-first but can be reordered if it improves grouping.

3. **Group into PRs.** Group by coupling, not line count:
   - Tickets sharing a runtime boundary belong in the same PR.
   - Each PR must be independently reviewable and testable.
   - Note estimated line count per PR for reference, but do not use it as the grouping criterion.

4. **Write the Verify command.** Decide the exact eval/structural commands `/bb-build` runs at each step boundary so it never has to invent them. For cortex this is the three-part check: `python scripts/test_agent.py` (structural) + `python evals/run_experiment.py --component <component> --altitude unit` + `python evals/run_experiment.py --altitude pipeline`. Name the `<component>` per ticket. Note any deliverable-altitude eval deferred to publish.

5. **Decide scope as a decision, not an option.** State what to build outright — "Build all N. #X is stretch → build unless told otherwise." Leave no open question for `/bb-build` to re-ask.

6. **Create the build-order issue.**
   - Title: `Build Order: [feature/version]`
   - Labels: `build-order`, version label
   - Body format (sequential — one ticket at a time; no parallel waves):

   ```
   Build order for **Epic #[N]** ([feature/version]). Plan status: **APPROVED — authoritative.**

   ## Scope
   Build all [N] tickets. #[X] is stretch → build it unless told otherwise.   ← a DECISION, not an option

   ## Verify   (run exactly these at each step boundary — nothing else)
   python scripts/test_agent.py
   python evals/run_experiment.py --component [component] --altitude unit
   python evals/run_experiment.py --altitude pipeline
   # note any deliverable-altitude eval deferred to publish.

   ## Dependency Graph

   #[number] creates:
     - [file/pattern] ([description])

   #[number] consumes:
     - [file/pattern] (from #[source]) [HARD]
     - [pattern] (from #[source]) [SOFT]

   ## Build Sequence

   1. #[number] — [title] ([complexity], [priority]) — [one-line reasoning]
   2. #[number] — [title] ([complexity], [priority]) — [one-line reasoning]

   ## PR Grouping

   PR 1: #[number] + #[number]
     Coupling: [shared runtime boundary rationale]
     Independently reviewable: yes — [reason]

   ## Flags

   - [reorderable pairs, independent tickets, or other sequencing notes]
   ```

   - Pin the issue: `gh issue pin [number]`

No additional user gate — the user already approved the breakdown in Phase 2. The build order is a deterministic consequence of that breakdown.

**Dependency strength:**
- **HARD** — ticket B cannot compile/run without ticket A's output. Must be sequential.
- **SOFT** — ticket B works without ticket A's output, but is better/cleaner with it. Can be reordered if needed.

---

## PRD Status Update

After all issues are created and the build-order issue is pinned, update the PRD frontmatter from `status: draft` to `status: built`. Read the PRD file, replace `status: draft` with `status: built` in the YAML frontmatter, and write it back.

---

## Key Principles

- **One ticket = one independently verifiable change** = roughly one PR.
- **AI-ready content** — explicit file paths, verifiable criteria, verification commands. No business justification (that's in the PRD).
- **No CLAUDE.md duplication** — tickets contain only the delta specific to this task.
- **Acceptance criteria are testable**, not subjective.
- **Dependencies are explicit** — blocked-by and blocks references using issue numbers.
- **Complexity is AI resource cost** (S/M/L), never time estimates.
