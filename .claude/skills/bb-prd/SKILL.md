---
name: bb-prd
description: "Create a PRD through guided discovery and codebase exploration. Use when participant has an idea for what to build, says 'I want to build', 'let's plan', 'I have a project idea', 'what's next' after orientation, or the instructor says 'start planning'. Also use when Claude detects the participant has completed orientation and is ready to start the dev track."
argument-hint: "Brief description of the feature (optional)"
---

Pipeline: /bb-prd → /bb-design → /bb-tickets → /bb-build → /bb-pr-review → /bb-refine
          ^^^ YOU ARE HERE ^^^

# /bb-prd — PRD Creation

You are a knowledgeable PA guiding the participant from a feature idea to a complete PRD. You work through four phases: initial understanding, codebase exploration, informed discovery, and PRD writing. Phase 0 handles project setup. You produce a product-focused PRD — problem, solution, scope, and success metrics. Architecture and UX design happen in the next step (`/bb-design`).

Follow the communication tone in `.claude/skills/bb-prd/prompts/tone.md`. Curious, encouraging, context-aware. You already know the project (you've read the files). Lead with what you know — don't make the participant re-explain things.

The PRD feeds into `/bb-design` for UX and solution design, which then feeds into `/bb-tickets` for engineering breakdown.

**Initial request:** $ARGUMENTS

---

## Phase 0: Project Setup

Before anything else, clean up from previous modules and ensure the project is ready.

### 0.0 Developer eval environment (MANDATORY — developers only)

The bb-* lifecycle uses evals as its verify gate, and the LLM-judges need an Anthropic
API key. This applies to **developers changing components** — never to people who only
run agents to generate outputs (they never reach this skill).

Check whether the developer's eval keys are configured:

```bash
grep -q '^ANTHROPIC_API_KEY=.' evals/.env 2>/dev/null && echo CONFIGURED || echo MISSING
```

If **MISSING**, STOP and prompt the developer before continuing:

> "You're starting development on cortex components, which runs through the eval gate.
> Run `bash evals/setup_dev.sh` once — it will prompt for **your own Anthropic API key**
> (for the LLM-judges) and seed the **shared Langfuse eval keys** (from the team). This
> is a one-time, developer-only setup; people who just run agents don't need it."

Do not proceed with the PRD until either `evals/.env` has `ANTHROPIC_API_KEY` or the
developer explicitly chooses to continue with judges skipped (deterministic checks only).

### 0.1 Previous plugin cleanup

Check if previous workshop plugins are still installed and remove them. This handles two paths:
- Fundamental participants: orientation → guided-build → here (both may be installed)
- Intermediate/advanced participants: orientation → here (guided-build was never installed, no-ops silently)

```bash
claude plugin uninstall orientation --scope user 2>/dev/null
claude plugin uninstall guided-build --scope user 2>/dev/null
```

If either was found and removed, tell the participant: "I've cleaned up the previous workshop plugins — you won't need them anymore. This plugin takes over from here."

If neither was found: proceed silently.

### 0.2 Project scan and context-aware opening

Before asking the first question, scan the project to understand where things stand. This is lightweight — a few file reads, not a full codebase exploration.

**Read:**
- `.prd/` directory — which PRDs exist, what status is each, what do they cover
- `.prd/backlog.md` (if present) — small issues parked by past reviews (see below)
- `README.md` — project identity and methodology
- `CLAUDE.md` — conventions, governance rules, contribution tiers
- Component layout — `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `templates/`, `presentations/`, `scripts/`, `evals/`

**Read the backlog:**

`.prd/backlog.md` is a notes file where past reviews parked small issues that weren't worth a full plan. It's plain notes, not a PRD — just a checklist of little findings. If it exists, glance at it AFTER you understand what the participant wants to build this cycle, then offer it as optional input:

> "Past reviews parked a few small issues in the backlog: [summarise the top 3-5 — e.g. '4 error handling gaps, 2 type safety tidy-ups']. Want to fold any of these into this cycle, or save them for later?"

For each item the participant chooses to address:
- Fold it into the Problem/Scope of the new draft (it becomes part of what you plan)
- Mark it done in `.prd/backlog.md` — change its `- [ ]` to `- [done v{N}]` so it isn't offered again next cycle

Leave the rest untouched — they're parked on purpose and stay available later. The backlog never triggers a cascade or version bump; it's just notes.

**If no backlog exists:** Proceed normally.

**Adapt the opening based on what you find:**

| State | Opening |
|-------|---------|
| Backlog has parked items | "Past reviews parked a few small issues — [summary]. Want to fold any in, or start fresh?" |
| Draft PRD exists | "You've already got a draft going (v{N}) — it covers [summary]. Let's finish that and get it built!" |
| Only built/archived PRDs, no draft | "Last time you planned [summary]. Ready for the next one?" |
| Components exist but no PRDs | "I can see you've got [system description] — agents, skills, pipeline. What are we planning next?" |
| Empty project | "What are you building?" |
| Participant's idea doesn't match existing project | Surface gently: "That sounds different from what's here — are we adding to this system or pivoting?" |

### 0.3 PRD lifecycle enforcement

Respect and enforce the PRD lifecycle: `draft → built → archived`.

**One-draft rule:**
- If a draft PRD already exists, do not create a new one. Encourage finishing it: "You've already got a draft — it's best not to have two at the same time. Let's finish this one and get it built!"
- If the participant explicitly wants to abandon the existing draft, allow it — set the old draft's status to `abandoned` and create a new one.

**Cascade on new draft:**
- When creating a new draft, flip all previous PRDs (`built`, `released`) to `archived`.
- Determine the correct version number from existing files in `.prd/`.

**Status transitions:**
- This command only ever creates PRDs with `status: draft`.
- Surface the current lifecycle state to the participant so they understand where they are.

### 0.4 Basic scaffolding

1. **Check `.prd/` folder.** If it doesn't exist, create it:
   - "I'm creating a `.prd/` folder — this is where your PRDs will live."
   - Explain the lifecycle briefly: "A PRD starts as a **draft**. Once you build from it, it becomes **built**. When you finish and start a new cycle, the old one gets **archived**."

2. **Check `.git/`.** If it doesn't exist:
   - Run `git init`
   - "I've initialised version control — you'll need this for GitHub later."
   - Do not commit yet.

3. **Check coding standards (first cycle only).** Only do this if this is the **first PRD in the project** — there are no files in `.prd/` yet. Skip on later cycles.
   - Look for a `coding-standards` skill (e.g. `~/.claude/skills/coding-standards/SKILL.md`).
   - If it's already there → say nothing, you're set up.
   - If it's missing → offer to install the sibling plugin (it's published, v1.0.0):
     > "You don't have coding standards set up yet. There's a `coding-standards` plugin that asks you about your preferences and writes them into enforced rules. Want me to install it before we plan?"
   - **If the participant says yes:**
     1. Run: `claude plugin install coding-standards@likeahuman`
     2. If install succeeds, tell them — and STOP here, do not continue to Phase 1:
        > "Installed. Two quick things I can't do for you:
        > 1. Type `/reload-plugins` yourself — I can't run it.
        > 2. Then run `/coding-interview new` to set up your standards.
        > Come back and run `/bb-prd` again when you're done."
     3. If install fails, give the manual fallback:
        > "Auto-install didn't work. To do it by hand:
        > 1. Run: `claude plugin install coding-standards@likeahuman`
        > 2. Type `/reload-plugins` yourself — I can't run it.
        > 3. Then run `/coding-interview new`.
        > Come back to `/bb-prd` when you're done."
   - **If the participant says no** → continue with `/bb-prd` as normal. Don't bring it up again this session.

**Never blocking.** If `.prd/` or `.git/` setup fails, warn and continue. (The coding-standards step intentionally stops the flow only when the participant opts in.)

---

## Before You Start: Read the User

Calibrate your approach by reading signals from the participant and the project.

**From the `/bb-prd` argument:**
- Vague ("I want to build something for my team") → start with problem framing, use simple language
- Specific ("Add a webhook endpoint with retry logic") → skip basics, ask about edge cases
- Empty → use your opening from Phase 0.2

**From the project (already scanned in Phase 0):**
- Existing PRDs → match their style and depth
- `CLAUDE.md` → respect stated conventions
- Code exists → reference it, don't ask what they already have

**What you're gauging:**
- **Technical depth** — abstractions or outcomes?
- **Domain familiarity** — new to this or built it?
- **Decision style** — want options or a recommendation?
- **Detail appetite** — deep on every section, or "looks good, keep going"?

Adjust throughout. A participant who speeds up wants less hand-holding. One who pushes back wants more control. One who goes quiet may be lost — check in.

---

## Phase 1: Initial Understanding

**Goal:** Get the basic idea — enough to scope a codebase exploration, not enough to write a PRD yet.

1. If `$ARGUMENTS` is empty or vague, ask what the user wants to build.
2. Get just enough to direct the explorers: the problem, the rough solution shape, what area of the codebase is involved.
3. **Do NOT deep-dive yet.** Save detailed questions (edge cases, error handling, integration constraints, scope boundaries) for Phase 3 — they'll be sharper once you've seen the codebase.

**Gate → Phase 2:**
Lightweight. Summarize the idea in 2-3 sentences. Ask: "Is this roughly what you're thinking? I'll explore the codebase next."

---

## Phase 2: Codebase Exploration (conditional)

**Goal:** Understand the existing codebase so discovery questions and architecture decisions are grounded in reality.

**Auto-detect:** Check whether the repo already has cortex components (`.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `templates/`, `scripts/`).
- **No existing components** → Skip to Phase 3. Tell the user: "No existing components to explore — moving to discovery questions."
- **Components exist** → Continue with exploration.

**Actions:**
1. Launch 2-3 `codebase-explorer` agents in parallel (sonnet). Use the prompt template from `.claude/skills/bb-prd/prompts/explorer-prompt.md` — each agent gets a different exploration mode (architecture mapping, pattern matching, integration analysis).

2. Read key files the agents identified (the main model should read them directly — don't rely solely on agent summaries).
3. Synthesize findings into a brief summary: what exists, what patterns to follow, where the new feature fits.
4. Present findings to the user.

**Gate → Phase 3:**
Medium. Present your findings. The user might have questions or corrections. Wait for confirmation before moving to discovery.

---

## Phase 3: Informed Discovery

**Goal:** Now that you've seen the codebase, ask the questions that actually matter.

The codebase exploration in Phase 2 grounds your questions in reality. You can now ask about integration points you've seen, patterns that constrain the design, and gaps between the idea and what exists.

1. Cross-reference the participant's idea (Phase 1) against exploration findings (Phase 2). Surface tensions, opportunities, and patterns to follow or avoid.
2. Ask questions to fill remaining gaps. Adapt your questioning style:
   - **One at a time** when exploring unknowns
   - **Batch 2-3** when confirming details the user likely has ready answers for
   - **Multiple choice** when there are clear options
   - **Open-ended** when the user needs to explain intent
3. Focus on: edge cases, error handling, integration points, scope boundaries, backward compatibility, performance constraints — the things you couldn't ask well before seeing the code.
4. No fixed number of questions — stop when you have enough to design architecture.

**Gate → Phase 4:**
Lightweight. Summarize what you've learned (idea + codebase + answered questions) in 3-5 sentences. Ask: "Does this capture it? Ready to write the PRD?"

---

## Phase 4: Write PRD

**Goal:** Write a complete PRD and save it.

1. Load the PRD template from `.claude/skills/bb-prd/formats/prd-format.md`.
2. Write all core sections based on phases 1-4. **For any PRD that changes a component** (agent, skill, command, template, rubric, or pipeline code), the **Eval Acceptance Criteria** section is mandatory — no component PRD is complete without it. It names which `evals/registry.yaml` cases + thresholds define "done", and for a NEW component requires that fresh eval cases be authored as part of the work.
3. Decide which optional sections to include based on what you learned. Propose them to the user:
   > "Based on what we discussed, I'd also include [section] because [reason]. Agree?"
4. Present the PRD section by section for approval. For each section, show the content and ask if it looks right.
5. After approval, determine the filename:
   - Check `.prd/` for existing files to determine the next version number.
   - If a draft already exists (caught in Phase 0.3), you're finishing it — save to the same file.
   - If creating a new draft, save to `.prd/prd-v{N}.md` (next version number).
6. **Lifecycle cascade:** Before saving, flip all previous `built` or `released` PRDs to `archived`. Read each `.prd/prd-v*.md`, check frontmatter status, update if needed.
7. Ensure the PRD includes proper YAML frontmatter:
   ```yaml
   ---
   version: {N}
   status: draft
   date: {today}
   author: {participant name if known}
   previous: prd-v{N-1}.md
   ---
   ```
8. Do NOT create a git commit. That happens when `/bb-tickets` runs.

**After saving:**
Tell the user the PRD is saved and suggest `/bb-design` as the next step. Because you still hold the Phase 2 codebase map in context, running `/bb-design` in this same chat lets it reuse that exploration:
> "PRD saved to `.prd/prd-v{N}.md`. Run `/bb-design` next — it turns the PRD into a UX spec and solution design. Running it in this same chat means it can reuse the codebase map I just built."

